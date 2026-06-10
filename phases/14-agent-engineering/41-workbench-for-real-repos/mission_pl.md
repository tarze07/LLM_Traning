# Misja - Środowisko pracy na prawdziwym repozytorium

## Cel
Uruchom to samo zadanie sprawdzania poprawności `/signup` za pomocą potoku wymagającego tylko podpowiedzi i potoku prowadzonego przez środowisko robocze w odniesieniu do tej samej przykładowej aplikacji, a następnie wyemituj raport porównawczy przed/po, który będzie mógł przeczytać sceptyk.

## Wejścia
- `sample_app/` z `app.py` (brak walidacji), `test_app.py` (jeden test szczęśliwej ścieżki), `README.md`, `scripts/release.sh` jako przynęta w strefie zabronionej
- Obydwa potoki są w pełni oskryptowane, bez prawdziwych wywołań LLM

## Elementy dostarczane
- `code/main.py` koordynujący oba rurociągi w oparciu o to samo urządzenie
- `before-after-report.md` z tabelą pięciu wyników
- `comparison.json` dla dalszych map

## Akceptacja
- `python3 code/main.py` wychodzi z zera
- Raport mierzy wszystkie pięć wyników: faktycznie przeprowadzone testy, akceptację, pliki poza zakresem, jakość przekazania, liczbę recenzentów
— Potok środowiska warsztatowego jest lepszy od potoku bezpośredniego w przypadku co najmniej czterech z pięciu

## Poza zakresem
- Podłączenie prawdziwego LLM. Potoki są oskryptowane pod kątem powtarzalności.
- Strojenie modelu. Porównanie utrzymuje model na stałym poziomie konstrukcyjnym.

## Referencje
- `docs/en.md` - pełna lekcja
- `code/main.py` - implementacja referencyjna
- `outputs/skill-workbench-benchmark.md` - wyodrębniona umiejętność