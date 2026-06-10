---

name: runtime-picker
description: Wybierz produkcyjne środowisko uruchomieniowe dla agenta (Agno, Mastra, LangGraph, SDK dostawcy) na podstawie stosu technologicznego, dopuszczalnych opóźnień i wymagań operacyjnych.
version: 1.0.0
phase: 14
lesson: 18
tags: [agno, mastra, langgraph, runtime, selection]

---

Na podstawie stosu technologicznego, dopuszczalnego budżetu opóźnień, wymaganych komponentów bazowych i specyfiki operacyjnej wybierz optymalne środowisko uruchomieniowe (runtime).

Kryteria wyboru:

1. Język Python + FastAPI + tysiące krótkotrwałych agentów na sekundę -> **Agno**.
2. Język TypeScript + Next.js/Vercel + ujednolicona integracja z wieloma dostawcami -> **Mastra**.
3. Trwałe zarządzanie stanem, modelowanie logiki za pomocą grafu, wznawianie pracy po awarii -> **LangGraph** (Lekcja 13).
4. Projekt oparty na modelach Claude, wymagający funkcjonalności znanych z Claude Code -> **Claude Agent SDK** (Lekcja 17).
5. Projekt oparty na modelach OpenAI, wymagający przekazywania zadań (handoffs), barier ochronnych (guardrails) oraz śledzenia (tracingu) -> **OpenAI Agents SDK** (Lekcja 16).
6. Architektura wieloagentowa, współbieżność oparta na modelu aktora, izolacja błędów -> **AutoGen v0.4** / **Microsoft Agent Framework** (Lekcja 14).
7. Współpraca agentów oparta na rolach lub deterministyczne przepływy pracy sterowane zdarzeniami -> **CrewAI** (Crew lub Flows) (Lekcja 15).
8. Żadne z powyższych -> bezpośrednia integracja z API i uproszczona pętla oparta na bibliotece standardowej (Lekcja 1).

Przygotuj:

- Krótki dokument uzasadniający decyzję (Architecture Decision Record - ADR): wybrany stos, docelowe opóźnienia, wymagane mechanizmy bazowe oraz zidentyfikowane kompromisy.
- Minimalny szablon projektu (scaffold) w wybranym środowisku uruchomieniowym.
- Plan migracji (jeśli aplikacja korzystała dotychczas z innego środowiska).

Kategoryczne odrzucenia (Twarde kryteria):

- Wybór Agno lub Mastry wyłącznie ze względu na deklarowaną wydajność w mikrosekundach, gdy rzeczywistym obciążeniem aplikacji jest pojedyncze, powolne wywołanie LLM na żądanie. W takich sytuacjach wydajność frameworka nie jest wąskim gardłem.
- Wybór środowiska w języku TypeScript w monorepo opartym na Pythonie bez wyraźnego, silnego uzasadnienia. Utrzymywanie kodu agentów w różnych językach zwiększa koszty utrzymania systemu.
- Wybór LangGraph do prostych, bezstanowych zadań. Mechanizmy zarządzania stanem generują niepotrzebny narzut, którego można uniknąć stosując prosty liniowy przepływ pracy (Lekcja 12).

Zasady odmowy wykonania usługi (Refusal rules):

- Jeśli użytkownik żąda porównania wszystkich dostępnych środowisk uruchomieniowych za pomocą ogólnych testów, odmów. Zamiast tego przeprowadź testy porównawcze na rzeczywistym obciążeniu roboczym (workload), ponieważ ogólne benchmarki dostarczane przez twórców frameworków mają charakter czysto orientacyjny.
- Jeśli użytkownik chce samodzielnie hostować funkcje z katalogów komercyjnych `ee/` Mastry w projekcie open source, odmów i wskaż na ograniczenia licencyjne.
- Jeśli produkt wymaga długotrwałych zadań asynchronicznych (trwających od kilku godzin do kilku dni), odmów wdrożenia opartego na klasycznym własnym hostingu i zarekomenduj rozwiązanie Claude Managed Agents lub architekturę opartą na kolejkach zadań (Lekcja 29).

Pliki wynikowe: dokument decyzyjny (ADR) + szkielet kodu + plik README. Zakończ sekcją „Dalsza lektura”, wskazując na Lekcję 24 (telemetria i obserwowalność) oraz Lekcję 29 (środowiska produkcyjne) w celu wdrożenia warstwy operacyjnej nad wybraną platformą.
