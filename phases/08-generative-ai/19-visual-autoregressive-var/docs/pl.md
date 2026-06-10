# Wizualne modelowanie autoregresyjne (VAR): przewidywanie w następnej skali

> Modele dyfuzji próbkują iteracyjnie w czasie (etapy odszumiania). VAR próbkuje iteracyjnie w skali — przewiduje żeton 1x1, następnie 2x2, następnie 4x4, aż do ostatecznej rozdzielczości, przy czym każda skala jest uzależniona od poprzedniej. W artykule z 2024 r. wykazano, że VAR dopasowuje się do praw skalowania w stylu GPT przy generowaniu obrazu i pokonuje DiT przy tym samym budżecie obliczeniowym. Ta lekcja buduje podstawowy mechanizm.

**Typ:** Kompilacja
**Języki:** Python (z PyTorch)
**Wymagania wstępne:** Faza 7, lekcja 03 (Uwaga wielogłowa), Faza 8, lekcja 06 (DDPM)
**Czas:** ~90 minut

## Problem

Modelowanie języka zdominowane przez generację autoregresyjną, ponieważ skaluje się w przewidywalny sposób: więcej obliczeń, więcej parametrów, mniejsza złożoność, lepsze wyniki. Generowanie obrazu miało dwie główne próby AR przed 2024 rokiem: PixelRNN/PixelCNN (piksel po pikselu) i DALL-E 1 / Parti / MuseGAN (token po tokenie w kodach VQ-VAE).

Obaj cierpieli na problem porządku pokoleń. Piksele i tokeny ułożone są w siatkę 2D, ale model AR musi je odwiedzać w kolejności rastrowej 1D. Wczesny piksel narożny nie ma pojęcia, czym ostatecznie stanie się obraz. Jakość generacji była skalowana gorzej niż GPT na tekście i nigdy nie osiągnęła jakości modelu dyfuzyjnego przy dopasowanych obliczeniach.

VAR rozwiązuje problem kolejności generacji, zmieniając to, co jest generowane. Zamiast przewidywać tokeny obrazów jeden po drugim w przestrzeni, VAR przewiduje cały obraz w coraz większej rozdzielczości. Krok 1: przewiduj token 1x1 (ogólne „podsumowanie”) obrazu. Krok 2: przewiduj siatkę tokenów 2x2 (grubsze cechy). Krok 3: przewiduj siatkę 4x4. Krok K: przewiduj ostateczną siatkę (H/8)x(W/8).

Każda skala odnosi się do wszystkich poprzednich skal (przyczynowo w „kolejności skali”) i jest równoległa w obrębie własnej skali. Problem kolejności znika: cały obraz w skali k powstaje w jednym przejściu transformatora.

## Koncepcja

### Wieloskalowy tokenizator VQ-VAE

VAR potrzebuje **dyskretnego tokenizera o wielu skalach**. W przypadku obrazu x tworzy sekwencję siatek tokenów o coraz wyższej rozdzielczości:

```
x -> encoder -> latent f
f -> tokenize at 1x1: token grid z_1 of shape (1, 1)
f -> tokenize at 2x2: token grid z_2 of shape (2, 2)
...
f -> tokenize at (H/p)x(W/p): token grid z_K of shape (H/p, W/p)
```

Każdy z_k używa tego samego słownika (typowy rozmiar 4096-16384). Tokenizacja w każdej skali nie jest niezależna — jest trenowana w taki sposób, że zsumowanie reszt w każdej skali rekonstruuje f:

```
f ≈ upsample(embed(z_1), target_size) + ... + upsample(embed(z_K), target_size)
```

To jest **szczątkowy wariant VQ**. Skala k oddaje to, co pominięto w skalach 1..k-1. Dekoder pobiera sumę wszystkich osadzania skali i tworzy obraz.

Wieloskalowy tokenizator VQ jest szkolony raz (jak VQGAN), a następnie zamrażany. Cała praca generatywna jest wykonywana przez model autoregresyjny znajdujący się na górze.

### Przewidywanie następnej skali

Model generatywny to transformator, który widzi tokeny ze wszystkich poprzednich skal i przewiduje tokeny w kolejnej skali.

Struktura sekwencji wejściowej:

```
[START, z_1 tokens, z_2 tokens, z_3 tokens, ..., z_K tokens]
```

