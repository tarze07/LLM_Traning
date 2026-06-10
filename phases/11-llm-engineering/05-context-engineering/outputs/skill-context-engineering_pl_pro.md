---

name: skill-context-engineering
description: Ramy decyzyjne projektowania potoków budowania okna kontekstowego w zależności od typu zadania, rozmiaru okna oraz budżetu opóźnień.
version: 1.0.0
phase: 11
lesson: 05
tags: [context-engineering, context-window, rag, memory, tool-selection, lost-in-the-middle]

---

# Inżynieria kontekstu (Context Engineering)

Projektując aplikację LLM, wykorzystaj poniższe zasady do stworzenia potoku budowania okna kontekstowego.

## Zasady kardynalne

1. **Kontekst jest zasobem ograniczonym.** Okno o pojemności 128k tokenów wydaje się ogromne, ale zapełnia się bardzo szybko. Precyzyjnie budżetuj każdy komponent.
2. **Rozkład uwagi modelu jest nierównomierny.** Modele skupiają największą uwagę na początku i na końcu okna kontekstowego. Tam umieszczaj kluczowe informacje. Środek kontekstu to tzw. martwa strefa (Lost-in-the-Middle).
3. **Dynamiczne dobieranie zamiast statycznych szablonów.** Różne zapytania wymagają odmiennego kontekstu. Buduj okno kontekstowe dynamicznie dla każdego zapytania, a nie jednorazowo przy starcie systemu.
4. **Mniej znaczy więcej.** Starannie wyselekcjonowany kontekst o rozmiarze 10k tokenów daje lepsze rezultaty niż 100k tokenów przeładowanych chaotycznymi informacjami. Stosunek sygnału do szumu (SNR) jest ważniejszy niż bezwzględna objętość danych.
5. **Mierz każdy element.** Nie zoptymalizujesz tego, czego nie monitorujesz. Zliczaj i loguj tokeny zużywane przez każdy komponent przy każdym zapytaniu API.

## Podział budżetu okna kontekstowego

| Komponent | Typowy rozmiar | Priorytet | Strategia optymalizacji |
|----------|-------------|----------|-----------------------------------|
| System Prompt | 200-1000 tokenów | Stały, wysoki | Zwięzła redakcja, usunięcie redundancji |
| Definicje narzędzi (tools) | 500-3000 tokenów | Dynamiczny, średni | Filtrowanie narzędzi na podstawie intencji użytkownika |
| Pobrany kontekst (RAG) | 1000-5000 tokenów | Dynamiczny, wysoki | Reranking + próg podobieństwa + deduplikacja |
| Historia konwersacji | 500-5000 tokenów | Dynamiczny, średni | Streszczanie starszych tur rozmowy |
| Przykłady (few-shot) | 500-2000 tokenów | Dynamiczny, wysoki | Dynamiczny dobór na podstawie podobieństwa semantycznego |
| Zapytanie użytkownika | 50-500 tokenów | Stały, krytyczny | Brak |
| Rezerwa na odpowiedź | 2000-8000 tokenów | Stały | Dobór parametru `max_tokens` pod kątem oczekiwanej odpowiedzi |

## Zastosowanie poszczególnych rodzajów pamięci

**Pamięć krótkoterminowa (historia konwersacji)**: Dotyczy bieżącej sesji. Zarządzana poprzez streszczanie i przycinanie. Kompresuj tury starsze niż 5–10 ostatnich wypowiedzi. Zachowuj w niezmienionej formie (literalnie) 3–4 ostatnie tury.

**Pamięć długoterminowa (baza faktów i preferencji)**: Informacje o użytkowniku lub projekcie, które muszą przetrwać między sesjami. Pobierana na początku sesji. Przykłady: „użytkownik preferuje Pythona”, „projekt opiera się na PostgreSQL”, „zespół pracuje w metodologii trunk-based development”. Przechowywana w plikach takich jak `CLAUDE.md`, relacyjnych bazach danych lub profilach użytkowników.

