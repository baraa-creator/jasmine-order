import json, pathlib, sys

if len(sys.argv) != 4:
    raise SystemExit("Usage: make_client_request.py <client_id> <client_name> <brands_json>")

client_id = sys.argv[1].strip()
client_name = sys.argv[2].strip()
brands = json.loads(sys.argv[3])

if not client_id or not client_name or not isinstance(brands, list) or not brands:
    raise SystemExit("Invalid client request")

pathlib.Path("client-requests").mkdir(exist_ok=True)
out = pathlib.Path("client-requests") / f"{client_id}.json"
out.write_text(json.dumps({
    "id": client_id,
    "name": client_name,
    "brands": [str(x).strip() for x in brands if str(x).strip()]
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(out)
