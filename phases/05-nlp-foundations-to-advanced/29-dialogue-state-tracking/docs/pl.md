# Śledzenie stanu dialogu

> „Chcę taniej restauracji na północy… właściwie to uczynić ją umiarkowaną… i dodać włoską”. Trzy tury, trzy aktualizacje stanu. Czas letni synchronizuje wartość przedziału czasowego, dzięki czemu rezerwacja działa.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 17 (Chatboty), Faza 5 · 20 (Wyjścia strukturalne)
**Czas:** ~75 minut

## Problem

W systemie dialogu zorientowanego na zadania cel użytkownika jest kodowany jako zbiór par szczelina-wartość: `{cuisine: italian, area: north, price: moderate}`. Każda tura użytkownika może dodać, zmienić lub usunąć miejsce. System musi odczytać całą rozmowę i poprawnie wyświetlić bieżący stan.

Jeśli pomylisz się w jednym miejscu, system zarezerwuje niewłaściwą restaurację, zaplanuje niewłaściwy lot lub obciąży niewłaściwą kartę. DST to zawias między tym, co powiedział użytkownik, a tym, co wykonuje backend.

Dlaczego w 2026 r. nadal ma to znaczenie pomimo LLM:

- Domeny wrażliwe na zgodność (bankowość, opieka zdrowotna, rezerwacje linii lotniczych) wymagają deterministycznych wartości przedziałów czasowych, a nie generowania w dowolnej formie.
— Agenci korzystający z narzędzi nadal wymagają rozpoznania szczeliny przed wywołaniem interfejsów API.
- Korekta wieloobrotowa jest trudniejsza niż się wydaje: „właściwie nie, zrób to w czwartek”.

Nowoczesny rurociąg: klasyczne koncepcje DST + ekstraktory LLM + poręcze o strukturalnym wyjściu.

## Koncepcja

![DST: historia okien dialogowych → stan wartości przedziału](../assets/dst.svg)

**Struktura zadań.** Schemat definiuje domeny (restauracja, hotel, taksówka) i ich przedziały (kuchnia, powierzchnia, cena, ludzie). Każde pole może być puste, wypełnione wartością ze zbioru zamkniętego (cena: {tanie, umiarkowane, drogie}) lub dowolną wartością (nazwa: „Miedziany Czajnik”).

**Dwa preparaty DST.**

- **Klasyfikacja.** Dla każdej pary (slot, wartość_kandydata) przewiduj tak/nie. Działa w przypadku automatów z zamkniętymi słownictwami. Standard sprzed 2020 r.
- **Generacja.** Biorąc pod uwagę dialog, wygeneruj wartości slotów jako dowolny tekst. Działa w przypadku automatów z otwartym słownictwem. Nowoczesne ustawienie domyślne.

**Metryczne.** Dokładność wspólnego celu (JGA) — ułamek tur, w którym *każde* miejsce jest prawidłowe. Wszystko albo nic. Ranking MultiWOZ 2.4 osiąga około 83% w 2026 roku.

**Architektury.**

1. **Oparte na regułach (wyrażenie regularne + słowo kluczowe).** Mocna linia bazowa dla wąskich domen. Debugowalne.
2. **TripPy / BERT-DST.** Generowanie oparte na kopiowaniu z kodowaniem BERT. Standard przed LLM.
3. **LDST (LLaMA + LoRA).** LLM dostrojony do instrukcji z monitem o miejsce w domenie. Osiąga jakość na poziomie ChatGPT w MultiWOZ 2.4.
4. **Bez ontologii (2024–26).** Pomiń schemat; bezpośrednio generuj nazwy i wartości gniazd. Obsługuje otwarte domeny.
5. **Podpowiedź + wyniki strukturalne (2024–26).** LLM ze schematem Pydantic + ograniczone dekodowanie. 5 linii kodu, gotowe do produkcji.

### Klasyczne tryby awarii

- **Współodniesienie w zakrętach.** „Pozostańmy przy pierwszej opcji”. Należy rozstrzygnąć, która opcja.
- **Nadpisz a dołącz.** Użytkownik mówi „dodaj włoski”. Zastępujesz kuchnię czy dodajesz?
- **Ukryte potwierdzenia.** „OK, super” – czy zaakceptowałeś oferowaną rezerwację?
- **Poprawka.** „Właściwie to o 19:00”. Należy zaktualizować czas bez czyszczenia innych miejsc.
- **Odniesienie do poprzedniej wypowiedzi systemowej.** „Tak, to.” Które „to”?

