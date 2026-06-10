---

name: skill-cost-patterns
description: Ramy decyzyjne dotyczące optymalizacji kosztów LLM - strategie buforowania, ograniczanie szybkości, routing modelu i kontrola budżetu
version: 1.0.0
phase: 11
lesson: 11
tags: [caching, cost-optimization, rate-limiting, model-routing, budget, llm-ops]

---

# Wzorce optymalizacji kosztów LLM

Tworząc aplikację LLM, która musi kontrolować koszty, zastosuj te ramy decyzyjne.

## Kiedy optymalizować

**Optymalizuj natychmiast, gdy:**
- Miesięczne wydatki LLM przekraczają 500 USD lub 10% budżetu na infrastrukturę
- Koszt zapytania przekracza 0,01 USD w przypadku produktu konsumenckiego
- Twój monit systemowy zawiera ponad 1000 tokenów i jest wysyłany przy każdym żądaniu
- Ponad 30% zapytań to duplikaty lub prawie duplikaty
- Skalujesz liczbę użytkowników od 100 do ponad 10 000 dziennie

**Nie optymalizuj jeszcze, gdy:**
- Masz mniej niż 100 DAU i nadal sprawdzasz dopasowanie produktu do rynku
- Miesięczne wydatki wynoszą poniżej 100 USD i powoli rosną
- Nadal wykonujesz iterację w oparciu o projekt monitu (buforowanie blokuje cię w wierszu zachęty)

## Wybór strategii buforowania

### Dokładne buforowanie

**Użyj, gdy:** temperatura=0, powtarzają się identyczne monity, potrzebne są deterministyczne dane wyjściowe.

```python
key = sha256(json.dumps({"model": m, "messages": msgs, "temp": 0}))
```

- Realizacja: 30 minut
- Współczynnik trafień: 10-25% dla większości aplikacji, 40-60% dla botów FAQ
- Opóźnienie: <1ms (dict lookup)
- Risk: stale responses if underlying data changes

**Skip when:** temperature > 0, każde zapytanie jest unikalne, potrzebne są dane w czasie rzeczywistym.

### Buforowanie semantyczne

**Użyj, gdy:** użytkownicy zadają to samo pytanie innymi słowami, produkty z dużą liczbą często zadawanych pytań, obsługa klienta.

- Wdrożenie: 2-4 godziny (osadzanie + podobieństwo + przechowywanie)
- Współczynnik trafień: 15-35% oprócz dokładnej pamięci podręcznej
- Opóźnienie: 10-50 ms (osadzanie + wyszukiwanie ANN)
- Ryzyko: fałszywe alarmy (zwracanie błędnej odpowiedzi z pamięci podręcznej na podobne, ale inne pytanie)

**Wytyczne dotyczące progów:**
- 0,98+: bardzo konserwatywny, prawie brak fałszywych alarmów, niższy współczynnik trafień
- 0,95: dobra równowaga w zakresie pytań i odpowiedzi opartych na faktach
- 0,90: agresywny, wyższy współczynnik trafień, ale ryzyko błędnych odpowiedzi
- 0,85: tylko dla aplikacji o niskiej stawce (sugestie, autouzupełnianie)

**Pomiń, gdy:** każde zapytanie ma unikalny kontekst (generowanie kodu), odpowiedzi muszą odzwierciedlać najnowsze dane, przestrzeń zapytań jest nieograniczona.

### Buforowanie monitów dostawcy

**Użyj, gdy:** monit systemowy > 1024 tokenów (OpenAI) lub minimum specyficzne dla modelu, ten sam prefiks wysyłany wielokrotnie.

| Dostawca | Akcja | Oszczędności |
|---------|--------|--------|
| Antropiczny | Dodaj `cache_control: {"type": "ephemeral"}` do komunikatu systemowego | 90% na prefiksie buforowanym (po 25% premii za zapis) |
| OpenAI | Nic (automatycznie) | 50% na prefiks w pamięci podręcznej |
| Google | Użyj interfejsu API buforowania kontekstowego z jawnym TTL | ~75% w kontekście buforowanym |

