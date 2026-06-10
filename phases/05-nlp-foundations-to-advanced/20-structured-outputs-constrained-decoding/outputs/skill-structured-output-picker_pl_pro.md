---

name: structured-output-picker
description: Wybierz podejście do ustrukturyzowanych danych wyjściowych, projektowania schematu i planu walidacji.
version: 1.0.0
phase: 5
lesson: 20
tags: [nlp, llm, structured-output]

---

Biorąc pod uwagę przypadek użycia (dostawca, budżet opóźnienia, złożoność schematu, tolerancja błędów), określ:

1. **Mechanizm**: Natywne ustrukturyzowane dane wyjściowe dostawcy API, mechanizm powtórzeń (retries) w bibliotece Instructor, automaty skończone (FSM) w Outlines lub gramatyki bezkontekstowe (CFG) w XGrammar. Uzasadnij wybór w jednym zdaniu.
2. **Projekt schematu**: Kolejność pól (najpierw proces rozumowania/łańcuch myśli, odpowiedź na samym końcu), dopuszczenie wartości `null` dla wartości nieznanych, typy wyliczeniowe (enum) kontra wyrażenia regularne, pola wymagane.
3. **Strategia obsługi błędów**: Maksymalna liczba powtórzeń, model zapasowy (fallback), łagodna obsługa wartości `null`, odmowa w przypadku danych spoza rozkładu (out-of-distribution).
4. **Plan walidacji**: Wskaźnik zgodności ze schematem (docelowo 100%), trafność semantyczna (oceniana przez LLM), pokrycie pól, opóźnienie (p50/p99).

Odrzuć każdy projekt, który umieszcza pole `answer` lub `decision` przed polami zawierającymi rozumowanie. Odmawiaj korzystania z samego trybu JSON (JSON Mode) bez zdefiniowanego schematu. Oznacz schematy rekurencyjne jako niekompatybilne, jeśli stosowana biblioteka obsługuje wyłącznie automaty skończone (FSM).
