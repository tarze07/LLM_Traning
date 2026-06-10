# STAR, V-STAR, Quiet-STAR — Rozumowanie samouka

> Najmniejsza możliwa pętla samodoskonalenia znajduje się w procesie uzasadniania. Model generuje łańcuch myśli (chain of thought), zachowuje te próby, które prowadzą do prawidłowych odpowiedzi, i na nich się dostraja. To jest istota metody STAR. V-STAR dodaje do tego weryfikator, dzięki czemu wybór w czasie wnioskowania (inference-time selection) jest trafniejszy. Quiet-STAR wprowadza generowanie wewnętrznych uzasadnień dla każdego tokenu. Wszystkie te trzy podejścia działają, ale żadne nie jest magiczne – pętla utrwala każdy skrót myślowy, który doprowadził do właściwej odpowiedzi.

**Typ:** Ucz się
**Języki:** Python (biblioteka standardowa, symulator pętli bootstrap)
**Wymagania wstępne:** Faza 13 · 01-03 (Rozumowanie i CoT), Faza 15 · 01 (dopasowanie długoterminowe)
**Czas:** ~60 minut

## Problem

Najprostszym sposobem nauczenia modelu rozumowania jest zebranie śladów rozumowania zapisanych przez człowieka. Jest to jednak kosztowne, powolne i ograniczone ilością wysokiej jakości łańcuchów myśli, które ludzie są w stanie napisać.

Twórcy projektu STaR (Self-Taught Reasoner, Zelikman i in., 2022) zadali pytanie: co się stanie, jeśli model zacznie pisać własne uzasadnienia i porównywać je ze znanymi odpowiedziami? Pętla wygląda następująco:

1. Wygeneruj ślad rozumowania i ostateczną odpowiedź.
2. Jeśli ostateczna odpowiedź jest prawidłowa, zachowaj wygenerowany ślad.
3. Dostrój model na zachowanych śladach.
4. Powtórz procedurę.

To podejście działa. Wyniki na zbiorach GSM8K i CommonsenseQA uległy poprawie bez udziału nowych ludzkich adnotacji. Jednak ta pętla ma wbudowaną wadę: każde uzasadnienie, które dało właściwą odpowiedź, zostaje zachowane – niezależnie od tego, czy samo rozumowanie było poprawne logicznie. V-STAR (Hosseini i in., 2024) rozwiązuje ten problem za pomocą wyuczonego weryfikatora, natomiast Quiet-STAR (Zelikman i in., 2024) uogólnia tę koncepcję na wewnętrzne uzasadnienia generowane dla poszczególnych tokenów.

## Koncepcja

### STAR: bootstrapping tego, co zadziałało

Zacznij od modelu bazowego o słabych zdolnościach rozumowania. Dla każdego problemu treningowego wygeneruj uzasadnienie i odpowiedź. Jeśli odpowiedź zgadza się z etykietą referencyjną, zachowaj trójkę (problem, uzasadnienie, odpowiedź). Następnie dostrój model na tak zgromadzonym zbiorze danych i powtórz cały proces.

Jest tu jednak pewien haczyk. Jeśli model nigdy nie będzie w stanie poprawnie rozwiązać dego problemu, pętla nie będzie miała z czego się uczyć. STaR dodaje więc **racjonalizację**: w przypadku problemów, w których model zawodzi, podaj mu poprawną odpowiedź jako wskazówkę i ponownie poproś o przedstawienie uzasadnienia, które do niej prowadzi. Te zracjonalizowane uzasadnienia są również dodawane do zbioru treningowego.

Wyniki w oryginalnej pracy (Zelikman i in., 2022): bazowy model GPT-J poprawił swoją skuteczność na GSM8K z 5,8% do 10,7% po powtarzanych rundach STaR z racjonalizacją – co oznacza bezwzględny wzrost o około 5 punktów procentowych. W CommonsenseQA wyszkolony za pomocą STaR model GPT-J 6B osiągnął wynik 72,5%, co jest porównywalne z dostrojonym modelem GPT-3 175B (~73%) – czyli modelem około 30-krotnie większym, trenowanym na ręcznie tworzonych komentarzach.

### V-STaR: trenowanie weryfikatora za pomocą DPO

STAR odrzuca błędne uzasadnienia. Hosseini i in. (2024) zauważyli, że te odrzucone próby również są wartościowymi danymi: każda para (uzasadnienie, informacja „czy jest poprawne”) może posłużyć do wytrenowania weryfikatora. Autorzy używają bezpośredniej optymalizacji preferencji (DPO) na poprawnych i niepoprawnych rozwiązaniach, aby zbudować model oceniający (rankingowy). W czasie wnioskowania system generuje N uzasadnień i wybiera to, które uzyskało najwyższą ocenę weryfikatora.

