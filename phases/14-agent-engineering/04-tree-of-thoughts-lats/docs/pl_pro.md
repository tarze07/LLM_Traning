# Drzewo Myśli (ToT) i LATS: celowe przeszukiwanie

> W klasycznym, liniowym łańcuchu myśli (CoT) nie ma możliwości wycofania się z błędnej ścieżki. Metoda Tree of Thoughts (ToT; Yao i in., 2023) przekształca proces rozumowania w strukturę drzewiastą z samooceną w każdym węźle. Z kolei LATS (Zhou i in., 2024) łączy ToT, ReAct oraz Reflexion w ramach przeszukiwania drzew Monte Carlo (MCTS). Skuteczność w grze logicznej „Game of 24” wzrasta dzięki ToT z 4% (dla CoT) do 74%, natomiast LATS osiąga wynik 92,7% pass@1 w teście HumanEval.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (Pętla agenta), Faza 14 · 03 (Odbicie)
**Czas:** ~75 minut

## Cele nauczania

- Zrozumienie procesu rozumowania jako wyszukiwania: węzły reprezentują „myśli”, krawędzie to „ścieżki rozwoju”, a wartości określają stopień przydatności danego rozwiązania.
- Zaimplementuj przeszukiwanie drzewa metodą BFS w stylu ToT, korzystając wyłącznie z biblioteki standardowej (stdlib), z dodaniem samooceny stanów.
- Rozbuduj rozwiązanie do uproszczonej pętli LATS MCTS obejmującej fazy wyboru, rozwijania, symulacji i wstecznej propagacji.
- Określ, kiedy zaawansowane przeszukiwanie uzasadnia zwielokrotnienie liczby zużytych tokenów (np. w grze 24, generowaniu kodu), a kiedy w zupełności wystarczy pojedyncza ścieżka wnioskowania (proste pytania i odpowiedzi).

## Problem

Łańcuch myśli (CoT) to proces liniowy. Jeśli pierwszy krok okaże się błędny, wszystkie kolejne etapy będą opierać się na fałszywych założeniach. W grze logicznej „Game of 24” (polegającej na wykonaniu działań arytmetycznych na czterech liczbach tak, aby wynik wynosił 24) GPT-4 z podejściem CoT osiąga zaledwie 4% dokładności. Model na wczesnym etapie wybiera niewłaściwe podwyrażenie i nie ma możliwości skorygowania tej decyzji.

Rozumowanie wymaga zdolności generowania wielu alternatywnych rozwiązań, ich oceny, wybierania najbardziej obiecujących ścieżek oraz wycofywania się ze ślepych zaułków. To klasyczny problem przeszukiwania przestrzeni stanów. Tree of Thoughts (Drzewo Myśli) oraz LATS to dwa podstawowe podejścia realizujące ten wzorzec.

## Koncepcja

### Drzewo myśli (Yao i in., NeurIPS 2023)

Każdy węzeł reprezentuje spójny krok pośredni („myśl”). Z każdego węzła można wyprowadzić K węzłów potomnych. Model LLM samodzielnie ocenia przydatność każdego węzła za pomocą odpowiedniego promptu oceniającego. Algorytm eksploruje powstałe drzewo za pomocą wyszukiwania wszerz (BFS), w głąb (DFS) lub przeszukiwania wiązkowego (beam search).

```
                     (root: "find 24 from 4 6 4 1")
                    /               |            \
           ("6 - 4 = 2")    ("4 + 1 = 5")    ("4 * 6 = 24")  <- Score: HIGH
              /   \              |                  |
          ...    ...          ...                finish
```

Kluczowym elementem systemu jest moduł samooceny. W publikacji przedstawiono three warianty: klasyfikację (`sure / likely / impossible`), ocenę punktową (`1..10`) oraz bezpośrednie głosowanie na najlepszego kandydata. Wszystkie te metody pozwoliły drastycznie poprawić wyniki w grze logicznej 24 w porównaniu do CoT (wzrost z 4% do 74% przy użyciu GPT-4).

### LATS (Zhou i in., ICML 2024)

LATS (Language Agent Tree Search) integruje podejścia ToT, ReAct oraz Reflexion w ramach algorytmu przeszukiwania drzew Monte Carlo (MCTS). Model LLM pełni w nim trzy role:

- **Polityka (Policy)**: generuje propozycje kolejnych działań (w stylu ReAct).
- **Funkcja wartości (Value function)**: ocenia częściowe ścieżki (samoocena w stylu ToT).
- **Refleksja (Reflexion)**: w przypadku niepowodzenia formułuje wnioski w języku naturalnym i wykorzystuje je do modyfikacji przyszłych ścieżek działania.

