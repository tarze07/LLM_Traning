# Warstwa routingu LLM — LiteLLM, OpenRouter, Portkey

> Blokowanie dostawców jest kosztowne. Różne obciążenia związane z wywoływaniem narzędzi odpowiadają różnym modelom. Bramy routingu zapewniają jedną powierzchnię API, ponowne próby, przełączanie awaryjne, śledzenie kosztów i poręcze. W roku 2026 dominują trzy archetypy: LiteLLM (samodzielny hosting typu open source), OpenRouter (zarządzany SaaS), Portkey (wersja produkcyjna, open source w marcu 2026 r.). W tej lekcji wymieniono kryteria decyzyjne i omówiono bramę routingu stdlib.

**Typ:** Ucz się
**Języki:** Python (stdlib, routing + przełączanie awaryjne + śledzenie kosztów)
**Warunki wstępne:** Faza 13 · 02 (wywołanie funkcji), Faza 13 · 17 (bramki)
**Czas:** ~45 minut

## Cele nauczania

- Rozróżnij opcje routingu samodzielnego, zarządzanego i produkcyjnego.
- Zaimplementuj łańcuch awaryjny, który ponawia próby w przypadku awarii dostawcy w określonej kolejności priorytetów.
- Śledź koszt żądania i wykorzystanie tokena u różnych dostawców.
- Zdecyduj pomiędzy LiteLLM, OpenRouter i Portkey dla danego ograniczenia produkcyjnego.

## Problem

Scenariusze, w których routing dostawcy ma znaczenie:

1. **Koszt.** Claude Sonnet kosztuje 3 razy więcej niż kosztuje Haiku. Do zadania selekcji wystarczy Haiku; do zadania syntezy Sonnet jest tego wart. Trasa na żądanie.

2. **Przełączenie awaryjne.** OpenAI ma złą godzinę. Każde żądanie kończy się niepowodzeniem. Chcesz automatycznego powrotu do Anthropic bez ponownego wdrażania.

3. **Opóźnienie.** Interfejs czatu na żywo wymaga szybkiego czasu do uzyskania pierwszego tokena. Podsumowanie partii nie. Trasa według umowy SLA o opóźnieniu.

4. **Zgodność.** Użytkownicy z UE muszą przebywać w regionach UE. Trasa według regionu.

5. **Eksperymentowanie.** A/B dwa modele przy tym samym obciążeniu. Trasa według segmentu testowego.

Ręczne kodowanie tego wszystkiego na integrację jest powtarzalne. Brama routingowa zapewnia jeden interfejs API zgodny z OpenAI i obsługuje resztę.

## Koncepcja

### Kształt proxy zgodny z OpenAI

Wszyscy mówią w kształcie OpenAI. Brama routingu udostępnia `/v1/chat/completions`, akceptuje schemat OpenAI i wewnętrznie łączy się z Anthropic / Gemini / Cohere / Ollama / czymkolwiek. Klienta to nie obchodzi.

### Aliasy modeli

Zamiast `claude-3-5-sonnet-20251022` Twój kod zawiera informację `our_smart_model`. Brama odwzorowuje aliasy na rzeczywiste modele. Kiedy Anthropic wysyła Claude 4, zmieniasz alias po stronie serwera; twój kod niczego nie dotyka.

### Łańcuchy awaryjne

```
primary: openai/gpt-4o
on 5xx: anthropic/claude-3-5-sonnet
on 5xx: google/gemini-1.5-pro
on 5xx: refuse
```

Bramy definiują to w konfiguracji. Ponowne próby wliczają się do budżetu, więc kaskady rezerwowe nie powodują gwałtownego wzrostu kosztów.

### Buforowanie semantyczne

Identyczne lub prawie identyczne monity trafiają do pamięci podręcznej zamiast do dostawcy. Oszczędności w przypadku powtarzających się pętli agentów mogą wynosić od 30 do 60 procent. Klucze opierają się na osadzaniu; niemal identyczne podpowiedzi mają wspólne miejsce na pamięć podręczną.

### Poręcze

Poziom bramy:

- ** Redakcja informacji umożliwiających identyfikację.** Przejście w oparciu o wyrażenia regularne lub ML przed wysłaniem monitu.
- **Naruszenia zasad.** Odrzucaj monity zawierające zabronioną treść.
- **Filtry wyjściowe.** Wyczyść wszystkie wycieki.

Zarówno Świstoklik, jak i Kong dostarczają poręcze ochronne. LiteLLM pozostawia je opcjonalne.

### Limity szybkości na klucz

Jeden klucz API = jeden zespół. Budżety dla poszczególnych kluczy uniemożliwiają jednemu zespołowi wykorzystanie współdzielonego przydziału. Większość bramek to obsługuje.

### Kompromisy na własnym serwerze i zarządzane

| Czynnik | LiteLLM (własny hosting) | OpenRouter (zarządzany) | Świstoklik (produkcja) |
|------------|----------------------|----------------------|----------------------|
| Kod | Otwarte oprogramowanie, Python | Zarządzany SaaS | Open source (marzec 2026) + zarządzane |
| Konfiguracja | Wdróż serwer proxy | Zarejestruj się | Albo |
| Dostawcy | 100+ | 300+ | 100+ |
| Rozliczenia | Twoje własne klucze | Kredyty OpenRouter | Twoje własne klucze |
| Obserwowalność | OtwartaTelemetria | Panel | Pełna redakcja Otel + PII |
| Najlepsze dla | Zespoły, które chcą pełnej kontroli | Szybkie prototypowanie | Produkcja zgodna z przepisami |

