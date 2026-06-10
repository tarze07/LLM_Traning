# Skalowalny nadzór i generalizacja od słabego do silnego

> Burns i in. (zespół OpenAI Superalignment, „Weak-to-Strong Generalization”, 2023) zaproponowali eksperymentalny substytut (proxy) problemu superdopasowania (superalignment): dostrojenie silnego modelu na etykietach wygenerowanych przez model słabszy. Jeśli silny model potrafi poprawnie uogólniać (generalizować) wiedzę na podstawie niedoskonałego, słabego nadzoru, to obecne metody dopasowania oparte na ocenie ludzkiej będą mogły zostać rozszerzone na systemy nadludzkie. Skalowalny nadzór (scalable oversight) i generalizacja od słabego do silnego (W2SG) uzupełniają się: skalowalny nadzór (poprzez debatę, rekurencyjne modelowanie nagród czy dekompozycję zadań) zwiększa efektywne możliwości nadzorcy, pozwalając mu nadążyć za nadzorowanym modelem. Z kolei W2SG gwarantuje, że silny model poprawnie uogólni reguły nawet z niedoskonałych instrukcji dostarczonych przez nadzorcę. Praca *Debate Helps Weak-to-Strong Generalization* (arXiv:2501.13124, styczeń 2025) łączy oba te podejścia.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulator luki W2SG)
**Wymagania wstępne:** Faza 18 · 01 (przestrzeganie instrukcji), Faza 18 · 10 (Kontrola AI), Faza 09 (podstawy RL)
**Czas:** ~60 minut

## Cele nauczania

- Zdefiniuj skalowalny nadzór oraz generalizację od słabego do silnego (weak-to-strong generalization) i wyjaśnij, w jaki sposób się uzupełniają.
- Opisz konfigurację eksperymentalną w pracy Burns i in. (2023): dostrojenie modelu klasy GPT-4 przy użyciu etykiet wygenerowanych przez model klasy GPT-2.
- Wyjaśnij wskaźnik odzyskanej luki w wydajności (Performance Gap Recovered, PGR) oraz to, co dokładnie mierzy.
- Wymień trzy główne mechanizmy skalowalnego nadzoru (debata, rekurencyjne modelowanie nagród, dekompozycja zadań) i wskaż po jednej mocnej stronie każdego z nich.

## Problem

Wszystkie dotychczasowe techniki dopasowania w Fazie 18 zakładały, że nadzorca jest w stanie ocenić poprawne zachowanie modelu. W przypadku systemów nadludzkich to ludzki nadzorca staje się najsłabszym ogniwem. Pytanie o superdopasowanie brzmi: czy słabszy nadzorca może w wiarygodny sposób wyszkolić silniejszy, dopasowany model?

Burns i in. sprowadzili ten problem do zoperacjonalizowanego układu empirycznego: nadzorowania silnego modelu przez słaby oraz pomiaru, jaka część zdolności silnego modelu przetrwa pod tak niedoskonałym nadzorem. Nie jest to jeszcze gotowe rozwiązanie problemu superdopasowania, lecz wskaźnik zastępczy (proxy) pozwalający mierzyć postępy w badaniach.

## Koncepcja

### W2SG: Konfiguracja w pracy Burns i in.

- Słaby model: klasa GPT-2.
- Silny model: klasa GPT-4.
- Cel: maksymalna wydajność silnego modelu GPT-4 w danym zadaniu (ceiling).

Procedura:
1. Pozyskanie predykcji słabego modelu w trybie zero-shot dla wybranego zadania.
2. Dostrojenie silnego modelu na danych oznaczonych słabymi etykietami.
3. Pomiar dokładności silnego modelu po dostrojeniu.

Warianty referencyjne: bazowa dokładność słabego modelu oraz maksymalna dokładność silnego modelu szkolonego na etykietach referencyjnych (gold labels).

Metryka luki: Odzyskana luka w wydajności (Performance Gap Recovered, PGR) = (dokładność po dostrojeniu – dokładność słabego) / (dokładność maksymalna – dokładność słabego). PGR o wartości 1,0 oznacza, że słaby nadzór całkowicie zamyka lukę wydajnościową; PGR równy 0 oznacza, że słaby nadzór w żaden sposób nie pomógł.

### Wyniki empiryczne Burns i in.

