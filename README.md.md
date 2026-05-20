# CV Matcher AI — Inteligentna analiza dopasowania CV do ofert pracy

## Opis projektu

CV Matcher AI to aplikacja webowa służąca do automatycznej analizy dopasowania CV do aktualnych ofert pracy IT.

System pobiera oferty pracy z wielu serwisów internetowych, analizuje ich treść z wykorzystaniem embeddingów semantycznych oraz porównuje je z przesłanym przez użytkownika CV.

Projekt został wykonany w ramach przedmiotu:

```text
Algorytmy Tekstowe
```

---

# Główne funkcjonalności

- scrapowanie ofert pracy z wielu źródeł,
- analiza semantyczna ofert i CV,
- obliczanie procentowego dopasowania,
- wykrywanie brakujących technologii,
- generowanie sugestii ulepszenia CV,
- upload CV w formacie PDF,
- ranking ofert pracy,
- statystyki i wykresy technologii,
- nowoczesny frontend React,
- REST API oparte o FastAPI,
- cache wyników,
- analiza embeddingów semantycznych.

---

# Zastosowane technologie

## Backend

- Python 3
- FastAPI
- SQLite
- NumPy
- requests
- BeautifulSoup4
- curl_cffi
- PyMuPDF
- sentence-transformers
- scikit-learn

## Frontend

- React
- Vite
- TailwindCSS
- Axios
- Recharts

## AI / NLP

- Embeddingi semantyczne
- Sentence Transformers
- Cosine Similarity
- Keyword Matching
- Analiza technologii IT

---

# Architektura systemu

```text
PDF CV
   ↓
Ekstrakcja tekstu
   ↓
Scrapowanie ofert pracy
   ↓
Embeddingi semantyczne
   ↓
Analiza podobieństwa
   ↓
Ranking ofert
   ↓
Sugestie ulepszenia CV
   ↓
Frontend React
```

---

# Źródła ofert pracy

Projekt obsługuje:

- OLX
- Pracuj.pl
- The Protocol

Każde źródło posiada dedykowany scraper.

---

# Algorytm dopasowania

System wykorzystuje hybrydowe podejście:

## 1. Semantic Matching

Treść CV i ofert pracy zamieniana jest na embeddingi semantyczne.

Następnie obliczana jest miara podobieństwa:

- cosine similarity,
- analiza semantyczna kontekstu,
- embeddingi sentence-transformers.

---

## 2. Keyword Matching

System wykrywa technologie występujące w:

- CV,
- ofertach pracy.

Przykładowe technologie:

- Python
- SQL
- Docker
- React
- AWS
- Linux
- FastAPI
- Django
- Machine Learning

---

## 3. Hybrid Score

Końcowy wynik dopasowania:

```text
Hybrid Score =
70% semantic similarity
+
30% keyword overlap
```

---

# Funkcje AI

## Sugestie ulepszenia CV

Jeżeli system nie znajdzie ofert o odpowiednim dopasowaniu, generowane są sugestie:

- brakujące technologie,
- najczęściej pojawiające się wymagania,
- rekomendacje rozwoju CV.

---

# Upload PDF CV

Użytkownik może przesłać własne CV w formacie PDF.

System:
- odczytuje tekst,
- analizuje treść,
- porównuje ją z aktualnymi ofertami pracy.

---

# Interfejs użytkownika

Frontend został wykonany w React + TailwindCSS.

Aplikacja zawiera:

- dashboard,
- ranking ofert,
- statystyki,
- wykresy technologii,
- modal szczegółów oferty,
- loading/progress system.

---

# Cache ofert

System wykorzystuje prosty cache backendowy:
- ogranicza ponowne scrapowanie,
- przyspiesza kolejne zapytania,
- zmniejsza obciążenie scraperów.

---

# Statystyki i wykresy

Frontend generuje wykresy:
- najczęściej brakujących technologii,
- dopasowania ofert,
- trendów technologicznych.

