# Benchmarki: SWE-bench, GAIA, AgentBench

> Trzy kluczowe benchmarki stanowiące punkt odniesienia do oceny agentów. SWE-bench weryfikuje zdolność do naprawiania (łatania) kodu. GAIA testuje ogólne wykorzystanie narzędzi w zróżnicowanych scenariuszach. AgentBench ocenia wnioskowanie w wielu środowiskach. Zapoznaj się z ich strukturą, problemem zanieczyszczenia danych (contamination) oraz tym, czego te testy nie mierzą.

**Typ:** Ucz się
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 06 (Użycie narzędzi)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnić pojęcie zestawu testów SWE-bench (FAIL_TO_PASS) i dlaczego stanowi on kluczowe kryterium w testach jednostkowych.
- Wyjaśnić, czym jest SWE-bench Verified (stworzony przez OpenAI zestaw 500 zadań) i jakie błędy eliminuje.
- Opisać architekturę benchmarku GAIA: zadania proste dla ludzi, lecz trudne dla AI, podzielone na trzy poziomy trudności.
- Wymienić osiem środowisk testowych wchodzących w skład AgentBench oraz wskazać główną barierę dla modeli open source.
- Podsumować wnioski z analizy zanieczyszczenia danych w badaniu SWE-bench+ oraz ich konsekwencje.

## Problem

Rankingi (leaderboards) wskazują jedynie, który model radzi sobie najlepiej w danym teście porównawczym. Nie informują jednak o tym:

- Czy benchmark nie jest zanieczyszczony (np. obecność rozwiązań w danych treningowych, wycieki z zestawów testowych).
- Czy test mierzy dokładnie te aspekty, na których Ci zależy (np. pisanie kodu, przeglądanie sieci vs zadania ogólne).
- Czy mechanizm oceny (evaluator) jest wiarygodny (np. analiza drzewa AST, testy spójności stanu, ręczny przegląd).

Zanim zaczniesz analizować wyniki liczbowe, zapoznaj się z trzema głównymi benchmarkami referencyjnymi i typowymi problemami, które mogą w nich występować.

## Koncepcja

### SWE-bench (Jimenez i in., ICLR 2024)

- Zawiera 2294 rzeczywistych problemów zgłoszonych na GitHubie w 12 popularnych repozytoriach napisanych w Pythonie.
- Agent otrzymuje: stan bazy kodu bezpośrednio przed wprowadzeniem poprawki oraz opis problemu w języku naturalnym.
- Agent generuje: poprawkę (patch).
- Ewaluator: aplikuje wygenerowaną poprawkę i uruchamia testy jednostkowe z repozytorium. Poprawka musi sprawić, że testy z grupy FAIL_TO_PASS (które wcześniej zgłaszały błąd, a po zmianie powinny przejść pomyślnie) zakończą się powodzeniem, nie powodując przy tym regresji w testach z grupy PASS_TO_PASS (które poprawnie przechodziły już wcześniej).

Projekt SWE-agent (Yang i in., 2024) osiągnął skuteczność na poziomie 12,5% w momencie publikacji, koncentrując się na interfejsach komunikacji agent-komputer (dedykowane komendy edycji plików, składnia wyszukiwania zoptymalizowana pod kątem LLM).

### SWE-bench Verified

Zestaw opublikowany przez OpenAI w sierpniu 2024 roku, zawierający podzbiór 500 zadań zweryfikowanych przez ekspertów. Eliminuje on niejednoznaczne opisy problemów, niestabilne testy jednostkowe (flaky tests) oraz zadania z niejasnymi kryteriami zaliczenia. Stanowi obecnie główny punkt odniesienia przy ocenie, czy dany agent potrafi generować poprawne poprawki kodu w rzeczywistych warunkach.

### Zanieczyszczenie danych (Contamination)

- Ponad 94% problemów wykorzystanych w SWE-bench powstało przed okresem odcięcia wiedzy (knowledge cutoff) większości modeli.
- **SWE-bench+** wykazał, że w przypadku 32,67% udanych napraw kod rozwiązania wyciekł bezpośrednio w opisie problemu (model miał wgląd w poprawkę), a kolejne 31,08% budziło wątpliwości ze względu na zbyt niski poziom pokrycia testami.
- Wersja Verified jest lepiej zweryfikowana, ale wciąż nie jest całkowicie wolna od zanieczyszczeń.

