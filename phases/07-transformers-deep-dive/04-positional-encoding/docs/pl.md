# Kodowanie pozycyjne — sinusoidalne, RoPE, ALiBi

> Uwaga jest niezmienna permutacyjna. „Kot usiadł na macie” i „mata na siedzącym kocie” dają ten sam sygnał wyjściowy bez sygnału pozycyjnego. Rozwiązują to trzy algorytmy — każdy z innym założeniem, co oznacza „pozycja”.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 02 (Samouważność), Faza 7 · 03 (Uwaga wielu głów)
**Czas:** ~45 minut

## Problem

Skalowana uwaga iloczynu skalarnego jest ślepa na porządek. Macierz uwagi `softmax(Q K^T / √d) V` jest obliczana na podstawie podobieństw parami. Potasuj wiersze `X`, tak samo pomieszaj wiersze wyniku. Nic wewnątrz uwagi nie dba o pozycję.

To nie jest błąd w modelu worka słów. Dla języka, kodu, dźwięku, wideo – wszystkiego, gdzie porządek niesie ze sobą znaczenie – jest to fatalne w skutkach.

Rozwiązanie polega na tym, aby w jakiś sposób wprowadzić pozycję do osadzania. Trzy epoki odpowiedzi:

1. **Absolutna sinusoida** (Vaswani 2017). Dodaj `sin/cos` pozycji do osadzenia. Proste, nie wymagające nauki, słabo ekstrapolujące poza wytrenowane długości.
2. **Lina — osadzenie w pozycji obrotowej** (Su 2021). Obróć wektory Q i K o kąt proporcjonalny do położenia. Koduje *względną* pozycję bezpośrednio w iloczynie skalarnym. Dominujący w 2026 roku.
3. **ALiBi – Uwaga z odchyleniami liniowymi** (Press 2022). Całkowicie pomiń osadzanie; dodaj karę liniową za głowę do wyników uwagi na podstawie odległości. Doskonała ekstrapolacja długości.

Od 2026 r. Zasadniczo każdy model typu frontier open wykorzystuje RoPE: Llama 2/3/4, Qwen 2/3, Mistral, Mixtral, DeepSeek-V3, Kimi. Kilka modeli o długim kontekście wykorzystuje ALiBi lub jego nowoczesne warianty. Absolutna sinusoida jest zjawiskiem historycznym.

## Koncepcja

![Sinusoidalna wartość bezwzględna vs rotacje RoPE vs błąd odległości ALiBi](../assets/positional-encoding.svg)

### Absolutna sinusoida

Oblicz wstępnie stałą macierz `PE` o kształcie `(max_len, d_model)`:

```
PE[pos, 2i]   = sin(pos / 10000^(2i / d_model))
PE[pos, 2i+1] = cos(pos / 10000^(2i / d_model))
```

Następnie `X' = X + PE[:N]` przed uwagą. Każdy wymiar jest sinusoidą o innej częstotliwości. Model uczy się odczytywać położenie ze wzoru fazowego. Niepowodzenie przekracza `max_len`: nic nie powiedziało modelowi, co dzieje się na pozycji 2048, podczas gdy widział tylko pozycje 0–2047.

### LINA

Obróć wektory Q i K (nie osadzania). Dla pary wymiarów `(2i, 2i+1)`:

```
[q'_2i    ]   [ cos(pos·θ_i)  -sin(pos·θ_i) ] [q_2i   ]
[q'_2i+1  ] = [ sin(pos·θ_i)   cos(pos·θ_i) ] [q_2i+1 ]

θ_i = base^(-2i / d_head),  base = 10000 by default
```

Zastosuj ten sam obrót do kluczy z pozycją `pos_k`. Iloczyn skalarny `q'_m · k'_n` staje się funkcją samego `(m - n)`. Oznacza to, że: **wynik uwagi zależy tylko od względnej odległości**, mimo że rotacja została wykluczona z pozycji bezwzględnych. Piękna sztuczka.

Rozszerzanie RoPE: `base` można skalować (z obsługą NTK, YaRN, LongRoPE) w celu ekstrapolacji na dłuższe konteksty bez ponownego szkolenia. W ten sposób Lama 3 rozszerzyła kontekst z 8K do 128K.

