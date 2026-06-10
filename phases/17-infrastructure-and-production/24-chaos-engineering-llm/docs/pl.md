# Inżynieria chaosu dla produkcji LLM

> Inżynieria chaosu dla LLM będzie odrębną dyscypliną w roku 2026. Warunki wstępne przed rozpoczęciem eksperymentów w środowisku produkcyjnym: zdefiniowane SLI/SLO, obserwowalność śledzenia+metryki+logów, automatyczne wycofywanie zmian, elementy Runbook, dyżury. Architektura składa się z czterech płaszczyzn: kontrola (harmonogram eksperymentów), cel (usługi, infrastruktura, magazyny danych), bezpieczeństwo (ochrona + przerwanie + filtry ruchu), obserwowalność (metryki + ślady + logi), informacja zwrotna (do korekt SLO). Poręcze są obowiązkowe: alerty dotyczące współczynnika spalania wstrzymują eksperymenty, jeśli dzienne zużycie budżetu błędów przekracza oczekiwane > 2x; okna tłumienia + korelacja identyfikatora śledzenia, deduplikacja hałasu alertu. Kadencja: cotygodniowy mały kanarek + przegląd SLO; miesięczny dzień gry + sekcja zwłok; kwartalny audyt odporności między zespołami + mapowanie zależności. Eksperymenty specyficzne dla LLM: przeciążenie pamięci, awarie sieci, awarie dostawców, zniekształcone monity, burze eksmisji pamięci podręcznej KV. Oprzyrządowanie: Harness Chaos Engineering (zalecenia oparte na LLM, zmniejszanie promienia wybuchu, integracja narzędzi MCP); LitmusChaos (CNCF); Chaos Mesh (natywny dla CNCF Kubernetes).

**Typ:** Ucz się
**Języki:** Python (stdlib, narzędzie do eksperymentowania z chaosem zabawek)
**Wymagania wstępne:** Faza 17 · 23 (SRE dla AI), Faza 17 · 13 (obserwowalność)
**Czas:** ~60 minut

## Cele nauczania

- Wymień pięć wymagań wstępnych inżynierii chaosu (SLI/SLO, obserwowalność, wycofywanie zmian, elementy Runbook, dyżur) i wyjaśnij, dlaczego pomijanie jakichkolwiek przerw zakłóca praktykę.
- Naszkicuj cztery płaszczyzny (kontrola, cel, bezpieczeństwo, obserwowalność) i pętlę sprzężenia zwrotnego w SLO.
- Wymień pięć eksperymentów specyficznych dla LLM (przeciążenie pamięci, awaria sieci, awaria dostawcy, źle sformułowany monit, burza wyrzucająca KV).
- Wybierz narzędzie — Uprząż, LitmusChaos, Chaos Mesh — dany stos.

## Problem

Ustanowiono testowanie chaosu w tradycyjnych stosach. Stosy LLM dodają nowe tryby awarii. Podpowiedź dotycząca żetonu 4K ze znakiem trucizny zatrzymuje tokenizator na 12 sekund. Dostawca wyższego szczebla 429s; Twoja brama podejmuje ponowną próbę; OOM Twojej usługi w przypadku współbieżności ze wzmocnioną ponowną próbą. Burza wyrzucania pamięci podręcznej KV pod obciążeniem seryjnym powoduje kaskady ponownego wstępnego napełniania, które nasycają moc obliczeniową.

Żadne z nich nie pojawia się w testach jednostkowych. Inżynieria chaosu polega na tym, że odkrywasz je, zanim zrobią to użytkownicy.

## Koncepcja

### Warunki wstępne

Nie wprowadzaj chaosu na produkcję bez:

1. **SLI/SLO** — zdefiniowane wskaźniki i cele poziomu usług.
2. **Obserwowalność** — ślady, metryki, logi połączone z pulpitami nawigacyjnymi.
3. **Automatyczne wycofywanie** — Faza 17 · 20 wycofywanie flag zasad.
4. **Elementy Runbook** — ustrukturyzowane, faza 17 · 23.
5. **Na wezwanie** — ktoś, kto odpowie.

