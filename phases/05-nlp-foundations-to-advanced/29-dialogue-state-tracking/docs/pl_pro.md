# Śledzenie stanu dialogu

> „Chcę tańszą restaurację na północy… właściwie — niech będzie w średniej cenie… i dodaj włoską". Trzy tury, trzy aktualizacje stanu. DST synchronizuje wartości szczelin, dzięki czemu rezerwacja działa poprawnie.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 17 (Chatboty), Faza 5 · 20 (Wyjścia strukturalne)
**Czas:** ~75 minut

## Problem

W systemie dialogu zorientowanego na zadania cel użytkownika jest kodowany jako zbiór par szczelina–wartość: `{cuisine: italian, area: north, price: moderate}`. W każdej turze użytkownik może dodać, zmienić lub usunąć wartość. System musi odczytać całą rozmowę i na tej podstawie poprawnie odtworzyć bieżący stan.

Jeden błąd w tym miejscu i system zarezerwuje niewłaściwą restaurację, zaplanuje zły lot lub obciąży nieodpowiednią kartę płatniczą. DST stanowi pomost między tym, co powiedział użytkownik, a tym, co wykonuje backend.

Dlaczego w 2026 r. nadal ma to znaczenie — mimo rosnącej roli LLM:

- Domeny wrażliwe na zgodność (bankowość, opieka zdrowotna, rezerwacje lotów) wymagają deterministycznych wartości szczelin, a nie swobodnie generowanego tekstu.
- Agenci korzystający z narzędzi wciąż potrzebują rozpoznania szczeliny przed wywołaniem API.
- Korekty w toku rozmowy są trudniejsze, niż się wydaje: „Nie, zrób to jednak w czwartek".

Nowoczesny potok łączy klasyczne koncepcje DST z ekstraktorami opartymi na LLM i ograniczeniami strukturalnego wyjścia.

## Koncepcja

![DST: historia dialogu → stan wartości szczelin](../assets/dst.svg)

