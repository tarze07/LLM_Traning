---

name: scope-contract
description: Generuj kontrakty dotyczące zakresu poszczególnych zadań z dozwolonymi/zabronionymi obszarami globalnymi, kryteriami akceptacji i planem wycofywania zmian, a także moduł sprawdzający obsługujący globalne rozwiązania, obsługujący CI, działający na wszystkich różnicach agentów.
version: 1.0.0
phase: 14
lesson: 36
tags: [scope, contract, globs, diff-check, ci]

---

Biorąc pod uwagę opis zadania i układ repozytorium, utwórz umowę dotyczącą zakresu i moduł sprawdzający uwzględniający różnice.

Wyprodukuj:

1. `scope_contract.json` dla zadania z polami: `task_id`, `goal`, `allowed_files` (globy), `forbidden_files` (globy), `acceptance_criteria`, `rollback_plan`, `approvals_required`.
2. `tools/scope_check.py`, który pobiera ścieżkę kontraktu i listę dotkniętych plików i zwraca `ScopeReport` plus niezerowe wyjście w przypadku jakiegokolwiek naruszenia.
3. Krok CI (`.github/workflows/scope-check.yml` lub odpowiednik), który uruchamia sprawdzanie różnicy scalającej.
4. Konwencja archiwalna `outputs/scope/closed/<task_id>.json`, więc umowy są dostarczane z historią zmian.

Twarde odrzucenia:

- Umowa bez `forbidden_files`. Przestrzeń negatywna jest częścią umowy.
- Kontrakt, który wyświetla nieprzetworzone ścieżki zamiast globów dla katalogów z kodem. Refaktoryzatory unieważniają surowe ścieżki z dnia na dzień.
— Pole `rollback_plan`, które jest puste lub „zobacz element Runbook”. Przeliteruj to.
- Zatwierdzenia wymienione jako „dla każdego przypadku”. Granice zatwierdzeń muszą być przeliczalne.

Zasady odmowy:

- Jeśli opis zadania nie ogranicza regionu repozytorium, odmów tworzenia `allowed_files` na podstawie samego opisu. Zapytaj o katalog, w którym znajduje się zadanie.
- Jeśli repozytorium nie ma polecenia testowego, odmów dodania `acceptance_criteria`, dopóki nie zostanie dostarczony lub zaznaczony. Umowa, której nie można zweryfikować, jest życzeniem.
- Jeśli środowisko wykonawcze agenta nie jest w stanie dotrzymać granic zatwierdzenia (bez udziału człowieka w pętli), wykryj lukę przed wysyłką; Dominującym niepowodzeniem będzie wkradanie się w zakres działań wymagających zatwierdzenia.

Struktura wyjściowa:

```
<repo>/
├── scope_contract.json
├── outputs/scope/closed/
│   └── T-XXX.json
├── tools/
│   └── scope_check.py
└── .github/
    └── workflows/
        └── scope-check.yml
```

Zakończ słowami „co przeczytać dalej”, wskazując:

- Lekcja 37 dotycząca informacji zwrotnych w czasie wykonywania, które łączą polecenia z kontraktem.
- Lekcja 38 dotycząca bramki weryfikacyjnej, która wykorzystuje raport zakresu.
- Lekcja 39 dla agenta recenzenta, który audytuje archiwum zamkniętej umowy.