# Warstwa routingu LLM — LiteLLM, OpenRouter i Portkey

> Uzależnienie od jednego dostawcy (vendor lock-in) jest kosztowne, a różne typy zadań (obciążenia) wymagają zastosowania różnych modeli językowych. Bramy routingu (routing gateways) udostępniają jednolity interfejs API, obsługują ponowne próby (retries), automatyczne przełączanie awaryjne (failover), śledzenie kosztów oraz filtry bezpieczeństwa (guardrails). W 2026 roku na rynku dominują trzy rozwiązania: LiteLLM (otwarta brama do samodzielnego hostowania), OpenRouter (zarządzana usługa SaaS) oraz Portkey (rozwiązanie klasy produkcyjnej, udostępnione jako open source w marcu 2026 r.). W tej lekcji omawiamy kryteria wyboru oraz analizujemy przykładową bramę routingu opartą na bibliotece standardowej Pythona.

**Typ:** Teoria
**Język:** Python (biblioteka standardowa, routing, failover i śledzenie kosztów)
**Wymagania wstępne:** Faza 13 · 02 (wywoływanie narzędzi/funkcji), Faza 13 · 17 (bramy sieciowe)
**Czas:** ~45 minut

## Cele lekcji

- Rozróżnianie architektury routingu samodzielnego (self-hosted), zarządzanego (SaaS) oraz klasy produkcyjnej.
- Implementacja łańcucha awaryjnego (failover chain) realizującego ponowne próby (retries) u kolejnych dostawców według zdefiniowanych priorytetów.
- Śledzenie kosztów zapytań oraz zużycia tokenów u różnych dostawców.
- Wybór optymalnego rozwiązania (LiteLLM, OpenRouter, Portkey) w zależności od wymagań produkcyjnych.

## Problem

Scenariusze, w których inteligentny routing ma kluczowe znaczenie:

1. **Optymalizacja kosztów.** Model Claude Sonnet jest trzykrotnie droższy od Claude Haiku. Do wstępnej selekcji (triage) wystarczy Haiku, natomiast do syntezy i generowania treści niezbędny jest Sonnet. Routing pozwala na dynamiczny dobór modelu w zależności od trudności zadania.

2. **Niezawodność (Failover).** W przypadku awarii API u jednego dostawcy (np. OpenAI), brama automatycznie przekierowuje ruch do zapasowego dostawcy (np. Anthropic) bez konieczności restartu czy redeploymentu aplikacji.

3. **Opóźnienia (Latency).** Kanały interaktywne (np. czat na żywo) wymagają jak najkrótszego czasu do wygenerowania pierwszego tokenu (TTFT), podczas gdy zadania przetwarzania wsadowego (batch) mogą mieć niższy priorytet. System kieruje ruch zgodnie z umową SLA.

4. **Zgodność z przepisami (Compliance).** Wymóg przetwarzania danych użytkowników z UE w centrach danych na terenie Unii Europejskiej. Brama kieruje ruch do odpowiednich regionów geograficznych.

5. **Testy A/B.** Porównywanie wydajności i jakości dwóch modeli pod tym samym obciążeniem poprzez kierowanie określonego odsetka ruchu do każdego z nich.

Samodzielne kodowanie tych mechanizmów dla każdej integracji prowadzi do powielania kodu. Dedykowana brama routingu udostępnia spójny interfejs API (zgodny ze standardem OpenAI) i przejmuje całą logikę na siebie.

## Założenia koncepcyjne

### Standard API zgodny z OpenAI

Współczesne bramy implementują interfejs zgodny z OpenAI. Brama udostępnia punkt końcowy `/v1/chat/completions`, przyjmuje żądania w standardowym formacie i tłumaczy je w locie na protokoły specyficzne dla systemów Anthropic, Gemini, Cohere czy lokalnego serwera Ollama. Klient nie musi modyfikować sposobu składania zapytań.

### Aliasy modeli

Zamiast używać w kodzie konkretnej nazwy modelu (np. `claude-3-5-sonnet-20251022`), aplikacja odwołuje się do zdefiniowanego aliasu (np. `our_smart_model`). Brama mapuje ten alias na fizyczny model na zapleczu. Po wydaniu nowszej wersji modelu, administrator zmienia jedynie konfigurację mapowania na bramie — kod aplikacji pozostaje bez zmian.

### Łańcuchy awaryjne (Failover Chains)

```
primary: openai/gpt-4o
on 5xx: anthropic/claude-3-5-sonnet
on 5xx: google/gemini-1.5-pro
on 5xx: refuse
```

Bramy zarządzają tymi regułami deklaratywnie. Ponowne próby są kontrolowane przez polityki wydatków, dzięki czemu kaskadowe przełączanie nie generuje niekontrolowanych kosztów.

### Buforowanie semantyczne (Semantic Caching)

