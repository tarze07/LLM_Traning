# Budżety działań, limity iteracji i zarządcy kosztów

> Miesięczny koszt zapytań LLM dla średniej wielkości agenta e-commerce wzrósł z 1200 do 4800 USD po tym, jak wdrożono funkcję „śledzenia zamówień”. Nie był to błąd w cenniku dostawcy – agent wpadł w nieskończoną pętlę i generował koszty bez żadnej kontroli. Narzędzie Agent Governance Toolkit od Microsoftu (wprowadzone 2 kwietnia 2026 r.) definiuje standardy ochrony przed tego typu incydentami: parametry `max_tokens` na zapytanie, limity tokenów i budżety finansowe na zadanie, limity dzienne/miesięczne, ograniczenia iteracji, warstwowy routing modeli (tiered routing), buforowanie promptów (prompt caching), zarządzanie oknem kontekstowym, punkty kontrolne HITL dla kosztownych operacji oraz automatyczne wyłączniki awaryjne (kill switches) po przekroczeniu budżetu. Pakiet Claude Code Agent SDK od Anthropic oferuje analogiczne funkcje pod innymi nazwami. Wprowadzenie limitów dynamiki kosztów (financial velocity limits) – np. blokada przy wydatkach powyżej 50 USD w ciągu 10 minut – pozwala wykryć zapętlenie znacznie szybciej niż limity miesięczne.

**Typ:** Ucz się
**Języki:** Python (stdlib, warstwowy symulator zarządzania kosztami)
**Wymagania wstępne:** Faza 15 · 10 (Tryby uprawnień), Faza 15 · 12 (Trwałe wykonanie)
**Czas:** ~60 minut

## Problem

Autonomiczni agenci generują realne koszty finansowe w każdej iteracji swojego działania. Błąd tradycyjnego chatbota skutkuje jedynie złą odpowiedzią; błąd w pętli autonomicznego agenta kończy się wysokim rachunkiem. Branżowym określeniem na ten scenariusz awarii jest „odmowa portfela” (Denial of Wallet) – sytuacja, w której agent wpada w pętlę rozumowania, nieprzerwanie wywołuje narzędzia i generuje opłaty, ponieważ w systemie zabrakło mechanizmu, który mógłby go zatrzymać.

Skutecznym rozwiązaniem nie jest pojedynczy limit. Bezpieczeństwo wymaga wdrożenia kaskady ograniczeń na różnych poziomach szczegółowości i w różnych przedziałach czasowych: na zapytanie, na zadanie, na godzinę, dobę czy miesiąc. Dobrze zaprojektowany system potrafi wykryć zapętlenie w ciągu kilku minut, powolne wycieki środków w kilka godzin, a anomalie budżetowe w ciągu jednego dnia. Pozwala to na utrzymanie kontroli nad kosztami przy długo działających agentach autonomicznych.

To ważna lekcja inżynieryjna: matematyczna implementacja tych ograniczeń jest prosta, wyzwaniem jest natomiast systemowa dyscyplina projektowa. Wszystkie opisane niżej mechanizmy są obecne w Microsoft Agent Governance Toolkit oraz Anthropic Claude Code Agent SDK.

## Koncepcja

### Stos zarządców kosztów

1. **`max_tokens` na zapytanie:** Podstawowe ograniczenie, które zapobiega generowaniu zbyt długich odpowiedzi przez model w pojedynczym wywołaniu.
2. **Budżet tokenów na zadanie:** Całkowity limit tokenów dopuszczalny w pełnym cyklu realizacji zadania.
3. **Budżet finansowy na zadanie:** Analogiczny limit określony bezpośrednio w walucie (parametr `max_budget_usd` w Claude Code).
4. **Limit wywołań konkretnego narzędzia:** Maksymalna liczba użyć danego narzędzia w sesji (np. dozwolona liczba wywołań `WebFetch` lub `shell_exec`).
5. **Limit iteracji (`max_turns`):** Maksymalna liczba kroków in pętli agenta, co zapobiega nieskończonemu zapętleniu procesu decyzyjnego.
6. **Limity czasowe (minutowe / godzinowe / dobowe / miesięczne):** Ruchome okna czasowe wykrywające nadmierne zużycie zasobów.
7. **Limity dynamiki kosztów (Velocity limits):** Np. reguła „blokada procesu w przypadku wydania ponad 50 USD w 10 minut”, co pozwala na błyskawiczne zatrzymanie zapętlonego agenta.
8. **Warstwowy routing modeli (Tiered routing):** Uruchamianie domyślnie mniejszych i tańszych modeli, a delegowanie zadań do większych modeli tylko wtedy, gdy klasyfikator uzna to za konieczne.
9. **Buforowanie promptów (Prompt caching):** Zapisywanie powtarzalnych elementów kontekstu po stronie dostawcy API, co redukuje koszty ponownego przetwarzania danych niemal do zera.
10. **Zarządzanie oknem kontekstowym:** Kompresja i podsumowywanie historii sesji w celu utrzymania rozmiaru kontekstu poniżej krytycznego poziomu, co bezpośrednio wpływa na koszty.
11. **Punkty kontrolne HITL dla kosztownych operacji:** Wymóg akceptacji przez człowieka przed uruchomieniem zadań generujących wysokie koszty (np. pobieranie gigabajtów danych, kosztowny finetuning modelu).
12. **Wyłącznik awaryjny (Kill switch) po przekroczeniu limitu:** Natychmiastowe przerwanie sesji agenta w momencie naruszenia dowolnego z nałożonych limitów; odblokowanie wymaga ręcznej interwencji administratora.

