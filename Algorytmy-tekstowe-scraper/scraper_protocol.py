import time
import hashlib
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://theprotocol.it"


def build_protocol_url(query):
    query = quote_plus(query.lower().strip()) if query else ""

    if query:
        return f"{BASE_URL}/praca/{query}"

    return f"{BASE_URL}/praca"


def get_headers():
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.7,en;q=0.6",
    }


def clean_text(text):
    if not text:
        return "N/A"

    return " ".join(text.split())


def make_offer_id(url):
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def fetch_page(url):
    try:
        response = requests.get(
            url,
            headers=get_headers(),
            timeout=20,
        )

        response.raise_for_status()
        return response.text

    except Exception as e:
        print(f"[The Protocol] Błąd pobierania strony: {e}")
        return None


def extract_cards(soup):
    cards = soup.find_all("a", href=True)

    filtered = []

    for card in cards:
        href = card.get("href", "")

        if "/praca/" in href:
            filtered.append(card)

    return filtered


def extract_title(card):
    for tag in ["h2", "h3", "span"]:
        el = card.find(tag)

        if el:
            text = clean_text(el.get_text())

            if len(text) > 5:
                return text

    return "N/A"


def extract_location(card):
    text = clean_text(card.get_text(" ", strip=True))

    cities = [
        "kraków",
        "warszawa",
        "wrocław",
        "poznań",
        "gdańsk",
        "katowice",
        "remote",
        "zdalnie",
    ]

    lower = text.lower()

    for city in cities:
        if city in lower:
            return city.title()

    return "N/A"


def extract_salary(card):
    text = clean_text(card.get_text(" ", strip=True))

    if "pln" in text.lower() or "zł" in text.lower():
        return text[:120]

    return "N/A"


def normalize_url(url):
    if url.startswith("http"):
        return url

    return BASE_URL + url


def extract_offer_description(soup):
    sections = []

    headers = [
        "technologies",
        "requirements",
        "nice to have",
        "responsibilities",
        "about the role",
        "must have",
    ]

    for header in soup.find_all(["h2", "h3", "h4"]):
        header_text = header.get_text(" ", strip=True).lower()

        if any(h in header_text for h in headers):
            parent = header.find_parent(["section", "div"])

            if parent:
                text = clean_text(parent.get_text(" ", strip=True))

                if text and text != "N/A":
                    sections.append(text)

    if sections:
        return " ".join(sections)

    main = soup.find("main")

    if main:
        text = clean_text(main.get_text(" ", strip=True))

        if text:
            return text[:5000]

    return "N/A"


def fetch_offer(url):
    html = fetch_page(url)

    if not html:
        return "N/A"

    soup = BeautifulSoup(html, "html.parser")

    return extract_offer_description(soup)


def fetch_offers(url, limit=20, delay=0.7):
    html = fetch_page(url)

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    cards = extract_cards(soup)

    offers = []
    seen = set()

    for card in cards:
        if len(offers) >= limit:
            break

        try:
            href = card.get("href")

            if not href:
                continue

            link = normalize_url(href)

            if link in seen:
                continue

            seen.add(link)

            title = extract_title(card)

            if title == "N/A":
                continue

            print(f"[The Protocol] Pobieranie: {title}")

            description = fetch_offer(link)

            time.sleep(delay)

            offers.append({
                "id": make_offer_id(link),
                "title": title,
                "price": extract_salary(card),
                "location": extract_location(card),
                "contract": "N/A",
                "work_load": "N/A",
                "description": description,
                "url": link,
                "source": "The Protocol",
            })

        except Exception as e:
            print(f"[The Protocol] Błąd parsowania: {e}")
            continue

    return offers


def get_jobs_protocol(query, limit=20):
    url = build_protocol_url(query)

    print(f"[The Protocol] URL: {url}")

    return fetch_offers(url, limit=limit)


if __name__ == "__main__":

    offers = get_jobs_protocol("python", limit=5)

    for offer in offers:
        print()
        print(offer["title"])
        print(offer["location"])
        print(offer["url"])
        print(offer["description"][:300])