import os, urllib.request, urllib.parse, json, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

TOKEN = "".join(os.environ.get("CRAWLBASE_TOKEN", "").split())
SB_URL = "".join(os.environ.get("SUPABASE_URL", "").split()).rstrip("/")
SB_KEY = "".join(os.environ.get("SUPABASE_SERVICE_KEY", "").split())

trefwoorden = ["helm", "fatbike", "e-bike", "elektrische fiets", "speed pedelec", "step"]
feeds = [
    ("NU.nl", "https://nu.nl"),
    ("NU.nl Tech", "https://nu.nl")
]

for bron, feed_url in feeds:
    api_url = f"https://crawlbase.com?{urllib.parse.urlencode({'token': TOKEN, 'url': feed_url})}"
    try:
        xml_data = urllib.request.urlopen(api_url, timeout=30).read()
        root = ET.fromstring(xml_data)
    except Exception as e:
        print(f"Fout bij {bron}:", e)
        continue

    for item in root.findall(".//item"):
        titel = item.findtext("title", "").strip()
        if not any(w in titel.lower() for w in trefwoorden):
            continue
        link = item.findtext("link", "").strip()
        pub = item.findtext("pubDate", "")
        datum = parsedate_to_datetime(pub).strftime("%Y-%m-%d") if pub else "2026-11-13"

        payload = json.dumps({"titel": titel, "url": link, "bron": bron, "datum": datum}).encode()
        req = urllib.request.Request(f"{SB_URL}/rest/v1/nieuws", data=payload, method="POST")
        req.add_header("apikey", SB_KEY)
        req.add_header("Authorization", f"Bearer {SB_KEY}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Prefer", "resolution=ignore-duplicates")
        try:
            urllib.request.urlopen(req)
            print(f"Opgeslagen ({datum}): {titel[:45]}")
        except Exception:
            pass
