# Przełączniki zabijania, wyłączniki automatyczne i żetony kanaryjskie

> Wyłącznik awaryjny (Kill switch) to zewnętrzna flaga logiczna (np. klucz w Redis, flaga funkcji/feature flag, cyfrowo podpisana konfiguracja) przechowywana poza zasięgiem zapisu agenta, która pozwala na natychmiastowe zatrzymanie jego pracy. Wyłącznik automatyczny (Circuit breaker) działa w sposób bardziej szczegółowy: reaguje na konkretne wzorce zachowań (np. pięć identycznych wywołań narzędzi z rzędu), wstrzymując ryzykowną ścieżkę wykonania i eskalując problem do człowieka. Token kanarkowy (Canary token) opiera się na klasycznym wzorcu Honeypota – fałszywym credentialu lub wpisie w bazie danych, którego agent nie ma powodu odczytywać, a próba interakcji z nim natychmiast generuje alert. W infrastrukturze Kubernetes, filtry sieciowe eBPF (np. Cilium) mogą w warstwie jądra przekierować ruch sieciowy z odizolowanego poda (poddanego kwarantannie) do Honeypota w celu analizy powłamaniowej. Publikowane benchmarki Cilium wykazują opóźnienie przesyłu danych (P99 latency) na poziomie poniżej milisekundy; czas reakcji systemu zależy głównie od szybkości propagacji nowych reguł w klastrze, a nie od samego eBPF. Detektory statystyczne (EWMA, CUSUM) adaptujące się do ruchomej średniej mogą zostać oszukane przez powolne zmiany zachowania (dryf) – dlatego należy je wzmocnić poprzez nałożenie sztywnych, niezmiennych ograniczeń o charakterze konstytucyjnym.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulator z trzema detektorami: wyłącznik awaryjny, wyłącznik automatyczny, kanarek)
**Wymagania wstępne:** Faza 15 · 13 (Zarządcy kosztami), Faza 15 · 10 (Tryby uprawnień)
**Czas:** ~60 minut

## Problem

Zarządcy kosztów (Lekcja 13) określają, jak wysokie opłaty może wygenerować agent. Nie ograniczają jednak rodzaju działań, jakie agent może podjąć w ramach przyznanego budżetu. Agent posiadający limit wydatków rzędu 50 USD wciąż może wykraść klucze API, opublikować szkodliwy post w mediach społecznościowych lub usunąć bazę danych – krytyczne zniszczenia są często bardzo tanie w przeliczeniu na tokeny zapytań.

W tej lekcji omówimy trzy typy detektorów uzupełniających kontrolę kosztów:

1. **Wyłącznik awaryjny (Kill switch):** Logiczny przycisk odcięcia zasilania znajdujący się całkowicie poza zasięgiem agenta.
2. **Wyłącznik automatyczny (Circuit breaker):** Analizator wzorców zachowań, który blokuje konkretną, wadliwą ścieżkę wykonania.
3. **Token kanarkowy (Canary token):** Element przynęty (Honeypot), którego agent nie powinien modyfikować ani odczytywać; interakcja z nim natychmiast wyzwala alarm.

Wszystkie te techniki wywodzą się z tradycyjnej inżynierii systemów i powstały na długo przed erą dużych modeli językowych (LLM). Nowością jest jednak powierzchnia ataku: agenci przetwarzają niezweryfikowane treści zewnętrzne (Lekcja 11), modyfikują własną pamięć i mogą łączyć pozornie bezpieczne kroki w złośliwe sekwencje. Opisane tu detektory są skuteczne, ponieważ nie polegają na informacjach zwrotnych generowanych przez samego agenta.

## Koncepcja

### Wyłączniki awaryjne (Kill switches)

Wyłącznik awaryjny to flaga logiczna (boolean), którą agent może jedynie odczytywać. Metody wdrożenia:

- **Flagi funkcji w usługach typu SaaS:** LaunchDarkly, Statsig, Unleash. Czas propagacji zmian wynosi zazwyczaj kilka sekund.
- **Klucz w bazie Redis (polling):** Prosta metoda wymagająca odpytywania bazy przez agenta in każdej iteracji.
- **Podpisany cyfrowo plik konfiguracyjny w chmurze:** Agent weryfikuje podpis przy każdym uruchomieniu i odrzuca konfiguracje bez ważnego podpisu.
- **Sygnały systemowe lub usunięcie kontenera:** Wykorzystanie poleceń `docker kill`, `kubectl delete pod` lub bezpośrednie zatrzymanie procesu w systemie operacyjnym.

Cechy poprawnie zaprojektowanego wyłącznika awaryjnego:

- Agent nie ma technicznej możliwości zmiany stanu flagi (np. nie posiada uprawnień zapisu do systemu przechowującego stan wyłącznika).
- Stan wyłącznika jest weryfikowany przed każdą kolejną akcją, a nie tylko raz podczas startu sesji.
- Po aktywacji wyłącznika agent nie wykonuje żadnych operacji zewnętrznych, w tym logowania do systemów, do których posiada uprawnienia.
- Przywrócenie działania agenta (ponowne włączenie) wymaga świadomej i ręcznej decyzji administratora, a nie automatycznego wygaśnięcia blokady.

