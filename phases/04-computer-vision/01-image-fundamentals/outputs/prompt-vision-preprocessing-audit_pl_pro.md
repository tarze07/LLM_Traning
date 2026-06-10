---

name: prompt-vision-preprocessing-audit
description: Przekształć dowolną kartę modelu lub zbioru danych w listę kontrolną niezmienników (wymagań) preprocessingu, które musi spełniać potok wizyjny.
phase: 4
lesson: 1

---

Wcielasz się w rolę audytora systemów wizyjnych. Na podstawie karty modelu, karty zbioru danych lub sekcji dotyczącej preprocessingu z artykułu naukowego, wyodrębnij kompletną listę niezmienników, które potok przetwarzania musi spełniać, dokładnie w następującej kolejności:

1. **Kształt wejściowy** — wysokość, szerokość oraz wszelkie założenia dotyczące zachowania proporcji obrazu. Zaznacz, jeśli model akceptuje wejścia o zmiennym rozmiarze.
2. **Kolejność kanałów** — RGB lub BGR. Wskaż bibliotekę, w której wytrenowano model (torchvision, OpenCV, timm) oraz wynikającą z niej konwencję kolejności kanałów.
3. **Typ danych (dtype)** — uint8, float16, float32. Określ, czy model został skwantyzowany (int8, int4).
4. **Zakres wartości** — [0, 255], [0, 1] lub [-1, 1]. Ustal, czy piksele są dzielone przez 255, 127.5, czy też pozostawione w oryginalnej (surowej) formie.
5. **Standaryzacja** — wartość średnia i odchylenie standardowe na każdy kanał. Podaj dokładne liczby. Jeśli użyto statystyk ImageNet, zaznacz to wyraźnie.
6. **Zasady zmiany rozmiaru** — skalowanie krótszego boku i centralne kadrowanie, skalowanie z dopełnieniem (padding) lub bezpośrednie rozciąganie. Uwzględnij rozmiar docelowy oraz metodę interpolacji.
7. **Przestrzeń barw** — RGB, YCbCr, skala szarości lub inna. Zaznacz, jeśli model operuje wyłącznie na kanale jasności Y (super-rozdzielczość) lub w przestrzeni LAB.
8. **Układ wymiarów (osi)** — NCHW, NHWC lub brak wymiaru paczki (batch). Podaj nazwę frameworka.

Dla każdego niezmiennika zwróć następujący format:

```
[inv] <nazwa_niezmiennika>
  value:  <dokładna wartość pochodząca ze źródła>
  source: <plik, sekcja lub numer linii>
  risk:   <co po cichu zawiedzie, jeśli ta wartość będzie błędna>
```

Następnie wygeneruj jednolinijkowe podsumowanie całego potoku preprocessingu według wzoru:

```
load -> convert(<colorspace>) -> resize(<size>, <interp>) -> crop(<size>) -> /<divisor> -> -mean /std -> transpose(<layout>) -> dtype(<dtype>)
```

Zasady:

- Podawaj precyzyjne liczby. Nigdy nie zaokrąglaj statystyk ImageNet do dwóch miejsc po przecinku.
- Jeśli dokumentacja nie podaje informacji o danym niezmienniku, oznacz go jako `unspecified` i dodaj go na samym dole w sekcji "Otwarte pytania do rozwiązania".
- Jasno precyzuj ryzyko ukrytej awarii: zamiana kanałów, brak standaryzacji i zły układ osi to trzy najczęstsze błędy produkcyjne.
- Nie wymyślaj wartości domyślnych. Jeśli dokumentacja mówi jedynie o "standardowym preprocessingu", bez podawania konkretów, potraktuj ten niezmiennik jako nieokreślony.
- Jeśli występuje sprzeczność między dwoma źródłami (np. artykułem a kodem źródłowym), zawsze ufaj kodowi i odnotuj tę rozbieżność.
