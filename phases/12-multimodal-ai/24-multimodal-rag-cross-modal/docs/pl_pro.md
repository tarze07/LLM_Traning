# Multimodalny RAG i wyszukiwanie międzymodalne

> Wyszukiwanie informacji w dokumentach graficznych (Vision RAG) to tylko jeden z elementów układanki. Wdrożenie produkcyjne w pełni multimodalnego systemu RAG ma znacznie szerszy zakres: obejmuje przeszukiwanie tekstów, obrazów, dźwięków i wideo dla takich zastosowań jak planowanie podróży („znajdź przytulne wegańskie miejsce na brunch z naturalnym oświetleniem”), wstępna diagnostyka medyczna („zidentyfikuj uraz na podstawie tego zdjęcia i opisu objawów”), e-commerce („znajdź ubrania podobne do mojego selfie w moim rozmiarze”) czy serwis techniczny („zdiagnozuj problem na podstawie nagrania pracy silnika i zdjęcia uszkodzonej części”). Trzy kompleksowe opracowania naukowe z 2025 roku (Abootorabi i in., Mei i in., Zhao i in.) skodyfikowały kluczowe wyzwania tej dziedziny: wyszukiwanie międzymodalne, fuzję wyników (retrieval fusion), ugruntowanie generowanej odpowiedzi (grounded generation) oraz multimodalną ewaluację. W tej lekcji przeanalizujemy te prace i zaprojektujemy produkcyjne potoki multimodalnego RAG.

**Typ:** Teoria / Przegląd
**Języki:** Python (biblioteka standardowa, wyszukiwarka międzymodalna z fuzją + ugruntowany generator)
**Wymagania wstępne:** Faza 12 · 23 (ColPali i systemy Vision-Native RAG), Faza 11 (Inżynieria LLM — podstawy RAG)
**Czas:** ~180 minut

## Cele kształcenia

- Projektowanie mechanizmów wyszukiwania międzymodalnego (cross-modal): tekst → obraz, obraz → tekst, audio → wideo itd.
- Porównanie trzech strategii fuzji: fuzja wyników (score fusion), fuzja oparta na atencji oraz fuzja typu MoE (Mixture of Experts).
- Wyjaśnienie mechanizmu ugruntowania (grounding): jak realizować cytowanie i wskazywanie źródeł, gdy dokumenty referencyjne należą do różnych modalności.
- Omówienie trzech kanonicznych przeglądów multimodalnego RAG z 2025 roku oraz zaproponowanej w nich taksonomii wyzwań.

## Problem

Jednomodalny (tekstowy) RAG to dobrze znany i opanowany schemat: generowanie wektora zapytania → generowanie wektorów fragmentów tekstu → wyszukiwanie podobieństwa → przekazanie do LLM. Z kolei w pełni multimodalny RAG niesie ze sobą nowe wyzwania:

1. **Obsługa wielu wyszukiwarek:** Każda modalność (tekst, obraz, audio) wymaga generowania osadzeń w kompatybilnej przestrzeni wektorowej.
2. **Fuzja wyników (Retrieval Fusion):** Konieczność spójnego łączenia wyników wyszukiwania z różnych modalności.
3. **Ugruntowanie generowania (Grounded Generation):** Model must potrafić cytować i wskazywać źródła pochodzące z różnych modalności.
4. **Multimodalna ewaluacja:** Opracowanie metryk oceny uwzględniających sygnały międzymodalne.

Wszystkie czołowe publikacje z 2025 roku opierają się na tej samej ogólnej taksonomii wyzwań.

## Koncepcja

### Wyszukiwanie międzymodalne (Cross-modal Retrieval)

Polega na wyszukiwaniu dokumentów w modalności B za pomocą zapytania sformułowanego w modalności A. Trzy powszechnie stosowane wzorce to:

1. **Wspólna przestrzeń osadzeń (Shared embedding space):** Modele takie jak CLIP (tekst + obraz) lub CLAP (tekst + audio) mapują różne modalności do tej samej przestrzeni wektorowej. Obliczanie podobieństwa cosinusowego działa w tym przypadku bezpośrednio. Metoda jest jednak ograniczona do modalności, na których dany model był trenowany.
2. **Osobne enkodery + warstwa translacji:** Zastosowanie dedykowanych enkoderów dla tekstu oraz obrazów, połączonych małą siecią neuronową pełniącą rolę translatora przestrzeni wektorowych (np. architektura Sen2Sen autorstwa Gupty i in.). Jest to rozwiązanie elastyczne, lecz zwiększa stopień skomplikowania systemu.
3. **VLM jako wspólny enkoder:** Wykorzystanie ukrytych reprezentacji (hidden states) zaawansowanego modelu VLM jako wektorów wyszukiwania. Pozwala to na obsługę dowolnej modalności wspieranej przez VLM, oferując najwyższą jakość kosztem dużego narzutu obliczeniowego.

Rekomendowany wybór: SigLIP 2 dla par tekst+obraz, CLAP dla tekstu i audio, oraz stany ukryte VLM w zadaniach wymagających najwyższej precyzji semantycznej.

### Strategie fuzji wyników

Załóżmy, że system wyszukał 10 wyników: 5 obrazów, 3 fragmenty tekstu oraz 2 klipy audio. Jak je spójnie połączyć i uszeregować?

- **Fuzja punktacji / Score Fusion (najtańsza obliczeniowo):** Każda wyszukiwarka zwraca własne dopasowania z określonymi wynikami numerycznymi. Wyniki te są normalizowane w ramach poszczególnych modalności, a następnie sumowane z odpowiednimi wagami. Podejście proste, wykazujące wysoką skuteczność w praktyce.
- **Fuzja oparta na atencji:** Odnalezione elementy są łączone w jedną sekwencję, po czym mała sieć atencji wyznacza ich względne wagi. Wymaga to zgromadzenia danych i dodatkowego treningu.
- **Fuzja MoE (Mixture of Experts):** Sieć bramkująca (router) kieruje zapytanie do ekspertów zajmujących się konkretnymi modalnościami. Zapytania o charakterze wizualnym nadadzą większą wagę obrazom, a zapytania tekstowe – dokumentom znakowym.

Domyślna konfiguracja produkcyjna: Fuzja punktacji (score fusion) z lekkim faworyzowaniem modalności, w której sformułowano zapytanie. Przejście na architekturę MoE zaleca się tylko wtedy, gdy testy A/B wykażą wyraźną przewagę w docelowej domenie.

### Ugruntowanie odpowiedzi (Grounded Generation)

Model LLM/VLM musi wskazywać, które z odnalezionych źródeł posłużyły do sformułowania poszczególnych twierdzeń. W systemach multimodalnych formatowanie odnośników wygląda następująco:
- **Źródło tekstowe:** Standardowy odnośnik typu `[1]`.
- **Źródło w postaci obrazu:** Odnośnik `[img 3]` wraz z krótkim opisem.
- **Źródło audio:** Odnośnik `[audio 2 at 0:34]` wskazujący konkretną sekundę nagrania.

Wymaga to szkolenia generatora na danych bogatych w takie oznaczenia (citation-aware training), dzięki czemu model uczy się naturalnie wplatać cytaty w treść odpowiedzi.

### Przeglądy literatury z 2025 roku

- **Abootorabi i in.** (arXiv:2502.08826, „Ask in Any Modality”): Kompleksowa taksonomia multimodalnego RAG, opisująca procesy wyszukiwania, fuzji oraz generowania. Najszersze opracowanie teoretyczne.
- **Mei i in.** (arXiv:2504.08748, „A Survey of Multimodal RAG”): Skupia się na szczegółowej analizie podzadań oraz analizie typowych błędów modeli (failure modes). Bardzo pomocne przy projektowaniu ewaluacji.
- **Zhao i in.** (arXiv:2503.18016): Przegląd koncentrujący się na modalności wizyjnej i systemach klasy ColPali.

