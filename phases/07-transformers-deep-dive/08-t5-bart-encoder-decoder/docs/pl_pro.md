# T5, BART — modele kodera-dekodera

> Kodery rozumieją. Dekodery generują. Połącz je razem, a otrzymasz model stworzony do zadań wejście → wyjście: tłumaczenie, streszczanie, przepisywanie, transkrypcja.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 05 (Pełny transformator), Faza 7 · 06 (BERT), Faza 7 · 07 (GPT)
**Czas:** ~45 minut

## Problem

GPT oparty wyłącznie na dekoderze i BERT oparty wyłącznie na koderze rozkładają architekturę z 2017 roku, każdy służąc innemu celowi. Wiele zadań ma jednak z natury charakter wejście-wyjście:

- Tłumaczenie: angielski → francuski.
- Streszczanie: artykuł na 5000 tokenów → podsumowanie na 200 tokenów.
- Rozpoznawanie mowy: tokeny dźwiękowe → tokeny tekstowe.
- Ekstrakcja strukturalna: proza → JSON.

W takich przypadkach architektura koder-dekoder stanowi najczystsze dopasowanie do problemu. Koder tworzy gęstą reprezentację źródła. Dekoder generuje dane wyjściowe, uwzględniając tę reprezentację na każdym kroku. Uczenie polega na przesunięciu o jeden token po stronie wyjściowej. Funkcja straty jest taka sama jak w GPT, lecz uzależniona od wyjścia kodera.

Dwa artykuły wyznaczyły nowoczesne standardy w tej dziedzinie:

1. **T5** (Raffel i in. 2019). „Transformator transferu tekstu na tekst". Każde zadanie NLP zostało przeformułowane jako przepływ tekstu na wejście i wyjście. Jedna architektura, jedno słownictwo, jedna funkcja straty. Wstępnie uczony na podstawie przewidywania zamaskowanych zakresów — uszkodzone zakresy trafiają na wejście, dekoder odtwarza je na wyjściu.
2. **BART** (Lewis i in. 2019). „Dwukierunkowy i autoregresyjny transformator". Autoenkoder oparty na odszumianiu: dane wejściowe są celowo niszczone na wiele sposobów (tasowanie, maskowanie, usuwanie, obracanie), a zadaniem dekodera jest rekonstrukcja oryginału.

W 2026 roku format koder-dekoder pozostaje aktualny wszędzie tam, gdzie struktura danych wejściowych ma znaczenie:

- Whisper (mowa → tekst).
- Stos tłumaczeń Google.
- Niektóre modele uzupełniania i naprawy kodu, które rozdzielają kontekst od edycji.
- Flan-T5 i warianty zadań ustrukturyzowanego rozumowania.

Architektura oparta wyłącznie na dekoderze znalazła się w centrum uwagi, jednak koder-dekoder nigdy nie zniknął.

## Koncepcja

![Koder-dekoder z uwagą wzajemną](../assets/encoder-decoder.svg)

### Pętla propagacji w przód

```
source tokens ─▶ encoder ─▶ (N_src, d_model)  ──┐
                                                 │
target tokens ─▶ decoder block                   │
                 ├─▶ masked self-attention       │
                 ├─▶ cross-attention ◀───────────┘
                 └─▶ FFN
                ↓
              next-token logits
```

Kluczowa obserwacja: koder przetwarza dane wejściowe tylko raz. Dekoder działa autoregresywnie, lecz na każdym kroku korzysta z *tego samego* wyjścia kodera. Buforowanie tego wyjścia stanowi bezpłatne przyspieszenie przy długich danych wejściowych.

### Wstępne uczenie T5 — uszkadzanie zakresów

Wybierane są losowe zakresy tokenów wejściowych (średnia długość 3 tokeny, łącznie 15%). Każdy zakres zastępowany jest unikalnym znacznikiem: `<extra_id_0>`, `<extra_id_1>` itd. Dekoder generuje wyłącznie uszkodzone zakresy, poprzedzone odpowiednim znacznikiem:

```
source: The quick <extra_id_0> fox jumps <extra_id_1> dog
target: <extra_id_0> brown <extra_id_1> over the lazy
```

To tańszy sygnał uczący niż przewidywanie całej sekwencji. W ablacjach z artykułu T5 wynik był porównywalny z MLM (BERT) i prefix-LM (UniLM).

