# Modele multimodalne wykorzystujące wyłącznie tokeny Chameleon i wczesną wersję Fusion

> W każdym VLM, który widzieliśmy do tej pory, obrazy i tekst są oddzielane. Tokeny wizualne pochodzą z kodera wizyjnego, przepływają do projektora, a następnie spotykają się z tekstem w LLM. Słownik wizji i tekstu nigdy się nie pokrywają. Chameleon (Meta, maj 2024) zapytał: co by było, gdyby tak było? Trenuj VQ-VAE, który zamienia obraz w sekwencję odrębnych tokenów ze wspólnego słownictwa. Każdy dokument multimodalny stanowi teraz jedną sekwencję — przeplatane tokeny tekstowe i tokeny graficzne, co stanowi pojedynczą stratę autoregresyjną. Efekt uboczny: model może generować wyniki o mieszanej modalności — naprzemienne tokeny tekstowe i graficzne w jednym wywołaniu wnioskowania. W tej lekcji czytamy tezę o wczesnej syntezie jądrowej i budujemy od początku do końca wersję zabawkową.

**Typ:** Kompilacja
**Języki:** Python (stdlib, tokenizer VQ-VAE + dekoder z przeplotem)
**Wymagania wstępne:** Faza 12 · 05, Faza 8 (Generatywna AI)
**Czas:** ~180 minut

## Cele nauczania

- Wyjaśnij, dlaczego wspólne słownictwo + pojedyncza strata zmieniają możliwości modelu.
- Opisz, w jaki sposób VQ-VAE tokenizuje obraz w dyskretną sekwencję zgodną z celem następnego żetonu transformatora.
- Wymień sztuczki Chameleona dotyczące stabilności treningu: QK-Norm, rozmieszczenie porzucania, porządkowanie LayerNorm.
- Porównaj podejście Chameleon i Q-Former BLIP-2 i opisz, kiedy każdy z nich jest właściwym wyborem.

## Problem

VLM oparte na adapterach (LLaVA, BLIP-2, Qwen-VL) traktują tekst i obraz jako dwie różne rzeczy. Token tekstowy przechodzi przez `embed(text_token)`; obraz przechodzi przez `visual_encoder(image) → projector → ... pseudo_tokens`. Model ma dwie ścieżki wejściowe, które częściowo się łączą.

Trzy konsekwencje:

1. LLM może jedynie konsumować obrazy, a nie je emitować. Dane wyjściowe to tylko tekst.
2. Dokumenty o mieszanej modalności (naprzemienne akapity i obrazy, jak w artykule) są niewygodne — albo analizujesz dane wejściowe multimodalne poza modelem, albo tworzysz łańcuch generacji.
3. Niedopasowanie dystrybucyjne. Tokeny wizualne i tokeny tekstowe znajdują się w różnych obszarach ukrytej przestrzeni, powodując subtelne problemy z wyrównaniem.

Chameleon odrzuca założenie: obrazy to po prostu sekwencje odrębnych tokenów ze wspólnego słownictwa. Wytrenuj model na dokumentach przeplatanych, z jedną stratą i jednym dekoderem autoregresyjnym, a bezpłatnie odblokujesz generowanie mieszanej modalności.

## Koncepcja

### VQ-VAE jako tokenizator obrazu

Tokenizator to wariacyjny autokoder skwantowany wektorowo. Architektura:

- Koder: CNN + ViT, który odwzorowuje obraz na mapę cech przestrzennych, powiedzmy cechy 32x32 o przyciemnieniu 256.
- Książka kodowa: wyuczone słownictwo wektorów K (Chameleon używa 8192), także przyciemnione 256.
- Kwantyzacja: dla każdej cechy przestrzennej wyszukaj najbliższy wpis w książce kodowej według odległości L2. Zamień cechę ciągłą na indeks całkowity.
- Dekoder: CNN, który przenosi skwantowane funkcje z powrotem do pikseli.

Szkolenie: utrata rekonstrukcji VAE + utrata zaangażowania + utrata książki kodowej. Indeksy książki kodowej tworzą dyskretny alfabet dla obrazów.

W przypadku Chameleona: jeden obraz staje się 32*32 = 1024 tokenami pobranymi ze słownika 8192. Połącz z tokenami tekstowymi (ze słownika BPE LLM, powiedzmy 32000). Końcowe słownictwo: 40192. Transformator widzi jedną sekwencję, jedną stratę.

### Wspólne słownictwo

