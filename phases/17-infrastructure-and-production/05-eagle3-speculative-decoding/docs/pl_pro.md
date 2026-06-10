# Dekodowanie spekulatywne EAGLE-3 w produkcji

> Dekodowanie spekulatywne (speculative decoding) łączy szybki, lekki model pomocniczy (draft model) z dużym modelem docelowym (target model). Model pomocniczy proponuje sekwencję $K$ tokenów, a model docelowy weryfikuje je wszystkie w jednym kroku propagacji w przód (forward pass) – każdy zaakceptowany token nie generuje dodatkowego kosztu obliczeniowego. W 2026 roku standardem produkcyjnym staje się technologia EAGLE-3. Uczy ona głowicę modelu pomocniczego (draft head) przewidywania na podstawie ukrytych stanów (hidden states) modelu docelowego, a nie samych tokenów wyjściowych. Pozwala to podnieść współczynnik akceptacji $\alpha$ do poziomu 0.6–0.8 w zadaniach konwersacyjnych. Kluczowym pytaniem wdrożeniowym nie jest „jak szybki jest model pomocniczy”, lecz „ile wynosi współczynnik $\alpha$ przy moim rzeczywistym ruchu”. Jeśli wartość $\alpha$ spadnie poniżej ~0.55, dekodowanie spekulatywne zacznie generować straty przy wysokiej współbieżności zapytań, ponieważ odrzucenie propozycji modelu pomocniczego wymusza wykonanie dodatkowego kroku weryfikacyjnego na modelu docelowym. Ta lekcja uczy, jak zmierzyć wskaźnik $\alpha$ przed włączeniem tej optymalizacji na produkcji.

**Typ:** Teoria (Learn)
**Języki:** Python (stdlib, prosty symulator współczynnika akceptacji)
**Wymagania wstępne:** Faza 17 · 04 (Wewnętrzne mechanizmy serwowania vLLM), faza 10 · 18 (Predykcja wielotokenowa)
**Czas:** ~60 minut

## Cele nauczania

- Poznaj trzy generacje algorytmów dekodowania spekulatywnego i dowiedz się, czym różni się EAGLE-3 od EAGLE-2 oraz od klasycznego podejścia opartego na osobnym modelu pomocniczym.
- Zdefiniuj współczynnik akceptacji $\alpha$, oblicz szacowane przyspieszenie na podstawie wartości $\alpha$ oraz $K$ (długości propozycji modelu pomocniczego) i wyznacz próg rentowności $\alpha$ dla określonej współbieżności zapytań.
- Wyjaśnij, dlaczego dekodowanie spekulatywne jest funkcją opcjonalną w vLLM i dlaczego włączanie go bez pomiaru wskaźnika $\alpha$ jest antywzorcem produkcyjnym.
- Przygotuj plan pomiarowy: dobór zestawu testowego, rozkład promptów wejściowych, określenie punktów pomiaru współbieżności oraz wybór kluczowych metryk.

## Problem

Generowanie tokenów (faza decode) jest ograniczone przepustowością pamięci (memory-bound). Na układzie H100 serwującym model Llama 3.3 70B FP8, każdy wygenerowany token wymaga odczytania z pamięci wag o rozmiarze ok. 140 GB i emituje tylko jeden token. Podczas dekodowania jednostki obliczeniowe GPU są niemal bezczynne – wąskim gardłem jest przepustowość pamięci HBM, a nie wydajność operacji mnożenia macierzy (matmul).

Dekodowanie spekulatywne pozwala wykorzystać te wolne moce obliczeniowe. Generujemy $K$ tokenów kandydatów za pomocą taniego modelu pomocniczego, a następnie zlecamy modelowi docelowemu weryfikację całej paczki $K$ tokenów w jednym kroku forward pass. Każdy zaakceptowany token jest w praktyce darmowy (amortyzowany w ramach weryfikacji paczki $K$ tokenów, którą model docelowy i tak musiałby przetworzyć).

