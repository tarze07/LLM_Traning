---

name: skill-segmentation-mask-inspector
description: Raportuje rozkład klas, statystyki przewidywanej maski oraz klasy z niedoszacowanymi lub rozmytymi granicami
version: 1.0.0
phase: 4
lesson: 7
tags: [computer-vision, segmentation, debugging, evaluation]

---

# Inspektor maski segmentacji

Diagnozowanie rozbieżności między niską wartością funkcji straty (loss) a rzeczywistą jakością wizualną generowanych masek segmentacyjnych.

## Zastosowanie

- Zaraz po zakończeniu treningu, gdy wartość mIoU wygląda obiecująco, ale wizualna inspekcja masek wskazuje na błędy.
- Przed wdrożeniem produkcyjnym: kontrola rozkładu klas w predykcjach w porównaniu do maski rzeczywistej (ground-truth).
- Gdy współczynnik IoU dla danej klasy jest wysoki dla dużych obiektów, lecz niski dla małych.
- Debugowanie artefaktów na krawędziach masek, które nie wpływają znacząco na ogólne IoU ze względu na małą liczbę pikseli w obszarach granicznych.

## Dane wejściowe (Inputs)

- `preds`: (N, H, W) – tensor z przewidywanymi identyfikatorami klas (wyniki operacji argmax).
- `targets`: (N, H, W) – tensor z rzeczywistymi identyfikatorami klas (ground-truth).
- `num_classes`: liczba wszystkich zdefiniowanych klas (integer).
- Opcjonalnie `class_names`: lista zawierająca nazwy poszczególnych klas (list of strings).

## Procedura analizy

1. **Histogramy rozkładu klas na poziomie pikseli.**
   Oblicz procentowy udział pikseli dla każdej klasy w `preds` i `targets`. Oznacz etykietą ostrzegawczą każdą klasę, w której odchylenie względne przekracza 30%, tj. `|pred% - gt%| / max(gt%, 1e-6) > 0.30`. W przypadku klas, które w ogóle nie występują w masce rzeczywistej (`gt% == 0`), zgłoś ostrzeżenie, jeśli ich przewidywany udział procentowy przekroczy `0.3%` (0.003).

2. **IoU oraz metryka Boundary F1 (bF1) dla każdej klasy.**
   Współczynnik Boundary F1 (dokładność granic) obliczany jest poprzez dylatację (rozszerzenie) krawędzi maski o określony bufor (np. 3 piksele), a następnie wyznaczenie precyzji i czułości na tych krawędziach. Klasy, które osiągają wysokie IoU (> 0.7), lecz ich bF1 wynosi < 0.5, są oznaczane jako mające rozmyte lub niedokładne granice (blurring edges).

3. **Czułość (recall) dla małych obiektów.**
   Podziel każdą spójną składową (connected component) maski rzeczywistej na przedziały rozmiarowe: bardzo małe (tiny < 100 px), małe (small < 1000 px), średnie (medium < 10000 px) i duże (large >= 10000 px). Zgłoś czułość (recall) w każdym z tych przedziałów dla każdej klasy. Sytuacja, w której czułość dla bardzo małych obiektów wynosi poniżej 0.3, podczas gdy dla dużych przekracza 0.9, wskazuje na problem z zbyt małą rozdzielczością wejściową lub niedostatecznym efektywnym polem recepcyjnym (receptive field) modelu.

4. **Najczęstsze pomyłki klas (confusion pairs).**
   Dla każdej klasy zidentyfikuj kategorię, z którą jest najczęściej mylona (czyli najczęstszą błędną predykcję wewnątrz obszaru maski rzeczywistej danej klasy). Zgłoś 3 pary generujące najwięcej błędów.

5. **Ocena pewności predykcji / nasycenia (wymaga tensorów `probs` lub `logits`, a no nie tylko `preds`).**
   Jeśli użytkownik przekaże surowy rozkład prawdopodobieństwa `probs: (N, C, H, W)` dla każdego piksela, oblicz odsetek pikseli, w których maksymalne prawdopodobieństwo przekracza 0.99 (`probs.max(dim=1) > 0.99`). Wysoki odsetek takich pikseli dla danej klasy (> 90%) sugeruje nadmierną pewność siebie modelu (overconfidence), co wskazuje na potrzebę zastosowania techniki wygładzania etykiet (label smoothing) lub kalibracji prawdopodobieństwa. Jeśli dostępne są tylko wartości po operacji argmax (`preds`), pomiń ten krok i odnotuj to w raporcie.

## Format raportu (Report Format)

```
[mask-inspector]
  classes: C

[class distribution]
  name       gt %    pred %   delta
  ...

[metrics]
  class       IoU     bF1    recall_tiny  recall_small  recall_medium  recall_large
  ...

[confusion pairs]
  klasa A mylona z klasą B: <N> pikseli (najczęstsza)
  klasa B mylona z klasą A: <N> pikseli
  ...

[verdict]
  most impactful issue: <jedno zdanie podsumowujące najpoważniejszy problem>
```

## Zasady i wskazówki

- Sortuj wiersze z wynikami klas według malejącego udziału pikseli w masce rzeczywistej (GT), tak aby najczęstsze klasy były wyświetlane jako pierwsze.
- Oznacz klasy o współczynniku IoU < 0.4 lub bF1 < 0.3 jako krytyczne (`critical`).
- Jeśli głównym problemem jest niska czułość (recall) dla małych obiektów, zalecane rozwiązania to: trening na wyższej rozdzielczości obrazów, zmniejszenie kroku (stride) w końcowych warstwach kodera lub zastosowanie dekodera opartego na piramidzie cech (Feature Pyramid Network - FPN).
- Jeśli dominującym problemem jest niska wartość metryki bF1 (słaba precyzja krawędzi), zaleca się: wdrożenie funkcji strat uwzględniających kontury (np. Lovasz-Softmax lub Boundary Loss), stosowanie augmentacji testowej (TTA - Test-Time Augmentation) z odbiciem lustrzanym w poziomie lub dekodowanie bez nadmiernej redukcji wymiarów przestrzennych.
- Nigdy nie wypisuj indeksów klas jako jedynego identyfikatora; jeśli podano listę `class_names`, użyj nazw klas w każdym wierszu tabeli i raportu.
