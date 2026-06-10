# Współdzielona pamięć i wzorce Blackboard

> W systemach wieloagentowych (stan na rok 2026) współistnieją dwa główne podejścia: **pula wiadomości** (message pool, gdzie każdy agent widzi wypowiedzi wszystkich pozostałych, jak w AutoGen GroupChat czy MetaGPT) oraz **tablica ogłoszeniowa z subskrypcją** (blackboard, gdzie agenci subskrybują wybrane zdarzenia lub tematy, jak w Context-Aware MCP lub frameworku Matrix). Oba rozwiązania stanowią jedyny stanowy element systemu wieloagentowego, co oznacza, że oba są podatne na specyficzne błędy. Klasycznym antywzorcem awarii jest **zatrucie pamięci (memory poisoning)**: jeden z agentów generuje błędne informacje (halucynuje „fakt”), a pozostali agenci traktują je jako zweryfikowane dane wejściowe. Powoduje to stopniowy spadek dokładności całego systemu, co jest znacznie trudniejsze do wykrycia i naprawienia niż nagła awaria (crash). W tej lekcji zaimplementujemy obie struktury z użyciem biblioteki standardowej Pythona, przeanalizujemy scenariusz zatrucia pamięci i przedstawimy trzy sprawdzone w środowisku produkcyjnym metody przeciwdziałania temu zjawisku.

**Typ:** Ucz się + Buduj
**Języki:** Python (biblioteka standardowa, `threading`)
**Wymagania wstępne:** Faza 16 · 04 (model prymitywny), Faza 16 · 09 (Równoległe sieci roju)
**Czas:** ~75 minut

## Problem

Systemy wieloagentowe potrzebują wspólnego obszaru do wymiany faktów. Najprostszą (dosłowną) opcją jest przekazywanie całej historii w każdej wiadomości — wiąże się to jednak z ciągłym kopiowaniem danych. Alternatywą jest udostępnienie globalnego dziennika zdarzeń (global log) — ten jednak rośnie bez ograniczeń i jest podatny na zatrucie pamięci. Trzecie podejście to projektowanie dedykowanych widoków dla każdego agenta (role-specific projections) — rozwiązanie skalowalne, ale wymagające wcześniejszego zdefiniowania schematów danych.

Gdy jeden z agentów halucynuje i zapisuje błędną informację we wspólnym stanie, każdy kolejny agent odczytujący ten stan przyjmuje tę halucynację jako niezaprzeczalny fakt. Zanim operator (człowiek) zorientuje się w sytuacji, łańcuch wnioskowania ma już za sobą kilka etapów, a jego pierwotną przyczyną okazuje się jedna z pierwszych wygenerowanych wiadomości. Debugowanie takiego spadku dokładności w systemie wieloagentowym jest znacznie trudniejsze niż diagnozowanie typowych awarii kodu.

To zjawisko to zatrucie pamięci (memory poisoning). Jest to druga najczęściej dokumentowana kategoria błędów w taksonomii MAST (Cemri et al., arXiv:2503.13657). Wynika ona bezpośrednio z architektury systemu: każdy projekt pamięci współdzielonej pozbawiony śledzenia pochodzenia (provenance) oraz niezależnego weryfikatora prędzej czy później ulegnie zatruciu.

## Koncepcja

### Dwie główne topologie

**Pełna pula wiadomości (Full message pool).** Każdy agent odczytuje każdą wiadomość. Model ten stosują AutoGen GroupChat i MetaGPT. Jest prosty i czytelny dla celów audytu, ale nie skaluje się powyżej około 10 agentów, ponieważ kontekst każdego z nich zostaje przepełniony działaniami pozostałych uczestników.

```
agent-A ──zapis──▶ ┌────────────────┐ ◀──odczyt── agent-D
                    │ message pool   │
agent-B ──zapis──▶ │                │ ◀──odczyt── agent-E
                    │ (global log)   │
agent-C ──zapis──▶ └────────────────┘ ◀──odczyt── agent-F
```

**Tablica ogłoszeniowa z subskrypcją (Blackboard).** Agenci deklarują zainteresowanie konkretnymi tematami (topics), a system przesyła do nich wyłącznie powiązane wiadomości. Model ten wykorzystują CA-MCP (arXiv:2601.11595) oraz zdecentralizowany framework Matrix (arXiv:2511.21686). Pozwala na znacznie lepsze skalowanie, ale wymaga wcześniejszego zaprojektowania schematu tematów.

```
                    ┌─ temat: ceny ────┐
agent-A ──pub────▶ │                  │ ──▶ agent-D (subskrybent)
                    ├─ temat: zamówienia┤
agent-B ──pub────▶ │                  │ ──▶ agent-E (subskrybent)
                    ├─ temat: alerty ──┤
agent-C ──pub────▶ │                  │ ──▶ agent-F (subskrybent)
                    └──────────────────┘
```

