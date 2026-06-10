# Wielojęzyczne przetwarzanie języka naturalnego (Wielojęzyczne NLP)

> Jeden model, ponad 100 języków i brak danych treningowych dla większości z nich. Transfer międzyjęzykowy (cross-lingual transfer) to jeden z najważniejszych przełomów w NLP w latach 20. XXI wieku.

**Typ:** Teoria
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 04 (GloVe, FastText, Tokenizacja podwyrazowa), Faza 5 · 11 (Tłumaczenie maszynowe)
**Czas:** ~45 minut

## Problem

Dla języka angielskiego istnieją miliardy oznaczonych przykładów treningowych. Dla urdu – tysiące. Dla języka maithili nie ma ich prawie wcale. Każdy wdrożony produkcyjnie system NLP o zasięgu globalnym musi obsługiwać tzw. długi ogon języków, dla których nie ma dedykowanych danych treningowych dla konkretnego zadania.

Wielojęzyczne modele językowe rozwiązują to wyzwanie poprzez jednoczesne uczenie na tekstach w wielu językach. Wspólna przestrzeń reprezentacji pozwala modelowi przenieść wiedzę z języków bogatych w zasoby (high-resource) na języki o ograniczonych zasobach (low-resource). Dostrojenie takiego modelu do analizy wydźwięku (sentiment analysis) na danych w języku angielskim pozwala uzyskać zaskakująco dobre wyniki dla języka urdu. Ten bezpośredni transfer międzyjęzykowy (cross-lingual transfer) zrewolucjonizował globalną dostępność technologii językowych.

W tej lekcji omówimy kompromisy projektowe, klasyczne modele oraz kluczową decyzję, na której często potykają się zespoły rozpoczynające pracę z wielojęzycznym NLP: wybór odpowiedniego języka źródłowego do transferu wiedzy.

## Koncepcja

![Transfer międzyjęzykowy poprzez wspólną przestrzeń osadzeń](../assets/multilingual.svg)

**Wspólne słownictwo (Shared vocabulary).** Modele wielojęzyczne wykorzystują tokenizatory SentencePiece lub WordPiece wytrenowane na tekstach we wszystkich docelowych językach. Dzięki temu to samo podsłowo (subword) reprezentuje ten sam morfem w pokrewnych językach – na przykład przedrostek `anti-` w języku angielskim i włoskim otrzyma ten sam token.

**Wspólna reprezentacja (Shared representation).** Transformer trenowany metodą zamaskowanego modelowania języka (masked language modeling) na wielu językach uczy się, że semantycznie zbliżone zdania w różnych językach generują podobne stany ukryte (hidden states). Zjawisko to występuje w modelach mBERT, XLM-R czy NLLB. Wektor osadzenia (embedding) słowa „cat” w języku angielskim znajduje się blisko francuskiego „chat” oraz hiszpańskiego „gato”. Podobna bliskość semantyczna dotyczy reprezentacji całych zdań.

**Zero-shot transfer.** Dostrajamy model na oznaczonych danych w jednym języku (najczęściej angielskim), a następnie wdrażamy go bezpośrednio do obsługi innych języków. Nie potrzebujemy żadnych oznaczonych danych w języku docelowym. Wyniki są zazwyczaj bardzo dobre dla języków o podobnej typologii i słabsze dla języków odległych lingwistycznie.

**Few-shot finetuning (Dostrojenie nielicznych przykładów).** Dodanie zaledwie 100–500 oznaczonych przykładów w języku docelowym pozwala podnieść jakość klasyfikacji do poziomu 95–98% wyniku uzyskiwanego dla języka angielskiego. To najbardziej opłacalny sposób na optymalizację wielojęzycznych systemów NLP.

## Modele

