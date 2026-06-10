# Rezolucja dotycząca odniesienia

> „Zadzwoniła do niego. Nie odebrał. Lekarz był na obiedzie.” Trzy odniesienia do dwóch osób i nikt nie jest wymieniony. Rezolucja Coreference określa, kto jest kim.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 06 (NER), Faza 5 · 07 (POS i parsowanie)
**Czas:** ~60 minut

## Problem

Wyodrębnij każdą wzmiankę o Apple Inc. z artykułu składającego się z 300 słów. Łatwe, gdy w artykule jest napisane „Apple”. Trudno, gdy jest napisane „firma”, „oni”, „gigant technologiczny z Cupertino” lub „firma Jobsa”. Bez przypisania tych wzmianek temu samemu podmiotowi potok NER pomija 60–80% wzmianek.

Rozdzielczość współodniesień łączy każde wyrażenie odnoszące się do tej samej jednostki świata rzeczywistego w jeden klaster. Jest spoiwem pomiędzy NLP na poziomie powierzchniowym (NER, parsowanie) a semantyką dalszą (IE, QA, podsumowanie, KG).

Dlaczego to ma znaczenie w 2026 roku:

- Podsumowanie: „Dyrektor generalny ogłosił…” vs „Tim Cook ogłosił…” — w podsumowaniu należy wymienić dyrektora generalnego.
- Odpowiedź na pytanie: „Do kogo dzwoniła?” wymaga rozwiązania „ona”.
- Ekstrakcja informacji: wykres wiedzy, w którym „PER1 założył Apple” i „Jobs założył Apple” jako osobne wpisy, jest błędny.
- IE wielodokumentowe: łączenie wzmianek w artykułach dotyczących tego samego wydarzenia to korelacja między dokumentami.

## Koncepcja

![Grupowanie koreferencji: wzmianki → podmioty](../assets/coref.svg)

**Zadanie.** Wejście: dokument. Wynik: skupienie wzmianek (zakresów), gdzie każdy klaster odnosi się do jednego podmiotu.

**Typy wzmianek.**

- **Wymieniony podmiot.** „Tim Cook”
- **Nominalna.** „dyrektor generalny”, „firma”
- **Zaimkowy.** „on”, „ona”, „oni”, „to”
- **Pozytywny.** „Tim Cook, dyrektor generalny Apple”

**Architektury.**

1. **Oparte na regułach (Hobbs, 1978).** Rozwiązywanie zaimków na podstawie drzewa syntaktycznego przy użyciu reguł gramatycznych. Dobra baza. Zaskakująco trudno pokonać zaimki.
2. **Klasyfikator par wzmianek.** Dla każdej pary wzmianek (m_i, m_j) oceń, czy odnoszą się one do korelacji. Klaster przez domknięcie przechodnie. Standard sprzed 2016 r.
3. **Ranking wzmianek.** Dla każdej wzmianki należy uszeregować kandydatów na poprzedników (w tym „brak poprzednika”). Wybierz górę.
4. **Kompleksowo oparty na zakresie zakresu (Lee i in., 2017).** Enkoder transformatorowy. Wylicz wszystkie rozpiętości kandydujące aż do ograniczenia długości. Przewiduj wyniki wzmianek. Przewiduj prawdopodobieństwo poprzednika dla każdego zakresu. Gromadź się łapczywie. Nowoczesne ustawienie domyślne.
5. **Generatywny (2024+).** Podpowiedz LLM: „Wymień każdy zaimek w tym tekście i jego poprzednik”. Dobrze sprawdza się w łatwych przypadkach, przy długich dokumentach i rzadkich referencjach.

**Metryki oceny.** Pięć standardowych metryk (MUC, B³, CEAF, BLANC, LEA), ponieważ żadna pojedyncza metryka nie odzwierciedla jakości klastrów. Podaj średnią z pierwszych trzech jako CoNLL F1. Najnowocześniejszy w 2026 r. na CoNLL-2012: ~83 F1.

**Znane trudne przypadki.**

