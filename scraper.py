import os, urllib.request, urllib.parse, json, re

TOKEN = "".join(os.environ.get("CRAWLBASE_TOKEN", "").split())
SB_URL = "".join(os.environ.get("SUPABASE_URL", "").split()).rstrip("/")
SB_KEY = "".join(os.environ.get("SUPABASE_SERVICE_KEY", "").split())

trefwoorden = ["helm", "fatbike", "e-bike", "elektrische fiets", "speed pedelec", "step"]
bronnen = [
    ("Rijksoverheid", "https://rijksoverheid.nl", "https://rijksoverheid.nl"),
    ("NOS", "https://nos.nl", "https://nos.nl")
]

for bron_naam, doel_url, basis_url in bronnen:
    api_url = f"https://crawlbase.com?{urllib.parse.urlencode({'token': TOKEN, 'url': doel_url})}"
    try:
        html = urllib.request.urlopen(api_url, timeout=30).read().decode("utf-8", errors="ignore")
        print(f"{bron_naam} opgehaald ({len(html)} bytes)")
    except Exception as e:
        print(f"Overgeslagen ({bron_naam}):", e)
        continue

    links = re.findall(r'<a[^>]+href="(/[^"]+)"[^>]*>(.*?)</a>', html, re.S)
    for pad, ruwe_titel in links:
        titel = re.sub(r'<[^>]+>', '', ruwe_titel).strip()
        if len(titel) < 20 or not any(w in titel.lower() for w in trefwoorden):
            continue
        payload = json.dumps({"titel": titel, "url": basis_url + pad, "bron": bron_naam}).encode()
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
