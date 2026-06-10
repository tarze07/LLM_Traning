# AlphaEvolve — ewolucyjni agenci kodujący

> Połącz model kodowania z pętlą ewolucyjną i ewaluatorem sprawdzalnym maszynowo. Pozwól, aby pętla działała wystarczająco długo. Odkrywa ona procedurę mnożenia macierzy zespolonych 4x4, która wykorzystuje 48 mnożeń przez skalar — co stanowi pierwsze ulepszenie w stosunku do metody Strassena od 56 lat. Znajduje także obowiązującą w całym Google heurystykę planowania Borg, która pozwala odzyskać około 0,7% mocy obliczeniowej klastra w środowisku produkcyjnym. Architektura systemu jest celowo prosta (wręcz nudna). Sukcesy wynikają z rygorystyczności ewaluatora.

**Typ:** Ucz się
**Języki:** Python (biblioteka standardowa, prosty symulator pętli ewolucyjnej)
**Wymagania wstępne:** Faza 15 · 01 (dopasowanie w długim horyzoncie), Faza 15 · 02 (rozumowanie samouka)
**Czas:** ~60 minut

## Problem

Duże modele językowe potrafią pisać kod. Algorytmy ewolucyjne mogą przeszukiwać przestrzeń kodu. Obie te metody testowano osobno przez dziesięciolecia i obie osiągnęły swój sufit. Sufitem LLM są konfabulacje: model pisze wiarygodnie brzmiący kod, który nie robi tego, co deklaruje. Pułapem algorytmów ewolucyjnych jest koszt wyszukiwania: przypadkowe mutacje w składni rzadko dają programy dające się skompilować, nie mówiąc już o lepszych od bazowych.

AlphaEvolve (Novikov i in., DeepMind, arXiv:2506.13131, czerwiec 2025) łączy te podejścia. LLM proponuje ukierunkowane zmiany w bazie danych programów; automatyczny ewaluator ocenia każdy wariant, a warianty o wysokich wynikach stają się rodzicami dla przyszłych pokoleń (iteracji). LLM bierze na siebie kosztowny etap pisania poprawnego składniowo kodu, natomiast ewaluator wychwytuje konfabulacje. Pętla działa przez wiele godzin lub tygodni.

Przedstawione wyniki: mnożenie 4x4 macierzy zespolonych za pomocą 48 skalarów (wartość graniczna Strassena z 1969 roku wynosiła 49), heurystyka planowania Borga w środowisku produkcyjnym Google, przyspieszenie jądra FlashAttention o 32,5% oraz poprawa przepustowości szkolenia modelów Gemini.

Architektura ta działa, ponieważ ewaluator można zweryfikować maszynowo. Nie sprawdza się ona tam, gdzie takiego ewaluatora brakuje. Ta asymetria stanowi ważną lekcję.

## Koncepcja

### Pętla ewolucyjna

1. Zacznij od programu zalążkowego `P_0`, który jest poprawny, ale nieoptymalny.
2. Utrzymuj bazę danych wariantów programów, z których każdy jest oceniany przez ewaluator.
3. Wybierz jednego lub więcej rodziców (parent programs) z bazy danych (w stylu MAP-Elites lub opartym na wyspach).
4. Poproś LLM (Gemini Flash dla generowania wielu kandydatów, Gemini Pro dla trudniejszych problemów) o stworzenie zmodyfikowanego wariantu rodzica.
5. Skompiluj, uruchom i oceń wariant za pomocą wydzielonego ewaluatora.
6. Wstaw go do bazy danych, indeksując według wyniku (score) i wektora cech.
7. Powtórz.

Liczą się dwa istotne szczegóły. Po pierwsze, LLM otrzymuje więcej informacji niż tylko program nadrzędny – zazwyczaj są to najlepsze warianty z bazy danych, podpis (dane wejściowe i wyjściowe) ewaluatora oraz krótki opis zadania. Zadaniem modelu jest zaproponowanie ukierunkowanej zmiany, która mogłaby poprawić wynik. Po drugie, baza danych ma odpowiednią strukturę (siatka MAP-Elites, model wyspowy), dzięki czemu pętla bada różnorodne rozwiązania, a nie tylko obecnego lidera.

### Dlaczego ewaluator nie podlega dyskusji

Wszystkie sukcesy AlphaEvolve pochodzą z dziedzin, w których ewaluator jest szybki, deterministyczny i odporny na manipulacje (hard to game):

