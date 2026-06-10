# Systemy odpowiadania na pytania

> Trzy systemy ukształtowały współczesną kontrolę jakości. Ekstrakcyjne znalezione przęsła. Dzięki funkcji wyszukiwania ugruntowano je w dokumentach. Odpowiedzi generowane generatywnie. Każdy nowoczesny asystent AI jest mieszanką tych trzech.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 11 (tłumaczenie maszynowe), Faza 5 · 10 (mechanizm uwagi)
**Czas:** ~75 minut

## Problem

Użytkownik pisze: „Kiedy pojawił się pierwszy iPhone?” i oczekuje „29 czerwca 2007 r.”. Nie „Historia Apple jest długa i zróżnicowana”. Nie „2007” siedzący w izolacji i bez wyroku. Bezpośrednia, uzasadniona i poprawna odpowiedź.

W ciągu ostatniej dekady w kontroli jakości zdominowały trzy architektury.

- **Wyodrębniająca kontrola jakości.** Biorąc pod uwagę pytanie i fragment, o którym wiadomo, że zawiera odpowiedź, znajdź początkowy i końcowy indeks zakresu odpowiedzi w tym fragmencie. SQuAD jest kanonicznym punktem odniesienia.
- **Kontrola jakości w domenie otwartej.** Nie podano fragmentu. Najpierw pobierz odpowiedni fragment, a następnie wyodrębnij lub wygeneruj odpowiedź. Stanowi to podstawę każdego dzisiejszego rurociągu RAG.
- **Generatywna / Kontrola jakości w formie zamkniętej księgi.** Duży model językowy odpowiada na podstawie pamięci parametrycznej. Żadnego odzyskiwania. Najszybszy we wnioskowaniu, najmniej wiarygodny w faktach.

Trend na rok 2026 ma charakter hybrydowy: pobierz kilka najlepszych fragmentów, a następnie poproś model generatywny o udzielenie odpowiedzi na podstawie tych fragmentów. To jest RAG, a lekcja 14 omawia wyszukiwanie w połowie dogłębnie. Ta lekcja buduje połowę kontroli jakości.

## Koncepcja

![Architektury kontroli jakości: wyodrębniająca, wspomagana wyszukiwaniem, generatywna](../assets/qa.svg)

**Wyciąg.** Zakoduj pytanie i fragment razem z transformatorem (rodzina BERT). Trenuj dwie głowy, które przewidują indeksy znaczników początkowych i końcowych odpowiedzi. Strata to entropia krzyżowa na ważnych pozycjach. Wyjście to rozpiętość od przejścia. Nigdy nie ma halucynacji (ze względu na konstrukcję), nigdy nie zadaje pytań, na które fragment nie może odpowiedzieć (ze względu na konstrukcję).

**Wspomagane odzyskiwanie (RAG).** Dwa etapy. Najpierw retriever znajduje górne `k` fragmenty korpusu. Po drugie, czytelnik (wyciągowy lub generatywny) tworzy odpowiedź, korzystając z tych fragmentów. Podział retrievera na czytelnika pozwala na niezależne szkolenie i ocenę każdego z nich. Współczesny RAG często dodaje między nimi zmianę rankingu.

**Generatywny.** Odpowiedzi LLM działające wyłącznie z dekoderem (GPT, Claude, Lama) na podstawie wyuczonych wag. Brak etapu pobierania. Znakomity w świetle powszechnej wiedzy, katastrofalny w przypadku rzadkich lub niedawnych faktów. Częstość halucynacji jest odwrotnie skorelowana z częstotliwością faktów w danych przedtreningowych.

## Zbuduj to

### Krok 1: wyodrębniająca kontrola jakości za pomocą wstępnie wytrenowanego modelu

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

`deepset/roberta-base-squad2` jest przeszkolony w zakresie SQuAD 2.0, który obejmuje pytania bez odpowiedzi. Domyślnie potok `question-answering` zwraca zakres o najwyższym wyniku, nawet jeśli zwycięży wynik zerowy modelu — *nie* automatycznie zwraca pustą odpowiedź. Aby uzyskać wyraźne zachowanie „brak odpowiedzi”, przekaż `handle_impossible_answer=True` do wywołania potoku: potok zwraca następnie pustą odpowiedź tylko wtedy, gdy wynik zerowy przekracza każdy wynik zakresu. Zawsze sprawdzaj pole `score` w dowolny sposób.

