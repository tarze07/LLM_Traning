# AI Scientist v2 — autonomiczne badania naukowe na poziomie warsztatowym

> Aplikacja AI Scientist v2 firmy Sakana (Yamada i in., arXiv:2504.08066) obsługuje pełną pętlę badawczą: od postawienia hipotezy, przez pisanie kodu, eksperymenty, generowanie wykresów, zredagowanie tekstu, aż po zgłoszenie artykułu (submission). Jest to pierwszy system, który wygenerował artykuł naukowy przyjęty na warsztaty konferencji ICLR 2025. Niezależna ocena (Beel i in.) wykazała jednak, że 42% eksperymentów zakończyło się niepowodzeniem z powodu błędów w kodowaniu, a automatyczny przegląd literatury często błędnie klasyfikował znane koncepcje jako nowatorskie. Dokumentacja Sakana AI ostrzega, że system uruchamia kod generowany bezpośrednio przez LLM, i zaleca stosowanie izolacji w Dockerze. Należy brać pod uwagę obie te perspektywy.

**Typ:** Ucz się
**Języki:** Python (biblioteka standardowa, prosty symulator pętli badawczej opartej na maszynie stanów)
**Wymagania wstępne:** Faza 15 · 03 (AlphaEvolve), Faza 15 · 04 (DGM)
**Czas:** ~60 minut

## Problem

Badania naukowe to zadanie o charakterze otwartym. W przeciwieństwie do wyszukiwania algorytmicznego w AlphaEvolve lub samomodyfikacji opartej na benchmarkach w DGM, wynik pracy badawczej nie posiada kryterium poprawności, które dałoby się zweryfikować w pełni maszynowo. Artykuł oceniają recenzenci (ludzie), a nie testy jednostkowe. To sprawia, że zamknięcie pętli jest trudniejsze, ale zarazem niezwykle wartościowe, ponieważ w badaniach naukowych tkwi motor postępu.

AI Scientist v1 (Sakana, 2024) zamknął tę pętlę, opierając się na szablonach stworzonych przez człowieka – LLM przeprowadzał eksperymenty wewnątrz sztywnych ram. AI Scientist v2 (Yamada i in., 2025) rezygnuje z szablonów na rzecz agenckiego przeszukiwania drzew (agentic tree search) połączonego z pętlą krytyczną opartą na modelach językowo-wizyjnych (VLM). System samodzielnie generuje pomysły, realizuje eksperymenty, tworzy wykresy, pisze artykuł i wprowadza poprawki na podstawie opinii recenzentów.

Werdykt procesu recenzji: jeden artykuł wygenerowany przez wersję v2 został przyjęty na warsztaty ICLR 2025 (przy pełnym ujawnieniu autorstwa AI). Werdykt niezależnego audytu: system jest wciąż daleki od niezawodności. Oba te stwierdzenia są prawdziwe.

## Koncepcja

### Architektura systemu

1. **Generowanie pomysłów.** LLM proponuje hipotezy badawcze na podstawie zadanego tematu i istniejącej literatury. Wersja v1 opierała się na szablonach; wersja v2 wykorzystuje agenckie przeszukiwanie drzew w przestrzeni hipotez.
2. **Weryfikacja nowości.** Krok wyszukiwania w bazach literatury sprawdza, czy dany pomysł nie został już opublikowany. W analizie Beela i in. krok ten okazał się słabym punktem – znane metody były często klasyfikowane jako nowatorskie.
3. **Planowanie eksperymentu.** Agent opracowuje protokół eksperymentu i pisze odpowiedni kod.
4. **Wykonanie.** Kod jest uruchamiany w piaskownicy (sandbox). Błędy wykonania są przekazywane z powrotem do pętli ponawiania prób. Z pomiarów Beela i in. wynika, że na tym etapie aż 42% eksperymentów zakończyło się niepowodzeniem z powodu błędów w kodzie.
5. **Generowanie wykresów.** Model wizyjno-językowy analizuje wygenerowane wykresy i poprawia je pod kątem czytelności. Był to kluczowy element techniczny dodany w wersji v2.
6. **Redagowanie tekstu.** LLM przygotowuje artykuł naukowy, który następnie przechodzi wstępną ocenę przez wewnętrznego recenzenta (LLM).
7. **Opcjonalnie: zgłoszenie.** Gotowy artykuł jest wysyłany do wybranego wydawnictwa lub na konferencję.

### Co rzeczywiście oznacza akceptacja na warsztatach

Jeden artykuł wygenerowany przez wersję v2 przeszedł pozytywnie recenzję podczas warsztatów ICLR 2025. Autorzy w pełni ujawnili komitetowi naukowemu pochodzenie publikacji. Ta akceptacja jest interesującym punktem odniesienia, ale nie oznacza, że system potrafi w pełni samodzielnie „prowadzić badania”.

