import sys
import os
import numpy as np
from database import OfferDatabase
from scraper import get_jobs_olx
from scraper_pracuj import get_jobs_pracuj
from fastembed import TextEmbedding
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine
from cv_advisor import generate_cv_suggestions
from skills import extract_skills
from scraper_protocol import get_jobs_protocol


# ---------------------------------------------------------------------------
# Model embeddingów (ONNX, bez PyTorch, wielojęzyczny ~120 MB)
# Pobierany raz, cache'owany w ~/.cache/fastembed
# ---------------------------------------------------------------------------
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def filter_offers_by_query(offers, query):
    query = query.lower()

    filtered = []

    for offer in offers:
        title = offer.get("title", "").lower()
        description = offer.get("description", "").lower()

        text = f"{title} {description}"

        keywords = extract_keywords(text)

        if query in keywords:
            filtered.append(offer)

    return filtered


def load_model() -> TextEmbedding:
    print(f"Ładowanie modelu embeddingów: {MODEL_NAME}...")
    return TextEmbedding(model_name=MODEL_NAME)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def build_doc(offer) -> str:
    """Łączy tytuł (x2) i opis oferty w jeden tekst wejściowy dla modelu."""
    title = offer.get("title") or ""
    desc  = offer.get("description") or ""
    if desc in ("N/A", "None"):
        desc = ""
    return f"{title}. {title}. {desc}".strip()


def embed(model: TextEmbedding, texts: list) -> np.ndarray:
    """Zwraca macierz embeddingów (n_texts, 384) jako ndarray."""
    # fastembed.embed() zwraca generator – konwertujemy do tablicy
    return np.array(list(model.embed(texts)), dtype=np.float32)


# ---------------------------------------------------------------------------
# Zapis ofert + ich embeddingów do bazy
# ---------------------------------------------------------------------------
def process_and_save_offers(offers: list, db: OfferDatabase, model: TextEmbedding):
    """
    Dla każdej oferty:
    1. Buduje tekst (tytuł + opis)
    2. Oblicza embedding modelem ONNX (fastembed)
    3. Zapisuje ofertę + wektor do bazy

    Embeddingi są NIEZALEŻNE od siebie – nowe oferty można dodawać
    bez przeliczania istniejących wektorów.
    """
    for offer in offers:
        title = offer.get("title", "Brak tytułu")
        doc   = build_doc(offer)

        if not doc:
            print(f" -> [BRAK TEKSTU] Zapis z wektorem zerowym: {title}")
            vector = np.zeros(384, dtype=np.float32)
        else:
            vector = embed(model, [doc])[0]  # ndarray (384,)
            print(f" -> Embedding + zapis: {title}")

        db.insert_offer(offer, vector=vector)


import re

def extract_keywords(text: str) -> set:
    """Prosta ekstrakcja potencjalnych słów kluczowych IT (alfanumeryczne, małe litery)."""
    words = re.findall(r'\b[a-zA-Z0-9+#]+\b', text.lower())
    stopwords = {
        "i", "w", "z", "na", "do", "to", "się", "że", "nie", "a", "jak", "o", "przez", 
        "po", "za", "tak", "jest", "są", "ze", "co", "ale", "dla", "przy", "od", "ich", 
        "lub", "oraz", "jako", "może", "więcej", "być", "tej", "który", "która", "które", 
        "możesz", "naszej", "naszego", "nasze", "twój", "jego", "jej", "np", "znam", 
        "mam", "poziomie", "podstawy", "podstawową", "znajomość", "interesuję", "pracowałem"
    }
    return {w for w in words if len(w) > 2 and w not in stopwords}


