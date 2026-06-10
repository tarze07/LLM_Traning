# Misja - Przekazanie wielu sesji

## Cel
Wygeneruj `handoff.md` i `handoff.json` z artefaktów środowiska roboczego na koniec sesji, aby następna sesja była produktywna w ciągu pierwszej minuty. Obie formy zawierają te same siedem pól; JSON wygrywa w przypadku braku porozumienia.

## Wejścia
- `agent_state.json`, `verification_report.json`, `review_report.json`, `feedback_record.jsonl` z wcześniejszych lekcji
- Siedem pól: podsumowanie, zmienione_pliki, polecenie_uruchomione, nieudane_próby, otwarte_ryzyko, następna_akcja, wskaźnik_werdyktu

## Elementy dostarczane
- Moduł ładujący `WorkbenchSnapshot` zawierający cztery artefakty
-`generate_handoff(snapshot) -> (markdown, payload)`
- Filtr sprzężenia zwrotnego, który wybiera ostatnie K rekordów i każde niezerowe wyjście
- `handoff.md` i `handoff.json` napisane obok skryptu

## Akceptacja
- `python3 code/main.py` wychodzi z zera
- Oba pliki zawierają wszystkie siedem pól i niepusty plik `next_action`
- Ponowne uruchomienie skryptu z tymi samymi danymi wejściowymi daje identyczny pakiet

## Poza zakresem
- Strategie zagęszczania (kompaktowy punkt końcowy Kodeksu, pięciostopniowy Kodeks Claude'a). Handoff zamyka sesję; zagęszczenie wydłuża się o jeden.
- Szablony PR. Przecenę można ponownie wykorzystać jako treść PR, ale lekcja kończy się na pliku.

## Referencje
- `docs/en.md` - pełna lekcja
- `code/main.py` - implementacja referencyjna
- `outputs/skill-handoff-generator.md` - wyodrębniona umiejętność