import os, urllib.request, urllib.parse, json, re

TOKEN = "".join(os.environ.get("CRAWLBASE_TOKEN", "").split())
SB_URL = "".join(os.environ.get("SUPABASE_URL", "").split()).rstrip("/")
SB_KEY = "".join(os.environ.get("SUPABASE_SERVICE_KEY", "").split())

bronnen = [
    ("NOS", "https://nos.nl", "https://nos.nl", r'(/artikel/\d+-[a-z0-9-]+)', False),
    ("NOS", "https://nos.nl", "https://nos.nl", r'(/artikel/\d+-[a-z0-9-]+)', False),
    ("Rijksoverheid", "https://rijksoverheid.nl", "https://rijksoverheid.nl", r'(/actueel/nieuws/\d{4}/\d{2}/\d{2}/[a-z0-9-]+)', True)
]
trefwoorden = ["helm", "fatbike", "e-bike", "fiets", "bromfiets", "step"]

for bron, doel, basis, patroon, filter_nodig in bronnen:
    api_url = f"https://api.crawlbase.com?{urllib.parse.urlencode({'token': TOKEN, 'url': doel})}"
    try:
        html = urllib.request.urlopen(urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Fout bij {bron}:", e)
        continue

    gevonden = list(dict.fromkeys(re.findall(patroon, html)))
    print(f"{bron} ({doel}): {len(gevonden)} links gevonden")
    for pad in gevonden[:10]:
        if filter_nodig and not any(w in pad.lower() for w in trefwoorden):
            continue
        slug = pad.rstrip("/").split("/")[-1]
        titel = re.sub(r'^\d+-', '', slug).replace("-", " ").capitalize()
        datum_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', pad)
        datum = f"{datum_match.group(1)}-{datum_match.group(2)}-{datum_match.group(3)}" if datum_match else "2026-10-01"

        payload = json.dumps({"titel": titel, "url": basis + pad, "bron": bron, "datum": datum}).encode()
        req = urllib.request.Request(f"{SB_URL}/rest/v1/nieuws", data=payload, method="POST")
        req.add_header("apikey", SB_KEY)
        req.add_header("Authorization", f"Bearer {SB_KEY}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Prefer", "resolution=ignore-duplicates")
        try:
            urllib.request.urlopen(req)
            print(f"Opgeslagen ({bron}): {titel[:45]}")
        except Exception:
            pass
