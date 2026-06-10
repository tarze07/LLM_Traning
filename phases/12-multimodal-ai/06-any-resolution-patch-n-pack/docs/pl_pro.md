# Wizja w dowolnej rozdzielczości: Patch-n'-Pack i NaFlex

> Rzeczywiste obrazy rzadko są idealnymi kwadratami o wymiarach 224x224. Paragon ma proporcje 9:16, wykres 16:9, skan medyczny może mieć rozdzielczość 4096x4096, a zrzut ekranu z telefonu 9:19,5. Podejście stosowane w modelach VLM przed 2024 rokiem — polegające na skalowaniu każdego obrazu do stałego kwadratu — niszczyło kluczowe informacje, które umożliwiają skuteczne działanie systemów OCR, analizowanie dokumentów oraz rozpoznawanie detali w wysokiej rozdzielczości. Model NaViT (Google, 2023) udowodnił, że patche o zmiennych proporcjach można efektywnie pakować w jedną paczkę (batch) transformatora za pomocą blokowo-diagonalnego maskowania uwagi. Z kolei mechanizm M-RoPE (2024) wprowadzony w Qwen2-VL całkowicie wyeliminował potrzebę stosowania bezwzględnych kodowań pozycyjnych. Metoda AnyRes w LLaVA-NeXT dzieli natomiast obrazy o wysokiej rozdzielczości na mniejsze kafelki podrzędne. Opracowany w 2025 roku wariant NaFlex dla modelu SigLIP 2 stał się domyślnym encoderem dla otwartych modeli VLM, które wymagają obsługi dowolnego formatu obrazu przez pojedynczy checkpoint. W tej lekcji zaimplementujemy potok Patch-n'-Pack od początku do końca.

**Typ:** Projekt / Implementacja
**Języki:** Python (biblioteka standardowa, pakowanie patchy + maskowanie blokowo-diagonalne)
**Wymagania wstępne:** Faza 12 · Lekcja 01 (patche ViT), Faza 12 · Lekcja 05 (LLaVA)
**Czas:** ~120 minut

## Cele nauczania

- Spakuj patche z zestawu obrazów o zmiennej rozdzielczości w jedną sekwencję i zbuduj dla niej blokowo-diagonalną maskę uwagi.
- Dobierz odpowiednią strategię dla danego zadania spośród: AnyRes (LLaVA-NeXT), NaFlex (SigLIP 2) oraz M-RoPE (Qwen2-VL).
- Oblicz budżet tokenów dla zadań typu OCR, analizy wykresów oraz fotografii bez konieczności zmiany proporcji obrazu.
- Wskaż trzy rodzaje błędów wynikających ze skalowania obrazów do kwadratu: zniekształcony tekst, obcięta zawartość oraz marnowanie tokenów na padding.

## Problem

Transformatory przetwarzają dane w postaci sekwencji. Tradycyjna paczka (batch) to stos sekwencji o równej długości. Jeśli Twoje obrazy mają rozmiar 224x224, z każdego otrzymasz dokładnie 196 tokenów patchy, padding nie jest wymagany i problem z głowy. Trenujesz na rozdzielczości 224, wnioskujesz na 224 i nie musisz myśleć o rozdzielczości.

Jednak rzeczywiste dane nie są tak regularne. Dokumenty mają orientację pionową (np. 8,5 x 11 cali, proporcje 2:3). Wykresy są panoramiczne (16:9). Paragony są wąskie i długie (1:3). Obrazy medyczne mają rozdzielczości rzędu 2048 x 2048 lub większe. Zrzuty ekranu z telefonów mają np. rozdzielczość 1170 x 2532 (0,46:1).

Trzy podejścia stosowane przed 2024 rokiem i powody ich porażki:

1. Skalowanie do stałego kwadratu (224x224 lub 336x336). Powoduje zniekształcenia tekstu i twarzy. Zmniejszenie rozdzielczości niszczy małe czcionki i uniemożliwia działanie OCR. Była to standardowa praktyka aż do modelu LLaVA-1.5.
2. Przycinanie (cropping) do stałych proporcji. Wiąże się z utratą większości obrazu, a wybór optymalnego obszaru kadrowania to osobny, skomplikowany problem wizyjny.
3. Dopełnianie (padding) do dłuższego boku. Zapobiega zniekształceniom, ale marnuje ponad 50% budżetu tokenów na puste wypełnienie przy obrazach portretowych. W dodatku płacisz pełen koszt obliczeniowy uwagi za te niepotrzebne tokeny paddingu.

Rozwiązanie z lat 2024–2025: pozwól transformatorowi przetwarzać patche w natywnej rozdzielczości obrazu i zaimplementuj pakowanie zróżnicowanej paczki w jedną sekwencję, eliminując straty mocy obliczeniowej.

## Koncepcja

