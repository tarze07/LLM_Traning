# Budowanie tokenizera od podstaw

> Lekcja 01 dała ci zabawkę. Ta lekcja daje ci narzędzie.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 10, Lekcja 01 (Tokenizatory: BPE, WordPiece, SentencePiece)
**Czas:** ~90 minut

## Cele nauczania

- Zbuduj tokenizator BPE klasy produkcyjnej obsługujący Unicode, normalizację białych znaków i tokeny specjalne
- Zaimplementuj rezerwę na poziomie bajtów, dzięki której tokenizator zakoduje dowolne dane wejściowe (w tym emoji, znaki CJK i kod) bez generowania nieznanych tokenów
- Dodaj wzorce wyrażeń regularnych stosowane przed tokenizacją, które dzielą tekst na granicach słów przed uruchomieniem scalania BPE
- Wytrenuj niestandardowy tokenizator na korpusie i oceń jego współczynnik kompresji w porównaniu z tiktoken na tekście wielojęzycznym

## Problem

Twój tokenizator BPE z Lekcji 01 działa poprawnie na tekście angielskim. Teraz podaj mu tekst japoński. Albo emotikony. Albo kod Pythona z mieszanymi tabulatorami i spacjami.

Przestanie działać.

Nie dlatego, że BPE jest błędne — lecz dlatego, że implementacja jest niepełna. Tokenizator produkcyjny obsługuje surowe bajty w dowolnym kodowaniu, normalizuje Unicode przed podziałem, zarządza tokenami specjalnymi, które nigdy nie są łączone, łączy wstępną tokenizację z podziałem na podciągi. Wszystko to musi działać wystarczająco szybko, aby nie stanowić wąskiego gardła potoku treningowego przetwarzającego 15 bilionów tokenów.

Tokenizator GPT-2 ma 50 257 tokenów. Llama 3 ma 128 256. GPT-4 ma około 100 000. To nie są liczby z zabawkowych projektów. Tablice scaleń stojące za tymi słownikami były trenowane na setkach gigabajtów tekstu. Otaczająca je maszyneria — normalizacja, wstępna tokenizacja, wstrzykiwanie tokenów specjalnych, formatowanie szablonów czatu — odróżnia tokenizator obsługujący „hello world" od tokenizatora obsługującego cały Internet.

Zbudujesz tę maszynerię.

## Koncepcja

### Pełny potok przetwarzania

Tokenizator produkcyjny to nie jeden algorytm. To proces składający się z pięciu etapów, z których każdy rozwiązuje odrębny problem.

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

Zadanie każdego etapu:

| Etap | Co robi | Dlaczego jest istotny |
|-------|------------|----------------|
| Normalizacja | NFKC Unicode, opcjonalnie zamiana na małe litery lub usuwanie akcentów | Ligatura „fi" (U+FB01) zamienia się w „fi" (dwa znaki). Bez normalizacji to samo słowo otrzymuje różne tokeny. |
| Wstępna tokenizacja | Podział tekstu na fragmenty przed BPE | Zapobiega łączeniu przez BPE tokenów przekraczających granice słów. „the cat" nigdy nie powinno dawać tokenu „ec". |
| Scalanie BPE | Zastosowanie wyuczonych reguł scalania do sekwencji bajtów | Rdzeń kompresji. Zamienia surowe bajty w tokeny podciągów. |
| Tokeny specjalne | Wstrzykiwanie [BOS], [EOS], [PAD] i znaczników szablonów czatu | Te tokeny mają stałe identyfikatory. Nigdy nie uczestniczą w scalaniu BPE. Model potrzebuje ich do budowania struktury wypowiedzi. |
| Mapowanie na identyfikatory | Zamiana ciągów tokenów na liczby całkowite | Model operuje na liczbach całkowitych, nie na ciągach znaków. |

### BPE na poziomie bajtu

Tokenizator z Lekcji 01 działał na bajtach UTF-8 — i to był właściwy wybór. Pominęliśmy jednak ważną kwestię: co się stanie, gdy bajty nie będą poprawnym UTF-8?

