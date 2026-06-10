# Rozstrzyganie koreferencji (Coreference Resolution)

> „Zadzwoniła do niego. Nie odebrał. Lekarz był na obiedzie”. Trzy odniesienia do dwóch osób, z których żadna nie została wymieniona z imienia i nazwiska. Rozstrzyganie koreferencji pozwala ustalić, kto jest kim.

**Typ:** Teoria
**Języki:** Python
**Wymagania wstępne:** Faza 5 · 06 (NER), Faza 5 · 07 (POS i parsowanie składniowe)
**Czas:** ~60 minut

## Problem

Wyobraź sobie, że musisz wyodrębnić wszystkie wzmiankę o firmie Apple Inc. z tekstu o długości 300 słów. Zadanie jest proste, gdy w tekście pojawia się słowo „Apple”. Staje się jednak trudne, gdy autor używa określeń: „firma”, „oni”, „gigant z Cupertino” czy „przedsiębiorstwo założone przez Jobsa”. Bez powiązania tych wszystkich odniesień z jednym, tym samym obiektem, tradycyjny potok NER (Named Entity Recognition) pomija od 60% do nawet 80% wzmianek.

Rozstrzyganie koreferencji (coreference resolution) łączy wszystkie wyrażenia odnoszące się do tego samego obiektu w świecie rzeczywistym w jedną grupę (klaster). Stanowi ono kluczowy pomost pomiędzy podstawową analizą tekstu (NER, parsowanie składniowe) a głębszym przetwarzaniem semantycznym (ekstrakcja informacji, systemy pytania-odpowiedzi, streszczanie tekstów, budowa grafów wiedzy).

Dlaczego koreferencja ma kluczowe znaczenie w 2026 roku:

- **Automatyczne streszczanie (Summarization):** Przekształcenie zdania „Dyrektor generalny ogłosił...” w „Tim Cook ogłosił...” pozwala na zachowanie precyzji w generowanym streszczeniu.
- **Systemy pytania-odpowiedzi (QA):** Aby odpowiedzieć na pytanie „Do kogo dzwoniła?”, system musi najpierw rozstrzygnąć, kim jest „ona”.
- **Ekstrakcja informacji (IE):** Bez koreferencji graf wiedzy (Knowledge Graph) mógłby zawierać błędne, zdublowane relacje typu „Osoba_X założyła Apple” i „Jobs założył Apple” jako osobne węzły.
- **Wielodokumentowa ekstrakcja informacji (Cross-document IE):** Powiązanie odniesień do tego samego obiektu w różnych artykułach prasowych.

## Koncepcja

![Grupowanie koreferencji: powiązanie wzmianek z obiektami](../assets/coref.svg)

**Zadanie.** Wejściem jest dokument tekstowy. Wyjściem są grupy (klastry) wzmianek (ang. spans / zakresów tekstu), z których każda odnosi się do jednego, konkretnego obiektu.

**Typy wzmianek (Mentions):**

- **Nazwy własne (Proper nouns):** np. „Tim Cook”
- **Frazy nominalne (Nominal mentions):** np. „dyrektor generalny”, „przedsiębiorstwo”
- **Zaimki (Pronominal mentions):** np. „on”, „ona”, „oni”, „to”
- **Apozycje (Appositives):** np. „Tim Cook, dyrektor generalny Apple”

**Architektury i podejścia:**

