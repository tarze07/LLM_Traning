# Ustrukturyzowane dane wyjściowe i dekodowanie z ograniczeniami (Constrained Decoding)

> Poprosisz model LLM o JSON – w większości przypadków go otrzymasz. W systemach produkcyjnych słowo „większość” stanowi jednak poważny problem. Dekodowanie z ograniczeniami (constrained decoding) zamienia „większość” w „zawsze” poprzez modyfikowanie logitów przed etapem próbkowania.

**Typ:** Projekt
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 17 (Chatboty), Faza 5 · 19 (Tokenizacja podwyrazowa)
**Czas:** ~60 minut

## Problem

Zadajesz modelowi LLM pytanie klasyfikacyjne: „Zwróć jedną z wartości: {pozytywny, negatywny, neutralny}”. Model odpowiada: „Wydźwięk jest pozytywny – ta recenzja jest w przeważającej mierze korzystna, ponieważ klient wyraźnie stwierdza, że...”. Twój parser składniowy ulega awarii, a miara F1 klasyfikatora spada do 0,0.

Generowanie tekstu w formacie wolnym (free-form generation) nie gwarantuje przestrzegania określonego formatu – to jedynie sugestia. Systemy produkcyjne wymagają jednak ścisłego kontraktu.

Obecnie wyróżniamy trzy poziomy rozwiązywania tego problemu:

1. **Prompt engineering (Podpowiadanie):** Zwykła prośba, np. „Zwróć wyłącznie obiekt JSON”. Działa w około 80% przypadków na wiodących modelach komercyjnych (frontier models) i znacznie gorzej na mniejszych modelach lokalnych.
2. **Natywne API do ustrukturyzowanych danych (Structured Outputs):** Funkcje takie jak `response_format` w OpenAI, wywołania narzędzi (tool use) w Anthropic czy tryb JSON w Gemini. Rozwiązanie niezwykle stabilne dla obsługiwanych schematów, lecz wiąże się z uzależnieniem od konkretnego dostawcy (vendor lock-in).
3. **Dekodowanie z ograniczeniami (Constrained decoding):** Modyfikowanie logitów na każdym etapie generowania tokenów, co fizycznie uniemożliwia modelowi wygenerowanie niepoprawnego znaku. Gwarantuje 100% poprawności strukturalnej i działa na każdym lokalnie uruchomionym modelu.

Ta lekcja pozwoli Ci zrozumieć intuicję stojącą za tymi trzema podejściami i pomoże zdecydować, które z nich wybrać do swojego projektu.

## Konceptja

![Dekodowanie z ograniczeniami maskuje niepoprawne tokeny na każdym kroku](../assets/constrained-decoding.svg)

**Jak działa dekodowanie z ograniczeniami.** Na każdym etapie generowania model LLM tworzy wektor logitów dla całego słownika (często ponad 100 000 tokenów). Specjalny *procesor logitów* (logits processor) wtrąca się między model a moduł próbkowania (sampler). Analizuje on, które tokeny są dopuszczalne na danym etapie analizy gramatyki docelowej (np. schematu JSON, wyrażenia regularnego czy gramatyki bezkontekstowej) i ustawia wartości logitów dla wszystkich niedozwolonych tokenów na ujemną nieskończoność (`-inf`). Po nałożeniu funkcji Softmax całe prawdopodobieństwo zostaje rozłożone wyłącznie na poprawne tokeny.

Najpopularniejsze implementacje:

