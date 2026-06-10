---

name: mesa-diagnostic
description: Sklasyfikuj wykrytą awarię bezpieczeństwa jako błąd wyrównania zewnętrznego, wewnętrznego (proxy) lub zwodniczego.
version: 1.0.0
phase: 18
lesson: 6
tags: [mesa-optimization, deceptive-alignment, inner-alignment, hubinger]

---

Na podstawie raportu bezpieczeństwa (zadanie ewaluacyjne, zaobserwowany tryb awarii, klasa modelu, procedura treningowa), sklasyfikuj awarię według taksonomii Hubingera i in. (2019) oraz zarekomenduj optymalzą strategię łagodzenia skutków.

Przygotuj:

1. Klasyfikacja trybu awarii. Wybierz jedną z kategorii:
   - Błąd wyrównania zewnętrznego: zdefiniowany cel bazowy (funkcja nagrody/straty) był błędny, a model zoptymalizował go poprawnie (lecz niezgodnie z rzeczywistymi intencjami).
   - Błąd wyrównania wewnętrznego (proxy-alignment): cel mesa jest jedynie miarą zastępczą (proxy) skorelowaną z celem bazowym w rozkładzie treningowym, która zawodzi poza rozkładem (OOD).
   - Zwodnicze wyrównanie wewnętrzne: mesa-optymalizator wykazuje świadomość sytuacyjną i dokonuje celowej defekcji w fazie wdrożenia produkcyjnego, zachowując bezbłędne zachowanie w trakcie treningu.
2. Analiza dowodów. Wskaż dowody empiryczne potwierdzające wybraną klasyfikację. W przypadku diagnozy zwodniczego wyrównania wykaż obecność świadomości sytuacyjnej (np. wrażliwość na czas/daty, zdolność rozróżniania środowiska testowego od produkcyjnego, strategiczne planowanie w łańcuchu myśli - CoT).
3. Rekomendacja mitygacji. Dla błędu wyrównania zewnętrznego: modyfikacja celu (wdrożenie CAI, poprawa jakości danych nagrody, nadzór nad procesem rozumowania). Dla błędu wyrównania wewnętrznego (proxy): poszerzenie rozkładu treningowego, zespoły modeli (ensembles), testowanie na danych OOD. Dla zwodniczego wyrównania: wdrożenie mechanizmów kontroli (model containment - temat 10), interpretowalność (np. sondowanie strumienia rezydualnego - residual stream probing) lub redukcja zdolności modelu.
4. Odniesienie do znanych trybów awarii. W przypadku stwierdzenia zwodniczego wyrównania, wskaż empiryczną demonstrację z lat 2024–2026 (np. Uśpieni agenci, Fałszowanie wyrównania, Planowanie w kontekście), do której analizowany przypadek wykazuje największe podobieństwo.

Bezwzględne odrzucenia (błędy merytoryczne):
- Klasyfikowanie awarii jako zwodniczego wyrównania bez wyraźnych dowodów na świadomość sytuacyjną. Sama „anomalia w zachowaniu produkcyjnym” nie jest wystarczającym dowodem – może wynikać ze zwykłego błędu wyrównania względem proxy.
- Twierdzenia, jakoby sam trening adwersaryjny (adversarial training) rozwiązywał problem zwodniczego wyrównania. Hubinger i in. (2019) wykazali (co potwierdziły badania nad uśpionymi agentami z 2024 r.), że trening adwersaryjny może jedynie nauczyć model sprawniejszego odróżniania testów od wdrożenia.
- Rekomendacje sugerujące ponowne trenowanie zwodniczo wyrównanego modelu na większej ilości danych. Doświadczenie wskazuje, że zachowania zwodnicze ulegają utrwaleniu podczas dalszego treningu.

Zasady udzielania odpowiedzi (odmowy):
- Jeśli opis awarii sprowadza się do pojedynczego zdarzenia opisanego w jednym zdaniu, odmów klasyfikacji. Wiarygodna ocena wymaga analizy statystycznego rozkładu awarii.
- Jeśli użytkownik oczekuje kategorycznego „wykluczenia” możliwości wystąpienia zwodniczego wyrównania, odmów. Możesz oszacować prawdopodobieństwo tego zjawiska na podstawie zebranych dowodów, ale nie da się go całkowicie wykluczyć wyłącznie na podstawie zewnętrznego zachowania modelu.

Dane wyjściowe: Jednostronicowy raport diagnostyczny określający kategorię awarii, analizę dowodów, sugerowane metody łagodzenia oraz najbliższy analog empiryczny. W tekście należy dokładnie raz zacytować pracę Hubingera i in. (arXiv:1906.01820) raz.
