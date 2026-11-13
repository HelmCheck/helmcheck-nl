import os, urllib.request, urllib.parse, json, re

TOKEN = os.environ.get("CRAWLBASE_TOKEN", "").strip()
SB_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
SB_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()

target = "https://rijksoverheid.nl"
api_url = f"https://crawlbase.com{TOKEN}&url={urllib.parse.quote(target)}"

try:
    html = urllib.request.urlopen(api_url, timeout=30).read().decode("utf-8", errors="ignore")
    print("Crawlbase succesvol! Lengte HTML:", len(html))
except Exception as e:
    print("FOUT BIJ CRAWLBASE:", e)
    exit(1)

links = re.findall(r'<a[^>]+href="(/actueel/nieuws/[^"]+)"[^>]*>(.*?)</a>', html, re.S)
print("Gevonden nieuwslinks:", len(links))

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
        print("Opgeslagen:", titel[:40])
    except Exception as e:
        print("FOUT BIJ SUPABASE:", e)
