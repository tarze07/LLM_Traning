# Flamingo i bramkowana uwaga krzyżowa dla modeli VLM few-shot

> Flamingo (2022) firmy DeepMind wprowadził dwa kluczowe rozwiązania przed konkurencją. Po pierwsze, wykazał, że pojedynczy model może przetwarzać dowolnie przeplatane sekwencje obrazów, wideo i tekstu. Po drugie, udowodnił, że modele VLM potrafią uczyć się w kontekście (in-context learning) — wystarczy podać prompt zawierający kilka ujęć (few-shot) z trzema przykładowymi parami obraz-opis, a model opisze nowy obraz bez wykonywania jakichkolwiek kroków aktualizacji gradientu. Odpowiada za to mechanizm: bramkowane warstwy cross-attention wstawione pomiędzy zamrożone warstwy LLM, z trenowalnym parametrem bramkowania tanh, który startuje od zera, co pozwala na pełne zachowanie zdolności tekstowych LLM podczas inicjalizacji. Lekcja ta omawia moduł Perceiver Resampler oraz architekturę bramkowanego cross-attention — prekursora przeplatanych danych wejściowych w Gemini oraz tokenów wizualnych w Idefics2.

**Typ:** Teoria / Zrozumienie
**Języki:** Python (biblioteka standardowa, bramkowany mechanizm cross-attention + demonstracja Perceiver Resampler)
**Wymagania wstępne:** Faza 12 · Lekcja 03 (BLIP-2 Q-Former)
**Czas:** ~120 minut

## Cele nauczania

- Wyjaśnij, w jaki sposób bramkowane cross-attention zachowuje zdolności tekstowe zamrożonego LLM podczas inicjalizacji dzięki ustawieniu tanh(gate) = 0.
- Zrozum działanie modułu Perceiver Resampler: mapowanie N patchy obrazu na K stałych „ukrytych” (latent) zapytań za pomocą mechanizmu cross-attention.
- Opisz, jak Flamingo przetwarza przeplatane sekwencje obrazów i tekstów za pomocą maskowania przyczynowego (causal masking) uwzględniającego pozycję obrazu.
- Odtwórz strukturę promptu multimodalnego dla uczenia few-shot (np. 3 przykłady opisów obrazów, po których następuje obraz zapytania).

## Problem

BLIP-2 przekazuje 32 tokeny wizualne bezpośrednio do zamrożonej warstwy wejściowej LLM. To rozwiązanie sprawdza się w przypadku jednego obrazu na prompt. Co jednak zrobić, gdy chcesz przekazać *wiele* obrazów przeplatanych tekstem, np.: „oto obraz A, opisz go; oto obraz B, opisz go; a teraz oto obraz C, podpisz go”? Warstwa self-attention modelu LLM musiałaby obsłużyć tokeny obrazów i tekstu w jednym strumieniu, a określenie, które pozycje mogą ze sobą oddziaływać, staje się skomplikowane i nieefektywne.

Rozwiązanie Flamingo: nie zmieniaj w ogóle wejściowego strumienia tokenów LLM. Zamiast tego wstaw dodatkowe warstwy cross-attention pomiędzy istniejącymi blokami LLM. Tokeny tekstowe przepływają jak zwykle przez przyczynowe (causal) warstwy self-attention LLM. Co kilka bloków LLM integrują się one również z cechami obrazu za pośrednictwem nowej bramkowanej warstwy. Współczynnik bramkowania (zainicjowany na zero) sprawia, że w kroku zerowym nowe warstwy nie wpływają na model — zachowuje się on dokładnie tak, jak oryginalnie wytrenowany LLM. W miarę postępu treningu bramka się otwiera i zaczyna przepływać informacja wizualna.

Drugie pytanie, na które odpowiada Flamingo: jak radzić sobie ze zmienną liczbą obrazów (0, 1 lub wiele) w prompcie? Służy do tego Perceiver Resampler — mały moduł uwagi, który pobiera dowolną liczbę patchy obrazu i generuje stałą liczbę wejściowych tokenów wizualnych. Dzięki temu warstwa cross-attention w LLM widzi ten sam kształt danych niezależnie od liczby obrazów w prompcie.

## Koncepcja

### Zamrożony LLM

Flamingo bazuje na zamrożonym modelu LLM Chinchilla 70B. Wszystkie wagi 70B parametrów pozostają nienaruszone. Istniejące warstwy self-attention dla tekstu oraz sieci FFN działają normalnie.

