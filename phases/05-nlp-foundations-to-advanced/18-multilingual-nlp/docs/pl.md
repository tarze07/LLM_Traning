# Wielojęzyczny NLP

> Jeden model, ponad 100 języków, dla większości z nich zero danych szkoleniowych. Transfer międzyjęzykowy to praktyczny cud lat 2020.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 04 (GloVe, FastText, Subword), Faza 5 · 11 (tłumaczenie maszynowe)
**Czas:** ~45 minut

## Problem

W języku angielskim znajdują się miliardy oznaczonych przykładów. Urdu ma tysiące. Maithili prawie nie ma. Każdy praktyczny system NLP, który służy globalnej publiczności, musi pracować na długim ogonie języków, w przypadku których nie istnieją dane szkoleniowe dotyczące konkretnego zadania.

Modele wielojęzyczne rozwiązują ten problem, ucząc jeden model w wielu językach jednocześnie. Wspólna reprezentacja pozwala modelowi przenieść umiejętności nabyte w językach o dużych zasobach do języków o niskich zasobach. Dopracuj model na podstawie analizy nastrojów w języku angielskim, a otrzymasz zaskakująco dobre przewidywania nastrojów w języku urdu. Jest to bezpośredni transfer międzyjęzykowy, który zmienił sposób, w jaki NLP dociera do świata.

W tej lekcji omówiono kompromisy, modele kanoniczne i jedyną decyzję, która naraża zespoły dopiero rozpoczynające pracę wielojęzyczną: wybór języka źródłowego do przeniesienia.

## Koncepcja

![Transfer międzyjęzykowy poprzez współdzieloną wielojęzyczną przestrzeń do osadzania](../assets/multilingual.svg)

**Wspólne słownictwo.** Modele wielojęzyczne wykorzystują tokenizer SentencePiece lub WordPiece przeszkolony na tekście ze wszystkich języków docelowych. Słownictwo jest wspólne: ta sama jednostka podsłów reprezentuje ten sam morfem w pokrewnych językach. `anti-` w języku angielskim i włoskim otrzymuje ten sam token.

**Wspólna reprezentacja.** Transformator przeszkolony w zakresie modelowania języka maskowanego w wielu językach uczy się, że semantycznie podobne zdania w różnych językach powodują podobne stany ukryte. Wszystkie mBERT, XLM-R i NLLB to wykazują. Osadzanie słowa „cat” w języku angielskim jest skupione w pobliżu słowa „chat” w języku francuskim i „gato” w języku hiszpańskim, podobnie jak osadzanie całych zdań.

**Transfer zerowy.** Dostosuj model na danych oznaczonych etykietami w jednym języku (zwykle angielskim). Podsumowując, uruchom go w dowolnym innym języku obsługiwanym przez model. Nie są potrzebne żadne etykiety w języku docelowym. Wyniki są dobre w przypadku języków pokrewnych typologicznie i słabsze w przypadku języków odległych.

**Kilka poprawek.** Dodaj 100–500 oznaczonych przykładów w języku docelowym. Dokładność skacze do 95-98% podstawowej wersji angielskiej w zadaniach klasyfikacyjnych. Jest to najbardziej opłacalna dźwignia wielojęzycznego NLP.

## Modele

| Modelka | Rok | Zasięg | Notatki |
|-------|------|----------|-------|
| MBERTA | 2018 | 104 języki | Trenowany na Wikipedii. Pierwszy praktyczny wielojęzyczny LM. Słaby przy małych zasobach. |
| XLM-R | 2019 | 100 języków | Przeszkolony na CommonCrawl (znacznie większym niż Wikipedia). Ustawia międzyjęzykową linię bazową. Podstawa 270M, duża 550M. |
| XLM-V | 2023 | 100 języków | XLM-R ze słownikiem tokenów 1M (w porównaniu do 250 tys.). Lepiej na niskich zasobach. |
| mT5 | 2020 | 101 języków | Architektura T5 do generowania wielojęzycznego. |
| NLLB-200 | 2022 | 200 języków | model translacyjny Meta; obejmuje 55 języków o niskich zasobach. |
| ROZkwit | 2022 | 46 języków + 13 programowania | Open 176B LLM przeszkolony wielojęzycznie. |
| Aya-23 | 2024 | 23 języki | Wielojęzyczny LLM Cohere. Mocno zna arabski, hindi, suahili. |

Wybierz według przypadku użycia. Klasyfikacja działa dobrze z bazą XLM-R jako rozsądną wartością domyślną. Zadania generowania wymagają mT5 lub NLLB w zależności od tłumaczenia i generacji otwartej. Praca w parach w stylu LLM z Aya-23 lub Claude przy użyciu wyraźnych wielojęzycznych podpowiedzi.

## Decyzja dotycząca języka źródłowego (badanie z 2026 r.)

Większość zespołów domyślnie wybiera język angielski jako źródło dostrajania. Ostatnie badania (2026 r.) pokazują, że często jest to błędne założenie.