Klasyczne podejście do dekodowania spekulatywnego wykorzystuje mniejszy model z tej samej rodziny (np. Llama 3.2 1B jako model pomocniczy dla Llama 3.3 70B). Rozwiązanie to działa, ale współczynnik akceptacji bywa przeciętny – rozkład prawdopodobieństwa małego modelu różni się od modelu docelowego. Algorytmy z rodziny EAGLE (EAGLE, EAGLE-2, a obecnie EAGLE-3) trenują lekką głowicę pomocniczą (draft head) bezpośrednio na stanach wewnętrznych modelu docelowego, dzięki czemu propozycje modelu pomocniczego znacznie lepiej odzwierciedlają rozkład modelu głównego. Pozwala to podnieść wskaźnik $\alpha$ z poziomu 0.4 (dla tradycyjnego małego modelu pomocniczego) do 0.6–0.8 dla EAGLE-3.

Należy pamiętać, że EAGLE-3 jest funkcją opcjonalną w vLLM. Parametr `speculative_config` musi zostać jawnie zdefiniowany. Bez odpowiedniej konfiguracji optymalizacja nie zostanie uruchomiona. Zespoły, które włączają tę opcję bez uprzedniego zmierzenia wskaźnika $\alpha$ dla rzeczywistego ruchu użytkowników, często obserwują wzrost opóźnień (zwłaszcza dla długiego ogona dystrybucji), zamiast ich spadku.

## Koncepcja

### Rzeczywiste zyski z dekodowania spekulatywnego

Bez dekodowania spekulatywnego koszt wygenerowania jednego tokena to jeden krok propagacji w przód modelu docelowego. Przy wdrożeniu dekodowania spekulatywnego dla długości propozycji $K$ i współczynnika akceptacji $\alpha$, oczekiwana liczba wygenerowanych tokenów na jeden krok forward pass modelu docelowego wynosi `1 + K * alpha`. Teoretyczne przyspieszenie określa wzór: `(1 + K * alpha) / (1 + epsilon)`, gdzie `epsilon` oznacza narzut związany z uruchomieniem modelu pomocniczego i weryfikacją. Dla parametrów $K=5$ i $\alpha=0.7$ otrzymujemy: `(1 + 5 * 0.7) / (1 + 0.1) = 4.5 / 1.1 = 4.1x`. W rzeczywistych warunkach produkcyjnych uzyskujemy przyspieszenie rzędu 2-3x, ponieważ wskaźnik $\alpha$ rzadko utrzymuje się na tak wysokim poziomie dla zróżnicowanego ruchu, a parametr `epsilon` rośnie wraz z rozmiarem paczki (batch size).

### Dlaczego współczynnik akceptacji $\alpha$ jest kluczowy?

Odrzucone tokeny nie znikają bez śladu – w przypadku odrzucenia propozycji modelu pomocniczego, pierwszy odrzucony token wymusza wykonanie dodatkowego kroku forward pass na modelu docelowym. Jeśli dla danego obciążenia wskaźnik $\alpha$ spada do poziomu 0.4, koszty uruchamiania modelu pomocniczego, weryfikacji i ponownego generowania przewyższają zyski. Przy wysokiej współbieżności (np. 256 aktywnych zapytań) wsad (batch) w fazie decode jest na tyle duży, że różnica w przepustowości pamięci między samym modelem docelowym a wariantem z weryfikacją maleje. Na większości sprzętu w 2026 roku, przy współczynniku $\alpha$ poniżej 0.55, dekodowanie spekulatywne staje się nieopłacalne.

Wskaźnik $\alpha$ silnie zależy od charakteru zapytań. W ogólnych zadaniach konwersacyjnych (np. na zestawie ShareGPT), głowica EAGLE-3 przeszkolona na tych danych osiąga $\alpha$ na poziomie 0.6–0.8. Jednak w przypadku ruchu wysoce specjalistycznego (kod źródłowy, medycyna, prawo), głowica wytrenowana na ogólnych tekstach notuje spadek $\alpha$ do 0.4–0.6. Wytrenowanie dedykowanej głowicy dla konkretnej domeny pozwala przywrócić wysoki wskaźnik $\alpha$ – jest to proces lekki i szybki w porównaniu z pełnym dostrajaniem (fine-tuning) modelu głównego.

