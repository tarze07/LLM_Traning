# Łączenie i ujednoznacznianie podmiotów

> NER znalazł „Paryż”. Decyduje połączenie podmiotów: Paryż, Francja? Paryż Hilton? Paryż, Teksas? Paryż (książę trojański)? Bez linków wykres wiedzy pozostanie niejednoznaczny.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 06 (NER), Faza 5 · 24 (Uchwała współodniesienia)
**Czas:** ~60 minut

## Problem

Zdanie brzmi: „Jordan pokonał prasę”. Twój NER oznacza „Jordan” jako PERSON. Dobry. Ale *która* Jordania?

- Michael Jordan (koszykówka)?
- Michael B. Jordan (aktor)?
- Michael I. Jordan (profesor ML w Berkeley — tak, to zamieszanie jest prawdziwe w artykułach ML)?
- Jordania (kraj)?
- Jordan (imię hebrajskie)?

Łączenie jednostek (EL) powoduje, że każda wzmianka jest unikalnym wpisem w bazie wiedzy: Wikidata, Wikipedia, DBpedia lub KB Twojej domeny. Dwa podzadania:

1. **Generacja kandydatów.** Biorąc pod uwagę „Jordan”, które wpisy KB są wiarygodne?
2. **Ujednoznacznienie.** Biorąc pod uwagę kontekst, który kandydat jest właściwy?

Obydwa kroki można się nauczyć. Obydwa są benchmarkiem. Połączony rurociąg jest stabilny od dekady – zmienia się jakość ujednoznaczniacza.

## Koncepcja

![Potok łączenia podmiotów: wzmianka → kandydaci → ujednoznaczniony podmiot](../assets/entity-linking.svg)

**Generowanie kandydatów.** Biorąc pod uwagę formę wzmianki („Jordan”), wyszukaj kandydatów w indeksie aliasów. Słowniki aliasów Wikipedii obejmują większość nazwanych podmiotów: „JFK” → John F. Kennedy, Jacqueline Kennedy, lotnisko JFK, JFK (film). Typowy indeks zwraca 10–30 kandydatów na wzmiankę.

**Ujednoznacznienie: trzy podejścia.**

1. **Wstęp + kontekst (Milne & Witten, 2008).** `P(entity | mention) × context-similarity(entity, text)`. Działa dobrze, szybko, bez szkolenia.
2. **Oparta na osadzaniu (ESS / REL / Blink).** Zakoduj wzmiankę + kontekst. Zakoduj opis każdego kandydata. Wybierz maksymalny cosinus. Wartość domyślna na lata 2020–2024.
3. **Generatywny (GENRE, 2021; oparty na LLM, 2023+).** Dekoduj nazwę kanoniczną podmiotu, token po tokenie. Ograniczone do próby prawidłowych nazw jednostek, więc gwarantowane jest, że dane wyjściowe będą prawidłowym identyfikatorem KB.

**Kompleksowe a potokowe.** Nowoczesne modele (ELQ, BLINK, ExtEnD, GENRE) obsługują NER + generowanie kandydatów + ujednoznacznienie w jednym przebiegu. W produkcji nadal dominują systemy rurociągów, ponieważ można wymieniać komponenty.

### Dwa pomiary

- **Przypomnienie wzmianki (kandydat gen).** Ułamek złota wskazuje, gdzie na liście kandydatów pojawia się prawidłowy wpis KB. Podłoga całego rurociągu.
- **Dokładność ujednoznacznienia / F1.** Biorąc pod uwagę poprawnych kandydatów, jak często pierwsza 1 ma rację.

Zawsze zgłaszaj oba. System zapewniający 99% ujednoznacznienia przy 80% odwołaniu kandydata to 80% rurociągu.

## Zbuduj to

### Krok 1: zbuduj indeks aliasów na podstawie przekierowań Wikipedii

```python
alias_to_entities = {
    "jordan": ["Q41421 (Michael Jordan)", "Q810 (Jordan, country)", "Q254110 (Michael B. Jordan)"],
    "paris":  ["Q90 (Paris, France)", "Q663094 (Paris, Texas)", "Q55411 (Paris Hilton)"],
    "apple":  ["Q312 (Apple Inc.)", "Q89 (apple, fruit)"],
}
```

Dane aliasów w Wikipedii: ~18 milionów par (alias, jednostka). Pobierz ze zrzutów Wikidanych. Zapisz jako odwrócony indeks.

