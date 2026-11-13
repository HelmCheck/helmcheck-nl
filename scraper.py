import os, urllib.request, urllib.parse, json, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

TOKEN = "".join(os.environ.get("CRAWLBASE_TOKEN", "").split())
SB_URL = "".join(os.environ.get("SUPABASE_URL", "").split()).rstrip("/")
SB_KEY = "".join(os.environ.get("SUPABASE_SERVICE_KEY", "").split())

feed_url = "https://google.com"
api_url = f"https://crawlbase.com?{urllib.parse.urlencode({'token': TOKEN, 'url': feed_url})}"

req_cb = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
xml_data = urllib.request.urlopen(req_cb, timeout=30).read()
root = ET.fromstring(xml_data)

for item in root.findall(".//item")[:10]:
    titel = item.findtext("title", "").rsplit(" - ", 1)[0].strip()
    bron = item.findtext("source", "Nieuws").strip()
    link = item.findtext("link", "").strip()
    pub_date = item.findtext("pubDate", "")
    datum_str = parsedate_to_datetime(pub_date).strftime("%Y-%m-%d") if pub_date else "2026-01-01"

    payload = json.dumps({"titel": titel, "url": link, "bron": bron, "datum": datum_str}).encode()
    req = urllib.request.Request(f"{SB_URL}/rest/v1/nieuws", data=payload, method="POST")
    req.add_header("apikey", SB_KEY)
    req.add_header("Authorization", f"Bearer {SB_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "resolution=ignore-duplicates")
    try:
        urllib.request.urlopen(req)
        print(f"Opgeslagen ({datum_str}): {titel[:40]}")
    except Exception:
        pass