W zadaniach z zakresu NLP, rozwiązywania zadań szachowych oraz modelowania nagród wskaźnik PGR był stale dodatni: silny model uogólniał wiedzę ponad błędy popełniane przez słabszego nadzorcę. W zależności od zadania wskaźnik PGR wahał się w granicach od ~20% do ~80%. Silny model „rozumie” intencję zadania na podstawie niedoskonałych etykiet, uzupełniając braki wiedzą pozyskaną na etapie wstępnego treningu (pre-trained priors).

Ograniczenia wskazane przez Burns i in.:
- Luka między słabym a silnym modelem dotyczy tu jedynie zdolności (capabilities), a nie samego dopasowania (alignment). Słaby model jest dopasowany; w rzeczywistym scenariuszu nadludzki model musiałby być dopasowywany przez człowieka przy znacznie większej różnicy w możliwościach.
- Uogólnienie silnego modelu może w większym stopniu bazować na ogólnej wiedzy o zadaniach niż na rzeczywistym odtworzeniu intencji z etykiet referencyjnych.
- Kluczowym wyzwaniem pozostaje wydobycie utajonej wiedzy (latent knowledge) silnego modelu; PGR mierzy jedynie specyficzną operacjonalizację tego procesu.

### Skalowalny nadzór: trzy mechanizmy

- **Debata (Irving i in., 2018).** Dwie instancje modelu U argumentują za przeciwnymi stanowiskami, a słaby sędzia decyduje o wyniku. Założenie: sformułowanie przekonującej i prawdziwej odpowiedzi jest łatwiejsze niż stworzenie przekonującego kłamstwa. Prace z lat 2024–2025 (Khan i in., Michael i in.) wskazują, że debata pomaga wybiórczo, w zależności od struktury konkretnego zadania.
- **Rekurencyjne modelowanie nagród (Recursive Reward Modeling, Leike i in., 2018).** Model U pomaga człowiekowi w szkoleniu modelu nagrody dla wersji U+1. Efektywna zdolność nadzorcza rośnie dzięki temu proporcjonalnie do rozwoju samego modelu.
- **Dekompozycja zadań (Task Decomposition, Christiano, Shlegeris, Amodei, 2018).** Rekurencyjne rozbicie złożonego zadania na mniejsze podzadania, które człowiek jest w stanie samodzielnie zweryfikować. Metoda zakłada pełną podzielność zadań.

Każdy z tych mechanizmów opiera się na specyficznych założeniach dotyczących struktury zadań lub dopasowania komponentów pośrednich.

### Dlaczego skalowalny nadzór i W2SG się uzupełniają

Skalowalny nadzór podnosi efektywną jakość sygnału generowanego przez nadzorcę.
Generalizacja W2SG pozwala zamknąć lukę wydajnościową mimo niedoskonałości sygnałów dostarczanych przez nadzorcę.

Praca Lang i in. – *Debate Helps Weak-to-Strong Generalization* (arXiv:2501.13124) łączy oba podejścia: protokół debaty dostarcza lepszej jakości słabych etykiet, na których następnie trenowany jest silny model. W badaniu odnotowano wzrost wskaźnika PGR w zadaniach NLP.

### Zmiany organizacyjne

Zespół OpenAI Superalignment został rozwiązany w maju 2024 r. po przejściu Jana Leikego do Anthropic. Realizacja programu badawczego (skalowalny nadzór, W2SG, zautomatyzowane badania nad dopasowaniem) była kontynuowana w Anthropic oraz w laboratoriach partnerskich: MATS (Lekcja 28), Redwood (Lekcja 10), Apollo (Lekcja 8) i METR (Lekcja 28). Zmianie uległa struktura organizacyjna, lecz pytania badawcze pozostały te same.

### Miejsce w strukturze Fazy 18

Lekcje 6-10 opisują charakter zagrożenia i paradygmat obronny oparty na założeniu, że U jest niegodne zaufania. Lekcja 11 przedstawia paradygmat aktywny: wyposażenie nadzorcy w narzędzia pozwalające zweryfikować dopasowanie modelu U. Kolejne lekcje (12-16) skupiają się na praktycznych narzędziach ewaluacji wrogiej (adversarial evaluation).

## Użycie kodu

Plik `code/main.py` symuluje dostrajanie W2SG w zadaniu syntetycznym. Słaby moduł etykietujący charakteryzuje się dokładnością na poziomie 70% i popełnia błędy strukturalne; z kolei silny model osiąga maksymalnie 95% dokładności na etykietach referencyjnych (gold labels). Dostrajając silny model na słabych etykietach, mierzysz wskaźnik PGR i porównujesz wyniki z wariantem referencyjnym oraz samym słabym modelem.

## Co otrzymasz

