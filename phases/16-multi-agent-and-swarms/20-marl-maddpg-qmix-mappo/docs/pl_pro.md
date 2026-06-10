# MARL – MADDPG, QMIX, MAPPO

> Wypracowane w ramach uczenia ze wzmacnianiem zasady koordynacji systemów wieloagentowych (MARL) stanowią fundament, który w 2026 roku znajduje bezpośrednie zastosowanie w systemach opartych na agentach LLM. Algorytm **MADDPG** (Lowe i in., NeurIPS 2017, arXiv:1706.02275) wprowadził paradygmat scentralizowanego uczenia i zdecentralizowanego działania (Centralized Training with Decentralized Execution – CTDE): w procesie treningu krytyk każdego agenta ma wgląd w stany i akcje wszystkich pozostałych agentów, natomiast podczas testów (lub wdrożenia produkcyjnego) działają wyłącznie lokalni aktorzy. Sprawdza się on w środowiskach kooperacyjnych, rywalizacyjnych oraz mieszanych. **QMIX** (Rashid i in., ICML 2018, arXiv:1803.11485) realizuje dekompozycję wartości (value factorization) przy użyciu monotonicznej sieci miksującej: indywidualne wartości Q poszczególnych agentów są łączone w globalną wartość Q w taki sposób, aby operacja `argmax` mogła być wykonywana w pełni zdecentralizowanie – algorytm ten zdominował testy StarCraft Multi-Agent Challenge (SMAC). **MAPPO** (Yu i in., NeurIPS 2022, arXiv:2103.01955) to z kolei algorytm PPO wyposażony w scentralizowaną funkcję wartości, który okazał się „zaskakująco skuteczny” w środowiskach takich jak Particle World, SMAC, Google Research Football czy Hanabi, wymagając przy tym minimalnego strojenia parametrów. Podejścia te definiują standardy szkolenia zdecentralizowanych zespołów agentów. MAPPO stanowi **domyślny model referencyjny (baseline) dla kooperacyjnego MARL w 2026 roku**. Ta lekcja wprowadza te trzy koncepcje na przykładzie uproszczonego środowiska siatki (gridworld), pozwalając utrwalić te mechanizmy przed przejściem do uczenia agentów opartych na LLM.

**Typ:** Ucz się
**Języki:** Python (stdlib, małe implementacje wolne od NumPy)
**Wymagania wstępne:** Faza 09 (Uczenie się przez wzmacnianie), Faza 16 · 09 (Równoległe sieci roju)
**Czas:** ~90 minut

## Problem

Systemy wieloagentowe oparte na LLM coraz częściej wymagają optymalizacji reguł koordynacji: podejmowania decyzji o tym, kiedy dany agent ma oddać głos innemu, kiedy podjąć działanie, a kiedy odpytać innego agenta. Metodologia szkolenia takich strategii opiera się na wieloagentowym uczeniu ze wzmacnianiem (Multi-Agent Reinforcement Learning – MARL) – dziedzinie, która rozwinęła się przed rewolucją LLM i posiada ugruntowany zbiór wiodących algorytmów.

Analiza literatury naukowej z zakresu MARL bywa trudna bez znajomości podstawowej terminologii. Pojęcia takie jak scentralizowane uczenie ze zdecentralizowanym działaniem (CTDE), dekompozycja wartości (value factorization) czy scentralizowany krytyk (centralized critic) to nie tylko hasła branżowe – to konkretne rozwiązania rzeczywistych wyzwań inżynieryjnych:

- **Niezależne uczenie (Independent RL):** każdy agent uczy się niezależnie, co sprawia, że środowisko z perspektywy pojedynczego agenta staje się niestacjonarne (zmienne w czasie). To nieefektywne podejście.
- **Scentralizowane uczenie (Centralized RL):** jeden agent podejmuje decyzje za wszystkich. Podejście to słabo się skaluje i narusza ograniczenia techniczne rzeczywistych wdrożeń.
- **Architektura CTDE:** łączy zalety obu podejść – proces szkolenia korzysta z wiedzy globalnej, natomiast wdrożone polityki działają w pełni lokalnie i zdecentralizowanie.

## Koncepcja

### Trzy klasyczne środowiska testowe w literaturze MARL

