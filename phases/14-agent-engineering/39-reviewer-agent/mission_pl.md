# Misja – Agent recenzenta: Oddziel Konstruktora od Markera

## Cel
Zbuduj pętlę recenzenta, która odczytuje artefakty konstruktora w trybie tylko do odczytu i emituje ocenę `review_report.json` w pięciu wymiarach, w sumie na 10, z werdyktem pozytywny, soft_fail lub hard_fail.

## Wejścia
- `ReviewerInputs` łączący różnicę, stan, informację zwrotną i werdykt z poprzednich lekcji
- Wymiary rubryk: dopasowanie problemu, dyscyplina zakresu, założenia, jakość weryfikacji, gotowość do przekazania

## Elementy dostarczane
- Jedna funkcja punktacji na wymiar (ocena pośrednia dla lekcji, deterministyczna)
- Pisarz `review_report.json` z pięcioma wynikami, sumą i werdyktem
- Dwa przypadki demonstracyjne: czysta zmiana i zmiana „właściwe testy, zły problem”.

## Akceptacja
- `python3 code/main.py` wychodzi z zera
- Czysta zmiana otrzymuje co najmniej 7 punktów z werdyktem `pass`
- Zmiana dotycząca błędnego problemu spada poniżej 5 w co najmniej jednym wymiarze i werdykt zostaje zmieniony na `hard_fail`

## Poza zakresem
- Prawdziwe połączenia LLM. Lekcja opisuje każdy wymiar; umiejętność zamienia się później w modelu.
- Edycja różnicy. Recenzent czyta, ocenia i raportuje. Łatki to zadanie budowniczego w następnej turze.

## Referencje
- `docs/en.md` - pełna lekcja
- `code/main.py` - implementacja referencyjna
- `outputs/skill-reviewer-agent.md` - wyodrębniona umiejętność