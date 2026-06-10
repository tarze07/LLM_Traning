# Teoria umysłu i wyłaniająca się koordynacja

> Li i in. (arXiv:2310.10701) wykazało, że agenci LLM w kooperacyjnej grze tekstowej wykazują **wyłaniającą się teorię umysłu wyższego rzędu** (ToM) — rozumowanie na temat tego, co inny agent sądzi na temat przekonań trzeciego agenta — ale nie udaje im się planować długoterminowo ze względu na zarządzanie kontekstem i halucynacje. Riedl (arXiv:2510.05174) zmierzył synergię wyższego rzędu w populacji i odkrył, że **tylko** warunek podpowiedzi ToM powoduje zróżnicowanie powiązane z tożsamością i komplementarność ukierunkowaną na cel; LLM o mniejszej wydajności wykazują jedynie pozorne pojawienie się. Oznacza to, że pojawienie się koordynacji jest warunkowe i zależne od modelu, a nie wolne. Ta lekcja implementuje minimalnego agenta obsługującego ToM, uruchamia wspólne zadanie z monitem ToM i bez niego oraz mierzy deltę koordynacji względem protokołu Riedl 2025.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 07 (Społeczeństwo umysłu i debaty), Faza 16 · 17 (Agenci generatywni)
**Czas:** ~75 minut

## Problem

Koordynacja wielu agentów często wygląda magicznie: agenci dzielą pracę, antycypują się nawzajem i unikają redundancji. Zazwyczaj to „pojawienie się” jest wytworem szybkiej inżynierii — ktoś kazał agentom „koordynować działania”. Usuń zachętę, usuń koordynację.

Ustalenia Riedla z 2025 r. są bardziej rygorystyczne: w kontrolowanych warunkach koordynacja pojawia się tylko wtedy, gdy agenci zostaną poproszeni o rozważenie **umysłów innych agentów** (ToM). Bez podpowiedzi ToM nawet silne modele wykazują wzorce koordynacji, które nie przetrwają kontroli statystycznej. Ma to znaczenie dla produkcji: zespoły dostarczają funkcje „koordynacji wieloagentowej”, które są zależne od szybkości i kruche.

Ta lekcja traktuje ToM jako specyficzną zdolność (wnioskowanie na temat przekonań na temat przekonań), buduje agenta minimalnie świadomego ToM i mierzy, jak wygląda rzeczywista koordynacja w porównaniu z tym, jak wygląda szybkie ubieranie się.

## Koncepcja

### Co oznacza ToM

Psychologia rozwojowa: 3-latek uważa, że wewnętrzny świat każdej osoby jest taki sam jak jego. Pięciolatek rozumie, że inni mają odmienne przekonania. 7-latka uzasadnia przekonania na temat przekonań („ona myśli, że ja myślę, że piłka jest pod kubkiem”). Są to ToM zerowego, pierwszego i drugiego rzędu.

W przypadku agentów LLM zamówienia ToM są mapowane na:

- **Porządek zerowy:** brak innych modeli. Agent działa wyłącznie na podstawie własnych obserwacji.
- **Pierwszy rząd:** agent ma model przekonań drugiego agenta. „Alicja wierzy X”.
- **Drugiego rzędu:** agent modeluje przekonania rekurencyjne. „Alicja wierzy, że Bob wierzy X”.

Li i in. W roku 2023 stwierdzono, że ToM pierwszego i drugiego rzędu pojawiają się u agentów LLM w grach kooperacyjnych, ale ulegają degradacji w miarę długiego horyzontu czasowego i zawodnej komunikacji.

### Test Sally-Anne, w skrócie

Test fałszywego przekonania z 1985 r.: Sally wkłada kulkę do koszyka A i wychodzi. Ania przenosi go do koszyka B. Gdzie Sally będzie patrzeć, kiedy wróci? Dziecko z ToM pierwszego rzędu mówi „kosz A” (przekonanie Sally różni się od rzeczywistości). Dziecko bez mówi koszyka B.

LLM z ery GPT-4 przechodzą testy w stylu Sally-Anne, gdy są postawione wyraźnie. Zawodzą, gdy narracja jest długa, scena zmienia się kilka razy lub pytanie jest sformułowane pośrednio. Taki jest praktyczny stan ToM w produkcyjnych LLM na rok 2026.

### Pomiar koordynacji Riedla

Riedl (arXiv:2510.05174) zbudował test na skalę populacyjną: N agentów, cel współpracy, zmienne warunki natychmiastowe. Zmierz:

1. **Zróżnicowanie powiązane z tożsamością.** Czy agenci z biegiem czasu rozwijają trwałe rozróżnienie ról?
2. **Komplementarność ukierunkowana na cel.** Czy działania agentów uzupełniają się (różne podzadania), a nie dublują się?
3. **Synergia wyższego rzędu.** Statystyczna miara tego, czy grupa osiąga to, czego nie byłby w stanie żaden podzbiór.

Wynik: tylko w przypadku warunku zachęty ToM wszystkie trzy metryki dają sygnał powyżej linii bazowej. Bez monitu ToM metryki oscylują wokół szansy w przypadku modeli o umiarkowanej wydajności. Duże modele wykazują pewną koordynację bez wyraźnego podpowiedzi ToM, ale efekt jest mniejszy niż w przypadku wyraźnego podpowiedzi.

### Iluzja koordynacji

Bez kontroli statystycznej „wyłaniająca się koordynacja” w demonstracjach często odzwierciedla:

- Szybka inżynieria, która działa w koordynacji (podpowiedzi systemowe z informacją „współpracuj”).
- Stronniczość obserwatora (widzimy wzorce, których się spodziewamy).
- Wybór post-hoc udanych przebiegów.

Systemy produkcyjne promujące „emergentną koordynację” bez mierzalnego sygnału należy traktować jako marketing. Zmierz przed złożeniem reklamacji.

### Minimalny agent obsługujący ToM

Struktura:

```
agent state:
  own_beliefs:    {facts the agent believes}
  other_models:   {other_agent_id -> {beliefs_the_agent_attributes_to_them}}
  actions_last_N: [history of others' actions]

observation update:
  - update own_beliefs from direct observation
  - update other_models[agent_id] from their action + prior beliefs

action selection:
  - enumerate candidate actions
  - for each, predict what each other agent will do next given their modeled beliefs
  - pick action that maximizes joint outcome under those predictions
```

Atrybut `other_models` określa stan ToM. ToM pierwszego rzędu utrzymuje tylko jeden poziom. Drugiego rzędu dodaje `other_models[i][other_models_of_j]` — to, w co według mnie agent i wierzy agent j.

### Dlaczego długa perspektywa boli

Li i in. dokument: ograniczenia kontekstu powodują, że agenci zapominają, które przekonanie należy do kogo. Halucynacje dodają fałszywe przekonania do modeli innych agentów. Obydwa powodują błędy „Myślałem, że pomyślał X”, które z czasem się nasilają.

Działania łagodzące udokumentowane w artykule oraz działania następcze w latach 2024-2026:

- **Jawny stan ToM w wierszu zachęty.** Format strukturalny: `{agent_id: belief_list}`. Wymusza wyszukiwanie w celu zachowania powiązania tożsamości z przekonaniami.
- **Krótsze łańcuchy rozumowania.** Mniej aktualizacji ToM na turę zmniejsza złożone halucynacje.
- **Zewnętrzny magazyn ToM.** Utrzymuj model poza kontekstem LLM; wstrzykiwać tylko odpowiednie części na obrót.

### Gdzie ToM zawodzi w produkcji

- **Ustawienia kontradyktoryjności.** Agentami z dobrym ToM łatwiej jest manipulować (możesz modelować to, co o tobie myślą, a następnie wykorzystywać).
- **Zespoły heterogeniczne.** Kiedy modele są różne, model ToM, który sprawdza się w przypadku jednego przeciwnika, nie powoduje uogólnień.
- **Zadania zależne od prawdy.** ToM dotyczy przekonań; jeśli poprawność zależy od faktów, ToM może odwracać uwagę.

### Koordynację, którą możesz zmierzyć

Trzy praktyczne sygnały, że koordynacja zespołu jest rzeczywista, a nie natychmiastowa:

1. **Komplementarność w czasie.** Czy w przypadku zadania wieloturowego działania agentów obejmują rozłączne podzadania?
2. **Przewidywanie.** Czy akcja agenta A w turze T+1 zależy od przewidywania dotyczącego akcji B w turze T+2, które okazało się prawidłowe?
3. **Poprawka.** Kiedy A błędnie odczytuje przekonania B w turze T, czy A poprawia w turze T+2?

Można je zmierzyć w logowanym systemie wieloagentowym. Stanowią one merytoryczną wersję narracji o „koordynacji”.

## Zbuduj to

`code/main.py` implementuje:

- `ToMAgent` — śledzi własne przekonania i modele przekonań poszczególnych agentów.
- Zadanie kooperacyjne: trzech agentów musi zebrać trzy żetony z trzech pudełek; w każdym pudełku może znajdować się jeden żeton. Agenci nie mogą się komunikować; wnioskują o zamiarach na podstawie wzajemnych działań.
- Dwie konfiguracje: `zeroth_order` (bez ToM) i `first_order` (ToM z jednopoziomowym modelem przekonań).
- Pomiar w ponad 200 randomizowanych badaniach: współczynnik ukończenia, współczynnik powielania (dwóch agentów celuje w to samo pole), średnia liczba obrotów do zakończenia.

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik: agenci zerowego rzędu dublują wysiłek w tempie ~35% i wykonują ~60% prób w 10 turach. Agenci ToM pierwszego rzędu duplikują się w ~5% i kończą w ~95%. Delta to mierzalny efekt koordynacji.

## Użyj tego

`outputs/skill-tom-auditor.md` to umiejętność, która sprawdza, czy system wieloagentowy zapewnia „wschodzącą koordynację”. Sprawdza szybkie ubieranie, istotność statystyczną w porównaniu z kontrolą i zmierzoną komplementarność.

## Wyślij to

Lista kontrolna roszczeń koordynacyjnych:

- **Warunek sterowania.** Wersja Twojego systemu bez podpowiedzi koordynacji. Zmierz oba.
- **Test statystyczny.** Czy różnica między systemem a kontrolą jest znacząca na poziomie `p < 0.05` według Twojego wskaźnika?
- **Miara komplementarności.** Rozbieżność działań w czasie, a nie tylko końcowy sukces.
- **Dziennik przypadków awarii.** Jak wygląda stan ToM, gdy agenci błędnie koordynują działania?
- **Ujawnienie pojemności modelu.** Jeśli efekt zniknie w mniejszych modelach, powiedz to.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że ToM pierwszego rzędu zmniejsza współczynnik powielania o ~7x. Czy różnica utrzymuje się po skalowaniu do 5 agentów i 5 skrzynek?
2. Wdrażaj ToM drugiego rzędu (agent A modeluje to, co B myśli o C). Czy poprawia się w stosunku do pierwszego rzędu? Na jakich zadaniach?
3. Wprowadź **halucynację** do stanu ToM: losowo odwróć jedno przekonanie na turę. Jak bardzo pogarsza to wydajność pierwszego rzędu?
4. Przeczytaj Li i in. (arXiv:2310.10701). Odtwórz wynik „degradacji w długim horyzoncie”: w miarę wzrostu liczby tur z 10 do 30, jak zmienia się wydajność ToM pierwszego rzędu?
5. Przeczytaj Riedl 2025 (arXiv:2510.05174). Zaimplementuj statystykę synergii wyższego rzędu w dziennikach symulacji. Czy efekt występuje bez warunku zachęty ToM?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Teoria umysłu | „Zrozumienie umysłów innych” | Zdolność do modelowania przekonań innego agenta. Oceniane według kolejności (0, 1, 2+). |
| Test Sally-Anne | „Test fałszywego przekonania” | 1985 psychologia rozwojowa; LLM przekazują proste wersje, zawodzą złożone. |
| ToM pierwszego rzędu | „A wierzy X” | Modelowanie wzajemnych przekonań na temat faktów. |
| ToM drugiego rzędu | „A wierzy, że B wierzy X” | Modelowanie rekurencyjne o jeden poziom głębiej. |
| Zróżnicowanie powiązane z tożsamością | „Role stabilne w czasie” | Metryka Riedla: role utrzymują się, a nie są przypadkowe. |
| Komplementarność ukierunkowana na cel | „Działania rozłączne” | Agenci celują w różne podzadania, a nie w to samo. |
| Synergia wyższego rzędu | „Grupa przekracza dowolny podzbiór” | Miara statystyczna Riedla dla rzeczywistej koordynacji. |
| Iluzja koordynacji | „Wygląda na skoordynowane” | Natychmiastowy wygląd koordynacji bez mierzalnego sygnału. |

## Dalsze czytanie

- [Li i in. — Teoria umysłu dla współpracy wielu agentów za pośrednictwem modeli wielkojęzykowych](https://arxiv.org/abs/2310.10701) — wyłaniające się ToM w grach kooperacyjnych; tryby awarii o długim horyzoncie
- [Riedl — Emergent Cooperative in Multi-Agent Language Models](https://arxiv.org/abs/2510.05174) — pomiar w skali populacji; Podpowiadanie ToM jest stanem nośnym
– [Premack i Woodruff – Czy szympans ma teorię umysłu?](https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/does-the-chimpanzee-have-a-theory-of-mind/1E96B02CD9850E69AF20F81FA7EB3595) – Pochodzenie koncepcji ToM w 1978 roku
- [Baron-Cohen, Leslie, Frith — Czy dziecko autystyczne ma teorię umysłu?] (https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/does-the-autistic-child-have-a-theory-of-mind/) – artykuł Sally-Anne (1985)