**Pomiń, gdy:** monit systemowy zmienia się na żądanie, długość monitu jest krótsza niż minimalna.

## Modelowe reguły routingu

### Na podstawie słów kluczowych (proste, szybkie)

```
simple:  <= 5 words OR matches FAQ keywords -> gpt-4o-mini ($0.15/$0.60)
medium:  general queries, summaries        -> claude-sonnet ($3/$15)
complex: "analyze", "compare", "debug"     -> gpt-4o ($2.50/$10)
```

- Realizacja: 1 godzina
- Dokładność: 70-80%
- Oszczędności: 40-60% kosztów modelu

### Oparte na osadzaniu (bardziej dokładne)

Umieść 50–100 zapytań oznaczonych etykietami na kategorię. Klasyfikuj nowe zapytania według najbliższego sąsiada.

- Realizacja: 4-8 godzin
- Dokładność: 85-92%
- Oszczędności: 50-70% kosztów modelu
- Dodatkowy koszt: ~ 0,02 USD/1 mln tokenów za osadzanie klasyfikacji (nieistotne)

### Na bazie ML (klasa produkcyjna)

Wytrenuj mały klasyfikator (regresja logistyczna lub mały BERT) na historycznych parach zapytanie/model.

- Realizacja: 1-2 tygodnie
- Dokładność: 90-95%
- Oszczędności: 60-75% kosztów modelu
- Wymaga: oznakowanych danych szkoleniowych z ruchu produkcyjnego

## Konfiguracja ograniczająca szybkość

### Parametry zasobnika tokenów według poziomu

| Poziom | Rozmiar wiadra | Szybkość uzupełniania | Maks. obroty | Czapka dzienna |
|------|-------------|------------|-------------|---------------|
| Bezpłatne | 50 tys. tokenów | 500/s | 10 | 50 tys. |
| Zawodowiec | 500 tys. tokenów | 5K/s | 60 | 500 tys. |
| Przedsiębiorstwo | 5M tokenów | 50 K/s | 300 | 5M |

### Lista kontrolna wdrożenia

1. Przechowuj segmenty w Redis (nie w pamięci) dla aplikacji z wieloma instancjami
2. Użyj operacji atomowych (MULTI/EXEC), aby zapobiec warunkom wyścigu
3. Zwróć nagłówek `Retry-After` z odpowiedziami na odrzucenie
4. Śledź odrzucone żądania jako metrykę (odrzucenie > 5% = limity poziomów zbyt wysokie)
5. Wprowadź płynną degradację: najpierw odrzuć żądania drogich modeli, zachowaj tani dostęp do modeli

## Kontrola budżetu

### Wyłącznik trójprogowy

| Próg | Akcja | Odwracalne |
|----------|--------|------------|
| 70% miesięcznego budżetu | Ostrzeżenie dotyczące dziennika, zespół powiadamiający za pośrednictwem Slack/PagerDuty | Tak (automatycznie) |
| 85% miesięcznego budżetu | Skieruj cały ruch do najtańszego modelu | Tak (automatycznie, następny cykl rozliczeniowy) |
| 95% miesięcznego budżetu | Podawaj tylko odpowiedzi z pamięci podręcznej, odrzucaj nowe połączenia LLM | Tak (reset ręczny lub następny cykl) |

### Śledzenie kosztów na użytkownika

Śledź skumulowany koszt na użytkownika. Oznacz użytkowników przekraczających 10-krotność mediany. Najczęstsze przyczyny:
- Uprawniony zaawansowany użytkownik (uaktualnij swój poziom)
- Pętla szybkiego wstrzykiwania (bot wysyłający automatyczne żądania)
- Nieefektywna integracja (klient ponawia próbę przy każdym błędzie)