- **Outlines:** Kompiluje schemat JSON lub wyrażenie regularne do postaci automatu skończonego (FSM). Wybór poprawnego kolejnego tokenu odbywa się w czasie O(1). Ze względu na ograniczenia automatów skończonych, struktury rekurencyjne wymagają spłaszczenia.
- **XGrammar / llguidance:** Silniki oparte na gramatykach bezkontekstowych (CFG). W pełni wspierają rekurencyjne schematy JSON przy niemal zerowym narzucie obliczeniowym. Na ich rozwiązaniach bazuje m.in. obsługa ustrukturyzowanych danych wyjściowych w API OpenAI.
- **Dekodowanie sterowane w vLLM (Guided decoding):** Wbudowane parametry `guided_json`, `guided_regex`, `guided_choice` oraz `guided_grammar`, działające pod maską w oparciu o silniki Outlines, XGrammar lub lm-format-enforcer.
- **Instructor:** Lekka biblioteka w Pythonie współpracująca z dowolnym dostawcą LLM. W przypadku niepoprawnego formatu automatycznie ponawia zapytanie (retry). Działa u różnych dostawców, lecz nie modyfikuje logitów w czasie rzeczywistym – opiera się na inżynierii promptów i walidacji odpowiedzi.

### Zaskakujący fakt wydajnościowy

Dekodowanie z ograniczeniami bywa w praktyce *szybsze* niż generowanie swobodne. Wynika to z dwóch powodów. Po pierwsze, zawęża przestrzeń poszukiwań kolejnego tokenu. Po drugie, zaawansowane implementacje potrafią całkowicie pominąć wywołanie modelu dla stałych fragmentów struktury (tzw. rusztowania/boilerplate, np. `{"name": "` – gdzie kolejne znaki są z góry narzucone przez schemat).

### Pułapka logiczna

Kolejność pól w schemacie ma kolosalne znaczenie. Jeśli umieścisz pole `answer` (odpowiedź) przed polem `reasoning` (rozumowanie), model zostanie zmuszony do podania ostatecznej odpowiedzi *zanim* wygeneruje ciąg myślowy. Wyjściowy JSON będzie poprawny składniowo, ale sama odpowiedź może być błędna, a żaden walidator nie wykryje tego błędu logicznego.

Kolejność pól w schemacie to struktura logiczna generowania, a nie tylko estetyka formatowania.

```json
// BŁĘDNIE
{"answer": "yes", "reasoning": "because ..."}

// POPRAWNIE
{"reasoning": "... therefore ...", "answer": "yes"}
```

## Zbuduj to

### Krok 1: Dekodowanie ograniczone wyrażeniem regularnym od podstaw

W pliku `code/main.py` znajdziesz kompletną implementację automatu skończonego (FSM). Oto główna idea przedstawiona w prostym kodzie:

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

Automat (FSM) śledzi postęp dopasowania do zdefiniowanej gramatyki. Funkcja `valid_tokens(state, tokenizer)` wyznacza listę tokenów ze słownika, które pozwalają przejść do kolejnego prawidłowego stanu automatu.

### Krok 2: Użycie biblioteki Outlines do generowania JSON

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

Gwarantuje to 100% poprawności strukturalnej. Dzięki FSM wygenerowanie niepoprawnego formatu jest fizycznie niemożliwe.

### Krok 3: Instructor do walidacji ustrukturyzowanych danych (multi-provider)

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

Działa to na innej zasadzie: biblioteka Instructor nie ingeruje w logity modelu. Automatycznie dołącza schemat do promptu, analizuje odpowiedź i ponawia zapytanie w przypadku błędu walidacji (domyślnie do 3 razy). Rozwiązanie to współpracuje z dowolnym dostawcą API. Choć ponowne próby generują dodatkowy koszt i opóźnienia, kluczową zaletą jest pełna przenaszalność kodu.

### Krok 4: Natywne API dostawcy (OpenAI Structured Outputs)

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

W tym przypadku dekodowanie z ograniczeniami odbywa się po stronie serwera OpenAI. Daje to równie wysoką niezawodność jak Outlines dla obsługiwanych typów schematów, eliminując potrzebę lokalnego uruchamiania modeli, ale uzależnia kod od jednego dostawcy.

## Typowe pułapki

