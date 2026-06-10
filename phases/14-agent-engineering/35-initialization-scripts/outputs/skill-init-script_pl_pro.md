---

name: init-script
description: Przeanalizuj strukturę projektu i wygeneruj deterministyczny skrypt init_agent.py zawierający pięć testów walidacyjnych (sond) oraz konfigurację przepływu pracy CI, która blokuje uruchomienie agenta w przypadku wykrycia błędów konfiguracyjnych.
version: 1.0.0
phase: 14
lesson: 35
tags: [init, probes, ci, workbench, fail-loud]

---

Biorąc pod uwagę strukturę repozytorium, produkt agenta oraz jego zależności, utwórz skrypt inicjalizacyjny dostosowany do projektu wraz z odpowiednią konfiguracją CI.

Wygeneruj:

1. `tools/init_agent.py` z testami sprawdzającymi: wersję środowiska uruchomieniowego, zainstalowane zależności, poprawność poleceń testowych, wymagane zmienne środowiskowe oraz aktualność pliku stanu.
2. Szablon raportu `init_report.json` udokumentowany obok skryptu. Każdy test zwraca wynik w formacie `(name, status: pass|warn|fail, detail)`.
3. Plik `.github/workflows/agent-init.yml` (lub jego odpowiednik), który uruchamia skrypt i blokuje zadanie agenta, jeśli jakikolwiek test o statusie krytycznym (fail) zakończy się niepowodzeniem.
4. Skrypt pomocniczy `pre-task`, który środowisko wykonawcze agenta uruchamia przed rozpoczęciem każdej sesji.
5. Dokumentację w `docs/init.md` opisującą każdy test, jego poziom ważności oraz instrukcję postępowania w przypadku wykrycia błędu.

Bezwarunkowe odrzucenia:

- Testy (sondy) wykonujące zapytania sieciowe bez zdefiniowanego limitu czasu (timeout). Inicjalizacja musi działać szybko i być bezpieczna w trybie offline.
- Sondy wymagające zapytań do modeli LLM. Inicjalizacja to deterministyczny proces techniczny.
- Tłumienie niezerowego kodu wyjścia przez skrypty uruchamiające (wrappery). Błędy konfiguracyjne muszą być zgłaszane jawnie i natychmiast.
- Sondy modyfikujące stan w sposób nieidempotentny. Dwa kolejne uruchomienia muszą wygenerować identyczny raport (z dokładnością do sygnatury czasowej).

Zasady odmowy:

- Jeśli projekt nie posiada zdefiniowanego polecenia testowego, odmów wygenerowania skryptu. Zamiast tego wskaż ten brak jako krytyczny problem w audycie środowiska pracy.
- Jeśli zmienne środowiskowe zawierają dane wrażliwe (hasła, tokeny), skrypt musi bezwzględnie zamaskować te wartości. Raporty inicjalizacyjne nigdy nie mogą zawierać sekretów w otwartym tekście.
- Jeśli uruchomienie testu w trybie dry-run trwa dłużej niż 3 sekundy, zoptymalizuj jego czas działania przed wdrożeniem. Zbyt wolne testy zamieniają inicjalizację w uciążliwy krok spowalniający pracę.

Struktura wyjściowa:

```
<repo>/
├── tools/
│   ├── init_agent.py
│   └── pre_task.sh
├── docs/
│   └── init.md
└── .github/
    └── workflows/
        └── agent-init.yml
```

Zakończ sekcją „Polecana lektura”, wskazując:

- Lekcję 36 omawiającą umowy zakresu zadań (task scopes), korzystające ze zdefiniowanych w raporcie ścieżek `repo_paths`.
- Lekcję 37 opisującą pętlę sprzężenia zwrotnego wykorzystującą zweryfikowane polecenie testowe.
- Lekcję 38 opisującą bramkę weryfikacyjną zależną od pomyślnego przejścia testów inicjalizacyjnych.
