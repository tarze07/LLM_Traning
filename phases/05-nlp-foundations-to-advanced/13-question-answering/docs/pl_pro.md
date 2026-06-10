# Systemy odpowiadania na pytania

> Trzy systemy ukształtowały współczesne podejście do odpowiadania na pytania (QA). Ekstrakcyjne lokalizują fragmenty odpowiedzi. Wspomagane wyszukiwaniem zakotwiczają odpowiedzi w dokumentach. Generatywne tworzą odpowiedzi od podstaw. Każdy nowoczesny asystent AI stanowi połączenie tych trzech podejść.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 11 (tłumaczenie maszynowe), Faza 5 · 10 (mechanizm uwagi)
**Czas:** ~75 minut

## Problem

Użytkownik pisze: „Kiedy pojawił się pierwszy iPhone?" i oczekuje odpowiedzi „29 czerwca 2007 r." — nie ogólnikowego stwierdzenia „Historia Apple jest długa i zróżnicowana", ani samego roku bez kontekstu. Liczy się odpowiedź bezpośrednia, uzasadniona i poprawna.

W ciągu ostatniej dekady w dziedzinie QA dominowały trzy architektury.

- **Wyodrębniające QA.** Mając dane pytanie i fragment tekstu, w którym z góry wiadomo, że znajduje się odpowiedź, zadaniem systemu jest znalezienie indeksów początku i końca odpowiedzi w tym fragmencie. Zbiór SQuAD stanowi kanoniczny punkt odniesienia.
- **QA w otwartej domenie.** Fragment tekstu nie jest z góry podany. System musi najpierw pobrać odpowiedni fragment, a następnie wyodrębnić lub wygenerować odpowiedź. To podejście stanowi fundament współczesnych potoków RAG.
- **Generatywne QA / QA z zamkniętą księgą.** Duży model językowy odpowiada wyłącznie na podstawie wiedzy zakodowanej w swoich wagach, bez etapu wyszukiwania. Najszybsze podczas wnioskowania, lecz najmniej wiarygodne pod względem faktograficznym.

Dominującym trendem w 2026 roku jest podejście hybrydowe: pobranie kilku najlepszych fragmentów, a następnie zlecenie modelowi generatywnemu udzielenia odpowiedzi na ich podstawie. To właśnie RAG — lekcja 14 szczegółowo omawia wyszukiwanie. Niniejsza lekcja buduje część odpowiedzialną za QA.

## Koncepcja

![Architektury QA: wyodrębniająca, wspomagana wyszukiwaniem, generatywna](../assets/qa.svg)

**Ekstrakcyjne QA.** Pytanie i fragment są razem kodowane przez transformer (rodzina BERT). Trenowane są dwie głowice przewidujące indeksy tokenów początku i końca odpowiedzi. Funkcją straty jest entropia krzyżowa na tych pozycjach, a wyjściem — zakres tekstu z fragmentu. Model nie halucynuje ze względu na swoją konstrukcję i nie odpowiada na pytania, na które fragment nie daje odpowiedzi.

**QA wspomagane wyszukiwaniem (RAG).** Architektura dwuetapowa. W pierwszym etapie retriever wyszukuje `k` najbardziej trafnych fragmentów z korpusu. W drugim etapie czytelnik (ekstrakcyjny lub generatywny) formułuje odpowiedź na podstawie tych fragmentów. Rozdzielenie retrievera od czytelnika umożliwia niezależne trenowanie i ocenę każdego z komponentów. Współczesny RAG często dodaje między nimi etap rerankingu.

**Generatywne QA.** Modele językowe oparte wyłącznie na dekoderze (GPT, Claude, Llama) udzielają odpowiedzi na podstawie wyuczonych wag. Nie ma tu etapu wyszukiwania. Sprawdzają się znakomicie w przypadku powszechnej wiedzy, natomiast zawodzą przy rzadkich lub aktualnych faktach. Częstość halucynacji jest odwrotnie skorelowana z częstością występowania danego faktu w danych przedtreningowych.

