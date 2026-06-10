# SDK agentów OpenAI: Przekazywanie, poręcze, śledzenie

> OpenAI Agents SDK to lekka platforma wieloagentowa zbudowana w oparciu o API Responses. Pięć elementów podstawowych: agent, przekazanie, poręcz, sesja, śledzenie. Przekazania to narzędzia o nazwie `transfer_to_<agent>`. Zadziałanie poręczy na wejściu lub wyjściu. Śledzenie jest domyślnie włączone.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (pętla agenta), faza 14 · 06 (użycie narzędzi)
**Czas:** ~75 minut

## Cele nauczania

- Wymień pięć elementów podstawowych pakietu SDK OpenAI Agents.
- Wyjaśnij przekazania: dlaczego są modelowane jako narzędzia, jaką nazwę kształtu widzi model i jak przenosi się kontekst.
- Rozróżnij poręcze wejściowe, wyjściowe i poręcze narzędziowe; wyjaśnij `run_in_parallel` vs tryb blokowania.
- Zaimplementuj środowisko wykonawcze stdlib z przekazywaniem + poręczami + śledzeniem w stylu zakresu.

## Problem

Agenci, którzy nie potrafią delegować zadań w sposób czysty, wrzucają wszystko do jednego monitu. Agenci bez barier ochronnych wysyłają informacje umożliwiające identyfikację, dane wyjściowe naruszające zasady lub zapętlają się na zawsze. Pakiet SDK OpenAI kodyfikuje trzy podstawowe elementy, które ułatwiają pracę wielu agentów.

## Koncepcja

### Pięć prymitywów

1. **Agent.** LLM + instrukcje + narzędzia + przekazania.
2. **Przekazanie.** Delegowanie innemu agentowi. Reprezentowane w modelu jako narzędzie o nazwie `transfer_to_<agent_name>`.
3. **Poręcz.** Walidacja danych wejściowych (tylko pierwszy agent), danych wyjściowych (tylko ostatni agent) lub wywołania narzędzia (dla każdego narzędzia funkcyjnego).
4. **Sesja.** Automatyczna historia rozmów w kolejnych turach.
5. **Tracing.** Wbudowane rozpiętości dla generacji LLM, wywołań narzędzi, przekazywania, poręczy.

### Przekazanie jako narzędzie

Model widzi `transfer_to_billing_agent` na swojej liście narzędzi. Wywołanie go sygnalizuje środowisku wykonawczemu:

1. Skopiuj kontekst rozmowy (lub zwiń go za pomocą `nest_handoff_history` beta).
2. Zainicjuj agenta docelowego za pomocą jego instrukcji.
3. Kontynuuj cykl z agentem docelowym.

Oto stworzony wzorzec nadzorcy (Lekcja 13 / Lekcja 28).

### Poręcze

Trzy smaki:

- **Wprowadź poręcze.** Uruchom na wejściu pierwszego agenta. Odrzucaj żądania niebezpieczne lub wykraczające poza zakres przed jakimkolwiek połączeniem LLM.
- **Poręcze wyjściowe.** Działają na wyjściu ostatniego agenta. Wychwytuj wycieki danych osobowych, naruszenia zasad i zniekształcone odpowiedzi.
- **Poręcze narzędzi.** Uruchomienie narzędzia według funkcji. Zweryfikuj argumenty, sprawdź uprawnienia, wykonaj audyt.

Tryb:

- **Równolegle** (domyślnie). Guardrail LLM biegnie wzdłuż głównego LLM. Niższe opóźnienie ogona. W przypadku potknięcia główna praca LLM zostaje odrzucona (odpad żetonowy).
- **Blokowanie** (`run_in_parallel=False`). Guardrail LLM biegnie jako pierwszy. W przypadku potknięcia nie marnuje się żadnych żetonów na główne połączenie.

Tripwires podnosi `InputGuardrailTripwireTriggered` / `OutputGuardrailTripwireTriggered`.

### Śledzenie

Domyślnie włączone. Każda generacja LLM, wywołanie narzędzia, przekazanie i poręcze emitują rozpiętość. `OPENAI_AGENTS_DISABLE_TRACING=1` rezygnuje. Liczba fanów `add_trace_processor(processor)` obejmuje Twój własny backend i rozwiązania OpenAI.

### Sesje

`Session` przechowuje historię rozmów w backendie (SQLite, Redis, niestandardowe). `Runner.run(agent, input, session=session)` automatycznie ładuje i dołącza.

