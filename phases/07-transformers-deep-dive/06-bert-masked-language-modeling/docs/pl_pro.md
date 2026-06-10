# BERT — Modelowanie języka zamaskowanego

> GPT przewiduje następne słowo. BERT przewiduje brakujące słowo. Jedna zdanie różnicy — i pół dekady wszystkiego, co opiera się na reprezentacjach wektorowych.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 05 (pełny transformator), faza 5 · 02 (reprezentacja tekstu)
**Czas:** ~45 minut

## Problem

W 2018 roku każde zadanie NLP — analiza nastrojów, NER, kontrola jakości, wykrywanie zaangażowania — wymagało wytrenowania osobnego modelu od zera na własnych oznaczonych danych. Nie istniał żaden gotowy punkt startowy w postaci modelu rozumiejącego język, który można by dostroić. Projekt ELMo (2018) pokazał, że dwukierunkowy LSTM pozwala wstępnie trenować kontekstowe reprezentacje słów. To był krok naprzód, lecz podejście słabo się uogólniało.

BERT (Devlin i in., 2018) postawił następujące pytanie: co by się stało, gdyby wziąć koder transformatorowy, wytrenować go na ogromnym zbiorze tekstów z internetu i zmusić do przewidywania brakujących słów na podstawie kontekstu z obu stron? Następnie wystarczy dostroić jedną głowę do konkretnego zadania. Efektywność parametryczna okazała się przełomem.

Efekt był spektakularny: w ciągu 18 miesięcy BERT i jego warianty (RoBERTa, ALBERT, ELECTRA) zdominowały wszystkie istniejące tabele liderów NLP. Do 2020 roku wyszukiwarki, systemy moderacji treści i silniki wyszukiwania semantycznego na całym świecie korzystały z BERT-a w swoim rdzeniu.

W 2026 roku modele oparte wyłącznie na koderze nadal pozostają właściwym wyborem do klasyfikacji, wyszukiwania i ekstrakcji strukturalnej. Działają 5–10 razy szybciej na token niż dekodery, a ich reprezentacje wektorowe stanowią fundament nowoczesnych systemów wyszukiwania. ModernBERT (grudzień 2024) rozwinął tę architekturę, wprowadzając kontekst 8K dzięki Flash Attention, RoPE oraz GeGLU.

## Koncepcja

![Modelowanie języka maskowanego: wybieraj tokeny, maskuj je, przewidywaj oryginały](../assets/bert-mlm.svg)

### Sygnał treningowy

Weź zdanie: `the quick brown fox jumps over the lazy dog`.

Zamaskuj losowo 15% tokenów:

```
input:  the [MASK] brown fox jumps [MASK] the lazy dog
target: the  quick brown fox jumps  over  the lazy dog
```

Wytrenuj model, aby przewidywał oryginalne tokeny na zamaskowanych pozycjach. Koder jest dwukierunkowy, więc przy przewidywaniu `[MASK]` na pozycji 1 może korzystać z kontekstu `brown fox jumps` na pozycjach 2+. To właśnie to, czego GPT nie potrafi.

### Reguła maskowania BERT

Spośród 15% tokenów wybranych do przewidywania:

- 80% zostaje zastąpionych przez `[MASK]`.
- 10% zostaje zastąpionych losowym tokenem.
- 10% pozostaje bez zmian.

Dlaczego nie zawsze `[MASK]`? Token `[MASK]` nigdy nie pojawia się podczas wnioskowania. Gdyby model uczył się wyłącznie na zamaskowanych pozycjach, powstałoby przesunięcie dystrybucji między etapem treningu wstępnego a dostrajaniem. Kombinacja 10% losowych tokenów i 10% niezmiennych sprawia, że model pozostaje odporny na ten efekt.

### Przewidywanie następnego zdania (NSP) — i dlaczego zostało porzucone

Oryginalny BERT trenował również zadanie NSP: mając dwa zdania A i B, model miał przewidzieć, czy B bezpośrednio następuje po A. Badania ablacyjne przeprowadzone w ramach projektu RoBERTa (2019) wykazały, że NSP nie tylko nie pomaga, lecz wręcz pogarsza wyniki. Nowoczesne kodery pomijają to zadanie.

### Co zmieniło się w 2026 roku: ModernBERT

Artykuł ModernBERT z 2024 roku przebudował blok transformatora z użyciem nowszych rozwiązań:

| Składnik | Oryginalny BERT (2018) | ModernBERT (2024) |
|----------|----------------------|--------------------------------|
| Kodowanie pozycji | Wyuczone, absolutne | RoPE |
| Aktywacja | GELU | GeGLU |
| Normalizacja | Layer Norm | Pre-Norm RMSNorm |
| Uwaga | Pełna, gęsta | Naprzemienna: lokalna (128) + globalna |
| Długość kontekstu | 512 | 8192 |
| Tokenizer | WordPiece | BPE |

Architektura jest natywnie przystosowana do Flash Attention. Wnioskowanie jest 2–3 razy szybsze przy sekwencjach długości 8K w porównaniu z DeBERTa-v3, przy jednoczesnej poprawie wyników na benchmarku GLUE.

### Przypadki użycia, w których koder wygrywa w 2026 roku

| Zadanie | Dlaczego koder przewyższa dekoder |
|------|--------------------------|
| Wyszukiwanie semantyczne / osadzanie | Dwukierunkowy kontekst = lepsza jakość reprezentacji na token |
| Klasyfikacja (nastroje, intencje, toksyczność) | Jedno przejście w przód; brak narzutu generowania |
| NER / tagowanie tokenów | Wyjście na każdej pozycji, natywnie dwukierunkowe |
| Zero-shot z NLI | Głowica klasyfikatora na wyjściu kodera |
| Reranking w RAG | Punktacja parami, 10 razy szybsza niż reranking przez LLM |

## Zbuduj to

### Krok 1: logika maskowania

Zobacz `code/main.py`. Funkcja `create_mlm_batch` przyjmuje listę identyfikatorów tokenów, rozmiar słownika i prawdopodobieństwo maskowania. Zwraca wejściowe identyfikatory (z zastosowanymi maskami) oraz etykiety — wyłącznie na zamaskowanych pozycjach, wszędzie indziej wartość -100 (konwencja ignorowania indeksu w PyTorch).

```python
def create_mlm_batch(tokens, vocab_size, mask_prob=0.15, rng=None):
    input_ids = list(tokens)
    labels = [-100] * len(tokens)
    for i, t in enumerate(tokens):
        if rng.random() < mask_prob:
            labels[i] = t
            r = rng.random()
            if r < 0.8:
                input_ids[i] = MASK_ID
            elif r < 0.9:
                input_ids[i] = rng.randrange(vocab_size)
            # else: keep original
    return input_ids, labels
```

### Krok 2: uruchom predykcję MLM na małym korpusie

Wytrenuj 2-warstwowy koder z głowicą MLM na słowniku złożonym z 20 słów i 200 zdań. Bez obliczania gradientów — jest to wyłącznie weryfikacja poprawności przejścia w przód. Pełny trening wymaga PyTorcha.

### Krok 3: porównaj strategie maskowania

Pokaż, jak reguła trójstronna zapewnia użyteczność modelu bez konieczności stosowania `[MASK]`. Podaj zdanie bez masek i zdanie z maskami. Oba powinny dawać rozsądne rozkłady tokenów, ponieważ model zetknął się z oboma wzorcami podczas treningu.

### Krok 4: dostrojenie głowicy

Zastąp głowicę MLM głowicą klasyfikacyjną na zabawkowym zbiorze danych do analizy nastrojów. Trenowana jest wyłącznie głowica — koder pozostaje zamrożony. Jest to standardowy schemat stosowany we wszystkich zastosowaniach BERT-a.

## Użyj tego

```python
from transformers import AutoModel, AutoTokenizer

tok = AutoTokenizer.from_pretrained("answerdotai/ModernBERT-base")
model = AutoModel.from_pretrained("answerdotai/ModernBERT-base")

text = "Attention is all you need."
inputs = tok(text, return_tensors="pt")
out = model(**inputs).last_hidden_state   # (1, N, 768)
```

**Modele do osadzania są dostrojonym BERT-em.** Modele `sentence-transformers`, takie jak `all-MiniLM-L6-v2`, to BERT trenowany ze stratą kontrastową. Architektura kodera pozostaje identyczna — zmienia się tylko funkcja straty.