| Model | Rok | Zasięg | Uwagi |
|-------|------|----------|-------|
| mBERT | 2018 | 104 języki | Trenowany na Wikipedii. Pierwszy praktyczny wielojęzyczny model językowy. Słabe wyniki dla języków o niskich zasobach. |
| XLM-R | 2019 | 100 języków | Trenowany na zbiorze CommonCrawl (znacznie większym niż Wikipedia). Wyznacza standard bazowy (baseline) dla transferu międzyjęzykowego. Dostępne wersje: base (270M) i large (550M). |
| XLM-V | 2023 | 100 języków | Wersja XLM-R ze słownikiem powiększonym do 1 miliona tokenów (w porównaniu do 250 tys. w XLM-R). Daje znacznie lepsze wyniki dla języków o niskich zasobach. |
| mT5 | 2020 | 101 języków | Wielojęzyczna wersja architektury T5 przeznaczona do zadań generatywnych. |
| NLLB-200 | 2022 | 200 języków | Model tłumaczeniowy od Meta; obsługuje 200 języków, w tym 55 o bardzo niskich zasobach. |
| BLOOM | 2022 | 46 języków + 13 progr. | Otwarty model LLM o rozmiarze 176B parametrów, trenowany wielojęzycznie. |
| Aya-23 | 2024 | 23 języki | Wielojęzyczny LLM od Cohere. Bardzo dobre wsparcie m.in. dla języka arabskiego, hindi i suahili. |

Wybór modelu zależy od zastosowania. Do klasyfikacji tekstu optymalnym i sprawdzonym punktem wyjścia jest model XLM-R. Zadania generatywne wymagają użycia modeli mT5 lub NLLB (dla tłumaczeń) bądź zaawansowanych modeli LLM, takich jak Aya-23 lub Claude, sterowanych za pomocą precyzyjnych promptów wielojęzycznych.

## Wybór języka źródłowego (stan wiedzy na rok 2026)

Większość inżynierów domyślnie wybiera język angielski jako bazę (źródło) do dostrajania modeli. Badania pokazują jednak, że nie zawsze jest to najlepsze rozwiązanie.

Podobieństwo typologiczne pozwala znacznie lepiej przewidzieć skuteczność transferu niż sam rozmiar korpusu treningowego. Przykładowo, przy transferze na języki słowiańskie jako źródło lepiej sprawdzi się język niemiecki lub rosyjski niż angielski. W przypadku języków indyjskich hindi daje lepsze rezultaty niż angielski. Metoda **qWALS** (oparta na bazach World Atlas of Language Structures) pozwala ilościowo ocenić to podobieństwo. Z kolei algorytm **LANGRANK** (Lin et al., ACL 2019) umożliwia uszeregowanie potencjalnych języków źródłowych na podstawie kombinacji podobieństwa typologicznego, rozmiaru korpusu oraz pokrewieństwa genetycznego.

**Złota zasada:** Jeśli Twój język docelowy ma bliskiego krewnika o bogatych zasobach (np. hiszpański dla katalońskiego), spróbuj w pierwszej kolejności dostroić model na danych z tego pokrewnego języka i porównaj wyniki z podejściem opartym na języku angielskim.

## Zbuduj to

### Krok 1: Zero-shot klasyfikacja międzyjęzykowa

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tok = AutoTokenizer.from_pretrained("joeddav/xlm-roberta-large-xnli")
model = AutoModelForSequenceClassification.from_pretrained("joeddav/xlm-roberta-large-xnli")

def classify(text, candidate_labels, hypothesis_template="This text is about {}."):
    scores = {}
    for label in candidate_labels:
        hypothesis = hypothesis_template.format(label)
        inputs = tok(text, hypothesis, return_tensors="pt", truncation=True)
        with torch.no_grad():
            logits = model(**inputs).logits[0]
        entail_score = torch.softmax(logits, dim=-1)[2].item()
        scores[label] = entail_score
    return dict(sorted(scores.items(), key=lambda x: -x[1]))

