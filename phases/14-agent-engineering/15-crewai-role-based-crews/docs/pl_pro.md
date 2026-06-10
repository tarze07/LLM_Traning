# CrewAI: Załogi i przepływy pracy opartych na rolach

> CrewAI to popularna platforma wieloagentowa oparta na rolach na rok 2026. Składa się z czterech fundamentów: Agent (Agent), Zadanie (Task), Załoga (Crew) oraz Proces (Process). Oferuje dwa główne podejścia orkiestracji: Załogi (autonomiczna współpraca oparta na rolach) oraz Przepływy (Flows - deterministyczne, sterowane zdarzeniami). Oficjalna dokumentacja wskazuje wprost: „w przypadku aplikacji produkcyjnych zawsze zaczynaj od przepływu (Flow)”.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 12 (Wzorce przepływu pracy), Faza 14 · 14 (Model aktora)
**Czas:** ~75 minut

## Cele nauczania

- Wymień cztery podstawowe komponenty CrewAI (Agent, Zadanie, Załoga, Proces) i opisz ich parametry.
- Rozróżnij proces sekwencyjny, hierarchiczny oraz konsensusowy i dobierz odpowiedni do charakterystyki zadania.
- Wyjaśnij różnice pomiędzy załogami (autonomiczne działanie oparte na rolach) a przepływami (deterministyczne, sterowane zdarzeniami) oraz powody rekomendacji produkcyjnych zawartych w dokumentacji.
- Twórz narzędzia (tools) za pomocą dekoratora `@tool` oraz klasy dziedziczącej po `BaseTool` i opisz korzyści płynące ze stosowania ustrukturyzowanych danych wyjściowych (structured outputs) w porównaniu z wolnym tekstem.
- Wymień cztery rodzaje pamięci w CrewAI i określ scenariusze, w których warto je zastosować.
- Zaimplementuj standardową załogę (Crew) złożoną z trzech agentów (badacz, pisarz, redaktor) w celu wygenerowania podsumowania (briefu).
- Zidentyfikuj trzy typowe problemy i antywzorce w CrewAI: nadmierny rozmiar promptów (context bloat), dodatkowy koszt orkiestracji menedżera (manager LLM tax) oraz niestabilne przekazywanie zadań pomiędzy agentami.

## Problem

Zespoły wdrażające systemy wieloagentowe szybko napotykają te same ograniczenia. Koncepcja „autonomicznej współpracy” wygląda imponująco w prezentacjach demo. W praktyce jednak, gdy klient zgłasza błąd, potrzebna jest możliwość deterministycznego odtworzenia ścieżki. Z kolei dział finansowy pyta o koszt pojedynczego uruchomienia załogi sterowanej przez LLM, a programista na dyżurze musi wiedzieć, który agent i dlaczego zablokował się o 3 rano.

W pełni autonomiczne załogi nie dają łatwych odpowiedzi na te pytania. Z kolei sztywne grafy (DAG) gwarantują kontrolę, ale eliminują elastyczność i potencjał kreatywny potrzebny na przykład podczas burzy mózgów.

CrewAI rozwiązuje ten dylemat poprzez wprowadzenie dwóch podejść. Załogi (Crews) są przeznaczone do swobodnej współpracy i zadań badawczych opartych na rolach. Przepływy (Flows) służą do budowania stabilnych wdrożeń produkcyjnych sterowanych zdarzeniami, w pełni kontrolowanych w kodzie i łatwych do audytowania. To ten sam framework oferujący dwie różne formuły orkiestracji – wybór zależy od konkretnego zastosowania.

## Koncepcja

### Cztery elementy podstawowe

Interfejs CrewAI jest stosunkowo prosty. Wystarczy opanować cztery kluczowe pojęcia, a reszta to konfiguracja:

- **Agent.** Parametry: `role` (rola), `goal` (cel), `backstory` (historia / kontekst), `tools` (narzędzia) oraz opcjonalnie `llm`. Definicja historii (`backstory`) ma kluczowe znaczenie – kształtuje ona styl wypowiedzi, sposób podejmowania decyzji oraz kryteria zakończenia pracy. Narzędzia to funkcje, które agent może wywoływać.
- **Zadanie (Task).** Parametry: `description` (opis), `expected_output` (oczekiwany wynik), `agent` (przypisany agent) oraz opcjonalnie `context` (lista zadań nadrzędnych, których wyniki zostaną przekazane) i `output_pydantic` (wymuszenie ustrukturyzowanego formatu danych wyjściowych). Zadanie to podstawowa jednostka pracy. Pole `expected_output` stanowi kontrakt wykonawczy.
- **Załoga (Crew).** Główny kontener. Grupuje listę agentów (`agents`), zadań (`tasks`), definiuje proces (`process`) oraz opcjonalnie ustawienia pamięci (`memory`), szczegółowości logów (`verbose`) czy modelu menedżera (`manager_llm`).
- **Proces (Process).** Strategia wykonania zadań. Może być sekwencyjna (Sequential), hierarchiczna (Hierarchical) lub konsensusowa (Consensus - w planach). Określa sposób przepływu pracy.

Agenci nie komunikują się ze sobą bezpośrednio – są przypisani do poszczególnych zadań. Załoga ustala kolejność zadań, a proces decyduje o sposobie ich przydzielania i wykonywania. To kompletny model koncepcyjny działania systemu.

