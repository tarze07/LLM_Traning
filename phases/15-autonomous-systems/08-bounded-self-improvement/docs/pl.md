# Ograniczone projekty samodoskonalenia

> Badania skupiły się na czterech podstawowych metodach ograniczania pętli samodoskonalenia. Niezmienniki formalne, które muszą obowiązywać podczas każdej edycji. Kotwy wyrównujące, których nie można modyfikować. Ograniczenia wielocelowe, w których musi obowiązywać każdy wymiar (bezpieczeństwo, uczciwość, solidność), a nie tylko wydajność. Wykrywanie regresji, które wstrzymuje pętlę, gdy metryki historyczne sugerują utratę możliwości. Żaden z nich nie jest dowodem bezpieczeństwa — wyniki teorii informacji (złożoność Kołmogorowa, twierdzenie Loba) ograniczają to, co każdy system może udowodnić na temat swoich własnych następców. Są to środki łagodzące, które zwiększają koszt cichej awarii.

**Typ:** Ucz się
**Języki:** Python (stdlib, pętla ograniczona z kontrolą niezmienniczą)
**Wymagania wstępne:** Faza 15 · 07 (RSI), Faza 15 · 04 (DGM)
**Czas:** ~60 minut

## Problem

Symulator wyścigu przedstawiony w lekcji 7 pokazał, że małe różnice w szybkości łączą się, tworząc duże luki. Studium przypadku DGM z lekcji 4 pokazało, że pętle mogą aktywnie oszukiwać swoich własnych ewaluatorów. Obydwa wyniki wskazują na to samo pytanie inżynierskie: jakie ograniczenia można nałożyć na pętlę samodoskonalenia, tak aby ograniczenia nie mogły zostać po cichu osłabione przez samą pętlę?

Podsumowanie warsztatów RSI ICLR 2026 (openreview.net/pdf?id=OsPQ6zTQXV) identyfikuje cztery takie elementy pierwotne. Zarówno RSP v3.0 firmy Anthropic (lekcja 19), jak i FSF v3 firmy DeepMind (lekcja 20) odnoszą się do nich w progach możliwości. Prace Meta HyperAgents i platformy społecznościowe, takie jak SAHOO (marzec 2026 r.), wdrażają podzbiory w środowisku produkcyjnym.

Uczciwe kadrowanie: są to środki łagodzące. Wyniki teorii informacji ograniczały to, co każdy system może udowodnić na temat swojego następcy, a żaden obecny projekt nie rozwiązuje formalnie problemu. Dobrze ograniczona pętla jest bezpieczniejsza niż nieograniczona, ale nie jest bezpieczna w wartościach bezwzględnych.

## Koncepcja

### Element podstawowy 1: niezmienniki formalne

Niezmiennik to właściwość, która musi obowiązywać przed i po każdej samomodyfikacji. Przykłady:

- Dystrybucja wyników jest uwarunkowana stałym nagłówkiem (Lekcja 17).
- Żadne wywołanie narzędzia nie jest kierowane do nieautoryzowanego punktu końcowego.
- Zapisy do pamięci przechodzą przez zarejestrowaną, podpisaną ścieżkę.
- Hash modułu oceniającego jest zgodny z zatwierdzoną wersją.

Niezmienniki są sprawdzane przez kod zewnętrzny, którego pętla nie może edytować. Jeśli proponowana modyfikacja narusza niezmiennik, zostaje odrzucona. Wychwytuje to tryb manipulacji ewaluatorem w stylu DGM (lekcja 4).

Najtrudniejszą częścią jest wybranie niezmienników, które są niezbędne ze względów bezpieczeństwa i możliwe do obliczenia w rozsądnym czasie. Przesadne określenie postępu w przestojach; niedostateczne określenie pozwala pętli ominąć ważne właściwości.

### Prymityw 2: kotwice wyrównujące

Kotwica wyrównania to niezmienna reprezentacja głównego celu pętli, przypięta poza powierzchnią edycyjną pętli. Przykłady:

- Tekst konstytucyjny (Lekcja 17), który jest ładowany z lokalizacji tylko do odczytu przy każdym wywołaniu.
- Ewaluator w osobnym repozytorium z niezależną kontrolą dostępu.
- Manifest uprawnień do narzędzia podpisany przez człowieka i ponownie weryfikowany w każdym cyklu.

Rolą kotwicy jest zapobieganie obiektywnemu dryfowi. Pętla może poprawić sposób realizacji celu, ale nie może edytować celu.

Subtelny tryb awarii: kotwica, której pętla nie może edytować, może zostać zinterpretowana na nowo przez pętlę, która zmienia sposób odczytywania kotwicy. Konstytucyjna sztuczna inteligencja (lekcja 17) jest wyraźnie oparta na rozumowaniu, aby radzić sobie w nowych sytuacjach; w tej warstwie rozumowania żyje dryf interpretacji. Kotwy są konieczne, ale niewystarczające.

### Prymityw 3: ograniczenia wielocelowe

Pętla optymalizująca pojedynczy wynik skalarny znajdzie skróty. Pętla, która musi jednocześnie spełniać wiele twardych ograniczeń, ma mniej dostępnych skrótów. Typowe osie:

- Wydajność (benchmark na poziomie zadania)
- Bezpieczeństwo (oceny zespołu czerwonego, odsetek odmów w przypadku znanych-złych)
- Sprawiedliwość (różne granice wpływu na wrażliwe podgrupy)
- Solidność (zestawy testowe OOD, obsługa kontradyktoryjnych danych wejściowych)

Modyfikacja jest akceptowana tylko wtedy, gdy spełnione są wszystkie ograniczenia. Gubernator ds. kosztów z lekcji 13 wiąże to z ograniczeniami finansowymi. Llama Guard z lekcji 18 podłącza się jako oś bezpieczeństwa.

### Prymityw 4: wykrywanie regresji

Wyniki każdego cyklu porównuje się z rozkładami historycznymi. Spadek poza skonfigurowaną tolerancję wstrzymuje pętlę. Wychwytuje to cichą utratę wydajności, która w przeciwnym razie zostałaby wchłonięta przez średnią bieżącą, gdy pętla „poprawiła się” po jej przekroczeniu.

Praktyczna implementacja: przechowuj wyniki poszczególnych zadań z ostatnich N cykli. Każdy nowy cykl oblicza deltę dla każdego zadania. Jeśli jakakolwiek delta spadnie poniżej progu, cykl zostanie odrzucony i dokonana zostanie weryfikacja przez człowieka.

### Granice teorii informacji

Złożoność Kołmogorowa i twierdzenie Loba wyznaczają górne granice tego, co system może udowodnić o sobie. Formalna maszyna Godela Schmidhubera (lekcja 4) miała na celu osiągnięcie najwyższej takiej granicy; nikt nie ukończył nietrywialnego dowodu. Wynik Loba mówi: jeśli system w sposób możliwy do udowodnienia wierzy, że „zrobię X, jeśli udowodnię, że powinienem zrobić X”, wykona X, nie udowadniając, że powinien, co jest dobrze znanym błędem samoodniesienia.

Konsekwencje dla naszych prymitywów: nie mogą zamknąć problemu bezpieczeństwa. Sprawiają, że cicha awaria jest droższa. Złośliwa lub dryfowana pętla, która po cichu ominęłaby brakującą kontrolę, musi teraz aktywnie podważać jawną, czyli bardziej wykrywalną sygnaturę.

### Sprawdzony przykład

Załóżmy, że agent proponuje zmianę. Stos bramkowy:

1. Kontrole niezmiennicze: skróty modułów, manifest uprawnień narzędzia, nagłówek konstytucyjny.
2. Kontrola zakotwiczenia: stwierdzenie obiektywne pasuje do zatwierdzonej wersji (bajtowo lub semantycznie).
3. Ocena wielocelowa: osie wydajności, bezpieczeństwa, uczciwości, solidności.
4. Wykrywanie regresji: żadna oś nie spada bardziej niż tolerancja.

