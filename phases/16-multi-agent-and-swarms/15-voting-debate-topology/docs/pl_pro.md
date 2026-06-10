# Głosowanie, samospójność (Self-Consistency) i topologia debaty

> Najprostsza i najtańsza metoda agregacji polega na wygenerowaniu N niezależnych odpowiedzi i przeprowadzeniu zwykłego głosowania większościowego. Podejście to, znane jako samospójność (Self-Consistency), zostało opisane przez Wanga i współpracowników w 2022 roku (polega na N-krotnym odpytaniu jednego modelu przy temperaturze > 0). W systemach wieloagentowych koncepcję tę rozszerza się o **heterogeniczne agenty**, aby przełamać monokulturę — stosuje się różne modele bazowe, zróżnicowane prompty, temperatury oraz odmienne konteksty. Poza samym procesem głosowania kluczowe znaczenie ma topologia debaty. W pracy MultiAgentBench (arXiv:2503.01935, ACL 2025) przeanalizowano różne topologie (gwiazda, łańcuch, drzewo, graf) i wykazano, że **topologia pełnego grafu (Graph) sprawdza się najlepiej w zadaniach badawczych**, chociaż generuje tzw. „podatek koordynacyjny” (coordination tax) przy zespole liczącym około 4 agentów. Z kolei praca AgentVerse (ICLR 2024) dokumentuje dwa emergentne wzorce zachowań w debatach wieloagentowych: wolontariat (volunteer behavior) oraz konformizm (conforming behavior). Konformizm ułatwia wypracowanie konsensusu, lecz niesie za sobą ryzyko myślenia grupowego (groupthink, Lekcja 24). W tej lekcji przeanalizujemy dostępne topologie, zaimplementujemy każdą z nich i zmierzymy narzut koordynacyjny.

**Typ:** Ucz się + Buduj
**Języki:** Python (biblioteka standardowa)
**Wymagania wstępne:** Faza 16 · 07 (Społeczeństwo umysłu i debaty), Faza 16 · 14 (Konsensus i BFT)
**Czas:** ~75 minut

## Problem

Debata wieloagentowa potrafi znacząco podnieść dokładność systemu (Du et al., arXiv:2305.14325). Może ją jednak również obniżyć. O tym, czy debata przyniesie korzyści, decydują cztery kluczowe czynniki strukturalne:

1. Schemat komunikacji (topologia).
2. Liczba rund debaty (zgodnie z pracą Du 2023: liczba rund oraz liczba agentów mają niezależny wpływ na wynik).
3. Heterogeniczność zespołu (zastosowanie różnych modeli bazowych eliminuje problem monokultury).
4. Obecność oponenta stosującego merytoryczne wzmacnianie argumentów (steelmanning) lub zniekształcenia (strawmanning).

Naiwne projekty oparte na zasadzie „uruchommy 5 agentów i zliczmy głosy” często osiągają gorsze wyniki niż pojedynczy agent. Niepowodzenia te nie son dziełem przypadku — wynikają bezpośrednio z błędnego doboru topologii i braku zróżnicowania modeli. Ta lekcja ma na celu usystematyzowanie wiedzy na temat topologii.

## Koncepcja

### Samospójność (Self-Consistency) — punkt odniesienia dla pojedynczego modelu

Wang et al. (2022, „Self-Consistency Improves Chain of Thought in Language Models”) polega na wielokrotnym (N-krotnym) odpytywaniu tego samego modelu przy temperaturze $> 0$ i wyłonieniu ostatecznej odpowiedzi drogą głosowania większościowego nad wygenerowanymi ścieżkami wnioskowania (Chain of Thought). W teście GSM8K metoda ta przy $N=40$ próbach przyniosła drastyczną poprawę w porównaniu do dekodowania zachłannego (greedy decoding). Samospójność stanowi fundament, na którym bazuje głosowanie wieloagentowe.

Ograniczenie: samospójność opiera się na jednym modelu bazowym. W rezultacie błędy są z założenia skorelowane — jeśli model posiada określone obciążenie systematyczne (bias), wystąpi ono we wszystkich N próbkach.

### Głosowanie wieloagentowe — podejście heterogeniczne

Polega na zastąpieniu N próbek tego samego modelu przez N *zróżnicowanych* agentów. Stosuje się różne modele bazowe (np. Claude, GPT, Llama), odmienne instrukcje (prompty) oraz zróżnicowane uprawnienia do narzędzi. Zaleta: eliminacja skorelowanych błędów. Koszt: zróżnicowane koszty API poszczególnych modeli oraz narzut wydajnościowy (opóźnienia) związany z ich koordynacją.

