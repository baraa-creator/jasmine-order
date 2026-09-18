import json, pathlib, re, sys

body = sys.argv[1]
def field(label):
    m = re.search(r"^"+re.escape(label)+r"\s*:\s*(.+)$", body, re.M)
    return m.group(1).strip() if m else ""

client_id = field("CLIENT_ID")
client_name = field("CLIENT_NAME")
brands_raw = field("BRANDS_JSON")
if not client_id or not client_name or not brands_raw:
    raise SystemExit("Issue body is missing CLIENT_ID, CLIENT_NAME or BRANDS_JSON")
brands = json.loads(brands_raw)
if not isinstance(brands, list) or not brands:
    raise SystemExit("BRANDS_JSON must be a non-empty JSON array")
pathlib.Path("client-requests").mkdir(exist_ok=True)
out = pathlib.Path("client-requests") / f"{client_id}.json"
out.write_text(json.dumps({"id":client_id,"name":client_name,"brands":brands},ensure_ascii=False,indent=2),encoding="utf-8")
print(out)
