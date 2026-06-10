# Misja – Agent recenzenta: Rozdzielenie roli wykonawcy i weryfikatora

## Cel
Zbuduj pętlę agenta-recenzenta, która odczytuje w trybie tylko do odczytu artefakty wygenerowane przez wykonawcę (buildera) i zapisuje raport `review_report.json` oceniający pracę w pięciu wymiarach (suma punktów max 10) wraz z werdyktem `pass`, `soft_fail` lub `hard_fail`.

## Wejścia
- Obiekt `ReviewerInputs` agregujący zmiany (diff), stan środowiska, logi (feedback) oraz werdykt bramki z poprzednich lekcji
- Wymiary rubryki ocen: zgodność z problemem, dyscyplina zakresu, założenia projektowe, jakość weryfikacji oraz gotowość do przekazania

## Produkty (Deliverables)
- Odrębna, deterministyczna funkcja oceny dla każdego z wymiarów (zaimplementowana statycznie na potrzeby lekcji)
- Generator raportu `review_report.json` zawierający oceny cząstkowe, sumę punktów i werdykt końcowy
- Dwa przypadki testowe: poprawna modyfikacja oraz zmiana typu „testy zaliczone, ale rozwiązano niewłaściwy problem”

## Kryteria akceptacji
- Polecenie `python3 code/main.py` kończy działanie z kodem wyjścia 0
- Poprawna modyfikacja otrzymuje co najmniej 7 punktów i werdykt `pass`
- Zmiana dotycząca niewłaściwego problemu spada poniżej progu 5 punktów w co najmniej jednym wymiarze, co skutkuje werdyktem `hard_fail`

## Poza zakresem
- Rzeczywiste wywołania modeli LLM. Lekcja definiuje reguły i logikę każdego wymiaru; zastąpienie ich zapytaniami do modeli LLM następuje na późniejszym etapie wdrożenia.
- Edycja kodu lub zmian (diff). Recenzent wyłącznie analizuje, ocenia i raportuje. Wprowadzanie poprawek należy do wykonawcy w kolejnym kroku pętli.

## Materiały odniesienia
- `docs/en.md` – pełna lekcja
- `code/main.py` – implementacja referencyjna
- `outputs/skill-reviewer-agent.md` – wyodrębniona umiejętność
