# Optymalizacja rojowa dla LLM (PSO, ACO)

> Algorytmy optymalizacji inspirowane naturą wracają do łask w erze modeli LLM. Metoda **LMPSO** (arXiv:2504.09247) adaptuje algorytm PSO (Particle Swarm Optimization), w którym prędkość cząstki jest reprezentowana przez prompt, a model LLM generuje kolejnego kandydata. Rozwiązanie to sprawdza się przy generowaniu danych o strukturze sekwencyjnej (np. wyrażenia matematyczne czy programy komputerowe). Projekt **Model Swarms** (arXiv:2410.11163) traktuje poszczególne wyspecjalizowane modele LLM jako cząstki w algorytmie PSO poruszające się w przestrzeni wag modelu, co pozwoliło uzyskać **średni wzrost skuteczności o 13,3%** w odniesieniu do 12 modeli referencyjnych na 9 zbiorach danych, przy użyciu zaledwie 200 przykładów uczących. **SwarmPrompt** (ICAART 2025) łączy PSO z algorytmem szarego wilka (Grey Wolf Optimizer) do automatycznej optymalizacji promptów. **AMRO-S** (arXiv:2603.12933) to z kolei system wieloagentowego routingu zapytań LLM inspirowany algorytmem mrówkowym (ACO). Wykorzystuje on mechanizm śladów feromonowych, zapewniając **4,7-krotne przyspieszenie działania**, w pełni interpretowalne reguły routingu oraz asynchroniczne aktualizacje kontrolowane jakościowo, co oddziela etap wnioskowania od uczenia się. W tej lekcji zaimplementujesz algorytm PSO w przestrzeni parametrów promptów oraz algorytm ACO do routingu agentów, a także przeanalizujesz, kiedy te klasyczne podejścia sprawdzają się w pracy z LLM, a kiedy zawodzą.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 09 (Równelegle sieci roju), Faza 16 · 14 (Konsensus i BFT)
**Czas:** ~75 minut

## Problem

Dysponujesz promptem, który w testach ewaluacyjnych osiąga skuteczność na poziomie 62%. Chcesz poprawić ten wynik. Ręczne wprowadzanie poprawek metodą prób i błędów (bez gradientów) jest naiwnym podejściem, które słabo się skaluje. Z kolei uczenie ze wzmacnianiem (RL) wymaga wyraźnych sygnałów nagrody oraz dużej liczby iteracji w celu przeprowadzenia treningu. Bezpośrednia optymalizacja promptów za pomocą spadku gradientu nie jest możliwa – prompt to dyskretny ciąg znaków, a nie różniczkowalny parametr.

Klasyczne algorytmy inspirowane naturą – PSO (optymalizacja rojem cząstek) dla ciągłych przestrzeni poszukiwań oraz ACO (optymalizacja mrówkowa) dla wyboru ścieżki – zostały zaprojektowane właśnie z myślą o takich problemach: nie wymagają one obliczania gradientów, bazują na populacji rozwiązań i są tanie w obliczeniach ewaluacyjnych. Połączenie ich z modelami LLM w celu wykonywania bezgradientowych kroków przeszukiwania daje w efekcie niezwykle praktyczne narzędzie optymalizacyjne.

Te same zasady dotyczą routingu (kierowania zapytań) w systemach wieloagentowych. Ślady feromonowe w stylu ACO pozwalają zapisać informację o tym, który agent najlepiej poradził sobie z konkretnym typem zadania, ułatwiając routerowi podejmowanie decyzji o wyborze optymalnej ścieżki i dostosowywanie poziomu feromonów w czasie, co umożliwia ciągłe odkrywanie nowych, lepszych tras.

## Koncepcja

### Przypomnienie algorytmu PSO (Kennedy i Eberhart, 1995)

