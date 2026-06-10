# Tokenizacja podwyrazowa (Subword Tokenization) – BPE, WordPiece, Unigram, SentencePiece

> Tokenizatory bazujące na całych słowach generują błędy przy nieznanych wyrazach. Tokenizatory znakowe nadmiernie wydłużają sekwencje. Tokenizatory podwyrazowe łączą zalety obu tych podejść. Każdy współczesny model LLM wykorzystuje jedną z tych metod.

**Typ:** Teoria
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 01 (Przetwarzanie tekstu), Faza 5 · 04 (GloVe / FastText / Metody podwyrazowe)
**Czas:** ~60 minut

## Problem

Załóżmy, że słownik Twojego modelu zawiera 50 000 słów. Użytkownik wpisuje wyraz „untokenizable”, a tokenizator zwraca token błędu `[UNK]`. W tym momencie model traci jakikolwiek sygnał semantyczny powiązany z tym słowem. Co gorsza, dokument z 90. percentyla Twojego korpusu może zawierać 40 rzadkich słów – to oznacza utratę 40 istotnych fragmentów informacji na dokument.

Tokenizacja podwyrazowa (subword tokenization) skutecznie rozwiązuje ten problem. Często występujące słowa są reprezentowane przez pojedyncze tokeny, natomiast rzadkie wyrazy są dzielone na mniejsze, znaczące cząstki: np. `untokenizable` → `un`, `token`, `izable`. Pozwala to obsłużyć każdy tekst wejściowy, ponieważ dowolny ciąg znaków można ostatecznie sprowadzić do sekwencji bajtów.

Wszystkie wiodące modele LLM w 2026 roku korzystają z jednego z trzech algorytmów (BPE, Unigram, WordPiece) wdrożonych za pomocą jednej z trzech bibliotek (tiktoken, SentencePiece, Hugging Face Tokenizers). Wybór i konfiguracja tokenizatora to pierwszy i kluczowy krok przy budowaniu dowolnego modelu językowego.

## Koncepcja

![BPE vs Unigram vs WordPiece, krok po kroku](../assets/subword-tokenization.svg)

**BPE (Byte Pair Encoding).** Uczenie rozpoczyna się od słownika zawierającego pojedyncze znaki. Następnie zlicza się wystąpienia sąsiadujących par jednostek i łączy najczęściej występującą parę w nowy token. Proces ten jest powtarzany iteracyjnie aż do osiągnięcia zadanego rozmiaru słownika. To dominujący algorytm w modelach takich jak GPT-2/3/4, Llama, Gemma, Qwen2 czy Mistral.

**Byte-level BPE (BBPE).** Odmiana algorytmu BPE operująca na surowych bajtach (256 podstawowych tokenów bajtowych) zamiast znaków Unicode. Gwarantuje to całkowity brak tokenów `[UNK]`, ponieważ dowolny tekst można zakodować jako sekwencję bajtów. Przykładowo, tokenizer GPT-2 ma słownik o rozmiarze 50 257 tokenów (256 bajtów bazowych + 50 000 reguł łączenia + 1 token specjalny).

**Unigram.** Uczenie zaczyna się od bardzo dużego słownika kandydatów. Każdemu tokenowi przypisuje się prawdopodobieństwo wystąpienia (unigram probability). W kolejnych krokach iteracyjnie usuwa się tokeny, których wyeliminowanie w najmniejszym stopniu zmniejsza wiarygodność logarytmiczną (log-likelihood) korpusu treningowego. Algorytm ma charakter probabilistyczny – pozwala na próbkowanie różnych wariantów tokenizacji jednego tekstu (tzw. regularyzacja podwyrazowa/subword regularization, przydatna do augmentacji danych). Stosowany m.in. w modelach T5, mBART, ALBERT, XLNet i Gemma.

**WordPiece.** Algorytm łączący te pary jednostek, które w największym stopniu zwiększają prawdopodobieństwo (likelihood) korpusu treningowego, a nie wyłącznie ich surową częstotliwość występowania. Stosowany w modelach BERT, DistilBERT oraz ELECTRA.

