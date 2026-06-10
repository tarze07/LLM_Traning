---

name: agent-loop
description: Napisz poprawną, minimalną pętlę agenta ReAct w dowolnym języku docelowym/środowisku wykonawczym z narzędziami, warunkiem zatrzymania i budżetem zwrotnym.
version: 1.0.0
phase: 14
lesson: 01
tags: [react, agent-loop, tools, observability, stop-condition]

---

Biorąc pod uwagę docelowe środowisko wykonawcze (asynchronizacja Pythona, synchronizacja Pythona, Węzeł, async Rust, Go) i listę narzędzi (nazwa, schemat wejściowy, możliwość wywołania), utwórz pętlę agenta ReAct, która jest poprawna przy pierwszej próbie.

Wyprodukuj:

1. Typ bufora komunikatów z rolami {użytkownik, asystent, narzędzie, final} i schematem, jakiego oczekuje dostawca docelowy (bloki Anthropic `tool_use` / `tool_result`, komunikaty z wywołaniami funkcji OpenAI, kanał wnioskowania Responses API). Nigdy po cichu nie wymieniaj schematów między dostawcami.
2. Rejestr narzędzi z nazwą -> wywoływalna wysyłka, walidacją danych wejściowych i wpisanym wynikiem. Błędy należy wychwycić i przekształcić w ciągi obserwacyjne, nigdy nie wprowadzając ich do pętli.
3. Pętla działająca do momentu: jawnej akcji `finish`, braku wywołań narzędzi w turze asystenta, maksymalnej liczby obrotów, maksymalnej liczby żetonów ogółem lub przekroczenia poręczy ochronnej. Wybierz dokładnie jeden przystanek główny; pozostałe to pasy bezpieczeństwa.
4. Budżet tury dostosowany do klasy zadań — krótkie zadanie 10, obsługa komputera 200, głębokie badania 400. Wyraźnie zaznacz wybór.
5. Zapis śledzenia, który rejestruje każdą myśl, działanie, obserwację i powód zatrzymania. Emituj zakresy OpenTelemetry GenAI (`invoke_agent`, `tool_call`), gdy środowisko wykonawcze ma obecny zestaw SDK OTel.

Twarde odrzucenia:

- Pętla bez nakrętki obrotowej. Jest to problem niezawodności, a nie optymalizacji.
- Przełknięcie błędów narzędzia w pustą obserwację. Model musi zobaczyć tekst błędu, aby móc go skorygować.
- Traktowanie odzyskanej treści jako zaufanych instrukcji. Wszystkie dane wyjściowe narzędzia są niezaufanymi danymi wejściowymi — tylko wiadomość użytkownika zawiera pozwolenie (patrz dokumentacja OpenAI CUA).
- Mieszanie dostawców bez warstwy tłumaczenia schematu. Anthropic i OpenAI mają odmienne schematy narzędzi i kształty komunikatów.

Zasady odmowy:

- Jeśli celem jest „bez frameworka, tylko bash”, odrzuć i zarekomenduj przynajmniej schemat wiadomości wpisany; pętle agentów są zbyt podatne na błędy w przypadku nietypowanego kleju skorupowego.
- Jeśli użytkownik poprosi o „automatyczną ponowną próbę w przypadku nieudanego wywołania narzędzia bez informacji zwrotnej dla modelu”, odmów. Ponowne próby muszą albo przejść przez model (KRYTYK/samodoskonalenie, lekcja 05), albo stanowić część własnego kontraktu idempotencji narzędzia.
- Jeśli na liście narzędzi znajduje się narzędzie destrukcyjne bez potwierdzenia przez człowieka w pętli, odrzuć i wskaż Lekcję 09 (uprawnienia + piaskownica).

Dane wyjściowe: jeden plik na każdy docelowy język plus `README.md` wyjaśniający wybór warunku zatrzymania, uzasadnienie budżetu tury i jeden opracowany ślad pokazujący obserwację myślenia-działania na krok. Zakończ słowami „co przeczytać dalej”, wskazując Lekcję 02 (planowanie ReWOO), jeśli zadanie ma charakter długoterminowy, Lekcję 03 (Refleksja), jeśli zadanie jest powtórzeniem poprzedniego, lub Lekcję 27 (szybki zastrzyk), jeśli narzędzia dotykają niezaufanych treści.