### Krok 2: potok wspomagany wyszukiwaniem (szkic)

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

Gazociąg dwustopniowy. Dense retriever (Zdanie-BERT) znajduje odpowiednie fragmenty na podstawie podobieństwa semantycznego. Czytnik ekstrakcyjny (RoBERTa-SQuAD) pobiera zakres odpowiedzi z połączonych górnych fragmentów. Działa na małych korpusach. W przypadku korpusu zawierającego milion dokumentów użyj bazy danych FAISS lub wektorów.

### Krok 3: generatywny z RAG

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

Szybki wzór ma znaczenie. Wyraźne nakazanie modelowi, aby ugruntował się w kontekście i zwrócił „Nie wiem”, gdy kontekst jest niewystarczający, zmniejsza częstość występowania halucynacji o 40–60% w porównaniu z naiwnym podpowiedzią. Bardziej wyszukane wzorce dodają cytaty, wskaźniki pewności i uporządkowaną ekstrakcję.

### Krok 4: ocena odzwierciedlająca świat rzeczywisty

SQuAD używa **Dokładnego dopasowania (EM)** i **F1 na poziomie tokena**. EM jest ścisłym dopasowaniem po normalizacji (małe litery, usuwanie znaków interpunkcyjnych, usuwanie artykułów) — albo przewidywanie pasuje dokładnie, albo daje wynik 0. F1 jest obliczane na podstawie nakładania się tokenów między przewidywaniem i odniesieniem i przyznaje częściowy kredyt. Obie parafrazy z niedostatecznym kredytem: „29 czerwca 2007” vs „29 czerwca 2007” zazwyczaj dają 0 EM (normalizacja łamania liczby porządkowej), ale nadal zarabiają znaczną F1 z nakładających się tokenów.

W przypadku produkcji QA:

- **Dokładność odpowiedzi** (oceniana przez LLM lub przez człowieka, ponieważ metryki nie odzwierciedlają równoważności semantycznej).
- **Dokładność cytowania.** Czy cytowany fragment rzeczywiście potwierdza odpowiedź? Trywialne automatyczne sprawdzanie zgodności ciągów między wygenerowanymi cytatami i pobranymi fragmentami.
- **Kalibracja odmowy.** Jeśli odpowiedzi nie ma w pobranych fragmentach, czy system poprawnie powie „nie wiem”? Zmierz współczynnik fałszywej ufności.
- **Przypomnienie aportowania.** Przed oceną czytnika zmierz, czy aporter prawidłowo przechodzi do góry-`k`. Czytelnik nie może naprawić brakującego fragmentu.

### RAGAS: ramy oceny produkcji na rok 2026

`RAGAS` został stworzony specjalnie dla systemów RAG i będzie domyślnym dostawcą w 2026 r. Ocenia cztery wymiary bez konieczności posiadania złotych referencji:

- **Wierność.** Czy każde twierdzenie w odpowiedzi pochodzi z odzyskanego kontekstu? Mierzone za pomocą analizy opartej na NLI. Twój główny wskaźnik halucynacji.
- **Trafność odpowiedzi.** Czy odpowiedź dotyczy pytania? Mierzone poprzez generowanie hipotetycznych pytań na podstawie odpowiedzi i porównywanie z rzeczywistym pytaniem.
- **Dokładność kontekstu.** Która część z odzyskanych fragmentów była rzeczywiście istotna? Niska precyzja = szum w podpowiedzi.
- **Przypomnienie kontekstu.** Czy pobrany zestaw zawierał wszystkie potrzebne informacje? Niska pamięć = czytelnik nie może odnieść sukcesu.