### Gdzie ten wzorzec jest błędny

- **Dryf przekazania.** Agent A przekazuje agentowi B, który przekazuje agentowi A. Dodaj licznik przeskoków.
- **Obejście poręczy.** Poręcze narzędzi działają tylko w przypadku narzędzi funkcyjnych; wbudowane narzędzia (czytnik plików, pobieranie z Internetu) wymagają osobnej polityki.
- **Nadmierne śledzenie.** Treść poufna w zakresach. Sparuj z regułami przechwytywania treści Otel GenAI (Lekcja 23) — przechowuj na zewnątrz, odwołaj się według identyfikatora.

## Zbuduj to

`code/main.py` implementuje kształt SDK w stdlib:

- `Agent`, `FunctionTool`, `Handoff` (jako narzędzie funkcyjne z semantyką transferu).
- `Runner` z barierkami wejściowymi/wyjściowymi/narzędziowymi, wysyłaniem przekazań i licznikiem przeskoków.
- Prosty emiter zakresu pokazujący kształt śladu.
- Agent selekcji, który przekazuje rozliczenia lub wsparcie na podstawie zapytania użytkownika; zadziałanie poręczy na jednym wejściu.

Uruchom to:

```
python3 code/main.py
```

Ślad pokazuje dwa udane przekazania, jedno wyłączenie poręczy wejściowej i drzewo opinające odzwierciedlające to, co emituje prawdziwy zestaw SDK.

## Użyj tego

- **OpenAI Agents SDK** dla produktów opartych na OpenAI.
- **SDK dla agenta Claude** (lekcja 17) dla produktów Claude-first.
- **LangGraph** (Lekcja 13), gdy chcesz mieć wyraźny stan i trwałe CV.
- **Niestandardowe**, gdy potrzebujesz dokładnej kontroli (głos, wielu dostawców, wdrożenia stowarzyszone).

## Wyślij to

`outputs/skill-agents-sdk-scaffold.md` stanowi szkielet aplikacji pakietu Agents SDK z agentem selekcji, przekazywaniem, poręczami wejścia/wyjścia/narzędzi, magazynem sesji i procesorem śledzenia.

## Ćwiczenia

1. Dodaj licznik przeskoków przekazania: odrzuć po N transferach. Śledź zachowanie.
2. Zaimplementuj `nest_handoff_history` jako opcję — zwiń poprzednie wiadomości w jedno podsumowanie przed przesłaniem.
3. Napisz blokującą poręcz wyjściową. Porównaj opóźnienia w przypadku komunikatów, które powodują jego wyłączenie, z tymi, które przechodzą.
4. Podłącz `add_trace_processor` do rejestratora JSON. Jaki kształt emituje na przęsło?
5. Przeczytaj dokumentację SDK. Przenieś swoją zabawkę stdlib do `openai-agents-python`. Co źle modelowałeś?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Agent | „LLM + instrukcje” | Typ agenta w SDK; posiada narzędzia i przekazy |
| Przekazanie | „Przeniesienie” | Narzędzie do delegowania wywołań modelu do innego agenta |
| Poręcz | „Sprawdzanie zasad” | Walidacja wejścia/wyjścia/wywołania narzędzia |
| Tripwire | „Wycieczka poręczą” | Wyjątek zgłaszany w przypadku odrzucenia poręczy |
| Sesja | „Sklep z historią” | Pamięć rozmów utrzymywała się pomiędzy uruchomieniami |
| Śledzenie | „Rozpiętości” | Wbudowana obserwowalność przez LLM + narzędzie + przekazanie + poręcz |
| Blokowanie poręczy | „Kontrola sekwencyjna” | Poręcz biegnie pierwsza; żadnych symbolicznych strat w podróży |
| Poręcz równoległa | „Kontrola współbieżna” | Poręcz biegnie obok; mniejsze opóźnienia, marnowanie tokenów podczas podróży |

## Dalsze czytanie

- [Dokumentacja pakietu SDK OpenAI Agents](https://openai.github.io/openai-agents-python/) — elementy podstawowe, przekazania, poręcze, śledzenie
- [Omówienie zestawu SDK Claude Agent](https://platform.claude.com/docs/en/agent-sdk/overview) — odpowiednik o smaku Claude
– [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-efektywne-agents) — kiedy w ogóle sięgać po przejęcia
- [Konwencje semantyczne OpenTelemetry GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — standardowy zestaw SDK agentów obejmuje mapę