1. **Systemy regułowe (np. Hobbs, 1978).** Rozstrzyganie zaimków na podstawie drzewa składniowego za pomocą predefiniowanych reguł gramatycznych. Stanowi solidny baseline, ponieważ zaimki są zaskakująco trudne do poprawnego sparowania innymi metodami.
2. **Klasyfikatory par wzmianek (Mention-pair classifiers).** Dla każdej pary wzmianek `(m_i, m_j)` klasyfikator ocenia prawdopodobieństwo współreferencji. Klastry są tworzone poprzez domknięcie przechodnie (transitive closure). Standard stosowany powszechnie przed rokiem 2016.
3. **Modele rankingowe (Mention-ranking models).** Dla każdej kolejnej wzmianki model ocenia i szereguje potencjalnych poprzedników (antecedents), uwzględniając opcję „brak poprzednika”. Wybierany jest kandydat o najwyższej ocenie.
4. **Modele end-to-end oparte na fragmentach (np. Lee et al., 2017).** Model oparty na transformerze wyznacza wszystkie potencjalne fragmenty tekstu (spans) do określonej długości, wylicza ich wektory reprezentacji, przewiduje ich ważność jako wzmianek oraz prawdopodobieństwo powiązania każdego fragmentu z poprzednikami. Klastrowanie odbywa się metodą zachłanną. To dominujący SOTA standard we współczesnym NLP.
5. **Podejście generatywne (od 2024 roku).** Sterowanie modelem LLM za pomocą promptu typu: „Wypisz wszystkie zaimki w tekście i wskaż ich poprzedników”. Działa dobrze dla prostych tekstów, długich dokumentów oraz rzadkich, lecz odległych nawiązań.

**Metodologia oceny.** Wykorzystuje się pięć standardowych metryk (MUC, B³, CEAF, BLANC, LEA), ponieważ żadna pojedyncza miara nie oddaje w pełni poprawności klastrowania. Jako główny wskaźnik (CoNLL F1) stosuje się średnią z pierwszych trzech metryk. Najlepsze modele w 2026 roku osiągają na zbiorze CoNLL-2012 wynik rzędu ~83 F1.

**Najtrudniejsze przypadki lingwistyczne:**

- Rozbudowane opisy nominalne odnoszące się do obiektów wprowadzonych wiele stron wcześniej.
- Anafora pomostowa (Bridging anaphora): np. słowo „koła” nawiązujące do wspomnianego wcześniej „samochodu”.
- Anafora zerowa (zjawisko powszechne m.in. w językach chińskim i japońskim, gdzie zaimek jest całkowicie pomijany w zdaniu).
- Katafora (zaimek występuje przed swoim desygnatem): np. „Kiedy **ona** weszła do pokoju, Mary uśmiechnęła się”.

## Zbuduj to

### Krok 1: Zastosowanie gotowych modeli koreferencji (spaCy / AllenNLP)

```python
import spacy
nlp = spacy.load("en_coreference_web_trf")   # eksperymentalny model
doc = nlp("Apple announced new products. The company said they would ship soon.")
for cluster in doc._.coref_clusters:
    print(cluster, "->", [m.text for m in cluster])
```

Dla dłuższego tekstu wynik będzie miał postać grup współreferencyjnych:
- Grupa 1: [Apple, the company, they]
- Grupa 2: [new products]

### Krok 2: Dydaktyczny model regułowy rozstrzygania zaimków

W pliku `code/main.py` znajdziesz uproszczony model oparty wyłącznie na bibliotece standardowej Pythona:

1. Ekstrakcja wzmianek: wykrywanie nazw własnych (rozpoczynających się wielką literą), zaimków (na podstawie słownika) oraz opisów określonych.
2. Dla każdego zaimka analizujemy `K` poprzednich wzmianek i oceniamy je pod kątem:
   - zgodności rodzaju i liczby (heurystyki gramatyczne),
   - odległości w tekście (wzmianki bliższe zaimkowi są preferowane),
   - roli składniowej (podmioty zdania mają wyższy priorytet).
3. Łączemy zaimek z poprzednikiem o najwyższej ocenie sumarycznej.

Model ten nie może konkurować z sieciami neuronowymi, lecz dobrze ilustruje przestrzeń poszukiwań oraz decyzje, jakie musi podejmować model end-to-end.

### Krok 3: Wykorzystanie modeli LLM do rozstrzygania koreferencji

```python
prompt = f"""Text: {text}

List every pronoun and noun phrase that refers to a person or company.
Cluster them by what they refer to. Output JSON:
[{{"entity": "Apple", "mentions": ["Apple", "the company", "it"]}}, ...]
"""
```

Należy uważać na dwa typowe problemy. Po pierwsze, modele LLM mają tendencję do nadmiernego scalania klastrów (np. błędnego łączenia zaimków „on” i „ona” przypisanych do różnych postaci). Po drugie, modele potrafią pomijać mniej widoczne wzmianki w długich tekstach. Zawsze weryfikuj poprawność wyjściowych indeksów znakowych.