Punktacja bez referencji umożliwia ocenę ruchu produkcyjnego na żywo bez wyselekcjonowanych złotych odpowiedzi. W przypadku pytań otwartych, w przypadku których wskaźniki dokładnego dopasowania są bezużyteczne, nałóż LLM jako sędzia.

`pip install ragas`. Podłącz swój retriever + czytnik. Uzyskaj cztery skalary na zapytanie. Alarm w przypadku regresji.

## Użyj tego

Stos 2026.

| Przypadek użycia | Polecane |
|--------|------------|
| Biorąc pod uwagę fragment, znajdź zakres odpowiedzi | `deepset/roberta-base-squad2` |
| Nad stałym korpusem, księga zamknięta nie jest akceptowalna | RAG: gęsty retriever + czytnik LLM |
| W czasie rzeczywistym w magazynie dokumentów | RAG z hybrydą (BM25 + gęsty) retriever + reranker (lekcja 14) |
| Kontrola jakości konwersacji (pytania uzupełniające) | LLM z historią rozmów + RAG w każdej turze |
| Bardzo rzeczowe, regulowane domeny | Ekstrakcyjny z autorytatywnego korpusu; nigdy sam generatywny |

Ekstrakcyjna kontrola jakości jest niemodna w 2026 r., ponieważ RAG z LLM obsługuje więcej spraw. Nadal jest dostępny w kontekstach, w których wymagany jest dosłowny cytat: badania prawne, zgodność z przepisami, narzędzia audytu.

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

1. **Łatwo.** Skonfiguruj rurociąg wydobywczy SQuAD powyżej na 10 fragmentach Wikipedii. Rękodzieło 10 pytań. Zmierz, jak często odpowiedź jest prawidłowa. Jeśli fragmenty i pytania są czyste, powinieneś zobaczyć 7-9.
2. **Średni.** Dodaj klasyfikator odmowy. Kiedy najwyższy wynik wyszukiwania jest poniżej progu (powiedzmy 0,3 cosinus), zwróć „Nie wiem” zamiast dzwonić do czytelnika. Dostrój próg na wyciągniętym zestawie.
3. **Trudne.** Zbuduj potok RAG na podstawie wybranego korpusu 10 000 dokumentów. Zastosuj pobieranie hybrydowe (BM25 + gęste) z fuzją RRF (patrz lekcja 14). Zmierz dokładność odpowiedzi z krokiem hybrydowym i bez niego. Udokumentuj, które typy pytań przynoszą największe korzyści.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Ekstrakcyjna kontrola jakości | Znajdź zakres odpowiedzi | Przewiduj indeksy początkowe i końcowe odpowiedzi w danym fragmencie. |
| Kontrola jakości w domenie otwartej | Kontrola jakości korpusu | Brak danego fragmentu; muszę odzyskać, a potem odpowiedzieć. |
| SZARA | Pobierz, a następnie wygeneruj | Generacja wzmocniona wyszukiwaniem. Retriever + potok czytnika. |
| SKŁAD | Punkt odniesienia kanoniczny | Zbiór danych odpowiedzi na pytania Stanforda. Wskaźniki EM + F1. |
| Halucynacja | Zmyślona odpowiedź | Dane wyjściowe czytnika nie są obsługiwane przez pobrany kontekst. |
| Odmowa kalibracji | Wiedz, kiedy się zamknąć | System poprawnie mówi „Nie wiem”, gdy nie może odpowiedzieć. |

## Dalsze czytanie

- [Rajpurkar i in. (2016). SQuAD: ponad 100 000 pytań do maszynowego zrozumienia tekstu](https://arxiv.org/abs/1606.05250) — dokument porównawczy.
- [Karpukhin i in. (2020). Dense Passage Retrieval dla kontroli jakości w otwartej domenie](https://arxiv.org/abs/2004.04906) — DPR, kanoniczny gęsty moduł pobierania dla kontroli jakości.
- [Lewis i in. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) — artykuł, który nazwał RAG.
- [Gao i in. (2023). Generowanie wspomagane wyszukiwaniem dla modeli wielkojęzycznych: ankieta](https://arxiv.org/abs/2312.10997) — obszerna ankieta RAG.