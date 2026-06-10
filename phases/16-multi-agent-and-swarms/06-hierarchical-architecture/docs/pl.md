# Architektura hierarchiczna i jej tryb awarii

> Hierarchiczny jest zagnieżdżony w nadzorcy. Agenci menedżerów nad podrzędnymi menedżerami nad pracownikami. CrewAI `Process.hierarchical` to wersja podręcznikowa: `manager_llm` dynamicznie deleguje zadania i sprawdza wyniki. Odpowiednikiem LangGraph jest `create_supervisor(create_supervisor(...))`. Jest to naturalny wzorzec, gdy zadaniem jest prawdziwy schemat organizacyjny. Jest to również schemat, który najprawdopodobniej popadnie w pętlę menedżerską – agenci menedżerowie źle przydzielają pracę, błędnie interpretują cząstkowe produkty lub nie osiągają konsensusu. Sekwencyjne często to bije.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania:** Faza 16 · 05 (Wzorzec Nadzorcy)
**Czas:** ~60 minut

## Problem

Kiedy już wzór nadzorcy się sprawdzi, naturalnym następnym krokiem będzie pytanie: „a co, jeśli pracownicy sami są przełożonymi?” Zespoły mają podzespoły; firmy mają działy działów. Odzwierciedlają to architektury hierarchiczne.

Problem: menedżerowie LLM to nie to samo, co menedżerowie-ludzie. Menedżer będący człowiekiem ma stabilne priorytety dotyczące tego, co wiedzą jego podwładni. Menedżer LLM na każdym kroku ponownie analizuje organizację, biorąc pod uwagę kontekst. W tym kontekście niewielka zmiana, a całe drzewo źle przydziela pracę.

## Koncepcja

### Kształt

```
                 Manager
                 ┌─────┐
                 └──┬──┘
           ┌────────┴────────┐
           ▼                 ▼
       Sub-Mgr A         Sub-Mgr B
       ┌─────┐           ┌─────┐
       └──┬──┘           └──┬──┘
         ┌┴──┬──┐          ┌┴──┐
         ▼   ▼  ▼          ▼   ▼
       W1  W2  W3         W4  W5
```

Każdy węzeł wewnętrzny planuje, deleguje i syntezuje. Tylko liście działają.

### Gdzie świeci

- **Wyraźne mapowanie organizacji.** Jeśli prawdziwe zadanie należy do działu („przegląd dokumentu pod kątem prawnym, przegląd finansowy dokumentu, przegląd techniczny dokumentu, a następnie podsumowanie dla kierownictwa”), hierarchia jest wyraźna.
- **Podsumowanie lokalne.** Każdy podrzędny menedżer syntezuje wyniki swojego zespołu, zanim zobaczy je najwyższy menedżer. Najwyższy menedżer widzi trzy podsumowania podrzędnych menedżerów, a nie piętnaście wyników pracowników.

### Gdzie się psuje

Sekcje zwłok z 2026 r. stale odkrywają trzy tryby awarii:

1. **Błąd w przydzieleniu zadania.** Menedżer odczytuje cel, ma halucynacje rozkładu i deleguje zadanie niewłaściwemu podrzędnemu menadżerowi. Ponieważ podrzędny menedżer posłusznie pracuje nad tym, co mu powierzono, błąd pojawia się dopiero na najwyższym szczeblu syntezy — o jeden poziom dalej od miejsca, w którym człowiek mógłby go wyłapać.
2. **Błędna interpretacja wyników.** Podrzędny menedżer zwraca „nie można zweryfikować roszczenia X”. Najwyższy menedżer podsumowuje to następująco: „twierdzenie X nie zostało potwierdzone”. Znaczenie dryfuje na każdym poziomie.
3. **Pętle konsensusu.** Dwóch podrzędnych menedżerów nie zgadza się; menedżer najwyższego szczebla prosi ich o pojednanie; ponownie delegują w dół; ponowne uruchomienie pracowników; podrzędni menedżerowie zwracają nieco inne odpowiedzi; pętla. `Process.hierarchical` CrewAI chroni przed tym za pomocą limitów kroków, ale sam limit jest teraz hiperparametrem.

### Decydujące pytanie

Sekwencyjny (liniowy potok) czy hierarchiczny: czy Twoje zadanie faktycznie składa się z niezależnych podzespołów, czy też jest to jeden liniowy przepływ udający drzewo? Jeśli to drugie, użyj sekwencyjnego. Jeśli to pierwsze, użyj hierarchicznych, ale jawnie budżetowych reguł uzgadniania.

### Implementacja CrewAI

`Process.hierarchical` kontaktuje się z menedżerem LLM w sprawie specjalistycznych załóg. Menedżer:

- otrzymuje zadanie najwyższego szczebla,
- przydziela podzadania załogom,
- ocenia dorobek załogi,
- decyduje, czy zaakceptować, ponownie delegować, czy powtórzyć.

Dokumentacja: https://docs.crewai.com/en/introduction (poszukaj „Proces hierarchiczny” w obszarze Podstawowe koncepcje).

### Implementacja LangGrapha

LangGraph używa zagnieżdżonych wywołań `create_supervisor`. Wewnętrzny nadzorca ma swój własny wykres; zewnętrzny nadzorca traktuje wykres wewnętrzny jako nieprzezroczysty węzeł. Jest to czystsze niż CrewAI do debugowania (możesz przechodzić przez każdy wykres osobno), ale trudniej wyrazić dynamiczne przekształcanie drzewa.

