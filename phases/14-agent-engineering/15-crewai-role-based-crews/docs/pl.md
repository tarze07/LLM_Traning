# CrewAI: Załogi i przepływy oparte na rolach

> CrewAI to platforma wieloagentowa oparta na rolach na rok 2026. Cztery elementy podstawowe: Agent, Zadanie, Załoga, Proces. Dwa kształty najwyższego poziomu: Załogi (autonomiczna współpraca oparta na rolach) i Przepływy (sterowane zdarzeniami, deterministyczne). Dokumenty są bez ogródek: „w przypadku dowolnej aplikacji gotowej do produkcji zacznij od przepływu”.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 12 (Wzorce przepływu pracy), Faza 14 · 14 (Model aktora)
**Czas:** ~75 minut

## Cele nauczania

- Wymień cztery podstawowe elementy CrewAI (Agent, Zadanie, Załoga, Proces) i co każdy z nich posiada.
- Rozróżnij proces sekwencyjny, hierarchiczny i planowany proces konsensusu; wybierz jedno na każde obciążenie.
- Odróżnij załogi (autonomiczne, oparte na rolach) od przepływów (deterministyczne sterowane zdarzeniami) i wyjaśnij zalecenia dotyczące produkcji dokumentów.
- Narzędzia drutowe z dekoratorem `@tool` i podklasą `BaseTool`; powód dotyczący ustrukturyzowanych wyników w porównaniu z wolnym tekstem.
- Wymień cztery typy pamięci CrewAI i określ, kiedy każdy z nich się opłaca.
- Zaimplementuj standardową załogę składającą się z trzech agentów (badacz, autor, redaktor), która tworzy brief.
- Znajdź trzy tryby awarii CrewAI: natychmiastowe wzdęcia, podatek od menedżera-LLM, kruche przekazania.

## Problem

Zespoły wdrażające platformy wieloagentowe uderzają w ten sam mur. „Autonomiczna współpraca” brzmi świetnie w wersji demonstracyjnej. Następnie klient zgłasza błąd i potrzebujesz deterministycznej powtórki. Lub finanse pytają, ile kosztuje załoga kierowana przez LLM za przejazd. Lub dyżurujący musi wiedzieć, który agent utknął w martwym punkcie o 3 rano.

Załogi kierowane przez LLM w dowolnej formie nie odpowiadają na żadne z nich w sposób czysty. Czyste DAG odpowiadają na wszystkie pytania, ale tracą charakter eksploracyjny, jakiego potrzebuje agent przeprowadzający burzę mózgów.

Podział CrewAI jest uczciwy w kwestii handlu. Załogi do współpracy, pracy eksploracyjnej opartej na rolach. Przepływy dla produkcji sterowanej zdarzeniami, należącej do kodu i podlegającej audytowi. Ta sama struktura, dwa kształty, wybór na powierzchnię.

## Koncepcja

### Cztery elementy podstawowe

Powierzchnia CrewAI jest niewielka. Zapamiętaj to, a reszta to konfiguracja.

- **Agent.** `role + goal + backstory + tools + (optional) llm`. Fabuła jest nośna. Kształtuje ton, osąd, kiedy agent przestaje. Narzędzia to funkcje, które agent może wywołać (więcej poniżej).
- **Zadanie.** `description + expected_output + agent + (optional) context + (optional) output_pydantic`. Jednostka pracy wielokrotnego użytku. `expected_output` to umowa. `context` wyświetla listę zadań nadrzędnych, których dane wyjściowe są przekazywane. `output_pydantic` wymusza uporządkowany kształt.
- **Załoga.** Kontener. Jest właścicielem listy `agents`, listy `tasks`, `process` i opcjonalnie `memory` + `verbose` + `manager_llm` ustawienia.
- **Proces.** Strategia wykonania. Sekwencyjny, hierarchiczny, konsensus (planowany). Wybiera kształt biegu.

Agenci nie widzą się bezpośrednio. Zadania agentów referencyjnych. Załoga sekwencjonuje zadania. Proces decyduje, kto wybierze następne zadanie. Oto cały model mentalny.

