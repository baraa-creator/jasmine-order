import json, pathlib, re, sys

REQ = pathlib.Path(sys.argv[1])
MASTER = pathlib.Path("index.html")

request = json.loads(REQ.read_text(encoding="utf-8"))
client_id = str(request["id"]).strip()
selected = {str(x).strip().lower() for x in request.get("brands", []) if str(x).strip()}
if not client_id or not selected:
    raise SystemExit("Invalid client request")

html = MASTER.read_text(encoding="utf-8")
marker_start = html.find("const DATA=")
marker_end = html.find(";function displaySize", marker_start)
if marker_start < 0 or marker_end < 0:
    raise SystemExit("Catalog DATA marker not found")

js = html[html.find("<script"):html.rfind("</script>")+9]
data_match = re.search(r"const DATA=(.*?);function displaySize", js, re.S)
if not data_match:
    raise SystemExit("Could not read embedded DATA")

data = json.loads(data_match.group(1))
brands = data.get("brands", [])
filtered = [b for b in brands if str(b.get("name", "")).strip().lower() in selected]
if not filtered:
    raise SystemExit("No selected brands exist in master catalog")

client_data = {"settings": data.get("settings", {}), "brands": filtered}
literal = json.dumps(client_data, ensure_ascii=False, separators=(",", ":")).replace("</script", "<\\/script")

script_match = re.search(r"<script>(.*?)</script>", html, re.S)
if not script_match:
    raise SystemExit("Main application script not found")

script = script_match.group(1)
script = re.sub(
    r"const DATA=.*?;function displaySize",
    "const DATA=" + literal + ";function displaySize",
    script,
    count=1,
    flags=re.S,
)

script += """
// ===== STATIC CLIENT OVERRIDES =====
function getVisibleBrandNames(){return brands.map(b=>b.name);}
function visibleBrandIndexes(){return brands.map((_,i)=>i);}
function loadSavedAdminData(){return;}
window.openAdmin=()=>{};
document.addEventListener('DOMContentLoaded',()=>{
  try{initProductSelectors();fillBrands();render();translateHome();}
  catch(e){console.error('JASMINE client initialization error',e);}
});
// ===== END STATIC CLIENT OVERRIDES =====
"""

client_html = html[:script_match.start(1)] + script + html[script_match.end(1):]

# Remove admin markup from the published page.
client_html = re.sub(r'<button[^>]*class="admin-launch"[^>]*>.*?</button>', '', client_html, flags=re.S)
client_html = re.sub(r'<div class="admin-panel" id="adminPanel">.*?</div>\s*</div>\s*<div class="modal" id="shareFallback"', '<div class="modal" id="shareFallback"', client_html, flags=re.S)
client_html = client_html.replace("</head>", '<style>.admin-launch,#adminPanel{display:none!important}</style></head>')

out_dir = pathlib.Path("clients") / client_id
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "index.html").write_text("<!doctype html>\n" + client_html, encoding="utf-8")
print(f"Published clients/{client_id}/index.html")
