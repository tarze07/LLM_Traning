# SRE dla AI — wieloagentowa reakcja na incydenty, procedury runbook i predykcyjne wykrywanie awarii

> Systemy AI SRE wykorzystują modele LLM zasilane danymi o infrastrukturze (logami, procedurami runbook, topologią usług) za pomocą mechanizmu RAG, aby automatyzować etapy analizy, dokumentacji i koordynacji incydentów. Standardowym wzorcem architektury w 2026 roku staje się orkiestracja wieloagentowa – wyspecjalizowani agenci (analizujący logi, metryki czy procedury runbook) są koordynowani przez agenta nadrzędnego (supervisor). Sztuczna inteligencja proponuje hipotezy i formułuje wnioski, natomiast ostateczne zatwierdzenie planu naprawczego leży w rękach człowieka. Narzędzia takie jak Datadog Bits AI czy Azure SRE Agent oferują tę funkcjonalność jako gotowe usługi zarządzane. Procedury runbook również ewoluują: na przykład NeuBird Hawkeye wykorzystuje ewaluację kontradyktoryjną (dwa niezależne modele analizują ten sam incydent – zgodność oznacza wysoką pewność diagnozy, a rozbieżność sygnalizuje niepewność); w ten sposób wiedza operacyjna pozostaje w organizacji niezależnie od rotacji pracowników. Automatyczna naprawa (auto-remediation) nadal jest stosowana ostrożnie: AI proponuje rozwiązania, a człowiek je akceptuje. W pełni autonomiczne działania są ograniczone do wąskiego zakresu (restart kontenera, wycofanie konkretnego wdrożenia) i obwarowane rygorystycznymi zabezpieczeniami – obietnice całkowicie bezobsługowych systemów ("ustaw i zapomnij") są obecnie mocno przesadzone. Nowym kierunkiem rozwoju jest predykcyjne wykrywanie awarii. Badania MIT wykazują, że modele LLM trenowane na historycznych logach, temperaturach układów GPU i wzorcach błędów API potrafią przewidzieć 89% przestojów z wyprzedzeniem 10–15 minut. Prognozuje się, że do końca 2026 roku 95% systemów LLM w przedsiębiorstwach będzie korzystać z automatycznego przełączania awaryjnego (failover).

**Typ:** Teoria / Nauka
**Języki:** Python (stdlib, zabawkowy wieloagentowy symulator selekcji incydentów)
**Wymagania wstępne:** Faza 17 · Lekcja 13 (Obserwowalność), Faza 17 · Lekcja 24 (Inżynieria Chaosu)
**Czas:** ~60 minut

## Cele nauczania

- Przedstaw schemat wieloagentowej architektury AI SRE: nadzorca (supervisor) + agenci dziedzinowi (logi, metryki, procedury runbook) + bramka zatwierdzania przez człowieka (human-in-the-loop).
- Wyjaśnij, dlaczego automatyczne naprawianie awarii ma wąski zakres (np. restart kontenera, wycofanie wdrożenia), a nie szeroki (np. przebudowa architektury usług).
- Opisz wzorzec ewaluacji kontradyktoryjnej (adversarial evaluation, np. NeuBird Hawkeye): zgodność dwóch modeli oznacza wysoką pewność; rozbieżność oznacza konieczność eskalacji do człowieka.
- Przywołaj wynik wczesnego wykrywania MIT na poziomie 89% i wskaż ograniczenie operacyjne: same prognozy, za którymi nie idą działania, to jedynie kolejne wykresy w panelu monitoringu.

## Problem

O godzinie 3:00 nad ranem inżynier pełniący dyżur otrzymuje powiadomienie o błędzie: „Wysoki poziom błędów przy kasie (checkout error rate)”. Sprawdza kolejno narzędzia Datadog i Loki, analizuje trzy procedury runbook oraz logi wdrożeń. Dopiero po 30 minutach orientuje się, że przyczyną awarii jest błąd braku pamięci (OOM) w vLLM, wywołany nagłym wzrostem rozmiaru pamięci podręcznej KV (KV cache). Restartuje kontener i problem znika.

W 2026 roku pierwsze 20 minut takiego dochodzenia można w pełni zautomatyzować. Agregowanie logów według usług, powiązanie ich z ostatnimi wdrożeniami oraz dopasowywanie do procedur runbook – wszystko to realizowane jest za pomocą mechanizmów RAG i dedykowanych narzędzi. Agent nadzorujący może dokonać wstępnej analizy i sformułować trafną hipotezę, zanim inżynier w ogóle otworzy panel Datadog.

