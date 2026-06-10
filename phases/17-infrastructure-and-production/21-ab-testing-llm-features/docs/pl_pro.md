# Testy A/B funkcjonalności LLM – GrowthBook, Statsig i problem wariancji (wibracji) wyników

> **Przegląd cen z dnia 2026-04.** Poniższe wartości odzwierciedlają stawki dostawców zarejestrowane w momencie publikacji tej lekcji; przed zacytowaniem ich w dalszej części tekstu zweryfikuj je z aktualną dokumentacją.

> Klasyczne platformy do testów A/B nie zostały zaprojektowane z myślą o niedeterministycznych modelach LLM. Kluczowe rozróżnienie polega na tym, że testy offline (evals) odpowiadają na pytanie: „Czy model potrafi poprawnie wykonać to zadanie?”, podczas gdy testy A/B odpowiadają na pytanie: „Czy ta zmiana ma znaczenie dla użytkowników końcowych?”. Obie metody są niezbędne, a era wdrażania zmian na podstawie samej intuicji („vibe-check”) bezpowrotnie minęła. W 2026 roku testom A/B podlegają głównie: inżynieria promptów (struktura i sformułowania), wybór modelu (np. GPT-4 vs Llama-OSS – kompromis: jakość vs koszt vs opóźnienia) oraz parametry generowania tekstu (temperatura, top-p). Rzeczywiste przypadki wdrożeń: optymalizacja modelu nagrody (reward model) w chatbotach przyniosła +70% wzrostu długości konwersacji i +30% retencji; testy tematów AI w serwisie Nextdoor przyniosły +1% CTR po dostrojeniu modelu; platforma Khanmigo (Khan Academy) stale eksperymentuje z balansem między opóźnieniami (latency) a dokładnością matematyczną (accuracy).
> Główne platformy eksperymentalne w 2026 roku:
> **Statsig** (przejęty przez OpenAI za 1,1 mld USD we wrześniu 2025 r.): kompletna platforma typu all-in-one oferująca testy sekwencyjne, metodę CUPED oraz grupy wstrzymane (holdout).
> **GrowthBook**: rozwiązanie open-source na licencji MIT, integrujące się bezpośrednio z hurtowniami danych (BigQuery/Snowflake). Oferuje silniki statystyczne (Bayesowski, częstotliwościowy, sekwencyjny), CUPED, detekcję SRM oraz korekty porównań wielokrotnych (metodami Benjaminiego-Hochberga oraz Bonferroniego). Wybór zależy od infrastruktury danych oraz polityki organizacyjnej dotyczącej zależności od dostawcy (OpenAI).

**Typ:** Teoria i praktyka
**Języki:** Python (stdlib, uproszczony symulator testów sekwencyjnych)
**Wymagania wstępne:** Faza 17 · 13 (Monitorowanie i obserwowalność), faza 17 · 20 (Shadow i Canary)
**Czas:** ~60 minut

## Cele naukowe

- Rozróżnianie testów offline (evals – „czy model potrafi wykonać zadanie”) od testów A/B (online – „czy użytkownicy to docenią”).
- Zdefiniowanie trzech osi testowych (prompt, model, parametry generowania) oraz dobranie metryk dla każdej z nich.
- Zrozumienie metod statystycznych: redukcji wariancji CUPED, testów sekwencyjnych oraz korekty porównań wielokrotnych Benjaminiego-Hochberga.
- Wybór pomiędzy platformą Statsig a GrowthBook z uwzględnieniem architektury hurtowni danych i powiązań z dostawcami.

## Problem

Ręcznie zmodyfikowałeś prompt systemowy. Zmiana wydaje się świetna. Wdrażasz ją. Wykresy konwersji wahają się, ale ruch wygląda na zwykły szum statystyczny. Nie wiesz, czy zmiana pomogła, czy też wina leży po stronie metryk. Inny scenariusz: wdrażasz nowy model, a wskaźniki ani drgną – czy model pogorszył jakość, czy też różnica była zbyt subtelna, by ją wychwycić? Brak testów A/B uniemożliwia wyciągnięcie wniosków.

Testy offline (evals) sprawdzają jedynie skuteczność modelu na ustalonym zbiorze danych. Nie dają odpowiedzi na pytanie, czy użytkownicy rzeczywiście wolą nowe odpowiedzi. Może to potwierdzić wyłącznie kontrolowany eksperyment online, przeprowadzony na odpowiednio dużej próbie, kompensujący niedeterminizm i korygujący błędy porównań wielokrotnych.

## Koncepcja

### Ewaluacje offline (Evals) vs Testy A/B online

- **Evals**: testy offline na zestawie walidacyjnym za pomocą sędziego (LLM-as-a-judge lub człowieka). Odpowiadają na pytanie: „Czy odpowiedzi modelu są poprawne i bezpieczne na przygotowanym zbiorze danych?”.
- **Testy A/B**: testy online na żywym ruchu z losowym podziałem użytkowników. Odpowiadają na pytanie: „Czy nowy wariant poprawia kluczowe wskaźniki biznesowe na poziomie zachowań użytkowników?”.

