---

name: patch-geometry-reader
description: Przeczytaj konfigurację ViT i utwórz token poprawki, parametry i analizę pamięci VRAM na potrzeby dalszego planowania VLM.
version: 1.0.0
phase: 12
lesson: 01
tags: [vit, patch-tokens, dinov2, siglip, vlm-backbone]

---

Biorąc pod uwagę konfigurację szkieletu wizji (rozmiar poprawki, rozdzielczość, ukryte przyciemnienie, głębokość, głowice, opcjonalne rejestry), utwórz analizę geometrii, która powie wywołującemu, ile tokenów wyemituje ten koder, ile VRAM kosztuje uruchomienie i czy jest to właściwy wybór dla dalszego zadania VLM lub gęstego przewidywania.

Wyprodukuj:

1. Siatka poprawek i długość sekwencji. Kształt siatki (H/P, W/P). Długość sekwencji, w tym CLS, rejestry i dowolny token łączenia. Podkreśl obsługę wielu rozdzielczości (NaFlex, AnyRes), gdy jest zadeklarowana.
2. Podział parametrów. Osadzanie łatek, osadzanie pozycji, bloki transformatorów (uwaga + MLP), końcowe LN, sumy zarówno dokładne, jak i czytelne dla człowieka (np. 86,4M).
3. FLOPy na napastnika. Uwaga (4 N D^2 + 2 N^2 D na blok) i MLP (16 N D^2 na blok), zsumowane według głębokości. Oznacz koszty kwadratowe w N, które będą przeszkadzać przy wysokiej rozdzielczości.
4. Oszacowanie pamięci VRAM. Pamięć aktywacji przy wnioskowaniu dla pojedynczego przesłania dalej na jednym obrazie plus pamięć podręczna równoważna KV, jeśli koder zasila dalszy LLM.
5. Zalecenie łączenia. CLS, średnia łatka, oparta na rejestrach lub pomijanie puli dla VLM, w oparciu o zadeklarowane dalsze zadanie.

Twarde odrzucenia:
- Dowolna analiza, która traktuje tokeny poprawek jako identyczne w pikselach z danymi wejściowymi. Projekcja jest wyuczoną mapą liniową; łaty są abstrakcyjnymi wektorami, a nie pikselami.
- Zgłaszanie CLS jest zawsze właściwym łączeniem. Nowoczesne ścieżki o gęstej strukturze i VLM całkowicie pomijają CLS.
- Traktowanie 2D-RoPE i wyuczonych osadzań pozycyjnych jako wymiennych, bez zwracania uwagi na elastyczność natywnej rozdzielczości w stylu NaFlex.

Zasady odmowy:
- Jeśli podana konfiguracja deklaruje rozmiar poprawki, który nie dzieli równomiernie rozmiaru obrazu, odmów — nie jest to konfiguracja kompatybilna z NaFlex bez zadeklarowanego schematu dopełniania.
- Jeśli dzwoniący poprosi o dokładne wyliczenie ciężarów dla zastrzeżonych modeli (Gemini, Claude, GPT-5), odmów – nie są one publikowane.
- Jeśli docelowa ilość pamięci VRAM w przypadku modelu klasy ViT-g/14 wynosi mniej niż 4 GB, odmów i zalecaj szkielet SigLIP SO400m/14 lub mniejszy.

Dane wyjściowe: jednostronicowa analiza geometrii zawierająca liczbę tokenów, zestawienie parametrów, oszacowanie wartości FLOP, budżet pamięci VRAM i zalecaną strategię łączenia. Zakończ akapitem „co dalej czytać” wskazującym na artykuł SigLIP 2 (arXiv:2502.14786) zawierający szczegóły NaFlex, artykuł DINOv2 na temat gęstych funkcji lub lekcję 12.06 na temat implementacji patch-n'-pack.