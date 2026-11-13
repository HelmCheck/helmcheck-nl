import os, urllib.request, urllib.parse, json, re

TOKEN = "".join(os.environ.get("CRAWLBASE_TOKEN", "").split())
SB_URL = "".join(os.environ.get("SUPABASE_URL", "").split()).rstrip("/")
SB_KEY = "".join(os.environ.get("SUPABASE_SERVICE_KEY", "").split())

trefwoorden = ["helmplicht", "fietshelm", "fatbike", "e-bike", "speed pedelec"]
doel = "https://bing.com"
params = urllib.parse.urlencode({"token": TOKEN, "url": doel})
api_url = f"https://api.crawlbase.com?{params}"

req_cb = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req_cb, timeout=30).read().decode("utf-8", errors="ignore")

links = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.S)
for url, ruwe_titel in links:
    titel = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', ruwe_titel)).strip()
    if len(titel) < 25 or url.count("/") < 4 or "bing.com" in url or "microsoft.com" in url:
        continue
    if not any(w in titel.lower() for w in trefwoorden):
        continue
    payload = json.dumps({"titel": titel, "url": url, "bron": "Actueel Nieuws"}).encode()
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
