# Natychmiastowe buforowanie i buforowanie kontekstowe

> Twój monit systemowy to 4000 tokenów. Twój kontekst RAG to 20 000 tokenów. Wysyłasz oba przy każdym żądaniu. Płacisz także za jedno i drugie — za każdym razem. Szybkie buforowanie pozwala dostawcy zachować ten prefiks w dobrej kondycji i naliczyć opłatę w wysokości 10% normalnej stawki za ponowne użycie. Używany prawidłowo, zmniejsza koszt wnioskowania o 50–90% i opóźnienie pierwszego tokena o 40–85%.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 11 · 01 (szybka inżynieria), faza 11 · 05 (inżynieria kontekstu), faza 11 · 11 (buforowanie i koszt)
**Czas:** ~60 minut

## Problem

Agent kodujący wysyła do Claude'a ten sam monit systemowy zawierający 15 000 tokenów w każdej turze rozmowy. Dwadzieścia tur przy $3/M input tokens is $0,90 samego kosztu wejściowego – przed jakąkolwiek faktyczną wiadomością użytkownika. Pomnóż przez 10 000 rozmów dziennie, a rachunek wyniesie 9000 USD dziennie za tekst, który nigdy się nie zmienia.

Nie można zmniejszyć podpowiedzi bez szkody dla jakości. Nie da się uniknąć wysłania go – model potrzebuje go w każdej turze. Jedynym posunięciem jest zaprzestanie płacenia pełnej ceny za prefiks, który dostawca już widział.

Ten ruch to szybkie buforowanie. Anthropic wypuściło go w sierpniu 2024 r. (z 1-godzinnym wariantem TTL z wydłużonym czasem w 2025 r.), OpenAI zautomatyzowało je pod koniec tego samego roku, Google dostarczyło jawne buforowanie kontekstu wraz z Gemini 1.5, a wszystkie trzy oferują je teraz jako pierwszorzędną funkcję w swoich pionierskich modelach.

## Koncepcja

![Pamięć podręczna: napisz raz, czytaj tanio](../assets/prompt-caching.svg)

**Mechanika.** Kiedy prefiks żądania pasuje do prefiksu z ostatniego żądania, dostawca udostępnia pamięć podręczną KV z poprzedniego uruchomienia zamiast ponownie kodować tokeny. Płacisz niewielką opłatę za zapis za pierwszym razem i dużą zniżkę za odczyt za każdym razem.

**Trzy rodzaje dostawców w 2026 r.**

| Dostawca | Styl API | Hit zniżki | Napisz premium | Domyślny TTL | Min. pamięć podręczna |
|---------|-----------|-------------|---------------|-------------|---------------|
| Antropiczny | Wyraźne znaczniki `cache_control` w blokach treści | 90% zniżki na wejście | 25% dopłaty | 5 min (z możliwością przedłużenia do 1 godziny) | 1024 tokeny (Sonnet/Opus), 2048 (Haiku) |
| OpenAI | Automatyczne wykrywanie prefiksu | 50% zniżki na wejście | żaden | Do 1 godziny (najlepiej) | 1024 tokeny |
| Google (Bliźnięta) | Jawny `CachedContent` API | Opłacane za przechowywanie; czytać przy ~25% normy | Opłata za przechowywanie za token·godzinę | Ustawienie użytkownika (domyślnie 1 godzina) | 4096 tokenów (Flash), 32 768 (Pro) |

**Niezmiennik.** Tylko wszystkie trzy prefiksy pamięci podręcznej. Jeśli jakikolwiek token różni się między żądaniami, wszystko po pierwszym różniącym się tokenie jest pomijane. Umieść *stabilne* części na górze, *zmienne* części na dole.

### Układ przyjazny dla pamięci podręcznej

```
[system prompt]          <-- cache this
[tool definitions]       <-- cache this
[few-shot examples]      <-- cache this
[retrieved documents]    <-- cache if reused, else don't
[conversation history]   <-- cache up to last turn
[current user message]   <-- never cache (different every time)
```

Narusz porządek — umieść wiadomość użytkownika nad podpowiedzią systemową, przeplataj dynamiczne pobieranie pomiędzy kilkoma strzałami — a pamięć podręczna nigdy nie trafi.

### Obliczenie progu rentowności

