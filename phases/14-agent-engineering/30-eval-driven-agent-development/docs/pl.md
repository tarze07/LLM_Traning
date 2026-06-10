# Rozwój agentów oparty na ewaluacji (Eval-Driven Agent Development)

> Wytyczne Anthropic: "zacznij od prostych promptów, optymalizuj je za pomocą kompleksowej ewaluacji, a wieloetapowe systemy agentowe dodawaj tylko wtedy, gdy są potrzebne". Ewaluacja to nie jest ostatni krok. To zewnętrzna pętla, która napędza każdy inny wybór w Fazie 14.

**Typ:** Nauka + Budowa
**Języki:** Python (stdlib)
**Wymagania wstępne:** Cała Faza 14.
**Czas:** ~60 minut

## Cele kształcenia

- Wymienienie trzech warstw ewaluacji — statyczne benchmarki, niestandardowe (offline), produkcyjne (online) — oraz do czego każda z nich służy.
- Wyjaśnienie szczelnej pętli ewaluator-optymalizator (evaluator-optimizer).
- Opisanie najlepszych praktyk na rok 2026: testy ewaluacyjne (evals) żyją obok kodu, działają w CI i blokują pull requesty (gating PRs).
- Powiązanie każdej lekcji z Fazy 14 z wygenerowanym przez nią przypadkiem testowym.

## Problem

Agenci zaliczają dema (wersje pokazowe). Zawodzą jednak na produkcji w sposób, którego dema nie są w stanie przewidzieć. Benchmarki odpowiadają na pytanie "czy ten model jest ogólnie zdolny?", a nie "czy ten agent dostarcza odpowiednie łatki dla mojego produktu?". Odpowiedź brzmi: ewaluacja na trzech warstwach, działająca w sposób ciągły, gdzie każdy strażnik (guardrail) i każda wyuczona reguła mapuje się na konkretny przypadek testowy.

## Koncepcja

### Trzy warstwy ewaluacji

1. **Statyczne benchmarki** — SWE-bench Verified dla kodu (Lekcja 19), WebArena/OSWorld do przeglądania stron / interakcji z systemem (Lekcja 20), GAIA jako test ogólny (Lekcja 19), BFCL V4 do używania narzędzi (Lekcja 06). Używaj ich do porównywania modeli i blokowania regresji. Zanieczyszczenie danych jest realne: SWE-bench+ wykazał 32,67% wycieku rozwiązań. Zawsze raportuj wyniki Verified / audytowane przez człowieka (+-audited).

2. **Niestandardowe testy offline** — dopasowane do specyfiki twojego produktu:
   - LLM-as-judge (LLM jako sędzia) (Langfuse, Phoenix, Opik — Lekcja 24).
   - Oparte na wykonaniu (uruchom łatkę, sprawdź testy).
   - Oparte na trajektorii (porównaj sekwencje akcji z wzorcową, "złotą" ścieżką; OSWorld-Human pokazuje, że najlepsi agenci potrzebują od 1,4x do 2,7x więcej kroków niż złoty standard).

3. **Testy online** — środowisko produkcyjne:
   - Odtwarzanie sesji (Langfuse).
   - Alerty wywoływane przez strażników (guardrails) (Lekcja 16, 21).
   - Śledzenie kosztów / opóźnień każdego kroku (Lekcja 23, zakresy OTel).

### Ewaluator-optymalizator (Anthropic)

Szczelna pętla:

1. Oferent (Proposer) generuje wynik.
2. Ewaluator go ocenia.
3. Proces udoskonalania trwa, aż ewaluator przepuści wynik.

To jest zgeneralizowany mechanizm Self-Refine (Lekcja 05). Każdy przepływ agenta, na którym ci zależy, może zostać obudowany ewaluatorem-optymalizatorem w celu zwiększenia niezawodności.

### Najlepsze praktyki z 2026 roku

