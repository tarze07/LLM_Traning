# Misja - Pamięć repozytorium i trwały stan

## Cel
Opracuj schematy JSON dla plików `agent_state.json` oraz `task_board.json`. Zaimplementuj klasę `StateManager` wykonującą atomowy odczyt, walidację, modyfikację i zapis stanu, oraz wykaż spójność zapisu i odczytu danych (round-trip) w trakcie dwuturowego przebiegu testowego.

## Wejścia
- Struktura środowiska pracy składająca się z trzech plików (z lekcji 32)
- Walidator oparty wyłącznie na bibliotece standardowej Pythona, obsługujący reguły: `required`, `type`, `enum`, `pattern`, `items`

## Rezultaty
- Pliki schematów `agent_state.schema.json` oraz `task_board.schema.json` umieszczone obok kodu
- Metody `StateManager.load`, `StateManager.update` oraz `StateManager.commit` obsługujące zapis do pliku tymczasowego i atomową zmianę nazwy
- Kod demonstracyjny modyfikujący stan w ciągu dwóch tur i wczytujący go poprawnie po restarcie

## Kryteria akceptacji
- `python3 code/main.py` kończy się kodem wyjścia zero
- Każda próba nieprawidłowego zapisu (brak wymagane pola, błędna wartość enum itp.) jest blokowana i nie uszkadza pliku stanu
- Wygenerowany plik `workdir/agent_state.json` przechodzi pomyślnie walidację ze swoim schematem

## Poza zakresem
- Integracja z bazą SQLite lub zewnętrznymi systemami przechowywania danych. Tematem tej lekcji są operacje na plikach lokalnych.
- Konfiguracja checkpointów w LangGraph czy bloków pamięci Letta.

## Źródła
- `docs/pl.md` - pełna lekcja w języku polskim
- `code/main.py` - implementacja referencyjna
- `outputs/skill-state-schema_pl.md` - wyodrębniona umiejętność
