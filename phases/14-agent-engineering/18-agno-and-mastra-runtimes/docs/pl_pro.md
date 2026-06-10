# Agno i Mastra: Czasy wykonania produkcji

> Agno (Python) i Mastra (TypeScript) to wiodące środowiska uruchomieniowe (runtimes) przeznaczone do wdrożeń produkcyjnych. Projekt Agno stawia na mikrosekundowe tworzenie instancji agentów oraz bezstanowe backendy oparte na FastAPI. Mastra oferuje agentów, narzędzia, przepływy pracy (workflows), ujednolicony routing modeli oraz elastyczną warstwę pamięci masowej (storage), bazując na Vercel AI SDK.

**Typ:** Ucz się
**Języki:** Python, TypeScript
**Wymagania wstępne:** Faza 14 · 01 (Pętla agenta), Faza 14 · 13 (LangGraph)
**Czas:** ~45 minut

## Cele nauczania

- Zidentyfikować cele wydajnościowe projektu Agno i określić, w jakich scenariuszach mają one kluczowe znaczenie.
- Wymienić trzy podstawowe komponenty frameworku Mastra (Agenci, Narzędzia, Przepływy pracy) oraz obsługiwane adaptery serwerowe.
- Wyjaśnić, dlaczego bezstanowy backend FastAPI o cyklu życia zorientowanym na sesję (session-scoped) jest rekomendowanym podejściem produkcyjnym w Agno.
- Dokonać właściwego wyboru między Agno a Mastra w zależności od stosu technologicznego (Python-first vs TypeScript-first).

## Problem

Frameworki takie jak LangGraph, AutoGen czy CrewAI narzucają określone wzorce architektoniczne. Zespoły, którym zależy na prostych, szybkich pętlach agenta działających bezpośrednio w ich własnym środowisku wykonawczym, chętnie sięgają po Agno (Python) lub Mastra (TypeScript). Oba te rozwiązania rezygnują z niektórych skomplikowanych abstrakcji frameworkowych na rzecz maksymalnej wydajności i łatwiejszej integracji z istniejącym kodem.

## Koncepcja

### Agno

- Środowisko uruchomieniowe dla języka Python (wcześniej znane pod nazwą Phi-data).
- „Bez grafów, łańcuchów (chains) czy skomplikowanych wzorców – po prostu czysty Python”.
- Deklarowane parametry wydajnościowe: czas inicjalizacji agenta na poziomie ~2μs, zużycie pamięci wynoszące zaledwie ~3,75 KiB na agenta oraz integracja z ~23 dostawcami modeli.
- Podejście produkcyjne: bezstanowy backend FastAPI o cyklu życia powiązanym z sesją. Każde zapytanie tworzy nową, lekką instancję agenta, podczas gdy stan sesji jest odczytywany i zapisywany w bazie danych.
- Natywna obsługa multimodalności (tekst, obraz, audio, wideo, pliki) oraz agentycznego RAG (Agentic RAG).

Wysoka wydajność inicjalizacji ma ogromne znaczenie przy obsłudze tysięcy krótkotrwałych agentów na sekundę (np. czaty o dużym natężeniu ruchu, potoki ewaluacyjne). Z kolei przy długo działających agentach (np. zadanie trwające 10 minut) narzut na start agenta staje się pomijalny.

### Mastra

- TypeScript, zbudowany na SDK Vercel AI.
- Trzy fundamenty: **Agenci (Agents)**, **Narzędzia (Tools)** z typowaniem za pomocą biblioteki Zod, oraz **Przepływy pracy (Workflows)**.
- Ujednolicony router modeli (Model Router) obsługujący ponad 3300 modeli od 94 dostawców.
- Kompozytowa warstwa zapisu (Composite Storage): niezależny zapis stanu pamięci, przepływów pracy i telemetrii do różnych baz danych (zalecana baza ClickHouse do obsługi telemetrii na dużą skalę).
- Licencja Apache 2.0 z wydzielonymi katalogami `ee/` udostępnianymi na zasadach licencji komercyjnej (source-available).
- Wbudowane adaptery serwerowe dla Express, Hono, Fastify i Koa; natywna integracja z Next.js oraz Astro.
- Narzędzie deweloperskie Mastra Studio (`localhost:4111`) ułatwiające debugowanie.
- Ponad 22 000 gwiazdek na GitHubie i ponad 300 000 pobrań tygodniowo z rejestru npm.

### Pozycjonowanie rynkowe

Żadne z tych rozwiązań nie próbuje kopiować LangGrapha. Rywalizacja dotyczy przede wszystkim:

- **Wygody języka programowania (Language Fit).** Agno dedykowane jest dla zespołów pythonowych, natomiast Mastra dla projektów TypeScript-first.
- **Ergonomii deweloperskiej.** Agno oferuje minimalny narzut konfiguracyjny, a Mastra świetnie integruje się z ekosystemem Vercel.
- **Telemetrii (Obserwowalności).** Oba frameworki integrują się z narzędziami takimi jak Langfuse, Phoenix czy Opik (Lekcja 24), przy czym Mastra oferuje dedykowane środowisko Mastra Studio.

### Kryteria wyboru

