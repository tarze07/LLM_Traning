# Wyszukiwanie i wyszukiwanie informacji

> BM25 jest precyzyjny, ale kruchy. Gęsty rzuca szeroką sieć, ale pomija słowa kluczowe. Hybryda to opcja domyślna na rok 2026. Wszystko inne to tuning.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 02 (BoW + TF-IDF), Faza 5 · 04 (GloVe, FastText, Subword)
**Czas:** ~75 minut

## Problem

Użytkownik wpisuje „co się stanie, jeśli ktoś kłamie, aby zdobyć pieniądze” i spodziewa się znaleźć ustawę, która faktycznie to reguluje: „Artykuł 420 PPC”. Wyszukiwanie słów kluczowych całkowicie to pomija (brak wspólnego słownictwa). Wyszukiwanie semantyczne pomija to, jeśli osadzanie nie zostało przeszkolone w zakresie tekstu prawnego. Prawdziwe wyszukiwanie musi obsłużyć jedno i drugie.

IR to potok w każdym systemie RAG, każdym pasku wyszukiwania, rozmytym wyszukiwaniu w każdej witrynie z dokumentami. Architektura 2026, która sprawdza się w produkcji, nie jest pojedynczą metodą. Jest to łańcuch uzupełniających się metod, z których każda wyłapuje błędy poprzedniej.

W tej lekcji omówiono każdy element i nazwano błędy, które każdy z nich wyłapał.

## Koncepcja

![Pobieranie hybrydowe: BM25 + gęste + RRF + zmiana rangi międzykodera](../assets/retrieval.svg)

Cztery warstwy. Wybierz te, których potrzebujesz.

1. **Wyszukiwanie rzadkie (BM25).** Szybkie, precyzyjne w przypadku dokładnych dopasowań, fatalne pod względem semantyki. Przejedź przez odwrócony indeks. Poniżej 10 ms na zapytanie w przypadku milionów dokumentów. Zawiera odniesienia do przepisów, kody produktów, komunikaty o błędach i nazwy podmiotów.
2. **Gęste pobieranie.** Koduj zapytania i dokumenty do wektorów. Wyszukiwanie najbliższego sąsiada. Wychwytuje parafrazy i podobieństwa semantyczne. Pomija dokładne dopasowania słów kluczowych, które różnią się jednym znakiem. 50-200 ms na zapytanie z FAISS lub wektorową bazą danych.
3. **Fusion.** Połącz listy rankingowe z rzadkich i gęstych. Prostą opcją domyślną jest Reciprocal Rank Fusion (RRF), ponieważ ignoruje surowe wyniki (które występują w różnych skalach) i wykorzystuje tylko pozycje rangi. Fuzja ważona jest opcją, gdy wiesz, że w Twojej domenie dominuje jeden sygnał.
4. **Ponowna ocena cross-enkodera.** Wybierz 30 najlepszych z fusion. Uruchom koder krzyżowy (razem zapytanie + dokument, oceniając każdą parę). Zachowaj top-5. Kodery krzyżowe działają wolniej na parę niż kodery podwójne, ale są znacznie dokładniejsze. Amortyzujesz, uruchamiając je tylko w pierwszej trzydziestce.

Wyszukiwanie trójkierunkowe (BM25 + gęste + wyuczone-rzadkie, takie jak SPLADE) zapewnia lepsze wyniki w przypadku dwukierunkowego wyszukiwania w benchmarkach z 2026 r., ale wymaga infrastruktury dla indeksów wyuczonych-rzadkich. Dla większości zespołów najlepszym rozwiązaniem jest zmiana rangi dwukierunkowej i międzykoderowej.

## Zbuduj to

### Krok 1: BM25 od podstaw

