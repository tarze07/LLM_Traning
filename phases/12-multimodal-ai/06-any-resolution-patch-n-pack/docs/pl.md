# Wizja dowolnej rozdzielczości: Patch-n'-Pack i NaFlex

> Prawdziwe obrazy nie są kwadratami o wymiarach 224x224. Paragon to 9:16, wykres to 16:9, skan medyczny może mieć rozdzielczość 4096x4096, zrzut ekranu mobilnego to 9:19,5. Odpowiedź VLM sprzed 2024 r. – zmiana rozmiaru wszystkiego na stały kwadrat – zniweczyła sygnał, który umożliwia działanie OCR, rozumienia dokumentów i analizowania scen w wysokiej rozdzielczości. NaViT (Google, 2023) pokazało, że można spakować poprawki o zmiennej rozdzielczości w jedną partię transformatora z maskowaniem po przekątnej blokowej. M-RoPE (2024) firmy Qwen2-VL całkowicie porzucił tabele pozycyjne bezwzględne. AnyRes firmy LLaVA-NeXT połączył obrazy o wysokiej rozdzielczości w obraz podstawowy i podrzędny. Wariant NaFlex SigLIP 2 (2025) jest teraz domyślnym koderem dla otwartych VLM, które chcą, aby pojedynczy punkt kontrolny obsługiwał każdy współczynnik kształtu. Ta lekcja implementuje patch-n'-pack od początku do końca.

**Typ:** Kompilacja
**Języki:** Python (stdlib, paker łatek + maska po przekątnej)
**Wymagania wstępne:** Faza 12 · 01 (łatki ViT), Faza 12 · 05 (LLaVA)
**Czas:** ~120 minut

## Cele nauczania

- Spakuj poprawki z partii obrazów o zmiennej rozdzielczości w jedną sekwencję i zbuduj maskę uwagi o przekątnej blokowej.
- Wybierz pomiędzy płytkami AnyRes (LLaVA-NeXT), NaFlex (SigLIP 2) i M-RoPE (Qwen2-VL) dla danego zadania.
- Oblicz budżety tokenów dla OCR, wykresów i fotografii bez zmiany rozmiaru.
- Wymień trzy tryby niepowodzenia zmiany rozmiaru kwadratu: zgnieciony tekst, przycięta treść, zmarnowane tokeny na dopełnienie.

## Problem

Transformatory oczekują sekwencji. Partia to stos sekwencji o tej samej długości. Jeśli Twoje obrazy mają rozmiar 224x224, za każdym razem otrzymasz 196 tokenów łatek, dopełnienie nie jest wymagane, zadanie wykonane. Trenuj na 224, wnioskuj na 224, nigdy więcej nie myśl o rozdzielczości.

Świat nie współpracuje. Dokumenty są w formacie pionowym (8,5 x 11 cali, 2:3). Zrzuty ekranu wykresów są w orientacji poziomej (16:9). Paragony są wysokie i cienkie (1:3). Obrazowanie medyczne jest dostarczane w rozdzielczości 2048 x 2048 lub większej. Zrzuty ekranu z urządzeń mobilnych mają rozdzielczość 1170 x 2532 (0,46:1).

Trzy opcje sprzed 2024 r. i dlaczego każda z nich kończy się niepowodzeniem:

1. Zmień rozmiar na stały kwadrat (224x224 lub 336x336). Zgniecenie zniekształca tekst i twarze. Zmniejszenie skali niszczy etykiety wykresów i zawartość OCR. Standardowa praktyka aż do LLaVA-1.5.
2. Przytnij do stałego współczynnika proporcji. Wyrzucasz większość obrazu, a wybór miejsca przycięcia jest problemem związanym z widzeniem.
3. Podkładka do najdłuższego boku. Naprawia zniekształcenia, ale marnuje ponad 50% tokenów na dopełnienie obrazów portretowych. Kwadratowy koszt uwagi na wszystkich tych żetonach padów.

Odpowiedź na lata 2024–2025: pozwól transformatorowi zjadać poprawki w natywnej rozdzielczości obrazu i wymyśl, jak spakować heterogeniczną partię w jedną sekwencję bez marnowania mocy obliczeniowej.