### Ewolucja technologii EAGLE

- **Klasyczny model pomocniczy (draft model):** Osobny, mały model z tej samej rodziny. Wskaźnik $\alpha$ w zakresie 0.3–0.5. Architektura jest prosta (ładowane są dwa niezależne modele, na każdy krok forward pass modelu docelowego przypada $K$ kroków modelu pomocniczego).
- **EAGLE-1 (2024):** Pojedyncza głowica trenowana na ukrytych stanach (hidden states) ostatniej warstwy modelu docelowego. Wskaźnik $\alpha$ w zakresie ~0.5–0.6. Minimalny narzut pamięciowy ponad model główny.
- **EAGLE-2 (2025):** Adaptacyjna długość sekwencji propozycji oraz generowanie propozycji w strukturze drzewa (tree-based draft), umożliwiające weryfikację wielu gałęzi w jednym kroku forward pass modelu głównego. Wskaźnik $\alpha$ w zakresie ~0.6–0.7. Zwiększona złożoność harmonogramu zapytań.
- **EAGLE-3 (2025-2026):** Głowica pomocnicza trenowana na wielu warstwach modelu docelowego (nie tylko na ostatniej), zapewniająca lepsze dopasowanie. Wskaźnik $\alpha$ w zakresie ~0.6–0.8 w zadaniach konwersacyjnych.

### Instrukcja wdrożenia produkcyjnego

1. Uruchom produkcyjnie standardowy model docelowy. Zmierz bazową przepustowość, wartości parametrów TTFT oraz ITL przy docelowym natężeniu ruchu.
2. Włącz obsługę EAGLE-3 za pomocą parametru `speculative_config` w vLLM. Uruchom ponownie testy porównawcze.
3. Monitoruj i rejestruj wskaźnik akceptacji $\alpha$. Silnik vLLM raportuje tę metrykę jako `spec_decode_metrics.accepted_tokens_per_request`. Podziel tę wartość przez zdefiniowaną długość propozycji $K$, aby wyznaczyć współczynnik $\alpha$.
4. Jeśli wskaźnik $\alpha$ dla rzeczywistego ruchu produkcyjnego spadnie poniżej 0.55, wyłącz dekodowanie spekulatywne lub wytrenuj dedykowaną głowicę EAGLE-3 dla swojej domeny.
5. Przeprowadź testy obciążeniowe przy docelowej współbieżności. Upewnij się, że percentyl P99 ITL nie uległ pogorszeniu.

### Pułapka produkcyjna: opóźnienia długiego ogona (percentyl P99)

Chociaż wdrożenie dekodowania spekulatywnego zazwyczaj obniża średnią wartość ITL, brak odpowiedniej optymalizacji może pogorszyć percentyl P99. Odrzucone propozycje modelu pomocniczego wymuszają sekwencję dwóch operacji (generowanie propozycji + weryfikacja zakończona niepowodzeniem + ponowne generowanie). Przy pełnym wysyceniu klastra te dodatkowe kroki są kolejkowane sekwencyjnie. Podczas wdrożenia monitoruj percentyl P99 ITL, a nie tylko średnią lub medianę (P50).

### Zastosowania rynkowe

Firma Google wdrożyła dekodowanie spekulatywne w swoich podsumowaniach wyszukiwania (AI Overviews) w 2025 roku w celu skrócenia czasu odpowiedzi. vLLM udostępnia parametr `speculative_config` jako standardowy interfejs; jądro dekodowania spekulatywnego N-gram na GPU jest rozwiązaniem w pełni kompatybilnym z chunked prefill. SGLang rekomenduje stosowanie EAGLE-3 jako domyślnego mechanizmu dla zadań wymagających intensywnego przetwarzania wspólnych prefiksów w pamięci podręcznej (prefix caching).

