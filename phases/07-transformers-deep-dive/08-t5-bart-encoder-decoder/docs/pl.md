# T5, BART — modele kodera-dekodera

> Koderzy rozumieją. Dekodery generują. Połącz je ponownie, a otrzymasz model zbudowany dla zadań wejściowych → wyjściowych: tłumaczenie, podsumowanie, przepisanie, transkrypcja.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 7 · 05 (Pełny transformator), Faza 7 · 06 (BERT), Faza 7 · 07 (GPT)
**Czas:** ~45 minut

## Problem

GPT przeznaczony tylko do dekodera i BERT przeznaczony wyłącznie do kodowania rozbierają architekturę 2017 do innego celu. Jednak wiele zadań ma w naturalny sposób charakter wejścia-wyjścia:

- Tłumaczenie: angielski → francuski.
- Podsumowanie: artykuł na 5000 tokenów → podsumowanie na 200 tokenów.
- Rozpoznawanie mowy: żetony dźwiękowe → żetony tekstowe.
- Ekstrakcja strukturalna: proza ​​→ JSON.

W tym przypadku koder-dekoder zapewnia najczystsze dopasowanie. Koder tworzy gęstą reprezentację źródła. Dekoder generuje sygnał wyjściowy, uwzględniając tę ​​reprezentację na każdym kroku. Trening polega na przesunięciu o jeden po stronie wyjściowej. Taka sama strata jak GPT, tylko uzależniona od wyjścia enkodera.

Dwa artykuły zdefiniowały nowoczesny podręcznik:

1. **T5** (Raffel i in. 2019). „Transformator transferu tekstu na tekst”. Każde zadanie NLP przeformułowane w formie wprowadzania i wysyłania tekstu. Pojedyncza architektura, jedno słownictwo, pojedyncza strata. Wstępnie przeszkolony na podstawie przewidywania maskowanego zakresu (uszkodzone zakresy na wejściu, dekoduj je na wyjściu).
2. **BART** (Lewis i in. 2019). „Transformator dwukierunkowy i autoregresyjny”. Odszumianie autoenkodera: zepsucie danych wejściowych na wiele sposobów (tasowanie, maskowanie, usuwanie, obracanie), poproś dekoder o zrekonstruowanie oryginału.

W 2026 r. format kodera-dekodera będzie nadal aktualny tam, gdzie liczy się struktura danych wejściowych:

- Szept (mowa → tekst).
- Stos tłumaczeń Google.
- Niektóre modele uzupełniania/naprawy kodu, które mają odrębne struktury kontekstu i edycji.
- Flan-T5 i warianty zadań ustrukturyzowanego rozumowania.

Tylko dekoder znalazł się w centrum uwagi, ale koder-dekoder nigdy nie zniknął.

## Koncepcja

![Koder-dekoder z możliwością wzajemnej uwagi](../assets/encoder-decoder.svg)

### Pętla do przodu

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

Co najważniejsze, koder działa raz na każde wejście. Dekoder działa w sposób autoregresyjny, ale na każdym kroku korzysta z *tego samego* sygnału wyjściowego kodera. Buforowanie wyjścia kodera jest darmowym przyspieszeniem w przypadku długich danych wejściowych.

### Wstępne szkolenie T5 — uszkodzenie zakresu

Wybierz losowe zakresy danych wejściowych (średnia długość 3 żetony, łącznie 15%). Zastąp każdy zakres unikalnym znacznikiem: `<extra_id_0>`, `<extra_id_1>` itd. Dekoder wyprowadza tylko uszkodzone zakresy z przedrostkiem wskaźnika:

```
source: The quick <extra_id_0> fox jumps <extra_id_1> dog
target: <extra_id_0> brown <extra_id_1> over the lazy
```

Tańszy sygnał niż przewidywanie całej sekwencji. Konkurencyjny z MLM (BERT) i prefiksem-LM (UniLM) w ablacji papieru T5.

### Trening wstępny BART — odszumianie wielu szumów

BART wypróbowuje pięć funkcji szumu:

1. Maskowanie tokenów.
2. Usunięcie tokena.
3. Wypełnienie tekstu (maskowanie zakresu, dekoder wstawia odpowiednią długość).
4. Permutacja zdania.
5. Rotacja dokumentów.