## Pola śledzenia kosztów

Rejestruj każde wywołanie API za pomocą tych pól:

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

### Kluczowe dane w panelu

– **Koszt zapytania** (P50, P95, P99) – według modelu, według funkcji, według poziomu użytkownika
- **Współczynnik trafień w pamięci podręcznej** – dokładny czy semantyczny, trend w czasie
- **Dystrybucja modelu** --% ruchu na model, koszt na model
- **Współczynnik wykorzystania budżetu** – bieżące wydatki w porównaniu z prognozowanymi miesięcznymi przy obecnym tempie
- **Współczynnik odrzuceń** --% żądań z ograniczoną szybkością, według poziomu

## Typowe błędy

| Błąd | Dlaczego to boli | Napraw |
|-------------|------------|-----|
| Buforowanie z temperaturą > 0 | Niedeterministyczne wyniki, przestarzała pamięć podręczna daje niewłaściwą odmianę | Buforuj tylko wywołania temp=0 lub zaakceptuj, że odpowiedzi w pamięci podręcznej tracą losowość |
| Próg pamięci podręcznej semantycznej zbyt niski | Zwraca błędne odpowiedzi na powierzchownie podobne zapytania | Zacznij od 0,95, obniżaj dopiero po zmierzeniu współczynnika wyników fałszywie dodatnich |
| Brak unieważnienia pamięci podręcznej | Odpowiedzi stają się nieaktualne, gdy zmieniają się dane podstawowe | Ustaw TTL (1 godzina dla danych dynamicznych, 24 godziny dla statycznych), unieważnij przy aktualizacjach danych |
| Kierowanie całego ruchu do najtańszego modelu | Spadek jakości, zauważają użytkownicy | Kieruj się według złożoności, mierz jakość na każdym poziomie, ustalaj minimalne progi jakości |
| Brak limitów na użytkownika | Jeden agresywny użytkownik spala cały budżet | Zawsze wdrażaj limity na użytkownika, nawet jeśli są duże |
| Ignorowanie tokenów wyjściowych | Koszty wyjściowe 2-5 razy większe niż koszty wejściowe na token | Ustaw odpowiednio max_tokens, użyj sekwencji stop, kompresuj wyjścia |
| Buforowanie przed monitem jest stabilne | Pamięć podręczna wypełnia się odpowiedziami ze starych podpowiedzi | Włącz buforowanie dopiero po sfinalizowaniu monitu, opróżnij pamięć podręczną po zmianach monitu |

## Ceny referencyjne (stan na kwiecień 2026 r.)

| Modelka | Wejście ($/1M) | Output ($/1M) | Dane wejściowe buforowane ($/1 mln) | Najlepsze dla |
|-------|------------|-------------|----------------------------------|---------| 
| gpt-4.1-nano | $0.10 | $0.40 | 0,025 $ | Proste zadania o dużej objętości |
| gpt-4o-mini | $0.15 | $0.60 | 0,075 $ | Proste trasowanie, klasyfikacja |
| gemini-2.5-flash | $0.15 | $0.60 | 0,0375 USD | Budżet multimodalny |
| claude-haiku-3.5 | $0.80 | $4.00 | 0,08 USD | Szybkie zadania średniego poziomu |
| o4-mini | $1.10 | $4.40 | 0,275 $ | Rozumowanie w sprawie budżetu |
| gemini-2.5-pro | $1.25 | $10.00 | 0,3125 $ | Długi kontekst, multimodalny |
| gpt-4o | $2.50 | $10.00 | 1,25 dolara | Ogólny cel, wywoływanie funkcji |
| claude-sonnet-4 | $3.00 | $15.00 | 0,30 $ | Zrównoważona jakość/koszt |
| claude-opus-4 | $15.00 | $75.00 | 1,50 dolara | Maksymalna jakość, złożone rozumowanie |