W literaturze akademickiej debata zróżnicowanych modeli bywa określana skrótem **A-HMAD** (Adversarial Heterogeneous Multi-Agent Debate). Definiuje on schemat debaty opartej na oponentach korzystających z różnych modeli bazowych, co minimalizuje ryzyko błędów systematycznych (monokultury).

### Cztery główne topologie

```
gwiazda (star)       łańcuch (chain)     drzewo (tree)       graf (graph)

    ┌─A─┐           A─B─C─D         ┌──A──┐              A───B
    │   │                           │     │              │ × │
    B   C                           B     C              D───C
    │   │                          / \   / \
    D   E                         D   E F   G         (pełne połączenie)
```

**Gwiazda (Star):** jeden centralny koordynator, pozostałe agenty komunikują się wyłącznie z nim. Odpowiednik schematu Supervisor-Worker bez bezpośredniej wymiany zdań między wykonawcami.

**Łańcuch (Chain):** komunikacja sekwencyjna (rurociąg), gdzie każdy kolejny agent analizuje wynik wygenerowany przez swojego poprzednika.

**Drzewo (Tree):** hierarchiczna struktura komunikacji, stosowana w złożonych systemach hierarchicznych (Lekcja 06).

**Graf (Graph):** komunikacja każdy z każdym. Może przyjąć postać pełnego grafu (kliki) lub dowolnego skierowanego grafu acyklicznego (DAG).

### Narzut koordynacyjny (MultiAgentBench)

W ramach projektu MultiAgentBench (MARBLE, ACL 2025, arXiv:2503.01935) przeprowadzono testy porównawcze topologii gwiazdy, łańcucha, drzewa i grafu w zadaniach badawczych, programistycznych i planistycznych. Kluczowe wnioski z pomiarów:

- Topologia **Graph** wykazuje najwyższą skuteczność w zadaniach badawczych (research). Umożliwia swobodną wymianę informacji między wszystkimi uczestnikami i wzajemną konstruktywną krytykę.
- Topologia **Star** (gwiazda) sprawdza się najlepiej w zadaniach opartych na faktach (fact-retrieval) i szybkich zapytaniach. Centralny węzeł skutecznie filtruje i konsoliduje informacje.
- Topologia **Chain** (łańcuch) jest optymalna dla procesów iteracyjnych, gdzie rozwiązanie jest stopniowo ulepszane krok po kroku.
- **Narzut (podatek) koordynacyjny** staje się odczuwalny przy zespole liczącym powyżej 4 agentów w topologii grafu. Zużycie tokenów oraz opóźnienia (wall-clock time) rosną szybciej niż zysk na dokładności.

Granica 4 agentów wynika z obserwacji empirycznych i odzwierciedla ograniczenia pojemności kontekstu modeli LLM: historia interakcji każdego agenta zapełnia się odpowiedziami pozostałych uczestników, co sprawia, że korzyść krańcowa z dodania kolejnego (N+1) agenta drastycznie spada w modelu komunikacji „każdy z każdym”.

### Ewaluacja strategii debat wieloagentowych

W publikacji arXiv:2311.17371 poddano analizie strategie debaty wieloagentowej (MAD). Kluczowy wniosek: warianty MAD strukturalnie zbliżone do prostej samospójności (niezależne próbkowanie i agregacja) często wykazują gorszy stosunek dokładności do kosztów niż tradycyjna samospójność przy tym samym budżetu. Model debaty przynosi największe korzyści, gdy agenty są silnie zróżnicowane (heterogeniczne), a dyskusja opiera się na kontrargumentacji (obecność oponenta).

### Zachowania emergentne w AgentVerse

Projekt AgentVerse (ICLR 2024) dokumentuje dwa zachowania, które pojawiają się spontanicznie podczas debat wieloagentowych, bez wcześniejszego zaprogramowania:

- **Wolontariat (Volunteer behavior).** Agent samodzielnie deklaruje chęć wykonania zadania („mogę zająć się kolejnym krokiem”) bez wyraźnego polecenia. Pomaga to przydzielić podzadanie najbardziej kompetentnemu wykonawcy.
- **Konformizm (Conforming behavior).** Agent modyfikuje swoje zdanie pod wpływem krytyki oponenta, nawet jeśli ten drugi się myli. Jest to odpowiednik potakiwania (sycophancy) w środowisku debaty (Lekcja 14).

Podatność na konformizm sprawia, że debata prowadzona do momentu osiągnięcia pełnej zgody promuje agenty dominujące. Wprowadzenie limitu rund oraz niezależnego sędziego skutecznie eliminuje to zjawisko.

