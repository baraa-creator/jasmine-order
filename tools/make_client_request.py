import json, pathlib, sys

if len(sys.argv) != 5:
    raise SystemExit("Usage: make_client_request.py <client_id> <client_name> <brands_json> <catalog_json>")

client_id = sys.argv[1].strip()
client_name = sys.argv[2].strip()
brands = json.loads(sys.argv[3])
catalog = json.loads(sys.argv[4])

if not client_id or not client_name or not isinstance(brands, list) or not brands or not isinstance(catalog, list) or not catalog:
    raise SystemExit("Invalid client request: catalog snapshot is required")
selected={str(x).strip().lower() for x in brands}
snapshot={str(x.get("name","")).strip().lower() for x in catalog if isinstance(x,dict)}
if selected != snapshot:
    raise SystemExit("Catalog snapshot brands do not match brands_json")

pathlib.Path("client-requests").mkdir(exist_ok=True)
out = pathlib.Path("client-requests") / f"{client_id}.json"
out.write_text(json.dumps({
    "id": client_id,
    "name": client_name,
    "brands": [str(x).strip() for x in brands if str(x).strip()],
    "catalog": catalog,
    "catalogSnapshotVersion": 1
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(out)