```python
import math
import re
from collections import Counter

TOKEN_RE = re.compile(r"[a-z0-9]+")

def tokenize(text):
    return TOKEN_RE.findall(text.lower())

class BM25:
    def __init__(self, corpus, k1=1.5, b=0.75):
        if not corpus:
            raise ValueError("corpus must not be empty")
        self.corpus = [tokenize(d) for d in corpus]
        self.k1 = k1
        self.b = b
        self.n_docs = len(self.corpus)
        self.avg_dl = sum(len(d) for d in self.corpus) / self.n_docs
        self.df = Counter()
        for doc in self.corpus:
            for term in set(doc):
                self.df[term] += 1

    def idf(self, term):
        n = self.df.get(term, 0)
        return math.log(1 + (self.n_docs - n + 0.5) / (n + 0.5))

    def score(self, query, doc_idx):
        q_tokens = tokenize(query)
        doc = self.corpus[doc_idx]
        dl = len(doc)
        freq = Counter(doc)
        score = 0.0
        for term in q_tokens:
            f = freq.get(term, 0)
            if f == 0:
                continue
            numerator = f * (self.k1 + 1)
            denominator = f + self.k1 * (1 - self.b + self.b * dl / self.avg_dl)
            score += self.idf(term) * numerator / denominator
        return score

    def rank(self, query, top_k=10):
        scored = [(self.score(query, i), i) for i in range(self.n_docs)]
        scored.sort(reverse=True)
        return scored[:top_k]
```

Dwa parametry, które warto poznać. `k1=1.5` kontroluje nasycenie terminowo-częstotliwościowe; wyższa oznacza większą wagę przy powtarzaniu semestru. `b=0.75` kontroluje normalizację długości; 0 ignoruje długość dokumentu, 1 całkowicie normalizuje. Wartości domyślne to zalecenia Robertsona z oryginalnej pracy i rzadko wymagają dostrajania.

### Krok 2: gęste pobieranie za pomocą bi-enkodera

```python
from sentence_transformers import SentenceTransformer
import numpy as np

def build_dense_index(corpus, model_id="sentence-transformers/all-MiniLM-L6-v2"):
    encoder = SentenceTransformer(model_id)
    embeddings = encoder.encode(corpus, normalize_embeddings=True)
    return encoder, embeddings

def dense_search(encoder, embeddings, query, top_k=10):
    q_emb = encoder.encode([query], normalize_embeddings=True)
    sims = (embeddings @ q_emb.T).flatten()
    order = np.argsort(-sims)[:top_k]
    return [(float(sims[i]), int(i)) for i in order]
```

L2 — normalizuj osadzania, aby iloczyn skalarny był równy cosinusowi. `all-MiniLM-L6-v2` jest 384-dim, szybki i wystarczająco mocny, aby umożliwić większość wyszukiwania w języku angielskim. W przypadku pracy wielojęzycznej użyj `paraphrase-multilingual-MiniLM-L12-v2`. Aby uzyskać najwyższą dokładność, `bge-large-en-v1.5` lub `e5-large-v2`.

### Krok 3: Wzajemna fuzja rang

```python
def reciprocal_rank_fusion(rankings, k=60):
    scores = {}
    for ranking in rankings:
        for rank, (_, doc_idx) in enumerate(ranking):
            scores[doc_idx] = scores.get(doc_idx, 0.0) + 1.0 / (k + rank + 1)
    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(score, doc_idx) for doc_idx, score in fused]
```

Stała `k=60` pochodzi z oryginalnej publikacji RRF. Wyższe `k` spłaszcza udział różnic rangowych; niższy `k` sprawia, że ​​dominują najwyższe pozycje. 60 jest opublikowaną wartością domyślną i rzadko wymaga dostrajania.

### Krok 4: wyszukiwanie hybrydowe + zmiana rankingu

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def hybrid_search(query, bm25, encoder, dense_embeddings, corpus, top_k=5, pool_size=30, reranker=reranker):
    sparse_ranking = bm25.rank(query, top_k=pool_size)
    dense_ranking = dense_search(encoder, dense_embeddings, query, top_k=pool_size)
    fused = reciprocal_rank_fusion([sparse_ranking, dense_ranking])[:pool_size]

    pairs = [(query, corpus[doc_idx]) for _, doc_idx in fused]
    scores = reranker.predict(pairs)
    reranked = sorted(zip(scores, [doc_idx for _, doc_idx in fused]), reverse=True)
    return reranked[:top_k]
