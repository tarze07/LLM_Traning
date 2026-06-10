# Budowanie tokenizera od podstaw

> Lekcja 01 dała ci zabawkę. Ta lekcja daje ci broń.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 10, Lekcja 01 (Tokenizatory: BPE, WordPiece, SentencePiece)
**Czas:** ~90 minut

## Cele nauczania

- Zbuduj tokenizator BPE klasy produkcyjnej, który obsługuje Unicode, normalizację białych znaków i tokeny specjalne
- Zaimplementuj rezerwę na poziomie bajtów, aby tokenizator mógł kodować dowolne dane wejściowe (w tym emoji, CJK i kod) bez nieznanych tokenów
- Dodaj wzorce wyrażeń regularnych przed tokenizacją, które dzielą tekst na granicach słów przed zastosowaniem scalania BPE
- Wytrenuj niestandardowy tokenizer na korpusie i oceń jego współczynnik kompresji w porównaniu z tiktokenem w tekście wielojęzycznym

## Problem

Twój tokenizer BPE z Lekcji 01 działa na tekście w języku angielskim. Teraz rzuć na to Japończyka. Lub emotikony. Lub kod Pythona z mieszanymi tabulatorami i spacjami.

To się łamie.

Nie dlatego, że BPE jest błędne – ponieważ wdrożenie jest niekompletne. Tokenizator produkcyjny obsługuje surowe bajty w dowolnym kodowaniu, normalizuje Unicode przed podziałem, zarządza specjalnymi tokenami, które nigdy nie są łączone, łączy wstępną tokenizację z dzieleniem podsłów, a wszystko to robi na tyle szybko, aby nie ograniczać potoku szkoleniowego przetwarzającego 15 bilionów tokenów.

Tokenizer GPT-2 ma 50 257 tokenów. Lama 3 ma 128 256. GPT-4 ma około 100 000. To nie są numerki do zabawek. Tabele scalania stojące za tymi słownikami zostały przeszkolone na setkach gigabajtów tekstu, a otaczająca je maszyneria – normalizacja, wstępna tokenizacja, specjalne wstrzykiwanie tokenów, formatowanie szablonu czatu – jest tym, co odróżnia tokenizator obsługujący „witaj świecie” od tego, który obsługuje cały Internet.

Zbudujesz tę maszynę.

## Koncepcja

### Pełny rurociąg

Tokenizator produkcyjny nie jest jednym algorytmem. Jest to proces składający się z pięciu etapów, z których każdy rozwiązuje inny problem.

```mermaid
graph LR
    A[Raw Text] --> B[Normalize]
    B --> C[Pre-Tokenize]
    C --> D[BPE Merge]
    D --> E[Special Tokens]
    E --> F[Token IDs]

    style A fill:#1a1a2e,stroke:#e94560,color:#fff
    style B fill:#1a1a2e,stroke:#e94560,color:#fff
    style C fill:#1a1a2e,stroke:#e94560,color:#fff
    style D fill:#1a1a2e,stroke:#e94560,color:#fff
    style E fill:#1a1a2e,stroke:#e94560,color:#fff
    style F fill:#1a1a2e,stroke:#e94560,color:#fff
```

Każdy etap ma określone zadanie:

| Scena | Co to robi | Dlaczego to ma znaczenie |
|-------|------------|----------------|
| Normalizuj | NFKC Unicode, opcjonalnie małe litery, opcjonalnie paski akcentujące | Ligatura „fi” (U+FB01) zmienia się w „fi” (dwa znaki). Bez tego to samo słowo otrzymuje różne tokeny. |
| Wstępna tokenizacja | Podziel tekst na fragmenty przed BPE | Zapobiega łączeniu BPE ponad granicami słów. „kot” nigdy nie powinien dawać żetonu „e c”. |
| Połączenie BPE | Zastosuj wyuczone reguły scalania do sekwencji bajtów | Kompresja rdzenia. Zamienia surowe bajty w tokeny słów podrzędnych. |
| Specjalne żetony | Wstrzyknij [BOS], [EOS], [PAD], znaczniki szablonów czatu | Tokeny te mają stałe identyfikatory. Nigdy nie uczestniczą w fuzjach BPE. Model potrzebuje ich do konstrukcji. |
| Mapowanie identyfikatora | Konwertuj ciągi tokenów na identyfikatory całkowite | Model widzi liczby całkowite, a nie ciągi znaków. |

