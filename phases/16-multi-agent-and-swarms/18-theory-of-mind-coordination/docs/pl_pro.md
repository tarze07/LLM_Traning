# Teoria umysłu i emergentna koordynacja

> Li i in. (arXiv:2310.10701) wykazali, że agenci oparci na modelach LLM w kooperacyjnej grze tekstowej przejawiają **emergentną Teorię Umysłu (Theory of Mind – ToM) wyższego rzędu** – potrafią wnioskować o tym, co dany agent sądzi na temat przekonań innego agenta. Jednak z powodu trudności z zarządzaniem kontekstem i halucynacjami mają problem z planowaniem długoterminowym. Riedl (arXiv:2510.05174) zbadał synergię wyższego rzędu w populacji agentów i odkrył, że **wyłącznie** wyraźne skłonienie agentów do ToM (poprzez odpowiedni prompt) prowadzi do trwałego zróżnicowania ról powiązanego z tożsamością oraz do komplementarności działań ukierunkowanych na cel. Słabsze modele LLM wykazują jedynie pozorne zachowania emergentne. Oznacza to, że zjawisko emergentnej koordynacji nie pojawia się samoistnie – jest warunkowe i zależy od klasy modelu. W tej lekcji zaimplementujesz prostego agenta obsługującego ToM, uruchomisz zadanie kooperacyjne z promptem ToM oraz bez niego, a następnie zmierzysz różnicę (deltę) w poziomie koordynacji według metodologii Riedla (2025).

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 07 (Społeczeństwo umysłu i debaty), Faza 16 · 17 (Agenci generatywni)
**Czas:** ~75 minut

## Problem

Koordynacja działań in systemach wieloagentowych często wydaje się niezwykle płynna: agenci dzielą się zadaniami, przewidują nawzajem swoje kroki i unikają powielania pracy. Zazwyczaj jednak ta „emergencja” jest po prostu efektem inżynierii promptów – poinstruowania agentów słowami: „koordynujcie swoje działania”. Wystarczy usunąć to polecenie, by cała koordynacja legła w gruzach.

Badania Riedla z 2025 roku dostarczają bardziej rygorystycznych wniosków: w kontrolowanych warunkach rzeczywista koordynacja pojawia się tylko wtedy, gdy agenci zostaną jawnie skłonieni do **analizowania stanów umysłu innych uczestników** (ToM). Bez promptów ToM nawet zaawansowane modele wykazują schematy koordynacji, które nie wytrzymują weryfikacji statystycznej. Ma to kluczowe znaczenie dla wdrożeń produkcyjnych: wiele oferowanych funkcji „koordynacji wieloagentowej” to w rzeczywistości rozwiązania niestabilne i podatne na drobne zmiany w promptach.

W tej lekcji potraktujemy ToM jako konkretną umiejętność (wnioskowanie o przekonaniach na temat przekonań), zbudujemy prostego agenta świadomego ToM i zmierzymy rzeczywisty poziom koordynacji w zestawieniu z efektami powierzchownego promptowania.

## Koncepcja

### Poziomy Teorii Umysłu (ToM)

Psychologia rozwojowa definiuje następujące etapy rozwoju tej zdolności: 3-letnie dziecko uważa, że wewnętrzny świat innych ludzi jest tożsamy z jego własnym. 5-latek rozumie już, że inni mogą mieć odmienne przekonania. Z kolei 7-letnie dziecko potrafi wnioskować o przekonaniach dotyczących przekonań („ona myśli, że ja myślę, iż piłka jest pod kubkiem”). Odpowiada to Teorii Umysłu zerowego, pierwszego i drugiego rzędu.

W kontekście agentów LLM poziomy te mapują się następująco:

- **Rząd zerowy (0-ToM):** brak modelowania innych. Agent działa wyłącznie na podstawie własnych obserwacji.
- **Pierwszy rząd (1-ToM):** agent modeluje przekonania drugiego agenta. „Alicja wierzy, że X jest prawdą”.
- **Drugi rząd (2-ToM):** agent modeluje przekonania rekurencyjne. „Alicja myśli, że Bob wierzy, że X jest prawdą”.

Li i in. (2023) wykazali, że wnioskowanie ToM pierwszego i drugiego rzędu pojawia się u agentów LLM w grach kooperacyjnych, jednak ulega degradacji przy długich horyzontach czasowych oraz w przypadku zakłóceń w komunikacji.

