# Kodowanie pozycyjne — sinusoidalne, RoPE, ALiBi

> Mechanizm uwagi jest niezmienniczy względem permutacji. „Kot usiadł na macie" i „mata na siedzącym kocie" dają identyczny wynik bez sygnału pozycyjnego. Problem ten rozwiązują trzy algorytmy — każdy z odmiennym podejściem do pojęcia „pozycja".

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 02 (Samouważność), Faza 7 · 03 (Uwaga wielu głów)
**Czas:** ~45 minut

## Problem

Skalowana uwaga iloczynu skalarnego jest ślepa na kolejność tokenów. Macierz uwagi `softmax(Q K^T / √d) V` jest obliczana wyłącznie na podstawie podobieństw parami. Przetasowanie wierszy `X` przesuwa odpowiadające im wiersze wyniku w identyczny sposób. Żaden element wewnętrzny mechanizmu uwagi nie uwzględnia pozycji.

Dla modelu worka słów nie stanowi to problemu. Jednak w przypadku języka naturalnego, kodu, dźwięku czy wideo — wszędzie tam, gdzie kolejność niesie znaczenie — brak informacji pozycyjnej jest wadą krytyczną.

Rozwiązanie polega na wstrzyknięciu informacji o pozycji do reprezentacji wektorowych. Wyróżnia się trzy generacje odpowiedzi na ten problem:

1. **Absolutna sinusoida** (Vaswani 2017). Do wektora osadzenia dodaje się wartości `sin/cos` zależne od pozycji. Metoda prosta, niewymagająca uczenia, lecz słabo ekstrapolująca poza wytrenowane długości sekwencji.
2. **RoPE — osadzenie w pozycji obrotowej** (Su 2021). Wektory Q i K są obracane o kąt proporcjonalny do pozycji. Pozycja *względna* jest kodowana bezpośrednio w iloczynie skalarnym. Dominujące rozwiązanie w 2026 roku.
3. **ALiBi — uwaga z odchyleniami liniowymi** (Press 2022). Całkowicie rezygnuje z osadzania pozycyjnego; zamiast tego do wyników uwagi dodawana jest kara liniowa zależna od odległości między tokenami, osobna dla każdej głowy. Zapewnia doskonałą ekstrapolację długości.

Od 2026 roku praktycznie każdy czołowy model open-source wykorzystuje RoPE: Llama 2/3/4, Qwen 2/3, Mistral, Mixtral, DeepSeek-V3, Kimi. Część modeli z długim kontekstem stosuje ALiBi lub jego nowsze warianty. Absolutna sinusoida ma już wyłącznie znaczenie historyczne.

## Koncepcja

![Sinusoidalna wartość bezwzględna vs rotacje RoPE vs błąd odległości ALiBi](../assets/positional-encoding.svg)

### Absolutna sinusoida

Wstępnie oblicza się stałą macierz `PE` o wymiarach `(max_len, d_model)`:

```
PE[pos, 2i]   = sin(pos / 10000^(2i / d_model))
PE[pos, 2i+1] = cos(pos / 10000^(2i / d_model))
```

Następnie przed warstwą uwagi wykonuje się operację `X' = X + PE[:N]`. Każdy wymiar odpowiada sinusoidzie o innej częstotliwości. Model uczy się odczytywać pozycję ze wzoru fazowego. Metoda zawodzi jednak poza zakresem `max_len` — model nie widział podczas treningu żadnych pozycji powyżej 2047, a więc nie wie, jak interpretować pozycję 2048.

### RoPE

Rotacji poddawane są wektory Q i K — nie wektory osadzenia. Dla każdej pary wymiarów `(2i, 2i+1)`:

```
[q'_2i    ]   [ cos(pos·θ_i)  -sin(pos·θ_i) ] [q_2i   ]
[q'_2i+1  ] = [ sin(pos·θ_i)   cos(pos·θ_i) ] [q_2i+1 ]

θ_i = base^(-2i / d_head),  base = 10000 by default
```

Do kluczy na pozycji `pos_k` stosuje się tę samą rotację. Iloczyn skalarny `q'_m · k'_n` staje się funkcją samej różnicy `(m - n)`. Oznacza to, że **wynik uwagi zależy wyłącznie od względnej odległości**, choć rotacja jest wyliczana na podstawie pozycji bezwzględnych. To elegancki trik matematyczny.

Rozszerzanie RoPE: parametr `base` można skalować (za pomocą NTK-aware scaling, YaRN, LongRoPE) w celu ekstrapolacji na dłuższe konteksty bez ponownego trenowania. W ten sposób Llama 3 rozszerzyła okno kontekstowe z 8K do 128K tokenów.

### ALiBi

Ta metoda rezygnuje ze wszelkiego osadzania pozycyjnego. Zamiast tego bezpośrednio modyfikuje wyniki uwagi:

```
attn_score[i, j] = (q_i · k_j) / √d  -  m_h · |i - j|
```