Lektura tych trzech prac pozwala na pełne zapoznanie się ze stanem wiedzy z pierwszej połowy 2025 roku. Większość omawianych w nich podproblemów wciąż stanowi aktywne pole badań akademickich.

### MuRAG – praca założycielska

Model MuRAG (Chen i in., 2022) to pierwszy opisany w literaturze system multimodalnego RAG. Pobierał on obrazy i teksty z multimodalnej bazy wiedzy w celu generowania odpowiedzi, dowodząc skuteczności tej koncepcji jeszcze przed masowym pojawieniem się modeli VLM. Nowoczesne systemy (VisRAG, M3DocRAG) bezpośrednio rozwijają te założenia.

### Przykład: Produkcyjne planowanie podróży

Zapytanie użytkownika: „znajdź przytulne wegańskie miejsce na brunch z naturalnym oświetleniem”.

Potok przetwarzania:
1. **Dekompozycja zapytania:** Fraza „przytulne” → analiza opinii tekstowych i audio; „wegańskie miejsce na brunch” → wyszukiwanie w menu i tekstach; „naturalne oświetlenie” → wyszukiwanie na zdjęciach wnętrz.
2. **Wyszukiwanie w modalnościach:**
   - Tekst: Wyszukiwanie opinii i menu zawierających frazy o wegańskim brunchu i kameralnej atmosferze.
   - Obrazy: Wyszukiwanie zdjęć wnętrz restauracji pod kątem nasłonecznienia i przestrzenności.
   - Audio: Weryfikacja nagrań hałasu otoczenia (ciche tło, brak głośnej muzyki).
3. **Fuzja wyników:** Obliczenie zagregowanej punktacji dla każdej restauracji.
4. **Generowanie odpowiedzi:** Model VLM otrzymuje top-k najlepiej dopasowanych lokali wraz z dowodami (obrazy, opinie, próbki audio) i formułuje ugruntowaną odpowiedź z odnośnikami.

Dzięki temu system potrafi podjąć decyzję na podstawie cech, które byłyby całkowicie pominięte w tradycyjnym, wyłącznie tekstowym potoku RAG.

### Agentowy multimodalny RAG (Multi-hop)

Jeśli pierwsze wyszukiwanie nie zwraca wyników o wysokiej wiarygodności, model LLM/VLM może przeformułować zapytanie i ponowić próbę. Stosuje się tu wzorce agentowe omawiane w Fazie 14, na przykład:
- Pobranie pierwszych 10 wyników → model zgłasza: „restauracje spełniają wymogi kulinarne, ale tło audio przekracza 40 dB” → ponowne wyszukiwanie z nowym filtrem audio.
- Wyszukanie obrazu lokalu → model identyfikuje obecność karty dań na zdjęciu → wywołanie OCR/VLM na tym konkretnym fragmencie menu w celu weryfikacji cen → ostateczna odpowiedź.

Podejście to wiąże się z wyższym opóźnieniem, lecz pozwala na obsługę bardzo złożonych i niejednoznacznych pytań.

### Ewaluacja i metryki

Ocena skuteczności systemów międzymodalnych jest trudna ze względu na brak uniwersalnych standardów. Najczęściej stosuje się:
- Wskaźnik Recall@k mierzony osobno dla każdej modalności.
- Zagregowaną dokładność wyboru top-k wyników.
- Ewaluację z udziałem ekspertów (human evaluation).
- Metryki biznesowe (np. współczynnik konwersji rezerwacji lub zakupów).

Większość prac naukowych skupia się na ocenie w ramach ściśle zdefiniowanych, wąskich dziedzin testowych.

## Zastosowanie w kodzie

