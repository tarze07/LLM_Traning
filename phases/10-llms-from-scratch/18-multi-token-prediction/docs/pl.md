# Przewidywanie wielu tokenów (MTP)

> Każdy autoregresyjny LLM od GPT-2 do Lamy 3 trenuje z jedną stratą na pozycję: przewiduj następny token. DeepSeek-V3 dodał drugą stratę na pozycję: następnie wytypuj token. Dodatkowe 14B parametrów (w modelu 671B) zostało oddestylowane z powrotem do głównego modelu poprzez przepływ gradientowy, a wyszkolone głowice MTP zostały ponownie wykorzystane na podstawie wnioskowania jako kreślacze spekulatywnego dekodowania z akceptacją ponad 80%. Przepustowość generacji 1,8× przyszła za darmo. Ta lekcja buduje sekwencyjny moduł MTP na podstawie raportu technicznego DeepSeek, oblicza stratę i układ parametrów wspólnej głowicy oraz wyjaśnia, dlaczego MTP utrzymuje łańcuch przyczynowy, podczas gdy oryginalny równoległy MTP Gloeckle'a i in. go przerwał.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 10 · 04 (wstępne szkolenie mini GPT), Faza 10 · 15 (dekodowanie spekulatywne)
**Czas:** ~60 minut

## Cele nauczania

- Podaj cel szkolenia MTP i oblicz łączną stratę na głębokościach przewidywania.
- Wyjaśnij różnicę między równoległymi głowicami MTP firmy Gloeckle i wsp. (2024) a sekwencyjnymi modułami MTP firmy DeepSeek-V3 i dlaczego konstrukcja sekwencyjna zachowuje łańcuch przyczynowy.
- Oblicz parametry i obciążenie pamięci związane z dodawaniem modułów MTP do przebiegu przedtreningowego.
- Zaimplementuj od podstaw jeden moduł MTP: współdzielone osadzanie, blok transformatora na głębokość, projekcja i współdzielona głowica wyjściowa.

## Problem

Przewidywanie następnego tokena jest standardowym celem szkolenia LLM. Każdy ukryty stan jest nadzorowany tak, aby przewidzieć dokładnie jedną rzecz: token bezpośrednio następujący po nim. To zaskakująco słaby sygnał. Większość informacji w sekwencji wykracza poza jeden symbol – strukturę, spójność, faktyczność, przepływ arytmetyczny. Model musi się tego nauczyć, gromadząc wiele sygnałów jednotokenowych z bilionów tokenów.

MTP pyta: co by było, gdyby każdy ukryty stan był nadzorowany w celu przewidywania wielu przyszłych tokenów jednocześnie? Gloeckle i in. (Meta, 2024) wykazały, że to pomaga. Ich wdrożenie umieściło kilka niezależnych głowic wyjściowych na szczycie szkieletu, z których każda przewidywała inne przesunięcie. Równoległe, proste, ale głowy widziały ten sam ukryty stan bez żadnego hierarchicznego udoskonalenia — a przewidywania nie łączyły się przyczynowo, więc nie można ich było używać do spekulatywnego dekodowania.

DeepSeek-V3 (grudzień 2024 r.) przeprojektował MTP jako moduły sekwencyjne, które utrzymują łańcuch przyczynowy na każdej głębokości przewidywania. Model przewiduje `t+1` na podstawie `h_i^(0)`, a następnie przewiduje `t+2` na podstawie nowego ukrytego stanu `h_i^(1)`, który łączy `h_i^(0)` z `E(t+1)` osadzanie i tak dalej. Każda głębokość to osobny mały blok transformatora. Wspólne osadzanie i wspólna głowica wyjściowa zapewniają skromne narzuty parametrów. W skali DeepSeek-V3, 14B dodatkowych parametrów w modułach MTP oprócz 671B wag modelu głównego. Te 2% narzutu pozwoliło kupić gęstsze sygnały treningowe ORAZ gotowy projekt dekodowania spekulatywnego przy wnioskowaniu.