- **Particle World (Multi-Agent Particle Environment - MPE).** Prosta dwuwymiarowa fizyka 2D z zadaniami opartymi na kooperacji i rywalizacji. Klasyczny poligon doświadczalny dla algorytmu MADDPG.
- **StarCraft Multi-Agent Challenge (SMAC).** Kooperacyjne mikrozarządzanie jednostkami w grze strategicznej przy częściowej obserwowalności (partial observability). Główne środowisko ewaluacji dla algorytmu QMIX, charakteryzujące się dyskretną przestrzenią akcji i ciągłą przestrzenią stanów.
- **Google Research Football, Hanabi, MPE.** Główne środowiska benchmarkowe wykorzystywane do ewaluacji algorytmu MAPPO.

Różne środowiska (environments) narzucają odmienne typy akcji oraz obserwacji, co determinuje dobór właściwego algorytmu.

### MADDPG (2017) – Klasyk paradygmatu CTDE

Każdy agent `i` posiada aktora `mu_i(o_i)`, który przekształca jego lokalne obserwacje w konkretne działania. Równolegle, każdy agent dysponuje krytykiem `Q_i(x, a_1, ..., a_n)`, który podczas szkolenia ma wgląd w stan globalny `x` (lub zbiór wszystkich lokalnych obserwacji) oraz akcje podjęte przez wszystkich agentów. Aktualizacja parametrów aktora odbywa się za pomocą gradientu polityki na podstawie ocen krytyka:

```
actor update:    grad_theta_i J = E[grad_theta mu_i(o_i) * grad_a_i Q_i(x, a_1..n) at a_i=mu_i(o_i)]
critic update:   TD on Q_i(x, a_1..n) given next-state joint estimate
```

Dlaczego CTDE działa: w fazie szkolenia dysponujemy kompletem informacji o zachowaniach wszystkich agentów, co pozwala zminimalizować wariancję ocen krytyków. W fazie wdrożeniowej (execution) każdy agent analizuje wyłącznie własne obserwacje `o_i` i na ich podstawie podejmuje decyzje przy użyciu lokalnego aktora `mu_i(o_i)`.

Tryb awarii (failure mode): rozmiar wejścia krytyka rośnie liniowo wraz z liczbą agentów (N), ponieważ musi on przetwarzać akcje wszystkich uczestników. Bez uproszczeń matematycznych algorytm ten staje się niewydajny dla populacji powyżej ~10 agentów.

### QMIX (2018) – Dekompozycja wartości (Value Factorization)

Algorytm dedykowany wyłącznie do zadań kooperacyjnych. Globalna wartość `Q_tot` jest reprezentowana jako monotoniczna funkcja indywidualnych wartości `Q_i` poszczególnych agentów:

```
Q_tot(tau, a) = f(Q_1(tau_1, a_1), ..., Q_n(tau_n, a_n)),   df/dQ_i >= 0
```

Warunek monotoniczności gwarantuje, że globalna operacja wyznaczenia optimum `argmax_a Q_tot` daje taki sam rezultat jak niezależne, lokalne wyznaczenie `argmax_{a_i} Q_i` przez każdego agenta z osobna. Zapewnia to **w pełni zdecentralizowane działanie systemu**. W fazie szkolenia sieć miksująca (mixing network) łączy indywidualne wartości `Q_i` w globalne `Q_tot`.

Dlaczego QMIX dominuje w SMAC: kooperacyjne zadania mikrozarządzania w StarCraft opierają się na populacjach homogenicznych agentów, lokalnych obserwacjach i wspólnej, globalnej nagrodzie, co idealnie odpowiada założeniom dekompozycji wartości.

Tryb awarii: założenie monotoniczności bywa zbyt restrykcyjne. Istnieją zadania o strukturze nagród, której nie da się rozłożyć z zachowaniem monotoniczności (np. sytuacje, gdy jeden z agentów musi poświęcić swój wynik dla dobra całego zespołu). Rozwiązaniem tego problemu są nowsze rozszerzenia, takie jak QTRAN czy QPLEX.

### MAPPO (2022) – Nowy standard referencyjny

Algorytm MAPPO (Multi-Agent PPO) to wariant PPO wyposażony w scentralizowaną funkcję wartości. Każdy agent uczy się własnej polityki działania, natomiast funkcja wartości (która może być współdzielona lub dedykowana dla każdego agenta) ma wgląd w pełny stan globalny systemu. W pracy z 2022 roku Yu i in. zestawili MAPPO z algorytmami MADDPG, QMIX oraz ich rozszerzeniami, dochodząc do następujących wniosków:

- MAPPO osiąga wyniki równe lub lepsze od algorytmów typu off-policy MARL w środowiskach Particle World, SMAC, Google Research Football czy Hanabi.
- Wymaga minimalnego nakładu pracy przy dostrajaniu hiperparametrów.
- Charakteryzuje się wysoką stabilnością szkolenia i powtarzalnością wyników przy różnych ziarnach losowości (seeds).

Przed publikacją tej pracy społeczność naukowa sceptycznie oceniała potencjał algorytmów on-policy w obszarze MARL. Obecnie MAPPO stanowi domyślny punkt odniesienia dla kooperacyjnych systemów wieloagentowych – każdy nowy algorytm w tym obszarze musi udowodnić swoją wyższość nad MAPPO.

### Znaczenie dla inżynierów systemów agentowych opartych na LLM

MARL znajduje zastosowanie w trzech kluczowych obszarach:

1. **Szkolenie routerów.** Projektowanie zachowań meta-agentów decydujących o przydziale zadań do podrzędnych agentów. Jest to klasyczny problem uczenia wieloagentowego z N zdecentralizowanymi wykonawcami i jednym scentralizowanym dyspozytorem – idealne zastosowanie dla MAPPO.
2. **Emergencja ról.** W symulacjach opartych na agentach generatywnych szkolenie agentów w celu wypracowania uzupełniających się profili działania jest ukrytym problemem MARL. Dekompozycja wartości w stylu QMIX z założenia wymusza komplementarność zachowań.
3. **Współdzielenie zasobów i narzędzi.** Gdy agenci konkurują o wspólne API lub budżet tokenów, zastosowanie podejścia CTDE pozwala na wypracowanie lokalnych reguł decyzyjnych uwzględniających ograniczenia systemowe.

Warto jednak pamiętać, że w 2026 roku większość produkcyjnych wdrożeń agentów opiera się na promptowaniu ich strategii działania. Złożone szkolenie MARL wdraża się w sytuacjach, kiedy dysponujemy dużą ilością danych interakcyjnych, stabilnym środowiskiem ewaluacji i odpowiednią infrastrukturą.

### CTDE jako uniwersalny wzorzec projektowy

Koncepcję CTDE można z powodzeniem stosować jako wzorzec architektury oprogramowania poza samym uczeniem ze wzmacnianiem:

- W fazie **projektowania i monitorowania** systemu zakładamy pełny, globalny wgląd w stan całego zespołu agentów.
- W fazie **uruchomieniowej (runtime)** rygorystycznie wymuszamy zdecentralizowane wykonanie: każdy agent podejmuje decyzje wyłącznie w oparciu o swój lokalny kontekst `o_i`.

Wzorzec ten ułatwia projektowanie czystych architektur z wyraźnie zarysowanymi granicami stanów i zmusza do uwzględnienia zjawiska częściowej obserwowalności. Wiele systemów wieloagentowych wdrożonych produkcyjnie niejawnie współdzieli cały stan między agentami – dyscyplina CTDE skutecznie zapobiega powstawaniu takich antywzorców.

### Problem niestacjonarności

Równoległe uczenie się wielu agentów powoduje, że środowisko z perspektywy pojedynczego uczestnika staje się niestacjonarne (ponieważ strategie innych agentów stale ewoluują). Wyklucza to stosowanie klasycznych algorytmów RL dedykowanych dla pojedynczych agentów. Wszystkie algorytmy MARL omawiane w tej lekcji adresują ten problem:

- MADDPG: globalny krytyk analizuje akcje wszystkich agentów, co stabilizuje szacunki wartości.
- QMIX: dekompozycja wartości mapuje proces uczenia do wspólnej przestrzeni Q, w której optymalność jest jednoznacznie zdefiniowana.
- MAPPO: scentralizowana funkcja wartości niweluje zaburzenia wynikające ze zmian zachowań innych uczestników.

W systemach opartych na LLM problem niestacjonarności często objawia się sytuacjami typu: „mój agent działał poprawnie w zeszłym miesiącu, ale po aktualizacji promptów u innego agenta w systemie, jego zachowanie uległo pogorszeniu”. Zastosowanie podejścia MARL z CTDE pozwala rozwiązać ten problem strukturalnie. Wprowadzanie poprawek bezpośrednio w promptach jest szybsze, lecz mniej stabilne w długiej perspektywie.

### Zakres lekcji