Informacje zwrotne ze środowiska (obserwacje) są łączone z funkcją wartości, co sprawia, że wyszukiwanie opiera się na realnych wynikach działania narzędzi, a nie tylko na subiektywnej ocenie modelu. Wyniki opublikowane w artykule: 92,7% pass@1 w teście HumanEval przy użyciu GPT-4 (ówczesny rekord SOTA) oraz średni wynik 75,9 w środowisku WebShop przy użyciu GPT-3.5 (porównywalny z modelami dostrajanymi gradientowo).

### MCTS, minimalnie

Cztery fazy w każdej iteracji:

1. **Wybór (Selection)** – przejście od węzła głównego do liścia z wykorzystaniem reguły UCT (Upper Confidence Bound applied to Trees).
2. **Rozszerzanie (Expansion)** – wygenerowanie K węzłów potomnych przy użyciu polityki.
3. **Symulacja (Simulation)** – przeprowadzenie próby (rollout) od nowego węzła z użyciem polityki i ocena stanu końcowego za pomocą funkcji wartości (lub zewnętrznej nagrody ze środowiska).
4. **Wsteczna propagacja (Backpropagation)** – uaktualnienie statystyk odwiedzin oraz wartości szacunkowych dla wszystkich węzłów na ścieżce prowadzącej do ocenionego stanu.

Wzór UCT: `Q(s, a) + c * sqrt(ln N(s) / N(s, a))`. Pierwszy człon odpowiada za eksploatację (wykorzystanie znanych dobrych stanów), drugi zaś za eksplorację (badanie mniej znanych ścieżek). Stałą `c` należy dostroić do specyfiki zadania.

### Rzeczywistość kosztowa

Złożone przeszukiwanie generuje ogromne zużycie tokenów. Metoda ToT w grze 24 zużywa od 100 do 1000 razy więcej tokenów niż standardowy łańcuch CoT. W przypadku LATS koszty są zbliżone. Z tego powodu przeszukiwanie należy rezerwować dla specyficznych zastosowań:

- Zadań, w których pojedyncza ścieżka wnioskowania jest wysoce niewystarczająca (np. gra 24, zaawansowane programowanie).
- Zadań, w których poprawność wyniku jest kluczowa, a czas odpowiedzi (latency) ma znaczenie drugorzędne.
- Zadań z jednoznaczną, łatwą do zweryfikowania funkcją oceny stanu (np. testy jednostkowe w kodzie, konkretny wynik równania matematycznego).

Jeśli zadanie ma tylko jedną właściwą odpowiedź, a ocena pośrednia (Evaluator) charakteryzuje się dużym szumem, algorytmy wyszukiwania mogą wręcz pogorszyć rezultaty, wybierając błędne rozwiązania, które przypadkowo uzyskały wysoką ocenę.

### Pozycjonowanie 2026

Większość produkcyjnych wdrożeń agentów nie korzysta bezpośrednio z LATS. Zamiast tego opierają się one na pętli ReAct z automatyczną weryfikacją wyników (wzorzec Krytyka, Lekcja 05). Metody przeszukiwania są stosowane głównie w wyspecjalizowanych niszach:

- W agentach programistycznych, gdzie testy jednostkowe pełnią funkcję weryfikacji stanów (jak w HumanEval).
- W systemach badawczych (Deep Research) analizujących równolegle wiele wątków zapytań.
- W złożonych przepływach pracy wymagających planowania w podgrafach LangGraph.

AlphaEvolve (Lekcja 11) to przykład zaawansowanego podejścia: ewolucyjne przeszukiwanie kodu z maszynową weryfikacją poprawności, które pozwoliło na wypracowanie nowatorskich rozwiązań (jak pierwsze od 56 lat przyspieszenie mnożenia macierzy 4x4).

## Zbuduj to

Plik `code/main.py` implementuje:

- Uproszczoną wersję ToT BFS realizującą zadanie doboru operacji arytmetycznych.
- Minimalną wersję pętli LATS MCTS dla tego samego zadania (wybór, rozwijanie, symulacja, wsteczna propagacja) z wykorzystaniem reguły UCT.
- Funkcję wartości łączącą ocenę regułową (symboliczną) z samooceną modelu LLM.

Uruchomienie:

```
python3 code/main.py
```

