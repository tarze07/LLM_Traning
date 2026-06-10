# Agno i Mastra: Czasy wykonania produkcji

> Agno (Python) i Mastra (TypeScript) to połączenie środowiska produkcyjnego i wykonawczego na rok 2026. Agno ma na celu tworzenie instancji agentów mikrosekundowych i bezstanowe backendy FastAPI. Mastra dostarcza agentów, narzędzia, przepływy pracy, ujednolicony routing modeli i złożoną pamięć masową na podłożu Vercel AI SDK.

**Typ:** Ucz się
**Języki:** Python, TypeScript
**Wymagania wstępne:** Faza 14 · 01 (Pętla agenta), Faza 14 · 13 (LangGraph)
**Czas:** ~45 minut

## Cele nauczania

- Zidentyfikuj cele wydajności Agno i kiedy mają one znaczenie.
- Nazwij trzy podstawowe elementy Mastry — Agenci, Narzędzia, Przepływy pracy — i obsługiwane adaptery serwerowe.
- Wyjaśnij, dlaczego bezstanowy backend FastAPI o zakresie sesji jest zalecaną ścieżką produkcyjną Agno.
- Wybierz Agno vs Mastra dla danego stosu (najpierw Python vs TypeScript).

## Problem

LangGraph, AutoGen, CrewAI są oparte na frameworku. Zespoły, które chcą „tylko pętli agenta, szybko i w moim środowisku wykonawczym”, sięgają po Agno (Python) lub Mastra (TypeScript). Obaj wymieniają niektóre prymitywy należące do frameworka na rzecz surowej szybkości i lepszego dopasowania do otaczającego stosu.

## Koncepcja

### Agno

- Środowisko wykonawcze Pythona, dawniej Phi-data.
- „Żadnych wykresów, łańcuchów ani zawiłych wzorców — po prostu czysty Python”.
- Cele wydajności określone w dokumentach: utworzenie instancji agenta ~2μs, ~3,75 KiB pamięci na agenta, ~23 dostawców modeli.
- Ścieżka produkcyjna: bezstanowy backend FastAPI o zasięgu sesji. Każde żądanie uruchamia nowego agenta; stan sesji znajduje się w bazie danych.
- Natywny multimodalny (tekst, obraz, audio, wideo, plik) i agentyczny RAG.

Docelowa prędkość ma znaczenie, gdy masz tysiące krótkotrwałych agentów na sekundę (wprowadzanie na czacie, potoki oceny). Mają mniejsze znaczenie, gdy jeden agent działa przez 10 minut.

### Mistrzu

- TypeScript, zbudowany na SDK Vercel AI.
- Trzy elementy podstawowe: **Agenci**, **Narzędzia** (typowane przez ZOD), **Przepływy pracy**.
- Ujednolicony model routera — ponad 3300 modeli od 94 dostawców (marzec 2026 r.).
- Pamięć masowa złożona: pamięć, przepływy pracy, obserwowalność dla różnych backendów; Zalecany ClickHouse ze względu na obserwowalność na dużą skalę.
- Apache 2.0 z katalogami `ee/` w ramach licencji korporacyjnej dostępnej ze źródła.
- Adaptery serwerowe dla Express, Hono, Fastify, Koa; pierwszorzędna integracja Next.js i Astro.
- Dostarcza Mastra Studio (localhost:4111) do debugowania.
- Ponad 22 tys. gwiazdek na GitHubie, ponad 300 tys. pobrań npm tygodniowo w wersji 1.0 (styczeń 2026 r.).

### Pozycjonowanie

Żaden z nich nie próbuje być LangGraphem. Konkurują na:

- **Dopasowanie językowe.** Agno dla zespołów korzystających z Pythona; Mastra dla TypeScript-najpierw.
- **Ergonomia pracy.** Agno = prawie zerowy koszt narzutu; Mastra = zintegrowana z ekosystemem Vercel.
- **Obserwowalność.** Obydwa integrują się z Langfuse/Phoenix/Opik (Lekcja 24), ale Mastra Studio jest własne.

### Kiedy wybrać każdy z nich

