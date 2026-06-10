# Kryteria sprawiedliwości – grupowe, indywidualne, kontrfaktyczne

> Literaturę na temat sprawiedliwości tworzą trzy rodziny. Sprawiedliwość grupowa: parytet demograficzny, wyrównane szanse, równość dokładności użycia warunkowego – średnio równe stawki we wszystkich grupach chronionych. Indywidualna sprawiedliwość (Dwork i in. 2012): podobne osoby otrzymują podobne decyzje; Warunek Lipschitza na mapie decyzyjnej. Sprawiedliwość kontrfaktyczna (Kusner i in. 2017): decyzja jest sprawiedliwa wobec jednostki, jeśli pozostaje niezmieniona w przypadku kontrfaktycznej zmiany wrażliwych atrybutów. Wynik teoretyczny za 2024 r. (NeurIPS 2024): istnieje nieodłączny kompromis między CF a dokładnością; metoda niezależna od modelu przekształca optymalny, ale nieuczciwy predyktor w predyktor CF z ograniczoną utratą dokładności. Wycofujące się scenariusze kontrfaktyczne (arXiv:2401.13935, styczeń 2024): nowy paradygmat, który pozwala uniknąć wymagania interwencji w zakresie atrybutów prawnie chronionych. Pojednanie filozoficzne (ICLR Blogposts 2024): w przypadku wykresów przyczynowych spełnienie pewnych miar sprawiedliwości grupowej pociąga za sobą sprawiedliwość kontrfaktyczną.

**Typ:** Ucz się
**Języki:** Python (stdlib, porównanie trzech kryteriów)
**Wymagania wstępne:** Faza 18 · 20 (odchylenie), Faza 02 (klasyczny ML)
**Czas:** ~60 minut

## Cele nauczania

- Podaj trzy kryteria uczciwości grupowej (parytet demograficzny, wyrównane szanse, równość dokładności użycia warunkowego) i jeden wynik niemożliwości.
- Opisać indywidualną sprawiedliwość za pomocą Dworka i in. Preparat Lipschitza z 2012 r.
- Opisać sprawiedliwość kontrfaktyczną i jej zależność od wykresu przyczynowego.
- Wyjaśnij alternatywne rozwiązania oparte na wycofywaniu się i dlaczego omijają one problem interwencji na chronionym atrybucie.

## Problem

Lekcja 20 dotyczyła pomiaru błędu systematycznego. Lekcja 21 dotyczy zdefiniowania standardu uczciwości, któremu powinien służyć pomiar. Te trzy rodziny wyznaczają strukturalnie różne standardy — model może być sprawiedliwy wobec grupy i niesprawiedliwy dla jednostki, sprawiedliwy w sposób kontrfaktyczny i niesprawiedliwy wobec grupy. Wybór standardu jest decyzją polityczną; żaden standard nie jest uniwersalnie optymalny.

## Koncepcja

### Sprawiedliwość grupowa

