---

name: skill-embedding-patterns
description: Produkcyjne wzorce projektowe dotyczące generowania embeddingów, wyszukiwania wektorowego i miar podobieństwa.
version: 1.0.0
phase: 11
lesson: 4
tags: [embeddings, vectors, similarity, search, chunking, quantization]

---

# Wzorce projektowe dla embeddingów

Każdy proces osadzania tekstu (embeddingu) realizuje poniższy kontrakt programistyczny:

```
text -> embed(text) -> vector (float array)
similarity(vector_a, vector_b) -> score (float)
```

Wybór modelu embeddingów oraz metryki podobieństwa to dwie najważniejsze decyzje projektowe. Cała reszta to warstwa techniczna (hydraulika systemowa).

## Kiedy stosować embeddingi

- Wyszukiwanie semantyczne w dokumentach (znajdowanie znaczenia i kontekstu, a nie tylko dopasowań słów kluczowych).
- Klasteryzacja / grupowanie podobnych elementów (np. zgłoszenia do pomocy technicznej, recenzje produktów, raporty o błędach).
- Klasyfikacja przy użyciu metody najbliższych sąsiadów (k-NN) – etykietowanie nowych elementów na podstawie podobieństwa do znanych przykładów.
- Systemy rekomendacji (znajdowanie treści lub produktów podobnych do preferowanych przez użytkownika).
- Deduplikacja danych (wyszukiwanie zduplikowanych lub niemal zidentyfikowanych treści przy użyciu progu podobieństwa).

## Kiedy NIE stosować embeddingów

- Dokładne dopasowanie słów kluczowych (w tym celu stosuj klasyczne wyszukiwanie pełnotekstowe, np. BM25).
- Zapytania strukturyzowane i filtrowanie (w tym celu stosuj zapytania SQL lub filtry relacyjne).
- Małe zbiory danych, gdzie ręczne skatalogowanie jest szybsze i tańsze (<100 elementów).
- Zadania, w których wyjaśnialność (explainability) decyzji ma większe znaczenie niż sama dokładność (embeddingi są strukturami nieprzezroczystymi / czarną skrzynką).

## Wybór modelu

Wybieraj w oparciu o specyficzne ograniczenia projektu:

- **Gdy potrzebujesz zewnętrznego API o najlepszym stosunku ceny do jakości**: OpenAI `text-embedding-3-small` (1536d, $0.02/1M tokenów).
- **Gdy wymagana jest maksymalna dokładność**: `voyage-3` (1024d, $0.06/1M tokenów, najwyższa pozycja w rankingu MTEB).
- **Gdy wymagane jest przetwarzanie lokalne/prywatne**: `BGE-M3` (1024d, bezpłatny, wielojęzyczny, zalecane GPU).
- **Gdy potrzebujesz szybkiego lokalnego prototypowania**: `all-MiniLM-L6-v2` (384d, bezpłatny, działa na CPU).
- **Gdy wymagane jest silne wsparcie wielojęzyczne**: `Cohere embed-v3` (1024d) lub `BGE-M3` (oba modele świetnie radzą sobie z wieloma językami).

Zasada: Nigdy nie mieszaj różnych modeli embeddingów na etapach indeksowania i wyszukiwania. Wektory wygenerowane przez różne modele należą do niekompatybilnych przestrzeni wektorowych.

## Zasady segmentacji (Chunking)

1. Celuj w 256–512 tokenów na segment z nakładaniem się (overlap) wynoszącym 50 tokenów.
2. Nigdy nie dziel tekstu w środku zdania, o ile to możliwe.
3. Dołączaj metadane (plik źródłowy, tytuł sekcji, pozycja) do każdego segmentu.
4. Dla dokumentów strukturyzowanych (Markdown, HTML) w pierwszej kolejności wykonuj podział na granicach nagłówków.
5. Testuj jakość segmentacji poprzez wyszukiwanie znanych odpowiedzi i weryfikację trafności wyników (retrieval).

## Wybór metryki podobieństwa

- **Podobieństwo cosinusowe (Cosine similarity)**: wybór domyślny, dobrze obsługuje teksty o zmiennej długości, znormalizowane.
- **Iloczyn skalarny (Dot product)**: stosuj, gdy wektory są już znormalizowane jednostkowo (np. w modelach OpenAI); metoda ta jest nieco szybsza obliczeniowo.
- **Odległość euklidesowa (L2 / Euclidean distance)**: stosuj w zadaniach klasteryzacji, gdy istotne jest bezwzględne położenie w przestrzeni.

Wszystkie trzy metryki dają identyczny ranking wyników, jeśli wektory są znormalizowane. Wybór ma znaczenie wyłącznie dla wektorów nieznormalizowanych.

## Optymalizacja przechowywania danych

Trzy poziomy kompresji (można je łączyć):