- **Agno** — backend Pythona, wielu krótkotrwałych agentów, duże wymagania dotyczące wydajności, sklep FastAPI.
- **Mastra** — backend TypeScript, wdrożenie Next.js / Vercel, ujednolicony routing modelu wielu dostawców, narzędzia typu Zod.
- **LangGraph** (Lekcja 13) — gdy trwały stan i jawne rozumowanie wykresu mają większe znaczenie niż sama prędkość.
- **OpenAI / Claude Agent SDK** — jeśli chcesz uzyskać produktywny kształt dostawcy (lekcje 16–17).

### Gdzie ten wzorzec jest błędny

- **Wydajność dla dobra wydajności.** Wybieranie Agno, ponieważ „2μs” brzmi dobrze, gdy obciążenie wynosi jedno powolne wywołanie agenta na żądanie. Koszty ogólne nie są wąskim gardłem.
- **Zablokowanie ekosystemu.** Integracja Mastry o smaku Vercel to plus w Vercel, minus gdzie indziej.
- **Pomieszanie z licencjami dla przedsiębiorstw.** Katalogi `ee/` Mastry są dostępne w źródłach, a nie w Apache 2.0. Przeczytaj licencje, jeśli planujesz rozwidlenie.

## Zbuduj to

Ta lekcja ma przede wszystkim charakter porównawczy — żaden pojedynczy artefakt kodu nie oddałby sprawiedliwości obu frameworkom. Zobacz `code/main.py`, aby zapoznać się z zabawką side-by-side: minimalny przepływ „uruchom agenta, przesyłaj strumieniowo dane wyjściowe, utrzymuj sesję” zaimplementowany dwukrotnie (raz w kształcie Agno, raz w kształcie Mastry).

Uruchom to:

```
python3 code/main.py
```

Dwa strukturalnie różne, ale funkcjonalnie równoważne ślady.

## Użyj tego

- **Agno** — Backend Pythona wymagający szybkości i kształtu FastAPI.
- **Mastra** — backend TypeScriptu z wieloma dostawcami i prymitywami przepływu pracy.
- Obydwa dostarczają własne haki umożliwiające obserwację. Obydwa integrują się z Langfuse.

## Wyślij to

`outputs/skill-runtime-picker.md` wybiera Agno, Mastra, LangGraph lub pakiet SDK dostawcy na podstawie stosu, budżetu opóźnień i kształtu operacyjnego.

## Ćwiczenia

1. Przeczytaj dokumentację Agno. Przenieś pętlę stdlib ReAct (lekcja 01) do Agno. Co zniknęło? Co zostało?
2. Przeczytaj dokumentację Mastry. Przenieś tę samą pętlę do Mastry. Co zmieniło się w pisaniu narzędzi (Zod vs nic)?
3. Test porównawczy: zmierz opóźnienie instancji agenta na swoim stosie. Czy 2μs Agno ma znaczenie dla Twojego obciążenia pracą?
4. Zaprojektuj migrację: jeśli korzystałeś z CrewAI w Pythonie, co się stanie, jeśli przejdziesz na Agno?
5. Przeczytaj warunki licencji `ee/` firmy Mastra. Jakie ograniczenia miałyby wpływ na rozwidlenie open source?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Agno | „Szybcy agenci Pythona” | Środowisko wykonawcze agenta bezstanowego o zasięgu sesji |
| Mistrz | „Agenci TypeScript w zestawie SDK Vercel AI” | Agenci + Narzędzia + Przepływy pracy + Model Router |
| Ujednolicony model routera | „Dostęp wielu dostawców” | Jeden klient dla ponad 3300 modeli u 94 dostawców |
| Magazyn kompozytowy | „Wiele backendów” | Pamięć/przepływy pracy/obserwowalność, każdy do innego sklepu |
| Studio Mastra | „Lokalny debuger” | localhost:4111 Interfejs użytkownika dla agentów introspekcji |
| Źródło dostępne | „Nie OSS” | Licencja umożliwia czytanie źródeł, ale ogranicza wykorzystanie komercyjne |

## Dalsze czytanie

- [Dokumentacja Agno Agent Framework](https://www.agno.com/agent-framework) — cele wydajnościowe, integracja z FastAPI
- [Dokumentacja Mastra](https://mastra.ai/docs) — elementy podstawowe, adaptery serwerowe, router modelowy
- [Omówienie LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) — alternatywa dla wykresu stanowego
- [Kometa Opik](https://www.comet.com/site/products/opik/) — porównania obserwowalności cytowane przez integracje Mastra