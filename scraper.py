import os, urllib.request, urllib.parse, json, re

TOKEN = "".join(os.environ.get("CRAWLBASE_TOKEN", "").split())
SB_URL = "".join(os.environ.get("SUPABASE_URL", "").split()).rstrip("/")
SB_KEY = "".join(os.environ.get("SUPABASE_SERVICE_KEY", "").split())

target = "https://rijksoverheid.nl"
params = urllib.parse.urlencode({"token": TOKEN, "url": target})
api_url = f"https://api.crawlbase.com/?{params}"

try:
    req_cb = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req_cb, timeout=30).read().decode("utf-8", errors="ignore")
    print("Crawlbase succes! Ontvangen bytes:", len(html))
except Exception as e:
    print("FOUT BIJ CRAWLBASE:", repr(e))
    exit(1)

links = re.findall(r'<a[^>]+href="(/actueel/nieuws/[^"]+)"[^>]*>(.*?)</a>', html, re.S)
print("Gevonden berichten:", len(links))

for pad, ruwe_titel in links[:5]:
    titel = re.sub(r'<[^>]+>', '', ruwe_titel).strip()
    if len(titel) < 15:
        continue
    payload = json.dumps({"titel": titel, "url": "https://rijksoverheid.nl" + pad, "bron": "Rijksoverheid"}).encode()
    req = urllib.request.Request(f"{SB_URL}/rest/v1/nieuws", data=payload, method="POST")
    req.add_header("apikey", SB_KEY)
    req.add_header("Authorization", f"Bearer {SB_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "resolution=ignore-duplicates")
    try:
        urllib.request.urlopen(req)
        print("Opgeslagen:", titel[:45])
    except Exception as e:
        print("FOUT BIJ SUPABASE:", repr(e))