- Ewaluacje żyją tuż obok kodu.
- Są uruchamiane w CI przy każdym PR (Pull Request).
- Stanowią bramkę (gate) przy merge'u bazującą na wynikach (np. "regresja nie większa niż 5% w stosunku do gałęzi main").
- Każdy strażnik (guardrail) mapuje się na przypadek ewaluacyjny.
- Każda wyuczona reguła (Reflexion, pro-workflow learn-rule) mapuje się na przypadek, w którym system wcześniej zawiódł.

### Podsumowanie Fazy 14

Każda lekcja w Fazie 14 generuje przypadki testowe dla ewaluacji:

| Lekcja | Wygenerowany przypadek testowy |
|--------|------------------------|
| 01 Pętla Agenta | Wyczerpanie budżetu, zabezpieczenie przed nieskończoną pętlą |
| 02 ReWOO | Planista odpowiednio dostosowuje plan, gdy narzędzie zawiedzie |
| 03 Reflexion | Wyuczone refleksje są stosowane przy ponownej próbie |
| 05 Self-Refine/CRITIC | Sędzia (judge) przepuszcza udoskonalony wynik |
| 06 Narzędzia | Wymuszenie argumentów działa; nieznane narzędzia są odrzucane |
| 07-10 Pamięć | Cytaty z wyszukiwania odpowiadają źródłom; nieaktualne fakty tracą ważność |
| 12 Wzorce Workflow | Każdy wzorzec generuje poprawne dane wyjściowe |
| 13 LangGraph | Wznowienie (resume) odtwarza stan w dokładnie taki sam sposób |
| 14 AutoGen (Aktorzy) | DLQ wyłapuje zawieszone lub zepsute handlery |
| 16 OpenAI Agents SDK | Strażnik reaguje na właściwe dane wejściowe |
| 17 Claude Agent SDK | Wyniki podagentów (subagents) wracają do orkiestratora |
| 19-20 Benchmarki | Wynik SWE-bench Verified, wskaźnik sukcesu WebArena, wydajność OSWorld |
| 21 Computer Use | Zabezpieczenie krok po kroku wyłapuje wstrzyknięty kod DOM |
| 23 OTel | Zakresy emitują wymagane atrybuty |
| 26 Tryby Awarii | Detektory oznaczają znane błędy |
| 27 Prompt Injection | PVE odrzuca zatrute wyniki z pamięci (retrievals) |
| 28 Orkiestracja | Nadzorca kieruje zadanie do odpowiedniego specjalisty |
| 29 Kształty Uruchomieniowe | DLQ radzi sobie z wyższym (N%) poziomem niepowodzeń |

Jeśli twój zestaw testów obejmuje przypadki dla każdego z nich, masz opanowaną Fazę 14.

### Gdzie rozwój oparty na ewaluacji zawodzi

- **Brak punktu odniesienia (baseline).** Ewaluacje bez zapisanego ostatniego dobrego stanu (last-known-good) są nieczytelne. Przechowuj bazowe wyniki.
- **Sędzia LLM bez uziemienia (grounding).** Sędziowie też halucynują. Wzorzec CRITIC (Lekcja 05) — sędzia weryfikuje dane w oparciu o narzędzia zewnętrzne.
- **Nadmierne dopasowanie do testów (Over-fitting).** Optymalizacja pod ewaluację mija się z przydatnością na produkcji. Zmieniaj przypadki testowe (rotate cases).
- **Niestabilne ewaluacje (Flaky evals).** Niedeterministyczne przypadki generują fałszywe alarmy. Ustawiaj "ziarna" (pin seeds), zapisuj zrzuty stanu (snapshot state).

## Zbuduj to

`code/main.py` to szkielet ewaluacyjny z biblioteki standardowej (stdlib):

- Rejestr przypadków testowych z kategoriami (benchmark, offline, online).
- Oskryptowany agent testowy.
- Pętla ewaluatora-optymalizatora: zaproponuj, oceń, udoskonalaj aż do pozytywnego wyniku lub osiągnięcia maksymalnej liczby rund.
- Bramka CI: zagregowany wskaźnik sukcesu + sprawdzanie regresji na podstawie punktu odniesienia (baseline).