Podobieństwo językowe pozwala lepiej przewidzieć jakość transferu niż surowy rozmiar korpusu. W przypadku celów słowiańskich niemiecki lub rosyjski często przewyższają angielski. W przypadku celów indyjskich język hindi często przewyższa angielski. Wskaźnik podobieństwa **qWALS** (2026, oparty na funkcjach Światowego Atlasu Struktur Językowych) określa to ilościowo. **LANGRANK** (Lin i in., ACL 2019) to osobna, wcześniejsza metoda, która szereguje kandydujące języki źródłowe na podstawie kombinacji podobieństwa językowego, wielkości korpusu i pokrewieństwa genetycznego.

Praktyczna zasada: jeśli Twój język docelowy ma typologicznie bliskiego krewnego o dużych zasobach, spróbuj najpierw dostroić ten język, a następnie porównaj z dostrojeniem angielskim.

## Zbuduj to

### Krok 1: bezproblemowa klasyfikacja międzyjęzykowa

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

Jeden model, trzy języki, to samo API. XLM-R przeszkolony w zakresie transferu danych NLI dobrze radzi sobie z klasyfikacją za pomocą sztuczki implikacyjnej.

### Krok 2: wielojęzyczna przestrzeń do osadzania

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

Tłumaczenia lądują blisko przestrzeni osadzania. Inne zdanie w języku angielskim trafia dalej. To właśnie sprawia, że ​​wyszukiwanie międzyjęzykowe, grupowanie i podobieństwo działa.

### Krok 3: strategia dostrajania obejmująca kilka strzałów

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

W przypadku 100–500 przykładów języków docelowych bezpiecznymi ustawieniami domyślnymi są `num_train_epochs=5` i `learning_rate=2e-5`. Wyższe wskaźniki uczenia się powodują załamanie wielojęzycznego dostosowania i otrzymujesz model wyłącznie w języku angielskim.

## Ocena, która faktycznie działa

- **Dokładność w przeliczeniu na język w wybranych zestawach.** Nie zagregowane. Agregat ukrywa długi ogon.
- **Porównanie z jednojęzycznym punktem odniesienia.** W przypadku języków z wystarczającą ilością danych model jednojęzyczny wytrenowany od podstaw czasami przewyższa model wielojęzyczny. Test.
- **Testy na poziomie jednostki.** Nazwane jednostki w języku docelowym. Modele wielojęzyczne często mają słabą tokenizację w przypadku pism odległych od łaciny.
- **Spójność międzyjęzykowa.** To samo znaczenie w dwóch językach powinno dawać takie same przewidywania. Zmierz szczelinę.

## Użyj tego

Stos na rok 2026:

| Zadanie | Polecane |
|-----|------------|
| Klasyfikacja, 100 języków | Dostrojona baza XLM-R (~270M) |
| Klasyfikacja tekstu zero-shot | `joeddav/xlm-roberta-large-xnli` |
| Wielojęzyczne osadzanie zdań | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Tłumaczenie, 200 języków | `facebook/nllb-200-distilled-600M` (patrz lekcja 11) |
| Generatywny wielojęzyczny | Claude, GPT-4, Aya-23, mT5-XXL |
| Język NLP o niskich zasobach | XLM-V lub dostrojenie specyficzne dla domeny w powiązanym języku o dużych zasobach |

Zawsze budżetuj na dostrojenie języka docelowego, jeśli wydajność ma znaczenie. Zero-shot to punkt wyjścia, a nie ostateczna odpowiedź.

### Podatek tokenizacyjny (co idzie nie tak w przypadku języków o niskich zasobach)

Modele wielojęzyczne mają ten sam tokenizer we wszystkich swoich językach. To słownictwo jest ćwiczone w korpusie zdominowanym przez angielski, francuski, hiszpański, chiński i niemiecki. W przypadku dowolnego języka spoza zestawu dominującego trzy podatki łączą się po cichu:

- **Podatek od płodności.** Tekst w języku o niskich zasobach tokenizuje się w znacznie więcej tokenów na słowo niż w języku angielskim. Zdanie w języku hindi może wymagać 3-5 razy więcej tokenów niż równoważne zdanie w języku angielskim. To 3-5x zjada okno kontekstowe, wydajność treningu i opóźnienia.
- **Podatek zwrotny od wariantu.** Każda literówka, wariant znaków diakrytycznych, niezgodność normalizacji Unicode lub zmiana wielkości liter stają się niepowiązaną sekwencją zimnego startu w przestrzeni osadzania. Model nie jest w stanie nauczyć się zgodności ortograficznej, którą rodzimy użytkownik języka uważa za oczywistą.
- **Podatek od przeniesienia mocy obliczeniowej.** Podatki 1 i 2 zużywają pozycje kontekstu, głębokość warstwy i wymiary osadzania. To, co pozostaje do faktycznego rozumowania, jest systematycznie mniejsze niż to, co język o dużych zasobach otrzymuje z tego samego modelu.