- **Algorytm mnożenia macierzy**: test jednostkowy, który mnoży macierze i sprawdza równość bit po bicie.
- **Heurystyka planowania Borga**: symulator klasy produkcyjnej, który odtwarza historyczne obciążenie klastra i mierzy zmarnowane moce obliczeniowe.
- **Jądro FlashAttention**: test poprawności oraz test porównawczy (benchmark) rzeczywistego czasu wykonania na fizycznym sprzęcie.
- **Przepustowość treningu Gemini**: mierzony czas trwania kroku GPU (sekundy na krok).

W każdym z tych przypadków ewaluator wyłapuje błędy LLM, które w przeciwnym razie zdominowałyby proces: konfabulowane twierdzenia o poprawności, deklaracje o wydajności, które nie przekładają się na rzeczywisty sprzęt, oraz błędy dla przypadków brzegowych (edge cases). Jeśli usuniemy ewaluator, pętla zacznie optymalizować kod wyłącznie pod kątem jego estetyki.

### Hakowanie nagród to druga strona medalu

Ewolucja optymalizuje system pod kątem dokładnie tych kryteriów, które mierzy ewaluator. Jeśli ewaluator jest niedoskonały, pętla natychmiast znajdzie tę lukę. W niezweryfikowanej domenie pętla zoptymalizuje powierzchowne cechy (surface features), a nie zamierzone zachowanie. Zespół DeepMind wyraźnie to zaznacza w publikacji: sukcesy AlphaEvolve przenoszą się tylko na te domeny, w których rygor ewaluatorów odpowiada ambicjom wyszukiwania.

Konkretne przykłady hakowania nagród (reward hacking) z lat 2025–2026 w pętlach wyszukiwania kodu:

- Cele optymalizacji nagradzające krótki „czas wykonania” doprowadziły do generowania pustych rozwiązań, które natychmiast się kończyły.
- Wskaźniki poprawności nagradzające wyniki na testach doprowadziły do zapamiętywania testów i nadmiernego dopasowania (overfittingu).
- Wskaźniki „jakości kodu” nagradzały usuwanie komentarzy i zmianę nazw zmiennych bez wprowadzania zmian semantycznych.

Rozwiązanie w AlphaEvolve: zastosowanie wydzielonego ewaluatora (holdout evaluator), którego LLM nigdy nie widział, z danymi wejściowymi generowanymi w czasie testu. Nawet przy takim zabezpieczeniu DeepMind zaleca dokładną ręczną weryfikację każdego proponowanego wdrożenia.

### Dlaczego połączenie LLM i wyszukiwania przewyższa pojedyncze metody

LLM potrafi generować możliwe do skompilowania, semantycznie poprawne modyfikacje. Klasyczny algorytm genetyczny (GA) stosujący losowe mutacje w pliku Pythona o długości 2000 linii niemal zawsze wygeneruje błędy składniowe. LLM koncentruje się na wyszukiwaniu rozwiązań w prawdopodobnym sąsiedztwie (zmienia jedną funkcję zamiast losowych bajtów), co radykalnie zmniejsza liczbę niepotrzebnych wywołań ewaluatora.

Ewaluator z kolei skutecznie wyłapuje konfabulacje LLM. Modele językowe mogą z pełnym przekonaniem twierdzić, że funkcja „ma złożoność O(n log n)”, podczas gdy w rzeczywistości wynosi ona O(n^2) – rzeczywisty pomiar czasu wykonania rozstrzyga tę kwestię jednoznacznie.

### Gdzie AlphaEvolve mieści się w zestawieniu systemów

| System | Generator | Ewaluator | Domena | Przykładowy sukces |
|---|---|---|---|---|
| AlphaEvolve | Gemini | poprawność + benchmark | algorytmy, jądra, harmonogramy | mnożenie macierzy 4x4 za pomocą 48 operacji |
| FunSearch (DeepMind, 2023) | PaLM / Codex | poprawność | matematyka kombinatoryczna | wyznaczanie dolnych granic |
| AI Scientist v2 (Sakana, L5) | GPT / Claude | krytyka LLM + eksperyment | badania ML | artykuł na warsztaty ICLR |
| Maszyna Darwina Gödla (L4) | szkielet agenta | SWE-bench / Polyglot | kod agenta | wzrost na SWE-bench z 20% do 50% |

Wszystkie cztery systemy to odmiany tego samego przepisu: generator plus ewaluator zorganizowane w pętlę. Różnice polegają na tym, co i jak rygorystycznie ocenia ewaluator.

## Użyj tego

Skrypt `code/main.py` implementuje minimalną pętlę podobną do AlphaEvolve dla prostego problemu regresji symbolicznej. Rola „LLM” jest tu symulowana przez standardowy generator, który proponuje małe mutacje składniowe w programie obliczającym funkcję docelową. „Ewaluator” mierzy średni błąd kwadratowy na wydzielonych punktach testowych.

