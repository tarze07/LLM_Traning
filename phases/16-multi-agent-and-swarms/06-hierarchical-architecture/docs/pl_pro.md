# Architektura hierarchiczna i jej tryby awarii

> Architektura hierarchiczna stanowi zagnieżdżoną odmianę wzorca nadzorcy: menedżerowie zarządzają podrzędnymi menedżerami, którzy z kolei nadzorują pracowników. Klasycznym przykładem jest proces hierarchiczny w CrewAI (`Process.hierarchical`), w którym `manager_llm` dynamicznie deleguje zadania i weryfikuje ich wyniki. W LangGraph odpowiednikiem jest zagnieżdżona struktura nadzorców `create_supervisor(create_supervisor(...))`. Wzorzec ten jest intuicyjny, gdy struktura zadań odzwierciedla realny schemat organizacyjny firmy. Niesie on jednak ze sobą wysokie ryzyko wpadnięcia w tzw. pętlę menedżerską — agenci na stanowiskach kierowniczych mogą błędnie delegować pracę, nieprawidłowo interpretować raporty cząstkowe lub mieć trudności z wypracowaniem konsensusu. Z tego powodu proste potoki sekwencyjne często okazują się skuteczniejsze.

**Typ:** Ucz się + Buduj  
**Języki:** Python (stdlib)  
**Wymagania:** Faza 16 · 05 (Wzorzec nadzorcy)  
**Czas:** ~60 minut  

## Problem

Gdy wzorzec pojedynczego nadzorcy zdaje egzamin, naturalnym krokiem wydaje się zagnieżdżanie tej struktury: „co jeśli pracownicy sami będą nadzorcami?”. W realnym świecie zespoły składają się z podzespołów, a firmy z pionów i departamentów. Architektury hierarchiczne próbują odtworzyć te zależności.

Problem polega na tym, że menedżerowie LLM różnią się zasadniczo od menedżerów-ludzi. Menedżer będący człowiekiem opiera się na stabilnych priorytetach i stałym zrozumieniu kompetencji podwładnych. Menedżer LLM przy każdym kroku na nowo analizuje sytuację w oparciu o aktualny kontekst. W tym modelu nawet minimalna zmiana w oknie kontekstowym może sprawić, że całe drzewo agentów błędnie przydzieli zadania.

## Koncepcja

### Struktura hierarchii

```
                   Menedżer
                   ┌─────┐
                   └──┬──┘
             ┌────────┴────────┐
             ▼                 ▼
        Podkierownik A    Podkierownik B
        ┌─────┐           ┌─────┐
        └──┬──┘           └──┬──┘
          ┌┴──┬──┐          ┌┴──┐
          ▼   ▼  ▼          ▼   ▼
        W1  W2  W3         W4  W5
```

Każdy węzeł wewnętrzny (menedżer) planuje, deleguje zadania i dokonuje ich syntezy. Pracę wykonawczą realizują wyłącznie liście drzewa (Workers).

### Gdzie ta architektura się sprawdza

- **Odzwierciedlenie struktury organizacyjnej.** Jeśli zadanie ma strukturę wprost zaczerpniętą z procesów biznesowych firmy (np. „analiza dokumentu pod kątem prawnym, następnie analiza finansowa, techniczna i na końcu podsumowanie dla zarządu”), hierarchia jest naturalnym odzwierciedleniem tego podziału.
- **Agregacja i lokalne podsumowania.** Każdy menedżer niższego szczebla dokonuje syntezy raportów swojego zespołu, zanim przekaże je wyżej. Dzięki temu dyrektor najwyższego szczebla zapoznaje się z trzema zwięzłymi podsumowaniami, a nie z piętnastoma surowymi raportami wykonawców.

### Gdzie architektura hierarchiczna zawodzi

Analizy wdrożeń produkcyjnych wskazują na trzy główne tryby awarii:

1. **Błąd przydziału zadań (Decomposition Drift).** Menedżer analizuje główny cel, błędnie go dekomponuje i deleguje zadanie niewłaściwemu podkierownikowi. Ponieważ podkierownik posłusznie wykonuje powierzoną pracę, błąd ten ujawnia się dopiero na najwyższym poziomie syntezy — daleko od miejsca, w którym człowiek mógłby go łatwo wykryć.
2. **Dryf znaczeniowy (Semantic Drift).** Podkierownik raportuje: „nie udało się jednoznacznie potwierdzić faktu X”. Menedżer najwyższego szczebla skraca to w podsumowaniu do: „fakt X jest nieprawdziwy”. Informacja ulega zniekształceniu na każdym poziomie hierarchii.
3. **Pętle decyzyjne (Consensus Loops).** Dwaj podkierownicy przedstawiają sprzeczne wnioski. Menedżer najwyższego szczebla odsyła je do ponownego uzgodnienia; podkierownicy delegują zadania w dół; pracownicy uruchamiają procesy na nowo; podkierownicy zwracają nieznacznie zmienione odpowiedzi, co ponownie uruchamia cały cykl. W CrewAI proces hierarchiczny jest chroniony limitami kroków (`max_iter`), ale sam limit staje się kolejnym hiperparametrem do dostrojenia.

### Decydujące pytanie

Czy potok powinien być sekwencyjny (liniowy), czy hierarchiczny? Zastanów się, czy zadanie rzeczywiście dzieli się na w pełni niezależne bloki, czy jest to tylko liniowy proces sztucznie rozpisany na drzewo. W tym drugim przypadku znacznie lepiej sprawdzi się potok sekwencyjny. Jeśli wybierasz hierarchię, musisz wdrożyć sztywne zasady budżetowania interakcji i uzgadniania wyników.

### Implementacja w CrewAI

W procesie hierarchicznym CrewAI automatycznie powołuje menedżera LLM, który:
- odbiera zadanie najwyższego poziomu,
- przydziela podzadania odpowiednim zespołom (crew),
- ocenia jakość dostarczonych wyników,
- podejmuje decyzję o akceptacji raportu, jego odrzuceniu lub ponownym delegowaniu z informacją zwrotną.

Szczegóły znajdziesz w dokumentacji pod hasłem „Hierarchical Process”.

### Implementacja w LangGraph

LangGraph realizuje ten wzorzec poprzez zagnieżdżanie wywołań `create_supervisor`. Wewnętrzny nadzorca zarządza własnym subgrafem, który z perspektywy zewnętrznego nadzorcy jest widoczny jako pojedynczy, czarnoskrzynkowy węzeł. To podejście ułatwia debugowanie (można testować i logować każdy subgraf niezależnie), ale utrudnia dynamiczne modyfikacje struktury drzewa w locie.

Szczegóły w dokumentacji: `langgraph-supervisor`.

## Zbuduj to

W pliku `code/main.py` zaimplementowano trójpoziomową hierarchię:
- Menedżer najwyższego szczebla (Top Manager) dzielący zadanie na pion „inżynieryjny” i „prawny”,
- Podkierownik inżynieryjny dzielący pracę pomiędzy programistów frontendu i backendu,
- Podkierownik ds. prawnych nadzorujący jednego pracownika.

Demo porównuje ścieżkę optymistyczną (happy path, w której wszyscy agenci są zgodni) ze **ścieżką zaburzoną (perturbed path)**. W ścieżce zaburzonej błędna dekompozycja na najwyższym szczeblu kieruje zagadnienie prawne do pionu finansowego. Możemy zaobserwować kaskadę błędów: podkierownik finansowy posłusznie realizuje analizy budżetowe, Top Manager dokonuje syntezy danych finansowych, a pierwotny problem prawny pozostaje nierozwiązany.

Uruchomienie:

```
python3 code/main.py
```

## Użyj tego

W pliku `outputs/skill-hierarchy-fitness.md` zdefiniowano umiejętność służącą do oceny, czy dany proces biznesowy powinien korzystać z architektury hierarchicznej, sekwencyjnej czy płaskiej. Narzędzie analizuje opis zadania, strukturę zespołu oraz budżet i rekomenduje optymalny wzorzec, wskazując ryzyka awarii, na które należy uważać.

## Wyślij to

Zasady wdrażania architektur hierarchicznych:

- **Ograniczenie głębokości drzewa do maksymalnie 2 poziomów.** Trzy poziomy zagnieżdżenia drastycznie utrudniają monitorowanie, sprawiając, że błędy stają się niewidoczne dla systemów obserwowalności.
- **Sztywny budżet uzgodnień (consensus budget).** Określ maksymalną liczbę rund poprawek, po której menedżer najwyższego szczebla musi podjąć ostateczną decyzję (zalecany limit to 2).
- **Śledzenie pochodzenia informacji (Lineage).** Każde podsumowanie generowane przez menedżera musi jasno wskazywać, na podstawie których raportów pracowników (Workers) powstało.
- **Detekcja dryfu dekompozycji.** Rejestruj plany dekompozycji na każdym poziomie i porównuj je z pierwotnym zapytaniem użytkownika. W przypadku wykrycia rozbieżności system powinien wygenerować alert.

## Ćwiczenia

1. Uruchom `code/main.py` i porównaj ścieżkę optymistyczną ze ścieżką zaburzoną. Ile kroków delegacji potrzeba, aby wynik końcowy całkowicie stracił powiązanie z pierwotnym pytaniem użytkownika?
2. Dodaj trzeci poziom zagnieżdżenia (Top → Middle → Sub-Middle → Worker). Zbadaj, jak głębokość hierarchii wpływa na zdolność systemu do samokorekty błędów delegacji.
3. Wprowadź pracownika typu „kanarek” na każdym poziomie zarządzania. Zadaniem kanarka jest przekazywanie pierwotnego pytania użytkownika w niezmienionej formie w głąb struktury w celu wykrywania dryfu dekompozycji. Jak powinien zareagować menedżer, gdy raport kanarka różni się od syntezy pozostałych pracowników?
4. Przeanalizuj proces hierarchiczny w CrewAI. Wskaż wbudowane mechanizmy zabezpieczające (np. limity iteracji, ograniczenia modelu menedżera) i opisz, przed którymi trybami awarii mają one chronić.
5. Porównaj zagnieżdżonych nadzorców w LangGraph z hierarchią w CrewAI. Które podejście ułatwia wykrywanie i przerywanie kosztownych pętli decyzyjnych?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Architektura hierarchiczna | „Struktura schematu organizacyjnego” | Układ zagnieżdżonych nadzorców, w którym pracę wykonawczą realizują wyłącznie liście drzewa (Workers). |
| Menedżer LLM | „Agent kierownik” | Model LLM odpowiedzialny za dekompozycję celów, przydział zadań i weryfikację wyników w węźle wewnętrznym. |
| Dryf dekompozycji | „Rozbieżność planu” | Błąd polegający na tym, że plany cząstkowe menedżerów przestają pokrywać się z pierwotnym celem głównym. |
| Pętla decyzyjna (Consensus Loop) | „Zapętlenie ustaleń” | Nieskończona wymiana poprawek i ponownych delegacji zadań pomiędzy poziomami zarządzania. |
| Limit głębokości do 2 | „Cap depth at 2” | Praktyczna zasada zabraniająca tworzenia struktur głębszych niż 2 poziomy w celu zachowania sterowalności. |
| Pracownik kanarek (Canary Worker) | „Weryfikator kontekstu” | Wyszukiwanie lub agent sprawdzający, który na każdym poziomie weryfikuje zgodność z pierwotnym celem. |
| Łańcuch pochodzenia (Lineage) | „Metadane pochodzenia” | Śledzenie i mapowanie wyników syntezy bezpośrednio do raportów źródłowych pracowników, którzy je wygenerowali. |

## Dalsze czytanie

- [CrewAI: Hierarchical Process](https://docs.crewai.com/en/introduction) — opis implementacji hierarchii z dedykowanym menedżerem LLM.
- [LangGraph: Zagnieżdżeni nadzorcy](https://reference.langchain.com/python/langgraph-supervisor) — dokumentacja orkiestracji hierarchicznej za pomocą `create_supervisor`.
- [Anthropic Engineering: Research System](https://www.anthropic.com/engineering/multi-agent-research-system) — uzasadnienie, dlaczego Anthropic świadomie zrezygnował z hierarchii na rzecz płaskiej struktury nadzorcy.
- [Cemri i in. — Why Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) — taksonomia MAST; sekcja dotycząca błędów koordynacji szczegółowo opisuje dryf dekompozycji.