### Krok 4: Ewaluacja modeli

Standardowy skrypt ewaluacyjny z benchmarku CoNLL-2012 oblicza metryki MUC, B³ oraz CEAF-φ4 i wyznacza ich średnią. W celach testów wewnętrznych warto zacząć od precyzji i pełności (precision/recall) wykrywania samych granic wzmianek, a następnie oceniać jakość powiązań (link-level F1).

## Typowe pułapki

- **Klastry jednoelementowe (Singleton explosion):** Niektóre systemy mają tendencję do umieszczania każdej wzmianki w osobnym, jednoelementowym klastrze. Metryka B³ ocenia takie zachowanie łagodnie, podczas gdy MUC nakłada surową karę. Zawsze analizuj pełen zestaw metryk.
- **Utrata sprawności w długich tekstach:** Skuteczność modeli spada o około 15 punktów F1, gdy dokument wejściowy przekracza 2000 tokenów. Dziel tekst na mniejsze sekcje z należytą starannością.
- **Uproszczone reguły rodzaju (gender bias):** Sztywno zakodowane reguły dotyczące płci/rodzaju gramatycznego zawodzą w przypadku zaimków neutralnych, nazw organizacji oraz zwierząt. Korzystaj z modeli uczonych na zróżnicowanych danych lub z algorytmów neutralnych genderowo.
- **Dryfowanie modeli LLM na długich dokumentach:** Pojedyncze zapytanie do API nie pozwala na stabilne klastrowanie wzmianek rozproszonych na przestrzeni kilkadziesiąt akapitów. Stosuj technikę okna przesuwnego z późniejszym scalaniem wyników.

## Rekomendowane podejścia

| Sytuacja | Zalecane rozwiązanie |
|----------|------|
| Język angielski, pojedyncze dokumenty | Dedykowany model `en_coreference_web_trf` (moduł spaCy) lub biblioteka AllenNLP |
| Wielojęzyczność | Modele SpanBERT / XLM-R dostrojone na zbiorze OntoNotes lub wielojęzycznych danych CoNLL |
| Koreferencja między dokumentami (Cross-document coref) | Dedykowane, wyspecjalizowane architektury end-to-end |
| Szybki baseline z użyciem LLM | GPT-4o / Claude ze strukturyzacją odpowiedzi (Structured Outputs) |
| Produkcyjne systemy dialogowe | Hybryda (reguły jako zabezpieczenie + model neuronowy + ręczna weryfikacja) |

Standard wdrożeniowy: najpierw uruchamiamy model NER, następnie rozstrzygamy koreferencje i na koniec łączymy klastry koreferencji z wykrytymi encjami NER. Dzięki temu kolejne moduły systemu operują na zunifikowanych obiektach (entities), a nie na rozproszonych, pojedynczych słowach.

## Zapisywanie szablonu

Zapisz jako `outputs/skill-coref-picker.md`:

```markdown
---
name: coref-picker
description: Wybierz metodę rozstrzygania koreferencji, zaprojektuj plan ewaluacji oraz strategię integracji.
version: 1.0.0
phase: 5
lesson: 24
tags: [nlp, coref, information-extraction]
---

Na podstawie scenariusza użycia (pojedynczy/wielokrotny dokument, dziedzina, język) wygeneruj:

1. Podejście: Regułowe, neuronowe (span-based), oparte na modelach LLM lub hybrydowe wraz z jednozdaniowym uzasadnieniem.
2. Model: Dokładna nazwa punktu kontrolnego (checkpoint) w przypadku modeli neuronowych.
3. Integracja: Kolejność operacji potoku (np. tokenizacja → NER → koreferencja → zadanie docelowe).
4. Plan ewaluacji: Wskaźnik CoNLL F1 (średnia z metryk MUC, B³ oraz CEAF-φ4) na wydzielonym zbiorze testowym oraz ręczny audyt klastrów dla przynajmniej 20 dokumentów.

Nigdy nie akceptuj rozwiązań opartych wyłącznie na LLM dla dokumentów dłuższych niż 2000 tokenów bez zastosowania okna przesuwnego z późniejszym scalaniem. Zawsze odrzucaj potoki przetwarzania, które nie generują raportu precyzji i pełności (precision/recall) na poziomie pojedynczych wzmianek. Oznaczaj jako ryzykowne systemy oparte na prostych regułach płci/rodzaju wdrażane dla zróżnicowanych demograficznie tekstów.
```

