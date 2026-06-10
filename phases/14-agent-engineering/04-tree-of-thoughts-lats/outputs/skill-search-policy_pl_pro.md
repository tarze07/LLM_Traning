---

name: search-policy
description: Dobierz odpowiednią strategię przeszukiwania przestrzeni stanów (ReAct, ToT, LATS, ewolucyjna) na podstawie struktury zadania, budżetu tokenów oraz wiarygodności modułu oceniającego.
version: 1.0.0
phase: 14
lesson: 04
tags: [tree-of-thoughts, lats, mcts, search, value-function]

---

Na podstawie struktury zadania (jedna odpowiedź / wiele odpowiedzi / otwarte), budżetu tokenów oraz typu dostępnego ewaluatora (testy skalarne / heurystyki / samoocena) przygotuj rekomendację strategii przeszukiwania wraz ze szczegółowymi parametrami.

Przygotuj:

1. Rekomendacja strategii: Wybierz jedno z podejść: liniowa pętla ReAct, przeszukiwanie wiązkowe ToT (z szerokością wiązki k), wyszukiwanie wszerz BFS ToT (z określoną maksymalną głębokością), wyszukiwanie w głąb DFS ToT z przycinaniem gałęzi, algorytm MCTS LATS (z podaniem liczby iteracji i stałej UCT c) lub przeszukiwanie ewolucyjne (tylko w przypadku, gdy ocena poprawności jest w pełni zautomatyzowana i programowo weryfikowalna).
2. Dobór parametrów: Zdefiniuj domyślne wartości parametrów dla wybranej metody (np. szerokość wiązki, limit głębokości, współczynnik rozgałęzienia K, liczba symulacji rollout na poziom, stała UCT c – domyślnie 1.4, limit czasu).
3. Definicja funkcji wartości: Określ precyzyjnie kryteria oceny węzła. Możliwe opcje to: wskaźnik zaliczonych testów jednostkowych, matematyczna miara odległości od celu, ocena modelu LLM na podstawie promptu (w formacie pewny/prawdopodobny/niemożliwy, w skali 1-10 lub poprzez głosowanie) bądź też bezpośrednia nagroda zwrotna ze środowiska.
4. Szacunkowy koszt tokenów: Oblicz pesymistyczny wariant zużycia tokenów według wzoru: `współczynnik_rozgałęzienia ^ głębokość * średnia_liczba_tokenów_promptu`. Przedstaw wyliczoną wartość liczbową. Jeśli szacowany koszt przekracza limit zadeklarowany przez użytkownika, zarekomenduj tańszą strategię.
5. Obsługa sytuacji awaryjnych: Wskaż dwa główne scenariusze błędów dla wybranej strategii oraz metody ich zapobiegania (np. w przypadku LATS z mało precyzyjnym ewaluatorem – zalecaj wdrożenie dodatkowej weryfikacji opartej na narzędziach zgodnie z wzorcem Krytyka, Lekcja 05).

Kryteria odrzucenia:
- Rekomendowanie zaawansowanego przeszukiwania drzewa w sytuacjach, gdy ocena stanów jest niewiarygodna (np. opiera się wyłącznie na samoocenie modelu, bez danych referencyjnych). W takich przypadkach należy powrócić do prostszej pętli ReAct + Krytyk.
- Ustawianie współczynnika rozgałęzienia K na wartość powyżej 5 bez wyraźnego uzasadnienia. Standardowe badania wskazują na wartości K=3-5; wyższe wartości (np. K=10) prowadzą do gwałtownego wzrostu kosztów.
- Wykorzystywanie LATS do zadań typu chat. Złożone przeszukiwanie nie przynosi korzyści w zwykłej konwersacji, o ile nie stawia ona przed agentem mierzalnego, programowego celu.
- Stosowanie przeszukiwania ewolucyjnego bez zautomatyzowanego, maszynowego systemu weryfikacji poprawności. Podejście typu AlphaEvolve ma sens jedynie wtedy, gdy ocena przystosowania (fitness) jest realizowana programowo (np. poprzez uruchomienie testów, pomiar wydajności lub formalną weryfikację dowodu).

Zasady odmowy wykonania zadania:
- Jeśli dostępny budżet tokenów jest mniejszy niż pięciokrotność kosztu pojedynczej ścieżki wnioskowania, odmów wdrożenia wyszukiwania i rekomenduj pętlę ReAct + Reflexion (Lekcja 03).
- Jeśli dopuszczalny czas odpowiedzi (latency) wynosi poniżej 10 sekund, odrzuć LATS i rekomenduj standardowy ReAct.
- Jeśli zadanie polega wyłącznie na wyszukiwaniu i agregowaniu informacji, odmów stosowania przeszukiwania stanów i zalecaj strukturę ReWOO (Lekcja 02).

Oczekiwany rezultat: Blok rekomendacji (wybrana strategia, parametry, definicja funkcji wartości oraz szacowany koszt tokenów) oraz sekcja „Sugerowane lektury” odsyłająca do Lekcji 05 (Krytyk) – w celu poprawy wiarygodności oceny stanów, Lekcji 11 (AlphaEvolve) – dla wariantów ewolucyjnych, lub Lekcji 30 (Rozwój oparty na ewaluacji) – pod kątem walidacji na poziomie benchmarków.
