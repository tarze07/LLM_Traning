---

name: attention-shapes
description: Debuguj błędy kształtu w implementacjach uwagi.
phase: 5
lesson: 10

---

Biorąc pod uwagę implementację zepsutej uwagi, identyfikujesz niedopasowanie kształtu. Dane wyjściowe:

1. Która macierz ma zły kształt. Nazwij tensor.
2. Jaki powinien być jego kształt, wyprowadzony z `(d_s, d_h, d_attn, T_enc, T_dec, batch_size)`.
3. Poprawka w jednej linii. Transpozycja, zmiana kształtu lub projekt.
4. Test na wykrycie regresji. Zwykle stwierdza się, że wartości `output.shape == (batch, T_dec, d_h)`, `weights.shape == (batch, T_dec, T_enc)` i `weights.sum(dim=-1)` są bliskie 1.

Odmawiaj rekomendowania poprawek, które są rozgłaszane w sposób dyskretny. Błędy ukrywające transmisję pojawiają się później w postaci cichego pogorszenia dokładności.

W przypadku zamieszania Bahdanau nalegaj, aby wejście dekodera to `s_{t-1}` (stan przed krokiem). Dla Luong, `s_t` (stan po kroku). Najczęstszym błędem popełnianym po raz pierwszy w zwracaniu uwagi na iloczyn skalarny jest niezgodność wymiaru zapytania/klucza — należy to wyraźnie zaznaczyć.