### Test Sally-Anne

Klasyczny test fałszywego przekonania (1985): Sally wkłada kulkę do koszyka A i wychodzi z pokoju. Wtedy Anne przekłada kulkę do koszyka B. Gdzie Sally będzie szukać kulki po powrocie? Dziecko posiadające ToM pierwszego rzędu odpowie, że w koszyku A (rozumie, że przekonanie Sally różni się od stanu faktycznego). Dziecko bez ToM wskazuje koszyk B.

Modele LLM klasy GPT-4 bez problemu zaliczają test Sally-Anne, gdy problem jest przedstawiony wprost. Jednak zaczynają się gubić, gdy historia jest długa, scena wielokrotnie ulega zmianie lub gdy pytanie jest zadane w sposób niebezpośredni. Taki jest faktyczny stan rozwoju ToM w modelach LLM dostępnych produkcyjnie w 2026 roku.

### Wskaźniki koordynacji według Riedla

Riedl (arXiv:2510.05174) zaprojektował testy populacyjne: N agentów realizuje wspólny cel przy zmiennych warunkach promptowania. Mierzy się w nich:

1. **Zróżnicowanie powiązane z tożsamością (identity-linked differentiation).** Czy agenci wypracowują z czasem stabilny i trwały podział ról?
2. **Komplementarność działań (goal-directed complementarity).** Czy zachowania agentów uzupełniają się (realizują różne podzadania), zamiast się duplikować?
3. **Synergię wyższego rzędu (higher-order synergy).** Statystyczny wskaźnik tego, czy cała grupa osiąga rezultat, którego nie zdołałby osiągnąć żaden z jej podzespołów osobno.

Wnioski: tylko w warunku z jawnym promptowaniem ToM wszystkie trzy metryki dają wyniki wyraźnie wyższe niż linia bazowa. Bez promptów ToM, w przypadku średniej klasy modeli, wyniki oscylują na poziomie losowym. Bardzo duże modele wykazują pewien stopień koordynacji nawet bez bezpośredniego promptowania ToM, ale efekt ten jest znacznie słabszy.

### Iluzja koordynacji

Brak rygorystycznej kontroli statystycznej sprawia, że rzekoma „emergentna koordynacja” w prezentacjach demo jest zazwyczaj złudzeniem wynikającym z:

- Inżynierii promptów wymuszającej współpracę (np. prompt systemowy nakazujący: „pracujcie zespołowo”).
- Błędu konfirmacji (dostrzegamy tylko te wzorce zachowań, które chcemy zobaczyć).
- Selektywnego wybierania udanych przebiegów symulacji (cherry-picking).

Systemy produkcyjne, których twórcy deklarują obecność „emergentnej koordynacji” bez przedstawienia mierzalnych dowodów, należy traktować z dystansem. Zanim sformułujesz takie wnioski, przeprowadź rzetelne pomiary.

### Minimalna architektura agenta ToM

Struktura stanu:

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

Atrybut `other_models` odpowiada za realizację ToM. ToM pierwszego rzędu (1-ToM) operuje na jednym poziomie głębokości. Drugi rząd (2-ToM) dodaje zagnieżdżenie `other_models[i][other_models_of_j]`, reprezentujące to, co agent A sądzi na temat przekonań agenta B o przekonaniach agenta C.

### Tryby awarii przy długim horyzoncie czasowym

Li i in. udokumentowali następujące problemy: ograniczenia długości kontekstu sprawiają, że agenci gubią przypisanie poszczególnych przekonań do konkretnych osób. Z kolei halucynacje wprowadzają błędne założenia do modeli myślowych pozostałych agentów. Oba zjawiska prowadzą do rozbieżności typu „sądziłem, że on myśli, iż X”, które nawarstwiają się w czasie.

Metody radzenia sobie z tymi problemami (na podstawie badań z lat 2024–2026):

