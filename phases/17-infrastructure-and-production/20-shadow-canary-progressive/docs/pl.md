# Shadow Traffic, wdrożenie Canary i stopniowe wdrażanie dla LLM

> Wdrożenia LLM łączą najtrudniejsze elementy wdrażania oprogramowania: brak testów jednostkowych, rozproszone tryby awarii, opóźnione sygnały. Sekwencja jest następująca: (1) tryb cienia — zduplikuj żądania produktu do potencjalnego modelu, zarejestruj, porównaj bez wpływu na użytkownika; uwzględnia oczywiste problemy związane z dystrybucją, ale nie stanowi gwarancji jakości; (2) wdrożenie kanarek — progresywne przesunięcie ruchu 10% → 25% → 50% → 75% → 100% z bramkami na każdym stopniu; śledź percentyle opóźnień, koszt/żądanie, wskaźnik błędów/odmów, rozkład długości wyników, wskaźnik opinii użytkowników; (3) Testy A/B dla różnych alternatyw po potwierdzeniu stabilności. Niedeterminizm jest nieredukowalny — do 15% zmienności dokładności w seriach z identycznymi danymi wejściowymi ze względu na brak asocjatywności procesora graficznego FP oraz wariancję wielkości partii. Koszt jest zmienny, a nie stały — model lepszy o 20% może być 3 razy droższy za połączenie. Szybkość wycofywania ma decydujące znaczenie: jeśli wycofywanie wymaga ponownego wdrożenia, oznacza to, że jesteś za wolny. Polityka znajduje się w konfiguracji/flagach; modelka żyje w rejestrze z przypiętymi podsumowaniami; wycofanie = odwrócenie polityki + przywrócenie progu + przypięcie starego modelu w kilka sekund.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulator postępu kanarków zabawkowych)
**Wymagania wstępne:** Faza 17 · 13 (obserwowalność), faza 17 · 21 (testowanie A/B)
**Czas:** ~60 minut

## Cele nauczania

- Rozróżnij tryb cienia (porównanie o zerowym wpływie), kanarkowy (progresywny ruch na żywo) i A/B (porównanie potwierdzone stabilnością).
- Wymień pięć wskaźników kanaryjskich specyficznych dla LLM (opóźnienie, koszt/żądanie, błąd/odmowa, rozkład długości wyjściowej, opinie użytkowników).
- Wyjaśnij, dlaczego niedeterminizm LLM (do 15%) zmienia znaczenie słowa „stabilny” we wdrożeniu.
- Zaprojektuj ścieżkę przywracania, która zajmie kilka sekund (odwrócenie zasad), a nie godziny (ponowne wdrożenie).

## Problem

Wysyłasz nowy model. Ewaluacje offline wykazują wzrost dokładności o 3%. Włączasz to na produkcji. W ciągu 24 godzin koszt wzrósł o 40%, liczba kciuków w dół wzrosła o 8%, a trzy zgłoszenia klientów zgłaszają „dziwne odpowiedzi”. Cofasz się. Ponowne wdrożenie zajmuje 3 godziny. Twój weekend jest zrujnowany.

Każdej części tego można było uniknąć. Tryb cienia wychwyciłby 40% wzrost kosztów, zanim jakikolwiek użytkownik by to zauważył. Canary zatrzymałby się na 10%, gdyby kciuk w dół się przesunął. Cofnięcie flagi zasad zajęłoby 30 sekund. Dyscyplina wypełnia lukę między „ocenami offline wygląda dobrze” a „prawdziwymi użytkownikami są zadowoleni”.

## Koncepcja

### Tryb cienia

Kandydat otrzymuje te same żądania, co produkcja; dane wyjściowe są rejestrowane, a nie zwracane użytkownikom. Zerowy wpływ na użytkownika. Dziennik:

- Zawartość wyjściowa (porównanie z produkcją).
- Liczba tokenów (delta kosztów).
- Opóźnienie.
- Odmowa i błąd.

Haki: wzrost kosztów, regresja długości, oczywiste zmiany w odmowie, twarde błędy. NIE wyłapuje: jakość delta, jaką dostrzegliby użytkownicy. Shadow to test dymny, a nie test jakości.

### Wprowadzenie na rynek Canary

Progresywna zmiana ruchu z bramkami. Typowa progresja: 1% → 10% → 25% → 50% → 75% → 100%. Bramka na 5 metrykach na każdym kroku:

1. **Percentyle opóźnienia** – P50, P95, P99. Naruszenie: kanarek ma P99 > 1,5x w punkcie wyjściowym.
2. **Koszt na żądanie** — mieszany $. Naruszenie: >20% powyżej wartości bazowej.
3. **Współczynnik błędów/odmów** — 5xx plus wyraźne odmowy. Naruszenie: 2x wartość bazowa.
4. **Rozkład długości wyjściowych** — średnia + P99. Naruszenie: zmiana dystrybucji.
5. **Wskaźnik opinii użytkowników** — kciuki w dół / zgłoszenia. Naruszenie: 1,5x wartość bazowa.

### Niedeterminizm to nowa wariancja

Identyczne wejścia dają nieidentyczne wyjścia. Powody:

- Brak asocjatywności GPU FP (kolejność redukcji zmiennoprzecinkowej różni się w zależności od partii).
- Różnice w wielkości partii (ten sam monit w partii 128 w porównaniu z partią 16).
- Pobieranie próbek (temperatura > 0).

Zmierzone: do 15% zmienności dokładności między przebiegami na identycznych zestawach ewaluacyjnych. „Stabilny” we wdrożeniu oznacza, że ​​dane mieszczą się w oczekiwanej rozbieżności, a nie są identyczne z wartościami wyjściowymi. Ustaw bramki powyżej poziomu szumów.