### Kiedy stosować dany model

- **Pełna pula (Full Pool)** sprawdza się przy niewielkiej liczbie agentów (< 10), gdy są oni zróżnicowani (niejednorodni), a interakcja jest krótkotrwała. Wnioskowanie o tym, kto i co napisał, jest proste, ponieważ cała historia jest dostępna dla każdego.
- **Tablica (Blackboard)** sprawdza się przy dużej liczbie agentów (np. roje agentów o podobnych rolach) i długotrwałych zadaniach. Filtrowanie komunikatów (routing) pozwala zredukować zużycie tokenów oraz zanieczyszczenie kontekstu (context pollution).

Systemy produkcyjne często łączą obie topologie: na poziomie strategicznym (warstwa planowania) stosuje się małą, pełną pulę wiadomości, a na poziomie wykonawczym (warstwa wykonawców/workers) — tablicę ogłoszeń.

### Scenariusz zatrucia pamięci

Trzej agenci współpracują przy zadaniu badawczym. Agent A odpowiada za wyszukiwanie informacji (retrieval), Agent B za ich streszczanie (summarization), a Agent C jest analitykiem.

1. Agent A pobiera dokument i zapisuje we wspólnym stanie informację: „Badanie wykazało poprawę dokładności o 42%”.
2. W rzeczywistości pobrana strona zawierała wartość „4,2%”. Nastąpił błąd odczytu części dziesiętnej (halucynacja).
3. Agent B, czytając wspólny stan, generuje streszczenie: „Zgłoszono znaczący wzrost dokładności o 42% (źródło: Agent A)”.
4. Agent C, bazując na tym wpisie, wnioskuje: „Rekomenduję wdrożenie — wzrost o 42% ma kluczowe znaczenie”.
5. Raport końcowy zawiera zmyślony fakt o 42% poprawie.

Żaden agent nie uległ awarii. Wszystkie testy syntaktyczne przeszły pomyślnie. System formalnie ukończył zadanie. Jednak halucynacja przedostała się z kontekstu jednego agenta do procesu wnioskowania pozostałych uczestników poprzez współdzielony stan.

### Dlaczego błąd ten wynika z samej architektury

Gdyby stan nie był współdzielony, błędna informacja Agenta A pozostałaby w jego lokalnym kontekście. Agenci wykonujący kolejne kroki mogliby samodzielnie pobrać źródło i zweryfikować dane. W przypadku naiwnego wdrożenia pamięci współdzielonej, kontekst jednego agenta staje się automatycznie kontekstem wszystkich, co natychmiastowo legitymizuje halucynację jako fakt.

Problem nie leży w samym współdzieleniu stanu, ale w jego udostępnianiu **bez kontroli pochodzenia (provenance) oraz bez niezależnej weryfikacji**. Sytuację tę rozwiązują trzy mechanizmy obronne:

1. **Jawne śledzenie pochodzenia (provenance).** Każdy zapis we wspólnym stanie rejestruje: autora wpisu, znacznik czasu, identyfikator promptu oraz cytowane źródła (np. adresy URL). Agenci odczytujący te dane oceniają ich wiarygodność na podstawie źródła.
2. **Zapisywanie wersji; tryb wyłącznie do zapisu (append-only).** Ewentualna korekta danych wprowadzana jest jako nowa wersja rekordu, a nie modyfikacja w miejscu (in-place update). Dzięki temu zachowywana jest pełna ścieżka audytu.
3. **Wprowadzenie agenta weryfikującego bez uprawnień do zapisu.** Dedykowany agent audytowy ma dostęp do pamięci wyłącznie w trybie do odczytu (read-only). Analizuje on wpisy, samodzielnie odpytuje oryginalne źródła danych i oznacza niespójności. Ponieważ nie ma uprawnień do modyfikacji wspólnego stanu, nie ulega zatruciu pamięci.

### Historyczne korzenie: Model Blackboard (Hayes-Roth, 1985)

Wzorzec tablicy (Blackboard) powstał na długo przed agentami LLM. Hayes-Roth (1985, „A Blackboard Architecture for Control”) opisała wyspecjalizowane źródła wiedzy (knowledge sources), które monitorują globalną tablicę, publikują cząstkowe rozwiązania i wyzwalają działanie innych modułów. Nowoczesne systemy (jak CA-MCP czy Matrix) stosują ten sam schemat, gdzie źródłami wiedzy są agenty LLM, a cząstkowymi rozwiązaniami — obiekty JSON. Klasyczna literatura informatyczna już dawno opisała problemy rywalizacji o zapis (write concurrency), kontroli oportunistycznej czy spójności, które twórcy współczesnych frameworków często odkrywają na nowo.

### Projekcja a pełny widok

