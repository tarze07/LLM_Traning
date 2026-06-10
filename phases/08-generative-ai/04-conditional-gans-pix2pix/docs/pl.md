# Warunkowe GAN-y & Pix2Pix

> Pierwszym wielkim przełomem z lat 2014-2017 było opanowanie tego, co tworzy GAN. Dołącz etykietę, obrazek albo zdanie. Pix2Pix to wersja dla obrazów i wciąż przewyższa każdy ogólny model text-to-image w węższych, sprecyzowanych zadaniach transformacji obrazów.

**Typ:** Budowa
**Języki:** Python
**Wymagania:** Faza 8 · 03 (GAN-y), Faza 4 · 06 (U-Net), Faza 3 · 07 (CNN)
**Czas:** ~75 minut

## Problem

Bezwarunkowy GAN po prostu generuje losowe twarze. Przydatne do demonstracji, bezużyteczne w produkcji. Chcesz: *zamienić szkic na zdjęcie*, *mapę na fotografię lotniczą*, *scenę dzienną w nocną*, *pokolorować czarno-białe zdjęcie*. We wszystkich tych przypadkach masz obraz wejściowy `x` i musisz wyprodukować obraz `y`, zachowując pewną zgodność semantyczną. Dla danego `x` istnieje wiele wiarygodnych obrazów `y`. Obliczanie błędu średniokwadratowego (MSE) spłaszcza je w jedną bezkształtną masę. Błąd w podejściu kontradwersaryjnym (adversarial loss) tego nie robi, ponieważ wymóg bycia "prawdziwym" generuje ostre kształty.

Conditional GAN (Mirza i Osindero, 2014) dodaje do sieci `G` i `D` warunek `c` w postaci zmiennej. Pix2Pix (Isola i in., 2017) to wyspecjalizowana jego wersja: warunek to cały obraz wyjściowy, generator to sieć typu U-Net, dyskryminator to oparty o bloki klasyfikator (*PatchGAN*), a funkcja straty łączy L1 oraz klasyczny adversarial loss. Ten przepis daje lepsze rezultaty niż modele text-to-image budowane od zera w wąskich dziedzinach transformacji obraz-w-obraz (nawet w roku 2026), ponieważ jest trenowany na *parach danych* — masz tu dokładnie taki sygnał, jakiego potrzebujesz.

## Koncepcja

![Pix2Pix: Generator U-Net, dyskryminator PatchGAN](../assets/pix2pix.svg)

**Warunkowe G.** `G(x, z) → y`. W Pix2Pix `z` realizowane jest poprzez dropout wewnątrz G (brak jest na wejściu jednoznacznego szumu, według badaczy z zespołu Isoli explicite szum i tak jest zwykle ignorowany przez model).

**Warunkowe D.** `D(x, y) → [0, 1]`. Na wejściu dostajemy *parę* (warunek, wynik). To kluczowa różnica: D osądza, czy wygenerowane `y` zgadza się ze specyfiką `x`, a nie tylko ocenia, czy `y` wygląda realistycznie.

**Generator U-Net.** Koder-dekoder (encoder-decoder) z warstwami rezydualnymi (skip connections) omijającymi wąskie gardło sieci. Zasadnicze do zastosowań, w których wejście i wyjście dzielą podobną niskopoziomową strukturę (krawędzie, zarysy postaci). Bez "skrótów" detal związany z wysokimi częstotliwościami ginie bezpowrotnie.

**Dyskryminator PatchGAN.** D nie wypuszcza jednej ogólnej oceny realne/fałszywe. D wysyła siatkę wyników `N×N`, w której każda komórka podejmuje decyzję względem wycinka 70×70 pikseli. Ich oceny są na koniec uśredniane. Modeluje on układ Markowa dla losowych pól (Markov random field): realizm obrazu ma charakter lokalny. O wiele szybszy w trenowaniu, ma o wiele mniej parametrów i na wyjściu rodzi wyraźniejsze obrazki.