print(classify("I love this product!", ["positive", "negative", "neutral"]))
print(classify("मुझे यह उत्पाद पसंद है!", ["positive", "negative", "neutral"]))
print(classify("J'adore ce produit !", ["positive", "negative", "neutral"]))
```

Jeden model obsługuje trzy różne języki za pomocą tego samego interfejsu API. Model XLM-R dostrojonony do zadania wnioskowania naturalnego (NLI) doskonale radzi sobie z klasyfikacją metodą weryfikacji implikacji (entailment).

### Krok 2: Wielojęzyczna przestrzeń osadzeń (embeddings)

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

pairs = [
    ("The cat is sleeping.", "Le chat dort."),
    ("The cat is sleeping.", "El gato está durmiendo."),
    ("The cat is sleeping.", "Die Katze schläft."),
    ("The cat is sleeping.", "The dog is barking."),
]

for eng, other in pairs:
    emb_eng = model.encode([eng], normalize_embeddings=True)[0]
    emb_other = model.encode([other], normalize_embeddings=True)[0]
    sim = float(np.dot(emb_eng, emb_other))
    print(f"  {eng!r} <-> {other!r}: cos={sim:.3f}")
```

Zdania będące swoimi tłumaczeniami lądują bardzo blisko siebie we wspólnej przestrzeni osadzeń, podczas gdy zdania o innym znaczeniu w tym samym języku znajdują się znacznie dalej. To zjawisko umożliwia wyszukiwanie międzyjęzykowe, grupowanie (clustering) oraz badanie podobieństwa semantycznego.

### Krok 3: Dydaktyczny szablon dostrajania few-shot

```python
from transformers import TrainingArguments, Trainer
from datasets import Dataset

def few_shot_finetune(base_model, base_tokenizer, examples):
    ds = Dataset.from_list(examples)

    def tokenize_fn(ex):
        out = base_tokenizer(ex["text"], truncation=True, max_length=128)
        out["labels"] = ex["label"]
        return out

    ds = ds.map(tokenize_fn)
    args = TrainingArguments(
        output_dir="out",
        per_device_train_batch_size=8,
        num_train_epochs=5,
        learning_rate=2e-5,
        save_strategy="no",
    )
    trainer = Trainer(model=base_model, args=args, train_dataset=ds)
    trainer.train()
    return base_model
```

Przy małej próbie (100–500 przykładów w języku docelowym) zaleca się bezpieczne parametry: `num_train_epochs=5` oraz współczynnik uczenia `learning_rate=2e-5`. Zbyt agresywne tempo uczenia się (learning rate) prowadzi do zjawiska zapominania cech wielojęzycznych (catastrophic forgetting), przez co model zaczyna dobrze obsługiwać tylko jeden język.

## Metodologia ewaluacji w praktyce

- **Ewaluacja per-language na wydzielonych zbiorach testowych.** Unikaj analizowania wyłącznie metryk zagregowanych, gdyż maskują one słabe wyniki dla języków z długiego ogona.
- **Porównanie z modelami jednojęzycznymi (monolingual baselines).** W przypadku języków dysponujących przyzwoitymi zasobami model jednojęzyczny wyszkolony od zera może przewyższać model wielojęzyczny. Należy to bezwzględnie zweryfikować empirycznie.
- **Testy jednostkowe dla specyficznych struktur językowych (np. nazwy własne w pismach niełacińskich).** Modele wielojęzyczne często charakteryzują się bardzo słabą jakością tokenizacji dla alfabetów innych niż łaciński.
- **Spójność międzyjęzykowa (Cross-lingual consistency).** Zdania o identycznym znaczeniu w różnych językach powinny generować zbieżne predykcje. Monitoruj różnice w wynikach.

## Rekomendowane biblioteki i modele

| Zadanie | Polecane rozwiązanie |
|-----|------------|
| Klasyfikacja tekstu (100+ języków) | Dostrojony model XLM-R base (~270M parametrów) lub large |
| Klasyfikacja zero-shot | `joeddav/xlm-roberta-large-xnli` |
| Międzyjęzykowe osadzanie zdań | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Tłumaczenie maszynowe (200 języków) | `facebook/nllb-200-distilled-600M` |
| Generowanie tekstu i zadania czatowe | Claude, GPT-4, Aya-23, mT5-XXL |
| Języki o bardzo niskich zasobach | XLM-V lub dostrajanie dziedzinowe na powiązanym języku o bogatych zasobach |