Osadzenie pozycji koduje zarówno indeks skali, jak i pozycję przestrzenną w skali. Uwaga ma charakter przyczynowy w kolejności na skali: żeton w skali k, pozycja (i, j) może dotyczyć wszystkich tokenów w skalach 1..k oraz samych tokenów w skali k, które pojawiają się wcześniej, niezależnie od zastosowanej kolejności wewnątrz skali (VAR wykorzystuje stałą uwagę pozycyjną bez związku przyczynowego wewnątrz skali — wszystkie pozycje w skali są przewidywane równolegle).

Strata treningowa: w każdej skali k przewiduj tokeny z_k, biorąc pod uwagę wszystkie tokeny poprzedniej skali. Strata entropii krzyżowej w dyskretnych kodach VQ. Taka sama struktura jak GPT, z tą różnicą, że „sekwencja” ma teraz strukturę skali.

### Pokolenie

Wnioskując:

```
generate z_1 = sample from p(z_1)                    # 1 token
generate z_2 = sample from p(z_2 | z_1)              # 4 tokens in parallel
generate z_3 = sample from p(z_3 | z_1, z_2)         # 16 tokens in parallel
...
decode: f = sum of embed-and-upsample scales 1..K
image = VAE_decoder(f)
```

Dla wag K = 10 generacja wynosi 10 przejść transformatora do przodu. Każde przejście generuje równolegle całą skalę — bez autoregresji na token w obrębie skali. W przypadku obrazu o wymiarach 256x256 jest to około 10 przejść w porównaniu z 28-50 DiT.

### Dlaczego następna skala wygrywa z następnym tokenem

Trzy zwycięstwa strukturalne:
1. **Od zgrubnej do dokładnej odpowiada statystykom naturalnego obrazu.** Zarówno percepcja wzrokowa człowieka, jak i zbiory danych obrazu wykazują prawidłowości zależne od skali: struktura niskich częstotliwości jest stabilna i przewidywalna; szczegóły o wysokiej częstotliwości są zależne od zawartości o niskiej częstotliwości. Wykorzystuje to przewidywanie na następną skalę.
2. **Równoległe generowanie w ramach skali.** W przeciwieństwie do AR tokenów w stylu GPT, VAR tworzy wszystkie tokeny na dużą skalę w jednym kroku. Efektywna długość generacji jest skalą logarytmiczną, a nie liniową.
3. **Brak błędu kolejności generacji.** Tokeny w skali k patrz wszystkie w skali k-1; nie ma błędu „po lewej stronie” ani „powyżej”, który zmusza wczesne tokeny do zatwierdzenia, zanim dostępny będzie późny kontekst.

### Prawo skalowania

Tian i in. wykazało, że VAR podąża za krzywą skalowania prawa potęgowego dla FID w ImageNet — podobnie jak GPT w przypadku zakłopotania. Podwojenie parametrów lub obliczeń niezawodnie zmniejsza błąd o połowę. Był to pierwszy model generujący obrazy, który wykazywał tego rodzaju zachowanie skalowania równie wyraźnie, jak modele językowe. W rezultacie przewidywania w skali VAR stają się przewidywalne na podstawie obliczeń, a nie empirycznych domysłów dotyczących danej architektury.

### Związek z rozpowszechnianiem

VAR i dyfuzja mają tę samą historię kompresji danych: oba dzielą problem generowania na sekwencję łatwiejszych podproblemów.

- Dyfuzja: stopniowo dodawaj szum, naucz się cofać jeden krok.
- VAR: stopniowo zwiększaj rozdzielczość, naucz się przewidywać następną skalę.

Są różnymi osiami problemu. Obydwa dają możliwe do zastosowania rozkłady warunkowe. Empirycznie VAR jest szybszy w wnioskowaniu (mniej przejść, wszystkie równoległe w skali) i dorównuje lub przewyższa DiT w ImageNet z warunkami klasowymi. Aktywnym kierunkiem badawczym jest tekstowo-warunkowy VAR (VARclip, HART).

## Zbuduj to

W `code/main.py` będziesz:
1. Zbuduj mały **wieloskalowy tokenizer VQ** na syntetycznych danych „obrazu” (pierścienie Gaussa 2D).
2. Wytrenuj **transformator w stylu VAR**, aby przewidywał tokeny w następnej skali.
3. Próbkę wywołując 4 razy transformator (4 skale) i dekodując.
4. Sprawdź, czy szkolenie uporządkowane według skali sprawia, że ​​generowanie jest równoległe w obrębie skali.

To jest implementacja zabawki. Chodzi o to, aby zobaczyć, że maska ​​uwagi o strukturze skali i generowanie równoległe w skali rzeczywiście działają.

## Wyślij to

Ta lekcja daje `outputs/skill-var-tokenizer-designer.md` — umiejętność projektowania wieloskalowego tokenizera: liczba skal, współczynniki skali, rozmiar książki kodowej, współdzielenie reszt, architektura dekodera.