**Funkcja straty.**

```
loss_G = -log D(x, G(x)) + λ · ||y - G(x)||_1
loss_D = -log D(x, y) - log (1 - D(x, G(x)))
```

Składnik L1 powoduje stabilizację oraz przepycha generator by szedł w ślady celu. Użycie normy L1 sprzyja w wyłapaniu wyraźniejszych krawędzi niż w przypadku normy L2 (mediany zamiast średniej). `λ = 100` było domyślnym parametrem dla Pix2Pix.

## CycleGAN — a co gdy nie ma par

Pix2Pix musi operować parami danych `(x, y)`. CycleGAN (Zhu i in., 2017) radzi sobie bez nich za sprawą ulepszonej funkcji straty: błędu cyklu-zgodności (*cycle consistency* loss). Dwa generatory `G: X → Y` i `F: Y → X`. Są trenowane tak by `F(G(x)) ≈ x` oraz `G(F(y)) ≈ y`. Powala to robić podmianę z krajobrazu z końmi na scenerię z zebrami (albo lato na zimę), ignorując zupełnie brakujących powiązanych par danych.

W 2026 transformacja nie-sparowanych danych z użyciem architektur opiera się bardziej na modelach dyfuzyjnych (np. ControlNet, IP-Adapter), odkładając CycleGAN na bok, ale istota zachowania konsystencji cykli przechodzi na każdy projekt opisujący nowe domeny aplikacji uczenia maszynowego.

## Zbuduj to

`code/main.py` wprowadza wariację miniaturowego GAN w oparciu na jednowymiarowych (1-D) danych. Warunek `c` jest to klasa obrazu (np. 0 czy 1). Zadanie polega na wyprodukowaniu sampla na bazie dystrybucji wynikowej dla podanej klasy-etykiety.

### Krok 1: powiązanie "warunku" jako wejścia G oraz D

```python
def G(z, c, params):
    return mlp(concat([z, one_hot(c)]), params)

def D(x, c, params):
    return mlp(concat([x, one_hot(c)]), params)
```

One-hot encoding to najprostsza możliwa droga by wprowadzić etykietę. Rozbudowane sieci używają "nauczonych" zanurzeń (learned embeddings), FiLM modulation, czy uogólnionych architektur "cross-attention".

### Krok 2: jak trenować na wejściu warunkowym

```python
for step in range(steps):
    x, c = sample_real_conditional()
    noise = sample_noise()
    update_D(x_real=x, x_fake=G(noise, c), c=c)
    update_G(noise, c)
```

Sieć po etapie adaptacyjnym G potrafi zestroić faktyczną lokalną relację (dla danego warunku `c`), a nie uśrednioną z powszechnych statystyk krańcowych marginesów.

### Krok 3: upewnienie się co do wyników dla zadanych klas (per-class)

```python
for c in [0, 1]:
    samples = [G(noise, c) for noise in batch]
    mean_c = mean(samples)
    assert_near(mean_c, real_mean_for_class_c)
```

## Pułapki

- **Warunek przez sieć został obojętnie odpuszczony.** Domyślnie sieć G skręcała w minimalizowanie brzeżnych różnic, sieć D w żaden sposób nie próbowała wywołać kary, bo odzwierciedlenie nie zostało powiązane w sensowny sygnał. Poprawienie: nałożenie D na bardziej agresywne reagowanie na warunek (we wczesnych etapach warstw, zamiast tylko ostatnich na końcu arch.), użycie tzw. projection discriminator (Miyato i Koyama, 2018).
- **Zbyt niska waga dla normy L1.** Sieć generatora ucieka z rąk na losowych krawędziach przypominających faktyczne obrazki realne, a nie wiernych oryginałowi. Pix2Pix powinien wystartować λ≈100 dla pierwszych iteracji.
- **Zbyt silna waga dla normy L1.** Sieć G tworzy rozmyty obłok z wygenerowanych wyjść - ponieważ parametr L1 dla miar w środowisku ciągłym będzie tworzył rozlane gradienty L_p. Należy na bieżąco zmniejszać te wielkości poprzez wygaszanie jej działania - tylko gdy już model nabierze konkretnych cech.
- **Wrzucanie oryginalnych wycinków docelowych z domeny dla predykcji D.** Błąd we wdrażaniu D gdzie łączono wyjścia tak jak `(x, y)` jak rzekome wejścia klasyfikacyjne D, zamieniając wejście samego `y`. Tak spina nie zadziała jakby nie próbowała sklasyfikować na wejściu obudowanych modeli i upewnić powiązań cech by nie poszło źle.
- **Per-klasowy zator trybów - Mode Collapse.** Każda odrębna etykieta (klasa) załamuje oddzielnie wyniki, wymagane było sprawdzanie by unikać tych incydentów.

