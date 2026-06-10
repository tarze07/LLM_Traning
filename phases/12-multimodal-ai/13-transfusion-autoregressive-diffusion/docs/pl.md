# Transfuzja: Tekst autoregresyjny + obraz dyfuzyjny w jednym transformatorze

> Chameleon i Emu3 stawiają wszystko na dyskretne żetony. Działają, ale widoczne jest wąskie gardło kwantyzacji — plateau jakości obrazu poniżej modeli dyfuzji w przestrzeni ciągłej. Transfusion (Meta, Zhou i in., sierpień 2024) przyjmuje odwrotne założenie: utrzymuje ciągłość obrazów, całkowicie porzuca VQ-VAE i szkoli jeden transformator z dwoma stratami. Tokeny tekstowe otrzymują prognozę następnego tokenu. Plamy obrazu uzyskują dopasowanie przepływu/utratę dyfuzji. Obydwa cele optymalizują te same wagi. Architektura leżąca u podstaw Stable Diffusion 3 (MMDiT) jest bliską kuzynką. W tej lekcji czytamy tezę o transfuzji, budujemy zabawkowy trener z dwiema stratami i rysujemy maskę uwagi, która pozwala jednemu transformatorowi wykonywać obie funkcje.

**Typ:** Kompilacja
**Języki:** Python (stdlib, trener z dwiema stratami na zabawce w skali MNIST)
**Wymagania wstępne:** Faza 12 · 11 (Kameleon), Faza 8 (Generatywna AI)
**Czas:** ~180 minut

## Cele nauczania

- Podłącz transformator obsługujący dwie straty (NTP na tokenach tekstowych, MSE dyfuzyjny na plamach obrazu) w jednym szkielecie.
- Wyjaśnij, dlaczego dwukierunkowa uwaga na fragmentach obrazu plus uwaga przyczynowa na żetonach tekstowych jest właściwym wyborem maski.
- Porównaj styl transfuzji (obrazy ciągłe, utrata dyfuzji) ze stylem Chameleon (obrazy dyskretne, NTP) pod względem obliczeń, jakości i złożoności kodu.
- Proszę wymienić wkład MMDiT: wagi specyficzne dla modalności w każdym bloku, wspólna uwaga na strumień resztkowy.

## Problem

Debata na temat tokenów obrazu dyskretnego i ciągłego jest starsza niż LLM. Ciągłe reprezentacje (surowe piksele, ukryte VAE) zachowują szczegóły. Dyskretne tokeny (indeksy VQ) pasują do natywnego słownika transformatora, ale tracą szczegóły na etapie kwantyzacji.

Chameleon/Emu3 poszedł dyskretnie: jedna strata, jedna architektura, ale wierność obrazu ograniczona jakością tokenizera.

Modele dyfuzji były ciągłe: wyjątkowa jakość obrazu, ale odrębny model od LLM, złożona inżynieria harmonogramu szumów i brak czystej integracji z generowaniem tekstu.

Transfuzja pyta: czy możemy mieć jedno i drugie? Zachowaj ciągłość obrazów, nadal trenuj jeden model, użyj dwóch strat połączonych w jeden krok gradientu.

## Koncepcja

### Architektura dwóch strat

Pojedynczy transformator obsługujący tylko dekoder przetwarza sekwencję zawierającą:

- Tokeny tekstowe (dyskretne, ze słownictwa BPE).
- Plamy obrazu (ciągłe bloki 16x16 pikseli rzutowane w ukryte przyciemnienie poprzez osadzanie liniowe - tak samo jak wejście kodera ViT).
- Tagi `<image>` i `</image>` oznaczające miejsce występowania ciągłych poprawek.

Podanie w przód wykonuje się raz. Przegrana wybiera jedną z dwóch reszek na żeton:

- W przypadku żetonów tekstowych: standardowa entropia krzyżowa na nagłówku vocab-logits.
- W przypadku fragmentów obrazu: utrata dyfuzji w obszarach ciągłych — należy przewidzieć szum dodany do każdego fragmentu obrazu.

Gradient przepływa przez wspólny korpus transformatora. Obie straty jednocześnie poprawiają wspólne wagi.

### Maska uwagi: tekst przyczynowy + obraz dwukierunkowy

