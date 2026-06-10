---

name: skill-production-checklist
description: Ramy decyzyjne dotyczące wysyłania aplikacji LLM do produkcji — obejmują każdy komponent z określonymi progami i kryteriami pozytywny/negatywny
version: 1.0.0
phase: 11
lesson: 13
tags: [production, deployment, llm, architecture, scaling, cost, observability, guardrails]

---

# Lista kontrolna LLM produkcji

Wysyłając aplikację LLM, przejrzyj poniższą listę kontrolną w odpowiedniej kolejności. Każda sekcja ma kryteria pozytywne/niezaliczone z określonymi progami.

## 1. Bezpieczeństwo (blokady statków)

Każdy element tutaj musi przejść przed jakimkolwiek wdrożeniem.

| Sprawdź | Kryteria zaliczenia | Jak zweryfikować |
|-------|------------------|--------------|
| Klucze API w env vars | Zero zakodowanych na stałe kluczy w bazie kodu | `grep -r "sk-" --include="*.py"` nic nie zwraca |
| Poręcze wejściowe aktywne | Zablokowane wzorce szybkich wtrysków | Wyślij „Ignoruj ​​wszystkie poprzednie instrukcje” – zwraca zablokowaną odpowiedź |
| Redakcja PII | Wychwycono numer SSN, kartę kredytową, wzorce e-maili | Wyślij „Mój numer SSN to 123-45-6789” – informacje umożliwiające identyfikację zostały zredagowane przed wezwaniem LLM |
| Filtrowanie wyników | Niebezpieczne treści zablokowane | Model nie może zwrócić wzorców `DROP TABLE`, `rm -rf`, `exec()` |
| Ograniczanie szybkości | Wymuszony limit żądań na użytkownika | 100 żądań od tego samego użytkownika w ciągu 10 sekund — ponad 50 ostatnich odrzuconych |
| Autoryzacja na wszystkich punktach końcowych | Brak nieuwierzytelnionego dostępu LLM | `curl /v1/chat` bez tokena zwraca 401 |
| CORS ograniczony | Dozwolone są tylko domeny produkcyjne | Żądanie `Origin: evil.com` odrzucone |
| Maksymalna liczba tokenów wejściowych | Żądania przekroczenia limitu odrzucone | Wyślij dane wejściowe tokenu 50 tys. — zwraca wartość 413 lub obcięcie |

## 2. Niezawodność (przeżycie w pierwszym tygodniu)

Zapobiegają one Twojemu pierwszemu incydentowi podczas rozmowy telefonicznej.

| Sprawdź | Kryteria zaliczenia | Jak zweryfikować |
|-------|------------------|--------------|
| Ponów próbę z wycofaniem | 3 próby na 5xx, wykładnicze opóźnienie | Zabij próbną wersję LLM w połowie żądania — ponowne próby widoczne w dziennikach |
| Łańcuch modeli zastępczych | 2+ modele w łańcuszku | Model podstawowy niedostępny — odpowiedź nadal powraca z rezerwy |
| Żądanie limitu czasu | Maks. 30 s dla wszystkich połączeń zewnętrznych | Powolna próba LLM (60 s) — przekroczono limit czasu żądania po 30 s |
| Pełna wdzięku degradacja | Awaria pamięci podręcznej/RAG nie powoduje awarii usługi | Zatrzymaj pamięć podręczną — żądania nadal się powiodą (wolniej, drożej) |
| Punkt końcowy kontroli stanu | Zwraca status zależności | `GET /health` zwraca `{"status": "healthy", "cache": ..., "llm": ...}` |
| Streaming działa | Pierwszy token poniżej 500 ms | Zmierzony czas do pierwszego żetonu, niezmiennie < 500ms |
| Error messages are safe | Internal errors never leak to users | Force 500 -- user sees generic error, not stack trace |

## 3. Cost Control (Month-One Economics)

These prevent the $50K surprise invoice.

