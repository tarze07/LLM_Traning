---

name: state-graph
description: Zbuduj maszynę stanów w stylu LangGraph z typowanym stanem, krawędziami warunkowymi, punktami kontrolnymi po każdym węźle i trwałym wznawianiem działania.
version: 1.0.0
phase: 14
lesson: 13
tags: [langgraph, state-machine, durable, checkpointing, human-in-the-loop]

---

W oparciu o docelowe środowisko uruchomieniowe, strukturę stanu, zestaw funkcji węzłów oraz backend punktów kontrolnych (checkpointera), utwórz graf agenta stanowego.

Wygeneruj:

1. Typowany `State` (słownik lub Pydantic). Udokumentuj każde pole. Węzły odczytują stan i zwracają słownik z aktualizacjami.
2. Klasę `StateGraph` z metodami `add_node`, `add_edge`, `add_conditional_edges`, `set_entry` oraz węzłami granicznymi `START`/`END`.
3. Interfejs `Checkpointer` oferujący metody `save(session_id, node, state)` oraz `load_latest(session_id)`. Domyślna implementacja powinna korzystać z SQLite; dopuść Postgres, Redis lub własne rozwiązania.
4. Moduł `Runner` przechodzący po grafie, serializujący stan po wykonaniu każdego węzła, przechwytujący wyjątek/sygnał `PausedAtNode` na potrzeby interakcji z człowiekiem (human-in-the-loop) oraz obsługujący metodę `resume_from` z opcjonalnym nadpisaniem stanu (`state_override`).
5. Trzy szablony topologii: nadzorca (centralny router), rój (przekazywanie zadań za pomocą wspólnych narzędzi) oraz hierarchiczny (zagnieżdżone podgrafy).

Kryteria odrzucenia (Hard rejects):

- Niedeterministyczne węzły bez przekazywania/przechwytywania ziarna losowości (seeds) lub czasu systemowego. Mechanizm wznawiania działania zakłada, że wynik węzła jest odtwarzalny przy tym samym stanie wejściowym.
- Checkpointer zapisujący wyłącznie stan skrócony („podsumowanie”). Serializacji musi podlegać pełny stan grafu, w przeciwnym razie mechanizm wznawiania działania ulegnie awarii.
- Grafy, w których każda krawędź jest krawędzią warunkową. Należy stosować czytelne, liniowe przepływ z nielicznymi rozgałęzieniami.

Zasady odmowy (Guardrails):

- Jeśli użytkownik żąda grafu stanowego dla zadania, które nie wymaga zachowania ciągłości stanu (persystencji/wznawiania), odmów. Grafy stanowe służą do trwałego wznawiania działania; jeśli ta funkcja jest zbędna, zasugeruj prostsze wzorce przepływu pracy z Lekcji 12.
- Jeśli użytkownik żąda zapisu punktów kontrolnych wyłącznie przy pomyślnym wykonaniu, odmów. Obsługa awarii bezwzględnie wymaga dostępu do stanu z momentu błędu – jest to kluczowe do debugowania.
- Jeśli graf składa się z ponad ok. 30 węzłów, odrzuć strukturę płaską i wymagaj stosowania zagnieżdżonych podgrafów. Płaskie grafy o takiej wielkości są nieczytelne i trudne w utrzymaniu.

Wygenerowana struktura: pliki `state.py`, `graph.py`, `checkpointer.py`, `runner.py` oraz `README.md` wyjaśniający schemat stanu, konfigurację checkpointera i semantykę wznawiania. Zakończ sekcją „Co czytać dalej”, odsyłając do Lekcji 14 (alternatywa w postaci modelu aktora), Lekcji 16 (przekazywanie zadań i guardrails) lub Lekcji 23 (śledzenie kroków grafu za pomocą OTel spans).
