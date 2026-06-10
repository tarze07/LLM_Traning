# Modele osadzeń (Embedding Models) – szczegółowa analiza (stan na rok 2026)

> Word2Vec tworzył pojedynczy wektor dla każdego słowa. Nowoczesne modele osadzeń generują wektory dla całych fragmentów tekstu, są wielojęzyczne i oferują reprezentacje gęste, rzadkie oraz wielowektorowe (multi-vector), umożliwiając dodatkowo elastyczne dostosowanie rozmiaru do potrzeb indeksowania. Błędny wybór modelu sprawi, że system RAG pobierze niepoprawne informacje.

**Typ:** Teoria
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 03 (Word2Vec), Faza 5 · 14 (Wyszukiwanie informacji)
**Czas:** ~60 minut

## Problem

Twój system RAG w 40% przypadków zwraca niepoprawny fragment tekstu. Przyczyną tego stanu rzeczy rzadko jest sama wektorowa baza danych czy jakość promptu – najczęściej winę ponosi model osadzeń (embedding model).

Wybór modelu osadzeń w 2026 roku wymaga podjęcia decyzji w pięciu wymiarach:

1. **Gęste vs rzadkie vs wielowektorowe:** Jeden wektor na fragment tekstu (dense), jeden wektor na każdy token (multi-vector) lub rzadki, ważony zbiór słów (sparse).
2. **Zasięg językowy:** Dedykowane, jednojęzyczne modele dla języka angielskiego wciąż osiągają najlepsze wyniki na danych wyłącznie angielskich. Modele wielojęzyczne są bezkonkurencyjne przy korpusach mieszanych.
3. **Długość kontekstu:** Od 512 tokenów do 8192 lub nawet 32 768. Należy jednak pamiętać, że rzeczywista, efektywna pojemność okna kontekstowego wynosi zazwyczaj 60-70% wartości deklarowanej.
4. **Budżet pamięci (wymiarowość wektora):** Wektor o rozmiarze 3072 liczb zmiennoprzecinkowych (float32) zajmuje około 12 KB pamięci. Przy 100 milionach wektorów koszt samego ich przechowywania w pamięci RAM może wynosić około 1300 USD miesięcznie. Zastosowanie techniki osadzeń typu Matrioszka (Matryoshka embeddings) pozwala zredukować ten koszt nawet 4-krotnie.
5. **Modele otwartoźródłowe (open-weights) vs komercyjne API:** Modele open-weights dają pełną kontrolę nad infrastrukturą i bezpieczeństwem danych. Korzystanie z API zewnętrznych dostawców to wygoda i stały dostęp to najnowszych rozwiązań kosztem utraty kontroli.

Ta lekcja pozwoli Ci zrozumieć intuicję stojącą za tymi trzema podejściami i pomoże zdecydować, które z nich wybrać do swojego projektu.

## Koncepcja

![Gęste, rzadkie i wielowektorowe osadzanie](../assets/embedding-modes.svg)

**Osadzenia gęste (Dense embeddings).** Reprezentacja w postaci jednego wektora o stałej długości dla całego fragmentu tekstu (zwykle od 384 do 3072 wymiarów). Podobieństwo cosinusowe (cosine similarity) pozwala uszeregować fragmenty według ich bliskości semantycznej. Przykłady: `text-embedding-3-large` od OpenAI, gęsty wariant BGE-M3, Voyage-3. Jest to najczęstszy wybór domyślny.

**Osadzenia rzadkie (Sparse embeddings).** Metody takie jak SPLADE. Transformer wyznacza wagi dla każdego tokenu z całego słownika, a następnie zeruje większość z nich. Wynikiem jest rzadki wektor o wymiarowości równej rozmiarowi słownika. Podejście to łączy zalety dopasowania leksykalnego (jak w BM25) z wyuczonym ważeniem pojęć. Bardzo dobrze sprawdza się w zapytaniach opartych na słowach kluczowych.

**Metody wielowektorowe / Późna interakcja (Multi-vector / Late interaction).** Rozwiązania takie jak ColBERTv2 czy Jina-ColBERT. Model generuje osobny wektor dla każdego tokenu w tekście. Ocena podobieństwa odbywa się za pomocą operatora MaxSim: dla każdego tokenu w zapytaniu wyszukuje się najbardziej podobny token w dokumencie, a następnie sumuje te wartości. Rozwiązanie droższe w przechowywaniu i obliczeniach, lecz niezwykle skuteczne przy długich zapytaniach oraz w specjalistycznych dziedzinach.

**BGE-M3: Trzy podejścia w jednym.** Pojedynczy model, który generuje jednocześnie reprezentacje gęste, rzadkie oraz wielowektorowe. Każdy tryb można przeszukiwać niezależnie, a następnie łączyć wyniki za pomocą średniej ważonej. To domyślne, uniwersalne rozwiązanie w 2026 roku zapewniające maksymalną elastyczność.

