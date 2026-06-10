# MARL — MADDPG, QMIX, MAPPO

> Dziedzictwo koordynacji wielu agentów polegające na uczeniu się przez wzmacnianie, które w 2026 r. nadal będzie obowiązywać w systemach LLM-agent. **MADDPG** (Lowe et al., NeurIPS 2017, arXiv:1706.02275) wprowadził scentralizowane szkolenie, zdecentralizowane wykonanie (CTDE): każdy krytyk widzi stany i działania wszystkich agentów podczas szkolenia; w czasie testu działają tylko lokalni aktorzy. Działa w środowiskach kooperacyjnych, konkurencyjnych i mieszanych. **QMIX** (Rashid et al., ICML 2018, arXiv:1803.11485) to rozkład wartości za pomocą monotonicznej sieci mieszania; Q na agenta łączą się w wspólne Q, dzięki czemu `argmax` rozprowadzane są w sposób czysty — dominujący w StarCraft Multi-Agent Challenge (SMAC). **MAPPO** (Yu i in., NeurIPS 2022, arXiv:2103.01955) to PPO ze scentralizowaną funkcją wartości; „zaskakująco skuteczny” w świecie cząstek, SMAC, Google Research Football, Hanabi przy minimalnym dostrojeniu. Stanowią one podstawę polityki szkoleniowej dla zespołów agentów, które muszą działać zdecentralizowane. MAPPO to **domyślny poziom bazowy MARL dla spółdzielni na rok 2026**. Ta lekcja opiera się na małej zabawce w świecie siatki i umieszcza trzy pomysły w pamięci mięśniowej przed dotknięciem szkolenia agenta LLM.

**Typ:** Ucz się
**Języki:** Python (stdlib, małe implementacje wolne od NumPy)
**Wymagania wstępne:** Faza 09 (Uczenie się przez wzmacnianie), Faza 16 · 09 (Równoległe sieci roju)
**Czas:** ~90 minut

## Problem

Systemy agentów LLM w coraz większym stopniu szkolą zasady koordynacji między agentami: kiedy odłożyć, kiedy działać, do kogo zadzwonić. Literatura, która mówi, jak szkolić takie polityki, to uczenie się przez wzmocnienie wieloagentowe (MARL), które powstało przed falą LLM i ma niewielki zestaw dominujących algorytmów.

Czytanie artykułów MARL bez słownictwa wzorcowego jest bolesne. Scentralizowane szkolenie ze zdecentralizowaną realizacją (CTDE), rozkładem wartości i scentralizowaną krytyką nie są modnymi hasłami — są to konkretne odpowiedzi na konkretne problemy:

- Niezależny RL (każdy agent uczy się sam) jest niestacjonarny z punktu widzenia każdego agenta. Zły.
- Scentralizowany RL (jeden agent kontroluje wszystko) nie skaluje się i narusza ograniczenia wykonawcze.
- CTDE wykorzystuje to, co najlepsze z obu: szkolenie z informacjami globalnymi, wdrażanie z lokalnymi politykami.

## Koncepcja

### Trzy środowiska, z których korzystają gazety

- **Świat cząstek (wieloagentowe środowisko cząstek).** Prosta fizyka 2D z zadaniami opartymi na współpracy/konkurencyjności. Oryginalne stanowisko testowe MADDPG.
- **StarCraft Multi-Agent Challenge (SMAC).** Kooperacyjne mikrozarządzanie, częściowa obserwacja. Stanowisko testowe QMIX. Działania dyskretne, stany ciągłe.
- **Google Research Football, Hanabi, MPE.** Wartości bazowe MAPPO.

Różne env mają różne typy działań/obserwacji. Algorytmy wybierają odpowiednio.

### MADDPG (2017) — wzór CTDE

Każdy agent `i` ma aktora `mu_i(o_i)`, który odwzorowuje jego własne obserwacje na działanie. Każdy agent ma także krytyka `Q_i(x, a_1, ..., a_n)`, który widzi wszystkie obserwacje i wszystkie działania podczas szkolenia. Aktor jest aktualizowany przez gradient polityki w stosunku do oceny krytyka.