## Zbuduj to

### Krok 1: ekstrakcyjne QA z wstępnie wytrenowanym modelem

```python
from transformers import pipeline

qa = pipeline("question-answering", model="deepset/roberta-base-squad2")

passage = (
    "Apple Inc. released the first iPhone on June 29, 2007. "
    "The device was announced by Steve Jobs at Macworld in January 2007."
)
question = "When was the first iPhone released?"

answer = qa(question=question, context=passage)
print(answer)
```

```python
{'score': 0.98, 'start': 57, 'end': 70, 'answer': 'June 29, 2007'}
```

Model `deepset/roberta-base-squad2` jest trenowany na zbiorze SQuAD 2.0, który zawiera również pytania bez odpowiedzi. Domyślnie potok `question-answering` zwraca zakres o najwyższym wyniku, nawet jeśli model preferuje wynik zerowy — *nie* zwraca automatycznie pustej odpowiedzi. Aby uzyskać jawne zachowanie „brak odpowiedzi", należy przekazać `handle_impossible_answer=True` do wywołania potoku: wówczas pusta odpowiedź jest zwracana tylko wtedy, gdy wynik zerowy przewyższa każdy wynik zakresu. W obu przypadkach warto zawsze sprawdzać pole `score`.

### Krok 2: potok wspomagany wyszukiwaniem (zarys)

```python
from sentence_transformers import SentenceTransformer
import numpy as np

encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

corpus = [
    "Apple Inc. released the first iPhone on June 29, 2007.",
    "Macworld 2007 featured the iPhone announcement by Steve Jobs.",
    "Android launched in 2008 as Google's mobile operating system.",
    "The first iPod was released in 2001.",
]
corpus_embeddings = encoder.encode(corpus, normalize_embeddings=True)

def retrieve(question, top_k=2):
    q_emb = encoder.encode([question], normalize_embeddings=True)
    sims = (corpus_embeddings @ q_emb.T).squeeze()
    order = np.argsort(-sims)[:top_k]
    return [corpus[i] for i in order]

def answer(question):
    passages = retrieve(question, top_k=2)
    combined = " ".join(passages)
    return qa(question=question, context=combined)

print(answer("When was the first iPhone released?"))
```

Potok jest dwuetapowy. Gęsty retriever (Sentence-BERT) odnajduje trafne fragmenty na podstawie podobieństwa semantycznego. Ekstrakcyjny czytelnik (RoBERTa-SQuAD) wyznacza zakres odpowiedzi z połączonych najlepszych fragmentów. Rozwiązanie działa sprawnie na małych korpusach. Przy zbiorach liczących milion dokumentów należy użyć biblioteki FAISS lub odpowiedniej bazy wektorowej.

### Krok 3: generatywne QA z RAG

```python
def rag_generate(question, llm):
    passages = retrieve(question, top_k=3)
    prompt = f"""Context:
{chr(10).join('- ' + p for p in passages)}

Question: {question}

Answer using only the context above. If the context does not contain the answer, say "I don't know."
"""
    return llm(prompt)
```

Sposób sformułowania promptu ma istotne znaczenie. Wyraźne polecenie, aby model oparł odpowiedź na podanym kontekście i zwrócił „Nie wiem" w przypadku jego niewystarczalności, zmniejsza częstość halucynacji o 40–60% w porównaniu z naiwnym promptem. Bardziej rozbudowane wzorce dodają cytaty, wskaźniki pewności i strukturyzowaną ekstrakcję.

### Krok 4: ocena odzwierciedlająca warunki produkcyjne

SQuAD stosuje metryki **Exact Match (EM)** oraz **F1 na poziomie tokenów**. EM to ścisłe dopasowanie po normalizacji (zamiana na małe litery, usunięcie interpunkcji i rodzajników) — predykcja albo pasuje dokładnie, albo otrzymuje wynik 0. F1 jest obliczane na podstawie części wspólnej tokenów predykcji i odpowiedzi referencyjnej, przyznając częściowy kredyt. Obie metryki niedoszacowują parafraz: „29 June 2007" vs „June 29, 2007" zazwyczaj daje EM równe 0 (ze względu na różnicę w zapisie liczebnika porządkowego), ale nadal uzyskuje wysokie F1 dzięki wspólnym tokenom.

