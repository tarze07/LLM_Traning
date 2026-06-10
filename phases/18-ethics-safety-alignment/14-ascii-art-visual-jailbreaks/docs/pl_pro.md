# Grafika ASCII i wizualne jailbreaki

> Jiang, Xu, Niu, Xiang, Ramasubramanian, Li, Poovendran, „ArtPrompt: ASCII Art-based Jailbreak Attacks Against Aligned LLMs” (ACL 2024, arXiv:2402.11753). Atak polega na zamaskowaniu tokenów kluczowych dla bezpieczeństwa w szkodliwym żądaniu, zastąpieniu ich literami wyrenderowanymi w formacie grafiki ASCII i wysłaniu tak zamaskowanego promptu. Modele GPT-3.5, GPT-4, Gemini, Claude oraz Llama-2 nie radzą sobie z bezpiecznym rozpoznawaniem tokenów przedstawionych w formacie grafiki ASCII. Atak skutecznie omija filtry perpleksji (PPL), mechanizmy obronne oparte na parafrazowaniu oraz retokenizację. Powiązane: benchmark ViTC mierzy zdolność rozpoznawania niesemantycznych promptów wizualnych; badanie *StructuralSleight* uogólnia stosowanie rzadkich struktur kodowanych tekstem (UTES, takich jak drzewa, grafy, zagnieżdżony format JSON) jako całą rodzinę ataków opartych na specyficznym kodowaniu.

**Typ:** Koduj i testuj
**Języki:** Python (stdlib, środowisko maskowania tokenów ArtPrompt)
**Wymagania wstępne:** Faza 18 · 12 (PAIR), Faza 18 · 13 (MSJ)
**Czas:** ~60 minut

## Cele nauczania

- Opisz algorytm ataku ArtPrompt: etap identyfikacji słów kluczowych, generowanie glifów w formacie grafiki ASCII oraz składanie ostatecznego zamaskowanego promptu.
- Wyjaśnij, dlaczego standardowe mechanizmy obronne (filtry perpleksji, parafrazowanie, retokenizacja) zawodzą w zderzeniu z ArtPrompt.
- Zdefiniuj benchmark ViTC i opisz, jakie właściwości modeli mierzy.
- Opisz koncepcję *StructuralSleight* jako uogólnienie ataków wykorzystujących dowolne, rzadkie struktury kodowane tekstem.

## Problem

Klasyczne ataki oparte na parafrazowaniu i odgrywaniu ról (Lekcja 12) oraz te wykorzystujące długi kontekst (Lekcja 13) operują na poziomie analizy semantyki tekstu. ArtPrompt działa na poziomie percepcji: model nie napotyka wprost zabronionego tokena tekstowego. Zaintast tego przetwarza obraz wyrenderowany przy użyciu znaków pisarskich. Filtr bezpieczeństwa widzi jedynie nieszkodliwe znaki interpunkcyjne i spacje, podczas gdy odpowiednio sprawny model odczytuje z nich zakazane słowo.

## Koncepcja

### Dwuetapowa procedura ArtPrompt

Krok 1. Identyfikacja słów kluczowych. W odpowiedzi na szkodliwe żądanie atakujący model LLM identyfikuje słowa kluczowe kluczowe dla bezpieczeństwa (np. słowo „bomba” w zdaniu „jak skonstruować bombę”).

Krok 2. Generowanie zamaskowanego promptu. Każde ze zidentyfikowanych słów jest zastępowane jego odpowiednikiem wyrenderowanym w formacie ASCII (blok znaków o wymiarach 7x5 lub 7x7 układający się w kształt danej litery). Model docelowy otrzymuje siatkę znaków interpunkcyjnych i spacji, które potrafi odczytać jako słowo, podczas gdy filtr bezpieczeństwa widzi w nich jedynie bezużyteczny szum znaków.

Wynik: Modele GPT-4, Gemini, Claude, Llama-2 oraz GPT-3.5 uległy tym próbom. Wskaźnik skuteczności ataku (ASR) przekroczył 75% na testowych zestawach danych.