Żetony tekstowe muszą mieć charakter przyczynowy — nie można pozwolić, aby żeton tekstowy zajmował się przyszłym tekstem lub aby nauczyciel wymuszał przerwy. Jednakże poprawki obrazu reprezentują jedną migawkę; powinny one zajmować się sobą dwukierunkowo w ramach tego samego bloku obrazu.

Maska:

```
M[i, j] = 1 if:
  (i is text and j is text and j <= i)   # causal for text
  OR (i is image and j is image and same_image_block(i, j))   # bidirectional within image
  OR (i is text and j is image and j < i_image_end)   # text attends to previous images
  OR (i is image and j is text and j < i_image_start)   # image attends to preceding text
```

Zaimplementowana jako maska blokowo-trójkątna podczas uczenia i wnioskowania.

### Strata dyfuzyjna wewnątrz transformatora

Strata dyfuzyjna jest standardowa: dodaj szum do fragmentu obrazu, poproś model o przewidzenie szumu (lub równoważnie czystego fragmentu). Wersja Transfusion wykorzystuje dopasowanie przepływu — przewiduje pole prędkości od szumu do czystego.

Podczas treningu:
1. Dla każdego fragmentu obrazu x0 pobierz losowy krok czasowy t.
2. Szum próbki ε, oblicz xt = (1-t) * x0 + t * ε (interpolacja liniowa dla dopasowania przepływu).
3. Transformator przewiduje v_theta(xt, t); strata = MSE(v_theta(xt, t), ε - x0).
4. Podpora obok tekstu Straty NTP z tej samej sekwencji.

Podsumowując, pokolenie to:
- Tokeny tekstowe: standardowe próbkowanie autoregresyjne.
- Łaty obrazu: pętla próbkowania dyfuzyjnego (typowo 10-30 kroków) uwarunkowana wcześniejszymi tokenami tekstowymi.

### MMDiT: Wariant Stable Diffusion 3

Stable Diffusion 3 (Esser i in., marzec 2024 r.) dostarczył MMDiT (Multimodal Diffusion Transformer) mniej więcej w tym samym czasie co Transfusion. Architektury są rodzeństwem.

Kluczowe różnice MMDiT:

- Wagi specyficzne dla modalności na blok. Każdy blok transformatora ma oddzielne wagi Q, K, V i MLP dla tokenów tekstowych i poprawek obrazu. Uwaga jest wspólna (crossmodalność); wszystko inne zależy od modalności.
- Trening poprawionego przepływu. Specyficzny wariant dopasowywania przepływu ze znanym próbkowaniem i prostszą matematyką niż DDPM.
- Skala. MMDiT jest podstawą SD3 (warianty parametrów 2B i 8B). Papier Transfusion skaluje się do 7B.

Obydwa opierają się na tej samej podstawowej idei: jeden transformator obsługuje NTP na tekście i rozprasza na ciągłych reprezentacjach obrazu.

### Dlaczego to bije styl Chameleona

Różnica w jakości pomiędzy ciągłą dyfuzją a dyskretnym NTP w generowaniu obrazu jest mierzalna. Raporty dotyczące transfuzji:

- Przy parametrach 7B, przewyższa model w stylu Chameleon tej samej wielkości na FID o 3-5 punktów.
- Nie jest wymagane szkolenie w zakresie tokenizacji - koder obrazu jest prostszy (projekcja liniowa do ukrytej, taka sama jak warstwa wejściowa ViT).
- Wnioskowanie może zrównoleglać odszumianie fragmentów obrazu, w przeciwieństwie do tokenów obrazu autoregresyjnego.

Wada: Transfuzja to model z podwójną stratą, co utrudnia dynamikę treningu. Wagi odchudzające wymagają dostrojenia. Niedopasowanie harmonogramu między NTP a dyfuzją może spowodować dominację jednej głowy.

### Co znajduje się w dole rzeki

Janus-Pro (lekcja 12.15) udoskonala pomysł Transfusion, oddzielając koder wizyjny w celu zrozumienia i generowania — SigLIP w jednym, VQ w drugim — jednocześnie dzieląc korpus transformatora. Show-o (lekcja 12.14) zamienia dyfuzję na dyfuzję dyskretną (zamaskowane przewidywanie). Rodzina zjednoczonego pokolenia rozgałęzia się szybko po transfuzji.