- Dokładne opisy odnoszące się do podmiotów wprowadzonych wcześniej na stronach.
- Anafora pomostowa („koła” → wspomniany wcześniej samochód).
- Zero anafory w językach takich jak chiński i japoński.
- Cataphora (zaimek przed desygnatem): „Kiedy **ona** weszła, Mary uśmiechnęła się”.

## Zbuduj to

### Krok 1: wstępnie wyszkolona koreferencja neuronowa (AllenNLP / spaCy-eksperymentalna)

```python
import spacy
nlp = spacy.load("en_coreference_web_trf")   # experimental model
doc = nlp("Apple announced new products. The company said they would ship soon.")
for cluster in doc._.coref_clusters:
    print(cluster, "->", [m.text for m in cluster])
```

W dłuższym dokumencie otrzymasz coś takiego:
- Grupa 1: [Apple, firma, oni]
- Klaster 2: [nowe produkty]

### Krok 2: rozpoznawanie zaimków w oparciu o reguły (nauczanie)

Zobacz `code/main.py`, aby zapoznać się z implementacją obsługującą tylko stdlib:

1. Wyciąg wymienia: nazwane byty (rozpiętości pisane wielką literą), zaimki (wyszukiwanie dyktowane), opisy określone („X”).
2. Dla każdego zaimka spójrz na poprzednie wzmianki K i oceń je według:
   - zgodność płci/liczby (heurystyka)
   - świeżość (bliżej zwycięstw)
   - rola syntaktyczna (preferowane przedmioty)
3. Połącz poprzednik z najwyższym wynikiem.

Niekonkurencyjny w stosunku do modeli neuronowych. Pokazuje jednak przestrzeń poszukiwań i decyzje, jakie musi podjąć model kompleksowy.

### Krok 3: użycie LLM do odniesienia

```python
prompt = f"""Text: {text}

List every pronoun and noun phrase that refers to a person or company.
Cluster them by what they refer to. Output JSON:
[{{"entity": "Apple", "mentions": ["Apple", "the company", "it"]}}, ...]
"""
```

Dwa tryby awarii do obejrzenia. Po pierwsze, LLM nadmiernie się łączą („on” i „ona” odnoszą się do dwóch różnych osób). Po drugie, LLM po cichu pozostawiają wzmianki w długich dokumentach. Zawsze sprawdzaj, sprawdzając przesunięcie zakresu.

### Krok 4: ocena

Standardowy skrypt conll-2012 oblicza MUC, B³, CEAF-φ4 i podaje średnią. W przypadku wewnętrznej oceny zacznij od precyzji na poziomie zakresu i przywołaj zestaw testów z adnotacjami, a następnie dodaj wzmiankę łączącą F1.

## Pułapki

- **Eksplozja Singletona.** Niektóre systemy zgłaszają każdą wzmiankę jako odrębną klaster. B³ jest łagodny. MUC karze to. Zawsze sprawdzaj wszystkie trzy wskaźniki.
- **Zaimki w długim kontekście.** Wydajność spada o ~15 F1 w przypadku dokumentów zawierających ponad 2000 tokenów. Kawałek ostrożnie.
- **Założenia dotyczące płci.** Zakodowane na stałe zasady dotyczące płci łamią zasady dotyczące niebinarnych odniesień, organizacji i zwierząt. Korzystaj z wyuczonych modeli lub neutralnej punktacji.
- **Dryfowanie LLM w przypadku długich dokumentów.** Pojedyncze wywołanie interfejsu API nie jest w stanie wiarygodnie grupować wzmianek w ponad 50 akapitach. Użyj przesuwanego okna + scalania.

## Użyj tego

Stos na rok 2026:

| Sytuacja | Wybierz |
|----------|------|
| Angielski, pojedynczy dokument | `en_coreference_web_trf` (eksperymentalny spaCy) lub rdzeń neuronowy AllenNLP |
| Wielojęzyczny | SpanBERT / XLM-R przeszkolony w zakresie OntoNotes lub wielojęzycznego CoNLL |
| Coref zdarzeń między dokumentami | Specjalistyczne modele typu end-to-end (2025–26 SOTA) |
| Szybka linia bazowa LLM | GPT-4o / Claude z podpowiedzią rdzenia o strukturalnym wyjściu |
| Systemy dialogu produkcyjnego | Awaria oparta na regułach + neuronowa podstawowa + ręczny przegląd krytycznych miejsc |