**Rerankerzy oparte na cross-enkoderach to również dostrojony BERT.** Klasyfikacja par odbywa się w formacie `[CLS] query [SEP] doc [SEP]`. Dwukierunkowa uwaga między zapytaniem a dokumentem to właśnie to, co daje cross-enkoderom przewagę jakościową nad bi-enkoderami.

**Kiedy nie wybierać BERT-a w 2026 roku.** We wszystkich zadaniach generatywnych. Koder nie ma sensownego sposobu na autoregresyjne tworzenie tokenów. Ponadto w scenariuszach, gdzie modele poniżej 1B parametrów mogłyby wystarczyć — mały dekoder, taki jak Phi-3-Mini czy Qwen2-1.5B, może dorównać jakością BERT-owi przy większej elastyczności.

## Wyślij to

Zobacz `outputs/skill-bert-finetuner.md`. Dokument opisuje dostrajanie BERT-a pod kątem nowego zadania klasyfikacji lub ekstrakcji: wybór szkieletu, specyfikacja głowicy, dane, ewaluacja i kryteria zatrzymania.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py` i wydrukuj rozkład masek na 10 000 tokenów. Sprawdź, czy wybrano ~15% tokenów, a z nich ~80% zostało zastąpionych tokenem `[MASK]`.
2. **Średnie.** Zastosuj maskowanie całych słów: jeśli słowo jest podzielone na podtokeny, maskuj wszystkie naraz lub żadnego. Zmierz, czy poprawia to dokładność MLM na korpusie złożonym z 500 zdań.
3. **Trudne.** Wytrenuj małego BERT-a (2 warstwy, d=64) na 10 000 zdań z publicznego zbioru danych. Dostosuj token `[CLS]` do zadania SST-2. Porównaj wyniki z bazowym modelem dekoderem przy zbliżonej liczbie parametrów — który wariant wygrywa?

## Kluczowe terminy

| Termin | Potoczne określenie | Właściwe znaczenie |
|------|-----------------|----------------------|
| MLM | „Modelowanie języka zamaskowanego" | Sygnał treningowy: losowo zamień 15% tokenów na `[MASK]`, przewiduj oryginalne wartości. |
| Dwukierunkowy | „Patrzy w obie strony" | Uwaga kodera nie ma maski przyczynowej — każda pozycja widzi każdą inną pozycję. |
| `[CLS]` | „Token puli" | Specjalny token dołączany na początku każdej sekwencji; jego końcowa reprezentacja służy jako osadzenie na poziomie zdania. |
| `[SEP]` | „Separator segmentów" | Rozdziela sparowane sekwencje (np. zapytanie/dokument, zdanie A/B). |
| NSP | „Przewidywanie następnego zdania" | Drugie zadanie treningu wstępnego BERT; uznane za bezużyteczne w RoBERTa, usunięte po 2019 roku. |
| Dostrajanie | „Adaptacja do zadania" | Koder pozostaje w większości zamrożony; trenuje się małą głowicę na jego wyjściu pod kątem konkretnego zadania. |
| Cross-enkoder | „Reranker" | BERT przyjmujący zarówno zapytanie, jak i dokument jako dane wejściowe; generuje wynik trafności. |
| ModernBERT | „Odświeżenie z 2024 roku" | Koder przebudowany z użyciem RoPE, RMSNorm, GeGLU oraz naprzemiennej uwagi lokalnej/globalnej; kontekst 8K. |

## Dalsze czytanie

- [Devlin i in. (2018). BERT: Pre-training of Deep Bilateral Transformers for Language Understanding](https://arxiv.org/abs/1810.04805) — artykuł oryginalny.
- [Liu i in. (2019). RoBERTa: solidnie zoptymalizowane podejście do treningu wstępnego BERT](https://arxiv.org/abs/1907.11692) — jak poprawnie trenować BERT; eliminuje NSP.
- [Clark i in. (2020). ELECTRA: Wstępne szkolenie koderów tekstu jako dyskryminatorów, a nie generatorów](https://arxiv.org/abs/2003.10555) — wykrywanie zastąpionego tokena przewyższa MLM przy identycznym budżecie obliczeniowym.
- [Warner i in. (2024). Inteligentniejszy, lepszy, szybszy, dłuższy: nowoczesny koder dwukierunkowy](https://arxiv.org/abs/2412.13663) — artykuł opisujący ModernBERT.
- [HuggingFace `modeling_bert.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/bert/modeling_bert.py) — kanoniczna implementacja kodera.