BPE na poziomie bajtu rozwiązuje ten problem, traktując każdą możliwą wartość bajtu (0–255) jako prawidłowy token. Bazowy słownik liczy dokładnie 256 wpisów. Dowolny plik — tekstowy, binarny, uszkodzony — można tokenizować bez generowania nieznanego tokenu.

GPT-2 dodał pewien trik: każdy bajt jest mapowany na możliwy do wydrukowania znak Unicode, co sprawia, że słownik pozostaje czytelny dla człowieka. Bajt 0x20 (spacja) odpowiada w tym odwzorowaniu znakowi „G". To czysto kosmetyczny zabieg — algorytm nie zwraca na to uwagi.

Prawdziwa siła BPE na poziomie bajtu polega na tym, że obsługuje każdy język świata. Chińskie znaki zajmują po 3 bajty UTF-8. Japoński może zajmować 3–4 bajty. Arabski, dewanagari, emoji — wszystko to jedynie sekwencje bajtów. Algorytm BPE wyszukuje wzorce w tych sekwencjach dokładnie tak samo, jak robi to dla bajtów angielskiego ASCII.

### Wstępna tokenizacja

Zanim BPE dotknie tekstu, należy podzielić go na fragmenty. Zapobiega to tworzeniu przez algorytm scalań obejmujących granice słów.

GPT-2 używa do podziału tekstu wzorca wyrażenia regularnego:

```
'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+
```