Zgłaszany przyrost skuteczności: od +4 do +17 punktów procentowych w porównaniu do wcześniejszych metod samodoskonalenia na zbiorach GSM8K i MATH. Większość tych zysków wynika z zastosowania weryfikatora do selekcji rozwiązań w czasie wnioskowania, a nie z dodatkowego dostrajania generatora.

### Quiet-STAR: wewnętrzne uzasadnienie dla każdego tokenu

Zelikman i in. (2024) zapytali: co się stanie, jeśli model nauczy się generować krótkie wewnętrzne uzasadnienie na pozycji każdego tokenu, a nie tylko pomiędzy pytaniem a ostateczną odpowiedzią? Quiet-STAR trenuje model tak, aby generował ukrytą „myśl” przed każdym przewidywanym tokenem, a następnie łączy prognozę uwzględniającą tę myśl z prognozą bazową za pomocą wyuczonej wagi.

Wynik: Mistral 7B poprawił swoją skuteczność w trybie zero-shot na zbiorze GSM8K z 5,9% do 10,9%, a na CommonsenseQA z 36,3% do 47,2% bez dostrajania pod konkretne zadanie. Model nauczył się, „kiedy myśleć” – trudniejsze tokeny otrzymują dłuższe wewnętrzne uzasadnienia, podczas gdy łatwe nie otrzymują ich prawie wcale.

### Dlaczego wszystkie trzy metody stwarzają wyzwania dla bezpieczeństwa

Wszystkie trzy metody wykorzystują ostateczną odpowiedź jako sygnał gradientu. Uzasadnienie, które prowadzi do właściwej odpowiedzi poprzez błędne rozumowanie – np. wykorzystując skróty myślowe (heurystyki), zgadując lub opierając się na regule, która nie ulega generalizacji – zostaje wzmocnione. W przypadku problemów zgodnych z rozkładem danych (in-distribution) taki skrót działa. Jednak w zadaniach spoza rozkładu (out-of-distribution) zawodzi po cichu.

Weryfikator V-STAR łagodzi ten problem, ucząc się oceny poprawności uzasadnień, ale jest on szkolony na tym samym zbiorze etykiet. Może więc nauczyć się wyżej oceniać dobrze sformatowane, ale błędne rozumowanie niż szczerą niepewność. Bezpieczniejszy projekt wymaga połączenia metod w stylu STaR z: (a) modelami nagród nadzorowanymi procesowo (PRM, nagradzającymi kroki pośrednie, a nie tylko sam wynik) oraz (b) oceną na wydzielonym zbiorze OOD, która uniemożliwia stosowanie prostych skrótów.

### Porównanie

| Metoda | Sygnał treningowy | Koszt wnioskowania | Efektywność wykorzystania danych | Znany tryb awarii |
|---|---|---|---|---|
| STAR | zachowanie pary (uzasadnienie, odpowiedź), jeśli jest poprawna | 1x | niska (odrzuca wszystkie błędne uzasadnienia) | uzasadnienia oparte na skrótach myślowych |
| STAR + racjonalizacja | jak wyżej + podpowiedź z poprawną odpowiedzią | 1x | wyższa | zracjonalizowane uzasadnienia mogą być nienaturalne |
| V-STAR | STaR + weryfikator DPO szkolony na obu klasach | Nx (wybór najlepszego z N) | wysoka (minimalne marnowanie) | weryfikator może utwierdzać model w błędzie |
| Quiet-STAR | uzasadnienie dla każdego tokenu + waga mieszania | 1,5-3x | wysoka (minimalne marnowanie) | nadal zależny od gradientu warunkowanego odpowiedzią |

### Gdzie to się plasuje w technologii na rok 2026