### Dlaczego kaskada limitów, a nie pojedyncza blokada?

Miesięczny limit na poziomie konta zatrzyma zapętlonego agenta dopiero wtedy, gdy wyczerpie on cały dostępny budżet. Z kolei pojedyncze limity na zapytanie nie chronią przed kosztami na poziomie całej sesji. Różne scenariusze awarii wymagają różnych mechanizmów obronnych w czasie:

- **Nagle zapętlenie** (np. ponawianie prób co 5 sekund po błędzie API): wykrywane przez limit dynamiki kosztów (velocity limit).
- **Powolny wyciek** (np. agent wykonuje dwa razy więcej pracy niż planowano na zadanie): wykrywany przez limit dobowy.
- **Błędy wdrożeniowe** (np. nowa wersja kodu generuje pięciokrotnie więcej tokenów): wykrywane przez limity tygodniowe lub miesięczne.
- **Uzasadniony wzrost kosztów** (wynikający z realnego obciążenia, a nie błędów): bezpiecznie monitorowany i raportowany w logach limitów krótkookresowych.

### Parametry budżetowe w Claude Code

Pakiet Claude Code Agent SDK udostępnia następujące parametry:

- `max_turns` — limit iteracji w pętli.
- `max_budget_usd` — limit finansowy, którego przekroczenie powoduje natychmiastowe przerwanie sesji.
- `allowed_tools` / `disallowed_tools` — biała i czarna lista narzędzi dostępnych dla agenta.
- Punkty wpięcia (hooks) przed uruchomieniem narzędzi pozwalające na szacowanie kosztów przed wykonaniem operacji.

Należy połączyć te parametry z poziomami uprawnień (patrz Lekcja 10). Uruchomienie sesji w trybie `autoMode` bez określonego parametru `max_budget_usd` oznacza brak kontroli nad kosztami. Anthropic wyraźnie wskazuje, że tryb automatyczny wymaga nałożenia limitów budżetowych, ponieważ klasyfikatory bezpieczeństwa nie analizują kosztów operacji.

### Zgodność z regulacjami (Ustawa o sztucznej inteligencji, OWASP Agentic Top 10)

Zestaw narzędzi do zarządzania agentami od Microsoftu uwzględnia wytyczne OWASP Agentic Top 10 oraz wymogi Artykułu 14 unijnej ustawy o sztucznej inteligencji (AI Act) dotyczące nadzoru ludzkiego. W przypadku wdrożeń produkcyjnych na terenie UE szczegółowe logowanie kosztów i egzekwowanie limitów operacyjnych są wymaganiami prawnymi.

### Analiza przypadku: wzrost kosztów z 1200 do 4800 USD

Jest to rzeczywisty przypadek opisany w dokumentacji Microsoftu: koszty operacyjne agenta e-commerce potroiły się po dodaniu nowego narzędzia pozwalającego na ciągłe odpytywanie statusu zamówień. System nie posiadał funkcji wykrywania pętli, limitów wywołań dla narzędzi ani powiadomień o nagłym wzroście kosztów w ujęciu tygodniowym. Rozwiązaniem było nałożenie limitu wywołań na nowo dodane narzędzie oraz wdrożenie dobowych alertów budżetowych. Przypadek ten pokazuje ważną zasadę: każde nowe narzędzie udostępnione agentowi to nowa potencjalna pętla zapętlenia, dlatego każde z nich powinno posiadać dedykowany limit wywołań oraz system ostrzegania.

