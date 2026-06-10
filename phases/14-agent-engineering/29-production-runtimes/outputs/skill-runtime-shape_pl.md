---
name: runtime-shape
description: Wybierz formę produkcyjnego środowiska uruchomieniowego (żądanie-odpowiedź, strumieniowanie, kolejka, zdarzenie, cron, trwałe) i zintegruj obserwowalność.
version: 1.0.0
phase: 14
lesson: 29
tags: [production, runtime, queue, event, durable, observability]
---

Mając daną klasę zadań (oczekiwany czas trwania, liczba kroków, typ wyzwalacza, budżet opóźnień), wybierz formę środowiska uruchomieniowego (runtime shape).

Decyzja:

1. < 30s, użytkownik czeka -> **żądanie-odpowiedź** (request-response).
2. Progresywny UX lub obsługa głosu -> **przesyłanie strumieniowe** (streaming).
3. Od minut do godzin, użytkownik nie czeka -> **oparte na kolejce** (queue-based).
4. Reagowanie na zdarzenia zewnętrzne -> **sterowane zdarzeniami** (event-driven).
5. Okresowe prace porządkowe -> **cron**.
6. Którekolwiek z powyższych, w których koszt restartu jest wysoki -> dodaj **trwałe wykonywanie** (durable execution).

Wytwórz:

1. Szkielet środowiska uruchomieniowego w wybranym stosie technologicznym.
2. Obserwowalność: punkty zaczepienia (spans) OTel GenAI (Lekcja 23), podpięty backend (Lekcja 24).
3. Dla kolejki: DLQ + polityka ponawiania prób (retry policy) + metryka długości kolejki (queue depth).
4. Dla zdarzeń: wyraźny rejestr subskrybentów + ścieżka odtwarzania (replay path).
5. Dla cron: plik blokady (lock file) lub blokada rozproszona, aby zapobiec nakładaniu się na siebie działań (overlapping runs).
6. Dla trwałego wykonywania: wybór backendu checkpointera + logika wznawiania (resume semantics).

Zdecydowanie odrzucaj:

- Synchroniczne zapytania HTTP dla 5-minutowych zadań. Użytkownicy rozłączą się; workerzy zaczną się piętrzyć.
- Działania kolejkowe bez DLQ (Dead-letter queue). Nieudane zadania po prostu wyparują.
- Działanie w tle bez funkcji eksportu śladów (trace export). Awarie są w zasadzie niewidoczne do momentu narzekania ze strony użytkowników.
- "Bez trwałego zapisu stanu, zwyczajnie to powtórzymy." Przy dłuższym horyzoncie zapisu stan kontrolny (checkpointing) musi wystąpić.

Zasady odmowy:

- Jeśli projekt ma wymagania SLA + powtórnego odtwarzania, odmów zastosowania topologii roju (swarm) + środowiska bez trwałego zapisywania stanu (non-durable runtime).
- Jeśli zadanie jest obwarowane wymogami zgodności (compliance), odmów użycia środowiska sterowanego zdarzeniami bez mechanizmów audytu.
- Jeśli użytkownik chce zadań cyklicznych (cron) bez żadnej blokady, odmów. Nakładające się uruchomienia zadania to w najlepszym wypadku zduplikowana praca, a w najgorszym - korupcja danych.

Dane wyjściowe: szkielet środowiska uruchomieniowego + punkty zaczepienia (hooks) na potrzeby obserwacji + README uwzględniające SLA, politykę powtórzeń oraz wybór checkpointera. Zakończ punktem "co czytać dalej", wskazującym na Lekcję 23 (OTel), Lekcję 24 (obserwowalność) lub Lekcję 17 (Managed Agents na potrzeby obsługi hostowanych zadań asynchronicznych o długim czasie trwania).