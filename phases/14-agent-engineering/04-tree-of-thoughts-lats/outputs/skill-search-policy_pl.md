---

name: search-policy
description: Wybierz strategię wyszukiwania (ReAct, ToT, LATS, ewolucyjna), biorąc pod uwagę kształt zadania, budżet tokena i jakość oceniającego.
version: 1.0.0
phase: 14
lesson: 04
tags: [tree-of-thoughts, lats, mcts, search, value-function]

---

Biorąc pod uwagę kształt zadania (jedna odpowiedź / wiele odpowiedzi / otwarte), budżet tokenów i dostępny ewaluator (test skalarny / heurystyka / samoocena), utwórz rekomendację strategii wyszukiwania z konkretnymi parametrami.

Wyprodukuj:

1. Decyzja. Jedno z nich: liniowy ReAct, belka ToT (z szerokością wiązki k), BFS ToT (z maksymalną głębokością), DFS ToT z przycinaniem, MCTS LATS (z iteracjami i UCT c), wyszukiwanie ewolucyjne (tylko jeśli ewaluator jest programowy i sprawdzalny).
2. Parametry. Dla każdej strategii konkretne wartości domyślne: szerokość belki, ograniczenie głębokości, współczynnik rozgałęzienia K, wdrożenia na poziom, UCT c (domyślnie 1.4), limit czasu.
3. Funkcja wartości. Określ dokładnie, co ocenia węzeł. Opcje: współczynnik zaliczenia testu jednostkowego, liczbowa odległość do celu, wynik LLM z podpowiedzią w formacie (pewny/prawdopodobny/niemożliwy lub 1..10 lub głos) lub nagroda środowiskowa.
4. Szacunkowy budżet tokenowy. Tokeny w najgorszym przypadku = współczynnik_rozgałęzienia ^ głębokość * avg_prompt_tokens. Pokaż numer. Jeśli przekracza budżet użytkownika, zarekomenduj tańszą strategię.
5. Tryby awarii. Dla każdej wybranej strategii wypisz dwa główne tryby awarii i sposoby ich łagodzenia (np. LATS + zaszumiony ewaluator -> dodaj weryfikację opartą na narzędziach według KRYTYKA, lekcja 05).

Twarde odrzucenia:

- Zalecanie poszukiwań, gdy osoba oceniająca jest niewiarygodna (tylko samoocena, bez podstawowej prawdy). Wróć do ReAct + KRYTYK.
- Ustawienie współczynnika rozgałęzienia K na wartość wyższą niż 5 bez ważnego powodu. K=3-5 to domyślny papier; K=10 koszt wybuchów.
- Stosowanie LATS do zadań w stylu czatu. Wyszukiwanie nie pomaga w konwersacyjnych pytaniach i odpowiedziach bez celu programowego.
- Poszukiwanie ewolucyjne bez sprawności sprawdzanej maszynowo. AlphaEvolve jest interesująca tylko wtedy, gdy sprawność ma charakter programowy (przeprowadź testy, zmierz prędkość, zweryfikuj twierdzenie).

Zasady odmowy:

- Jeśli budżet tokena < 5x koszt pojedynczej trajektorii, odmów wyszukiwania i zaleć ReAct + Reflexion (Lekcja 03).
- Jeśli budżet opóźnienia zegara ściennego < 10 sekund, odrzuć LATS i zaleć ReAct.
- Jeśli zadaniem jest wyłącznie wyszukiwanie informacji, odmów wyszukiwania i poleć ReWOO (Lekcja 02).

Dane wyjściowe: blok rekomendacji (wybrana strategia, parametry, funkcja wartości, szacunkowy budżet) plus uwaga „co dalej czytać” wskazująca Lekcję 05 (KRYTYCZNOŚĆ) w przypadku wiarygodności ewaluatora, Lekcję 11 (AlphaEvolve) w przypadku wariantów ewolucyjnych lub Lekcję 30 (rozwój oparty na ewaluacji) w celu walidacji na poziomie benchmarku.