Pominięcie czegokolwiek oznacza, że ​​chaos staje się prawdziwym wydarzeniem.

### Cztery płaszczyzny + informacja zwrotna

**Płaszczyzna sterowania** — harmonogram eksperymentów (przepływ pracy Latmus, harmonogram Chaos Mesh, interfejs użytkownika Harness).

**Płaszczyzna docelowa** — usługi, pody, węzły, moduły równoważenia obciążenia, magazyny danych.

**Płaszczyzna bezpieczeństwa** — wyłącznik awaryjny, okna tłumienia, limity promienia wybuchu, bramki budżetowe błędów.

**Płaszczyzna obserwowalności** — normalne metryki + korelacja Trace-ID w celu odróżnienia awarii wywołanych chaosem od awarii naturalnych.

**Pętla informacji zwrotnej** — ustalenia są uwzględniane w dostosowaniu SLO, aktualizacjach elementów Runbook i poprawkach kodu.

### Poręcze są obowiązkowe

- **Alert dotyczący współczynnika spalania**: wstrzymaj eksperyment, jeśli dzienny budżet błędów przekroczy oczekiwaną wartość dwukrotnie.
- **Okna tłumienia**: wyciszają alerty niezwiązane z eksperymentem w promieniu wybuchu podczas eksperymentu.
- **Korelacja Trace-ID**: wszystkie błędy powstałe w wyniku eksperymentu mają znacznik, dzięki czemu można je deduplikować podczas rozmowy telefonicznej.

### Pięć eksperymentów specyficznych dla LLM

1. **Przeciążenie pamięci** — wymuś burzę wywłaszczania pamięci podręcznej KV poprzez wysyłanie żądań o długim kontekście z dużą współbieżnością. Zaobserwuj: czy usługa elegancko się zawiesza lub zawiesza?

2. **Awaria sieci** — przerwanie łączności pomiędzy bramą wnioskowania a dostawcą. Zwróć uwagę: czy w ramach umowy SLA włącza się rezerwa? (Faza 17 · 19)

3. **Symulacja awarii dostawcy** — 100% 429 z OpenAI. Zaobserwuj: czy routing jest przełączany awaryjnie do Anthropic? (Faza 17 · 16, 19)

4. **Zniekształcony monit** — wstrzyknij ładunek blokujący tokenizer (np. głęboko zagnieżdżony kod Unicode, ogromny punkt kodowy UTF-8). Zwróć uwagę: czy pojedyncze żądanie powoduje zamknięcie pracownika?

5. **Burza eksmisji KV** — wymuszenie eksmisji poprzez nasycenie budżetu bloku vLLM. Obserwuj: czy LMCache odzyskuje siły, czy też jakość usług ulega pogorszeniu?

### Kadencja

- **Co tydzień** — małe kanarkowe eksperymenty w inscenizacji, może 5% prod.
- **Miesięcznie** — zaplanowany dzień gry według określonego scenariusza; obecność między zespołami; sekcja zwłok.
- **Kwartalnie** – międzyzespołowy audyt odporności; aktualizacja mapy zależności.

### Oprzyrządowanie

- **Harness Chaos Engineering** – komercyjny; Zalecenia dotyczące eksperymentów oparte na sztucznej inteligencji; zmniejszanie promienia wybuchu; Integracja narzędzi MCP.
- **LitmusChaos** — absolwent CNCF; Kubernetes oparty na przepływie pracy.
- **Chaos Mesh** — piaskownica CNCF; Natywny styl CRD dla Kubernetes.
- **Gremlin** – komercyjny; szerokie wsparcie.
- **AWS FIS** / **Azure Chaos Studio** — oferty w chmurze zarządzanej.