Zapytania o identycznym lub zbliżonym znaczeniu semantycznym są obsługiwane z lokalnej pamięci podatkowej zamiast być przesyłane do zewnętrznego dostawcy. Oszczędności w przypadku powtarzalnych pętli agentów sięgają od 30% do nawet 60%. Klucze wyszukiwania bazują na wektorach cech (embeddings) – semantycznie tożsame zapytania współdzielą ten sam wpis w pamięci podręcznej.

### Filtry bezpieczeństwa (Guardrails)

Funkcje realizowane na poziomie bramy:

- **Anonimizacja PII.** Wykrywanie i maskowanie danych osobowych przy użyciu wyrażeń regularnych lub modeli uczenia maszynowego przed wysłaniem zapytania do zewnętrznego API.
- **Filtrowanie treści.** Odrzucanie zapytań naruszających polityki bezpieczeństwa.
- **Weryfikacja odpowiedzi.** Blokowanie odpowiedzi zawierających wrażliwe dane lub niedozwolone treści.

Zarówno Portkey, jak i Kong posiadają wbudowane mechanizmy guardrails. W LiteLLM są one opcjonalne i wymagają dodatkowej konfiguracji.

### Limity żądań na klucz API

Mapowanie kluczy API na zespoły deweloperskie pozwala na kontrolowanie wydatków. Dedykowane limity i budżety zapobiegają sytuacji, w której jeden zespół konsumuje całą pulę środków lub limitów zapytań organizacji. Większość współczesnych bram obsługuje te funkcje.

### Porównanie rozwiązań

| Czynnik | LiteLLM (Self-hosted) | OpenRouter (SaaS) | Portkey (Klasa produkcyjna) |
|------------|----------------------|----------------------|----------------------|
| Kod | Open Source, Python | Zarządzana usługa SaaS | Open Source (od marca 2026 r.) + SaaS |
| Konfiguracja | Wdoczenie własnego proxy | Rejestracja w usłudze | Własne proxy lub SaaS |
| Dostawcy | 100+ | 300+ | 100+ |
| Rozliczenia | Własne klucze API dostawców | Rozliczenie w usłudze (kredyty) | Własne klucze API dostawców |
| Obserwowalność | OpenTelemetry | Panel | Pełna integracja OTel + anonimizacja PII |
| Najlepsze dla | Zespoły wymagające pełnej suwerenności danych | Szybkie prototypowanie i testy | Wdrożenia produkcyjne o wysokich wymogach zgodności |

LiteLLM jest optymalnym wyborem dla organizacji posiadających własne zespoły inżynierów SRE i wymagających pełnej suwerenności danych. OpenRouter sprawdza się najlepiej, gdy celem jest minimalizacja narzutu infrastrukturalnego i rozliczanie za pomocą jednej subskrypcji. Portkey to najlepszy wybór w scenariuszach wymagających zaawansowanych filtrów bezpieczeństwa (guardrails) oraz zgodności z regulacjami.

### Śledzenie kosztów

Każde zapytanie rejestruje parametry: `provider`, `model`, `input_tokens` oraz `output_tokens`. Koszt jest wyliczany w locie poprzez przemnożenie zużycia przez aktualne stawki (pobierane z cennika zarządzanego przez bramę). Dane te są następnie agregowane w podziale na użytkowników, zespoły lub projekty.

### Integracja z MCP

Brama może kontrolować zarówno zapytania do modeli językowych, jak i żądania próbkowania (sampling) z protokołu MCP. Gdy parametr `modelPreferences` wskazuje preferowany model, brama kieruje zapytanie do odpowiedniego dostawcy. W zaawansowanych architekturach brama MCP (Faza 13 · 17) oraz brama routingu LLM są często łączone w jeden system.

### Strategie routingu

- **Statyczny priorytet.** Próba wywołania pierwszego modelu z listy; przełączenie na zapasowy w przypadku błędu.
- **Równoważenie obciążenia (Load Balancing).** Kierowanie ruchu metodą Round-Robin lub z użyciem wag.
- **Routing zorientowany na koszty.** Wybór najtańszego modelu, który spełnia zdefiniowane wymagania jakościowe i czasowe.
- **Routing zorientowany na opóźnienia.** Kierowanie ruchu do modelu, który charakteryzował się najkrótszym doomed czasem odpowiedzi w ostatnim oknie czasowym.
- **Routing kontekstowy (Task-aware).** Klasyfikator bada treść zapytania i kieruje zadania programistyczne do jednego modelu, a zadania redakcyjne do innego.

## Zastosowanie w praktyce

Skrypt `code/main.py` implementuje uproszczoną bramę routingu w około 150 liniach kodu. Przyjmuje zapytania w formacie zgodnym z OpenAI, mapuje je na protokoły konkretnych dostawców, obsługuje priorytetowy łańcuch awaryjny (failover), zlicza koszty wywołań oraz filtruje dane wejściowe. Przetestuj jego działanie w trzech scenariuszach: (1) poprawne zapytanie standardowe; (2) symulowana awaria dostawcy głównego z przekierowaniem na zapasowy; (3) wykrycie i zablokowanie próby przesłania danych osobowych (PII).

