---

name: scope-contract
description: Generuj umowy dotyczące zakresu (scope contracts) dla konkretnych zadań z uwzględnieniem dozwolonych/zabronionych wzorców glob, kryteriów akceptacji oraz planu wycofania zmian. Narzędzie tworzy również obsługujący wzorce glob i przystosowany do CI moduł sprawdzający, który analizuje zmiany (diff) wprowadzane przez agenta.
version: 1.0.0
phase: 14
lesson: 36
tags: [scope, contract, globs, diff-check, ci]

---

Na podstawie opisu zadania oraz struktury repozytorium utwórz umowę dotyczącą zakresu (scope contract) oraz moduł sprawdzający zmiany (diff checker).

Wymagane elementy:

1. Plik `scope_contract.json` dla zadania z następującymi polami: `task_id`, `goal`, `allowed_files` (wzorce glob), `forbidden_files` (wzorce glob), `acceptance_criteria`, `rollback_plan`, `approvals_required`.
2. Skrypt `tools/scope_check.py`, który przyjmuje ścieżkę do kontraktu oraz listę zmodyfikowanych plików, a następnie zwraca raport `ScopeReport` i kończy działanie niezerowym kodem wyjścia w przypadku wykrycia jakiegokolwiek naruszenia.
3. Krok CI (`.github/workflows/scope-check.yml` lub jego odpowiednik), który uruchamia weryfikację zmian (diff) w pull requestach.
4. Standard archiwizacji `outputs/scope/closed/<task_id>.json`, dzięki czemu zakończone kontrakty są przechowywane wraz z historią zmian.

Bezwzględne odrzucenia (Twarde kryteria):

- Kontrakt bez zdefiniowanego pola `forbidden_files`. Wykluczenia (negatywny zakres) stanowią kluczową część umowy.
- Kontrakt zawierający bezpośrednie ścieżki zamiast wzorców glob dla katalogów z kodem źródłowym. Refaktoryzacja kodu może natychmiast unieważnić bezpośrednie ścieżki.
- Pole `rollback_plan`, które jest puste lub zawiera ogólne sformułowania typu „zobacz instrukcję (runbook)”. Procedura wycofania zmian musi być szczegółowo opisana.
- Wymóg zatwierdzeń określony w sposób niejednoznaczny (np. „w zależności od przypadku”). Granice autoryzacji muszą być precyzyjnie określone.

Zasady odmowy współpracy (Refusal rules):

- Jeśli opis zadania nie określa jednoznacznie obszaru repozytorium, odmów wygenerowania listy `allowed_files` wyłącznie na podstawie opisu. Poproś o wskazanie katalogu roboczego dla danego zadania.
- Jeśli w repozytorium nie zdefiniowano polecenia uruchamiającego testy, odmów określenia `acceptance_criteria` do czasu jego podania lub zweryfikowania. Umowa, której nie da się zweryfikować testami, jest jedynie życzeniem.
- Jeśli środowisko wykonawcze agenta nie potrafi wyegzekwować granic autoryzacji (bez udziału człowieka w pętli), zgłoś tę lukę bezpieczeństwa przed wdrożeniem. Głównym źródłem problemów jest ciche wykonywanie przez agenta akcji wymagających zatwierdzenia.

Struktura plików:

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

Na koniec dodaj sekcję „Co przeczytać dalej”, wskazującą na:

- Lekcję 37 dotyczącą pętli informacji zwrotnej w czasie rzeczywistym (runtime feedback loops), która wiąże uruchamiane polecenia z kontraktem.
- Lekcję 38 poświęconą bramce weryfikacyjnej (verification gate), która wykorzystuje raport z kontroli zakresu.
- Lekcję 39 dotyczącą agenta-recenzenta (reviewer agent), który przeprowadza audyt archiwum zamkniętych umów.