### Wstępne uczenie BART — odszumianie wielopoziomowe

BART testuje pięć rodzajów szumu:

1. Maskowanie tokenów.
2. Usuwanie tokenów.
3. Wypełnianie tekstu (maskowanie zakresu — dekoder musi dopasować właściwą długość).
4. Permutacja zdań.
5. Rotacja dokumentu.

Najlepsze wyniki w zadaniach downstream uzyskano dla kombinacji wypełniania tekstu i permutacji zdań. Dekoder zawsze rekonstruuje oryginalną sekwencję. Wyjście BART to pełna sekwencja, a nie tylko uszkodzone zakresy — stąd koszt obliczeniowy wstępnego uczenia jest wyższy niż w T5.

### Wnioskowanie

Generowanierzebiega autoregresywnie, tak samo jak w GPT. Obowiązują te same strategie dekodowania: zachłanna, wiązki (beam search) i top-p. Wyszukiwanie wiązki (szerokość 4–5) jest standardem przy tłumaczeniu i streszczaniu, ponieważ rozkład prawdopodobieństw jest węższy niż w zastosowaniach konwersacyjnych.

### Kiedy wybrać dany wariant w 2026 r.

| Zadanie | Koder-dekoder? | Dlaczego |
|------|----------------------|-----|
| Tłumaczenie | Tak, zazwyczaj | Czysta sekwencja źródłowa; stabilna dystrybucja mocy; beam search działa dobrze |
| Zamiana mowy na tekst | Tak (Whisper) | Modalność wejścia różni się od wyjścia; koder modeluje cechy audio |
| Rozmowa / rozumowanie | Nie, tylko dekoder | Brak stałego „wejścia" — rozmowa jest jedną ciągłą sekwencją |
| Uzupełnianie kodu | Zazwyczaj nie | Architektura wyłącznie dekoderowa wygrywa przy długim kontekście; modele takie jak Qwen 2.5 Coder są oparte wyłącznie na dekoderze |
| Streszczanie | Oba rozwiązania sprawdzają się | BART i PEGASUS pobiły wcześniejsze modele oparte tylko na dekoderze; dorównują im nowoczesne LLM dekoderocentryczne |
| Ekstrakcja strukturalna | Oba | T5 jest wygodny, ponieważ podejście „tekst → tekst" przyjmuje dowolny format wyjścia |

Trend od około 2022 roku: architektura oparta wyłącznie na dekoderze przejmuje zadania, które dotychczas należały do koder-dekodera. Dzieje się tak z trzech powodów: (a) LLM dostrojone do instrukcji uogólniają na dowolne zadania poprzez odpowiednie promptowanie, (b) jedna architektura skaluje się łatwiej niż dwie, (c) RLHF zakłada użycie dekodera. Koder-dekoder pozostaje atrakcyjny tam, gdzie modalność wejścia jest odmienna (mowa, obrazy) lub gdzie liczy się jakość beam search.

## Zbuduj to

Zobacz `code/main.py`. Implementujemy uszkadzanie zakresów w stylu T5 dla przykładowego korpusu — to najważniejszy element tej lekcji, ponieważ ten mechanizm pojawia się w każdym przepisie wstępnego uczenia koder-dekoder od tamtej pory.

### Krok 1: uszkadzanie zakresów

```python
def corrupt_spans(tokens, mask_rate=0.15, mean_span=3.0, rng=None):
    """Pick spans summing to ~mask_rate of tokens. Return (corrupted_input, target)."""
    n = len(tokens)
    n_mask = max(1, int(n * mask_rate))
    n_spans = max(1, int(round(n_mask / mean_span)))
    ...
```

Format docelowy stosuje konwencję T5: `<sent0> span0 <sent1> span1 ...`. Uszkodzone dane wejściowe przeplatają niezmienione tokeny z tokenami wartowniczymi w miejscach usuniętych zakresów.

### Krok 2: weryfikacja odwracalności

Mając uszkodzone wejście i cel, odtwarzamy oryginalne zdanie. Jeśli uszkadzanie jest odwracalne, propagacja w przód jest dobrze zdefiniowana. To sprawdzenie poprawności — rzeczywiste uczenie nigdy tego nie robi, lecz test jest tani i wyłapuje pojedyncze błędy w zarządzaniu zakresami.

### Krok 3: zakłócanie w stylu BART

