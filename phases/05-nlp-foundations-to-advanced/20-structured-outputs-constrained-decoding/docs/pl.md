# Ustrukturyzowane wyniki i ograniczone dekodowanie

> Zapytaj LLM o JSON. Pobieraj JSON przez większość czasu. W produkcji problemem jest „większość”. Ograniczone dekodowanie zamienia „większość” w „zawsze” poprzez edycję logitów przed próbkowaniem.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 17 (Chatboty), Faza 5 · 19 (Tokenizacja słów podrzędnych)
**Czas:** ~60 minut

## Problem

Klasyfikator podpowiada LLM: „Zwróć jeden z {pozytywny, negatywny, neutralny}”. Model zwraca „Nastroje są pozytywne — ta recenzja jest w przeważającej mierze korzystna, ponieważ klient wyraźnie stwierdza, że…”. Twój analizator ulega awarii. F1 Twojego klasyfikatora wynosi 0,0.

Generowanie w dowolnej formie nie jest umową. To jest sugestia. System produkcyjny wymaga kontraktu.

W roku 2026 istnieją trzy warstwy.

1. **Podpowiadanie.** Ładnie poproś. „Zwróć tylko obiekt JSON.” Działa ~80% na modelach frontierowych, mniej na mniejszych.
2. **Natywne interfejsy API do strukturalnych wyników wyjściowych.** OpenAI `response_format`, użycie narzędzi Anthropic, tryb Gemini JSON. Niezawodny na obsługiwanych schematach. Blokada dostawcy.
3. **Ograniczone dekodowanie.** Modyfikuj logity na każdym etapie generowania, aby model *nie* mógł emitować nieprawidłowych tokenów. 100% ważne konstrukcyjnie. Działa na każdym modelu lokalnym.

Ta lekcja buduje intuicję dla wszystkich trzech i pomaga określić, kiedy po które sięgnąć.

## Koncepcja

![Ograniczone dekodowanie maskuje nieprawidłowe tokeny na każdym kroku](../assets/constrained-decoding.svg)

**Jak działa dekodowanie z ograniczeniami.** Na każdym etapie generowania LLM generuje wektor logitowy dla całego słownictwa (~100 tys. tokenów). *Procesor logitowy* znajduje się pomiędzy modelem a próbnikiem. Oblicza, które tokeny są prawidłowe, biorąc pod uwagę bieżącą pozycję w gramatyce docelowej — schemat JSON, wyrażenie regularne, gramatyka bezkontekstowa — i ustawia logity wszystkich nieprawidłowych tokenów na ujemną nieskończoność. Softmax na pozostałych logitach umieszcza masę prawdopodobieństwa tylko na prawidłowych kontynuacjach.

Realizacje w 2026 roku:

- **Kontury.** Kompiluje schemat JSON lub wyrażenie regularne na maszynę o skończonych stanach. Każdy token otrzymuje wyszukiwanie O(1) prawidłowego następnego tokenu. Oparte na FSM, więc schematy rekurencyjne wymagają spłaszczenia.
- **XGramatyka / wskazówki.** Bezkontekstowe silniki gramatyczne. Obsługa rekurencyjnego schematu JSON. Prawie zerowy narzut na dekodowanie. OpenAI przyznało wsparcie w zakresie wdrażania ustrukturyzowanych wyników do roku 2025.
- **Dekodowanie sterowane vLLM.** Wbudowane `guided_json`, `guided_regex`, `guided_choice`, `guided_grammar` poprzez backendy Outlines, XGrammar lub lm-format-enforcer.
- **Instruktor.** Opakowanie oparte na Pythonie dla dowolnego LLM. Ponawia próbę w przypadku niepowodzenia sprawdzania poprawności. Między dostawcami, ale nie modyfikuje logów — opiera się na ponownych próbach i podpowiedziach uwzględniających uporządkowane dane wyjściowe.

### Wynik sprzeczny z intuicją

Dekodowanie z ograniczeniami jest często *szybsze* niż generowanie bez ograniczeń. Dwa powody. Po pierwsze, zmniejsza przestrzeń wyszukiwania następnego tokenu. Po drugie, sprytne implementacje całkowicie pomijają generowanie tokenów w przypadku tokenów wymuszonych (rusztowanie takie jak `{"name": "` — określany jest każdy bajt).

### Pułapka, która Cię kosztuje

Kolejność w terenie ma znaczenie. Umieść `answer` przed `reasoning`, a model zatwierdzi odpowiedź, zanim pomyśli. JSON jest prawidłowy. Odpowiedź jest błędna. Żadna walidacja tego nie łapie.

