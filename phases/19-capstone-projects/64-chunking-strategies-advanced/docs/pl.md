# Porównanie strategii dzielenia

> Kawałki decydują o tym, co Twój retriever może kiedykolwiek wynurzyć. Źle określ granice i żaden model osadzania, żadna zmiana rankingu, żaden LLM nie będzie w stanie naprawić szkód w dalszej części.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 11, lekcje 04 (osadzenie), 06 (RAG), 07 (zaawansowany RAG); Faza 19 Podstawy ścieżki B (lekcje 20-29)
**Czas:** ~90 minut

## Cele nauczania
- Zaimplementuj od podstaw pięć strategii dzielenia na porcje: stałe okno, zdanie, dzielenie rekursywne, grupowanie semantyczne i nagłówki strukturalne.
- Zmierz przypomnienie@k na korpusie urządzeń ze złotymi etykietami zakresów odpowiedzi i wyjaśnij, dlaczego jedna strategia wygrywa w przypadku prozy, a inna strategia wygrywa w dokumentach technicznych.
- Przeczytaj rozkład długości fragmentów i rozpoznaj tryby niepowodzeń, jakie wprowadza każda strategia: zdania osierocone, cięcia w połowie symboli, fragmenty zawierające tylko nagłówek, dryf semantyczny.
- Wybierz wartość domyślną dla nowego korpusu bez przeprowadzania testu porównawczego, sprawdzając trzy właściwości: typ dokumentu, średnią długość akapitu i to, czy format ma wyraźną strukturę.

## Problem

Każdy rurociąg RAG zaczyna się od pocięcia dokumentów źródłowych na kawałki na tyle małe, aby pasował do nich model osadzania, i na tyle duże, że każdy fragment zawiera samodzielny pomysł. Wybór miejsca cięcia nie jest hiperparametrem. Jest to górna granica tego, co retriever może kiedykolwiek zwrócić.

Zapytanie z pytaniem „jak wygląda próg przerwania budżetu” może zakończyć się powodzeniem tylko wtedy, gdy fragment zawierający próg przerwania jest osiągalny. Jeśli rozdzielacz o stałym oknie odetnie wartość progową z otaczającego kontekstu, osadzanie zostanie przeniesione do innego klastra, wynik BM25 spadnie, osoby zmieniające ranking zobaczą szum, a odpowiedź wygenerowana przez LLM będzie błędna. W artykule z 2024 r. „LongRAG: Enhancing Retrieval-Augmented Generation with Long-context LLMs” zmierzono 35-procentową bezwzględną zmianę w przypominaniu sobie wyszukiwania wyłącznie na podstawie wyboru fragmentacji. Dalsze prace przeprowadzone w 2025 r. dotyczące kontekstowych nagłówków fragmentów zmniejszyły tę lukę, ale jej nie zamknęły.

W tej lekcji opracowano pięć strategii obok siebie, porównano je z zestawem urządzeń z zakresami odpowiedzi oznaczonymi złotymi etykietami i umożliwiono samodzielne odczytanie liczb przypomnień.

## Koncepcja

```mermaid
flowchart LR
  Doc[Source Document] --> S1[Fixed Window]
  Doc --> S2[Sentence]
  Doc --> S3[Recursive Split]
  Doc --> S4[Semantic Cluster]
  Doc --> S5[Structural Markdown]
  S1 --> Chunks1[Chunks]
  S2 --> Chunks2[Chunks]
  S3 --> Chunks3[Chunks]
  S4 --> Chunks4[Chunks]
  S5 --> Chunks5[Chunks]
  Chunks1 --> Index[Embedding Index]
  Chunks2 --> Index
  Chunks3 --> Index
  Chunks4 --> Index
  Chunks5 --> Index
  Index --> Eval[Recall@k vs Gold Spans]
```

### Stałe okno

Podstawowa metoda brute-force. Wytnij każde N znaków. Opcjonalnie nakładaj się, tak aby zdanie wycięte w pozycji N pojawiało się w całości wewnątrz fragmentu rozpoczynającego się w pozycji N – nakładanie się. Szybki, deterministyczny, straszny na granicach. Używaj go jako elementu sterującego, a nie domyślnego.

### Zdanie

Podziel granice zdań za pomocą wyrażenia regularnego lub prostej maszyny stanu. Spakuj jedno lub więcej zdań w porcję, aż do docelowego budżetu postaci. Zatrzymuje cięcie w połowie słowa. Nadal ucina środkowy akapit i środkową sekcję. Wartość domyślna w wielu wczesnych projektach RAG i rozsądny wybór w przypadku prozy bez innej struktury.

