# Skalowalny nadzór i generalizacja od słabej do mocnej

> Burns i in. (OpenAI Superalignment, „Weak-to-Strong Generalization”, 2023) zaproponował zastępcze rozwiązanie problemu superwyrównania: dostrojenie silnego modelu za pomocą etykiet utworzonych przez słabszy model. Jeśli silny model prawidłowo uogólnia na podstawie niedoskonałego słabego nadzoru, obecne metody dopasowywania na skalę ludzką mogą rozszerzyć się na systemy nadludzkie. Skalowalny nadzór i W2SG uzupełniają się. Skalowalny nadzór (debata, rekurencyjne modelowanie nagród, dekompozycja zadań) zwiększa efektywne możliwości nadzorcy, dzięki czemu może nadążać za nadzorowanym modelem. W2SG zapewnia, że ​​silny model prawidłowo uogólnia na podstawie niedoskonałego nadzoru zapewnianego przez nadzorcę. Debata pomaga W2SG (arXiv:2501.13124, styczeń 2025) łączy je.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulator luki W2SG)
**Wymagania wstępne:** Faza 18 · 01 (przestrzeganie instrukcji), Faza 18 · 10 (Kontrola AI), Faza 09 (podstawy RL)
**Czas:** ~60 minut

## Cele nauczania

- Zdefiniuj skalowalny nadzór i generalizację od słabej do mocnej oraz wyjaśnij, w jaki sposób się uzupełniają.
- Opisz zespół Burnsa i in. Konfiguracja eksperymentalna na rok 2023: dostrojenie GPT-4 przy użyciu etykiet z GPT-2.
- Wyjaśnij wskaźnik odzyskanej luki w wydajności (PGR) i jego pomiar.
- Podaj trzy główne skalowalne mechanizmy nadzoru (debata, rekurencyjne modelowanie nagród, rozkład zadań) i jedną mocną stronę każdego z nich.

## Problem

Każda technika dopasowywania dotychczas w fazie 18 zakłada, że nadzorca może ocenić zachowanie modelu. Kiedy model jest nadludzki, nadzorca jest słabym ogniwem. Pytanie dotyczące superdopasowania: czy słabszy przełożony może niezawodnie stworzyć silniejszy, dostosowany model?

Burns i in. zredukuj to do zoperacjonalizowanego układu empirycznego: nadzoruj silny ze słabym, zmierz, jaka część możliwości silnego modelu przetrwa słaby nadzór. To nie jest rozwiązanie problemu superwyrównania — to wskaźnik zastępczy, który pozwala nam mierzyć postęp.

## Koncepcja

### W2SG: Burns i in. konfiguracja

- Słaby model: klasa GPT-2.
- Mocny model: klasa GPT-4.
- Cel: mocny pułap GPT-4 w zadaniu.

Procedura:
1. Uzyskaj prognozy zerowego strzału słabego modelu dla zadania.
2. Dostosuj mocny model na słabo oznakowanych danych.
3. Zmierz dokładność dobrze dostrojonego modelu.

Linie bazowe: słaba dokładność własna modelu, mocny nadzorowany sufit modelu na złotych etykietach.

Wskaźnik luki: Odzyskana luka w wydajności (PGR) = (dostrojona – słaba) / (pułap – słaba). PGR wynoszący 1,0 oznacza, że ​​słaby nadzór całkowicie zamyka lukę; PGR równy 0 oznacza, że ​​słaby nadzór nie pomógł.

### Burns i in. ustalenia empiryczne

W przypadku zadań związanych z NLP, łamigłówkami szachowymi i modelowaniem nagród PGR był niezmiennie pozytywny: silny model uogólnił się poza błędy słabego przełożonego. PGR specyficzny dla zadania wahał się od ~20% do ~80%. Silny model „rozumie” zamierzone zadanie z niedoskonałych etykiet, wypełniając je wcześniej wytrenowanymi priorytetami.

Ograniczenia Burns i in. uwaga:
- Różnica między słabą a silną stroną polega na możliwościach, a nie na dostosowaniu. Słaby model jest wyrównany; prawdziwie nadludzki model mógłby zostać opracowany przez człowieka, ale przy znacznie większej luce w możliwościach.
- Uogólnienie silnego modelu może bardziej dotyczyć priorytetów zadań niż odzyskania intencji opartej na zasadzie prawdy.
- Prawdziwym problemem jest wydobycie ukrytej wiedzy silnego modelu; PGR mierzy konkretną operacjonalizację.

### Skalowalny nadzór: trzy mechanizmy

- **Debata (Irving et al. 2018).** Dwa przypadki U argumentują przeciwne strony; słaby sędzia decyduje. Założenie: znalezienie przekonującej, prawdziwej odpowiedzi jest łatwiejsze niż znalezienie przekonującej fałszywej odpowiedzi. Niedawne prace z lat 2024–2025 (Khan i in., Michael i in.) pokazują, że debata czasami pomaga, a czasami nie, a to, czy pomaga, zależy od struktury zadań.
- **Rekurencyjne modelowanie nagród (Leike i in. 2018).** U pomaga człowiekowi wyszkolić model nagrody dla U+1. Efektywna zdolność nadzorcy rośnie wraz z umiejętnością modelu.
- **Dekompozycja zadań (Christiano, Shlegeris, Amodei 2018).** Rozłóż trudne zadanie na podzadania, które człowiek może sprawdzić rekurencyjnie. Zakłada rozkład.

Każdy mechanizm zakłada coś na temat struktury zadania lub ułożenia elementów pośrednich.

### Dlaczego skalowalny nadzór i W2SG uzupełniają się