Ta lekcja buduje od podstaw pojedynczy moduł MTP i stratę głębokości D. Matematyka jest czysta. Implementacja obejmuje 150 linii.

## Koncepcja

### Sekwencyjny przepis MTP

DeepSeek-V3 dodaje `D` moduły MTP na wierzchu modelu głównego. Każdy moduł `k` (dla `k = 1..D`) przewiduje token na głębokości `k` — czyli `t_{i+k}` z przedrostkiem przechodzącym przez pozycję `i`.

Moduł `k` składa się z:

- Blok transformatorowy `T_k` z własną uwagą i MLP.
- Macierz projekcyjna `M_k`, która łączy stan ukryty z poprzedniej głębokości z osadzeniem tokena prawdy gruntowej następnej głębokości.
- Udostępnione osadzanie `E` (tak samo jak w modelu głównym).
- Wspólna głowica wyjściowa `Out` (taka sama jak model główny).

Podczas szkolenia, dla przedrostka do pozycji `i`, stan ukryty według głębokości to:

```
h_i^(0) = main model backbone at position i
h_i^(k) = T_k( M_k * concat(RMSNorm(h_i^(k-1)), RMSNorm(E(t_{i+k}))) )   for k >= 1
```

Przewidywanie głębokości wynosi:

```
logits_{i+k} = Out(h_i^(k-1))   for k = 1..D
```

Strata na głębokość jest entropią krzyżową w stosunku do prawdy naziemnej `t_{i+k}`:

```
L_k = CE(logits_{i+k}, t_{i+k})
```

Wspólne straty na głębokościach:

```
L_MTP = (lambda / D) * sum_{k=1..D} L_k
```

`lambda` to niewielki współczynnik ważący — DeepSeek-V3 używa 0,3 przez pierwsze 10% treningu i 0,1 później. Całkowita strata w treningu wynosi `L_main + L_MTP`.

### Dlaczego sekwencyjne, a nie równoległe

Oryginalny równoległy MTP firmy Gloeckle miał D głowic wyjściowych, każda bezpośrednio zastosowana do `h_i^(0)`. Każda głowa przewiduje `t_{i+k}` na podstawie tego samego stanu ukrytego szkieletu. To dobrze trenuje, ale przewidywania nie są od siebie zależne. Nie możesz użyć wyjścia `head_1`, aby pomóc `head_2` — głowice uruchamiają się równolegle.

Sekwencyjny projekt DeepSeek-V3 opiera się na `h_i^(k)` z `h_i^(k-1)` plus faktyczne osadzenie następnego tokenu `E(t_{i+k})`. Zachowuje to łańcuch przyczynowy: aby przewidzieć `t_{i+k+1}`, moduł na głębokości `k+1` widzi, co było w `t_{i+k}`. Jest to strukturalnie identyczne z tym, jak dekoder autoregresyjny zużywa własne wyjście – dzięki czemu moduły MTP można bezpośrednio wykorzystać jako kreślarze dekodowania spekulatywnego.

Podsumowując: podaj `h_i^(k-1)` i wersję roboczą `t_{i+k}` do modułu `k+1`, uzyskaj prognozę dla `t_{i+k+1}`. Powtarzać. To jest dokładnie projekt w stylu EAGLE, wykorzystujący przeszkolony moduł MTP jako sieć roboczą. DeepSeek-V3 zgłasza ponad 80% akceptacji pierwszego modułu MTP i przyspieszenie ~1,8x.

### Rozliczanie parametrów

Dla modelu z ukrytym `h` i słownictwem `V`:

- Model główny: miliardy parametrów plus jedna głowica wyjściowa o rozmiarze `V * h`.
- Wspólna głowica wyjściowa: ponowne wykorzystanie głowicy głównego modelu. Żadnych dodatkowych parametrów.
- Udostępnione osadzanie: ponowne wykorzystanie osadzania głównego modelu. Żadnych dodatkowych parametrów.
- Moduł na MTP:
  - Projekcja `M_k`: `(2h) * h = 2h^2`.
  - Blok transformatora `T_k`: uwaga (`4h^2` dla MHA) plus MLP (zazwyczaj `8h^2` dla SwiGLU o przełożeniu 8/3). Około `12h^2` na blok.

Łącznie dodatek na moduł: `~14h^2`. Dla modułu `h = 7168` DeepSeek-V3, D = 1 moduł: parametry `~14 * 7168^2 = ~720M` na papierze. DeepSeek-V3 raportuje 14B — różnica polega głównie na tym, że warstwy eksperckie są również MoE w module MTP.

### Zapłata za dekodowanie spekulatywne

Podczas treningu wstępnego moduły MTP spowalniają trening o około 10% (więcej obliczeń do przodu, dodatkowe straty). Zapłata jest dwojaka:

1. Gęstszy sygnał treningowy. Każdy stan ukryty widzi cele nadzoru D+1. Zmierzony wpływ na MMLU, GSM8K, MATH, HumanEval: stała poprawa o kilka punktów procentowych w ablacjach DeepSeek-V3.

2. Bezpłatny spekulacyjny projekt dekodowania przy wnioskowaniu. Moduł MTP jest już przeszkolony do przewidywania kilku kolejnych tokenów. Przekształcona w sieć projektową, zapewnia współczynnik akceptacji wynoszący ponad 80%. Na tym poziomie dekodowanie specyfikacji N=3 lub N=5 daje przepustowość 1,8×. Koszt czasu szkolenia wynoszący 10% zwraca się przy pierwszym uruchomieniu wnioskowania.

### Powiązanie z EAGLE

EAGLE trenuje model małego zanurzenia OSOBNO po treningu wstępnym. MTP piecze projekt przedszkoleniowy. Obydwa podejścia zbiegają się pod względem podobnych współczynników akceptacji, ale za pośrednictwem różnych potoków:

| Wymiar | ORZEŁ-3 | MTP (DeepSeek-V3) |
|----------|---------|--------------------------------|
| Kiedy przeszkolony | Po treningu przedtreningowym | Podczas treningu przedtreningowego |
| Kompatybilny wstecz z istniejącymi ciężarkami | Tak | Nie (trzeba się przeszkolić) |
| Projekt parametrów | 1-2 warstwy transformatora | 1 blok transformatorowy + projekcja |
| Wskaźnik akceptacji | 0,88-0,92 | 0,80+ na głębokości 1 |
| Korzyści wykraczające poza przyspieszenie | Tylko dekodowanie spekulatywne | Gęstszy sygnał treningowy + przyspieszenie |

## Zbuduj to

`code/main.py` buduje od początku do końca pojedynczy moduł MTP: wspólne osadzanie, projekcja, blok transformatora, wspólna głowica wyjściowa. Następnie oblicza stratę entropii krzyżowej na głębokość na podstawie krótkiej sekwencji syntetycznej i drukuje liczbę parametrów według składnika. Zabawkowy słownik składający się z 32 żetonów zapewnia czytelność liczb.

### Krok 1: udostępniona tabela do osadzania

Pojedyncza tabela `vocab_size x hidden` jest wykorzystywana przez model główny ORAZ przez każdy moduł MTP na każdej głębokości. Nie druga kopia — dosłownie ten sam tensor.

### Krok 2: kombinacja głębokości

```python
def combine(prev_hidden, next_token_embed, M_k):
    # concat along feature dim, then project down to hidden
    concat = rms_norm(prev_hidden) + rms_norm(next_token_embed)  # vector addition stand-in
    projected = matvec(M_k, concat)
    return projected
```

Real DeepSeek-V3 łączy dwa wektory RMSNormed w `[2h]` i projekty z macierzą `h x 2h`. Zabawka wykorzystuje dodawanie wektorów w celu zapewnienia zwięzłości stdlib.