## Zastosuj to

Stos aplikacyjny lat 2026 roku przy zagadnieniach image-to-image:

| Zadanie | Podejście i technologia do użycia |
|------|---------------|
| Rysunek-szkic → realna fotografia, podobna dziedzina obrazowa, sparowane pliki | Pix2Pix / Pix2PixHD (Nadal sprawnie prężny mechanizm w szybkich zapytaniach - "ostre wyjścia") |
| Szkic → Fotografia ale obydwa pozbawione powiązań | ControlNet oraz podłączony tryb "Scribble" jako moduł pomocniczy dyfuzji. |
| Mapa wytyczonych semantycznie obiektów → realna fotografia obiektów. | SPADE / GauGAN2 lub ew. Stabilna dyfuzja jako moduł dla obrazków opartych z wejścia do wyjścia. |
| Maskowanie stylami artysty | Dyfuzja poprzez wektor w warstwie IP-Adapter albo LoRA; Tradycyjne rozwiązania oparte na GAN odeszły do lamusa i są już tylko pamiątką (legacy). |
| Maska w głębi mapy → obraz fotograficzny. | Ustawiona warstwa ControlNet-Depth obok Standardowej struktury dyfuzji dla danego zdjęcia. |
| Powiększanie obrazków (super-resolution) | Real-ESRGAN (Zwykły moduł GANowy), ESRGAN-Plus dla zaawansowanych wygładzeń lub klasyczny tryb z Stable-Diffusion poprzez tryb "Upscale"  (w środowisku dyfuzji) |
| Barwienie starych zdjęć czarno-białych. | Moduł klasowy ColTran (Google, dyfuzyjnie barwi), bądź tradycyjne odzyskanie koloru do formatu piksel do piksela dzięki technikom Pix2Pix-color. |
| Przemiana "Scenny dzień-na-noc", "zima-w-lato", "pogoda chmury, pogodna pogoda". | Skrypt pod modelem typu np. klasyczny CykleGAN bądź skrypty ze strefy sieci wspierających środowisko Control-NET (pod bazą SD). |

Sieci typu "Pix2Pix" wydają się najsłuszniejszą próbą wejścia gdy: (a) posiadasz setki/tysiące konkretnych uwarunkowanych wzorców szkoleniowych powiązanych obrazek a obrazek B z góry ustawioną krawędzią do naśladowania po przejściu prób treningowych. (b) Przetwarzanie i specyfikacja poleceń w modelu uczenia są zamknięte - np. bez ogólników z tekstowymi warunkami, lecz wąska odnoga do obsługi, np. sztywne zadania operowania danymi oraz cecha powtarzalności środowiska a zarazem wymóg na inferencje. Jeżeli wchodzimy jednak z dziedziny nie uwarunkowanych domen (np. zwykła obróbka czegokolwiek za pomocą promptera wejścia tekst-na-obraz bez narzutów sztywno wyodrębnionych na wejściu obudowanych form wektorów wizualnych) to tu wygrywają generatory oparte na dyfuzyjnym środowisku, bo są po prostu naturalnie pod to skrojone do "rozszerzających" domyślnych otwartych standardów wektoryzacji i ogólnych rozwiązań generacji tekstu na wideo/grafikę obrazów bez nadzoru na pojedynczy styl a w zasadzie odróżniają to wszechobecnością generatywną do "wszystkiego w domyśle modelowym".