**Pamięć epizodyczna (wcześniejsze interakcje)**: Zapis konkretnych rozmów lub sesji z przeszłości, które mogą ułatwić rozwiązanie obecnego zadania. Przechowywana w postaci embeddingów i wyszukiwana semantycznie. Przykład: „W zeszłym tygodniu debugowaliśmy podobny problem z autoryzacją API” – to jest właśnie pamięć epizodyczna.

## Strategia selekcji narzędzi (Tools)

Nie przekazuj opisu wszystkich narzędzi w każdym zapytaniu API. Marnuje to tokeny i zwiększa ryzyko błędnego wyboru (tool hallucination) przez model.

1. Sklasyfikuj intencję zapytania (np. generowanie kodu, wysyłka e-maila, kalendarz, wyszukiwanie informacji).
2. Przypisz zidentyfikowane intencje do odpowiednich grup narzędzi.
3. Przekaż do promptu wyłącznie wyselekcjonowane, pasujące narzędzia.
4. Jeśli intencja użytkownika jest dwuznaczna, uwzględnij narzędzia z dwóch najbardziej prawdopodobnych kategorii.
5. Zawsze dołączaj jedno uniwersalne narzędzie (np. wyszukiwarkę internetową) jako opcję rezerwową (fallback).

Oczekiwane oszczędności: redukcja zużycia tokenów przeznaczonych na opisy narzędzi o 60–80% w przypadku zapytań o sprecyzowanej intencji.

## Najlepsze praktyki dla systemów RAG

- **Zawsze stosuj reranking.** Wyszukiwanie wektorowe to jedynie filtr zgrubny. Zastosowanie modelu rerankingu (np. Cohere Rerank, Cross-Encoder) drastycznie zwiększa precyzję wyników.
- **Wprowadź sztywny próg podobieństwa.** Odrzucaj segmenty o współczynniku podobieństwa cosinusowego poniżej 0.3. Wstrzykują one szum do okna kontekstowego.
- **Deduplikuj wyniki.** Jeśli dwa pobrane segmenty wykazują ponad 80% zbieżności tekstu, zachowaj tylko ten z wyższą oceną podobieństwa.
- **Optymalizuj kolejność (Lost-in-the-Middle).** Najbardziej trafne segmenty umieszczaj na samym początku i na samym końcu okna kontekstowego.
- **Kładź nacisk na jakość, a nie na ilość.** Przekaż 3–5 wysoce trafnych segmentów zamiast 15 o średniej przydatności.

## Zarządzanie historią konwersacji

- Przechowuj 3–4 ostatnie tury dialogu w postaci dosłownej (model bezwzględnie wymaga świeżego kontekstu).
- Starsze wypowiedzi agreguj w formie syntetycznego podsumowania (np. „Użytkownik zapytał o X, wybrano rozwiązanie Y”).
- Usuwaj z historii tury systemowe, które nie wnoszą wartości merytorycznej (np. puste wywołania narzędzi lub wewnętrzne logi systemowe).
- Uruchamiaj procedurę kompresji (streszczania) historii za każdym razem, gdy zaczyna ona zajmować ponad 30% budżetu okna kontekstowego.

## Sygnały ostrzegawcze (Red Flags)

- System Prompt przekracza 2000 tokenów: najprawdopodobniej zawiera statyczne dane, które powinny być wstrzykiwane dynamicznie.
- Wszystkie opisy narzędzi przekazywane w każdym zapytaniu API: brak wdrożonej selekcji na podstawie intencji.
- Brak filtrowania wyników wyszukiwania RAG: wstrzykiwanie szumu informacyjnego bezpośrednio do okna kontekstowego.
- Nieograniczony wzrost rozmiaru historii: brak zaimplementowanego mechanizmu streszczania.
- Brak rezerwy na generowanie odpowiedzi: model przedwcześnie urywa odpowiedzi z powodu limitu tokenów.
- Te same informacje powtórzone w wielu miejscach jednocześnie (System Prompt, pobrane dokumenty RAG, historia): wymagana deduplikacja.
- Stopień zapełnienia kontekstu powyżej 60%: pozostawia to zbyt mało wolnej pamięci na proces wnioskowania modelu (reasoning space).