Optymalizacja rojem cząstek (Particle Swarm Optimization) polega na symulowaniu populacji cząstek poruszających się w ciągłej przestrzeni poszukiwań. Każda cząstka charakteryzuje się położeniem `x_i` oraz prędkością `v_i`. W każdej iteracji następuje aktualizacja parametrów według wzorów:

```
v_i <- w * v_i + c1 * r1 * (p_best_i - x_i) + c2 * r2 * (g_best - x_i)
x_i <- x_i + v_i
evaluate fitness(x_i)
update p_best_i if improved
update g_best if global best
```

Gdzie `p_best_i` to najlepsza pozycja znaleziona dotychczas przez daną cząstkę, `g_best` to najlepsza pozycja znaleziona przez cały rój, `w` to współczynnik bezwładności (inertia weight), `c1` i `c2` to odpowiednio wagi dążenia poznawczego (cognitive) i społecznego (social), a `r1` i `r2` to losowe wartości z przedziału [0, 1].

### Algorytm PSO w optymalizacji wyjść LLM – LMPSO

Praca arXiv:2504.09247 adaptuje algorytm PSO do ustrukturyzowanych danych generowanych przez LLM (takich jak wyrażenia matematyczne czy kod programów). Każda cząstka reprezentuje wygenerowaną treść. Prędkość jest wyrażona w formie promptu opisującego, jak zmodyfikować aktualne wyjście w kierunku najlepszej pozycji własnej lub globalnej. Model LLM generuje nową propozycję na podstawie promptu reprezentującego prędkość. „Bezwładność” (inertia) prędkości jest realizowana przez instrukcję typu „dokonaj niewielkich, stopniowych zmian”.

Takie podejście sprawdza się, gdy:
- Wygenerowane dane posiadają wyraźną strukturę (można je łatwo sparsować i poddać ewaluacji).
- Ocena przystosowania (fitness) odbywa się w pełni automatycznie (np. testy jednostkowe, obliczenia matematyczne).
- Populacja jest niewielka (~10-30 cząstek), co pozwala utrzymać liczbę zapytań do LLM na rozsądnym poziomie.

Rozwiązanie to nie sprawdza się, gdy ocena przystosowania wymaga udziału człowieka – koszt i czas trwania pojedynczej iteracji stają się wtedy zbyt wysokie.

### Model Swarms (Roje modeli)

Praca arXiv:2410.11163 przenosi mechanizm PSO z poziomu wygenerowanego tekstu bezpośrednio na poziom *parametrów modelu*. Każda „cząstka” to wyspecjalizowany model LLM (jego parametry). Rój przesuwa wagi modeli w kierunku najlepszego rozwiązania za pomocą bezgradientowych aktualizacji. Autorzy raportują średni wzrost skuteczności o 13,3% w porównaniu z 12 modelami referencyjnymi na 9 zbiorach danych, przy użyciu zelenie 200 przykładów na iterację.

Kluczową obserwacją jest to, że wyspecjalizowane modele LLM współdzielą tę samą przestrzeń parametrów (np. wagi adapterów LoRA). Uruchomienie PSO w tej niskowymiarowej podprzestrzeni okazuje się niezwykle tanie i efektywne.

### Przypomnienie algorytmu ACO (Dorigo, 1992)

Optymalizacja mrówkowa (Ant Colony Optimization): sztuczne mrówki poruszają się po grafie poszukiwań, w którym każda krawędź jest oznaczona śladem feromonowym. Prawdopodobieństwo wyboru danej ścieżki zależy od intensywności feromonów. Mrówki, które pomyślnie rozwiążą zadanie, pozostawiają na swojej trasie dodatkowy feromon proporcjonalnie do jakości rozwiązania. Feromony stopniowo ulatniają się (parują) w czasie.

### AMRO-S – Algorytm mrówkowy (ACO) w routingu agentów

Praca arXiv:2603.12933 wykorzystuje algorytm ACO do zarządzania routingiem w systemach wieloagentowych. Każdy typ zadania reprezentuje „cel podróży”, a poszczególni agenci stanowią potencjalne ścieżki. Ślad feromonowy wzmacnia połączenia, które przyniosły wysokie wskaźniki jakościowe. Kluczowe zalety rozwiązania to:

- **Interpretowalność reguł routingu.** Poziom stężenia feromonów jest łatwym do odczytania sygnałem dla programisty.
- **Asynchroniczne aktualizacje sterowane bramką jakości.** Wartości feromonów są modyfikowane dopiero po pomyślnym zaliczeniu testu kontroli jakości, co oddziela proces wykonywania zapytań (wnioskowanie) od uczenia się systemu.
- **4,7-krotne przyspieszenie działania** w testach porównawczych systemów wieloagentowych.

Bramka jakości (quality gate) jest tu kluczowa: bez niej szybcy, ale zwracający błędne odpowiedzi agenci szybko akumulowaliby feromony, co blokowałoby system na suboptymalnych ścieżkach.

### Kiedy stosować algorytmy PSO i ACO w projektach z LLM

**Zastosuj PSO, gdy:**
- Przestrzeń poszukiwań jest ciągła lub da się ją zmapować na parametry ciągłe (np. osadzanie promptów/prompt embeddings, wagi LoRA, parametry generowania danych).
- Funkcja przystosowania (fitness function) jest tania obliczeniowo i w pełni zautomatyzowana.
- Wystarczy niewielka populacja cząstek (od 10 do 30).

**Zastosuj ACO, gdy:**
- Rozwiązujesz problem routingu zapytań lub wyboru optymalnej ścieżki przepływu zadań.
- Występuje powtarzalność decyzji w czasie (te same typy zadań pojawiają się regularnie).
- Wymagana jest pełna interpretowalność i możliwość inspekcji decyzji dotyczących routingu.

**Unikaj tych metod, gdy:**
- Ewaluacja przystosowania wymaga udziału człowieka (zbyt wysoki koszt na iterację).
- Przestrzeń poszukiwań ma charakter dyskretny i kombinatoryczny, którego nie da się łatwo odwzorować w PSO (w takich przypadkach lepiej sprawdzają się algorytmy genetyczne).
- Wnioskowanie w czasie rzeczywistym wymaga minimalnych opóźnień (zbieżność PSO/ACO wymaga czasu w porównaniu do heurystyk jednoprzebiegowych).

### Dlaczego podejście inspirowane naturą wciąż wygrywa

Klasyczne metody gradientowe wymagają ciągłego i różniczkowalnego sygnału. Wyniki generowane przez LLM oraz decyzje o routingu nie są łatwo różnicowalne. Metody oparte na pseudogradientach (np. routery trenowane przez uczenie ze wzmacnianiem czy optymalizacja promptów za pomocą DPO) działają, ale wiążą się z kosztownym procesem szkolenia.

PSO i ACO wymagają jedynie prostej funkcji oceniającej (fitness function). Jeśli potrafisz liczbowo ocenić jakość wygenerowanego tekstu lub poprawność skierowania zadania, możesz skutecznie przeszukiwać i optymalizować tę przestrzeń. Dzięki temu bariera wdrożenia takich rozwiązań jest znacznie niższa.

### Praktyczne ograniczenia i wyzwania

- **Budżet obliczeniowy populacji.** Koszt rośnie liniowo: `N cząstek * T iteracji * koszt ewaluacji`. Przy cenie zapytania LLM na poziomie ~$0,02, uruchomienie PSO z 20 cząstkami na przestrzeni 50 iteracji będzie kosztować ~$20. Należy zaplanować budżet z wyprzedzeniem.
- **Balans między eksploracją a eksploatacją.** Szybkość parowania feromonów w ACO oraz wagi bezwładności w PSO mają kluczowe znaczenie. Zbyt szybkie parowanie feromonów sprawia, że system gubi dobre ścieżki; zbyt wolne – blokuje się w lokalnych optimach.
- **Katastrofalny dryf (catastrophic drift).** Oba algorytmy mogą osiągnąć stan zbieżności, a następnie zacząć się rozchodzić, jeśli ulegnie zmianie profil zadań (przesunięcie dystrybucji danych). Należy stale monitorować stabilność najlepszego wyniku (g_best).