- **Schematy rekurencyjne:** Biblioteka Outlines spłaszcza rekurencję do określonej głębokości. Generowanie struktur drzewiastych (np. zagnieżdżone komentarze, drzewa AST) wymaga użycia silników opartych na gramatykach bezkontekstowych, takich jak XGrammar czy llguidance (opartych na CFG).
- **Zbyt duże listy dopuszczalnych wartości (enums):** Definiowanie enuma z tysiącami opcji drastycznie spowalnia kompilację automatu skończonego lub powoduje błędy przekroczenia limitu czasu (timeout). Lepszym rozwiązaniem jest wcześniejsze wyselekcjonowanie wąskiej listy kandydatów metodą wyszukiwania (retrieval) i ograniczenie wyboru tylko do nich.
- **Zbyt restrykcyjna gramatyka:** Jeśli wymusisz sztywny format daty `YYYY-MM-DD`, a dane wejściowe nie będą jej zawierać, model nie będzie mógł wygenerować odpowiedzi „brak danych”. W efekcie model zostanie zmuszony do zhalucynowania daty. Zawsze dopuszczaj wartości typu `null` lub opcjonalne tokeny awaryjne.
- **Przedwczesna deklaracja odpowiedzi (Premature commitment):** Zmuszenie modelu do podania wyniku przed uzasadnieniem (patrz wyżej). Zawsze projektuj schemat tak, by pole z rozumowaniem/przemyśleniami (reasoning) było generowane jako pierwsze.
- **Tryb JSON bez schematu:** Natywny tryb JSON gwarantuje jedynie poprawność syntaktyczną wyjściowego JSON-a, a nie zgodność z Twoim schematem biznesowym. Zawsze przekazuj dokładną definicję schematu (JSON Schema).

## Rekomendowane podejścia

| Sytuacja | Zalecane rozwiązanie |
|----------|------|
| Modele komercyjne (OpenAI/Anthropic/Gemini), standardowy schemat | Natywne API dostawcy (Structured Outputs) |
| Dowolny dostawca API, integracja z Pydantic, akceptowalne ponowne próby | Biblioteka Instructor |
| Model lokalny, krytyczna niezawodność, płaski schemat | Outlines (FSM) |
| Model lokalny, schemat rekurencyjny (drzewa, AST) | XGrammar lub llguidance (CFG) |
| Własny serwer wnioskowania (inference server) | Wbudowane dekodowanie sterowane w vLLM |
| Przetwarzanie wsadowe (batching) przy niskim budżecie | Instructor + tańszy model pomocniczy |

## Zapisywanie szablonu

Zapisz jako `outputs/skill-structured-output-picker.md`:

```markdown
---
name: structured-output-picker
description: Wybierz metodę generowania ustrukturyzowanych danych, zaprojektuj schemat i określ plan walidacji.
version: 1.0.0
phase: 5
lesson: 20
tags: [nlp, llm, structured-output]
---

Na podstawie wymagań (dostawca, limit opóźnień, złożoność schematu, tolerancja błędów) wygeneruj:

1. Mechanizm: Natywne Structured Outputs dostawcy, automatyczne ponowienia (Instructor), Outlines (FSM) lub XGrammar (CFG) wraz z jednozdaniowym uzasadnieniem.
2. Projekt schematu: Kolejność pól (najpierw rozumowanie/reasoning, na końcu decyzja/answer), obsługa pól opcjonalnych (nullable) dla przypadków nieznanych, definicje enumów i wyrażeń regularnych.
3. Strategia obsługi błędów: Maksymalna liczba prób, model awaryjny (fallback), bezpieczna obsługa wartości `null`, odmowy dla danych spoza dystrybucji.
4. Plan walidacji: Wskaźnik zgodności ze schematem (cel: 100%), poprawność semantyczna (oceniana przez LLM-as-a-judge), stopień wypełnienia pól oraz statystyki opóźnień (p50/p99).

Nigdy nie akceptuj projektów schematów, które umieszczają pola decyzyjne (`answer`, `decision`) przed polami wyjaśniającymi (`reasoning`, `thought`). Zawsze odrzucaj propozycje użycia czystego trybu JSON (bare JSON mode) bez zdefiniowanego schematu. Oznaczaj schematy rekurencyjne jako niekompatybilne z bibliotekami opartymi wyłącznie na FSM.
```

