# Ruch testowy (Shadow Traffic), wdrożenia Canary i stopniowe wdrażanie modeli LLM

> **Przegląd cen z dnia 2026-04.** Poniższe wartości odzwierciedlają stawki dostawców zarejestrowane w momencie publikacji tej lekcji; przed zacytowaniem ich w dalszej części tekstu zweryfikuj je z aktualną dokumentacją.

> Wdrażanie modeli LLM łączy najtrudniejsze aspekty inżynierii oprogramowania: brak jednoznacznych testów jednostkowych, rozproszone scenariusze awarii oraz opóźnione informacje zwrotne. Bezpieczny proces wdrożenia obejmuje trzy etapy:
> (1) **Tryb cienia (Shadow serve)**: powielanie zapytań produkcyjnych do nowego modelu (kandydata) i rejestrowanie jego zachowania bez zwracania odpowiedzi użytkownikowi; pozwala to wykryć problemy infrastrukturalne, ale nie weryfikuje jakości;
> (2) **Wdrożenie typu Canary (Canary deployment)**: stopniowe przekierowywanie ruchu (np. 1% → 10% → 25% → 50% → 100%) z kontrolą wskaźników (bramek) na każdym etapie – monitorujemy opóźnienia, koszty zapytań, współczynnik błędów/odmów, rozkład długości generowanego tekstu oraz bezpośrednie oceny użytkowników;
> (3) **Testy A/B**: porównywanie alternatywnych wariantów funkcjonalnych po potwierdzeniu pełnej stabilności nowej infrastruktury.
> Niedeterminizm modeli jest cechą stałą – ta sama konfiguracja wejścia może dawać do 15% wariancji w dokładności ze względu na brak łączności operacji zmiennoprzecinkowych na GPU (FP non-associativity) oraz zmiany rozmiaru partii (dynamic batching). Koszt wnioskowania jest zmienny, a nie stały – model oferujący o 20% wyższą jakość może być 3-krotnie droższy w utrzymaniu. Szybkość wycofania zmian (rollback) jest kluczowa: jeśli wymaga ona pełnego redeploymentu kodu, Twój system jest zbyt wolny. Logika routingu powinna znajdować się w dynamicznej konfiguracji (feature flags), a sam model w rejestrze modeli pod unikalnym hashem (digest) – wtedy wycofanie zmian sprowadza się do zmiany flagi i powrotu do poprzedniego modelu w kilka sekund.

**Typ:** Teoria i praktyka
**Języki:** Python (stdlib, uproszczony symulator wdrażania typu canary)
**Wymagania wstępne:** Faza 17 · 13 (Monitorowanie i obserwowalność), faza 17 · 21 (Testy A/B dla modeli LLM)
**Czas:** ~60 minut

## Cele naukowe

- Rozróżnianie trybu cienia (shadow – porównanie w tle), wdrożenia canary (stopniowe włączanie ruchu na produkcji) oraz testów A/B (porównanie wersji funkcjonalnych na stabilnej infrastrukturze).
- Omówienie pięciu kluczowych metryk monitorowanych przy wdrożeniach canary modeli LLM (opóźnienia, koszt zapytania, współczynnik błędów/odmów, rozkład długości odpowiedzi, oceny użytkowników).
- Wyjaśnienie, dlaczego niedeterminizm modeli (sięgający 15%) redefiniuje pojęcie „stabilności” wdrożenia produkcyjnego.
- Zaprojektowanie procedury awaryjnego wycofania zmian (rollback) trвающей kilka sekund (przełączenie flag konfiguracyjnych) zamiast kilku godzin (redeploy kodu).

## Problem

Wdrażasz nowy model. Testy offline (evals) wykazały wzrost dokładności o 3%. Uruchamiasz go na produkcji. W ciągu pierwszej doby koszty rosną o 40%, wskaźnik negatywnych ocen od użytkowników (kciuk w dół) wzrasta o 8%, a klienci zgłaszają w ticketach dziwne, niespójne odpowiedzi. Decydujesz o wycofaniu wersji. Proces ponownego wdrożenia starego kodu zajmuje jednak 3 godziny.

