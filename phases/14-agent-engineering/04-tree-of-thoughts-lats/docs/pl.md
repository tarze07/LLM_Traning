# Drzewo myśli i LATS: celowe wyszukiwanie

> W przypadku pojedynczej trajektorii łańcucha myślowego nie ma miejsca na wycofanie się. ToT (Yao i in., 2023) zamienia rozumowanie w drzewo z samooceną w każdym węźle. LATS (Zhou i in., 2024) ujednolica ToT z ReAct i Reflexion w ramach wyszukiwania drzewa Monte Carlo. Gra 24 wzrasta z 4% (CoT) do 74% (ToT); LATS osiąga 92,7% pass@1 w HumanEval.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (Pętla agenta), Faza 14 · 03 (Odbicie)
**Czas:** ~75 minut

## Cele nauczania

- Rozumowanie ramowe jako wyszukiwanie: węzły to „myśli”, krawędzie to „rozszerzenia”, wartość to „jak obiecujące”.
- Zaimplementuj przeszukiwanie drzewa BFS w stylu stdlib ToT z punktacją samooceny.
- Rozszerzenie do zabawkowej pętli LATS MCTS z wyborem / rozwinięciem / symulacją / propagacją wsteczną.
- Zdecyduj, kiedy wyszukiwanie jest warte mnożnika tokena (gra w 24, generowanie kodu), a kiedy wystarczy pojedyncza trajektoria (proste pytania i odpowiedzi).

## Problem

Łańcuch myśli to spacer liniowy. Jeśli pierwszy krok jest błędny, każdy kolejny opiera się na złych założeniach. W grze 24 (użyj czterech cyfr z + − × ÷, aby uzyskać 24), GPT-4 CoT osiąga dokładność 4%. Model wcześnie wybiera nieprawidłowe podwyrażenie i nie może go odzyskać.

Rozumowanie wymaga umiejętności zaproponowania wielu kandydatów, oceny ich, wybrania obiecujących i wycofania się, gdy pojawią się ślepe zaułki. To jest szukanie. Drzewo Myśli i LATS to dwa kanoniczne sformułowania.

## Koncepcja

### Drzewo myśli (Yao i in., NeurIPS 2023)

Każdy węzeł jest spójnym krokiem pośrednim („myślą”). Każdy węzeł może rozwinąć się do K myśli dziecka. LLM samodzielnie ocenia każdy węzeł, wyświetlając monit o ocenę. Wyszukiwanie eksploruje drzewo — BFS, DFS lub belkę.

```
                     (root: "find 24 from 4 6 4 1")
                    /               |            \
           ("6 - 4 = 2")    ("4 + 1 = 5")    ("4 * 6 = 24")  <- Score: HIGH
              /   \              |                  |
          ...    ...          ...                finish
```

Samoocena jest elementem nośnym. W artykule przedstawiono trzy warianty: klasyfikację `sure / likely / impossible`, ocenę liczbową `1..10` oraz głosowanie pomiędzy kandydatami. Cała trójka znacznie pokonała CoT w grze 24 (4% -> 74% z GPT-4).

### LATS (Zhou i in., ICML 2024)

LATS ujednolica ToT, ReAct i Reflexion w ramach MCTS. LLM odgrywa trzy role:

- **Polityka**: proponuj kolejne działania kandydata (w stylu ReAct).
- **Funkcja wartości**: zdobądź częściową trajektorię (samoocena w stylu ToT).
- **Refleksja**: w przypadku niepowodzenia napisz refleksję w języku naturalnym (w stylu refleksji) i użyj jej do ponownego zaplanowania przyszłych wdrożeń.

Informacje zwrotne ze środowiska (obserwacje) łączą się z funkcją wartości, dzięki czemu wyszukiwanie opiera się na rzeczywistych wynikach narzędzi, a nie tylko opiniach modeli. Wyniki w momencie publikacji artykułu: HumanEval pass@1 92,7% z GPT-4 (SOTA), średnia WebShop 75,9 z GPT-3,5 (zbliża się dostrajanie oparte na gradiencie).

### MCTS, minimalnie

Cztery fazy na iterację:

1. **Wybierz** — przejdź od korzenia do liścia za pomocą UCT (górna granica ufności dla drzew).
2. **Rozwiń** — wygeneruj K dzieci za pomocą polityki.
3. **Symulacja** — wdrożenie od dziecka przy użyciu polityki, oceń liść funkcją wartości (lub nagrodą środowiskową).
4. **Wsteczna propagacja** — aktualizacja liczby odwiedzin i szacunkowych wartości w dalszej ścieżce.

Formuła UCT: `Q(s, a) + c * sqrt(ln N(s) / N(s, a))`. Pierwszym terminem jest wyzysk; drugie to eksploracja. Dostosuj `c` do każdego zadania.

### Rzeczywistość kosztowa

Szukaj eksploduje tokeny. ToT w grze 24 wykorzystuje 100–1000 razy więcej tokenów CoT. LATS jest podobny. To nie jest bezpłatne; rezerwowe wyszukiwanie:

- Zadania, w których pojedyncza trajektoria jest wyraźnie niewystarczająca (Gra w 24, złożony kod).
- Zadania, w których zegar ścienny jest mniej ważny niż poprawność.
- Zadania z tanią, niezawodną funkcją wartości (testy jednostkowe dla kodu, jawny cel dla matematyki).