```json
// BAD
{"answer": "yes", "reasoning": "because ..."}

// GOOD
{"reasoning": "... therefore ...", "answer": "yes"}
```

Kolejność pól schematu jest logiczna, a nie formatowana.

## Zbuduj to

### Krok 1: generowanie od podstaw ograniczonego wyrażenia regularnego

Zobacz `code/main.py`, aby zapoznać się z samodzielną implementacją FSM. Podstawowa idea w 30 linijkach:

```python
def mask_logits(logits, valid_token_ids):
    mask = [float("-inf")] * len(logits)
    for tid in valid_token_ids:
        mask[tid] = logits[tid]
    return mask

def generate_constrained(model, tokenizer, prompt, fsm):
    ids = tokenizer.encode(prompt)
    state = fsm.initial_state
    while not fsm.is_accept(state):
        logits = model.next_token_logits(ids)
        valid = fsm.valid_tokens(state, tokenizer)
        logits = mask_logits(logits, valid)
        tok = sample(logits)
        ids.append(tok)
        state = fsm.transition(state, tok)
    return tokenizer.decode(ids)
```

FSM śledzi, jakie części gramatyki spełniliśmy do tej pory. `valid_tokens(state, tokenizer)` oblicza, które tokeny słownictwa mogą przyspieszyć FSM bez opuszczania ścieżki akceptacji.

### Krok 2: Konspekty schematu JSON

```python
from pydantic import BaseModel
from typing import Literal
import outlines

class Review(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float
    evidence_span: str

model = outlines.models.transformers("meta-llama/Llama-3.2-3B-Instruct")
generator = outlines.generate.json(model, Review)

result = generator("Classify: 'The wait staff was attentive and the food arrived hot.'")
print(result)
# Review(sentiment='positive', confidence=0.93, evidence_span='attentive ... hot')
```

Zero błędów walidacyjnych. Kiedykolwiek. FSM sprawia, że ​​nieprawidłowe dane wyjściowe są nieosiągalne.

### Krok 3: Instruktor dla Pydantic niezależnego od dostawcy

```python
import instructor
from anthropic import Anthropic
from pydantic import BaseModel, Field

class Invoice(BaseModel):
    vendor: str
    total_usd: float = Field(ge=0)
    line_items: list[str]

client = instructor.from_anthropic(Anthropic())
invoice = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    response_model=Invoice,
    messages=[{"role": "user", "content": "Extract from: 'Acme Corp $420. Widget, Gizmo.'"}],
)
```

Inny mechanizm. Instruktor nie dotyka logitów. Formatuje schemat do znaku zachęty, analizuje dane wyjściowe i ponawia próbę w przypadku niepowodzenia sprawdzania poprawności (domyślnie 3 razy). Współpracuje z każdym dostawcą. Ponowne próby zwiększają opóźnienia i koszty. Zaletą jest możliwość przenoszenia między dostawcami.

### Krok 4: API natywnego dostawcy

```python
from openai import OpenAI

client = OpenAI()
response = client.responses.create(
    model="gpt-5",
    input=[{"role": "user", "content": "Classify: 'The food was cold.'"}],
    text={"format": {"type": "json_schema", "name": "sentiment",
          "schema": {"type": "object", "required": ["sentiment"],
                     "properties": {"sentiment": {"type": "string",
                                                  "enum": ["positive", "negative", "neutral"]}}}}},
)
print(response.output_parsed)
```

Dekodowanie ograniczone po stronie serwera. Parytet niezawodności z zarysami dla obsługiwanych schematów. Brak lokalnego zarządzania modelami. Blokuje Cię dla dostawcy.

## Pułapki

- **Schematy rekursywne.** Kontury spłaszczają rekurencję do ustalonej głębokości. Wyniki o strukturze drzewa (komentarze zagnieżdżone, AST) wymagają XGrammar lub llguidance (oparte na CFG).
- **Ogromne wyliczenia.** Wyliczenie 10 000 opcji kompiluje się powoli lub przekroczono limit czasu. Przejdź na retrievera: najpierw przewidź kandydatów z najwyższej półki i ogranicz się do nich.
- **Gramatyka zbyt rygorystyczna.** Wymuś wyrażenie regularne `date: "YYYY-MM-DD"`, a model nie będzie mógł wyprowadzić `"unknown"` w przypadku brakujących dat. Modelka rekompensuje to wymyślając datę. Zezwól na `null` lub strażnika.
- **Przedwczesne zaangażowanie.** Zobacz pułapkę dotyczącą zamówień terenowych powyżej. Zawsze na pierwszym miejscu stawiaj rozumowanie.
- **Tryb JSON dostawcy bez schematu.** Tryb czystego JSON gwarantuje tylko prawidłowy JSON, a nie ważny *w Twoim przypadku użycia*. Zawsze podawaj pełny schemat.

