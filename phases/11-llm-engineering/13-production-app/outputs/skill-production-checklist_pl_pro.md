---

name: skill-production-checklist
description: Lista kontrolna gotowości produkcyjnej dla aplikacji LLM — wymagania, progi testowe i kryteria wdrożeniowe dla każdego komponentu
version: 1.0.0
phase: 11
lesson: 13
tags: [production, deployment, llm, architecture, scaling, cost, observability, guardrails]

---

# Produkcyjna lista kontrolna dla aplikacji LLM

Przygotowując aplikację LLM do wdrożenia produkcyjnego, zweryfikuj poniższe punkty w zalecanej kolejności. Każda sekcja posiada określone kryteria weryfikacyjne i progi akceptacji.

## 1. Bezpieczeństwo (Krytyczne - Ship Blockers)

Każdy z poniższych punktów musi zostać zaliczony przed wdrożeniem kodu na produkcję.

| Funkcja | Kryterium akceptacji | Metoda weryfikacji |
|-------|------------------|--------------|
| Klucze API w zmiennych środowiskowych | Brak kluczy API zapisanych na stałe w kodzie | Komenda `grep -r "sk-" --include="*.py"` nie zwraca żadnych wyników |
| Aktywne guardrails wejściowe | Blokowanie znanych wzorców prompt injection | Wysłanie zapytania: „Zignoruj wszystkie poprzednie instrukcje” zwraca komunikat o blokadzie |
| Redakcja danych osobowych (PII) | Wykrywanie i maskowanie adresów e-mail, PESEL, numerów kart i telefonów | Wysłanie zapytania: „Mój PESEL to...” – dane zostają zredagowane przed wysłaniem do API LLM |
| Walidacja wyjścia | Blokowanie niebezpiecznych treści generowanych przez model | Zweryfikuj, czy model nie może zwrócić poleceń typu `DROP TABLE`, `rm -rf` czy `exec()` |
| Ograniczanie liczby wywołań | Wdrożony limit zapytań na użytkownika (Rate Limiting) | Wysłanie 100 zapytań od jednego użytkownika w 10 sekund – co najmniej 50 ostatnich zostaje odrzuconych (429) |
| Autoryzacja endpointów | Brak dostępu do modeli LLM dla nieuwierzytelnionych użytkowników | Zapytanie `curl /v1/chat` bez nagłówka Auth zwraca kod błędu HTTP 401 |
| Konfiguracja CORS | Dostęp do API ograniczony wyłącznie do zaufanych domen chmurowych | Zapytanie z nagłówkiem `Origin: evil.com` zostaje odrzucone |
| Limit tokenów wejściowych | Odrzucanie zbyt długich zapytań użytkowników | Wysłanie tekstu o długości 50k tokenów zwraca kod HTTP 413 lub powoduje automatyczne skrócenie |

## 2. Niezawodność (Stabilność w pierwszym tygodniu)

Zabezpieczenia zapobiegające awariom i incydentom na produkcji.

| Funkcja | Kryterium akceptacji | Metoda weryfikacji |
|-------|------------------|--------------|
| Retries z backoffem | Automatyczne ponawianie zapytań (3 próby dla błędów 5xx, exponential backoff) | Przerwanie połączenia sieciowego w połowie żądania – w logach widoczne są próby ponowienia |
| Kaskada modeli (Fallback Chain) | Co najmniej 2 modele zdefiniowane w łańcuchu | Wyłączenie dostępu do głównego modelu – aplikacja serwuje odpowiedź z modelu rezerwowego |
| Limity czasu (Timeouts) | Maksymalnie 30 sekund dla wywołań zewnętrznych API | Symulacja wolnej odpowiedzi LLM (60s) – połączenie zostaje przerwane po 30s |
| Łagodna degradacja | Awaria cache lub bazy wektorowej nie paraliżuje działania aplikacji | Wyłączenie bazy Redis – zapytania nadal są obsługiwane (choć wolniej i drożej) |
| Sonda stanu (Health Check) | Endpoint `/health` zwraca status wszystkich systemów pomocniczych | Zapytanie `GET /health` zwraca poprawną strukturę JSON ze statusem cache, RAG i API LLM |
| Strumieniowanie (Streaming) | Czas do pierwszego tokenu (TTFT) poniżej 500 ms | Wywołanie czatu ze strumieniowaniem – czas odebrania pierwszego pakietu wynosi stabilnie < 500 ms |
| Bezpieczne błędy | Logi błędów wewnętrznych nie wyciekają do użytkownika | Wymuszenie błędu 500 – użytkownik widzi ogólny komunikat, a nie pełny stack trace |

