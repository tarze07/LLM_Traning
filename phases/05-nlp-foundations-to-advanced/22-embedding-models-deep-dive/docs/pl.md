# Osadzanie modeli — głębokie nurkowanie w 2026 roku

> Word2Vec dał ci wektor na słowo. Nowoczesne modele osadzania zapewniają wektor na fragment, wielojęzyczny, z widokami rzadkimi, gęstymi i wielowektorowymi, o rozmiarze dopasowanym do indeksu. Wybierz źle, a RAG pobierze niewłaściwą rzecz.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 03 (Word2Vec), Faza 5 · 14 (wyszukiwanie informacji)
**Czas:** ~60 minut

## Problem

Twój system RAG w 40% przypadków wykrywa nieprawidłowy fragment. Winowajcą rzadko jest baza danych wektorowych lub zachęta. Jest to model osadzania.

Wybór osadzania w 2026 r. oznacza wybór w pięciu osiach:

1. **Gęsty vs rzadki vs wielowektorowy.** Jeden wektor na fragment, jeden na token lub rzadki, ważony zbiór słów.
2. **Zasięg językowy.** Jednojęzyczne modele angielskie nadal wygrywają w zadaniach wyłącznie w języku angielskim. Modele wielojęzyczne wygrywają, gdy korpusy są mieszane.
3. **Długość kontekstu.** 512 tokenów vs 8192 vs 32768 — a rzeczywista efektywna pojemność często wynosi 60-70% reklamowanej maksymalnej.
4. **Budżet wymiarowy.** 3072 pływaków przy pełnej precyzji = 12 KB na wektor. Przy 100 milionach wektorów koszt przechowywania wynosi 1300 USD miesięcznie. Obcięcie Matrioszki tnie to 4×.
5. **Otwarte czy hostowane.** Otwarta waga oznacza, że ​​masz kontrolę nad stosem i danymi. Hostowane oznacza, że ​​zamieniasz kontrolę na zawsze najświeższe informacje.

W tej lekcji wymieniono kompromisy, dzięki czemu można opierać się na dowodach, a nie na tym, co było popularne w ostatnim kwartale.

## Koncepcja

![Gęste, rzadkie i wielowektorowe osadzanie](../assets/embedding-modes.svg)

**Gęste osadzenie.** Jeden wektor na przejście (zwykle 384–3072 wymiary). Podobieństwo cosinusowe szereguje fragmenty według bliskości semantycznej. OpenAI `text-embedding-3-large`, tryb gęsty BGE-M3, Voyage-3. Domyślny wybór.

**Rzadkie osadzania.** W stylu SPLADE. Transformator przewiduje wagę każdego żetonu słownictwa, a następnie większość z nich zeruje. Wynikiem jest rzadki wektor rozmiaru |vocab|. Przechwytuje dopasowanie leksykalne (jak BM25), ale z wyuczonymi wagami terminów. Silny w przypadku zapytań zawierających dużo słów kluczowych.

**Wielowektorowy (późna interakcja).** ColBERTv2, Jina-ColBERT. Jeden wektor na token. Punktacja za pomocą MaxSim: dla każdego tokenu zapytania znajdź najbardziej podobny token dokumentu i zsumuj wyniki. Droższe w przechowywaniu i ocenianiu, ale wygrywają w przypadku długich zapytań i korpusów specyficznych dla domeny.

**BGE-M3: wszystkie trzy na raz.** Pojedynczy model generuje jednocześnie reprezentacje gęste, rzadkie i wielowektorowe. Każde z nich może być sprawdzane niezależnie; wyniki bezpiecznika poprzez sumę ważoną. Wartość domyślna z 2026 r., jeśli chcesz mieć elastyczność w jednym punkcie kontrolnym.

**Uczenie się reprezentacji Matrioszki.** Wytrenowane tak, aby pierwsze N ​​wymiarów wektora tworzyło użyteczne, samodzielne osadzenie. Skróć wektor o 1536 przyciemnieniach do 256 przyciemnień i zapłać ~1% za dokładność, aby uzyskać 6-krotnie większą oszczędność miejsca na dysku. Obsługiwane przez OpenAI tekst-3, Cohere v4, Voyage-4, Jina v5, Gemini Embedding 2, Nomic v1.5+.

### Tablica liderów MTEB przedstawia częściową historię

Test porównawczy ogromnego osadzania tekstu — 56 zadań w 8 typach zadań w chwili premiery (2022 r.), rozszerzony do ponad 100 zadań w MTEB v2. Na początku 2026 r. Gemini Embedding pozyskało 2 szczyty (67,71 MTEB-R). Cohere embed-v4 prowadzi ogólnie (65,2 MTEB). BGE-M3 prowadzi w wersji otwartej wielojęzycznej (63,0). Tablica liderów jest konieczna, ale niewystarczająca — zawsze przeprowadzaj testy porównawcze w swojej domenie.

