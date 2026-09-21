import json, pathlib, re, sys

REQ = pathlib.Path(sys.argv[1])
MASTER = pathlib.Path("index.html")

request = json.loads(REQ.read_text(encoding="utf-8"))
client_id = str(request["id"]).strip()
selected = {str(x).strip().lower() for x in request.get("brands", []) if str(x).strip()}
if not client_id or not selected:
    raise SystemExit("Invalid client request")

html = MASTER.read_text(encoding="utf-8")

# The master page keeps the catalog inside the main application <script> as:
#   const DATA={...};const ORIGINAL_DATA=...;function displaySize(...)
script_match = re.search(r"<script>(.*?)</script>", html, re.S)
if not script_match:
    raise SystemExit("Main application script not found")

script = script_match.group(1)
data_match = re.search(r"const DATA=(.*?);const ORIGINAL_DATA=", script, re.S)
if not data_match:
    raise SystemExit("Catalog DATA marker not found")

try:
    data = json.loads(data_match.group(1))
except json.JSONDecodeError as exc:
    raise SystemExit(f"Could not parse embedded DATA: {exc}") from exc

# Prefer the catalog snapshot captured by the Admin Panel at client creation.
# This guarantees that disabled/deleted products, sizes, and fragrances do not
# reappear in a newly generated client merely because index.html still contains
# the master/original catalog.
snapshot = request.get("catalog")
snapshot_version = request.get("catalogSnapshotVersion") or request.get("catalog_snapshot_version")
if not isinstance(snapshot, list) or not snapshot:
    raise SystemExit(
        "CATALOG_JSON is required for client publishing. "
        "Refusing to fall back to the master catalog because that could publish deleted products/sizes/fragrances."
    )
if str(snapshot_version or "1") != "1":
    raise SystemExit(f"Unsupported catalog snapshot version: {snapshot_version}")

snapshot_names = {str(b.get("name", "")).strip().lower() for b in snapshot if isinstance(b, dict)}
if snapshot_names != selected:
    raise SystemExit(
        f"CATALOG_JSON brand mismatch. Selected={sorted(selected)} Snapshot={sorted(snapshot_names)}"
    )

filtered = [
    b for b in snapshot
    if isinstance(b, dict)
    and str(b.get("name", "")).strip().lower() in selected
]

if not filtered:
    raise SystemExit("No selected brands exist in the client catalog snapshot")

client_data = {
    "settings": data.get("settings", {}),
    "brands": filtered,
}
literal = json.dumps(
    client_data,
    ensure_ascii=False,
    separators=(",", ":"),
).replace("</script", "<\\/script")

# Replace only the DATA payload. ORIGINAL_DATA remains derived from DATA,
# so the client keeps only its own filtered baseline.
script, replacements = re.subn(
    r"const DATA=.*?;const ORIGINAL_DATA=",
    "const DATA=" + literal + ";const ORIGINAL_DATA=",
    script,
    count=1,
    flags=re.S,
)
if replacements != 1:
    raise SystemExit("Could not replace embedded DATA")

script += """
// ===== STATIC CLIENT OVERRIDES =====
function getVisibleBrandNames(){return brands.map(b=>b.name);}
function visibleBrandIndexes(){return brands.map((_,i)=>i);}
function loadSavedAdminData(){return;}
window.openAdmin=()=>{};
document.addEventListener('DOMContentLoaded',()=>{
  try{
    initProductSelectors();
    fillBrands();
    render();
    translateHome();
  }catch(e){
    console.error('JASMINE client initialization error:',e);
  }
});
// ===== END STATIC CLIENT OVERRIDES =====
"""

client_html = html[:script_match.start(1)] + script + html[script_match.end(1):]

client_html = re.sub(
    r'<button[^>]*class="admin-launch"[^>]*>.*?</button>',
    '',
    client_html,
    flags=re.S,
)
client_html = client_html.replace(
    "</head>",
    '<style>.admin-launch,#adminPanel{display:none!important}</style></head>',
    1,
)

# GitHub Pages project sites are most reliable when client URLs point to an
# explicit .html file instead of relying on directory-index routing.
# Keep the directory/index.html copy for backward compatibility, but make the
# canonical published URL clients/<id>.html.
clients_dir = pathlib.Path("clients")
clients_dir.mkdir(parents=True, exist_ok=True)

canonical_path = clients_dir / f"{client_id}.html"
canonical_path.write_text(
    "<!doctype html>\n" + client_html,
    encoding="utf-8",
)

legacy_dir = clients_dir / client_id
legacy_dir.mkdir(parents=True, exist_ok=True)
(legacy_dir / "index.html").write_text(
    "<!doctype html>\n" + client_html,
    encoding="utf-8",
)

print(f"Published {canonical_path}")
print(f"Published legacy {legacy_dir / 'index.html'}")