## Koncepcja

### NaViT i pakiety poprawek

Artykułem, który pokazał, że to działa na dużą skalę, był NaViT (Dehghani i in., 2023). Pomysł jest mechaniczny:

1. Dla każdego obrazu w partii oblicz jego natywną siatkę fragmentów przy wybranym rozmiarze fragmentu (powiedzmy 14).
2. Spłaszcz obszary każdego obrazu, tworząc własną sekwencję o zmiennej długości.
3. Połącz wszystkie poprawki obrazów w jedną długą sekwencję dla partii.
4. Zbuduj maskę uwagi o przekątnej blokowej, tak aby plamy obrazu A znajdowały się tylko na obrazie A.
5. Przenoszenie informacji o pozycji na łatce (osadzenia w 2D RoPE lub ułamkowej pozycji).

Partia trzech obrazów o wymiarach 336 x 336 (576 tokenów), 224 x 224 (256 tokenów) i 448 x 336 (768 tokenów) tworzy jedną sekwencję 1600 tokenów z maską o przekątnej 1600 x 1600. Brak wyściółki. Bez zbędnych obliczeń. Transformator obsługuje dowolne proporcje.

NaViT wprowadziło także ułamkowe usuwanie łatek podczas treningu — losowe upuszczanie 50% łatek w całej partii — co zarówno reguluje, jak i przyspiesza trening. SigLIP 2 odziedziczył to.

### AnyRes (LLaVA-NeXT)

AnyRes firmy LLaVA-NeXT jest pragmatyczną alternatywą. Biorąc pod uwagę obraz o wysokiej rozdzielczości i stały koder (CLIP lub SigLIP w 336), umieść obraz sąsiadująco:

1. Wybierz układ siatki z predefiniowanego zestawu — (1x1), (1x2), (2x1), (1x3), (3x1), (2x2) itp. — który najlepiej pasuje do proporcji obrazu.
2. Umieść pełny obraz w siatce; każda płytka staje się przycięciem o wymiarach 336 x 336.
3. Utwórz także miniaturę: rozmiar całego obrazu został zmieniony na 336x336 jako token kontekstu globalnego.
4. Zakoduj każdą płytkę za pomocą zamrożonego kodera 336. Połącz żetony płytek i żetony miniatur.

Dla obrazu o wymiarach 672 x 672 w siatce 2 x 2 plus miniatura: 4 * 576 + 576 = 2880 tokenów wizualnych. Drogie, ale skuteczne — LLM widzi zarówno szczegóły lokalne, jak i kontekst globalny.

AnyRes to trasa z wyboru, gdy koder jest zablokowany i obsługuje tylko jedną rozdzielczość. Eksploduje liczbę tokenów dla dużych obrazów (obraz 1344x1344 w siatce 4x4 to 9216 + 576 ≈ 9800 tokenów, co wypełnia większość kontekstu LLM 8k).

### Lina M (Qwen2-VL)

Qwen2-VL wprowadził wielomodalne osadzanie w pozycji obrotowej. Zamiast pozycji ułamkowych NaViT lub kafelków i miniatur AnyRes, każda łatka zawiera pozycję 3D (czas, wysokość, szerokość). Rotacje zapytań/kluczy obsługują dowolną długość H, W i czasową.

M-RoPE zapewnia natywną dynamiczną rozdzielczość bez konieczności ponownego szkolenia. Podsumowując, podajesz dowolny obraz HxW, moduł osadzający łatę generuje tokeny H/14 x W/14, każdy token otrzymuje swoją pozycję (t=0, r=rząd, c=col), RoPE obraca uwagę z właściwymi częstotliwościami i gotowe. Kontynuują to Qwen2.5-VL i Qwen3-VL. V2PE InternVL3 to ten sam pomysł ze zmiennym kodowaniem dla każdej modalności.

W przeciwieństwie do AnyRes, M-RoPE to tokeny O(H x W / P^2) w natywnej rozdzielczości — bez narzutu na kafelki multiplikatywne. W przeciwieństwie do NaViT nadal oczekuje jednego obrazu na przesyłanie dalej. Przesyłanie wsadowe w różnych rozdzielczościach nadal wymaga łatania i pakowania.