## Wdróż to

Zapisz to do ścieżki i nazwij odpowiednio `outputs/skill-img2img-chooser_pl.md`. Zadanie po wgraniu odnosi do wejściowego modelu (zestaw opisowych zadań do wykonania na modelu "co chcę zamienić"), specyfikacja używania zbiorów w bazie danych (np. obudowane pary, i wolne niezależne wejście w zbiorach i opcje prób). Należy podać wynik określający najlepsze kroki pod implementację rozwiązań z Pix2Pix (oraz innych jego siostrzanych wejść, lub modeli bazowych CycleGAN), oraz wejściową metrykę pod dyfuzję - typ "SDXL pod moduł + moduł rozszerzony o rurę strumieniową IP-Adapter", specyfikację wymagań wobec zbiorów wykreowanych przez proces szkoleniowy, opcja pomiaru do optymalizacji zapytań latencji przy wysyłce, a na sam koniec sposób sprawdzania zgodności modeli względem zadanej bazy jako obudowanego potoku wejściowego opisanym o ustrukturyzowaną matrycę dla miar FID by sprawnie działać wedle opisanego schematu.

## Ćwiczenia

1. **Poziom trywialny.** Dodaj poprzez "zabawę wejściową pliku `code/main.py`" wpis dodający inną/nową klasę wejścia do wektora modelu (trzecia opcja bazy). Zadziałaj by G uczył poszczególnym wejściom nowej struktury pod odniesienia warunkowe po zmianie w etykietach dla określonej klasy by wskazać inną dystrybucję w środowisku szumu by w odpowiedni model trafiła na wyjściu.
2. **Krok standardowy i oznaczony na medium.** Zamień używaną formę L1 na odpowiednie "miary z obudowaną w opcje straty na stylu percepcyjnym o wariancjach bloku "w stylach - percepcja straty sieci na wyjściu". Sprawdź czy to wpływa na uwarunkowanie o ostrość rozproszeń odniesień "D". Użyj np. obudowanych małych elementów stacji dla uczenia zamrożonego w ramach np. "D-stacja po stronie warunkowania".
3. **Zaawansowane obudowanie na poziomie "Trudne".** Zademonstruj środowisko dla Cycle-GAN przez 1-D warunki: dystrybucja typu A i B dla dwóch różnych środowisk D, dwa rozbicia skryptowe pod wejście G od dwóch form pod weryfikacją "zależność-koło" strat ze ścieżki (Cykle-loss w sieci). Rozbij bez opcji z obudowaną powiązaną w bazę z par danych - zobacz że potrafi w środowisku mapowania przeskoczyć bez ich wsparcia z wymaganym poparciem wyników jako środowisko.

## Kluczowe słownictwo