Wnioski praktyczne: model uzyskujący 50% skuteczności w klasycznym SWE-bench może osiągnąć jedynie 35% w SWE-bench+. Chcąc zachować rzetelność wyników w testach SWE-bench, należy raportować oba te wskaźniki.

### GAIA (Mialon i in., listopad 2023)

- Zawiera 466 pytań, z czego 300 jest zastrzeżonych w celu ewaluacji na prywatnym rankingu na platformie Hugging Face.
- Założenie projektowe: zadania proste dla człowieka (średnio 92% poprawnych odpowiedzi), lecz niezwykle trudne dla sztucznej inteligencji (np. GPT-4 z wtyczkami osiągał zaledwie 15%).
- Wverifykuje umiejętności logicznego wnioskowania, obsługi wielu modalności, korzystania z sieci i zewnętrznych narzędzi.
- Podział na trzy poziomy trudności, gdzie Poziom 3 wymaga budowania długich łańcuchów wywołań narzędzi i przetwarzania danych w różnych formatach.

GAIA jest doskonałym narzędziem do oceny ogólnych zdolności agentycznych. Nie należy jej mylić z benchmarkami przeznaczonymi ściśle do testowania kodu.

### AgentBench (Liu i in., ICLR 2024)

- Składa się z 8 środowisk testowych obejmujących kodowanie (Bash, bazy danych, grafy wiedzy), gry tekstowe (Alfworld, LTP), interakcje sieciowe (WebShop, Mind2Web) oraz zadania otwarte.
- Długie, wieloturowe interakcje (~4-13 tys. tur w poszczególnych podziałach).
- Kluczowy wniosek: długoterminowe wnioskowanie, podejmowanie decyzji i ścisłe przestrzeganie złożonych instrukcji stanowią największą barierę uniemożliwiającą modelom open source (OSS LLM) dorównanie komercyjnym odpowiednikom.

### Czego te benchmarki nie mierzą

- Rzeczywistych kosztów operacyjnych (zużycie tokenów, czas wykonania).
- Bezpieczeństwa i stabilności działania w niesprzyjających lub wrogich warunkach (adversarial environments).
- Skuteczności w konkretnej domenie biznesowej (do tego służą własne ewaluacje – Lekcja 30).
- Rzadkich awarii brzegowych (benchamarki podają uśrednione wyniki, podczas gdy na produkcji kluczowy bywa najgorszy 1% przypadków - tail failures).

### Najczęstsze błędy w benchmarkowaniu

- **Skupianie się na jednej liczbie.** Informacja, że skuteczność wynosi 50%, mówi znacznie mniej niż analiza rozkładu kosztów (P50/P75/P95) oraz liczby kroków wykonanych przez agenta.
- **Niejasne raportowanie wyników.** Podawanie wyników SWE-bench bez doprecyzowania, czy chodzi o wersję Verified lub bez odniesienia do analizy zanieczyszczeń SWE-bench+, może wprowadzać w błąd.
- **Traktowanie benchmarku jako celu samego w sobie (Prawo Goodharta).** Optymalizacja systemu wyłącznie pod kątem konkretnych pytań testowych drastycznie obniża jego realną przydatność na produkcji.

## Przykład implementacji

Plik `code/main.py` implementuje uproszczony framework testowy na wzór SWE-bench:

- Zdefiniowano 3 syntetyczne zadania polegające na poprawianiu błędów.
- Zaimplementowano uproszczonego „agenta” proponującego modyfikacje kodu.
- Zaimplementowano moduł uruchamiania testów weryfikujący kryteria `FAIL_TO_PASS` (czy błąd został naprawiony) oraz `PASS_TO_PASS` (czy nie wprowadzono regresji).
- Dodano klasyfikator trudności zadań inspirowany strukturą GAIA.

Uruchomienie:

```
python3 code/main.py
```

Wyniki wyjściowe pokazują wskaźnik rozwiązanych zadań w podziale na stopień trudności i ilustrują mechanizm działania ewaluatora.

