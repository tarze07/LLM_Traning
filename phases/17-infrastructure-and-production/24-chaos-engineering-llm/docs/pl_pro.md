# Inżynieria chaosu w środowiskach produkcyjnych LLM

> Inżynieria chaosu w kontekście systemów LLM stanowi osobną, dojrzałą dyscyplinę. Warunki konieczne przed rozpoczęciem jakichkolwiek eksperymentów na produkcji obejmują: precyzyjnie zdefiniowane wskaźniki SLI/SLO, pełną obserwowalność (metryki, logi, rozproszony tracing), automatyczne wycofywanie zmian (rollbacks), ustrukturyzowane procedury runbook oraz aktywny system dyżurów inżynierskich (on-call). Architektura testów chaosu składa się z czterech warstw: kontrolnej (harmonogramowanie i orkiestracja), docelowej (usługi, infrastruktura, magazyny danych), bezpieczeństwa (wyłączniki awaryjne, filtry ruchu, ograniczanie promienia wybuchu) oraz obserwowalności (metryki, logi, ślady), z pętlą informacji zwrotnej służącą do korekty wskaźników SLO. Wdrożenie zabezpieczeń (guardrails) jest obligatoryjne: alerty o tempie wyczerpywania budżetu błędów (burn rate alerts) natychmiast przerywają testy, jeśli dzienne zużycie budżetu przekroczy zakładany poziom ponad dwukrotnie; kluczowe są także okna wyciszania alertów (suppression windows), korelacja identyfikatorów śledzenia (trace ID correlation) oraz mechanizmy deduplikacji szumu w powiadomieniach. Zalecany harmonogram: cotygodniowe małe testy typu canary i weryfikacja SLO; miesięczne warsztaty praktyczne (Game Days) wraz z analizą powdrożeniową (post-mortem); kwartalne audyty odporności systemów między zespołami połączone z mapowaniem zależności. Testy specyficzne dla LLM obejmują: przeciążenie pamięci podręcznej, awarie sieci, symulację awarii zewnętrznych dostawców API, wstrzykiwanie uszkodzonych promptów (prompt poisoning) oraz masowe czyszczenie pamięci podręcznej KV (KV cache eviction storms). Dostępne narzędzia: Harness Chaos Engineering (rekomendacje wspierane przez LLM, ograniczanie promienia wybuchu, wsparcie dla protokołu MCP), LitmusChaos (projekt CNCF) oraz Chaos Mesh (natywny dla Kubernetes, projekt CNCF).

**Typ:** Teoria / Nauka
**Języki:** Python (stdlib, narzędzie do eksperymentowania z chaosem zabawek)
**Wymagania wstępne:** Faza 17 · Lekcja 23 (SRE dla AI), Faza 17 · Lekcja 13 (obserwowalność)
**Czas:** ~60 minut

## Cele nauczania

- Wymień pięć warunków wstępnych wdrożenia inżynierii chaosu (SLI/SLO, obserwowalność, automatyczne wycofywanie, procedury runbook, dyżury) i wyjaśnij, dlaczego pominięcie któregokolwiek z nich uniemożliwia bezpieczne prowadzenie testów.
- Przedstaw cztery warstwy architektury chaosu (kontrolną, docelową, bezpieczeństwa, obserwowalności) oraz rolę pętli sprzężenia zwrotnego w optymalizacji SLO.
- Opisz pięć scenariuszy testowych specyficznych dla LLM (przeciążenie pamięci, awaria łączności sieciowej, awaria dostawcy API, uszkodzony prompt, gwałtowne usuwanie bloków pamięci KV cache).
- Dobierz odpowiednie narzędzie (Harness, LitmusChaos, Chaos Mesh) do określonego stosu technologicznego.

## Problem

Testowanie chaosu w tradycyjnych systemach jest już dobrze znaną praktyką. Jednak architektury oparte na LLM wprowadzają zupełnie nowe, specyficzne tryby awarii. Na przykład szkodliwy prompt wejściowy o długości 4K tokenów może zablokować tokenizer na kilkanaście sekund. Z kolei błąd 429 (Rate Limit Exceeded) u zewnętrznego dostawcy powoduje, że bramka (gateway) zaczyna ponawiać zapytania; przy wysokiej współbieżności i nakładających się próbach ponowienia usługa ulega awarii z powodu braku pamięci (OOM). Dodatkowo, gwałtowne czyszczenie pamięci podręcznej KV (KV cache eviction storm) pod nagłym obciążeniem wywołuje kaskadowe procesy ponownego obliczania (pre-filling), które całkowicie nasycają dostępną moc obliczeniową układów GPU.

Żaden z tych problemów nie wyjdzie na jaw w trakcie klasycznych testów jednostkowych. Istotą inżynierii chaosu jest wykrycie tych ryzyk operacyjnych, zanim zderzą się z nimi użytkownicy końcowi.

## Koncepcja

### Warunki wstępne

Nie wprowadzaj chaosu do środowiska produkcyjnego bez spełnienia poniższych warunków:

1. **SLI/SLO** – precyzyjnie zdefiniowane wskaźniki i cele poziomu usług.
2. **Obserwowalność** – metryki, logi i rozproszone ślady (traces) zagregowane w spójne panele kontrolne (dashboards).
3. **Automatyczne wycofywanie (rollbacks)** – mechanizmy automatycznego wycofywania zmian lub konfiguracji (Faza 17 · Lekcja 20).
4. **Procedury runbook** – ustrukturyzowana i sprawdzona dokumentacja operacyjna (Faza 17 · Lekcja 23).
5. **System dyżurów (on-call)** – inżynier pełniący dyżur, gotowy do natychmiastowej reakcji.

Zignorowanie któregokolwiek z tych punktów sprawia, że testy chaosu przerodzą się w rzeczywistą i niekontrolowaną awarię.

### Cztery warstwy architektury + pętla informacji zwrotnej

**Warstwa kontrolna (Control Plane)** – orkiestracja i harmonogramowanie testów (np. workflow w LitmusChaos, harmonogramy w Chaos Mesh, interfejs Harness).

**Warstwa docelowa (Target Plane)** – infrastruktura poddawana testom: usługi, kontenery (pody), węzły, load balancery, bazy danych.

**Warstwa bezpieczeństwa (Safety Plane)** – wyłączniki awaryjne (kill switches), okna wyciszania alertów, limity promienia wybuchu (blast radius limits) oraz bramki budżetu błędów.

**Warstwa obserwowalności (Observability Plane)** – standardowy monitoring oraz korelacja po ID śladu (Trace ID correlation) służąca do jednoznacznego odróżnienia skutków celowej symulacji od rzeczywistych, niezależnych awarii.

**Pętla informacji zwrotnej (Feedback Loop)** – wnioski z testów przekładają się bezpośrednio na rewizję wskaźników SLO, aktualizację procedur runbook oraz poprawki w kodzie aplikacji.

### Zabezpieczenia są obowiązkowe

- **Alert o tempie wyczerpywania budżetu (burn rate alert)**: natychmiast wstrzymaj eksperyment, jeśli zużycie budżetu błędów w skali dnia przekroczy zakładaną normę ponad dwukrotnie.
- **Okna wyciszania (suppression windows)**: tłumienie nieistotnych alertów pochodzących z obszaru objętego eksperymentem na czas jego trwania.
- **Korelacja Trace ID**: automatyczne tagowanie błędów wywołanych testem chaosu, ułatwiające ich deduplikację i odróżnienie w trakcie analizy.

### Pięć testów specyficznych dla LLM

1. **Przeciążenie pamięci**: wywołanie gwałtownego czyszczenia pamięci podręcznej KV poprzez wysyłanie zapytań o bardzo długim kontekście przy wysokiej współbieżności. Obserwuj: czy usługa bezpiecznie degraduje swoją wydajność, czy też całkowicie zawiesza działanie kontenerów?
2. **Awaria sieci**: przerwanie łączności między bramą wnioskowania a dostawcą API. Zweryfikuj: czy mechanizm rezerwowy (fallback) uruchamia się zgodnie z SLA? (Faza 17 · Lekcja 19)
3. **Symulacja awarii dostawcy**: zasymulowanie otrzymywania wyłącznie błędów 429 z API OpenAI. Obserwuj: czy routing automatycznie przełącza się na model rezerwowy (np. Anthropic)? (Faza 17 · Lekcje 16, 19)
4. **Szkodliwy prompt**: wstrzyknij treść, która może zawiesić lub zablokować tokenizer (np. głęboko zagnieżdżone znaki Unicode, błędne sekwencje UTF-8). Zweryfikuj: czy pojedyncze zapytanie doprowadzi do awarii całego procesu roboczego (worker crash)?
5. **KV Cache Eviction Storm**: wymuszenie gwałtownego zwalniania pamięci podręcznej poprzez nasycenie pamięci przydzielonej dla vLLM. Obserwuj: czy mechanizm LMCache poprawnie przywraca stan systemu, czy też następuje trwała degradacja wydajności?

### Harmonogram i częstotliwość

- **Co tydzień**: uruchamianie niewielkich testów w środowisku stagingowym (staging), ewentualnie na bardzo ograniczonym ruchu produkcyjnym (np. 5%).
- **Co miesiąc**: zaplanowany dzień praktycznych ćwiczeń (Game Day) według określonego scenariusza z udziałem różnych zespołów, zakończony sporządzeniem raportu poawaryjnego (post-mortem).
- **Co kwartał**: międzyzespołowy audyt odporności systemów oraz aktualizacja mapy zależności.

### Dostępne narzędzia

- **Harness Chaos Engineering**: rozwiązanie komercyjne; oferuje rekomendacje testów oparte na AI, automatyczne ograniczanie promienia wybuchu oraz integrację z protokołem MCP.
- **LitmusChaos**: dojrzały projekt CNCF; orkiestracja testów w Kubernetes oparta na workflowach.
- **Chaos Mesh**: projekt w inkubatorze CNCF; natywny dla Kubernetes, zarządzany za pomocą obiektów CRD.
- **Gremlin**: rozwiązanie komercyjne z bogatym wsparciem technicznym.
- **AWS FIS / Azure Chaos Studio**: dedykowane usługi zarządzane w chmurach publicznych.