W definiowaniu automatycznych środków zaradczych kryje się jednak inne wyzwanie. Restart kontenera (podu): bezpieczny. Skalowanie puli GPU: bezpieczne, o ile pozwalają na to zdefiniowane limity. Przebudowa architektury usługi: absolutnie niedopuszczalna. Kluczem jest wytyczenie bardzo precyzyjnej granicy.

## Koncepcja

### Architektura wieloagentowa

```
          Incydent
             │
             ▼
         Nadzorca (Supervisor)
        /    |    \
       ▼     ▼     ▼
 Agent logów   Agent metryk   Agent runbooków
       │     │     │
       └─────┴─────┘
             │
             ▼
     Hipoteza + dowody
             │
             ▼
 Zatwierdzenie przez człowieka
             │
             ▼
  Działanie (wąski zakres)
```

Nadzorca dzieli incydent na mniejsze zapytania. Wyspecjalizowani agenci mają dostęp do narzędzi diagnostycznych (przeszukiwanie logów, zapytania PromQL, wyszukiwanie w dokumentacji). Nadzorca syntetyzuje zebrane informacje, a następnie przedstawia hipotezę wraz z dowodami człowiekowi. Inżynier zatwierdza proponowane akcje lub przejmuje kontrolę.

### Zakres automatycznej naprawy

**Bezpieczne (wąski zakres)**: restart kontenera (podu), wycofanie (rollback) konkretnego wdrożenia, skalowanie puli zasobów w zdefiniowanych granicach, aktywacja zatwierdzonej flagi funkcji (feature flag).

**Niebezpieczne (szeroki zakres)**: zmiana topologii usług, modyfikacja limitów zasobów, wdrożenie nowego kodu, zmiana uprawnień (IAM), modyfikacja schematu bazy danych.

Oferty obiecujące całkowicie bezobsługowe działanie są nierealistyczne. Zbiór bezpiecznych operacji będzie rósł wraz z rozwojem systemów AI SRE, ale granica bezpieczeństwa pozostaje nienaruszalna.

### Ewaluacja kontradyktoryjna (NeuBird Hawkeye)

Dwa modele niezależnie analizują ten sam incydent. Jeśli ich wnioski co do głównej przyczyny (root cause) są zgodne, poziom pewności jest wysoki. W przypadku rozbieżności, sprawa trafia do człowieka z prezentacją obu hipotez. To prosty, ale bardzo skuteczny filtr zapobiegający halucynowaniu przyczyn awarii.

### Pamięć operacyjna

Rotacja pracowników to cichy zabójca w tradycyjnych zespołach SRE – wraz z ludźmi odchodzi wiedza i doświadczenie zespołu (knowledge drain). AI SRE przechowuje procedury runbook oraz raporty z awarii (post-mortems) w wektorowej bazie danych. Przy każdym nowym incydencie agenci przeszukują te zasoby, dzięki czemu nowi inżynierowie mają od razu dostęp do pełnej historii operacyjnej.

### Predykcyjne wykrywanie awarii

Badanie przeprowadzone przez MIT w 2025 roku wykazało, że model LLM wytrenowany na historycznych logach, temperaturach procesorów GPU oraz wzorcach błędów API był w stanie przewidzieć 89% awarii na 10-15 minut przed ich wystąpieniem.

Zderzenie z rzeczywistością: same prognozy, za którymi nie idą automatyczne działania, stają się tylko kolejnymi wykresami. Kluczowe pytanie brzmi: co robimy po wykryciu zagrożenia awarią? Czy uruchamiamy prewencyjne przekierowanie ruchu (preemptive draining)? Wysyłamy alert? Uruchamiamy autoskalowanie? Decyzja zależy od przyjętej polityki operacyjnej.

### Narzędzia dostępne w 2026 roku

- **Datadog Bits AI** – zarządzany asystent (copilot) SRE zintegrowany z Datadog.
- **Azure SRE Agent** – natywne narzędzie dla chmury Azure.
- **NeuBird Hawkeye** – ewaluacja kontradyktoryjna i pamięć operacyjna.
- **PagerDuty AIOps** – automatyczna klasyfikacja (triage) i deduplikacja alertów.
- **Incident.io Autopilot** – koordynacja i zarządzanie przebiegiem incydentów.

### Procedury runbook jako kod

Dokumentacja procedur runbook ewoluuje z tradycyjnych stron w Confluence do formatu Markdown o ustrukturyzowanej formie (objawy, hipoteza, weryfikacja, akcja). Taka struktura ułatwia przeszukiwanie baz za pomocą RAG. Wdrażanie systemów AI SRE warto rozpocząć właśnie od uporządkowania i standaryzacji istniejących procedur.