### Podział rekurencyjny

Strategia hierarchii spopularyzowana przez biblioteki ery 2023 roku. Spróbuj najpierw podzielić na najsilniejszy separator (podwójny znak nowej linii, akapit), następnie przejść do następnego (pojedynczy znak nowej linii), następnie na zdania, a następnie na znaki. Rekurencja kończy się, gdy fragment mieści się w budżecie. Silny w przypadku dokumentów o niespójnej strukturze, ponieważ dostosowuje się do regionu.

### Grupowanie semantyczne

Osadź każde zdanie. Grupuj sąsiadujące ze sobą zdania, które mają wspólny środek ciężkości tematu. Obcinaj, gdy bieżące podobieństwo do środka ciężkości spadnie poniżej progu. Granice odzwierciedlają znaczenie, a nie znaki. Wolniejsze w tworzeniu i zależne od modelu osadzania, ale odporne na dokumenty zmieniające tematy w akapicie.

### Strukturalne nagłówki przecen

W przypadku dokumentów o wyraźnej strukturze (przecena, reStructuredText, numerowane sekcje w stylu RFC) należy przyciąć na granicach nagłówków. Każdy fragment staje się nagłówkiem plus wszystko pod nim, aż do następnego nagłówka na tym samym lub wyższym poziomie. Najmniejsze fragmenty na temat, ale dostępne tylko wtedy, gdy korpus jest dobrze uformowany.

### W jaki sposób przypomnieć@k mierzy wybór granicy

Zapytanie oznaczone złotą etykietą zawiera w dokumencie źródłowym dokładne przesunięcia znaków zakresu odpowiedzi. Po pocięciu zadajesz sobie pytanie: czy którykolwiek z kawałków o najwyższej wartości k, które zwrócił retriever, pokrywa się ze złotym zakresem? Jeśli tak, wartość odwołania@k dla tego zapytania wynosi 1. Jeśli nie, wynosi 0. Średnia w zestawie zapytań. Przeprowadź tę samą ocenę dla każdej strategii, a rozkład pokaże, która polityka granic przetrwa korpus, który posiadasz.

## Zbuduj to

`code/main.py` implementuje:

- `fixed_window(text, size, overlap)` – wartość bazowa.
- `sentence_chunks(text, target)` - prosty paker zdań.
- `recursive_split(text, separators, target)` - rekurencja hierarchiczna.
- `semantic_chunks(text, similarity_threshold)` – grupowanie oparte na centroidach na bazie deterministycznego próbnego osadzania.
- `structural_markdown(text)` – rozdzielacz uwzględniający nagłówki.
- `mock_embed(text, dim)` – osadzanie oparte na skrótach, dzięki czemu pętla działa w trybie offline.
- `DenseIndex` — ten sam kształt, który został użyty w lekcji odzyskiwania hybrydowego w Fazie 19, na ścieżce B.
- `eval_recall(strategy, corpus, queries, k)` – pętla porównawcza.
- Element `main()`, który uruchamia każdą strategię w korpusie urządzeń i wypisuje tabelę odwołania@k.

Uruchom to:

```bash
python3 code/main.py
```

Dane wyjściowe to mała tabela z jednym wierszem na strategię i jedną kolumną na k. Zdanie przegrywa w ustrukturyzowanym urządzeniu. Przecena strukturalna wygrywa w przypadku przeceny. Rekursywność sprawdza się w przypadku mieszanych urządzeń, ponieważ rekurencja się dostosowuje. Grupowanie semantyczne wygrywa w przypadku prozy, w której nie ma użytecznych wskazówek strukturalnych.

## Tryby awarii, których tabela nie ukryje

**Zdania osierocone.** Pakowanie zdań tworzy fragmenty, w których brakuje zdania będącego tematem. Osadzanie wskazuje następnie niewłaściwy klaster.

**Wycięcia w środku symbolu.** Wewnątrz kodu o stałym oknie lub YAML podzielisz identyfikator na pół. Obie połówki osadzają się w hałasie.

**Części zawierające tylko nagłówek.** Strukturalna przecena powoduje wyemitowanie fragmentu zawierającego tylko `## Title`. Odfiltruj je lub dołącz pierwszy akapit następnego fragmentu.

**Dryf semantyczny.** Podcięcia w grupowaniu semantycznym, gdy korpus jest jednakowo zgodny z tematem. Kawałek zawierający 5000 znaków zawiera wiele konkretnych odpowiedzi w jednym rozproszonym osadzeniu. Połącz semantykę z twardym ograniczeniem znaku.