**Osadzenia typu Matrioszka (Matryoshka Representation Learning).** Modele te są trenowane w taki sposób, aby pierwsze `N` wymiarów wektora tworzyło w pełni funkcjonalne, samodzielne osadzenie o mniejszym rozmiarze. Skrócenie wektora o wymiarowości 1536 do 256 wymiarów wiąże się ze spadkiem dokładności o zaledwie ~1%, przy jednoczesnym 6-krotnym zmniejszeniu zajętości pamięci dyskowej. Technika ta jest obsługiwana m.in. przez modele OpenAI text-3, Cohere v4, Voyage-4, Jina v5, Gemini Embedding 2 czy Nomic v1.5+.

### Ranking MTEB to tylko część prawdy

Benchmark MTEB (Massive Text Embedding Benchmark) w momencie premiery w 2022 roku składał się z 56 zadań podzielonych na 8 kategorii, a w wersji MTEB v2 został rozszerzony do ponad 100 testów. Na początku 2026 roku model Gemini Embedding zajął dwa czołowe miejsca (wynik 67,71 w MTEB-R). Cohere embed-v4 prowadzi w rankingu ogólnym (65,2), natomiast model BGE-M3 dominuje wśród otwartych modeli wielojęzycznych (63,0). Rankingi są cennym drogowskazem, ale nie zastąpią ewaluacji na własnych danych dziedzinowych.

### Trzystopniowa architektura wyszukiwania (Search Pattern)

| Krok | Metoda |
|---------|---------|
| Szybkie pierwsze przejście (Retrieval) | Gęsty bi-encoder (np. BGE-M3, text-embedding-3-small) |
| Zwiększenie pokrycia (Recall boost) | Wyszukiwanie rzadkie (np. SPLADE, rzadki wariant BGE-M3) połączone metodą RRF |
| Precyzyjna selekcja TOP-50 (Reranking) | Reranker wielowektorowy (np. ColBERTv2) lub model typu cross-encoder |

Większość produkcyjnych systemów wyszukiwania łączy te trzy poziomy.

## Zbuduj to

### Krok 1: Wzorzec bazowy – gęste osadzenia przy użyciu Sentence-Transformers

```python
from sentence_transformers import SentenceTransformer
import numpy as np

encoder = SentenceTransformer("BAAI/bge-small-en-v1.5")
corpus = [
    "The first iPhone launched in 2007.",
    "Apple released the iPod in 2001.",
    "Android is an operating system from Google.",
]
emb = encoder.encode(corpus, normalize_embeddings=True)

query = "When was the iPhone released?"
q_emb = encoder.encode([query], normalize_embeddings=True)[0]
scores = emb @ q_emb
print(sorted(enumerate(scores), key=lambda x: -x[1]))
```

Ustawienie parametru `normalize_embeddings=True` sprawia, że iloczyn skalarny (dot product) staje się tożsamy z podobieństwem cosinusowym. Należy zawsze stosować tę konfigurację.

### Krok 2: Skracanie wektorów typu Matrioszka

```python
def truncate(vectors, dim):
    out = vectors[:, :dim]
    return out / np.linalg.norm(out, axis=1, keepdims=True)

emb_256 = truncate(emb, 256)
emb_128 = truncate(emb, 128)
```

Po skróceniu wektora należy go ponownie znormalizować. Modele takie jak Nomic v1.5, OpenAI Text-3 czy Voyage-4 są specjalnie trenowane w tym celu, dzięki czemu spadek jakości przy ograniczeniu wymiarowości jest znikomy. Zwykłe modele (np. klasyczny Sentence-BERT) po obcięciu wektorów tracą większość swoich właściwości semantycznych.

### Krok 3: Wykorzystanie modelu BGE-M3 w trzech trybach

```python
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)

output = model.encode(
    corpus,
    return_dense=True,
    return_sparse=True,
    return_colbert_vecs=True,
)
# output["dense_vecs"]:    (n_docs, 1024)
# output["lexical_weights"]: słownik postaci {token_id: weight}
# output["colbert_vecs"]:  lista macierzy o rozmiarze (n_tokens, 1024)
```

Model generuje trzy reprezentacje podczas jednego przebiegu (inference). Fuzja wyników wygląda następująco:

```python
dense_score = ... # podobieństwo cosinusowe dla dense_vecs
sparse_score = model.compute_lexical_matching_score(q_lex, d_lex)
colbert_score = model.colbert_score(q_col, d_col)
final = 0.4 * dense_score + 0.2 * sparse_score + 0.4 * colbert_score
```

Wagi te należy dostosować w zależności od specyfiki analizowanej dziedziny.

### Krok 4: Uruchomienie ewaluacji MTEB dla własnych zadań