### Kluczowe dane do zapamiętania

- Wczesne wykrywanie (MIT): 89% awarii wykrywanych z 10-15 minutowym wyprzedzeniem.
- Klasyfikacja wieloagentowa: nadzorca + agenci dziedzinowi (logi, metryki, procedury runbook) + człowiek.
- Bezpieczne akcje automatycznej naprawy: restart kontenera (podu), przywrócenie poprzedniej wersji wdrożenia, skalowanie w zdefiniowanych limitach.
- Ewaluacja kontradyktoryjna: dwa niezależne modele; zgodność = wysoka pewność.

## Kod demonstracyjny

Skrypt `code/main.py` symuluje automatyczną klasyfikację wieloagentową: agent logów wykrywa błąd, agent metryk identyfikuje skok obciążenia procesora, a agent procedur runbook dopasowuje zdarzenie do znanej procedury naprawczej. Nadzorca koordynuje proces i przedstawia spójną hipotezę.

## Rezultat zadania

W ramach tej lekcji powstanie plik `outputs/skill-ai-sre-plan.md`. Na podstawie bieżącego obciążenia dyżurami, częstotliwości incydentów oraz stopnia dojrzałości zespołu projektowane jest wdrożenie systemu AI SRE.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Co się stanie, jeśli agent logów i agent metryk wysuną rozbieżne wnioski? W jaki sposób nadzorca rozwiąże ten konflikt?
2. Zdefiniuj trzy „bezpieczne” akcje automatycznej naprawy (auto-remediation) dla swojej usługi. Uzasadnij wybór każdej z nich.
3. Przygotuj ustrukturyzowany szablon procedury runbook: określ wymagane sekcje, pola oraz polecenia weryfikacyjne.
4. Algorytm predykcyjny sygnalizuje awarię z 12-minutowym wyprzedzeniem. Jaka powinna być reakcja systemu – wysłanie alertu, prewencyjne przekierowanie ruchu, czy obie te akcje jednocześnie?
5. Rozważ, czy 3-osobowy zespół powinien wdrażać rozwiązania AI SRE już w 2026 roku, czy lepiej z tym poczekać. Weź pod uwagę dojrzałość technologii, liczbę obsługiwanych incydentów oraz potencjalne ryzyko.

## Słownik pojęć

| Termin | Jak się potocznie mówi | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| AI SRE | „agent na dyżurze” | Analiza incydentów i koordynacja działań wspierana przez LLM |
| Agent nadzorczy (Supervisor) | „orkiestrator” | Agent nadrzędny, który dzieli badanie incydentu na mniejsze podzadania |
| Agent dziedzinowy | „agent domeny” | Podagent posiadający dostęp do konkretnych narzędzi (logów, metryk, procedur runbook) |
| Automatyczna naprawa (Auto-remediation) | „AI samo naprawi błąd” | Wykonanie wąskiej, z góry zatwierdzonej procedury; nie oznacza to automatycznej przebudowy kodu/infrastruktury |
| Pamięć operacyjna | „runbooki w bazie wektorowej” | Baza wiedzy zawierająca raporty poawaryjne (post-mortems) oraz procedury runbook podłączone do RAG |
| Ewaluacja kontradyktoryjna | „kontrola dwóch modeli” | Niezależna analiza incydentu przez dwa modele; zgodność wniosków = wysoka pewność |
| NeuBird Hawkeye | „narzędzie kontradyktoryjne” | Gotowy produkt wykorzystujący ewaluację kontradyktoryjną i pamięć operacyjną |
| Bits AI | „agent SRE od Datadoga” | Rozwiązanie klasy AI SRE wbudowane i zarządzane w ramach platformy Datadog |
| Predykcyjne wykrywanie awarii | „wczesne ostrzeganie” | Wykrywanie anomalii zwiastujących awarię z 10-15 minutowym wyprzedzeniem |

## Materiały uzupełniające

- [incident.io — Kompletny przewodnik AI SRE 2026](https://incident.io/blog/what-is-ai-sre-complete-guide-2026)
- [InfoQ — sztuczna inteligencja skupiona na człowieku dla SRE](https://www.infoq.com/news/2026/01/opsworker-ai-sre/)
- [DZone – AI w SRE 2026](https://dzone.com/articles/ai-in-sre-whats-actually-coming-in-2026)
- [Datadog Bits AI](https://www.datadoghq.com/product/bits-ai/)
- [NeuBird Hawkeye](https://www.neubird.ai/)
- [awesome-ai-sre](https://github.com/agamm/awesome-ai-sre)