## Użyj tego

Stos na rok 2026:

| Sytuacja | Wybierz |
|----------|------|
| Model OpenAI/Anthropic/Google, prosty schemat | Ustrukturyzowane dane wyjściowe dostawcy natywnego |
| Każdy dostawca, przepływ pracy Pydantic, może tolerować ponowne próby | Instruktor |
| Model lokalny, wymaga 100% trafności, schemat płaski | Kontury (FSM) |
| Model lokalny, schemat rekurencyjny | XGramatyka lub wskazówki |
| Własny serwer wnioskowania | Dekodowanie sterowane vLLM |
| Przetwarzanie wsadowe z dopuszczalnymi ponownymi próbami | Instruktor + najtańszy model |

## Wyślij to

Zapisz jako `outputs/skill-structured-output-picker.md`:

```markdown
---
name: structured-output-picker
description: Choose a structured output approach, schema design, and validation plan.
version: 1.0.0
phase: 5
lesson: 20
tags: [nlp, llm, structured-output]
---

Given a use case (provider, latency budget, schema complexity, failure tolerance), output:

1. Mechanism. Native vendor structured output, Instructor retries, Outlines FSM, or XGrammar CFG. One-sentence reason.
2. Schema design. Field order (reasoning first, answer last), nullable fields for "unknown", enum vs regex, required fields.
3. Failure strategy. Max retries, fallback model, graceful `null` handling, out-of-distribution refusal.
4. Validation plan. Schema compliance rate (target 100%), semantic validity (LLM-judge), field-coverage rate, latency p50/p99.

Refuse any design that puts `answer` or `decision` before reasoning fields. Refuse to use bare JSON mode without a schema. Flag recursive schemas behind an FSM-only library.
```

## Ćwiczenia

1. **Łatwe.** Wyświetl mały model z otwartymi ciężarami (np. Llama-3.2-3B) bez ograniczonego dekodowania dla `Review(sentiment, confidence, evidence_span)`. Zmierz ułamek, który jest analizowany jako prawidłowy JSON w 100 recenzjach.
2. **Średni.** Ten sam korpus w trybie Outlines JSON. Porównaj współczynnik zgodności, opóźnienia i dokładność semantyczną.
3. **Trudne.** Zaimplementuj od podstaw dekoder z ograniczeniami wyrażeń regularnych dla numerów telefonów (`\d{3}-\d{3}-\d{4}`). Zweryfikuj 0 nieprawidłowych wyników na 1000 próbek.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Ograniczone dekodowanie | Wymuś prawidłowe wyjście | Maskuj nieprawidłowe logity tokenów na każdym etapie generowania. |
| Procesor logitowy | Rzecz, która ogranicza | Funkcja: `(logits, state) -> masked_logits`. |
| FSM | Maszyna o skończonych stanach | Skompilowana reprezentacja gramatyczna; O(1) wyszukiwanie prawidłowego następnego tokenu. |
| CFG | Gramatyka bezkontekstowa | Gramatyka obsługująca rekurencję; wolniejszy, ale bardziej wyrazisty niż FSM. |
| Kolejność pól schematu | Czy to ma znaczenie? | Tak — zatwierdzenie pierwszego pola; zawsze przed odpowiedzią umieszczaj uzasadnienie. |
| Dekodowanie z przewodnikiem | nazwa vLLM | Ta sama koncepcja zintegrowana z serwerem wnioskowania. |
| Tryb JSON | Wczesna wersja OpenAI | Gwarantuje składnię JSON; NIE gwarantuje zgodności schematu. |

## Dalsze czytanie

- [Willard, Louf (2023). Efektywne generowanie kierowane dla LLM](https://arxiv.org/abs/2307.09702) – dokument Outlines.
- [Artykuł XGrammar (2024)](https://arxiv.org/abs/2411.15100) — szybkie, ograniczone dekodowanie oparte na CFG.
- [vLLM — Structured Outputs](https://docs.vllm.ai/en/latest/features/structured_outputs.html) — integracja serwera wnioskowania.
- [OpenAI — przewodnik po uporządkowanych wynikach](https://platform.openai.com/docs/guides/structured-outputs) — Informacje o API + gotchas.
- [Biblioteka instruktorów](https://python.useinstructor.com/) — Pydantic + ponowne próby u różnych dostawców.
- [JSONSchemaBench (2025)](https://arxiv.org/abs/2501.10868) — analiza porównawcza 6 struktur dekodowania z ograniczeniami.