Premia za zapis w Anthropic wynosząca 25% oznacza, że ​​blok w pamięci podręcznej musi zostać odczytany co najmniej dwukrotnie, aby zaoszczędzić pieniądze. 1 zapis + 1 odczyt to średnio 0,675x koszt na żądanie (oszczędność 32%); 1 zapis + 10 odczytów to średnio 0,205x (oszczędność 80%). Ogólna zasada: buforuj wszystko, czego spodziewasz się ponownie użyć, co najmniej 3 razy w ramach TTL.

## Zbuduj to

### Krok 1: Antropiczne buforowanie podpowiedzi z jawnymi znacznikami

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
        model="claude-opus-4-7",
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": code}],
    )
```

Znacznik `cache_control` informuje firmę Anthropic o konieczności przechowywania bloku przez 5 minut. Użyj ponownie w tym oknie trafień; użyj ponownie po wygaśnięciu i zapisz ponownie.

**Pola użycia odpowiedzi:**

```python
response = review(code_a)
response.usage
# InputTokensUsage(
#     input_tokens=120,
#     cache_creation_input_tokens=15023,   # paid at 1.25x
#     cache_read_input_tokens=0,
#     output_tokens=340,
# )

response_b = review(code_b)
response_b.usage
# cache_creation_input_tokens=0
# cache_read_input_tokens=15023           # paid at 0.1x
```

Sprawdź oba pola w CI — jeśli wartość `cache_read_input_tokens` w żądaniach pozostaje równa zeru, oznacza to, że klucze pamięci podręcznej dryfują.

### Krok 2: jednogodzinne przedłużenie TTL

W przypadku długotrwałych zadań wsadowych domyślny czas 5 minut wygasa między zadaniami. Ustaw `ttl`:

```python
{"type": "text", "text": RUBRIC, "cache_control": {"type": "ephemeral", "ttl": "1h"}}
```

1-godzinny TTL kosztuje 2x premię za zapis (50% powyżej wartości bazowej zamiast 25%), ale zwraca się szybko w przypadku dowolnej partii ponownego użycia prefiksu więcej niż 5 razy.

### Krok 3: Automatyczne buforowanie OpenAI

OpenAI nie daje niczego do skonfigurowania. Każdy prefiks powyżej 1024 tokenów, który pasuje do ostatniego żądania, automatycznie otrzymuje 50% zniżki.

```python
from openai import OpenAI
client = OpenAI()

resp = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},   # long and stable
        {"role": "user", "content": user_msg},
    ],
)
resp.usage.prompt_tokens_details.cached_tokens  # the discounted portion
```

Obowiązuje ta sama zasada układu przyjaznego pamięci podręcznej. Dwie rzeczy zabijają pamięć podręczną OpenAI, która nie zabija pamięci podręcznej Anthropic: zmiana pola `user` (używanego jako kluczowy komponent pamięci podręcznej) i zmiana kolejności narzędzi.

### Krok 4: Buforowanie kontekstu jawnego Gemini

Gemini traktuje skrytkę jako obiekt najwyższej klasy, który tworzysz i nazywasz:

```python
from google import genai
from google.genai import types

client = genai.Client()

cache = client.caches.create(
    model="gemini-3-pro",
    config=types.CreateCachedContentConfig(
        display_name="rubric-v3",
        system_instruction=RUBRIC,
        contents=[FEW_SHOT_EXAMPLES],
        ttl="3600s",
    ),
)

