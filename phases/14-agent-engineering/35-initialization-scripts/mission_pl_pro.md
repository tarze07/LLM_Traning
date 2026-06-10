# Misja - Skrypty inicjalizacyjne dla agentów

## Cel
Zbuduj skrypt `init_agent.py`, który weryfikuje wersje środowiska uruchomieniowego, zainstalowane zależności, polecenie testowe, wymagane zmienne środowiskowe oraz aktualność pliku stanu. Skrypt powinien generować raport `init_report.json` i zatrzymywać działanie agenta z kodem błędu, jeśli jakikolwiek kluczowy test (blocker) zakończy się niepowodzeniem.

## Wejścia
- Repozytorium z plikiem `requirements.txt` (lub odpowiednikiem), poleceniem testowym oraz plikiem stanu środowiska pracy (z lekcji 34)
- Lista testów walidacyjnych (środowisko uruchomieniowe, zależności, ścieżki, zmienne środowiskowe, aktualność stanu, ostatnie znane dobre zatwierdzenie)

## Rezultaty
- Skrypt `init_agent.py` z funkcjami walidacyjnymi dla każdego testu, zwracającymi wynik w formacie `(name, status, detail)`
- Raport `init_report.json` zawierający szczegółowe wyniki testów oraz znacznik czasu
- Kod wyjścia różny od zera (niezerowy) w przypadku wykrycia błędu krytycznego (blocker)

## Kryteria akceptacji
- `python3 code/main.py` kończy się kodem wyjścia zero przy prawidłowej konfiguracji (happy path)
- Dwukrotne uruchomienie skryptu z rzędu jest idempotentne (wyniki różnią się wyłącznie znacznikiem czasu)
- Symulowany brak wymaganej zmiennej środowiskowej jest poprawnie odnotowywany w raporcie i powoduje zwrócenie niezerowego kodu wyjścia

## Poza zakresem
- Automatyczne instalowanie brakujących zależności. Skrypt jedynie zatrzymuje działanie i raportuje problem operatorowi w celu ręcznej naprawy.
- Wysyłanie zapytań do LLM w ramach testów walidacyjnych. Sondy muszą pozostać deterministyczne.

## Źródła
- `docs/pl.md` - pełna lekcja w języku polskim
- `code/main.py` - implementacja referencyjna
- `outputs/skill-init-script_pl.md` - wyodrębniona umiejętność