## Zbuduj to

### Krok 1: ekstraktor slotów oparty na regułach

Zobacz `code/main.py`. Słowniki Regex + synonimy obejmują 70% wyrażeń kanonicznych w wąskich domenach:

```python
CUISINE_SYNONYMS = {
    "italian": ["italian", "pasta", "pizza", "italy"],
    "chinese": ["chinese", "chow mein", "noodles"],
}

def extract_cuisine(utterance):
    for canonical, synonyms in CUISINE_SYNONYMS.items():
        if any(syn in utterance.lower() for syn in synonyms):
            return canonical
    return None
```

Kruche poza słownictwem kanonicznym. Działa w przypadku deterministycznych potwierdzeń slotów.

### Krok 2: pętla aktualizacji stanu

```python
def update_state(state, utterance):
    new_state = dict(state)
    for slot, extractor in SLOT_EXTRACTORS.items():
        value = extractor(utterance)
        if value is not None:
            new_state[slot] = value
    for slot in NEGATION_CLEARS:
        if is_negated(utterance, slot):
            new_state[slot] = None
    return new_state
```

Trzy niezmienniki:

- Nigdy nie resetuj slotu, którego użytkownik nie dotknął.
- Wyraźna negacja („nieważna kuchnia”) musi być jasna.
- Korekta użytkownika („właściwie…”) musi zostać nadpisana, a nie dołączona.

### Krok 3: DST oparty na LLM z wynikami strukturalnymi

```python
from pydantic import BaseModel
from typing import Literal, Optional
import instructor

class RestaurantState(BaseModel):
    cuisine: Optional[Literal["italian", "chinese", "indian", "thai", "any"]] = None
    area: Optional[Literal["north", "south", "east", "west", "center"]] = None
    price: Optional[Literal["cheap", "moderate", "expensive"]] = None
    people: Optional[int] = None
    day: Optional[str] = None

def llm_dst(history, llm):
    prompt = f"""You track the slot values of a restaurant booking across turns.
Dialogue so far:
{render(history)}

Update the state based on the latest user turn. Output only the JSON state."""
    return llm(prompt, response_model=RestaurantState)
```

Instructor + Pydantic gwarantuje prawidłowy obiekt stanu. Żadnych wyrażeń regularnych, żadnych niedopasowań schematów, żadnych halucynacyjnych szczelin.

### Krok 4: Ocena JGA

```python
def joint_goal_accuracy(predicted_states, gold_states):
    correct = sum(1 for p, g in zip(predicted_states, gold_states) if p == g)
    return correct / len(predicted_states)
```

Kalibruj: w jakiej części obrotów system poprawnie ustawia WSZYSTKIE miejsca? Dla MultiWOZ 2.4, topowe systemy z 2026 roku: 80-83%. Twój system w domenie powinien przewyższać Twoje wąskie słownictwo, w przeciwnym razie linia bazowa LLM Cię pokona.

### Krok 5: korekta obsługi

```python
CORRECTION_CUES = {"actually", "no wait", "on second thought", "change that to"}

def is_correction(utterance):
    return any(cue in utterance.lower() for cue in CORRECTION_CUES)
```

W przypadku wykrytej poprawki zastąp ostatnio zaktualizowany slot, zamiast dodawać. Trudno to osiągnąć bez pomocy LLM. Nowoczesny wzorzec: zawsze pozwalaj LLM regenerować cały stan na podstawie historii, a nie stopniowo aktualizować – to w naturalny sposób radzi sobie z poprawkami.

## Pułapki

- **Koszt regeneracji w pełnej historii.** Pozwolenie LLM na regenerację w każdej turze kosztuje łącznie O(n²) żetonów. Zakończ historię lub podsumuj starsze zakręty.
- **Dryf schematu.** Dodanie nowych slotów post-hoc powoduje przerwanie starych danych szkoleniowych. Wersjonuj swój schemat.
- **Uwzględnianie wielkości liter.** „Włoski” kontra „włoski” kontra „WŁOSKI” — normalizuj wszędzie.
- **Dziedziczenie ukryte.** Jeśli użytkownik określił wcześniej „dla 4 osób”, nowe żądanie dotyczące innego czasu nie powinno wyczyścić osób. Zawsze przekazuj pełną historię.
- **Forma dowolna a zbiór zamknięty.** Imiona, godziny i adresy wymagają wolnych pól; kuchnie i obszary są zamknięte. Połącz oba na schemacie.