### Krok 2: ujednoznacznienie w oparciu o kontekst

```python
def disambiguate(mention, context, alias_index, entity_desc):
    candidates = alias_index.get(mention.lower(), [])
    if not candidates:
        return None, 0.0
    context_words = set(tokenize(context))
    best, best_score = None, -1
    for entity_id in candidates:
        desc_words = set(tokenize(entity_desc[entity_id]))
        union = len(context_words | desc_words)
        score = len(context_words & desc_words) / union if union else 0.0
        if score > best_score:
            best, best_score = entity_id, score
    return best, best_score
```

Nakładka Jaccard to zabawka. Zamień na cosinus podobieństwo w przypadku osadzania (patrz `code/main.py` krok 2 dla wersji transformatora).

### Krok 3: osadzanie (w stylu BLINK)

```python
from sentence_transformers import SentenceTransformer
encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_mention(text, mention_span):
    start, end = mention_span
    marked = f"{text[:start]} [MENTION] {text[start:end]} [/MENTION] {text[end:]}"
    return encoder.encode([marked], normalize_embeddings=True)[0]

def embed_entity(entity_id, description):
    return encoder.encode([f"{entity_id}: {description}"], normalize_embeddings=True)[0]
```

W czasie indeksowania osadzaj raz każdą jednostkę KB. W czasie zapytania osadź raz wzmiankę + kontekst, iloczyn kropkowy w stosunku do puli kandydatów, wybierz max.

### Krok 4: łączenie encji generatywnych (koncepcja)

GATUNEK dekoduje tytuł podmiotu w Wikipedii znak po znaku. Ograniczone dekodowanie (zobacz lekcję 20) gwarantuje, że na wyjściu mogą zostać wygenerowane tylko prawidłowe tytuły. Ścisła integracja z próbą wspieraną przez KB. Współczesnym potomkiem jest EL oparty na REL-GEN i LLM z ustrukturyzowanym wyjściem.

```python
prompt = f"""Text: {text}
Mention: {mention}
List the best Wikipedia title for this mention.
Respond with JSON: {{"title": "..."}}"""
```

W połączeniu z białą listą (Outlines `choice`) jest to najprostszy rurociąg EL do wysyłki w 2026 r.

### Krok 5: ocena na AIDA-CoNLL

AIDA-CoNLL to standardowy benchmark EL: 1393 artykuły Reuters, 34 tys. wzmianek, wpisy w Wikipedii. Zgłaszaj dokładność w KB (`P@1`) i współczynnik wykrywania NIL poza KB.

## Pułapki

- **Obsługa NIL.** Niektóre wzmianki nie znajdują się w KB (powstające podmioty, nieznani ludzie). Systemy muszą przewidzieć NIL, zamiast zgadywać niewłaściwą jednostkę. Mierzone osobno.
- **Wspomnij o błędach granic.** NER w górnym biegu rzeki nie obejmuje częściowych zakresów („Bank of America” oznaczony jako po prostu „Bank”). Spada przywołanie EL.
- **Błąd popularności.** Wytrenowane systemy nadmiernie przewidują częste jednostki. Wzmianka o „Michaelu I. Jordanie” w gazecie ML często nawiązuje do koszykarskiej Jordanii.
- **Międzyjęzyczny EL.** Mapowanie wzmianek w tekście chińskim na jednostki angielskiej Wikipedii. Wymaga wielojęzycznego kodera lub etapu tłumaczenia.
- **Nieaktualność KB.** Nowych firm, wydarzeń, ludzi nie ma w zeszłorocznym zrzucie Wikipedii. Rurociągi produkcyjne wymagają pętli odświeżania.

## Użyj tego

Stos na rok 2026:

| Sytuacja | Wybierz |
|----------|------|
| Angielski ogólnego przeznaczenia + Wikipedia | MIGA lub REL |
| Międzyjęzykowe, KB = Wikipedia | mgatunek |
| Przyjazny dla LLM, kilka wzmianek/dzień | Podpowiedz Claude/GPT-4 z listą kandydatów + ograniczonym JSON |
| KB specyficzne dla domeny (medyczne, prawne) | Niestandardowy BERT z wyszukiwaniem uwzględniającym KB + dostrojenie zestawu w stylu AIDA domeny |
| Wyjątkowo małe opóźnienia | Tylko wcześniejsze dopasowanie dokładne (linia bazowa Milne-Witten) |
| Badania SOTA | GATUNEK / ExtEnD / generatywny LLM-EL |

