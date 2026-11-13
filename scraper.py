import os, urllib.request, urllib.parse, json

TOKEN = "".join(os.environ.get("CRAWLBASE_TOKEN", "").split())
SB_URL = "".join(os.environ.get("SUPABASE_URL", "").split()).rstrip("/")
SB_KEY = "".join(os.environ.get("SUPABASE_SERVICE_KEY", "").split())

zoek_url = "https://google.nl"
params = urllib.parse.urlencode({"token": TOKEN, "url": zoek_url, "scraper": "google-serp"})
api_url = f"https://crawlbase.com?{params}"

try:
    raw = urllib.request.urlopen(api_url, timeout=45).read().decode("utf-8")
    data = json.loads(raw)
except Exception as e:
    print("Fout bij Crawlbase:", repr(e))
    exit(1)

artikelen = data.get("body", {}).get("news", []) or data.get("body", {}).get("organic", [])
print("Gevonden artikelen:", len(artikelen))

for item in artikelen[:8]:
    titel = item.get("title", "").strip()
    link = item.get("url", "").strip()
    bron = item.get("source", "Nieuws").strip()
    if not titel or not link:
        continue
    payload = json.dumps({"titel": titel, "url": link, "bron": bron}).encode()
    req = urllib.request.Request(f"{SB_URL}/rest/v1/nieuws", data=payload, method="POST")
    req.add_header("apikey", SB_KEY)
    req.add_header("Authorization", f"Bearer {SB_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "resolution=ignore-duplicates")
    try:
        urllib.request.urlopen(req)
        print("Opgeslagen:", titel[:50])
    except Exception:
        pass