### Zróżnicowanie (heterogeniczność) jako klucz do dokładności

Zasada sprawdzona w praktyce produkcyjnej: zastąpienie jednego z N agentów innym modelem bazowym daje większy przyrost dokładności niż proste zwiększenie liczebności zespołu (N+1). Wynika to bezpośrednio z unikania monokultury — wprowadzenie nowego źródła nieskorelowanych błędów ma większą wartość niż kolejna skorelowana próbka.

W środowiskach produkcyjnych zróżnicowanie modeli wygrywa z ich liczbą. Trzy różne modele bazowe osiągają lepsze wyniki niż pięć instancji tego samego modelu w większości zadań o obiektywnych kryteriach poprawności.

### Metody oparte na panelach sędziowskich (Jury)

Koncepcja paneli sędziowskich (Jury) formalizuje proces oceny poprzez delegowanie ról w zespole (np. jeden agent zadaje pytania, inny dostarcza kontekst merytoryczny, a trzeci ocenia wiarygodność wypowiedzi). Stanowi to złoty środek między prostym głosowaniem większościowym (tani, ale podatny na monokulturę) a pełną debatą (droga i podatna na konformizm).

### Kiedy stosować głosowanie z debatą

- Zadanie posiada obiektywne kryteria poprawności (fakt, matematyka, testy kodu), dzięki czemu zbieżność głosów ma realne znaczenie.
- Agenty mają dostęp do różnych narzędzi lub zróżnicowanych źródeł wiedzy (wysoki stopień heterogeniczności).
- Liczba rund jest ograniczona (zazwyczaj do 2-3), a ostateczną decyzję podejmuje niezależny weryfikator lub sędzia.
- Budżet pozwala na uruchomienie 3-5 agentów. Powyżej tej granicy w topologii grafu narzut koordynacyjny staje się nieuzasadniony.

### Kiedy debata przynosi szkody

- Zadanie ma charakter subiektywny (opinie, syntezy). Agenty mają tendencję do zgadzania się z wypowiedziami generowanymi z największą pewnością siebie, co nie gwarantuje poprawności.
- Wszystkie agenty korzystają z tego samego modelu bazowego (zagrożenie monokulturą).
- Rundy są nieograniczone, co prowadzi do ulegania konformizmowi.
- Zadanie jest proste. Zastosowanie spójności wewnętrznej (Self-Consistency) na jednym modelu przy N=5 jest tańsze i równie dokładne.

## Zbuduj to

Plik `code/main.py` implementuje:

- `run_star(agents, hub, question)` — centralny koordynator odpytuje wykonawców i agreguje wyniki.
- `run_chain(agents, question)` — sekwencyjne ulepszanie odpowiedzi.
- `run_tree(root, children, question)` — struktura hierarchiczna z dwupoziomową agregacją.
- `run_graph(agents, question, rounds)` — debata typu każdy z każdym (Graph) z ograniczoną liczbą rund.
- Symulację heterogeniczności: każdy agent posiada przypisany parametr `error_bias` reprezentujący jego systematyczny błąd.
- System pomiarowy analizujący działanie poszczególnych topologii dla $N=3, 5, 7$ (dokładność, liczba tokenów, czas wykonania).

Uruchomienie:

```bash
python3 code/main.py
```

Oczekiwany wynik: tabela topologii × N -> (dokładność, tokeny, opóźnienie). Topologia pełnego grafu (Graph) wykazuje najwyższą dokładność dla N=3-5 w zadaniach badawczych; gwiazda (Star) jest optymalna dla szybkich zapytań faktograficznych. Przy N=7 w topologii grafu wyraźnie widać podatek koordynacyjny (opóźnienie rośnie nieproporcjonalnie do przyrostu dokładności).

## Zastosowanie

Plik `outputs/skill-topology-picker.md` określa metodologię wyboru topologii komunikacji w zależności od profilu zadania: rekomendując liczbę agentów (N), poziom heterogeniczności (modele bazowe) oraz limity rund.

## Wdrożenie produkcyjne

Dla dowolnego zespołu agentów:

- Rozpocznij od **samospójności (Self-Consistency) przy N=5** na jednym, silnym modelu bazowym. Stanowi to tani punkt odniesienia.
- Jeśli wymagana jest wyższa dokładność, wdróż **głosowanie heterogeniczne przy N=3** i zmierz przyrost skuteczności.
- Przejdź do **pełnej debaty** wyłącznie w przypadku złożonych zadań (np. badania wieloetapowe) i pamiętaj o nałożeniu sztywnego limitu rund.
- Zawsze loguj głosy mniejszości (minority clusters). Jeśli mniejszość ma rację, jest to znak, że różnorodność modeli działa poprawnie.
- Monitoruj czas wykonania oraz zużycie tokenów obok dokładności. Zwiększenie dokładności kosztem 10-krotnego wzrostu kosztów to decyzja biznesowa.

