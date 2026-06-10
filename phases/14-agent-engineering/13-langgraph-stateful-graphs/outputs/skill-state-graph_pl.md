---

name: state-graph
description: Zbuduj maszynę stanów w kształcie LangGrapha ze stanem wpisanym, krawędziami warunkowymi, punktami kontrolnymi dla poszczególnych węzłów i trwałym CV.
version: 1.0.0
phase: 14
lesson: 13
tags: [langgraph, state-machine, durable, checkpointing, human-in-the-loop]

---

Biorąc pod uwagę docelowy czas wykonania, kształt stanu, zestaw funkcji węzła i zaplecze wskaźnika kontrolnego, utwórz graf agenta stanowego.

Wyprodukuj:

1. Wpisany `State` (dict lub Pydantic). Dokumentuj każde pole. Węzły czytają stan; zwracają aktualizacje.
2. `StateGraph` z `add_node`, `add_edge`, `add_conditional_edges`, `set_entry` i strażnikami `START`/`END`.
3. Interfejs `Checkpointer` z `save(session_id, node, state)` i `load_latest(session_id)`. Domyślnie SQLite; zezwól na Postgres/Redis/custom.
4. `Runner`, który przechodzi przez wykres, serializuje stan po każdym węźle, przechwytuje `PausedAtNode` w poszukiwaniu człowieka w pętli i obsługuje `resume_from` z opcjonalnym `state_override`.
5. Trzej pomocnicy topologii: nadzorca (router centralny), rój (przekazywanie współdzielonych narzędzi), hierarchiczny (podgrafy).

Twarde odrzucenia:

- Węzły niedeterministyczne bez jawnego przechwytywania losowego lub zegara ściennego. Wznów zakłada się, że dane wyjściowe węzła są odtwarzalne przy danym stanie wejściowym.
- Wskaźnik kontrolny, który zapisuje tylko stan „podsumowania”. Serializuj pełny stan lub wznawiaj przerwy.
- Wykresy, w których każda krawędź jest warunkowa. Preferuj łańcuchy liniowe z okazjonalnymi rozgałęzieniami.

Zasady odmowy:

- Jeśli użytkownik bez uporu poprosi o wykres stanu, odmów. Chodzi o trwałe CV; jeśli nie potrzebujesz CV, skorzystaj ze wzorców przepływu pracy z Lekcji 12.
- Jeśli użytkownik poprosi o „punkt kontrolny tylko w przypadku powodzenia”, odmów. Awarie również wymagają stanu — od tego zaczyna się debugowanie.
- Jeśli graf ma więcej niż ~30 węzłów, odrzuć układ płaski i wymagaj zagnieżdżonych podgrafów. Płaskich wykresów 30-węzłowych nie można przeglądać.

Dane wyjściowe: `state.py`, `graph.py`, `checkpointer.py`, `runner.py`, `README.md` wyjaśniające schemat stanu, wybór punktu kontrolnego i semantykę wznowienia. Zakończ słowami „Co dalej czytać”, wskazując Lekcję 14 na temat alternatywy modelu aktora, Lekcję 16 na temat warstwy przekazań/poręczy ochronnych lub Lekcji 23 na temat rozpiętości OTel na krokach wykresu.