Plik `code/main.py` zawiera:
- Makiety trzech wyszukiwarek (tekstowej, obrazkowej i dźwiękowej) operujących na wspólnej bazie restauracji.
- Moduł fuzji punktacji (score fusion), łączący wyniki wyszukiwania z konfigurowalnymi wagami dla poszczególnych modalności.
- Moduł generatora tworzący ugruntowaną odpowiedź z odnośnikami źródłowymi.
- Prostą pętlę agenta przeformułowującą zapytanie w przypadku niskiej wiarygodności pierwszego odczytu.

## Rezultat

Do tej lekcji dołączono dokument `outputs/skill-multimodal-rag-designer.md` (dostępny w powiązanym katalogu). Pomaga on zaprojektować potoki wyszukiwania, algorytmy fuzji, generatory oraz metryki oceny na podstawie specyfikacji multimodalnych zapytań użytkowników.

## Ćwiczenia

1. Zaprojektuj architekturę multimodalnego RAG dla potrzeb medycznej selekcji chorych (triage). Wejściem systemu jest zdjęcie urazu oraz opis objawów. Jakie bazy wiedzy i jakie modalności będą odpytywane?
2. Fuzja punktacji opiera się na prostej sumie ważonej. Przed jakimi błędami (failure modes) chroni zastosowanie zaawansowanej fuzji typu MoE?
3. Przeczytaj sekcję 3 publikacji Abootorabi i in. Wymień trzy kluczowe podproblemy tam opisane i wyjaśnij, jak odnoszą się one do projektowanego przez Ciebie systemu.
4. Zaproponuj plan ewaluacji dla multimodalnego asystenta podróży. Jakie metryki pozwolą ocenić poprawność doboru zdjęć, dźwięków oraz spójność sformułowanej odpowiedzi?
5. Agentowe wyszukiwanie wielokrokowe (multi-hop) drastycznie zwiększa opóźnienie systemu. Przy jakim poziomie skomplikowania zapytań zysk na precyzji uzasadnia ten koszt czasowy?

## Kluczowe pojęcia

| Termin | Potoczne określenie | Co to dokładnie oznacza |
| :--- | :--- | :--- |
| **Wyszukiwanie międzymodalne** | „Cross-modal retrieval” | Zdolność systemu do wyszukiwania danych w modalności B za pomocą zapytania w modalności A (np. tekst wyszukuje obrazy). |
| **Fuzja punktacji (Score fusion)** | „Łączenie punktów” | Najprostsza metoda fuzji oparta na wyznaczeniu ważonej sumy znormalizowanych wyników z poszczególnych wyszukiwarek. |
| **Fuzja MoE** | „Bramkowanie modalności” | Zastosowanie sieci bramkującej, która dynamicznie decyduje, którym wyszukiwarkom modalności przyznać największą wagę dla danego zapytania. |
| **Ugruntowanie odpowiedzi** | „Cytowanie źródeł” | Generowanie odpowiedzi, w której każde twierdzenie jest poparte bezpośrednim odnośnikiem do konkretnego pliku źródłowego (tekstu, klatki wideo itp.). |
| **MuRAG** | „Pierwszy multimodalny RAG” | Pionierska publikacja z 2022 roku, która zdefiniowała ramy i pojęcia dla multimodalnego wyszukiwania RAG. |
| **Agentowy multi-hop** | „Wyszukiwanie wielokrokowe” | Pętla decyzyjna, w której model na bieżąco analizuje wyniki i samodzielnie ponawia oraz modyfikuje zapytania do baz danych. |

## Literatura uzupełniająca

- [Abootorabi i in. — Ask in Any Modality (arXiv:2502.08826)](https://arxiv.org/abs/2502.08826)
- [Mei i in. — A Survey of Multimodal RAG (arXiv:2504.08748)](https://arxiv.org/abs/2504.08748)
- [Zhao i in. — Vision RAG Survey (arXiv:2503.18016)](https://arxiv.org/abs/2503.18016)
- [Chen i in. — MuRAG (arXiv:2210.02928)](https://arxiv.org/abs/2210.02928)
- [Liu i in. — REACT (arXiv:2301.10382)](https://arxiv.org/abs/2301.10382)