**Nieaktualne osadzania.** Klastrowanie semantyczne wykorzystuje model osadzania. Jeśli zmienisz model, zmienisz także fragmenty. Przypnij model fragmentu oddzielnie od modelu pobierania lub odbuduj indeks razem.

## Wybór ustawienia domyślnego bez uruchamiania testu porównawczego

Trzy właściwości decydują o domyślnym fragmentatorze dla nowego korpusu.

| Nieruchomość | Wartość | Domyślne |
|---------|-------|--------|
| Typ dokumentu | Proza bez struktury | Podział rekurencyjny, cel 800 |
| Typ dokumentu | Dokumentacja Markdown / RFC / API | Przecena strukturalna |
| Typ dokumentu | Kod | Obsługuje AST (poza zakresem; zob. faza 19, lekcja 02) |
| Długość akapitu | Długi, pojedynczy temat | Wyrok, cel 500 |
| Długość akapitu | Krótkie, mieszane tematy | Semantyczny, próg 0,6 |

W razie wątpliwości wybierz podział rekurencyjny. Jest to najsilniejszy punkt odniesienia dla pojedynczej strategii.

## Użyj tego

Wzory produkcyjne:

- Uruchom eval przed wysłaniem nowego rurociągu; nie ufaj strategii domyślnej Twojej biblioteki.
- Uruchom ponownie eval za każdym razem, gdy zmienisz model osadzania lub miks korpusu; zwycięzca jest zależny od korpusu.
- Zachowaj nazwę strategii w metadanych każdego fragmentu, aby móc później przypisać regresje.

## Wyślij to

Kompleksowy system RAG Track F z lekcji 69 wykorzystuje wybrany tutaj fragmentator jako swój pierwszy etap. Uprząż eval z lekcji 68 odczytuje przypomnienie@k z tego samego kształtu, który `eval_recall` zwraca w tej lekcji. Wybierz strategię, która zwycięży w Twoim korpusie i przekaż ją dalej.

## Ćwiczenia

1. Dodaj szóstą strategię: okno tokena, używając `tiktoken` zamiast liczby znaków. Porównaj z oknem stałym na tym samym urządzeniu.
2. Wstrzyknij 30-procentową część bloków kodu do urządzenia prozatorskiego. Uruchom ponownie tabelę. Wyjaśnij, dlaczego każda strategia z wyjątkiem strukturalnej przeceny traci pamięć.
3. Zamień osadzenie deterministyczne na osadzenie pochodzące od prawdziwego dostawcy projektu. Zmierz różnicę przypominania klastrów semantycznych. Zgłoś, czy spread między strategiami poszerza się, czy zawęża.
4. Dodaj pole `summary` na każdą porcję: jednozdaniowy opis centroidu. Uruchom ponownie eval z podsumowaniem dołączonym do treści fragmentu. Zmierz siłę wycofania.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Przypomnij@k | „Czy dostaliśmy właściwy kawałek?” | Część zapytań, w których dowolna z k górnych części pokrywa się ze złotym zakresem odpowiedzi |
| Kawałki nakładają się | „Przesuwane okno” | Dołącz ponownie N ostatnich znaków poprzedniego fragmentu do następnego fragmentu |
| Rozdzielacz strukturalny | „Części uwzględniające nagłówki” | Cięcie na granicach H1/H2/H3; tekst nagłówka jest częścią fragmentu |
| Semantyczny fragmentator | „Fragmenty tematyczne” | Osadź zdania, grupuj według podobieństwa centroidów, wycinaj według dryfu |
| Dryf środka ciężkości | „Zmiana tematu” | Podobieństwo cosinusowe między średnią bieżącą a następnym zdaniem przekracza próg |

## Dalsze czytanie

— [LongRAG: Ulepszone generowanie rozszerzonego wyszukiwania za pomocą LLM o długim kontekście (arXiv 2406.15319)](https://arxiv.org/abs/2406.15319)
– [Antropiczne, pobieranie kontekstowe](https://www.anthropic.com/news/contextual-retrieval)
- [LlamaIndex, Strategie fragmentowania dla produkcji RAG](https://docs.llamaindex.ai/en/stable/optimizing/production_rag/)
- Faza 11, lekcja 06 - Podstawy RAG
- Faza 11, lekcja 07 - zaawansowany RAG
- Faza 19, lekcja 65 - pobieranie hybrydowe, które klasyfikuje wyprodukowane tutaj kawałki
- Faza 19, lekcja 68 - uprząż ewaluacyjna, która ocenia wybór strategii w produkcji