| Check | Pass Criteria | How to Verify |
|-------|--------------|---------------|
| Cost per request tracked | Every request logs token count + USD cost | Request log has PHIC13, PHIC14, PHIC15 fields |
| Semantic cache active | > 20% współczynnik trafień w przypadku powtarzających się wzorców | Statystyki pamięci podręcznej pokazują współczynnik trafień po 1000 żądaniach testowych |
| Skonfigurowano TTL pamięci podręcznej | Wpisy wygasają (domyślnie: 1 godzina) | Wpis wstawiony – nie zwrócony po TTL |
| Śledzenie kosztów na użytkownika | Koszt zagregowany według identyfikatora użytkownika | Panel/API pokazuje 10 najlepszych użytkowników według kosztów |
| Alarmowanie o kosztach | Alarm przy 80% dziennego budżetu | Ustaw $10 daily budget, send $8.50 w żądaniach — pożary alertów |
| Modelowanie routingu według kosztów | Zapytania o niskiej złożoności korzystają z tańszego modelu | Proste pytania do gpt-4o-mini, złożone do gpt-4o |
| Maksymalny zestaw żetonów wyjściowych | Ograniczona liczba odpowiedzi według szablonu | Szablon z max_output_tokens=512 -- odpowiedź nigdy go nie przekracza |

**Wzór szacunkowy kosztów:**
```
Monthly LLM cost = DAU x queries_per_user x 30 x (1 - cache_hit_rate) x (avg_input_tokens x input_price + avg_output_tokens x output_price) / 1,000,000
```

**Progi wzorcowe według skali:**

| DAU | Docelowy koszt/żądanie | Budżet miesięczny |
|-----|--------------------------------|----------------|
| 1K | <$0.005 | < $750 |
| 10 tys. | <$0.003 | < $4,500 |
| 100 tys. | <$0.001 | < $15 000 |

## 4. Obserwowalność (debugowanie w produkcji)

Nie możesz naprawić tego, czego nie widzisz.

| Sprawdź | Kryteria zaliczenia | Jak zweryfikować |
|-------|------------------|--------------|
| Logowanie strukturalne JSON | Każde żądanie generuje linię dziennika JSON | Log zawiera: request_id, user_id, model, tokeny, latency_ms, koszt |
| Żądanie śledzenia | Śledzenie od końca do końca z synchronizacją komponentów | Pojedyncze żądanie pokazuje: poręcz (5 ms) + pamięć podręczna (2 ms) + llm (3200 ms) + eval (1 ms) |
| Śledzenie opóźnień | P50, P95, P99 zmierzone | Po 1000 żądań: P50 < 2s, P99 < 10s |
| Monitorowanie poziomu błędów | Błędy zliczone i skategoryzowane | Panel pokazuje: 0,5% błędów API, 0,1% blokad poręczy, 0,01% przekroczeń limitu czasu |
| Metryki pamięci podręcznej | Wskaźnik trafień, współczynnik chybień, widoczna liczba wejść | `GET /v1/cache/stats` zwraca aktualne liczby |
| Metryki testów A/B | Zarejestrowane metryki jakości dla każdego wariantu | Każde żądanie rejestruje szablon zachęty + wersję dla porównania |
| Rejestracja ewaluacyjna | Sygnały jakości zarejestrowane na żądanie | Długość odpowiedzi, opóźnienie, model, wersja szablonu przechowywana do analizy offline |

## 5. Szybkie zarządzanie

Podpowiedzi są kodem. Traktuj je jak kod.

