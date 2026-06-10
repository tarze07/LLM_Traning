# GPT — przyczynowe modelowanie języka

> BERT widzi obie strony. GPT widzi tylko przeszłość. Maska trójkątna to najważniejsza pojedyncza linia kodu we współczesnej sztucznej inteligencji.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 02 (Samouwaga), Faza 7 · 05 (Pełny transformator), Faza 7 · 06 (BERT)
**Czas:** ~75 minut

## Problem

Model językowy odpowiada na jedno pytanie: mając pierwsze `t-1` tokenów, jaki jest rozkład prawdopodobieństwa dla tokenu `t`? Trenując na tym sygnale — przewidywaniu następnego tokenu — otrzymujemy model zdolny do generowania dowolnego tekstu, jeden token na raz.

Aby trenować od początku do końca na całej sekwencji, przewidywanie każdej pozycji musi zależeć wyłącznie od pozycji wcześniejszych. W przeciwnym razie model w trywialny sposób oszukuje, zaglądając do odpowiedzi.

Właśnie temu służy maska przyczynowa. Jest to pojedyncza macierz górnotrójkątna wypełniona wartościami `-inf`, dodawana do wyników uwagi przed softmaxem. Po zastosowaniu softmaxu zamaskowane pozycje otrzymują wagę zero — każda pozycja uwzględnia wyłącznie siebie i pozycje wcześniejsze. Ponieważ maskę stosuje się raz do całej sekwencji, w jednym przebiegu do przodu uzyskujemy N równoległych przewidywań następnego tokenu.

GPT-1 (2018), GPT-2 (2019), GPT-3 (2020), GPT-4 (2023), GPT-5 (2024), Claude, Llama, Qwen, Mistral, DeepSeek, Kimi — wszystkie są przyczynowymi transformatorami typu decoder-only z tą samą pętlą rdzeniową. Różnią się skalą, jakością danych i technikami RLHF.

## Koncepcja

![Maska przyczynowa tworzy trójkątną macierz uwagi](../assets/causal-attention.svg)

### Maska

Dla sekwencji o długości `N` budujemy macierz `N × N`:

```
M[i, j] = 0       if j <= i
M[i, j] = -inf    if j > i
```

Dodajemy `M` do surowych wyników uwagi przed softmaxem. Ponieważ `exp(-inf) = 0`, zamaskowane pozycje mają zerową wagę. Każdy wiersz macierzy uwagi stanowi rozkład prawdopodobieństwa ograniczony wyłącznie do poprzednich pozycji.

Koszt implementacji: jedno wywołanie `torch.tril()`. Czas obliczeń: nanosekundy. Znaczenie praktyczne: fundamentalne.

### Trenowanie równoległe, wnioskowanie sekwencyjne

Podczas trenowania: przepuszczamy całą sekwencję `(N, d_model)` jednorazowo, obliczamy N strat entropii krzyżowej (po jednej na pozycję), sumujemy i liczymy gradient. Przetwarzanie przebiega równolegle. Właśnie dlatego trenowanie GPT dobrze się skaluje — w jednym przebiegu GPU przetwarzamy milion tokenów w ramach jednej partii.

Podczas wnioskowania: generujemy token po tokenie. Podajemy `[t1, t2, t3]`, otrzymujemy `t4`. Następnie podajemy `[t1, t2, t3, t4]`, otrzymujemy `t5` i tak dalej. Pamięć podręczna KV (lekcja 12) przechowuje ukryte stany `t1…tn`, eliminując potrzebę ich ponownego obliczania na każdym kroku. Głębokość sekwencyjna przy wnioskowaniu jest jednak równa długości generowanego wyjścia — to właśnie jest podatek autoregresyjny i przyczyna, dla której dekodowanie stanowi wąskie gardło każdego LLM.

### Strata — przesunięcie o jeden

Mając tokeny `[t1, t2, t3, t4]`:

- Dane wejściowe: `[t1, t2, t3]`
- Cele: `[t2, t3, t4]`

Dla każdej pozycji `i` obliczamy `-log P(target_i | inputs[:i+1])` i sumujemy wyniki. To jest entropia krzyżowa dla całej sekwencji.

Na tej stracie trenowany jest każdy transformator językowy, o którym słyszałeś — zarówno przy pretrenowaniu, jak i przy dostrajaniu (SFT). Strata pozostaje ta sama; zmieniają się tylko dane.