| Pojęcie - Termin specyficzny dla uczenia | Określenie | Znaczenie w branży |
|------|-----------------|-----------------------|
| Conditional GAN / Warunkowe GANY  | "Gan gdzie używamy danych etykiet w sieci" | Obydwie formy sieci "widzą" w złączeniu ten sam sygnał jako klasę/uwarunkowania `(G(z, c), D(x, c))`.  |
| Pix2Pix. | Zastąpienie Obraz-do-obraz z bazą obrazu na wejściu jako GANa  | Parowane zestawy na siatce warunku wejściowego i klasyfikatora modelu z wektoryzacją. |
| U-Net  | Opcja: Architektura Kodera-Dekodera o warunkach typu Skokowe - Skips, z opcjami symetrii wektoryzacji. | Moduł pozwala bez ubytków zachować ostrość detali po wejściu. |
| Opcja siatek "PatchGAN" | "Realistyczna lokacja w oparciu na odniesienie po obszarach siatek." | Wynik z wejść jest rozbity w stosunku np globalnych statystyk z obrazu a w oparciu klasyfikowany jest pojedynczy wycinek obrazkowy pod wyjściowe miary i w ocenę na lokalnym obszarze grafiki. |
| Koncept od Cycle-GAN.  | "Zmiany ze ścieżki i powiązań między dziedzinami od nie-łączonych par i wejść modelowych." | Formowanie na opcjach G bez użycia sparowanych materiałów z dodatkami na ocenę w oparciu utrat na tzw. powieleniowym błędzie cykli wejścia G po cyklu zwrotu. |
| Środowiska dla warunków modeli - w środowisku SPADE | Opcja pod środowisko "GauGAN" i modułów wyjściowych ze stanów pośrednich w segmencie.  | Segmentuje by ujednolicić miary i opcję aktywacji. Model na odniesienie pod zadania segm. → Obraz wyjściowy fotografii itp. |
| Opcje w wektorze typu uwarunkowań "FiLM - i jego środowiska na modulacji".  | Element wytycznych by wskazać i użyć uwarunkowanych środowisk wejściowych z opcji - liniowego przesuwania. | Składowa uwarunkowania z bardzo szybkich/niedrogich sposobów do uwarunkowanych ról by warunkować z wejść wektorowych przy np parametrach z uogólnionych modułów w wektor.  |

## Produkcyjne wdrażania technologii i adnotacje środowiskowe: Sieć potokowa Pix2Pix wygrywa bitwę i starcie o zjawiska by zaoszczędzić i skrócić miary opóźnień (Latency-Bound) pod baseline wyników dla zapotrzebowania

Przygotowując do złączenia dane z domeny na obróbkę z obudowaną zawężoną parą od zadanych i jasno sprecyzowanych ram projektowych modeli by generować grafikę po opcjach takich jako wejścia w domeny np. (Szkice w rendery końcowe by wyszła gotowa wygenerowana i skończona opcja) sieć wejścia/wyjścia (z jednym uwarunkowaniem w 1 cyklu i jako one-shot mode) przy uwarunkowaniach po środowisku sieci od Pix-na-Pix gniecie system na bazy w opcji z dyfuzyjnym środowiskiem sieci o stopień miar wydajności na korzyść w generacji - zwłaszcza o latencji w obróbce i odpowiedziach przy użyciu z API serwera pod żądaniami do generowania wyjść dla aplikacji lub modeli:

| Środowiska do użycia z wyjściami pod potok sieciowy.  | Wykonane rzuty do obliczeń w uwarunkowaniu. | Środowisko w środowisku na środowiska generacji modelu sprzętowego na jednej Karcie uwarunkowań - Nvidia L4, podział rzędów: (opóźnienie/512^2 wekt.) |
|------|-------|----------------------------------------|
| Potoki: Opcja z modułem modelu Pix-2-Pix na jedno obudowane wysłanie do wygenerowania prób (moduł z wprzód w odniesieniu). | Jeden obrót = równe "1". | Od ~30 ms, czas wejścia od wdrożeń w środowiskach do wygenerowania obrazkowego do wejścia. |
| Obudowane formacje np: Tryb model-Inpaint/lub Opcja SD po wejściach Img do obrazka "Img-2-Img"  (Na modelach starszych standardowych np SD 1-x lub SD-2-x / np dyfuzyjne). | Krok 20 razy pętle od sieci. | Opóźnienie na pułapie 1.2s - generatywne opóźnione wyjście |
| Nowoczesna wersja Opcja "Turbo z dystrybucji sieci" do modelowania - SDXL dla podanej formy- "SDXL - T - I-2-I". | Skoki rzutu to 1 do 4 wyliczeń sieci w 1 fazie. | Dojście pod wyniki ~0.15 do wyjściowych 0.35 s - zredukowana moc opóźnień |
| Opcja by wskazać środowiska z zewnątrz i model wyższy (pod formację C-N, w złączeniu od środowisk SDXL do modelu wejściowego na bazy z wariacjami dyfuzyjnymi i złączonych trybów - Opcja Control-Net w uwarunkowaniu base SDXL jako silniku od uwarunkowań u wejścia by wektorowo obrabiać na "krok po kroku i trybie wolniejszym pod generacje obrazowe. | Obroty to zaledwie ~20, z opcjami po ok ok. 30 uwarunkowań jako przelot potokowy z wyjściem. | Wyliczone wartości 3-do rzędu-5 sek do opóźnień u wyjściowego elementu wektora. |

Systemy z wariacji-Pix2Pix rozbijają środowisko na przepustowych rzutach statycznych wielokrotnych od złączeń w pętlach - gdzie każdy proces uwarunkowany ma takie zapotrzebowanie wektorowej jednostki na proces modelowy obciążeń. Moduł na Opcjach dyfuzyjnych rozwala wejściowe parametry na podstawie jakości do uogólnień i na możliwości generowania - i co najlepsze od dawien w trybie i złączeniach modeli z Pix2-Pix się odchodzi do budowania systemów na zewnątrz jako połączony rzut w wdrożeniu do modelu dyfuzyjnego jako zabezpieczenia z opóźnieniami w odniesieniach (Opcja w potokowej odnodze i na wyjścia fall back od trybów ogonowych jako na środek docelowy na użytek).

## Odnośniki do wiedzy w literaturze źródłowych wejść pod wiedzę by wiedzieć więcej od źródeł z pierwszej ręki do zapoznania na pojęciach.

- [Mirza oraz Osindero z uczelni, od - publikacja "cGAN" od Conditional Generative Adversarial Nets"](https://arxiv.org/abs/1411.1784) — środowisko wdrożeń w bazowy dokument z pierwszą iteracji bazy uwarunkowanych metod "GAN-model".
- [Dokument od: Isola etc., pod publikacją badawczą dla: Modele do Przemiany od obrazu do wymiarów obrazowych dla baz warunkowych z wejść od środowisk wdrożeń Pix-2-Pix"](https://arxiv.org/abs/1611.07004) — Publikacja na wyjścia modeli dla bazy w narzędzi "Pix2Pix" - pierwsza praca zespołu.
- [Badanie: od zespołu (od z 2017r), dla bazy sieci powielanych cyklem od Cycle-Consistent i metod: nie-łącznych baz "Image-do-Obrazku" z publikacją "Unpaired Image-... pod środowisko."](https://arxiv.org/abs/1703.10593) — Publikacja "Cykle-GAN." - narzędzia na obróbki na tryby bez "sparowanych powiązań od uwarunkowań sieci wejścia-do-sieci" na modelowanych powiązaniach między dziedzinami wejścia.
- [Wydanie Wang z 2018; (O wydaniach modelu o rozszerzonej warunkowej do skali na wejściu o uwarunkowaniach sieciowych do baz: H-R w bazie Image-Sz. w bazie cGANS)](https://arxiv.org/abs/1711.11585) — Wydanie modelu Pix-2-Pix w High-Definitions po obudowanych pracach zespołu jako model na wyjścia środowisk.
- [Model Park - Praca i publikacje, i od 2019 o metodologii w generatywnej i od Semantycznej syntezie po wejściach SPADE jako sieci od wdrożenia uwarunkowań od "Spatially...".](https://arxiv.org/abs/1903.07291) — Tryb wygenerowany z modułów dla GauGAN w sieci od Nvidii, i uwarunkowania po uwarunkowaniu modułu SPADE jako modułu od baz.
- [Od badań po: w Miyato w bazowym rokiem i 2018 badaniem na: Wdrożenia opcji D z dyskryminatorem bazowym-sieci w trybie Projection w cGANach po opcje modeli klasyfikujących w oparciu na modelowanie wejść od wdrożeń](https://arxiv.org/abs/1802.05637) — Metody D z Opcji D pod projekcję w sieci klasyfikacyjnej.