Zawsze planuj budżet na dostrojenie modelu do docelowego języka (target language fine-tuning), jeśli jakość ma kluczowe znaczenie. Podejście zero-shot to punkt startowy, a nie docelowy system produkcyjny.

### Podatek tokenizacyjny (Tokenization Tax)

Wielojęzyczne modele współdzielą jeden tokenizator dla wszystkich języków. Słownik tokenizatora powstaje w oparciu o dane zdominowane przez języki takie jak angielski, francuski, hiszpański, chiński i niemiecki. W przypadku języków spoza tej grupy, inżynierowie zderzają się z potrójnym „podatkiem”::

- **Podatek od płodności (Fertility rate tax):** Słowa w językach o niskich zasobach są dzielone na znacznie krótsze fragmenty, co drastycznie zwiększa liczbę tokenów przypadających na słowo. Zdanie w języku hindi po tokenizacji może mieć 3-5 razy więcej tokenów niż jego angielski odpowiednik. Skraca to efektywne okno kontekstowe modelu, podnosi koszt treningu oraz zwiększa opóźnienia (latency).
- **Podatek od wariantów zapisu:** Wszelkie literówki, różnice w znakach diakrytycznych, błędy w normalizacji Unicode czy wielkości znaków tworzą osobne tokeny o niskiej częstości występowania. Model ma trudności z powiązaniem ich semantyki, co utrudnia naukę podstawowych zależności ortograficznych.
- **Podatek od alokacji pojemności modelu:** Nadmierna liczba tokenów i ich niska spójność konsumują cenne zasoby modelu (pozycje kontekstu, wymiary osadzeń, pojemność warstw uwagi). W efekcie model ma mniejsze możliwości „rozumowania” w językach o niskich zasobach niż w językach dominujących.

Typowy objaw: model uczy się poprawnie, strata (loss) maleje, perpleksja na zbiorze walidacyjnym wygląda dobrze, jednak wyniki produkcyjne są nie do zaakceptowania. Morfologia słów załamuje się, a rzadkie formy gramatyczne są generowane błędnie. **Zwiększanie ilości danych nie rozwiąże problemu wadliwego tokenizatora.**

Środki zaradcze: Wybierz model z tokenizatorem o lepszym pokryciu Twojego języka (np. słownik XLM-V o rozmiarze 1M tokenów); zweryfikuj wskaźnik płodności tokenizacji (tokens-to-words ratio) przed rozpoczęciem uczenia; upewnij się, że tokenizator posiada obsługę bajtów awaryjnych (SentencePiece z `byte_fallback=True` lub tokenizatory bajtowe w stylu BPE z GPT-2), dzięki czemu model nie wygeneruje błędów OOV (Out-of-Vocabulary).

## Zapisywanie szablonu

Zapisz jako `outputs/skill-multilingual-picker.md`:

```markdown
---
name: multilingual-picker
description: Wybierz język źródłowy, model bazowy oraz plan ewaluacji dla wielojęzycznego zadania NLP.
version: 1.0.0
phase: 5
lesson: 18
tags: [nlp, multilingual, cross-lingual]
---

Na podstawie wymagań (języki docelowe, typ zadania, dostępne oznaczone dane dla każdego języka) wygeneruj:

1. Język źródłowy do dostrojenia: Domyślnie angielski; sprawdź LANGRANK lub qWALS, jeśli język docelowy posiada bliskiego typologicznie krewniaka o bogatych zasobach.
2. Model bazowy: XLM-R (klasyfikacja), mT5 (generowanie), NLLB (tłumaczenie), Aya-23 (model LLM).
3. Budżet few-shot: Użyj 100–500 przykładów z języka docelowego, jeśli są dostępne. Podejście zero-shot stosuj wyłącznie, gdy etykietowanie jest niemożliwe.
4. Plan ewaluacji: Dokładność dla każdego języka osobno (unikaj metryk zagregowanych), spójność międzyjęzykowa, miara F1 dla nazw własnych w alfabetach niełacińskich.

Nigdy nie wdrażaj modelu wielojęzycznego bez przeprowadzenia ewaluacji dla każdego języka osobno – metryki zagregowane maskują błędy w mniej popularnych językach. Oznaczaj języki o słabym pokryciu tokenizatora (np. amharski, tigrinia, wiele języków afrykańskich) jako wymagające tokenizatora z obsługą bajtów awaryjnych (byte-fallback) lub tokenizacji na poziomie bajtów.
```

