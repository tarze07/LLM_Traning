---

name: debate
description: Stwórz szkielet debaty wieloagentowej z N debatantami, rundami R, konfigurowalną topologią (pełna siatka, gwiazda, pierścień) i regułą zbieżności.
version: 1.0.0
phase: 14
lesson: 25
tags: [debate, multi-agent, society-of-minds, sparse-topology]

---

Biorąc pod uwagę klasę pytań i cel dokładności, przygotuj protokół debaty.

Wyprodukuj:

1. `Debater` z różnymi podpowiedziami (i idealnie różnymi modelami), aby uniknąć homogenizacji.
2. Runda okrągła: topologia z pełną siatką, gwiazdą lub pierścieniem.
3. Zasada konwergencji: głos większościowy ważony wotum zaufania lub większość przeważająca z rezerwą.
4. Runda 1 wymuszona niezgoda: każdy debatujący, jeśli to możliwe, przedstawia odrębną propozycję.
5. Rachunek kosztów: całkowita liczba operacji krytycznych + koszt symboliczny na pytanie.

Twarde odrzucenia:

- Wszyscy debatanci z tym samym podpowiedzią ORAZ tym samym modelem. Gwarantowane myślenie grupowe.
- Pełne oczko z N >= 6 bez sprawdzania kosztów. Skala operacji debaty O(N*R).
- Brak reguły zbieżności. Zwrócenie odpowiedzi debatanta 0 w postaci okrągłego R nie jest zbieżnością.

Zasady odmowy:

- Jeśli produkt jest wrażliwy na opóźnienia (budżet <1 s), odrzuć debatę. Zamiast tego użyj samodoskonalenia (lekcja 05) lub głosowania równoległego (lekcja 12).
- Jeśli klasa pytań dotyczy prostego wyszukiwania faktów (wielka litera, data, definicja), odrzuć debatę. Wyszukiwanie + KRYTYK (Lekcja 05) jest tańsze.
- Jeżeli po pierwszej rundzie debatujący nie mają różnicy zdań w jakiejkolwiek kwestii w zestawie ewaluacyjnym, odrzuć protokół. Potrzebujesz różnorodności modeli / podpowiedzi.

Dane wyjściowe: `debater.py`, `topology.py`, `convergence.py`, `runner.py`, `README.md` wyjaśniające wybór N/R, uzasadnienie topologii oraz pomiary stosunku kosztu do dokładności w zestawie ewaluacyjnym. Zakończ słowami „Co przeczytać dalej”, wskazując Lekcję 12 (wzorce przepływu pracy), jeśli zadanie jest prostsze, lub Lekcję 28 (wzorce aranżacji), aby osadzić debatę w większym systemie.