### Dlaczego standardowe mechanizmy obronne zawodzą

- **Filtry perpleksji (PPL).** Grafika ASCII charakteryzuje się wysoką wartością perpleksji (perplexity) – podobnie jednak jak wszelkie nietypowe dane wejściowe. Ustawienie progów filtrów tak czule, by blokowały one ArtPrompt, skutkuje odrzucaniem wielu poprawnych, strukturalnych zapytań użytkowników.
- **Parafrazowanie promptów.** Przetworzenie promptu przez model parafrazujący powinno w teorii zniszczyć strukturę grafiki ASCII. W praktyce jednak modele parafrazujące LLM często zachowują lub wręćz rekonstruują te wzorce wizualne.
- **Retokenizacja.** Zmiana sposobu podziału tekstu na tokeny nie eliminuje zdolności modelu do rozpoznawania kształtów liter na poziomie percepcji wizualnej.

Główna przyczyna tkwi w tym, że filtry bezpieczeństwa operują na poziomie tokenów lub analizy semantycznej, podczas gdy ArtPrompt wykorzystuje mechanizmy wizualnego rozpoznawania kształtów.

### Benchmark ViTC

ViTC służy do oceny zdolności rozpoznawania niesemantycznych promptów wizualnych. Mierzy on sprawność modelu w odczytywaniu grafiki ASCII, czcionek symbolicznych (np. wingdings) oraz innych wizualnych treści zakodowanych tekstowo. Skuteczność ataku ArtPrompt koreluje bezpośrednio z dokładnością modelu w benchmarku ViTC: im lepiej model radzi sobie z interpretacją tekstu wizualnego, tym łatwiej ulega manipulacji za pomocą ArtPrompt. Stanowi to klasyczny kompromis między zdolnościami modelu a jego bezpieczeństwem.

### Rzadkie struktury kodowane tekstem (StructuralSleight)

Koncepcja ta uogólnia atak ArtPrompt na inne rzadkie struktury kodowane tekstem (Uncommon Text-Encoded Structures, UTES). Obejmuje ona grafy, drzewa, zagnieżdżony format JSON, tabele CSV osadzone w plikach JSON czy bloki kodu w formacie różnicowym (diff). Jeśli dana struktura rzadko pojawiała się w danych treningowych związanych z bezpieczeństwem, lecz model potrafi ją poprawnie zinterpretować, może posłużyć do przemycenia szkodliwych instrukcji.

Wniosek dla systemów obronnych: mechanizmy bezpieczeństwa muszą poprawnie uogólniać reguły na wszelkie ustrukturyzowane reprezentacje danych, które model jest w stanie przetworzyć. Zbiór tych struktur jest ogromny i stale rośnie.

### Odpowiedniki w modalności wizualnej (obrazy)

Multimodalne modele LLM (przetwarzające obraz) znacząco poszerzają przestrzeń zagrożeń. Ataki w stylu ArtPrompt wykorzystujące rzeczywiste pliki graficzne wykazują znacznie większą skuteczność niż ich tekstowe odpowiedniki ASCII, jako że kodery obrazu (vision encoders) dostarczają do modelu znacznie bogatszy sygnał informacyjny.

### Miejsce w strukturze Fazy 18

Lekcje 12-14 opisują trzy niezależne wektory ataków: optymalizację iteracyjną (PAIR), wykorzystanie długości kontekstu (MSJ) oraz manipulację kodowaniem (ArtPrompt/StructuralSleight). Lekcja 15 przenosi środek ciężkości z ataków bezpośrednich na ataki na granicy systemu (pośrednie wstrzykiwanie promptów). Lekcja 16 przedstawia narzędzia i metody defensywne.

## Użycie kodu

Plik `code/main.py` implementuje uproszczony schemat ArtPrompt. Pozwala on zastąpić wybrane słowa w szkodliwym zapytaniu glifami ASCII, zweryfikować, czy tak zmodyfikowany ciąg omija prosty filtr słów kluczowych, oraz podjąć próbę zdekodowania znaków z powrotem na tekst przy użyciu prostego algorytmu rozpoznawania kształtów.