Każdego z tych problemów można było uniknąć. Tryb cienia (shadow traffic) wykryłby 40-procentowy wzrost kosztów zanim model trafiłby do pierwszego klienta. Z kolei wdrożenie canary automatycznie zatrzymałoby się na etapie 10% ruchu, widząc wzrost negatywnych ocen. Wycofanie zmian za pomocą zmiany konfiguracji (feature flags) potrwałoby zaledwie 30 sekund. Stosowanie odpowiednich praktyk wdrożeniowych pozwala połączyć optymizm testów offline z rzeczywistym zadowoleniem użytkowników końcowych.

## Koncepcja

### Tryb cienia (Shadow Traffic)

Nowy model (kandydat) otrzymuje kopie tych samych zapytań, które trafiają na produkcję. Odpowiedzi są zapisywane w logach i nie trafiają do użytkownika końcowego. Metoda ta nie wpływa na działanie aplikacji. Analizie podlegają:

- Zbieżność odpowiedzi (porównanie semantyczne z wersją produkcyjną).
- Liczba generowanych tokenów (analiza różnic w kosztach).
- Opóźnienia (latency).
- Wskaźniki błędów oraz odmów odpowiedzi (refusal rate).

Zastosowanie: wykrywanie wzrostu kosztów, anomalii w długości odpowiedzi, błędów technicznych i problemów z odmowami. Tryb cienia to tzw. smoke test (test dymny) infrastruktury, a nie ostateczny test jakości odpowiedzi.

### Wdrożenie typu Canary (Canary Rollout)

Stopniowe przełączanie ruchu użytkowników na nowy model z weryfikacją wskaźników jakościowych. Typowa ścieżka: 1% → 10% → 25% → 50% → 100%. Proces jest wstrzymywany lub cofany w przypadku przekroczenia limitów (bramek) dla 5 kluczowych metryk:

1. **Percentyle opóźnień (P50, P95, P99)**: wskaźnikiem alarmowym jest np. wzrost opóźnienia P99 nowej wersji o ponad 1.5x w stosunku do linii bazowej.
2. **Koszt na zapytanie**: średnia cena za zapytanie. Alarm przy wzroście o >20% ponad normę.
3. **Współczynnik błędów i odmów (Error & Refusal Rate)**: błędy serwerowe API 5xx oraz jawne odmowy odpowiedzi ze strony modelu. Alarm przy 2-krotnym wzroście.
4. **Rozkład długości odpowiedzi**: średnia liczba tokenów wyjściowych oraz percentyl P99. Alarm przy nagłych zmianach rozkładu (np. model staje się zbyt gadatliwy).
5. **Oceny i zgłoszenia użytkowników**: wskaźnik negatywnych ocen (kciuk w dół) oraz ticketów. Alarm przy 1.5-krotnym wzroście.

### Niedeterminizm modeli (LLM Non-determinism)

Identyczne zapytania wejściowe mogą dawać różne odpowiedzi na poziomie pojedynczych tokenów. Wynika to z:

- Braku łączności operacji zmiennoprzecinkowych na GPU (FP non-associativity) – kolejność sumowania zależy od bieżącego obciążenia karty.
- Dynamicznego tworzenia partii (dynamic batching) – ten sam prompt jest przetwarzany w partii o zmiennym rozmiarze (np. raz w batch=16, raz w batch=128).
- Parametru temperatury i próbkowania (gdy temperatura > 0).

W praktyce dokładność modelu w kolejnych testach na tym samym zbiorze może wahać się do 15%. Pojęcie „stabilności” nowego wdrożenia oznacza zatem, że metryki mieszczą się w dopuszczalnym przedziale wariancji (szumie informacyjnym), a nie są stuprocentowo identyczne. Bramki alarmowe muszą być skonfigurowane powyżej poziomu tego szumu.