Słownictwo Chameleona łączy tokeny tekstowe, tokeny graficzne i separatory modalności. Każdy token ma jeden identyfikator. Warstwa osadzania danych wejściowych odwzorowuje każdy identyfikator na ukryty wektor D-dim. Mapy projekcji wyjściowych ukryte z powrotem do logitów słownikowych. Softmax wybiera następny token, niezależnie od modalności.

Separatory mają znaczenie: tagi `<image>` i `</image>` nawiasują sekwencję tokenów obrazu. Jeśli w czasie generowania model emituje `<image>`, oprogramowanie znajdujące się poniżej wie, że kolejne 1024 tokeny to indeksy VQ, które należy wysłać do dekodera w celu renderowania pikseli.

### Generowanie w trybie mieszanym

Wnioskowanie to przewidywanie następnego tokenu we wspólnym słownictwie. Przykładowy monit: „Narysuj kota i opisz go”. Kameleon emituje:

```
<image> 4821 1029 2891 ... (1024 image tokens) </image>
The cat is orange, sitting on a windowsill...
```

Model samodzielnie wybiera kolejność — może utworzyć obraz, potem tekst, tekst, potem obraz lub przeplatać. Ten sam dekoder, ta sama strata.

Porównanie z adapterami VLM, w których generowanie odbywa się wyłącznie w trybie tekstowym. Chameleon ponownie otwiera kwestię modalności wyjściowych modelu.

### Stabilność treningu — QK-Norm, przerwanie, kolejność LayerNorm

Szkolenie w zakresie wczesnej fuzji jest niestabilne na skalę. Artykuł Chameleona dokumentuje trzy sztuczki:

- Norma QK. Zastosuj LayerNorm do zapytania i kluczowych rzutów w uwadze, przed iloczynem kropkowym. Zapobiega eksplozji o wielkości logitowej na głębokości. Używany przez wiele dużych modeli po 2024 roku.
- Miejsce porzucenia. Rezygnacja po każdym dodaniu reszty, a nie tylko po zwróceniu uwagi i MLP. Wymagana jest większa regularyzacja, gdy mogą dominować gradienty z tokenów obrazu.
- Porządkowanie LayerNorm. Pre-LN na odgałęzieniu resztkowym (standard), plus dodatkowy LN na połączeniu pomijanym ostatniego bloku. Stabilizuje przepływ gradientowy ostatniej warstwy.

Bez tych sztuczek trening Chameleona o parametrach 34B różnił się w wielu punktach kontrolnych. Z nimi to się zbiega. Recepta na trening jest w takim samym stopniu wkładem, jak architektura.

### Sufit rekonstrukcji tokenizera

VQ-VAE jest stratny. Przy 8192 wpisach książki kodowej i 1024 tokenach na obraz 512x512, rekonstrukcja PSNR ogranicza się do około 26-28 dB. To wystarczy do generowania rozpoznawalnego obrazu, ale jest wyraźnie gorsze niż dyfuzja w przestrzeni ciągłej (Stable Diffusion 3 osiąga 32+ dB).

Tokenizer jest wąskim gardłem. Lepsze tokenizery (MAGVIT-v2, IBQ, SBER-MoVQGAN) podnoszą sufit. Emu3 (lekcja 12.12) osiąga generację o jakości SDXL dzięki samemu lepszemu tokenizerowi.

### Kameleon kontra BLIP-2 / LLaVA

Chameleon (wczesna fuzja, wspólne słownictwo):
- Jedna strata, jeden dekoder.
- Generuje dane wyjściowe o mieszanej modalności.
- Tokenizer to pułap jakości.
- Drogie: dekoder VQ-VAE na wygenerowany obraz na ścieżce wnioskowania.

BLIP-2 / LLaVA (późna fuzja, oddzielne wieże):
- Wizja, tylko tekst.
- Ponownie wykorzystuje wstępnie przeszkolony LLM.
- Brak wąskiego gardła tokenizera dla zrozumienia.
- Tanie: pojedyncze podanie do przodu.

Wybierz według zadania. Jeśli potrzebujesz generowania obrazu, rodzina Chameleon. Jeśli potrzebujesz tylko zrozumienia, adapter-VLM jest prostszy i wykorzystuje więcej wstępnie przeszkolonych obliczeń.

### Fuyu i AnyGPT

Fuyu (Adept, 2023) to pokrewne podejście: całkowicie pomiń oddzielny koder wizji, przepuść surowe fragmenty obrazu przez projekcję wejściową LLM tak, jakby były tokenami, bez tokenizatora. Prostszy niż Chameleon, traci generowanie wyników współdzielonego słownika.

AnyGPT (Zhan i in., 2024) rozszerza Chameleon na cztery modalności: tekst, obraz, mowę i muzykę. Ta sama sztuczka VQ-VAE dla każdego wspólnego transformatora. Każde pokolenie. Więcej omówiono w lekcji 12.16.