> **Zatwierdzono względem** CrewAI 0.86 (2026-05). Nowsze wersje mogą zmieniać nazwy lub łączyć typy procesów; sprawdź [dokumentację procesów CrewAI](https://docs.crewai.com/concepts/processes), zanim zaczniesz polegać na konkretnym kształcie.

### Sekwencyjne, hierarchiczne i konsensusowe wykonanie

- **Sekwencyjny (Sequential).** Zadania są uruchamiane jedno po drugim w kolejności ich definicji. Wynik zadania N jest automatycznie przekazywany jako kontekst (`context`) do zadania N+1. Jest to najtańsze i najbardziej przewidywalne rozwiązanie, zalecane, gdy przepływ pracy jest stały.
- **Hierarchiczny (Hierarchical).** Specjalny agent zarządzający (wymagający osobnego wywołania LLM) koordynuje pracę agentów wykonawczych. CrewAI automatycznie tworzy agenta menedżera na podstawie parametru `manager_llm`. Menedżer dynamicznie przydziela kolejne zadania, weryfikuje ich wyniki i może nakazać ich poprawę lub zmienić ścieżkę wykonania. Użyj tej strategii, gdy zespół liczy 4 lub więcej agentów, a kolejność kroków zależy bezpośrednio od cząstkowych rezultatów.
- **Konsensusowy (Consensus).** Rozwiązanie zapowiadane w planach rozwojowych, obecnie niedostępne w publicznym API. Nie należy na nim bazować w bieżących projektach.

Proces hierarchiczny generuje dodatkowe zapytanie do LLM (menedżera) przy każdym kroku agenta wykonawczego. Koszt tokenów przy pięcioetapowym zadaniu może wzrosnąć nawet trzykrotnie. Stosuj to rozwiązanie tylko wtedy, gdy dynamiczny routing jest naprawdę wymagany.

### Załogi kontra przepływy

To podział architektoniczny, według którego inżynierowie projektują systemy:

- **Załoga (Crew).** Pełna autonomia sterowana przez LLM. Framework decyduje o ścieżce wykonania w czasie rzeczywistym. Doskonale sprawdza się w zadaniach badawczych, burzach mózgów, generowaniu pierwszych wersji szkiców oraz wszędzie tam, gdzie sam proces dochodzenia do wyniku ma charakter otwarty. Jest jednak trudna w testowaniu i odtwarzaniu błędów, choć tania w fazie szybkiego prototypowania.
- **Przepływ (Flow).** Graf sterowany zdarzeniami, którego strukturę w pełni kontrolujesz w kodzie. Dekorator `@start` definiuje punkt wejścia, a `@listen(topic)` oznacza metodę uruchamianą w odpowiedzi na określone zdarzenie (wyemitowany temat). Każdy krok to standardowa funkcja w Pythonie (wewnątrz której można wywołać uruchomienie załogi). Jest to rozwiązanie rekomendowane na produkcję: w pełni przewidywalne, łatwe w testowaniu i obserwowalności.

Rekomendacja produkcyjna: zacznij projekt od zdefiniowania przepływu (Flow). Załogi wywołuj wewnątrz poszczególnych kroków za pomocą `Crew.kickoff()`. Wprowadzaj autonomiczne załogi tylko tam, gdzie elastyczność LLM przynosi realne korzyści. Przepływ (Flow) gwarantuje przejrzystą ścieżkę audytu, podczas gdy załoga (Crew) umożliwia eksplorację problemu. Łącz obie te koncepcje zamiast wybierać tylko jedną.

### Integracja narzędzi

Trzy sposoby na wyposażenie Agenta w narzędzie. Wybierz najprostszy, który pasuje:

1. **Dekorator `@tool`.** Przekształca standardowe funkcje w narzędzia dla modeli. Sygnatura funkcji definiuje schemat parametrów, a docstring stanowi opis narzędzia interpretowany przez LLM. Idealne rozwiązanie dla prostych funkcji pomocniczych.

   ```python
   from crewai.tools import tool

   @tool("Przeszukaj internet")
   def search(query: str) -> str:
       """Zwróć najlepsze wyniki dla zapytania."""
       return run_search(query)
   ```

2. **Dziedziczenie po klasie `BaseTool`.** Umożliwia tworzenie narzędzi obiektowych z jawnym schematem argumentów (Pydantic), obsługą asynchroniczności oraz logiką ponawiania prób. Stosowane, gdy narzędzie przechowuje stan (np. klient bazy danych, pamięć podręczna) lub wymaga złożonych parametrów strukturalnych.

   ```python
   from crewai.tools import BaseTool
   from pydantic import BaseModel

   class SearchArgs(BaseModel):
       query: str
       limit: int = 10

   class SearchTool(BaseTool):
       name: str = "wyszukiwarka_web"
       description: str = "Przeszukaj sieć i uzyskaj najlepsze wyniki."
       args_schema: type[BaseModel] = SearchArgs

       def _run(self, query: str, limit: int = 10) -> str:
           return self.client.search(query, limit=limit)
   ```

3. **Wbudowane zestawy narzędzi.** CrewAI oferuje gotowe adaptery, takie jak `SerperDevTool`, `FileReadTool`, `DirectoryReadTool`, `CodeInterpreterTool`, `RagTool` czy `WebsiteSearchTool`, które można zaimportować i natychmiast wdrożyć.

Wymuszanie ustrukturyzowanego formatu danych (Structured Outputs). Zdefiniuj parametr `output_pydantic=MyModel` w zadaniu. CrewAI automatycznie zweryfikuje odpowiedź LLM pod kątem zgodności ze schematem Pydantic i w razie niezgodności podejmie próbę poprawy. Połącz to z precyzyjnym opisem w `expected_output`. Tekst o dowolnej strukturze sprawdza się w przypadku wersji roboczych; dane ustrukturyzowane są niezbędne do przekazania wyników do kolejnych etapów systemu.

### Integracja z systemami pamięci

CrewAI oferuje cztery rodzaje pamięci, które mogą działać równolegle w ramach jednej załogi.

> **Uwaga:** Wersja 0.86 (maj 2026 r.) integruje te funkcje w ramach jednolitego modułu `Memory`. Poniższy podział koncepcyjny pozostaje aktualny, jednak szczegóły implementacyjne API mogą się różnić w zależności od wersji – przed wdrożeniem sprawdź aktualną dokumentację pamięci CrewAI.

- **Krótkoterminowa (Short-term memory).** Lokalny bufor konwersacji czyszczony po zakończeniu uruchomienia.
- **Długoterminowa (Long-term memory).** Pamięć persystentna utrzymywana pomiędzy różnymi uruchomieniami. Przechowywana w bazie wektorowej (domyślnie Chroma) i przeszukiwana semantycznie pod kątem bieżącego zadania.
- **Pamięć jednostek (Entity memory).** Przechowywanie konkretnych faktów o podmiotach (np. „Klient X korzysta z planu Enterprise”). Dane są indeksowane bezpośrednio identyfikatorem jednostki, a nie podobieństwem semantycznym, i są zachowywane pomiędzy uruchomieniami.
- **Kontekstowa (Contextual memory).** Dynamiczne wyszukiwanie informacji z historii w momencie, gdy agent wykonuje dane zadanie, zamiast statycznego ładowania danych na początku.

Pamięć włącza się w konfiguracji załogi poprzez parametr `memory=True` lub szczegółowe ustawienia. Funkcja ta wykorzystuje zdefiniowany model osadzeń (domyślnie OpenAI). Obsługa pamięci to jedna z największych zalet CrewAI w porównaniu do uboższych frameworków, takich jak czysty LangGraph, gdzie każdy rodzaj pamięci należy wdrażać i łączyć samodzielnie.

### Kiedy warto stosować CrewAI

- Zespoły składające się z 3-6 agentów o wyraźnie zdefiniowanych rolach wykonujące zadania wymagające ścisłej współpracy (np. research, pisanie tekstów, recenzowanie).
- Procesy, w których dynamiczny routing i ocena postępów przez LLM stanowią kluczową wartość systemu (strategia hierarchiczna).
- Scenariusze, w których dla zespołu czytelniejsza i wygodniejsza jest praca z opisami typu `role + goal + backstory` niż bezpośrednia analiza grafów sterowania w kodzie.

### Kiedy unikać CrewAI

- Deterministyczne przepływy pracy (DAG) o sztywnej strukturze. W takich przypadkach znacznie lepszą abstrakcją jest graf stanowy w LangGraph (Lekcja 13), podczas jak próba wymuszenia tego za pomocą ról w CrewAI generuje niepotrzebny narzut.
- Wymagania dotyczące niskich opóźnień (poniżej sekundy). Strategia hierarchiczna generuje dodatkowe wywołania modeli, a nawet proces sekwencyjny wymaga czasu na sformatowanie i przesłanie pełnych profili agentów oraz wyników poprzednich zadań.
- Proste pętle z udziałem jednego agenta. W takich przypadkach stosowanie frameworka to nadmiarowość; znacznie prostsza jest klasyczna pętla agentowa (Lekcja 01) z rejestrem narzędzi.

Lekcja 17 (Kompromisy w ramach agenta) przedstawia to w formie macierzy porównawczej. Podsumowując: CrewAI idealnie pokrywa scenariusze zaklasyfikowane jako „współpraca oparta na rolach”.

### Wymogi i ekosystem

Kod jest niezależny od LangChain, wspiera Python 3.10-3.13 i korzysta z menedżera pakietów `uv`. Wdrożenia z AWS Bedrock są w pełni wspierane. Testy benchmarkowe producenta wskazują na wyższą wydajność w zadaniach QA w porównaniu do LangGraph, jednak ze względu na brak szczegółowych publikacji metodologii testowej (zbiory danych, parametry sprzętowe), wyniki te należy traktować wyłącznie orientacyjnie.

### Potencjalne problemy i wady wzorca

- **Nadmierny rozmiar profili (Context bloat).** Długie opisy (`backstory`) rzędu 2000 słów na agenta przy pięcioosobowej załodze potrafią wyczerpać okno kontekstowe modelu jeszcze przed wywołaniem pierwszego narzędzia. Staraj się utrzymywać opisy poniżej 200 słów i unikać powtarzania tych samych reguł u różnych agentów.
- **Dodatkowy koszt orkiestracji (Manager LLM tax).** Proces hierarchiczny wykonuje zapytanie do menedżera przed każdym uruchomieniem specjalisty. Przy pięciu zadaniach generuje to sześć zapytań LLM zamiast pięciu, a zapytanie menedżera zawiera pełny kontekst zadań i dotychczasowych rezultatów. Jeśli routing nie zależy bezpośrednio od wyników, stosuj proces sekwencyjny.
- **Niestabilne przekazywanie wyników.** Jeśli zadanie N zwraca nieustrukturyzowany tekst jako „konspekt”, a zadanie N+1 próbuje go sparsować i wyodrębnić sekcje, każda drobna zmiana w strukturze tekstu wygenerowanego przez LLM może uszkodzić kolejny krok. Należy wymusić ustrukturyzowany model wyjściowy za pomocą `output_pydantic` w zadaniu N, tak aby zadanie N+1 operowało na typowanym obiekcie.
- **Wdrażanie autonomicznej załogi bezpośrednio na produkcję.** Zmienność zachowania LLM na produkcji jest wysoka, a brak deterministycznej kontroli uniemożliwia stabilne utrzymanie systemu. Zawsze pakuj logikę załogi w przepływy pracy (Flows).

## Zbuduj to

Plik `code/main.py` implementuje uproszczone wersje obu modeli orkiestracji oraz załogę składającą się z trzech agentów.

Struktura kodu:

- Klasy danych `Agent` i `Task` odpowiadające strukturze API CrewAI.
- Metodę `SequentialCrew.kickoff(inputs)` uruchamiającą zadania sekwencyjnie i przekazującą ich wyniki jako kontekst.
- Metodę `HierarchicalCrew.kickoff(topic)` wprowadzającą agenta zarządzającego (menedżera), który decyduje o kolejności uruchamiania specjalistów aż do osiągnięcia celu.
- Klasę `Flow` z dekoratorami `@start` i `@listen(topic)`, prostą pętlą zdarzeń oraz logowaniem ścieżki.
- Dekorator `tool(name)` odzwierciedlający działanie `@tool` w CrewAI.
- Moduł `Memory` z obsługą pamięci krótkoterminowej, długoterminowej i jednostek (z mockowanym wyszukiwaniem semantycznym).
- Mockowane odpowiedzi LLM zaimplementowane jako statyczne teksty uwzględniające rolę agenta i parametry wejściowe, co gwarantuje pełny determinizm bez połączeń sieciowych.

Przykładowy scenariusz: zespół złożony z badacza, pisarza i redaktora przygotowuje raport na temat „Agent Engineering 2026”. Badacz wyszukuje źródła (mock), pisarz tworzy wersję roboczą, a redaktor ją weryfikuje i poprawia. Ten sam proces jest realizowany w strukturze przepływu (Flow), pokazując różnice w stabilności działania.

Uruchomienie:

```bash
python3 code/main.py
```

Logi (trace) obejmują: sekwencyjne przekazywanie wyników jako kontekstu, proces hierarchiczny z decyzjami menedżera (badacz -> pisarz -> redaktor -> zakończenie), wykonanie przepływu z jawnymi zdarzeniami (`researched`, `drafted`, `edited`), wywołania narzędzi `@tool` oraz odczyt z pamięci długoterminowej pomiędzy uruchomieniami.

Logi załogi wykazują elastyczność – menedżer może dynamicznie zmieniać kolejność zadań. Logi przepływu (Flow) mają stałą strukturę. Zrozumienie tego wyboru to kluczowy element lekcji.

## Użyj tego

- Stosuj **CrewAI Flows** w środowiskach produkcyjnych. Nawet jeśli przepływ składa się z jednego kroku wywołującego `Crew.kickoff()`, struktura Flow wyznacza czytelną granicę audytowalności systemu.
- Stosuj **CrewAI Crews** ze strategią sekwencyjną do organizacji ustrukturyzowanej współpracy agentów (np. pisanie pierwszych wersji szkiców, pętle recenzenckie).
- Stosuj **CrewAI Crews** ze strategią hierarchiczną wyłącznie wtedy, gdy routing zadań zależy dynamicznie od cząstkowych rezultatów i zespół liczy co najmniej 4 agentów.
- **LangGraph** (Lekcja 13) do jawnych maszyn stanowych, trwałego wznawiania działania i ścisłego porządkowania.
- **AutoGen v0.4** (Lekcja 14) dla współbieżności modelu aktora i izolacji błędów.
- **OpenAI Agents SDK** (Lekcja 16) dla produktów opartych na modelach OpenAI z wbudowanym routingiem i guardrails.
- **Claude Agent SDK** (Lekcja 17) dla produktów opartych na modelach Anthropic z subagentami i sesyjnym stanem.

## Wyślij to

Plik `outputs/skill-crew-or-flow.md` ułatwia dobór właściwego wariantu (Crew vs Flow) dla danego zadania i generuje jego minimalną implementację. Odrzuca projekty załóg bez określonej historii (backstory), przepływy bez jawnych zdarzeń/tematów oraz procesy hierarchiczne z mniej niż trzema specjalistami.

## Pułapki wdrożeniowe

- **Opisy agentów (`backstory`).** Profil agenta bezpośrednio wpływa na generowane wyniki. Przetestuj różne warianty i zamroź ostateczną, najbardziej stabilną wersję w kodzie.
- **Pomijanie pola `expected_output`.** Bez zdefiniowanego kontraktu kolejne zadania będą próbowały przetwarzać nieprzewidywalną treść wygenerowaną przez model, co nieuchronnie prowadzi do błędów integracji.
- **Bezkrytyczne włączanie pamięci.** Zapisywanie wszystkich danych z każdego uruchomienia powoduje szybki wzrost bazy wektorowej i wprowadza szum informacyjny przy wyszukiwaniu. Ograniczaj zapis do pamięci długoterminowej wyłącznie do kluczowych faktów.
- **Modyfikacje promptu menedżera.** Prompt systemowy menedżera w procesie hierarchicznym jest ukryty pod maską. Jeśli routing zaczyna działać niepoprawnie, włącz tryb szczegółowy (`verbose=True`) i przeanalizuj logi wywołań.
- **Efekty uboczne w narzędziach agentów.** Autonomiczny agent może wywołać to samo narzędzie wielokrotnie lub w nieprzewidywalny sposób. Operacje krytyczne (takie jak wysyłka maili, usuwanie zasobów, transakcje płatnicze) powinny być realizowane wyłącznie na poziomie kodu przepływu (Flow), a nie bezpośrednio w narzędziach wywoływanych przez agentów załogi.

## Ćwiczenia

1. Przepisz proces sekwencyjny na strukturę przepływu (Flow). Przeanalizuj punkty, w których redukowana jest zmienność wyników oraz wpływ tej zmiany na czytelność kodu.
2. Zaimplementuj pamięć jednostek (entity memory) w załodze: zapisz stałe fakty o kliencie i zweryfikuj, czy mechanizm pamięci poprawnie je pobiera i udostępnia agentom przy kolejnych wywołaniach.
3. Zaimplementuj proces hierarchiczny, w którym agent menedżer odrzuca wersję pisarza i nakazuje jej poprawę, dopóki wygenerowany tekst nie będzie składał się z co najmniej trzech akapitów. Przeanalizuj ścieżkę logów dla takiej sytuacji.
4. Zaimplementuj narzędzie wyszukiwania dziedziczące po klasie `BaseTool`. Porównaj logi wywołań z wariantem opartym na dekoratorze `@tool`.
5. Zdefiniuj parametry `output_pydantic=Brief` (z polami `title`, `summary`, `sections`) w zadaniu redaktora. Zasymuluj uszkodzony format JSON na wyjściu pisarza i zaobserwuj, jak CrewAI radzi sobie z automatyczną próbą poprawy błędnej struktury.
6. Zapoznaj się z wstępem do dokumentacji CrewAI. Przepisz uproszczoną implementację stdlib z użyciem rzeczywistej biblioteki `crewai`. Przeanalizuj, jakie produkcyjne zabezpieczenia zostały pominięte w wersji uproszczonej.
7. Zintegruj system śledzenia (np. AgentOps lub Langfuse - Lekcja 24) z rzeczywistym uruchomieniem załogi. Porównaj głębokość uzyskiwanych logów.

## Kluczowe terminy

| Termin | Co mówią ludzie | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Agent | „Osoba” | Rola + cel + historia + narzędzia |
| Zadanie (Task) | „Jednostka pracy” | Opis + expected_output (oczekiwany wynik) + osoba przypisana + opcjonalny wynik strukturalny |
| Załoga (Crew) | „Zespół agentów” | Kontener grupujący agentów, zadania oraz proces |
| Proces (Process) | „Strategia wykonania” | Strategia sekwencyjna (Sequential) / hierarchiczna (Hierarchical) / konsensusowa (w planach) |
| Przepływ (Flow) | „Deterministyczny przepływ pracy” | Sterowana zdarzeniami, zdefiniowana w kodzie i w pełni testowalna struktura orkiestracji |
| Historia (Backstory) | „Prompt profilujący” | Definicja kontekstu i cech osobowości agenta kształtująca styl i kryteria decyzyjne |
| `@tool` | „Narzędzie funkcyjne” | Dekorator przekształcający standardową funkcję w narzędzie wywoływane przez agenta |
| `BaseTool` | „Narzędzie obiektowe” | Klasa bazowa do tworzenia zaawansowanych narzędzi ze schematem Pydantic i obsługą błędów |
| Pamięć jednostek | „Dane podmiotu” | Baza faktów przypisana do konkretnej encji (np. klienta), zachowywana pomiędzy uruchomieniami |
| Pamięć długoterminowa | „Pamięć semantyczna” | Baza wektorowa pozwalająca zachować i wyszukiwać kluczowe fakty pomiędzy różnymi uruchomieniami |
| Pamięć kontekstowa | „Dynamiczne pobieranie” | Automatyczne wyszukiwanie i dołączanie informacji z historii w momencie wykonywania zadania |
| Menedżer LLM | „Agent routera” | Dodatkowy model orkiestrujący w procesie hierarchicznym, rozdzielający zadania specjalistom |
| `expected_output` | „Kontrakt zadania” | Ciąg tekstowy definiujący dokładną strukturę i kształt danych wyjściowych z zadania |

## Dalsze czytanie

- [Wprowadzenie do dokumentacji CrewAI](https://docs.crewai.com/en/introduction) — oficjalne koncepcje i wytyczne produkcyjne
- [Przewodnik po przepływach CrewAI](https://docs.crewai.com/en/concepts/flows) — model sterowania zdarzeniami z dekoratorami `@start` i `@listen`
- [Integracja narzędzi w CrewAI](https://docs.crewai.com/en/concepts/tools) — szczegółowy opis `@tool`, `BaseTool` oraz biblioteki gotowych narzędzi
- [Zarządzanie pamięcią w CrewAI](https://docs.crewai.com/en/concepts/memory) — konfiguracja pamięci krótko- i długoterminowej oraz jednostek
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — analiza, kiedy stosować orkiestrację wieloagentową, a kiedy prostsze systemy
- [Dokumentacja LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) — grafowa alternatywa dla maszyn stanowych
