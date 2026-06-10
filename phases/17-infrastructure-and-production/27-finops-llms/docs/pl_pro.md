# FinOps dla LLM — ekonomia jednostkowa (unit economics) i alokacja kosztów in systemach wielodostępnych

> Klasyczne podejście FinOps zawodzi w przypadku kosztów związanych z LLM. Koszty generowane są przez transakcyjne zużycie tokenów, a nie czas działania infrastruktury. Tradycyjne tagowanie zasobów nie działa – pojedyncze zapytanie do API to krótkotrwałe zdarzenie, a nie stały zasób chmurowy. W tym modelu każda decyzja inżynieryjna (np. konstrukcja promptu, rozmiar okna kontekstowego czy długość generowanego tekstu) bezpośrednio przekłada się na koszty finansowe. Standardem staje się alokacja kosztów w trzech wymiarach, które należy monitorować od samego początku: na użytkownika (`user_id`) – kluczowe przy modelach rozliczeń per-seat; na zadanie (`task_id` + `route`) – pomocne przy optymalizacji kosztów poszczególnych funkcji produktu; oraz na najemcę/klienta (`tenant_id`) – niezbędne do wyznaczania ekonomii jednostkowej i kalkulacji umów. Koszty tokenów należy dzielić na cztery warstwy (prompt wejściowy, wywołania narzędzi, pamięć kontekstowa, odpowiedź wyjściowa) – wrzucanie wszystkiego do jednego worka uniemożliwia optymalizację. W architekturach wielodostępnych (multi-tenant) zaleca się stosowanie stopniowanych limitów: limit częstotliwości zapytań na najemcę (ustawiony na 2-3x średniego szczytowego zapotrzebowania, zwracający błąd 429 i nagłówek Retry-After); dzienny limit wydatków (1,5-3x zakontraktowanego budżetu, wyzwalający ostrzeżenie); oraz automatyczny wyłącznik awaryjny (kill switch) aktywowany przy nagłym skoku zużycia (np. gdy Z-score kosztów > 4), który wstrzymuje obsługę i powiadamia dyżurnego inżyniera. Metody alokacji kosztów obejmują: tagowanie metadanych, integrację telemetrii z systemami bilingowymi (najwyższa dokładność), próbkowanie statystyczne, alokację opartą na modelach estymacji, strumieniowanie zdarzeń (np. Kafka) oraz raportowanie w czasie rzeczywistym. Kluczowe metryki powinny być zorientowane na biznes (np. koszt pojedynczej rozwiązanej sprawy, koszt wygenerowanego raportu), a nie suche wskaźniki typu $/M tokenów. Próba wstecznego tagowania logów zawsze kończy się niepowodzeniem – system rozliczeniowy należy zaprojektować i zaimplementować równolegle z integracją samego modelu.

**Typ:** Teoria / Nauka
**Języki:** Python (stdlib, symulator atrybucji kosztów zabawek z wyłącznikiem awaryjnym)
**Wymagania wstępne:** Faza 17 · Lekcja 13 (obserwowalność), faza 17 · Lekcja 14 (buforowanie)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnij, dlaczego tradycyjne podejście FinOps zawodzi przy rozliczaniu modeli LLM, i opisz trzy kluczowe wymiary alokacji kosztów.
- Wymień cztery warstwy zużycia tokenów (prompt, narzędzia, pamięć, odpowiedź) i wyjaśnij, dlaczego ich agregacja utrudnia optymalizację wydatków.
- Zaprojektuj trzystopniowy system limitów (rate limit -> limit wydatków -> kill switch) dla aplikacji typu multi-tenant.
- Dobierz biznesowe metryki jednostkowe (np. koszt rozwiązanej sprawy lub wygenerowanego zasobu) zamiast surowych kosztów tokenów $/M.

## Problem

