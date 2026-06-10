# Planowanie za pomocą HTN i wyszukiwania ewolucyjnego

> Planowanie symboliczne sprawdza się w scenariuszach, w których wymagane jest udowodnienie poprawności planu. Ewolucyjne wyszukiwanie kodu ma zastosowanie tam, gdzie funkcję przystosowania (fitness function) można zweryfikować maszynowo. Rozwiązania ChatHTN (2025) oraz AlphaEvolve (2025) pokazują możliwości, jakie niesie ze sobą połączenie tych podejść z LLM.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 02 (ReWOO i Plan-and-Execute)
**Czas:** ~75 minut

## Cele nauczania

- Wyjaśnij działanie hierarchicznych sieci zadań (HTN): zadania, metody, operatory, warunki wstępne oraz efekty.
- Opisz hybrydową pętlę ChatHTN – wyszukiwanie symboliczne z zapasowym dekomponowaniem za pomocą LLM (fallback).
- Wyjaśnij pętlę ewolucyjną w AlphaEvolve i powód, dla którego działa ona wyłącznie z programowym ewaluatorem.
- Zaimplementuj w Pythonie (stdlib) uproszczony planer HTN oraz ewolucyjne wyszukiwanie wyrażeń.

## Problem

Frameworki takie jak ReWOO (Lekcja 02), Plan-and-Execute oraz ReAct pokrywają większość typowych scenariuszy planowania agentów. Istnieją jednak dwie klasy problemów, z którymi sobie nie radzą:

1. **Plany z formalnie dowiedzioną poprawnością.** Planowanie tras lotniczych, zgodne z przepisami przepływy pracy (compliance) – plan musi być z założenia bezbłędny. Generowane przez LLM plany, w których może pojawić się halucynacja choćby jednego kroku, są nieakceptowalne.
2. **Optymalizacje z maszynowo weryfikowalną funkcją celu (przystosowania).** Mnożenie macierzy, heurystyki szeregowania zadań, optymalizacje kompilatora – celem nie jest po prostu znalezienie „prawidłowego planu”, ale znalezienie planu optymalnego (najlepszego).

Planowanie HTN oraz podejście AlphaEvolve rozwiązują te dwa różne problemy. Oba systemy wykorzystują LLM jako komponenty wspomagające, a nie jako całkowite zastępstwo logiki sterowania.

## Koncepcja

### Hierarchiczne sieci zadań (Hierarchical Task Networks - HTN)

Komponenty HTN:

- **Zadania (Tasks)** – złożone (podlegające dekompozycji) i pierwotne/prymitywne (bezpośrednio wykonywalne).
- **Metody (Methods)** – sposoby rozkładania zadania złożonego na podzadania wraz z określonymi warunkami wstępnymi.
- **Operatory (Operators)** – działania pierwotne z określonymi warunkami wstępnymi i efektami.
- **Stan (State)** – zbiór faktów opisujących środowisko.

Proces planowania: mając dany cel i stan początkowy, znajdź dekompozycję na operatory pierwotne, których warunki wstępne są kolejno spełniane.

Podejście HTN powstało na długo przed LLM i nadal stanowi standard dla planów o formalnie dowiedzionej poprawności.

### ChatHTN (Gopalakrishnan i in., 2025)

ChatHTN (arXiv:2505.11814) łączy symboliczne planowanie HTN z zapytaniami do LLM:

1. Podejmij próbę dekompozycji bieżącego zadania złożonego na podstawie istniejących metod.
2. Jeśli żadna z metod nie ma zastosowania, zapytaj LLM: „w jaki sposób dokonałbyś dekompozycji zadania `task` w stanie `s`?”
3. Przetłumacz odpowiedź LLM na listę potencjalnych podzadań.
4. Zweryfikuj wyniki na podstawie schematu operatora i odrzuć nieprawidłowe dekompozycje.
5. Powtórz krok.

Główna teza publikacji: każdy wygenerowany plan ma formalnie dowiedzioną poprawność, ponieważ sugestie LLM są traktowane wyłącznie jako propozycje dekompozycji podlegające walidacji, a nie bezpośrednie instrukcje wykonawcze. Warstwa symboliczna gwarantuje poprawność, podczas gdy LLM rozszerza bazę dostępnych metod.

