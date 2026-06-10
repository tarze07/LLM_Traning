---

name: init-script
description: Przeprowadź wywiad z projektem i wyemituj deterministyczny plik init_agent.py z pięcioma sondami oraz przepływem pracy CI, który odmawia uruchomienia agenta, jeśli którakolwiek sonda zakończy się niepowodzeniem.
version: 1.0.0
phase: 14
lesson: 35
tags: [init, probes, ci, workbench, fail-loud]

---

Biorąc pod uwagę repozytorium, produkt agenta i jego powierzchnię zależności, utwórz skrypt init specyficzny dla projektu i okablowanie CI.

Wyprodukuj:

1. `tools/init_agent.py` z tymi sondami: wersja środowiska uruchomieniowego, wymienione zależności, rozpoznawalność poleceń testowych, wymagane zmienne środowiskowe, aktualność pliku stanu.
2. Schemat `init_report.json` udokumentowany obok skryptu. Każda sonda zwraca `(name, status: pass|warn|fail, detail)`.
3. `.github/workflows/agent-init.yml` (lub odpowiednik), który uruchamia skrypt i blokuje zadanie agenta w przypadku dowolnej sondy o wadze awarii.
4. Skrypt przechwytujący `pre-task`, który środowisko wykonawcze agenta może wywołać przed rozpoczęciem każdej sesji.
5. Dokumentacja w `docs/init.md` zawierająca listę każdej sondy, jej wagę i sposób usunięcia awarii.

Twarde odrzucenia:

- Sondy, które wołają do sieci bez limitu czasu. Init musi być szybki i bezpieczny w trybie offline.
- Sondy wymagające wywołań LLM. Init jest deterministyczną hydrauliką.
- Niezerowy kod wyjścia, który połyka opakowanie. O to właśnie chodzi w głośnych porażkach.
- Sondy dotykające stanu bez idempotencji. Dwa uruchomienia z rzędu muszą generować identyczne raporty ze znacznikiem czasu modulo.

Zasady odmowy:

- Jeśli w projekcie nie ma polecenia testowego, odmów wysłania skryptu. Zamiast tego dodaj lukę do audytu środowiska roboczego.
- Jeśli lista env var zawiera sekrety, skrypt wydrukuje, odrzuci i wymusi redakcję. Raporty początkowe nigdy nie powinny zawierać tajemnic.
- Jeżeli praca sondy na sucho trwa dłużej niż trzy sekundy, przed wysyłką należy sprawdzić pomiar czasu. Długie sondy zamieniają inicjację w ceremonię.

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

Zakończ słowami „co przeczytać dalej”, wskazując:

- Lekcja 36 dotycząca umowy dotyczącej zakresu poszczególnych zadań, która wykorzystuje `repo_paths` raportu początkowego.
- Lekcja 37 dotycząca pętli sprzężenia zwrotnego w czasie wykonywania, która wykorzystuje rozpoznane polecenie testowe.
- Lekcja 38 dla bramki weryfikacyjnej zależnej od przejścia sond.