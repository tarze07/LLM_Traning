---

name: workbench-pack
description: Wygeneruj dostosowany do projektu pakiet środowiska roboczego dla agentów — zasady dostosowane do historii zespołu, obszary zakresów dopasowane do repozytorium, wymiary rubryk rozszerzone o jeden wpis specyficzny dla domeny.
version: 1.0.0
phase: 14
lesson: 42
tags: [capstone, workbench-pack, installer, schemas, drop-in]

---

Biorąc pod uwagę repozytorium, historię incydentów zespołu i działający w nim produkt agenta, wyemituj dostrojony pakiet agenta-workbench-pack i instalator.

Wyprodukuj:

1. Katalog `agent-workbench-pack/` odpowiadający układowi kanonicznemu: AGENTS.md, docs/, schemas/, scripts/, bin/, README.md, VERSION.
2. `bin/install.sh`, który odmawia zniszczenia istniejącego pakietu bez `--force` i zapisuje `.workbench-version` w docelowym repozytorium.
3. Dostosowane do projektu wersje `agent-rules.md` (z co najmniej jedną regułą na kategorię pochodzącą z sześciu ostatnich incydentów zespołu), `reviewer-rubric.md` (z szóstym wymiarem domeny) i `scope_contract.schema.json` (z globami specyficznymi dla projektu).
4. Skrypt `lint_pack.py`, który nie działa przy dryfowaniu między skryptami i schematami lub między WERSJĄ a `schema_version` schematów.
5. Opcjonalna integracja CI, która instaluje pakiet w gałęziach demonstracyjnych i uruchamia bramkę weryfikacyjną w odniesieniu do znanego, dobrego zadania.

Twarde odrzucenia:

- Pakiet zawierający zadania specyficzne dla projektu. Zadania znajdują się na tablicy docelowego repozytorium.
- Pakiet powiązany z pakietem SDK jednego dostawcy. Tylko niezależny od frameworka; Okablowanie SDK to zadanie docelowego repozytorium.
- Instalator mutujący pliki stanu. Instalator jest idempotentny tylko powierzchniowo; państwo należy do agenta i ludzi.
- Reguły bez odpowiedniej funkcji sprawdzającej. Zasady aspiracji należą do elementu onboardingu, a nie do pakietu.

Zasady odmowy:

- Jeśli historia zdarzeń jest pusta, odmów wysyłki dostrojonego `agent-rules.md`. Użyj kanonicznego ustawienia domyślnego i wykryj lukę.
- Jeśli CI repozytorium docelowego jest niezgodne z instalacją (brak `.github/workflows/`, brak odpowiednika), odrzuć opcjonalny krok CI i udokumentuj ręczną ścieżkę.
- Jeśli zespół korzysta z prywatnego rozwidlenia pakietu, odmów napisania publicznego instalatora. Prywatni instalatorzy wykonują prywatne niezmienniki.

Struktura wyjściowa:

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

Zakończ słowami „co przeczytać dalej”, wskazując:

- Lekcja 41 dotycząca testu porównawczego przed/po, który udoskonala ten pakiet.
- Lekcja 30 (Rozwój agenta w oparciu o Eval) na temat pętli eval, która wykorzystuje werdykty pakietu.
- [SkillKit](https://github.com/rohitg00/skillkit) do dystrybucji pakietu wśród 32 agentów AI.