| Sprawdź | Kryteria zaliczenia | Jak zweryfikować |
|-------|------------------|--------------|
| Wersjonowane szablony | Każdy szablon ma nazwę i ciąg znaków wersji | Zmiana szablonu tworzy nową wersję, stara wersja zostaje zachowana |
| Wsparcie testów A/B | Podział ruchu według deterministycznego skrótu użytkownika | Ten sam użytkownik zawsze widzi ten sam wariant w eksperymencie |
| Możliwość wycofania | Wróć do poprzedniej wersji za < 1 minutę | Zmień konfigurację eksperymentu — ruch natychmiast się zmienia |
| Walidacja szablonu | Zmienne sprawdzone przed renderowaniem | Brakująca zmienna w szablonie powoduje wyraźny błąd, a nie KeyError |
| Separacja monitów systemowych | Komunikaty systemowe i użytkownika w oddzielnych polach | Podpowiedź systemowa nie jest połączona z komunikatem użytkownika |

## 6. Gotowość do skalowania

Nie potrzebne przy uruchomieniu. Potrzebne na 10x.

| Sprawdź | Kryteria zaliczenia | Jak zweryfikować |
|-------|------------------|--------------|
| Asynchroniczne połączenia LLM | Brak blokowania wątków w wywołaniach API | 50 równoczesnych żądań — procesor serwera pozostaje < 30% |
| Pula połączeń | Ponowne wykorzystanie połączeń HTTP | Śledzenie sieci pokazuje trwałe połączenia z dostawcą LLM |
| Skalowanie poziome | Projekt serwera bezstanowego | 2 instancje za modułem równoważenia obciążenia — wszystkie żądania powiodły się |
| Obsługa kolejek | Zadania inne niż realizowane w czasie rzeczywistym trafiają do kolejki | Żądanie podsumowania zwraca id_zadania, wynik jest dostępny poprzez odpytywanie |
| Testowane obciążenie | 100 jednoczesnych użytkowników, współczynnik błędów < 5% | Test `wrk` lub `locust` przebiega pomyślnie przy docelowej współbieżności |

## Kolejność realizacji nowych projektów

1. **Dzień 1:** Serwer API + szablony podpowiedzi + pojedyncze wywołanie LLM z ponowną próbą
2. **Dzień 2:** Poręcze wejściowe + poręcze wyjściowe + obsługa błędów
3. **Dzień 3:** Semantyczna pamięć podręczna + śledzenie kosztów na żądanie
4. **Dzień 4:** Transmisja strumieniowa (SSE) + punkt końcowy kontroli stanu
5. **Dzień 5:** Logowanie strukturalne + śledzenie żądań + rejestrowanie ewaluacji
6. **Tydzień 2:** Testy A/B + szybkie wersjonowanie + wycofanie zmian
7. **Tydzień 3:** Łańcuch modeli awaryjnych + płynna degradacja
8. **Tydzień 4:** Testowanie obciążenia + optymalizacja asynchroniczna + skalowanie poziome

## Szybka diagnostyka

Jeśli coś jest nie tak w produkcji, sprawdź w następującej kolejności:

1. **Użytkownicy skarżą się na błędy?** Sprawdź punkt końcowy kondycji, następnie poziom błędów w dziennikach, a następnie stronę stanu dostawcy LLM
2. **Odpowiedzi są powolne?** Sprawdź opóźnienie P99, następnie współczynnik trafień w pamięci podręcznej, a następnie czasy odpowiedzi LLM w śladach
3. **Gwałtowny wzrost kosztów?** Sprawdź trend kosztu żądania, następnie współczynnik trafień w pamięci podręcznej, następnie najlepsi użytkownicy według kosztów, a następnie poszukaj szybkich zmian w szablonie, które zwiększyły liczbę tokenów
4. **Spadek jakości?** Sprawdź, czy wdrożono nową wersję podpowiedzi, sprawdź, czy zmieniła się dokładność wyszukiwania RAG, sprawdź, czy dostawca modelu zmienił domyślną wersję modelu
5. **Incydent związany z bezpieczeństwem?** Sprawdź częstotliwość blokowania poręczy (nagły upadek = wyłączenie poręczy), sprawdź dzienniki żądań pod kątem nietypowych wzorców, natychmiast zamień klucze API