Aby edycja mogła zostać zastosowana, wszystkie cztery muszą przejść. Każda pojedyncza awaria wstrzymuje pętlę.

## Użyj tego

`code/main.py` uruchamia ograniczoną pętlę samodoskonalenia na zabawce w stylu DGM z lekcji 4, ale z czterema elementami podstawowymi nałożonymi na wierzch. Każdy prymityw można włączyć lub wyłączyć indywidualnie. Demonstracja polega na tym, że każdy element podstawowy przechwytuje określoną klasę niepowodzeń i że usunięcie dowolnego z nich umożliwia przejście tej klasy niepowodzeń.

## Wyślij to

`outputs/skill-bounded-loop-review.md` sprawdza proponowaną ograniczoną pętlę i ocenia, który z czterech elementów podstawowych jest faktycznie implementowany, w porównaniu do roszczeń.

## Ćwiczenia

1. Uruchom `code/main.py` z włączonymi wszystkimi operacjami podstawowymi. Potwierdź, że pętla nadal poprawia podstawową metrykę, nie pozwalając hackowi wygrać.

2. Wyłącz wykrywanie regresji. Skonstruuj wejście, które prowadzi do zaakceptowania cichej utraty zdolności.

3. Wyłącz ograniczenie wielu celów. Pokaż, że pętla zbiega się na osi wydajności, podczas gdy oś bezpieczeństwa spada.

4. Zaprojektuj kotwę wyrównującą dla środka kodującego. Jaki tekst, gdzie przechowywany, sprawdzany w jaki sposób?

5. Przeczytaj podsumowanie warsztatów RSI ICLR 2026. Wybierz jeden z czterech prymitywów i zaproponuj konkretne ulepszenie obecnego stanu wiedzy.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| Niezmienny | „Właściwość zawsze prawdziwa” | Właściwość sprawdzana przez kod zewnętrzny przed i po każdej edycji |
| Kotwica wyrównania | „Przypięty cel” | Niezmienna reprezentacja głównego celu poza powierzchnią edycyjną pętli |
| Ograniczenie wielocelowe | „Wszystkie osie muszą wytrzymać” | Wydajność, bezpieczeństwo, uczciwość, solidność — wszystko wymagane |
| Wykrywanie regresji | „Wstrzymaj po opuszczeniu” | Wstrzymaj pętlę, gdy historyczne delty metryk sugerują utratę możliwości |
| Kołmogorow związany | „Granica teorii informacji” | Ogranicza to, co system może udowodnić o swoim następcy |
| Twierdzenie Loba | „Pułapka samoodniesień” | System może działać zgodnie z „powinienem” bez udowadniania, że ​​powinien |
| Stos bram | „Sprawdzenie warstwowe” | Połączono wiele prymitywów; każda awaria powoduje odrzucenie edycji |
| Ograniczona poprawa | „Łagodzenie, a nie dowód” | Zwiększa koszty cichych awarii; nie zamyka problemu bezpieczeństwa |

## Dalsze czytanie

- [Podsumowanie warsztatów RSI ICLR 2026 (OpenReview)](https://openreview.net/pdf?id=OsPQ6zTQXV) — zbieżność czterech pierwotnych.
- [Polityka odpowiedzialnego skalowania firmy Anthropic, wersja 3.0](https://anthropic.com/responsible-scaling-policy/rsp-v3-0) — progi zdolności obejmujące wiele celów.
- [DeepMind Frontier Safety Framework v3](https://deepmind.google/blog/strengthening-our-frontier-safety-framework/) — monitorowanie zwodniczego dopasowania jako niezmienny prymityw.
- [Schmidhuber (2003). Maszyny Godela](https://people.idsia.ch/~juergen/goedelmachine.html) — formalnie udowodniony przodek tych prymitywów.
– [Anthropic — Konstytucja Claude’a (styczeń 2026 r.)](https://www.anthropic.com/news/claudes-constitution) — kotwica dostosowania oparta na powodach.