# Protokół przekazania

Każda sesja musi zakończyć się wygenerowaniem pakietu przekazania (handoff) zawierającego następujące elementy:

- podsumowanie
- zmienione_pliki
- polecenia_uruchom
- nieudane_próby
- open_risks (waga + szczegóły)
- next_action (jedno konkretne działanie)
- verdict_pointer (ścieżki do weryfikacji + raporty z przeglądu)

Pakiet jest zapisywany zarówno w formacie `handoff.md` (dla ludzi), jak i `handoff.json` (do odczytu przez kolejnego agenta).
Brak jakichkolwiek wymaganych pól przerywa działanie skryptu kończącego sesję (post-session hook).