**SentencePiece vs tiktoken.** SentencePiece to biblioteka umożliwiająca *uczenie* i stosowanie słowników (zarówno BPE, jak i Unigram) bezpośrednio na surowym tekście Unicode, kodując spacje jako charakterystyczny znak ` ` (lub `▁`). Z kolei `tiktoken` to zoptymalizowany pod kątem wydajności *koder* (tokenizer) stworzony przez OpenAI do obsługi gotowych słowników – nie służy on do uczenia nowych modeli tokenizacji.

Zalecenia projektowe:

- **Do uczenia nowego słownika:** SentencePiece (doskonały do projektów wielojęzycznych, nie wymaga pre-tokenizacji) lub Hugging Face Tokenizers.
- **Do szybkiej tokenizacji/detokenizacji za pomocą słowników OpenAI:** tiktoken (`cl100k_base`, `o200k_base`).
- **Kompleksowe rozwiązanie:** Hugging Face Tokenizers – jedna biblioteka do uczenia i produkcyjnego wdrażania.

## Zbuduj to

### Krok 1: BPE od podstaw

Zobacz `code/main.py`. Pętla główna wygląda następująco:

```python
def train_bpe(corpus, num_merges):
    vocab = {tuple(word) + ("</w>",): count for word, count in corpus.items()}
    merges = []
    for _ in range(num_merges):
        pairs = Counter()
        for symbols, freq in vocab.items():
            for a, b in zip(symbols, symbols[1:]):
                pairs[(a, b)] += freq
        if not pairs:
            break
        best = pairs.most_common(1)[0][0]
        merges.append(best)
        vocab = apply_merge(vocab, best)
    return merges
```

Warto zwrócić uwagę na trzy kluczowe aspekty tej implementacji: symbol `</w>` oznacza koniec wyrazu (dzięki czemu sufiks i przedrostek o tym samym zapisie nie zostaną błędnie połączone); ważenie częstością sprawia, że najpopularniejsze pary są łączone jako pierwsze; kolejność reguł łączenia (merges) jest ściśle zdefiniowana i musi być stosowana identycznie podczas tokenizacji.

### Krok 2: Tokenizacja za pomocą wyuczonych reguł łączenia

```python
def encode_bpe(word, merges):
    symbols = list(word) + ["</w>"]
    for a, b in merges:
        i = 0
        while i < len(symbols) - 1:
            if symbols[i] == a and symbols[i + 1] == b:
                symbols = symbols[:i] + [a + b] + symbols[i + 2:]
            else:
                i += 1
    return symbols
```

Ta uproszczona implementacja ma złożoność O(n · |merges|). Systemy produkcyjne (takie jak tiktoken czy tokenizatory HF napisane w języku Rust) wykorzystują kolejki priorytetowe i indeksowanie rang reguł łączenia, dzięki czemu działają w czasie niemal liniowym.

### Krok 3: SentencePiece w praktyce

```python
import sentencepiece as spm

spm.SentencePieceTrainer.train(
    input="corpus.txt",
    model_prefix="my_tokenizer",
    vocab_size=8000,
    model_type="bpe",          # lub "unigram"
    character_coverage=0.9995, # niższa wartość dla CJK (np. 0.9995 dla ang., 0.995 dla jap.)
    normalization_rule_name="nmt_nfkc",
)

sp = spm.SentencePieceProcessor(model_file="my_tokenizer.model")
print(sp.encode("untokenizable", out_type=str))
# ['_un', 'token', 'izable']
```

Uwaga: SentencePiece nie wymaga wcześniejszego podziału tekstu na słowa (pre-tokenization). Spacje są kodowane jako specjalny znak. Parametr `character_coverage` określa, jaki odsetek unikalnych znaków z korpusu ma zostać bezpośrednio uwzględniony w słowniku, a jaki zostanie zmapowany do tokena `<unk>`.

### Krok 4: Użycie biblioteki tiktoken do obsługi modeli OpenAI

```python
import tiktoken
enc = tiktoken.get_encoding("o200k_base")
print(enc.encode("untokenizable"))        # [127340, 101028]
print(len(enc.encode("Hello, world!")))   # 4
```

