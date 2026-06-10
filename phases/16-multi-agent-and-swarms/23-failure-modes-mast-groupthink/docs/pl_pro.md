# Tryby awarii – MAST, myślenie grupowe, monokultura i błędy kaskadowe

> Standardem referencyjnym w 2026 roku jest taksonomia **MAST** (Cemri i in., NeurIPS 2025, arXiv:2503.13657), opracowana na podstawie analizy 1642 śladów wykonania w 7 najnowocześniejszych systemach wieloagentowych (MAS) typu open source, wykazująca **wskaźnik awaryjności na poziomie 41–86,7%**. Definiuje ona trzy główne kategorie błędów: **Problemy ze specyfikacją** (41,77%) – np. niejednoznaczność ról, niejasne definicje zadań; **Błędy koordynacji** (36,94%) – np. problemy z komunikacją, brak synchronizacji stanu; **Luki w weryfikacji** (21,30%) – np. brak walidacji wyników pośrednich, brak kontroli jakości. Publikacja dotycząca zjawiska **myślenia grupowego (Groupthink)** (arXiv:2508.05687) uzupełnia tę listę o: kryzys monokultury (użycie tego samego modelu bazowego prowadzi do skorelowanych błędów), błąd konformizmu (agenci wzmacniają nawzajem swoje pomyłki), wadliwą Teorię Umysłu, dynamikę o motywach mieszanych oraz kaskadowe awarie niezawodności. Przykładem awarii kaskadowej jest „burza ponownych prób” (retry storm), w której jednostkowy błąd bramki płatniczej wywołuje lawinę ponowień weryfikacji koszyka i stanów magazynowych, przeciążając bazę danych (dziesięciokrotny wzrost ruchu w ciągu kilku sekund – problem wymagający wdrożenia wyłączników/circuit breakers). Innym zagrożeniem jest skażenie pamięci: halucynacja jednego agenta trafia do pamięci współdzielonej, a kolejni agenci traktują ją jako fakt; prowadzi to do stopniowego, trudnego do zdiagnozowania spadku dokładności całego systemu. Framework **STRATUS** (NeurIPS 2025) raportuje 1,5-krotną poprawę wskaźnika sukcesu dzięki wdrożeniu dedykowanych agentów do detekcji, diagnostyki i walidacji błędów. W tej lekcji podejdziemy do trybów awarii jako do kluczowych założeń projektowych.

**Typ:** Ucz się
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 13 (pamięć współdzielona), faza 16 · 14 (konsensus i BFT), faza 16 · 15 (topologia głosowania i debaty)
**Czas:** ~75 minut

## Problem

Systemy wieloagentowe w realnych zadaniach produkcyjnych zawodzą w 41–86,7% przypadków (co wykazali Cemri i in., 2025 na bazie 7 projektów MAS typu open source). Problemów tych nie da się rozwiązać prostym podejściem typu „dodajmy kolejnych agentów”. Awarie te wynikają z przyczyn strukturalnych. Taksonomia MAST definiuje ich kategorie. W tej lekcji powiążemy każdą z tych kategorii z konkretnymi wzorcami detekcji, diagnostyki i przeciwdziałania błędom.

Praktyka inżynieryjna w 2026 roku wymaga traktowania trybów awarii jako kluczowych założeń na etapie projektowania systemu. Architektura nie może zostać uznana za gotową produkcyjnie, dopóki nie potrafisz wskazać dla każdej kategorii MAST konkretnych, wdrożonych zabezpieczeń.

## Koncepcja

### Kategorie błędów według taksonomii MAST

**Problemy ze specyfikacją (Specification Issues - 41,77% awarii):** brak precyzyjnego zdefiniowania celów lub granic odpowiedzialności agentów. Przykłady:

- **Niejednoznaczność ról:** dwaj agenci błędnie zakładają, że pełnią tę samą funkcję (np. obaj próbują recenzować kod).
- **Niedoprecyzowanie zadania:** polecenie brzmi „podsumuj artykuł”, podczas gdy użytkownik oczekiwał analizy pod konkretnym kątem.
- **Niejawne kryteria sukcesu:** agent nie dysponuje narzędziami do jednoznacznej oceny, czy poprawnie zakończył zadanie.