## Użyj tego

Stos na rok 2026:

| Sytuacja | Podejście |
|----------|----------|
| Wąska domena (jedna lub dwie intencje) | Oparte na regułach + wyrażenie regularne |
| Szeroka domena, dostępne dane oznaczone | LDST (LLaMA + LoRA na danych typu MultiWOZ) |
| Szeroka domena, bez etykiet, gotowa do produkcji | LLM + Instruktor + Schemat Pydantyczny |
| Mówione / głos | ASR + normalizator + LLM-DST |
| Przepływ rezerwacji w wielu domenach | LLM sterowany schematem z modelami Pydantic dla poszczególnych domen |
| Wrażliwe na zgodność | Podstawowy oparty na regułach, rezerwowy LLM z przepływem potwierdzenia |

## Wyślij to

Zapisz jako `outputs/skill-dst-designer.md`:

```markdown
---
name: dst-designer
description: Design a dialogue state tracker — schema, extractor, update policy, evaluation.
version: 1.0.0
phase: 5
lesson: 29
tags: [nlp, dialogue, task-oriented]
---

Given a use case (domain, languages, vocab openness, compliance needs), output:

1. Schema. Domain list, slots per domain, open vs closed vocabulary per slot.
2. Extractor. Rule-based / seq2seq / LLM-with-Pydantic. Reason.
3. Update policy. Regenerate-whole-state / incremental; correction handling; negation handling.
4. Evaluation. Joint Goal Accuracy on a held-out dialogue set, slot-level precision/recall, confusion on the hardest slot.
5. Confirmation flow. When to explicitly ask the user to confirm (destructive actions, low-confidence extractions).

Refuse LLM-only DST for compliance-sensitive slots without a rule-based secondary check. Refuse any DST that cannot roll back a slot on user correction. Flag schemas without version tags.
```

## Ćwiczenia

1. **Łatwe.** Zbuduj oparty na regułach moduł do śledzenia stanu w `code/main.py` dla 3 przedziałów (kuchnia, obszar, cena). Przetestuj na 10 ręcznie wykonanych dialogach. Zmierz JGA.
2. **Średni.** Ten sam zestaw danych z Instruktorem + Pydantic + małym LLM. Porównaj JGA. Sprawdź najtrudniejsze zakręty.
3. **Trudne.** Zaimplementuj oba i trasę: podstawowa oparta na regułach, rezerwowa LLM, gdy oparta na regułach emituje z pewnością <2 gniazda. Zmierz łączny koszt JGA i wnioskowania na turę.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Czas letni | Śledzenie stanu dialogu | Utrzymuj dyktowaną wartość slotu podczas tur dialogu. |
| Gniazdo | Jednostka intencji użytkownika | Nazwany parametr potrzebny backendowi (kuchnia, data). |
| Domena | Obszar zadań | Restauracja, hotel, taksówka — zestawy automatów. |
| JGA | Dokładność wspólnego celu | Część zwojów, w której każdy slot jest poprawny. Wszystko albo nic. |
| MultiWOZ | Punkt odniesienia | Wielodomenowy zbiór danych WOZ; standardowa ocena DST. |
| DST wolny od ontologii | Brak schematu | Generuj nazwy i wartości slotów bezpośrednio, bez stałej listy. |
| Korekta | „Właściwie…” | Obrót, który nadpisuje wcześniej zajęte miejsce. |

## Dalsze czytanie

- [Budzianowski i in. (2018). MultiWOZ — wielkoskalowy, wielodomenowy Czarnoksiężnik z krainy Oz](https://arxiv.org/abs/1810.00278) — kanoniczny punkt odniesienia.
- [Feng i in. (2023). W kierunku śledzenia stanu dialogu opartego na LLM (LDST)](https://arxiv.org/abs/2310.14970) — strojenie instrukcji LLaMA + LoRA dla czasu letniego.
- [Heck i in. (2020). TripPy — strategia potrójnego kopiowania do śledzenia stanu dialogu neuronowego niezależnego od wartości](https://arxiv.org/abs/2005.02877) — koń pociągowy DST oparty na kopiowaniu.
- [Król, Flanigan (2024). Nienadzorowany, kompleksowy dialog zorientowany na zadania z LLM](https://arxiv.org/abs/2404.10753) – TOD bez nadzoru oparty na EM.
- [Tablica liderów MultiWOZ](https://github.com/budzianowski/multiwoz) — kanoniczne wyniki czasu letniego.