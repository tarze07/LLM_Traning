# Multimodalny RAG i wyszukiwanie międzymodalne

> Dokument RAG z wizją to jeden kawałek. Produkcja multimodalnego RAG ma szerszy zakres — pobiera tekst, obrazy, dźwięk i wideo na potrzeby takich procesów, jak planowanie podróży („znajdź mi spokojny wegański brunch przy naturalnym świetle”), selekcja medyczna („jaki uraz pasuje do tego zdjęcia + te notatki”), handel elektroniczny („stroje podobne do tego selfie, w moim rozmiarze”) i usługi terenowe („zdiagnozuj dźwięk silnika plus zdjęcie części”). Trzy badania przeprowadzone w 2025 r. — Abootorabi i in., Mei i in., Zhao i in. — skodyfikował podproblemy: wyszukiwanie międzymodalne, fuzja wyszukiwania, uziemianie generacji, ocena multimodalna. Podczas tej lekcji czytane są ankiety i projektowane rurociągi produkcyjne.

**Typ:** Kompilacja
**Języki:** Python (stdlib, crossmodalny retriever z fuzją + uziemiony generator)
**Wymagania wstępne:** Faza 12 · 23 (ColPali), Faza 11 (podstawy RAG)
**Czas:** ~180 minut

## Cele nauczania

- Projektowanie wyszukiwania intermodalnego: tekst → obraz, obraz → tekst, audio → wideo itp.
- Porównaj trzy strategie fuzji: fuzja wyników, fuzja oparta na uwadze, fuzja MoE.
- Wyjaśnij uziemienie pokoleń: jak wygląda „cytuj swoje źródła”, gdy źródła są mieszanką modalności.
- Wymień trzy kanoniczne multimodalne badania RAG z 2025 r. i ich taksonomię podproblemów.

## Problem

Jednomodalny RAG to rozwiązany wzorzec: osadzanie zapytania, osadzanie fragmentów, pobieranie, umieszczanie w LLM. Multimodalny RAG wymaga:

1. Wiele głowic pobierających (każda modalność wymaga osadzenia w kompatybilnej przestrzeni).
2. Połączenie wyników wyszukiwania w różnych modalnościach.
3. Ugruntowanie pokoleń, które cytuje źródła w różnych modalnościach.
4. Metryki oceny obejmujące sygnał crossmodalny.

Wszystkie badania przeprowadzone w 2025 r. opierają się na tej samej taksonomii.

## Koncepcja

### Pobieranie międzymodalne

Pobierz dokumenty modalności B na podstawie zapytania dotyczącego modalności A. Trzy wzorce:

1. Wspólna przestrzeń do osadzania. CLIP i CLAP umożliwiają osadzanie tekstu + obrazu / tekstu + dźwięku we wspólnej przestrzeni. Podobieństwo cosinusa między modalnościami działa bezpośrednio. Ograniczone do par przeszkolonych w CLIP.

2. Koder permodalny + tłumaczenie. Koder tekstu + koder obrazu + mały moduł tłumacza mapujący spacje. Sen2Sen autorstwa Gupty i in. i inne projekty 2024. Elastyczny, ale zwiększa złożoność.

3. VLM jako koder. Użyj ukrytych stanów VLM jako reprezentacji pobierania. Każda modalność obsługiwana przez VLM działa. Wyższa jakość, droższe.

Wybór: CLIP / SigLIP 2 dla tekstu+obrazu; CLAP dla tekstu i dźwięku; Stany ukryte za pomocą VLM dla połączeń międzymodalnych o granicznej jakości.

### Strategie fuzyjne

Pobrałeś 10 wyników: 5 obrazów, 3 fragmenty tekstu, 2 klipy audio. Jak się łączycie?

Fuzja partytur (najtańsza). Każda modalność ma swojego własnego retrievera, każdy zwraca wyniki. Normalizuj wyniki w ramach modalności, a następnie sumuj. Proste, często działa.

Fuzja oparta na uwadze. Połącz wszystkie odzyskane elementy i pozwól, aby niewielka sieć uwagi je zważyła. Potrzebuje szkolenia.

Fuzja MoE. Bramkowanie tras sieciowych do ekspertów zajmujących się konkretną modalnością. Różne typy zapytań kierują się w różny sposób – pytanie wizualne nadaje obrazom większą wagę.

Domyślne ustawienia produkcyjne: fuzja wyników z lekkim odchyleniem w stronę dominującej modalności zapytania. Przejdź na MoE, jeśli A/B wyraźnie wygrywa w Twojej domenie.

### Uziemienie generacji

LLM powinien podać, który odzyskany przedmiot był podstawą każdego roszczenia. W przypadku transportu multimodalnego:

- Źródło tekstu: cytat standardowy `[1]`.
- Źródło obrazu: `[img 3]` z krótkim podpisem.
- Dźwięk: `[audio 2 at 0:34]`.

Trenuj generator za pomocą danych uwzględniających uziemienie: każde oświadczenie w celu szkoleniowym jest oznaczone indeksem źródłowym. Podsumowując, model w naturalny sposób generuje cytaty.

### Ankiety z 2025 r

Abootorabi i in. (arXiv:2502.08826, „Zapytaj w dowolnej modalności”): taksonomia multimodalnego RAG. Obejmuje odzyskiwanie, fuzję i generowanie. Najszerszy zasięg.

Mei i in. (arXiv:2504.08748, „A Survey of Multimodal RAG”): skupia się na wzorcach podzadań i trybach awarii. Przydatne przy projektowaniu ewaluacji.

Zhao i in. (arXiv:2503.18016): badanie skupiające się na wizji. Mocny w pracy z rodziną ColPali.