### Wyłączniki automatyczne (Circuit breakers)

Wyłącznik automatyczny blokuje konkretną, podejrzaną ścieżkę wykonania, a nie całą sesję agenta. Klasyczna maszyna stanowa (zgodnie z wzorcem Nygarda z 2007 r.) obejmuje stany:

- **Zamknięty (Closed):** Normalna praca, akcje są dozwolone.
- **Otwarty (Open):** Wykryto anomalię, wywołanie akcji jest blokowane.
- **Półotwarty (Half-Open):** Po okresie wyciszenia (cool-off) dozwolone są pojedyncze próby testowe; powodzenie zamyka wyłącznik, a jakikolwiek kolejny błąd ponownie go otwiera.

Przykładowe warunki aktywacji wyłącznika w systemach agentowych:

- Wykrycie pętli: pięć identycznych wywołań tego samego narzędzia z rzędu.
- Wykrycie awarii: pięć kolejnych błędów narzędzia przy różnych parametrach wejściowych.
- Przekroczenie limitów dynamiki kosztów (patrz Lekcja 13).
- Reguły warunkowe: uruchomienie niebezpiecznego narzędzia (np. usuwania plików) bezpośrednio po odczytaniu danych z niezaufanego źródła (patrz Lekcja 11).

### Tokeny kanarkowe (Canary tokens)

Tokeny kanarkowe (Honeytokeny) to specjalne, nieużywane zasoby, z którymi agent w normalnych warunkach nie powinien wchodzić w interakcję. Każdy dostęp do nich generuje alarm bezpieczeństwa.

Przykłady zastosowania:

- **Fałszywe klucze API:** Umieszczenie nieaktywnego klucza `AWS_SECRET_ACCESS_KEY` w środowisku testowym. Próba jego użycia przez agenta pozwala na natychmiastowe wykrycie ataku.
- **Przynęta w bazie danych (Honey record):** Wpis w bazie oznaczony unikalnym identyfikatorem; odczytanie lub modyfikacja tego rekordu natychmiast uruchamia powiadomienie.
- **Plik przynęta (Honey file):** Pozornie atrakcyjny plik w katalogu projektu, którego odczyt lub edycja wskazuje na niepożądane działanie agenta.
- **Zatruwanie pamięci testowej (Memory canary):** Fałszywy wpis dodany do kontekstu agenta. Jeśli pojawi się on w zewnętrznych zapytaniach sieciowych, oznacza to eksfiltrację danych.

Projektowanie tokenów kanarkowych musi być dostosowane to konkretnego zadania. Jeśli agent wejdzie w interakcję z kanarkiem w ramach prawidłowego działania, wygeneruje to fałszywy alarm (szum).

### Łączenie limitów statystycznych ze sztywnymi regułami

Detektory statystyczne (takie jak EWMA, CUSUM czy współczynnik z-score w analizie wywołań narzędzi) dynamicznie dostosowują się do zmieniającego się profilu obciążenia (linii bazowej). Choć ułatwia to obsługę naturalnych wahań ruchu, tworzy podatność na ataki typu slow-rate (dryf kontradyktoryjny) – napastnik może zwiększać aktywność na tyle wolno, by detektor nie wykrył anomalii.

Sztywne reguły o charakterze konstytucyjnym (patrz Lekcja 17) są niezmienne. Przykładowo, reguła „bezwzględny zakaz wysyłania wiadomości e-mail na adres `secrets@`” jest prosta w weryfikacji i odporna na powolną manipulację profilu ruchu. Optymalna architektura powinna łączyć obie metody: statystyka eliminuje standardowy szum, a sztywne reguły blokują wyrafinowane próby ominięcia detektorów.

### Izolacja sesji i kwarantanna z użyciem eBPF

Filtry sieciowe Cilium oparte na eBPF pozwalają na automatyczne przekierowanie ruchu sieciowego z izolowanego poda (poddanego kwarantannie) do bezpiecznego Honeypota bezpośrednio w warstwie jądra systemu operacyjnego. Publikowane benchmarki wykazują, że opóźnienie przesyłu pakietów (P99 latency) wynosi poniżej milisekundy. Czas od momentu podjęcia decyzji o nałożeniu kwarantanny do faktycznego zablokowania portów zależy od propagacji reguł w Kubernetesie i wynosi zazwyczaj kilkaset milisekund (w zależności od rozmiaru klastra). Takie rozwiązanie daje dwie korzyści: po pierwsze, zapobiega wyciekowi rzeczywistych danych; po drugie, pozwala na bezpieczną obserwację zachowania agenta w izolowanym środowisku. To ta sama idea co token kanarkowy, zaimplementowana w innej warstwie infrastruktury: agent ujawnia swoje intencje poprzez próby wykonania zablokowanych operacji.

### Czego nie wykryje żaden z detektorów?