Gdzie `m_h` to nachylenie charakterystyczne dla danej głowy (np. `1 / 2^(8·h/H)`). Bliższe tokeny otrzymują wyższe wyniki; odległe są penalizowane. Metoda nie generuje żadnych dodatkowych kosztów obliczeniowych podczas treningu. Autorzy artykułu pokazują, że ekstrapolacja długości jest lepsza niż w przypadku sinusoidy i porównywalna z RoPE w granicach oryginalnie wytrenowanej długości.

### Co wybrać w 2026 roku

| Wariant | Ekstrapolacja | Koszt treningu | Stosowany przez |
|--------|---------------|--------------|---------|
| Absolutna sinusoida | słaba | brak | oryginalny Transformer, wczesny BERT |
| Wyuczone osadzenie absolutne | brak | znikomy | GPT-2, GPT-3 |
| RoPE | dobra przy skalowaniu | brak | Llama 2/3/4, Qwen 2/3, Mistral, DeepSeek-V3, Kimi |
| RoPE + YaRN | doskonała | etap dostrajania | Qwen2-1M, Llama 3.1 128K |
| ALiBi | doskonała | brak | BLOOM, MPT, Baichuan |

RoPE zwyciężyło, ponieważ nie wymaga zmian w architekturze, koduje pozycję względną, a jego hiperparametr `base` stanowi proste narzędzie do dostrajania zakresu kontekstu.

## Zbuduj to

### Krok 1: kodowanie sinusoidalne

Zobacz `code/main.py`. Obliczenie w czterech liniach:

```python
def sinusoidal(N, d):
    pe = [[0.0] * d for _ in range(N)]
    for pos in range(N):
        for i in range(d // 2):
            theta = pos / (10000 ** (2 * i / d))
            pe[pos][2 * i]     = math.sin(theta)
            pe[pos][2 * i + 1] = math.cos(theta)
    return pe
```

Wynik dodaje się do macierzy osadzenia przed pierwszą warstwą uwagi.

### Krok 2: RoPE zastosowane do Q i K

RoPE działa lokalnie na Q i K. Dla każdej pary wymiarów:

```python
def apply_rope(x, pos, base=10000):
    d = len(x)
    out = list(x)
    for i in range(d // 2):
        theta = pos / (base ** (2 * i / d))
        c, s = math.cos(theta), math.sin(theta)
        a, b = x[2 * i], x[2 * i + 1]
        out[2 * i]     = a * c - b * s
        out[2 * i + 1] = a * s + b * c
    return out
```

Ważne: tę samą funkcję stosuje się do Q na pozycji `m` i K na pozycji `n`. Ich iloczyn skalarny zyskuje współczynnik `cos((m-n)·θ_i)` w każdej parze współrzędnych. Mechanizm uwagi uczy się pozycji względnej bez żadnych dodatkowych nakładów.

### Krok 3: nachylenie i odchylenie ALiBi

```python
def alibi_bias(n_heads, seq_len):
    # slope_h = 2 ** (-8 * h / n_heads) for h = 1..n_heads
    slopes = [2 ** (-8 * (h + 1) / n_heads) for h in range(n_heads)]
    bias = []
    for m in slopes:
        row = [[-m * abs(i - j) for j in range(seq_len)] for i in range(seq_len)]
        bias.append(row)
    return bias  # add to attention scores before softmax
```

Macierz `bias[h]` o wymiarach `(seq_len, seq_len)` dodaje się do macierzy wyników uwagi głowy `h` przed operacją softmax.

### Krok 4: weryfikacja właściwości RoPE dotyczącej odległości względnej

Wybierz dwa losowe wektory `a` i `b`. Obróć je o kąty `(pos_a, pos_b)`, a następnie o `(pos_a + k, pos_b + k)`. Oba iloczyny skalarne powinny być zgodne w granicach błędu zmiennoprzecinkowego. Ta właściwość stanowi istotę RoPE — niezmienniczość względem przesunięcia bezwzględnego, przy zachowaniu wrażliwości na odległość względną.

## Użyj tego

PyTorch 2.5+ udostępnia narzędzia RoPE w `torch.nn.functional`. Większość kodu produkcyjnego korzysta z `flash_attn` lub `xformers`, gdzie RoPE jest stosowana wewnątrz jądra uwagi.

```python
from transformers import AutoModel
model = AutoModel.from_pretrained("meta-llama/Llama-3.2-3B")
# model.config.rope_scaling → {"type": "yarn", "factor": 32.0, "original_max_position_embeddings": 8192}
```

**Techniki rozszerzania kontekstu w 2026 r.:**