```python
from mteb import MTEB

tasks = ["ArguAna", "SciFact", "NFCorpus"]
evaluation = MTEB(tasks=tasks)
results = evaluation.run(encoder, output_folder="./mteb-results")
```

Uruchom testy modeli na *reprezentatywnym* podzbiorze swoich danych. Nie polegaj wyłącznie na publicznych rankingach – wydajność w Twojej dziedzinie może się znacząco różnić.

### Krok 5: Klasyczne obliczanie podobieństwa cosinusowego od podstaw

W pliku `code/main.py` znajdziesz uproszczoną implementację opartą na średnich wektorach słów (tylko z użyciem biblioteki standardowej Pythona). Kod ten ma charakter wyłącznie poglądowy, lecz dobrze obrazuje strukturę potoku: tokenizacja → mapowanie na wektor → normalizacja → iloczyn skalarny.

## Typowe pułapki

- **Symetryczność kodowania (Asymmetric encoding):** Niektóre modele (np. Voyage czy Jina-ColBERT) wymagają innego sposobu kodowania dla zapytań (queries), a innego dla dokumentów (documents). Należy zawsze weryfikować dokumentację modelu (model card).
- **Brak wymaganych prefiksów:** Modele z rodziny `bge-*` wymagają dodania przedrostka `"Represent this sentence for searching relevant passages: "` na początku każdego zapytania testowego. Pominięcie tego kroku może obniżyć metrykę Recall o 3-5 punktów procentowych.
- **Zbyt agresywne skracanie Matrioszki:** Redukcja wymiarów z 1536 do 256 zazwyczaj nie wpływa drastycznie na jakość, lecz zejście do 64 wymiarów może zniszczyć reprezentację semantyczną. Zawsze weryfikuj to na zbiorze walidacyjnym.
- **Ciche obcinanie kontekstu (Context truncation):** Większość modeli po cichu odrzuca tokeny wykraczające poza ich maksymalny limit długości wejścia. Długie teksty muszą zostać podzielone na mniejsze części przed zakodowaniem (patrz lekcja 23).
- **Ignorowanie opóźnień (Latency):** Rankingi MTEB nie pokazują opóźnień generowania (np. metryki p99). Większy model o rozmiarze 600M parametrów może osiągnąć wynik lepszy o 2 punkty od modelu 335M, ale koszt jego uruchomienia i czas odpowiedzi mogą być 3-krotnie wyższe.

## Rekomendowane podejścia

| Sytuacja | Zalecane rozwiązanie |
|----------|------|
| Tylko język angielski, wysoka szybkość, usługi chmurowe API | `text-embedding-3-large` lub `voyage-3-large` |
| Modele otwartoźródłowe (open-weights), język angielski | `BAAI/bge-large-en-v1.5` |
| Modele otwartoźródłowe (open-weights), wielojęzyczne | `BAAI/bge-m3` lub `Qwen3-Embedding-8B` |
| Długi kontekst (32k+ tokenów) | `voyage-3-large`, `embed-english-v3.0` (Cohere) lub `Qwen3-Embedding-8B` |
| Wdożenia wyłącznie na procesorach (CPU-only) | `nomic-embed-text-v1.5` lub wersje MoE |
| Ograniczony budżet dyskowy/RAM | Osadzenia typu Matrioszka + kwantyzacja do formatu int8 |
| Wyszukiwanie oparte na słowach kluczowych | Hybryda (gęsty model + rzadki model SPLADE) połączone algorytmem RRF |

Sprawdzona praktyka w 2026 roku: zacznij od modelu `BAAI/bge-m3` lub `text-embedding-3-large`. Przeprowadź ewaluację na własnym korpusie i zmień model tylko wtedy, gdy alternatywne rozwiązanie da przyrost metryki wyszukiwania o więcej niż 3 punkty.

## Zapisywanie szablonu

Zapisz jako `outputs/skill-embedding-picker.md`:

```markdown
---
name: embedding-picker
description: Wybierz model osadzeń, wymiarowość wektorów oraz tryb wyszukiwania dla podanego korpusu i architektury wdrożenia.
version: 1.0.0
phase: 5
lesson: 22
tags: [nlp, embeddings, retrieval]
---

Na podstawie parametrów korpusu (rozmiar, języki, dziedzina, średnia długość), środowiska uruchomieniowego (chmura / urządzenia brzegowe / on-premise), limitów opóźnień oraz budżetu dyskowego wygeneruj:

1. Model: Dokładna nazwa punktu kontrolnego (checkpoint) lub usługa API wraz z jednozdaniowym uzasadnieniem.
2. Wymiarowość: Pełna / skrócona (Matryoshka) / skwantyzowana do int8 wraz z uzasadnieniem budżetowym.
3. Tryb wyszukiwania: Gęsty / rzadki / wielowektorowy / hybrydowy wraz z uzasadnieniem.
4. Prefiks zapytania (Query prefix) lub szablon promptu (jeśli jest wymagany przez specyfikację modelu).
5. Plan ewaluacji: Lista powiązanych zadań z benchmarku MTEB oraz testy na własnym, wydzielonym zbiorze z wykorzystaniem metryki nDCG@10.

Nigdy nie rekomenduj skracania wektorów Matrioszki do mniej niż 64 wymiarów bez przeprowadzenia dokładnej walidacji dziedzinowej. Zawsze odrzucaj propozycję stosowania modeli ColBERTv2 dla korpusów mniejszych niż 10 000 fragmentów (narzut infrastrukturalny przewyższa korzyści). Oznaczaj korpusy o długich tekstach (>8k tokenów) przekazywane do modeli o małym oknie kontekstowym (np. 512 tokenów).
```

## Ćwiczenia praktyczne

1. **Poziom łatwy:** Zakoduj 100 zdań za pomocą modelu `bge-small-en-v1.5` przy pełnej wymiarowości (384), a następnie zredukuj wektory metodą Matrioszki do 128 wymiarów. Zmierz różnicę w metryce MRR dla 10 przykładowych zapytań.
2. **Poziom średni:** Porównaj skuteczność wyszukiwania w trybie gęstym, rzadkim oraz wielowektorowym (ColBERT) na zbiorze 500 fragmentów z własnej dziedziny. Porównaj wartość metryki Recall@10. Sprawdź, czy fuzja wyników metodą RRF przewyższa pojedyncze tryby.
3. **Poziom trudny:** Uruchom testy MTEB dla trzech różnych modeli na dwóch kluczowych dla Ciebie zadaniach wyszukiwania. Przedstaw zestawienie wyników dokładności, opóźnień p99 dla paczek po 100 zapytań oraz kosztów obsługi dla miliona zapytań. Wskaż model optymalny w sensie Pareto.

## Kluczowe pojęcia

| Termin | Potoczne określenie | Znaczenie precyzyjne |
|------|-----------------|----------------------|
| Osadzenie gęste (Dense embedding) | Wektor | Pojedynczy wektor o stałej długości reprezentujący cały tekst; porównywany za pomocą podobieństwa cosinusowego. |
| Osadzenie rzadkie (Sparse embedding) | Nauczyłem się BM25 | Wektor o wymiarowości słownika, gdzie większość wartości to zera; uczy się wag konkretnych słów kluczowych. |
| Model wielowektorowy (Multi-vector / Late interaction) | W stylu ColBERTa | Generowanie osobnego wektora dla każdego tokenu w tekście i porównywanie ich operatorem MaxSim; większy rozmiar indeksu w zamian za wyższą jakość wyszukiwania. |
| Osadzenia typu Matrioszka (Matryoshka) | Rosyjska lalka | Technika treningu sprawiająca, że pierwsze `N` wymiarów wektora stanowi w pełni funkcjonalne osadzenie o mniejszym rozmiarze. |
| MTEB (Massive Text Embedding Benchmark) | Punkt odniesienia | Główny benchmark do oceny modeli osadzeń tekstowych, zawierający obecnie ponad 100 różnych zadań testowych. |
| BEIR Benchmark | BEIR | Podzbiór benchmarku MTEB skupiony na zadaniach wyszukiwania informacji (Information Retrieval) w trybie zero-shot. |
| Kodowanie asymetryczne (Asymmetric encoding) | Zapytanie ≠ ścieżka dokumentu | Architektura, w której zapytania użytkownika i dokumenty w bazie są kodowane przez osobne podsieci lub z użyciem innych prefiksów. |

## Literatura uzupełniająca

- [Reimers & Gurevych (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks](https://arxiv.org/abs/1908.10084) — praca wprowadzająca efektywne uczenie osadzeń zdań.
- [Muennighoff et al. (2022). MTEB: Massive Text Embedding Benchmark](https://arxiv.org/abs/2210.07316) — publikacja opisująca strukturę i założenia benchmarku MTEB.
- [Chen et al. (2024). BGE-M3: A Unified Multi-Function, Multi-Lingual and Multi-Granularity Sequence Encoder](https://arxiv.org/abs/2402.03216) — opis architektury modelu BGE-M3.
- [Kusupati et al. (2022). Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147) — praca wprowadzająca matematyczne podstawy skalowalnych wektorów osadzeń.
- [Santhanam et al. (2021). ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction](https://arxiv.org/abs/2112.01488) — publikacja opisująca technikę późnej interakcji (late interaction).
- [Oficjalny ranking MTEB na platformie Hugging Face](https://huggingface.co/spaces/mteb/leaderboard) — rankingi na żywo.