### Krok 3: blok transformatora na głębokości k

Samouważność plus MLP. W zabawce jednowarstwowy liniowy blok uwagi i SwiGLU MLP sprawiają, że struktura jest widoczna bez numpy.

### Krok 4: wspólna głowica wyjściowa

Użyj ponownie rzutu wyjściowego głównego modelu. Loguje się nad słownictwem.

### Krok 5: utrata głębokości

Entropia krzyżowa softmax(logits) względem tokena prawdy podstawowej w przesunięciu `k`. Agreguj dane na różnych głębokościach za pomocą współczynnika skalowania `lambda / D`.

### Krok 6: rozliczanie parametrów

Wydrukuj całkowitą liczbę parametrów, liczbę współdzielonych (osadzanie, głowicę) i dodatkową liczbę na moduł. Pokaż stosunek dodatkowego MTP do rozmiaru głównego modelu.

## Użyj tego

MTP jest zintegrowany z DeepSeek-V3 (grudzień 2024 r.) i serią DeepSeek-R1. Wnioskując:

- Własny stos obsługujący DeepSeek wykorzystuje moduły MTP jako dekodery spekulacyjne od razu po wyjęciu z pudełka.
- vLLM i SGLang mają ścieżki integracji dla DeepSeek-V3 MTP od kwietnia 2026 r.
- Poradnik AMD ROCm SGLang pokazuje konkretną konfigurację dekodowania spekulatywnego MTP ze zmierzonym przyspieszeniem 1,8x w punkcie kontrolnym V3.

Kiedy stosować MTP w nowym biegu przedtreningowym:

- Kontrolujesz pełny potok przedtreningowy i chcesz przesyłać gęstszy sygnał treningowy.
- Wiesz, że będziesz obsługiwać model na dużą skalę i chcesz bezpłatnie dekodować spekulacyjnie.
- Twój ukryty rozmiar wynosi co najmniej 4096. W skali 1B narzut bardziej boli niż wzmocnienie pomaga.

Kiedy nie:

- Dostrajanie istniejącego, wstępnie wytrenowanego, gęstego modelu. Moduł MTP nie jest szkolony.
- Modele badawcze, z którymi chcesz porównać czystą linię bazową. MTP zmienia architekturę.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-mtp-planner.md`. Biorąc pod uwagę specyfikację przebiegu przed uczeniem (rozmiar modelu, dane, obliczenia), zwraca plan integracji MTP: liczba głębokości D, harmonogram `lambda`, obciążenie pamięci i okablowanie dekodowania spekulatywnego w czasie wnioskowania.

## Ćwiczenia

1. Uruchom `code/main.py`. Pokaż, że strata na głębokość zmniejsza się monotonicznie wraz ze wzmocnieniem sygnału syntetycznego. Zmodyfikuj materiał syntetyczny, aby używał stałego wzoru i sprawdź, czy straty na głębokości 1 i głębokości 2 są zbieżne.

2. Oblicz narzut parametrów dla gęstego modelu 70B (ukryty 8192, 80 warstw) z modułem MTP D=1. W porównaniu z DeepSeek-V3 zgłoszonym narzutem 14B. Wyjaśnij, dlaczego liczba DeepSeek jest wyższa: blok transformatora MTP dziedziczy tę samą strukturę MoE, zawyżając liczbę parametrów na moduł.

3. Zaimplementuj D=2 w zabawce: dodaj drugi moduł MTP, który pobiera h^(1) i przewiduje `t_{i+2}`. Sprawdź, czy strata wspólna i księgowanie parametrów odpowiadają równaniom 19-21 z artykułu DeepSeek.

4. Przełącz zabawkę na równoległe MTP (w stylu Gloeckle): dodaj D głowice wyjściowe na wierzch głównego stanu ukrytego, każda przewidująca inne przesunięcie. Zmierz straty na głębokość w porównaniu z wersją sekwencyjną na tym samym sygnale syntetycznym. Wersja sekwencyjna powinna dawać niższą stratę głębokości k dla k > 1, ponieważ opiera się na przewidywaniach pośrednich.

5. Użyj przeszkolonego modułu MTP jako wersji roboczej w stylu EAGLE: wywołaj moduł k, aby zaproponować `t_{i+k}` podczas wnioskowania. Zmierz współczynnik akceptacji tych tokenów wersji roboczej w porównaniu z przewidywaniami głównego modelu w wstrzymanej sekwencji. Jeśli osiągniesz 50% + na zabawce, odtworzyłeś empiryczną właściwość MTP w wersji roboczej.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Moduł MTP | „Blokada dodatkowych strat” | Mały blok transformatora plus projekcja, która przewiduje pozycję tokena `k` przed głównym modelem |
| Głębokość przewidywania | „Jakie przesunięcie” | Liczba całkowita `k` taka, że ​​moduł `k` przewiduje `t_{i+k}` od przedrostka do pozycji `i` |
| Równolegle MTP | „W stylu rękawiczek” | D niezależne głowy w tym samym stanie ukrytym szkieletu, bez łańcucha warunkowego |
| Sekwencyjne MTP | „Styl DeepSeek-V3” | Warunkiem każdego modułu jest stan ukrycia poprzedniej głębokości oraz osadzenie kolejnego żetonu; zachowuje łańcuch przyczynowy |
| Wspólna głowica wyjściowa | „Użyj ponownie głównej głowy” | Moduły MTP nazywają głowicę LM głównego modelu, a nie osobną projekcję wyjściową |
| Udostępnione osadzanie | „Użyj ponownie stołu głównego” | Wszędzie używana jest ta sama tabela osadzania słownictwa; brak zduplikowanych parametrów |
| Macierz projekcyjna M_k | „Połącz ukryty + następny token” | `h x 2h` warstwa liniowa, która składa poprzedni stan ukryty i osadza token celu w wejściu następnej głębokości |
| Wspólna strata L_MTP | „Średnie straty dodatkowe” | Średnia arytmetyczna strat entropii krzyżowej na głębokość, skalowana przez `lambda` |
| Wskaźnik akceptacji na głębokości 1 | „Jak często projekt MTP ma rację” | Częstotliwość, z jaką przewidywanie najwyższej pozycji modułu D=1 MTP jest równe przewidywaniu najwyższej pozycji modelu głównego; 80%+ na DeepSeek-V3 |
| Ważenie lambda | „Znaczenie dodatkowych strat” | Współczynnik skalowania na głębokość; 0,3 na początku treningu, 0,1 później w DeepSeek-V3 |

## Dalsze czytanie

- [DeepSeek-AI — Raport techniczny DeepSeek-V3 (arXiv:2412.19437)](https://arxiv.org/abs/2412.19437) — pełny sekwencyjny opis MTP (sekcja 2.2), w tym równania strat wspólnych i przyspieszenie 1,8× przy wnioskowaniu
- [Gloeckle i in. — Lepsze i szybsze modele dużych języków dzięki przewidywaniu wielu tokenów (arXiv:2404.19737)](https://arxiv.org/abs/2404.19737) — równoległy podstawowy projekt DeepSeek MTP poprawia się
– [Karta modelu DeepSeek-V3 na twarzy ściskającej](https://huggingface.co/deepseek-ai/DeepSeek-V3) — łącznie 685B (671B główne + 14B MTP), uwagi dotyczące wdrożenia
- [Lewiatan i in. — Szybkie wnioskowanie z transformatorów poprzez dekodowanie spekulatywne (arXiv:2211.17192)](https://arxiv.org/abs/2211.17192) — struktura dekodowania spekulatywnego MTP pasuje do
- [Li i in. — EAGLE-3 (arXiv:2503.01840)](https://arxiv.org/abs/2503.01840) — Projekt architektury EAGLE 2025, odpowiednik MTP konkuruje