- **NTK-aware scaling.** Parametr `base` przeskalowuje się do `base * (scale_factor)^(d/(d-2))` przy rozszerzaniu zakresu z 4K do 16K i więcej.
- **YaRN.** Zaawansowana metoda interpolacji zachowująca entropię uwagi w długich kontekstach. Stosowana przez Llama 3.1 128K.
- **LongRoPE.** Metoda Microsoftu z 2024 r., która wykorzystuje przeszukiwanie ewolucyjne do doboru współczynników skalowania osobno dla każdego wymiaru. Stosowana przez Phi-3-Long.
- **Interpolacja pozycyjna + dostrajanie.** Wystarczy zmniejszyć wartości pozycji o współczynnik rozszerzenia i dostroić model na 1–5 miliardach tokenów. Zaskakująco skuteczne podejście.

## Wyślij to

Zobacz `outputs/skill-positional-encoding-picker.md`. Umiejętność dobiera strategię kodowania pozycyjnego dla nowego modelu na podstawie docelowej długości kontekstu, wymagań ekstrapolacyjnych i budżetu treningowego.

## Ćwiczenia

1. **Łatwe.** Zwizualizuj sinusoidalną macierz `PE` jako mapę cieplną dla `max_len=512, d=128`. Potwierdź wzorzec „pasy stają się szersze wraz ze wzrostem indeksu wymiaru".
2. **Średnie.** Zastosuj NTK-aware scaling dla RoPE. Wytrenuj mały model językowy na sekwencjach o długości 256, a następnie przetestuj go na długości 1024 — ze skalowaniem i bez. Zmierz perpleksję.
3. **Trudne.** Zaimplementuj ALiBi i RoPE w tym samym module uwagi. Wytrenuj czterowarstwy Transformer na zadaniu kopiowania z sekwencjami o długości 512. Przeprowadź ekstrapolację do 2048 tokenów podczas testowania. Porównaj degradację obu metod.

## Kluczowe terminy

| Termin | Co się mówi | Co to faktycznie oznacza |
|------|-----------------|----------------------|
| Kodowanie pozycyjne | „Mówi uwadze o kolejności" | Dowolny sygnał dodany do osadzenia lub wyniku uwagi, który przekazuje informację o pozycji tokenu. |
| Sinusoidalne | „Oryginalne" | Wartości `sin/cos` przy częstotliwościach geometrycznych dodawane do osadzenia; bez możliwości ekstrapolacji. |
| RoPE | „Obrotowe osadzenie pozycyjne" | Obrót Q i K o kąt zależny od pozycji; iloczyn skalarny koduje odległość względną. |
| ALiBi | „Sztuczka z liniowym odchyleniem" | Dodanie `-m·\|i-j\|` do wyników uwagi; nie wymaga osadzenia, zapewnia świetną ekstrapolację. |
| base | „Pokrętło RoPE" | Skalar częstotliwości w RoPE; zwiększenie wartości rozszerza efektywny zasięg kontekstu przy inferencji. |
| NTK-aware scaling | „Sztuczka skalowania RoPE" | Przeskalowanie `base` tak, aby wymiary o wysokiej częstotliwości nie były nadmiernie kompresowane przy rozszerzaniu kontekstu. |
| YaRN | „Ta zaawansowana metoda" | Interpolacja i ekstrapolacja dostosowana do poszczególnych wymiarów, zachowująca entropię uwagi. |
| Ekstrapolacja | „Działa poza wytrenowaną długością" | Zdolność schematu pozycyjnego do generowania poprawnych wyników powyżej wartości `max_len` obserwowanej podczas treningu. |

## Dalsze czytanie

- [Vaswani i in. (2017). Uwaga to wszystko, czego potrzebujesz §3.5](https://arxiv.org/abs/1706.03762) — oryginalna sinusoida.
- [Su i in. (2021). RoFormer: ulepszony Transformer z osadzeniem w pozycji obrotowej](https://arxiv.org/abs/2104.09864) — artykuł źródłowy RoPE.
- [Press, Smith, Lewis (2021). Trenuj krótko, testuj długo: uwaga z odchyleniami liniowymi umożliwia ekstrapolację długości wejścia](https://arxiv.org/abs/2108.12409) — ALiBi.
- [Peng i in. (2023). YaRN: wydajne rozszerzenie okna kontekstowego dla dużych modeli językowych](https://arxiv.org/abs/2309.00071) — najnowocześniejsze skalowanie RoPE.
- [Chen i in. (2023). Rozszerzanie okna kontekstowego dużych modeli językowych poprzez interpolację pozycyjną](https://arxiv.org/abs/2306.15595) — artykuł Meta dotyczący Llama 2 z długim kontekstem.
- [Ding i in. (2024). LongRoPE: rozszerzanie okna kontekstowego LLM poza 2 miliony tokenów](https://arxiv.org/abs/2402.13753) — metoda Microsoftu stosowana przez Phi-3-Long.
- [HuggingFace Transformers — `modeling_rope_utils.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/modeling_rope_utils.py) — produkcyjne implementacje wszystkich schematów skalowania RoPE (domyślny, liniowy, dynamiczny, YaRN, LongRoPE, Llama-3).
