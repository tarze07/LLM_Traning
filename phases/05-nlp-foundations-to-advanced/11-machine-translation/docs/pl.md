# Tłumaczenie maszynowe

> Tłumaczenie to zadanie, które opłacało badania nad NLP przez trzydzieści lat i opłaca się nadal.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 10 (mechanizm uwagi), Faza 5 · 04 (GloVe, FastText, Subword)
**Czas:** ~75 minut

## Problem

Model czyta zdanie w jednym języku i tworzy zdanie w innym. Długość jest różna. Kolejność słów jest różna. Niektóre słowa źródłowe odpowiadają wielu słowom docelowym i odwrotnie. Idiomy odrzucają mapowanie jeden do jednego. „Tęsknię za tobą” po francusku to „tu me manques” – dosłownie „brakuje mi ciebie”. Żadne wyrównanie na poziomie słów nie jest w stanie tego przetrwać.

Tłumaczenie maszynowe to zadanie, które zmusiło NLP do wynalezienia koderów-dekoderów, uwagi, transformatorów i ostatecznie całego paradygmatu LLM. Każdy krok naprzód był osiągany, ponieważ jakość tłumaczeń była mierzalna, a przepaść między człowiekiem a maszyną była uparta.

Ta lekcja pomija lekcję historii i przedstawia plan działania na rok 2026: wstępnie wyszkolony wielojęzyczny koder-dekoder (NLLB-200 lub mBART), tokenizacja podsłów, wyszukiwanie wiązki, ocena BLEU i chrF oraz kilka trybów awarii, które wciąż są wysyłane do produkcji w stanie niezauważonym.

## Koncepcja

![Potok MT: tokenizuj → koduj → dekoduj z uwagą → detokenizuj](../assets/mt-pipeline.svg)

Modern MT to enkoder-dekoder transformatorowy przeszkolony na tekście równoległym. Koder odczytuje źródło w tokenizacji swojego języka. Dekoder generuje cel, jedno podsłowo na raz, korzystając z sygnału wyjściowego kodera w drodze wzajemnej uwagi (lekcja 10). Dekodowanie wykorzystuje przeszukiwanie wiązki, aby uniknąć pułapki zachłannego dekodowania. Dane wyjściowe są poddawane detokenizacji, detruecase'owi i oceniane w oparciu o referencję.

Trzy możliwości operacyjne wpływają na rzeczywistą jakość MT.

- **Tokenizer.** SentencePiece BPE przeszkolony w korpusie wielojęzycznym. Wspólne słownictwo w różnych językach umożliwia tworzenie par zerowych w NLLB.
- **Rozmiar modelu.** NLLB-200 destylowany 600M pasuje do laptopa. NLLB-200 3.3B to opublikowana wersja domyślna produkcyjna. 54,5B to pułap badawczy.
- **Dekodowanie.** Szerokość wiązki 4-5 dla treści ogólnych. Kara za długość, aby uniknąć zbyt krótkich wyników. Ograniczone dekodowanie, gdy potrzebujesz spójności terminologii.

## Zbuduj to

### Krok 1: wstępnie wytrenowane wywołanie MT

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

Liczą się tutaj trzy rzeczy. `src_lang` informuje tokenizator, jaki skrypt i segmentację ma zastosować. `forced_bos_token_id` informuje dekoder, który język ma wygenerować. Obie są sztuczkami specyficznymi dla NLLB; mBART i M2M-100 korzystają z własnych konwencji i nie można ich stosować zamiennie.

### Krok 2: BLEU i chrF

BLEU mierzy n-gramowe nakładanie się sygnału wyjściowego i odniesienia. Cztery referencyjne wielkości n-gramowe (1-4), średnia geometryczna precyzji, kara za zwięzłość w przypadku zbyt krótkich wyników. Wynik jest w [0, 100]. Powszechnie używane. Frustrująca interpretacja: 30 BLEU jest „użyteczne”; 40 to „dobrze”; 50 jest „wyjątkowe”; różnice poniżej 1 BLEU to szum.

chrF mierzy wynik F na poziomie postaci. Bardziej wrażliwy na języki bogate morfologicznie, w których BLEU zaniża dopasowania. Często zgłaszane razem z BLEU.

```python
import sacrebleu

hypotheses = ["Les chats courent."]
references = [["Les chats courent."]]

bleu = sacrebleu.corpus_bleu(hypotheses, references)
chrf = sacrebleu.corpus_chrf(hypotheses, references)
print(f"BLEU: {bleu.score:.1f}  chrF: {chrf.score:.1f}")
```

Zawsze używaj `sacrebleu`. Normalizuje tokenizację, dzięki czemu wyniki są porównywalne w różnych dokumentach. Przeprowadzanie własnych obliczeń BLEU to sposób, w jaki wprowadzają w błąd testy porównawcze.