Środki zaradcze:
- Tworzenie jednoznacznych reguł odpowiedzialności. Systemowy prompt każdego agenta powinien precyzyjnie definiować jego zakres obowiązków oraz ograniczenia (czym się *nie* zajmuje).
- Definiowanie kryteriów akceptacji (Acceptance Criteria). Przed zleceniem zadania określ format docelowy („definicja ukończenia / definition of done”).
- Wdrożenie weryfikacji wstępnej (pre-flight checks): osobny agent dokonuje analizy poprawności sformułowania zadania przed jego uruchomieniem.

**Błędy koordynacji (Coordination Errors - 36,94% awarii):** problemy z przepływem informacji lub synchronizacją stanu. Przykłady:

- Jednoczesna modyfikacja współdzielonego stanu przez dwóch agentów bez mechanizmów blokad.
- Utrata komunikatów sieciowych (błędy kolejki, przekroczenia limitów czasu/timeouts).
- Rozbieżność stanów (state drift): agent A zakłada, że zadanie dobiegło końca, podczas gdy agent B kontynuuje jego realizację.

Środki zaradcze:
- Wdrożenie wersjonowania stanu współdzielonego z obsługą blokad optymistycznych (optimistic concurrency control).
- Wymóg jawnego potwierdzania odbioru kluczowych komunikatów (mechanizm ponowień do momentu uzyskania potwierdzenia).
- Cykliczna synchronizacja stanów z punktami kontrolnymi w celu wczesnego wykrywania anomalii.

**Luki w weryfikacji (Verification Gaps - 21,30% awarii):** brak niezależnej ewaluacji poprawności wyników. Przykłady:

- Akceptowanie raportu agenta o sukcesie bez zewnętrznej weryfikacji.
- Bezrefleksyjne ufanie wynikom dostarczonym przez poprzedniego agenta w potoku przetwarzania.
- Brak pokrycia testowego dla złożonych, emergentnych interakcji.

Środki zaradcze:
- Wykorzystywanie niezależnych agentów oceniających (lekcja 13) działających w trybie tylko do odczytu, z bezpośrednim dostępem do źródeł danych.
- Jawne definiowanie warunków przejścia (handover contracts): „wyjście z modułu A musi zostać pomyślnie zweryfikowane przez moduł C, zanim zostanie przekazane do modułu B”.
- Logowanie kompletnych danych wyjściowych na potrzeby późniejszych analiz (post-mortem).

### Zagrożenia związane z myśleniem grupowym (Groupthink)

Wyróżnia się pięć powiązanych ze sobą trybów awarii występujących w sytuacjach, gdy agenci upodabniają swoje zachowania:

- **Monokultura:** wykorzystanie tego samego modelu bazowego lub tych samych danych treningowych skutkuje skorelowanymi błędami. Gdy grupa agentów odpytuje ten sam model LLM, powielają oni te same halucynacje.
- **Błąd konformizmu (conformity bias):** agenci dostosowują swoje decyzje do opinii agenta o najwyższym poziomie pewności (confidence score) podawanej w odpowiedzi, nawet jeśli jest ona błędna.
- **Niedostateczne modelowanie stanów wiedzy (insufficient ToM):** brak wdrożenia Teorii Umysłu powoduje rozbieżności w ocenie intencji i załamanie koordynacji (lekcja 18).
- **Konflikt interesów (mixed-motive dynamics):** agenci o częściowo sprzecznych celach wypracowują zgniły kompromis, który nie realizuje poprawnie żadnego z założeń projektowych.
- **Kaskadowe awarie niezawodności:** błędy w jednym komponencie wywołują lawinowe awarie w elementach zależnych.

### Przykład awarii kaskadowej: Burza ponownych prób (Retry Storm)

Klasyczny schemat awarii systemów produkcyjnych w 2026 roku:

```
Błąd API płatności (10% zapytań kończy się błędem)
   ↓
Agent obsługi zamówień ponawia płatność (naiwne ponowienia)
   ↓
Każde ponowienie generuje nowe zapytanie o stan magazynowy
   ↓
Usługa magazynowa odnotowuje dwukrotny wzrost ruchu
   ↓
Usługa magazynowa zaczyna zgłaszać timeouts (przekroczenia czasu)
   ↓
Wszystkie zamówienia zaczynają ponawiać próby sprawdzenia magazynu
   ↓
Usługa magazynowa odnotowuje dziesięciokrotny wzrost obciążenia
   ↓
Cały klaster usług ulega awarii
```

Rozwiązaniem tego problemu jest klasyczny wzorzec z systemów rozproszonych: **wyłącznik (circuit breaker)**. Gdy wskaźnik błędów w zewnętrznej usłudze przekroczy próg, wyłącznik przerywa dalsze próby połączeń i natychmiast zwraca wynik domyślny lub dane z pamięci podręcznej (cache). Należy również wdrożyć limity budżetów ponownych prób (retry budgets) dla poszczególnych żądań. Wyłączniki to jedne z nielicznych narzędzi stabilizacyjnych, które można przenieść bezpośrednio z klasycznej inżynierii systemów rozproszonych do systemów wieloagentowych bez żadnych zmian.

### Skażenie pamięci (Memory Poisoning)

Zjawisko omówione w Lekcji 13: halucynacja jednego agenta zostaje zapisana w pamięci współdzielonej, a kolejni agenci traktują ją jako bezsporny fakt. Z perspektywy taksonomii MAST jest to klasyczna luka w weryfikacji danych na poziomie warstwy pamięci.

Głównym objawem skażenia pamięci jest powolny spadek precyzji działania systemu, który nie wywołuje twardych błędów ani wyjątków w logach. Taki dryf jest niezwykle trudny do wykrycia i diagnozy.

Środki zaradcze: pamięć typu append-only (wyłącznie do dopisywania), rejestracja pochodzenia danych (provenance) oraz dedykowany moduł walidacyjny. Szczegółowo zagadnienia te opisano w Lekcji 13.

### STRATUS: Dedykowane role nadzorcze

Metodologia STRATUS (NeurIPS 2025) pozwala uzyskać 1,5-krotny wzrost skuteczności radzenia sobie z błędami poprzez wdrożenie trzech ról:

- **Agent detekcyjny (Detection Agent):** monitoruje profil działania systemu w poszukiwaniu anomalii (np. nagłe rozbieżności odpowiedzi, skoki liczby ponowień, dryf dokładności).
- **Agent diagnostyczny (Diagnostic Agent):** na podstawie symptomów określa najbardziej prawdopodobną przyczynę źródłową błędu w oparciu o kategorie MAST.
- **Agent walidacyjny (Validation Agent):** po wdrożeniu automatycznego środka zaradczego sprawdza, czy symptomy ustąpiły.

Wszystkie te trzy funkcje mogą być realizowane przez wyspecjalizowane agenty oparte na LLM z odpowiednimi promptami systemowymi.

### Procedura audytu trybów awarii

Dobrą praktyką inżynieryjną jest przeprowadzanie regularnych audytów (np. co kwartał lub przy wydaniach wersji głównych):

1. **Próbkowanie śladów:** pobranie losowej próbki ~1000 śladów wykonania zadań (execution traces) z produkcji.
2. **Klasyfikacja błędów:** zaklasyfikowanie zidentyfikowanych awarii według kategorii taksonomii MAST oraz zjawiska Groupthink.
3. **Statystyka kategorii:** określenie, które rodzaje błędów dominują w systemie.
4. **Priorytetyzacja działań:** wskazanie usprawnień, które wyeliminują najwięcej błędów.
5. **Wdrożenie poprawek:** zaimplementowanie 2-3 kluczowych zabezpieczeń i powtórzenie audytu w kolejnym cyklu.

Najważniejsze w tym procesie jest utrzymanie dyscypliny operacyjnej. Bez systematycznych audytów błędy produkcyjne stają się tłem (noise) i nigdy nie zostaną trwale wyeliminowane.

### Ciche awarie (Silent Failures)