Skalowalny nadzór zwiększa efektywną jakość sygnału nadzorcy.
W2SG wypełnia lukę w stosunku do wszelkich niedoskonałych sygnałów, jakie może dostarczyć nadzorca.

Langa i in. — Debata pomaga w uogólnieniu od słabego do silnego (arXiv:2501.13124) łączy je: protokół debaty zapewnia lepsze słabe etykiety, a silny model jest szkolony na tych etykietach. Zgłoszone zyski PGR z zadań NLP.

### Dramat organizacyjny

Zespół OpenAI Superalignment rozwiązał się w maju 2024 r. po odejściu Jana Leike'a do Anthropic. Program (skalowalny nadzór, W2SG, zautomatyzowane badania nad wyrównaniem) był kontynuowany w Anthropic i laboratoriach akademickich — MATS (lekcja 28), Redwood (lekcja 10), Apollo (lekcja 8), METR (lekcja 28). Zmieniła się struktura organizacyjna; pytania badawcze nie.

### Gdzie to pasuje do fazy 18

Lekcje 6-10 opisują zagrożenie i paradygmat obronny przy założeniu, że U jest niegodne zaufania. Lekcja 11 to paradygmat ofensywny: uczyń nadzorcę wystarczająco silnym, aby zweryfikował ułożenie U. Następnie lekcje 12-16 skupiają się na praktycznych narzędziach ewaluacji kontradyktoryjnej.

## Użyj tego

`code/main.py` symuluje dostrojenie W2SG w zadaniu syntetycznym. Słaby etykietujący ma 70% dokładności z błędami strukturalnymi; mocny model ma 95% pułapu na złotych etykietach. Dostrajasz mocny model na słabych etykietach, mierzysz PGR i porównujesz z silnym na złocie i samym słabym.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-w2sg-pgr.md`. Biorąc pod uwagę opis konfiguracji nadzoru, identyfikuje on słabego nadzorcę, mocny model, jakość nadzoru i oblicza (lub żąda) PGR. Zaznacza, czy stwierdzenie brzmi „słaby może nadzorować silny” lub „słaby + mechanizm nadzoru może nadzorować silny”.

## Ćwiczenia

1. Uruchom `code/main.py`. Zgłoś PGR dla słabej dokładności = 0,60, 0,70, 0,80. Wyjaśnij kształt krzywej PGR.

2. Zmodyfikuj słaby znacznik tak, aby zawierał błąd strukturalny (np. zawsze błędny w określonej klasie wejściowej). Czy PGR rośnie, maleje, czy pozostaje taki sam? Wyjaśnić.

3. Przeczytaj Burns i in. 2023 Sekcja 4.3 (Zadania NLP). Odtwórz intuicję „pomocnicza utrata zaufania”: kto wygrywa, gdy silny model jest bardziej pewny siebie niż słabe marki?

4. Zaprojektuj skalowalny protokół nadzoru, który łączy debatę i dekompozycję zadań dla zadania inżynierii oprogramowania. Nazwij jeden tryb awarii każdego komponentu i wyjaśnij, w jaki sposób kombinacja rozwiązuje lub nie rozwiązuje każdego z nich.

5. Wyartykułuj, co fałszowałoby twierdzenie, że „uogólnienie od słabego do silnego jest realną drogą do superwyrównania”. Określ szczegółowo podpis empiryczny, który musisz zobaczyć.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Skalowalny nadzór | „uczynić nadzorcę silniejszym” | Mechanizmy zwiększające zdolność nadzorcy do oceny bardziej sprawnego modelu |
| W2SG | „słaby nadzoruje silny” | Dostrajanie silnego modelu na słabych etykietach i mierzenie odzyskanej zdolności |
| PGR | „odzyskano lukę w wydajności” | (dostrojony - słaby) / (sufit - słaby); 1,0 = całkowicie zamknięte, 0 = brak pomocy |
| Debata | „dwa wystąpienia U kłócą się” | Skalowalny mechanizm nadzoru, w którym słaby sędzia wybiera pomiędzy dwoma obrońcami U |
| RRM | „rekurencyjne modelowanie nagród” | U pomaga trenować model nagrody dla U+1; zdolność nadzorcy śledzi U |
| Rozkład zadań | „zadania podrzędne, które sprawdza człowiek” | Podziel trudne zadanie na podzadania, które człowiek może zweryfikować rekurencyjnie |
| Superwyrównanie | „dostosowanie nadludzkiej sztucznej inteligencji” | Program badań dotyczy ujednolicenia modeli, których człowiek nie może bezpośrednio ocenić |

## Dalsze czytanie

- [Burns i in. — Generalizacja od słabej do silnej (OpenAI 2023)](https://openai.com/index/weak-to-strong-generalization/) — artykuł W2SG
- [Irving, Christiano, Amodei — Bezpieczeństwo sztucznej inteligencji poprzez debatę (arXiv:1805.00899)](https://arxiv.org/abs/1805.00899) — mechanizm debaty
- [Leike i in. — Skalowalne dopasowanie agentów poprzez modelowanie nagród (arXiv:1811.07871)](https://arxiv.org/abs/1811.07871) — rekurencyjne modelowanie nagród
- [Khan i in. — Debata z bardziej przekonującymi LLM prowadzi do bardziej prawdziwych odpowiedzi (arXiv:2402.06782)](https://arxiv.org/abs/2402.06782) — Badanie empiryczne debaty z silniejszymi debatantami z 2024 r.
- [Lang i in. — Debata pomaga w uogólnianiu od słabego do silnego (arXiv:2501.13124)](https://arxiv.org/abs/2501.13124) — Połączenie debaty 2025 + W2SG