Biblioteka służy wyłącznie do kodowania i dekodowania. Jest niezwykle szybka dzięki silnikowi napisanemu w języku Rust. Zapewnia dokładne odwzorowanie tokenizacji modeli GPT-4/5, co pozwala na precyzyjne wyliczanie długości kontekstu oraz szacowanie kosztów API.

## Typowe pułapki i problemy (stan na rok 2026)

- **Rozbieżność słowników (Tokenizer drift):** Trenowanie modelu z użyciem słownika A i próba wnioskowania na słowniku B. Ponieważ identyfikatory (IDs) tokenów się nie zgadzają, model generuje całkowicie losowy tekst. Dobrą praktyką jest weryfikacja sumy kontrolnej pliku `tokenizer.json` w potokach CI.
- **Niejednoznaczność białych znaków:** Te same słowa poprzedzone lub niepoprzedzone spacją mogą dawać zupełnie inne tokeny. Zawsze precyzyjnie definiuj parametry `add_special_tokens` oraz `add_prefix_space`.
- **Problem niedouczonych tokenizatorów wielojęzycznych:** Tokenizatory trenowane na korpusach zdominowanych przez język angielski dzielą teksty w pismach niełacińskich na bardzo krótkie fragmenty (często pojedyncze litery lub bajty). w efekcie ten sam prompt w języku japońskim czy arabskim generował 5–10 razy więcej tokenów (i kosztował odpowiednio więcej) w modelach GPT-3.5 niż w angielskim. Nowe słowniki (np. `o200k_base` w GPT-4o) znacznie złagodziły ten problem.
- **Dzielenie emotikonów (Emoji splitting):** Pojedynczy znak emoji po tokenizacji może zostać rozbity nawet na 5 odrębnych tokenów bajtowych. Należy to uwzględnić przy szacowaniu limitów okna kontekstowego.

## Rekomendowane podejścia

| Sytuacja | Zalecane rozwiązanie |
|----------|------|
| Trening modelu jednojęzycznego od zera | Hugging Face Tokenizers (BPE) |
| Trening modelu wielojęzycznego | SentencePiece (Unigram, `character_coverage=0.9995`) |
| Integracja z API OpenAI / Szacowanie kosztów | tiktoken (`o200k_base` dla modeli z rodziny GPT-4) |
| Słownictwo dziedzinowe (kod, matematyka, chemia/białka) | Wytrenuj dedykowany tokenizer BPE na korpusie dziedzinowym i połącz go ze słownikiem bazowym |
| Urządzenia brzegowe (Edge AI) / Małe modele | Unigram (mniejsze słowniki dają lepszą kompresję i wyższą jakość) |

Rozmiar słownika (vocabulary size) to hiperparametr skalowania, a nie stała wartość. Ogólna reguła: ~32k tokenów dla modeli <1B parametrów, 50k–100k dla modeli 1B–10B, oraz 200k+ dla modeli wielojęzycznych i flagowych (frontier models).

## Zapisywanie szablonu

Zapisz jako `outputs/skill-bpe-vs-wordpiece.md`:

```markdown
---
name: tokenizer-picker
description: Wybierz algorytm tokenizacji, rozmiar słownika oraz bibliotekę dla podanego korpusu i celu wdrożenia.
version: 1.0.0
phase: 5
lesson: 19
tags: [nlp, tokenization]
---

Na podstawie charakterystyki korpusu (rozmiar, języki, domena) oraz celu wdrożenia (trening od zera, dostrajanie, zgodność z zewnętrznym API) wygeneruj:

1. Algorytm: BPE, Unigram lub WordPiece (wraz z jednozdaniowym uzasadnieniem).
2. Biblioteka: SentencePiece, Hugging Face Tokenizers lub tiktoken (wraz z uzasadnieniem).
3. Rozmiar słownika: Zaokrąglony do najbliższego tysiąca (powiązany z rozmiarem modelu i zakresem obsługiwanych języków).
4. Konfiguracja pokrycia: Wartości parametrów `character_coverage`, `byte_fallback` oraz lista tokenów specjalnych.
5. Plan walidacji: Średnia liczba tokenów na słowo na wydzielonym zbiorze testowym, wskaźnik OOV, współczynnik kompresji oraz test poprawności rekonstrukcji tekstu (round-trip decode equality).

Nigdy nie trenuj tokenizatora z parametrem `character_coverage` <0.995 na korpusach zawierających rzadkie alfabety/znaki. Bezwzględnie wymagaj weryfikacji sumy kontrolnej pliku `tokenizer.json` w potokach CI. Oznaczaj każdy słownik jednojęzyczny o rozmiarze poniżej 16k jako zbyt ubogi.
```