1. **Skracanie metodą Matryoshki (Matryoshka truncation)**: redukcja wymiarowości (np. 1536 -> 256 daje 6-krotną oszczędność pamięci przy utracie dokładności o zaledwie 3–5%).
2. **Kwantyzacja do Float16**: zmniejszenie rozmiaru pamięci o połowę dla każdego wymiaru (2-krotna oszczędność, spadek dokładności < 1%).
3. **Kwantyzacja binarna (Binary quantization)**: redukcja do 1 bitu na wymiar (32-krotna oszczędność pamięci, utrata dokładności o 5–10%; zalecane stosowanie w połączeniu z ponownym ocenianiem/rescoringiem).

Produkcyjny wzorzec projektowy: wykonaj wyszukiwanie przybliżone na skwantyzowanym binarnie całym korpusu, wybierz top 1000 kandydatów, a następnie dokonaj dokładnego przeliczenia na oryginalnych wektorach Float32.

## Wyszukiwanie dwuetapowe (Retrieve and Rerank)

Dwuetapowy potok przetwarzania (pipeline) zapewniający najwyższą precyzję:

1. **Szybkie pobranie (Retrieve)**: Bi-enkoder wyodrębnia top 100 kandydatów (operacja szybka, bazuje na wstępnie wygenerowanych embeddingach).
2. **Ponowne ocenianie (Rerank)**: Cross-enkoder ocenia i sortuje top 10 wyników (operacja wolniejsza, analizuje pełną relację między parą zapytanie-dokument).

Podejście to poprawia wskaźniki trafności (precision/recall) o 10–15% w porównaniu do wyszukiwania jednoetapowego. Stosuj wszędzie tam, gdzie precyzja odpowiedzi ma priorytet nad opóźnieniami (latency).

## Typowe błędy

- Używanie różnych modeli embeddingów na etapach indeksowania i wyszukiwania.
- Generowanie embeddingów dla całych, długich dokumentów zamiast ich segmentacji (wektor staje się zbyt ogólny i traci kluczowe szczegóły).
- Brak normalizacji wektorów przed obliczeniem podobieństwa cosinusowego (większość modeli zwraca wektory już znormalizowane, ale warto to zweryfikować).
- Pomijanie nakładania się segmentów (zdania przecięte na granicy podziału tracą swój kontekst semantyczny).
- Zapisywanie samych wektorów bez powiązania z tekstem źródłowym (do ostatecznego wyświetlenia wyniku potrzebujesz tekstu).
- Zaniechanie ponownego generowania wektorów po zmianie modelu (stare wektory są bezużyteczne i niekompatybilne).
- Dobieranie wymiarowości wyłącznie na podstawie dokładności (koszt przechowywania i opóźnienia rosną liniowo wraz z liczbą wymiarów).

## Debugowanie wyszukiwania wektorowego

Jeśli jakość wyszukiwania jest niesatysfakcjonująca:

1. Upewnij się, czy wektor zapytania nie składa się z samych zer (puste ciągi znaków lub znaki niedrukowalne mogą generować wektory zerowe).
2. Ręcznie zbadaj wartość podobieństwa (similarity score) dla dokumentu, który na pewno jest powiązany z zapytaniem.
3. Przetestuj przeformułowanie zapytania, dopasowując je do słownictwa występującego w dokumentach bazowych.
4. Zweryfikuj granice podziału segmentów (chunks), upewniając się, że kluczowe informacje nie zostały nienaturalnie rozdzielone.
5. Porównaj wyniki top-k uzyskane za pomocą różnych metryk podobieństwa (cosinus, iloczyn skalarny, L2), aby wykluczyć błędy związane z brakiem normalizacji.
6. Wykonaj test jednostkowy z zapytaniem będącym dokładną kopią fragmentu dokumentu bazowego, aby potwierdzić techniczne działanie całego potoku.

## Parametry produkcyjne

- **Rozmiar segmentu**: 256–512 tokenów.
- **Nakładanie się segmentów (overlap)**: 50 tokenów (ok. 10–20% rozmiaru segmentu).
- **Liczba pobieranych elementów (Top-k)**: 5–10 w przypadku bezpośredniego użycia, 50–100 na potrzeby rerankingu.
- **Próg podobieństwa (Similarity threshold)**: 0.7+ dla podobieństwa cosinusowego (wyniki poniżej tej wartości są zazwyczaj nieistotne).
- **Przetwarzanie wsadowe (Batching)**: wysyłaj 100–500 fragmentów tekstu w jednym wywołaniu API w celu maksymalizacji przepustowości.
- **Aktualizacja indeksu (Re-indexing)**: wygeneruj wektory ponownie, gdy zmieni się model bazowy lub dokumenty źródłowe zostaną znacząco zmodyfikowane.