### Uproszczony wzór progu rentowności

Teoretyczne przyspieszenie określa wzór: `S(alpha, K) = (1 + K * alpha) / (1 + verify_overhead)`. Podstawienie `S = 1` pozwala wyznaczyć próg rentowności dla wskaźnika $\alpha$: `alpha_breakeven = verify_overhead / K`. Przy typowym narzucie weryfikacji na poziomie ~0.15 i długości propozycji $K=5$, otrzymujemy `alpha_breakeven = 0.03`. Jest to jednak kalkulacja czysto teoretyczna dla pojedynczego zapytania. W warunkach wysokiej współbieżności narzut weryfikacji rośnie, a duże paczki (batch) i tak amortyzują odczyty wag z pamięci, przez co w praktyce rzeczywisty próg opłacalności `alpha_breakeven` wzrasta do poziomu ~0.45–0.55.

### Kiedy unikać dekodowania spekulatywnego?

- Przetwarzanie wsadowe offline (batch) o rozmiarze paczki 1, gdzie opóźnienie pojedynczej odpowiedzi nie ma znaczenia. Używaj standardowego modelu docelowego.
- Bardzo krótkie odpowiedzi (poniżej 50 tokenów) – koszty inicjalizacji i weryfikacji dominują nad zyskami.
- Specjalistyczne dziedziny wiedzy, dla których nie przeszkolono dedykowanej głowicy pomocniczej – współczynnik $\alpha$ będzie zbyt niski.
- Silnik vLLM w wersji v0.18.0 przy próbie jednoczesnego włączenia dekodowania spekulatywnego z zewnętrznym modelem pomocniczym oraz chunked prefill (`--enable-chunked-prefill`). Taka konfiguracja nie skompiluje się; jedynym wyjątkiem jest jądro N-gram na GPU.

## Użyj tego

Skrypt `code/main.py` symuluje pętlę generowania odpowiedzi z dekodowaniem spekulatywnym oraz bez niego, analizując wyniki dla różnych wartości współczynnika $\alpha$ i długości propozycji $K$. Zwraca on próg rentowności dla wskaźnika $\alpha$, zmierzone przyspieszenie oraz zachowanie opóźnień dla długiego ogona dystrybucji. Uruchom symulację dla różnych kombinacji parametrów ($\alpha$, $K$), aby sprawdzić, kiedy stosowanie dekodowania spekulatywnego przestaje być opłacalne.

## Wdróż to (Ship It)

Do tej lekcji dołączono narzędzie `outputs/skill-eagle3-rollout.md`. Na podstawie wybranego modelu docelowego, charakterystyki ruchu użytkowników oraz planowanej współbieżności wygeneruje ono etapowy plan wdrożenia technologii EAGLE-3 – od testów porównawczych, przez konfigurację parametrów, pomiar wskaźnika $\alpha$, po weryfikację stabilności percentyla P99 ITL.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Przy długości propozycji $K=5$, jaka wartość współczynnika $\alpha$ jest wymagana do uzyskania 2-krotnego przyspieszenia generacji? A dla 3-krotnego? Przeanalizuj, jak te wyniki zależą od parametru narzutu weryfikacji (`verify_overhead`).
2. Załóżmy, że ruch produkcyjny w Twojej aplikacji składa się w 70% z ogólnych konwersacji czatowych, a w 30% z zapytań programistycznych (pisanie kodu). W zadaniach czatowych głowica EAGLE-3 (trenowana na ShareGPT) osiąga $\alpha=0.7$, natomiast w zadaniach programistycznych wskaźnik ten spada do $\alpha=0.4$. Oblicz średni wskaźnik $\alpha$ dla całego systemu i określ, czy wdrożenie dekodowania spekulatywnego będzie w tym przypadku opłacalne.
3. Przeanalizuj parametry konfiguracyjne `speculative_config` w silniku vLLM. Wskaż trzy obsługiwane tryby (model pomocniczy, EAGLE, N-gram) i określ, który z nich jest kompatybilny z chunked prefill.
4. Po włączeniu głowicy EAGLE-3 średnia wartość wskaźnika ITL spadła o 25%, jednak percentyl P99 ITL wzrósł o 15%. Zdiagnozuj przyczynę tego zachowania i zaproponuj rozwiązanie optymalizacyjne.
5. Oblicz narzut pamięciowy (VRAM) generowany przez głowicę pomocniczą EAGLE-3 dla modelu Llama 3.3 70B. Porównaj ten wynik z narzutem pamięciowym przy uruchomieniu osobnego modelu pomocniczego Llama 3.2 1B w klasycznej konfiguracji.