### Perceiver Resampler

Dla każdego obrazu w prompcie encoder ViT generuje N tokenów patchy. Perceiver Resampler posiada K stałych, trenowalnych wektorów latentnych (Flamingo używa K=64). Każdy blok resamplera składa się z dwóch podetapów:

1. Cross-attention: wektory latentne K odpytują N tokenów patchy (Q pochodzi z latentów, K/V z patchy).
2. Self-attention + FFN na wektorach latentnych.

Po przejściu przez 6 bloków resamplera na wyjściu otrzymujemy dokładnie K=64 tokenów wizualnych o wymiarze (dim) 1024, niezależnie od tego, ile patchy wygenerował encoder ViT. Zarówno obraz 224x224 (196 patchy), jak i obraz 480x480 (900 patchy) są konwertowane do 64 tokenów resamplera.

W przypadku wideo resampler jest stosowany w wymiarze czasowym: patche z każdej klatki tworzą 64 latentne reprezentacje, a czasowe kodowanie pozycyjne (temporal positional encoding) pozwala modelowi odróżnić t=0 od t=N. Cały klip wideo jest reprezentowany jako sekwencja tokenów wizualnych o rozmiarze T * 64.

### Bramkowana uwaga krzyżowa (Gated Cross-Attention)

Co M warstw zamrożonego LLM (we Flamingo M=4) wstawiany jest nowy bramkowany blok uwagi (GATED FATT, Gated Attention Dense):

```
x_after_llm_block = llm_block(x_before)
cross = cross_attn(x_after, resampler_output)
gated = tanh(alpha) * cross + x_after
x_before_next_block = gated
```

- `alpha` to trenowalny skalar, zainicjowany wartością zero.
- `tanh(0) = 0`, co oznacza, że na początku treningu ścieżka bramkowana zwraca zero.
- W miarę wzrostu wartości `alpha` wpływ mechanizmu cross-attention rośnie w płynny sposób.
- Połączenie rezydualne (residual connection) gwarantuje, że nawet przy w pełni otwartej bramce reprezentacja tekstowa z LLM nie zostanie nadpisana; informacje wizualne są do niej jedynie dodawane.

Jest to najważniejsza decyzja projektowa we Flamingo: warunkowanie wizualne jest addytywne, bramkowane i zerowane przy inicjalizacji. W kroku zerowym (step 0) Flamingo zachowuje się dokładnie jak oryginalna Chinchilla 70B, jeśli wejściem jest wyłącznie tekst.

### Maskowane cross-attention dla przeplatanych danych wejściowych

W prompcie typu „<image A> opis A <image B> opis B <image C>?” każdy token tekstowy powinien brać pod uwagę tylko te obrazy, które pojawiły się przed nim w sekwencji. Maska cross-attention wymusza, aby token tekstowy na pozycji `t` przetwarzał wyłącznie tokeny z resamplera obrazu o indeksie `i < i_t`, gdzie `i_t` to indeks ostatniego obrazu występującego przed pozycją `t`. Można wybrać strategię „widzi tylko ostatni poprzedni obraz” lub „widzi wszystkie poprzedzające obrazy”; autorzy Flamingo wybrali tę pierwszą.

### Uczenie few-shot w kontekście (In-Context Learning)

Przykładowy prompt dla Flamingo wygląda następująco:

```
<image1> A photo of a cat. <image2> A photo of a dog. <image3> A photo of a
```

Model rozpoznaje wzorzec i generuje odpowiednie słowo (np. „bird” – w zależności od tego, co przedstawia trzeci obraz). Odbywa się to bez jakiejkolwiek aktualizacji wag (gradientu). Zdolność uczenia w kontekście zamrożonego LLM jest przekazywana do warstw wizualnych dzięki bramkowanemu cross-attention — i to jest główny wniosek oraz siła tej architektury.

### Dane treningowe

Flamingo zostało przeszkolone na trzech głównych zbiorach danych:

1. MultiModal MassiveWeb (M3W): 43 miliony stron internetowych zawierających przeplatane obrazy i tekst, zachowujące naturalną kolejność czytania.
2. Pary obraz-tekst (ALIGN + LTIP): 4,4 miliarda par.
3. Pary wideo-tekst (VTP): 27 milionów krótkich klipów wideo.

