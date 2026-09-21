import json, pathlib, re, sys

body = sys.argv[1]
def field(label):
    m = re.search(r"^"+re.escape(label)+r"\s*:\s*(.+)$", body, re.M)
    return m.group(1).strip() if m else ""

client_id = field("CLIENT_ID")
client_name = field("CLIENT_NAME")
brands_raw = field("BRANDS_JSON")
catalog_raw = field("CATALOG_JSON")
if not client_id or not client_name or not brands_raw:
    raise SystemExit("Issue body is missing CLIENT_ID, CLIENT_NAME or BRANDS_JSON")
brands = json.loads(brands_raw)
if not isinstance(brands, list) or not brands:
    raise SystemExit("BRANDS_JSON must be a non-empty JSON array")

if not catalog_raw:
    raise SystemExit(
        "CATALOG_JSON is required. Refusing to create a client request without "
        "the current admin catalog snapshot."
    )

catalog = json.loads(catalog_raw)
if not isinstance(catalog, list) or not catalog:
    raise SystemExit("CATALOG_JSON must be a non-empty JSON array")

catalog_names = {str(b.get("name","")).strip().lower() for b in catalog if isinstance(b, dict)}
selected_names = {str(b).strip().lower() for b in brands}
if catalog_names != selected_names:
    raise SystemExit("CATALOG_JSON brands do not match BRANDS_JSON")

pathlib.Path("client-requests").mkdir(exist_ok=True)
out = pathlib.Path("client-requests") / f"{client_id}.json"
payload = {
    "id":client_id,
    "name":client_name,
    "brands":brands,
    "catalog":catalog,
    "catalogSnapshotVersion":1
}
out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print(out)
