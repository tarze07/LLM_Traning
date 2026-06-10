---

name: skill-embedding-patterns
description: Wzorce produkcyjne dotyczące osadzania, wyszukiwania wektorów i podobieństwa
version: 1.0.0
phase: 11
lesson: 4
tags: [embeddings, vectors, similarity, search, chunking, quantization]

---

# Osadzanie wzorów

Każdy proces osadzania jest zgodny z tą umową:

```
text -> embed(text) -> vector (float array)
similarity(vector_a, vector_b) -> score (float)
```

Model osadzania i metryka podobieństwa to jedyne dwie decyzje, które mają znaczenie. Cała reszta to hydraulika.

## Kiedy używać osadzania

- Wyszukiwanie semantyczne w dokumentach (znajdź znaczenie, a nie słowa kluczowe)
- Grupowanie podobnych elementów (zgłoszenia do pomocy technicznej, recenzje produktów, raporty o błędach)
- Klasyfikacja według najbliższych sąsiadów (oznacz nowe elementy według podobieństwa do oznaczonych przykładów)
- Systemy rekomendacji (znajdź przedmioty podobne do tego, co lubił użytkownik)
- Deduplikacja (znajdź prawie zduplikowaną treść za pomocą progu podobieństwa)

## Kiedy NIE używać osadzania

- Dokładne dopasowanie słów kluczowych (użyj wyszukiwania pełnotekstowego)
- Zapytania strukturalne (użyj SQL, filtrów)
- Małe zbiory danych, w których ręczne etykietowanie jest szybsze (<100 items)
- Tasks where explainability matters more than accuracy (embeddings are opaque)

## Model selection

Pick based on your constraints:

- **Need an API, best value**: OpenAI text-embedding-3-small (1536d, $0.02/1M tokens)
- **Need maximum accuracy**: Voyage-3 (1024d, $0.06/1M tokens, highest MTEB)
- **Need local/private**: BGE-M3 (1024d, free, multilingual, GPU recommended)
- **Need fast local prototyping**: all-MiniLM-L6-v2 (384d, free, runs on CPU)
- **Need multilingual**: Cohere embed-v3 (1024d) or BGE-M3 (both strong multilingual)

Rule: never mix embedding models between indexing and querying. Vectors from different models live in incompatible spaces.

## Chunking rules

1. Target 256-512 tokens per chunk with 50-token overlap
2. Never split mid-sentence if you can avoid it
3. Include metadata (source file, section title, position) with every chunk
4. For structured docs (Markdown, HTML), split at heading boundaries first
5. Test chunk quality by searching for known answers and checking retrieval

## Similarity metric selection

- **Cosine similarity**: default choice, handles variable-length text, normalized
- **Dot product**: use when vectors are already unit-normalized (OpenAI models are), slightly faster
- **Euclidean distance**: use for clustering, when absolute position matters

All three give the same ranking when vectors are normalized. The choice only matters for non-normalized vectors.

## Storage optimization

Three levels of compression, stackable:

1. **Matryoshka truncation**: reduce dimensions (1536 -> 256 = 6x oszczędności, utrata dokładności 3-5%)
2. **Kwantyzacja Float16**: zmniejszenie pamięci o połowę na każdy wymiar (2x oszczędności, <1% utraty dokładności)
3. **Kwantyzacja binarna**: 1 bit na wymiar (32x oszczędność, 5-10% utrata dokładności, użycie z ponowną punktacją)

Wzorzec produkcji: przeszukiwanie binarne całego korpusu, wyszukiwanie 1000 najlepszych wektorów float32.

## Pobierz, a następnie zmień rangę

Dwustopniowy rurociąg zapewniający najlepszą dokładność:

1. Bi-encoder pobiera 100 najlepszych kandydatów (szybko, wykorzystuje wstępnie obliczone osadzania)
2. Cross-enkoder ponownie plasuje się w pierwszej 10 (powolny, przetwarza każdą parę zapytanie-dokument)

Pobija to pobieranie jednoetapowe o 10–15% w przypadku wskaźników precyzji. Użyj, gdy dokładność jest ważniejsza niż opóźnienie.

## Typowe błędy

- Używanie różnych modeli osadzania do indeksowania i wykonywania zapytań
- Osadzanie całych dokumentów zamiast fragmentów (osadzanie staje się przeciętnością wszystkiego)
- Brak normalizacji wektorów przed podobieństwem cosinus (większość modeli wstępnie normalizuje, ale weryfikuje)
- Ignorowanie nakładania się fragmentów (zdania podzielone na granicach tracą kontekst)
- Przechowywanie tylko wektorów bez oryginalnego tekstu (potrzebujesz obu do pobrania)
- Brak ponownego osadzania po zmianie modelu (stare wektory są niekompatybilne)
- Wybór wymiarów w oparciu o samą dokładność (skala przechowywania i opóźnienia liniowo z wymiarami)

## Debugowanie osadzania

Jeśli wyniki wyszukiwania są słabe:

1. Sprawdź, czy osadzenie zapytania jest niezerowe (puste dane wejściowe lub białe znaki dają wektory zerowe)
2. Sprawdź ręcznie stopień podobieństwa znanego, istotnego dokumentu
3. Spróbuj przeformułować zapytanie tak, aby pasowało do słownictwa dokumentu
4. Sprawdź granice porcji, aby upewnić się, że odpowiednia treść nie jest podzielona na porcje
5. Porównaj wyniki top-k dla różnych metryk (cosinus, kropka, euklidesowa), aby wykryć problemy z normalizacją
6. Przetestuj za pomocą banalnie dopasowanego zapytania (skopiuj zdanie z dokumentu), aby potwierdzić, że potok działa

## Parametry produkcyjne

- Rozmiar porcji: 256-512 tokenów
- Nakładanie się porcji: 50 tokenów (10-20% wielkości porcji)
- Odzyskiwanie Top-k: 5-10 do bezpośredniego użycia, 50-100 do zmiany rankingu
- Próg podobieństwa: 0,7+ dla cosinusa (poniżej tego wyniki są zwykle nieistotne)
- Osadzanie wsadowe: przetwarzaj 100-500 tekstów na wywołanie API w celu zapewnienia przepustowości
- Przebudowa indeksu: osadzaj ponownie, gdy model się zmieni lub dokumenty zostaną znacząco zaktualizowane