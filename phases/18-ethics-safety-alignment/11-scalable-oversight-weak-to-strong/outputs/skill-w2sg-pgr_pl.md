---

name: w2sg-pgr
description: Przeprowadź audyt skalowalnego nadzoru lub roszczenia W2SG za pomocą metryki odzyskanej luki w wydajności.
version: 1.0.0
phase: 18
lesson: 11
tags: [scalable-oversight, weak-to-strong, pgr, debate, recursive-reward-modeling]

---

Biorąc pod uwagę skalowalny nadzór lub dokument/raport W2SG, sprawdź, czy konfiguracja potwierdza swoje twierdzenia.

Wyprodukuj:

1. Słaba/silna identyfikacja. Wyraźnie nazwij słabego przełożonego i mocny model. Czy lukę w możliwościach mierzy się parametrami, tokenami szkoleniowymi, wynikami testów porównawczych lub oceną dotyczącą konkretnego zadania?
2. Definicja sufitu. Jaki jest nadzorowany pułap zadania przez silnego modela? Bez sufitu nie można obliczyć PGR.
3. Obliczenia PGR. PGR = (dostrojony - słaby) / (sufit - słaby). Sprawdź znak, wielkość i mianownik. Małe mianowniki sztucznie zawyżają PGR.
4. Wstępna kontrola szczelności. Czy dane przedtreningowe silnego modelu obejmują podstawową prawdę zadania? Jeśli tak, „odzyskiwanie” może oznaczać wcześniejsze odzyskanie informacji, a nie uogólnienie.
5. Podział na dopasowanie i możliwości. Czy luka między słabymi a mocnymi wynika z luki w możliwościach czy luki w dostosowaniu? Burns i in. Rok 2023 wyraźnie wskazuje, że różnica między nimi wynika z możliwości; luki w kształcie linii trasowania mogą zachowywać się inaczej.

W przypadku audytów mechanizmów skalowalnego nadzoru:
- Debata: określ wiedzę sędziego, strukturę dyskutującego oraz to, czy zadanie nagradza dążenie do prawdy. Cytuj Khana i in. 2024 (arXiv:2402.06782) o tym, gdzie debata pomaga, a gdzie kończy się niepowodzeniem.
- RRM: zidentyfikuj głębokość rekurencji i co się stanie, jeśli U+1 jest już niegodny zaufania.
- Dekompozycja zadań: należy określić procedurę dekompozycji i sprawdzić, czy podzadania można niezależnie sprawdzić.

Twarde odrzucenia:
- Wszelkie roszczenia PGR bez pułapu na złotych etykietach.
- Każde twierdzenie W2SG, które twierdzi, że rozwiązuje wyrównanie - W2SG mierzy odzyskiwanie zdolności, a nie dostosowanie.
- Wszelkie twierdzenia oparte na mechanizmie debaty, które ignorują literaturę empiryczną z 2024 r. dotyczącą tego, kiedy debata pomaga, a kiedy szkodzi.

Zasady odmowy:
- Jeśli użytkownik zapyta „czy W2SG rozwiązuje superosiowość”, odrzuć odpowiedź binarną i wyjaśnij, że PGR jest mierzalny, a nie rozwiązaniem.
- Jeśli użytkownik zapyta, który skalowalny mechanizm nadzoru jest najlepszy, odmów – odpowiedź zależy od zadania.

Wynik: jednostronicowy audyt, który wypełnia pięć powyższych sekcji, raportuje lub żąda PGR oraz wskazuje, czy luka między słabymi a mocnymi stronami ma kształt zdolności czy dostosowania. Cytuj Burns i in. 2023 oraz Lang i in. (arXiv:2501.13124) raz każdy.