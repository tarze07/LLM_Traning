---

name: runtime-picker
description: Wybierz środowisko wykonawcze agenta produkcyjnego (Agno, Mastra, LangGraph, SDK dostawcy) dla danego stosu, budżetu opóźnień i kształtu operacyjnego.
version: 1.0.0
phase: 14
lesson: 18
tags: [agno, mastra, langgraph, runtime, selection]

---

Biorąc pod uwagę stos, budżet opóźnień, wymagane elementy podstawowe i kształt operacyjny, wybierz środowisko wykonawcze.

Decyzja:

1. Python + FastAPI + tysiące krótkotrwałych agentów na sekundę -> **Agno**.
2. TypeScript + Next.js/Vercel + ujednolicony wielu dostawców -> **Mastra**.
3. Stan trwały, jawny wykres, wznowienie po awarii -> **LangGraph** (Lekcja 13).
4. Pierwszy produkt Claude, wymaga kształtu uprzęży Claude Code -> **Claude Agent SDK** (Lekcja 17).
5. Pierwszy produkt OpenAI, wymaga przekazania + poręczy + śledzenia -> **OpenAI Agents SDK** (Lekcja 16).
6. Zespół wieloagentowy, współbieżność aktor-model, izolacja błędów -> **AutoGen v0.4** / **Microsoft Agent Framework** (Lekcja 14).
7. Współpraca oparta na rolach lub deterministyczne przepływy pracy sterowane zdarzeniami -> **CrewAI** Załoga lub przepływ (Lekcja 15).
8. Żadne z powyższych -> bezpośrednie wywołania API + pętla stdlib z lekcji 01.

Wyprodukuj:

- Krótki dokument decyzyjny: stos, docelowe opóźnienie, potrzebne prymitywy, zaobserwowane kompromisy.
- Minimalne rusztowanie w wybranym czasie działania.
- Plan migracji, jeśli obecnie używane jest inne środowisko wykonawcze.

Twarde odrzucenia:

- Wybieranie Agno lub Mastry wyłącznie ze względu na „wydajność”, gdy obciążenie pracą wynosi jedno wolne połączenie na żądanie. Wydajność rzadko jest wąskim gardłem.
- Wybieranie środowiska wykonawczego TypeScript w monorepo Pythona bez uzasadnienia. Kod agenta wielojęzycznego jest podatkiem operacyjnym.
- Wybieranie LangGraph dla krótkich zadań bezstanowych. Wskaźnik kontrolny zwiększa obciążenie, którego unika prosty przepływ pracy (lekcja 12).

Zasady odmowy:

- Jeśli użytkownik chce „porównać wszystkie pięć środowisk wykonawczych”, odmów. Test porównawczy obciążenia pracą; Testy porównawcze dostawców ram mają charakter kierunkowy.
- Jeśli użytkownik chce samodzielnie hostować funkcje `ee/` Mastry, odmów i wskaż warunki licencji.
- Jeśli produkt wymaga długotrwałej pracy asynchronicznej (z godzin na dni), odrzuć opcję samodzielnego hostowania i przekieruj do agentów zarządzanych Claude lub architektury opartej na kolejkach (Lekcja 29).

Dane wyjściowe: dokument decyzyjny + szkielet + plik README. Zakończ słowami „Co dalej czytać”, wskazując Lekcję 24 (obserwowalność) i Lekcję 29 (środowiska produkcyjne) dla warstwy operacyjnej powyżej platformy.