# Wzór nadzorcy/orkiestratora-pracownika

> Jeden główny agent planuje i deleguje; wyspecjalizowani pracownicy wykonują zadania w równoległych kontekstach i składają raporty. Taki jest wzór stojący za systemem badawczym Anthropic (Claude Opus 4 jako główny, Sonnet 4 jako subagenci), zmierzony na poziomie +90,2% w porównaniu z Opus 4 z jednym agentem, według wewnętrznych ocen badań. W poście inżynierskim Anthropic podano, że 80% rozbieżności w BrowseComp wynika z samego użycia tokena — wieloagent wygrywa głównie dlatego, że każdy podagent otrzymuje nowe okno kontekstowe. Ta lekcja buduje wzorzec nadzorcy na podstawie elementów podstawowych i obejmuje wnioski inżynieryjne z roku 2026 z wdrożeń produkcyjnych.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib, `threading`)
**Wymagania wstępne:** Faza 16 · 04 (model prymitywny)
**Czas:** ~75 minut

## Problem

Badania to prototypowe zadanie, którego zawodzą systemy jednoagentowe. Pytasz „co zmieniło się w systemach wieloagentowych w latach 2023–2026?” Pojedynczy agent czyta kolejno pięć artykułów, wypełnia ich tekstem połowę kontekstu, a następnie musi je wszystkie razem przemyśleć. Zapomina o pierwszym artykule, zanim dotrze do piątego. Nie może być równoległe.

Wzorzec nadzorcy rozwiązuje ten problem: jeden główny agent planuje wyszukiwanie, deleguje każde pytanie cząstkowe pracownikowi i dokonuje syntezy. Każdy pracownik otrzymuje własne okno o wartości 200 tys. tokenów na wąskie pytanie. Potencjalny klient nigdy nie widzi surowych dokumentów — jedynie streszczenia pracowników.

System badawczy firmy Anthropic raportuje +90,2% ocen wewnętrznych badań w porównaniu z pojedynczym Opusem 4. W tym samym poście zauważono, że 80% wariancji BrowseComp wynika z *samego użycia tokena*. Głównym mechanizmem jest świeży kontekst dla każdego subagenta.

## Koncepcja

### Wzór

```
                 ┌──────────────┐
                 │   Lead       │  plans, decomposes,
                 │  (Opus 4)    │  synthesizes
                 └──┬────┬───┬──┘
                    │    │   │
            ┌───────┘    │   └───────┐
            ▼            ▼           ▼
      ┌─────────┐  ┌─────────┐  ┌─────────┐
      │ Worker1 │  │ Worker2 │  │ Worker3 │
      │(Sonnet) │  │(Sonnet) │  │(Sonnet) │
      └─────────┘  └─────────┘  └─────────┘
         fresh       fresh        fresh
         context     context      context
```

Lead nigdy nie czyta surowców. Pracownicy nigdy nie widzą się nawzajem, dopóki ołów nie zsyntetyzuje. Każda strzałka to połączenie z wąskim artefaktem.

### Dlaczego wygrywa

Trzy mechanizmy:

1. **Nowy kontekst na podagenta.** Pracownik badający „dziedzictwo FIPA-ACL” nie ma przy sobie 40 tys. tokenów wydanych na planowanie. Dostaje 200 tys. okien na jedno pytanie.
2. **Specjalizacja poprzez zachętę.** Podpowiedź potencjalnego klienta brzmi „rozłóż i zsyntetyzuj”, a nie „badania”. Podpowiedź każdego pracownika jest wąska: „znajdź, co zmieniło się w X”. Skoncentrowane podpowiedzi dają ukierunkowane wyniki.
3. **Równoległość.** Pracownicy pracują jednocześnie. Czas zegara ściennego to mniej więcej `max(worker_times) + plan + synthesis`, a nie `sum(worker_times)`.

### Lekcje inżynierii (Anthropic 2025)

W poście Anthropic wymieniono kilka lekcji dotyczących produkcji, które są nadal istotne w roku 2026:

- **Skaluj wysiłek, aby zapytać o złożoność.** Proste zapytania: jeden agent, 3–10 wywołań narzędzi. Złożone zapytania: ponad 10 agentów. Lead musi to oszacować, a nie rozmówca.
- **Szerokie, a potem wąskie.** Najpierw rozłóż na ogólne pytania cząstkowe, a następnie stwórz więcej robotników na każde pytanie podrzędne, jeśli odpowiedź wymaga głębi.
- **Wdrożenia Rainbow.** Agenci działają długotrwale i stanowo. Tradycyjny niebiesko-zielony nie działa. Anthropic wykorzystuje tęczę: stopniowe wdrażanie nowych wersji, podczas gdy stare się wyczerpują.
- **Dominuje użycie tokenów.** Multiagent to ~15 razy więcej tokenów niż jeden agent. Uruchamiaj go tylko wtedy, gdy wartość zadania uzasadnia koszt.

### Zakręt LangGraph

Pierwotnie LangGraph dostarczył bibliotekę `langgraph-supervisor` z wysokopoziomowym pomocnikiem `create_supervisor`. W 2025 roku LangChain przeniósł zalecenie na wdrożenie wzorca nadzorcy poprzez bezpośrednie wywoływanie narzędzi, ponieważ wywołania narzędzi dają większą kontrolę nad *tym, co widzi nadzorca* (inżynieria kontekstu). Biblioteka nadal działa; dokumentacja zaleca teraz formularz wywoływania narzędzi.

### Tryby awarii

- **Ołów ma halucynacje na temat planu.** Jeśli potencjalny klient generuje pytania podrzędne, które nie rozkładają prawdziwego pytania, pracownicy przeprowadzają dokładne badania pod kątem niewłaściwego celu.
- **Pracownicy nadmiernie eksplorują.** Bez wyraźnych granic zakresu pracownicy wykraczają poza przypisane im pytania poboczne i zanieczyszczają etap syntezy.
- **Konflikty syntezy.** Dwóch pracowników podaje sprzeczne fakty. Prowadzący musi albo zapytać ponownie (dodać rundę), albo wyraźnie odnotować brak porozumienia. Ciche wybieranie jednej ze stron jest najgorszą porażką: użytkownik nigdy nie wie, że doszło do nieporozumienia.

### Kiedy przełożony się myli

- **Zadania sekwencyjne.** Jeśli krok 2 dosłownie potrzebuje danych wyjściowych kroku 1, równoległość nic nie daje. Użyj potoku (CrewAI Sequential, wykres liniowy LangGraph).
- **Proste zapytania.** Pojedynczy agent obsługuje je szybciej i taniej. Przed odrodzeniem pracowników użyj testu „skali wysiłku” potencjalnego klienta.
- **Ścisły determinizm.** Przełożony korzysta z delegacji wybranej przez LLM. Wykresy statyczne są lepsze, gdy audyt/powtórka ma większe znaczenie niż zdolność adaptacji.

## Zbuduj to

`code/main.py` implementuje nadzorcę trzech równoległych pracowników przy użyciu `threading`. Namiar rozkłada zapytanie na pytania podrzędne, pracownicy pracują jednocześnie nad każdym pytaniem podrzędnym, a namiar dokonuje syntezy. Żadnych prawdziwych LLM — pracownicy mają skrypt symulujący pobieranie i podsumowywanie.

Struktura klucza:

- `Lead.plan(query)` dzieli zapytanie na 3 pytania cząstkowe.
- `Worker.run(sub_q)` zwraca fałszywe podsumowanie (może to być dowolny agent korzystający z narzędzia w środowisku produkcyjnym).
- `Lead.run(query)` uruchamia procesy robocze w wątkach, łączy i syntezuje.

Uruchom:

```
python3 code/main.py
```

Dane wyjściowe przedstawiają plan, równoległe ścieżki robocze ze znacznikami czasu rozpoczęcia i zakończenia oraz końcową syntezę. Możesz zobaczyć, jak wygrywa zegar ścienny: trzech pracowników pracujących w czasie 0,3 sekundy działa w ~0,35 sekundy, a nie 0,9.

## Użyj tego

`outputs/skill-supervisor-designer.md` pobiera zapytanie użytkownika i tworzy projekt wzorca nadzorcy: monit systemu prowadzącego, role pracowników, zasady rozkładu pytań podrzędnych i szablon syntezy. Użyj tego przed zbudowaniem nowego systemu agentów w stylu badawczym.

## Wyślij to

Lista kontrolna przed wdrożeniem wzorca nadzorcy:

- **Parowanie modeli.** Kieruj modelem na poziomie rozumowania (klasa Opus, klasa `o3`). Pracownicy korzystający z szybszego i tańszego modelu (Sonnet, `o4-mini`).
- **Przekroczenie limitu czasu pracy.** Każdy pracownik, który przekroczy 2× średni czas działania, zostaje zabity; lead albo pojawia się ponownie z węższym zakresem, albo działa bez niego.
- **Limit tokenów na pracownika.** Sztywny limit (powiedzmy 10-krotność oczekiwanego wkładu syntezy) zapobiega nadmiernemu zużyciu budżetu przez uciekającego pracownika.
- **Obserwowalność.** Śledź plan potencjalnego klienta, wywołania narzędzi każdego pracownika i syntezę. Jest to podstawa każdego debugowania post-hoc.
- **Wdrożenie Rainbow.** Długotrwali agenci stanowi wymagają stopniowego przejścia wersji, a nie wymiany podczas pracy.

## Ćwiczenia

1. Uruchom `code/main.py`, a następnie zmodyfikuj przewód, aby odrodzić 5 robotników zamiast 3. Obserwuj efekt zegara ściennego. Przy jakiej liczbie pracowników koszty odradzania przekraczają równoległe oszczędności w tym demo?
2. Wprowadź limit czasu dla pracownika: zabij dowolnego pracownika, który działa dłużej niż 0,5 sekundy i poproś prowadzącego o syntezę pozostałych wyników. Jaka obserwowalność jest potrzebna, aby wiedzieć, że pracownik został przecięty?
3. Dodaj etap wykrywania konfliktu do syntezy leada: jeśli dwóch pracowników zwróci sprzeczne odpowiedzi, lead odnotuje różnicę zdań, zamiast wybrać jedną. Jak wykryć sprzeczność bez wywoływania LLM?
4. Przeczytaj post dotyczący inżynierii systemów badawczych firmy Anthropic. Wymień trzy praktyki, które ta wersja demonstracyjna zabawki musiałaby zostać zastosowana, aby mogła zostać uruchomiona w środowisku produkcyjnym.
5. Porównaj `create_supervisor` LangGraph (starsze) z nowym zaleceniem dotyczącym wywoływania narzędzi. Co daje lepszą kontrolę nad tym, co widzi przełożony? Dlaczego Anthropic wyraźnie przekazuje do syntezy tylko odpowiedzi cząstkowe, a nie surowy kontekst pracownika?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Nadzorca | „Agent wiodący” | Agent orkiestratora, który planuje, deleguje i syntetyzuje. Nie wykonuje pracy samodzielnie. |
| Pracownik | „Subagenta” | Skoncentrowany agent przywoływany przez przełożonego, o wąskim zakresie i własnym oknie kontekstowym. |
| Orkiestrator-pracownik | „Wzorzec nadzorcy” | To samo, inna nazwa. W literaturze z roku 2026 używa się obu. |
| Świeży kontekst | „Czyste okno” | Kontekst pracownika zaczyna się od podpowiedzi systemowej i przypisanego mu pytania, a nie od historii potencjalnego klienta. |
| Wdrożenie tęczy | „Stopniowe wdrażanie” | Długotrwałe agenty stanowe wymagają wersjonowania typu opróżnij i wymień, a nie niebiesko-zielonego. |
| Dominacja symboliczna | „Kontekst jest zmienną” | 80% wariancji w ocenie badań wynika z całkowitej liczby wykorzystanych tokenów, a nie z wyboru modelu, według Anthropic. |
| Skala wysiłku | „Dopasuj liczbę agentów do złożoności” | Lead szacuje trudność zapytania i odpowiednio tworzy 1 na 10+ pracowników. |
| Konflikt syntezy | „Pracownicy się nie zgadzają” | Dwóch pracowników podaje sprzeczne fakty; lider musi ujawnić różnicę zdań, a nie po cichu wybierać jedno. |

## Dalsze czytanie

- [Inżynieria antropiczna — Jak zbudowaliśmy nasz wieloagentowy system badawczy](https://www.anthropic.com/engineering/multi-agent-research-system) — odniesienie produkcyjne dla wzorca nadzorcy
- [Przepływy pracy i agenci LangGraph](https://docs.langchain.com/oss/python/langgraph/workflows-agents) — zalecaną formą jest teraz nadzór nad wywoływaniem narzędzi
- [Odniesienie do nadzorcy LangGraph](https://reference.langchain.com/python/langgraph-supervisor) — starszy pomocnik, nadal używany w produkcji z 2026 r.
- [Książka kucharska OpenAI — Agenci orkiestrujący: procedury i przekazywanie](https://developers.openai.com/cookbook/examples/orchestrating_agents) — wariant nadzorcy oparty na przekazywaniu