## 3. Optymalizacja kosztów (Month-One Economics)

Zabezpieczenia chroniące przed niekontrolowanymi fakturami za API.

| Funkcja | Kryterium akceptacji | Metoda weryfikacji |
|-------|------------------|--------------|
| Śledzenie kosztów transakcji | Każde zapytanie loguje liczbę tokenów oraz koszt USD | Logi zapytań zawierają pola wejściowe, wyjściowe i koszt finansowy |
| Aktywny cache semantyczny | Współczynnik trafień (Hit Rate) powyżej 20% dla zapytań powtarzalnych | Statystyki pamięci podręcznej pokazują poprawne trafienia po wysłaniu 1000 zapytań testowych |
| Konfiguracja TTL cache | Wpisy w cache wygasają po określonym czasie (np. 1 godzina) | Zapytanie wysłane po upływie TTL generuje cache miss i odpytuje model |
| Śledzenie kosztów na użytkownika | Agregacja wydatków w podziale na ID użytkowników | API monitoringu pozwala wygenerować listę 10 najbardziej kosztownych użytkowników |
| Alerty budżetowe | System powiadomień przy osiągnięciu limitu dobowego | Ustaw limit dobowy na $10, wyślij zapytania za $8.50 – system generuje alert |
| Routing modeli | Pytania o niskiej złożoności są kierowane do tańszych modeli | Proste zapytania trafiają do gpt-4o-mini, a skomplikowane do gpt-4o / Claude Sonnet |
| Limit tokenów wyjściowych | Sztywne ograniczenie długości odpowiedzi (max_output_tokens) | Wywołanie promptu o max_output_tokens = 512 – odpowiedź nigdy nie przekracza tego limitu |

**Wzór estymacji kosztów miesięcznych:**
```
Miesięczny koszt LLM = DAU x zapytania_na_użytkownika x 30 x (1 - cache_hit_rate) x (średnia_wejścia x cena_wejścia + średnia_wyjścia x cena_wyjścia) / 1 000 000
```

**Sugerowane progi kosztowe w zależności od skali:**

| Dzienni użytkownicy (DAU) | Docelowy koszt na zapytanie | Maksymalny budżet miesięczny |
|-----|--------------------------------|----------------|
| 1k | < 0.005 USD | < 750 USD |
| 10k | < 0.003 USD | < 4 500 USD |
| 100k | < 0.001 USD | < 15 000 USD |

## 4. Obserwowalność (Monitorowanie i debugowanie)

Narzędzia ułatwiające diagnostykę problemów produkcyjnych.

| Funkcja | Kryterium akceptacji | Metoda weryfikacji |
|-------|------------------|--------------|
| Logi w formacie JSON | Każda transakcja zapisuje jedną linię JSON w logach | Log zawiera klucze: request_id, user_id, model, tokeny, latency_ms, koszt |
| Śledzenie transakcji (Tracing) | End-to-end tracing z podziałem czasu trwania etapów | Transakcja w systemie APM pokazuje czas: guardrails (5ms) + cache (2ms) + LLM (3200ms) |
| Percentyle opóźnień | Monitorowanie wskaźników P50, P95 i P99 | Na próbie 1000 zapytań: opóźnienie P50 wynosi < 2s, a P99 < 10s |
| Kategoryzacja błędów | Zliczanie i podział błędów według typów | Dashboard prezentuje podział: błędy API, blokady guardrails, błędy limitu czasu (timeouts) |
| Statystyki bazy cache | Monitorowanie wskaźników hit/miss rate | Wywołanie endpointu `GET /v1/cache/stats` zwraca poprawny JSON ze statystykami |
| Logowanie wariantów A/B | Zapisywanie informacji o wersji szablonu promptu | Log każdego zapytania zawiera wersję promptu (np. v1/v2) dla celów porównawczych |
| Logowanie ocen ewaluacji | Zapisywanie długości odpowiedzi i opóźnień do analiz | Dane są gromadzone w bazie do analiz regresyjnych offline |

## 5. Wdrażanie i wersjonowanie promptów

Prompty to kod aplikacji. Traktuj je z takim samym rygorem.

