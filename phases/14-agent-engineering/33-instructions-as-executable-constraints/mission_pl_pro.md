# Misja - Instrukcje agenta jako ograniczenia wykonywalne

## Cel
Przekształć opisowe instrukcje w sprawdzalne maszynowo reguły w pięciu kategoriach i wygeneruj raport z walidacji reguł, który może zostać oceniony przez recenzenta.

## Wejścia
- `docs/agent-rules.md` z jedną regułą na nagłówek, z których każda zawiera kategorię, opis oraz pole `check`
- Przykładowe uruchomienie agenta, które celowo narusza dwie reguły

## Rezultaty
- Parser ładujący reguły z pliku `agent-rules.md` do obiektów typu dataclass
- Skrypt walidacyjny `rule_checker.py` zawierający funkcje sprawdzające dla każdego pola `check`
- Raport `rule_report.json` zawierający statusy pass/fail dla każdej reguły oraz zagregowany poziom ważności

## Kryteria akceptacji
- `python3 code/main.py` kończy się kodem wyjścia zero
- Standardowe wyjście (stdout) wyświetla przeanalizowany zestaw reguł, logi z uruchomienia oraz wyniki weryfikacji (pass/fail) dla każdej reguły
- Raport `rule_report.json` poprawnie wykrywa dwa zamierzone naruszenia reguł

## Poza zakresem
- Integracja modułu sprawdzającego z systemem CI. Lekcja kończy się wygenerowaniem raportu.
- Barierki ochronne platformy (OpenAI SDK, hooki/punkty przerwania w LangGraph). Zestaw reguł stanowi kontrakt, który te mechanizmy mają wdrożyć.

## Źródła
- `docs/pl.md` - pełna lekcja w języku polskim
- `code/main.py` - implementacja referencyjna
- `outputs/skill-rule-set-builder_pl.md` - wyodrębniona umiejętność