```

Skomponowane trzy etapy. BM25 znajduje dopasowania leksykalne. Gęsty znajduje dopasowania semantyczne. RRF łączy oba rankingi bez konieczności kalibracji wyników. Cross-enkoder ponownie ocenia 30 najlepszych, używając razem par zapytanie-dokument, co pozwala uchwycić szczegółowe znaczenie, które przeoczył bi-enkoder. Zachowaj top-5.

### Krok 5: ocena

| Metryczne | Znaczenie |
|------------|--------|
| Przypomnij@k | W przypadku zapytań, w których istnieje właściwy dokument, jak często znajduje się on na górze k? |
| MRR (średnia ranga wzajemna) | Średnia 1/pozycja pierwszego odpowiedniego dokumentu. |
| nDCG@k | Uwzględnia gradację trafności, a nie tylko znaczenie binarne/nie. |

W przypadku RAG najważniejszym numerem jest **Recall@k** ​​retrievera. Czytelnik nie może odpowiedzieć, jeśli w pobranym zestawie nie ma odpowiedniego fragmentu.

Wskazówka dotycząca debugowania: w przypadku nieudanych zapytań należy różnicować rankingi rzadkie i gęste. Jeśli jeden znajdzie właściwy dokument, a drugi nie, oznacza to niedopasowanie słownictwa (poprawka: dodaj brakującą połowę) lub niejednoznaczność semantyczną (poprawka: lepsze osadzanie lub zmiana rankingu).

## Użyj tego

Stos na rok 2026:

| Skala | Stos |
|-------|-------|
| Dokumenty od 1 tys. do 100 tys. | BM25 w pamięci + osadzanie `all-MiniLM-L6-v2` + RRF. Brak osobnej bazy danych. |
| Dokumenty 100 tys.–10 mln | FAISS lub pgvector dla gęstego + Elasticsearch / OpenSearch dla BM25. Biegaj równolegle. |
| Ponad 10 milionów dokumentów | Qdrant / Weaviate / Vespa / Milvus ze wsparciem hybrydowym. Cross-enkoder ponownie uplasował się na pierwszej 30-tce. |
| Granica najlepszej jakości | Trójstronny (BM25 + gęsty + SPLADE) + zmiana rankingu późnej interakcji ColBERT |

Cokolwiek wybierzesz, budżet na ocenę. Przywołanie danych porównawczych przed wykonaniem analizy porównawczej dokładności RAG od początku do końca. Czytelnik nie jest w stanie naprawić tego, co przeoczył retriever.

### Z trudem wyciągnięte wnioski z produkcji RAG z 2026 roku

- **80% błędów RAG wynika z przyjmowania i fragmentowania, a nie z modelu.** Zespoły spędzają tygodnie na wymianie LLM i podpowiedziach dostrajania, podczas gdy pobieranie po cichu zwraca zły kontekst co trzecie zapytanie. Najpierw napraw fragmentację.
- **Strategia dzielenia na kawałki ma większe znaczenie niż rozmiar porcji.** Stały rozmiar podziału dzieli tabele, kod i zagnieżdżone nagłówki. Domyślną opcją jest rozpoznawanie zdań; Podział semantyczny lub oparty na LLM opłaca się w przypadku dokumentacji technicznej i podręczników produktów.
- **Wzorzec dokumentu nadrzędnego.** Dla precyzji pobieraj małe fragmenty „podrzędne”. Gdy pojawi się wiele elementów podrzędnych z tej samej sekcji nadrzędnej, zamień blok nadrzędny, aby zachować kontekst. To stale podnosi jakość odpowiedzi bez konieczności ponownego szkolenia.
- **k_rerank=3 jest zwykle optymalny.** Każdy dodatkowy fragment w przeszłości zwiększa koszt tokena i opóźnienie generowania bez podnoszenia jakości odpowiedzi. Jeśli dla Ciebie k=8 jest w dalszym ciągu lepsze niż k=3, oznacza to, że osoba zajmująca się rerankingiem ma słabsze wyniki.
- **HyDE / rozszerzenie zapytania.** Wygeneruj hipotetyczną odpowiedź na zapytanie, osadź ją i pobierz. Wypełnia lukę w sformułowaniach między krótkimi pytaniami a długimi dokumentami. Bezpłatny podnośnik precyzyjny bez szkolenia.
- **Budżet kontekstowy poniżej 8 tys. tokenów.** Stałe trafienia w tym limicie oznaczają, że próg zmiany rankingu jest zbyt luźny.
- **Wersja wszystkiego.** Podpowiedzi, zasady dzielenia, model osadzania, zmiana rankingu. Jakikolwiek dryf dyskretnie psuje jakość odpowiedzi. Bramki CI dotyczące wierności, precyzji kontekstu i regresji blokowych odsetka pytań bez odpowiedzi, zanim użytkownicy je zobaczą.
- **Wyszukiwanie trójkierunkowe (BM25 + gęste + wyuczone-rzadkie jak SPLADE) jest lepsze niż dwukierunkowe** w testach porównawczych z 2026 r., szczególnie w przypadku zapytań łączących rzeczowniki własne z semantyką. Wyślij go, gdy infrastruktura obsługuje indeksy SPLADE.

Według pomiarów branżowych z 2026 r. właściwy projekt odzyskiwania zmniejsza halucynacje o 70–90%. Większość przyrostów wydajności RAG wynika z lepszego wyszukiwania, a nie z dostrajania modelu.

## Wyślij to

Zapisz jako `outputs/skill-retrieval-picker.md`:

```markdown
---
name: retrieval-picker
description: Pick a retrieval stack for a given corpus and query pattern.
version: 1.0.0
phase: 5
lesson: 14
tags: [nlp, retrieval, rag, search]
---

