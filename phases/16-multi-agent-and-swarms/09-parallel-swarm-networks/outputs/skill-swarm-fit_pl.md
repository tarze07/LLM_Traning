---

name: swarm-fit
description: Zdecyduj, czy zadanie pasuje do architektury roju (zdecentralizowanej), czy nadzorczej (scentralizowanej).
version: 1.0.0
phase: 16
lesson: 09
tags: [multi-agent, swarm, decentralized, langgraph, matrix]

---

Biorąc pod uwagę zadanie i jego wymagania dotyczące przepustowości/determinizmu, zarekomenduj rój lub nadzorcę i wypisz konkretne opcje kolejki i poręczy.

Wyprodukuj:

1. **Sprawdzanie niezależności zadań.** Czy podzadania są niezależne, czy też od siebie zależne? Rój pasuje tylko wtedy, gdy niezależność jest wysoka.
2. **Rozkład czasu trwania.** Jednolity vs zmienny. Swarm wygrywa głównie w przypadku obciążeń o zmiennym czasie trwania.
3. **Wymagania dotyczące zamówienia.** Rygorystyczne, swobodne lub żadne. Rój nie strzeże porządku; przełożony tak.
4. **Wymagana debugowalność.** Wysoki (finanse, medycyna) → przełożony. Średni → rój z identyfikatorami śledzenia dla poszczególnych zadań.
5. **Wybór kolejki.** W pamięci (`queue.Queue`) dla wersji demonstracyjnych; Kafka / Redis Streams / NATS / trwałe wsparcie DB do produkcji.
6. **Wymagania dotyczące projektu pracownika.** Musi być idempotentny; musi emitować ślad dla każdego zadania; musi poradzić sobie z przeciwciśnieniem.
7. **Plan przeciwdziałający głodowi.** Priorytetowe starzenie się, specjalizacja pracowników, ograniczona kolejka.
8. **Plan obserwowalności.** Identyfikatory poszczególnych zadań, zdarzenia początkowe/końcowe, schemat puli wyników.

Twarde odrzucenia:

- Rekomendacja roju dla zadań o trudnych wymaganiach dotyczących zamawiania.
- Rój bez idempotentnych pracowników.
- Rój bez trwałej kolejki w produkcji.

Zasady odmowy:

- Jeśli zadanie ma mniej niż 10 niezależnych jednostek na sekundę, odrzuć rój i poleć przełożonego. Narzut roju nie jest uzasadniony przy niskiej przepustowości.
- Jeśli wymagania obserwowalności wymagają jednego spójnego śladu (audyt, zgodność), odrzuć rój i zamiast tego poleć deterministyczny graf LangGraph.

Wynik: jednostronicowy brief architektoniczny. Otwórz z werdyktem dopasowania, zamknij z konkretnym zaleceniem brokera komunikatów dla docelowej przepustowości.