### Strategie dekodowania

Po wytrenowaniu modelu dobór strategii próbkowania ma większe znaczenie, niż zwykle się przyjmuje.

| Metoda | Działanie | Kiedy stosować |
|--------|-----------|----------------|
| Zachłanna | Argmax na każdym kroku | Zadania deterministyczne, uzupełnianie kodu |
| Temperatura | Dziel logity przez T, próbkuj | Zadania twórcze; wyższe T = większa różnorodność |
| Top-k | Próbkuj tylko z k najbardziej prawdopodobnych tokenów | Odcina ogony o niskim prawdopodobieństwie |
| Top-p (jądrowa) | Próbkuj z najmniejszego zbioru o skumulowanym prawdopodobieństwie ≥ p | Domyślna od 2020+; dostosowuje się do kształtu rozkładu |
| Min-p | Zachowaj tokeny spełniające `p > min_p * max_p` | Od 2024+; lepiej odrzuca długie ogony niż top-p |
| Dekodowanie spekulatywne | Mały model proponuje N tokenów, duży weryfikuje | Redukcja opóźnień 2–3× przy tej samej jakości |

W 2026 roku rozsądną wartością domyślną dla modeli z otwartymi wagami jest temperatura 0,7 z min-p. Dekodowanie spekulatywne to już standard w każdym produkcyjnym stosie wnioskowania.

### Co sprawiło, że „przepis GPT" zadziałał

1. **Tylko dekoder.** Brak narzutu kodera. Jedno przejście uwagi i FFN na warstwę.
2. **Skalowanie.** 124M → 1,5B → 175B → biliony parametrów. Prawa skalowania (lekcja 13) precyzują, jak efektywnie wykorzystywać moc obliczeniową.
3. **Uczenie się w kontekście.** Pojawiło się przy rozmiarach 6B–13B. Model potrafi naśladować przykłady few-shot bez dodatkowego dostrajania.
4. **RLHF.** Trenowanie na podstawie ludzkich preferencji przekształciło surowy model pretrenowany w asystenta konwersacyjnego.
5. **Pre-norm + RoPE + SwiGLU.** Stabilne trenowanie w dużej skali.

Podstawowa architektura nie uległa zasadniczym zmianom od czasów GPT-2. Wszystko, co istotne, dokonało się na poziomie danych, skali i procesu po trenowaniu.

## Zbuduj to

### Krok 1: maska przyczynowa

Zobacz `code/main.py`. Jedna linijka:

```python
def causal_mask(n):
    return [[0.0 if j <= i else float("-inf") for j in range(n)] for i in range(n)]
```

Dodaj to do wyników uwagi przed softmaxem. To cały mechanizm.

### Krok 2: dwuwarstwowy model w stylu GPT

Złóż dwa bloki dekodera (zamaskowana samouwaga + FFN, bez wzajemnej uwagi). Dodaj osadzanie tokenów, kodowanie pozycyjne oraz projekcję wyjściową powiązaną z macierzą osadzania tokenów — standardowa technika stosowana od czasów GPT-2.

### Krok 3: przewidywanie następnego tokenu, od początku do końca

Używając słownika zabawkowego złożonego z 20 tokenów, utwórz logity na każdej pozycji. Oblicz stratę entropii krzyżowej względem celów przesuniętych o jeden. Bez obliczania gradientu — to weryfikacja poprawności przebiegu w przód.

### Krok 4: próbkowanie

Zaimplementuj strategie zachłanną, temperaturową, top-k, top-p i min-p. Uruchom każdą z nich dla tego samego podpowiedzi i porównaj wyniki. Funkcja próbkowania zmieści się w 10 liniach.

## Użyj tego

PyTorch, idiom z 2026:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")
tok = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")

