import os, urllib.request, urllib.parse, json, re

TOKEN = os.environ["CRAWLBASE_TOKEN"]
SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_KEY"]

target = "https://rijksoverheid.nl"
api_url = f"https://crawlbase.com{TOKEN}&url={urllib.parse.quote(target)}"

html = urllib.request.urlopen(api_url).read().decode("utf-8", errors="ignore")
links = re.findall(r'<a[^>]+href="(/actueel/nieuws/[^"]+)"[^>]*>(.*?)</a>', html, re.S)

for pad, ruwe_titel in links[:5]:
    titel = re.sub(r'<[^>]+>', '', ruwe_titel).strip()
    if len(titel) < 15:
        continue
    data = json.dumps({"titel": titel, "url": "https://rijksoverheid.nl" + pad, "bron": "Rijksoverheid"}).encode()
    req = urllib.request.Request(f"{SB_URL}/rest/v1/nieuws", data=data, method="POST")
    req.add_header("apikey", SB_KEY)
    req.add_header("Authorization", f"Bearer {SB_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "resolution=ignore-duplicates")
    try:
        urllib.request.urlopen(req)
    except Exception:
        pass