Given requirements (corpus size, query pattern, latency budget, quality bar, infra constraints), output:

1. Stack. BM25 only, dense only, hybrid (BM25 + dense + RRF), hybrid + cross-encoder rerank, or three-way (BM25 + dense + learned-sparse).
2. Dense encoder. Name the specific model. Match to language(s), domain, and context length.
3. Reranker. Name the specific cross-encoder model if used. Flag that rerank adds 30-100ms latency on top-30.
4. Evaluation plan. Recall@10 is the primary retriever metric. MRR for multi-answer. Baseline first, incremental improvements measured against it.

Refuse to recommend dense-only for corpora with named entities, error codes, or product SKUs unless the user has evidence dense handles exact matches. Refuse to skip reranking for high-stakes retrieval (legal, medical) where the final top-5 decides the user's answer.
```

## Ćwiczenia

1. **Łatwe.** Zaimplementuj `hybrid_search` powyżej w korpusie zawierającym 500 dokumentów. Przetestuj 20 zapytań. Porównaj wycofanie przy 5 pomiędzy tylko BM25, tylko gęstym i hybrydowym.
2. **Średni.** Dodaj obliczenie MRR. Dla każdego zapytania testowego ze znanym poprawnym dokumentem znajdź rangę prawidłowego dokumentu w rankingach BM25, gęstych i hybrydowych. Zgłoś MRR dla każdego.
3. **Trudne.** Dostosuj gęsty koder w swojej domenie za pomocą MultipleNegativesRankingLoss (Transformatory zdań). Zbuduj zestaw szkoleniowy z 500 par zapytanie-dokument. Porównaj przypominanie przed i po dostrojeniu.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| BM25 | Wyszukiwanie słów kluczowych | Okap BM25. Ocenia dokumenty według częstotliwości terminów, IDF i długości. |
| Gęste pobieranie | Wyszukiwanie wektorów | Zakoduj zapytanie + dokument na wektory, znajdź najbliższych sąsiadów. |
| Bi-enkoder | Osadzanie modelu | Niezależnie koduje zapytanie i dokument. Szybko w czasie zapytania. |
| Koder krzyżowy | Model zmiany rankingu | Koduje zapytanie + dokument razem. Powolny, ale dokładny. |
| RRF | Fuzja rang | Połącz dwa rankingi, sumując `1/(k + rank)`. |
| Przypomnij@k | Metryka pobierania | Część zapytań, w przypadku których odpowiedni dokument znajduje się na górze k. |

## Dalsze czytanie

- [Robertson i Saragossa (2009). Probabilistyczne ramy istotności: BM25 i dalej] (https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf) — ostateczne leczenie BM25.
- [Karpukhin i in. (2020). Dense Passage Retrieval for Open-Domain QA](https://arxiv.org/abs/2004.04906) — DPR, kanoniczny bi-enkoder.
- [Formal i in. (2021). SPLADE: rzadki model leksykalny i rozszerzający](https://arxiv.org/abs/2107.05720) — wyuczony, rzadki retriever, który wypełnia lukę gęstym.
- [Cormack, Clarke, Büttcher (2009). Reciprocal Rank Fusion przewyższa Condorcet i indywidualne metody uczenia się rang](https://plg.uwaterloo.ca/~gvcormac/cormacsigir09-rrf.pdf) — artykuł RRF.
- [Khattab i Zaharia (2020). ColBERT: Wydajne i skuteczne wyszukiwanie fragmentów](https://arxiv.org/abs/2004.12832) — wyszukiwanie po późnej interakcji.