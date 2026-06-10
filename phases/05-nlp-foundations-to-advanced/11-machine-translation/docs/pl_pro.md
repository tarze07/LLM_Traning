# Tłumaczenie maszynowe (Machine Translation)

> Tłumaczenie maszynowe to zadanie, które finansowało i napędzało badania nad NLP przez trzydzieści lat – i robi to nadal.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · Lekcja 10 (Mechanizm uwagi), Faza 5 · Lekcja 04 (GloVe, FastText i jednostki podsłowowe)
**Czas:** ~75 minut

## Problem

Model analizuje tekst w języku źródłowym i generuje jego odpowiednik w języku docelowym. Długość sekwencji bywa różna, podobnie jak szyk wyrazów. Pojedyncze słowo źródłowe może odpowiadać wielu słowom docelowym (i odwrotnie), a idiomy wykluczają proste mapowanie jeden do jednego. Na przykład polskie wyrażenie „tęsknię za tobą” po francusku brzmi „tu me manques” (co dosłownie oznacza „brakujesz mi”). Tradycyjne metody dopasowania na poziomie słów nie potrafią poprawnie obsłużyć takich struktur.

Tłumaczenie maszynowe to wyzwanie, które wymusiło rozwój kluczowych technologii w NLP: architektur Encoder-Decoder, mechanizmów uwagi, Transformerów, aż po współczesny paradygmat LLM. Postęp ten był możliwy, ponieważ jakość tłumaczeń dało się mierzyć matematycznie, co pozwalało na systematyczne zmniejszanie różnicy skuteczności między człowiekiem a algorytmem.

W tej lekcji pomijamy aspekt historyczny i przedstawiamy nowoczesne standardy (stan na rok 2026): wykorzystanie wielojęzycznych modeli typu Encoder-Decoder (np. NLLB-200 lub mBART), tokenizację na poziomie podsłów, wyszukiwanie wiązkowe (beam search), ewaluację za pomocą metryk BLEU i chrF, a także analizę krytycznych błędów (trybów awarii), które wciąż bywają niezauważane w systemach produkcyjnych.

## Pojęcia

Nowoczesne systemy tłumaczenia maszynowego (NMT) wykorzystują architekturę Transformer z enkoderem i dekoderem, wyszkoloną na korpusach równoległych. Enkoder przetwarza tekst źródłowy stokenizowany dla danego języka. Dekoder generuje tekst docelowy podsłowo po podsłowie, wykorzystując reprezentacje enkodera poprzez mechanizm uwagi krzyżowej (cross-attention, lekcja 10). Proces generowania opiera się na wyszukiwaniu wiązkowym (beam search), aby uniknąć błędów dekodowania zachłannego. Ostateczny tekst docelowy podlega detokenizacji, korekcie wielkości liter (detruecasing) i ewaluacji w odniesieniu do tłumaczeń referencyjnych.

Trzy decyzje wdrożeniowe mają kluczowy wpływ na jakość systemów MT:

- **Tokenizer:** SentencePiece (wariant BPE) wyszkolony na korpusie wielojęzycznym. Współdzielenie słownika między różnymi językami umożliwia tłumaczenie par zero-shot w modelach NLLB.
- **Rozmiar modelu:** Wersja destylowana `NLLB-200 (600M parameters)` jest na tyle lekka, że działa bezpośrednio na laptopie. Model `NLLB-200 (3.3B)` stanowi standard produkcyjny, natomiast wersja `54.5B` to flagowy model badawczy.
- **Dekodowanie:** Szerokość wiązki (beam width) rzędu 4-5 dla ogólnych tekstów. Stosowanie kary za długość (length penalty) zapobiega generowaniu zbyt krótkich zdań. Wprowadzenie dekodowania warunkowego (constrained decoding) wymusza użycie spójnej terminologii słownikowej.

## Implementacja krok po kroku

### Krok 1: Wywołanie gotowego modelu MT

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_id = "facebook/nllb-200-distilled-600M"
tok = AutoTokenizer.from_pretrained(model_id, src_lang="eng_Latn")
model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

src = "The cats are running."
inputs = tok(src, return_tensors="pt")

