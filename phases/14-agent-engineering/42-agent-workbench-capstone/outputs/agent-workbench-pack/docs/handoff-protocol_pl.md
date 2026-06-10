# Protokół przekazania

Każda sesja kończy się pakietem przekazania zawierającym:

- podsumowanie
- zmienione_pliki
- polecenia_uruchom
- nieudane_próby
- open_risks (waga + szczegóły)
- next_action (jeden konkretny krok)
- verdict_pointer (ścieżki do weryfikacji + raporty z przeglądu)

Pakiet jest wysyłany zarówno jako handoff.md (ludzie), jak i handoff.json (następny agent).
Brakujące pola zatrzymują hak końca sesji.