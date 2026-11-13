import os, urllib.request, urllib.parse, json, re

TOKEN = "".join(os.environ.get("CRAWLBASE_TOKEN", "").split())
SB_URL = "".join(os.environ.get("SUPABASE_URL", "").split()).rstrip("/")
SB_KEY = "".join(os.environ.get("SUPABASE_SERVICE_KEY", "").split())

trefwoorden = ["helm", "fatbike", "e-bike", "elektrische-fiets", "speed-pedelec", "fietshelm"]
bronnen = [
    ("NOS", "https://nos.nl", "https://nos.nl", r'(/artikel/\d+-[a-z0-9-]+)'),
    ("NOS", "https://nos.nl", "https://nos.nl", r'(/artikel/\d+-[a-z0-9-]+)'),
    ("Rijksoverheid", "https://rijksoverheid.nl", "https://rijksoverheid.nl", r'(/actueel/nieuws/\d{4}/\d{2}/\d{2}/[a-z0-9-]+)')
]

for bron, doel, basis, patroon in bronnen:
    api_url = f"https://api.crawlbase.com?{urllib.parse.urlencode({'token': TOKEN, 'url': doel})}"
    html = urllib.request.urlopen(urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode("utf-8", errors="ignore")
    gevonden = list(dict.fromkeys(re.findall(patroon, html)))
    print(f"{bron}: {len(gevonden)} unieke links gevonden")

    for pad in gevonden[:8]:
        if not any(w in pad.lower() for w in trefwoorden):
            continue
        slug = pad.rstrip("/").split("/")[-1]
        titel = re.sub(r'^\d+-', '', slug).replace("-", " ").capitalize()
        payload = json.dumps({"titel": titel, "url": basis + pad, "bron": bron}).encode()
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