resp = client.models.generate_content(
    model="gemini-3-pro",
    contents=["Review this code:\n" + code],
    config=types.GenerateContentConfig(cached_content=cache.name),
)
```

Gemini ładuje pamięć za token·godzinę przez cały czas działania pamięci podręcznej i odczytuje z szybkością ~25% normalnej szybkości wejściowej. Jest to właściwy kształt, jeśli używasz tego samego gigantycznego podpowiedzi w wielu sesjach w ciągu kilku dni.

### Krok 5: pomiar współczynnika trafień w produkcji

Zobacz `code/main.py`, aby poznać symulowanego księgowego składającego się z trzech dostawców, który śledzi licznik zapisów/odczytów/pominięć i oblicza mieszany koszt na 1 tys. żądań. Brama jest uruchamiana z docelowym współczynnikiem trafień — większość produkcyjnych konfiguracji antropicznych powinna po rozgrzewce widzieć >80% frakcji odczytu.

## Pułapki, które nadal będą widoczne w 2026 r

- **Dynamiczne znaczniki czasu na górze.** `"Current time: 2026-04-22 15:30:02"` na górze monitu systemowego. Każda prośba mija się z celem. Przenieś znaczniki czasu poniżej punktu przerwania pamięci podręcznej.
- **Zmiana kolejności narzędzi.** Serializuj narzędzia w stabilnej kolejności — przetasowanie poleceń pomiędzy wdrożeniami przerywa każde trafienie.
- **Dowolny tekst prawie zduplikowany.** „Jesteś pomocny”. vs „Jesteś pomocnym asystentem”. — jeden bajt różnicy = pełne chybienie.
- **Zbyt małe bloki.** Anthropic wymusza minimalną liczbę 1024 żetonów (2048 w przypadku Haiku). Mniejsze bloki po cichu nie buforują.
- **Panel kosztów ślepych.** Podziel „tokeny wejściowe” na buforowane i niebuforowane. W przeciwnym razie spadek ruchu wygląda jak wygrana pamięci podręcznej.

## Użyj tego

Stos buforowania 2026:

| Sytuacja | Wybierz |
|----------|------|
| Agent ze stabilnym monitem systemowym 10k+, wiele tur | Antropiczny `cache_control` z 5-minutowym TTL |
| Zadanie wsadowe z ponownym użyciem prefiksu przez ponad 30 minut | Antropiczny z `ttl: "1h"` |
| Bezserwerowe punkty końcowe na GPT-5, bez niestandardowej infrastruktury | OpenAI automatyczne (po prostu ustaw swój prefiks stabilny i długi) |
| Wielodniowe ponowne wykorzystanie gigantycznego korpusu kodu/dokumentacji | Bliźnięta jawne `CachedContent` |
| Rozwiązanie zastępcze między dostawcami | Zachowaj identyczny układ prefiksów buforowanych u różnych dostawców, aby każde trafienie zadziałało |

Połącz z buforowaniem semantycznym (faza 11 · 11) dla warstwy komunikatów użytkownika: buforowanie podpowiedzi obsługuje ponowne użycie *identyczne z tokenem*, uchwyty buforowania semantycznego *identyczne-znaczenie* ponowne użycie.

## Wyślij to

Zapisz `outputs/skill-prompt-caching-planner.md`:

```markdown
---
name: prompt-caching-planner
description: Design a cache-friendly prompt layout and pick the right provider caching mode.
version: 1.0.0
phase: 11
lesson: 15
tags: [llm-engineering, caching, cost]
---

Given a prompt (system + tools + few-shot + retrieval + history + user) and a usage profile (requests per hour, TTL needed, provider), output:

1. Layout. Reordered sections with a single cache breakpoint marked; explain which sections are stable, which are volatile.
2. Provider mode. Anthropic cache_control, OpenAI automatic, or Gemini CachedContent. Justify from TTL and reuse pattern.
3. Break-even. Expected reads per write within TTL; net cost vs no-cache with math.
4. Verification plan. CI assertion that cache_read_input_tokens > 0 on the second identical request; dashboard split by cached vs uncached tokens.
5. Failure modes. List the three most likely reasons the cache will miss in this setup (dynamic timestamp, tool reorder, near-duplicate text) and how you will prevent each.

