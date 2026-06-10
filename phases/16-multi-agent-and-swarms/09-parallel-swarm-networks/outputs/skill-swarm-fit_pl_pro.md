---

name: swarm-fit
description: Zdecyduj, czy zadanie pasuje do architektury roju (zdecentralizowanej), czy architektury z nadzorcą (scentralizowanej).
version: 1.0.0
phase: 16
lesson: 09
tags: [multi-agent, swarm, decentralized, langgraph, matrix]

---

Na podstawie analizy zadania oraz jego wymagań dotyczących przepustowości i determinizmu, zarekomenduj architekturę roju lub nadzorcy, a także wskaż konkretne opcje kolejek i mechanizmów zabezpieczających (guardrails).

Opracuj:

1. **Ocena niezależności zadań.** Czy podzadania są niezależne, czy powiązane zależnościami? Architektura roju sprawdza się tylko przy wysokim stopniu niezależności zadań.
2. **Rozkład czasu wykonania.** Jednolity kontra zmienny. Rój (swarm) sprawdza się najlepiej przy obciążeniach o dużej zmienności czasu wykonania.
3. **Wymagania dotyczące kolejności.** Rygorystyczne, elastyczne lub brak. Architektura roju nie gwarantuje zachowania kolejności; architektura z nadzorcą tak.
4. **Wymagany poziom debugowalności.** Wysoki (np. finanse, medycyna) → nadzorca. Średni → rój z identyfikatorami śledzenia (trace IDs) dla poszczególnych zadań.
5. **Wybór kolejki.** Kolejka w pamięci (`queue.Queue`) dla wersji demonstracyjnych; Kafka / Redis Streams / NATS / trwała baza danych w środowisku produkcyjnym.
6. **Wymagania dotyczące implementacji wykonawcy (workera).** Musi być idempotentny; musi generować logi śledzenia (trace) dla każdego zadania; musi radzić sobie z przeciążeniem (backpressure).
7. **Strategia zapobiegania zagłodzeniu zadań (starvation).** Priorytetyzacja wiekowa (aging), specjalizacja wykonawców, ograniczona pojemność kolejki (bounded queue).
8. **Plan obserwowalności (observability).** Identyfikatory zadań (task IDs), zdarzenia rozpoczęcia/zakończenia, schemat agregacji wyników (results pool).

Kryteria wykluczające architekturę roju:

- Zalecenie roju dla zadań o rygorystycznych wymaganiach dotyczących kolejności.
- Rój bez idempotentnych wykonawców (workers).
- Rój bez trwałej kolejki w środowisku produkcyjnym.

Zasady wykluczenia:

- Jeśli natężenie zadań wynosi mniej niż 10 niezależnych jednostek na sekundę, odrzuć architekturę roju i zaleć nadzorcę. Narzut wydajnościowy roju nie jest uzasadniony przy niskiej przepustowości.
- Jeśli wymogi obserwowalności wymagają jednego, spójnego śladu wykonania (audyt, zgodność z przepisami), odrzuć rój i zaleć deterministyczny graf (np. w LangGraph).

Format wyjściowy: jednostronicowy brief architektoniczny. Rozpocznij od werdyktu dotyczącego dopasowania architektury, a zakończ konkretną rekomendacją brokera komunikatów dostosowaną do docelowej przepustowości.