Najbardziej problematycznym typem awarii są ciche błędy poprawności (silent failures). Wykrycie twardych błędów (wyjątki, błędy połączeń) w systemach monitoringu jest stosunkowo proste. Z kolei system, który generuje pozornie poprawne, lecz merytorycznie błędne odpowiedzi, nie wywoła żadnych alertów w logach. Z tego powodu luki w weryfikacji są najbardziej kosztowną kategorią błędów, mimo że statystycznie stanowią jedynie 21,30% przypadków.

Środkami zaradczymi w tym obszarze są:
- Regularna manualna weryfikacja losowych próbek odpowiedzi przez ekspertów.
- Testy regresji na referencyjnych zbiorach danych (golden datasets).
- Wzajemna weryfikacja wyników (cross-checking) przez niezależne agenty.

### Awarie nagłe vs powolny dryf

Klasyczne awarie nagłe (np. przekroczenie czasu oczekiwania, błędy autoryzacji, niezgodność formatu danych) są łatwe i tanie w detekcji. Powolne awarie (dryf monokultury, skażenie pamięci, nakładanie się ról) wymagają zaawansowanego monitorowania.

Rozwiązaniem inżynieryjnym jest wdrożenie wskaźników pomocniczych (proxy metrics) wykrywających dryf zanim przełoży się on na krytyczny błąd systemu. Do przydatnych wskaźników należą: współczynnik zgodności odpowiedzi agentów, statystyka liczby ponownych prób, rozkład długości generowanych odpowiedzi oraz odległość edycyjna (Levenshteina) między kolejnymi wersjami wypowiedzi agenta.

## Zbuduj to

Skrypt `code/main.py` implementuje:

- `FailureTaxonomy` – klasyfikator kategoryzujący zdarzenia awarii według taksonomii MAST oraz zjawiska Groupthink.
- `CircuitBreaker` – wzorzec wyłącznika sieciowego otwierającego się po przekroczeniu dopuszczalnego poziomu błędów.
- `RetryStormSimulator` – symulator awarii kaskadowej, demonstrujący zachowanie systemu z aktywnym wyłącznikiem oraz bez niego.
- `DetectionAgent` – uproszczonego agenta detekcji dopasowującego symptomy błędów zgodnie z zasadami STRATUS.

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik:
- Symulacja burzy ponowień bez wyłącznika: lawinowe błędy bazy danych stanu magazynowego.
- Symulacja z wyłącznikiem: zablokowanie zapytań po przekroczeniu progu i zwrócenie bezpiecznej odpowiedzi domyślnej.
- Logi agenta detekcji poprawnie identyfikujące schemat awarii i wskazujące właściwą kategorię MAST.

## Użyj tego

Plik `outputs/skill-mast-auditor.md` zawiera instrukcje przeprowadzania audytów trybów awarii w standardzie MAST dla systemów wieloagentowych (analiza śladów, klasyfikacja, priorytetyzacja poprawek).

## Wdrożenie produkcyjne

Zasady zarządzania stabilnością systemów wieloagentowych na produkcji:

- **Przeprowadzaj audyty MAST co kwartał.** Profil awarii ewoluuje wraz z rozwojem kodu i zmianami profili zapytań.
- **Stosuj wyłączniki (circuit breakers) dla wszystkich integracji zewnętrznych.** Każde połączenie do API zewnętrznego lub mikrousługi powinno być zabezpieczone wyłącznikiem o domyślnym progu otwarcia 5–10% błędów.
- **Utrzymuj referencyjne zbiory testowe (golden datasets).** Powinny to być niewielkie, ręcznie zweryfikowane bazy pytań i odpowiedzi, uruchamiane w cotygodniowych testach regresyjnych.
- **Wdróż agentów monitorujących w stylu STRATUS.** Zacznij od prostych modułów detekcji anomalii; zaawansowane moduły diagnostyki LLM wdrażaj dopiero wtedy, gdy wolumen logów utrudnia manualną analizę.
- **Zdefiniuj budżet błędów (error budget).** Ustąpienie od realizacji planu wdrożeń produkcyjnych powinno następować automatycznie po przekroczeniu zdefiniowanych limitów wskaźników awaryjności poszczególnych kategorii.

## Ćwiczenia