W systemach QA na środowisku produkcyjnym stosuje się:

- **Dokładność odpowiedzi** (oceniana przez LLM lub człowieka, ponieważ metryki automatyczne nie odzwierciedlają równoważności semantycznej).
- **Dokładność cytowania.** Czy przytoczony fragment rzeczywiście potwierdza udzieloną odpowiedź? Prosta automatyczna weryfikacja polega na sprawdzeniu zgodności wygenerowanych cytatów z pobranymi fragmentami.
- **Kalibracja odmowy.** Czy system poprawnie odpowiada „nie wiem", gdy odpowiedź nie jest obecna w pobranych fragmentach? Miarą oceny jest wskaźnik fałszywej pewności.
- **Recall retrievera.** Przed oceną czytelnika należy sprawdzić, czy retriever poprawnie zwraca właściwy fragment w top-`k`. Czytelnik nie jest w stanie nadrobić brakującego fragmentu.

### RAGAS: framework oceny dla środowisk produkcyjnych w 2026 roku

`RAGAS` został zaprojektowany specjalnie z myślą o systemach RAG i jest domyślnym frameworkiem oceny w 2026 roku. Mierzy cztery wymiary bez konieczności posiadania złotych odpowiedzi referencyjnych:

- **Wierność.** Czy każde twierdzenie zawarte w odpowiedzi wynika z pobranego kontekstu? Mierzona przy użyciu analizy opartej na NLI. To główna metryka halucynacji.
- **Trafność odpowiedzi.** Czy odpowiedź faktycznie odnosi się do zadanego pytania? Mierzona przez generowanie hipotetycznych pytań na podstawie odpowiedzi i porównywanie ich z pytaniem oryginalnym.
- **Precyzja kontekstu.** Jaka część pobranych fragmentów była rzeczywiście istotna? Niska precyzja oznacza szum w prompcie.
- **Recall kontekstu.** Czy pobrane fragmenty zawierały wszystkie potrzebne informacje? Niski recall sprawia, że czytelnik nie może udzielić pełnej odpowiedzi.

Ocena bez referencji umożliwia ewaluację ruchu produkcyjnego na żywo, bez wcześniej przygotowanych złotych odpowiedzi. W przypadku pytań otwartych, gdzie metryki dokładnego dopasowania są nieprzydatne, warto zastosować LLM jako sędziego.

`pip install ragas`. Podłącz swój retriever i czytelnik. Uzyskaj cztery skalary na zapytanie. Ustaw alarm na wypadek regresji.

## Zastosowania

Zestawienie zaleceń na 2026 rok.

| Przypadek użycia | Zalecane rozwiązanie |
|--------|------------|
| Znalezienie zakresu odpowiedzi w danym fragmencie | `deepset/roberta-base-squad2` |
| Praca nad stałym korpusem, tryb zamkniętej księgi niedopuszczalny | RAG: gęsty retriever + czytelnik LLM |
| Praca w czasie rzeczywistym z repozytorium dokumentów | RAG z hybrydowym retrieverem (BM25 + gęsty) i rerankerem (lekcja 14) |
| Konwersacyjne QA (pytania uzupełniające) | LLM z historią rozmowy + RAG w każdej turze |
| Bardzo rzeczowe, regulowane dziedziny | Podejście ekstrakcyjne z autorytatywnego korpusu; nigdy samo generatywne |

Ekstrakcyjne QA traci na popularności w 2026 roku, gdyż RAG z LLM obsługuje więcej przypadków użycia. Pozostaje jednak niezastąpione tam, gdzie wymagane są dosłowne cytaty: badania prawne, zgodność z regulacjami, narzędzia audytowe.

## Wyślij to

Zapisz jako `outputs/skill-qa-architect.md`:

```markdown
---
name: qa-architect
description: Choose QA architecture, retrieval strategy, and evaluation plan.
version: 1.0.0
phase: 5
lesson: 13
tags: [nlp, qa, rag]
---

Given requirements (corpus size, question type, factuality constraint, latency budget), output:

1. Architecture. Extractive, RAG with extractive reader, RAG with generative reader, or closed-book LLM. One-sentence reason.
2. Retriever. None, BM25, dense (name the encoder), or hybrid.
3. Reader. SQuAD-tuned model, LLM by name, or "domain-fine-tuned DistilBERT."
4. Evaluation. EM + F1 for extractive benchmarks; answer accuracy + citation accuracy + refusal calibration for production. Name what you are measuring and how you are measuring it.

Refuse closed-book LLM answers for regulatory or compliance-sensitive questions. Refuse any QA system without a retrieval-recall baseline (you cannot evaluate the reader without knowing the retriever surfaced the right passage). Flag questions that require multi-hop reasoning as needing specialized multi-hop retrievers like HotpotQA-trained systems.
```

## Ćwiczenia

1. **Łatwe.** Skonfiguruj powyższy potok ekstrakcyjny SQuAD na 10 fragmentach z Wikipedii. Przygotuj ręcznie 10 pytań. Zmierz, jak często odpowiedź jest poprawna. Przy czystych fragmentach i pytaniach wynik powinien mieścić się w przedziale 7–9.
2. **Średnie.** Dodaj klasyfikator odmowy. Gdy najwyższy wynik wyszukiwania spada poniżej progu (np. 0,3 podobieństwa kosinusowego), zwróć „Nie wiem" zamiast przekazywać fragment do czytelnika. Dostosuj próg na wydzielonym zbiorze walidacyjnym.
3. **Trudne.** Zbuduj potok RAG na wybranym korpusie 10 000 dokumentów. Zastosuj pobieranie hybrydowe (BM25 + gęste) z fuzją RRF (zob. lekcja 14). Zmierz dokładność odpowiedzi z krokiem hybrydowym i bez niego. Udokumentuj, które typy pytań zyskują najwięcej na tym podejściu.

## Kluczowe terminy

| Termin | Potoczne znaczenie | Właściwe znaczenie |
|------|-----------------|----------------------|
| Ekstrakcyjne QA | Znajdź fragment odpowiedzi | Przewiduj indeksy początku i końca odpowiedzi w danym fragmencie. |
| QA w otwartej domenie | QA na całym korpusie | Fragment nie jest podany z góry; system musi najpierw go pobrać, a potem udzielić odpowiedzi. |
| RAG | Pobierz, potem wygeneruj | Retrieval-Augmented Generation. Potok retriever + czytelnik. |
| SQuAD | Kanoniczny punkt odniesienia | Stanfordzki zbiór danych do odpowiadania na pytania. Metryki EM + F1. |
| Halucynacja | Zmyślona odpowiedź | Dane wyjściowe czytelnika nie są poparte pobranym kontekstem. |
| Kalibracja odmowy | Wiedzieć, kiedy przyznać się do niewiedzy | System poprawnie mówi „nie wiem", gdy nie potrafi udzielić odpowiedzi. |

## Dalsza lektura

- [Rajpurkar i in. (2016). SQuAD: ponad 100 000 pytań do maszynowego rozumienia tekstu](https://arxiv.org/abs/1606.05250) — artykuł opisujący zbiór benchmarkowy.
- [Karpukhin i in. (2020). Dense Passage Retrieval dla QA w otwartej domenie](https://arxiv.org/abs/2004.04906) — DPR, kanoniczny gęsty retriever dla QA.
- [Lewis i in. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) — artykuł, który wprowadził nazwę RAG.
- [Gao i in. (2023). Generowanie wspomagane wyszukiwaniem dla dużych modeli językowych: przegląd](https://arxiv.org/abs/2312.10997) — obszerne opracowanie przeglądowe dotyczące RAG.