Połączenie wypełniania tekstu i permutacji zdań pozwoliło uzyskać najlepsze liczby w dalszej części tekstu. Dekoder zawsze rekonstruuje oryginał. Dane wyjściowe BART to pełna sekwencja, a nie tylko uszkodzone zakresy — zatem obliczenia przedtreningowe są wyższe niż T5.

### Wnioskowanie

Ta sama generacja autoregresji co GPT. Obowiązuje próbkowanie zachłanne/wiązka/top-p. Wyszukiwanie wiązki (szerokość 4–5) jest standardem w przypadku tłumaczeń i podsumowań, ponieważ rozkład wyników jest węższy niż czat.

### Kiedy wybrać każdy wariant w 2026 r

| Zadanie | Koder-dekoder? | Dlaczego |
|------|----------------------|-----|
| Tłumaczenie | Tak, zwykle | Wyczyść sekwencję źródłową; stała dystrybucja mocy; wyszukiwanie belek działa |
| Zamiana mowy na tekst | Tak (szeptem) | Modalność wejściowa różni się od wyjściowej; koder kształtuje funkcje audio |
| Rozmowa / rozumowanie | Nie, tylko dekoder | Brak trwałego „wejściowego” — rozmowa jest sekwencją |
| Uzupełnianie kodu | Zwykle nie | Wygrywa wyłącznie dekoder z długim kontekstem; modele kodu, takie jak Qwen 2.5 Coder, są przeznaczone wyłącznie do dekodera |
| Podsumowanie | Albo działa | BART i PEGASUS pobiły wcześniejsze wartości bazowe przeznaczone wyłącznie dla dekodera; pasują do nich nowoczesne LLM obsługujące tylko dekoder |
| Ekstrakcja strukturalna | Albo | T5 jest czysty, ponieważ „tekst → tekst” pochłania dowolny format wyjściowy |

Trend od ~ 2022 r.: tylko dekoder przejmuje zadania, które kiedyś posiadał koder-dekoder, ponieważ (a) LLM dostrojone wyłącznie do instrukcji uogólniają do czegokolwiek poprzez monitowanie, (b) jedna architektura skaluje się łatwiej niż dwie, (c) RLHF zakłada dekoder. Koder-dekoder sprawdza się tam, gdzie modalność wejścia jest inna (mowa, obrazy) lub gdzie liczy się jakość wyszukiwania wiązki.

## Zbuduj to

Zobacz `code/main.py`. Implementujemy zniekształcanie zakresu w stylu T5 dla korpusu zabawek — najbardziej przydatny pojedynczy element tej lekcji, ponieważ pojawia się od tamtej pory w każdym przepisie wstępnego uczenia kodera-dekodera.

### Krok 1: uszkodzenie zakresu

```python
def corrupt_spans(tokens, mask_rate=0.15, mean_span=3.0, rng=None):
    """Pick spans summing to ~mask_rate of tokens. Return (corrupted_input, target)."""
    n = len(tokens)
    n_mask = max(1, int(n * mask_rate))
    n_spans = max(1, int(round(n_mask / mean_span)))
    ...
```

Format docelowy to konwencja T5: `<sent0> span0 <sent1> span1 ...`. Uszkodzone dane wejściowe przeplatają niezmienione żetony z żetonami wartowniczymi w lokalizacjach przęseł.

### Krok 2: sprawdź podróż w obie strony

Biorąc pod uwagę uszkodzone dane wejściowe i cel, zrekonstruuj oryginalne zdanie. Jeśli twoje zepsucie jest odwracalne, podanie w przód jest dobrze zdefiniowane. To jest sprawdzenie zdrowego rozsądku — prawdziwe szkolenie nigdy tego nie robi, ale test jest tani i wyłapuje pojedyncze błędy w księgowości zakresu.

### Krok 3: Zakłócanie BART-u

Pięć funkcji: `token_mask`, `token_delete`, `text_infill`, `sentence_permute`, `document_rotate`. Skomponuj dwa z nich i pokaż wynik.

## Użyj tego

Odniesienie do HuggingFace:

```python
from transformers import T5ForConditionalGeneration, T5Tokenizer
tok = T5Tokenizer.from_pretrained("google/flan-t5-base")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

inputs = tok("translate English to French: Attention is all you need.", return_tensors="pt")
out = model.generate(**inputs, max_new_tokens=32)
print(tok.decode(out[0], skip_special_tokens=True))
```

Sztuczka T5: nazwa zadania trafia do tekstu wejściowego. Ten sam model obsługuje dziesiątki zadań, ponieważ każde zadanie polega na wprowadzaniu i wysyłaniu tekstu. W 2026 roku ten wzorzec został uogólniony w modelach wyposażonych wyłącznie w dekoder dostrojony zgodnie z instrukcjami, ale T5 najpierw go skodyfikował.

## Wyślij to

Zobacz `outputs/skill-seq2seq-picker.md`. Umiejętność wybiera pomiędzy koderem-dekoderem a dekoderem tylko dla nowego zadania, biorąc pod uwagę strukturę wejścia-wyjścia, opóźnienie i cele jakościowe.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`, zastosuj uszkodzenie zakresu do 30-znakowego zdania, sprawdź, czy połączenie tokenów źródłowych innych niż wartownicze z zdekodowanymi zakresami docelowymi odtwarza oryginał.
2. **Średni.** Zaimplementuj szum `text_infill` BART: zamień losowe zakresy na pojedynczy token `<mask>`, a dekoder musi wywnioskować poprawną długość zakresu i zawartość. Pokaż jeden przykład.
3. **Trudne.** Dopracuj `flan-t5-small` na małym korpusie angielsko-świńskim-łacińskim (200 par). Zmierz BLEU na wystawionym zestawie 50 par. Porównanie z dostrajaniem `Llama-3.2-1B` na tych samych danych i przy tych samych obliczeniach.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Koder-dekoder | „Transformator Seq2seq” | Dwa stosy: dwukierunkowy koder dla wejścia, dekoder przyczynowy z koncentracją uwagi dla wyjścia. |
| Uwaga krzyżowa | „Gdzie źródło rozmawia z celem” | Q dekodera × K/V kodera. Jedyne miejsce, w którym informacja z kodera trafia do dekodera. |
| Uszkodzenie zakresu | „Sztuczka przedtreningowa T5” | Zamień losowe obszary na żetony Strażników; dekoder wyprowadza zakresy. |
| Cel odszumiania | „Gra BARTA” | Zastosuj funkcję szumu na wejściu i naucz dekoder rekonstrukcji czystej sekwencji. |
| Żeton Strażnika | „Span class="notranslate">__IC_15__</span> symbol zastępczy” | Specjalne tokeny, które oznaczają uszkodzone przęsła w źródle i ponownie oznaczają je w celu. |
| Flan | „T5 dostosowany do instrukcji” | T5 dostrojony do > 1800 zadań; uczynił koder-dekoder konkurencyjnym w wykonywaniu instrukcji. |
| Wyszukiwanie wiązki | „Strategia dekodowania” | Zachowaj górne k częściowych sekwencji na każdym kroku; standard tłumaczenia/streszczenia. |
| Nauczyciel zmusza | „Wprowadzanie czasu treningu” | Podczas uczenia podaj do dekodera prawdziwy poprzedni token wyjściowy, a nie próbkowany. |

## Dalsze czytanie

- [Raffel i in. (2019). Odkrywanie granic uczenia się transferowego za pomocą ujednoliconego transformatora zamiany tekstu na tekst](https://arxiv.org/abs/1910.10683) — T5.
- [Lewis i in. (2019). BART: Wstępne szkolenie w zakresie odszumiania sekwencji po sekwencji w zakresie generowania, tłumaczenia i rozumienia języka naturalnego](https://arxiv.org/abs/1910.13461) – BART.
- [Chung i in. (2022). Instrukcje skalowania — dostrojone modele językowe](https://arxiv.org/abs/2210.11416) — Flan-T5.
- [Radford i in. (2022). Solidne rozpoznawanie mowy dzięki słabemu nadzorowi na dużą skalę](https://arxiv.org/abs/2212.04356) — Whisper, kanoniczny koder-dekoder na rok 2026.
- [HuggingFace `modeling_t5.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/t5/modeling_t5.py) — implementacja referencyjna.