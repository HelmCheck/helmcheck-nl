import os, urllib.request, urllib.parse, json, re

TOKEN = "".join(os.environ.get("CRAWLBASE_TOKEN", "").split())
SB_URL = "".join(os.environ.get("SUPABASE_URL", "").split()).rstrip("/")
SB_KEY = "".join(os.environ.get("SUPABASE_SERVICE_KEY", "").split())

trefwoorden = ["helmplicht", "fatbike", "e-bike", "elektrische fiets", "speed pedelec", "elektrische step", "helm"]
pagina = "https://rijksoverheid.nl"
params = urllib.parse.urlencode({"token": TOKEN, "url": pagina})
api_url = f"https://crawlbase.com?{params}"

req_cb = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req_cb, timeout=30).read().decode("utf-8", errors="ignore")

links = re.findall(r'<a[^>]+href="(/onderwerpen/fiets/[^"]+|/actueel/nieuws/[^"]+)"[^>]*>(.*?)</a>', html, re.S)
for pad, ruwe_titel in links:
    titel = re.sub(r'<[^>]+>', ' ', ruwe_titel).strip()
    titel = re.sub(r'\s+', ' ', titel)
    if len(titel) < 20 or not any(w in titel.lower() for w in trefwoorden):
        continue
    payload = json.dumps({"titel": titel, "url": "https://rijksoverheid.nl" + pad, "bron": "Rijksoverheid"}).encode()
    req = urllib.request.Request(f"{SB_URL}/rest/v1/nieuws", data=payload, method="POST")
    req.add_header("apikey", SB_KEY)
    req.add_header("Authorization", f"Bearer {SB_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "resolution=ignore-duplicates")
    try:
        urllib.request.urlopen(req)
        print("Opgeslagen:", titel[:55])
    except Exception:
        pass
