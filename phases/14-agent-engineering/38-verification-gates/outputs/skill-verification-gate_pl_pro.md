---

name: verification-gate
description: Skonfiguruj deterministyczną bramkę weryfikacyjną, która łączy raporty z zakresu prac, reguł oraz logów sprzężenia zwrotnego w jeden plik verification_report.json dla każdego zadania. Narzędzie integruje się również z potokiem CI, blokując scalenie zmian w przypadku negatywnego werdyktu.
version: 1.0.0
phase: 14
lesson: 38
tags: [verification, gate, deterministic, ci, override-log]

---

Na podstawie kryteriów akceptacji projektu oraz istniejących artefaktów środowiska roboczego utwórz bramkę weryfikacyjną oraz mechanizm rejestrowania nadpisań dla celów audytowych.

Wymagane elementy:

1. Skrypt `tools/verify_agent.py` udostępniający czystą, deterministyczną funkcję `verify(task_id, artifacts) -> VerdictReport` (bez wywołań modeli LLM).
2. Plik raportu `outputs/verification/<task_id>.json` stanowiący jedyne źródło prawdy o statusie zadania.
3. Skrypt `tools/override.py` dopisujący autoryzowane informacje o nadpisaniu reguł do pliku `outputs/verification/overrides.jsonl` (rekord must zawierać uzasadnienie, identyfikator użytkownika, znacznik czasu oraz kod powiązanego błędu).
4. Konfigurację potoku CI, który kończy się błędem, gdy flaga `passed` ma wartość `false`, i bezpośrednio wyświetla raport weryfikacji.
5. Dokument `docs/verification.md` opisujący każdy sprawdzany warunek, jego poziom istotności (severity), artefakt źródłowy oraz procedury nadpisywania.

Bezwzględne odrzucenia (Twarde kryteria):

- Weryfikacja opierająca się na odpytywaniu modeli LLM. Bramka weryfikacyjna to deterministyczny mechanizm techniczny; ocena z użyciem LLM jest zadaniem recenzenta.
- Możliwość nadpisania reguł przez agenta bez autoryzowanego (podpisanego) wpisu. Ignorowanie błędów jest uprawnieniem zastrzeżonym wyłącznie dla ludzi.
- Raport weryfikacji, który nie zawiera ścieżek do przeanalizowanych artefaktów. Raport musi umożliwiać pełny audyt.
- Naruszenia o statusie blokady, które potok CI mógłby zignorować lub wyciszyć. Status istotności jest definiowany na etapie sprawdzania warunku (zapis raportu), a nie podczas analizy wyników.

Zasady odmowy współpracy (Refusal rules):

- Jeśli w projekcie nie zdefiniowano polecenia testowego akceptacji, odmów wdrożenia bramki do czasu jego dodania. Bramka, która niczego nie weryfikuje, to jedynie pozór kontroli.
- Jeśli raport z weryfikacji reguł (`rule_report.json`) nie istnieje, odmów pominięcia tego kroku; weryfikacja musi zakończyć się błędem.
- Jeśli logi sprzężenia zwrotnego (`feedback_record.jsonl`) nie istnieją, odmów pominięcia weryfikacji kryteriów akceptacji; brak logów wykonania poleceń sam w sobie stanowi błąd blokujący.
- Jeśli rejestr nadpisań nie jest objęty kontrolą wersji (git), odmów wdrożenia mechanizmu nadpisywania; nieoficjalne obejścia niweczą sens istnienia bramki.

Struktura plików:

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

Na koniec dodaj sekcję „Co przeczytać dalej”, wskazującą na:

- Lekcję 39 poświęconą agentowi-recenzentowi (reviewer agent), podejmującemu ostateczną decyzję po uzyskaniu pozytywnego werdyktu.
- Lekcję 40 dotyczącą generatora przekazania prac (handoff generator), który załącza werdykt w wygenerowanym pakiecie.
- Lekcję 41 dotyczącą testowania bramki weryfikacyjnej na rzeczywistej aplikacji deweloperskiej.