### NaViT i pakowanie patchy (Patch Packing)

Publikacją, która wykazała skuteczność tej metody na dużą skalę, była praca NaViT (Dehghani et al., 2023). Idea opiera się na prostym procesie:

1. Dla każdego obrazu w paczce oblicz jego natywną siatkę patchy dla wybranego rozmiaru patcha (np. 14x14).
2. Spłaszcz patche każdego obrazu do postaci sekwencji o zmiennej długości.
3. Połącz (skonkatenuj) sekwencje patchy ze wszystkich obrazów w jedną długą sekwencję.
4. Zbuduj blokowo-diagonalną maskę uwagi, dzięki czemu patche z obrazu A wchodzą w interakcje wyłącznie z innymi patchami z obrazu A.
5. Przekaż informacje o pozycji dwuwymiarowej patcha za pomocą 2D RoPE lub ułamkowego kodowania pozycyjnego.

Paczka składająca się z trzech obrazów o wymiarach odpowiednio: 336x336 (576 tokenów), 224x224 (256 tokenów) oraz 448x336 (768 tokenów) tworzy jedną spakowaną sekwencję o długości 1600 tokenów z maską o wymiarach 1600 x 1600. Brak paddingu. Brak marnowania cykli procesora. Transformator bez problemu przetwarza dowolne proporcje.

NaViT wprowadziło także technikę ułamkowego odrzucania patchy (fractional patch dropping) podczas treningu — polegającą na losowym odrzucaniu 50% patchy w paczce. Działa to zarówno jako regularyzacja, jak i przyspieszenie treningu. Metodę tę zaadaptowano również w modelu SigLIP 2.

### AnyRes (LLaVA-NeXT)

Technika AnyRes w LLaVA-NeXT to pragmatyczna alternatywa. Mając obraz o wysokiej rozdzielczości oraz encoder o stałym rozmiarze wejścia (np. CLIP lub SigLIP pracujący na rozdzielczości 336x336), proces kafelkowania wygląda następująco:

1. Wybierz układ siatki z predefiniowanego zestawu — np. (1x1), (1x2), (2x1), (1x3), (3x1), (2x2) — który najlepiej odpowiada proporcjom obrazu.
2. Wpisz pełen obraz w wybraną siatkę; każdy kafelek (tile) staje się osobnym wycinkiem o rozmiarze 336x336.
3. Utwórz także miniaturę: cały obraz jest skalowany do rozmiaru 336x336 i służy jako kontekst globalny.
4. Zakoduj każdy kafelek osobnym przebiegiem encodera. Skonkatenuj tokeny wszystkich kafelków oraz tokeny miniatury globalnej.

Dla obrazu o wymiarach 672x672 przetworzonego w układzie siatki 2x2 wraz z miniaturą otrzymujemy: 4 * 576 + 576 = 2880 tokenów wizualnych. Jest to kosztowne rozwiązanie, ale bardzo skuteczne — model LLM otrzymuje zarówno precyzyjne detale lokalne, jak i kontekst globalny.

AnyRes to optymalny wybór, gdy używasz zamrożonego encodera o stałej rozdzielczości wejściowej. Wadą jest jednak szybki wzrost liczby tokenów dla bardzo dużych obrazów (np. obraz 1344x1344 w siatce 4x4 daje 9216 + 576 ≈ 9800 tokenów, co potrafi przepełnić standardowy kontekst LLM 8k).

### M-RoPE (Qwen2-VL)

Qwen2-VL wprowadził wielomodalne rotacyjne kodowanie pozycyjne (Rotary Position Embedding). Zamiast ułamkowego kodowania z NaViT czy kafelków i miniatur z AnyRes, każdy patch otrzymuje pozycję trójwymiarową (czas, wysokość, szerokość). Rotacje wektorów zapytań i kluczy (Q/K) naturalnie obsługują dowolne wartości H, W oraz wymiar czasowy (wideo).

M-RoPE pozwala na natywną obsługę dynamicznych rozdzielczości bez potrzeby zmiany architektury. Podajesz obraz o dowolnym rozmiarze HxW, moduł patch embeddingu generuje wejściowe tokeny w liczbie H/14 x W/14, a każdy token otrzymuje swoje współrzędne (t=0, wiersz, kolumna). Następnie mechanizm RoPE odpowiednio modyfikuje uwagą z właściwymi częstotliwościami. Rozwiązanie to jest rozwijane w modelach Qwen2.5-VL oraz Qwen3-VL. Podobną ideę (V2PE) z adaptacyjnym kodowaniem dla różnych modalności stosuje InternVL3.

W odróżnieniu od AnyRes, M-RoPE generuje liczbę tokenów proporcjonalną do rzeczywistego rozmiaru O(H x W / P^2) — eliminując narzut kafelkowania. Z kolei w przeciwieństwie do NaViT, model przetwarza pojedyncze obrazy. Spakowanie paczki o zróżnicowanych rozdzielczościach wciąż wymaga procedury pakowania (packing).