## Przykład praktyczny

Skrypt `code/main.py` symuluje działanie agenta z wdrożonym stosem limitów oraz w przypadku ich braku. Symulowany agent wpada w pętlę odpytywania; system zabezpieczeń potrafi go zatrzymać dzięki limitowi dynamiki kosztów (velocity limit), podczas gdy pojedynczy limit miesięczny zareagowałby dopiero po kilku dniach i wygenerowaniu ogromnych kosztów.

## Zadanie wdrożeniowe

Plik `outputs/skill-agent-budget-audit.md` służy do weryfikacji mechanizmów kontroli kosztów w proponowanym projekcie agenta i wskazuje brakujące warstwy zabezpieczeń.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Potwierdź, że limit dynamiki kosztów (velocity limit) uruchamia się przed limitem iteracji w przypadku zapętlenia. Wyłącz limit dynamiki i zmierz, ile kosztów wygeneruje agent, zanim zatrzyma go limit iteracji.
2. Zaprojektuj limity wywołań dla narzędzi agenta przeglądarkowego (patrz Lekcja 11). Które z narzędzi wymaga najbardziej restrykcyjnego limitu? Które narzędzie może działać z mniejszymi ograniczeniami?
3. Zapoznaj się z dokumentacją Microsoft Agent Governance Toolkit. Wskaż nazwy dostępnych pakietów narzędzi i przypisz je do konkretnych typów awarii (nagłe zapętlenie, powolny wyciek środków, błędy wdrożeniowe, skok obciążenia).
4. Oszacuj budżet dla nienadzorowanego zadania uruchamianego na noc (np. „analiza 50 zgłoszeń w repozytorium kodu”). Ustaw parametr `max_budget_usd` na poziomie dwukrotności szacowanego kosztu nominalnego i uzasadnij ten bufor bezpieczeństwa.
5. Parametr `max_budget_usd` w Claude Code bazuje na sumarycznym koszcie sesji. Zaprojektuj zewnętrzny mechanizm limitu dynamiki kosztów (velocity limit). Określ warunki jego aktywacji oraz procedurę bezpiecznego restartu sesji.

## Kluczowe terminy

| Termin | Co mówią potocznie | Co to dokładnie oznacza |
|---|---|---|
| Odmowa portfela (Denial of Wallet) | „Uciekający rachunek” | Awaria agenta polegająca na zapętleniu i generowaniu ogromnych opłat bez automatycznego zatrzymania |
| max_tokens | „Limit na zapytanie” | Maksymalna liczba tokenów wygenerowana w pojedynczej odpowiedzi modelu |
| max_turns | „Limit iteracji” | Maksymalna dopuszczalna liczba kroków/tur agenta w ramach jednej sesji |
| max_budget_usd | „Wyłącznik finansowy” | Limit kosztów sesji, którego przekroczenie natychmiast przerywa działanie agenta |
| Limity dynamiki kosztów (Velocity limits) | „Limit tempa wydatków” | Limit wydatków w krótkim przedziale czasu (np. do 50 USD na 10 minut) |
| Warstwowy routing (Tiered routing) | „Najpierw tańszy model” | Strategia kierowania zapytań najpierw to tańszego modelu i eskalacji do większego tylko przy trudnych zadaniach |
| Buforowanie promptów (Prompt caching) | „Cache kontekstu” | Mechanizm zapamiętywania stałej części promptu systemowego w celu obniżenia kosztów API |
| Punkt kontrolny HITL (HITL Checkpoint) | „Bramka autoryzacji” | Wymóg zatwierdzenia akcji przez człowieka przed uruchomieniem kosztownych operacji |

## Dalsza lektura

- [Anthropic Claude Code Agent SDK — pętla agenta i budżety](https://code.claude.com/docs/en/agent-sdk/agent-loop) — parametry `max_turns`, `max_budget_usd` oraz białe listy narzędzi.
- [Microsoft Agent Framework — działanie człowieka w pętli i zarządzanie](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) — punkty kontrolne odpowiedzialne za zarządzanie kosztami.
- [Anthropic — przegląd agentów zarządzanych przez Claude](https://platform.claude.com/docs/en/managed-agents/overview) — mechanizmy kontroli kosztów dostawcy.
- [Anthropic — Prompt caching (dokumentacja API Claude)](https://platform.claude.com/docs/en/prompt-caching) — szczegóły techniczne mechanizmu cache.
- [Anthropic — Pomiar autonomii agentów w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — analiza profilu kosztowego agentów pracujących w długim horyzoncie.
