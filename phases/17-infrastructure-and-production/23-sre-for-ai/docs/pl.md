# SRE dla AI — wieloagentowa reakcja na incydenty, elementy Runbook, wykrywanie predykcyjne

> AI SRE wykorzystuje LLM oparte na danych infrastruktury (dzienniki, elementy Runbook, topologia usług) za pośrednictwem RAG w celu automatyzacji faz badania, dokumentacji i koordynacji. Wzorzec architektury 2026 to orkiestracja wieloagentowa — wyspecjalizowani agenci (dzienniki, metryki, elementy Runbook) koordynowani przez przełożonego; Sztuczna inteligencja proponuje hipotezy i pytania, ludzie zatwierdzają wnioski o wydanie opinii. Datadog Bits AI i Azure SRE Agent dostarczają to jako produkty zarządzane. Elementy Runbook ewoluują: NeuBird Hawkeye wykorzystuje ocenę kontradyktoryjną (dwa modele analizują ten sam incydent; zgoda = pewność, niezgoda = niepewność); pamięć operacyjna utrzymuje się pomimo zmian w zespole. Automatyczna naprawa pozostaje ostrożna: sztuczna inteligencja sugeruje, ludzie aprobują. W pełni autonomiczne działanie jest wąskie (ponowne uruchomienie kapsuły, specyficzne wdrożenie wycofania) z ciasnymi barierami ochronnymi — każdy, kto sprzedaje „ustaw i zapomnij”, sprzedaje za dużo. Emerging frontier: przewidywanie przed incydentem. Badania MIT donoszą, że LLM przeszkolony na podstawie dzienników historycznych, temperatur GPU i wzorców błędów API przewidział 89% przestojów 10–15 minut wcześniej. Prognoza: do końca 2026 r. 95% przedsiębiorstw LLM będzie miało automatyczne przełączanie awaryjne.

**Typ:** Ucz się
**Języki:** Python (stdlib, zabawkowy wieloagentowy symulator selekcji incydentów)
**Wymagania wstępne:** Faza 17 · 13 (Obserwowalność), Faza 17 · 24 (Inżynieria Chaosu)
**Czas:** ~60 minut

## Cele nauczania

- Diagram wieloagentowej architektury AI SRE: nadzorca + wyspecjalizowani agenci (logi, metryki, elementy runbook) + bramka zatwierdzania przez człowieka.
- Wyjaśnij, dlaczego automatyczne korygowanie jest wąskie (uruchom ponownie moduł, cofnij wdrożenie), a nie szerokie (usługa zmiany architektury).
- Nazwij kontradyktoryjny wzorzec oceny (NeuBird Hawkeye): dwa modele zgodne = pewność; nie zgadzać się = eskalować.
- Przytocz wynik wczesnego wykrywania MIT wynoszący 89% i ograniczenie operacyjne: prognozy bez uruchomienia to tylko pulpity nawigacyjne.

## Problem

O 3:00 inżynier dyżurujący otrzymuje wezwanie „Wysoki poziom błędów przy kasie”. Sprawdzają Datadog, Lokiego, trzy elementy Runbook i dziennik wdrażania. 30 minut później zdają sobie sprawę, że główną przyczyną jest vLLM OOM wynikający ze skoku pamięci podręcznej KV. Ponownie uruchamiają kapsułę; błąd zostaje usunięty.

W 2026 r. pierwsze 20 minut tego śledztwa będzie można zautomatyzować. Grupowanie dzienników według usługi, korelacja z ostatnimi wdrożeniami, dopasowywanie do elementów Runbook — wszystkie korzystają z narzędzi RAG +. Nadzorowany agent może przeprowadzić selekcję przy pierwszym przejściu i przedstawić hipotezę, zanim człowiek otworzy Datadog.

Całkowicie autonomiczne środki zaradcze to inny problem. Uruchom ponownie kapsułę: bezpiecznie. Skaluj pulę GPU: bezpieczna, jeśli pozwalają na to zasady. Zmień architekturę usługi: absolutnie nie. Dyscyplina polega na rysowaniu wąskiej linii.

## Koncepcja

### Architektura wieloagentowa

```
          Incident
             │
             ▼
        Supervisor
        /    |    \
       ▼     ▼     ▼
  Log agent  Metric agent  Runbook agent
       │     │     │
       └─────┴─────┘
             │
             ▼
        Hypothesis + evidence
             │
             ▼
        Human approval
             │
             ▼
        Action (narrow set)
```

Przełożony dzieli zdarzenie na podzapytania. Wyspecjalizowani agenci mają dostęp do narzędzi (przeszukiwanie logów, PromQL, wyszukiwanie dokumentów). Przełożony dokonuje syntezy, przedstawia hipotezę i dowody człowiekowi. Człowiek zatwierdza lub przekierowuje.

### Zakres automatycznej naprawy

**Bezpieczny (wąski)**: uruchom ponownie moduł, przywróć określone wdrożenie, skaluj pulę w ramach wstępnie zatwierdzonych granic, włącz flagę wstępnie zatwierdzonych funkcji.

**Niebezpieczne (szerokie)**: zmień topologię usług, zmodyfikuj limity zasobów, wdróż nowy kod, zmień uprawnienia, zmień bazy danych.

Każdy, kto sprzedaje „załóż i zapomnij”, sprzedaje za dużo. Bezpieczny zbiór rośnie w miarę dojrzewania AI SRE, ale granica jest realna.

### Ocena kontradyktoryjna (NeuBird Hawkeye)

