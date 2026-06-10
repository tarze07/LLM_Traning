---

name: permission-mode-picker
description: Dopasuj zadanie Claude Code do odpowiedniego trybu uprawnień, limitów budżetowych i wymaganej izolacji środowiska przed uruchomieniem agenta.
version: 1.0.0
phase: 15
lesson: 10
tags: [claude-code, permission-modes, auto-mode, budgets, isolation]

---

Dla zadeklarowanego zadania w Claude Code dobierz właściwy tryb uprawnień, określ limity budżetowe oraz zdefiniuj minimalne wymagania dotyczące izolacji środowiska przed uruchomieniem agenta.

Przygotuj:

1. **Profil zadania.** Jedno zdanie opisujące cel i zakres zadania oraz jedno zdanie określające zakres potencjalnych szkód (blast radius) w przypadku wystąpienia awarii.
2. **Rekomendowany tryb.** Wybierz jeden z trybów: `plan`, `default`, `acceptEdits`, `acceptExec`, `autoMode`, `yolo`, `bypassPermissions`. Przedstaw jednozdaniowe uzasadnienie odwołujące się do szacowanego zakresu szkód.
3. **Wartości budżetowe.** Określ konkretne wartości dla `max_turns`, `max_budget_usd` oraz ewentualne limity dla poszczególnych narzędzi. W przypadku nienadzorowanych sesji trwających ponad godzinę ustaw limit finansowy na poziomie nieprzekraczającym kwoty, jaką dopuszczasz jako koszt ewentualnego, nieodwracalnego błędu.
4. **Wymagania dotyczące izolacji.** Zdefiniuj dostęp do systemu plików (tylko katalog projektu, katalog tymczasowy, kontener efemeryczny), zasady sieciowe (całkowity brak ruchu wychodzącego, biała lista domen, pełny dostęp) oraz zakres danych uwierzytelniających (brak, token o ograniczonym zakresie, token o szerokim dostępie). W przypadku trybów `bypassPermissions` lub `yolo` sesja musi być uruchomiona w kontenerze efemerycznym bez dostępu do danych produkcyjnych.
5. **Plan audytu trajektorii.** Wskaż, w jaki sposób i przez kogo zostanie przeprowadzony przegląd ścieżki działań (trajektorii) agenta po zakończeniu pracy. Krok ten jest obowiązkowy dla trybów `autoMode`, `yolo` oraz wszystkich sesji trwających dłużej niż 30 minut.

Kryteria odrzucenia (Hard Rejections):
- Użycie `bypassPermissions` w repozytorium zawierającym niezatwierdzone (unstaged/uncommitted) zmiany.
- Uruchomienie `autoMode` bez określonych limitów budżetowych.
- Użycie dowolnego trybu o wyższych uprawnieniach niż `acceptEdits` w środowisku z szerokimi uprawnieniami (np. dostęp do AWS, GCP lub GitHub PAT z pełnym zakresem repozytoriów).
- Uruchamianie nienadzorowanych zadań trwających ponad godzinę bez zaplanowanego audytu trajektorii.
- Zakładanie, że sam klasyfikator w trybie automatycznym jest w pełni wystarczający do zabezpieczenia nowych typów zadań.

Zasady odmowy wykonania zadania (Denial Policies):
- Jeśli użytkownik nie potrafi określić potencjalnego zakresu szkód (blast radius), należy odmówić wykonania zadania i zażądać analizy najgorszego scenariusza przed startem.
- Jeśli użytkownik żąda uruchomienia `autoMode` w obszarze roboczym z dostępem do danych uwierzytelniających produkcyjnej bazy danych, należy odmówić i zażądać ograniczenia uprawnień danych uwierzytelniających lub użycia kontenera efemerycznego.
- Jeśli proponowany limit budżetu przekracza kwotę, którą użytkownik jest gotowy stracić w przypadku niekontrolowanego zapętlenia lub awarii agenta, należy odmówić i zażądać obniżenia limitu finansowego.

Format danych wyjściowych:

Przedstaw jednostronicową kartę uruchomienia (run card) zawierającą:
- **Podsumowanie zadania** (jedno zdanie)
- **Zakres szkód (Blast Radius)** (jedno zdanie opisujące najgorszy scenariusz)
- **Tryb uprawnień** (jawnie określony)
- **Budżet** (`max_turns`, `max_budget_usd`, limity dla narzędzi)
- **Izolacja środowiska** (dostęp do systemu plików, zasady sieciowe, zakres danych uwierzytelniających)
- **Plan audytu** (osoba odpowiedzialna za przegląd trajektorii, czas wykonania oraz kryteria oceny)
