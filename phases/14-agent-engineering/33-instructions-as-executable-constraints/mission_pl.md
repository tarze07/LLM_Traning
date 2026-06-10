# Misja - Instrukcje agenta jako ograniczenia pliku wykonywalnego

## Cel
Zamień instrukcje pisarskie w reguły sprawdzalne maszynowo w pięciu kategoriach i wygeneruj raport o regułach, który będzie mógł ocenić recenzent.

## Wejścia
- `docs/agent-rules.md` z jedną regułą na nagłówek, każdy nośnik, kategorię, opis i pole `check`
- Uruchomienie agenta demonstracyjnego, które celowo narusza dwie zasady

## Elementy dostarczane
- Parser ładujący `agent-rules.md` do klasy danych
- Funkcje w stylu `rule_checker.py`, po jednej dla każdego odniesienia do `check`
- `rule_report.json` z pass/fail dla każdej reguły i łączną ważnością

## Akceptacja
- `python3 code/main.py` wychodzi z zera
- Dane wyjściowe wyświetlają przeanalizowany zestaw reguł, przebieg przebiegu oraz wynik pozytywny/nieudany dla każdej reguły
- `rule_report.json` wyłapuje dwa zamierzone naruszenia

## Poza zakresem
- Podłączenie kontrolera do CI. Lekcja kończy się pisemnym sprawozdaniem.
- Poręcze szkieletowe (OpenAI SDK, przerwania LangGraph). Zbiór zasad to czytelna dla człowieka umowa, którą wdrażają.

## Referencje
- `docs/en.md` - pełna lekcja
- `code/main.py` - implementacja referencyjna
- `outputs/skill-rule-set-builder.md` - wyodrębniona umiejętność