Ten wzorzec wyodrębnia skróty („don't" dzieli się na „don" i „'t"), słowa z opcjonalną spacją wiodącą, liczby, znaki interpunkcyjne i białe znaki. Spacja wiodąca jest dołączana do słowa — „the cat" staje się więc `["the", " cat"]`, nie `["the", "", "cat"]`.

Llama korzysta z SentencePiece, które całkowicie pomija wyrażenia regularne. Traktuje surowy strumień bajtów jako jedną długą sekwencję i pozostawia algorytmowi BPE swobodę wyznaczania granic. Podejście prostsze, ale dające BPE większą swobodę w tworzeniu tokenów łączących różne słowa.

Wybór ma znaczenie. Wzorzec wyrażenia regularnego z GPT-2 uniemożliwia tokenizatorowi nauczenie się połączeń między końcem jednego słowa a początkiem następnego. SentencePiece na to zezwala, co czasem daje lepszą kompresję, lecz tokeny są trudniejsze do interpretacji.

### Tokeny specjalne

Każdy tokenizator produkcyjny rezerwuje identyfikatory tokenów dla znaczników strukturalnych:

| Token | Przeznaczenie | Używany przez |
|-------|---------|--------|
| `[BOS]` / `<s>` | Początek sekwencji | Llama 3, GPT |
| `[EOS]` / `</s>` | Koniec sekwencji | Wszystkie modele |
| `[PAD]` | Wypełnienie przy wyrównywaniu partii | BERT, T5 |
| `[UNK]` | Nieznany token (BPE na poziomie bajtu eliminuje tę potrzebę) | BERT, WordPiece |
| `<\|im_start\|>` | Początek bloku wiadomości czatu | ChatGPT, Qwen |
| `<\|im_end\|>` | Koniec bloku wiadomości czatu | ChatGPT, Qwen |
| `<\|user\|>` | Znacznik tury użytkownika | Llama 3 |
| `<\|assistant\|>` | Znacznik tury asystenta | Llama 3 |

Tokeny specjalne nigdy nie są dzielone przez BPE. Są dopasowywane dokładnie przed uruchomieniem algorytmu scalania, zastępowane stałym identyfikatorem, a otaczający tekst jest tokenizowany normalnie.

### Szablony czatu

To właśnie w tym miejscu większość implementacji zawodzi, a wielu programistów się gubi.

Gdy wysyłasz wiadomości do modelu czatu, API przyjmuje listę wiadomości:

```
[
  {"role": "system", "content": "You are helpful."},
  {"role": "user", "content": "Hello"},
  {"role": "assistant", "content": "Hi there!"}
]
```

Model nie widzi JSON. Widzi płaską sekwencję tokenów. Szablon czatu konwertuje listę wiadomości na tę płaską sekwencję za pomocą tokenów specjalnych. Każdy model robi to inaczej:

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

Błąd w szablonie skutkuje tym, że model generuje bełkot. Został wytrenowany na ściśle określonym formacie. Każde odchylenie — brakująca nowa linia, zamieniony token, dodatkowa spacja — sprawia, że dane wejściowe wykraczają poza rozkład treningowy.

### Wydajność

Python jest zbyt wolny do tokenizacji produkcyjnej.

tiktoken (OpenAI) jest napisany w Rust z powiązaniami dla Pythona. Tokenizatory HuggingFace również korzystają z Rust. SentencePiece używa C++. Wszystkie te implementacje są 10–100 razy szybsze od czystego Pythona.

Dla zobrazowania skali: tokenizowanie 15 bilionów tokenów na potrzeby wstępnego trenowania Llamy 3 przy szybkości 1 miliona tokenów na sekundę (szybki Python) zajęłoby 174 dni. Przy 100 milionach tokenów na sekundę (Rust) zajmuje to 1,7 dnia.

W tej lekcji budujesz tokenizator w Pythonie, by zrozumieć algorytm. W środowisku produkcyjnym korzystałbyś ze skompilowanej implementacji i dotykał wyłącznie pythonowego opakowania.

## Zbuduj to

### Krok 1: Kodowanie na poziomie bajtu

Fundament całego systemu. Zamień dowolny ciąg znaków na sekwencję bajtów, odwzoruj każdy bajt na możliwy do wydrukowania znak (w celu wyświetlania) i odwróć ten proces.

```python
def bytes_to_tokens(text):
    return list(text.encode("utf-8"))

def tokens_to_text(token_bytes):
    return bytes(token_bytes).decode("utf-8", errors="replace")
```

Przetestuj tekst wielojęzyczny, by zobaczyć liczbę bajtów:

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

„hello" ma 5 bajtów. „你好" to 6 bajtów (3 na znak). Ogniste emoji zajmuje 4 bajty. Tokenizator bajtowy nie interesuje się językiem — bajty to bajty.

### Krok 2: Wstępna tokenizacja wyrażeniem regularnym

Podziel tekst na fragmenty przy użyciu wzorca wyrażenia regularnego z GPT-2. Każdy fragment jest tokenizowany przez BPE niezależnie.

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

Moduł `regex` obsługuje właściwości Unicode (`\p{L}` dla liter, `\p{N}` dla cyfr). Standardowy moduł `re` nie posiada tej funkcjonalności, więc używa się wówczas klas ASCII. Do produkcyjnych tokenizerów wielojęzycznych zainstaluj `regex`.

Przykład użycia:

```python
print(pre_tokenize("Hello, world! Don't stop."))
# [' Hello', ',', ' world', '!', " Don", "'t", ' stop', '.']
```

Spacja wiodąca pozostaje połączona ze słowem. Skrócenia rozdzielają się przy apostrofie. Interpunkcja staje się odrębnym fragmentem. BPE nigdy nie połączy tokenów ponad tymi granicami.

### Krok 3: BPE na sekwencjach bajtów

Podstawowy algorytm z Lekcji 01, działający tym razem niezależnie na każdym wstępnie stokenizowanym fragmencie.

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

### Krok 4: Obsługa tokenów specjalnych

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

### Krok 5: Pełna klasa tokenizatora

Połącz wszystkie elementy: normalizacja, podział na tokeny specjalne, wstępna tokenizacja, scalanie BPE, mapowanie na identyfikatory.

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

Prawdziwa próba. Podaj tokenizatorowi angielski, chiński, emoji i kod.

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

Chińskie znaki zajmują po 3 bajty. Emoji generuje 4 bajty. Żaden z nich nie powoduje awarii tokenizatora ani nie generuje nieznanych tokenów. To właśnie siła BPE na poziomie bajtu.

## Użyj tego

### Porównanie rzeczywistych tokenizerów

Załaduj tokenizatory z Llamy 3, GPT-4 i Mistrala. Sprawdź, jak każdy z nich radzi sobie z tym samym wielojęzycznym akapitem.

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

Dla tego samego tekstu każdy tokenizator zwróci inną liczbę tokenów. Llama 3 ze słownikiem 128 tys. wpisów agresywniej łączy częste wzorce. GPT-4 ze słownikiem 100 tys. plasuje się pośrodku. Mistral ze słownikiem 32 tys. produkuje więcej tokenów, lecz wymaga mniejszej warstwy osadzania.

Kompromis jest zawsze taki sam: większy słownik oznacza krótsze sekwencje, ale więcej parametrów modelu.

## Wyślij to

Ta lekcja generuje gotowy prompt do tworzenia i debugowania tokenizerów produkcyjnych. Zobacz `outputs/prompt-tokenizer-builder.md`.

## Ćwiczenia

1. **Łatwe:** Dodaj metodę `get_token_bytes(id)`, która zwraca surowe bajty dla dowolnego identyfikatora tokena. Użyj jej, by sprawdzić, co faktycznie reprezentują najczęściej scalane tokeny.
2. **Średnie:** Zaimplementuj wstępny tokenizator w stylu Llamy, który dzieli na białe znaki i cyfry, lecz zachowuje spacje wiodące. Porównaj uzyskany słownik z podejściem opartym na wyrażeniu regularnym GPT-2 dla tego samego korpusu.
3. **Trudne:** Dodaj metodę szablonu czatu, która przyjmuje listę wiadomości `{"role": ..., "content": ...}` i generuje poprawną sekwencję tokenów dla formatu czatu Llamy 3. Przetestuj wynik w odniesieniu do implementacji HuggingFace.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to faktycznie oznacza |
|------|----------------|----------------------|
| BPE na poziomie bajtu | „Tokenizator bajtowy" | BPE z bazowym słownikiem 256 bajtów — obsługuje dowolne dane wejściowe bez nieznanych tokenów |
| Wstępna tokenizacja | „Podział przed BPE" | Podział tekstu na podstawie wyrażeń regularnych lub innych reguł, zapobiegający scalaniu BPE ponad granicami słów |
| Normalizacja NFKC | „Oczyszczanie Unicode" | Kanoniczny rozkład z kompozycją zgodności — ligatura „fi" staje się „fi", „A" o pełnej szerokości staje się „A" |
| Szablon czatu | „Przekształcanie wiadomości na tokeny" | Ściśle określony format konwersji listy wiadomości (rola/treść) na płaską sekwencję tokenów — specyficzny dla modelu i musi odpowiadać formatowi treningowemu |
| Tokeny specjalne | „Tokeny sterujące" | Zarezerwowane identyfikatory omijające BPE — [BOS], [EOS], [PAD], znaczniki czatu — dopasowywane dokładnie przed scalaniem |
| Płodność (fertility) | „Tokeny na słowo" | Stosunek liczby tokenów wyjściowych do słów wejściowych — 1,3 dla angielskiego w GPT-4, 2–3 dla koreańskiego; wyższa wartość oznacza zmarnowany kontekst |
| tiktoken | „Tokenizator OpenAI" | Implementacja BPE w Rust z powiązaniami dla Pythona — 10–100 razy szybsza niż czysty Python |
| Tablica scaleń | „Słownik" | Uporządkowana lista par bajtów wyuczonych podczas treningu — to właśnie jest wyuczona wiedza tokenizatora |

## Dalsze czytanie

- [Źródło tiktoken (OpenAI)](https://github.com/openai/tiktoken) -- implementacja BPE w Rust używana przez GPT-3.5/4
- [Tokenizatory HuggingFace](https://github.com/huggingface/tokenizers) -- biblioteka tokenizerów w Rust obsługująca BPE, WordPiece, Unigram
- [Artykuł Llama 3 (Meta, 2024)](https://arxiv.org/abs/2407.21783) -- szczegóły dotyczące słownika 128 tys. wpisów i trenowania tokenizatora
- [SentencePiece (Kudo i Richardson, 2018)](https://arxiv.org/abs/1808.06226) -- tokenizacja niezależna od języka
- [Źródło tokenizatora GPT-2](https://github.com/openai/gpt-2/blob/master/src/encoder.py) -- oryginalne odwzorowanie bajtów na Unicode