### Zaczynam od małego

Pierwszy eksperyment: zabij poda jedną replikę dekodującą przy stałym ruchu. Obserwuj przekierowania i odzyskiwanie. Jeśli to działa i wygląda bezpiecznie, przejdź do chaosu sieciowego.

Pierwszy eksperyment specyficzny dla LLM: wstrzyknij jednego dostawcę 429 na 5 minut. Obserwuj powrót. Większość zespołów odkrywa, że ​​ich rozwiązanie awaryjne nie zostało w pełni przetestowane.

### Liczby, które powinieneś zapamiętać

- Cztery płaszczyzny: kontrola, cel, bezpieczeństwo, obserwowalność.
- Przerwa w spalaniu: 2x oczekiwane dzienne zużycie budżetu.
- Kadencja: cotygodniowy kanarek, miesięczny dzień gry, kwartalny audyt.
- Pięć eksperymentów LLM: pamięć, sieć, dostawca, zniekształcony monit, burza KV.

## Użyj tego

`code/main.py` symuluje trzy eksperymenty chaosu z bramkami samolotu bezpieczeństwa. Raporty, które eksperymenty spowodują przerwanie szybkości spalania.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-chaos-plan.md`. Biorąc pod uwagę stos i dojrzałość, wybiera pierwsze trzy eksperymenty i oprzyrządowanie.

## Ćwiczenia

1. Uruchom `code/main.py`. Który eksperyment uruchamia bramkę szybkości spalania i dlaczego?
2. Zaprojektuj pierwsze pięć eksperymentów z chaosem dla usługi RAG opartej na vLLM. Uwzględnij kryteria sukcesu.
3. Alert dotyczący szybkości spalania wstrzymał eksperyment. Jak określić pierwotną przyczynę – chaos czy naturalną?
4. Przedyskutuj, czy chaos powinien panować na etapie produkcji, czy tylko w fazie inscenizacji. Kiedy produkcja jest właściwą odpowiedzią?
5. Wymień trzy specyficzne dla LLM tryby awarii, których ogólny chaos sieciowy nie jest w stanie odtworzyć.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| SLI / SLO | „cele usług” | Wskaźnik + cel; wymagany warunek |
| Promień wybuchu | „zakres” | Zestaw usług/użytkowników objętych eksperymentem |
| Alarm szybkości spalania | „brama budżetowa” | Uruchamia się, gdy współczynnik wykorzystania budżetu błędów > 2x oczekiwany |
| Dzień gry | „miesięczne ćwiczenia” | Zaplanowane międzyzespołowe ćwiczenia chaosu |
| LakmusChaos | „Przebieg pracy CNCF” | Ukończone narzędzie chaosu CNCF Kubernetes |
| Siatka Chaosu | „CNCF CRD” | Sandbox CNCF Kubernetes – natywny chaos |
| Uprząż CE | „komercyjne wspomaganie sztucznej inteligencji” | Opanuj chaos dzięki rekomendacjom AI |
| Źle sformułowany monit | „bomba tokenizująca” | Dane wejściowe wstrzymujące tokenizację |
| Burza eksmisyjna KV | „kaskada wywłaszczania” | Masowe eksmisje powodujące ponowne napełnienie |

## Dalsze czytanie

- [Szkoła DevSecOps — Przewodnik Chaos Engineering 2026](https://devsecopsschool.com/blog/chaos-engineering/)
- [Ankush Sharma — Obserwowalność dla LLM (książka)](https://www.amazon.com/Observability-Large-Language-Models-Engineering-ebook/dp/B0DJSR65TR)
- [LitmusChaos (CNCF)](https://litmuschaos.io/)
- [Siatka chaosu (CNCF)](https://chaos-mesh.org/)
— [Harness Chaos Engineering](https://www.harness.io/products/chaos-engineering)
- [AWS FIS](https://aws.amazon.com/fis/)