### ALiBi

Pomiń sztuczkę osadzania. Bezpośrednio wpływaj na wyniki uwagi:

```
attn_score[i, j] = (q_i · k_j) / √d  -  m_h · |i - j|
```

Gdzie `m_h` to nachylenie charakterystyczne dla głowy (np. `1 / 2^(8·h/H)`). Bliższe tokeny zostają wzmocnione; odległe żetony są karane. Brak kosztów związanych z czasem szkolenia. Artykuł pokazuje, że ekstrapolacja długości przewyższa sinusoidę i dopasowuje RoPE do jej pierwotnie wytrenowanej długości.

### Co wybrać w 2026 roku

| Wariant | Ekstrapolacja | Koszt szkolenia | Używany przez |
|--------|---------------|--------------|---------|
| Absolutna sinusoida | biedny | za darmo | oryginalny transformator, wczesny BERT |
| Nauczyłem się absolutu | żaden | malutki | GPT-2, GPT-3 |
| LINA | dobry ze skalowaniem | za darmo | Lama 2/3/4, Qwen 2/3, Mistral, DeepSeek-V3, Kimi |
| LINA + Przędza | doskonale | dostroić etap | Qwen2-1M, Lama 3.1 128K |
| ALiBi | doskonale | za darmo | BLOOM, MPT, Baichuan |

RoPE zwyciężyło, ponieważ przyciąga uwagę bez zmiany architektury, koduje położenie względne, a jego hiperparametr `base` zapewnia proste pokrętło do dostrajania w długim kontekście.

## Zbuduj to

### Krok 1: kodowanie sinusoidalne

Zobacz `code/main.py`. Obliczenie 4-liniowe:

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

Dodaj to do matrycy osadzania przed pierwszą warstwą uwagi.

### Krok 2: Lina zastosowana do Q, K

RoPE działa lokalnie na Q i K. Dla każdej pary ściemnień:

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

Ważne: zastosuj tę samą funkcję do Q na pozycji `m` i K na pozycji `n`. Ich iloczyn skalarny pobiera współczynnik `cos((m-n)·θ_i)` w każdej parze współrzędnych. Uwaga uczy się pozycji względnej za darmo.

### Krok 3: Nachylenie i odchylenie ALiBi

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

Dodaj `bias[h]` do `(seq_len, seq_len)` macierzy oceny uwagi głowy `h`, a następnie softmax.

### Krok 4: sprawdź właściwość RoPE dotyczącą odległości względnej

Wybierz dwa losowe wektory `a, b`. Obróć o `(pos_a, pos_b)`. Następnie przez `(pos_a + k, pos_b + k)`. Obydwa iloczyny skalarne muszą się zgadzać w granicach błędu zmiennoprzecinkowego. Ta właściwość stanowi cały sens RoPE — jest niezmienna w stosunku do przesunięcia bezwzględnego, liczy się tylko względna szczelina.

## Użyj tego

PyTorch 2.5+ dostarcza narzędzia RoPE w `torch.nn.functional`. Większość kodu produkcyjnego wykorzystuje `flash_attn` lub `xformers`, gdzie RoPE jest stosowana wewnątrz jądra uwagi.

```python
from transformers import AutoModel
model = AutoModel.from_pretrained("meta-llama/Llama-3.2-3B")
# model.config.rope_scaling → {"type": "yarn", "factor": 32.0, "original_max_position_embeddings": 8192}
```

**Sztuczki o długim kontekście w 2026 r.:**

- **Interpolacja zgodna z NTK.** Przeskaluj `base` do `base * (scale_factor)^(d/(d-2))` przy rozszerzaniu z 4K do 16K+.
- **YaRN.** Inteligentniejsza interpolacja, która pozwala zachować entropię uwagi w długich kontekstach. Używa go Lama 3.1 128K.
- **LongRoPE.** Metoda firmy Microsoft z 2024 r., która wykorzystuje wyszukiwanie ewolucyjne w celu wybrania współczynników skali według wymiaru. Używa go Phi-3-Long.
- **Interpolacja pozycji + dostrajanie.** Wystarczy zmniejszyć pozycje o współczynnik rozszerzenia i dostroić dla tokenów 1–5B. Zaskakująco skuteczny.