Oba etapy są niezbędne. Evals zapobiegają wdrożeniu wadliwego modelu na produkcję, a testy A/B potwierdzają jego realną wartość biznesową.

### Co testować w systemach LLM

1. **Inżynieria promptów (Prompt Engineering)**: modyfikacje treści, struktury promptów systemowych i dobór przykładów (few-shot). Metryki: wskaźnik sukcesu zadania (task success rate), retencja użytkowników, średni koszt zapytania.
2. **Wybór modelu**: np. GPT-4 vs Llama-OSS. Metryki: dokładność odpowiedzi, koszt na milion tokenów, opóźnienie (P99 latency). Jest to optymalizacja wielokryterialna.
3. **Parametry generowania (Hyperparameters)**: temperatura, wartości top-p, limit max_tokens. Metryki: powtarzalność i determinizm odpowiedzi vs kreatywność.

### CUPED (Redukcja wariancji)

Metoda statystyczna wykorzystująca dane użytkowników zebrane przed rozpoczęciem eksperymentu (pre-experiment data). Pozwala ona wyczyścić szum i różnice indywidualne przed porównaniem wyników. Zapewnia redukcję wariancji o 30–70%, co oznacza bezpłatne zwiększenie efektywnej wielkości próby. Metoda CUPED jest natywnie wspierana zarówno przez Statsig, jak i GrowthBook.

### Testowanie Sekwencyjne (Sequential Testing)

Klasyczne testy A/B wymagają z góry określonej, stałej wielkości próby. Przedwczesne sprawdzanie wyników (tzw. peeking) drastycznie zwiększa liczbę fałszywych alarmów (błędów I rodzaju). Metody sekwencyjne (np. algorytm mSPRT czy sekwencje ufności Howarda) kontrolują ten błąd, umożliwiając bezpieczne zakończenie testu przed czasem w przypadku wykrycia jednoznacznego zwycięzcy.

### Korekta porównań wielokrotnych (Multiple Comparisons Correction)

Testowanie 20 hipotez jednocześnie na poziomie ufności 95% statystycznie gwarantuje wykazanie co najmniej jednego fałszywie dodatniego wyniku (błędu). Korekta Bonferroniego drastycznie zaostrza próg istotności (alfa), natomiast metoda Benjaminiego-Hochberga kontroluje odsetek fałszywych odkryć (FDR). GrowthBook wspiera obie te analizy.

### SRM (Sample Ratio Mismatch)

Algorytm losowania dzieli ruch użytkowników na warianty. Jeśli przy planowanym podziale 50/50 rzeczywisty podział wynosi 47/53, oznacza to błąd dystrybucji ruchu (SRM). Obie platformy automatycznie alarmują o wystąpieniu tego zjawiska.

### Statsig vs GrowthBook

- **Statsig**:
  - Usługa SaaS przejęta przez OpenAI za 1.1 mld USD we wrześniu 2025 roku.
  - Oferuje testy sekwencyjne, CUPED oraz grupy wstrzymane (holdout).
  - Podejście all-in-one: zarządzanie flagami (feature flags), analityka i logowanie w jednym systemie.
  - Kiedy stosować: zespoły poszukujące gotowego, zintegrowanego pakietu, akceptujące zależność od technologii OpenAI.
- **GrowthBook**:
  - Projekt open-source (licencja MIT) z silną integracją z bazami SQL (odpytuje bezpośrednio Snowflake/BigQuery/Redshift).
  - Wspiera wiele silników statystycznych: Bayesowski, częstotliwościowy oraz sekwencyjny.
  - Posiada wbudowane CUPED, weryfikację SRM oraz korekty Bonferroniego/BH.
  - Dostępny w wersji self-hosted oraz w chmurze zarządzanej.
  - Kiedy stosować: firmy posiadające własny dział analityki danych (data team), preferujące licencje open-source i bezpośredni dostęp do baz SQL.

### Niedeterminizm a moc testu (Statistical Power)

Niedeterminizm modeli LLM powoduje, że dane wejściowe nie spełniają w pełni założeń o niezależnym rozkładzie (IID). W efekcie rzeczywista moc statystyczna testu spada. Aby to skompensować, zaleca się zwiększenie wymaganej liczby użytkowników w próbie o bufor rzędu 1.3-1.5x.

### Przykłady z wdrożeń produkcyjnych

- Chatboty: optymalizacja modelu nagrody przełożyła się na +70% wzrostu długości konwersacji oraz +30% wzrostu retencji użytkowników.
- Nextdoor: wdrożenie algorytmów rekomendacyjnych przyniosło +1% CTR po dostrojeniu modelu.
- Khan Academy (Khanmigo): ciągłe eksperymentowanie na osi latency vs matematyczna poprawność odpowiedzi.

