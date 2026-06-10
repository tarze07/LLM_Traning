---

name: skill-cost-patterns
description: Ramy decyzyjne dotyczące optymalizacji kosztów LLM - strategie buforowania, ograniczanie liczby wywołań, routing modeli i kontrola budżetu
version: 1.0.0
phase: 11
lesson: 11
tags: [caching, cost-optimization, rate-limiting, model-routing, budget, llm-ops]

---

# Wzorce optymalizacji kosztów LLM

Tworząc aplikację LLM, która musi efektywnie kontrolować koszty, zastosuj poniższe zasady decyzyjne.

## Kiedy wdrażać optymalizacje

**Optymalizuj natychmiast, gdy:**
- Miesięczne wydatki na API LLM przekraczają 500 USD lub stanowią ponad 10% budżetu na infrastrukturę.
- Średni koszt pojedynczego zapytania przekracza 0.01 USD w przypadku produktu masowego.
- Twój prompt systemowy przekracza 1000 tokenów i jest przesyłany przy każdym żądaniu.
- Ponad 30% zapytań użytkowników to dokładne powtórzenia lub bliskie parafrazy.
- Skalujesz liczbę aktywnych użytkowników od 100 do ponad 10 000 dziennie.

**Wstrzymaj się z optymalizacją, gdy:**
- Posiadasz mniej niż 100 DAU i nadal weryfikujesz dopasowanie produktu do rynku (product-market fit).
- Miesięczne wydatki na API wynoszą poniżej 100 USD i rosną powoli.
- Nadal intensywnie modyfikujesz strukturę promptów (buforowanie może utrudniać testowanie zmian w promptach).

## Wybór strategii buforowania

### Dokładne buforowanie (Exact Match Caching)

**Zastosuj, gdy:** Parametr temperatura = 0, użytkownicy często wysyłają identyczne prompty i wymagana jest pełna deterministyczność odpowiedzi.

```python
key = sha256(json.dumps({"model": m, "messages": msgs, "temp": 0}))
```

- **Czas wdrożenia:** ~30 minut.
- **Współczynnik trafień (Hit Rate):** 10-25% dla większości aplikacji, 40-60% dla systemów FAQ.
- **Opóźnienie:** < 1 ms (proste odpytanie bazy klucz-wartość / słownika).
- **Ryzyko:** Zwracanie nieaktualnych odpowiedzi, jeśli dane źródłowe uległy zmianie.

**Pomiń, gdy:** Parametr temperatura > 0, każde zapytanie jest unikalne lub wymagana jest prezentacja danych w czasie rzeczywistym.

### Buforowanie semantyczne (Semantic Caching)

**Zastosuj, gdy:** Użytkownicy zadają bardzo podobne pytania, formułując je własnymi słowami (np. w systemach FAQ, wirtualnych asystentach lub obsłudze klienta).

- **Czas wdrożenia:** 2-4 godziny (integracja z bazą wektorową, wyliczanie podobieństwa).
- **Współczynnik trafień (Hit Rate):** Dodatkowe 15-35% oszczędności obok dokładnego buforowania.
- **Opóźnienie:** 10-50 ms (wygenerowanie osadzenia + wyszukiwanie najbliższych sąsiadów ANN).
- **Ryzyko:** Fałszywe trafienia (false positives) – zwrócenie z pamięci podręcznej odpowiedzi na pytanie, które brzmi podobnie, ale ma inne znaczenie biznesowe.

**Zalecane progi podobieństwa:**
- **0.98+**: Bardzo konserwatywny próg, minimalne ryzyko pomyłki, niższy wskaźnik trafień.
- **0.95**: Optymalny balans dla systemów pytań i odpowiedzi opartych na faktach.
- **0.90**: Agresywny próg, wysoka oszczędność kosztów, ale zauważalne ryzyko fałszywych trafień.
- **0.85**: Dopuszczalne tylko dla zastosowań o niskiej stawce (np. systemy sugestii, autouzupełnianie).

**Pomiń, gdy:** Każde zapytanie wymaga unikalnego kontekstu (np. generowanie kodu), odpowiedzi muszą natychmiast odzwierciedlać najświeższe dane dynamiczne lub zbiór zapytań jest całkowicie nieprzewidywalny.

### Buforowanie promptów u dostawcy (Prompt Caching)

**Zastosuj, gdy:** Prompt systemowy lub historia konwersacji przekraczają 1024 tokeny (OpenAI/Anthropic) i te same bloki danych są wielokrotnie przesyłane w kolejnych zapytaniach.