### Wzór trójpoziomowy

| Przypadek użycia | Wzór |
|---------|---------|
| Szybkie pierwsze przejście | Gęsty bi-enkoder (BGE-M3, tekst-3-mały) |
| Przypomnij sobie wzmocnienie | Rzadki (SPLADE, BGE-M3 rzadki) + bezpiecznik RRF |
| Precyzja na top-50 | Narzędzie do zmiany rankingu wielowektorowego (ColBERTv2) lub między koderami |

Większość stosów produkcyjnych wykorzystuje wszystkie trzy.

## Zbuduj to

### Krok 1: linia bazowa — gęste osadzenie za pomocą Sentence-BERT

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

`normalize_embeddings=True` sprawia, że iloczyn skalarny jest równy podobieństwu cosinusowi. Zawsze ustawiaj.

### Krok 2: Obcięcie Matrioszki

```python
def truncate(vectors, dim):
    out = vectors[:, :dim]
    return out / np.linalg.norm(out, axis=1, keepdims=True)

emb_256 = truncate(emb, 256)
emb_128 = truncate(emb, 128)
```

Ponowna normalizacja po obcięciu. Nomic v1.5, OpenAI Text-3 i Voyage-4 są trenowane, więc na pierwszych kilku poziomach jest to bezstratne. Modele inne niż Matrioszka (oryginalne zdanie-BERT) ulegają gwałtownej degradacji po obcięciu.

### Krok 3: Wielofunkcyjność BGE-M3

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
# output["lexical_weights"]: list of dict {token_id: weight}
# output["colbert_vecs"]:  list of (n_tokens, 1024) arrays
```

Trzy indeksy, jedno wywołanie wnioskowania. Fuzja punktacji:

```python
dense_score = ... # cosine over dense_vecs
sparse_score = model.compute_lexical_matching_score(q_lex, d_lex)
colbert_score = model.colbert_score(q_col, d_col)
final = 0.4 * dense_score + 0.2 * sparse_score + 0.4 * colbert_score
```

Dostosuj wagi w swojej domenie.

### Krok 4: Ocena MTEB dla niestandardowego zadania

```python
from mteb import MTEB

tasks = ["ArguAna", "SciFact", "NFCorpus"]
evaluation = MTEB(tasks=tasks)
results = evaluation.run(encoder, output_folder="./mteb-results")
```

Uruchom swoje modele kandydatów na *reprezentatywnym* podzbiorze. Nie ufaj jedynie rankingowi w tabeli liderów – Twoja domena ma znaczenie.

### Krok 5: ręcznie walcowany cosinus od podstaw

Zobacz `code/main.py`. Uśrednione osadzanie sztuczki mieszającej (tylko stdlib). Nie konkuruje z osadzonymi transformatorami, ale pokazuje kształt: tokenizacja → wektor → normalizacja → iloczyn skalarny.

## Pułapki

- **Ten sam model dla zapytań i dokumentów.** Niektóre modele (Voyage, Jina-ColBERT) wykorzystują kodowanie asymetryczne — zapytania i dokumenty przechodzą różnymi ścieżkami. Zawsze sprawdzaj kartę modelu.
- **Brakujący przedrostek.** Modele `bge-*` wymagają `"Represent this sentence for searching relevant passages: "` dodawanego na początku zapytań. Jeśli zapomnisz, różnica w przypomnieniu 3-5 punktów.
- **Nadmierne przycięcie Matrioszki.** 1536 → 256 jest zwykle bezpieczne. 1536 → 64 nie. Sprawdź poprawność swojego zestawu eval.
- **Obcinanie kontekstu.** Większość modeli dyskretnie obcina dane wejściowe na ich maksymalnej długości. Długie dokumenty wymagają porcjowania (patrz lekcja 23).
- **Ignorowanie ogona opóźnienia.** Wyniki MTEB ukrywają opóźnienie p99. Model 600M może pokonać model 335M o 2 punkty, ale kosztuje 3 razy więcej za zapytanie.

## Użyj tego

Stos na rok 2026:

| Sytuacja | Wybierz |
|----------|------|
| Tylko w języku angielskim, szybkie, API | `text-embedding-3-large` lub `voyage-3-large` |
| Waga otwarta, angielski | `BAAI/bge-large-en-v1.5` |
| Otwarta waga, wielojęzyczna | `BAAI/bge-m3` lub `Qwen3-Embedding-8B` |
| Długi kontekst (32 tys.+) | Voyage-3-large, Cohere embed-v4, Qwen3-Embedding-8B |
| Wdrożenie tylko procesora | Nomic Embed v2 (137M parametrów, MoE) |
| Ograniczone przechowywanie | Matrioszka-skrócona + kwantyzacja int8 |
| Zapytania zawierające dużo słów kluczowych | Dodaj rzadki SPLADE, bezpiecznik RRF z gęstym |

Wzór 2026: zacznij od BGE-M3 lub Text-3-large, oceń na swojej domenie za pomocą MTEB, zamień, jeśli model specyficzny dla domeny wygra o więcej niż 3 punkty.

## Wyślij to

Zapisz jako `outputs/skill-embedding-picker.md`:

```markdown
---
name: embedding-picker
description: Pick embedding model, dimension, and retrieval mode for a given corpus and deployment.
version: 1.0.0
phase: 5
lesson: 22
tags: [nlp, embeddings, retrieval]
---

