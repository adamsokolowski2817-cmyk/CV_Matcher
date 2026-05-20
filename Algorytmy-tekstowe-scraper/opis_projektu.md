# Opis Projektu: Agregator i Wektoryzator Ofert Pracy (NLP)

## 1. Cel i ogólne działanie projektu
Projekt to aplikacja analityczna napisana w języku Python, służąca do automatycznego pobierania (scrapowania) ofert pracy z wiodących polskich portali ogłoszeniowych (OLX oraz Pracuj.pl) i ich zaawansowanego przetwarzania. Aplikacja nie tylko zbiera ustrukturyzowane metadane z ogłoszeń (takie jak tytuł, proponowane wynagrodzenie, lokalizacja, rodzaj umowy czy wymiar czasu pracy), ale wchodzi głębiej: nawiguje pod unikalne adresy URL każdej oferty i pobiera pełne opisy stanowisk (zakres obowiązków i wymagań). 

Pobrane dane tekstowe są następnie poddawane analizie i przekształcane na wielowymiarowe wektory (tzw. _embeddings_) przy użyciu biblioteki przetwarzania języka naturalnego (NLP) **spaCy**. Całość zarchiwizowana jest w stworzonej, natywnej bazie danych opartej na silniku SQLite z dostosowanym formatem binarnym pozwalającym na przechowywanie tablic numerycznych biblioteki NumPy. 

Zebranie danych i ich wektoryzacja stanowią fundament do budowy systemów rekomendacyjnych (np. dopasowanie profilu z pliku `sample_cv.txt` do wektorów ofert korzystając z algorytmów podobieństwa) i klasyfikacyjnych.

## 2. Architektura i Przepływ Pracy
Architektura aplikacji składa się z warstwy akwizycji danych (skrypty scrapujące), warstwy transformacji i wektoryzacji (NLP) oraz warstwy utrwalania (Baza Danych). 
Przepływ pracy (Work-flow) sterowany jest przez plik `main.py`:
1. Uruchomienie z parametrami wyszukiwania (domyślnie stanowisko puste, a miasto to "Krakow").
2. Aktywacja scrapera dla portalu **OLX** w poszukiwaniu ofert pasujących do parametrów.
3. Aktywacja scrapera dla portalu **Pracuj.pl** dla analogicznego zapytania.
4. Pobranie z każdego z portali szczegółowych opisów do znalezionych kart ofert.
5. Inicjalizacja modelu językowego i przekształcenie tekstów na wektory w sposób zautomatyzowany.
6. Przechowanie zgromadzonych wyników w tabelach bazy danych SQLite.
7. Wczytanie profilu kandydata (np. z pliku `sample_cv.txt`) i wektoryzacja jego treści.
8. Porównanie wektora CV ze wszystkimi ofertami w bazie danych, obliczenie procentowego podobieństwa (dopasowania) i wyświetlenie w konsoli najlepszych wyników (tytuł, ID oraz wskaźnik %).

## 3. Szczegóły techniczne i struktura kodu

### A. Główny moduł wykonawczy (`main.py`)
Centralny skrypt orkiestrujący całą operację.
- Przyjmuje z linii poleceń opcjonalne argumenty do zdefiniowania lokalizacji wyszukiwania i nazwy stanowiska / słowa kluczowego (np. `python main.py "Krakow" "Python"`).
- Inicjalizuje model **spaCy** (`en_core_web_sm`).
- Przekazuje pobrane słowniki ogłoszeń wraz z instancją połączenia bazy danych i modelem językowym do funkcji `process_and_save_offers()`, która odpowiada za obliczenie wektora właściwości `.vector` obiektyzowanego tekstu za pośrednictwem funkcji modelującej (`nlp()`) i wpisanie go poprzez interfejs bazy.
- Zapewnia silnik **Rekomendacji i Dopasowania (Matchmaking)**: Wczytuje i wektoryzuje aplikację/życiorys kandydata (np. `sample_cv.txt`), a następnie oblicza odległość i podobieństwo tego profilu do każdej ze zarchiwizowanych w bazie danych ofert pracy.
- Zwraca w konsoli ranking (wynik wprost na standardowe wyjście) wyłaniający najbardziej pasujące ogłoszenia, prezentując jasno ich: **nazwę/tytuł**, **ID z bazy danych** oraz wyliczony **procentowy współczynnik dopasowania (Match %)**.