### Antywzorzec: wdrażanie na podstawie intuicji („vibe-check”)

Większość inżynierów spotkała się z sytuacją wdrożenia nowej wersji modelu, która „wydawała się lepsza” podczas ręcznego testowania. Brak kontrolowanego testu A/B często maskuje regresje wskaźników biznesowych, które są wykrywane dopiero po wielu miesiącach. Testy A/B wymuszają obiektywność ocen.

## Praktyczne zastosowanie

Skrypt `code/main.py` symuluje działanie testu A/B w wariancie klasycznym (o stałej próbie) oraz sekwencyjnym. Pokazuje, jak metody sekwencyjne pozwalają na bezpieczne, przedwczesne przerwanie eksperymentu w przypadku wyraźnego zwycięstwa jednego z wariantów.

## Zadanie wdrożeniowe

W ramach tej lekcji przygotowano szablon planu `outputs/skill-ab-plan.md`. Narzędzie to, na podstawie modyfikacji funkcjonalnej i danych wejściowych, pomaga w doborze platformy eksperymentalnej, bramek alarmowych oraz wielkości próby.

## Ćwiczenia

1. Uruchom `code/main.py`. Dla oczekiwanego wzrostu wskaźnika (MDE) o 5% przy bazowej konwersji wynoszącej 3%, jaka wielkość próby jest niezbędna do uzyskania mocy statystycznej 80%?
2. Wybierz i uzasadnij wybór platformy (Statsig lub GrowthBook) dla klienta z branży medycznej (regulowanej prawnie).
3. Zaprojektuj eksperyment A/B porównujący modele GPT-4 i GPT-3.5 pod kątem jednostkowego kosztu skutecznego obsłużenia zgłoszenia klienta (ticketu). Zdefiniuj metrykę główną (primary metric), metrykę bezpieczeństwa (guardrail metric) oraz metryki pomocnicze (secondary metrics).
4. Nowy model pomyślnie przeszedł bramki wdrożenia typu canary, ale test A/B wykazuje spadek konwersji o 1.2%. Czy zdecydujesz się na wdrożenie go na 100% użytkowników? Sformułuj kryteria eskalacji decyzyjnej.
5. Wdrożono CUPED z wykorzystaniem danych historycznych, co pozwoliło zredukować wariancję o 60%. Oblicz, o ile zmniejszy to wymaganą wielkość próby dla uzyskania tej samej mocy statystycznej.

## Słownik pojęć

| Termin | Popularne określenie | Rzeczywiste znaczenie |
|------|----------------|--------------------------------------|
| Evals | „testy offline” | Ewaluacja jakości odpowiedzi modelu na przygotowanym, oznaczonym zbiorze danych |
| Test A/B | „eksperyment online” | Kontrolowane, losowe porównanie zachowań użytkowników na żywym ruchu produkcyjnym |
| CUPED | „redukcja wariancji” | Metoda statystyczna korygująca wahania wskaźników z użyciem danych przedeksperymentalnych |
| Testy Sekwencyjne | „dynamiczny test A/B” | Bezpieczne testy statystyczne umożliwiające monitorowanie wyników na żywo i wcześniejsze zakończenie |
| Porównania Wielokrotne | „błąd skumulowany” | Zjawisko wzrostu szansy na fałszywy alarm przy jednoczesnym testowaniu wielu hipotez |
| Korekta Bonferroniego | „konserwatywny próg” | Metoda podziału dopuszczalnego błędu (alfa) przez liczbę jednocześnie testowanych hipotez |
| Benjamini-Hochberg | „kontrola FDR” | Metoda kontroli odsetka fałszywych odkryć, bardziej elastyczna niż korekta Bonferroniego |
| SRM | „anomalia podziału ruchu” | Błąd algorytmu randomizacji powodujący nierównomierny podział użytkowników między warianty |
| Statsig | „platforma Statsig” | Zintegrowana platforma analityczno-wdrożeniowa, należąca do OpenAI od 2025 r. |
| GrowthBook | „narzędzie GrowthBook” | Otwarta platforma eksperymentalna (MIT) odczytująca dane bezpośrednio z SQL |
| mSPRT | „test mSPRT” | Algorytm statystyczny będący fundamentem współczesnych testów sekwencyjnych |

## Materiały uzupełniające

- [GrowthBook – How to A/B test AI: A practical guide](https://blog.growthbook.io/how-to-a-b-test-ai-a-practical-guide/)
- [Statsig – Beyond Prompts: Data-driven LLM optimization](https://www.statsig.com/blog/llm-optimization-online-experimentation)
- [Statsig vs GrowthBook Comparison](https://www.statsig.com/perspectives/ab-testing-feature-flags-comparison-tools)
- [Deng et al. – CUPED Method](https://www.exp-platform.com/Documents/2013-02-CUPED-ImprovingSensitivityOfControlledExperiments.pdf)
- [Howard – Confidence Sequences](https://arxiv.org/abs/1810.08240)