Pięć funkcji: `token_mask`, `token_delete`, `text_infill`, `sentence_permute`, `document_rotate`. Złóż dowolne dwie z nich i pokaż wynik.

## Użyj tego

Przykład z HuggingFace:

```python
from transformers import T5ForConditionalGeneration, T5Tokenizer
tok = T5Tokenizer.from_pretrained("google/flan-t5-base")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

inputs = tok("translate English to French: Attention is all you need.", return_tensors="pt")
out = model.generate(**inputs, max_new_tokens=32)
print(tok.decode(out[0], skip_special_tokens=True))
```

Kluczowy trick T5: nazwa zadania trafia bezpośrednio do tekstu wejściowego. Ten sam model obsługuje dziesiątki zadań, ponieważ każde z nich sprowadza się do przepływu tekst → tekst. W 2026 roku ten wzorzec uogólniły modele oparte wyłącznie na dekoderze, dostrojone zgodnie z instrukcjami — jednak T5 skodyfikował go jako pierwszy.

## Wyślij to

Zobacz `outputs/skill-seq2seq-picker.md`. Opisana tam umiejętność pozwala wybrać między architekturą koder-dekoder a dekoderocentryczną dla nowego zadania, uwzględniając strukturę wejście-wyjście, opóźnienie i cele jakościowe.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`, zastosuj uszkadzanie zakresów do 30-tokenowego zdania i sprawdź, czy połączenie nietkniętych tokenów źródłowych z dekodowanymi zakresami docelowymi odtwarza oryginał.
2. **Średnie.** Zaimplementuj szum `text_infill` z BART: zastąp losowe zakresy pojedynczym tokenem `<mask>`, a dekoder musi wywnioskować poprawną długość i zawartość zakresu. Pokaż jeden przykład.
3. **Trudne.** Dostosuj `flan-t5-small` na małym korpusie angielsko-pig-latin (200 par). Zmierz wynik BLEU na wydzielonym zestawie testowym 50 par. Porównaj z dostrajaniem `Llama-3.2-1B` na tych samych danych i przy tym samym budżecie obliczeniowym.

## Kluczowe terminy

| Termin | Co się mówi | Co to faktycznie oznacza |
|------|-----------------|----------------------|
| Koder-dekoder | „Transformator seq2seq" | Dwa stosy: dwukierunkowy koder dla wejścia, przyczynowy dekoder z uwagą wzajemną dla wyjścia. |
| Uwaga wzajemna (cross-attention) | „Miejsce, gdzie źródło spotyka cel" | Q dekodera × K/V kodera. Jedyny punkt, w którym informacja z kodera trafia do dekodera. |
| Uszkadzanie zakresów | „Trick przedtreningowy T5" | Zastąp losowe fragmenty tokenami wartowniczymi; dekoder odtwarza te fragmenty. |
| Cel odszumiania | „Gra BART-a" | Wprowadź szum na wejście i naucz dekoder rekonstrukcji czystej sekwencji. |
| Token wartowniczy | „Symbol zastępczy `<extra_id_N>`" | Specjalne tokeny oznaczające uszkodzone zakresy w źródle i odpowiadające im cele. |
| Flan | „T5 dostrojony do instrukcji" | T5 dostrojony na ponad 1800 zadaniach; uczynił koder-dekoder konkurencyjnym w wykonywaniu instrukcji. |
| Beam search | „Strategia dekodowania" | Zachowaj k najlepszych częściowych sekwencji na każdym kroku; standard w tłumaczeniu i streszczaniu. |
| Teacher forcing | „Dane wejściowe podczas uczenia" | Podczas uczenia podawaj dekoderowi rzeczywisty poprzedni token wyjściowy zamiast tokenu próbkowanego. |

## Literatura

- [Raffel i in. (2019). Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer](https://arxiv.org/abs/1910.10683) — T5.
- [Lewis i in. (2019). BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension](https://arxiv.org/abs/1910.13461) — BART.
- [Chung i in. (2022). Scaling Instruction-Finetuned Language Models](https://arxiv.org/abs/2210.11416) — Flan-T5.
- [Radford i in. (2022). Robust Speech Recognition via Large-Scale Weak Supervision](https://arxiv.org/abs/2212.04356) — Whisper, kanoniczny koder-dekoder w 2026 roku.
- [HuggingFace `modeling_t5.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/t5/modeling_t5.py) — implementacja referencyjna.