### Trójstopniowa hierarchia ocen (2026)

Współczesna ocena MT wykorzystuje trzy uzupełniające się rodziny metryk. Wysyłka z co najmniej dwoma.

- **Heurystyka** (BLEU, chrF). Szybki, oparty na odniesieniach, możliwy do zinterpretowania, niewrażliwy na parafrazę. Służy do porównywania starszych wersji i wykrywania regresji.
- **Nauczony** (COMET, BLEURT, BERTScore). Modele neuronowe wytrenowane na podstawie ludzkiej oceny; porównać semantyczne podobieństwo tłumaczenia do źródła i odniesienia. COMET ma najwyższy poziom powiązania z badaniami MT od 2023 r. i jest domyślnym producentem w 2026 r., gdy jakość ma znaczenie.
- **LLM-as-sędzia** (bez referencji). Poproś duży model o ocenę tłumaczeń pod względem płynności, adekwatności, tonu i stosowności kulturowej. GPT-4-as-sędzia odpowiada ludzkiej zgodzie w ~80% przypadków, gdy rubryka jest dobrze zaprojektowana. Stosuj w przypadku treści otwartych, gdzie nie ma odniesienia.

Praktyczny stos 2026: `sacrebleu` dla BLEU i chrF, `unbabel-comet` dla COMET oraz LLM z podpowiedzią dla końcowego sygnału skierowanego w stronę człowieka. Skalibruj każdą metrykę na podstawie 50–100 przykładów oznaczonych przez ludzi, zanim zaufasz jej danym produkcyjnym.

Wskaźniki bezodniesieniowe (COMET-QE, BLEURT-QE, LLM-as-judge) umożliwiają ocenę tłumaczeń bez odniesienia, co ma znaczenie w przypadku par językowych z długim ogonem, w przypadku których nie istnieją tłumaczenia referencyjne.

### Krok 3: co psuje się w produkcji

Powyższy działający potok będzie tłumaczył płynnie w 80% przypadków, a w pozostałych 20% nie powiedzie się cicho. Nazwane tryby awarii:

- **Halucynacja.** Modelka wymyśla treści, których nie było w źródle. Powszechne w nieznanym słownictwie dziedzinowym. Symptom: sygnał wyjściowy jest płynny, ale zawiera fakty, których źródło nie podało. Łagodzenie: ograniczone dekodowanie terminów domeny, weryfikacja treści regulowanych przez człowieka, monitorowanie wyników znacznie dłużej niż danych wejściowych.
- **Generacja poza docelową.** Model został przetłumaczony na niewłaściwy język. NLLB jest zaskakująco podatny na to w przypadku rzadkich par językowych. Środki zaradcze: sprawdź `forced_bos_token_id` i zawsze dekoduj, sprawdzając model identyfikatora języka na wyjściu.
- **Zmiana terminologii.** „Zarejestruj się” zmienia się na „s'inscrire” w dokumencie 1 i „créer un compte” w dokumencie 2. W przypadku tekstu interfejsu użytkownika i ciągów znaków widocznych dla użytkownika spójność ma większe znaczenie niż surowa jakość. Środki zaradcze: dekodowanie ograniczone do glosariusza lub słownik po edycji.
- **Niedopasowanie formalne.** Francuskie „tu” kontra „vous”, japońskie poziomy uprzejmości. Model wybiera tę formę, która była bardziej popularna podczas treningu. W przypadku treści skierowanych do klienta jest to zwykle błędne podejście. Łagodzenie: przedrostek monitu z tokenem formalności, jeśli model go obsługuje, lub dostrojenie małego modelu w korpusach wyłącznie formalnych.
- **Eksplozja długości przy krótkich wpisach.** Bardzo krótkie zdania wejściowe często powodują powstanie zbyt długich tłumaczeń, ponieważ kara za długość spada poniżej ~5 tokenów źródłowych. Ograniczenie: twarde ograniczenie maksymalnej długości proporcjonalne do długości źródła.

### Krok 4: dostrojenie domeny

Modele wstępnie wyszkolone są modelami generalizującymi. Tłumaczenie prawne, medyczne lub dialogi z gier przynosi wymierne korzyści dzięki dostrojeniu danych równoległych domeny. Przepis nie jest egzotyczny:

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

Kilka tysięcy wysokiej jakości przykładów równoległych pokonuje kilkaset tysięcy hałaśliwych przykładów pochodzących z sieci. Jakość danych szkoleniowych jest największą pojedynczą dźwignią produkcyjną.

## Użyj tego

Stos produkcyjny MT na rok 2026:

| Przypadek użycia | Zalecany punkt wyjścia |
|--------|--------------------------|
| Każdy z każdym, 200 języków | `facebook/nllb-200-distilled-600M` (laptop) lub `nllb-200-3.3B` (produkcja) |
| Anglojęzyczny, wysoka jakość, 50 języków | `facebook/mbart-large-50-many-to-many-mmt` |
| Krótkie serie, tanie wnioskowanie, angielski-francuski/niemiecki/hiszpański | Helsinki-NLP / Modele Mariana |
| Po stronie przeglądarki krytycznej dla opóźnień | Kwantyzowany ONNX Marian (~50 MB) |
| Maksymalna jakość, gotowi zapłacić | GPT-4 / Claude / Gemini z podpowiedziami do tłumaczenia |

Od 2026 r. LLM przewyższają obecnie wyspecjalizowane modele MT w kilku parach językowych, szczególnie pod względem treści idiomatycznych i długiego kontekstu. Kompromisem jest koszt tokenu i opóźnienie. Wybierz LLM, gdy długość kontekstu, spójność stylistyczna lub dostosowanie domeny poprzez podpowiedzi są ważniejsze niż przepustowość.

## Wyślij to

Zapisz jako `outputs/skill-mt-evaluator.md`:

```markdown
---
name: mt-evaluator
description: Evaluate a machine translation output for shipping.
version: 1.0.0
phase: 5
lesson: 11
tags: [nlp, translation, evaluation]
---

Given a source text and a candidate translation, output:

1. Automatic score estimate. BLEU and chrF ranges you would expect. State whether a reference is available.
2. Five-point human-verifiable check list: (a) content preservation (no hallucinations), (b) correct language, (c) register / formality match, (d) terminology consistency with glossary if provided, (e) no truncation or length explosion.
3. One domain-specific issue to probe. E.g., for legal: named entities and statute citations. For medical: drug names and dosages. For UI: placeholder variables `{name}`.
4. Confidence flag. "Ship" / "Ship with review" / "Do not ship". Tie to the severity of issues found in step 2.

Refuse to ship a translation without a language-ID check on output. Refuse to evaluate without a reference unless the user explicitly opts in to reference-free scoring (COMET-QE, BLEURT-QE). Flag any content over 1000 tokens as likely needing chunked translation.
```

## Ćwiczenia

1. **Łatwe.** Przetłumacz 5-zdaniowy akapit w języku angielskim na francuski i z powrotem na angielski, używając `nllb-200-distilled-600M`. Zmierz, jak blisko oryginału jest podróż w obie strony. Powinieneś zobaczyć zachowanie semantyki z dryfem w wyborze słowa.
2. **Średni.** Zaimplementuj sprawdzanie identyfikatora języka w wynikach tłumaczeń za pomocą `fasttext lid.176` lub `langdetect`. Zintegruj się z wezwaniem MT, aby pokolenia spoza grupy docelowej zostały złapane przed powrotem.
3. **Trudne.** Dostosuj `nllb-200-distilled-600M` w wybranym korpusie domen składającym się z 5000 par. Zmierz BLEU na wyciągniętym zestawie przed i po dostrojeniu. Oceń, które rodzaje zdań uległy poprawie, a które uległy regresji.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| NIEBIESKI | Wynik tłumaczenia | Precyzja w N-gramach z karą za zwięzłość. [0, 100]. |
| chrF | Wynik F postaci | Wynik F na poziomie postaci. Bardziej wrażliwy na języki bogate morfologicznie. |
| NMT | Neuronowy MT | Koder-dekoder transformatorowy przeszkolony na tekście równoległym. Wartość domyślna 2017+. |
| NLLB | Żaden język nie pozostał w tyle | Rodzina modeli MT firmy Meta z 200 językami. |
| Ograniczone dekodowanie | Kontrolowane wyjście | Wymuś pojawienie się/niepojawienie się określonych tokenów lub n-gramów na wyjściu. |
| Halucynacja | Wymyślona treść | Dane wyjściowe modelu, które nie są obsługiwane przez źródło. |

## Dalsze czytanie

- [Costa-jussà i in. (2022). No Language Left Behind: skalowanie tłumaczenia maszynowego skoncentrowanego na człowieku](https://arxiv.org/abs/2207.04672) – artykuł NLLB.
- [Post (2018). Apel o przejrzystość w zgłaszaniu wyników BLEU](https://aclanthology.org/W18-6319/) – dlaczego `sacrebleu` to jedyny prawidłowy sposób zgłaszania BLEU.
- [Popović (2015). chrF: znak n-gram F-score do automatycznej oceny MT](https://aclanthology.org/W15-3049/) — artykuł chrF.
- [Przewodnik po Hugging Face MT](https://huggingface.co/docs/transformers/tasks/translation) — praktyczny przewodnik po dostrajaniu.