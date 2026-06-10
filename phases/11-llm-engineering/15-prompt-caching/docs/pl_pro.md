# Buforowanie promptów (Prompt Caching) i buforowanie kontekstowe

> Twój prompt systemowy zajmuje 4000 tokenów. Twój kontekst RAG to kolejne 20 000 tokenów. Wysyłasz oba te elementy przy każdym zapytaniu. Co gorsza, płacisz za nie w pełnej kwocie za każdym razem. Buforowanie promptów (Prompt Caching) umożliwia dostawcom API utrzymywanie tego prefiksu w pamięci podręcznej i naliczanie opłaty na poziomie zaledwie 10% standardowej stawki przy kolejnych zapytaniach. Prawidłowo wdrożone buforowanie promptów obniża koszty wnioskowania o 50–90% oraz skraca czas do wygenerowania pierwszego tokenu (TTFT) o 40–85%.

**Typ:** Kompilacja  
**Języki:** Python  
**Wymagania wstępne:** Faza 11 · 01 (prompt engineering), Faza 11 · 05 (inżynieria kontekstu), Faza 11 · 11 (buforowanie i koszty)  
**Czas:** ~60 minut  

## Problem

Agent programistyczny wysyła ten sam prompt systemowy o długości 15 000 tokenów przy każdej turze rozmowy z modelem Claude. 20 tur konwersacji przy cenie $3 za milion tokenów wejściowych generuje koszt $0.90 za samo przetwarzanie wejścia (input) – zanim użytkownik napisze chociaż jedno słowo. Przy 10 000 takich konwersacji dziennie daje to koszt 9000 USD na dobę za przetwarzanie tekstu, który w ogóle się nie zmienia.

Nie możesz skrócić promptu systemowego bez straty na jakości wnioskowania. Nie możesz też przestać go wysyłać – model potrzebuje tych instrukcji w każdej turze. Jedynym rozwiązaniem jest eliminacja opłat za ciągłe przetwarzanie tego samego, niezmiennego tekstu.

Odpowiedzią na ten problem jest buforowanie promptów. Anthropic zaprezentował tę funkcję w sierpniu 2024 roku (z opcją przedłużenia TTL do 1 godziny w 2025 roku), OpenAI zautomatyzowało ją pod koniec 2024 roku, a Google Gemini udostępniło jawne buforowanie kontekstu (Context Caching). Wszyscy wiodący dostawcy oferują to rozwiązanie jako standard w swoich flagowych modelach.

## Koncepcja

![Pamięć podręczna: napisz raz, czytaj tanio](../assets/prompt-caching.svg)

**Zasada działania.** Gdy prefiks nowego żądania dokładnie pasuje do prefiksu z poprzedniego wywołania, dostawca API odczytuje przetworzony kontekst (klucze i wartości KV cache) bezpośrednio z pamięci karty graficznej zamiast ponownie przetwarzać (tokenizować) tekst. Płacisz standardową stawkę (z niewielką dopłatą) za pierwszy zapis, a za każdy kolejny odczyt płacisz z ogromnym rabatem.

**Porównanie mechanizmów u dostawców:**

| Dostawca | Model integracji | Rabat za trafienie | Dopłata za zapis | Domyślny TTL | Minimalny rozmiar cache |
|---------|-----------|-------------|---------------|-------------|---------------|
| Anthropic | Jawne znaczniki `cache_control` w wiadomościach | 90% zniżki na input | 25% dopłaty | 5 min (z opcją przedłużenia do 1h) | 1024 tokeny (Sonnet/Opus), 2048 (Haiku) |
| OpenAI | Automatyczne dopasowanie prefiksów | 50% zniżki na input | brak | Do 1 godziny (best-effort) | 1024 tokeny |
| Google Gemini | Jawne API `CachedContent` | Rozliczane za czas przechowywania; ~75% zniżki na odczyt | Opłata za przechowywanie za token/godzinę | Konfigurowalny (domyślnie 1h) | 4096 tokenów (Flash), 32 768 (Pro) |

**Niezmiennik działania (Invariant).** Wszystkie mechanizmy cache opierają się na dopasowywaniu prefiksów. Jeśli chociaż jeden token ulegnie zmianie na początku promptu, cały cache znajdujący się po nim zostaje unieważniony. Dlatego kluczowe jest umieszczanie elementów *stabilnych* na samej górze struktury promptu, a elementów *zmiennych* na samym dole.

### Układ promptu przyjazny dla cache