Nauka online (online learning - OpenReview `gwYEDY9j2x`, kontynuacja z 2025 r.) wprowadza moduł uczący się, który uogólnia dekompozycje zaproponowane przez LLM, zmniejszając częstotliwość odpytywania modelu o nawet 75%.

### AlphaEvolve (Novikov i in., 2025)

AlphaEvolve (arXiv:2506.13131, DeepMind, czerwiec 2025) to zupełnie inne podejście: ewolucyjne wyszukiwanie kodu opracowane przez zespół Gemini 2.0 Flash/Pro.

Przebieg pętli:

1. Rozpocznij od programu bazowego oraz ewaluatora (zwracającego wynik dopasowania/fitness).
2. Zespół agentów LLM proponuje mutacje kodu.
3. Uruchom zmutowany kod w ewaluatorze.
4. Zachowaj najlepsze rozwiązania i poddaj je kolejnym mutacjom.

Osiągnięte sukcesy:

- Pierwsza od 56 lat poprawa algorytmu Strassena dla mnożenia macierzy zespolonych 4x4 (redukcja do 48 mnożeń skalarnych).
- Oszczędność 0,7% mocy obliczeniowej Google dzięki zoptymalizowaniu heurystyk szeregowania zadań systemu Borg.
- Przyspieszenie działania FlashAttention o 32% przy skrajnych obciążeniach.

Kluczowe ograniczenie: funkcja przystosowania (fitness function) musi być weryfikowalna maszynowo. Ewolucyjne poszukiwanie rozwiązań opisywanych prozą nie wykazuje zbieżności.

### Porównanie podejść

| Klasa problemu | Rozwiązanie | Rationale |
|----------|-----|-----|
| Planowanie ze sztywnymi regułami | HTN + ChatHTN | Dowiedziona poprawność planu |
| Optymalizacja kodu / kompilatora | AlphaEvolve | Weryfikowalna maszynowo funkcja dopasowania |
| Wieloetapowe wykonanie zadań | ReAct / ReWOO | LLM w pętli decyzyjnej, brak formalnych gwarancji |
| Ulepszanie kodu na podstawie testów | AlphaEvolve | Testy jednostkowe jako ewaluator |
| Automatyzacja procesów zgodności (policy) | HTN | Warunki wstępne opisują reguły biznesowe |

### Potencjalne problemy i wady wzorców

- **HTN bez zdefiniowanych operatorów.** Bez schematów warunków wstępnych oraz efektów gwarancje poprawności przestają istnieć. Mechanizm ChatHTN wymaga schematu operatorów do walidacji i odrzucania błędnych propozycji LLM.
- **AlphaEvolve bez obiektywnego ewaluatora.** Odpytywanie LLM o to, „czy kod jest lepszy”, nie stanowi poprawnej funkcji przystosowania. Ewaluator musi działać szybko i w sposób deterministyczny.
- **Nadmierna inżynieria (overengineering).** Większość zadań agentowych nie wymaga tak złożonych struktur. W pierwszej kolejności zaleca się stosowanie prostszych pętli ReAct lub ReWOO.

## Zbuduj to

Plik `code/main.py` implementuje dwa uproszczone przykłady:

- Planer HTN w Pythonie (stdlib) z operatorami, metodami, warunkami wstępnymi, efektami oraz mechanizmem `LLMFallback`, który uruchamia się, gdy żadna ze zdefiniowanych metod nie pasuje do zadania złożonego. Moduł „LLM” został uproszczony za pomocą skryptu dekomponującego, co pozwala na działanie planera w trybie offline.
- Ewolucyjne wyszukiwanie wyrażeń arytmetycznych w Pythonie (stdlib): generowanie formuł matematycznych minimalizujących wartość `|f(x) - target|` na zbiorze testowym. Ewaluator działa w sposób w pełni deterministyczny.

Uruchomienie:

```
python3 code/main.py
```