out = model.generate(
    **inputs,
    forced_bos_token_id=tok.convert_tokens_to_ids("fra_Latn"),
    num_beams=5,
    length_penalty=1.0,
    max_new_tokens=64,
)
print(tok.batch_decode(out, skip_special_tokens=True)[0])
```

```text
Les chats courent.
```

Kluczowe szczegóły: argument `src_lang` określa język źródłowy na potrzeby poprawnej tokenizacji. `forced_bos_token_id` wymusza na dekoderze generowanie w określonym języku docelowym. Te parametry są specyficzne dla modeli NLLB – modele takie jak mBART lub M2M-100 posiadają własną składnię konfiguracji języków docelowych.

### Krok 2: Ewaluacja z użyciem metryk BLEU i chrF

Metryka BLEU mierzy stopień pokrycia n-gramów między tekstem wygenerowanym a referencyjnym. Analizuje ona n-gramy o długościach od 1 do 4, oblicza średnią geometryczną precyzji i nakłada karę za zwięzłość (brevity penalty) dla zbyt krótkich tłumaczeń. Wyniki mieszczą się w przedziale [0, 100]. Metryka ta jest powszechnie stosowana, choć jej interpretacja bywa subiektywna: wynik 30 BLEU uważa się za akceptowalny/użyteczny, 40 za dobry, a 50 za wyjątkowo wysoki. Różnice wyników poniżej 1.0 BLEU traktuje się zazwyczaj jako szum statystyczny.

Metryka **chrF** oblicza wartość F-score na poziomie pojedynczych znaków (character n-grams). Jest znacznie czulsza w przypadku języków o bogatej fleksji (takich jak język polski), dla których metryka BLEU (bazująca na całych słowach) często zaniża rzeczywistą jakość tłumaczenia. chrF zazwyczaj raportuje się łącznie z BLEU.

```python
import sacrebleu

hypotheses = ["Les chats courent."]
references = [["Les chats courent."]]

bleu = sacrebleu.corpus_bleu(hypotheses, references)
chrf = sacrebleu.corpus_chrf(hypotheses, references)
print(f"BLEU: {bleu.score:.1f}  chrF: {chrf.score:.1f}")
```

Złota zasada: zawsze korzystaj z biblioteki `sacrebleu`. Wprowadza ona ustandaryzowaną tokenizację wewnętrzną, dzięki czemu wyniki są w pełni porównywalne między publikacjami. Samodzielne implementowanie obliczania BLEU prowadzi do nieporównywalnych wyników i zniekształceń w testach benchmarkowych.

### Trzystopniowa hierarchia ewaluacji (stan na 2026 r.)

Współczesna ewaluacja jakości tłumaczenia maszynowego opiera się na trzech uzupełniających się podejściach. Zaleca się stosowanie co najmniej dwóch z nich równolegle:

- **Metryki heurystyczne (BLEU, chrF):** Szybkie, oparte na dopasowaniu znaków i słów do referencji, łatwo interpretowalne, lecz nieodporne na stosowanie synonimów (parafraz). Stosowane do szybkiej weryfikacji i wykrywania regresji.
- **Metryki oparte na modelach neuronowych (COMET, BLEURT, BERTScore):** Wykorzystują modele wyszkolone na ludzkich ocenach jakości tłumaczeń. Oceniają podobieństwo semantyczne między tekstem źródłowym, generowanym i referencyjnym. Model **COMET** wykazuje najwyższy stopień korelacji z ocenami ludzkimi i jest standardem produkcyjnym w 2026 roku.
- **Ewaluacja LLM-as-a-Judge (bez referencji):** Duży model językowy (np. GPT-4) ocenia wygenerowany tekst pod kątem poprawności językowej (płynności), zgodności merytorycznej ze źródłem (adekwatności), tonu wypowiedzi i dopasowania kulturowego. Dobrze zaprojektowany prompt pozwala osiągnąć zgodność ocen z ludzkimi ekspertami na poziomie około 80%. Stosowane przy braku tłumaczeń referencyjnych.

Metryki bezreferencyjne (takie jak COMET-QE, BLEURT-QE czy LLM-as-a-Judge) umożliwiają ocenę tekstu bez dostępu do referencji, co ma kluczowe znaczenie przy rzadkich parach językowych (tzw. low-resource languages), dla których brak gotowych zbiorów testowych.

### Krok 3: Analiza typowych problemów produkcyjnych (tryby awarii)

Opisany potok tłumaczenia będzie działał poprawnie w około 80% przypadków. W pozostałych 20% mogą wystąpić ciche błędy (silent failures). Do najważniejszych należą:

1. **Halucynacje:** Model generuje treści nieobecne w tekście źródłowym. Zjawisko to występuje często przy specyficznym słownictwie dziedzinowym. Objaw: wygenerowany tekst brzmi naturalnie i płynnie, lecz zawiera zmyślone fakty. Zapobieganie: dekodowanie warunkowe z użyciem słowników pojęć kluczowych, weryfikacja ekspercka (human-in-the-loop) dla wrażliwych treści, automatyczne odrzucanie tłumaczeń o długości znacznie wykraczającej poza tekst źródłowy.
2. **Tłumaczenie na niewłaściwy język (off-target generation):** Model generuje poprawny tekst, lecz w innym języku niż zdefiniowany. Modele NLLB wykazują tę podatność przy rzadkich parach językowych. Zapobieganie: upewnij się, że parametr `forced_bos_token_id` jest ustawiony poprawnie, oraz filtruj dane wyjściowe za pomocą klasyfikatora identyfikacji języka (Language ID classifier).
3. **Niespójność terminologiczna:** Np. angielski zwrot „Sign up” w jednym dokumencie zostaje przetłumaczony jako „s'inscrire”, a w innym jako „créer un compte”. W przypadku tekstów interfejsu użytkownika (UI) lub komunikatów systemowych spójność ma kluczowe znaczenie. Zapobieganie: stosowanie słowników terminologicznych w procesie dekodowania warunkowego lub automatyczne zastępowanie fraz po tłumaczeniu.
4. **Niedopasowanie rejestru (grzecznościowego/formalnego):** Np. wybór między zaimkami „ty” (informal) a „Pan/Pani/Państwo” (formal) w języku polskim lub francuskim („tu” vs „vous”). Model domyślnie generuje formy dominujące w zbiorze treningowym, co w komunikacji z klientem bywa błędem. Zapobieganie: dodawanie tagu formalności na początku sekwencji (jeśli model go profesjonalnie obsługuje) lub dostrojenie modelu na korpusie o jednolitym rejestrze językowym.
5. **Eksplozja długości dla krótkich zdań:** Bardzo krótkie teksty wejściowe (np. pojedyncze słowa) bywają tłumaczone jako rozwlekłe frazy z powodu zaburzeń kary za długość dla krótkich sekwencji. Zapobieganie: stosowanie sztywnych ograniczeń na maksymalną długość wyjściową proporcjonalnie do liczby słów wejściowych.

### Krok 4: Adaptacja dziedzinowa (dostrojenie)

Wstępnie wytrenowane modele mają charakter ogólny. Wprowadzenie terminologii prawnej, medycznej czy lokalizacji gier wymaga dostrojenia (fine-tuning) na danych równoległych z danej dziedziny. Schemat uczenia w PyTorch jest następujący:

```python
from transformers import Trainer, TrainingArguments
from datasets import Dataset