### NaFlex (SigLIP 2)

NaFlex to natywny tryb elastyczny punktu kontrolnego SigLIP 2. Pojedynczy model obsługuje wiele długości sekwencji (256, 729, 1024 tokenów) podczas wnioskowania. Wewnętrznie wykorzystuje patch-n'-pack w stylu NaViT podczas treningu i bezwzględne pozycje ułamkowe na patch. Punkt sprzedaży: jeden punkt kontrolny, wybierz budżet tokenów na podstawie wniosków na podstawie zadania.

Za zadanie semantyczne (klasyfikacja, wyszukiwanie) 256 tokenów. Do OCR lub zrozumienia wykresów 1024 tokeny. Żadnego przekwalifikowania.

### Maska pakowania

Większość implementacji potyka się z maską po przekątnej blokowej. W przypadku upakowanej sekwencji o długości `N_total` obejmującej obrazy `i=0..B-1` o długościach `n_i` maska `M` kształtu `(N_total, N_total)` wynosi 1, jeśli oba indeksy mieszczą się w bloku tego samego obrazu, w przeciwnym razie 0. Możesz go zbudować z listy skumulowanej długości:

```
offsets = [0, n_0, n_0+n_1, ..., N_total]
M[i, j] = 1 iff there exists b where offsets[b] <= i < offsets[b+1] and offsets[b] <= j < offsets[b+1]
```

To jest jedna linia w PyTorch z `torch.block_diag` lub jawnym zbieraniem. Ścieżka FlashAttention o zmiennej długości (`cu_seqlens`) całkowicie pomija maskę i uczestniczy w sekwencjach bezpośrednio przy użyciu tensora skumulowanej długości — ~10 razy szybciej niż gęsta maska ​​dla typowych partii.

### Budżety tokenowe

Wybierz strategię według zadania:

- OCR/dokumenty: 1024-4096 tokenów. SigLIP 2 NaFlex w 1024 lub AnyRes 3x3 + miniatura.
- Wykresy i interfejs użytkownika: 729-1024 tokenów przy 384-448 natywnych. Dynamiczna rozdzielczość Qwen2.5-VL z maksymalną liczbą pikseli.
- Zdjęcia naturalne: 256-576 tokenów w zupełności wystarczy. Dalszy LLM widzi wystarczająco dużo. Płać za tokeny, w których gęstość treści jest wysoka.
- Wideo: 64-128 tokenów na klatkę po łączeniu przestrzennym, 2-8 FPS. Lekcja 12.17 omawia ten temat.

Reguła produkcyjna na rok 2026: wybierz limit maksymalnej liczby pikseli na zadanie, zakoduj w natywnych proporcjach aż do tego limitu, spakuj partię i pomiń dopełnianie. Qwen2.5-VL udostępnia `min_pixels` i `max_pixels` dla dokładnie tego pokrętła.

## Użyj tego

`code/main.py` implementuje patch-n'-pack dla heterogenicznej partii obrazów o współrzędnych w pikselach będących liczbami całkowitymi. To:

- Wykonuje listę rozmiarów obrazu (wys., szer.).
- Oblicza długość sekwencji fragmentów każdego obrazu w rozmiarze patcha 14.
- Pakuje je w jedną sekwencję o łącznej długości `sum(n_i)`.
- Buduje blokowo-przekątną maskę uwagi (gęstą, dla przejrzystości).
- Porównuje koszt opakowania w porównaniu ze zmianą rozmiaru kwadratu i układaniem płytek AnyRes.
- Drukuje tabelę budżetu tokenowego dla partii mieszanej (paragon, wykres, zrzut ekranu, zdjęcie).