### NaFlex (SigLIP 2)

NaFlex to elastyczny tryb natywny wprowadzony w modelu SigLIP 2. Pojedynczy checkpoint pozwala na wybór długości sekwencji wejściowej (np. 256, 729, 1024 tokeny) na etapie wnioskowania bez potrzeby dotrenowywania. Pod maską model wykorzystuje technikę Patch-n'-Pack w stylu NaViT podczas treningu oraz bezwzględne ułamkowe kodowanie pozycji na poziomie patchy. Główny atut: jeden checkpoint, elastyczny dobór budżetu tokenów w zależności od zadania.

W zadaniach semantycznych (klasyfikacja, wyszukiwanie) wystarczy 256 tokenów. W zadaniach OCR czy analizie wykresów można wybrać 1024 tokeny — wszystko bez modyfikacji modelu.

### Maska pakowania (Packing Mask)

Najczęstszym problemem przy implementacji jest poprawne generowanie blokowo-diagonalnej maski uwagi. Dla spakowanej sekwencji o łącznej długości `N_total`, składającej się z obrazów `i=0..B-1` o długościach `n_i`, maska `M` o kształcie `(N_total, N_total)` przyjmuje wartość 1, jeśli oba indeksy należą do tego samego obrazu, w przeciwnym razie 0. Maskę tę można wygenerować na podstawie listy skumulowanych długości:

```
offsets = [0, n_0, n_0+n_1, ..., N_total]
M[i, j] = 1 wtedy i tylko wtedy, gdy istnieje b, dla którego offsets[b] <= i < offsets[b+1] oraz offsets[b] <= j < offsets[b+1]
```

W PyTorch można to zrealizować w jednej linijce za pomocą funkcji `torch.block_diag`. Z kolei implementacje oparte na FlashAttention dla zmiennych długości (`cu_seqlens`) całkowicie pomijają tworzenie jawnej maski i przetwarzają sekwencje bezpośrednio na podstawie wektora skumulowanych długości — co jest około 10 razy szybsze niż operowanie na gęstej masce dla typowych rozmiarów paczek.

### Dobór budżetu tokenów

Strategię należy dobrać bezpośrednio pod typ zadania:

- OCR i analiza dokumentów: 1024-4096 tokenów. SigLIP 2 NaFlex skonfigurowany na 1024 tokeny lub AnyRes w układzie 3x3 z miniaturą.
- Analiza wykresów i interfejsów użytkownika: 729-1024 tokeny przy rozdzielczości natywnej 384-448. Dynamiczna rozdzielczość w Qwen2.5-VL z ograniczoną maksymalną liczbą pikseli.
- Zdjęcia naturalne: w zupełności wystarczy 256-576 tokenów. Model LLM ma wystarczająco dużo informacji. Warto płacić za tokeny tylko tam, gdzie gęstość informacji jest wysoka.
- Dane wideo: 64-128 tokenów na klatkę przy zastosowaniu poolingu przestrzennego, przy próbkowaniu 2-8 FPS. Szczegółowo omawia to Lekcja 12.17.

Złota zasada produkcyjna w 2026 roku: zdefiniuj maksymalny limit pikseli dla danego zadania, zakoduj obraz w jego natywnych proporcjach do tego limitu, spakuj paczkę i unikaj paddingu. Model Qwen2.5-VL udostępnia do tego celu parametry `min_pixels` i `max_pixels`.

## Użycie praktyczne

Skrypt `code/main.py` implementuje procedurę Patch-n'-Pack dla paczki obrazów o zróżnicowanych rozdzielczościach. Kod:

- Pobiera listę rozmiarów obrazów (wysokość, szerokość).
- Oblicza długość sekwencji patchy dla każdego obrazu przy rozmiarze patcha 14.
- Pakuje je w jedną sekwencję o łącznej długości `sum(n_i)`.
- Generuje gęstą blokowo-diagonalną maskę uwagi w celach demonstracyjnych.
- Porównuje narzut tokenów przy pakowaniu w stosunku do skalowania do kwadratu oraz kafelkowania AnyRes.
- Wypisuje tabelę podsumowującą budżet tokenów dla zróżnicowanej paczki (paragon, wykres, zrzut ekranu, zdjęcie).

Uruchomienie skryptu pozwala naocznie przekonać się, dlaczego w 2026 roku wszystkie otwarte modele VLM wykorzystują techniki pakowania patchy.

## Zadanie zaliczeniowe