OBELICS (2023) to otwarta reprodukcja przeplatanego korpusu internetowego, na którym trenowano modele Idefics, Idefics2 oraz większość otwartych modeli typu „Flamingo”.

### OpenFlamingo i Otter

OpenFlamingo (2023) to otwarta implementacja tej architektury (Perceiver Resampler + bramkowane cross-attention na zamrożonych modelach LLaMA lub MPT) z checkpointami o rozmiarach 3B, 4B i 9B. Wyniki są nieco słabsze niż w przypadku oryginalnego Flamingo ze względu na mniejszy bazowy LLM oraz mniejszą ilość danych treningowych.

Otter (2023) bazuje na OpenFlamingo i dodaje dostrajanie instruktażowe na zbiorze MIMIC-IT (multimodal instruction dataset), wykazując skuteczność bramkowanego cross-attention również w zadaniach wykonywania instrukcji.

### Następcy i warianty

- Idefics / Idefics2 / Idefics3: Linia modeli od Hugging Face z bramkowanym cross-attention, ulegająca ciągłemu uproszczeniu (Idefics2 zrezygnował z resamplera na rzecz bezpośrednich tokenów patchy z adaptacyjnym poolingiem).
- Przejście do wczesnej fuzji (early fusion): do 2024 roku wiele zespołów przeszło na architekturę wczesnej fuzji tokenów (Lekcja 12.11); w scenariuszach wymagających zamrożenia modeli bazowych bramkowana uwaga w stylu Flamingo nadal pozostaje kluczowym rozwiązaniem wdrożeniowym.
- Przeplatany kontekst w Gemini: koncepcyjnie dziedziczy elastyczność przeplatanych danych z Flamingo, choć dokładny mechanizm działania jest autorskim rozwiązaniem producenta.

### Porównanie z BLIP-2

| Cecha | BLIP-2 | Flamingo |
|---|---|---|
| Mostek wizualny | Q-Former aplikowany raz na wejściu | Bramkowane cross-attention wstawiane co M warstw LLM |
| Tokeny wizualne | 32 na obraz | 64 na obraz na każdą warstwę cross-attention |
| Zamrożony LLM | Tak | Tak |
| Uczenie few-shot | Słabe | Silne — kluczowy atut publikacji |
| Przeplatane dane wejściowe | Brak natywnego wsparcia | Tak, podstawowy cel projektowy |
| Dane treningowe | 130 milionów par | 1,3 miliarda par + 43 miliony przeplatanych stron www |
| Liczba trenowanych parametrów | 188M | ~10B (dodatkowe warstwy wstawione do LLM) |
| Zasoby obliczeniowe | Dni na 8 kartach A100 | Tygodnie na tysiącach jednostek TPUv4 |

Wybierz BLIP-2 dla zadań VQA na pojedynczych obrazach przy ograniczonych zasobach. Wybierz Flamingo/Idefics2 dla przeplatanych danych wejściowych, uczenia few-shot lub analizy wielu obrazów jednocześnie.

## Użycie praktyczne

Skrypt `code/main.py` demonstruje:

1. Działanie Perceiver Resampler na 36 testowych tokenach patchy z użyciem 8 trenowalnych wektorów latentnych (czysty mechanizm cross-attention napisany w Pythonie).
2. Działanie kroku bramkowanego cross-attention: gdy `alpha = 0` → wyjście jest równe wejściu (brak zmian w LLM), a gdy `alpha = 2.0` → następuje wymieszanie reprezentacji z cechami wizualnymi.
3. Generator masek dla przeplatanego wejścia, tworzący dwuwymiarową maskę uwagi dla sekwencji: „(obraz 1) (tekst 1) (obraz 2) (tekst 2)”.

## Zadanie zaliczeniowe

W ramach tej lekcji należy stworzyć dokument `outputs/skill-gated-bridge-diagnostic_pro.md`. Na podstawie specyfikacji otwartego modelu VLM (użycie resamplera, częstotliwość warstw cross-attention, schemat bramkowania), sklasyfikuj elementy architektury w odniesieniu do oryginalnego projektu Flamingo i wyjaśnij strategię zamrażania wag. Zadanie to jest przydatne do diagnozowania spadków jakości generowania tekstu (np. gdy współczynnik bramkowania rośnie zbyt szybko w początkowej fazie treningu).