Ta lekcja przygotowuje plik `outputs/skill-w2sg-pgr.md`. Na podstawie opisu konfiguracji nadzoru dokument ten identyfikuje słabego nadzorcę, silny model oraz jakość nadzoru, a także oblicza (bądź wymaga podania) wskaźnik PGR. Określa również, czy stawiana teza głosi, że „słaby model może nadzorować silny”, czy też „słaby model wspierany przez mechanizm nadzoru może nadzorować silny”.

## Ćwiczenia

1. Uruchom `code/main.py`. Zgłoś wartość PGR dla parametrów słabej dokładności (weak_accuracy) równych 0,60, 0,70 oraz 0,80. Wyjaśnij kształt uzyskanej krzywej PGR.

2. Zmodyfikuj słaby moduł etykietujący tak, aby generował błędy strukturalne (np. stale podawał błędne wyniki dla konkretnej klasy danych wejściowych). Czy wskaźnik PGR wzrośnie, spadnie, czy pozostanie bez zmian? Uzasadnij odpowiedź.

3. Przeczytaj sekcję 4.3 w pracy Burns i in. (2023) dotyczącą zadań NLP. Odtwórz intuicję stojącą za pomocniczą funkcją straty opartą na pewności (confidence auxiliary loss): jak zachowuje się system, gdy silny model wykazuje większą pewność niż słabe etykiety?

4. Zaprojektuj protokół skalowalnego nadzoru łączący debatę i dekompozycję zadań w scenariuszu inżynierii oprogramowania. Wskaż po jednym scenariuszu awarii (failure mode) dla każdego z tych komponentów i wyjaśnij, jak ich połączenie eliminuje bądź nie eliminuje te zagrożenia.

5. Sformułuj warunki, które pozwoliłyby obalić tezę, że „generalizacja od słabego do silnego (W2SG) jest skuteczną drogą do osiągnięcia superdopasowania”. Opisz precyzyjnie oczekiwany wzorzec empiryczny.

## Kluczowe terminy

| Termin | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|--------------------------------------|
| Skalowalny nadzór (Scalable oversight) | „zwiększanie siły nadzorcy” | Metody podnoszące zdolność nadzorcy do rzetelnej oceny modelu o wyższych możliwościach |
| Generalizacja W2SG | „słaby nadzoruje silnego” | Dostrajanie silnego modelu na słabych etykietach i pomiar odsetka odzyskanych zdolności |
| PGR | „odzyskana luka wydajności” | (wynik po dostrojeniu - słaby) / (maksymalny - słaby); 1,0 = pełne zamknięcie luki, 0 = brak poprawy |
| Debata (Debate) | „dyskusja instancji modelu U” | Protokół skalowalnego nadzoru, w którym słaby sędzia wybiera lepszą odpowiedź spośród argumentów dwóch instancji U |
| RRM | „rekurencyjne modelowanie nagród” | Model U pomaga w szkoleniu modelu nagrody dla wersji U+1; możliwości nadzorcze rosną wraz z rozwojem modelu |
| Dekompozycja zadań | „dzielenie zadań dla człowieka” | Podział złożonego problemu na podzadania, które człowiek jest w stanie zweryfikować w sposób rekurencyjny |
| Superdopasowanie (Superalignment) | „dopasowanie nadludzkiej AI” | Program badawczy dotyczący metod bezpiecznego dopasowywania systemów AI, których człowiek nie potrafi bezpośrednio ocenić |

## Dalsze czytanie

- [Burns et al. — Weak-to-Strong Generalization (OpenAI 2023)](https://openai.com/index/weak-to-strong-generalization/) – kanoniczna publikacja dotycząca W2SG
- [Irving, Christiano, Amodei — AI safety via debate (arXiv:1805.00899)](https://arxiv.org/abs/1805.00899) – pierwotny opis mechanizmu debaty
- [Leike et al. — Scalable agent alignment via reward modeling (arXiv:1811.07871)](https://arxiv.org/abs/1811.07871) – koncepcja rekurencyjnego modelowania nagród
- [Khan et al. — Debating with More Persuasive LLMs Leads to More Truthful Answers (arXiv:2402.06782)](https://arxiv.org/abs/2402.06782) – badanie z 2024 r. nad skutecznością debaty przy silniejszych uczestnikach
- [Lang et al. — Debate Helps Weak-to-Strong Generalization (arXiv:2501.13124)](https://arxiv.org/abs/2501.13124) – praca z 2025 r. łącząca debatę z generalizacją W2SG