### Koszt jako zmienna biznesowa

Model o 20% dokładniejszy może wygenerować 3-krotnie wyższy koszt pojedynczego wywołania. Średni koszt zapytania jest jedną z kluczowych bramek kontrolnych. Wdrożenie dokładniejszego modelu, który drastycznie pogarsza jednostkową ekonomię aplikacji (unit economics), jest podstawą do wycofania wersji.

### Natychmiastowy Rollback jako podstawa bezpieczeństwa

- **Zarządzanie flagami (Feature Flags)**: procentowy podział ruchu konfigurowany dynamicznie w locie (trwa to ułamki sekund).
- **Przypinanie wersji (Model Pinning)**: wersja modelu zdefiniowana przez jednoznaczny hash (digest) w rejestrze, zapobiegająca automatycznym, niekontrolowanym aktualizacjom.
- **Rollback**: wycofanie zmian polega na natychmiastowym przełączeniu flagi w systemie konfiguracji na poprzedni stabilny hash modelu. Trwa to sekundy, a nie godziny.

Jeśli Twoja infrastruktura wymaga ponownego wdrożenia kodu lub restartu kontenerów w celu wycofania wersji modelu, usprawnij ten proces przed uruchomieniem jakichkolwiek testów produkcyjnych.

### Narzędzia i infrastruktura

- **Argo Rollouts / Flagger**: kontrolery progresywnego wdrażania na Kubernetes. Integrują się z routingiem ważonym w siatkach usług (service mesh).
- **Istio / Linkerd**: pozwalają na precyzyny, ważony podział ruchu sieciowego na poziomie infrastruktury.
- **KServe / Seldon Core**: silniki serwowania modeli (model serving) ze wsparciem dla wdrożeń canary.
- **Systemy Feature Flags (LaunchDarkly, Flagsmith, Unleash)**: umożliwiają natychmiastową zmianę kierunku ruchu na poziomie logicznym aplikacji, bez zmian w infrastrukturze.

### Częstotliwość weryfikacji metryk (Evaluation Window)

Bramki canary powinny analizować dane w interwałach 5–15 minut w zależności od wolumenu ruchu. Przykładowo, 1% ruchu przy 10 zapytaniach na minutę daje 50–150 pomiarów na jedno okno weryfikacji. Jest to wystarczająca próba dla oceny opóźnień, ale zbyt mała i podatna na szum w przypadku analizy ocen użytkowników. Przejście do kolejnego kroku wdrożenia powinno nastąpić dopiero po zebraniu statystycznie istotnej próby danych na danym etapie.

### Rola testów A/B

Jeśli nowy model wprowadza widoczne zmiany funkcjonalne (inna stylistyka odpowiedzi, zmieniona struktura kosztów), po pomyślnym zakończeniu fazy canary warto uruchomić długoterminowy test A/B (np. podział ruchu 50/50). Jeśli nowa wersja jest jedynie optymalizacją techniczną (np. spadek kosztów przy tej samej jakości), po zaliczeniu bramek canary można od razu przełączyć ruch na 100%.

### Kluczowe statystyki do zapamiętania

- Przykładowe etapy wdrażania canary: 1% → 10% → 25% → 50% → 100%.
- Szum niedeterminizmu: wahania wyników do 15% między testami na identycznych danych wejściowych.
- Pięć kluczowych metryk canary: opóźnienia, koszty zapytań, współczynnik błędów/odmów, długość odpowiedzi, oceny użytkowników.
- Bramka kosztowa: wzrost kosztów o >20% traktowany jest jako przekroczenie limitu i powód do rollbacku.
- Czas wycofania zmian (Rollback): liczony w sekundach, a nie godzinach.

## Praktyczne zastosowanie

