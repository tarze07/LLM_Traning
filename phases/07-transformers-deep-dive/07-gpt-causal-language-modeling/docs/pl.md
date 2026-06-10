# GPT — przyczynowe modelowanie języka

> BERT widzi obie strony. GPT widzi tylko przeszłość. Maska trójkątna to najważniejsza pojedyncza linia kodu we współczesnej sztucznej inteligencji.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 02 (Samouwaga), Faza 7 · 05 (Pełny transformator), Faza 7 · 06 (BERT)
**Czas:** ~75 minut

## Problem

Model językowy odpowiada na jedno pytanie: biorąc pod uwagę pierwsze tokeny `t-1`, jaki jest rozkład prawdopodobieństwa dla tokenu `t`? Trenuj na tym sygnale — przewidywanie następnego tokenu — a otrzymasz model, który może generować dowolny tekst po jednym toenie na raz.

Aby wytrenować go od początku do końca na całej sekwencji, przewidywanie każdej pozycji musi zależeć tylko od wcześniejszych pozycji. W przeciwnym razie model w trywialny sposób oszukuje, patrząc na odpowiedź.

Robi to maska ​​przyczynowa. Jest to pojedyncza macierz górno-trójkątna zawierająca wartości `-inf` dodawane do wyników uwagi przed softmaxem. Po softmax te pozycje stają się 0. Każda pozycja może zajmować się tylko sobą i wcześniejszymi pozycjami. A ponieważ zastosujesz to raz do całej sekwencji, otrzymasz N równoległych przewidywań dotyczących następnego tokenu w jednym przebiegu do przodu.

GPT-1 (2018), GPT-2 (2019), GPT-3 (2020), GPT-4 (2023), GPT-5 (2024), Claude, Llama, Qwen, Mistral, DeepSeek, Kimi — wszystkie są transformatorami przyczynowymi przeznaczonymi wyłącznie do dekodera z tą samą pętlą rdzenia. Po prostu większe, lepsze dane i lepszy RLHF.

## Koncepcja

![Maska przyczynowa tworzy trójkątną macierz uwagi](../assets/causal-attention.svg)

### Maska

Mając ciąg długości `N`, zbuduj macierz `N × N`:

```
M[i, j] = 0       if j <= i
M[i, j] = -inf    if j > i
```

Dodaj `M` do surowych wyników uwagi przed softmax. `exp(-inf) = 0`, więc zamaskowane pozycje mają zerową wagę. Każdy wiersz macierzy uwagi jest rozkładem prawdopodobieństwa wyłącznie w odniesieniu do poprzednich pozycji.

Koszt wdrożenia: jedno `torch.tril()` wywołanie. Czas obliczeń: nanosekundy. Wpływ na boisku: wszystko.

### Uczenie równoległe, wnioskowanie szeregowe

Trening: wykonaj jednokrotnie całą sekwencję `(N, d_model)`, oblicz N strat entropii krzyżowej (po jednej na pozycję), sumę, podpórkę. Równolegle w ciągu. Właśnie dlatego szkolenie GPT skaluje się — przetwarzasz 1 milion tokenów wsadowo w jednym przebiegu GPU.

Wnioskowanie: generujesz token po tokenie. Podaj `[t1, t2, t3]`, pobierz `t4`. Kanał `[t1, t2, t3, t4]`, pobierz `t5`. Kanał `[t1, t2, t3, t4, t5]`, pobierz `t6`. Pamięć podręczna KV (lekcja 12) zapisuje ukryte stany `t1…tn`, więc nie musisz ich ponownie obliczać w każdym kroku. Ale głębokość szeregowa przy wnioskowaniu = długość wyjściowa. To jest podatek autoregresyjny i dlatego dekodowanie jest wąskim gardłem każdego LLM.

### Strata — przesunięcie o jeden

Biorąc pod uwagę tokeny `[t1, t2, t3, t4]`:

- Dane wejściowe: `[t1, t2, t3]`
- Cele: `[t2, t3, t4]`

