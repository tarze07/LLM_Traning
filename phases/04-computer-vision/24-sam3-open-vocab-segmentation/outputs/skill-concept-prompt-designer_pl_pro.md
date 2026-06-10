---

name: skill-concept-prompt-designer
description: Logika przetwarzająca potoczne zapytania użytkowników na precyzyjne podpowiedzi pojęciowe (concept prompts) interpretowane przez model SAM 3
version: 1.0.0
phase: 4
lesson: 24
tags: [sam3, open-vocab, prompt-engineering, segmentation]

---

# Projektant podpowiedzi pojęciowych (Concept Prompt Designer)

Skuteczność modelu SAM 3 w dużej mierze zależy od struktury podpowiedzi tekstowych. Niniejszy moduł normalizuje potoczne zapytania użytkownika na format optymalny dla wejścia modelu.

## Zastosowanie

- Projektowanie interfejsów użytkownika akceptujących zapytania w języku naturalnym.
- Udostępnianie API modelu SAM 3, gdzie klienci przesyłają surowe zdania tekstowe.
- Debugowanie i analiza błędnych detekcji SAM 3 – często problem leży po stronie źle sformułowanej podpowiedzi, a nie samego modelu.

## Dane wejściowe

- `utterance`: surowe zapytanie tekstowe wpisane przez użytkownika.
- `context`: opcjonalny kontekst dziedzinowy (np. `monitoring`, `medycyna`, `e-commerce`).
- `max_concepts`: maksymalna dopuszczalna liczba pojęć wyodrębnionych z pojedynczego zapytania (domyślnie: 5).

## Zasady konstrukcji optymalnych zapytań dla SAM 3

- **Krótkie frazy rzeczownikowe zamiast pełnych zdań**: zapytanie `"cat"` da lepsze rezultaty niż `"there is a cat"`.
- **Używanie rzeczowników konkretnych**: hasło `"skateboard"` jest lepsze niż opisowe `"thing to ride on"`.
- **Określenia bezpośrednio przed rzeczownikiem**: fraza `"red car"` zadziała lepiej niż `"car that is red"`.
- **Małe litery**: choć model jest odporny na wielkość liter, empirycznie zaleca się konwersję całego zapytania do małych liter.
- **Liczba pojedyncza lub mnoga**: obie formy są obsługiwane; użycie liczby mnogiej ułatwia detekcję, gdy na scenie znajduje się wiele instancji tego samego obiektu.

## Algorytm postępowania

1. **Tokenizacja i podział**: rozdzielenie tekstu na podstawie typowych separatorów (przecinki, średniki, spójniki „i”, „lub”, znak „&”).
2. **Usuwanie słów pomocniczych (stop words)**: odrzucenie czasowników i przedimków (np. „znajdź”, „pokaż”, „zaznacz”, „wykryj”, „a”, „an”, „the”).
3. **Weryfikacja określeń**: zachowanie cech wizualnych (np. `"striped red umbrella"`), przy jednoczesnym odrzuceniu cech niewizualnych (np. `"umbrella from yesterday"` – informacja o czasie nie jest zakodowana geometrycznie ani optycznie na obrazie).
4. **Ujednoznacznianie (Disambiguation)** przy użyciu opcjonalnego parametru `context`:
   - `"window"` w kontekście monitoringu -> `"building window"`.
   - `"window"` w kontekście medycznym -> potencjalna niejednoznaczność (np. okienko kostne); należy poprosić użytkownika o sprecyzowanie.
5. **Obsługa awaryjna (Fallback)**: jeśli podział nie wygenerował żadnego pojęcia, a zapytanie zawiera co najmniej jeden konkretny rzeczownik, użyj oryginalnego sformułowania. W przeciwnym razie nie wysyłaj zapytania do modelu – zwróć ostrzeżenie i poproś użytkownika o sprecyzowanie.
6. **Ograniczenie liczby zapytań**: jeśli liczba wyodrębnionych pojęć przekracza wartość parametru `max_concepts`, pozostaw tylko pierwsze `max_concepts` elementów, a pozostałe zapisz na liście `dropped` z oznaczeniem powodu (`"exceeded max_concepts"`). Zapobiega to nadmiernemu obciążeniu systemu przy wklejeniu przez użytkownika długich list wyliczeniowych.

## Format wyjściowy

```
[designed prompts]
  utterance:    <original>
  concepts:     ["concept_1", "concept_2", ...]
  dropped:      ["pominięte_słowa", ...]
  warnings:     ["zbyt abstrakcyjne pojęcie", "może pasować do wielu klas", ...]

[sam3 calls]
  Dla każdego pojęcia uruchom: sam3.detect(image, concept)
  Połącz wyniki przypisując unikalne etykiety pojęciowe dla każdej detekcji.
```

## Przykłady

```
Wejście: "can you find me a cat or two dogs?"
Wyjście: ["cat", "dogs"]
dropped: ["can you find me", "a", "or two", "?"]
Uwaga: Słowo "dogs" zachowano w liczbie mnogiej ze względu na obecność liczebnika "two" – informacja o ilości została zachowana.

Wejście: "segment the big red truck and the blue sedan"
Wyjście: ["big red truck", "blue sedan"]
dropped: ["segment", "the", "and"]

Wejście: "thing near the door"
Wyjście: ["door"]
warnings: ["słowo 'thing' jest zbyt abstrakcyjne dla modelu SAM 3; użyto słowa awaryjnego 'door'"]

Wejście: "striped red umbrella, green hat, pink balloon"
Wyjście: ["striped red umbrella", "green hat", "pink balloon"]
```

## Zasady i dobre praktyki

- Nie przekazuj do modelu SAM 3 fraz dłuższych niż 8 słów; powyżej tej długości dokładność detekcji drastycznie spada.
- Jeżeli zapytanie nie zawiera konkretnych rzeczowników do wyodrębnienia, zablokuj wywołanie modelu SAM 3, zwróć ostrzeżenie i poproś użytkownika o sprecyzowanie.
- Nie rozdzielaj fraz ujętych w cudzysłów; potraktuj frazę `"black and white cat"` jako jedno spójne pojęcie, jeśli została w ten sposób zapisana.
- Zawsze loguj oryginalne zapytanie użytkownika oraz wyodrębnione z niego pojęcia w celu ułatwienia późniejszego debugowania systemu produkcyjnego.