### BPE na poziomie bajtu

Tokenizer z lekcji 01 działał na bajtach UTF-8. To było właściwe wezwanie. Ale pominęliśmy coś ważnego: co się stanie, jeśli te bajty nie będą miały prawidłowego formatu UTF-8?

BPE na poziomie bajtu rozwiązuje ten problem, traktując każdą możliwą wartość bajtu (0-255) jako ważny token. Twoje podstawowe słownictwo to dokładnie 256 haseł. Dowolny plik — tekstowy, binarny, uszkodzony — można tokenizować bez tworzenia nieznanego tokena.

GPT-2 dodał sztuczkę: zmapuj każdy bajt na możliwy do wydrukowania znak Unicode, dzięki czemu słownictwo pozostanie czytelne dla człowieka. Bajt 0x20 (spacja) staje się w ich mapowaniu znakiem „G”. To jest czysto kosmetyczne. Algorytmu to nie obchodzi.

Prawdziwa moc: BPE na poziomie bajtów obsługuje każdy język na świecie. Chińskie znaki mają po 3 bajty UTF-8. Japoński może mieć 3-4 bajty. Arabski, dewanagari, emoji – wszystkie to tylko sekwencje bajtów. Algorytm BPE znajduje wzorce w tych sekwencjach bajtów dokładnie w taki sam sposób, w jaki znajduje wzorce w bajtach angielskiego ASCII.

### Wstępna tokenizacja

Zanim BPE dotknie Twojego tekstu, musisz podzielić go na kawałki. Zapobiega to tworzeniu przez algorytm scalania tokenów obejmujących granice słów.

GPT-2 używa wzorca wyrażenia regularnego do dzielenia tekstu:

```
'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+
```

