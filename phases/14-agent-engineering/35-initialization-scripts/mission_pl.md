# Misja - Skrypty inicjujące dla agentów

## Cel
Zbuduj `init_agent.py`, który sprawdza czas wykonania, zależności, polecenie testowe, zmienne środowiskowe i świeżość stanu, a następnie zapisuje `init_report.json` i głośno zatrzymuje sesję, gdy zawiedzie sonda ważności bloku.

## Wejścia
- Repozytorium z `requirements.txt` (lub odpowiednikiem), poleceniem testowym i plikiem stanu środowiska roboczego z lekcji 34
- Tabela sondująca z lekcji (czas wykonania, deps, ścieżki, env, świeżość stanu, ostatnie znane dobre zatwierdzenie)

## Elementy dostarczane
- `init_agent.py` z jedną funkcją na sondę zwracającą `(name, status, detail)`
- `init_report.json` zawierający pełny zestaw sond i znacznik czasu
- Niezerowe wyjście w przypadku awarii sondy o ważności bloku

## Akceptacja
- `python3 code/main.py` wychodzi z zera na szczęśliwą ścieżkę
- Uruchomienie go dwa razy z rzędu nie jest możliwe, z wyjątkiem znacznika czasu
- Symulowana brakująca sonda env var pojawia się w raporcie i odwraca kod wyjścia

## Poza zakresem
- Automatyczna instalacja brakujących zależności. Scenariusz zatrzymuje się i wypływa na powierzchnię; człowiek naprawia.
- Wywoływanie LLM z sondy. Sondy pozostają deterministyczne.

## Referencje
- `docs/en.md` - pełna lekcja
- `code/main.py` - implementacja referencyjna
- `outputs/skill-init-script.md` - wyodrębniona umiejętność