W ramach tej lekcji należy stworzyć dokument `outputs/skill-resolution-budget-planner_pro.md`. Na podstawie opisu obciążeń o zróżnicowanych proporcjach (zadania OCR, wykresy, zdjęcia, klatki wideo) oraz zadanego limitu tokenów, dobierz optymalną strategię (NaFlex, AnyRes, M-RoPE lub stały kwadrat) i wygeneruj odpowiednią konfigurację parametrów. Umiejętność ta jest kluczowa przy wdrażaniu modeli VLM do systemów produkcyjnych — zapobiega ona niekontrolowanemu wzrostowi liczby tokenów, który negatywnie wpływa na opóźnienia (latency).

## Ćwiczenia

1. Paragon ma wymiary 600x1500 (proporcje 1:2,5). Ile tokenów wygeneruje w rozdzielczości natywnej przy rozmiarze patcha 14x14? Ile tokenów wygeneruje po przeskalowaniu do kwadratu 336x336? Które podejście w praktyce spowoduje większą utratę dokładności w zadaniu OCR?

2. Wygeneruj blokowo-diagonalną maskę uwagi dla paczki czterech obrazów o długościach sekwencji odpowiednio: 256, 576, 729 oraz 1024. Upewnij się, że macierz uwagi ma wymiar 2585 x 2585 i zawiera dokładnie `256^2 + 576^2 + 729^2 + 1024^2` elementów niezerowych.

3. Dla obrazu o wymiarach 1792x896 i rozmiarze patcha 14, porównaj: (a) skalowanie do kwadratu 336x336 i kodowanie, (b) AnyRes w układzie 2x1 z miniaturą globalną, (c) natywny format M-RoPE. Które z tych rozwiązań zużywa najmniej tokenów? Które zachowuje najwięcej szczegółów?

4. Zaimplementuj ułamkowe odrzucanie patchy (fractional patch dropping): napisz funkcję, która losowo odrzuca dokładnie 50% tokenów ze spakowanej sekwencji i odpowiednio aktualizuje blokowo-diagonalną maskę uwagi. Zmierz wpływ tej operacji na rzadkość (sparsity) maski.

5. Przeczytaj sekcję 3.2 w artykule o Qwen2-VL (arXiv:2409.12191). Opisz w dwóch zdaniach, za co odpowiadają parametry `min_pixels` oraz `max_pixels` i dlaczego określenie obu tych granic jest istotne.

## Słownik pojęć

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|-----------------|--------------------------------------|
| Patch-n'-pack | „Pakowanie w stylu NaViT” | Metoda łączenia sekwencji patchy o zmiennej długości z różnych obrazów w jeden wspólny wymiar paczki (batch). |
| Maska blokowo-diagonalna | „Maska pakowania” | Maska uwagi, która ogranicza przepływ informacji tak, że patche z danego obrazu wchodzą w interakcje tylko ze sobą nawzajem. |
| AnyRes | „Kafelkowanie w LLaVA-NeXT” | Podział obrazu o wysokiej rozdzielczości na siatkę kafelków o stałym rozmiarze oraz globalną miniaturę; każdy element jest kodowany osobno. |
| NaFlex | „Native Flex w SigLIP 2” | Wariant modelu SigLIP 2 pozwalający na dynamiczny dobór budżetu tokenów (np. 256/729/1024) przy wnioskowaniu bez zmian w wagach. |
| M-RoPE | „Wielomodalne RoPE” | Kodowanie pozycyjne 3D (czas, wiersz, kolumna) pozwalające na bezproblemowe przetwarzanie obrazów o dowolnym kształcie H, W i czasie T. |
| cu_seqlens | „Długości sekwencji FlashAttention” | Wektor skumulowanych długości sekwencji przekazywany bezpośrednio do FlashAttention zamiast stosowania jawnej maski blokowej. |
| min_pixels / max_pixels | „Limity rozdzielczości” | Parametry konfiguracyjne w Qwen2.5-VL pozwalające ograniczyć minimalną i maksymalną liczbę tokenów wizualnych na obraz. |
| Budżet tokenów wizualnych | „Liczba tokenów na obraz” | Docelowa liczba tokenów patchy generowana dla pojedynczego obrazu; określa narzut na warstwy uwagi modelu LLM. |

## Dalsze czytanie

- [Dehghani et al. — Patch n' Pack: NaViT (arXiv:2307.06304)](https://arxiv.org/abs/2307.06304)
- [Wang et al. — Qwen2-VL (arXiv:2409.12191)](https://arxiv.org/abs/2409.12191)
- [Laurençon et al. — What matters when building vision-language models? (Idefics2, arXiv:2405.02246)](https://arxiv.org/abs/2405.02246)
- [Tschannen et al. — SigLIP 2 (arXiv:2502.14786)](https://arxiv.org/abs/2502.14786)
- [Qwen Team — Qwen2.5-VL Technical Report (arXiv:2502.13923)](https://arxiv.org/abs/2502.13923)