Ten wzorzec dzieli się na skurcze („nie” staje się „don” + „'t”), słowa z opcjonalnymi spacjami wiodącymi, liczbami, znakami interpunkcyjnymi i białymi znakami. Wiodąca spacja jest dołączona do słowa - więc „kot” staje się [„the”, „cat”], a nie [„the”, „”, „cat”].

Lama używa SentencePiece, które całkowicie pomija wyrażenie regularne. Traktuje surowy strumień bajtów jako jedną długą sekwencję i pozwala algorytmowi BPE określić granice. Jest to prostsze, ale daje BPE większą swobodę w tworzeniu tokenów krzyżówek.

Wybór ma znaczenie. Wyrażenie regularne GPT-2 uniemożliwia tokenizatorowi nauczenie się, że „the” na końcu jednego słowa i „the” na początku następnego powinny się połączyć. Pozwala na to SentencePiece, co czasami zapewnia bardziej wydajną kompresję, ale tokeny mniej interpretowalne.

### Specjalne żetony

Każdy tokenizator produkcyjny rezerwuje identyfikatory tokenów dla znaczników strukturalnych:

| Znak | Cel | Używany przez |
|-------|---------|--------|
| `[BOS]` / `<s>` | Początek sekwencji | Lama 3, GPT |
| `[EOS]` / `</s>` | Koniec sekwencji | Wszystkie modele |
| `[PAD]` | Wyściółka do wyrównania partii | BERT, T5 |
| `[UNK]` | Nieznany token (BPE na poziomie bajtów eliminuje to) | BERT, WordPiece |
| `<\|im_start\|>` | Początek granicy wiadomości czatu | CzatGPT, Qwen |
| `<\|im_end\|>` | Koniec granicy wiadomości czatu | CzatGPT, Qwen |
| `<\|user\|>` | Znacznik skrętu użytkownika | Lama 3 |
| `<\|assistant\|>` | Asystent znacznika skrętu | Lama 3 |

Tokeny specjalne nigdy nie są dzielone przez BPE. Są one dopasowywane dokładnie przed uruchomieniem algorytmu scalania, zastępowane ich stałym identyfikatorem, a otaczający tekst jest normalnie tokenizowany.

### Szablony czatu

W tym miejscu większość ludzi jest zdezorientowana i większość implementacji się psuje.

Kiedy wysyłasz wiadomości do modelu czatu, API akceptuje listę wiadomości:

```
[
  {"role": "system", "content": "You are helpful."},
  {"role": "user", "content": "Hello"},
  {"role": "assistant", "content": "Hi there!"}
]
```

Model nie widzi JSON. Widzi płaską sekwencję tokenów. Szablon czatu konwertuje wiadomości na płaską sekwencję za pomocą specjalnych tokenów. Każdy model robi to inaczej:

```
Llama 3:
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are helpful.<|eot_id|><|start_header_id|>user<|end_header_id|>

Hello<|eot_id|><|start_header_id|>assistant<|end_header_id|>

Hi there!<|eot_id|>

ChatGPT:
<|im_start|>system
You are helpful.<|im_end|>
<|im_start|>user
Hello<|im_end|>
<|im_start|>assistant
Hi there!<|im_end|>
```

Jeśli źle zrobisz szablon, model wygeneruje śmieci. Został przeszkolony w jednym dokładnym formacie. Każde odchylenie — brak nowej linii, zamieniony token, dodatkowa spacja — powoduje umieszczenie danych wejściowych poza dystrybucją uczącą.

### Prędkość

Python jest zbyt wolny do tokenizacji produkcyjnej.

tiktoken (OpenAI) jest napisany w Rust z powiązaniami z Pythonem. Tokenizatory HuggingFace to także Rust. Fragment zdania to C++. Osiągają one 10-100-krotne przyspieszenie w porównaniu z czystym Pythonem.

Dla perspektywy: tokenizowanie 15 bilionów tokenów na potrzeby wstępnego szkolenia Lamy 3 przy szybkości 1 miliona tokenów na sekundę (szybki Python) zajęłoby 174 dni. Przy 100 milionach tokenów na sekundę (Rust) zajmuje to 1,7 dnia.

Budujesz w Pythonie, aby zrozumieć algorytm. W środowisku produkcyjnym używałbyś skompilowanej implementacji i dotykał tylko opakowania Pythona.

## Zbuduj to

### Krok 1: Kodowanie na poziomie bajtów

Fundament. Konwertuj dowolny ciąg znaków na sekwencję bajtów, mapuj każdy bajt na znak, który można wydrukować w celu wyświetlenia, i odwróć proces.

```python
def bytes_to_tokens(text):
    return list(text.encode("utf-8"))

def tokens_to_text(token_bytes):
    return bytes(token_bytes).decode("utf-8", errors="replace")
```

Przetestuj tekst wielojęzyczny, aby zobaczyć liczbę bajtów:

```python
texts = [
    ("English", "hello"),
    ("Chinese", "你好"),
    ("Emoji", "🔥"),
    ("Mixed", "hello你好🔥"),
]

for label, text in texts:
    b = bytes_to_tokens(text)
    print(f"{label}: {len(text)} chars -> {len(b)} bytes -> {b}")
```

„cześć” ma 5 bajtów. „你好” to 6 bajtów (3 na znak). Emoji ognia ma 4 bajty. Tokenizator na poziomie bajtów nie dba o to, jaki to język. Bajty to bajty.

### Krok 2: Wstępny tokenizator z użyciem wyrażenia regularnego

Podziel tekst na fragmenty, używając wzorca wyrażenia regularnego GPT-2. Każda porcja jest niezależnie tokenizowana przez BPE.

```python
import re

try:
    import regex
    GPT2_PATTERN = regex.compile(
        r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
    )
except ImportError:
    GPT2_PATTERN = re.compile(
        r"""'(?:[sdmt]|ll|ve|re)| ?[a-zA-Z]+| ?[0-9]+| ?[^\s\w]+|\s+(?!\S)|\s+"""
    )

def pre_tokenize(text):
    return [match.group() for match in GPT2_PATTERN.finditer(text)]
```

Moduł `regex` obsługuje zmiany właściwości Unicode (`\p{L}` dla liter, `\p{N}` dla liczb). Moduł standardowej biblioteki `re` tego nie robi, więc wracamy do klas znaków ASCII. W przypadku produkcyjnych wielojęzycznych tokenizerów zainstaluj `regex`.

Wypróbuj:

```python
print(pre_tokenize("Hello, world! Don't stop."))
# [' Hello', ',', ' world', '!', " Don", "'t", ' stop', '.']
```

Wiodąca spacja pozostaje połączona ze słowem. Skurcze rozdzielają się przy apostrofie. Interpunkcja staje się odrębną częścią. BPE nigdy nie będzie łączyć tokenów poza tymi granicami.

### Krok 3: BPE w sekwencjach bajtów

Podstawowy algorytm z lekcji 01, ale teraz działający niezależnie na wstępnie tokenizowanych fragmentach.

```python
from collections import Counter

def get_byte_pairs(chunks):
    pairs = Counter()
    for chunk in chunks:
        byte_seq = list(chunk.encode("utf-8"))
        for i in range(len(byte_seq) - 1):
            pairs[(byte_seq[i], byte_seq[i + 1])] += 1
    return pairs

def apply_merge(byte_seq, pair, new_id):
    merged = []
    i = 0
    while i < len(byte_seq):
        if i < len(byte_seq) - 1 and byte_seq[i] == pair[0] and byte_seq[i + 1] == pair[1]:
            merged.append(new_id)
            i += 2
        else:
            merged.append(byte_seq[i])
            i += 1
    return merged
```

### Krok 4: Specjalna obsługa tokenów

Tokeny specjalne wymagają dokładnego dopasowania i stałych identyfikatorów. Całkowicie omijają BPE.

```python
class SpecialTokenHandler:
    def __init__(self):
        self.special_tokens = {}
        self.pattern = None

    def add_token(self, token_str, token_id):
        self.special_tokens[token_str] = token_id
        escaped = [re.escape(t) for t in sorted(self.special_tokens.keys(), key=len, reverse=True)]
        self.pattern = re.compile("|".join(escaped))

    def split_with_specials(self, text):
        if not self.pattern:
            return [(text, False)]
        parts = []
        last_end = 0
        for match in self.pattern.finditer(text):
            if match.start() > last_end:
                parts.append((text[last_end:match.start()], False))
            parts.append((match.group(), True))
            last_end = match.end()
        if last_end < len(text):
            parts.append((text[last_end:], False))
        return parts
```

### Krok 5: Pełna klasa tokenizera

Połącz wszystko razem: normalizuj, dziel na specjalne tokeny, wstępnie tokenizuj, łącz BPE, mapuj na identyfikatory.

```python
import unicodedata

class ProductionTokenizer:
    def __init__(self):
        self.merges = {}
        self.vocab = {i: bytes([i]) for i in range(256)}
        self.special_handler = SpecialTokenHandler()
        self.next_id = 256

    def normalize(self, text):
        return unicodedata.normalize("NFKC", text)

    def train(self, text, num_merges):
        text = self.normalize(text)
        chunks = pre_tokenize(text)
        chunk_bytes = [list(chunk.encode("utf-8")) for chunk in chunks]

        for i in range(num_merges):
            pairs = Counter()
            for seq in chunk_bytes:
                for j in range(len(seq) - 1):
                    pairs[(seq[j], seq[j + 1])] += 1
            if not pairs:
                break
            best = max(pairs, key=pairs.get)
            new_id = self.next_id
            self.next_id += 1
            self.merges[best] = new_id
            self.vocab[new_id] = self.vocab[best[0]] + self.vocab[best[1]]
            chunk_bytes = [apply_merge(seq, best, new_id) for seq in chunk_bytes]

    def add_special_token(self, token_str):
        token_id = self.next_id
        self.next_id += 1
        self.special_handler.add_token(token_str, token_id)
        self.vocab[token_id] = token_str.encode("utf-8")
        return token_id

    def encode(self, text):
        text = self.normalize(text)
        parts = self.special_handler.split_with_specials(text)
        all_ids = []
        for part_text, is_special in parts:
            if is_special:
                all_ids.append(self.special_handler.special_tokens[part_text])
            else:
                for chunk in pre_tokenize(part_text):
                    byte_seq = list(chunk.encode("utf-8"))
                    for pair, new_id in self.merges.items():
                        byte_seq = apply_merge(byte_seq, pair, new_id)
                    all_ids.extend(byte_seq)
        return all_ids

    def decode(self, ids):
        byte_parts = []
        for token_id in ids:
            if token_id in self.vocab:
                byte_parts.append(self.vocab[token_id])
        return b"".join(byte_parts).decode("utf-8", errors="replace")

    def vocab_size(self):
        return len(self.vocab)
```

### Krok 6: Test wielojęzyczny

Prawdziwy sprawdzian. Rzuć na to angielski, chiński, emoji i kod.

```python
corpus = (
    "The quick brown fox jumps over the lazy dog. "
    "The quick brown fox runs through the forest. "
    "Machine learning models process natural language. "
    "Deep learning transforms how we build software. "
    "def train(model, data): return model.fit(data) "
    "def predict(model, x): return model(x) "
)

tok = ProductionTokenizer()
tok.train(corpus, num_merges=50)

bos = tok.add_special_token("<|begin|>")
eos = tok.add_special_token("<|end|>")

test_texts = [
    "The quick brown fox.",
    "你好世界",
    "Hello 🌍 World",
    "def foo(x): return x + 1",
    f"<|begin|>Hello<|end|>",
]

for text in test_texts:
    ids = tok.encode(text)
    decoded = tok.decode(ids)
    print(f"Input:   {text}")
    print(f"Tokens:  {len(ids)} ids")
    print(f"Decoded: {decoded}")
    print()
```

Chińskie znaki zajmują po 3 bajty każdy. Emoji generuje 4 bajty. Żaden z nich nie powoduje awarii tokenizera. Żaden nie generuje nieznanych tokenów. To jest moc BPE na poziomie bajtów.

## Użyj tego

### Porównanie prawdziwych tokenizerów

Załaduj rzeczywiste tokenizery z Lamy 3, GPT-4 i Mistral. Zobacz, jak każdy z nich radzi sobie z tym samym wielojęzycznym akapitem.

```python
import tiktoken

gpt4_enc = tiktoken.get_encoding("cl100k_base")

test_paragraph = "Machine learning is powerful. 机器学习很强大。 L'apprentissage automatique est puissant. 🤖💪"

tokens = gpt4_enc.encode(test_paragraph)
pieces = [gpt4_enc.decode([t]) for t in tokens]
print(f"GPT-4 ({len(tokens)} tokens): {pieces}")
```

```python
from transformers import AutoTokenizer

llama_tok = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
mistral_tok = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")

for name, tok in [("Llama 3", llama_tok), ("Mistral", mistral_tok)]:
    tokens = tok.encode(test_paragraph)
    pieces = tok.convert_ids_to_tokens(tokens)
    print(f"{name} ({len(tokens)} tokens): {pieces[:20]}...")
```

Zobaczysz różne liczby tokenów dla tego samego tekstu. Lama 3 ze 128 tys. słownictwa bardziej agresywnie łączy wspólne wzorce. GPT-4 z 100K znajduje się pośrodku. Mistral z 32K produkuje więcej tokenów, ale ma mniejszą warstwę osadzającą.

Kompromis jest zawsze taki sam: większe słownictwo oznacza krótsze sekwencje, ale więcej parametrów.

## Wyślij to

Ta lekcja generuje monit dotyczący tworzenia i debugowania tokenizatorów produkcyjnych. Zobacz `outputs/prompt-tokenizer-builder.md`.

## Ćwiczenia

1. **Łatwe:** dodaj metodę `get_token_bytes(id)`, która pokazuje nieprzetworzone bajty dla dowolnego identyfikatora tokena. Użyj go, aby sprawdzić, co faktycznie reprezentują najpopularniejsze scalone tokeny.
2. **Średni:** Zaimplementuj wstępny tokenizator w stylu lamy, który dzieli na białe znaki i cyfry, ale zachowuje spacje wiodące. Porównaj jego słownictwo z podejściem do wyrażeń regularnych GPT-2 w tym samym korpusie.
3. **Trudne:** dodaj metodę szablonu czatu, która pobiera listę wiadomości `{"role": ..., "content": ...}` i generuje poprawną sekwencję tokenów dla formatu czatu Lama 3. Przetestuj to w porównaniu z implementacją HuggingFace.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|----------------------|
| BPE na poziomie bajtu | „Tokenizer działający na bajtach” | BPE z podstawowym słownikiem o wartości 256 bajtów - obsługuje dowolne dane wejściowe bez nieznanych tokenów |
| Wstępna tokenizacja | „Podział przed BPE” | Podział na podstawie wyrażeń regularnych lub reguł, który zapobiega łączeniu BPE poza granicami słów |
| Normalizacja NFKC | „Oczyszczanie Unicode” | Rozkład kanoniczny, po którym następuje kompozycja zgodności — ligatura „fi” staje się „fi”, „A” o pełnej szerokości staje się „A” |
| Szablon czatu | „Jak wiadomości stają się tokenami” | Dokładny format konwertowania listy komunikatów o roli/treści na płaską sekwencję tokenów — specyficzny dla modelu i musi pasować do formatu szkoleniowego |
| Specjalne żetony | „Żetony kontrolne” | Zarezerwowane identyfikatory tokenów omijające BPE — [BOS], [EOS], [PAD], znaczniki czatu — dopasowane dokładnie przed połączeniem |
| Płodność | „Tokeny za słowo” | Stosunek tokenów wyjściowych do słów wejściowych — 1,3 dla języka angielskiego w GPT-4, 2-3 dla języka koreańskiego, wyższy oznacza zmarnowany kontekst |
| tiktoken | „Tokenizator OpenAI” | Implementacja Rust BPE z powiązaniami Pythona — 10–100 razy szybsza niż czysty Python |
| Połącz tabelę | „Słownictwo” | Uporządkowana lista łączeń par bajtów wyuczona podczas szkolenia - JEST to wiedza wyuczona tokenizatora |

## Dalsze czytanie

- [Źródło tiktokena OpenAI](https://github.com/openai/tiktoken) -- Implementacja Rust BPE używana przez GPT-3.5/4
- [Tokenizatory HuggingFace](https://github.com/huggingface/tokenizers) -- Biblioteka tokenizerów Rust obsługująca BPE, WordPiece, Unigram
– [Artykuł Lama 3 (Meta, 2024)](https://arxiv.org/abs/2407.21783) – szczegółowe informacje na temat 128 tys. słownictwa i szkolenia w zakresie tokenizatora
– [SentencePiece (Kudo i Richardson, 2018)](https://arxiv.org/abs/1808.06226) – tokenizacja niezależna od języka
- [Źródło tokenizera GPT-2](https://github.com/openai/gpt-2/blob/master/src/encoder.py) -- oryginalne mapowanie bajtów na Unicode