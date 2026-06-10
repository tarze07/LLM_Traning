---
name: entity-linker
description: Zaprojektuj potok łączenia encji: określ bazę wiedzy, generator kandydatów, moduł ujednoznaczniania oraz plan ewaluacji.
version: 1.0.0
phase: 5
lesson: 25
tags: [nlp, entity-linking, knowledge-graph]
---

Na podstawie wymagań scenariusza użycia (dziedzinowa baza wiedzy, język, wolumen zapytań, limit opóźnień) wygeneruj:

1. Baza wiedzy: Wikidata / Wikipedia / rejestr wewnętrzny, data wersji oraz częstotliwość aktualizacji.
2. Generator kandydatów: Indeks aliasów, wyszukiwanie wektorowe lub metoda hybrydowa wraz z docelową wartością Recall@K.
3. Ujednoznaczniacz: Prawdopodobieństwo a priori + kontekst, oparte na osadzeniach, generatywne lub oparte na LLM.
4. Strategia obsługi NIL: Próg odcięcia wyniku, dodatkowy klasyfikator lub jawny kandydat NIL.
5. Plan ewaluacji: Wskaźnik Recall@30 dla kandydatów, dokładność TOP-1 oraz miara F1 dla detekcji NIL na wydzielonym zbiorze testowym.

Zawsze odrzucaj projekty potoków EL, które nie posiadają zdefiniowanego baseline dla pokrycia kandydatów (wyszukiwania nie da się poprawnie ocenić bez pewności, że poprawny obiekt znalazł się na liście kandydatów). Nigdy nie akceptuj rozwiązań opartych o LLM, które nie stosują dekodowania z ograniczeniami (constrained decoding) do poprawnych identyfikatorów z bazy wiedzy. Oznaczaj jako wymagające dostrojenia systemy, w których błąd popularności (popularity bias) fałszuje wyniki dla rzadkich encji o zbieżnych nazwach.