Szkolenie rzeczywistych sieci neuronowych jest przedmiotem lekcji w Fazie 09. W tej lekcji skupimy się na implementacji uproszczonych, skryptowych strategii działania, które demonstrują zasady CTDE, dekompozycji wartości oraz scentralizowanej ewaluacji bez konieczności prowadzenia treningu gradientowego. Naszym celem jest zrozumienie architektury tych rozwiązań przed przejściem do dedykowanych bibliotek MARL (takich jak PyMARL, MARLlib czy RLlib).

## Zbuduj to

Skrypt `code/main.py` implementuje demonstrację trzech wzorców w uproszczonym, kooperacyjnym środowisku gridworld dla dwóch agentów:

- Środowisko: siatka o wymiarach 4x4 z dwoma agentami i jednym celem (nagrodą). Nagroda wynosi 1, gdy którykolwiek z agentów dotrze do celu, co kończy dany epizod.
- `IndependentAgents` – wariant bazowy (baseline), w którym każdy agent traktuje pozostałych uczestników jako część pasywnego środowiska.
- `MADDPGStyle` – wariant ze scentralizowanym krytykiem wyliczającym łączną wartość, na podstawie której aktualizowana jest skryptowa strategia aktora.
- `QMIXStyle` – wariant z dekompozycją wartości realizowaną przez monotoniczną sieć miksującą.
- `MAPPOStyle` – wariant ze scentralizowaną funkcją wartości i optymalizacją strategii względem współdzielonej linii bazowej (baseline).

Wszystkie cztery warianty realizują te same epizody testowe i raportują średnią liczbę kroków potrzebnych do osiągnięcia celu. Warianty oparte na CTDE uzyskują krótsze ścieżki dojścia niż podejście niezależne.

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik: niezależni agenci potrzebują średnio ~6 kroków do celu, natomiast warianty oparte na CTDE zbiegają się do poziomu ~3,5 kroku (optymalny wynik na siatce 4x4 wynosi 3). Zalety architektury CTDE są wyraźnie widoczne nawet przy zastosowaniu reguł skryptowych.

## Użyj tego

Plik `outputs/skill-marl-picker.md` definiuje umiejętność ułatwiającą dobór odpowiedniego algorytmu MARL do specyfiki zadania (kooperacja vs rywalizacja, populacje homogeniczne vs heterogeniczne, typ przestrzeni akcji, skala oraz charakterystyka sygnału nagrody).

## Wdrożenie produkcyjne

Metody MARL są rzadko stosowane bezpośrednio w systemach produkcyjnych. Decydując się na ich wdrożenie, pamiętaj o poniższych zasadach:

- **Zacznij od MAPPO.** Badania z 2022 roku potwierdzają, że jest to najlepszy punkt wyjścia. Zbudowanie wariantu referencyjnego w oparciu o MAPPO oszczędzi czas, który mógłby zostać zmarnowany na próby wdrożenia bardziej skomplikowanych algorytmów.
- **Loguj szczegółowo obserwacje i akcje poszczególnych agentów.** Próby debugowania systemów MARL bez dostępu do logów jednostkowych są z góry skazane na niepowodzenie.
- **Rygorystycznie oddzielaj kod szkoleniowy od produkcyjnego (runtime).** Architektura CTDE to dyscyplina projektowa: upewnij się, że w trybie wykonania agent ma dostęp wyłącznie do lokalnego kontekstu `o_i`.
- **Ostrożnie projektuj funkcję nagrody (reward shaping).** Systemy MARL są niezwykle wrażliwe na zmiany w strukturze nagród. Błędy w projektowaniu zachęt mogą prowadzić do tego, że agenci nauczą się wykorzystywać luki w systemie zamiast realizować cel główny. Zawsze przeprowadzaj testy warunków skrajnych.
- **W przypadku agentów LLM** w pierwszej kolejności stosuj reguły oparte na promptowaniu. Decyzję o przejściu na trening MARL podejmij tylko wtedy, gdy dysponujesz bogatym zbiorem danych interakcyjnych, stabilnym środowiskiem ewaluacji i odpowiednią infrastrukturą.

## Ćwiczenia