Uruchom to:

```bash
python3 code/main.py
```

Wyjście: status przejścia/błędu dla każdego przypadku, flaga regresji, werdykt bramki CI.

## Użyj tego

- Pisz przypadki ewaluacyjne w tym samym repozytorium, w którym znajduje się kod agenta.
- Uruchamiaj je dla każdego PR za pomocą CI.
- Przerwij proces budowania (fail build) w przypadku wystąpienia regresji.
- Śledź wskaźnik zaliczeń (pass rate) w czasie.
- Łącz każdy nowy błąd na produkcji z nowym przypadkiem testowym.

## Wdróż to

`outputs/skill-eval-suite.md` buduje trzywarstwowy pakiet ewaluacyjny dla produktu, wykorzystujący bramki CI i śledzenie regresji.

## Ćwiczenia

1. Weź jedną z awarii ze swojego środowiska produkcyjnego. Napisz przypadek ewaluacyjny, który ją odwzorowuje. Czy twój agent radzi sobie z nim teraz?
2. Zbuduj kryteria dla sędziego LLM, dla twojej domeny operacyjnej z trzema wymiarami (fakty, ton wypowiedzi, zasięg operacyjny). Przetestuj to na 50 sesjach.
3. Podłącz pakiet ewaluacyjny do CI. Wymuś zatrzymanie builda na poziomie >=5% wykazanej regresji.
4. Dodaj metrykę na podstawie trajektorii i jej przebytej wydajności (trajectory-efficiency): ile kroków wykonał dany agent w odniesieniu do ludzkiej wzorcowej interakcji (gold trajectory)?
5. Odwzoruj każdą lekcję Fazy 14 względem danego przypadku ewaluacyjnego z twojego osobistego pakietu (suite). Czy zauważasz jakieś pominiecie? Jeśli tak to jest to ubytek, który powinieneś wyeliminować.

## Kluczowe pojęcia

| Termin | Co mówią ludzie | Co to w rzeczywistości oznacza |
|------|----------------|------------------------|
| Statyczny benchmark (Static benchmark) | "Test z półki" | SWE-bench, GAIA, AgentBench, WebArena, OSWorld |
| Niestandardowy test offline (Custom offline eval) | "Test domenowy" | Oparty na sędziowaniu ze strony LLM (LLM-as-judge) / bazowaniu na wykonywaniu poleceń lub wyznaczaniu trajektorii pracy specyficznej dla twojej grupy |
| Test produkcyjny (Online eval) | "Test produkcyjny" | System retransmisji sesyjnej (Session replay), powiadomień połączonych ze strażnikami (guardrails), koszty kroków / lub operacji bazujących na śledzeniu opóźnień |
| Ewaluator-optymalizator (Evaluator-optimizer) | "Zaproponuj-oceń-popraw" | Podejmuj systematyczne iteracje celem przejścia i pomyślnego testu po stronie sędziego weryfikacyjnego (judge) |
| Bramka CI (CI gate) | "Merge blocker" | Przerwanie zatwierdzania zapisu z błędem w systemie budowania podparte testem wykazanej regresji testu |
| Punkt odniesienia (Baseline) | "Ostatnio-znany-z-dobrym-stanem" | Wyznaczony stan stanowiący podstawowy model zapobiegający powstawaniu odchyleń od normy operacyjnej |
| Wydajność trajektorii (Trajectory efficiency) | "Kroki w porównaniu do standardu" | Wskaźnik liczby zrealizowanych na szlaku operacyjnym kroków podejmowanych przez danego z agentów przez nałożenie wzorca zachowania wykreowanego przez człowieka w danym wariancie zadania |

## Dalsza lektura

- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — "zacznij prosto, optymalizuj ewaluacjami"
- [OpenAI, SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) — moderowany benchmark testowy
- [Berkeley Function Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html) — zestaw weryfikujący pod względem integracji z narzędziami
- [Langfuse docs](https://langfuse.com/) — testy + retransmisje sesyjne w aspekcie praktycznym