## Co otrzymasz

Ta lekcja przygotowuje plik `outputs/skill-encoding-audit.md`. Na podstawie raportu z testów odporności dokument ten klasyfikuje zbadane rodziny ataków opartych na kodowaniu (grafika ASCII, Base64, leet-speak, homoglify UTF-8, struktury UTES) i określa mechanizmy obronne chroniące przed każdym z tych wektorów.

## Ćwiczenia

1. Uruchom `code/main.py`. Sprawdź, czy zakodowany ciąg znaków omija prosty filtr słów kluczowych. Zgłoś niezbędne zmiany na poziomie parametrów klasyfikatora.

2. Zaimplementuj alternatywne kodowanie: zakoduj to samo słowo kluczowe w formacie Base64. Porównaj skuteczność ominięcia filtra z wynikami metody ArtPrompt oraz przeanalizuj trudność odzyskania tekstu przez model.

3. Zapoznaj się z sekcją 4.3 w pracy Jiang i in. (2024) (wyniki dla pięciu modeli). Zaproponuj hipotezę wyjaśniającą, dlaczego model Claude wykazuje wyższą odporność na ataki ArtPrompt niż Gemini w tej samej konfiguracji testowej.

4. Zaprojektuj regułę obronną (input filter), która wykrywa w promptach wejściowych obszary o strukturze grafiki ASCII. Zmierz odsetek błędnych odrzuceń (false positives) dla poprawnych bloków kodu, tabel tekstowych oraz zapisów matematycznych.

5. W pracy StructuralSleight wymieniono 10 typowych struktur kodowania. Zaproponuj koncepcję uniwersalnej obrony obsługującej wszystkie te struktury i oszacuj jej narzut obliczeniowy w przeliczeniu na pojedyncze zapytanie użytkownika.

## Kluczowe terminy

| Termin | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|--------------------------------------|
| ArtPrompt | „atak grafiką ASCII” | Dwuetapowa metoda jailbreaku maskująca słowa kluczowe za pomocą ich wizualnych odpowiedników ASCII |
| Maskowanie (Cloaking) | „ukrywanie słów” | Zastępowanie zabronionych tokenów ich reprezentacją wizualną, którą model potrafi zinterpretować, lecz prosty filtr ją pomija |
| UTES | „rzadkie struktury” | Rzadkie struktury kodowane tekstem (drzewa, grafy, zagnieżdżony JSON), wykorzystywane do przemycania szkodliwych treści |
| ViTC | „odczytywanie tekstu wizualnego” | Benchmark oceniający sprawność modelu w interpretacji niesemantycznych reprezentacji wizualnych |
| Filtr perpleksji (Perplexity filter) | „obrona PPL” | Blokowanie promptów o wysokiej wartości perpleksji; może odrzucać poprawne, ustrukturyzowane zapytania |
| Retokenizacja (Retokenization) | „zmiana podziału na tokeny” | Przetwarzanie wejściowego promptu innym tokenizerem; nie chroni przed interpretacją wizualną |
| Homoglify (Homoglyphs) | „łudząco podobne znaki” | Znaki Unicode o wyglądzie identycznym z literami alfabetu łacińskiego, stosowane do obchodzenia filtrów tekstowych |

## Dalsze czytanie

- [Jiang et al. — ArtPrompt (ACL 2024, arXiv:2402.11753)](https://arxiv.org/abs/2402.11753) – publikacja opisująca jailbreak oparty na grafice ASCII
- [Li et al. — StructuralSleight (arXiv:2406.08754)](https://arxiv.org/abs/2406.08754) – praca opisująca ataki z wykorzystaniem struktur UTES
- [Chao et al. — PAIR (Lekcja 12, arXiv:2310.08419)](https://arxiv.org/abs/2310.08419) – opis komplementarnego ataku iteracyjnego
- [Anil et al. — Many-shot Jailbreaking (Lekcja 13)](https://www.anthropic.com/research/many-shot-jailbreaking) – opis komplementarnego ataku wykorzystującego długi kontekst
