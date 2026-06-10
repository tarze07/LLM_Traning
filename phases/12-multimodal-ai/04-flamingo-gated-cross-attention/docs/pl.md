# Flamingo i bramkowana uwaga krzyżowa dla kilku VLM-ów

> Flamingo (2022) firmy DeepMind zrobił dwie rzeczy przed kimkolwiek innym. Pokazało, że pojedynczy model może przetwarzać dowolnie przeplatane sekwencje obrazów, filmów i tekstu. Pokazało też, że VLM mogą uczyć się w kontekście — wyświetlają monit składający się z kilku ujęć z trzema przykładowymi parami (obraz i podpis), a model podpisuje nowy obraz bez żadnego kroku gradientu. Mechanizm: bramkowane warstwy wzajemnej uwagi, umieszczone pomiędzy zamrożonymi istniejącymi warstwami LLM, z wyuczoną bramką tanha, która zaczyna się od zera, dzięki czemu zdolność tekstowa LLM zostaje zachowana podczas inicjalizacji. Ta lekcja dotyczy resamplera Perceiver firmy Flamingo i bramkowanej architektury krzyżowej uwagi — przodka przeplatanych danych wejściowych Gemini i tokenów wizualnych Idefics2.

**Typ:** Ucz się
**Języki:** Python (stdlib, bramkowana funkcja cross-attention + demo resamplera Perceiver)
**Wymagania wstępne:** Faza 12 · 03 (BLIP-2 Q-Former)
**Czas:** ~120 minut

## Cele nauczania

- Wyjaśnij, w jaki sposób bramkowana uwaga krzyżowa zachowuje zdolność tekstową zamrożonego LLM podczas inicjalizacji poprzez tanh(gate) = 0.
- Przejdź przez moduł resamplera Perceiver: N poprawek obrazu → K naprawionych „ukrytych” zapytań poprzez wzajemne skupienie.
- Opisz, jak Flaming radzi sobie z przeplatanymi sekwencjami obrazu i tekstu z maskowaniem przyczynowym, które uwzględnia rozmieszczenie obrazu.
- Odtwórz wielomodalną strukturę podpowiedzi składającą się z kilku ujęć (3 przykłady podpisów obrazów, a następnie obraz zapytania).

## Problem

BLIP-2 dostarcza 32 tokeny wizualne do zamrożonej warstwy wejściowej LLM. Działa dla jednego obrazu na monit. Ale co, jeśli chcesz zasilić *wiele* obrazów przeplatanych tekstem, jak w przypadku „tutaj jest obraz A, opisz go; tutaj jest obraz B, opisz go; teraz tutaj jest obraz C, podpisz go”? Samouważność LLM musiałaby obsłużyć tokeny graficzne i tokeny tekstowe w jednym strumieniu oraz kwestię, które pozycje mogą zająć, które obrazy stają się wybredne.

Odpowiedź Flamingo: w ogóle nie zmieniaj strumienia wejściowego LLM. Wstaw dodatkowe warstwy wzajemnej uwagi pomiędzy istniejącymi blokami LLM. Tokeny tekstowe nadal jak zawsze przepływają przez przyczynową samouważność LLM. Co kilka bloków LLM tokeny tekstowe również łączą się z funkcjami obrazu za pośrednictwem nowej warstwy bramkowanej. Bramka (zainicjowana na zero) oznacza, że ​​w kroku zerowym nowe warstwy nie działają — model zachowuje się dokładnie tak, jak wstępnie wyszkolony LLM. W miarę postępu szkolenia brama otwiera się i zaczynają płynąć informacje wizualne.

Drugie pytanie, na które odpowiedział Flamingo: jak radzisz sobie ze zmienną liczbą obrazów (0, 1 lub wiele) na zachętę? Resampler Perceiver — mały moduł skupiający uwagę, który pobiera dowolną liczbę posiadanych poprawek i generuje stałą liczbę ukrytych tokenów wizualnych. Warstwa wzajemnej uwagi LLM widzi ten sam kształt niezależnie od liczby obrazów w monicie.

