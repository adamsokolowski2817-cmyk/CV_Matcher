import time
import hashlib
from urllib.parse import quote_plus

from curl_cffi import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.pracuj.pl"


def build_pracuj_url(city, query, category="praca", filters=None):
    city = city.strip().lower().replace(" ", "-") if city else ""
    query = quote_plus(query.strip().lower()) if query else ""

    url = f"{BASE_URL}/{category}"

    if query:
        url += f"/{query};kw"

    if city:
        url += f"/{city};wp"

    params = []

    if filters:
        for key, value in filters.items():
            if isinstance(value, list):
                for v in value:
                    params.append(f"{key}={v}")
            else:
                params.append(f"{key}={value}")

    if params:
        url += "?" + "&".join(params)

    return url


def get_headers():
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.7,en;q=0.6",
    }


def clean_text(text):
    if not text:
        return "N/A"

    return " ".join(text.split())


def make_offer_id(url):
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def normalize_url(link):
    if not link:
        return None

    if link.startswith("http"):
        return link

    if link.startswith("/"):
        return BASE_URL + link

    return BASE_URL + "/" + link


def fetch_page(url):
    try:
        response = requests.get(
            url,
            headers=get_headers(),
            impersonate="chrome",
            timeout=20,
        )
        response.raise_for_status()
        return response.text

    except Exception as e:
        print(f"[Pracuj.pl] Błąd pobierania strony: {e}")
        return None


def extract_title(card):
    selectors = [
        ("h2", {}),
        ("h3", {}),
        ("a", {"data-test": "link-offer"}),
        ("a", {"data-test": "offer-title"}),
    ]

    for tag_name, attrs in selectors:
        tag = card.find(tag_name, attrs)
        if tag:
            text = clean_text(tag.get_text(" ", strip=True))
            if text != "N/A":
                return text

    return "N/A"


def extract_link(card):
    link_tag = card.find("a", href=True)

    if not link_tag:
        return None

    return normalize_url(link_tag["href"])


def extract_details(card):
    details = {
        "price": "N/A",
        "location": "N/A",
        "contract": "N/A",
        "work_load": "N/A",
    }

    texts = []

    for tag in card.find_all(["li", "p", "span", "div"]):
        text = clean_text(tag.get_text(" ", strip=True))
        if text != "N/A":
            texts.append(text)

    for text in texts:
        lower = text.lower()

        if details["price"] == "N/A" and any(x in lower for x in ["pln", "zł", "brutto", "netto"]):
            details["price"] = text

        elif details["contract"] == "N/A" and any(
            x in lower for x in ["umowa", "b2b", "kontrakt", "zlecenie", "dzieło"]
        ):
            details["contract"] = text

        elif details["work_load"] == "N/A" and any(
            x in lower for x in ["pełny etat", "część etatu", "etat", "praktyki", "staż"]
        ):
            details["work_load"] = text

        elif details["location"] == "N/A" and len(text) < 100:
            if any(city in lower for city in ["kraków", "warszawa", "wrocław", "poznań", "gdańsk", "katowice"]):
                details["location"] = text

    return details


def find_offer_cards(soup):
    selectors = [
        ("div", {"data-test": "default-offer"}),
        ("div", {"data-test": "offer-card"}),
        ("article", {}),
    ]

    for tag_name, attrs in selectors:
        cards = soup.find_all(tag_name, attrs)
        if cards:
            return cards

    links = soup.find_all("a", href=True)
    fallback_cards = []

    for link in links:
        href = link.get("href", "")

        if "/praca/" in href and ("oferta" in href or "pracuj.pl" in href):
            parent = link.find_parent(["div", "article", "section"])
            if parent:
                fallback_cards.append(parent)

    unique = []
    seen = set()

    for card in fallback_cards:
        card_id = id(card)
        if card_id not in seen:
            seen.add(card_id)
            unique.append(card)

    return unique


def extract_description_from_detail_page(soup):
    sections = [
        {"data-test": "section-responsibilities"},
        {"data-test": "section-requirements"},
        {"data-test": "section-benefits"},
        {"data-test": "text-description"},
        {"data-test": "offer-description"},
    ]

    collected = []

    for attrs in sections:
        section = soup.find("div", attrs)
        if section:
            text = clean_text(section.get_text(" ", strip=True))
            if text != "N/A":
                collected.append(text)

    if collected:
        return " ".join(collected)

    headers = [
        "twój zakres obowiązków",
        "nasze wymagania",
        "mile widziane",
        "opis stanowiska",
        "wymagania",
        "obowiązki",
        "technologie",
    ]

    for header in soup.find_all(["h2", "h3", "h4"]):
        h_text = header.get_text(" ", strip=True).lower()

        if any(h in h_text for h in headers):
            parent = header.find_parent(["section", "div"])
            if parent:
                text = clean_text(parent.get_text(" ", strip=True))
                if text != "N/A":
                    collected.append(text)

    if collected:
        return " ".join(collected)

    main = soup.find("main")
    if main:
        text = clean_text(main.get_text(" ", strip=True))
        return text[:5000] if text != "N/A" else "N/A"

    return "N/A"


def fetch_offer(url):
    if not url:
        return "N/A"

    html = fetch_page(url)

    if not html:
        return "N/A"

    soup = BeautifulSoup(html, "html.parser")
    return extract_description_from_detail_page(soup)


def fetch_offers(url, limit=20, delay=0.7):
    html = fetch_page(url)

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    cards = find_offer_cards(soup)

    if not cards:
        print("[Pracuj.pl] Nie znaleziono kart ofert. Struktura strony mogła się zmienić.")
        return []

    offers = []
    seen_urls = set()

    for card in cards:
        if len(offers) >= limit:
            break

        try:
            title = extract_title(card)
            link = extract_link(card)

            if not link or link in seen_urls:
                continue

            seen_urls.add(link)
            details = extract_details(card)

            print(f"[Pracuj.pl] Pobieranie opisu: {title}")
            description = fetch_offer(link)
            time.sleep(delay)

            offers.append({
                "id": make_offer_id(link),
                "title": title,
                "price": details["price"],
                "location": details["location"],
                "contract": details["contract"],
                "work_load": details["work_load"],
                "description": description,
                "url": link,
                "source": "Pracuj.pl",
            })

        except Exception as e:
            print(f"[Pracuj.pl] Błąd parsowania karty: {e}")
            continue

    return offers


def get_jobs_pracuj(city, query, filters=None, limit=20):
    url = build_pracuj_url(city, query, filters=filters)
    print(f"[Pracuj.pl] URL: {url}")
    return fetch_offers(url, limit=limit)