## Zbuduj to

Skrypt `code/main.py` implementuje:

- `LMPSO` – algorytm PSO optymalizujący parametry numeryczne generowania (np. temperaturę oraz wagę parametru top_k). Działanie LLM dla każdej cząstki jest symulowane przez oskryptowaną funkcję przystosowania. Algorytm jest uruchamiany na 30 iteracji, pokazując proces zbieżności do globalnego optimum (`g_best`).
- `AMRO_S` – mechanizm routingu zapytań oparty na ACO. System zawiera 3 agentów, obsługuje 4 typy zadań, przechowuje macierz feromonów i przetwarza 100 zapytań. Logi prezentują rozkład wyborów agentów w czasie (`typ_zadania -> wybór agenta`), obrazując powstawanie stabilnych ścieżek.
- Ewaluację porównawczą: zestawienie losowego routingu z routingiem ACO na tym samym strumieniu zadań. Mierzone są jakość odpowiedzi oraz opóźnienie.

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik:
- LMPSO: wartość `g_best` rośnie od poziomu losowego do bliskiego optymalnemu w ciągu 30 iteracji.
- AMRO-S: macierz feromonów stabilizuje optymalne powiązania agentów z typami zadań. Routing ACO przewyższa routing losowy o 30-40% pod względem jakości, jednocześnie skracając czas odpowiedzi (dzięki redukcji liczby ponownych prób).

## Użyj tego

Plik `outputs/skill-swarm-optimizer.md` ułatwia wybór pomiędzy algorytmami PSO, ACO, genetycznymi oraz metodami opartymi na gradientach w kontekście optymalizacji modeli LLM i systemów agentowych.

## Wdrożenie produkcyjne

- **Zacznij od małej skali.** Użyj populacji 10–20 cząstek na przestrzeni 20–50 iteracji. Zwiększaj te wartości dopiero wtedy, gdy krzywa zbieżności wykazuje wyraźny trend wzrostowy.
- **Loguj stan feromonów oraz g_best w każdej iteracji.** Debugowanie algorytmów rojowych bez pełnej historii stanów jest niezwykle trudne.
- **Stosuj bramki jakości (quality gates).** W przypadku routingu ACO kluczowe jest zablokowanie możliwości odkładania feromonów przez agentów, którzy zwracają szybkie, lecz niepoprawne odpowiedzi.
- **Dostosuj współczynnik parowania przy zmianach dystrybucji zapytań.** Gdy zmienia się charakter zapytań wejściowych, dotychczasowe poziomy feromonów tracą aktualność. Wtedy należy tymczasowo zresetować macierz lub przyspieszyć proces parowania.
- **Monitoruj koszty.** Loguj i kontroluj koszty każdej iteracji. Algorytm optymalizacji promptów, którego uruchomienie kosztuje 500 USD i daje jedynie 0,5% poprawy, nie kwalifikuje się do wdrożenia produkcyjnego.

## Ćwiczenia

