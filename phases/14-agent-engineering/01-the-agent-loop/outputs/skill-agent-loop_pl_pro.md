---

name: agent-loop
description: Zaimplementuj poprawną, minimalną pętlę agenta ReAct w wybranym języku i środowisku uruchomieniowym z obsługą rejestru narzędzi, warunków stopu oraz budżetu iteracji (tur).
version: 1.0.0
phase: 14
lesson: 01
tags: [react, agent-loop, tools, observability, stop-condition]

---

Na podstawie docelowego środowiska uruchomieniowego (Python async/sync, Node.js, Rust async, Go) oraz wykazu narzędzi (nazwa, schemat parametrów, logika wykonania) opracuj kompletną pętlę agenta ReAct.

Wygeneruj następujące sekcje:

1. Bufor wiadomości (Message Buffer). Zdefiniuj strukturę wiadomości z podziałem na role (user, assistant, tool, system) oraz schemat zgodny z wymaganiami wybranego dostawcy API (np. bloki `tool_use`/`tool_result` dla Anthropic, struktura `tool_calls`/`tool` dla OpenAI lub dedykowany kanał rozumowania w API). Unikaj mieszania niekompatybilnych schematów.
2. Rejestr narzędzi (Tool Registry). Klasa mapująca nazwy narzędzi na funkcje wraz z walidacją parametrów i formatowaniem wyników. Błędy wykonania narzędzi muszą być przechwytywane i przekazywane modelowi jako tekst obserwacji (nie mogą powodować awarii pętli).
3. Warunki stopu (Stopping Criteria). Implementacja kryteriów wyjścia z pętli: jawne wywołanie funkcji kończącej `finish`, brak żądań narzędziowych ze strony modelu, osiągnięcie limitu iteracji, limitu tokenów lub zadziałanie filtrów bezpieczeństwa (guardrails). Wybierz jedno główne kryterium stopu, a pozostałe traktuj jako zabezpieczenia awaryjne.
4. Budżet iteracji (Iteration Budget). Zdefiniowanie limitu kroków dopasowanego do klasy zadania (np. 10 dla zadań prostych, 200 dla obsługi interfejsu systemu, 400 dla pogłębionych analiz).
5. Logowanie trajektorii. Zapis kroków wnioskowania (Thought), akcji (Action), obserwacji (Observation) oraz przyczyny zatrzymania. Wdrożenie generowania zakresów OpenTelemetry GenAI (`invoke_agent`, `tool_call`) in przypadku integracji z SDK OTel.

Kategoryczne odrzucenia:
- Pętla bez zdefiniowanego limitu iteracji (turn cap) - krytyczne zagrożenie dla stabilności systemu.
- Ignorowanie (wyciszanie) błędów narzędzi i zwracanie pustej obserwacji (model musi otrzymać komunikat o błędzie, aby podjąć próbę samokorekty).
- Traktowanie danych pobranych przez narzędzia jako zaufanych instrukcji systemowych (dane z zewnątrz są niezaufane; wyłącznie bezpośrednie polecenia użytkownika stanowią autoryzację do działań).
- Integracja wielu dostawców bez warstwy translacji schematów wiadomości i definicji narzędzi.

Reguły odmowy:
- Jeśli docelowym rozwiązaniem ma być nietypowany skrypt powłoki (shell glue, np. bash), odrzuć projekt i zalecaj użycie języka wspierającego typowanie bufora wiadomości.
- Jeśli projekt zakłada automatyczne ponawianie nieudanych wywołań narzędzi bez przekazania informacji zwrotnej do modelu, odrzuć go. Decyzja o ponownej próbie musi leżeć po stronie modelu (lekcja 05 - samokorekta) lub być częścią wewnętrznej logiki samego narzędzia (idempotentność).
- Jeśli wykaz narzędzi zawiera operacje o charakterze destrukcyjnym, które mogą być wywołane bez potwierdzenia przez człowieka (human-in-the-loop), odrzuć projekt i wskaż na reguły z Fazy 13 Lekcji 09.

Format wyjściowy: Kompletny kod źródłowy pętli w wybranym języku oraz plik `README.md` wyjaśniający dobór warunków stopu, uzasadnienie budżetu iteracji oraz przykładowy log z trajektorią agenta (Thought -> Action -> Observation). Na końcu dodaj sekcję polecanej lektury odsyłającą do Lekcji 02 (planowanie ReWOO) dla zadań wieloetapowych, Lekcji 03 (Reflexion) dla zadań iteracyjnych lub Lekcji 27 (wstrzykiwanie promptów) przy pracy z niezaufanymi źródłami danych.