# ---------------------------------------------------------------------------
# Matchmaking CV ↔ oferty
# ---------------------------------------------------------------------------
def match_cv_to_offers(
    cv_text: str,
    model: TextEmbedding,
    all_offers: list,
    top_n: int = 10,
):
    """
    Porównuje CV z ofertami za pomocą HYBRID SEARCH:
    1. Semantic Similarity (Wektory z modelu) - 70% wagi
    2. Keyword Overlap (Pokrycie słów kluczowych) - 30% wagi
    """
    cv_vec = embed(model, [cv_text])  # (1, 384)
    cv_keywords = extract_skills(cv_text)

    offer_vecs   = []
    valid_offers = []
    for offer in all_offers:
        raw = offer.get("vector")
        if raw is None:
            continue
        arr = raw if isinstance(raw, np.ndarray) else np.frombuffer(raw, dtype=np.float32)
        offer_vecs.append(arr)
        valid_offers.append(offer)

    if not offer_vecs:
        print("Brak wektorów w bazie. Uruchom najpierw scraping.")
        return

    offer_matrix = np.vstack(offer_vecs)                     # (n_offers, 384)
    similarities = sklearn_cosine(cv_vec, offer_matrix)[0]   # (n_offers,)

    results = []
    for i, o in enumerate(valid_offers):
        # Ekstrakcja słów kluczowych z oferty
        offer_text = (o.get("title", "") + " " + (o.get("description", "") or "")).lower()
        offer_keywords = extract_skills(offer_text)
        
        # Obliczanie pokrycia słów kluczowych (Keyword Score)
        overlap = cv_keywords.intersection(offer_keywords)
        keyword_score = len(overlap) / max(len(offer_keywords), 1)
        
        raw_semantic_score = float(similarities[i])
        semantic_score = (raw_semantic_score - 0.25) / (0.65 - 0.25)
        semantic_score = max(0.0, min(1.0, semantic_score))
        
        # Hybrid Score: 70% Semantic + 30% Keywords
        # Modele embeddingów często mają bazowe podobieństwo ~0.3-0.5, więc keyword_score robi dużą różnicę
        hybrid_score = (semantic_score * 0.7) + (keyword_score * 0.3)
        
        missing_keywords = sorted(list(offer_keywords - cv_keywords))
        matched_keywords = sorted(list(cv_keywords.intersection(offer_keywords)))

        results.append({
            "id": o.get("id"),
            "title": o.get("title", "Brak tytułu"),
            "match": hybrid_score * 100,
            "semantic_score": semantic_score * 100,
            "keyword_score": keyword_score * 100,
            "matched_keywords": matched_keywords[:15],
            "missing_keywords": missing_keywords[:20],
            "url": o.get("url"),
            "location": o.get("location"),
            "source": o.get("source", "Unknown"),
        })

    results.sort(key=lambda x: x["match"], reverse=True)

    print(f"\nTop {min(top_n, len(results))} najlepiej dopasowanych ofert (Hybrid Score):\n")
    print(f"{'Rank':<5} {'ID':<30} {'Match %':<10} {'Tytuł'}")
    print("-" * 90)
    for i, r in enumerate(results[:top_n], start=1):
        print(f"{i:<5} {str(r['id']):<30} {r['match']:<10.2f} {str(r['title'])[:45]}")

    advisor_result = generate_cv_suggestions(results, min_score=50.0)

    print("\n" + "=" * 60)
    print("ANALIZA CV")
    print("=" * 60)
    print(advisor_result["message"])

    if advisor_result["status"] == "weak_cv":
        print("\nSugestie poprawy CV:")
        for suggestion in advisor_result["suggestions"]:
            print(f"- {suggestion}")

    return {
        "results": results[:top_n],
        "advisor": advisor_result,
    }
# ---------------------------------------------------------------------------
# Główna funkcja
# ---------------------------------------------------------------------------
def run_pipeline(city: str = "Krakow", query: str = "", source: str = "all", cv_text: str | None = None):
    # Ładuj model raz – reużywany do zapisu ofert i matchmakingu
    model = load_model()

    print(f"\nPobieranie ofert pracy... Zapytanie: '{query}', Lokacja: '{city}'")

    all_scraped_offers = []

    if source in ("olx", "all"):
        print("\n[OLX] Uruchamianie scrapera OLX...")
        olx_offers = get_jobs_olx(city, query, limit=5)
        olx_offers = filter_offers_by_query(olx_offers, query)
        print(f"Pobrano {len(olx_offers)} ofert z OLX.")
        all_scraped_offers.extend(olx_offers)

    if source in ("pracuj", "all"):
        print("\n[Pracuj.pl] Uruchamianie scrapera Pracuj.pl...")
        pracuj_offers = get_jobs_pracuj(city, query, limit=5)
        pracuj_offers = filter_offers_by_query(pracuj_offers, query)
        print(f"Pobrano {len(pracuj_offers)} ofert z Pracuj.pl.")
        all_scraped_offers.extend(pracuj_offers)

    if source in ("protocol", "all"):
        print("\n[The Protocol] Uruchamianie scrapera The Protocol...")
        protocol_offers = get_jobs_protocol(query, limit=5)
        protocol_offers = filter_offers_by_query(protocol_offers, query)
        print(f"Pobrano {len(protocol_offers)} ofert z The Protocol.")
        all_scraped_offers.extend(protocol_offers)

    # --- 3. Embedding + zapis do bazy ---
    print("\nObliczanie embeddingów i zapis do bazy SQLite (offers.db)...")

    with OfferDatabase() as db:

        db.delete_all_offers()

        if all_scraped_offers:

            print(f"\nZapisywanie {len(all_scraped_offers)} ofert do bazy...")

            process_and_save_offers(
                all_scraped_offers,
                db,
                model
            )

        else:
            print("Nie pobrano żadnych ofert.")

    print("\nZakończono zapisywanie ofert z embeddingami!")

    # --- 4. Matchmaking: CV vs oferty ---
    print("\n" + "=" * 60)
    print("REKOMENDACJE: Dopasowanie CV do ofert (Semantic Embeddings)")
    print("=" * 60)

    if cv_text is None:
        cv_path = "sample_cv.txt"

        if not os.path.exists(cv_path):
            print(f"Nie znaleziono pliku CV: {cv_path}")
            return

        with open(cv_path, "r", encoding="utf-8") as f:
            cv_text = f.read()

    print("Ładowanie ofert z bazy...")
    with OfferDatabase() as db:
        all_offers = db.get_all_offers()

    if not all_offers:
        print("Baza danych jest pusta. Najpierw pobierz oferty.")
        return

    print("Obliczanie podobieństwa CV ↔ oferty...")
    return match_cv_to_offers(cv_text, model, all_offers)


if __name__ == "__main__":
    cmd_city = sys.argv[1] if len(sys.argv) > 1 else "Krakow"
    cmd_query = sys.argv[2] if len(sys.argv) > 2 else ""
    cmd_source = sys.argv[3] if len(sys.argv) > 3 else "all"

    run_pipeline(city=cmd_city, query=cmd_query, source=cmd_source)

    