Otrzymujesz fakturę na 40 000 USD. Nie jesteś jednak w stanie określić:
- Który najemca (klient) wygenerował te koszty.
- Która funkcja produktu była za to odpowiedzialna.
- Czy doszło do nadużyć ze strony konkretnego użytkownika.
- Czy głównym czynnikiem był rozrost promptów (prompt bloat), wywołania narzędzi (function calling), czy narzut pamięci kontekstowej.

Tradycyjne tagowanie i agregacja kosztów po stronie dostawcy chmury sprawdza się przy stałej infrastrukturze (np. instancjach EC2 czy pamięci S3), gdzie tagi są na stałe przypisane do zasobów. Zapytania do API LLM są z kolei transakcyjne i krótkotrwałe – musisz sam oznaczyć i przekazać identyfikatory użytkownika, zadania i najemcy w momencie wykonywania zapytania. Próba odtworzenia tych powiązań wstecznie (post-facto) jest obarczona dużym marginesem błędu.

## Koncepcja

### Trzy wymiary atrybucji

**Na użytkownika** (`user_id`): precyzyjnie określa koszty generowane przez poszczególnych użytkowników. Kluczowe przy modelach licencjonowania per-seat, negocjacjach umów oraz wykrywaniu użytkowników generujących nietypowe obciążenie.

**Na zadanie** (`task_id` + `route`): wskazuje koszty powiązane z konkretnymi funkcjonalnościami w aplikacji. Pozwala podejmować świadome decyzje o rozwoju, optymalizacji lub rezygnacji z rentownych funkcji.

**Na najemcę** (`tenant_id`): pozwala określić rentowność poszczególnych klientów. Niezbędne do kalkulacji marży (unit economics), planowania cen odnowień kontraktów (renewals) oraz wyznaczania limitów w planach abonamentowych.

Zaimplementuj śledzenie wszystkich trzech wymiarów w punkcie wywołania API od pierwszego dnia pracy nad systemem. Próby wdrożenia tego wstecznie są skomplikowane i nieefektywne.

### Cztery warstwy tokenów

| Warstwa zużycia | Przykład użycia | Szacowany % całkowitych kosztów |
|-------|---------|-------------------------|
| Prompt (Wejście) | System prompt + zapytanie użytkownika | 40-60% |
| Narzędzia (Tools) | Dane z wykonania funkcji przekazywane modelowi | 20-40% (wysoki udział w systemach agentowych) |
| Pamięć (Context) | Historia konwersacji / dokumenty wstrzyknięte przez RAG | 10-30% |
| Odpowiedź (Wyjście) | Tekst wygenerowany przez model | 10-30% |

Łączenie wszystkich czterech razem sprawia, że optymalizacja jest ślepa. Rozdziel je w swoim schemacie atrybucji.

### Stopniowane limity (Enforcement Ladder)

1. **Limit częstotliwości zapytań (Rate Limit)** per najemca: Ustawiony na poziomie 2-3x średniego szczytowego zapotrzebowania. Przekroczenie zwraca kod błędu 429 z nagłówkiem `Retry-After`. Klient napotyka chwilowe ograniczenie, co chroni system przed nagłą destabilizacją kosztową.
2. **Dzienny limit wydatków (Daily Spend Limit)** per najemca: Ustawiony na 1,5-3x zakontraktowanego budżetu dziennego. Przekroczenie wyzwala automatyczne zaostrzenie limitu częstotliwości i wysyła powiadomienie do działu obsługi klienta (Customer Success).
3. **Automatyczny wyłącznik awaryjny (Kill Switch)**: Aktywowany w sytuacji, gdy koszty najemcy przekraczają standardową linię bazową (np. wartość Z-score > 4). Automatycznie wstrzymuje obsługę tego klienta, wysyła alert do dyżurnego inżyniera i eskaluje sprawę do zespołów operacyjnych oraz obsługi.

### Wzorce alokacji kosztów

