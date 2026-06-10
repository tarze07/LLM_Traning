---

name: handoff-designer
description: Zaprojektuj topologię przekazywania dla systemu w stylu Swarm/Agents-SDK: którzy agenci istnieją, jakie przekazania mogą wywołać, jaki transfer kontekstu.
version: 1.0.0
phase: 16
lesson: 11
tags: [multi-agent, swarm, handoff, openai-agents-sdk]

---

Biorąc pod uwagę zadanie stojące przed użytkownikiem (często segregacja lub routing oparty na umiejętnościach), utwórz topologię przekazania gotową do mapowania na OpenAI Swarm lub SDK OpenAI Agents.

Wyprodukuj:

1. **Spis agentów.** Każdy agent: nazwa, cel w jednym zdaniu, narzędzia i inni agenci, którym może przekazać.
2. **Funkcje przekazywania.** Podpisy narzędzi dla każdego agenta. Każda funkcja przekazania zwraca agenta docelowego.
3. **Zasady transferu kontekstu.** Na każdym krańcu przekazania: pełna historia, N ostatnich wiadomości lub podsumowanie migawki. Uzasadniać.
4. **Poręcze ochronne.** Weryfikacja danych wejściowych dla każdego agenta (jakie monity mogą powodować przekazanie do wrażliwych specjalistów), uwierzytelnianie przy przekazywaniu, jeśli jest to konieczne.
5. **Wykrywanie pętli.** Reguła wykrywania ping-ponga (np. „A przekazał B; B przekazał z powrotem A” występująca więcej niż raz z rzędu).
6. **Zachowanie awaryjne.** Jeśli brakuje celu przekazania (usunięty agent, błąd uwierzytelnienia), który agent obsługuje sesję.
7. **Plan sesji / pamięci.** Określa, czy używać sesji pakietu Agents SDK, pamięci zarządzanej przez rozmówcę, czy też nie używać wcale pamięci.

Twarde odrzucenia:

- Dowolny projekt przełączania bez wykrywania pętli.
- Funkcje przekazywania, które przekazują pełną historię specjalistom z różnymi uprawnieniami do narzędzi (zagrożenie bezpieczeństwa).
- Projekty, które zakładają bezstanowe zachowanie Swarma, ale wymagają pamięci wieloobrotowej — zamiast tego korzystają z sesji Agents SDK.

Zasady odmowy:

- Jeśli zadanie wymaga równoległego wykonania, odrzuć Swarm i zamiast tego poleć przełożonego (Lekcja 05).
- Jeśli zadanie wymaga deterministycznego audytu/powtórki, odmów i poleć statyczny wykres LangGraph.
- Jeśli zadanie jest prostym DAG składającym się z etapów (badania → kod → recenzja), zamiast tego polecamy CrewAI Sequential.

Wynik: jednostronicowy opis przekazania. Zakończ notatką bezpieczeństwa dotyczącą tego, jak szybkie wstrzyknięcie może wywołać niechciane przekazania i jakie bariery to blokują.