Dla każdej pozycji `i` oblicz `-log P(target_i | inputs[:i+1])`. Suma. Jest to entropia krzyżowa dla całej sekwencji.

Każdy transformator LM, o którym słyszałeś, pociągi na tej stracie. Szkolenie wstępne, dostrajanie, SFT – ta sama strata, różne dane.

### Strategie dekodowania

Po szkoleniu wybór próbek ma większe znaczenie, niż się ludziom wydaje.

| Metoda | Co to robi | Kiedy używać |
|--------|-------------|------------|
| Chciwy | Argmax na każdym kroku | Zadania deterministyczne, uzupełnianie kodu |
| Temperatura | Podziel logity przez T, próbka | Zadania kreatywne, wyższe T = większa różnorodność |
| Top-k | Próbka tylko z tokenów top-k | Zabija ogony o niskim prawdopodobieństwie |
| Top-p (jądro) | Próbka z najmniejszego zbioru z skumulowanym prawdopodobieństwem ≥ p | 2020+ domyślnie; dostosowuje się do kształtu rozkładu |
| Min-p | Przechowuj tokeny za pomocą `p > min_p * max_p` | 2024+; lepiej odrzuca długie ogony niż top-p |
| Dekodowanie spekulatywne | Szkic modelu proponuje N tokenów, duży model weryfikuje | 2–3× redukcja opóźnień przy tej samej jakości |

W roku 2026 temperatura min-p + 0,7 jest rozsądną wartością domyślną dla modeli z otwartymi ciężarami. Dekodowanie spekulatywne to stawki tabelaryczne dla dowolnego stosu wnioskowań produkcyjnych.

### Co sprawiło, że „przepis GPT” zadziałał

1. **Tylko dekoder.** Brak narzutu na koder. Jedno przejście uwagi + FFN na warstwę.
2. **Skalowanie.** 124M → 1,5B → 175B → biliony. Prawa skalowania szynszyli (Lekcja 13) mówią Ci, jak wydawać moc obliczeniową.
3. **Uczenie się w kontekście.** Pojawiło się około 6B–13B. Model może wzorować się na kilkustrzałowych przykładach bez dostrajania.
4. **RLHF.** Po szkoleniu dotyczącym ludzkich preferencji przekształcono surowy, wstępnie wytrenowany tekst w asystentów czatu.
5. **Pre-norm + RoPE + SwiGLU.** Stabilny trening na dużą skalę.

Podstawowa architektura nie zmieniła się zbytnio od czasu GPT-2. Wszystko, co interesujące, wydarzyło się w danych, skali i po treningu.

## Zbuduj to

### Krok 1: maska przyczynowa

Zobacz `code/main.py`. Jednolinijkowy:

```python
def causal_mask(n):
    return [[0.0 if j <= i else float("-inf") for j in range(n)] for i in range(n)]
```

Dodaj to do wyników uwagi przed softmax. Ot cały mechanizm.

### Krok 2: 2-warstwowy model w stylu GPT

Ułóż dwa bloki dekodera (zamaskowana samouwaga + FFN, bez wzajemnej uwagi). Dodaj osadzanie tokena, kodowanie pozycyjne i usuwanie osadzania (powiązane z macierzą osadzania tokenów — standardowa sztuczka od czasu GPT-2).

### Krok 3: przewidywanie następnego tokenu, od początku do końca

Używając słownictwa zabawkowego za 20 żetonów, stwórz logity w każdej pozycji. Oblicz stratę entropii krzyżowej względem docelowego przesunięcia o jeden. Brak gradientu — jest to kontrola poprawności przejścia do przodu.

### Krok 4: pobieranie próbek

Zaimplementuj zachłanny, temperatura, top-k, top-p, min-p. Uruchom każdy z nich w stałym wierszu zachęty i porównaj wyniki. Funkcja próbkowania to 10 linii.

## Użyj tego

PyTorch, idiom 2026:

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