### Metoda małych kroków

Pierwszy eksperyment: usuń (zabij) pojedynczy kontener (pod) z instancją dekodującą przy stałym natężeniu ruchu. Obserwuj proces przekierowywania żądań i powrotu do pełnej sprawności. Jeśli system zachowa się stabilnie, przejdź do symulacji zakłóceń sieciowych.

Pierwszy eksperyment specyficzny dla LLM: zasymuluj zwracanie błędu 429 przez zewnętrznego dostawcę przez 5 minut. Obserwuj zachowanie systemu. Wiele zespołów dopiero na tym etapie odkrywa, że ich mechanizm failover nie działa w pełni poprawnie pod obciążeniem.

### Kluczowe dane do zapamiętania

- Cztery warstwy architektury: kontrolna, docelowa, bezpieczeństwa, obserwowalności.
- Próg awaryjny (burn rate): zużycie budżetu błędów przekraczające 2x oczekiwaną normę dzienną.
- Harmonogram: cotygodniowy kanarek, miesięczny Game Day, kwartalny audyt.
- Pięć testów LLM: przeciążenie pamięci, błędy sieci, awaria dostawcy API, szkodliwy prompt, czyszczenie pamięci podręcznej KV.

## Kod demonstracyjny

Skrypt `code/main.py` symuluje trzy testy chaosu kontrolowane przez automatyczne mechanizmy warstwy bezpieczeństwa. Raportuje, które z eksperymentów doprowadzą do przekroczenia dozwolonego wskaźnika burn rate i zostaną przerwane.

## Rezultat zadania

W ramach tej lekcji powstanie plik `outputs/skill-chaos-plan.md`. Na podstawie struktury stosu technologicznego oraz dojrzałości operacyjnej zespołu dobierane są pierwsze trzy eksperymenty oraz odpowiednie narzędzia.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Który z eksperymentów aktywuje wyłącznik bezpieczeństwa z powodu wskaźnika burn rate i dlaczego?
2. Zaprojektuj zestaw pierwszych pięciu eksperymentów chaosu dla usługi RAG opierającej się na silniku vLLM. Zdefiniuj wskaźniki sukcesu każdego testu.
3. Wyzwolenie alertu burn rate wstrzymało eksperyment. W jaki sposób ustalisz, czy przyczyną była celowa symulacja chaosu, czy rzeczywista, niezależna awaria systemu?
4. Rozważ, czy testy chaosu powinny być wykonywane bezpośrednio w środowisku produkcyjnym, czy wyłącznie na stagingu. Kiedy i pod jakimi warunkami prowadzenie ich na produkcji jest uzasadnione?
5. Wymień trzy specyficzne dla LLM tryby awarii, których nie da się zasymulować przy użyciu prostego generowania zakłóceń sieciowych.

## Słownik pojęć

| Termin | Jak się potocznie mówi | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| SLI / SLO | „cele wydajnościowe” | Mierzalny wskaźnik oraz cel poziomu usług; absolutny wymóg przed testami |
| Promień wybuchu (Blast radius) | „zasięg awarii” | Zbiór usług, węzłów lub użytkowników dotkniętych bezpośrednio przez test |
| Alert burn rate | „bezpiecznik budżetowy” | Alarm aktywowany, gdy tempo wyczerpywania budżetu błędów przekracza 2x oczekiwaną normę |
| Game Day | „ćwiczenia z awarii” | Wspólny, zaplanowany trening zespołów inżynieryjnych symulujący awarie na żywo |
| LitmusChaos | „narzędzie CNCF do chaosu” | Zaakceptowany i dojrzały projekt CNCF do testów odporności w Kubernetes |
| Chaos Mesh | „chaos przez CRD” | Projekt w inkubatorze CNCF oferujący natywne mechanizmy chaosu w Kubernetes |
| Harness CE | „komercyjny chaos z AI” | Platforma wspierana przez AI, ułatwiająca dobór testów i kontrolę bezpieczeństwa |
| Uszkodzony prompt | „bomba w prompcie” | Specjalnie spreparowane zapytanie, które potrafi zablokować lub zawiesić tokenizer |
| KV Cache Eviction Storm | „kaskada wywłaszczania KV” | Zjawisko masowego usuwania danych z pamięci podręcznej KV, powodujące narzut obliczeniowy przy ponownych zapytaniach |

## Materiały uzupełniające

- [Szkoła DevSecOps — Przewodnik Chaos Engineering 2026](https://devsecopsschool.com/blog/chaos-engineering/)
- [Ankush Sharma — Obserwowalność dla LLM (książka)](https://www.amazon.com/Observability-Large-Language-Models-Engineering-ebook/dp/B0DJSR65TR)
- [LitmusChaos (CNCF)](https://litmuschaos.io/)
- [Chaos Mesh (CNCF)](https://chaos-mesh.org/)
- [Harness Chaos Engineering](https://www.harness.io/products/chaos-engineering)
- [AWS FIS](https://aws.amazon.com/fis/)