## Ćwiczenia praktyczne

1. **Poziom łatwy:** Wytrenuj tokenizer BPE z limitem 500 reguł łączenia (merges) na niewielkim korpusie z pliku `code/main.py`. Zakoduj trzy nowe słowa. Ile z nich zostało reprezentowanych przez dokładnie 1 token, a ile przez więcej niż jeden?
2. **Poziom średni:** Porównaj liczbę tokenów wygenerowanych dla 100 angielskich zdań z Wikipedii za pomocą tokenizatorów `cl100k_base`, `o200k_base` oraz SentencePiece BPE wytrenowanego przez Ciebie ze słownikiem o rozmiarze 32k. Podaj współczynniki kompresji dla każdego z nich.
3. **Poziom trudny:** Wytrenuj tokenizatory BPE, Unigram oraz WordPiece na tym samym korpusie tekstowym. Zmierz wpływ wyboru tokenizatora na końcową jakość małego klasyfikatora wydźwięku. Czy zmiana algorytmu tokenizacji wpływa na miarę F1 o więcej niż 1 punkt procentowy?

## Kluczowe pojęcia

| Termin | Potoczne określenie | Znaczenie precyzyjne |
|------|-----------------|----------------------|
| BPE | Kodowanie par bajtów | Algorytm zachłannego łączenia najczęstszych par znaków/bajtów aż do uzyskania docelowej wielkości słownika. |
| Byte-level BPE (BBPE) | Brak tokenów nieznanych (no UNK) | Odmiana BPE operująca na 256 podstawowych bajtach; standard stosowany m.in. w modelach GPT-2 czy Llama. |
| Unigram | Tokenizator probabilistyczny | Algorytm odrzucający tokeny z dużego zestawu kandydatów na podstawie wiarygodności logarytmicznej; stosowany w T5 i modelach Gemma. |
| SentencePiece | SentencePiece | Biblioteka realizująca tokenizację BPE/Unigram na surowym tekście; spacje są kodowane jako specjalny znak. |
| tiktoken | tiktoken | Zoptymalizowany pod kątem szybkości tokenizer BPE stworzony w języku Rust na potrzeby modeli OpenAI; nie wspiera uczenia nowych słowników. |
| Reguły łączenia (Merges) | Reguły scalania | Uporządkowana lista reguł postaci `(a, b) -> ab`, aplikowanych w procesie tokenizacji w identycznej kolejności, w jakiej zostały wyuczone. |
| Pokrycie znaków (Character coverage) | Character coverage | Odsetek znaków z korpusu treningowego bezpośrednio uwzględnianych w słowniku; dla tekstów łacińskich standardem jest wartość 0.9995. |

## Literatura uzupełniająca

- [Sennrich, Haddow, Birch (2015). Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909) — oryginalna publikacja wprowadzająca algorytm BPE do translacji maszynowej.
- [Kudo (2018). Subword Regularization: Improving Neural Network Translation Models with Ultra-fast Subword Algorithms](https://arxiv.org/abs/1804.10959) — praca wprowadzająca tokenizację Unigram i metodę regularyzacji podwyrazowej.
- [Kudo & Richardson (2018). SentencePiece: A simple and language independent subword tokenizer for neural text processing](https://arxiv.org/abs/1808.06226) — publikacja prezentująca architekturę i możliwości biblioteki SentencePiece.
- [Hugging Face — podsumowanie tokenizatorów](https://huggingface.co/docs/transformers/tokenizer_summary) — zwięzłe omówienie i porównanie różnych algorytmów.
- [Repozytorium tiktoken OpenAI](https://github.com/openai/tiktoken) — oficjalny kod źródłowy oraz przykłady użycia biblioteki tiktoken.