1. Uruchom `code/main.py`. Przetestuj działanie wyłącznika sieciowego w scenariuszu burzy ponowień. Zaobserwuj wpływ zmiany progu aktywacji na stabilność systemu.
2. Zaimplementuj monitorowanie wskaźnika zgodności (consensus rate) dla 3 równolegle odpytywanych agentów. Zaprojektuj mechanizm ostrzegania w przypadku nagłego wzrostu konformizmu (skrajnie wysoka zgodność przy spadku precyzji).
3. Przeczytaj publikację MAST (arXiv:2503.13657). Wybierz jeden z 7 analizowanych przez autorów systemów MAS typu open source i przeanalizuj 3 główne zidentyfikowane dla niego kategorie błędów.
4. Przeczytaj publikację poświęconą zjawisku Groupthink (arXiv:2508.05687). Wskaż, który z pięciu trybów awarii jest najtrudniejszy do wykrycia w rzeczywistym wdrożeniu i zaproponuj dla niego metrykę pomocniczą.
5. Zaprojektuj trio agentów nadzoru STRATUS (detekcja, diagnoza, walidacja) dla dowolnego systemu wieloagentowego. Określ, jakie symptomy powinien monitorować agent detekcji, jakie akcje zaradcze powinien rekomendować agent diagnostyki i jak agent walidacyjny zweryfikuje ich skuteczność.

## Kluczowe terminy

| Termin | Co się potocznie mówi | Co to właściwie oznacza |
|---|---|---|
| MAST | „Taksonomia błędów 2026” | Zaprezentowany przez Cemriego w 2025 r. standard klasyfikacji awarii systemów wieloagentowych, obejmujący 3 kategorie główne i 14 podtypów. |
| Problem ze specyfikacją | „Niejasne cele” | Błędy wynikające z niedookreślenia zadań lub niejednoznaczności przypisania ról agentom. |
| Błędy koordynacji | „Brak synchronizacji” | Awaria kanałów komunikacyjnych lub rozbieżność stanów (state drift) między agentami. |
| Luki w weryfikacji | „Brak kontroli” | Sytuacja, w której wyniki pracy agentów są akceptowane bez niezależnej walidacji poprawności. |
| Zjawiska Groupthink | „Myślenie grupowe” | Klasa błędów wynikających z ujednolicania zachowań agentów (monokultura, konformizm, brak ToM). |
| Monokultura (Monoculture) | „Ten sam model, ten sam błąd” | Skorelowane awarie całej populacji wynikające z oparcia wszystkich agentów na tym samym modelu bazowym LLM. |
| Burza ponownych prób (Retry Storm) | „Przeciążenie kaskadowe” | Awaria, w której błąd jednego komponentu wywołuje pętlę ponowień, przeciążając usługi w dalszej części potoku. |
| Wyłącznik (Circuit Breaker) | „Bezpiecznik sieciowy” | Wzorzec projektowy natychmiastowo przerywający połączenie z przeciążoną usługą w celu ochrony stabilności systemu. |
| STRATUS | „Agenci SRE” | Architektura oparta na wyspecjalizowanych agentach detekcji, diagnostyki i walidacji błędów produkcyjnych. |
| Skażenie pamięci (Memory Poisoning) | „Rozprzestrzenianie halucynacji” | Błąd weryfikacji, w którym halucynacja jednego agenta zostaje zapisana w pamięci i powielona przez kolejnych agentów. |

## Dalsze czytanie

- [Cemri i in. – Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) – taksonomia błędów MAST (NeurIPS 2025)
- [Groupthink Failures in Multi-Agent Large Language Models](https://arxiv.org/abs/2508.05687) – analiza zjawiska monokultury i konformizmu w systemach agentowych
- [STRATUS – Incident Response Agents for MAS](https://neurips.cc/) – publikacja w materiałach konferencyjnych NeurIPS 2025
- [Release It! – Design and Deploy Production-Ready Software (Nygard)](https://pragprog.com/titles/mnee2/release-it-second-edition/) – kanoniczny podręcznik opisujący wzorzec Circuit Breaker
- [Anthropic – Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) – praktyczne uwagi inżynieryjne na temat trybów awarii systemów agentowych