- **Ataki semantyczne oparte na dozwolonych krokach:** Sytuacje, w których każda pojedyncza akcja z osobna nie narusza żadnych reguł bezpieczeństwa, lecz ich połączona sekwencja wywołuje szkody (złożony scenariusz awarii opisywany w Lekcji 10).
- **Ataki modyfikujące same detektory:** Jeśli agent odczyta złośliwą instrukcję typu „wyłącz tokeny kanarkowe przed wykonaniem zadania” i posiada uprawnienia do modyfikacji konfiguracji bezpieczeństwa, system zostanie skompromitowany. Dlatego detektory i konfiguracja kanarków muszą być zlokalizowane w systemach, do których agent nie ma dostępu.

## Przykład praktyczny

Skrypt `code/main.py` symuluje działanie agenta monitorowanego przez trzy detektory: zewnętrzny wyłącznik awaryjny (kill switch), wyłącznik automatyczny (circuit breaker) aktywujący się po 5 powtarzających się wywołaniach narzędzi oraz plik kanarkowy (canary), którego odczytanie natychmiast generuje alert bezpieczeństwa. Kod testowy przetwarza syntetyczną trajektorię agenta i prezentuje blokowanie działań w różnych scenariuszach awarii.

## Zadanie wdrożeniowe

Plik `outputs/skill-tripwire-design.md` służy to weryfikacji stosu detektorów w projekcie agenta i wskazuje potencjalne podatności (brak wyłącznika awaryjnego, brak tokenów kanarkowych lub zbyt wysokie progi aktywacji wyłączników automatycznych).

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Potwierdź, że wyłącznik automatyczny (circuit breaker) aktywuje się w 5. iteracji (piąte identyczne wywołanie narzędzia), a token kanarkowy generuje alert w iteracji 9. (próba odczytu pliku przynęty).
2. Dodaj statystyczny detektor oparty na EWMA dla częstotliwości wywołań narzędzi. Zasymuluj trajektorię ataku z powolnym wzrostem częstotliwości (dryf) i wykaż, że detektor nie generuje alertu. Następnie nałóż sztywny limit (np. maksymalnie 50 wywołań na 10 minut) i potwierdź jego skuteczność w tym samym scenariuszu.
3. Zaprojektuj zestaw tokenów kanarkowych dla agenta przeglądarkowego (patrz Lekcja 11). Wskaż co najmniej trzy typy przynęt i opisz, jakie konkretnie zachowania mają wykrywać.
4. Zapoznaj się z zasadami sieciowymi (Network Policies) w Cilium. Opisz techniczny przebieg kwarantanny sieciowej: wskaż regułę filtru, docelowy pod, sposób przekierowania ruchu oraz mechanizm alarmowy. Co ma największy wpływ na opóźnienie czasu blokady (od decyzji do pierwszego przekierowanego pakietu)?
5. Opracuj procedurę ponownego uruchomienia agenta po aktywacji wyłącznika awaryjnego (kill switch). Określ, kto posiada uprawnienia do przywrócenia sesji, jakie analizy powłamaniowe muszą zostać udokumentowane oraz jakie zmiany w konfiguracji agenta należy wprowadzić przed jego startem.

## Kluczowe terminy

| Termin | Co mówią potocznie | Co to dokładnie oznacza |
|---|---|---|
| Wyłącznik awaryjny (Kill switch) | „Przycisk wyłącznika” | Flaga logiczna umieszczona poza zasięgiem agenta, sprawdzana przed wykonaniem każdego kroku |
| Wyłącznik automatyczny (Circuit breaker) | „Blokada wzorca” | Zabezpieczenie zatrzymujące konkretną akcję po wykryciu zapętlenia lub powtarzających się awarii |
| Token kanarkowy (Canary token) | „Przynęta” | Nieużywany zasób (np. plik, wpis w bazie), którego odczytanie lub edycja uruchamia alert |
| Honeypot | „Piaskownica testowa” | Odizolowane środowisko służące do bezpiecznego monitorowania i badania zachowania agenta |
| EWMA | „Średnia krocząca” | Wykładniczo ważona średnia ruchoma, stosowana do detekcji anomalii statystycznych |
| CUSUM | „Suma skumulowana” | Algorytm wykrywania zmian w charakterystyce sygnału lub linii bazowej |
| Sztywny limit (Hard limit) | „Niezmienna reguła” | Stałe, niezmienne ograniczenie bezpieczeństwa (np. limit wywołań na minutę) |
| Granica konstytucyjna | „Reguła nadrzędna” | Niezmienna zasada postępowania wpisana w system (patrz Lekcja 17), której agent nie może modyfikować |

## Dalsza lektura

- [Anthropic — Pomiar autonomii agentów w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — wyłączniki awaryjne i automatyczne w systemach autonomicznych.
- [Microsoft Agent Framework — HITL i nadzór](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) — wzorce orkiestracji i zarządzania.
- [OWASP LLM / Agentic Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — wytyczne w zakresie detekcji i reagowania na incydenty.
- [Cilium — Zasady sieciowe i eBPF](https://docs.cilium.io/en/stable/security/network/) — kwarantanna kontenerów i integracja z systemami Honeypot.
- [Anthropic — Konstytucja Claude'a (styczeń 2026 r.)](https://www.anthropic.com/news/claudes-constitution) — koncepcja twardych reguł konstytucyjnych.