- **Tagowanie i agregacja**: oznaczanie żądań w nagłówkach metadanych i późniejsza agregacja logów. Metoda prosta, ale mało precyzyjna.
- **Integracja telemetrii (Telemetry Linker)**: powiązanie rozproszonych śladów (traces) z systemem billingowym za pomocą unikalnych Trace ID. Zapewnia najwyższą precyzję i jest standardem w dojrzałych zespołach.
- **Próbkowanie statystyczne i ekstrapolacja**: analiza 5-10% ruchu i pomnożenie wyników. Rozwiązanie tanie w realizacji, ale pomija nagłe skoki kosztów w nielicznych, skrajnych zapytaniach.
- **Estymacja modelowa**: wykorzystanie modeli regresyjnych do szacowania kosztów na podstawie historycznych danych bez tagów.
- **Strumieniowanie zdarzeń (Event Sourcing)**: przesyłanie zdarzeń kosztowych bezpośrednio do kolejki (np. Kafka lub AWS Kinesis) w czasie rzeczywistym.

### Wskaźniki biznesowe jako metryki jednostkowe

Kalkulacja $/M tokenów to metryka czysto techniczna. Wskaźniki biznesowe powinny mierzyć:
- Koszt obsługi pojedynczego zgłoszenia (support ticket).
- Koszt wytworzenia pojedynczego artykułu/dokumentu.
- Koszt pomyślnie wykonanej misji przez agenta.
- Koszt minuty aktywnej sesji użytkownika.

Powiązanie kosztów z realną wartością biznesową dostarczaną przez produkt pozwala na skuteczną optymalizację.

### Schemat danych dla alokacji kosztów

```yaml
trace_id: abc123
  user_id: u_42
  tenant_id: t_7
  task_id: task_classify_doc
  route: model_haiku
  layers:
    prompt_tokens: 1800
    tool_tokens: 600
    memory_tokens: 400
    response_tokens: 150
  cost_usd: 0.0135
  cached_input: true
  batch: false
```

Generuj taki rekord przy każdym wywołaniu API i zapisuj go w data lake do późniejszej agregacji. Śledzenie to integruje się bezpośrednio z systemem obserwowalności (Faza 17 · Lekcja 13).

### Skumulowane oszczędności (Stacked Optimization)

Połączenie czterech mechanizmów: buforowania, przetwarzania wsadowego, dynamicznego routingu oraz optymalizacji bramki pozwala uzyskać maksymalne oszczędności:
- Buforowanie L2 (Faza 17 · Lekcja 14): do 10x tańsze przetwarzanie promptów wejściowych.
- Przetwarzanie wsadowe (Batching, Faza 17 · Lekcja 15): 50% zniżki na zapytania asynchroniczne.
- Dynamiczny routing do tańszych modeli (Faza 17 · Lekcja 16): do 60% redukcji kosztów.
- Bramka AI (Faza 17 · Lekcja 19): inteligentna obsługa błędów, failover i ponawianie prób.

W optymalnym wariancie skumulowanym koszty mogą spaść do zaledwie 5-10% początkowych założeń bazowych. Większość zespołów wdraża 2-3 z tych mechanizmów; nieliczni integrują wszystkie cztery.

### Kluczowe dane do zapamiętania

- Wymiary alokacji kosztów: użytkownik, zadanie, najemca (tenant).
- Cztery warstwy zużycia tokenów: prompt (wejście), narzędzia, pamięć (kontekst), odpowiedź (wyjście).
- Wyłącznik awaryjny (Kill Switch): aktywowany przy nagłym skoku kosztów o Z-score > 4.
- Metryka jednostkowa: koszt realizacji celu biznesowego (np. rozwiązanej sprawy), a nie techniczny koszt tokenów $/M.
- Skumulowana optymalizacja: możliwość obniżenia wydatków końcowych do 5-10% kosztów bazowych.

## Kod demonstracyjny

