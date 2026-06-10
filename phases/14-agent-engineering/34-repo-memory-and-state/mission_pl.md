# Misja - Pamięć Repo i trwały stan

## Cel
Autor schematów JSON dla `agent_state.json` i `task_board.json`, zbuduje `StateManager`, który ładuje, sprawdza poprawność, mutuje i zapisuje atomowo, a także udowadnia podróż w obie strony w dwóch turach.

## Wejścia
- Kształt stołu warsztatowego z trzema pilnikami z lekcji 32
- Walidator tylko stdlib obejmujący wymagane typy, wyliczenia, wzorce i elementy

## Elementy dostarczane
- `agent_state.schema.json` i `task_board.schema.json` obok kodu
- `StateManager.load`, `StateManager.update`, `StateManager.commit` z zapisami tymczasowymi i zmianą nazwy
- Uruchomienie demonstracyjne, które zmienia stan w ciągu dwóch tur i ładuje się czysto

## Akceptacja
- `python3 code/main.py` wychodzi z zera
- Zły zapis (brak wymaganego pola, złe wyliczenie) zostaje odrzucony i nie jest utrwalany
- `workdir/agent_state.json` po uruchomieniu sprawdza zgodność ze schematem

## Poza zakresem
- Zaplecze SQLite lub pamięci zewnętrznej. Plik lokalny jest lekcją.
- Punkty kontrolne LangGraph, bloki pamięci Letta. Ten sam pomysł, inne przechowywanie; poza zakresem tutaj.

## Referencje
- `docs/en.md` - pełna lekcja
- `code/main.py` - implementacja referencyjna
- `outputs/skill-state-schema.md` - wyodrębniona umiejętność