---

# Struktura projektu

```text
Algorytmy-tekstowe-scraper/
│
├── api.py
├── main.py
├── database.py
├── skills.py
├── cv_reader.py
├── cv_advisor.py
│
├── scraper.py
├── scraper_pracuj.py
├── scraper_protocol.py
│
├── offers.db
├── sample_cv.txt
└── requirements.txt


Algorytmy-tekstowe-web/
│
├── src/
│   ├── components/
│   │   ├── Navbar.jsx
│   │   ├── SearchPanel.jsx
│   │   ├── OfferCard.jsx
│   │   ├── OfferModal.jsx
│   │   ├── StatsCards.jsx
│   │   └── SkillStats.jsx
│   │
│   ├── App.jsx
│   └── main.jsx
│
├── package.json
└── vite.config.js
```

---

# Miejsce na screenshoty

## Dashboard

![Dashboard](screenshots/dashboard.png)

---

## Ranking ofert

![Offers](screenshots/offers.png)

---

## Analiza CV

![Advisor](screenshots/advisor.png)

---

## Szczegóły oferty

![Modal](screenshots/modal.png)

---

## Wykres technologii

![Chart](screenshots/chart.png)

---

# Instalacja projektu

# 1. Klonowanie repozytorium

```bash
git clone <LINK_DO_REPO>
```

---

# 2. Backend — instalacja

## Przejście do folderu backendu

```bash
cd Algorytmy-tekstowe-scraper
```

---

## Utworzenie virtualenv

### Linux / WSL

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## Instalacja zależności

```bash
pip install -r requirements.txt
```

---

## Dodatkowe zależności backendu

```bash
pip install fastapi uvicorn python-multipart
```

---

# 3. Frontend — instalacja

## Przejście do folderu frontendu

```bash
cd ../Algorytmy-tekstowe-web
```

---

## Instalacja zależności

```bash
npm install
```

---

## Dodatkowe biblioteki

```bash
npm install axios recharts
```

---

# Uruchamianie projektu

# Backend

W folderze:

```text
Algorytmy-tekstowe-scraper
```

uruchom:

```bash
uvicorn api:app --reload
```

Backend będzie dostępny pod:

```text
http://127.0.0.1:8000
```

---

# Dokumentacja API

```text
http://127.0.0.1:8000/docs
```

---

# Frontend

W folderze:

```text
Algorytmy-tekstowe-web
```

uruchom:

```bash
npm run dev
```

Frontend będzie dostępny pod:

```text
http://localhost:5173
```

---

# Uruchamianie projektu w WSL

## Backend

```bash
cd /mnt/c/Users/<USER>/Desktop/algorytmy\ tekstowe/Algorytmy-tekstowe-scraper

source venv/bin/activate

uvicorn api:app --reload
```

---

## Frontend

```bash
cd /mnt/c/Users/<USER>/Desktop/algorytmy\ tekstowe/Algorytmy-tekstowe-web

npm run dev
```

---

# Przykładowy workflow działania systemu

1. Użytkownik przesyła CV PDF.
2. System pobiera aktualne oferty pracy.
3. Obliczane są embeddingi semantyczne.
4. Generowany jest ranking dopasowania.
5. System wyświetla:
   - najlepsze oferty,
   - brakujące technologie,
   - sugestie ulepszenia CV.

---

# Możliwe dalsze rozszerzenia

- asynchroniczne scrapowanie,
- deployment online,
- Docker,
- vector database,
- autoryzacja użytkowników,
- analiza wielu CV,
- rekomendacje ścieżki kariery,
- analiza trendów rynku pracy.

---

# Autorzy projektu

Projekt wykonany w ramach przedmiotu:

```text
Algorytmy Tekstowe
```

Autorzy:
- [IMIĘ I NAZWISKO]
- [IMIĘ I NAZWISKO]
- [IMIĘ I NAZWISKO]
- Adam Sokołowski