## Wyślij to

Zobacz `outputs/skill-positional-encoding-picker.md`. Umiejętność wybiera strategię kodowania dla nowego modelu, biorąc pod uwagę długość kontekstu docelowego, potrzeby ekstrapolacji i budżet szkoleniowy.

## Ćwiczenia

1. **Łatwo.** Narysuj sinusoidalną macierz `PE` jako mapę cieplną dla `max_len=512, d=128`. Potwierdź wzór „paski stają się szersze wraz ze wzrostem indeksu wymiaru”.
2. **Średni.** Zastosuj skalowanie RoPE obsługujące NTK. Trenuj mały LM na sekwencjach o długości 256, a następnie przetestuj na długości 1024 ze skalowaniem i bez. Zmierz zakłopotanie.
3. **Trudne.** Zaimplementuj ALiBi i RoPE w tym samym module uwagi. Wytrenuj transformator 4-warstwowy w zadaniu kopiowania z sekwencjami o długości 512. Ekstrapoluj do 2048 w czasie testu. Porównaj degradację.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Kodowanie pozycyjne | „Mówi uwagę o porządku” | Dowolny sygnał dodany do osadzania lub uwagi, który koduje pozycję. |
| Sinusoidalny | „Oryginalny” | `sin/cos` przy częstotliwościach geometrycznych dodanych do osadzania; nie ekstrapoluje. |
| LINA | „Osadzenia obrotowe” | Obróć Q, K o kąt zależny od położenia; iloczyn kropkowy koduje odległość względną. |
| ALiBi | „Sztuczka z liniowym odchyleniem” | Dodaj `-m·\|i-j\|` do wyników uwagi; nie wymaga osadzania, świetna ekstrapolacja. |
| podstawa | „Gałka liny” | Skaler częstotliwości w RoPE; zwiększyć, aby rozszerzyć kontekst przy wnioskowaniu. |
| Obsługuje NTK | „Sztuczka skalowania RoPE” | Przeskaluj `base`, aby przyciemnienia o wysokiej częstotliwości nie były ściskane w miarę rozszerzania się kontekstu. |
| Przędza | „Ten fantazyjny” | Interpolacja i ekstrapolacja według wymiarów, która pozwala zachować entropię uwagi. |
| Ekstrapolacja | „Działa poza wyszkoloną długością” | Czy schemat pozycji może wyświetlać prawidłowe dane wyjściowe powyżej `max_len` zaobserwowanych podczas szkolenia? |

## Dalsze czytanie

- [Vaswani i in. (2017). Uwaga to wszystko, czego potrzebujesz §3.5](https://arxiv.org/abs/1706.03762) — oryginalna sinusoidalna.
- [Su i in. (2021). RoFormer: ulepszony transformator z osadzeniem w pozycji obrotowej](https://arxiv.org/abs/2104.09864) — papier RoPE.
- [Prasa, Smith, Lewis (2021). Trenuj krótko, testuj długo: Uwaga z odchyleniami liniowymi umożliwia ekstrapolację długości danych wejściowych](https://arxiv.org/abs/2108.12409) — ALiBi.
- [Peng i in. (2023). YaRN: wydajne rozszerzenie okna kontekstowego dla dużych modeli językowych](https://arxiv.org/abs/2309.00071) — najnowocześniejsze skalowanie RoPE.
- [Chen i in. (2023). Rozszerzanie okna kontekstowego dużych modeli językowych poprzez interpolację pozycyjną](https://arxiv.org/abs/2306.15595) — artykuł Meta's Llama 2 o długim kontekście.
- [Ding i in. (2024). LongRoPE: Rozszerzanie okna kontekstowego LLM poza 2 miliony tokenów](https://arxiv.org/abs/2402.13753) — metoda firmy Microsoft używana przez Phi-3-Long i cytowana w sekcji Użyj tego.
- [HuggingFace Transformers — `modeling_rope_utils.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/modeling_rope_utils.py) — implementacje produkcyjne każdego schematu skalowania RoPE (domyślny, liniowy, dynamiczny, YaRN, LongRoPE, Llama-3).