- **Jawny stan ToM w promptach.** Zastosowanie ustrukturyzowanego formatu: `{agent_id: belief_list}`. Wymusza to precyzyjne powiązanie tożsamości agenta z przypisywanymi mu przekonaniami podczas wyszukiwania.
- **Krótsze łańcuchy wnioskowania.** Zredukowanie liczby aktualizacji ToM w jednej turze ogranicza nawarstwianie się halucynacji.
- **Zewnętrzny magazyn stanów ToM.** Przechowywanie modelu poza oknem kontekstowym LLM i wstrzykiwanie do promptu wyłącznie danych kluczowych dla bieżącej tury.

### Gdzie ToM zawodzi w środowisku produkcyjnym

- **Środowiska rywalizacji (adversarial settings).** Agentami o wysokiej zdolności ToM łatwiej manipulować – przeciwnik może modelować ich przewidywania i celowo wprowadzać ich w błąd.
- **Zespoły heterogeniczne.** Jeśli agenci korzystają z różnych modeli bazowych, wnioskowanie ToM dopasowane do jednego z nich może nie działać w interakcji z innymi.
- **Zadania czysto faktograficzne.** ToM służy do modelowania subiektywnych przekonań. W zadaniach, gdzie liczy się obiektywna prawda o faktach, dodatkowe warstwy modelowania intencji mogą niepotrzebnie rozpraszać model.

### Mierzalne wskaźniki rzeczywistej koordynacji

Oto trzy konkretne sygnały potwierdzające, że koordynacja zespołu jest realnym zjawiskiem, a nie jedynie kwestią promptowania:

1. **Komplementarność działań w czasie.** Czy w zadaniach wieloetapowych agenci podejmują działania, które pokrywają niezależne, niepokrywające się podzadania?
2. **Antycypacja (przewidywanie).** Czy działanie agenta A w kroku T+1 zależy od trafnej prognozy działania agenta B w kroku T+2?
3. **Autokorekta.** Jeśli agent A w turze T błędnie oceni przekonania agenta B, czy potrafi skorygować ten błąd w turze T+2?

Metryki te można łatwo wyliczyć na podstawie logów systemu wieloagentowego. Dają one obiektywny obraz koordynacji w miejsce ogólnych zapewnień.

## Zbuduj to

Skrypt `code/main.py` implementuje:

- `ToMAgent` – klasę agenta śledzącego własne przekonania oraz modelującego stany wiedzy pozostałych uczestników.
- Zadanie kooperacyjne: trzech agentów musi zebrać trzy żetony ukryte w trzech różnych pudełkach (w każdym pudełku znajduje się maksymalnie jeden żeton). Agenci nie mogą się bezpośrednio komunikować; wnioskują o intencjach innych na podstawie obserwowanych działań.
- Dwie konfiguracje: `zeroth_order` (bez ToM) oraz `first_order` (z ToM pierwszego rzędu).
- Ewaluację na dystansie ponad 200 losowych prób: mierzone są wskaźnik ukończenia zadania, wskaźnik duplikacji (dwóch agentów wybiera to samo pudełko) oraz średnia liczba tur potrzebna do zakończenia.

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik: agenci poziomu zerowego (0-ToM) powielają działania w około 35% przypadków i kończą sukcesem jedynie ~60% prób w ciągu 10 tur. Agenci pierwszego rzędu (1-ToM) duplikują wysiłki tylko w ~5% przypadków i osiągają wskaźnik sukcesu na poziomie ~95%. Różnica ta stanowi mierzalny dowód na skuteczność koordynacji.

## Użyj tego

Plik `outputs/skill-tom-auditor.md` definiuje umiejętność audytu systemów pod kątem deklaracji o rzekomej „emergentnej koordynacji”. Pomaga ona zidentyfikować powierzchowne promptowanie, zweryfikować istotność statystyczną wyników w grupie kontrolnej oraz zmierzyć poziom komplementarności działań.

## Wdrożenie produkcyjne

Lista kontrolna przy zgłaszaniu sprawności koordynacyjnej systemu:

- **Grupa kontrolna (control condition).** Przygotuj wersję systemu pozbawioną promptów koordynacyjnych i porównaj wyniki obu wariantów.
- **Testy statystyczne.** Upewnij się, czy różnica w wynikach między wariantem testowym a kontrolnym jest istotna statystycznie (zalecany próg `p < 0.05`).
- **Pomiar komplementarności.** Badaj stopień dywersyfikacji działań agentów w czasie, a nie wyłącznie końcowy wskaźnik sukcesu.
- **Rejestrowanie błędów (failure trace).** Loguj stan przekonań ToM w sytuacjach, kiedy koordynacja między agentami kończy się niepowodzeniem.
- **Zależność od klasy modelu.** Otwarcie informuj, jeśli pozytywne efekty koordynacji zanikają przy przejściu na mniejsze modele LLM.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że ToM pierwszego rzędu redukuje współczynnik duplikacji około 7-krotnie. Czy ta zależność utrzyma się po wyskalowaniu symulacji do 5 agentów i 5 pudełek?
2. Zaimplementuj ToM drugiego rzędu (agent A modeluje to, co agent B sądzi na temat przekonań agenta C). Czy przynosi to poprawę w stosunku do modelu pierwszego rzędu? W jakiego typu zadaniach?
3. Wprowadź sztuczne **halucynacje** do reprezentacji ToM: raz na turę losowo zmień jedno z przypisanych przekonań na przeciwne. Jak mocno wpłynie to na skuteczność agentów pierwszego rzędu?
4. Przeczytaj pracę Li i in. (arXiv:2310.10701). Odtwórz zjawisko „degradacji przy długim horyzoncie czasowym” – jak zmienia się skuteczność ToM pierwszego rzędu przy wydłużeniu liczby tur z 10 do 30?
5. Przeczytaj publikację Riedla z 2025 roku (arXiv:2510.05174). Zaimplementuj obliczanie synergii wyższego rzędu na podstawie logów symulacji. Czy efekt synergii jest mierzalny w próbie bez promptowania ToM?

## Kluczowe terminy

| Termin | Co się potocznie mówi | Co to właściwie oznacza |
|---|---|---|
| Teoria Umysłu (Theory of Mind - ToM) | „Rozumienie intencji innych” | Zdolność do modelowania stanów wiedzy i przekonań innych agentów. Klasyfikowana według poziomu zagnieżdżenia (0, 1, 2+). |
| Test Sally-Anne | „Test fałszywego przekonania” | Klasyczne badanie z psychologii rozwojowej (1985). Modele LLM radzą sobie z jego prostymi wersjami, ale zawodzą przy bardziej złożonych scenariuszach. |
| ToM pierwszego rzędu (1-ToM) | „A myśli, że X” | Modelowanie bezpośrednich przekonań innego agenta o faktach. |
| ToM drugiego rzędu (2-ToM) | „A myśli, że B sądzi, że X” | Rekurencyjne modelowanie stanów wiedzy o poziom głębiej. |
| Zróżnicowanie powiązane z tożsamością | „Stabilny podział ról” | Metryka Riedla sprawdzająca, czy role agentów są trwałe w czasie, a nie przydzielane losowo w każdym kroku. |
| Komplementarność działań | „Niepokrywające się zadania” | Sytuacja, w której agenci realizują uzupełniające się cele zamiast powielać te same kroki. |
| Synergia wyższego rzędu | „Grupa osiąga więcej niż suma części” | Opracowany przez Riedla statystyczny wskaźnik rzeczywistego zgrania zespołu. |
| Iluzja koordynacji | „Wygląda na to, że ze sobą współpracują” | Powierzchowna płynność działania systemu bez statystycznego potwierdzenia w wynikach. |

## Dalsze czytanie

- [Li i in. – Theory of Mind for Multi-Agent Collaboration via Large Language Models](https://arxiv.org/abs/2310.10701) – analiza emergentnego ToM w grach kooperacyjnych oraz trybów błędów w długich horyzontach czasowych
- [Riedl – Emergent Cooperation in Multi-Agent Language Models](https://arxiv.org/abs/2510.05174) – badania populacyjne wykazujące kluczową rolę promptowania ToM w koordynacji
- [Premack i Woodruff – Does the chimpanzee have a theory of mind?](https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/does-the-chimpanzee-have-a-theory-of-mind/1E96B02CD9850E69AF20F81FA7EB3595) – przełomowa praca z 1978 roku wprowadzająca pojęcie Teorii Umysłu
- [Baron-Cohen, Leslie, Frith – Does the autistic child have a theory of mind?](https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/does-the-autistic-child-have-a-theory-of-mind/1E96B02CD9850E69AF20F81FA7EB3595) – oryginalna publikacja prezentująca test Sally-Anne (1985)