### Koszt jest zmienną

Model lepszy o 20% może być 3 razy droższy za połączenie. Koszt/żądanie to jedna z pięciu bramek. Wysyłka „lepszego” modelu, który psuje ekonomię jednostki, jest przypadkiem wycofania.

### Wycofanie się to broń

- Flaga polityki (system flag funkcji): odwróć procent w konfiguracji; zajmuje sekundy.
- Przypinanie modelu (podsumowanie rejestru): przypięty model nie jest automatycznie aktualizowany.
- Wycofanie = przywrócenie flagi + ustawienie przypiętego podsumowania na poprzednie. Sekundy, nie godziny.

Jeśli Twój stos wymaga ponownego wdrożenia w celu wycofania zmian, napraw to przed wykonaniem rzutu.

### Oprzyrządowanie

**Wdrożenia Argo** / **Flagger** — kontrolery dostaw progresywnych Kubernetes. Integracja z routingiem ważonym Istio/Linkerd.

**Routing ważony Istio** — podział ruchu na poziomie siatki usług.

**KServe / Seldon Core** — model serwujący z wbudowanym kanarkiem.

**Flagi funkcji** — LaunchDarkly, Flagsmith, Unleash. Odwrócenie na poziomie zasad, bez ponownego wdrażania.

### Pomiar rytmu

Bramy Canary sprawdzają co 5–15 minut, w zależności od natężenia ruchu. 1% ruchu przy 10 wymaganiach/min daje 50–150 punktów danych na okno — wystarczające do opóźnienia, ale hałaśliwe, aby uzyskać opinie użytkowników. 10% daje ~10x więcej. Postępy powinny zostać wstrzymane na tyle długo, aby zgromadzić wystarczającą liczbę próbek na każdym etapie.

### Krok A/B jest opcjonalny

Jeśli nowy model wyraźnie się różni (inne zachowanie, inna krzywa kosztów, inny ton), wykonaj test A/B na poziomie 50% po przejściu kanarków. Jeśli to tylko ulepszona wersja, przejdź do 100%, gdy miną bramy kanaryjskie.

### Liczby, które powinieneś zapamiętać

- Progresja kanarkowa: 1% → 10% → 25% → 50% → 75% → 100%.
- Pułap niedeterminizmu: do 15% wariancji między seriami na identycznych danych wejściowych.
- Pięć kanaryjskich wskaźników: opóźnienie, koszt, błąd/odmowa, długość wyniku, opinie użytkowników.
- Bramka kosztowa: >20% powyżej wartości bazowej stanowi naruszenie.
- Wycofywanie: sekundy, a nie godziny.

## Użyj tego

`code/main.py` symuluje wdrożenie typu canary z wstrzykniętymi regresjami. Raportuje, na którym etapie wdrożenie się zatrzymuje i która bramka została uruchomiona.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-rollout-runbook.md`. Biorąc pod uwagę model kandydata, linię bazową i tolerancję ryzyka, projektuje cień → kanarek → plan 100%.

## Ćwiczenia

1. Uruchom `code/main.py`. Wprowadź regresję kosztów o 25%. Na którym etapie kanarek się zatrzymuje?
2. Twój nowy model ma 3% wzrost dokładności w trybie offline, ale koszt/żądanie wynosi +18%. Czy to statek? Zależy od polityki — wpisz obie ścieżki.
3. Zaprojektuj wycofanie, które zajmie od początku do końca mniej niż 60 sekund. Wymień wymaganą infrastrukturę.
4. Niedeterminizm pokazuje ±7% w twojej ewaluacji. Ustaw bramy kanaryjskie, aby nie wywołać fałszywego alarmu. Jakich mnożników używasz?
5. Tryb cienia generuje wzrost kosztów o 40% przed kanarkiem. Napisz regułę alertu uruchamianą w cieniu.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Tryb cienia | „duplikuj do nowego” | Bezproblemowe wysyłanie do kandydata w celu logowania |
| Kanarek | „ruch progresywny” | Stopniowe wdrażanie udostępniane użytkownikom z bramkami |
| Bramy | „kontrole wdrożenia” | Progi metryczne blokujące postęp |
| Niedeterminizm | „Wariancja LLM” | Nieredukowalne różnice między rundami |
| Flaga polityczna | „przywrócenie flagi” | Wycofywanie na poziomie konfiguracji, sekundy, a nie godziny |
| Pin modelowy | „podsumowanie rejestru” | Niezmienne odniesienie do wersji modelu |
| Wdrożenia Argo | „Progresywny K8” | Natywny kontroler Canary/rollback dla Kubernetes |
| KServ | „wnioskowanie K8” | Model serwujący z prymitywami kanarkowymi |
| Istio ważone | „podział siatki” | Rozdzielacz ruchu w siatce usług |

## Dalsze czytanie

— [TianPan — udostępnianie funkcji AI bez przerywania produkcji](https://tianpan.co/blog/2026-04-09-llm-gradual-rollout-shadow-canary-ab-testing)
— [MarkTechPost — Bezpieczne wdrażanie modeli uczenia maszynowego](https://www.marktechpost.com/2026/03/21/safely-deploying-ml-models-to-production-four-control-strategies-a-b-canary-interleaved-shadow-testing/)
- [APXML — zaawansowane wzorce wdrażania LLM](https://apxml.com/courses/mlops-for-large-models-llmops/chapter-4-llm-deployment-serving-optimization/advanced-llm-deployment-patterns)
– [Dokumentacja Argo Rollouts](https://argo-rollouts.readthedocs.io/)
- [Dokumentacja osób zgłaszających] (https://docs.flagger.app/)