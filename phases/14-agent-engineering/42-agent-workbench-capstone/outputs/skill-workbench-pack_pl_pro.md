---

name: workbench-pack
description: Generowanie dostosowanego do projektu pakietu środowiska warsztatowego dla agentów — zasady dostosowane do historii incydentów zespołu, definicje zakresu dopasowane do struktury repozytorium oraz kryteria ocen (rubryki) rozszerzone o wpis specyficzny dla danej domeny.
version: 1.0.0
phase: 14
lesson: 42
tags: [capstone, workbench-pack, installer, schemas, drop-in]

---

Mając do dyspozycji repozytorium, historię incydentów w zespole oraz wykorzystywane rozwiązanie agentowe, wygeneruj dostosowany pakiet `agent-workbench-pack` wraz ze skryptem instalacyjnym.

Wymagane rezultaty:

1. Katalog `agent-workbench-pack/` zgodny z kanoniczną strukturą: AGENTS.md, docs/, schemas/, scripts/, bin/, README.md, VERSION.
2. Skrypt `bin/install.sh`, który uniemożliwia nadpisanie istniejącego pakietu (chyba że użyto flagi `--force`) i zapisuje plik `.workbench-version` w repozytorium docelowym.
3. Dostosowane do projektu wersje plików: `agent-rules.md` (zawierający co najmniej jedną regułę w każdej kategorii opartą na analizie 6 ostatnich incydentów zespołu), `reviewer-rubric.md` (rozszerzony o szósty kryterium oceny specyficzne dla domeny) oraz `scope_contract.schema.json` (z regułami dopasowania ścieżek/glob patterns specyficznymi dla projektu).
4. Skrypt weryfikacyjny `lint_pack.py`, który zgłasza błąd w przypadku rozbieżności (dryfu) między skryptami a schematami, lub gdy wersja w pliku `VERSION` różni się od `schema_version` w schematach.
5. Opcjonalna integracja z procesem CI, która wdraża pakiet w gałęziach demonstracyjnych (demo branches) i uruchamia bramkę weryfikacyjną na sprawdzonym, poprawnie wykonanym zadaniu.

Kryteria odrzucenia (Twarde reguły):

- Pakiet zawierający zadania specyficzne dla konkretnego projektu. Zadania powinny być zdefiniowane wyłącznie na tablicy zadań w repozytorium docelowym.
- Powiązanie pakietu z SDK konkretnego dostawcy. Pakiet musi być niezależny od frameworków i platform (framework-agnostic); integracja z SDK leży po stronie repozytorium docelowego.
- Modyfikowanie plików stanu przez instalator. Skrypt instalacyjny musi być idempotentny i dotyczyć wyłącznie struktury środowiska; stan należy do agenta i zespołu.
- Reguły bez przypisanej funkcji walidującej (sprawdzającej). Zasady o charakterze czysto intencyjnym/szkoleniowym powinny być częścią onboardingu, a nie pakietu technicznego.

Kryteria odmowy wykonania:

- Jeśli historia incydentów jest pusta, odmów przygotowania dostosowanego pliku `agent-rules.md`. Użyj domyślnych, kanonicznych ustawień i zgłoś brak danych.
- Jeśli środowisko CI repozytorium docelowego nie wspiera integracji (brak `.github/workflows/` lub odpowiednika), pomiń konfigurację kroku CI i opisz procedurę ręczną.
- Jeśli zespół korzysta z prywatnego forka pakietu, odmów przygotowania publicznego instalatora. Prywatne instalatory służą do obsługi prywatnych, specyficznych reguł.

Struktura katalogów i plików:

```
agent-workbench-pack/
├── AGENTS.md
├── docs/
├── schemas/
├── scripts/
├── bin/install.sh
├── lint_pack.py
├── VERSION
└── README.md
```

Zakończ sekcją „Co przeczytać dalej”, wskazując na:

- Lekcję 41 dotyczącą benchmarku przed/po, który weryfikuje ten pakiet.
- Lekcję 30 (Rozwój agentów oparty na ewaluacji) dotyczącą pętli ewaluacyjnych wykorzystujących decyzje z pakietu.
- Narzędzie [SkillKit](https://github.com/rohitg00/skillkit) ułatwiające dystrybucję pakietu do wielu agentów AI.