Kluczowe elementy:

- Słownik `ROUTES` mapujący aliasy na uporządkowaną priorytetowo listę dostawców.
- Obsługa błędów z grupy 5xx i automatyczne przełączanie w pętli failover.
- Moduł rozliczeniowy wyliczający koszt na podstawie zużycia tokenów i cennika.
- Filtr bezpieczeństwa sprawdzający obecność wrażliwych wzorców (np. PESEL/SSN) przed wysłaniem żądania.

## Zadanie praktyczne

Efektem tej lekcji powinno być przygotowanie pliku `outputs/skill-routing-config-designer.md`. Na podstawie parametrów obciążenia (opóźnienia, koszty, wymogi zgodności) należy dokonać wyboru między systemami LiteLLM, OpenRouter i Portkey oraz opracować konfigurację reguł routingu.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Przetestuj scenariusz awarii dostawcy głównego; upewnij się, że żądanie zostało obsłużone przez dostawcę zapasowego, a koszt wywołania został poprawnie przypisany.

2. Zaimplementuj uproszczone buforowanie: wygeneruj skrót SHA256 zapytania wejściowego jako klucz wyszukiwania; w przypadku trafienia zwróć wynik natychmiast z pamięci podręcznej. Zmierz czas odpowiedzi i oszczędność kosztów.

3. Zaimplementuj prosty klasyfikator intencji (prompt classifier): zapytania zaczynające się od słów związanych z programowaniem kieruj do aliasu zorientowanego na zaawansowaną logikę, a zapytania redakcyjne i podsumowania do modelu zorientowanego na szybkość.

4. Zaprojektuj mechanizm kontroli budżetowej: zdefiniuj miesięczne limity wydatków dla zespołów i blokuj wywołania po ich przekroczeniu. Przeanalizuj wady i zalety weryfikacji limitów w czasie rzeczywistym vs. w oknach czasowych.

5. Przeanalizuj i porównaj dokumentację techniczną LiteLLM, OpenRouter oraz Portkey. Wskaż po jednej unikalnej funkcjonalności dla każdego z tych systemów, która nie występuje u konkurentów.

## Kluczowe pojęcia

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Brama routingu | „Proxy LLM” | Serwer pośredniczący udostępniający spójny interfejs API do wielu dostawców LLM |
| Zgodność z OpenAI | „Standard API OpenAI” | Obsługa punktu końcowego `/v1/chat/completions` i formatu danych OpenAI |
| Alias modelu | „Model abstrakcyjny” | Logiczna nazwa modelu w kodzie, mapowana przez bramę na fizyczne API |
| Łańcuch awaryjny | „Lista rezerwowa (Failover)” | Priorytetyzowana lista modeli zapasowych odpytywanych w przypadku awarii usług |
| Buforowanie semantyczne | „Inteligentny cache” | Zapisywanie wyników w oparciu o bliskość wektorową zapytań (embeddings) |
| Filtry bezpieczeństwa (Guardrails) | „Walidacja wejścia/wyjścia” | Mechanizmy anonimizacji danych osobowych (PII) oraz filtrowania treści |
| Limit na klucz API | „Kontrola limitów” | Ograniczanie liczby wywołań oraz wydatków przypisane do konkretnego klucza API |
| Śledzenie kosztów | „Monitoring wydatków” | Wyliczanie kosztów wywołań w oparciu o zużycie tokenów i cenniki modeli |
| LiteLLM | „Otwarta brama proxy” | Popularna, lekka brama routingu o otwartym kodzie źródłowym do samodzielnego hostowania |
| OpenRouter | „Agregator SaaS” | Chmurowa usługa routingu agregująca setki modeli z rozliczenie w formie doładowań |
| Portkey | „Brama klasy produkcyjnej” | Rozwiązanie zintegrowane z zaawansowanymi filtrami guardrails oraz logowaniem telemetrycznym |

## Polecana literatura / dokumentacja

- [LiteLLM — dokumentacja](https://docs.litellm.ai/) — hostowana brama routingu
- [OpenRouter — szybki start](https://openrouter.ai/docs/quickstart) — zarządzany routing SaaS
- [Portkey — dokumentacja](https://portkey.ai/docs) — trasowanie produkcji z poręczami
- [TrueFoundry — LiteLLM vs OpenRouter](https://www.truefoundry.com/blog/litellm-vs-openrouter) — przewodnik dotyczący podejmowania decyzji
- [Relayplane — porównanie bramek LLM 2026](https://relayplane.com/blog/llm-gateway-comparison-2026) — ankieta dla dostawców