Klasyczny STAR to starsza metoda. Jednak ten sam wzorzec powraca w latach 2025–2026. Uczenie ze wzmocnieniem (RL) w weryfikowalnych zadaniach matematycznych (DeepSeek-R1, Kimi-k1.5, o1) to w gruncie rzeczy przeskalowany sygnał gradientowy STAR warunkowany ostatecznym wynikiem. Modele nagród procesowych (Lightman i in., 2023; „Let's Verify Step by Step” od OpenAI) stanowią alternatywę nadzorowaną procesowo. AlphaEvolve (Lekcja 3) to STAR zastosowany do kodu, gdzie zamiast etykiet referencyjnych używa się automatycznego ewaluatora programów. Maszyna Darwina Gödla (Lekcja 4) stosuje koncepcję STAR do kodu samego agenta (szkieletu/rusztowania).

Zrozumienie STAR jest kluczem do pojęcia wszystkich tych systemów. Jest to minimalna działająca pętla samodoskonalenia.

## Użyj tego

Plik `code/main.py` uruchamia symulowaną pętlę STAR w prostym zadaniu arytmetycznym. Możesz zaobserwować:

- Jak dokładność rośnie w kolejnych rundach uczenia początkowego (bootstrappingu).
- Jak wkradają się skróty myślowe: symulator zawiera „leniwą” klasę generatora uzasadnień, która w 40% przypadków daje właściwą odpowiedź, ale źle się generalizuje. Zobacz, czy STAR zachowa te próby.
- W jaki sposób weryfikator (w stylu V-STAR) pomaga przy wnioskowaniu, ale nie jest w stanie całkowicie wyeliminować skrótów utrwalonych podczas treningu.

## Wdrożenie

Szablon `outputs/skill-star-loop-reviewer.md` pomaga przeprowadzić audyt proponowanego potoku rozumowania samouka przed rozpoczęciem kosztownych obliczeń treningowych.

## Ćwiczenia

1. Uruchom symulator. Ustaw częstotliwość generowania skrótów myślowych na zero, a następnie na 0,4. Jak bardzo różni się ostateczna dokładność między tymi dwoma przebiegami, mimo że w obu przypadkach model osiąga >90% na zbiorze treningowym?

2. Dodaj do symulatora wydzielony test OOD. Wygeneruj zadania z innego rozkładu i oceń model na zbiorze treningowym oraz OOD. Oblicz różnicę w wynikach.

3. Przeczytaj artykuł Quiet-STAR (arXiv:2403.09629), część 3. Wyjaśnij w trzech zdaniach rolę tokenu „końca myśli” (thought-end token) oraz głowicy mieszającej (mixing head).

4. Porównaj stosowane w STAR filtrowanie typu „zachowaj poprawne” z alternatywą nadzorowaną procesowo, która niezależnie ocenia każdy krok rozumowania. Wskaż różnice w kosztach adnotacji oraz przewidywanej jakości modeli.

5. Zaprojektuj jeden test ewaluacyjny, który ujawniłby stosowanie skrótów myślowych w gotowym do wdrożenia modelu. Test nie musi być idealny – ważne, aby uniemożliwiał przejście najprostszych heurystyk, które pętla STAR mogłaby wzmocnić.

## Kluczowe terminy

| Termin | Co mówią ludzie | Co to naprawdę oznacza |
|---|---|---|
| STAR | „Rozumujący samouk” | Dostrajanie modelu na wygenerowanych przez niego uzasadnieniach, które dały poprawne odpowiedzi; powtarzanie tego procesu |
| Racjonalizacja | „Druga próba ze wskazówką” | Podanie poprawnej odpowiedzi i ponowne żądanie uzasadnienia dla zadań, na których model bazowy poległ |
| V-STAR | „Weryfikator STAR” | Wytrenowanie weryfikatora za pomocą DPO na poprawnych i błędnych uzasadnieniach; użycie go przy wyborze odpowiedzi w czasie wnioskowania |
| Quiet-STAR | „Uzasadnienia na poziomie tokenów” | Generowanie ukrytych myśli na pozycji każdego tokenu i łączenie ich z prognozą bazową |
| Gradient warunkowany odpowiedzią | „Sygnał oparty na wyniku” | Pętla treningowa nagradza ostateczny wynik, a nie poprawność poszczególnych kroków rozumowania |
| Model nagrody procesu | „Weryfikator krok po kroku” | Model nagrody oceniany pod kątem poprawności poszczególnych etapów wnioskowania, a nie samego wyniku końcowego (w przeciwieństwie do STAR) |
| Uzasadnienie oparte na skrócie | „Poprawna odpowiedź, błędne rozumowanie” | Uzasadnienie prowadzące do dobrej etykiety poprzez regułę, która nie ulega generalizacji; STAR utrwala takie przypadki |

## Dalsze czytanie

- [Zelikman i in. (2022). STAR: Bootstrapping Reasoning With Reasoning](https://arxiv.org/abs/2203.14465) – oryginalna publikacja.
- [Hosseini i in. (2024). V-STAR: Training Verifiers for Self-Taught Reasoners](https://arxiv.org/abs/2402.06457) – rozszerzenie o weryfikator DPO.
- [Zelikman i in. (2024). Quiet-STAR: Language Models Can Teach Themselves to Think Before Speaking](https://arxiv.org/abs/2403.09629) – wewnętrzne uzasadnienia na poziomie tokenów.
- [Lightman i in. (2023). Let's Verify Step by Step](https://arxiv.org/abs/2305.20050) – modele nagród procesowych jako alternatywny sygnał uczenia.
- [Publikacja DeepSeek-R1 (arXiv:2501.12948)](https://arxiv.org/abs/2501.12948) – uczenie ze wzmocnieniem na weryfikowalnych zadaniach, czyli STaR przeskalowany do poziomu modeli bazowych.