Wzorzec integracji wprowadzony w 2026 r.: najpierw uruchom NER, uruchom coref, połącz klastry coref w jednostki NER. Zadania niższego szczebla widzą jedną jednostkę na klaster, a nie jedną jednostkę na wzmiankę.

## Wyślij to

Zapisz jako `outputs/skill-coref-picker.md`:

```markdown
---
name: coref-picker
description: Pick a coreference approach, evaluation plan, and integration strategy.
version: 1.0.0
phase: 5
lesson: 24
tags: [nlp, coref, information-extraction]
---

Given a use case (single-doc / multi-doc, domain, language), output:

1. Approach. Rule-based / neural span-based / LLM-prompted / hybrid. One-sentence reason.
2. Model. Named checkpoint if neural.
3. Integration. Order of operations: tokenize → NER → coref → downstream task.
4. Evaluation. CoNLL F1 (MUC + B³ + CEAF-φ4 average) on held-out set + manual cluster review on 20 documents.

Refuse LLM-only coref for documents over 2,000 tokens without sliding-window merge. Refuse any pipeline that runs coref without a mention-level precision-recall report. Flag gender-heuristic systems deployed in demographically diverse text.
```

## Ćwiczenia

1. **Łatwe.** Uruchom mechanizm rozpoznawania reguł oparty na regułach w `code/main.py` w 5 ręcznie utworzonych akapitach. Zmierz dokładność linków wzmiankowych w stosunku do podstawowej prawdy.
2. **Średni.** Użyj wstępnie wytrenowanego modelu rdzenia neuronowego w artykule prasowym. Porównaj klastry z własnymi ręcznymi adnotacjami. Gdzie się nie udało?
3. **Trudne.** Zbuduj rurociąg NER ulepszony za pomocą rdzenia Coref: najpierw NER, a następnie połącz za pośrednictwem klastrów Coref. Zmierz poprawę zasięgu jednostek w porównaniu z samym NER w 100 artykułach.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Wspomnij | Odniesienie | Zakres tekstu odnoszący się do jednostki (nazwy, zaimka, frazy rzeczownikowej). |
| Poprzednik | Do czego odnosi się „to” | Wcześniejsza wzmianka, późniejsza, odnosi się do. |
| Gromada | Wzmianki o podmiocie | Zbiór wzmianek, z których wszystkie odnoszą się do tej samej istoty ze świata rzeczywistego. |
| Anafora | Odniesienie wsteczne | Późniejsza wzmianka odnosi się do wcześniejszej („on” → „Jan”). |
| Katafora | Odniesienie do przodu | Wcześniejsza wzmianka odnosi się do później („Kiedy przybył, Jan…”). |
| Mostowanie | Niejawne odniesienie | „Kupiłem samochód. Koła były w złym stanie”. (koła TEGO samochodu.) |
| KONLL F1 | Liczba w rankingach | Średnia wyników MUC, B³, CEAF-φ4 F1. |

## Dalsze czytanie

- [Jurafsky i Martin, SLP3 Ch. 26 – Rozdzielczość współodniesień i łączenie podmiotów](https://web.stanford.edu/~jurafsky/slp3/26.pdf) – rozdział podręcznika kanonicznego.
- [Lee i in. (2017). Kompleksowe rozpoznawanie rdzeni neuronowych](https://arxiv.org/abs/1707.07045) — kompleksowo w oparciu o zakres.
- [Joshi i in. (2020). SpanBERT](https://arxiv.org/abs/1907.10529) — trening wstępny poprawiający coref.
- [Pradhan i in. (2012). Wspólne zadanie CoNLL-2012](https://aclanthology.org/W12-4501/) — punkt odniesienia.
- [Hobbs (1978). Rozwiązywanie odwołań do zaimków](https://www.sciencedirect.com/science/article/pii/0024384178900064) — klasyk oparty na regułach.