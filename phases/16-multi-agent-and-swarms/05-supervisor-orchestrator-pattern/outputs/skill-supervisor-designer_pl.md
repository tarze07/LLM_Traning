---

name: supervisor-designer
description: Zaprojektuj system przełożony/orkiestrator-pracownik dla danego zapytania w stylu badawczym, określając monit wiodący, role pracowników, zasady dekompozycji i szablon syntezy.
version: 1.0.0
phase: 16
lesson: 05
tags: [multi-agent, supervisor, orchestrator, anthropic-research, langgraph]

---

Biorąc pod uwagę zapytanie użytkownika, które korzysta z równoległych badań podagentów, utwórz projekt wzorca nadzorcy gotowy do podłączenia do dowolnej platformy (LangGraph, OpenAI Agents SDK, CrewAI Hierarchical).

Wyprodukuj:

1. **Oszacowanie złożoności.** Czy to zapytanie jest proste (1 agent, 3–10 wywołań narzędzi), średnie (2–4 pracowników) czy złożone (5+ pracowników)? Uzasadnij jednym zdaniem, korzystając z heurystyki wysiłku skali firmy Anthropic.
2. **Monitor systemu leadów.** Musi zawierać: (a) instrukcje rozkładu, (b) instrukcje syntezy, (c) wyraźną zasadę, że lead nigdy nie czyta surowych treści źródłowych, a jedynie streszczenia pracowników.
3. **Podpowiedzi systemu pracownika.** Po jednym na rolę, każdy z podaniem wąskiego zakresu i formatu wyjściowego, jakiego oczekuje potencjalny klient.
4. **Zasady rozkładu pytań podrzędnych.** W jaki sposób lead dzieli zapytanie? Najpierw szerokie, potem wąskie, czy bezpośredni rozkład? Co dyskwalifikuje pytanie podrzędne (pokrywa się z innym, jest zbyt szerokie)?
5. **Szablon syntezy.** Jasna zasada rozwiązywania konfliktów: jeśli dwóch pracowników przedstawi sprzeczne fakty, synteza musi wydobyć na światło dzienne różnicę zdań, a nie milczeć wybieranie jednego.
6. **Parowanie modeli.** Który model dla leada (poziom rozumowania), który dla pracowników (poziom szybszy/tańszy). Wyjaśnij kompromis.
7. **Wymagania obserwowalności.** Minimalne punkty śledzenia: plan, początek/koniec każdego pracownika, wejście syntezy, wyjście syntezy.

Twarde odrzucenia:

- Dowolny projekt, w którym przewód sam korzysta z narzędzia. Prowadzić tylko plany i syntezę.
- Podpowiedzi pracownika, które pozwalają na zmianę zakresu (np. „zbadaj wszystko, co jest powiązane z X” bez ograniczeń).
- Szablony syntezy, które ukrywają konflikty.

Zasady odmowy:

- Jeśli zapytanie jest proste (w sumie mniej niż 10 wywołań narzędzi), odrzuć projekt i zamiast tego zarekomenduj jednego agenta. Przytocz ustalenia dotyczące kosztu tokena Anthropic 15×.
- Jeśli zapytanie jest sekwencyjne (krok 2 wymaga danych wyjściowych kroku 1), odrzuć i zamiast tego zarekomenduj wzorzec potoku/łańcucha.
- Jeśli użytkownik optymalizuje pod kątem determinizmu i audytu, odmów przełożonemu i zalecaj statyczny wykres LangGraph.

Wynik: jednostronicowy opis projektu. Zacznij od oszacowania złożoności i oceny dopasowania wzorca („pasuje przełożony”). Zamknij, wyświetlając przypomnienie o wdrożeniu Rainbow, jeśli system będzie działał nieprzerwanie.