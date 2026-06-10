---

name: permission-mode-picker
description: Dopasuj zadanie Claude Code do prawidłowego trybu uprawnień, ograniczeń budżetowych i wymaganej izolacji przed rozpoczęciem przebiegu.
version: 1.0.0
phase: 15
lesson: 10
tags: [claude-code, permission-modes, auto-mode, budgets, isolation]

---

Biorąc pod uwagę proponowane zadanie Claude Code, wybierz tryb uprawnień, ustaw budżety i określ minimalną izolację wymaganą przed uruchomieniem agenta.

Wyprodukuj:

1. **Profil zadania.** Jedno zdanie na temat działania zadania, jedno zdanie na temat promienia wybuchu, jeśli coś pójdzie nie tak.
2. **Zalecany tryb.** Jeden z: `plan`, `default`, `acceptEdits`, `acceptExec`, `autoMode`, `yolo`, `bypassPermissions`. Uzasadnij jednym zdaniem odnoszącym się do promienia wybuchu.
3. **Liczby budżetowe.** Konkretne wartości dla `max_turns`, `max_budget_usd` i wszelkich nasadek dla poszczególnych narzędzi. W przypadku przejazdów bez nadzoru trwających ponad godzinę określ limit w dolarach równy lub niższy od kwoty, jaką zapłaciłbyś za błąd ludzki, którego nie można cofnąć.
4. **Wymagania dotyczące izolacji.** Zakres systemu plików (tylko katalog projektu, katalog tymczasowy, kontener efemeryczny). Zasady sieciowe (zakaz ruchu wychodzącego, tylko lista dozwolonych, pełny). Powierzchnia poświadczeń (brak, token o określonym zakresie, token o szerokim zakresie). W przypadku `bypassPermissions` lub `yolo` przebieg musi znajdować się w tymczasowym kontenerze bez zamontowanych poświadczeń produkcyjnych.
5. **Plan audytu trajektorii.** W jaki sposób człowiek dokona przeglądu trajektorii po biegu? Wymagane w przypadku `autoMode`, `yolo` i wszystkiego, co trwa dłużej niż 30 minut.

Twarde odrzucenia:
- `bypassPermissions` względem repozytorium z niezatwierdzonymi zmianami.
- `autoMode` bez limitu budżetu.
- Dowolny tryb powyżej `acceptEdits` z szerokimi uprawnieniami w środowisku (AWS, GCP, GitHub PAT z zakresem repo).
- Działa bez nadzoru dłużej niż godzinę i nie zaplanowano audytu trajektorii.
- Twierdzenie, że sam klasyfikator trybu automatycznego jest wystarczający do nowatorskiego podziału zadań.

Zasady odmowy:
- Jeśli użytkownik nie jest w stanie określić promienia wybuchu awarii, odmów i przed rozpoczęciem zażądaj wyraźnego określenia najgorszego przypadku.
- Jeśli użytkownik zażąda `autoMode` w obszarze roboczym z dostępnymi poświadczeniami produkcyjnej bazy danych, odmów i zażądaj najpierw poświadczeń o określonym zakresie lub kontenera tymczasowego.
- Jeśli proponowany limit budżetu przekracza kwotę, którą użytkownik jest skłonny stracić w przypadku złej passy, ​​odmów i żądaj niższego limitu.

Format wyjściowy:

Zwróć jednostronicową kartę przebiegu zawierającą:
- **Podsumowanie zadania** (jedno zdanie)
- **Promień wybuchu** (jedno zdanie, najgorszy przypadek)
- **Tryb** (jawny)
- **Budżety** (`max_turns`, `max_budget_usd`, nakładki na narzędzia)
- **Izolacja** (zakres fs, polityka sieciowa, powierzchnia danych uwierzytelniających)
- **Plan audytu** (kto dokonuje przeglądu trajektorii, kiedy i w oparciu o jakie kryteria)