## Kluczowe terminy

| Termin | Potoczny opis | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Speculative decoding | „generowanie i weryfikacja” | Metoda generowania tokenów, w której model pomocniczy proponuje $K$ tokenów, a model główny weryfikuje je w jednym kroku forward pass. |
| Acceptance rate $\alpha$ | „współczynnik akceptacji” | Odsetek tokenów zaproponowanych przez model pomocniczy, które zostały zaakceptowane przez model główny; kluczowa metryka opłacalności. |
| Draft length $K$ | „długość propozycji” | Liczba tokenów generowana przez model pomocniczy w jednym kroku przed weryfikacją; typowo wynosi od 4 do 8. |
| Verification overhead | „narzut weryfikacji” | Dodatkowy koszt obliczeniowy weryfikacji propozycji i obsługi odrzuceń na modelu docelowym; rośnie wraz z rozmiarem paczki (batch). |
| EAGLE-3 | „nowy EAGLE” | Zoptymalizowany algorytm pomocniczy, trenowany na wielu warstwach ukrytych modelu docelowego; osiąga $\alpha$ na poziomie 0.6–0.8. |
| `speculative_config` | „konfiguracja w vLLM” | Parametr konfiguracyjny w silniku vLLM, którego jawne zdefiniowanie jest wymagane do uruchomienia dekodowania spekulatywnego. |
| N-gram spec decode | „wyszukiwanie N-gramowe” | Metoda generowania propozycji na GPU w oparciu o analizę powtórzeń fraz w promptach; w pełni kompatybilna z chunked prefill. |
| Alpha breakeven | „próg rentowności alfa” | Wartość współczynnika akceptacji, przy której zyski z dekodowania spekulatywnego równoważą narzut obliczeniowy. |
| Draft rejection | „odrzucenie propozycji” | Sytuacja, w której model główny odrzuca tokeny modelu pomocniczego; wymusza dodatkowe obliczenia i może pogorszyć percentyl P99 ITL. |

## Dalsze czytanie

- [vLLM Documentation — Speculative Decoding](https://docs.vllm.ai/en/latest/features/spec_decode/) — oficjalne informacje o konfiguracji `speculative_config` oraz kompatybilności z chunked prefill w wersji V1.
- [vLLM Speculative Config API](https://docs.vllm.ai/en/latest/api/vllm/config/speculative/) — pełna specyfikacja pól konfiguracyjnych.
- [EAGLE Paper (arXiv:2401.15077)](https://arxiv.org/abs/2401.15077) — oryginalna publikacja wprowadzająca architekturę głowic pomocniczych EAGLE.
- [EAGLE-2 Paper (arXiv:2406.16858)](https://arxiv.org/abs/2406.16858) — specyfikacja adaptacyjnej długości propozycji i weryfikacji opartej na strukturze drzewa.
- [UC Berkeley EECS-2025-224](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2025/EECS-2025-224.html) — analiza wydajności systemów LLM z wykorzystaniem dekodowania spekulatywnego.
- [BentoML — Speculative Decoding Guide](bentoml.com/llm/inference-optimization/speculative-decoding) — lista kontrolna i najlepsze praktyki dla wdrożeń produkcyjnych.