Produkcyjne VLM z 2026 roku, które emitują obrazy — Gemini 3 Pro, GPT-5, ścieżka generowania obrazu Claude Opus 4.7 — prawie na pewno korzystają z potomka tej rodziny. Szczegóły są zastrzeżone.

## Użyj tego

`code/main.py` buduje zabawkową transfuzję na drobnym problemie podobnym do MNIST:

- Podpisy tekstowe to krótkie ciągi liczb całkowitych opisujące cyfrę (0-9).
- Obrazy to siatka bajtów o wymiarach 4x4.
- Para występów liniowych o wspólnym obciążeniu pełni funkcję zastępczą transformatora; Utrata NTP w tekście, utrata MSE w zaszumionych fragmentach.
- Pętla treningowa zmienia dwie straty, maska ​​uwagi jest wyraźna.
- Generacja tworzy podpis tekstowy i obraz 4x4 w jednym przebiegu do przodu.

Transformator to zabawka. Prawdziwymi artefaktami są dwustratna instalacja wodno-kanalizacyjna, konstrukcja maski uwagi i pętla wnioskowania.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-two-loss-trainer-designer.md`. Biorąc pod uwagę nowe multimodalne zadanie szkoleniowe (tekst + obraz, tekst + dźwięk, tekst + wideo), projektuje harmonogram dwóch strat (wagi strat, kształt maski, bloki współdzielone i specyficzne dla modalności) i zaznacza ryzyko wdrożenia.

## Ćwiczenia

1. Model typu transfuzji trenuje 70% tokenów tekstowych i 30% poprawek obrazu. Straty spowodowane dyfuzją obrazu są ~10 razy większe niż utrata wartości NTP tekstu. Jakie wagi strat je równoważą?

2. Zaimplementuj maskę blokowo-trójkątną dla sekwencji: `[T, T, <image>, P, P, P, P, </image>, T]`. Zaznacz każdy wpis 0 lub 1.

3. MMDiT posiada wagi QKV specyficzne dla modalności. Jakie narzuty związane z liczbą parametrów to dodaje w porównaniu z w pełni współdzielonym transformatorem Transfusion? Czy przy parametrach 7B warto?

4. Generowanie: po otrzymaniu monitu tekstowego model uruchamia NTP dla 50 tokenów, następnie trafia do `<image>`, a następnie przeprowadza dyfuzję na 256 poprawkach w 20 krokach odszumiania. Ile łącznie podań w przód?

5. Przeczytaj artykuł SD3, Sekcja 3. Opisz wyprostowany przepływ i dlaczego zbiega się on w mniejszej liczbie kroków wnioskowania niż DDPM.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Trening z dwiema stratami | „NTP + dyfuzja” | Pojedynczy transformator optymalizuje zarówno entropię krzyżową na tokenach tekstowych, jak i MSE na ciągłych fragmentach obrazu w tym samym kroku gradientu |
| Dopasowanie przepływu | „Przepływ skorygowany” | Wariant dyfuzyjny, który przewiduje pole prędkości od szumu do czystych danych; prostsza matematyka niż DDPM |
| MMDiT | „Multimodalny DiT” | Architektura Stable Diffusion 3: wspólna uwaga, MLP i normy specyficzne dla modalności |
| Maska blokowo-trójkątna | „Tekst przyczynowy + obraz dwukierunkowy” | Maska uwagi, która jest przyczynowa w całym tekście, ale dwukierunkowa w obszarach obrazu |
| Ciągła reprezentacja obrazu | „Brak VQ” | Poprawki obrazu jako wektory o wartościach rzeczywistych, a nie całkowite indeksy książki kodowej |
| Przewidywanie prędkości | "v-parametryzacja" | Dane wyjściowe sieci to pole prędkości pomiędzy szumem a danymi, a nie sam szum

## Dalsze czytanie

- [Zhou i in. — Transfuzja (arXiv:2408.11039)](https://arxiv.org/abs/2408.11039)
- [Esser i in. — Stable Diffusion 3 / MMDiT (arXiv:2403.03206)](https://arxiv.org/abs/2403.03206)
– [Peebles i Xie — DiT (arXiv:2212.09748)](https://arxiv.org/abs/2212.09748)
- [Zhao i in. — MonoFormer (arXiv:2409.16280)](https://arxiv.org/abs/2409.16280)
- [Xie i in. — Show-o (arXiv:2408.12528)](https://arxiv.org/abs/2408.12528)