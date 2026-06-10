---

name: lm-baseline
description: Przed szkoleniem neuronowego LM zbuduj powtarzalny model bazowy języka n-gramowego.
phase: 5
lesson: 16

---

Biorąc pod uwagę korpus i zastosowanie docelowe (przewidywanie następnego słowa, ponowna punktacja, poziom bazowy zakłopotania), wynik:

1. Rząd N-gramowy. Trygram dla ogólnego języka angielskiego, 4 gramy, jeśli korpus jest duży, 5 gramów dla ponownej oceny mowy.
2. Wygładzanie. Domyślnym ustawieniem jest zmodyfikowany Kneser-Ney; Laplace'a tylko do nauczania.
3. Biblioteka. `kenlm` do produkcji, `nltk.lm` do nauczania, rzuć własne tylko po to, aby nauczyć się matematyki.
4. Ocena. Utrzymujące się zakłopotanie przy spójnej tokenizacji między zestawami pociągowymi i testowymi.

Odmów zgłaszania zakłopotania obliczonego przy różnej tokenizacji między porównywanymi systemami — liczby zakłopotania są porównywalne tylko przy identycznej tokenizacji. Oznacz współczynnik OOV w zestawie testowym; KN słabo radzi sobie z OOV, chyba że podczas szkolenia zarezerwujesz specjalny token `<UNK>`.