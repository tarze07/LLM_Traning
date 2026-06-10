---

name: structured-output-picker
description: Wybierz podejście do ustrukturyzowanych wyników, projekt schematu i plan walidacji.
version: 1.0.0
phase: 5
lesson: 20
tags: [nlp, llm, structured-output]

---

Biorąc pod uwagę przypadek użycia (dostawca, budżet opóźnień, złożoność schematu, tolerancja na awarie), wynik:

1. Mechanizm. Strukturalne dane wyjściowe natywnego dostawcy, ponowne próby instruktora, Outlines FSM lub XGrammar CFG. Powód w jednym zdaniu.
2. Projekt schematu. Kolejność pól (najpierw rozumowanie, odpowiedź ostatnia), pola dopuszczające wartość null dla „nieznanego”, wyliczenie vs wyrażenie regularne, pola wymagane.
3. Strategia porażki. Maksymalna liczba ponownych prób, model awaryjny, płynna obsługa `null`, odmowa poza dystrybucją.
4. Plan walidacji. Stopień zgodności schematu (docelowy 100%), trafność semantyczna (ocena LLM), współczynnik pokrycia pola, opóźnienie p50/p99.

Odrzuć każdy projekt, który stawia `answer` lub `decision` przed polami rozumowania. Odmawiaj używania samego trybu JSON bez schematu. Oznacz schematy rekurencyjne za biblioteką obsługującą tylko FSM.