## Ćwiczenia praktyczne

1. **Poziom łatwy:** Uruchom regułowy model koreferencji z pliku `code/main.py` na 5 przygotowanych akapitach tekstu. Oblicz dokładność powiązania zaimków z ich rzeczywistymi poprzednikami.
2. **Poziom średni:** Przetestuj gotowy, neuronowy model koreferencji na wybranym artykule prasowym. Porównaj wygenerowane automatycznie klastry z własnymi ręcznymi adnotacjami. Wskaż, w jakich sytuacjach model popełnił błędy.
3. **Poziom trudny:** Zaimplementuj potok NER wspomagany modułem koreferencji: najpierw wykryj encje (NER), a następnie zunifikuj je w oparciu o klastry koreferencji. Zmierz przyrost pokrycia (coverage) encji w odniesieniu do klasycznego modelu NER na próbie 100 artykułów.

## Kluczowe pojęcia

| Termin | Potoczne określenie | Znaczenie precyzyjne |
|------|-----------------|----------------------|
| Wzmianka (Mention) | Odniesienie | Fragment tekstu (nazwa własna, zaimek, fraza nominalna) reprezentujący dany obiekt. |
| Poprzednik (Antecedent) | Do czego odnosi się „to” | Wcześniejsza wzmianka w tekście, do której odnosi się dane wyrażenie. |
| Klaster współreferencyjny (Cluster) | Klastry | Zbiór wszystkich wzmianek w tekście odnoszących się do tego samego obiektu w świecie rzeczywistym. |
| Anafora (Anaphora) | Odniesienie wsteczne | Wyrażenie nawiązujące do wcześniej wprowadzonego obiektu (np. „Jan wpadł na chwilę. Powiedział, że...” -> „Powiedział” odnosi się do „Jan”). |
| Katafora (Cataphora) | Odniesienie do przodu | Wyrażenie nawiązujące do obiektu, który zostanie wprowadzony dopiero w dalszej części zdania. |
| Anafora pomostowa (Bridging) | Mostowanie | Relacja pośrednia, np. „Kupiłem dom. Dach wymaga remontu” – słowo „dach” nawiązuje do dachu zakupionego domu. |
| CoNLL F1 | Wynik modelu | Uśredniony wynik F1 wyliczony z trzech metryk: MUC, B³ oraz CEAF-φ4; standard oceny w zadaniach koreferencji. |

## Literatura uzupełniająca

- [Jurafsky & Martin. Speech and Language Processing (3rd ed.), Chapter 26: Coreference Resolution and Entity Linking](https://web.stanford.edu/~jurafsky/slp3/26.pdf) — kanoniczny rozdział w podręczniku akademickim.
- [Lee et al. (2017). End-to-end Neural Coreference Resolution](https://arxiv.org/abs/1707.07045) — przełomowa praca wprowadzająca modele neuronowe oparte na fragmentach (spans).
- [Joshi et al. (2020). SpanBERT: Improving Pre-training by Segmenting and Predicting Spans](https://arxiv.org/abs/1907.10529) — publikacja opisująca technikę SpanBERT poprawiającą jakość koreferencji.
- [Pradhan et al. (2012). CoNLL-2012 Shared Task: Modeling Multilingual Unrestricted Coreference in OntoNotes](https://aclanthology.org/W12-4501/) — specyfikacja i wyniki oficjalnego benchmarku.
- [Hobbs (1978). Resolving Pronoun References](https://www.sciencedirect.com/science/article/pii/0024384178900064) — klasyczna publikacja prezentująca regułowe podejście do rozstrzygania zaimków.