## Podsumowanie zastosowań

- **SWE-bench Verified** w przypadku ewaluacji agentów programistycznych. Zawsze raportuj wyniki z tej wersji.
- **GAIA** do testowania agentów ogólnego przeznaczenia. Warto korzystać z oficjalnego, prywatnego zestawu testowego.
- **AgentBench** w celu porównania sprawności agentów w zróżnicowanych ekosystemach.
- **Dedykowane testy domenowe** (Lekcja 30) odzwierciedlające realne przypadki użycia w Twojej aplikacji.

## Zadanie wdrożeniowe

Plik `outputs/skill-benchmark-harness.md` zawiera wytyczne dotyczące budowy środowiska testowego na wzór SWE-bench dla dowolnego zestawu zadań kodowych, z automatyczną weryfikacją kryteriów FAIL_TO_PASS / PASS_TO_PASS.

## Ćwiczenia praktyczne

1. Dostosuj uproszczone środowisko testowe, aby działało na rzeczywistym repozytorium kodu. Przygotuj 3 testy typu FAIL_TO_PASS dla znanych, historycznych błędów.
2. Dodaj metrykę zliczającą wykonane kroki. Zmierz, ile kroków potrzebuje agent na rozwiązanie każdego z trzech zadań.
3. Przeczytaj dokumentację SWE-bench+. Zaimplementuj prosty mechanizm wykrywania wycieku rozwiązań (np. poprzez dopasowanie fragmentów kodu z poprawki do tekstu opisu problemu).
4. Pobierz przykładowe zadanie z publicznego zestawu GAIA. Przeanalizuj krok po kroku, jak powinien zachować się agent klasy GPT-4. Jakich narzędzi potrzebuje?
5. Zapoznaj się z podziałem środowisk w AgentBench. Które z nich najbardziej przypomina obszar działania Twojego produktu? Jaki jest obecny stan zaawansowania (SOTA) w tej kategorii?

## Kluczowe terminy

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| SWE-bench | „Ewaluacja agentów programistycznych” | Zestaw 2294 problemów z GitHub; poprawka musi pomyślnie przejść testy z grupy FAIL_TO_PASS |
| SWE-bench Verified | „Zweryfikowany zestaw SWE” | Wyselekcjonowany przez ekspertów podzbiór 500 zadań eliminujący niejednoznaczności |
| FAIL_TO_PASS | „Weryfikacja poprawki” | Testy jednostkowe, które przed modyfikacją kodu zgłaszały błąd, a po jego wdrożeniu muszą zakończyć się sukcesem |
| PASS_TO_PASS | „Testy regresji” | Testy jednostkowe, które przechodziły pomyślnie przed zmianami i muszą wciąż kończyć się sukcesem po wdrożeniu poprawki |
| GAIA | „Ogólny benchmark agentyczny” | Zestaw 466 złożonych pytań weryfikujących korzystanie z wielu narzędzi (proste dla ludzi, trudne dla AI) |
| AgentBench | „Testy wielośrodowiskowe” | Zestaw testów obejmujący 8 różnych środowisk; wymaga logicznego wnioskowania w długim horyzoncie czasowym |
| Zanieczyszczenie danych | „Wyciek danych testowych” | Sytuacja, w której dane lub rozwiązania z zadań testowych znalazły się w zbiorze treningowym LLM |
| SWE-bench+ | „Audyt zanieczyszczenia danych” | Badanie, które wykazało obecność rozwiązań bezpośrednio w opisach dla 32,67% zadań w klasycznym SWE-bench |

## Dalsze czytanie

- [Jimenez i in., SWE-bench (arXiv:2310.06770)](https://arxiv.org/abs/2310.06770) — oryginalny test porównawczy
- [OpenAI, SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) — wyselekcjonowany podzbiór
- [Mialon i in., GAIA (arXiv:2311.12983)](https://arxiv.org/abs/2311.12983) — ogólny punkt odniesienia
- [Liu i in., AgentBench (arXiv:2308.03688)](https://arxiv.org/abs/2308.03688) — pakiet wielośrodowiskowy