1. Uruchom `code/main.py`. Zwróć uwagę na przebieg zbieżności LMPSO. Przetestuj rozmiary populacji: 5, 10, 20 oraz 50 cząstek. Przy jakiej wielkości populacji czas potrzebny do osiągnięcia zbieżności przestaje się poprawiać?
2. Przeprowadź test „katastrofalnego dryfu”: po 30. iteracji zmień kryteria funkcji przystosowania. Jak szybko algorytm PSO dostosuje się do nowej sytuacji? Czy wyczyszczenie historii `p_best` przyspiesza adaptację?
3. Wprowadź bramkę jakości do `AMRO_S`: pozwól na odkładanie feromonów tylko tym przebiegom, które uzyskały ocenę powyżej 0,7. Jak wpłynie to na szybkość i stabilność zbieżności w porównaniu do wersji bazowej?
4. Przeczytaj publikację LMPSO (arXiv:2504.09247). Zastanów się, jak opisana koncepcja „prędkości wyrażonej jako tekst promptu” odnosi się do tradycyjnej prędkości numerycznej. Co tracimy, a co zyskujemy w takiej symulacji?
5. Przeczytaj publikację AMRO-S (arXiv:2603.12933). Zaimplementuj asynchroniczną aktualizację feromonów działającą w tle, wydzieloną z głównego wątku wnioskowania. Jak ta zmiana wpływa na opóźnienia systemu pod stałym obciążeniem zapytań?

## Kluczowe terminy

| Termin | Co się potocznie mówi | Co to właściwie oznacza |
|---|---|---|
| PSO (Particle Swarm Optimization) | „Optymalizacja rojem cząstek” | Opracowany przez Kennedy'ego i Eberharta w 1995 r. algorytm bezgradientowej optymalizacji bazujący na populacji cząstek. |
| ACO (Ant Colony Optimization) | „Optymalizacja mrówkowa” | Opracowana przez Dorigo w 1992 r. metaheurystyka wyszukiwania optymalnych ścieżek z użyciem śladów feromonowych. |
| LMPSO | „PSO z generowaniem przez LLM” | Koncepcja z pracy arXiv:2504.09247, w której prędkość jest opisana słownie, a model LLM proponuje kolejne rozwiązania. |
| Model Swarms | „Rój modeli / PSO na wagach” | Metoda z pracy arXiv:2410.11163 umożliwiająca bezgradientową optymalizację parametrów w podprzestrzeni wag modeli LLM. |
| AMRO-S | „ACO w routingu zapytań” | Opisany w arXiv:2603.12933 system routingu oparty na macierzy feromonów wiążącej typy zadań z agentami. |
| p_best / g_best | „Najlepszy wynik własny / globalny” | Zapisane optymalne stany osiągnięte odpowiednio przez pojedynczą cząstkę (`p_best`) oraz całą populację (`g_best`). |
| Feromony (Pheromones) | „Pamięć routingu” | Wartości przypisane do krawędzi w grafie routingu; ulegają stopniowemu parowaniu, a ich poziom jest zwiększany za dobre decyzje. |
| Aktualizacja sterowana jakością | „Nagradzanie tylko poprawnych przebiegów” | Zasada dopuszczania do aktualizacji feromonów wyłącznie po pomyślnym przejściu weryfikacji jakościowej. |
| Katastrofalny dryf (Catastrophic Drift) | „Przesunięcie rozkładu danych” | Zmiana środowiska ewaluacji powodująca, że dotychczas wypracowane optimum globalne oraz poziomy feromonów stają się nieaktualne. |

## Dalsze czytanie

- [Kennedy i Eberhart – Particle Swarm Optimization](https://ieeexplore.ieee.org/document/488968) – oryginalna publikacja naukowa z 1995 r. opisająca algorytm PSO
- [Dorigo – Ant Colony Optimization](https://www.aco-metaheuristic.org/about.html) – fundamenty teoretyczne metaheurystyki mrówkowej z 1992 r.
- [LMPSO – Language Model Particle Swarm Optimization](https://arxiv.org/abs/2504.09247) – zastosowanie PSO do optymalizacji ustrukturyzowanych wyjść modeli językowych
- [Model Swarms – Gradient-Free Fine-Tuning of Language Models](https://arxiv.org/abs/2410.11163) – bezgradientowa optymalizacja modeli w przestrzeni wag LoRA
- [AMRO-S – Ant Colony Multi-Agent Routing with Quality Gates](https://arxiv.org/abs/2603.12933) – routing zapytań bazujący na feromonach z automatyczną bramką kontrolną