- **Parytet demograficzny.** P(Y=1 | A=a) = P(Y=1 | A=a') dla wszystkich grup. Równe wskaźniki akceptacji.
- **Wyrównane szanse.** P(Y=1 | Y*=y, A=a) = P(Y=1 | Y*=y, A=a'). Równe TPR i FPR we wszystkich grupach.
- **Warunkowa równość dokładności użycia.** P(Y*=y | Y=y, A=a) = P(Y*=y | Y=y, A=a'). Równa wartość predykcyjna we wszystkich grupach.

Niemożliwość (Chouldechova, Kleinberg-Mullainathan-Raghavan 2017): tych trzech nie można spełnić jednocześnie przy nierównych stawkach podstawowych.

### Indywidualna sprawiedliwość

Dwork i in. 2012. Mapa decyzyjna f jest indywidualnie sprawiedliwa w odniesieniu do metryki podobieństwa specyficznej dla zadania d, jeśli |f(x) - f(x')| <= L * d(x, x') dla pewnej stałej Lipschitza L. Podobne osoby podejmują podobne decyzje.

Wymaga zdefiniowania d. Pytanie polityczne, a nie statystyczne.

### Uczciwość alternatywna

Kusner i in. 2017. Decyzja jest sprawiedliwa wobec jednostki i, jeśli w przyczynowym modelu populacji decyzja pozostaje niezmieniona, gdy w kontrfaktyczny sposób zmienione są wrażliwe atrybuty i.

Wymaga przyczynowego DAG. DAG to wybór modelowy. Sprawiedliwość alternatywna jest uzasadniona tylko w takim stopniu, jak DAG.

### Kompromis CF vs dokładność

Teoria NeurIPS 2024: istnieje nieodłączny kompromis pomiędzy uczciwością kontrfaktyczną a dokładnością przewidywań. Metoda niezależna od modelu może przekształcić optymalny, ale nieuczciwy predyktor w predyktor CF, przy ograniczonym koszcie dokładności. Koszt dokładności zależy od wielkości współczynnika atrybutu wrażliwości w optymalnym nieuczciwym predyktorze.

### Wycofywanie się ze scenariuszy alternatywnych

arXiv:2401.13935 (styczeń 2024). Tradycyjne scenariusze alternatywne wymagają interwencji w odniesieniu do wrażliwego atrybutu – „czy decyzja zmieniłaby się, gdyby ta osoba była innej płci?”. Z prawnego punktu widzenia jest to problematyczne: w prawie klasyfikacyjnym nie można ingerować w chronione atrybuty.

Wycofywanie się ze scenariuszy alternatywnych odwraca kierunek: zamiast interweniować w sprawie atrybutu, zapytaj, jaka kombinacja rzeczywistych cech jednostki dałaby wynik alternatywny. To omija zarzut prawny.

### Pojednanie filozoficzne

ICLR Blogposts 2024. Mając w ręku wykres przyczynowy, spełnienie pewnych miar uczciwości grupowej pociąga za sobą sprawiedliwość kontrfaktyczną. Te trzy rodziny nie są ortogonalne; są to różne aspekty tej samej podstawowej struktury przyczynowej.

Nie rozwiązuje to twierdzeń o niemożliwości (nierówne stawki podstawowe w dalszym ciągu uniemożliwiają jednoczesną uczciwość grupową). Pokazuje jednak, że pozorna opozycja między „grupą” a „jednostką / kontrfaktem” jest częściowo skutkiem braku jednoznacznego określenia modelu przyczynowego.

### Gdzie to pasuje do fazy 18

Lekcja 20 to pomiar błędu systematycznego. Lekcja 21 to definicja sprawiedliwości. Lekcja 22 to prywatność (prywatność różnicowa). Lekcja 23 to znak wodny. Są to lekcje związane z alokacją, uzupełniające lekcje 7-11 dotyczące oszustwa.

## Użyj tego

`code/main.py` tworzy zabawkowy zbiór danych klasyfikacji binarnej z wrażliwym atrybutem i nierównymi stawkami podstawowymi. Oblicz parytet demograficzny, wyrównane szanse i równość dokładności użycia warunkowego w prostym klasyfikatorze. Zwróć uwagę na trzy metryki, które się nie zgadzają. Zastosuj ponowne ważenie parytetu demograficznego i obserwuj jego koszt w pozostałych dwóch przypadkach.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-fairness-criterion.md`. Biorąc pod uwagę twierdzenie lub zasadę uczciwości, określa, które kryterium jest wymagane, czy model może spełnić pozostałe kryteria w ramach deklarowanych nierównych stawek bazowych oraz od jakiego związku przyczynowego DAG zależy to roszczenie.

## Ćwiczenia

1. Uruchom `code/main.py`. Zgłoś metryki trzech grup na danych domyślnych. Zastosuj ponowne ważenie i ponowne zgłoszenie w oparciu o parytet demograficzny.

2. Zastosuj metodę Dworka i in. Wskaźnik uczciwości indywidualnej z 2012 r. wykorzystujący L2 w przypadku cech niewrażliwych. Podaj, ile par narusza Lipschitza przy stałej L=1.

3. Przeczytaj Kusnera i in. 2017. Skonstruuj prosty, dwufunkcyjny przyczynowy DAG do oceny punktacji wznowieniowej i zidentyfikuj warunek uczciwości kontrfaktycznej, który on sugeruje.

4. W dokumencie dotyczącym wycofywania się i scenariuszy alternatywnych z 2024 r. unika się interwencji w zakresie chronionych atrybutów. Opisz scenariusz, w którym ma to znaczenie dla zgodności z prawem.

5. W uzgodnieniu ICLR 2024 argumentuje się, że sprawiedliwość grupowa i sprawiedliwość kontrfaktyczna to aspekty tej samej struktury. Wybierz dwa z trzech kryteriów w `code/main.py` i podaj założenie przyczynowe, które sprawi, że będą one równoważne.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Parytet demograficzny | „równe stawki” | P(Y=1 | A=a) równe w grupach |
| Wyrównane szanse | „równe TPR/FPR” | Równe odsetki wyników prawdziwie dodatnich i fałszywie dodatnich we wszystkich grupach |
| Dokładność warunkowego użycia | „równe PPV/NPV” | Równe wartości predykcyjne we wszystkich grupach |
| Indywidualna sprawiedliwość | „Stan Lipschitza” | Podobne osoby dostają podobne decyzje |
| Sprawiedliwość kontrfaktyczna | „niezmienniczość zmian przyczynowych” | Decyzja niezmieniona w związku ze zmianą atrybutu alternatywnego |
| Wycofywanie się ze scenariusza alternatywnego | „wyjaśnij za pomocą faktów” | Kontrfaktyczne rozumowanie wstecz od wyniku, a nie dalej od atrybutu |
| Twierdzenie o niemożliwości | „konflikt trzech” | Chouldechova / KMR 2017: kryteria grupowe wzajemnie się wykluczające w ramach nierównych stawek podstawowych |

## Dalsze czytanie

- [Dwork i in. — Sprawiedliwość poprzez świadomość (arXiv:1104.3913)](https://arxiv.org/abs/1104.3913) — sprawiedliwość indywidualna
- [Kusner, Loftus, Russell, Silva — Sprawiedliwość kontrfaktyczna (arXiv:1703.06856)](https://arxiv.org/abs/1703.06856) — sprawiedliwość kontrfaktyczna
- [Chouldechova — Uczciwa prognoza o różnym wpływie (arXiv:1703.00056)](https://arxiv.org/abs/1703.00056) — niemożliwość
– [Backtracking Counterfactuals (arXiv:2401.13935)](https://arxiv.org/abs/2401.13935) — nowy paradygmat interwencji opartych na atrybutach chronionych