Jeśli Twoje zadanie ma jedną poprawną odpowiedź i hałaśliwą osobę oceniającą, wyszukiwanie często pogarsza sytuację — znajduje złą odpowiedź o „dobrym wyniku”.

### Pozycjonowanie 2026

Większość agentów produkcyjnych nie obsługuje LATS. Uruchamiają ReAct z weryfikacją opartą na narzędziach (KRYTYK, lekcja 05). Wyszukiwanie pojawia się w wyspecjalizowanych niszach:

- Agenci kodujący, którzy uruchamiają testy jako funkcję wartości (w stylu HumanEval).
- Agenci zajmujący się głębokimi badaniami, którzy badają wiele ścieżek zapytań.
- Przepływy pracy wymagające planowania w podgrafach LangGraph.

AlphaEvolve (lekcja 11) to ekstremum roku 2025: ewolucyjne przeszukiwanie kodu, sprawność sprawdzana maszynowo, nowatorskie osiągnięcia (pierwsze ulepszenie Matmul 4x4 od 56 lat).

## Zbuduj to

`code/main.py` implementuje:

- Mały ToT BFS ze stylizowanym zadaniem „wybierz operacje arytmetyczne”.
- Zabawkowa pętla LATS MCTS dla tego samego zadania (Wybierz / Rozwiń / Symulacja / Propaguj wstecz) z wyborem UCT.
- Funkcja wartości, która składa się z wyniku symbolicznego i wyniku samooceny.

Uruchom to:

```
python3 code/main.py
```

Ślad pokazuje, że ToT rozwija trzech kandydatów na węzeł za pomocą BFS, w porównaniu z LATS zbiegającym się przy najlepszym wdrożeniu za pośrednictwem MCTS. Liczba żetonów wydrukowana dla obu.

## Użyj tego

LangGraph udostępnia eksplorację w stylu ToT jako wzorce podgrafów; Blog zespołu LangChain na temat LATS (maj 2024 r.) jest poradnikiem referencyjnym. LlamaIndex dostarcza agenta `TreeOfThoughts`. W przypadku większości agentów produkcyjnych 2026 ten wzorzec kryje się za bramką `if task_complexity > threshold: use_search()` — zobacz wzorzec modułu oceniającego-optymalizatora w Lekcji 05.

## Wyślij to

`outputs/skill-search-policy.md` wybiera pomiędzy liniowym ReAct, ToT, LATS i wyszukiwaniem ewolucyjnym, biorąc pod uwagę kształt zadania, budżet i wierność oceniającego.

## Ćwiczenia

1. Uruchom zabawkę LATS z UCT c=0,1 vs c=2,0. Jakie zmiany w śladzie?
2. Zamień funkcję wartości na głośniejszą funkcję punktacji (dodaj losowy jitter). Czy MCTS nadal znajduje najlepszy liść? Jaki jest minimalny stosunek sygnału do szumu, jaki toleruje?
3. Zaimplementuj ToT z przeszukiwaniem wiązki (utrzymuj top-k na każdym poziomie) i porównaj z BFS. Co jest lepsze przy napiętym budżecie symbolicznym?
4. Przeczytaj LATS Sekcja 5.1. Odtwórz liczbę trajektorii HumanEval: ile wdrożeń potrzeba, aby osiągnąć zgłoszony wynik@1?
5. Przeczytaj dyskusję w artykule LATS na temat „kiedy LATS pomaga mniej”. Napisz jednoakapitową regułę decyzyjną odwzorowującą kształt zadania na strategię wyszukiwania.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Drzewo Myśli | „Oddział CoT” | Yao i in. — drzewo węzłów myślowych z samooceną |
| ŁATY | „MCTS dla LLM” | Zhou i in. — ujednolica ToT + ReAct + Reflexion w ramach MCTS |
| UCT | „Górna granica ufności” | Wybierz formułę równoważącą eksploatację (Q) i eksplorację (ln N/n) |
| Funkcja wartości | „Jak dobry jest ten stan” | Podpowiadany wynik LLM lub nagroda środowiskowa; zasila podporę |
| Polityka | „Proponujący działanie” | Generator w stylu ReAct; emituje kolejne myśli/działania kandydata |
| Wdrożenie | „Symulowana trajektoria” | Przejdź od węzła do liścia, korzystając z zasad, oceń wartość |
| Propaguj wstecznie | „Aktualizuj przodków” | Przesuń nagrodę liścia w górę ścieżki, aktualizując liczbę odwiedzin i Q |
| Koszt wyszukiwania | „Tokenowa eksplozja” | 100-1000x CoT w grze 24; budżet przed przyjęciem |

## Dalsze czytanie

- [Yao i in., Tree of Thoughts (arXiv:2305.10601)](https://arxiv.org/abs/2305.10601) — artykuł kanoniczny
– [Zhou i in., LATS (arXiv:2310.04406)](https://arxiv.org/abs/2310.04406) — MCTS ze sprzężeniem zwrotnym Reflexion
- [Omówienie LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) — wzorce podgrafów do wyszukiwania
- [AlphaEvolve (arXiv:2506.13131)](https://arxiv.org/abs/2506.13131) — wyszukiwanie ewolucyjne za pomocą ewaluatorów programowych