1. Uruchom `code/main.py`. Zmierz różnicę in liczbie kroków potrzebnych do osiągnięcia celu między wariantem niezależnym a wariantem MAPPO. Czy wraz ze zwiększeniem wymiarów siatki do 6x6 różnica ta rośnie, czy maleje?
2. Zaimplementuj wariant rywalizacyjny (adversarial): dwóch agentów, jeden cel, nagrodę otrzymuje wyłącznie agent, który dotrze do niego jako pierwszy. Który z wzorców najlepiej radzi sobie z obsługą rywalizacji? (Historycznie jest to MADDPG).
3. Przeczytaj rozdział 3 w pracy MADDPG (arXiv:1706.02275). Zapisz symboliczną regułę aktualizacji krytyka w pseudokodzie własnymi słowami.
4. Przeczytaj publikację MAPPO (arXiv:2103.01955). Jakie argumenty przedstawiają autorzy na poparcie tezy, że scentralizowana funkcja wartości połączona z on-policy PPO przewyższa metody off-policy MARL w testach porównawczych? Wymień trzy kluczowe twierdzenia.
5. Zaprojektuj architekturę CTDE dla hipotetycznego systemu opartego na agentach LLM (np. agent badawczy + podsumowujący + programista). Jakie informacje o stanie systemu powinny być dostępne podczas projektowania i monitorowania (uczenia), a jakie muszą być ukryte przed poszczególnymi agentami w czasie wykonywania zapytań (runtime)?

## Kluczowe terminy

| Termin | Co się potocznie mówi | Co to właściwie oznacza |
|---|---|---|
| MARL (Multi-Agent Reinforcement Learning) | „Wieloagentowy RL” | Uczenie ze wzmacnianiem w środowiskach z wieloma współdziałającymi lub rywalizującymi agentami. |
| CTDE (Centralized Training with Decentralized Execution) | „Scentralizowane uczenie, zdecentralizowane działanie” | Paradygmat projektowania, w którym model uczy się z dostępem do wiedzy globalnej, ale w runtime podejmuje decyzje wyłącznie lokalnie. |
| MADDPG | „Wieloagentowy DDPG” | Algorytm CTDE oparty na DDPG, w którym krytyk każdego agenta analizuje obserwacje i akcje całej populacji. |
| QMIX | „Dekompozycja wartości / faktoryzacja” | Algorytm kooperacyjny łączący indywidualne wartości Q agentów za pomocą monotonicznej sieci miksującej. |
| MAPPO | „Wieloagentowe PPO” | Wariant algorytmu PPO wykorzystujący scentralizowaną funkcję wartości. Standard referencyjny w 2026 r. |
| Dekompozycja wartości (Value Factorization) | „Łączenie wartości Q” | Reprezentowanie globalnej wartości użytkowej Q jako monotonicznej funkcji wartości indywidualnych poszczególnych agentów. |
| Niestacjonarność (Non-stationarity) | „Ruchomy cel” | Ciągła zmiana dynamiki środowiska z perspektywy pojedynczego agenta wynikająca z jednoczesnego uczenia się pozostałych uczestników. |
| On-policy / Off-policy | „Uczenie na żywo vs z pamięci podręcznej” | Algorytmy on-policy uczą się na podstawie bieżących interakcji (np. PPO/MAPPO); off-policy korzystają z bufora powtórek (np. DDPG, Q-learning). |
| SMAC (StarCraft Multi-Agent Challenge) | „Benchmark StarCrafta” | Popularne środowisko testowe dla kooperacyjnych algorytmów MARL, będące domeną algorytmu QMIX. |

## Dalsze czytanie

- [Lowe i in. – Multi-Agent Actor-Critic for Mixed Cooperative-Competitive Environments](https://arxiv.org/abs/1706.02275) – oryginalna publikacja prezentująca algorytm MADDPG (NeurIPS 2017)
- [Rashid i in. – QMIX: Monotonic Value Function Factorisation for Deep Multi-Agent Reinforcement Learning](https://arxiv.org/abs/1803.11485) – praca wprowadzająca dekompozycję wartości QMIX (ICML 2018)
- [Yu i in. – The Surprising Effectiveness of PPO in Cooperative Multi-Agent Games](https://arxiv.org/abs/2103.01955) – badania nad skutecznością algorytmu MAPPO (NeurIPS 2022)
- [Wpis na blogu BAIR dotyczący MAPPO](https://bair.berkeley.edu/blog/2021/07/14/mappo/) – przystępne omówienie założeń i wyników algorytmu MAPPO
- [Repozytorium kodu SMAC](https://github.com/oxwhirl/smac) – kod źródłowy środowiska StarCraft Multi-Agent Challenge