Ważny kontekst: wymagania dla artykułów warsztatowych są znacznie niższe niż na głównej konferencji. Proces recenzowania bywa zmienny i obarczony szumem. Ten sukces to dowód koncepcji (proof of concept), a nie gwarancja niezawodności. Co więcej, późniejszy artykuł opublikowany w Nature w 2026 roku dokumentował pętlę od początku do końca, ale powstał przy współudziale badaczy-ludzi; nie można więc twierdzić, że „system sam napisał artykuł w Nature”.

### Co wykazała niezależna ocena

Beel i in. (arXiv:2502.14297) przeprowadzili zewnętrzną ocenę systemu. Główne wnioski:

- **Błędy w eksperymentach.** 42% eksperymentów zakończyło się awarią z powodu błędów w kodzie (błędne importy, niedopasowanie wymiarów macierzy, niezdefiniowane zmienne). Pętla ponawiania prób wychwyciła tylko część z nich.
- **Błędna klasyfikacja nowości.** Moduł wyszukiwania literatury często uznawał znane koncepcje za nowatorskie. Jest to naukowy odpowiednik halucynacji.
- **Efekt maskowania dopracowaniem (polish masking).** Krytyka wykresów prowadzona przez model wizyjny pozwalała uzyskać ilustracje o jakości publikacyjnej, co skutecznie maskowało fundamentalne wady samych eksperymentów.

Ostatnie ustalenie ma kluczowe znaczenie dla bezpieczeństwa. System generujący atrakcyjnie wyglądające artykuły naukowe bez rzetelnie przeprowadzonych badań jest bardziej niebezpieczny niż system, który ewidentnie i w prosty sposób zawodzi. Ocena musi dotyczyć leżących u podstaw twierdzeń naukowych, a nie zatrzymywać się na estetyce wykresów.

### Problem ucieczki z piaskownicy (sandbox escape)

Plik README oficjalnego repozytorium Sakana AI ostrzega:

> Ze względu na charakter tego oprogramowania, które uruchamia kod generowany przez LLM, nie możemy zagwarantować pełnego bezpieczeństwa. Istnieje ryzyko związane z niebezpiecznymi pakietami, niekontrolowanym dostępem do sieci i uruchamianiem niezamierzonych procesów. Używasz oprogramowania na własne ryzyko. Rozważ uruchamianie go wyłącznie w odizolowanym środowisku Docker.

Taki jest operacyjny wymiar autonomii w otwartych domenach. LLM pisze kod; kod jest uruchamiany i może wykonać dowolną akcję w ramach uprawnień procesu. Bez piaskownicy, która sztywno ogranicza dostęp do systemu plików, sieci i procesów systemowych, autonomiczny agent badawczy może wykradać dane, marnować zasoby obliczeniowe lub niekontrolowanie modyfikować własny kod.

W AlphaEvolve piaskownica jest prostsza, ponieważ ewaluator nakłada sztywne ramy. AI Scientist v2 uruchamia otwarty kod o niesprecyzowanych z góry celach. Wymaga to znacznie silniejszej izolacji (minimum to Docker, optymalnie gVisor lub seccomp) oraz ręcznej weryfikacji każdego pliku wyjściowego, zanim opuści on piaskownicę.

### Miejsce v2 w zestawieniu systemów

| System | Cel | Typ wyniku | Ewaluator | Główna słabość |
|---|---|---|---|---|
| AlphaEvolve | algorytmy | kod | testy jednostkowe + benchmarki | ograniczony rygorem testów |
| DGM | szkielet agenta | kod | SWE-bench | hakowanie nagród |
| AI Scientist v2 | artykuły naukowe | tekst + kod + wykresy | recenzja naukowa (podatna na szum) | błędy eksperymentów, halucynacje nowości, maskowanie wad dopracowaną formą |

Wersja v2 ma najsłabszy automatyczny ewaluator z całego zestawienia, najszerszy format wyników oraz najkrótszą drogę do generowania publicznie dostępnych artefaktów. Większość zadań związanych z bezpieczeństwem spoczywa tu na kontrolach operacyjnych (izolacja w piaskownicy, ręczna weryfikacja, ujawnianie autorstwa AI).

## Użyj tego

Skrypt `code/main.py` symuluje działanie pętli v2 w formie maszyny stanów: pomysł → weryfikacja nowości → eksperyment → wykresy → redagowanie → recenzja → akceptacja lub poprawki. Każdy stan ma przypisane prawdopodobieństwo błędu na podstawie danych empirycznych Beela i in. Uruchom symulację dla N cykli i przeanalizuj:

- Ile pomysłów zostało ostatecznie zgłoszonych jako artykuły.
- Jaka część z nich zawiera krytyczne błędy eksperymentalne zamaskowane atrakcyjną formą prezentacji.
- Jak budżet ponownych prób (retry budget) wpływa na ostateczną jakość i wydajność procesu.

## Wdrożenie

Lista kontrolna `outputs/skill-ai-scientist-sandbox-review.md` definiuje dwuetapową procedurę weryfikacji (dwubramkową) dla wszystkich artefaktów wyprodukowanych w pętli badawczej przed ich eksportem z piaskownicy.

## Ćwiczenia

1. Uruchom `code/main.py` z domyślnymi parametrami. Jaki procent przebiegów generuje całkowicie poprawny artykuł? Jaki procent kończy się publikacją o ładnej formie, ale z ukrytą wadą eksperymentalną?

2. Domyślne wartości symulacji opierają się na wskaźnikach Beela i in. (42% błędów / 25% błędnej oceny nowości). Uruchom symulację ponownie z parametrami `--experiment-failure 0.20 --novelty-mislabel 0.10`, a następnie `--experiment-failure 0.60 --novelty-mislabel 0.40`. Jak zmienia się proporcja dopracowanych, lecz wadliwych prac?

3. Przeczytaj instrukcje w repozytorium AI Scientist v2 na temat konfiguracji piaskownicy. Wskaż dwa dodatkowe ograniczenia bezpieczeństwa (poza samym Dockerem), które wdrożyłbyś przy wielodniowym, autonomicznym uruchomieniu pętli.

4. Przeczytaj sekcję 4 artykułu Beela i in. dotyczącą maskowania wad formą prezentacji (presentation quality gap). Zaprojektuj jeden dodatkowy, zautomatyzowany test oceniający, który potrafiłby wykryć ładnie napisany, lecz niespójny merytorycznie artykuł.

5. Zaproponuj protokół ręcznej weryfikacji prac generowanych przez sztuczną inteligencję, który byłby bardziej skalowalny niż podejście typu „człowiek z doktoratem czyta od deski do deski każdy tekst”. Wskaż główne wąskie gardło i zaprojektuj rozwiązanie wokół niego.

## Kluczowe terminy

| Termin | Co mówią ludzie | Co to naprawdę oznacza |
|---|---|---|
| AI Scientist v1 | „Agent badawczy Sakana oparty na szablonie” | Pierwsza wersja systemu realizująca eksperymenty wewnątrz sztywno zdefiniowanych ram |
| AI Scientist v2 | „Agent badawczy bez szablonów” | Przeszukiwanie drzewa hipotez przez agenta z krytyką wykresów za pomocą VLM |
| Agenckie przeszukiwanie drzew | „Rozgałęzione badanie hipotez” | Równoległe rozwijanie wielu ścieżek eksperymentów i odrzucanie słabych gałęzi przez wewnętrznego krytyka |
| Krytyka wykresów za pomocą VLM | „Polerowanie wykresów przez model wizyjny” | Zastosowanie modelu multimodalnego do odczytu ilustracji i poprawy ich czytelności |
| Weryfikacja nowości | „Sprawdzanie literatury” | Automatyczne wyszukiwanie wcześniejszych publikacji w celu oceny nowatorstwa hipotezy – obarczone ryzykiem halucynacji |
| Maskowanie dopracowaniem | „Ładny artykuł, wadliwe badania” | Zjawisko, w którym wysoka jakość prezentacji i wykresów maskuje fundamentalne błędy w metodologii i kodzie |
| Ucieczka z piaskownicy | „Wyjście kodu LLM poza granice” | Sytuacja, w której kod wygenerowany i uruchomiony przez agenta wykonuje operacje niezamierzone przez projektanta systemu |

## Dalsze czytanie

- [Yamada i in. (2025). The AI Scientist-v2: Towards Fully Autonomous Scientific Research](https://arxiv.org/abs/2504.08066) – publikacja źródłowa.
- [Wpis Sakana AI o publikacji w Nature w 2026 roku](https://sakana.ai/ai-scientist-nature/) – kontekst recenzji naukowej i udziału ludzi.
- [Beel i in. (2025). An Independent Evaluation of The AI Scientist](https://arxiv.org/abs/2502.14297) – szczegółowe wyniki zewnętrznego audytu.
- [Publikacja o AI Scientist v1 (Sakana AI, 2024)](https://arxiv.org/abs/2408.06292) – pierwsza wersja oparta na szablonach.
- [Anthropic — Measuring Agent Autonomy](https://www.anthropic.com/research/measuring-agent-autonomy) – szersze spojrzenie na bezpieczeństwo i badanie autonomii agentów.
