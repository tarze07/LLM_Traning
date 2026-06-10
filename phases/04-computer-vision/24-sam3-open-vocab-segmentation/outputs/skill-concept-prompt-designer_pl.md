---

name: skill-concept-prompt-designer
description: Zamień wypowiedzi użytkowników w dobrze sformułowane podpowiedzi koncepcyjne SAM 3 z podziałem, ujednoznacznieniem i odwołaniami
version: 1.0.0
phase: 4
lesson: 24
tags: [sam3, open-vocab, prompt-engineering, segmentation]

---

# Projektant podpowiedzi koncepcyjnych

Dokładność SAM 3 zależy w dużej mierze od sposobu sformułowania podpowiedzi. Ta umiejętność normalizuje swobodne wypowiedzi użytkownika w podpowiedzi, z którymi SAM 3 dobrze sobie radzi.

## Kiedy używać

- Budowa interfejsu użytkownika, który akceptuje zapytania obiektowe w języku naturalnym.
- Ujawnienie SAM 3 poprzez API, gdzie osoby wywołujące wysyłają zdania.
- Debugowanie słabych dopasowań SAM 3 — często komunikat jest zniekształcony, a nie model.

## Wejścia

- `utterance`: surowy ciąg użytkownika.
- `context`: opcjonalna wskazówka dotycząca domeny (np. „nadzór”, „medycyna”, „handel detaliczny”).
- `max_concepts`: maksymalna liczba pojęć do wyodrębnienia na wypowiedź; domyślnie 5.

## Zasady preferowane przez SAM 3

- **Krótkie wyrażenia rzeczownikowe, a nie zdania.** `"cat"` wygrywa z `"there is a cat"`.
- **Rzeczowniki konkretne.** `"skateboard"` wygrywa z `"thing to ride on"`.
- **Modyfikatory bezpośrednio przed rzeczownikiem.** `"red car"` wygrywa z `"car that is red"`.
- **Małe litery.** SAM 3 jest solidny, ale empirycznie nieco lepszy w przypadku wprowadzania małych liter.
- **Liczba pojedyncza lub mnoga.** Obydwa działają; liczba mnoga pomaga, gdy oczekuje się wielu wystąpień.

## Kroki

1. **Tokenizacja za pomocą zwykłych separatorów** — przecinek, średnik, „i”, „lub”, „&”.
2. **Przedrostki wypełniaczy** — „znajdź”, „pokaż”, „segment”, „wykryj”, „lokalizuj”, „a”, „an”, „the”.
3. **Zachowaj modyfikatory przyimkowe** tylko wtedy, gdy są wizualne — `"striped red umbrella"` tak, `"umbrella from yesterday"` nie (`"from yesterday"` nie jest na obrazie).
4. **Ujednoznacznienie kolizji** przy użyciu opcjonalnego `context`:
   - `"window"` w kontekście nadzoru -> `"building window"`.
   - `"window"` w kontekście medycznym -> często błąd; zasugeruj użytkownikowi wyjaśnienie.
5. **Powrót** do dokładnego ciągu, jeśli podział daje zero pojęć *i* wypowiedź zawiera co najmniej jeden rzeczownik konkretny. Jeśli nie można wyodrębnić konkretnego rzeczownika, nie emituj pojęcia — zwróć jedynie ostrzeżenia i poproś użytkownika o wyjaśnienie (patrz Zasady).
6. **Ograniczenie do `max_concepts`.** Jeśli wyodrębniono więcej pojęć, niż prosił dzwoniący, zachowaj porządek wypowiedzi w pierwszym `max_concepts`, a resztę wyemituj pod `dropped` z powodem `"exceeded max_concepts"`. Dzięki temu opóźnienia są ograniczone, gdy użytkownik wkleja długie wyliczenie.

##Format wyjściowy

```
[designed prompts]
  utterance:    <original>
  concepts:     ["concept_1", "concept_2", ...]
  dropped:      ["filler_1", ...]
  warnings:     ["concept too abstract", "may match many classes", ...]

[sam3 calls]
  For each concept run: sam3.detect(image, concept)
  Merge outputs with distinct concept tags per detection.
```

## Przykłady

```
in:  "can you find me a cat or two dogs?"
out: ["cat", "dogs"]
dropped: ["can you find me", "a", "or two", "?"]
note: "dogs" kept plural because the utterance says "two dogs" — plural hint preserved.

in:  "segment the big red truck and the blue sedan"
out: ["big red truck", "blue sedan"]
dropped: ["segment", "the", "and"]

in:  "thing near the door"
out: ["door"]
warnings: ["'thing' is too abstract for SAM 3; fell back to 'door'"]

in:  "striped red umbrella, green hat, pink balloon"
out: ["striped red umbrella", "green hat", "pink balloon"]
```

## Zasady

- Nigdy nie przekazuj SAM 3 zdań dłuższych niż 8 słów — dokładność spada powyżej tego.
- Jeśli wypowiedź nie zawiera konkretnych rzeczowników, które można wyodrębnić, nie uruchamiaj SAM 3; zwróć ostrzeżenia i poproś o wyjaśnienia.
- Nie rozdzielaj znaków interpunkcyjnych w cudzysłowach; zachować `"black and white cat"` jako jedną koncepcję, jeśli jest cytowana.
— Zawsze rejestruj oryginalną wypowiedź i pochodne koncepcje na potrzeby debugowania produkcyjnego.