### B. Warstwa persystencji bazy danych (`database.py`)
Skrypt odpowiedzialny za przechowywanie danych (Data Access Layer) z unikalnym podejściem do zapisywania tablic analitycznych.
- **Custom Adapters/Converters SQLite:** Ze względu na to, że relacyjna baza danych SQLite natywnie nie wspiera obsługi struktur macierzowych ani tablic `numpy.ndarray`, aplikacja definiuje `adapt_array` oraz `convert_array`. Funkcje te z wykorzystaniem pamięci buforowej w RAM (`io.BytesIO`) pozwalają na binarny zapis i odczyt z zastosowaniem funkcji `np.save()` i `np.load()`.
- **Klasa OfferDatabase:** Konstruktor przyjmuje opcjonalny argument na ścieżkę do `offers.db` i uruchamia silnik z modyfikatorem zachowania `detect_types=sqlite3.PARSE_DECLTYPES`, zmuszającym silnik do wykrywania naszego własnego pseudo-typu `ARRAY`. Row factory zmieniono na `sqlite3.Row`, przez co wiersze wyników symulują właściwości słowników, na jakich operują skrypty. Menedżer klas wspiera interfejs _Context Managera_ (metody `__enter__` i `__exit__`), zabezpieczając bazę przez wyciekami zasobów i blokadami I/O (Database locking).

### C. Web Scraper - OLX (`scraper.py`)
Moduł realizujący wyszukiwanie informacji ze struktury DOM (Document Object Model) portalu ogłoszeniowego OLX. W tym celu użyto podstawowej biblioteki w ekosystemie: `requests` w kooperacji z biblioteką parsującą tagi – `BeautifulSoup`.
- Transformacja i sanitacja URL z budową specjalistycznych list parametrów i filtrów typowych dla standardów wyszukiwarki portalu.
- Parser oparty jest o wyszukiwanie konkretnych atrybutów, ze względu na generowane dynamicznie tagi klas, m.in. używając `data-testid='listing-grid'` oraz `data-cy='l-card'`.
- Ekstrakcja kluczowych własności ogłoszenia poprzez rekursywne iterowanie i tworzenie logiki opartej o detekcję słów kluczowych uwarunkowanych polskim rynkiem pracy (np. "zł" oznacza pole *Wynagrodzenie*; "B2B" / "Umowa" - *Rodzaj Kontraktu*; "etat" / "Praca" - *Wymiar Pracy*).
- System w locie podnosi proces dla każdej oferty wyciągając pełny opis (uruchomienie `fetch_offer()`), filtrując zbędne elementy DOM, zatrzymując się na poszukiwanym tagu `<h2>`.

### D. Web Scraper - Pracuj.pl (`scraper_pracuj.py`)
Moduł dedykowany do największego w Polsce portalu Pracuj.pl.
- Zapytania na Pracuj.pl wymusiły zmianę metodyki łączenia – aplikacja wykorzystuje wysoce wyspecjalizowaną bibliotekę `curl_cffi` imitującą podpisy przeglądarkowe (TLS/JA3 signatures) na wzór przeglądarki Chromium (`impersonate="chrome"`). Dzięki temu scraper sprawnie radzi sobie z firewallami aplikacyjnymi nałożonymi przez oprogramowanie Cloudflare chroniącymi platformę Pracuj.pl.
- Struktura nawigacji URL wykorzystuje kodowanie na podstawie znaczników wpisywanych w ścieżkę adresu, np. `/{query};kw/{city};wp`.
- Skrypt poszukuje listingów wykorzystując ustrukturyzowane wartości atrybutu `data-test` np. `section-offers` z fallbackiem na detekcję po klasie CSS i atrybutach kart `default-offer`. Z racji niestabilności drzewa w poszukiwaniu opisu stanowiska analizowane są tagi kontenerów np. `section-responsibilities`.

### E. Wykorzystywane pliki pomocnicze
- **`sample_cv.txt`** oraz **`offers.json`**: Próbki systemowe, pliki używane najpewniej do prototypowania lub operacji ewaluacji i dopasowywania (np. modelowego sprawdzania zgodności życiorysów ze stanowiskami dla modułów klasyfikujących).

## 4. Technologie i Wymagania
Aplikacja została zaprogramowana w języku Python. Najistotniejsze pakiety, których wersje i instrukcje środowiskowe skrystalizowano w pliku `requirements.txt`:
* **Ekstrakcja i parsowanie WWW:** `beautifulsoup4`, `requests`, `curl_cffi` (omijanie Cloudflare Anti-Bot)
* **Silnik językowy (NLP):** `spacy` (Model: `en_core_web_sm`)
* **Obliczenia naukowe i typy danych:** `numpy`, (potencjalnie `scikit-learn` i `scipy` uwzględnione w zależnościach pod rekomendacje analityczne)
* **Obsługa danych pomocniczych PDF/JSON:** Pakiet analityczny `PyMuPDF` oraz pakiety standardowe Pythona do wczytywania JSON-ów.

Projekt stanowi gotowe narzędzie bazowe umożliwiające rozbudowę pipeline'u uczenia maszynowego poprzez zebrany dataset i unikalną bazę danych wyposażoną natywnie we wsparcie do wektorów.
