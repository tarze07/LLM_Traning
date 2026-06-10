---
name: runtime-shape
description: Wybór modelu produkcyjnego środowiska uruchomieniowego (żądanie-odpowiedź, strumieniowanie, kolejka, zdarzenie, cron, trwałe) oraz integracja z systemami obserwowalności.
version: 1.0.0
phase: 14
lesson: 29
tags: [production, runtime, queue, event, durable, observability]
---

Mając zdefiniowaną klasę zadań (szacowany czas trwania, liczba kroków, typ wyzwalacza, dopuszczalne opóźnienia), dobierz odpowiedni model środowiska uruchomieniowego (runtime shape).

Zasady wyboru:

1. Czas wykonania < 30 s, użytkownik oczekuje na wynik -> Wybierz model **żądanie-odpowiedź** (request-response).
2. Wymagany progresywny interfejs użytkownika lub obsługa głosu -> Wybierz model **przesyłanie strumieniowe** (streaming).
3. Czas wykonania od minut do godzin, asynchroniczność -> Wybierz model **kolejkowy** (queue-based).
4. Reagowanie na wyzwalacze z systemów zewnętrznych -> Wybierz model **sterowany zdarzeniami** (event-driven).
5. Cykliczne prace administracyjne lub rutynowe -> Wybierz model **zadań cyklicznych** (cron).
6. Dowolny z powyższych scenariuszy, w którym koszt ponownego uruchomienia zadania w razie awarii jest wysoki -> Zintegruj **trwałe wykonywanie** (durable execution).

Zakres wdrożenia:

1. Szkielet kodu środowiska uruchomieniowego w wybranym stosie technologicznym.
2. Integracja z obserwowalnością: punkty zaczepienia (spans) OTel GenAI (lekcja 23) oraz integracja z platformą monitoringu (lekcja 24).
3. W modelu kolejkowym: konfiguracja kolejki DLQ, polityka ponawiania prób (retry policy) oraz monitorowanie długości kolejki (queue depth).
4. W modelu sterowanym zdarzeniami: rejestr subskrybentów oraz mechanizm ponownego odtwarzania zdarzeń (replay path).
5. W zadaniach cyklicznych (cron): plik blokady (lock file) lub blokada rozproszona zapobiegająca równoległemu nakładaniu się uruchomień (overlapping runs).
6. W trwałym wykonywaniu: wybór bazy danych dla checkpointera oraz zdefiniowanie logiki wznawiania procesów (resume semantics).

Kryteria odrzucenia (Hard Rejects):

- Stosowanie synchronicznych zapytań HTTP dla procesów trwających dłużej niż 30 sekund. Użytkownicy utracą połączenie, a serwery zostaną zablokowane przez nakładające się wątki robocze.
- Wdrażanie systemów kolejkowych bez obsługi Dead-letter queue (DLQ). Nieudane zadania bezpowrotnie znikną z systemu.
- Uruchamianie procesów w tle bez mechanizmów eksportu śladów (traces). Awarie pozostaną niewykryte, dopóki klienci nie zaczną zgłaszać błędów.
- Brak wdrożenia punktów kontrolnych stanu (checkpointing) przy długich procesach. Założenie „w razie awarii po prostu zaczniemy od zera” generuje wysokie koszty i ryzyko niespójności danych.

Zasady odmowy (Refusal Rules):

- Jeśli projekt nakłada rygorystyczne wymagania dotyczące SLA i odtwarzalności stanów, odmów wdrożenia topologii roju (swarm) w połączeniu z bezstanowym środowiskiem uruchomieniowym.
- Jeśli procesy biznesowe podlegają audytowi i wymogom compliance, odmów wdrożenia architektury sterowanej zdarzeniami bez kompletnych mechanizmów logowania zdarzeń.
- Jeśli użytkownik wnioskuje o wdrożenie zadań cron bez mechanizmów blokad (locks), odmów. Równoległe uruchomienie tego samego skryptu grozi uszkodzeniem danych.

Dane wyjściowe: Szkielet środowiska uruchomieniowego, punkty zaczepienia (hooks) dla obserwowalności oraz plik README.md dokumentujący SLA, polityki retencji/powtórzeń oraz architekturę checkpointingu. Zakończ sekcją „Co przeczytać dalej”, wskazującą na lekcję 23 (OTel), lekcję 24 (Platformy obserwowalności) lub lekcję 17 (Managed Agents do obsługi asynchronicznych operacji długoterminowych).