| Dostawca | Wymagane działanie | Efekt optymalizacji |
|---------|--------|--------|
| Anthropic | Dodaj flagę `"cache_control": {"type": "ephemeral"}` do bloku systemowego | 90% zniżki na buforowany prefiks (po 25% dopłacie za pierwszy zapis) |
| OpenAI | Automatyczne działanie po stronie API | 50% zniżki na buforowany prefiks |
| Google Gemini | Użyj dedykowanego API Context Caching z określeniem czasu życia (TTL) | ~75% zniżki na buforowany kontekst |

**Pomiń, gdy:** Prompt systemowy lub przesyłany kontekst zmieniają się dynamicznie przy każdym zapytaniu, lub ich długość jest mniejsza niż wymagany przez dostawcę próg minimalny.

## Reguły routingu modeli

### Metoda oparta na słowach kluczowych (prosta i szybka)

```
simple:  krótsze niż 5 słów LUB słowa kluczowe FAQ -> gpt-4o-mini ($0.15 / $0.60)
medium:  zapytania ogólne, podsumowania tekstów   -> claude-3-5-sonnet ($3.00 / $15.00)
complex: słowa kluczowe "analizuj", "porównaj"     -> gpt-4o ($2.50 / $10.00)
```

- **Czas wdrożenia:** 1 godzina.
- **Trafność routingu:** 70-80%.
- **Oszczędność:** 40-60% kosztów API.

### Metoda oparta na osadzeniach wektorowych (bardziej precyzyjna)

Przygotuj 50–100 zapytań testowych oznaczonych etykietami złożoności dla każdej kategorii. Klasyfikuj nowe zapytania, dopasowując je do najbliższych sąsiadów w bazie wektorowej.

- **Czas wdrożenia:** 4-8 godzin.
- **Trafność routingu:** 85-92%.
- **Oszczędność:** 50-70% kosztów API.
- **Koszt dodatkowy:** Marginalny (~$0.02 za 1M tokenów na wyliczenie wektora).

### Metoda oparta na uczeniu maszynowym (klasa produkcyjna)

Wytrenuj mały, dedykowany klasyfikator (np. regresję logistyczną lub zoptymalizowany model BERT) na historycznych logach zapytań i wybranych dla nich modelach docelowych.

- **Czas wdrożenia:** 1-2 tygodnie.
- **Trafność routingu:** 90-95%.
- **Oszczędność:** 60-75% kosztów API.
- **Wymagania:** Dostęp do odpowiednio dużej, oznaczonej bazy danych z ruchu produkcyjnego.

## Konfiguracja limitów wywołań (Rate Limiting)

### Parametry Token Bucket dla poszczególnych poziomów

| Poziom (Tier) | Pojemność koszyka | Tempo regeneracji | Maks. RPM | Limit dobowy |
|------|-------------|------------|-------------|---------------|
| Free | 50 000 tokenów | 500 / sek | 10 | 50 000 |
| Pro | 500 000 tokenów | 5 000 / sek | 60 | 500 000 |
| Enterprise | 5 000 000 tokenów | 50 000 / sek | 300 | 5 000 000 |

### Lista kontrolna dla wdrożenia produkcyjnego

1. W architekturach rozproszonych przechowuj stany koszyków w bazie Redis (nie w pamięci RAM instancji aplikacji).
2. Zabezpiecz operacje na bazie Redis transakcjami (MULTI/EXEC), aby zapobiec zjawisku race conditions.
3. Zwracaj standardowy nagłówek HTTP `Retry-After` wraz z kodem błędu 429 dla odrzuconych żądań.
4. Monitoruj liczbę odrzuceń (rate limit block rate). Jeśli wskaźnik ten przekracza 5%, limity mogą być zbyt restrykcyjne.
5. Wdrażaj strategię łagodnej degradacji: w pierwszej kolejności blokuj zapytania do najdroższych modeli, zachowując dostęp do tańszych alternatyw.

## Kontrola budżetu i bezpieczeństwo finansowe

### Wyłącznik awaryjny (Circuit Breaker) o trzech progach

| Zużycie budżetu | Działanie | Automatyczny powrót |
|----------|--------|------------|
| 70% limitu miesięcznego | Rejestracja ostrzeżenia w logach, wysyłka alertu na Slack / PagerDuty | Tak |
| 85% limitu miesięcznego | Przełączenie całości ruchu na najtańsze modele (degradacja jakości) | Tak (w kolejnym okresie rozliczeniowym) |
| 95% limitu miesięcznego | Blokada nowych zapytań do modeli LLM, serwowanie odpowiedzi wyłącznie z cache | Tak (po ręcznym resecie lub w nowym cyklu) |

### Monitorowanie zużycia na użytkownika

Stale analizuj skumulowany koszt generowany przez poszczególnych użytkowników. Oznaczaj flagą osoby generujące koszty przekraczające 10-krotność mediany. Najczęstsze powody anomalii:
- Użytkownicy o ekstremalnie intensywnym profilu pracy (potencjalni kandydaci do wyższego planu).
- Ataki typu prompt injection lub pętle zapytań (złośliwe skrypty automatyzujące).
- Błędy w integracji po stronie klienta (np. nieskończone ponawianie zapytań przy błędach sieciowych).