```
actor update:    grad_theta_i J = E[grad_theta mu_i(o_i) * grad_a_i Q_i(x, a_1..n) at a_i=mu_i(o_i)]
critic update:   TD on Q_i(x, a_1..n) given next-state joint estimate
```

Dlaczego CTDE: w czasie szkolenia znamy działania wszystkich; używamy tego, aby zmniejszyć wariancję u każdego krytyka. W czasie wdrażania każdy agent widzi tylko `o_i` i wywołuje `mu_i(o_i)`.

Tryb niepowodzenia: krytycy rosną wraz z N agentami (dane wejściowe obejmują wszystkie działania). Nie skaluje się powyżej ~10 agentów bez przybliżeń.

### QMIX (2018) — dekompozycja wartości

Tylko spółdzielcze. Nagroda globalna to suma monotonicznej funkcji wartości Q na agenta:

```
Q_tot(tau, a) = f(Q_1(tau_1, a_1), ..., Q_n(tau_n, a_n)),   df/dQ_i >= 0
```

Gwarancje monotoniczności `argmax_a Q_tot` mogą zostać obliczone przez każdego agenta wybierającego `argmax_{a_i} Q_i` niezależnie. To jest **dokładnie zdecentralizowana właściwość wykonania**, której potrzebujesz. W czasie szkolenia sieć mieszająca generuje `Q_tot` z Qs poszczególnych agentów.

Dlaczego QMIX wygrywa na SMAC: kooperatywny mikrozarządzanie StarCraft ma jednorodnych agentów, lokalne obserwacje, globalną nagrodę – idealnie pasuje do rozkładu wartości.

Tryb awarii: ograniczenie monotoniczności jest restrykcyjne; niektóre zadania mają strukturę nagród, których nie można rozkładać na monotonię (jeden agent poświęca się dla zespołu). Rozszerzenia (QTRAN, QPLEX) łagodzą to.

### MAPPO (2022) — pomijana opcja domyślna

Multi-Agent PPO: PPO ze scentralizowaną funkcją wartości. Każdy agent ma swoją własną politykę; wszyscy agenci współdzielą (lub mają dla poszczególnych agentów) funkcje wartości, które widzą pełny stan. Yu i in. W roku 2022 porównano MAPPO z MADDPG, QMIX i ich rozszerzeniami w pięciu testach porównawczych i stwierdzono:

- MAPPO dorównuje lub pokonuje niezgodne z zasadami metody MARL w świecie cząstek, SMAC, Google Research Football, Hanabi, MPE.
- Wymagane jest minimalne dostrojenie hiperparametrów.
- Stabilny trening; powtarzalne w nasionach.

Aż do tego artykułu społeczność nie doceniała MARL dotyczącego polityki. W 2026 r. MAPPO będzie domyślnym punktem odniesienia dla spółdzielczego MARL; każda nowa metoda musi ją pokonać.

### Dlaczego inżynierowie agentów LLM powinni się tym przejmować

Trzy bezpośrednie zastosowania:

1. **Szkolenie routera.** Metaagent wybiera, który podagent zajmie się danym zadaniem. Jest to problem MARL z N zdecentralizowanymi agentami podrzędnymi i jednym scentralizowanym routerem. MAPPO pasuje.
2. **Pojawienie się ról.** W symulacjach agentów generatywnych szkolenie agentów, aby z czasem przyjmowali uzupełniające się role, jest ukrytym problemem MARL. Rozkład wartości w stylu QMIX wymusza komplementarność poprzez konstrukcję.
3. **Wykorzystanie narzędzi wieloagentowych.** Kiedy agenci dzielą się narzędziami i rywalizują o budżet, szkolenie ich za pośrednictwem CTDE tworzy możliwe do wdrożenia lokalne zasady, które uwzględniają ograniczenia zasobów.

Praktyczne zastrzeżenie: w 2026 r. większość produkcyjnych systemów agentów LLM będzie podpowiadać swoje zasady, zamiast ich szkolić. MARL pojawia się, gdy masz (a) dużo danych dotyczących interakcji, (b) wyraźny sygnał nagrody oraz (c) chęć inwestowania w infrastrukturę szkoleniową.

### CTDE jako wzorzec projektowy wykraczający poza RL

Nawet bez szkolenia CTDE jest użytecznym wzorem architektonicznym:

- Podczas *projektowania* załóż pełną widoczność zespołu.
- W *runtime* wymuszaj zdecentralizowane wykonanie: każdy agent widzi tylko `o_i`.

Wzorzec zmusza Cię do zachowania jawności stanu poszczególnych agentów i myślenia o częściowej obserwowalności z góry. Wiele produkcyjnych systemów wieloagentowych po cichu przyjmuje wszędzie stan współdzielony — dyscyplina CTDE temu zapobiega.

### Problem niestacjonarności

Gdy wielu agentów uczy się jednocześnie, środowisko każdego agenta (w tym zasady innych) jest niestacjonarne. Klasyczne dowody RL z jednym agentem psują się. Wszystkie algorytmy MARL omówione w tej lekcji rozwiązują ten problem:

- MADDPG: krytyk globalny widzi wszystkie działania, więc jego szacunkowa wartość jest stacjonarna.
- QMIX: rozkład wartości przenosi naukę do wspólnej przestrzeni Q, gdzie optymalność jest dobrze zdefiniowana.
- MAPPO: scentralizowana funkcja wartości tłumi odchylenia wynikające ze zmian polityki innych osób.

W systemach agentów LLM niestacjonarność objawia się tym, że „mój agent pracował w zeszłym miesiącu, teraz, gdy zmienił się inny agent na górze, mój zachowuje się niewłaściwie”. Szkolenie MARL z CTDE to rozwiązanie oparte na zasadach; poprawki na poziomie podpowiedzi są szybsze, ale mniej trwałe.

### Czego NIE omawia ta lekcja

Szkolenie rzeczywistych sieci jest tematem fazy 09. W tej lekcji tworzone są wersje zasad oparte na skryptach, które demonstrują CTDE, rozkład wartości i wzorce wartości scentralizowanych bez aktualizacji gradientów. Celem jest internalizacja wzorców przed wybraniem pełnej biblioteki MARL (PyMARL, MARLlib, wieloagentowy RLlib).

## Zbuduj to

`code/main.py` implementuje trzy demonstracje wzorców, a wszystko to w małym, kooperacyjnym świecie gridowym składającym się z dwóch agentów:

- Środowisko: 2 agentów na siatce 4x4, jedna kulka-nagroda. Nagroda = 1, jeśli jakikolwiek agent dotrze do kulki; zadanie się kończy.
- `IndependentAgents` — każdy agent traktuje innych jak środowisko. Linia bazowa.
- `MADDPGStyle` — scentralizowany krytyk oblicza łączną wartość; Z niego aktualizują się zasady aktora. Skryptowe ulepszenie zasad.
- `QMIXStyle` — rozkład wartości za pomocą miksera monotonicznego.
- `MAPPOStyle` — scentralizowana funkcja wartości; aktualizacja zasad względem udostępnionej linii bazowej.

Wszyscy czterej realizują te same odcinki i zgłaszają średnią liczbę kroków do celu. Warianty CTDE zbiegają się w krótsze ścieżki niż niezależna linia bazowa.

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik: niezależni agenci wykonują średnio ~6 kroków; Warianty CTDE zbiegają się w kierunku ~ 3,5 stopnia (optymalnie dla siatki 4x4 to 3). Różnica we wzorcach pojawia się pomimo zasad opartych na skryptach.

## Użyj tego

`outputs/skill-marl-picker.md` to umiejętność wybierania algorytmu MARL dla danego zadania wieloagentowego: współpraca vs rywalizacja, jednorodność vs heterogeniczność, typ przestrzeni akcji, skala, sygnał nagrody.

## Wyślij to

MARL w produkcji jest rzadkością. Kiedy go użyjesz:

– **Zacznij od MAPPO.** W artykule z 2022 r. ustalono to jako punkt odniesienia; odtworzenie go w pierwszej kolejności oszczędza tygodnie pogoni za bardziej wyrafinowanymi metodami.
- ** Rejestruj obserwacje i strumienie działań każdego agenta. ** Debugowanie MARL bez śladów poszczególnych agentów jest beznadziejne.
- **Oddziel kod szkoleniowy od kodu wykonawczego.** CTDE to dyscyplina; niech ścieżka wykonania naprawdę widzi tylko `o_i`.
- **Ostrzeżenie o kształtowaniu nagrody.** MARL jest wyjątkowo wrażliwy na projektowanie nagród. Jeden błąd koordynacji w kształtowaniu i agenci uczą się go wykorzystywać. Przeprowadź testy kontradyktoryjne.
- **W przypadku agentów LLM** należy najpierw rozważyć zasady na poziomie podpowiedzi. Inwestuj w szkolenie MARL tylko wtedy, gdy dostępne są dane dotyczące interakcji, sygnał nagrody i infrastruktura.

## Ćwiczenia

1. Uruchom `code/main.py`. Zmierz różnicę między krokami do celu między niezależnymi agentami a agentami w stylu MAPPO. Czy odstęp rośnie czy zmniejsza się na siatce 6x6?
2. Wprowadź wariant rywalizacji: dwóch agentów, jedna kulka, nagrodę otrzymuje tylko ten, kto dotrze jako pierwszy. Który wzorzec radzi sobie z konkurencją w sposób czysty? MADDPG historycznie.
3. Przeczytaj MADDPG (arXiv:1706.02275) Sekcja 3. Zaimplementuj dokładną regułę aktualizacji krytyka symbolicznie w pseudokodzie, własnymi słowami.
4. Przeczytaj MAPPO (arXiv:2103.01955). Dlaczego autorzy twierdzą, że scentralizowana wartość + PPO pokonuje niestosowną politykę MARL w swoich benchmarkach? Wymień trzy najsilniejsze twierdzenia.
5. Zastosuj CTDE jako wzorzec projektowy do hipotetycznego systemu agenta LLM (np. agent badawczy + podsumowujący + programista). Jakie wspólne informacje są dostępne w czasie projektowania, a które nie są dostępne w czasie wykonywania?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| MARL | „Wieloagentowy RL” | Uczenie się przez wzmacnianie w systemach wieloagentowych. |
| CTDE | „Scentralizowane szkolenie, zdecentralizowane wykonanie” | Trenuj z informacjami globalnymi; wdrożyć zgodnie z lokalnymi zasadami. |
| MADDPG | „Wieloagentowy DDPG” | CTDE z krytykiem poszczególnych agentów, który widzi wszystkie obserwacje i działania. |
| QMIX | „Rozkład wartości” | Monotoniczne mieszanie Qs na agenta. Spółdzielnia. |
| MAPPO | „Wieloagentowy PPO” | PPO ze scentralizowaną funkcją wartości. Domyślny poziom bazowy na rok 2026. |
| Rozkład wartości | „Suma poszczególnych Q” | Wspólne Q reprezentowane jako monotoniczna funkcja Qs na agenta. |
| Niestacjonarność | „Ruchome cele” | Środowisko każdego agenta zmienia się w miarę uczenia się innych. Podstawowy problem MARL. |
| W ramach zasad / poza zasadami | „Ucz się z bieżącego / powtórki” | PPO jest zgodne z polityką (MAPPO); DDPG i Q-learning są niezgodne z polityką. |
| SMAK | „Wyzwanie wieloagentowe StarCraft” | Punkt odniesienia w zakresie mikrozarządzania spółdzielczego; Ziemia własna QMIX. |

## Dalsze czytanie

- [Lowe i in. — Wieloagentowy aktor-krytyk w mieszanych środowiskach kooperatywno-konkurencyjnych](https://arxiv.org/abs/1706.02275) — MADDPG; NeuroIPS 2017
- [Rashid i in. — QMIX: Monotoniczna faktoryzacja funkcji wartości na potrzeby głębokiego uczenia się przez wieloagentowe wzmocnienie](https://arxiv.org/abs/1803.11485) — QMIX; ICML 2018
- [Yu i in. — Zaskakująca skuteczność PPO w kooperacyjnych grach wieloagentowych] (https://arxiv.org/abs/2103.01955) — MAPPO; NeuroIPS 2022
- [post na blogu BAIR na temat MAPPO](https://bair.berkeley.edu/blog/2021/07/14/mappo/) — czytelne sformułowanie wyniku MAPPO
- [Repozytorium SMAC](https://github.com/oxwhirl/smac) — Wyzwanie wieloagentowe StarCraft