import time
import hashlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus


BASE_URL = "https://www.olx.pl"


def build_olx_url(city, query, category="praca", filters=None):
    city = city.strip().lower().replace(" ", "-") if city else ""
    query = quote_plus(query.strip().lower()) if query else ""

    if city and query:
        url = f"{BASE_URL}/{category}/{city}/q-{query}/"
    elif city:
        url = f"{BASE_URL}/{category}/{city}/"
    elif query:
        url = f"{BASE_URL}/{category}/q-{query}/"
    else:
        url = f"{BASE_URL}/{category}/"

    params = ["search%5Border%5D=created_at:desc"]

    if filters:
        for key, value in filters.items():
            if isinstance(value, list):
                for i, v in enumerate(value):
                    params.append(f"search[filter_enum_{key}][{i}]={v}")
            else:
                params.append(f"search[filter_enum_{key}][0]={value}")

    return url + "?" + "&".join(params)


def get_headers():
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
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
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"[OLX] Błąd pobierania strony: {e}")
        return None


def extract_card_title(card):
    for selector in ["h4", "h6", "h3"]:
        tag = card.find(selector)
        if tag:
            return clean_text(tag.get_text())

    return "N/A"


def extract_card_link(card):
    link_tag = card.find("a", href=True)

    if not link_tag:
        return None

    return normalize_url(link_tag["href"])


def extract_card_details(card):
    details = {
        "price": "N/A",
        "location": "N/A",
        "contract": "N/A",
        "work_load": "N/A",
    }

    all_texts = []

    for tag in card.find_all(["p", "span", "div"]):
        text = clean_text(tag.get_text(" ", strip=True))

        if text and text != "N/A":
            all_texts.append(text)

    for text in all_texts:
        lower = text.lower()

        if details["price"] == "N/A" and ("zł" in lower or "pln" in lower):
            details["price"] = text

        elif details["contract"] == "N/A" and any(
            word in lower for word in ["umowa", "b2b", "kontrakt", "zlecenie", "samozatrudnienie"]
        ):
            details["contract"] = text

        elif details["work_load"] == "N/A" and any(
            word in lower for word in ["pełny etat", "część etatu", "dodatkowa", "praca zdalna", "hybrydowa"]
        ):
            details["work_load"] = text

        elif details["location"] == "N/A":
            if "," in text and len(text) < 80:
                details["location"] = text
            elif any(city_word in lower for city_word in ["kraków", "warszawa", "wrocław", "poznań", "gdańsk"]):
                details["location"] = text

    return details


def find_offer_cards(soup):
    cards = soup.find_all("div", {"data-cy": "l-card"})

    if cards:
        return cards

    cards = soup.find_all("div", {"data-testid": "l-card"})

    if cards:
        return cards

    cards = soup.find_all("a", href=True)

    fallback_cards = []

    for a in cards:
        href = a.get("href", "")

        if "/oferta/" in href or "/d/oferta/" in href:
            parent = a.find_parent("div")
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


def fetch_offer(url):
    if not url:
        return "N/A"

    html = fetch_page(url)

    if not html:
        return "N/A"

    soup = BeautifulSoup(html, "html.parser")

    possible_sections = [
        {"data-cy": "ad_description"},
        {"data-testid": "ad-description"},
        {"data-testid": "description"},
    ]

    for attrs in possible_sections:
        section = soup.find("div", attrs)
        if section:
            text = clean_text(section.get_text(" ", strip=True))
            if text and text != "N/A":
                return text

    for h2 in soup.find_all(["h2", "h3"]):
        if "opis" in h2.get_text(strip=True).lower():
            parent = h2.find_parent()
            if parent:
                text = clean_text(parent.get_text(" ", strip=True))
                if text:
                    return text

    main = soup.find("main")
    if main:
        text = clean_text(main.get_text(" ", strip=True))
        return text[:4000] if text else "N/A"

    return "N/A"


def fetch_offers(url, limit=20, delay=0.7):
    html = fetch_page(url)

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    cards = find_offer_cards(soup)

    if not cards:
        print("[OLX] Nie znaleziono kart ofert. Struktura strony mogła się zmienić.")
        return []

    offers = []
    seen_urls = set()

    for card in cards:
        if len(offers) >= limit:
            break

        try:
            title = extract_card_title(card)
            link = extract_card_link(card)

            if not link or link in seen_urls:
                continue

            seen_urls.add(link)

            details = extract_card_details(card)

            print(f"[OLX] Pobieranie opisu: {title}")
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
                "source": "OLX",
            })

        except Exception as e:
            print(f"[OLX] Błąd parsowania karty: {e}")
            continue

    return offers


def get_jobs_olx(city, query, filters=None, limit=20):
    url = build_olx_url(city, query, filters=filters)
    print(f"[OLX] URL: {url}")
    return fetch_offers(url, limit=limit)