## Ćwiczenia praktyczne

1. **Poziom łatwy:** Przetestuj mały model open-weights (np. Llama-3.2-3B) bez dekodowania z ograniczeniami dla schematu `Review(sentiment, confidence, evidence_span)`. Zmierz odsetek poprawnie sparsowanych obiektów JSON na próbie 100 recenzji.
2. **Poziom średni:** Przeprowadź ten sam test z użyciem biblioteki Outlines. Porównaj stabilność formatu, statystyki opóźnień (latency) oraz poprawność semantyczną odpowiedzi.
3. **Poziom trudny:** Zaimplementuj od podstaw procesor logitów realizujący dekodowanie z ograniczeniami dla numerów telefonów w formacie `\d{3}-\d{3}-\d{4}`. Upewnij się, że na próbie 1000 generowań model nie popełni ani jednego błędu formatu.

## Kluczowe pojęcia

| Termin | Potoczne określenie | Znaczenie precyzyjne |
|------|-----------------|----------------------|
| Dekodowanie z ograniczeniami (Constrained Decoding) | Wymuszenie formatu | Fizyczne blokowanie niepoprawnych tokenów poprzez modyfikowanie logitów na każdym etapie generowania. |
| Procesor logitów (Logits Processor) | Blokada logitów | Obiekt modyfikujący rozkład logitów przed próbkowaniem na podstawie gramatyki: `(logits, state) -> masked_logits`. |
| Automat skończony (FSM) | FSM | Reprezentacja gramatyki skompilowana do postaci grafu przejść; pozwala na sprawdzenie poprawności kolejnego tokenu w czasie O(1). |
| Gramatyka bezkontekstowa (CFG) | CFG | Formalizm gramatyczny wspierający zagnieżdżenia i rekurencję; bardziej elastyczny niż FSM, ale o wyższym koszcie obliczeniowym. |
| Kolejność pól w schemacie | Kolejność generowania | Kluczowy aspekt determinujący proces myślowy modelu. Uporządkowanie pól wpływa na kierunek generowania (zawsze umieszczaj pole `reasoning` przed `answer`). |
| Dekodowanie sterowane (Guided Decoding) | Guided decoding | Określenie stosowane w silniku vLLM dla wbudowanych mechanizmów dekodowania z ograniczeniami. |
| Tryb JSON (JSON Mode) | JSON Mode | Funkcja gwarantująca jedynie poprawność syntaktyczną wyjściowego JSON-a, bez walidacji zgodności z konkretnym schematem. |

## Literatura uzupełniająca

- [Willard & Louf (2023). Efficient Guided Generation for Large Language Models](https://arxiv.org/abs/2307.09702) — praca opisująca podstawy teoretyczne biblioteki Outlines.
- [XGrammar Team (2024). XGrammar: Ultra-fast Context-Free Grammar Integration for Structured LLM Generation](https://arxiv.org/abs/2411.15100) — publikacja dotycząca wydajnej integracji CFG z modelami LLM.
- [Dokumentacja vLLM – Structured Outputs](https://docs.vllm.ai/en/latest/features/structured_outputs.html) — integracja silnika z ograniczeniami w serwerach produkcyjnych.
- [Dokumentacja OpenAI – Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs) — specyfikacja techniczna i ograniczenia natywnego API.
- [Dokumentacja biblioteki Instructor](https://python.useinstructor.com/) — deklaratywne parsowanie Pydantic i mechanizmy ponownych prób.
- [JSONSchemaBench (2025)](https://arxiv.org/abs/2501.10868) — analiza porównawcza 6 struktur dekodowania z ograniczeniami pod kątem wydajności i stabilności.