Skrypt `code/main.py` symuluje proces wdrażania typu canary ze sztucznie wprowadzonymi regresjami. Raportuje, na którym etapie proces wdrażania zostaje zatrzymany i która bramka kontrolna wywołała alert.

## Zadanie wdrożeniowe

W ramach tej lekcji przygotowano plik `outputs/skill-rollout-runbook.md`. Narzędzie to, na podstawie parametrów modelu-kandydata, linii bazowej oraz poziomu tolerancji ryzyka, projektuje kompletny plan wdrożenia (Shadow → Canary → 100%).

## Ćwiczenia

1. Uruchom `code/main.py`. Wprowadź sztuczną regresję kosztów na poziomie 25%. Na którym etapie wdrożenie typu canary zostanie przerwane?
2. Nowy model wykazuje o 3% wyższą dokładność w testach offline, ale koszt zapytania rośnie o 18%. Czy wdrożysz go na produkcję? Przedstaw argumenty za i przeciw w zależności od założeń biznesowych projektu.
3. Zaprojektuj procedurę rollbacku, która od momentu wykrycia błędu do pełnego wycofania wersji trwa mniej niż 60 sekund. Wymień niezbędne komponenty infrastruktury.
4. Wahania wyników wynikające z niedeterminizmu wynoszą w Twoich testach ±7%. Skonfiguruj progi alarmowe bramek canary tak, aby uniknąć fałszywych alertów. Jakie mnożniki zastosujesz?
5. W fazie shadow traffic wykryto nagły wzrost kosztów o 40% przed uruchomieniem canary. Napisz regułę alertu, która powinna wyzwolić powiadomienie w tej fazie.

## Słownik pojęć

| Termin | Popularne określenie | Rzeczywiste znaczenie |
|------|----------------|--------------------------------------|
| Shadow Traffic | „ruch w tle” | Kopiowanie zapytań produkcyjnych i przesyłanie ich do testowanego modelu w celu weryfikacji logów |
| Canary Deployment | „wdrożenie kanaryjskie” | Progresywne udostępnianie nowej wersji modelu wybranym grupom użytkowników |
| Rollout Gates | „bramki wdrożeniowe” | Zdefiniowane progi metryk, których przekroczenie wstrzymuje lub cofa proces wdrażania |
| Niedeterminizm | „wahania odpowiedzi” | Nieredukowalna cecha modeli LLM powodująca drobne różnice w odpowiedziach na to samo zapytanie |
| Feature Flags | „flagi funkcji” | Dynamiczne zarządzanie konfiguracją w locie, umożliwiające natychmiastowe wycofanie zmian (rollback) |
| Model Pinning | „przypinanie hasha” | Wskazywanie konkretnego, niezmiennego hasha (digest) wersji modelu w rejestrze |
| Argo Rollouts | „progresywny K8s” | Kontroler dla Kubernetes automatyzujący wdrożenia typu canary oraz rollbacki |
| KServe | „serwowanie modeli w K8s” | Standardowa platforma do hostowania modeli na Kubernetes ze wsparciem dla wdrożeń canary |
| Istio Traffic Splitting | „podział ruchu” | Mechanizm siatki usług (service mesh) służący do ważonego rozdzielania pakietów sieciowych |

## Materiały uzupełniające

- [TianPan – Safely rolling out LLM features without breaking production](https://tianpan.co/blog/2026-04-09-llm-gradual-rollout-shadow-canary-ab-testing)
- [MarkTechPost – Safely deploying ML models to production](https://www.marktechpost.com/2026/03/21/safely-deploying-ml-models-to-production-four-control-strategies-a-b-canary-interleaved-shadow-testing/)
- [APXML – Advanced LLM Deployment Patterns](https://apxml.com/courses/mlops-for-large-models-llmops/chapter-4-llm-deployment-serving-optimization/advanced-llm-deployment-patterns)
- [Argo Rollouts Documentation](https://argo-rollouts.readthedocs.io/)
- [Flagger Documentation](https://docs.flagger.app/)
