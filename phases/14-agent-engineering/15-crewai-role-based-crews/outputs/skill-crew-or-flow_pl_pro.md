---

name: crew-or-flow
description: Wybierz CrewAI Crew lub Flow dla danego zadania i wygeneruj jego minimalną implementację.
version: 1.0.0
phase: 14
lesson: 15
tags: [crewai, crews, flows, multi-agent, role-based]

---

Na podstawie opisu zadania dobierz odpowiedni wariant — Załoga (autonomiczna) lub Przepływ (deterministyczny) — a następnie wygeneruj jego szkielet.

Drzewo decyzyjne:

1. Czy zadanie posiada sztywne wymagania dotyczące SLA, zgodności (compliance) lub deterministycznego odtwarzania ścieżki? -> Wybierz Przepływ (Flow).
2. Czy zadanie ma charakter otwarty lub eksploracyjny (research, pierwsza wersja szkicu, burza mózgów)? -> Wybierz Załogę (Crew).
3. Czy zadanie wymaga zaangażowania ponad 4 specjalistów, a kolejność kroków powinna być dynamicznie dobierana przez model? -> Wybierz Załogę o strukturze hierarchicznej (Hierarchical Crew).
4. Czy zadanie wymaga sekwencyjnej współpracy <= 3 specjalistów w stałej kolejności? -> Wybierz załogę sekwencyjną lub przepływ (z rekomendacją na przepływ).

Dla wariantu Załogi (Crew) wygeneruj:

1. Definicje agentów: rola (`role`), cel (`goal`), historia (`backstory` - zwięzła, <=200 słów) oraz narzędzia (`tools`).
2. Definicje zadań: opis (`description`), oczekiwany wynik (`expected_output`) oraz przypisany agent.
3. Konfigurację załogi z odpowiednio dobranym procesem (sekwencyjnym lub hierarchicznym).
4. Kod testowy uruchamiający załogę na przykładowych danych i weryfikujący poprawność wyników.

Dla wariantu Przepływu (Flow) wygeneruj:

1. Metodę wejściową oznaczoną dekoratorem `@start`.
2. Kroki oznaczone dekoratorem `@listen(topic)` tworzące graf skierowany (DAG).
3. Jasno zdefiniowane tematy zdarzeń (event topics) zamiast niejawnego przekazywania danych.
4. Mechanizm powtarzalności pozwalający na deterministyczne odtworzenie przebiegu na podstawie danych wejściowych.

Kryteria odrzucenia (Hard rejects):

- Tworzenie agentów załogi bez zdefiniowanej historii (`backstory`). Profilowanie jest kluczowe dla jakości działania.
- Przepływy bez jawnie nazwanej struktury tematów. Stosowanie niejawnych powiązań narusza zasadę pełnej kontroli nad przepływem.
- Wybór hierarchicznej struktury załogi dla zaledwie 2 specjalistów. Koszt orkiestracji przez dodatkowego menedżera przewyższa wtedy korzyści z podziału zadań.

Zasady odmowy (Guardrails):

- Jeśli użytkownik żąda autonomicznej załogi do zadań czysto produkcyjnych (wymagających SLA), odmów i zaproponuj wdrożenie oparte na strukturze przepływu (Flow).
- Jeśli użytkownik próbuje wymusić strukturę Flow for zadań badawczych o charakterze otwartym, odmów i przekieruj rozwiązanie na autonomiczną załogę (Crew).
- Jeśli opis historii agenta (`backstory`) przekracza 200 słów, odmów i zażądaj jego skrócenia ze względu na optymalizację okna kontekstowego.

Wygenerowana struktura: pliki `agents.py`, `tasks.py`, `crew.py` lub `flow.py` oraz `README.md` z uzasadnieniem wybranej architektury. Zakończ sekcją „Co czytać dalej”, odsyłając do Lekcji 24 (narzędzia obserwowalności: Langfuse/AgentOps) lub Lekcji 13 (jeśli przepływ wymaga trwałego zapisywania punktów kontrolnych i wznawiania działania).