Odniesienie: https://reference.langchain.com/python/langgraph-supervisor.

## Zbuduj to

`code/main.py` obsługuje 3-poziomową hierarchię:

- top manager: dzieli zadanie na gałęzie „inżynierską” i „prawną”,
- sub-menedżer inżynieryjny: dzieli się na pracowników "frontendowych" i "backendowych",
- zastępca kierownika prawnego: jeden pracownik.

Demo porównuje szczęśliwą ścieżkę (wszyscy się z tym zgadzają) z **zaburzoną ścieżką**, w której rozkład dokonany przez najwyższego menedżera błędnie oznacza „legalne” jako „finanse” i obserwuje kaskadę błędów – podrzędny menedżer posłusznie finansuje prace, czołowy syntezator zgłasza ustalenia dotyczące finansów, pierwotne pytanie prawne pozostaje bez odpowiedzi.

Uruchom:

```
python3 code/main.py
```

Dane wyjściowe pokazują obie ścieżki z wyraźnym zestawieniem „o co poproszono” i „co dostarczono”.

## Użyj tego

`outputs/skill-hierarchy-fitness.md` ocenia, czy dane zadanie powinno używać nadzorcy hierarchicznego, sekwencyjnego czy płaskiego. Dane wejściowe: opis zadania, struktura organizacyjna, budżet uzgodnieniowy. Dane wyjściowe: zalecenie wzorca z konkretnymi trybami awarii, przed którymi należy się chronić.

## Wyślij to

Jeśli wysyłasz hierarchicznie:

- **Głębokość drzewa czapek na poziomie 2.** Trzy poziomy już ukrywają większość błędów przed obserwowalnością.
- **Wyraźny budżet uzgodnienia.** Ustaw maksymalną liczbę rund, zanim najwyższy menedżer będzie musiał zatwierdzić. Zwykle 2.
- **Pochodzenie każdej syntezy.** Podsumowanie każdego węzła musi zawierać informację, które liście go wytworzyły.
- **Powiadomienie o dryfie rozkładu.** Rejestrowanie rozkładu menedżera na każdy krok; diff względem zapytania użytkownika. Jeśli rozkład nie obejmuje już zapytania, uruchom alert.

## Ćwiczenia

1. Uruchom `code/main.py` i porównaj radość i zaniepokojenie. Ile poziomów przekazania menedżera potrzeba, zanim najwyższy wynik całkowicie odbiega od pytania użytkownika?
2. Dodaj trzeci poziom (górny → podrzędny → podrzędny → pracownik). Zmierz, jak często zaburzona ścieżka koryguje się lub całkowicie rozchodzi w miarę wzrostu głębokości.
3. Wprowadź pracownika „kanarka” u każdego podrzędnego menedżera, który będzie zawsze zadawał pierwotne pytanie użytkownika w niezmienionej formie. Użyj odpowiedzi kanarkowej, aby wykryć dryf rozkładu. Jak powinien zareagować menedżer, gdy kanarek nie zgadza się z syntezowaną odpowiedzią?
4. Przeczytaj dokumentację `Process.hierarchical` CrewAI. Zidentyfikuj jedną konkretną poręcz, którą stosuje CrewAI (limit kroków, ograniczenie manager_llm) i opisz, na jaki tryb awarii ma ona być ukierunkowana.
5. Porównaj zagnieżdżone nadzorcy LangGraph z hierarchią CrewAI. Co sprawia, że ​​pętle uzgadniające są tańsze w wykrywaniu?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Hierarchiczny | „Wzór schematu organizacyjnego” | Przełożeni nad przełożonymi; tylko liście działają. |
| Menedżer LLM | „Szef” | LLM, który rozkłada, przypisuje i sprawdza poprawność w węźle wewnętrznym. |
| Dryf rozkładu | „Szef zgubił fabułę” | Podział najwyższego menedżera nie obejmuje już pierwotnego pytania. |
| Pętla uzgadniania | „Niekończące się spotkania” | Podrzędni menedżerowie nie zgadzają się z tym; najlepsi redelegaci; ponowne uruchomienie pracowników; pętla aż do wyczerpania budżetu. |
| Sufit o głębokości 2 | „Nie schodź głębiej niż 2 poziomy” | Empiryczna poręcz: ponad 3 poziomy załamują obserwowalność. |
| Pytanie kanaryjskie | „Podstawowa prawda na każdym poziomie” | Pracownikowi zawsze zadawane jest pierwotne zapytanie bez zmian, aby wykryć dryf. |
| Łańcuch pochodzenia | „Kto co powiedział” | Prześledź każdą syntezę z powrotem do liści, które ją wytworzyły. |

## Dalsze czytanie

- [Wprowadzenie do CrewAI — Process.hierarchical](https://docs.crewai.com/en/introduction) — podręcznik hierarchiczny z menadżerem LLM
- [Odniesienie do nadzorcy LangGraph](https://reference.langchain.com/python/langgraph-supervisor) — nadzorca zagnieżdżony poprzez `create_supervisor`
- [Inżynieria antropiczna — System badawczy](https://www.anthropic.com/engineering/multi-agent-research-system) — dlaczego firma Anthropic celowo wybrała płaskiego nadzorcę zamiast hierarchicznego
- [Cemri i in. — Dlaczego wieloagentowe systemy LLM zawodzą?](https://arxiv.org/abs/2503.13657) — taksonomia MAST; sekcja poświęcona błędom koordynacji dokumentuje dryf rozkładu