---

name: skill-content-classifier-integration
description: Trzy klasyfikatory po stronie wyjściowej (toksyczność, PII, wyciek instrukcji) za jednym routerem ważności z akcjami blokowania, redagowania, ostrzegania i rejestrowania
version: 1.0.0
phase: 19
lesson: 85
tags: [safety, classifier, output-filter]

---

# Integracja klasyfikatora treści

Trzy klasyfikatory, jeden router, cztery działania.

## Struktura werdyktu

```text
ClassifierVerdict
  name: str
  severity: none | low | medium | high
  score: float in [0, 1]
  findings: list[str]
```

## Tabela akcji

| Dotkliwość | Akcja | Efekt |
|---|---|---|
| wysoki | blok | wynik zastąpiony odmową polityczną |
| średni | zredagować | zastosowane w kolejności redaktory według klasyfikatorów |
| niski | ostrzegam | dane wyjściowe dostarczane z dołączoną miękką notatką |
| żaden | log | dane wyjściowe wysłane bez zmian, werdykt zarejestrowany |

## Zachowanie według klasyfikatora

- toksyczność – terminy nękające z białą granicą i małą kontrolą negacji w lewym oknie; redaguje do `[redacted-language]`
- pii - e-mail, telefon, numer SSN, karta z certyfikatem Luhn, IPv4; dotkliwość wzrasta w przypadku numeru SSN i ​​karty; redaguje każdy kształt do znacznika
- wyciek instrukcji - cosinus trygramu vs znany komunikat systemowy; skale dotkliwości nakładające się; redaguje pierwszą linię monitu systemowego

## Artefakt

`outputs/classifier_report.json` zawiera czasownik akcji, wagę, zredagowane dane wyjściowe i pełną listę werdyktów dla każdego przypadku.