Given a corpus (size, languages, domain, avg length), deployment target (cloud / edge / on-prem), latency budget, and storage budget, output:

1. Model. Named checkpoint or API. One-sentence reason.
2. Dimension. Full / Matryoshka-truncated / int8-quantized. Reason tied to storage budget.
3. Mode. Dense / sparse / multi-vector / hybrid. Reason.
4. Query prefix / template if required by the model card.
5. Evaluation plan. MTEB tasks relevant to domain + held-out domain eval with nDCG@10.

Refuse recommendations that truncate Matryoshka to <64 dims without domain validation. Refuse ColBERTv2 for corpora under 10k passages (overhead not justified). Flag long-document corpora (>8k tokens) routed to models with 512-token windows.
```

## Ćwiczenia

1. **Łatwe.** Zakoduj 100 zdań za pomocą `bge-small-en-v1.5` przy pełnym przyciemnieniu (384), a następnie na Matrioszce 128. Zmierz spadek MRR w 10 zapytaniach.
2. **Średni.** Porównaj BGE-M3 gęsty, rzadki i colbert na 500 fragmentach z Twojej domeny. Kto wygrywa w programie Recreation@10? Czy fuzja RRF pokonuje najlepszy tryb pojedynczy?
3. **Trudne.** Uruchom MTEB na trzech modelach kandydujących w 2 najważniejszych zadaniach domeny. Raportuj wynik MTEB, opóźnienie p99 w partii 100 zapytań i zapytania o wartości 1 mln USD. Wybierz optymalny w Pareto.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Gęste osadzenie | Wektor | Jeden wektor o stałym rozmiarze na tekst. Cosinus podobieństwa dla rankingu. |
| Rzadkie osadzanie | Nauczyłem się BM25 | Jeden ciężar na żeton słownictwa; głównie zera; przeszkolony od końca do końca. |
| Wielowektorowy | W stylu ColBERTA | Jeden wektor na token; Punktacja MaxSima; większy indeks, lepsza pamięć. |
| Matrioszka | Rosyjska sztuczka z lalką | Pierwsze N ​​przyciemnień jest samodzielnym prawidłowym mniejszym osadzeniem. |
| MTEB | Punkt odniesienia | Test porównawczy osadzania ogromnego tekstu — 56 zadań w chwili premiery, ponad 100 w wersji 2. |
| BEIR | Punkt odniesienia w zakresie wyszukiwania | 18 zadań odzyskiwania typu zero-shot; często cytowany ze względu na niezawodność w wielu domenach. |
| Kodowanie asymetryczne | Zapytanie ≠ ścieżka dokumentu | Model wykorzystuje różne prognozy dla zapytań i dokumentów. |

## Dalsze czytanie

- [Reimers, Gurevych (2019). Zdanie-BERT](https://arxiv.org/abs/1908.10084) — dokument dotyczący bi-encodera.
- [Muennighoff i in. (2022). MTEB: test porównawczy osadzania ogromnego tekstu](https://arxiv.org/abs/2210.07316) — dokument liderów.
- [Chen i in. (2024). BGE-M3: wielojęzyczność, wielofunkcyjność, wieloziarnistość](https://arxiv.org/abs/2402.03216) — ujednolicony model trzech trybów.
- [Kusupati i in. (2022). Uczenie się reprezentacji Matrioszki](https://arxiv.org/abs/2205.13147) — cel szkolenia w postaci drabiny wymiarowej.
- [Santhanam i in. (2022). ColBERTv2: Skuteczne i wydajne wyszukiwanie poprzez lekką późną interakcję](https://arxiv.org/abs/2112.01488) — późna interakcja w produkcji.
- [Tabela liderów MTEB na Hugging Face](https://huggingface.co/spaces/mteb/leaderboard) — rankingi na żywo.