- **Agno** – backend w Pythonie, duża liczba krótkotrwałych agentów, wysokie wymagania wydajnościowe, bezstanowa architektura FastAPI.
- **Mastra** – backend w TypeScript, wdrażanie na platformie Vercel (Next.js), ujednolicony routing modeli od wielu dostawców, walidacja za pomocą Zod.
- **LangGraph** (Lekcja 13) – gdy zarządzanie stanem i modelowanie logiki za pomocą grafu są ważniejsze niż czas inicjalizacji agenta.
- **OpenAI / Claude Agent SDK** (Lekcje 16–17) – jeśli preferujesz oficjalne biblioteki bezpośrednio od dostawców modeli.

### Najczęstsze błędy projektowe

- **Optymalizacja wydajności dla samej zasady.** Wybieranie Agno tylko ze względu na obietnicę „2μs”, podczas gdy wąskim gardłem jest jedno powolne zapytanie do LLM. W takich przypadkach narzut frameworka nie ma wpływu na UX.
- **Uzależnienie od ekosystemu (Vendor Lock-in).** Głęboka integracja Mastry z rozwiązaniami Vercel ułatwia wdrożenia na tej platformie, ale utrudnia migrację w inne środowiska.
- **Nieuwaga przy licencjonowaniu.** Kod w katalogach `ee/` projektu Mastra jest udostępniany na licencji komercyjnej (source-available), a nic Apache 2.0. Należy dokładnie zweryfikować licencję przed ewentualnymi forkami.

## Przykład porównawczy

Ponieważ lekcja ta ma charakter porównawczy, plik `code/main.py` przedstawia uproszczoną implementację side-by-side. Zaimplementowano w nim ten sam podstawowy przepływ: „uruchomienie agenta, strumieniowanie odpowiedzi, zachowanie sesji” w wersji wzorowanej na Agno oraz na frameworku Mastra.

Uruchomienie:

```
python3 code/main.py
```

Otrzymasz dwa odmienne pod względem struktury, lecz funkcjonalnie równoważne logi śledzenia.

## Podsumowanie zastosowań

- **Agno** – backend w Pythonie z naciskiem na minimalne opóźnienia i architekturę FastAPI.
- **Mastra** – backend w TypeScript z zaawansowanym routingiem modeli i gotowymi szablonami przepływów pracy.
- Oba rozwiązania udostępniają własne mechanizmy śledzenia (telemetrii) i bezproblemowo integrują się z Langfuse.

## Zadanie wdrożeniowe

Plik `outputs/skill-runtime-picker.md` zawiera wytyczne ułatwiające wybór optymalnego środowiska (Agno, Mastra, LangGraph lub oficjalnego SDK) na podstawie stosu technologicznego, dopuszczalnych opóźnień oraz architektury systemu.

## Ćwiczenia praktyczne

1. Przeanalizuj dokumentację Agno i przenieś uproszczoną pętlę ReAct (zaimplementowaną w Lekcji 1) do tego frameworka. Zwróć uwagę, które elementy Twojego kodu zostały zastąpione wbudowanymi funkcjami.
2. Zapoznaj się z dokumentacją Mastry i przenieś tę samą pętlę ReAct do TypeScriptu z jej użyciem. Jak wpłynęło wprowadzenie biblioteki Zod na definiowanie i typowanie narzędzi?
3. Przeprowadź testy porównawcze (benchmark) i zmierz czas potrzebny na zainicjowanie agenta. Czy deklarowana przez Agno mikrosekundowa szybkość rzeczywiście wpłynie na wydajność Twojego systemu?
4. Zaprojektuj plan migracji: jak wyglądałoby przeniesienie logiki z frameworka CrewAI do Agno w Pythonie?
5. Przeczytaj warunki licencji dla katalogów `ee/` frameworku Mastra. Jakie ograniczenia komercyjne napotkasz przy próbie stworzenia własnej wersji open source (forka)?

## Kluczowe terminy

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| Agno | „Szybkie pętle w Pythonie” | Środowisko uruchomieniowe stawiające na bezstanowość i szybką inicjalizację instancji w cyklu życia sesji |
| Mastra | „Środowisko agentyczne w TypeScript” | Ekosystem integrujący agentów, narzędzia, przepływy pracy oraz router modeli oparty na Vercel AI SDK |
| Ujednolicony model routera | „Agregacja dostawców” | Jednolite API umożliwiające przełączanie się między tysiącami modeli od dziesiątek dostawców |
| Magazyn kompozytowy | „Niezależne bazy danych” | Możliwość kierowania historii sesji, logów przepływów i telemetrii do osobnych, dedykowanych baz danych |
| Mastra Studio | „Graficzny panel deweloperski” | Lokalne narzędzie webowe pod adresem localhost:4111 służące do wizualizacji i debugowania zachowań agenta |
| Source-available | „Dostępny kod źródłowy” | Licencja pozwalająca na wgląd w kod, lecz nakładająca ograniczenia dotyczące komercyjnego wykorzystania lub redystrybucji |

## Dalsze czytanie

- [Dokumentacja Agno](https://www.agno.com/agent-framework) — cele wydajnościowe, integracja z FastAPI
- [Dokumentacja Mastra](https://mastra.ai/docs) — elementy podstawowe, adaptery serwerowe, router modelowy
- [Omówienie LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) — alternatywa dla wykresu stanowego
- [Opik (Comet)](https://www.comet.com/site/products/opik/) — porównania obserwowalności cytowane przez integracje Mastra