## Ćwiczenia

1. Oblicz liczbę parametrów wizualnych w modelu Flamingo-9B: 9B LLM + 1,4B w ramach warstw bramkowanego cross-attention + 64M w module resamplera. Jaki procent wszystkich parametrów podlega trenowaniu?

2. Zaimplementuj bramkowane połączenie rezydualne `y = tanh(alpha) * cross + x` w PyTorch. Pokaż eksperymentalnie, że dla `alpha=0` na początku treningu zachodzi dokładnie `y == x`.

3. Przeczytaj sekcję 3.2 w artykule OpenFlamingo (arXiv:2308.01390) dotyczącą obsługi wielu obrazów w paczce (batch), gdy każdy prompt zawiera inną liczbę obrazów. Opisz zastosowaną strategię uzupełniania (padding).

4. Dlaczego maska uwagi we Flamingo pozwala tokenowi tekstowemu na przetwarzanie *wyłącznie ostatniego* poprzedzającego go obrazu, zamiast wszystkich obrazów wcześniejszych? Przeczytaj sekcję 2.4 w artykule o Flamingo i wyjaśnij ten kompromis projektowy.

5. Uczene few-shot w kontekście: stwórz prompt z 4 przykładami w formacie „obraz → dominujący kolor obiektu” dla modelu Flamingo. Opisz przewidywany wykres dokładności (accuracy) przy zmianie liczby przykładów od 0 do 8.

## Słownik pojęć

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| Perceiver Resampler | „Latent cross-attention” | Moduł generujący stałą liczbę K tokenów wizualnych z dowolnej, zmiennej liczby patchy wejściowych. |
| Bramkowana uwaga | „Mostek z bramką tanh” | Warstwa rezydualna `y = tanh(alpha) * cross + x` z trenowalnym parametrem alfa, zainicjowanym wartością 0. |
| Przeplatane dane wejściowe | „Mixed-modality sequence” | Format wejściowy, w którym obrazy i teksty są swobodnie przeplatane zgodnie z naturalną kolejnością czytania. |
| Zamrożony LLM | „Brak gradientów w LLM” | Wagi modelu tekstowego LLM pozostają niezmienne; trenowany jest tylko resampler oraz nowo dodane warstwy cross-attention. |
| Few-shot learning | „Uczenie z kilku przykładów” | Podanie w prompcie kilku par (obraz, odpowiedź) w celu uogólnienia wiedzy przez model bez aktualizacji wag. |
| OBELICS | „Przeplatany korpus webowy” | Otwarty zbiór danych zawierający 141 milionów stron internetowych z przeplatanymi obrazami i tekstami w kolejności czytania. |
| Chinchilla | „Zamrożona baza 70B” | Zamrożony model LLM będący podstawą tekstową oryginalnego Flamingo. |
| Harmonogram bramkowania | „Gate scheduling” | Sposób i tempo otwierania bramki cross-attention (czyli zmiany parametru alfa) w trakcie treningu. |
| Częstotliwość cross-attention | „Co ile warstw M” | Parametr określający, jak gęsto wstawiane są bloki bramkowanego cross-attention (we Flamingo M=4). |
| OpenFlamingo | „Otwarta replika” | Otwarta wersja modelu Flamingo o rozmiarach 3-9B przygotowana przez MosaicML/LAION. |

## Dalsze czytanie

- [Alayrac et al. — Flamingo (arXiv:2204.14198)](https://arxiv.org/abs/2204.14198) — oryginalna publikacja naukowa.
- [Awadalla et al. — OpenFlamingo (arXiv:2308.01390)](https://arxiv.org/abs/2308.01390) — otwarta reprodukcja projektu.
- [Laurençon et al. — OBELICS (arXiv:2306.16527)](https://arxiv.org/abs/2306.16527) — publikacja o przeplatanym zbiorze danych.
- [Jaegle et al. — Perceiver IO (arXiv:2107.14795)](https://arxiv.org/abs/2107.14795) — ogólna architektura Perceiver.
- [Li et al. — Otter (arXiv:2305.03726)](https://arxiv.org/abs/2305.03726) — model pochodny Flamingo z dostrojeniem instruktażowym.
- [Laurençon et al. — Idefics2 (arXiv:2405.02246)](https://arxiv.org/abs/2405.02246) — współczesne uproszczenie architektury Flamingo.