Przeczytanie wszystkich trzech daje aktualny stan wiedzy na wiosnę 2025 r. Większość podproblemów jest nadal otwarta.

### MuRAG — artykuł założycielski

MuRAG (Chen i in., 2022) był pierwszym multimodalnym RAG. Pobrano obraz + tekst z multimodalnego KB, wygenerowano odpowiedzi. Pokazano wykonalność przed falą VLM. Na tym bazują nowoczesne systemy (REACT, VisRAG, M3DocRAG).

### Przykład planowania podróży produkcyjnych

Zapytanie: „znajdź mi spokojny wegański brunch z naturalnym światłem”.

Rurociąg:

1. Rozłóż zapytanie. „cichy” → słowo kluczowe audio/recenzja; „wegański brunch” → pozycja menu; „naturalne światło” → funkcja obrazu.
2. Pobierz według modalności:
   - Wyszukiwanie tekstu recenzji: „wegański brunch, spokojna atmosfera”.
   - Wyszukiwanie obrazu na zdjęciach restauracji: „naturalne światło, przestronność”.
   - Pobieranie dźwięku w klipach z dźwiękiem otoczenia: „niski poziom decybeli, brak muzyki”.
3. Wyniki bezpieczników. Każda restauracja ma złożony wynik.
4. Top-k restauracji → Generator VLM ze wszystkimi dowodami → odpowiedz z cytatami.

To znacznie wykracza poza tekst-RAG. Każda modalność dodaje sygnał, który pomija sam tekst.

### Agentyczny multimodalny RAG

Multi-hop: jeśli pierwsze wyszukanie nie zwróci odpowiedzi o wysokim stopniu pewności, LLM ponownie formułuje i pobiera ponownie. Obowiązują tutaj agentyczne wzorce RAG z fazy 14. Przykłady:

- Pobierz początkowe 10 najlepszych → LLM pyta „zbyt głośno, filtr dla <40 dB” → pobierz ponownie.
- Pobierz obrazy → LLM widzi, że masz menu → pobierz tekst menu → odpowiedź.

Zwiększa złożoność, ale obsługuje zapytania, których nie można pobrać jednorazowo.

### Ocena

Ocena międzymodalna jest wciąż niedojrzała. Typowe proxy:

- Recall@k według modalności.
- Połączona dokładność najwyższej k.
- Kompleksowa satysfakcja oceniana przez człowieka.
- Zadaniowe (zakończone rezerwacje, dokonane zakupy).

Żaden standardowy test porównawczy nie obejmuje wszystkich modalności. Większość artykułów ocenia zadania specyficzne dla danej dziedziny.

## Użyj tego

`code/main.py`:

- Trzy próbne aportery (tekst, obraz, dźwięk) działające we wspólnym korpusie restauracji.
- Fuzja wyników, która łączy wyniki modalności z konfigurowalnymi wagami.
- Odcinek generatora, który emituje ostateczną odpowiedź z cytatami.
- Prosta pętla agenta, która przeformułuje zapytanie, jeśli pewność jest niska.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-multimodal-rag-designer.md`. Biorąc pod uwagę specyfikację produktu z multimodalnym przepływem zapytań, projektuje moduły pobierające, fuzję, generator i ocenę.

## Ćwiczenia

1. Zaproponuj multimodalny RAG medyczno-triage: zapytanie = zdjęcie urazu + tekst objawów. Jakie modalności pobierane są z jakiego KB?

2. Fuzja wyników to prosta suma ważona. Jakiego trybu awarii ma unikanie fuzji MoE?

3. Przeczytaj taksonomię Abootorabiego i wsp. (część 3). Jakie są trzy kanoniczne podproblemy i jak odnoszą się one do wybranego przez Ciebie produktu?

4. Zaprojektuj specyfikację ewaluacyjną dla multimodalnego RAG do planowania podróży. Jakie wskaźniki obejmują przypominanie obrazu, przypominanie dźwięku i poprawność kompozycji?

5. Agentic multi-hop RAG ma podatek za opóźnienia w obie strony. Przy jakiej trudności zapytania wzrost dokładności uzasadnia opóźnienie?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Wyszukiwanie międzymodalne | „Zapytaj o jedną modalność, pobierz inną” | Zapytanie tekstowe pobiera obrazy; zapytanie obrazowe pobiera tekst; wymaga wspólnej przestrzeni lub tłumacza |
| Fuzja partytur | „Połącz wyniki” | Ważona suma wyników wyszukiwania według modalności; najprostsza fuzja |
| Fuzja MoE | „Eksperci ukierunkowani na modalność” | Sieć bramkująca wybiera dla zapytania wyniki modalności, którym można zaufać |
| Generacja uziemiona | „Podaj źródła” | Każde twierdzenie w odpowiedzi oznaczone indeksem źródłowym |
| MuRAG | „Pierwszy multimodalny RAG” | Artykuł z 2022 r., w którym ustalono multimodalny wzór RAG |
| Agentyczny multi-hop | „Przeformułuj i spróbuj ponownie” | LLM ponownie wysyła zapytania do retrieverów, gdy pewność pierwszego przejścia jest niska |

## Dalsze czytanie

- [Abootorabi i in. — Zapytaj w dowolny sposób (arXiv:2502.08826)](https://arxiv.org/abs/2502.08826)
- [Mei i in. — Badanie multimodalnych RAG (arXiv:2504.08748)](https://arxiv.org/abs/2504.08748)
- [Zhao i in. — Ankieta Vision RAG (arXiv:2503.18016)](https://arxiv.org/abs/2503.18016)
- [Chen i in. — MuRAG (arXiv:2210.02928)](https://arxiv.org/abs/2210.02928)
- [Liu i in. — REAKTUJ (arXiv:2301.10382)](https://arxiv.org/abs/2301.10382)