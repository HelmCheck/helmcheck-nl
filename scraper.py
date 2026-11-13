import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser


# Vereiste omgevingsvariabelen
SUPABASE_URL = os.environ["SUPABASE_URL"].strip().rstrip("/")
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"].strip()

# De officiële websites. Het script zoekt hier automatisch de feed-links.
BRONNEN = [
    ("Rijksoverheid", "https://feeds.rijksoverheid.nl"),
    ("NOS", "https://feeds.nos.nl"),
    ("NOS Politiek", "https://feeds.nos.nl"),
]

TREFWOORDEN = [
    "fatbike",
    "fatbikes",
    "helmplicht",
    "fietshelm",
    "helm",
    "e-bike",
    "elektrische fiets",
    "speed pedelec",
    "bromfiets",
]


class FeedLinkParser(HTMLParser):
    """Vindt RSS- en Atom-feed-links in de HTML van een website."""

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "link":
            return

        eigenschappen = {naam.lower(): waarde for naam, waarde in attrs}
        rel = eigenschappen.get("rel", "").lower().split()
        content_type = eigenschappen.get("type", "").lower()
        href = eigenschappen.get("href")

        is_feed = (
            "alternate" in rel
            and href
            and (
                "rss" in content_type
                or "atom" in content_type
                or "xml" in content_type
            )
        )

        if is_feed:
            self.links.append(href)


def haal_op(url):
    verzoek = urllib.request.Request(
        url,
        headers={
            "User-Agent": "FatbikeNieuwsBot/1.0",
            "Accept": "text/html,application/rss+xml,application/atom+xml,application/xml",
        },
    )
    with urllib.request.urlopen(verzoek, timeout=30) as antwoord:
        return antwoord.read(), antwoord.geturl(), antwoord.headers.get("Content-Type", "")


def vind_feed_urls(website_url):
    """Zoekt feed-links op de officiële website."""
    inhoud, uiteindelijke_url, content_type = haal_op(website_url)

    # Als de opgegeven URL zelf al een XML-feed is.
    if "xml" in content_type or "rss" in content_type or "atom" in content_type:
        return [uiteindelijke_url]

    parser = FeedLinkParser()
    parser.feed(inhoud.decode("utf-8", errors="replace"))

    # Maak relatieve feed-links volledig.
    return list(dict.fromkeys(
        urllib.parse.urljoin(uiteindelijke_url, link)
        for link in parser.links
    ))


def lokale_naam(tag):
    """Verwijdert een eventuele XML-namespace uit een tagnaam."""
    return tag.rsplit("}", 1)[-1].lower()


def vind_kind(element, namen):
    for kind in element:
        if lokale_naam(kind.tag) in namen:
            return kind
    return None


def tekst(element):
    if element is None:
        return ""
    waarde = " ".join(element.itertext())
    waarde = re.sub(r"<[^>]*>", " ", waarde)
    return re.sub(r"\s+", " ", waarde).strip()


def veldtekst(element, namen):
    return tekst(vind_kind(element, namen))


def artikel_link(item):
    link_element = vind_kind(item, {"link"})
    if link_element is None:
        return ""

    # Atom gebruikt meestal een href-attribuut; RSS meestal tekst.
    return (
        link_element.attrib.get("href", "").strip()
        or tekst(link_element)
    )


def artikel_datum(item):
    datum_tekst = veldtekst(
        item,
        {"pubdate", "published", "updated", "date", "created"},
    )

    if not datum_tekst:
        return None

    try:
        datum = parsedate_to_datetime(datum_tekst)
    except (TypeError, ValueError):
        try:
            datum = datetime.fromisoformat(datum_tekst.replace("Z", "+00:00"))
        except ValueError:
            return None

    if datum.tzinfo is None:
        datum = datum.replace(tzinfo=timezone.utc)

    return datum.date().isoformat()


def lees_feed(feed_url):
    inhoud, _, _ = haal_op(feed_url)
    root = ET.fromstring(inhoud)

    return [
        element
        for element in root.iter()
        if lokale_naam(element.tag) in {"item", "entry"}
    ]


def sla_op(artikel):
    endpoint = f"{SUPABASE_URL}/rest/v1/nieuws"
    endpoint += "?" + urllib.parse.urlencode({"on_conflict": "url"})

    gegevens = json.dumps(artikel).encode("utf-8")
    verzoek = urllib.request.Request(endpoint, data=gegevens, method="POST")
    verzoek.add_header("apikey", SUPABASE_SERVICE_KEY)
    verzoek.add_header("Authorization", f"Bearer {SUPABASE_SERVICE_KEY}")
    verzoek.add_header("Content-Type", "application/json")
    verzoek.add_header(
        "Prefer",
        "resolution=ignore-duplicates,return=minimal",
    )

    with urllib.request.urlopen(verzoek, timeout=30):
        pass


def verwerk_bron(bron, website_url):
    print(f"\nBron: {bron}")

    try:
        feed_urls = vind_feed_urls(website_url)
    except Exception as fout:
        print(f"Website niet bereikbaar: {fout}")
        return

    if not feed_urls:
        print("Geen RSS- of Atom-feed gevonden op de website.")
        return

    for feed_url in feed_urls:
        print(f"Feed: {feed_url}")

        try:
            items = lees_feed(feed_url)
        except Exception as fout:
            print(f"Feed kon niet worden gelezen: {fout}")
            continue

        for item in items:
            titel = veldtekst(item, {"title"})
            beschrijving = veldtekst(
                item,
                {"description", "summary", "content", "encoded"},
            )
            link = artikel_link(item)

            if not titel or not link:
                continue

            zoektekst = f"{titel} {beschrijving}".lower()
            if not any(term in zoektekst for term in TREFWOORDEN):
                continue

            artikel = {
                "titel": titel,
                "url": link,
                "bron": bron,
                "datum": artikel_datum(item),
            }

            try:
                sla_op(artikel)
                print(f"Opgeslagen: {titel}")
            except urllib.error.HTTPError as fout:
                details = fout.read().decode("utf-8", errors="replace")
                print(f"Supabase-fout {fout.code}: {details}")
            except Exception as fout:
                print(f"Opslaan mislukt: {fout}")


if __name__ == "__main__":
    for bron, website_url in BRONNEN:
        verwerk_bron(bron, website_url)