> **Zatwierdzono względem** CrewAI 0.86 (2026-05). Nowsze wersje mogą zmieniać nazwy lub łączyć typy procesów; sprawdź [dokumentację procesów CrewAI](https://docs.crewai.com/concepts/processes), zanim zaczniesz polegać na konkretnym kształcie.

### Sekwencyjne, hierarchiczne i konsensusowe

- **Sekwencyjne.** Zadania uruchamiane w kolejności deklaracji. Dane wyjściowe zadania N są dostępne jako `context` do zadania N+1. Najniższy koszt. Najbardziej przewidywalne. Użyj, gdy kolejność jest ustalona.
- **Hierarchiczny.** Agent menedżerski (oddzielne połączenie LLM) łączy specjalistów. CrewAI uruchamia menedżera z konfiguracji `manager_llm` lub z konfiguracji domyślnej. Menedżer wybiera kolejne zadanie w każdej rundzie i może odmówić wykonania zadania lub zmienić jego trasę. Użyj, jeśli masz czterech lub więcej specjalistów, a zamówienie naprawdę zależy od wcześniejszych wyników.
- **Konsensus.** Planowane, obecnie nie zaimplementowane w publicznym API. Dokumenty zastrzegają tę nazwę dla przyszłego procesu opartego na głosowaniu. Nie polegaj na tym dzisiaj.

Hierarchical dodaje wezwanie LLM (menedżera) na rundę do każdego wezwania specjalisty. Koszt tokena może potroić się w pięciu krokach. Płać tylko wtedy, gdy potrzebujesz routingu.

### Załogi kontra przepływy

Takie są ramy, według których lekarze będą prowadzić badania w 2026 r.

- **Załoga.** Autonomia oparta na LLM. Framework wybiera kształt w czasie wykonywania. Nadaje się do: badań, burzy mózgów, pierwszych wersji roboczych, wszędzie tam, gdzie ścieżka jest częścią odpowiedzi. Trudno odtworzyć. Trudno przetestować. Tanie w prototypowaniu.
- **Przepływ.** Wykres sterowany zdarzeniami, którego jesteś właścicielem. `@start` zaznacza wpis. `@listen(topic)` oznacza krok, który jest uruchamiany, gdy inny krok wyemituje ten temat. Każdy krok to zwykły Python (można wewnętrznie wywołać załogę). Dobry do: produkcji. Zauważalny. Testowalne. Deterministyczny.

Zalecenia dotyczące produkcji na rok 2026 dokumentów: zacznij od Flow. Złóż ekipę podczas `Crew.kickoff()` wezwań z wewnątrz. Kroki przepływu, gdy autonomia zarabia. Flow zapewnia ścieżkę audytu, załoga umożliwia eksplorację. Komponuj, nie wybieraj.

### Integracja narzędzi

Trzy sposoby na wyposażenie Agenta w narzędzie. Wybierz najprostszy, który pasuje.

1. **`@tool` dekorator.** Czyste funkcje stają się narzędziami. Podpis jest schematem; docstring to opis, który widzi LLM. Najlepiej dla jednorazowych pomocników.

   ```python
   z narzędzia do importowania załogi.tools

   @tool("Przeszukaj internet")
   def szukaj (zapytanie: str) -> str:
       """Zwróć najlepsze wyniki dla zapytania."""
       zwróć run_search(zapytanie)
   ```

2. **`BaseTool` podklasa.** Narzędzie oparte na klasach z jawnym schematem argumentów, obsługą asynchronii, ponownymi próbami. Użyj, gdy narzędzie ma stan (klient, pamięć podręczna) lub potrzebuje argumentów strukturalnych.

```python
   z załogi.tools zaimportuj BaseTool
   z pydantycznego importu BaseModel

   klasa SearchArgs(Model bazowy):
       zapytanie: ul
       limit: int = 10

   klasa SearchTool(BaseTool):
       nazwa = "wyszukiwarka_web"
       opis = "Przeszukaj sieć i uzyskaj najlepsze wyniki."
       args_schema = SearchArgs

       def _run(self, zapytanie: str, limit: int = 10) -> str:
           zwróć self.client.search(zapytanie, limit=limit)
   ```

3. **Wbudowane zestawy narzędzi.** CrewAI dostarcza własne adaptery: `SerperDevTool`, `FileReadTool`, `DirectoryReadTool`, `CodeInterpreterTool`, `RagTool`, `WebsiteSearchTool`. Przewodowo z jednym importem.

Ustrukturyzowane wyjścia korzystają z Pydantic. Przekaż `output_pydantic=MyModel` zadanie. CrewAI sprawdza odpowiedź LLM pod kątem modelu i albo wymusza, albo ponawia próbę. Połącz to z ciasnym ciągiem `expected_output`. Dane wyjściowe w formacie dowolnego tekstu są odpowiednie w przypadku wersji roboczych; ustrukturyzowane wyniki są tym, co mogą wykorzystać przepływy niższego szczebla.

### Haki pamięci

CrewAI dostarcza cztery typy pamięci od razu po wyjęciu z pudełka. Tworzą: Załoga może włączyć wszystkie cztery na raz.

> **Zatwierdzono względem** CrewAI 0.86 (2026-05). Najnowsze wersje kierują wszystko przez ujednolicony system `Memory` obejmujący te cztery sklepy. Poniższy model koncepcyjny nadal obowiązuje, ale w nowszych wersjach powierzchnia klasy publicznej może zapaść się do jednego `Memory` punktu wejścia; sprawdź [dokumentację pamięci CrewAI] (https://docs.crewai.com/concepts/memory), aby sprawdzić bieżący interfejs API.

- **Krótkoterminowe.** Bufor rozmów w jednym przebiegu. Wycierane na koniec.
- **Długoterminowe.** Utrzymujące się w trakcie serii. Przechowywane w wektorowym DB (domyślnie Chroma, z możliwością wymiany). Pobrane przez podobieństwo do bieżącego zadania.
- **Podmiot.** Fakty dotyczące poszczególnych podmiotów. „Klient X korzysta z planu Enterprise”. Kluczowane według podmiotu, a nie podobieństwa. Przetrwa w biegach.
- **Kontekstowe.** Wyszukiwanie w czasie montażu. Pobiera odpowiednią pamięć w momencie, gdy Agent jej potrzebuje, a nie jest wstępnie ładowana.

Włącz w załodze za pomocą `memory=True` lub konfiguracji według typu. Obsługiwane przez skonfigurowanego przez Ciebie dostawcę osadzania (domyślnie jest to OpenAI, z możliwością zamiany na lokalny). Pamięć jest jednym z miejsc, w których CrewAI zarabia na życie w przypadku cieńszych frameworków; czysty LangGraph wymaga samodzielnego okablowania każdego z nich.

### Kiedy CrewAI pasuje

- Od trzech do sześciu agentów z nazwanymi rolami i przepływem pracy opartym na współpracy. Szkicowanie, recenzowanie, planowanie, burza mózgów.
- Trasa, w której ocena LLM dotycząca następnego kroku jest częścią wartości (hierarchiczna).
- Wszędzie tam, gdzie zespół jest bardziej zadowolony z czytania `role + goal + backstory` niż czytania definicji wykresu.

### Kiedy CrewAI nie pasuje

- Deterministyczne DAG ze ścisłym uporządkowaniem. Użyj LangGraph (lekcja 13). Kształt wykresu jest właściwą abstrakcją; Ustalanie ról w CrewAI polega na tarciu.
- Budżety opóźnień poniżej sekundy. Hierarchiczny dodaje podróże w obie strony. Nawet Sequential serializuje podpowiedzi zawierające historie i wcześniejsze wyniki.
- Pętle pojedynczego agenta. Pomiń ramy; pętla agenta (lekcja 1) plus rejestr narzędzi jest krótsza.

Lekcja 17 (Kompromisy w ramach agenta) przedstawia to w formie macierzy. Krótka wersja: CrewAI znajduje się w narożniku „współpracy opartej na rolach”.

### Kształt zależności

Niezależny od LangChain. Python 3.10 do 3.13. Używa `uv`. Liczba gwiazdek: zobacz [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) (migawka z dnia 2026–2005). Integracja z AWS Bedrock jest udokumentowana; testy porównawcze dostawców zgłaszają znaczne przyspieszenie w porównaniu z LangGraph w przypadku obciążeń związanych z kontrolą jakości, ale metodologia (zestaw danych, sprzęt, metryka oceny) nie jest publikowana, dlatego liczby dostawców platformy należy traktować wyłącznie kierunkowo.

### Gdzie ten wzorzec jest błędny

- **Szybkie rozwinięcie historii.** Historia zawierająca 2000 słów na agenta i pięcioosobowa załoga pochłania budżet kontekstowy przed pierwszym wywołaniem narzędzia. Trzymaj historie poniżej 200 słów. Wykorzystuj zwroty ponownie u agentów; nie powtarzaj stylu domu pięć razy.
- **Podatek od tokenów menedżera-LLM.** Proces hierarchiczny dodaje połączenie menedżera LLM przed każdym wezwaniem specjalisty. W przypadku załogi składającej się z pięciu zadań jest to sześć wezwań LLM zamiast pięciu, a wezwanie menedżera zawiera pełną listę zadań oraz wcześniejsze wyniki. Przełącz na tryb sekwencyjny, chyba że routing zależy od wyjścia.
- **Kruche połączenia.** Zadanie N `expected_output` to „konspekt”. Zadanie N+1 odczytuje to jako `context` i próbuje przeanalizować trzy sekcje. LLM wyprodukowało cztery. Ad-libs agenta niższego szczebla. Napraw za pomocą `output_pydantic` w Zadaniu N, aby Zadanie N+1 czytało obiekt wpisany, a nie dowolny tekst.
- **Załoga jako produkt.** Załoga w dowolnej formie wysyłana do produkcji bez opakowania Flow. Zmienność wyników jest wysoka; powtórka jest niemożliwa; dyżur nie jest w stanie rozróżnić złej passy od dobrej. Owiń z prądem.

## Zbuduj to

`code/main.py` implementuje standardowe wersje obu kształtów oraz załogę składającą się z trzech agentów.

Kształt:

- `Agent`, `Task` klasy danych pasujące do powierzchni CrewAI.
- `SequentialCrew.kickoff(inputs)` uruchamia zadania w kolejności deklaracji, łącząc dane wyjściowe jako `context`.
- `HierarchicalCrew.kickoff(topic)` dodaje menedżera Agenta, który w każdej rundzie wybiera kolejnego specjalistę, zatrzymuje się na „gotowe”.
- `Flow` z dekoratorami `@start` i `@listen(topic)`, małą pętlą zdarzeń i śladem.
- Dekorator `tool(name)` odzwierciedlający kształt `@tool` CrewAI.
- `Memory` ze sklepami `short_term`, `long_term`, `entity`; wyśmiewane podobieństwo używa numpy.
- Próbne odpowiedzi LLM to zakodowane na stałe ciągi znaków z wyłączoną rolą i prefiksem wejściowym. Brak sieci. Deterministyczny.

Konkretne demo: badacz, pisarz, zespół redaktorów przygotowujący brief na temat „Inżynierii agentów 2026”. Badacz wyciąga (wyśmiewa) źródła. Szkice pisarza. Redaktor zaciska palce. Ta sama załoga przebiega przez przepływ, aby pokazać deterministyczny kształt.

Uruchom to:

```bash
python3 code/main.py
```

Śledzenie obejmuje: sekwencyjne przeplatanie wyników przez zespół `context`, zespół hierarchiczny z wyborem menedżera (badacz, autor, redaktor, a następnie „gotowe”), przebieg obejmujący te same trzy kroki z wyraźnie określonymi tematami (`researched`, `drafted`, `edited`), wywołania narzędzi kierowane przez `@tool` i pamięć długoterminowa, która przetrwała dwa uruchomienia.

Ślad załogi jest płynny; kierownik mógłby w zasadzie ponownie zamówić. Ślad przepływu jest naprawiony. Ten wybór jest lekcją.

## Użyj tego

- **CrewAI Flow** dla produkcji. Nawet jeśli Flow jest jednym krokiem wywołującym `Crew.kickoff()`. Przepływ wyznacza granicę audytu.
- **CrewAI Crew (sekwencyjna)** do jasnego porządkowania wspólnej pracy, zwłaszcza pierwszych wersji roboczych i pętli recenzyjnych.
- **Załoga CrewAI (hierarchiczna)**, gdy wyznaczanie trasy zależy od wyników i masz czterech lub więcej specjalistów.
- **LangGraph** (Lekcja 13) dla jawnych maszyn stanowych, trwałe CV, ścisłe uporządkowanie.
- **AutoGen v0.4** (Lekcja 14) dla współbieżności modelu aktora i izolacji błędów.
- **OpenAI Agents SDK** (Lekcja 16) dla produktów opartych na OpenAI z funkcjami przekazywania i poręczami.
- **Claude Agent SDK** (Lekcja 17) dla produktów Claude-first z subagentami i sklepem sesyjnym.

## Wyślij to

`outputs/skill-crew-or-flow.md` wybiera dla zadania opcję Crew vs Flow i tworzy minimalną implementację. Zdecydowanie odrzuca w przypadku ekipy bez historii, przepływu bez wyraźnych tematów, hierarchii z mniej niż trzema specjalistami.

## Pułapki

- **Historia jako smak.** Kształtuje wyniki. Przetestuj trzy warianty na agenta; rozbieżność jest faktem. Wybierz jedno i zamroź.
- **Pomijanie `expected_output`.** Bez kontraktu na zadanie dalsze zadania przejmują wszystko, co wyprodukowało LLM. Załoga biegnie; audyt kończy się niepowodzeniem.
- **Pamięć zawsze włączona.** Długoterminowy zapis przy każdym uruchomieniu. Vector DB rośnie. Odzyskiwanie staje się głośne. Zakres zapisuje do zadań, w których fakt jest trwały.
- **Zmiana monitu menedżera.** Monit menedżera hierarchicznego jest ukryty. Jeśli routing stanie się dziwny, przełącz go w tryb szczegółowy i przeczytaj.
- **Efekty uboczne narzędzi w załogach.** Załoga może przywołać narzędzie więcej razy, niż oczekiwano. WYŚLIJ, USUŃ, płatność należy do etapu przepływu, nigdy do narzędzia załogi.

## Ćwiczenia

1. Przekształć załogę sekwencyjną w przepływ. Policz punkty styku, w których spada zmienność. Zwróć uwagę, gdzie spadła czytelność.
2. Dodaj do załogi pamięć jednostek: fakty o kliencie pozostają niezmienne przez cały czas rozpoczęcia pracy. Sprawdź, czy pobieranie pobiera właściwy element.
3. Wdrożyć proces hierarchiczny, w którym menedżer odmawia skierowania tekstu do redaktora, dopóki tekst autora nie będzie zawierał co najmniej trzech akapitów. Śledź ponowną próbę.
4. Podłącz podklasę `BaseTool` do (wyśmiewanej) wyszukiwarki internetowej. Porównaj kształt śledzenia z wersją dekoratora `@tool`.
5. Dodaj `output_pydantic=Brief` do zadania edytora, gdzie `Brief` ma `title`, `summary`, `sections`. Spraw, aby dane wyjściowe zadania piszącego były raz zniekształcone w formacie JSON; sprawdź zachowanie CrewAI podczas ponownych prób w śladzie.
6. Przeczytaj wstęp do dokumentacji CrewAI. Przenieś zabawkę do prawdziwego API `crewai`. Jakie gwarancje pominęła wersja stdlib?
7. Podłącz AgentOps lub Langfuse (lekcja 24) do prawdziwego działania. Które ślady przeoczyłeś w wersji stdlib?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Agent | „Osoba” | Rola + cel + historia + narzędzia |
| Zadanie | „Jednostka pracy” | Opis + oczekiwany wynik + osoba przypisana + opcjonalny wynik strukturalny |
| Załoga | „Zespół agenta” | Kontener dla Agentów + Zadania + Proces |
| Proces | „Strategia wykonania” | Sekwencyjny / Hierarchiczny / Konsensus (planowany) |
| Przepływ | „Deterministyczny przepływ pracy” | Sterowany zdarzeniami, własnością kodu, testowalny |
| Historia | „Podpowiedź dotycząca osoby” | Kształtownik tonu i oceny Agenta |
| `@tool` | „Narzędzie funkcyjne” | Dekorator zamieniający funkcję w narzędzie, które Agent może wywołać |
| `BaseTool` | „Narzędzie klasowe” | Narzędzie oparte na klasach ze schematem argumentów, ponownymi próbami, obsługą asynchronii |
| Pamięć bytu | „Fakty dotyczące poszczególnych jednostek” | Pamięć ograniczona do klienta / konta / problemu |
| Pamięć długoterminowa | „Pamięć krzyżowa” | Pamięć oparta na wektorach, która przetrwa pomiędzy startami |
| Pamięć kontekstowa | „Odbiór na czas” | Pamięć została wyciągnięta w momencie, gdy Agent jej potrzebuje |
| Menedżer LLM | „Agent routera” | Dodatkowy LLM w procesie hierarchicznym, który wybiera następne zadanie |
| `expected_output` | „Umowa zadaniowa” | Ciąg, który mówi agentowi (i audytowi), jaki kształt ma zwrócić |

## Dalsze czytanie

- [Wprowadzenie do dokumentacji CrewAI](https://docs.crewai.com/en/introduction): koncepcje i zalecana ścieżka produkcji
– [Przewodnik po przepływach CrewAI](https://docs.crewai.com/en/concepts/flows): kształt sterowany zdarzeniami, `@start`, `@listen`
- [Informacje o narzędziach CrewAI](https://docs.crewai.com/en/concepts/tools): `@tool`, `BaseTool`, wbudowane zestawy narzędzi
- [Pamięć CrewAI](https://docs.crewai.com/en/concepts/memory): krótkoterminowa, długoterminowa, jednostkowa, kontekstowa
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-efektywne-agents): kiedy wieloagent pomaga, a kiedy nie
- [Omówienie LangGraph](https://docs.langchain.com/oss/python/langgraph/overview): alternatywa dla maszyny stanowej