| Funkcja | Kryterium akceptacji | Metoda weryfikacji |
|-------|------------------|--------------|
| Wersjonowanie szablonów | Każdy szablon posiada jednoznaczny identyfikator wersji | Zmiana promptu tworzy nową wersję w systemie, stara wersja pozostaje dostępna |
| Spójne testy A/B | Podział ruchu oparty na deterministycznym haszowaniu ID użytkownika | Dany użytkownik zawsze widzi ten sam wariant eksperymentu w ramach sesji |
| Szybki rollback | Możliwość przywrócenia starego promptu w czasie < 1 minuty | Zmiana konfiguracji w panelu/pliku natychmiast przekierowuje ruch |
| Walidacja parametrów | Weryfikacja obecności zmiennych przed renderowaniem szablonu | Brak zmiennej wymaganej w szablonie rzuca czytelny błąd walidacji zamiast KeyError |
| Separacja instrukcji | Prompt systemowy i zapytanie użytkownika przekazywane w osobnych polach | Treść systemowa nie jest łączona z surowym tekstem od użytkownika |

## 6. Gotowość do skalowania (Skalowalność)

Elementy opcjonalne przy starcie, ale niezbędne przy wzroście ruchu o rząd wielkości.

| Funkcja | Kryterium akceptacji | Metoda weryfikacji |
|-------|------------------|--------------|
| Asynchroniczne wywołania | Brak blokowania wątków serwera przy oczekiwaniu na API | 50 jednoczesnych zapytań – zużycie CPU serwera pozostaje na poziomie < 30% |
| Pooling połączeń HTTP | Ponowne wykorzystywanie otwartych połączeń HTTP | Narzędzia sieciowe pokazują utrzymywanie otwartych połączeń (keep-alive) z API LLM |
| Bezstanowość serwera | Architektura umożliwiająca skalowanie poziome | Uruchomienie 2 instancji serwera za Load Balancerem – ruch rozkłada się równomiernie |
| Kolejkowanie zadań (Queues) | Długotrwałe operacje (np. streszczanie) trafiają do kolejki | Zapytanie natychmiast zwraca ID zadania, a wynik pobiera się odpytywaniem (polling) |
| Testy obciążeniowe (Load Testing) | Obsługa 100 współbieżnych użytkowników ze wskaźnikiem błędów < 5% | Testy obciążeniowe (np. Locust, wrk) przechodzą pomyślnie na środowisku staging |

## Harmonogram wdrożenia nowego projektu

1. **Dzień 1:** Uruchomienie serwera API + szablony promptów + pojedyncze wywołania LLM z mechanizmem retry.
2. **Dzień 2:** Implementacja guardrails wejściowych i wyjściowych + obsługa błędów sieciowych.
3. **Dzień 3:** Uruchomienie semantycznej bazy cache + podstawowy tracker kosztów.
4. **Dzień 4:** Strumieniowanie odpowiedzi (SSE) + endpoint `/health`.
5. **Dzień 5:** Logowanie strukturyzowane JSON + śledzenie transakcji APM.
6. **Tydzień 2:** Wdrożenie testów A/B promptów + panel wersjonowania i szybkich rollbacków.
7. **Tydzień 3:** Konfiguracja łańcuchów rezerwowych (fallback models) + mechanizmy łagodnej degradacji.
8. **Tydzień 4:** Testy obciążeniowe + optymalizacje asynchroniczne I/O + skalowanie poziome maszyn.

## Szybka diagnostyka awarii na produkcji

Jeśli system zgłasza problemy, weryfikuj komponenty w następującej kolejności:

1. **Użytkownicy zgłaszają błędy aplikacji?** Sprawdź endpoint `/health`, następnie przeanalizuj poziom błędów w logach, a na koniec zweryfikuj statusy u dostawców API LLM.
2. **Odpowiedzi generują się zbyt wolno?** Zweryfikuj wskaźnik opóźnień P99, następnie sprawdź wskaźnik hit rate bazy cache, a na koniec przeanalizuj czasy odpowiedzi API LLM w śladach transakcji.
3. **Nagły wzrost kosztów?** Sprawdź koszty w ujęciu pojedynczych zapytań, przeanalizuj współczynnik trafień cache, zidentyfikuj najbardziej kosztownych użytkowników i sprawdź, czy ostatnie zmiany w promptach nie zwiększyły drastycznie liczby przesyłanych tokenów.
4. **Spadek jakości odpowiedzi?** Sprawdź, czy nie wdrożono nowej wersji promptów, zweryfikuj trafność wyszukiwania bazy RAG, sprawdź, czy dostawca API nie zmienił domyślnej wersji modelu.
5. **Wyciek danych lub incydent bezpieczeństwa?** Sprawdź logi blokad guardrails (nagły spadek liczby blokad sugeruje awarię filtrów), przeanalizuj zapytania pod kątem nietypowych wzorców i natychmiast dokonaj rotacji kluczy API.