Praktyczny symptom: Twój model normalnie trenuje w języku hindi, krzywa strat wygląda prawidłowo, zakłopotanie w ocenie wydaje się rozsądne, a wyniki produkcyjne są nieznacznie błędne. Morfologia załamuje się w połowie zdania. Rzadkie przegięcia pozostają nie do odzyskania. **Nie możesz skalować danych, aby wyjść z uszkodzonego tokenizera.**

Środki zaradcze: wybierz tokenizer z dobrym pokryciem dla Twojego języka docelowego (słownictwo XLM-V zawierające 1 milion tokenów jest bezpośrednim rozwiązaniem); przed treningiem zweryfikuj płodność tokenizacji na wyciągniętym tekście docelowym; użyj rezerwy na poziomie bajtów (SentencePiece `byte_fallback=True`, BPE na poziomie bajtów w stylu GPT-2) dla naprawdę długich skryptów, więc nic nie jest nigdy OOV.

## Wyślij to

Zapisz jako `outputs/skill-multilingual-picker.md`:

```markdown
---
name: multilingual-picker
description: Pick source language, target model, and evaluation plan for a multilingual NLP task.
version: 1.0.0
phase: 5
lesson: 18
tags: [nlp, multilingual, cross-lingual]
---

Given requirements (target languages, task type, available labeled data per language), output:

1. Source language for fine-tuning. Default English; check LANGRANK or qWALS if target language has a typologically close high-resource language.
2. Base model. XLM-R (classification), mT5 (generation), NLLB (translation), Aya-23 (generative LLM).
3. Few-shot budget. Start with 100-500 target-language examples if available. Zero-shot only if labeling is infeasible.
4. Evaluation plan. Per-language accuracy (not aggregate), cross-lingual consistency, entity-level F1 on non-Latin scripts.

Refuse to ship a multilingual model without per-language evaluation — aggregate metrics hide long-tail failures. Flag scripts with low tokenization coverage (Amharic, Tigrinya, many African languages) as needing a model with byte-fallback (SentencePiece with byte_fallback=True, or byte-level tokenizer like GPT-2).
```

## Ćwiczenia

1. **Łatwe.** Uruchom potok klasyfikacji zero-shot na 10 zdaniach na język w języku angielskim, francuskim, hindi i arabskim. Zgłoś dokładność każdego z nich. Powinieneś zobaczyć mocny francuski, przyzwoity hindi, zmienny arabski.
2. **Średni.** Użyj `paraphrase-multilingual-MiniLM-L12-v2`, aby zbudować międzyjęzycznego retrievera na małym korpusie wielojęzycznym. Zapytaj w języku angielskim, uzyskaj dokumenty w dowolnym języku. Zmierz przypomnienie@5.
3. **Trudne.** Porównaj dostrojenie źródeł angielskich i hindi dla zadania klasyfikacji w języku hindi. Użyj 500 przykładów języków docelowych w celu doprecyzowania kilku strzałów w obu systemach. Zgłoś, które źródło zapewnia lepszą dokładność w języku hindi i o ile. Oto teza LANGRANKA w miniaturze.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Model wielojęzyczny | Jeden model, wiele języków | Wspólne słownictwo i parametry w różnych językach. |
| Transfer międzyjęzykowy | Trenuj w jednym języku, uruchamiaj w innym | Dostosuj źródło, oceń cel bez etykiet w języku docelowym. |
| Zerowy strzał | Brak etykiet języka docelowego | Transfer bez dostrajania języka docelowego. |
| Kilka strzałów | Małe etykiety docelowe | 100-500 przykładów języków docelowych używanych do dostrajania. |
| MBERTA | Pierwszy wielojęzyczny LM | 104-językowy BERT wstępnie przeszkolony w Wikipedii. |
| XLM-R | Standardowa międzyjęzykowa linia bazowa | RoBERTa w 100 językach przeszkolona w CommonCrawl. |
| NLLB | Meta's MT w 200 językach | Żaden język nie pozostał w tyle. Obejmuje 55 języków o niskich zasobach. |

## Dalsze czytanie

- [Conneau i in. (2019). Uczenie się reprezentacji międzyjęzykowej bez nadzoru na dużą skalę](https://arxiv.org/abs/1911.02116) — artykuł XLM-R.
- [Pires, Schlinger, Garrette (2019). Jak wielojęzyczny jest wielojęzyczny BERT?](https://arxiv.org/abs/1906.01502) — artykuł analityczny, który zapoczątkował linię badań nad transferem międzyjęzykowym.
- [Costa-jussà i in. (2022). Żaden język nie pozostał w tyle](https://arxiv.org/abs/2207.04672) — artykuł NLLB-200.
- [Üstün i in. (2024). Model Aya: Dopracowany wielojęzyczny model języka o otwartym dostępie do instrukcji](https://arxiv.org/abs/2402.07827) — Aya, wielojęzyczny LLM firmy Cohere.
- [Language podobieństwo przewiduje wydajność uczenia się w ramach transferu międzyjęzykowego (2026)](https://www.mdpi.com/2504-4990/8/3/65) — dokument dotyczący języka źródłowego qWALS / LANGRANK.