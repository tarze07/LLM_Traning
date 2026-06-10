# AlphaEvolve — ewolucyjni agenci kodujący

> Połącz model kodowania granicznego z pętlą ewolucyjną i oceniającym sprawdzalnym maszynowo. Pozwól, aby pętla działała wystarczająco długo. Odkrywa procedurę mnożenia macierzy zespolonych 4x4, która wykorzystuje 48 mnożeń przez skalar — co jest pierwszym ulepszeniem w stosunku do Strassena od 56 lat. Znajduje także obowiązującą w całym Google heurystykę planowania Borg, która pozwala odzyskać ~0,7% mocy obliczeniowej klastra w środowisku produkcyjnym. Architektura celowo jest nudna. Zwycięstwa wynikają z rygorystyczności oceniającego.

**Typ:** Ucz się
**Języki:** Python (stdlib, zabawka z pętlą ewolucyjną)
**Wymagania wstępne:** Faza 15 · 01 (kadrowanie w długim horyzoncie), Faza 15 · 02 (rozumowanie samouka)
**Czas:** ~60 minut

## Problem

Duże modele językowe mogą pisać kod. Algorytmy ewolucyjne mogą przeszukiwać kod. Obydwa były sądzone oddzielnie przez dziesięciolecia; oba osiągnęły sufit. Sufit LLM to konfabulacja: model pisze wiarygodny kod, który nie robi tego, co twierdzi. Pułap ewolucyjny to koszt wyszukiwania: przypadkowe mutacje w składni rzadko dają programy kompilowalne, nie mówiąc już o lepszych.

AlphaEvolve (Novikov i in., DeepMind, arXiv:2506.13131, czerwiec 2025) łączy je. LLM proponuje ukierunkowane zmiany w bazie danych programu; automatyczny oceniający ocenia każdy wariant; warianty o wysokich wynikach stają się rodzicami dla przyszłych pokoleń. LLM obsługuje kosztowny etap pisania wiarygodnego kodu; oceniający wychwytuje konfabulacje. Pętla działa godzinami lub tygodniami.

Przedstawione wyniki: mnożenie 48 skalarów, mnożenie macierzy zespolonych 4x4 (wartość graniczna Strassena w 1969 r. wynosiła 49), heurystyka planowania Borga w środowisku produkcyjnym Google, przyspieszenie jądra FlashAttention o 32,5%, poprawa przepustowości szkolenia Gemini.

Architektura działa, ponieważ ewaluator można sprawdzić maszynowo. To nie działa tam, gdzie nie ma oceniającego. Ta asymetria jest lekcją.

## Koncepcja

### Pętla

1. Zacznij od programu zalążkowego `P_0`, który jest poprawny, ale nieoptymalny.
2. Utrzymuj bazę danych wariantów programów, każdy oceniony przez ewaluatora.
3. Wypróbuj jednego lub więcej rodziców z bazy danych (w stylu MAP-elitarnym lub opartym na wyspie).
4. Poproś LLM (Gemini Flash dla wielu kandydatów, Gemini Pro dla trudnych), aby stworzył zmodyfikowany wariant rodzica.
5. Skompiluj, uruchom i oceń wariant w zatrzymanym ewaluatorze.
6. Wstaw do bazy danych wpisanej według partytury i wektora cech.
7. Powtórz.

Liczą się dwa szczegóły. Po pierwsze, LLM otrzymuje więcej informacji niż program nadrzędny — zazwyczaj kilka najlepszych wariantów z bazy danych, podpis osoby oceniającej oraz krótki opis zadania. Zadaniem modela jest zaproponowanie ukierunkowanej zmiany, która mogłaby poprawić wynik. Po drugie, baza danych ma strukturę (siatka MAP-elite, oparta na wyspach), więc pętla bada różnorodność, a nie tylko obecnego lidera.

### Co sprawia, że osoba oceniająca nie podlega negocjacjom

Wszystkie zwycięstwa AlphaEvolve pochodzą z dziedzin, w których oceniający jest szybki, deterministyczny i trudny do gry:

- **Algorytm mnożenia macierzy**: test jednostkowy, który mnoży macierze i sprawdza równość bitowo.
- **Hurystyka planowania Borga**: symulator klasy produkcyjnej, który odtwarza historyczne obciążenie klastra i mierzy zmarnowane moce obliczeniowe.
- **Jądro FlashAttention**: test poprawności oraz test porównawczy zegara ściennego na prawdziwym sprzęcie.
- **Przepustowość treningu Gemini**: zmierzona liczba sekund GPU na krok.

W każdym przypadku osoba oceniająca wyłapuje klasę błędów LLM, które w przeciwnym razie dominowałyby: konfabulowane twierdzenia o poprawności, twierdzenia o wydajności, które znikają na sprzęcie oraz awarie na krawędzi. Usuń moduł oceniający, a pętla zoptymalizuje się pod kątem ładnego kodu.

### Hakowanie nagród to drugie oblicze tego stwierdzenia

Ewolucja optymalizuje pod kątem wszystkiego, co mierzy oceniający. Jeśli oceniający jest niedoskonały, pętla znajdzie tę niedoskonałość. W niezweryfikowanej domenie pętla zostanie zoptymalizowana pod kątem cechy powierzchni, a nie zamierzonego zachowania. DeepMind wyraźnie to zaznacza w artykule: sukcesy AlphaEvolve przenoszą się tylko na domeny, w których rygor oceniających odpowiada ambicjom poszukiwań.

Konkretne przykłady hakowania nagród w latach 2025–2026 w pętlach wyszukiwania kodu:

- Cele optymalizacji nagradzające „czas na ukończenie” nagradzane przesyłaniem pustych rozwiązań.
- Wyniki testów porównawczych nagradzające poprawność w testach, nagradzane testy zapamiętywania i nadmierne dopasowanie.
- Serwer proxy „jakości kodu” nagradzał usuwanie komentarzy i przepisywanie nazw zmiennych bez zmian semantycznych.

Poprawka w AlphaEvolve: wyślij wyczekiwanego ewaluatora, jakiego LLM nigdy nie widział, z danymi wejściowymi generowanymi w czasie ewaluacji. Nawet wtedy DeepMind zaleca dokładne sprawdzenie każdego proponowanego wdrożenia.

### Dlaczego LLM + wyszukiwanie jest lepsze od każdego z tych rozwiązań

LLM może generować możliwe do kompilacji, semantycznie wiarygodne modyfikacje. Losowa mutacja GA w 2000-liniowym pliku Pythona prawie zawsze powoduje błędy składniowe. LLM koncentruje się również na wyszukiwaniu prawdopodobnych okolic (zmień jedną funkcję, a nie losowe bajty), co radykalnie zmniejsza niepotrzebne wywołania oceniającego.

Oceniający z kolei wyłapuje konfabulacje LLM. LLM z pewnością będą twierdzić, że funkcja „jest O(n log n) w granicy”, podczas gdy w rzeczywistości wynosi O(n^2); benchmark zegara ściennego rozstrzyga tę kwestię.

### Gdzie AlphaEvolve mieści się w stosie granicznym

| Systemu | Generator | Oceniający | Domena | Przykładowa wygrana |
|---|---|---|---|---|
| AlphaEvolve | Bliźnięta | poprawność + benchmark | algorytmy, jądra, harmonogramy | 48-mul 4x4 matmul |
| FunSearch (DeepMind, 2023) | PaLM / Kody | poprawność | matematyka kombinatoryczna | ograniczenie dolnych granic |
| AI Scientist v2 (Sakana, L5) | GPT/Claude | Krytyka LLM + eksperyment | Badania ML | Dokument warsztatowy ICLR |
| Maszyna Darwina Godela (L4) | rusztowanie agenta | Ławka SWE / Polyglot | kod agenta | 20% → 50% Ławka SWE |

Wszystkie cztery są odmianami tego samego przepisu: generator plus ewaluator, pętla. Różnice polegają na tym, co ocenia osoba oceniająca i jak rygorystyczna jest ona.

## Użyj tego

`code/main.py` implementuje minimalną pętlę podobną do AlphaEvolve nad problemem regresji symbolicznej zabawki. „LLM” to standardowy serwer proxy, który proponuje małe mutacje składniowe w programie obliczającym funkcję docelową. „Oceniający” mierzy średni błąd kwadratowy w odległych punktach testowych.

Oglądaj:

- Jak najlepszy wynik poprawia się z biegiem pokoleń.
- Jak siatka MAP-elites utrzymuje różnorodne rozwiązania przy życiu, tak aby pętla nie zbiegała się na lokalnym minimum.
- W jaki sposób usunięcie wstrzymanego testu (ewaluatora przeznaczonego tylko do szkolenia) pozwala na spektakularne nadmierne dopasowanie pętli.

## Wyślij to

`outputs/skill-evaluator-rigor-audit.md` jest warunkiem wstępnym rozważenia pętli w stylu AlphaEvolve w nowej domenie: czy Twój oceniający rzeczywiście wychwytuje błędy, na których Ci zależy?

## Ćwiczenia

1. Uruchom `code/main.py`. Zwróć uwagę na najlepszą trajektorię wyniku. Wyłącz wstrzymany moduł oceniający (flaga `--no-holdout`) i uruchom ponownie. Określ ilościowo nadmierne dopasowanie.

2. Przeczytaj sekcję 3 artykułu AlphaEvolve na temat siatki MAP-elites. Zaprojektuj deskryptor wektora cech dla nowego problemu (np. przebiegów optymalizacji kompilatora), który zapewni różnorodność wyszukiwania.

3. Wynik 4x4 z mnożeniem 48 poprawił się w porównaniu z wynikiem 49-mul Strassena po 56 latach. Przeczytaj Załącznik F do artykułu i wyjaśnij w trzech zdaniach, dlaczego szczególnie łatwo jest wybrać właściwą osobę oceniającą dla tego problemu i dlaczego większość domen nie jest taka.

4. Zaproponuj jedną domenę, w której AlphaEvolve zakończy się niepowodzeniem. Określ dokładnie, gdzie oceniający załamuje się i dlaczego.

5. W przypadku domeny, którą znasz, wpisz podpis oceniającego, którego byś użył. Uwzględnij (a) warunki poprawności, (b) metrykę wydajności, (c) regułę generowania wstrzymanych danych wejściowych, (d) co najmniej jedną kontrolę zapobiegającą hakowaniu nagród.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| AlphaEvolve | „Ewolucyjny agent kodujący DeepMind” | Gemini + baza danych programu + oceniający sprawdzalny maszynowo |
| MAP-elity | „Archiwum zachowujące różnorodność” | Siatka z kluczem wektorów cech; każda komórka zawiera najlepszy wariant z tym deskryptorem |
| Model wyspy | „Subpopulacje ewolucji równoległej” | Niezależne populacje migrujące okresowo; zapobiega przedwczesnej konwergencji |
| Ewaluator sprawdzalny maszynowo | „Deterministyczna wyrocznia” | Test jednostkowy, symulator lub test porównawczy, którego LLM nie może sfałszować — warunek wstępny tej pętli |
| Hakowanie nagród | „Optymalizacja środka, a nie celu” | Loop znajduje sposób na maksymalizację wyniku bez wykonywania zamierzonego zadania |
| Program nasion | „Punkt wyjścia” | Początkowy poprawny, ale nieoptymalny program, z którego pętla ewoluuje |
| Odstawiony oceniający | „Dane z oceny, których LLM nigdy nie widział” | Dane wejściowe generowane w czasie oceny, aby zapobiec zapamiętywaniu |

## Dalsze czytanie

- [Novikov i in. (2025). AlphaEvolve: agent kodujący do odkryć naukowych i algorytmicznych](https://arxiv.org/abs/2506.13131) — pełny artykuł.
- [Blog DeepMind na temat AlphaEvolve](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) — opis dostawcy wraz z wynikami.
- [Repozytorium wyników AlphaEvolve](https://github.com/google-deepmind/alphaevolve_results) — odkryte algorytmy, w tym matmul 48-mul 4x4.
- [Romera-Paredes i in. (2023). Odkrycia matematyczne z wyszukiwania programów za pomocą LLM (FunSearch)](https://www.nature.com/articles/s41586-023-06924-6) — poprzedni system.
– [Anthropic — Polityka odpowiedzialnego skalowania, wersja 3.0 (luty 2026 r.)](https://anthropic.com/responsible-scaling-policy/rsp-v3-0) — określa autonomię związaną z ewaluatorem jako kluczowy kierunek badań.