## Rekord logowania kosztów

Zalecana struktura pojedynczego wpisu logu wywołania API:

```json
{
  "timestamp": "2026-04-02T10:30:00Z",
  "model": "gpt-4o",
  "input_tokens": 1523,
  "output_tokens": 487,
  "cached_input_tokens": 1024,
  "latency_ms": 1847,
  "cost_usd": 0.006142,
  "user_id": "user_abc123",
  "cache_status": "partial_hit",
  "request_category": "customer_support",
  "complexity_class": "medium",
  "routed_from": "gpt-4o"
}
```

### Kluczowe metryki na panelu kontrolnym (Dashboard)

- **Średni koszt zapytania** (P50, P95, P99) – analizowany w podziale na modele, funkcjonalności i poziomy użytkowników.
- **Wskaźnik trafień w cache (Hit Rate)** – osobno dla dopasowań dokładnych (exact) oraz semantycznych (semantic).
- **Rozkład ruchu modeli** – procentowy udział zapytań i generowanych kosztów przez poszczególne modele LLM.
- **Tempo zużycia budżetu (Burn Rate)** – porównanie dotychczasowych wydatków z prognozą na koniec miesiąca przy aktualnym ruchu.
- **Współczynnik blokad (Rate Limit Block Rate)** – procent odrzuconych zapytań z podziałem na poziomy.

## Typowe błędy i pułapki

| Błąd | Skutki | Rozwiązanie |
|-------------|------------|-----|
| Caching przy temperaturze > 0 | Przestarzały cache blokuje naturalną różnorodność odpowiedzi | Buforuj wyłącznie zapytania o temperaturze = 0 lub zaakceptuj utratę stochastyczności |
| Zbyt niski próg podobieństwa w cache | Serwowanie błędnych odpowiedzi na pytania o innym znaczeniu | Rozpocznij od progu 0.95 i obniżaj go wyłącznie po analizie fałszywych trafień |
| Brak mechanizmu unieważniania cache | Serwowanie nieaktualnych danych po zmianie bazy wiedzy | Wprowadź czas życia TTL (np. 1 godzina dla danych dynamicznych, 24 godziny dla statycznych) |
| Kierowanie całości ruchu do najtańszego modelu | Drastyczny spadek jakości odpowiedzi, frustracja użytkowników | Dobieraj model pod kątem złożoności pytania; regularnie testuj jakość na każdym poziomie |
| Brak limitów na pojedynczego użytkownika | Jeden agresywny skrypt lub użytkownik potrafi wyczerpać cały budżet | Zawsze wdrażaj limity tokenów dla użytkowników, nawet na bardzo wysokich poziomach |
| Ignorowanie kosztów tokenów wyjściowych | Tokeny wyjściowe są od 2 do 5 razy droższe niż tokeny wejściowe | Ustawiaj parametr `max_tokens`, stosuj sekwencje stop i dbaj o zwięzłość odpowiedzi |
| Caching przed sfinalizowaniem struktury promptu | Pamięć podręczna zapełnia się odpowiedziami wygenerowanymi przez stare prompty | Aktywuj cache dopiero po zamrożeniu kodu promptów; czyść cache przy każdym wdrożeniu zmian |

## Cennik referencyjny (kwiecień 2026 r.)

| Model | Koszt wejścia ($ / 1M) | Koszt wyjścia ($ / 1M) | Koszt wejścia z cache ($ / 1M) | Główne zastosowanie |
|-------|------------|-------------|----------------------------------|---------|
| gpt-4.1-nano | $0.10 | $0.40 | $0.025 | Masowe, proste operacje tekstowe |
| gpt-4o-mini | $0.15 | $0.60 | $0.075 | Lekkie klasyfikacje, routing |
| gemini-2.5-flash | $0.15 | $0.60 | $0.0375 | Tanie przetwarzanie multimodalne |
| claude-haiku-3.5 | $0.80 | $4.00 | $0.08 | Szybkie zadania o średniej złożoności |
| o4-mini | $1.10 | $4.40 | $0.275 | Wnioskowanie i logika przy niskim budżecie |
| gemini-2.5-pro | $1.25 | $10.00 | $0.3125 | Analiza długiego kontekstu |
| gpt-4o | $2.50 | $10.00 | $1.25 | Zadania ogólne, wywoływanie funkcji |
| claude-sonnet-4 | $3.00 | $15.00 | $0.30 | Złoty środek między jakością a kosztem |
| claude-opus-4 | $15.00 | $75.00 | $1.50 | Zaawansowane wnioskowanie naukowe i kodowanie |