Generowane logi (trace) pokazują dekompozycję zadania przez planer HTN (z zapasowym użyciem LLM w trakcie procesu) oraz przebieg pętli ewolucyjnej zbiegającej się do oczekiwanego wyrażenia.

## Użyj tego

- **Planery HTN** – `pyhop`, `SHOP3` lub własne implementacje w celu wymuszania reguł specyficznych dla danej domeny.
- **ChatHTN** – kod badawczy; wzorzec połączenia planowania symbolicznego z zapasowym LLM można łatwo zintegrować z dowolnym planerem HTN.
- **AlphaEvolve** – koncepcja DeepMind; wzorzec (zespół agentów + ewaluator) jest powtarzalny. Na rynku pojawiają się projekty takie jak OpenEvolve oraz inne rozwiązania open-source.
- **Frameworki agentowe** – żaden z wiodących frameworków nie oferuje jeszcze wbudowanego wsparcia dla HTN czy AlphaEvolve. Należy implementować je jako subagenty lub procesy tła.

## Wyślij to

Plik `outputs/skill-hybrid-planner.md` tworzy szkielet hybrydowego planera (HTN lub ewolucyjnego) z precyzyjnie określonym zakresem odpowiedzialności LLM.

## Ćwiczenia

1. Rozbuduj planer HTN o mechanizm nawrotów (backtracking): w przypadku niepowodzenia warunku końcowego operatora w czasie wykonywania, wycofaj się i przetestuj kolejną dostępną metodę.
2. Zaimplementuj pamięć podręczną (cache) metod LLM w ChatHTN: po dokonaniu przez LLM dekompozycji zadania `T` w stanie `P`, zapisz ten schemat. Przy kolejnym identycznym wywołaniu skorzystaj z pamięci podręcznej przed odpytaniem LLM.
3. Zastąp uproszczony ewaluator wyszukiwania ewolucyjnego rzeczywistym zestawem testów. Wygeneruj funkcję sortującą przechodzącą 20 przypadków testowych i przeanalizuj liczbę generacji potrzebną do osiągnięcia zbieżności.
4. Zapoznaj się z założeniami projektowymi ewaluatora AlphaEvolve. Zaprojektuj ewaluator dla wybranej dziedziny (np. optymalizacja zapytań SQL, walidacja konfiguracji YAML).
5. Połącz oba podejścia: użyj HTN do dekompozycji złożonego zadania na podzadania, a następnie zastosuj wyszukiwanie ewolucyjne do optymalizacji operatorów pierwotnych dla każdego z podzadań. Przeanalizuj wady i zalety takiego rozwiązania.

## Kluczowe terminy

| Termin | Co mówią ludzie | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| HTN | „Hierarchiczny planer” | Dekompozycja zadań z użyciem operatorów, warunków wstępnych i efektów |
| Metoda | „Reguła rozkładu” | Sposób podziału zadania złożonego na podzadania |
| Operator | „Operator pierwotny / prymitywny” | Konkretny krok wykonawczy z określonym warunkiem wstępnym i efektem |
| ChatHTN | „LLM + HTN” | Planer symboliczny odpytujący LLM w przypadku braku pasującej metody |
| AlphaEvolve | „Poszukiwanie kodu ewolucyjnego” | Wielu agentów LLM mutuje kod, a deterministyczny ewaluator selekcjonuje najlepsze rozwiązania |
| Funkcja fitness | „Ewaluator” | Deterministyczna, maszynowo weryfikowalna ocena poprawności lub wydajności działania |
| Nauka online | „Rozkład LLM w pamięci podręcznej” | Zapisywanie i uogólnianie dekompozycji LLM w celu redukcji liczby zapytań do modelu |

## Dalsze czytanie

- [Gopalakrishnan i in., ChatHTN (arXiv:2505.11814)](https://arxiv.org/abs/2505.11814) — połączenie planowania symbolicznego z zapasowym LLM
- [Novikov et al., AlphaEvolve (arXiv:2506.13131)](https://arxiv.org/abs/2506.13131) — ewolucyjne wyszukiwanie kodu z mutacjami generowanymi przez LLM
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — wytyczne dotyczące wyboru między złożonym planerem a prostą pętlą wykonawczą
