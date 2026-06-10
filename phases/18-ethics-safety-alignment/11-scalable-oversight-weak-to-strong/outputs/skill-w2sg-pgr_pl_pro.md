---
name: w2sg-pgr
description: Przeprowadź audyt założeń skalowalnego nadzoru lub generalizacji W2SG za pomocą metryki odzyskanej luki w wydajności (PGR).
version: 1.0.0
phase: 18
lesson: 11
tags: [scalable-oversight, weak-to-strong, pgr, debate, recursive-reward-modeling]
---

Na podstawie artykułu lub raportu dotyczącego skalowalnego nadzoru lub generalizacji W2SG, zweryfikuj, czy konfiguracja eksperymentalna uzasadnia stawiane tezy.

Wyprodukuj:

1. Identyfikacja słabego i silnego komponentu. Wskaż jednoznacznie słabego nadzorcę oraz silny model. W jaki sposób mierzona jest luka w zdolnościach (liczba parametrów, tokeny treningowe, wyniki w benchmarkach czy ewaluacja dedykowana dla danego zadania)?
2. Określenie pułapu wydajności (ceiling). Jaki jest maksymalny poziom wydajności (pułap) silnego modelu trenowanego na etykietach referencyjnych? Bez wyznaczenia tego pułapu obliczenie PGR jest niemożliwe.
3. Wyliczenie wskaźnika PGR. Oblicz: PGR = (wynik po dostrojeniu - wynik słabego) / (pułap - wynik słabego). Zweryfikuj znak wartości, jej rząd wielkości oraz mianownik (małe wartości w mianowniku sztucznie zawyżają wskaźnik PGR).
4. Weryfikacja wycieku wiedzy (prior leakage). Czy dane z etapu przedtreningowego silnego modelu zawierają etykiety referencyjne (ground truth) dla danego zadania? Jeśli tak, „odzyskanie” luki może wynikać z odtworzenia zapamiętanych informacji (prior retrieval), a nie z rzeczywistego uogólniania.
5. Podział na dopasowanie i zdolności. Czy różnica między słabym a silnym modelem wynika z luki w zdolnościach (capability gap), czy w dopasowaniu (alignment gap)? Burns i in. (2023) wprost wskazują, że badana przez nich luka dotyczy zdolności; luki w dopasowaniu mogą zachowywać się w odmienny sposób.

W przypadku audytów mechanizmów skalowalnego nadzoru:
- Debata (Debate): określ poziom wiedzy sędziego, strukturę uczestników debaty oraz to, czy konstrukcja zadania faworyzuje wypowiedzi prawdziwe (truth-leans). Przytocz wnioski z pracy Khan i in. (2024, arXiv:2402.06782) na temat tego, w jakich obszarach debata pomaga, a w jakich zawodzi.
- Rekurencyjne modelowanie nagród (RRM): zidentyfikuj głębokość rekurencji oraz przeanalizuj konsekwencje sytuacji, w której model U+1 jest już niegodny zaufania.
- Dekompozycja zadań: opisz procedurę podziału zadania i zweryfikuj, czy poszczególne podzadania mogą być oceniane niezależnie.

Twarde odrzucenia:
- Jakiekolwiek deklaracje dotyczące wskaźnika PGR bez wyznaczenia pułapu wydajności na etykietach referencyjnych (gold labels).
- Twierdzenia, jakoby generalizacja W2SG rozwiązywała problem dopasowania (alignment) – W2SG mierzy odzyskiwanie zdolności (capabilities), a nie dopasowanie.
- Wnioski oparte na protokole debaty, które ignorują doniesienia empiryczne z 2024 roku określające, kiedy debata przynosi korzyści, a kiedy szkodzi procesowi oceny.

Zasady odmowy:
- Jeśli użytkownik zapyta: „Czy W2SG rozwiązuje problem superdopasowania?”, odmów udzielenia jednoznacznej odpowiedzi tak/nie i wyjaśnij, że PGR to jedynie mierzalna metryka postępu, a nie gotowe rozwiązanie.
- Jeśli użytkownik zapyta, który z mechanizmów skalowalnego nadzoru jest najlepszy, odmów udzielenia odpowiedzi – wskazanie zależy bezpośrednio od charakteru zadania.

Wynik: Jednostronicowy raport z audytu, który pokrywa pięć powyższych punktów, podaje lub wymaga podania wartości PGR oraz precyzuje, czy różnica między słabym a silnym modelem ma charakter luki w zdolnościach, czy w dopasowaniu. Należy jednokrotnie zacytować pracę Burns i in. (2023) oraz Lang i in. (arXiv:2501.13124) w tekście.