Schemat produkcji, który będzie dostępny w 2026 r.: NER → coref → EL przy każdej wzmiance → zwiń klastry do jednej jednostki kanonicznej na klaster. Dane wyjściowe: jeden identyfikator KB na jednostkę w dokumencie, a nie jeden na wzmiankę.

## Wyślij to

Zapisz jako `outputs/skill-entity-linker.md`:

```markdown
---
name: entity-linker
description: Design an entity linking pipeline — KB, candidate generator, disambiguator, evaluation.
version: 1.0.0
phase: 5
lesson: 25
tags: [nlp, entity-linking, knowledge-graph]
---

Given a use case (domain KB, language, volume, latency budget), output:

1. Knowledge base. Wikidata / Wikipedia / custom KB. Version date. Refresh cadence.
2. Candidate generator. Alias-index, embedding, or hybrid. Target mention recall @ K.
3. Disambiguator. Prior + context, embedding-based, generative, or LLM-prompted.
4. NIL strategy. Threshold on top score, classifier, or explicit NIL candidate.
5. Evaluation. Mention recall @ 30, top-1 accuracy, NIL-detection F1 on held-out set.

Refuse any EL pipeline without a mention-recall baseline (you cannot evaluate a disambiguator without knowing candidate gen surfaced the right entity). Refuse any pipeline using LLM-prompted EL without constrained output to valid KB ids. Flag systems where popularity bias affects minority entities (e.g. name-clashes) without domain fine-tuning.
```

## Ćwiczenia

1. **Łatwe.** Zaimplementuj ujednoznacznienie wcześniejszego+kontekstu w `code/main.py` na 10 niejednoznacznych wzmiankach (Paryż, Jordania, Apple). Ręcznie oznacz właściwy element. Zmierz dokładność.
2. **Średni.** Zakoduj 50 niejednoznacznych wzmianek za pomocą transformatora zdań. Umieść opis każdego kandydata. Porównaj ujednoznacznienie oparte na osadzaniu z nakładaniem się kontekstu Jaccard.
3. **Trudne.** Zbuduj domenę KB zawierającą 1 tys. podmiotów (np. pracownicy + produkty w Twojej firmie). Kompleksowe wdrożenie NER + EL. Zmierz precyzję i przypomnij sobie 100 odrzuconych zdań.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Łączenie jednostek (EL) | Link do Wikipedii | Przypisz wzmiankę do unikalnego wpisu bazy wiedzy. |
| Pokolenie kandydatów | Kto to może być? | Zwróć krótką listę wiarygodnych wpisów KB, aby uzyskać wzmiankę. |
| Ujednoznacznienie | Wybierz właściwy | Oceniaj kandydatów na podstawie kontekstu i wybierz zwycięzcę. |
| Indeks aliasów | Tabela przeglądowa | Mapa z formy powierzchniowej → podmioty kandydujące. |
| NIL | Nie w KB | Jawne przewidywanie, że żaden wpis KB nie pasuje. |
| KB | Baza wiedzy | Wikidane, Wikipedia, DBpedia lub Twoja domena KB. |
| AIDA-ConLL | Punkt odniesienia | 1393 artykuły Reutersa z linkami do złotych podmiotów. |

## Dalsze czytanie

- [Milne, Witten (2008). Nauka łączenia z Wikipedią](https://www.cs.waikato.ac.nz/~ihw/papers/08-DM-IHW-LearningToLinkWithWikipedia.pdf) — podstawowe podejście oparte na wcześniejszym kontekście.
- [Wu i in. (2020). Zero-shot Entity Linking with Dense Entity Retrieval (BLINK)](https://arxiv.org/abs/1911.03814) — narzędzie oparte na osadzaniu.
- [De Cao i in. (2021). Autoregresywne pobieranie jednostek (GENRE)](https://arxiv.org/abs/2010.00904) — generatywne EL z ograniczonym dekodowaniem.
- [Hoffart i in. (2011). Solidne ujednoznacznienie nazwanych podmiotów w tekście (AIDA)](https://www.aclweb.org/anthology/D11-1072.pdf) — dokument porównawczy.
- [REL: An Entity Linker Standing on the Shoulders of Giants (2020)](https://arxiv.org/abs/2006.01969) — otwarty stos produkcyjny.