LiteLLM wygrywa, gdy masz zespół SRE i chcesz mieć suwerenność danych. OpenRouter wygrywa, gdy chcesz mieć pojedynczą subskrypcję i brak infrastruktury. Świstoklik wygrywa, gdy potrzebujesz poręczy i zgodności od razu po wyjęciu z pudełka.

### Śledzenie kosztów

Każde żądanie zawiera `provider`, `model`, `input_tokens`, `output_tokens`. Pomnóż przez ceny za model i token (pobrane z arkusza cenowego prowadzonego przez bramę). Agregacja na użytkownika / zespół / projekt.

### MCP plus routing

Brama może kierować zarówno wywołania LLM ORAZ żądania próbkowania MCP. Gdy modelPreferences żądania próbkowania preferuje określony model, brama przekłada się na prawy backend. W tym miejscu faza 13 · 17 (brama MCP) i brama routingu z tej lekcji czasami łączą się w jedną usługę.

### Strategie routingu

- **Priorytet statyczny.** Pierwszy na liście; cofnij się do błędu.
- **Równoważenie obciążenia.** Praca okrężna lub ważona.
- **Świadomość kosztów.** Wybierz najtańszy model spełniający wymagania dotyczące opóźnień i jakości.
- **Uwzględnianie opóźnień.** Wybierz najszybszy model w ciągu ostatnich N minut.
- **Obsługuje zadania.** Klasyfikator podpowiedzi kieruje kodowanie do jednego modelu, podsumowanie do drugiego.

## Użyj tego

`code/main.py` implementuje bramę routingu w ~150 liniach: akceptuje żądania w kształcie OpenAI, tłumaczy na kody pośredniczące poszczególnych dostawców, uruchamia priorytetowy łańcuch awaryjny, śledzi koszt żądania i stosuje redakcję danych wejściowych do danych wejściowych. Uruchom go z trzema scenariuszami: normalne żądanie, awaria głównego dostawcy powodująca powrót do sieci, wyciek danych osobowych wykryty przez redakcję.

Na co zwrócić uwagę:

- `ROUTES` dict: alias -> lista konkretnych dostawców uporządkowana według priorytetów.
- Ponowne próby pętli awaryjnej w dniu 5xx.
- Moduł śledzenia kosztów mnoży wykorzystanie tokenów przez stawki za model.
- Redaktor PII przegląda wzorce w kształcie numeru SSN przed przesłaniem.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-routing-config-designer.md`. Biorąc pod uwagę profil obciążenia (opóźnienie, koszt, zgodność), umiejętność wybiera LiteLLM/OpenRouter/Portkey i tworzy konfigurację routingu.

## Ćwiczenia

1. Uruchom `code/main.py`. Uruchom scenariusz przestoju; potwierdź, że rezerwa trafia do drugiego dostawcy, a koszt jest poprawnie przypisany.

2. Dodaj buforowanie semantyczne: SHA256 zachęty jest kluczem wyszukiwania; trafienia w pamięci podręcznej powracają natychmiast. Mierz oszczędności w przypadku powtarzających się połączeń.

3. Dodaj klasyfikator podpowiedzi, który kieruje podpowiedzi „kod…” do aliasu preferującego inteligencję, a podpowiedzi „podsumuj…” do aliasu preferującego szybkość.

4. Zaprojektuj budżety na zespół: każdy zespół ma miesięczny limit wydatków; brama odrzuca żądania po osiągnięciu limitu. Wybierz stopień szczegółowości egzekwowania (na żądanie lub w oknie).

5. Przeczytaj obok siebie dokumentację LiteLLM, OpenRouter i Portkey. Nazwij jedną cechę każdego statku, której nie mają pozostałe dwa.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Brama routingowa | „Proxy LLM” | Warstwa powierzchniowa jednego interfejsu API dla wielu dostawców |
| Kompatybilny z OpenAI | „Obsługuje schemat OpenAI” | Akceptuje kształt `/v1/chat/completions`, przekłada się na dowolny backend |
| Alias ​​modelu | „nasz_inteligentny_model” | Nazwij w kodzie, którą brama odwzorowuje na konkretny model |
| Łańcuch awaryjny | „Lista ponownych prób” | Uporządkowana lista dostawców, których próbowano dokonać w przypadku niepowodzenia |
| Buforowanie semantyczne | „Pamięć podręczna szybkiego osadzania” | Kluczem jest osadzenie podpowiedzi; prawie duplikaty udostępniają trafienie w pamięci podręcznej |
| Poręcze | „Filtry wejścia/wyjścia” | Redaguj informacje umożliwiające identyfikację, odrzucaj naruszenia zasad |
| Limit szybkości na klucz | „Budżet zespołu” | Przydział ograniczony do klucza API |
| Śledzenie kosztów | „Wydatki na żądanie” | Łączne użycie tokena x cena za model |
| LiteLLM | „Otwarty serwer proxy” | Samoobsługowa brama routingu OSS |
| OtwórzRouter | „Zarządzany SaaS” | Hostowana bramka z rozliczeniami opartymi na kredytach |
| Świstoklik | „Opcja produkcyjna” | Open-source + zarządzany z wbudowanymi poręczami |

## Dalsze czytanie

- [LiteLLM — dokumentacja] (https://docs.litellm.ai/) — hostowana brama routingu
- [OpenRouter — szybki start](https://openrouter.ai/docs/quickstart) — zarządzany routing SaaS
- [Portkey — dokumentacja] (https://portkey.ai/docs) — trasowanie produkcji z poręczami
- [TrueFoundry — LiteLLM vs OpenRouter](https://www.truefoundry.com/blog/litellm-vs-openrouter) — przewodnik dotyczący podejmowania decyzji
- [Relayplane — porównanie bramek LLM 2026](https://relayplane.com/blog/llm-gateway-comparison-2026) — ankieta dla dostawców