Pod maską `generate()` wykonuje przejście do przodu, pobiera logity z końcowej pozycji, pobiera następny token, dołącza go i powtarza. Każdy produkcyjny stos wnioskowania LLM (vLLM, TensorRT-LLM, llama.cpp, Ollama, MLX) implementuje tę samą pętlę z dużą optymalizacją — wstępne wypełnianie wsadowe, ciągłe wsadzanie, stronicowanie pamięci podręcznej KV, dekodowanie spekulatywne.

**GPT vs BERT, po jednej linii:** GPT przewiduje `P(x_t | x_{<t})`. BERT przewiduje `P(x_masked | x_unmasked)`. Strata określa, czy model może generować.

## Wyślij to

Zobacz `outputs/skill-sampling-tuner.md`. Umiejętność wybiera parametry próbkowania dla zadania nowej generacji i flagi, gdy wymagane jest dekodowanie deterministyczne.

## Ćwiczenia

1. **Łatwo.** Uruchom `code/main.py` i sprawdź, czy po softmax macierz uwagi przyczynowej jest dolno-trójkątna. Kontrola wyrywkowa: wiersz 3 powinien mieć wagi tylko w kolumnach 0–3.
2. **Średni.** Zaimplementuj wyszukiwanie belki pod kątem szerokości 4. Porównaj złożoność belki-4 z zachłannością w 10 krótkich podpowiedziach. Czy promień zawsze wygrywa? (Wskazówka: zwykle do tłumaczenia, a nie do otwartego czatu.)
3. **Trudne.** Zaimplementuj dekodowanie spekulatywne: użyj małego 2-warstwowego modelu jako wersji roboczej i 6-warstwowego modelu jako weryfikatora. Zmierz przyspieszenie zegara ściennego po 100 uzupełnieniach o długości 64. Potwierdź, że wyniki odpowiadają zachłanności weryfikatora.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Maska przyczynowa | „Trójkąt” | Górnotrójkątna macierz `-inf` dodana do wyników uwagi, więc pozycja `i` widzi tylko pozycje `≤ i`. |
| Przewidywanie następnego tokenu | „Strata” | Entropia krzyżowa rozkładu modelu względem prawdziwego następnego tokena na każdej pozycji. |
| Autoregresja | „Generuj pojedynczo” | Podaj wynik z powrotem jako wejście; równoległość tylko podczas uczenia, a nie podczas generowania. |
| Logity | „Wyniki przed softmax” | Surowy wynik głowicy LM przed softmaxem; pobieranie próbek odbywa się na nich. |
| Temperatura | „Pokrętło kreatywności” | Podziel logity przez T; T → 0 = zachłanny, T → ∞ = jednolity. |
| Do góry | „Pobieranie próbek jądra” | Obetnij rozkład do najmniejszego zbioru sumującego do ≥p; próbkę z tego, co zostało. |
| Min-p | „Lepsze niż top-p” | Przechowuj tokeny tam, gdzie `p ≥ min_p × max_p`; dostosowuje odcięcie do ostrości dystrybucji. |
| Dekodowanie spekulatywne | „Szkic + weryfikacja” | Tani model proponuje N tokenów; duży model sprawdza równolegle. |
| Nauczyciel zmusza | „Sztuczka treningowa” | Podczas uczenia podawaj prawdziwy poprzedni token, a nie przewidywanie modelu. Standard dla każdego seq2seq LM. |

## Dalsze czytanie

- [Radford i in. (2018). Poprawa rozumienia języka poprzez generatywne szkolenie wstępne](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf) — GPT-1.
- [Radford i in. (2019). Modele językowe to osoby uczące się wielozadaniowo bez nadzoru](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) — GPT-2.
- [Brown i in. (2020). Modele językowe to niewielu uczniów](https://arxiv.org/abs/2005.14165) — GPT-3 i nauka w kontekście.
- [Lewiatan, Kalman, Matias (2023). Szybkie wnioskowanie z transformatorów poprzez dekodowanie spekulatywne](https://arxiv.org/abs/2211.17192) — dokument dotyczący dekodowania specyfikacji.
- [HuggingFace `modeling_llama.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/modeling_llama.py) — kanoniczny kod odniesienia przyczynowego-LM.