Refuse to ship a cache plan that places a dynamic field above the breakpoint. Refuse to enable 1h TTL without a reuse count that makes the 2x write premium pay back.
```

## Ćwiczenia

1. **Łatwe.** Weź udział w 10-turowej rozmowie z komunikatem systemowym o wartości 5000 tokenów przeciwko Claude'owi. Uruchom go bez `cache_control`, a następnie z. Zgłoś rachunek za token wejściowy dla każdego.
2. **Średni.** Napisz zestaw testowy, który na podstawie szablonu podpowiedzi i dziennika żądań obliczy oczekiwany współczynnik trafień i oszczędności w dolarach na dostawcę (Anthropic 5m, Anthropic 1h, OpenAI automatyczne, Gemini jawne).
3. **Trudne.** Utwórz optymalizator układu: mając monit i listę pól oznaczonych `stable=True/False`, przepisz zachętę, aby umieścić pojedynczy punkt przerwania pamięci podręcznej w maksymalnej pozycji przyjaznej dla pamięci podręcznej bez utraty informacji. Sprawdź na prawdziwym antropicznym punkcie końcowym.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Natychmiastowe buforowanie | „Sprawia, że ​​długie podpowiedzi są tanie” | Ponowne wykorzystanie pamięci podręcznej KV po stronie dostawcy do dopasowywania prefiksów; Rabat 50-90% na powtarzające się tokeny wejściowe. |
| `cache_control` | „Znacznik antropiczny” | Atrybut bloku treści, który deklaruje, że „wszystko do tej pory można buforować”; `{"type": "ephemeral"}`. |
| Zapis w pamięci podręcznej | „Płacenie składki” | Pierwsze żądanie wypełniające pamięć podręczną; rozliczane według ~1,25x stawki wejściowej w Anthropic, bezpłatnie w OpenAI. |
| Odczyt pamięci podręcznej | „Zniżka” | Kolejne żądania pasujące do prefiksu; rozliczane w wysokości 10% (Anthropic), 50% (OpenAI), ~25% (Gemini). |
| TTL | „Jak długo żyje” | Sekundy, w których pamięć podręczna pozostaje ciepła; Domyślnie Anthropic 5 m (z możliwością przedłużenia o 1 godz.), OpenAI best-effort do 1 godz., ustawienie użytkownika Gemini. |
| Rozszerzony TTL | „1-godzinna skrytka antropiczna” | `{"type": "ephemeral", "ttl": "1h"}`; 2x premia za zapis, ale warto w przypadku ponownego wykorzystania wsadowego. |
| Dopasowanie przedrostka | „Dlaczego moja pamięć podręczna przepadła” | Pamięci podręczne trafiają tylko wtedy, gdy każdy token od początku do punktu przerwania jest identyczny pod względem bajtów. |
| Buforowanie kontekstowe (Gemini) | „Ten wyraźny” | Nazwany obiekt pamięci podręcznej Google z opłatą za miejsce; najlepsze do wielodniowego ponownego wykorzystania dużych korpusów. |

## Dalsze czytanie

- [Anthropic — buforowanie podpowiedzi](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — `cache_control`, 1 godz. TTL, tabele progu rentowności.
- [OpenAI — Buforowanie podpowiedzi](https://platform.openai.com/docs/guides/prompt-caching) — automatyczne dopasowywanie prefiksów.
– [Google — buforowanie kontekstowe](https://ai.google.dev/gemini-api/docs/caching) — `CachedContent` Ceny interfejsów API i miejsca na dane.
— [Inżynieria antropiczna — Szybkie buforowanie dla obciążeń o długim kontekście] (https://www.anthropic.com/news/prompt-caching) — oryginalny post o uruchomieniu z numerami opóźnień.
- Faza 11 · 05 (Inżynieria kontekstu) — gdzie podzielić zachętę, aby pamięć podręczna mogła wylądować.
- Faza 11 · 11 (Buforowanie i koszt) — połącz buforowanie podpowiedzi z semantyczną pamięcią podręczną wiadomości użytkownika.
- [Pope i in., „Efficiently Scaling Transformer Inference” (2022)](https://arxiv.org/abs/2211.05102) — model pamięci podręcznej KV, który udostępnia użytkownikom buforowanie monitujące; wyjaśnia, dlaczego przedrostek zapisany w pamięci podręcznej jest ~10 razy tańszy w ponownym odczytaniu niż ponownym obliczeniu.
- [Agrawal i in., „SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills” (2023)](https://arxiv.org/abs/2308.16369) — wstępne wypełnienie to skróty do buforowania podpowiedzi fazy; ten artykuł wyjaśnia, dlaczego TTFT drastycznie spada po trafieniu w pamięć podręczną, podczas gdy TPOT pozostaje niezmieniony.
– [Leviathan i in., „Fast Inference from Transformers via Speculative Decoding” (2023)](https://arxiv.org/abs/2211.17192) — buforowanie natychmiastowe znajduje się obok dekodowania spekulatywnego, Flash Attention i MQA/GQA jako dźwignie zaginające krzywą kosztów wnioskowania; przeczytaj to dla pozostałych trzech.