```
[prompt systemowy]       <-- buforuj ten blok
[definicje narzędzi]     <-- buforuj ten blok
[przykłady few-shot]     <-- buforuj ten blok
[pobrany kontekst RAG]   <-- buforuj, jeśli powtarza się w innych zapytaniach
[historia konwersacji]   <-- buforuj do przedostatniej tury
[aktualna wiadomość]     <-- nigdy nie buforuj (zmienna przy każdym zapytaniu)
```

Zaburzenie tej kolejności — np. umieszczenie wiadomości użytkownika nad promptem systemowym lub przeplatanie dynamicznych danych z RAG pomiędzy przykładami few-shot — sprawi, że cache nigdy nie zostanie trafiony.

### Próg rentowności (Break-even)

Wdrożenie buforowania w Anthropic wiąże się z 25% dopłatą za pierwszy zapis. Oznacza to, że aby optymalizacja przyniosła realne oszczędności, dany blok musi zostać odczytany z cache co najmniej dwukrotnie. 1 zapis + 1 odczyt to średnio 0.675x kosztu standardowego zapytania (oszczędność 32%). Z kolei 1 zapis + 10 odczytów to koszt rzędu 0.205x stawki bazowej (oszczędność 80%). Złota zasada: buforuj te sekcje, które zostaną użyte ponownie co najmniej 3 razy przed wygaśnięciem TTL.

## Zbuduj to

### Krok 1: Buforowanie promptów w Anthropic za pomocą cache_control

Wskażemy za pomocą nagłówków, które części promptu systemowego powinny zostać zapamiętane w cache.

```python
import anthropic

client = anthropic.Anthropic()

SYSTEM = [
    {
        "type": "text",
        "text": "You are a senior Python reviewer. Follow the rubric exactly.\n\n" + RUBRIC_15K_TOKENS,
        "cache_control": {"type": "ephemeral"},
    }
]

def review(code: str):
    return client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": code}],
    )
```

Flaga `cache_control` instruuje platformę Anthropic, aby zapisała wskazany blok na 5 minut. Każde kolejne zapytanie w tym oknie czasowym odnowi licznik TTL i skorzysta z tańszej taryfy.

**Struktura zużycia tokenów w odpowiedzi:**

```python
response = review(code_a)
response.usage
# Zapis do cache (cache creation) przy pierwszym wywołaniu:
# InputTokensUsage(
#     input_tokens=120,
#     cache_creation_input_tokens=15023,   # rozliczane ze stawką 1.25x
#     cache_read_input_tokens=0,
#     output_tokens=340,
# )

response_b = review(code_b)
response_b.usage
# Odczyt z cache (cache read) przy kolejnym wywołaniu:
# cache_creation_input_tokens=0
# cache_read_input_tokens=15023           # rozliczane ze stawką 0.1x
```

Weryfikuj te pola w testach CI – jeśli wskaźnik `cache_read_input_tokens` na powtarzających się zapytaniach wynosi 0, oznacza to dryf struktury promptu i unieważnianie pamięci podręcznej.

### Krok 2: Konfiguracja przedłużonego czasu życia (extended TTL)

Dla długotrwałych zadań wsadowych domyślny 5-minutowy czas życia cache może być zbyt krótki. Możesz jawnie zdefiniować parametr `ttl`:

```python
{"type": "text", "text": RUBRIC, "cache_control": {"type": "ephemeral", "ttl": "1h"}}
```

Czas życia cache równy 1 godzinie zwiększa koszt pierwszego zapisu (premia 50% zamiast 25%), ale zwraca się z nawiązką, jeśli prefiks jest odczytywany częściej niż 5 razy na godzinę.

### Krok 3: Automatyczne buforowanie w OpenAI

OpenAI nie wymaga żadnej konfiguracji w kodzie. Każdy stabilny prefiks promptu przekraczający 1024 tokeny automatycznie korzysta z 50% zniżki przy kolejnych zapytaniach.

```python
from openai import OpenAI
client = OpenAI()

resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},   # długi i stabilny blok systemowy
        {"role": "user", "content": user_msg},
    ],
)
# Odczytamy liczbę tokenów obsłużonych z cache:
resp.usage.prompt_tokens_details.cached_tokens
```

Układ promptu musi być ściśle uporządkowany (stabilne bloki na górze). Pamiętaj, że zmiana kolejności zdefiniowanych narzędzi (tools) lub modyfikacja roli w wiadomości użytkownika unieważnią cache w OpenAI.

### Krok 4: Jawne buforowanie kontekstu (Context Caching) w Gemini

