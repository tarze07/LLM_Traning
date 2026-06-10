---

name: verification-gate
description: Wygeneruj deterministyczną bramkę weryfikacyjną, która łączy artefakty zakresu, reguł i informacji zwrotnych w jeden plik Verification_report.json dla każdego zadania, a także okablowanie CI, które nie pozwala na połączenie bez wydania zielonego wyroku.
version: 1.0.0
phase: 14
lesson: 38
tags: [verification, gate, deterministic, ci, override-log]

---

Biorąc pod uwagę kryteria akceptacji projektu i istniejące artefakty środowiska roboczego, utwórz bramkę weryfikacyjną i zastąp dziennik audytu.

Wyprodukuj:

1. `tools/verify_agent.py` odsłaniający `verify(task_id, artifacts) -> VerdictReport`. Czysta funkcja, deterministyczna, bez wywołań LLM.
2. `outputs/verification/<task_id>.json` jako jedyne źródło prawdy.
3. `tools/override.py`, który dołącza podpisane wpisy zastępujące do `outputs/verification/overrides.jsonl` (musi zawierać przyczynę, identyfikator użytkownika, znacznik czasu, kod wyszukiwania).
4. Przepływ pracy CI, który kończy się niepowodzeniem na `passed: false` i wyświetla raport bezpośrednio.
5. `docs/verification.md` wymienia każdą kontrolę, jej wagę, artefakt źródłowy i zasady obejścia.

Twarde odrzucenia:

- Czek wywołujący LLM. Brama jest deterministyczną instalacją wodno-kanalizacyjną; Ocena LLM należy do recenzenta.
- Ścieżka zastąpienia, którą agent może wybrać bez podpisanego wpisu. Zastąpienia są dostępne wyłącznie dla ludzi.
- Raport z weryfikacji, który pomija wykorzystane ścieżki artefaktów. Raporty muszą podlegać audytowi.
- Ustalenia dotyczące ważności bloku, które przepływ pracy może po cichu obniżyć. Ważność jest ustalana w czasie zapisu, a nie w czasie odczytu.

Zasady odmowy:

- Jeśli w projekcie nie ma polecenia odbioru, odmów wysyłki bramy do czasu jego pojawienia się. Brama, która niczego nie udowadnia, to teatr.
- Jeśli raport reguły nie istnieje, odmów pominięcia sprawdzania reguł; porażka zamknięta.
- Jeśli dziennik opinii nie istnieje, odmów pominięcia kontroli akceptacji; brakujące dzienniki same w sobie są blokiem.
- Jeśli wpisy zastąpienia nie są kontrolowane przez wersję, odmów podłączenia ścieżki zastąpienia; nieoficjalne zastąpienia pokonują bramę.

Struktura wyjściowa:

```
<repo>/
├── tools/
│   ├── verify_agent.py
│   └── override.py
├── outputs/verification/
│   ├── overrides.jsonl
│   └── <task_id>.json
├── docs/verification.md
└── .github/workflows/verify.yml
```

Zakończ słowami „co przeczytać dalej”, wskazując:

- Lekcja 39 dla agenta recenzenta, który podejmuje decyzję po wydaniu zielonego wyroku.
- Lekcja 40 dotycząca generatora przekazania, który zawiera werdykt w pakiecie.
- Lekcja 41 dotycząca uruchamiania bramy w porównaniu z przykładową aplikacją w prawdziwym stylu.