pairs = [
    {"src": "The defendant pleaded guilty.", "tgt": "L'accusé a plaidé coupable."},
]

ds = Dataset.from_list(pairs)

def preprocess(ex):
    return tok(
        ex["src"],
        text_target=ex["tgt"],
        truncation=True,
        max_length=128,
        padding="max_length",
    )

ds = ds.map(preprocess, remove_columns=["src", "tgt"])

args = TrainingArguments(output_dir="out", per_device_train_batch_size=4, num_train_epochs=3, learning_rate=3e-5)
Trainer(model=model, args=args, train_dataset=ds).train()
```

Kilka tysięcy precyzyjnie etykietowanych zdań da lepsze rezultaty niż setki tysięcy zaszumionych tekstów pobranych automatycznie z sieci. Czystość i jakość danych treningowych to najważniejsza dźwignia optymalizacji systemów tłumaczenia.

## Rekomendacje doboru technologii MT (stan na 2026 r.)

| Scenariusz | Rekomendacja |
|--------|--------------------------|
| Tłumaczenie wielojęzyczne (200 języków) | `facebook/nllb-200-distilled-600M` (lokalnie/edge) lub `facebook/nllb-200-3.3B` (produkcja) |
| Wysoka jakość dla 50 głównych języków | `facebook/mbart-large-50-many-to-many-mmt` |
| Wydajne, tanie wnioskowanie dla popularnych par językowych | Modele Marian z projektu Helsinki-NLP |
| Tłumaczenie bezpośrednio w przeglądarce użytkownika | Skwantyzowane modele Marian w formacie ONNX (~50 MB) |
| Maksymalna jakość (bez ograniczeń budżetowych i czasowych) | Monity do modeli LLM (GPT-4, Claude, Gemini) |

W 2026 roku duże modele językowe (LLM) często przewyższają dedykowane systemy MT w tłumaczeniu treści idiomatycznych i analizie długiego kontekstu. Wadą są koszty tokenów oraz wyższe opóźnienia. LLM to optymalny wybór, gdy kluczowa jest spójność stylu, obsługa długiego dokumentu w całości lub możliwość sterowania tekstem za pomocą promptów.

## Szablon do wdrożenia

Zapisz go jako `outputs/skill-mt-evaluator.md`:

```markdown
---
name: mt-evaluator
description: Dokonaj ewaluacji modelu tłumaczenia maszynowego przed wdrożeniem produkcyjnym.
version: 1.0.0
phase: 5
lesson: 11
tags: [nlp, translation, evaluation]
---