Dwa modele niezależnie analizują to samo zdarzenie. Jeśli zgodzą się co do pierwotnej przyczyny, pewność jest wysoka. Jeśli się nie zgadzają, skieruj sprawę do człowieka z widocznymi obiema hipotezami. Prosty wzór, skuteczny filtr przeciwko pierwotnym przyczynom halucynacji.

### Pamięć operacyjna

Rotacja zespołu to cichy zabójca tradycyjnego SRE — liści wiedzy plemiennej. AI SRE przechowuje elementy Runbook i badania pośmiertne w wektorowej bazie danych; agenci pobierają informacje o każdym nowym zdarzeniu. Kiedy dołączają nowi inżynierowie, sztuczna inteligencja ma pełną historię.

### Przewidywanie przed incydentem

Badania MIT 2025: LLM przeszkolony w zakresie logów historycznych, temperatur GPU i wzorców błędów API przewidział 89% przestojów na 10–15 minut przed ich wystąpieniem na zestawie testowym.

Kontrola rzeczywistości: prognozy bez uruchomienia to pulpity nawigacyjne. Pytanie operacyjne brzmi: „co robimy, kiedy przewidujemy?” Drenaż zapobiegawczy? Pagera? Automatyczne skalowanie? Odpowiedź zależy od konkretnej polityki.

### Produkty w 2026 roku

- **Datadog Bits AI** — zarządzany drugi pilot SRE w Datadog.
- **Agent SRE platformy Azure** — natywny dla platformy Azure.
- **NeuBird Hawkeye** — ocena kontradyktoryjna + pamięć operacyjna.
- **PagerDuty AIOps** — segregacja + deduplikacja.
- **Incident.io Autopilot** — dowódca incydentu + koordynacja.

### Elementy Runbook jako kod

Elementy Runbook ewoluują od stron Confluence do wersji Markdown z ustrukturyzowanymi sekcjami (objaw, hipoteza, weryfikacja, działanie). Ustrukturyzowane elementy Runbook zapewniają lepsze pobieranie RAG. Rozpocznij wdrażanie AI-SRE, przekształcając nieustrukturyzowane elementy Runbook w ustrukturyzowane.

### Liczby, które powinieneś zapamiętać

- Wczesne wykrywanie MIT: 89% przestojów, czas realizacji 10-15 minut.
- Selekcja wieloagentowa: przełożony + (logi, metryki, elementy runbook) + człowiek.
- Bezpieczny zestaw automatycznej naprawy: uruchom ponownie kapsułę, przywróć wdrożenie, skaluj w granicach.
- Ocena kontradyktoryjna: dwa niezależne modele; zgoda = pewność.

## Użyj tego

`code/main.py` symuluje segregację wieloagentową: agent dziennika znajduje błąd, agent metryki znajduje skok wydajności procesora, agent elementu Runbook dopasowuje znany problem. Opiekun szereguje hipotezy.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-ai-sre-plan.md`. Biorąc pod uwagę aktualną liczbę dyżurów, liczbę incydentów i dojrzałość zespołu, projektuje wdrożenie AI SRE.

## Ćwiczenia

1. Uruchom `code/main.py`. Co się stanie, jeśli agenci dziennika i metryk nie będą się zgadzać? Jak rozwiązuje to przełożony?
2. Zdefiniuj trzy „bezpieczne” działania automatycznej naprawy dla swojej usługi. Uzasadnij każde.
3. Napisz ustrukturyzowany szablon elementu Runbook: sekcje, wymagane pola, polecenia weryfikacji.
4. Wykrywanie predykcyjne uruchamia się po 12 minutach wyprzedzenia. Jaka jest Twoja polityka — pager, wstępne opróżnianie, a może jedno i drugie?
5. Przedyskutuj, czy 3-osobowy zespół powinien wdrożyć AI SRE w 2026 roku, czy poczekać. Weź pod uwagę termin zapadalności, wolumen i ryzyko.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| AI SRE | „agent na wezwanie” | Badanie incydentów + koordynacja wspierane przez LLM |
| Agent nadzorczy | „Orkiestrator” | Agent najwyższego poziomu dzieli incydenty na podzapytania |
| Wyspecjalizowany agent | "agent domeny" | Subagent z dostępem do narzędzi (logi, metryki, runbooki) |
| Automatyczna naprawa | „AI to naprawia” | Wąskie, wstępnie zatwierdzone działanie; NIE szeroka rearchitektura |
| Pamięć operacyjna | „wektorowe elementy Runbook” | Sekcje zwłok + runbooki w wektorowym DB dla RAG |
| Ocena przeciwnika | „kontrola dwóch modeli” | Niezależne analizy; zgoda = pewność |
| NeuBird Hawkeye | „ten przeciwny” | Produkt z oceną kontradyktoryjną + wzorcem pamięci |
| Bity AI | „Agent SRE firmy Datadog” | AI SRE zarządzane przez Datadog |
| Przewidywanie przed incydentem | „wczesne wykrycie” | Czas realizacji 10-15 min w przypadku przewidywania przestojów |

## Dalsze czytanie

- [incident.io — Kompletny przewodnik AI SRE 2026](https://incident.io/blog/what-is-ai-sre-complete-guide-2026)
— [InfoQ — sztuczna inteligencja skupiona na człowieku dla SRE](https://www.infoq.com/news/2026/01/opsworker-ai-sre/)
– [DZone – AI w SRE 2026](https://dzone.com/articles/ai-in-sre-whats-actually-coming-in-2026)
- [Datadog Bits AI](https://www.datadoghq.com/product/bits-ai/)
- [NeuBird Hawkeye] (https://www.neubird.ai/)
- [awesome-ai-sre](https://github.com/agamm/awesome-ai-sre)