## Ćwiczenia praktyczne

1. **Poziom łatwy:** Uruchom potok klasyfikacji zero-shot dla 10 zdań w językach: angielskim, francuskim, hindi i arabskim. Porównaj uzyskaną dokładność. Powinieneś zaobserwować wysokie wyniki dla francuskiego, zadowalające dla hindi i zmienne dla arabskiego.
2. **Poziom średni:** Wykorzystaj model `paraphrase-multilingual-MiniLM-L12-v2` do budowy międzyjęzykowego systemu wyszukiwania (retriever) na małym korpusie wielojęzycznym. Zadaj pytanie w języku angielskim i wyszukaj dokumenty w innych językach. Zmierz wartość metryki Recall@5.
3. **Poziom trudny:** Porównaj efektywność transferu z języka angielskiego i hindi do zadania klasyfikacji w języku hindi. Zastosuj dostrajanie few-shot przy użyciu 500 przykładów z języka docelowego w obu wariantach. Sprawdź, który język źródłowy zapewnia wyższą dokładność i jaka jest różnica. To ćwiczenie w praktyce ilustruje założenia stojące za algorytmem LANGRANK.

## Kluczowe pojęcia

| Termin | Potoczne określenie | Znaczenie precyzyjne |
|------|-----------------|----------------------|
| Model wielojęzyczny (Multilingual LM) | Jeden model, wiele języków | Model ze wspólnymi parametrami i słownikiem współdzielonym przez wiele języków. |
| Transfer międzyjęzykowy (Cross-lingual transfer) | Trenuj w jednym języku, uruchamiaj w innym | Dostrajanie modelu na danych w języku źródłowym i ewaluacja na języku docelowym bez użycia tamtejszych etykiet. |
| Zero-shot | Brak etykiet języka docelowego | Transfer wiedzy bez dostrajania do specyfiki języka docelowego. |
| Few-shot | Nieliczne przykłady | Zastosowanie małej liczby przykładów (np. 100–500) z języka docelowego do precyzyjnego dostrojenia. |
| mBERT | Pierwszy wielojęzyczny LM | Wielojęzyczny wariant modelu BERT obsługujący 104 języki, trenowany na Wikipedii. |
| XLM-R | Standardowa międzyjęzykowa linia bazowa | Model RoBERTa trenowany na 100 językach ze zbioru CommonCrawl; klasyczny baseline. |
| NLLB | Meta's MT w 200 językach | Model tłumaczeniowy od Meta (No Language Left Behind), obsługujący 200 języków, w tym 55 o niskich zasobach. |

## Literatura uzupełniająca

- [Conneau et al. (2019). Unsupervised Cross-lingual Representation Learning at Scale](https://arxiv.org/abs/1911.02116) — publikacja wprowadzająca model XLM-R.
- [Pires, Schlinger, Garrette (2019). How Multilingual is Multilingual BERT?](https://arxiv.org/abs/1906.01502) — analiza zdolności transferowych modelu mBERT.
- [Costa-jussà et al. (2022). No Language Left Behind: Translation for 200+ languages](https://arxiv.org/abs/2207.04672) — dokumentacja projektu NLLB-200.
- [Üstün et al. (2024). Aya Model: An Instruction Finetuned Open-Access Multilingual Language Model](https://arxiv.org/abs/2402.07827) — publikacja dotycząca modelu Aya firmy Cohere.
- [Language similarity predicts transfer learning performance in cross-lingual tasks (2026)](https://www.mdpi.com/2504-4990/8/3/65) — publikacja dotycząca optymalizacji wyboru języka źródłowego (qWALS / LANGRANK).