prompt = "Attention is all you need because"
inputs = tok(prompt, return_tensors="pt")
out = model.generate(
    **inputs,
    max_new_tokens=64,
    temperature=0.7,
    top_p=0.9,
    do_sample=True,
)
print(tok.decode(out[0]))
```

Pod maską `generate()` wykonuje przebieg w przód, pobiera logity z ostatniej pozycji, wyznacza następny token, dołącza go i powtarza cykl. Każdy produkcyjny stos wnioskowania LLM — vLLM, TensorRT-LLM, llama.cpp, Ollama, MLX — implementuje tę samą pętlę, lecz ze znacznymi optymalizacjami: wsadowe wypełnianie wstępne, ciągłe tworzenie partii, stronicowanie pamięci podręcznej KV oraz dekodowanie spekulatywne.

**GPT kontra BERT, w jednym zdaniu:** GPT przewiduje `P(x_t | x_{<t})`. BERT przewiduje `P(x_masked | x_unmasked)`. Funkcja straty decyduje o tym, czy model potrafi generować tekst.

## Wyślij to

Zobacz `outputs/skill-sampling-tuner.md`. Umiejętność dobiera parametry próbkowania do nowego zadania generatywnego i sygnalizuje, gdy wymagane jest dekodowanie deterministyczne.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py` i sprawdź, czy po softmaxie macierz uwagi przyczynowej jest dolnotrójkątna. Weryfikacja wyrywkowa: wiersz 3 powinien mieć wagi niezerowe wyłącznie w kolumnach 0–3.
2. **Średnie.** Zaimplementuj przeszukiwanie wiązką o szerokości 4. Porównaj złożoność wiązki-4 z podejściem zachłannym na 10 krótkich podpowiedziach. Czy szersza wiązka zawsze daje lepsze wyniki? (Wskazówka: zwykle tak — przy tłumaczeniu, ale nie w otwartej rozmowie.)
3. **Trudne.** Zaimplementuj dekodowanie spekulatywne: użyj małego modelu 2-warstwowego jako szkicownika i modelu 6-warstwowego jako weryfikatora. Zmierz przyspieszenie rzeczywistego czasu generowania po 100 uzupełnieniach o długości 64 tokenów. Upewnij się, że wyniki pokrywają się z wynikami zachłannego weryfikatora.

## Kluczowe terminy

| Termin | Potoczne określenie | Właściwe znaczenie |
|--------|--------------------|--------------------|
| Maska przyczynowa | „Trójkąt" | Górnotrójkątna macierz `-inf` dodawana do wyników uwagi; pozycja `i` widzi tylko pozycje `≤ i`. |
| Przewidywanie następnego tokenu | „Strata" | Entropia krzyżowa rozkładu modelu względem prawdziwego następnego tokenu na każdej pozycji. |
| Autoregresja | „Generuj jeden po jednym" | Wynik jednego kroku staje się wejściem następnego; równoległość obowiązuje tylko podczas trenowania, nie podczas generowania. |
| Logity | „Wyniki przed softmaxem" | Surowy wynik głowicy LM przed softmaxem; próbkowanie odbywa się na ich podstawie. |
| Temperatura | „Pokrętło kreatywności" | Dzielenie logitów przez T; T → 0 oznacza wybór zachłanny, T → ∞ — rozkład jednostajny. |
| Top-p | „Próbkowanie jądrowe" | Obetnij rozkład do najmniejszego zbioru sumującego do ≥ p; próbkuj z pozostałej części. |
| Min-p | „Lepsze niż top-p" | Zachowaj tokeny, gdzie `p ≥ min_p × max_p`; próg odcięcia dostosowuje się do ostrości rozkładu. |
| Dekodowanie spekulatywne | „Szkic + weryfikacja" | Tani model proponuje N tokenów; duży model sprawdza je równolegle. |
| Teacher forcing | „Sztuczka treningowa" | Podczas trenowania podawaj prawdziwy poprzedni token zamiast przewidywania modelu. Standard w każdym sekwencyjnym modelu językowym. |

## Dalsze czytanie

- [Radford i in. (2018). Poprawa rozumienia języka poprzez generatywne szkolenie wstępne](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf) — GPT-1.
- [Radford i in. (2019). Modele językowe to osoby uczące się wielozadaniowo bez nadzoru](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) — GPT-2.
- [Brown i in. (2020). Modele językowe to niewielu uczniów](https://arxiv.org/abs/2005.14165) — GPT-3 i uczenie się w kontekście.
- [Lewiatan, Kalman, Matias (2023). Szybkie wnioskowanie z transformatorów poprzez dekodowanie spekulatywne](https://arxiv.org/abs/2211.17192) — oryginalna publikacja dotycząca dekodowania spekulatywnego.
- [HuggingFace `modeling_llama.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/modeling_llama.py) — kanoniczny kod referencyjny przyczynowego modelu językowego.