**Struktura zadania.** Schemat definiuje domeny (restauracja, hotel, taksówka) i ich szczeliny (kuchnia, obszar, cena, liczba osób). Każde pole może być puste, wypełnione wartością ze zbioru zamkniętego (cena: {tanie, umiarkowane, drogie}) lub dowolnym tekstem (nazwa: „Miedziany Czajnik").

**Dwa podejścia do DST.**

- **Klasyfikacja.** Dla każdej pary (szczelina, wartość_kandydata) model przewiduje tak/nie. Sprawdza się w przypadku zamkniętych słowników. Standard sprzed 2020 r.
- **Generacja.** Model otrzymuje cały dialog i generuje wartości szczelin jako dowolny tekst. Działa przy otwartym słowniku. Współczesne podejście domyślne.

**Metryki.** Dokładność wspólnego celu (JGA) — odsetek tur, w których *każda* szczelina jest poprawna. Zasada „wszystko albo nic". Czołowe systemy w rankingu MultiWOZ 2.4 osiągają około 83% w 2026 roku.

**Architektury.**

1. **Oparte na regułach (wyrażenia regularne + słowa kluczowe).** Solidna linia bazowa dla wąskich domen. Łatwa w debugowaniu.
2. **TripPy / BERT-DST.** Generowanie oparte na kopiowaniu z kodowaniem BERT. Standard z okresu przed LLM.
3. **LDST (LLaMA + LoRA).** LLM dostrojony do instrukcji z monitem uwzględniającym domenę i szczeliny. Osiąga jakość porównywalną z ChatGPT na MultiWOZ 2.4.
4. **Bez ontologii (2024–26).** Pomija schemat — nazwy i wartości szczelin generowane są bezpośrednio. Obsługuje otwarte domeny.
5. **Promptowanie + wyjście strukturalne (2024–26).** LLM ze schematem Pydantic i ograniczonym dekodowaniem. Kilka linii kodu, gotowe do produkcji.

### Typowe tryby awarii

- **Koreferencja między turami.** „Zostańmy przy pierwszej opcji". System musi rozstrzygnąć, która to opcja.
- **Nadpisanie a dodanie.** Użytkownik mówi „dodaj włoską". Czy zastąpić kuchnię, czy ją dołączyć?
- **Ukryte potwierdzenia.** „OK, super" — czy użytkownik zaakceptował proponowaną rezerwację?
- **Korekta.** „Właściwie to o 19:00". Należy zaktualizować godzinę bez kasowania pozostałych szczelin.
- **Odwołanie do poprzedniej wypowiedzi systemu.** „Tak, to." — które „to"?

## Zbuduj to

### Krok 1: ekstraktor szczelin oparty na regułach

Zob. `code/main.py`. Słowniki wyrażeń regularnych i synonimów pokrywają około 70% kanonicznych wyrażeń w wąskich domenach:

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

Podejście jest kruche poza kanonicznym słownictwem, ale sprawdza się przy deterministycznym potwierdzaniu szczelin.

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

- Nigdy nie resetuj szczeliny, której użytkownik nie dotknął.
- Jawna negacja („nieważna kuchnia") musi prowadzić do jej wyczyszczenia.
- Korekta użytkownika („właściwie…") musi nadpisać wartość, a nie jej towarzyszyć.

### Krok 3: DST oparty na LLM z wyjściem strukturalnym

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

Połączenie Instructor i Pydantic gwarantuje poprawny obiekt stanu. Żadnych wyrażeń regularnych, niezgodności schematów ani halucynowanych szczelin.

### Krok 4: ocena JGA

```python
def joint_goal_accuracy(predicted_states, gold_states):
    correct = sum(1 for p, g in zip(predicted_states, gold_states) if p == g)
    return correct / len(predicted_states)
```

Pytanie kalibracyjne: w ilu turach system poprawnie ustawia WSZYSTKIE szczeliny? Dla MultiWOZ 2.4 czołowe systemy z 2026 roku osiągają 80–83%. Twój system dla konkretnej domeny powinien ten wynik przewyższać — w przeciwnym razie ogólna linia bazowa LLM okaże się lepsza.

### Krok 5: obsługa korekt

```python
CORRECTION_CUES = {"actually", "no wait", "on second thought", "change that to"}

def is_correction(utterance):
    return any(cue in utterance.lower() for cue in CORRECTION_CUES)
```

Po wykryciu korekty zastąp ostatnio zaktualizowaną szczelinę, zamiast dodawać do niej. Samo to trudno osiągnąć bez LLM. Nowoczesny wzorzec: zawsze pozwalaj LLM regenerować cały stan na podstawie historii, zamiast aktualizować go przyrostowo — to naturalnie radzi sobie z korektami.

## Pułapki

- **Koszt regeneracji na pełnej historii.** Gdy LLM regeneruje stan w każdej turze, łączny koszt rośnie jak O(n²) tokenów. Ogranicz historię lub podsumowuj starsze tury.
- **Dryf schematu.** Dodanie nowych szczelin po fakcie psuje stare dane treningowe. Wersjonuj schemat.
- **Wielkość liter.** „Włoska", „włoska", „WŁOSKA" — normalizuj wszędzie.
- **Ukryte dziedziczenie wartości.** Jeśli użytkownik wcześniej podał „dla 4 osób", nowa prośba dotycząca innej godziny nie powinna kasować liczby gości. Zawsze przekazuj pełną historię.
- **Tekst swobodny a zbiór zamknięty.** Imiona, godziny i adresy wymagają pól otwartych; kuchnie i obszary — zamkniętych. Schemat powinien łączyć oba rodzaje.

## Zastosowanie

Zalecany stos na rok 2026:

| Sytuacja | Podejście |
|----------|----------|
| Wąska domena (jedna lub dwie intencje) | Oparte na regułach + wyrażenia regularne |
| Szeroka domena, dostępne dane z etykietami | LDST (LLaMA + LoRA na danych w stylu MultiWOZ) |
| Szeroka domena, brak etykiet, wdrożenie produkcyjne | LLM + Instructor + schemat Pydantic |
| Mowa / głos | ASR + normalizator + LLM-DST |
| Rezerwacje wielodomenowe | LLM sterowany schematem z oddzielnymi modelami Pydantic dla każdej domeny |
| Domeny wrażliwe na zgodność | Podstawa oparta na regułach, LLM jako rezerwa z przepływem potwierdzenia |

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

1. **Łatwe.** Zbuduj oparty na regułach moduł śledzenia stanu w `code/main.py` dla 3 szczelin (kuchnia, obszar, cena). Przetestuj na 10 ręcznie przygotowanych dialogach. Zmierz JGA.
2. **Średnie.** Ten sam zestaw danych, lecz z Instructor + Pydantic + małym LLM. Porównaj JGA. Przeanalizuj najtrudniejsze tury.
3. **Trudne.** Zaimplementuj oba podejścia i wprowadź routing: podstawa oparta na regułach, LLM jako rezerwa, gdy wariant regułowy wyodrębnia mniej niż 2 szczeliny z wystarczającą pewnością. Zmierz łączne JGA i koszt wnioskowania na turę.

## Kluczowe terminy

| Termin | Potoczne określenie | Rzeczywiste znaczenie |
|------|-----------------|----------------------|
| DST | Śledzenie stanu dialogu | Utrzymywanie aktualnych wartości szczelin przez kolejne tury rozmowy. |
| Szczelina (slot) | Jednostka intencji użytkownika | Nazwany parametr wymagany przez backend (kuchnia, data). |
| Domena | Obszar zadania | Restauracja, hotel, taksówka — zestawy szczelin pogrupowane tematycznie. |
| JGA | Dokładność wspólnego celu | Odsetek tur, w których każda szczelina jest poprawna. Zasada „wszystko albo nic". |
| MultiWOZ | Punkt odniesienia | Wielodomenowy zbiór danych WOZ; standardowa miara oceny DST. |
| DST wolny od ontologii | Bez schematu | Generowanie nazw i wartości szczelin bezpośrednio, bez ustalonej listy. |
| Korekta | „Właściwie…" | Tura, w której użytkownik nadpisuje wcześniej podaną wartość. |

## Dalsze czytanie

- [Budzianowski i in. (2018). MultiWOZ — wielkoskalowy, wielodomenowy Wizard of Oz](https://arxiv.org/abs/1810.00278) — kanoniczny punkt odniesienia.
- [Feng i in. (2023). W kierunku śledzenia stanu dialogu opartego na LLM (LDST)](https://arxiv.org/abs/2310.14970) — dostrajanie LLaMA + LoRA do DST metodą instrukcji.
- [Heck i in. (2020). TripPy — strategia potrójnego kopiowania do neuronowego śledzenia stanu dialogu niezależnego od wartości](https://arxiv.org/abs/2005.02877) — klasyczny DST oparty na kopiowaniu.
- [Król, Flanigan (2024). Nienadzorowany dialog zorientowany na zadania z LLM](https://arxiv.org/abs/2404.10753) — TOD bez nadzoru oparty na EM.
- [Tablica liderów MultiWOZ](https://github.com/budzianowski/multiwoz) — aktualne wyniki DST.