Jesteś doradcą ds. kontroli jakości systemów tłumaczenia maszynowego (MT). Na podstawie tekstu źródłowego i wygenerowanego tłumaczenia określ:

1. Szacunkowe metryki automatyczne: oczekiwany zakres wartości BLEU oraz chrF (z zaznaczeniem, czy dostępna jest referencja).
2. Pięciopunktową listę weryfikacyjną dla człowieka: (a) zgodność semantyczna (brak halucynacji), (b) poprawny język docelowy, (c) rejestr / poziom formalności języka, (d) zgodność terminologii z dostarczonym słownikiem (glosariuszem), (e) brak sztucznego skrócenia lub eksplozji długości zdania.
3. Jeden kluczowy aspekt dziedzinowy do zbadania (np. dla prawa: nazwy własne i artykuły prawne; dla medycyny: nazwy leków i dawkowanie; dla UI: zachowanie zmiennych szablonu typu `{name}`).
4. Decyzję wdrożeniową: „Wdróż” (Ship) / „Wdróż po weryfikacji” (Ship with review) / „Zablokuj wdrożenie” (Do not ship) powiązana z wagą wykrytych błędów.

Odmów wdrożenia tłumaczenia bez automatycznej weryfikacji identyfikatora języka (Language ID) na wyjściu. Odmów ewaluacji przy braku referencji, chyba że użytkownik jawnie akceptuje metryki bezreferencyjne (np. COMET-QE, BLEURT-QE). Oznacz teksty o długości ponad 1000 tokenów jako wymagające podziału na mniejsze fragmenty przed tłumaczeniem.
```

## Ćwiczenia

1. **Łatwe.** Przetłumacz 5-zdaniowy tekst z angielskiego na francuski i z powrotem na angielski (back-translation) przy użyciu modelu `nllb-200-distilled-600M`. Zmierz stopień zniekształcenia oryginalnego zdania. Zaobserwujesz zachowanie ogólnego sensu przy jednoczesnej zmianie pojedynczych wyrazów.
2. **Średnie.** Zaimplementuj automatyczną weryfikację języka docelowego w wyjściowym tekście z użyciem klasyfikatora `fasttext lid.176` lub biblioteki `langdetect`. Zintegruj to rozwiązanie z potokem tłumaczenia, aby odfiltrowywać tłumaczenia wygenerowane w złym języku przed przekazaniem ich dalej.
3. **Trudne.** Dostrój model `nllb-200-distilled-600M` na dziedzinowym korpusi równoległym o wielkości 5000 par zdań. Zmierz i porównaj wynik BLEU na zbiorze walidacyjnym przed i po treningu. Wykonaj analizę błędów, wskazując, które typy zdań uległy poprawie, a w których jakość uległa pogorszeniu.

## Kluczowe pojęcia

| Pojęcie | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|----------------------|
| BLEU | Wynik tłumaczenia | Metryka oparta na precyzji pokrycia n-gramów słów z nałożeniem kary za zwięzłość. Wartości z przedziału [0, 100]. |
| chrF | Wynik F-score znaków | Metryka F-score obliczana na poziomie n-gramów znakowych. Bardzo czuła na jakość języków o bogatej fleksji. |
| NMT | Neuronowe tłumaczenie maszynowe | Architektura oparta na sieciach neuronowych (głównie Transformer Encoder-Decoder) szkolona na korpusach równoległych. Standard od 2017 r. |
| NLLB | No Language Left Behind | Opracowana przez Meta rodzina zaawansowanych modeli tłumaczenia maszynowego wspierająca ponad 200 języków. |
| Dekodowanie warunkowe | Sterowanie generowaniem | Metoda wymuszania obecności (lub braku) określonych słów lub n-gramów w wyjściowym tekście. |
| Halucynacja | Treści zmyślone | Wygenerowany przez model tekst, który nie znajduje pokrycia w treści wejściowej. |

## Dalsze czytanie

- [Costa-jussà et al. (2022). No Language Left Behind: Scaling Human-Centered Machine Translation](https://arxiv.org/abs/2207.04672) — oficjalny artykuł o architekturze modeli NLLB.
- [Post, M. (2018). A Call for Clarity in Reporting BLEU Scores](https://aclanthology.org/W18-6319/) — wyjaśnienie, dlaczego standard `sacrebleu` jest jedyną wiarygodną metodą raportowania BLEU.
- [Popović, M. (2015). chrF: character n-gram F-score for automatic MT evaluation](https://aclanthology.org/W15-3049/) — oryginalny artykuł opisujący strukturę metryki chrF.
- [Hugging Face Translation Task Guide](https://huggingface.co/docs/transformers/tasks/translation) — praktyczny poradnik krok po kroku dostrajania modeli seq2seq do tłumaczenia.