Klasyczna tablica dostarcza każdemu subskrybentowi taką samą projekcję danych (w ramach danego tematu). Bardziej zaawansowane podejście to **projekcja dedykowana dla agenta (per-agent projection)**: każdy agent otrzymuje widok ściśle dostosowany do jego roli. Reduktory stanu (reducers) w LangGraph stanowią flagowy przykład takiego rozwiązania — funkcja redukująca filtruje i przekształca stan globalny w wycinek przeznaczony dla konkretnego agenta.

Dedykowane projekcje pozwalają na lepsze skalowanie systemu, ale wymagają zdefiniowania sztywnego schematu danych. Bez niego logika filtrowania musiałaby być tworzona doraźnie (ad hoc) w promptach poszczególnych agentów.

### Rywalizacja o zapis (Write concurrency)

Równoczesny zapis realizowany przez wielu agentów to klasyczny problem współbieżności. W praktyce stosuje się trzy wzorce:

- **Sekwencyjny zapis (Single Writer).** Wszystkie operacje zapisu są kolejkowane i realizowane przez jednego agenta koordynującego. Rozwiązanie proste, ale tworzy wąskie gardło.
- **Optymistyczna kontrola współbieżności (Optimistic Concurrency Control).** Każdy wpis posiada numer wersji. Próba zapisu z nieaktualną wersją kończy się niepowodzeniem i wymaga ponowienia operacji. Jest to klasyczna technika bazodanowa.
- **Partycjonowanie tematów (Topic partitioning).** Poszczególni agenci mają wyłączne uprawnienia do zapisu w określonych tematach. Eliminuje to konflikty zapisu, lecz wymaga precyzyjnego podziału domeny.

Większość współczesnych frameworków domyślnie wykorzystuje sekwencyjny zapis, ponieważ czas odpowiedzi LLM jest na tyle długi, że konflikty zapisu występują rzadko, a narzut związany z kolejkowaniem nie wpływa znacząco na ogólną wydajność.

### Niezależny weryfikator (Verifier)

Wdrożenie dedykowanego weryfikatora tylko do odczytu to wysoce zalecana praktyka. Zasady jego implementacji:

- Weryfikator odczytuje stan ze wspólnego obszaru (puli lub tablicy).
- Weryfikator nie posiada uprawnień do zapisu we wspólnej pamięci — raportuje wyniki wyłącznie do oddzielnego kanału audytowego.
- Weryfikator niezależnie pobiera i weryfikuje cytowane źródła danych, zgłaszając ewentualne rozbieżności.
- Wyniki analizy weryfikatora są przekazywane do operatora (human-in-the-loop) lub niezależnego agenta decyzyjnego; nigdy nie są zapisywane z powrotem we wspólnej pamięci.

Bez tej separacji raporty weryfikatora stawałyby się nowymi wpisami we wspólnej puli. W efekcie skażony stan pamięci mógłby zatruć proces wnioskowania samego weryfikatora, całkowicie pozbawiając go wiarygodności.

## Zbuduj to

Plik `code/main.py` implementuje obie topologie w standardowej bibliotece Pythona, a także symuluje scenariusz zatrucia pamięci oraz prezentuje trzy metody ochrony:

- `MessagePool` — bezpieczny wątkowo dziennik zdarzeń typu append-only (wyłącznie do zapisu) z pełnym odczytem.
- `Blackboard` — tablica typu pub/sub z podziałem tematycznym i subskrypcjami dla agentów.
- `ProvenanceEntry` — struktura przechowująca metadane każdego zapisu (autor, znacznik czasu, skrót promptu, źródłowy adres URI).
- `PoisoningScenario` — symulacja zadania badawczego realizowanego przez trzech agentów, w którym Agent A halucynuje część dziesiętną. Wypisuje raport końcowy.
- `Verifier` — agent weryfikujący z dostępem tylko do odczytu, który pobiera źródła i zgłasza rozbieżności. Uruchamia ten sam scenariusz z aktywnym audytem.

Uruchomienie:

```bash
python3 code/main.py
```

Oczekiwany wynik działania:
- Uruchomienie 1 (bez weryfikatora): zhalucynowana wartość 42% trafia do raportu końcowego.
- Uruchomienie 2 (z weryfikatorem): weryfikator wykrywa niespójność, pula zostaje oznaczona flagą ostrzegawczą, a raport końcowy zawiera sprostowanie.

## Zastosowanie

Plik `outputs/skill-memory-auditor.md` definiuje procedurę audytu pamięci współdzielonej w dowolnym systemie wieloagentowym pod kątem pochodzenia danych, wersjonowania oraz separacji procesów weryfikacji. Warto go stosować przed wdrożeniem produkcyjnym nowych architektur.

## Wdrożenie produkcyjne

Lista kontrolna dla systemów z pamięcią współdzieloną:

- Zapisuj pochodzenie danych (provenance) przy każdej operacji zapisu: `(writer, timestamp, prompt_hash, tool_calls_cited, source_uri)`.
- Skonfiguruj pamięć w trybie append-only (wyłącznie do zapisu). Korekty informacji powinny być nowymi wpisami wskazującymi na wersje zastępowane.
- Wdróż przynajmniej jednego agenta weryfikującego w trybie tylko do odczytu, posiadającego niezależny dostęp do weryfikowanych źródeł danych.
- Kieruj wyniki analizy weryfikatora do zewnętrznego kanału raportowania, unikając zapisywania ich we wspólnej pamięci.
- Monitoruj wskaźnik zastępowania danych (override rate) — nagły wzrost tej metryki sygnalizuje występowanie halucynacji w procesie wnioskowania agentów.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że pierwsze uruchomienie propaguje halucynację, a drugie poprawnie ją wykrywa.
2. Dodaj kolejny błąd: niech Agent B zmyśli rozmiar analizowanego zbioru danych. Upewnij się, że weryfikator wykryje obie nieprawidłowości bez konieczności ręcznego dostrajania kodu.
3. Przekształć pulę wiadomości w tablicę podzieloną na tematy (`prices`, `summaries`, `analyses`). Przeanalizuj, w jakich sytuacjach taki podział tematów ogranicza ryzyko zatrucia pamięci, a w jakich nie przynosi korzyści.
4. Przeczytaj publikację Hayes-Roth (1985, „A Blackboard Architecture for Control”). Wskaż dwa opisane tam wzorce sterowania (pominięte w tej lekcji), które mogą przynieść korzyści nowoczesnym systemom agentowym.
5. Zapoznaj się z publikacją na temat CA-MCP (arXiv:2601.11595). Spróbuj odwzorować strukturę współdzielonego kontekstu z tej pracy na klasy `MessagePool` lub `Blackboard` z pliku `code/main.py`. Jakie dodatkowe mechanizmy wprowadza specyfikacja CA-MCP?

## Kluczowe terminy

| Termin | Obiegowe określenie | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Pula wiadomości (Message pool) | „Wspólna historia czatów” | Dziennik typu append-only odczytywany przez wszystkich agentów. Pełna przejrzystość, ale słaba skalowalność. |
| Tablica (Blackboard) | „Wspólna przestrzeń robocza” | Przestrzeń pub/sub z podziałem tematycznym. Agenci subskrybują wybrane tematy. Ułatwia skalowanie systemu. |
| Pochodzenie danych (Provenance) | „Kto co napisał” | Metadane powiązane z każdym zapisem: autor, czas, prompt systemowy, cytowane źródła. |
| Zatrucie pamięci (Memory poisoning) | „Rozprzestrzeniające się halucynacje” | Błąd wnioskowania jednego agenta trafia do pamięci współdzielonej, skąd jest pobierany przez kolejne agenty jako fakt. |
| Wyłącznie do zapisu (Append-only) | „Brak modyfikacji w miejscu” | Korekty stanowią nowe wpisy zastępujące stare wersje. Zachowuje pełną historię audytu. |
| Niezapisywalny weryfikator | „Niezależny audytor” | Agent z dostępem wyłącznie do odczytu, weryfikujący źródła danych i zgłaszający niespójności do zewnętrznego kanału. |
| Projekcja (Projection) | „Zawężony widok” | Obliczony na podstawie stanu globalnego widok pamięci dostosowany do roli konkretnego agenta (np. reduktory w LangGraph). |
| Źródło wiedzy (Knowledge source) | „Agent specjalistyczny” | Historyczne określenie Hayesa-Rotha (1985) na autonomicznego uczestnika tablicy ogłoszeń. |

## Literatura uzupełniająca

- [Cemri i in. — Dlaczego wieloagentowe systemy LLM zawodzą?](https://arxiv.org/abs/2503.13657) — taksonomia MAST; zatrucie pamięci zostało sklasyfikowane jako podrodzina błędów koordynacji.
- [CA-MCP — Context-Aware Multi-Server MCP](https://arxiv.org/abs/2601.11595) — koncepcja Shared Context Store dla skoordynowanych serwerów MCP.
- [Matrix — zdecentralizowany framework wieloagentowy](https://arxiv.org/abs/2511.21686) — tablica oparta na kolejce wiadomości bez centralnego koordynatora.
- [Stan i reduktory w LangGraph](https://docs.langchain.com/oss/python/langgraph/workflows-agents) — produkcyjny wzorzec projekcji stanu dla poszczególnych agentów.
- [Anthropic — Jak zbudowaliśmy nasz wieloagentowy system badawczy](https://www.anthropic.com/engineering/multi-agent-research-system) — notatki inżynieryjne na temat śledzenia pochodzenia danych i weryfikacji w systemach produkcyjnych.