## Ćwiczenia

1. Uruchom `code/main.py`. Wykreśl krzywą podatku koordynacyjnego dla topologii grafów: dokładność vs N, tokeny vs N. Przy jakim N krzywa ulega załamaniu?
2. Zaimplementuj wariant A-HMAD: trzy agenty o celowo zróżnicowanych profilach błędu systematycznego. Porównaj wyniki z jednorodnym zespołem w warunkach ataku monokulturowego z Lekcji 14.
3. Wprowadź rolę sędziego do topologii grafu, który nie bierze udziału w debacie, a jedynie ocenia ostateczny konsensus. Zaobserwuj, jak wpływa to na zjawisko konformizmu.
4. Zapoznaj się z pracą AgentVerse (ICLR 2024). Sprawdź, które z emergentnych zachowań są najbardziej widoczne w Twojej implementacji. Spróbuj wywołać zachowania przeciwstawne za pomocą modyfikacji promptu.
5. Przeczytaj Sekcję 4 pracy MultiAgentBench (arXiv:2503.01935) dotyczącą eksperymentów z topologiami. Spróbuj zreplikować wynik potwierdzający przewagę topologii grafu w zadaniach badawczych.

## Kluczowe terminy

| Termin | Obiegowe określenie | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Samospójność (Self-Consistency) | „N-krotnia próba i głosowanie” | Wang 2022. Wygenerowanie N próbek z jednego modelu (temperatura > 0) i zliczanie głosów nad ścieżkami wnioskowania. |
| Heterogeniczność | „Zróżnicowanie modeli” | Zastosowanie zróżnicowanych modeli bazowych lub wersji instrukcji w celu eliminacji monokultury. |
| MAD | „Debata wieloagentowa” | Ogólne określenie na wymianę opinii i krytyki między agentami w turach (np. Du 2023). |
| A-HMAD | „Kontradyktoryjna zróżnicowana debata” | Wariant debaty MAD kładący nacisk na heterogeniczność modeli i obecność oponenta. |
| Topologia | „Schemat komunikacji” | Struktura przepływu informacji w zespole: gwiazda (Star), łańcuch (Chain), drzewo (Tree), graf (Graph). |
| Podatek koordynacyjny | „Narzut koordynacyjny” | Zjawisko polegające na tym, że powyżej ~4 agentów w grafie koszt (opóźnienia, tokeny) rośnie szybciej niż zysk na dokładności. |
| Wolontariat (Volunteer behavior) | „Samodzielna deklaracja pomocy” | Emergentny wzorzec z AgentVerse: agent sam proponuje wykonanie kolejnego etapu pracy. |
| Konformizm (Conforming behavior) | „Uleganie sugestii” | Emergentny wzorzec z AgentVerse: agent zmienia zdanie pod wpływem nacisku lub krytyki oponenta. |
| Panel sędziowski (Jury) | „Dedykowany panel ekspercki” | Zespół agentów o wyspecjalizowanych rolach (np. pytający, oceniający, dostarczający kontekst). |

## Literatura uzupełniająca

- [Wang i in. — Self-Consistency Improves Chain of Thought in Language Models](https://arxiv.org/abs/2203.11171) — badanie bazowe dla jednego modelu.
- [Du i in. — Improving Factuality and Reasoning in Language Models through Multi-Agent Debate](https://arxiv.org/abs/2305.14325) — wykazanie, że liczba agentów i liczba rund wpływają na wynik niezależnie.
- [MultiAgentBench / MARBLE](https://arxiv.org/abs/2503.01935) — test porównawczy topologii wykazujący przewagę topologii grafu w badaniach oraz łańcucha w procesach iteracyjnych.
- [Should We Go Mad?](https://arxiv.org/abs/2311.17371) — przegląd strategii MAD; analiza porównawcza z samospójnością przy stałym budżecie.
- [AgentVerse (ICLR 2024)](https://proceedings.iclr.cc/paper_files/paper/2024/file/578e65cdee35d00c708d4c64bce32971-Paper-Conference.pdf) — praca opisująca zachowania wolontariackie i konformizm.
- [Repozytorium MARBLE](https://github.com/ulab-uiuc/MARBLE) — referencyjna implementacja benchmarku.
