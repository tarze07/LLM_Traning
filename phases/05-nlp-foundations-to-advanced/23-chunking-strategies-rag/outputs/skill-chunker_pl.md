---

name: chunker
description: Wybierz strategię fragmentowania, rozmiar i nakładanie się dla danego korpusu i dystrybucji zapytań.
version: 1.0.0
phase: 5
lesson: 23
tags: [nlp, rag, chunking]

---

Biorąc pod uwagę korpus (typy dokumentów, średnią długość, domenę) i rozkład zapytań (faktoid/analityczny/wiele przeskoków), wynik:

1. Strategia. Rekurencyjne / zdanie / semantyczne / dokument nadrzędny / późne / kontekstowe. Powód.
2. Rozmiar kawałka. Liczba tokenów. Powód powiązany z typem zapytania.
3. Nakładanie się. Domyślnie 0; uzasadnij, jeśli >0.
4. Egzekucja minimalna/maks. Osłony `min_tokens`, `max_tokens`.
5. Plan ewaluacji. Recall@5 na warstwowym zestawie ewaluacyjnym składającym się z 50 zapytań (faktoid, analityczny, multi-hop).

Odrzuć jakąkolwiek strategię dzielenia na porcje bez wymuszania minimalnego/maksymalnego rozmiaru porcji. Odmówić nakładania się powyżej 20% bez ablacji pokazującej, że to pomaga. Oznacz rekomendacje dotyczące fragmentacji semantycznej bez minimalnej wartości minimalnej.