Gemini traktuje cache jako niezależny obiekt, który tworzysz i zarządzasz nim za pomocą dedykowanych metod API:

```python
from google import genai
from google.genai import types

client = genai.Client()

cache = client.caches.create(
    model="gemini-1.5-pro",
    config=types.CreateCachedContentConfig(
        display_name="rubric-v3",
        system_instruction=RUBRIC,
        contents=[FEW_SHOT_EXAMPLES],
        ttl="3600s",
    ),
)

resp = client.models.generate_content(
    model="gemini-1.5-pro",
    contents=["Review this code:\n" + code],
    config=types.GenerateContentConfig(cached_content=cache.name),
)
```

Gemini nalicza opłaty za przechowywanie danych w pamięci (storage fee per token/hour) przez cały czas życia cache oraz daje ~75% rabatu na każde odpytanie. Jest to optymalny wybór, gdy ten sam ogromny zestaw danych (np. cała dokumentacja techniczna firmy) jest wielokrotnie odpytywany w różnych sesjach w ciągu dnia.

### Krok 5: Analiza i monitorowanie wskaźników cache na produkcji

W pliku `code/main.py` znajdziesz kompletną klasę symulującą rozliczenia u trzech różnych dostawców chmurowych, która zlicza zapisy, odczyty i chybienia cache oraz oblicza uśredniony koszt zapytań. W produkcyjnych systemach opartych o Anthropic wskaźnik odczytów z cache (cache read ratio) po rozgrzaniu bazy powinien stabilnie przekraczać 80%.

## Typowe błędy unieważniające cache

- **Dynamiczne znaczniki czasu na początku promptu.** Wstrzykiwanie linii `"Current time: 2026-04-22 15:30:02"` na samej górze promptu systemowego powoduje unieważnienie cache przy każdym pojedynczym zapytaniu. Umieszczaj dynamiczne zmienne czasowe na samym dole promptu.
- **Losowa kolejność narzędzi.** Zmienna kolejność serializacji funkcji (tools) przy kolejnych wdrożeniach kodu niszczy strukturę cache. Zawsze sortuj definicje narzędzi alfabetycznie przed wysłaniem ich do API.
- **Niewielkie różnice znakowe.** Frazy „Jesteś pomocny.” oraz „Jesteś pomocnym asystentem.” różnią się kilkoma znakami. Różnica jednego bajtu na początku unieważnia cały cache znajdujący się poniżej.
- **Zbyt małe bloki danych.** Anthropic wymaga minimum 1024 tokenów wejściowych (2048 dla modeli Haiku). Mniejsze bloki są pomijane przez mechanizm buforowania.
- **Brak rozbicia metryk na panelu.** Monitoruj tokeny wejściowe w podziale na `cached` i `uncached`. W przeciwnym razie ogólne spadki ruchu użytkowników mogą być błędnie interpretowane jako wzrost wydajności bazy cache.

## Rekomendacje doboru technologii buforowania

| Scenariusz biznesowy | Rekomendowane rozwiązanie |
|----------|------|
| Wieloturowy agent konwersacyjny ze stabilnym promptem systemowym > 10k tokenów | Anthropic `cache_control` z domyślnym 5-minutowym TTL |
| Zadania asynchroniczne (batch) z ponownym użyciem prefiksów przez czas > 30 minut | Anthropic `cache_control` z wydłużonym TTL (`ttl: "1h"`) |
| Serwery bezstanowe na modelach OpenAI (GPT-4o/5) bez własnej infrastruktury | Automatyczny cache OpenAI (zadbaj o statyczną strukturę na początku promptu) |
| Wielodniowe odpytywanie gigantycznej bazy wiedzy lub dokumentacji technicznej | Google Gemini i jawne buforowanie `CachedContent` |
| Praca w architekturze Multi-LLM | Ujednolicenie kolejności sekcji promptu u wszystkich dostawców w celu zachowania spójności cache |

*Wskazówka: Połącz buforowanie promptów (Prompt Caching) na poziomie API z buforowaniem semantycznym (Semantic Caching) na poziomie aplikacji. Pierwsze z nich odpowiada za identyczne dopasowania wejściowe (token-to-token), a drugie za zapytania o tej samej intencji wyrażone innymi słowami.*

## Co zostało wygenerowane

Ta lekcja tworzy plik `outputs/skill-prompt-caching-planner.md` — ramy decyzyjne i szablon do projektowania strategii buforowania:

```markdown
---
name: prompt-caching-planner
description: Zaprojektuj układ promptu przyjazny dla pamięci podręcznej i dobierz optymalny model buforowania dostawcy.
version: 1.0.0
phase: 11
lesson: 15
tags: [llm-engineering, caching, cost]
---

Na podstawie struktury promptu (system + tools + few-shot + retrieval + history + user) oraz profilu użycia (częstotliwość zapytań, wymagany TTL, dostawca) wygeneruj:

1. Układ promptu: Uporządkowana struktura sekcji ze wskazaniem granicy cache (cache breakpoint) oraz wyjaśnieniem, które dane są stabilne, a które zmienne.
2. Model buforowania: Dobór i uzasadnienie wdrożenia (Anthropic cache_control, OpenAI automatic, Gemini CachedContent) w zależności od TTL i wzorca ponownego użycia.
3. Analiza rentowności: Obliczenie liczby wymaganych odczytów na jeden zapis w oknie TTL oraz symulacja kosztów przed i po optymalizacji.
4. Plan weryfikacji: Asercje testowe CI sprawdzające, czy `cache_read_input_tokens > 0` przy powtórzonych zapytaniach testowych oraz konfiguracja metryk.
5. Ryzyka unieważnienia cache: Wyszczególnienie trzech głównych powodów unieważniania cache w danej architekturze (np. dynamiczne daty, kolejność narzędzi) wraz z metodami ich eliminacji.

Blokuj wdrożenia umieszczające zmienne dynamiczne powyżej granicy cache. Blokuj wdrożenia 1h TTL w Anthropic bez wykazania opłacalności finansowej względem 2x wyższego kosztu zapisu.
```

## Ćwiczenia

1. **Poziom łatwy.** Przeprowadź 10-turową konwersację z modelem Claude przy użyciu promptu systemowego o długości 5000 tokenów. Uruchom test bez znacznika `cache_control`, a następnie z aktywnym znacznikiem. Zmierz i porównaj ostateczną liczbę naliczonych tokenów wejściowych (input tokens) dla obu wariantów.
2. **Poziom średni.** Napisz skrypt testowy, który na podstawie struktury szablonu promptu oraz logów zapytań z bazy danych zasymuluje i wyliczy potencjalne oszczędności finansowe dla czterech modeli buforowania (Anthropic 5m, Anthropic 1h, OpenAI automatic, Gemini CachedContent), ułatwiając dobór optymalnego dostawcy.
3. **Poziom trudny.** Stwórz parser optymalizujący strukturę promptu: na podstawie wejściowego szablonu oraz słownika zmiennych z flagami `stable=True/False` automatycznie przeorganizuj kolejność sekcji tak, aby uzyskać maksymalną długość stabilnego bloku (cache breakpoint) bez zmiany semantyki promptu. Przetestuj poprawność działania na rzeczywistym API Anthropic.

## Kluczowe terminy

| Termin | Potoczne rozumienie | Rzeczywiste znaczenie techniczne |
|------|-----------------|----------------------|
| Prompt Caching | „Tani cache promptów” | Buforowanie stanu KV-cache po stronie dostawcy API dla identycznych prefiksów wejściowych; daje 50-90% zniżki |
| `cache_control` | „Tag w Anthropic” | Wskaźnik w bloku wiadomości API określający, że dotychczasowy tekst ma zostać zapamiętany w cache; format `{"type": "ephemeral"}` |
| Zapis w cache (Cache Write) | „Inicjalizacja cache” | Pierwsze zapytanie budujące cache; wiąże się z dopłatą 25% w Anthropic, darmowe w OpenAI |
| Odczyt z cache (Cache Read) | „Trafienie w cache” | Zapytanie dopasowane do prefiksu korzystające z rabatu (10% ceny w Anthropic, 50% w OpenAI) |
| TTL (Time To Live) | „Czas życia cache” | Okres ważności cache; domyślnie 5 min w Anthropic (odnawiane przy trafieniach), do 1h w OpenAI, konfigurowalny w Gemini |
| Extended TTL | „Długi cache Anthropic” | Przechowywanie cache do 1 godziny; wymaga dopłaty 50% za zapis, opłacalne przy rzadszych zadaniach wsadowych |
| Dopasowanie prefiksu | „Zasada zgodności” | Zasada działania cache oparta na dopasowaniu znak po znaku; jakakolwiek zmiana na początku unieważnia cały cache poniżej |
| Context Caching | „Cache w Gemini” | Trwałe buforowanie dużych bazy danych w Gemini na zasadzie opłaty za przechowywanie (storage fee per token/hour) |