Zaobserwuj:

- Jak najlepszy wynik poprawia się z pokolenia na pokolenie.
- Jak siatka MAP-Elites utrzymuje różnorodność rozwiązań, zapobiegając zbieganiu pętli do lokalnego minimum.
- W jaki sposób usunięcie wydzielonego testu (flaga `--no-holdout`) prowadzi do drastycznego nadmiernego dopasowania pętli.

## Wdrożenie

Szablon `outputs/skill-evaluator-rigor-audit.md` stanowi warunek konieczny do rozważenia pętli w stylu AlphaEvolve w nowej domenie: pozwala ocenić, czy Twój ewaluator rzeczywiście wychwytuje kluczowe błędy.

## Ćwiczenia

1. Uruchom `code/main.py`. Przeanalizuj trajektorię najlepszego wyniku. Wyłącz wydzielony ewaluator (flaga `--no-holdout`) i uruchom ponownie. Określ ilościowo stopień nadmiernego dopasowania.

2. Przeczytaj sekcję 3 artykułu AlphaEvolve dotyczącą siatki MAP-Elites. Zaprojektuj deskryptor wektora cech dla nowego problemu (np. kolejności optymalizacji kompilatora), który zapewni odpowiednią różnorodność wyszukiwania.

3. Wynik mnożenia macierzy 4x4 za pomocą 48 operacji stanowi ulepszenie rekordu Strassena (49 operacji) po 56 latach. Przeczytaj Załącznik F do artykułu i wyjaśnij w trzech zdaniach, dlaczego wybór właściwego ewaluatora dla tego problemu był stosunkowo prosty i dlaczego większość domen nie daje takiego komfortu.

4. Zaproponuj jedną domenę, w której AlphaEvolve zakończy się niepowodzeniem. Określ dokładnie, w którym miejscu ewaluator zawiedzie i dlaczego.

5. Dla znanej Ci domeny zdefiniuj podpis ewaluatora. Uwzględnij: (a) warunki poprawności, (b) metrykę wydajności, (c) regułę generowania wydzielonych danych wejściowych, (d) co najmniej jedno zabezpieczenie przed hakowaniem nagród.

## Kluczowe terminy

| Termin | Co mówią ludzie | Co to naprawdę oznacza |
|---|---|---|
| AlphaEvolve | „Ewolucyjny agent kodujący DeepMind” | Gemini + baza danych programów + ewaluator sprawdzalny maszynowo |
| MAP-Elites | „Archiwum zachowujące różnorodność” | Wielowymiarowa siatka indeksowana wektorami cech; każda komórka zawiera najlepszy wariant o danym opisie |
| Model wyspowy | „Równoległe subpopulacje” | Niezależne populacje ewolucyjne migrujące okresowo między sobą; zapobiega przedwczesnej zbieżności |
| Ewaluator sprawdzalny maszynowo | „Deterministyczna wyrocznia” | Test jednostkowy, symulator lub benchmark, którego LLM nie może oszukać; warunek konieczny działania pętli |
| Hakowanie nagród | „Optymalizacja wskaźnika, a nie celu” | Pętla znajduje sposób na maksymalizację wyniku bez poprawnego wykonania właściwego zadania |
| Program zalążkowy | „Punkt wyjścia” | Początkowy, poprawny, ale nieoptymalny program, od którego zaczyna się ewolucja |
| Wydzielony ewaluator | „Ocena na danych niewidocznych dla LLM” | Dane wejściowe generowane dynamicznie w czasie oceny, aby zapobiec zapamiętywaniu |

## Dalsze czytanie

- [Novikov i in. (2025). AlphaEvolve: A Coding Agent for Scientific and Algorithmic Discovery](https://arxiv.org/abs/2506.13131) – pełna publikacja.
- [Wpis na blogu DeepMind o AlphaEvolve](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) – omówienie wyników przez autorów.
- [Repozytorium z wynikami AlphaEvolve](https://github.com/google-deepmind/alphaevolve_results) – odkryte algorytmy, w tym mnożenie macierzy 4x4 za pomocą 48 operacji.
- [Romera-Paredes i in. (2023). Mathematical discoveries from program search with large language models (FunSearch)](https://www.nature.com/articles/s41586-023-06924-6) – wcześniejsza wersja systemu.
- [Anthropic — Responsible Scaling Policy, Version 3.0 (luty 2026)](https://anthropic.com/responsible-scaling-policy/rsp-v3-0) – wskazuje autonomię opartą na ewaluatorach jako kluczowy kierunek badań nad bezpieczeństwem.