## Koncepcja

### Zamrożony LLM

Flaming zaczyna od mrożonej szynszyli 70B LLM. Wszystkie obciążniki 70B nietknięte. Istniejący tekst samouważności i FFN działają normalnie.

### Próbnik perceivera

Dla każdego obrazu w monicie ViT generuje N żetonów łatek. Resampler Perceiver ma K stałych, możliwych do nauczenia się latentów (Flamingo używa K=64). Każdy blok resamplera składa się z dwóch podetapów:

1. Wzajemna uwaga: Utajone K nadzorują N żetonów łaty (Q z utajonych, K/V z łatek).
2. Samouważność + FFN w utajonych.

Po 6 blokach resamplera na wyjściu znajduje się K=64 wizualnych tokenów o dim 1024, niezależnie od tego, ile fragmentów wytworzył ViT. Obraz 224x224 (196 fragmentów) i obraz 480x480 (900 fragmentów) są wysyłane jako 64 tokeny resamplera.

W przypadku wideo resampler jest stosowany czasowo: fragmenty każdej klatki tworzą 64 utajone kodowania, a czasowe kodowanie pozycyjne pozwala modelowi odróżnić t=0 od t=N. Pełne wideo staje się tokenami wizualnymi T * 64.

### Bramkowana uwaga krzyżowa

Pomiędzy każdymi M warstwami zamrożonego LLM (Flamingo używa M=4) wstaw nowy bramkowany blok uwagi:

```
x_after_llm_block = llm_block(x_before)
cross = cross_attn(x_after, resampler_output)
gated = tanh(alpha) * cross + x_after
x_before_next_block = gated
```

- `alpha` to skalar, którego można się nauczyć, zainicjowany na zero.
- `tanh(0) = 0`, więc na początku gałąź bramkowana wnosi zero.
- W miarę jak `alpha` odchodzi od zera, udział wzajemnej uwagi rośnie płynnie.
- Połączenie resztkowe oznacza, że ​​nawet całkowicie otwarta brama nie nadpisuje reprezentacji tekstowej LLM; po prostu dodaje informacje wizualne na górze.

Jest to najważniejszy wybór projektowy we Flamingo: warunkowanie wizualne jest addytywne, bramkowane i zerowane przy inicjalizacji. Flaming w kroku 0 to idealna szynszyla 70B, jeśli wprowadzane są tylko teksty.

### Maskowana uwaga krzyżowa dla przeplatanych wejść

W podpowiedzi takiej jak „<image A> caption A <image B> caption B <image C>?” każdy znacznik tekstowy powinien wyświetlać tylko obrazy, które pojawiły się przed nim w sekwencji. Maska wzajemnej uwagi wymusza: token tekstowy na pozycji `t` obsługuje tylko tokeny modułu ponownego próbkowania obrazu, których indeks obrazu `i < i_t` gdzie `i_t` jest najnowszym obrazem przed pozycją `t`. „Widzi tylko ostatni poprzedni obraz” lub „widzi wszystkie poprzednie obrazy” to prawidłowe opcje; Flaming wybrał to pierwsze.

### Krótka nauka kontekstowa

Podpowiedź Flamingo wygląda następująco:

```
<image1> A photo of a cat. <image2> A photo of a dog. <image3> A photo of a
```

Model widzi wzorzec ukończenia i wyświetla „ptak” (lub cokolwiek innego, co pokazuje obraz 3). Brak stopni gradientu. Zdolność uczenia się w kontekście zamrożonego LLM przenosi się poprzez bramkowaną uwagę krzyżową — oto puenta artykułu i powód, dla którego jest to ważne.

### Dane treningowe

Flamingo trenował na trzech zbiorach danych:

1. MultiModal MassiveWeb (M3W): 43 miliony stron internetowych z przeplatanymi obrazami i tekstem, odtwarzające kolejność czytania.
2. Pary obraz-tekst (ALIGN + LTIP): 4,4B par.
3. Pary wideo-tekst (VTP): 27 milionów krótkich klipów wideo.

OBELICS (2023) to otwarta reprodukcja przeplatanego korpusu sieci, na którym trenują Idefics, Idefics2 i większość otwartych modeli „podobnych do flamingów”.

### OpenFlamingo i Wydra

OpenFlamingo (2023) jest reprodukcją otwartą. Architektura identyczna (resampler Perceivera + bramkowana uwaga krzyżowa na zamrożonym LLaMA lub MPT). Punkty kontrolne przy 3B, 4B, 9B. Jakość jest opóźniona we Flamingo ze względu na mniejszą bazę LLM i mniej danych.

Otter (2023) opiera się na OpenFlamingo z dostrajaniem instrukcji w MIMIC-IT (zbiór danych instrukcji multimodalnych), pokazując działania bramkowanej uwagi krzyżowej również w przypadku wykonywania instrukcji.

### Potomkowie

- Idefics / Idefics2 / Idefics3: Bramkowana linia uwagi krzyżowej Hugging Face, coraz prostsza (Idefics2 porzucił resampler na rzecz tokenów bezpośrednich łat z adaptacyjnym łączeniem).
- Przejście z Flaminga na Kameleona: do 2024 r. wiele zespołów przeszło na wczesną fuzję (lekcja 12.11); Tam, gdzie wymagane jest zamrażanie szkieletu, w produkcji pozostaje bramkowana kontrola uwagi w stylu flamingów.
- Przeplatane dane wejściowe Gemini: koncepcyjnie dziedziczy elastyczność formatu przeplatanego Flamingo, chociaż dokładny mechanizm jest zastrzeżony.

### Porównanie z BLIP-2

| | BLIP-2 | Flaming |
|---|---|---|
| Most wizualny | Q-Former raz na wejściu | Bramkowana uwaga krzyżowa na każdej warstwie M |
| Tokeny wizualne | 32 na obraz | 64 na obraz na warstwę krzyżową |
| Zamrożone LLM | Tak | Tak |
| Kilka ujęć w kontekście | Słaby | Mocny — centralny element gazety |
| Przeplatane wejścia | Brak natywnego wsparcia | Tak, cel projektu |
| Dane treningowe | 130 mln par | 1,3 miliarda par + 43 miliony przeplatanych stron |
| Liczba parametrów | 188M przeszkolonych | Przeszkolonych ~10B (warstwy między sieciami) |
| Oblicz | Dni na 8 A100 | Tygodnie na tysiącach TPUv4 |

Wybierz BLIP-2, aby uzyskać VQA na jednym obrazie przy ograniczonym budżecie. Wybierz Flamingo/Idefics2 do wnioskowania przeplatanego, kilku ujęć lub wielu obrazów.

## Użyj tego

`code/main.py` demonstruje:

1. Resampler Perceivera na 36 fałszywych tokenach łatek z 8 możliwymi do nauczenia się ukrytymi cechami (czysta uwaga krzyżowa w Pythonie).
2. Etap bramkowanej uwagi, w którym `alpha = 0` → wynik równa się wejściu (LLM bez zmian), następnie `alpha = 2.0` → zmieszany wkład wizualny.
3. Konstruktor masek przeplatanych, który tworzy dwuwymiarową maskę uwagi dla sekwencji „(obraz 1) (tekst 1) (obraz 2) (tekst 2)”.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-gated-bridge-diagnostic.md`. Biorąc pod uwagę otwartą konfigurację VLM (resampler T/N, częstotliwość cross-attn, schemat bramki), identyfikuje ona elementy linii Flamingo i wyjaśnia strategię zamrażania. Przydatne do debugowania, dlaczego należy dostroić obniżoną wydajność tekstu (odpowiedź: brama stała się zbyt szeroka i zbyt szybko).

## Ćwiczenia

1. Oblicz liczbę parametrów wizualnych Flamingo-9B: 9B LLM + 1,4B bramkowanych warstw krzyżowej uwagi + 64M resamplera. Jaka część wszystkich parametrów jest trenowana?

2. Zaimplementuj bramkowaną resztę `y = tanh(alpha) * cross + x` w PyTorch. Pokaż eksperymentalnie, że z `alpha=0`, `y==x` dokładnie na początku.

3. Przeczytaj sekcję 3.2 OpenFlamingo (arXiv:2308.01390) na temat obsługi wielu obrazów wsadowo, gdy każdy monit ma inną liczbę obrazów. Opisz strategię wypełniania.

4. Dlaczego maska ​​skupienia uwagi Flamingo pozwala, aby token tekstowy obsługiwał *tylko najnowszy* poprzedzający obraz, a nie wszystkie poprzedzające obrazy? Przeczytaj artykuł Flamingo, sekcja 2.4 i wyjaśnij kompromis.

5. Kilka ujęć w kontekście: utwórz zachętę z 4 przykładami „obrazu → koloru głównego obiektu” dla nowego wariantu Flamingo. Opisz oczekiwany wzór dokładności, zmieniając liczbę przykładów od 0 do 8.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Resampler perceivera | „Stała-ukryta uwaga krzyżowa” | Moduł wytwarzający K stałych tokenów ze zmiennej liczby poprawek wejściowych |
| Bramkowana uwaga | „Most z bramą Tanh” | Warstwa resztkowa `y = tanh(alpha)*cross + x`, alfa do nauczenia, init 0 |
| Dane wejściowe z przeplotem | „Sekwencja mieszana” | Prosty format z obrazami i tekstem swobodnie mieszanymi w kolejności czytania |
| Zamrożone LLM | „Brak gradientów LLM” | Tekst Wagi LLM nie są aktualizowane; tylko resampler + pociąg warstw krzyżowych |
| Kilka strzałów | „Przykłady w kontekście” | Podaj kilka par (obrazek, odpowiedź) w podpowiedzi; model uogólnia bez dostrajania |
| OBELIKI | „Przeplatany korpus sieciowy” | Otwarty zbiór danych obejmujący 141 milionów stron internetowych z obrazami i tekstem w kolejności czytania |
| Szynszyla | „Zamrożona baza 70B” | Zamrożony tekst Flamingo LLM, z artykułu o szynszyli firmy DeepMind |
| Harmonogram bramek | „Jak porusza się alfa” | Szybkość, z jaką otwiera się bramka krzyżowo-uważna podczas treningu |
| Częstotliwość krzyżowa | „Co M warstw” | Jak często wstawiana jest bramkowana blokada uwagi; Flaming wykorzystuje M=4 |
| OtwórzFlamingo | „Reprodukcja otwarta” | Otwarty punkt kontrolny MosaicML/LAION pod adresem 3-9B; architektura identyczna z Flamingo |

## Dalsze czytanie

- [Alayrac i in. — Flamingo (arXiv:2204.14198)](https://arxiv.org/abs/2204.14198) — artykuł oryginalny.
- [Awadalla i in. — OpenFlamingo (arXiv:2308.01390)](https://arxiv.org/abs/2308.01390) — reprodukcja otwarta.
- [Laurençon i in. — OBELICS (arXiv:2306.16527)](https://arxiv.org/abs/2306.16527) — przeplatany korpus sieciowy.
- [Jaegle i in. — Perceiver IO (arXiv:2107.14795)](https://arxiv.org/abs/2107.14795) — ogólna architektura Perceiver.
- [Li i in. — Wydra (arXiv:2305.03726)](https://arxiv.org/abs/2305.03726) — potomek Flaminga dostrojony do instrukcji.
- [Laurençon i in. — Idefics2 (arXiv:2405.02246)](https://arxiv.org/abs/2405.02246) — nowoczesne uproszczenie podejścia Flamingo.