Logi (ślad wykonania) pokazują, że ToT rozwija trzech kandydatów na węzeł za pomocą BFS, podczas gdy LATS zbiega się ku optymalnej ścieżce dzięki MCTS. Dla obu podejść wypisujemy liczbę zużytych tokenów.

## Użyj tego

LangGraph wspiera eksplorację przestrzeni stanów w stylu ToT za pomocą szablonów podgrafów. Szczegółowym źródłem wiedzy jest artykuł na blogu LangChain poświęcony LATS (maj 2024). Biblioteka LlamaIndex udostępnia wbudowanego agenta `TreeOfThoughts`. W większości systemów produkcyjnych wzorzec ten jest aktywowany warunkowo (np. za pomocą reguły `if task_complexity > threshold: use_search()`) – patrz wzorzec oceniający-optymalizator w Lekcji 05.

## Wyślij to

Plik `outputs/skill-search-policy.md` opisuje proces wyboru pomiędzy liniową pętlą ReAct, ToT, LATS a przeszukiwaniem ewolucyjnym na podstawie struktury zadania, budżetu tokenów i wiarygodności modułu oceniającego.

## Ćwiczenia

1. Przetestuj uproszczony model LATS z parametrem eksploracji UCT c=0.1 oraz c=2.0. Jak zmienia się przebieg wykonania?
2. Wprowadź szum do funkcji wartości (np. dodając losowe fluktuacje wyników). Czy algorytm MCTS wciąż potrafi zidentyfikować optymalny węzeł końcowy? Jaki minimalny stosunek sygnału do szumu (SNR) jest w stanie tolerować?
3. Zaimplementuj ToT z przeszukiwaniem wiązkowym (utrzymując k najlepszych stanów na każdym poziomie) i porównaj wyniki z BFS. Które podejście jest efektywniejsze przy ograniczonym budżecie tokenów?
4. Zapoznaj się z sekcją 5.1 artykułu o LATS. Przeanalizuj liczbę trajektorii dla HumanEval: ile prób (rollouts) było wymaganych do osiągnięcia raportowanego wskaźnika pass@1?
5. Przeanalizuj fragment artykułu o LATS poświęcony sytuacjom, w których algorytm ten przynosi mniejsze korzyści. Sformułuj jednoakapitową regułę decyzyjną dopasowującą charakterystykę zadania do odpowiedniej strategii wyszukiwania.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to w rzeczywistości oznacza |
|------|----------------|--------------------------------------|
| Tree of Thoughts | „Rozgałęzianie CoT” | Wzorzec (Yao i in.) – drzewo węzłów reprezentujących myśli z mechanizmem samooceny pośrednich stanów. |
| LATS | „MCTS dla agentów LLM” | Wzorzec (Zhou i in.) integrujący ToT, ReAct i Reflexion w ramach wyszukiwania MCTS. |
| UCT | „Górna granica ufności dla drzew” | Wzór optymalizujący wybór węzła przez równoważenie eksploatacji (Q) i eksploracji (ln N/n). |
| Funkcja wartości | „Ocena atrakcyjności stanu” | Wynik działania reguły lub ocena LLM zasilająca algorytm wyboru kolejnego kroku. |
| Polityka (Policy) | „Generator kolejnych kroków” | Moduł (np. w stylu ReAct) generujący propozycje kolejnych myśli lub akcji. |
| Rollout | „Symulacja ścieżki” | Przejście od wybranego węzła do stanu końcowego (liścia) w celu oceny jego wartości. |
| Wsteczna propagacja | „Aktualizacja wartości przodków” | Przeniesienie oceny z węzła końcowego w górę drzewa w celu uaktualnienia statystyk odwiedzin oraz wartości Q. |
| Koszt wyszukiwania | „Wzrost zużycia tokenów” | Wysokie zapotrzebowanie na zasoby (nawet 100-1000x więcej tokenów niż CoT) wymagające wcześniejszego planowania budżetu. |

## Dalsze czytanie

- [Yao i in., Tree of Thoughts (arXiv:2305.10601)](https://arxiv.org/abs/2305.10601) — artykuł kanoniczny
- [Zhou i in., LATS (arXiv:2310.04406)](https://arxiv.org/abs/2310.04406) — MCTS ze sprzężeniem zwrotnym Reflexion
- [Omówienie LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) — wzorce podgrafów do wyszukiwania
- [AlphaEvolve (arXiv:2506.13131)](https://arxiv.org/abs/2506.13131) — wyszukiwanie ewolucyjne za pomocą ewaluatorów programowych
