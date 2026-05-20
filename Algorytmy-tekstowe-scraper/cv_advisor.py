from collections import Counter


def generate_cv_suggestions(results, min_score=50.0, max_suggestions=8):
    """
    Jeżeli CV słabo pasuje do rynku, generuje sugestie na podstawie:
    - brakujących słów kluczowych,
    - najczęściej powtarzających się technologii w ofertach,
    - najlepszych, ale nadal słabych dopasowań.
    """

    good_matches = [r for r in results if r["match"] >= min_score]

    if good_matches:
        return {
            "status": "ok",
            "message": f"Znaleziono {len(good_matches)} ofert z dopasowaniem >= {min_score}%.",
            "suggestions": [],
        }

    missing_counter = Counter()

    for result in results:
        for keyword in result.get("missing_keywords", []):
            missing_counter[keyword] += 1

    most_missing = missing_counter.most_common(max_suggestions)

    suggestions = []

    for keyword, count in most_missing:
        suggestions.append(
            f"Dodaj lub rozwiń w CV: {keyword} — pojawia się w {count} analizowanych ofertach."
        )

    if not suggestions:
        suggestions.append(
            "CV ma niskie dopasowanie, ale nie udało się jednoznacznie wykryć brakujących technologii. "
            "Warto dopisać konkretne projekty, technologie, narzędzia i poziom doświadczenia."
        )

    return {
        "status": "weak_cv",
        "message": f"Nie znaleziono ofert z dopasowaniem >= {min_score}%.",
        "suggestions": suggestions,
    }