## Ćwiczenia

1. **Ablacja skali.** Trenuj VAR z 4, 6, 8, 10 skalami. Zmierz jakość rekonstrukcji w funkcji liczby przejść autoregresyjnych. Więcej łusek = mniejsze pozostałości = lepsza jakość, ale więcej przejść.

2. **Rozmiar książki kodowej.** Trenuj tokenizery o rozmiarach książki kodowej 512, 4096, 16384. Większe książki kodowe zapewniają lepszą rekonstrukcję, ale trudniejsze przewidywanie. Znajdź kolano.

3. **Kontrola równoległa w skali.** W przypadku wyszkolonego VAR-a należy wyraźnie zmierzyć wzorzec uwagi. Czy w skali k model uwzględnia pozycje międzyskalowe, ale nie wewnątrzskalowe? Sprawdź implementację maski.

4. **Skalowanie VAR vs DiT.** W przypadku tego samego zadania warunkowego klasy ImageNet trenuj VAR i DiT przy dopasowanych budżetach parametrów (np. 33M, 130M, 458M). Wykres FID vs obliczenia. VAR powinien wyprzedzać DiT w każdym rozmiarze — odtwarzać wynik papieru w małej skali.

5. **Kondycjonowanie tekstu.** Rozszerz VAR, aby uwzględnić osadzanie tekstu (w sumie CLIP) jako dodatkowe wejście warunkujące przez adaLN. To jest przepis HART. O ile poprawia się FID w przypadku próbkowania wyrównanego do tekstu?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| VAR | „Wizualna autoregresja” | Generowanie obrazu poprzez przewidywanie następnej skali na podstawie piramidy siatek tokenów VQ |
| Przewidywanie następnej skali | „Przewiduj grubsze, a potem drobniejsze” | Model przewiduje tokeny w rosnących skalach rozdzielczości, uwzględniając wszystkie poprzednie skale |
| Wieloskalowy tokenizer VQ | „Resztkowe VQ” | VQ-VAE, który tworzy K siatek tokenów o rosnącej rozdzielczości, z dekoderem sumującym wszystkie skale |
| Skala k | „Piramida poziom k” | Jeden z K poziomów rozdzielczości, od 1x1 przy k=1 do (H/p)x(W/p) przy k=K |
| Równolegle w skali | „Jeden napastnik na skalę” | Wszystkie tokeny w skali k są przewidywane w jednym przebiegu transformatora, a nie autoregresywnie |
| Skale przyczynowe | „Uwaga uporządkowana według skali” | Żeton w skali k może dotyczyć wszystkich skal 1..k, ale nie skal k+1..K |
| Resztkowe VQ | „Tokenizacja addytywna” | Żetony każdej skali kodują resztę pozostawioną przez niższe skale; dekoder sumuje wszystkie osadzania skali |
| Prawo skalowania VAR | „Skalowanie obrazu GPT” | FID kieruje się przewidywalnym prawem potęgowym w obliczeniach, takim jak złożoność modeli językowych |
| HART | „Hybrydowy VAR + tekst” | Warunkowy tekstowy wariant VAR łączący iteracyjne dekodowanie w stylu MaskGIT ze strukturą skali VAR |
| Osadzanie pozycji skali | „(skala, wiersz, kolumna) potrójna” | Kodowanie pozycyjne przenosi zarówno indeks skali, jak i współrzędne przestrzenne w skali |

## Dalsze czytanie

- [Tian et al., 2024 — „Wizualne modelowanie autoregresyjne: generowanie skalowalnego obrazu za pomocą przewidywania nowej skali”](https://arxiv.org/abs/2404.02905) — artykuł VAR, odniesienie kanoniczne
– [Peebles i Xie, 2022 – „Scalable Diffusion Models with Transformers”](https://arxiv.org/abs/2212.09748) – DiT, punkt odniesienia porównania dyfuzji
– [Esser et al., 2021 — „Taming Transformers for High-Resolution Image Synthesis”](https://arxiv.org/abs/2012.09841) — VQGAN, rodzina tokenizerów Wieloskalowy tokenizer VAR rozszerza się
- [van den Oord i in., 2017 — „Neural Discrete Representation Learning”](https://arxiv.org/abs/1711.00937) — VQ-VAE, podstawa tokenizacji obrazu dyskretnego
- [Tang i in., 2024 — „HART: Efficient Visual Generation with Hybrid Autoregressive Transformer”](https://arxiv.org/abs/2410.10812) — VAR warunkowy tekstowy