## Użyj tego

`code/main.py` buduje zabawkowy, kompleksowy model wczesnej syntezy:

- Mały kwantyzator w stylu VQ-VAE, który odwzorowuje pola 8x8 na indeksy książki kodowej (K=16).
- Wspólne słownictwo (identyfikatory tekstu 0..31) + (identyfikatory obrazów 32..47) + (separatory 48, 49).
- Zabawkowy dekoder autoregresyjny (tabela bigramów) wytrenowany na syntetycznych podpisach + sekwencje tokenów obrazu.
- Pętla próbkowania, która emituje naprzemienny tekst i tokeny obrazu po otrzymaniu monitu.

Kod celowo sprawia, że ​​transformator jest mały (bigramy), dzięki czemu można prześledzić przepływ sygnału od końca do końca.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-tokenizer-vs-adapter-picker.md`. Biorąc pod uwagę specyfikację produktu (tylko zrozumieć vs zrozumieć + wygenerować, wymagana jakość obrazu, budżet), wybiera pomiędzy rodziną Chameleon (wczesna fuzja) a rodziną LLaVA (późna fuzja) i uzasadnia to ilościowymi zasadami.

## Ćwiczenia

1. Chameleon wykorzystuje K=8192 wpisów w książce kodów i 1024 tokenów na obraz 512x512. Oszacuj współczynnik kompresji w porównaniu z 24-bitowym obrazem RGB. Czy jest stratny? Jak stratny?

2. Ile tokenów obrazu tworzy obraz 4K (3840x2160) przy tej samej gęstości VQ-VAE? Czy model w stylu Chameleon może wygenerować obraz 4K w jednym wywołaniu wnioskowania? Co psuje się jako pierwsze — kontekst, jakość tokenizera czy pamięć podręczna KV?

3. Zaimplementuj QK-Norm w czystym Pythonie. Biorąc pod uwagę zapytanie i klucz o 64 dim, pokaż iloczyn skalarny przed i po LayerNorm. Dlaczego kontrola wielkości jest ważna na głębokości?

4. Przeczytaj rozdział 2.3 Chameleon dotyczący stabilności treningu. Opisz dokładny tryb awarii, jaki zaobserwował papier w 34B bez normy QK. Jaki był podpis „normalnej eksplozji”?

5. Rozszerz dekoder zabawki, aby emitował odpowiedź o mieszanej modalności, po otrzymaniu monitu tekstowego. Zmierz, jak często model wybiera najpierw obraz w porównaniu z tekstem, biorąc pod uwagę dystrybucję danych szkoleniowych 60% najpierw tekst / 40% najpierw obraz.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Wczesna fuzja | „Ujednolicone tokeny” | Obrazy zamienione na dyskretne tokeny udostępniające słownictwo transformatora z kroku pierwszego |
| VQ-VAE | „Tokenizator obrazu” | CNN + ViT + książka kodów, która odwzorowuje obrazy na indeksy całkowite, które transformator może przewidzieć |
| Wspólne słownictwo | „Jeden słownik” | Pojedyncza przestrzeń identyfikacyjna tokenu obejmująca tekst + obraz + separatory modalności |
| Norma QK | „Stabilizator uwagi” | LayerNorm zastosowany do zapytania i klucza przed iloczynem skalarnym, zapobiega powielaniu norm |
| Generacja mieszana | „Tekst + obraz” | Wnioskowanie, które autonomicznie generuje przeplatane tokeny tekstu i obrazu w jednym przebiegu |
| Rozmiar książki kodowej | „K wpisów” | Liczba dyskretnych wektorów, do których VQ-VAE może kwantyzować; zamienia kompresję na wierność |
| Sufit tokenizera | „Granica odbudowy” | Najlepszy PSNR osiągalny poprzez dekodowanie tokenów VQ; ogranicza jakość obrazu modelu |

## Dalsze czytanie

— [Zespół Chameleon — Chameleon: Mieszane modalne modele wczesnej fuzji (arXiv:2405.09818)](https://arxiv.org/abs/2405.09818)
- [Aghajanyan i in. — CM3 (arXiv:2201.07520)](https://arxiv.org/abs/2201.07520)
- [Yu i in. — CM3Leon (arXiv:2309.02591)](https://arxiv.org/abs/2309.02591)
- [Zhan i in. — AnyGPT (arXiv:2402.12226)](https://arxiv.org/abs/2402.12226)
- [Adept — blog Fuyu-8B (adept.ai)](https://www.adept.ai/blog/fuyu-8b)