Uruchom to. Liczby, które odpadają, są powodem, dla którego każdy otwarty VLM w 2026 roku korzysta z poprawki i pakietu.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-resolution-budget-planner.md`. Biorąc pod uwagę obciążenie pracą o mieszanych proporcjach (OCR, wykresy, zdjęcia, klatki wideo) i całkowity budżet tokenów, wybiera właściwą strategię (NaFlex, AnyRes, M-RoPE lub stały kwadrat) i emituje konfigurację na żądanie. Użyj tej umiejętności, gdy dopasujesz VLM do produktu — zapobiega to cichemu 10-krotnemu powiększeniu tokena, który zabija budżety opóźnień.

## Ćwiczenia

1. Paragon ma wymiary 600x1500 (1:2,5). Ile tokenów rozdzielczości natywnej przy rozmiarze łatki 14? Ile po zmianie rozmiaru kwadratu na 336? Co w praktyce traci większą dokładność OCR?

2. Zbuduj maskę o przekątnej blokowej dla grupy czterech obrazów o długościach 256, 576, 729, 1024. Sprawdź, czy macierz uwagi ma wymiary 2585 x 2585 i zawiera dokładnie `256^2 + 576^2 + 729^2 + 1024^2` niezerowe wpisy.

3. Dla obrazu 1792x896 w patchu 14 porównaj: (a) zmianę rozmiaru do kwadratu na 336, a następnie zakodowanie, (b) AnyRes 2x1 + miniatura, (c) M-RoPE w wersji natywnej. Który wykorzystuje najmniej tokenów? Który zachowuje najwięcej szczegółów?

4. Zaimplementuj ułamkowe usuwanie łatek: biorąc pod uwagę spakowaną sekwencję, upuść losowo równomiernie 50% tokenów i odpowiednio zaktualizuj maskę po przekątnej. Zmierz zmianę rzadkości maski.

5. Przeczytaj sekcję 3.2 artykułu Qwen2-VL (arXiv:2409.12191). Opisz w dwóch zdaniach, co kontrolują `min_pixels` i `max_pixels` i dlaczego obie granice mają znaczenie.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Patch-n'-pack | „Opakowanie w stylu NaViT” | Połącz sekwencje łat o zmiennej długości z różnych obrazów w jeden wymiar wsadowy |
| Maska blokowo-diagonalna | „Maska do pakowania” | Maska uwagi, która ogranicza obszary każdego obrazu tak, aby zajmowały się tylko sobą, a nie sąsiadami w stadzie |
| DowolnaRes | „Układanie płytek LLaVA-NeXT” | Podziel obraz o wysokiej rozdzielczości na siatkę płytek o stałym rozmiarze i globalną miniaturę; zakoduj każdą płytkę za pomocą stałego kodera |
| NaFlex | „Natywny Flex SigLIP 2” | Pojedynczy punkt kontrolny SigLIP 2 obsługujący budżety 256/729/1024 tokenów przy wnioskowaniu bez ponownego szkolenia |
| Lina M | „Lina multimodalna” | Kodowanie pozycji obrotowej 3D (czas, wiersz, kolumna), które obsługuje dowolne H, W, T bez tabel pozycji |
| cu_seqlens | „Pakowanie FlashAttention” | Tensor długości skumulowanej używany w ścieżce FlashAttention varlen zamiast gęstej maski blokowo-przekątnej |
| min_piksele / maks._piksele | „Granice rozdzielczości” | Pokrętła Qwen2.5-VL na żądanie ograniczające liczbę tokenów na bardzo małych lub bardzo dużych wejściach |
| Budżet tokena wizualnego | „Ile tokenów na obraz” | Przybliżona liczba tokenów poprawek emitowanych na obraz; ustala budżet i koszt uwagi LLM |

## Dalsze czytanie

- [Dehghani i in. — Patch n' Pack: NaViT (arXiv:2307.06304)](https://arxiv.org/abs/2307.06304)
- [Wang i in. — Qwen2-VL (arXiv:2409.12191)](https://arxiv.org/abs/2409.12191)
- [Laurençon i in. — Co jest ważne przy budowaniu modeli wizjonersko-językowych? (Idefiks2, arXiv:2405.02246)](https://arxiv.org/abs/2405.02246)
- [Tschannen i in. — SigLIP 2 (arXiv:2502.14786)](https://arxiv.org/abs/2502.14786)
— [Zespół Qwen — raport techniczny Qwen2.5-VL (arXiv:2502.13923)](https://arxiv.org/abs/2502.13923)