Skrypt `code/main.py` symuluje działanie usługi LLM w środowisku wielodostępnym (multi-tenant) zabezpieczonej trzystopniowym systemem limitów. Symulacja wstrzykuje klienta generującego nagły, ogromny ruch i demonstruje automatyczne wyzwolenie wyłącznika awaryjnego.

## Rezultat zadania

W ramach tej lekcji powstanie plik `outputs/skill-finops-plan.md`. Na podstawie specyfiki produktu oraz zakładanej skali działania definiuje on schemat alokacji kosztów oraz zasady progów bezpieczeństwa.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Przy jakiej wartości wskaźnika Z-score aktywuje się wyłącznik awaryjny? Jak dobrać ten próg w warunkach produkcyjnych?
2. Zaprojektuj panel kontrolny (dashboard) kosztów w podziale na najemców i konkretne zadania. Jakie 5 wykresów/widoków przygotujesz w pierwszej kolejności?
3. Twój kluczowy klient (najemca) generuje ujemną marżę (ujemną ekonomikę jednostkową). Zaproponuj trzy możliwe działania naprawcze, szeregując je od najmniej do najbardziej uciążliwych dla klienta.
4. Oblicz szacowany koszt pojedynczego rozwiązanego zgłoszenia w systemie wsparcia: przyjmij 3M tokenów na jedno zgłoszenie, wolumen ~800 zgłoszeń dziennie oraz stawki z uwzględnieniem buforowania promptów dla nowego modelu (np. GPT-5).
5. Rozważ, czy próby alokacji kosztów wstecznie (post-facto) mogą dać wiarygodne wyniki. Kiedy takie podejście jest dopuszczalne?

## Słownik pojęć

| Termin | Jak się potocznie mówi | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| Alokacja na użytkownika | „koszt per użytkownik” | Przypisywanie `user_id` do każdego zapytania do API |
| Alokacja na zadanie | „koszt danej funkcji” | Powiązanie `task_id` i `route` z konkretnym modułem aplikacji |
| Alokacja na najemcę | „koszt per klient” | Przypisywanie `tenant_id` w celu liczenia marży jednostkowej |
| Cztery warstwy tokenów | „podział kosztów zapytania” | Rozbicie kosztów na prompt, wywołania narzędzi, pamięć kontekstową i odpowiedź |
| Limit częstotliwości (Rate Limit) | „zabezpieczenie 429” | Maksymalna dozwolona liczba żądań na sekundę na jednego najemcę |
| Dzienny limit wydatków | „dzienny limit budżetu” | Maksymalny dozwolony koszt dobowy dla jednego klienta wyzwalający alerty |
| Wyłącznik awaryjny (Kill Switch) | „bezpiecznik” | Automatyczna blokada obsługi klienta przy nagłym skoku kosztów o Z-score > 4 |
| Koszt realizacji celu | „koszt jednostki biznesowej” | Mierzenie kosztu w odniesieniu do dostarczonej wartości (np. zamkniętej sprawy), a nie do tokenów |
| Integracja z telemetrią | „śledzenie bilingowe” | Metoda alokacji oparta na powiązaniu rozproszonych śladów (traces) z billingiem |
| Skumulowana optymalizacja | „optymalizacja warstwowa” | Połączenie buforowania, routingu i przetwarzania wsadowego obniżające koszty o 90% |

## Materiały uzupełniające

- [Fundacja FinOps — przegląd FinOps for AI](https://www.finops.org/wg/finops-for-ai-overview/)
- [Szkoła FinOps — przewodnik dotyczący kosztów jednostkowych na rok 2026](https://finopsschool.com/blog/cost-per-unit/)
- [Digital Applied – przypisanie kosztów agenta LLM 2026](https://www.digitalapplied.com/blog/llm-agent-cost-attribution-guide-production-2026)
- [PointFive — zarządzane LLM w Azure OpenAI](https://www.pointfive.co/blog/finops-for-ai-economics-of-managed-llms-in-azure-open-ai)
