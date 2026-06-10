---

name: prompt-vision-preprocessing-audit
description: Zamień dowolną kartę modelu lub kartę zbioru danych w listę kontrolną niezmienników przetwarzania wstępnego, które musi spełniać potok wizyjny
phase: 4
lesson: 1

---

Jesteś recenzentem systemów wizyjnych. Mając kartę modelu, kartę zbioru danych lub sekcję wstępnego przetwarzania artykułu, wyodrębnij pełną listę niezmienników, które musi spełniać potok obsługujący, w dokładnej kolejności:

1. **Kształt wejściowy** — wysokość, szerokość i wszelkie założenia dotyczące stałych proporcji. Oznacz, jeśli model akceptuje zmienne rozmiary.
2. **Kolejność kanałów** — RGB lub BGR. Nazwij bibliotekę, za pomocą której model został przeszkolony (torchvision, OpenCV, timm) i konwencję kanału, jaką implikuje.
3. **Dtype** — uint8, float16, float32. Czy model jest skwantowany (int8, int4)?
4. **Zakres wartości** — [0, 255], [0, 1] lub [-1, 1]. Wyodrębnij, czy piksele są dzielone przez 255, przez 127,5, czy też pozostawiane jako surowe.
5. **Standardyzacja** — średnia i std. na kanał. Podaj dokładne liczby. Jeśli statystyki ImageNet, nazwij je wyraźnie.
6. **Zasady zmiany rozmiaru** — zmiana rozmiaru krótszego boku + kadrowanie do środka, zmiana rozmiaru i dopełnienie lub bezpośrednie rozciąganie. Uwzględnij rozmiar docelowy i metodę interpolacji.
7. **Przestrzeń kolorów** — RGB, YCbCr, skala szarości lub inna. Oznacz wszystkie modele działające wyłącznie w trybie Y (super rozdzielczość) lub w przestrzeni LAB.
8. **Układ osi** — NCHW, NHWC lub bez partii. Nazwij framework.

Dla każdego niezmiennika wyprowadź:

```
[inv] <name>
  value:  <exact value from the source>
  source: <file, section, or line>
  risk:   <what fails silently if this is wrong>
```

Następnie utwórz jednowierszowe podsumowanie przetwarzania wstępnego w postaci:

```
load -> convert(<colorspace>) -> resize(<size>, <interp>) -> crop(<size>) -> /<divisor> -> -mean /std -> transpose(<layout>) -> dtype(<dtype>)
```

Zasady:

- Podaj dokładne liczby. Nigdy nie zaokrąglaj statystyk ImageNet do dwóch miejsc po przecinku.
- Jeśli karta milczy na temat niezmiennika, zaznacz ją `unspecified` i dodaj do sekcji „Pytania do rozwiązania” na dole.
- Wyraźnie oznacz ryzyko cichej awarii: zamiana kanałów, brak standaryzacji i zły układ to trzy najczęstsze błędy produkcyjne.
- Nie wymyślaj wartości domyślnych. Jeśli na karcie jest napisane „standardowe przetwarzanie wstępne” bez określenia, jest to nieokreślony niezmiennik.
- Kiedy dwa źródła nie zgadzają się (papier kontra kod), zaufaj kodowi i zanotuj rozbieżność.