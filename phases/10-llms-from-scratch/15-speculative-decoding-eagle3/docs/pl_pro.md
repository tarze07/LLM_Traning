# Dekodowanie spekulatywne i EAGLE-3

> Faza 7 · Lekcja 16 dowiodła matematycznie, że reguła odrzucenia Lewiatana dokładnie zachowuje rozkład weryfikatora. Niniejsza lekcja prezentuje perspektywę stosu szkoleniowego na spekulatywne dekodowanie w środowiskach produkcyjnych w roku 2026. EAGLE-3 przekształcił model roboczy z taniego przybliżenia w specjalnie zaprojektowaną małą sieć, wytrenowaną na ukrytych stanach samego weryfikatora, a następnie wzbogacił ją o pętlę testową podczas uczenia, która wyrównuje rozkłady treningu i wnioskowania. Wynik to przyspieszenie od 3× do 6,5× w ujęciu całościowym, wskaźnik akceptacji tokenów przekraczający 0,9 w zastosowaniach czatowych oraz brak jakichkolwiek kompromisów jakościowych. W 2026 roku każdy produkcyjny stos wnioskowania dostarcza to rozwiązanie domyślnie.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 7 · 16 (dekodowanie spekulatywne), Faza 10 · 12 (optymalizacja wnioskowania)
**Czas:** ~75 minut

## Cele nauczania

- Sformułuj twierdzenie Lewiatana w jednym zdaniu i udowodnij, że pętla spekulacyjna generuje próbki o rozkładzie identycznym z rozkładem weryfikatora.
- Prześledzić dwuletni postęp od standardowego dekodowania spekulatywnego (Lewiatan 2023) przez EAGLE, EAGLE-2 aż do EAGLE-3, wskazując dokładne ograniczenia usuwane na każdym etapie.
- Obliczyć oczekiwane przyspieszenie na podstawie współczynnika akceptacji `α` i stosunku kosztów modelu roboczego do weryfikatora `c`, a następnie wybrać optymalną długość sekwencji roboczej `N` dla danego przypadku użycia.
- Zaimplementować od zera kompletną pętlę spekulacyjną: szkicowanie, weryfikację, próbkowanie z rozkładu resztkowego po odrzuceniu, wycofywanie pamięci podręcznej KV po odrzuceniu oraz emisję tokenu bonusowego po pełnej akceptacji.

## Problem

Dekodowanie autoregresyjne w modelu 70B osiąga na H100 około 35 tokenów na sekundę. Procesor graficzny nie jest przy tym wcale nasycony — wąskim gardłem jest przepustowość pamięci. Każdy token wymaga załadowania 70 miliardów wag z HBM, wykonania jednego kroku arytmetycznego i wygenerowania jednej wartości zmiennoprzecinkowej. Jednostki obliczeniowe przez większość czasu pozostają bezczynne.

Dekodowanie spekulatywne przekształca ten problem w zadanie przepustowościowe, które można faktycznie rozwiązać. Tani model roboczy proponuje `N` tokenów w `N` małych przejściach w przód. Weryfikator uruchamia się raz dla prefiksu i wszystkich `N` tokenów roboczych łącznie. Jeśli rozkład weryfikatora na pozycji `i` jest zgodny z propozycją modelu roboczego (w sensie statystycznym, który doprecyzujemy), token zostaje zaakceptowany; w przeciwnym razie jest odrzucany, a korekta pobierana jest z rozkładu resztkowego. Dzięki temu jedno przejście dużego modelu generuje do `N+1` zaakceptowanych tokenów zamiast jednego.

Kluczowe jest twierdzenie Lewiatana, Kalmana i Matiasa (ICML 2023): rozkład wynikowych próbek jest identyczny z tym, co uzyskano by przez bezpośrednie próbkowanie z weryfikatora — nie w przybliżeniu, lecz dokładnie. To właśnie sprawia, że dekodowanie spekulatywne jest akceptowalne w środowiskach produkcyjnych: jest to czysta optymalizacja opóźnień, bez żadnych kompromisów jakościowych.

Faza 7 · Lekcja 16 dostarczyła matematycznych podstaw. Niniejsza lekcja zajmuje się stosem szkoleniowym. Dobry model roboczy może zapewnić dwukrotnie większe przyspieszenie niż model tani. EAGLE, EAGLE-2 i EAGLE-3 (Li i in., 2024–2025) zamieniły formułę „model roboczy = mniejsza wersja tego samego modelu" w precyzyjną dziedzinę inżynieryjną. Produkcyjne serwery wnioskowania w 2026 roku domyślnie korzystają z EAGLE-3.

## Koncepcja

### Niezmiennik: próbkowanie z odrzucaniem według Lewiatana

Niech `p(t)` będzie rozkładem modelu roboczego dla następnego tokenu przy danym prefiksie, a `q(t)` rozkładem weryfikatora. Pobieramy token roboczy `d ~ p` i akceptujemy go z prawdopodobieństwem `min(1, q(d) / p(d))`. Po odrzuceniu pobieramy próbkę z rozkładu resztkowego `(q - p)_+ / ||(q - p)_+||_1`. Powstałe próbki mają rozkład zgodny z `q` — niezależnie od jakości `p`. Im gorszy jest `p`, tym częściej następują odrzucenia, lecz wynik pozostaje dokładny.

Procedurę tę łączymy dla `N` pozycji, wykonując jedno przejście weryfikatora dla prefiksu oraz `d_1 + ... + d_N`. Weryfikator zwraca jednocześnie `q_1, q_2, ..., q_{N+1}`. Przechodzimy od lewej do prawej: przy pierwszym odrzuceniu na pozycji `j` pobieramy próbkę z `residual(q_j, p_j)` i przerywamy. Jeśli wszystkie tokeny zostały zaakceptowane, losujemy jeden token bonusowy z `q_{N+1}`.

### Co decyduje o przyspieszeniu

Niech `α` oznacza oczekiwany współczynnik akceptacji przypadający na wygenerowany token, a `c = cost(draft) / cost(verifier)` stosunek kosztów. Oczekiwana liczba zaakceptowanych tokenów na jedno przejście weryfikatora wynosi:

```
E[accepted] = (1 - α^(N+1)) / (1 - α)
```

Oczekiwany całkowity czas ściany na zaakceptowany token wynosi `(N * c + 1) / E[accepted]`. Minimalizacja tej wartości względem `N` daje optymalny punkt pracy. Dla `α = 0.8, c = 0.05`: optymalne `N` wynosi około 5–7, a przyspieszenie osiąga 3,2×. Dla `α = 0.95, c = 0.02`: optymalne `N` to około 8–10, a przyspieszenie wzrasta do 5×.

Największą pojedynczą dźwignią jest `α`. Przejście z `α = 0.6` (bazowy model roboczy) do `α = 0.9` (EAGLE-3) przy stałym `N = 5` zwiększa oczekiwaną liczbę zaakceptowanych tokenów na wywołanie weryfikatora z 2,2 do 4,1 — oznacza to niemal dwukrotny wzrost przepustowości przy tym samym weryfikatorze.

### Dwuletnia ewolucja

**Bazowe dekodowanie spekulatywne (Lewiatan, 2023).** Model roboczy to niezależnie wytrenowany mniejszy LLM z tej samej rodziny. Proste w integracji, `α ≈ 0.6`, przyspieszenie najwyżej około 2×.

**EAGLE-1 (Li et al., 2024).** Model roboczy to niewielki transformator — zazwyczaj jedno- lub dwuwarstwowy — przyjmujący jako wejście stan ukryty ostatniej warstwy weryfikatora i bezpośrednio przewidujący następny token. Dzięki uwzględnieniu reprezentacji cech weryfikatora jego rozkład jest znacznie bliższy rozkładowi weryfikatora. Wartość `α` wzrasta do 0,7–0,8.

**EAGLE-2 (Li et al., 2024).** Wprowadza dynamiczne drzewo robocze: zamiast proponować pojedynczą sekwencję `N` tokenów, model zgłasza małe drzewo kandydatów. Weryfikator ocenia je wszystkie w jednym przejściu (z mechanizmem uwagi drzewa), a następnie wybierana jest ścieżka o najwyższym prawdopodobieństwie. Głębokość eksploracji dostosowuje się w każdym kroku. Wartość `α` dla tokenów zaakceptowanej ścieżki przekracza 0,85.

**EAGLE-3 (Li i in., 2025, NeurIPS).** Wprowadza dwie istotne zmiany. Po pierwsze, całkowicie porzuca uczenie na przewidywaniu cech — EAGLE-1/2 trenowały model roboczy tak, aby dopasowywał ukryte stany weryfikatora, co ograniczało ilość użytecznych danych. EAGLE-3 uczy się bezpośrednio przewidywania tokenów. Po drugie, stosuje test czasu uczenia (TTT): podczas treningu model roboczy otrzymuje własne wcześniejsze predykcje jako wejście w kolejnych krokach, dokładnie tak jak dzieje się to podczas wnioskowania. Eliminuje to rozbieżność między rozkładami treningu i testowania oraz zapobiega kumulacji błędów. Zmierzone przyspieszenie: do 6,5× w zastosowaniach czatowych, 38-procentowa poprawa przepustowości przy partii 64 w SGLang na H100.

### Wycofywanie pamięci podręcznej KV

Weryfikacja rozszerza pamięć podręczną KV weryfikatora o `N` wpisów w jednym przebiegu. Jeśli odrzucenie nastąpi na pozycji `j`, wpisy w pamięci podręcznej za pozycją `j-1` są już nieważne. Stosuje się dwa typowe podejścia: przechowywanie w buforze tymczasowym z zatwierdzeniem po akceptacji (vLLM, TensorRT-LLM) albo utrzymywanie fizycznej pamięci podręcznej KV razem z długością logiczną i obcinanie jej po odrzuceniu. W obu przypadkach koszt wycofania to kilka bajtów na warstwę i głowicę — pomijalny w porównaniu z kosztem przejścia w przód.

W przypadku wyszukiwania drzewa w EAGLE-2 weryfikator stosuje uwagę z maską nieprzyczynoważną uwzględniającą topologię drzewa. Konstrukcja maski jest złożona, jednak same obliczenia sprowadzają się do standardowego wywołania mechanizmu uwagi z niestandardową maską.

### Strategie architekturalne w 2026 r

| Strategia | Typ modelu roboczego | `α` | Przyspieszenie | Koszt uczenia |
|--------------|-----------|-----|---------|---------------|
| Bazowa | Oddzielny mniejszy LLM | 0,55-0,70 | 1,8-2,3× | Brak (ponowne użycie istniejącego modelu) |
| Medusa | Dodatkowe głowice LM w weryfikatorze | 0,65-0,75 | 2-3× | ~1B tokenów SFT |
| EAGLE-1 | Transformator 1-warstwowy na stanach ukrytych | 0,70-0,80 | 2,5-3× | ~60B tokenów |
| EAGLE-2 | EAGLE-1 + dynamiczne drzewo robocze | 0,80-0,88 | 3-4× | ~60B tokenów |
| EAGLE-3 | Wielowarstwowa fuzja cech + TTT | 0,88-0,92 | 3,5-6,5× | ~60-200B tokenów |
| Lookahead | Brak modelu roboczego (iteracja Jacobiego) | Nie dotyczy | 1,3-1,6× | Brak |

W produkcji 2026: vLLM i SGLang domyślnie korzystają z EAGLE-3, jeśli jest dostępny, a w przeciwnym razie z EAGLE-2. TensorRT-LLM oferuje najszybszą ścieżkę Medusa dla publicznych modeli Meta i NVIDIA. llama.cpp dostarcza bazowy model roboczy na potrzeby wdrożeń procesorowych.

## Zbuduj to

Zobacz `code/main.py`. Jest to kompletna pętla spekulacyjna Lewiatana zawierająca wszystkie elementy: szkicowanie `N` tokenów, równoległe przejście weryfikatora, odrzucanie według pozycji, próbkowanie z rozkładu resztkowego, token bonusowy, wycofywanie KV oraz empiryczna weryfikacja zgodności rozkładu wyjściowego z bezpośrednim próbkowaniem z `q`.

### Krok 1: reguła odrzucenia

```python
def accept(q_prob, p_prob, u):
    if p_prob <= 0:
        return True
    return u < min(1.0, q_prob / p_prob)
```

### Krok 2: rozkład resztkowy

```python
def residual(q, p):
    raw = [max(0.0, qi - pi) for qi, pi in zip(q, p)]
    s = sum(raw)
    if s == 0:
        return list(q)
    return [r / s for r in raw]
```

### Krok 3: pełny krok spekulacyjny

Funkcja `spec_step` pobiera `N` tokenów z `p`, a następnie weryfikuje je wszystkie w jednej równoległej ewaluacji `q`. Do każdego tokenu stosuje regułę odrzucenia i przy pierwszym odrzuceniu pobiera korektę z rozkładu resztkowego. Jeśli wszystkie tokeny przejdą weryfikację, emitowany jest token bonusowy z `q_{N+1}`.

### Krok 4: księgowanie wycofania KV

Symulator śledzi logiczną `kv_length` dla każdego wątku. Po zaakceptowaniu `k` tokenów roboczych wartość `kv_length` zwiększa się o `k`. W przypadku odrzucenia na pozycji `j` pamięć podręczna jest już zapisana poza pozycję `j`, ale długość logiczna jest ustawiana na `prefix_length + j + 1` — o jeden za tokenem korekty. Kolejne odczyty są obcinane do tej długości logicznej.

### Krok 5: test Lewiatana

Wykonaj 50 000 kroków spekulacyjnych. Policz empiryczny rozkład zaakceptowanych tokenów i porównaj go z 50 000 próbkami pobranymi bezpośrednio z `q`. Statystyka chi-kwadrat powinna być znacznie poniżej wartości krytycznej. Twierdzenie sprawdza się w praktyce.

### Krok 6: przyspieszenie w zależności od α

Stopniowo poprawiaj jakość modelu roboczego, zaburzając `p` względem `q` przy różnych amplitudach. Zmierz `α`, a następnie wykreśl oczekiwaną liczbę tokenów na wywołanie weryfikatora jako funkcję `α` i `N`. Kod wyświetla tabelę pokazującą, jak jakość modelu roboczego klasy EAGLE-3 (`α ≈ 0.9`) umożliwia uzyskanie 4–5 tokenów na wywołanie weryfikatora.

## Użyj tego

Uruchomienie na poziomie produkcyjnym z `vllm serve` i EAGLE-3:

```bash
vllm serve meta-llama/Llama-3.3-70B-Instruct \
  --speculative-config '{
    "model": "yuhuili/EAGLE3-LLaMA3.3-Instruct-70B",
    "num_speculative_tokens": 5,
    "method": "eagle3"
  }'
```

SGLang z EAGLE-3 przy partii 64 na H100 osiąga według artykułu EAGLE-3 około 1,38 raza większą przepustowość niż dekodowanie bazowe przy tej samej konfiguracji.

Kiedy warto stosować dekodowanie spekulatywne:

- W każdym interaktywnym zastosowaniu czatowym, gdzie opóźnienie p50 jest ważniejsze niż szczytowa przepustowość.
- Przy generowaniu kodu i ustrukturyzowanego wyjścia (JSON, SQL). Wartość `α` przekracza 0,9, ponieważ docelowy rozkład jest bardzo przewidywalny.
- Przy długim generowaniu (tysiące tokenów). Uśrednione przyspieszenie nadal się opłaca.

Kiedy nie warto:

- W przypadku bardzo małych modeli (< 3B). Model roboczy nie jest dużo tańszy od weryfikatora.
- Przy jednoelementowych wsadach wsadowych przetwarzanych na procesorze. Narzut pamięciowy modelu roboczego może przewyższyć zyski.
- Przy twórczym próbkowaniu w bardzo wysokiej temperaturze, gdy wartość `α` gwałtownie spada.

## Wyślij to

Ta lekcja dostarcza `outputs/skill-eagle3-tuner.md`. Na podstawie opisu obciążenia wnioskowania (model, rozmiar partii, docelowe opóźnienie, profil zadania) narzędzie rekomenduje strategię dekodowania spekulatywnego wraz z parametrami dostrajania (rodzina modelu roboczego, `N`, głębokość drzewa, przełączanie uwzględniające temperaturę).

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że statystyka chi-kwadrat w teście rozkładu Lewiatana pozostaje poniżej wartości krytycznej 95% przy 50 000 próbek.

2. Zmieniaj `N` od 1 do 10, utrzymując `α` na poziomie 0,9 i `c` na poziomie 0,04. Wykreśl oczekiwaną liczbę tokenów na wywołanie weryfikatora oraz rzeczywisty czas ściany na token. Znajdź `N` minimalizujące czas ściany i wyjaśnij kształt krzywej.

3. Zmodyfikuj kod tak, aby symulował przeszukiwanie drzewa EAGLE-2: w każdym kroku model roboczy proponuje drzewo o kształcie `[2, 2, 2]` (osiem ścieżek kandydujących). Weryfikator uruchamia się raz, a wygrywa zaakceptowana ścieżka o najwyższym prawdopodobieństwie. Oblicz `α` na liść oraz łączną liczbę tokenów na wywołanie weryfikatora. Porównaj wyniki z dekodowaniem spekulatywnym na liniowym łańcuchu przy równoważnych nakładach obliczeniowych.

4. Zaimplementuj symulator wsadowego wycofywania KV dla dwóch współbieżnych sekwencji. W sekwencji A wszystkie tokeny robocze zostają zaakceptowane; sekwencja B odrzuca token na pozycji 2. Pokaż, że `kv_length` jest poprawnie aktualizowana dla każdej sekwencji i że żadna praca nie jest wykonywana niepotrzebnie.

5. Przeczytaj sekcję 4 artykułu EAGLE-3 (Test czasu uczenia). Wyjaśnij w dwóch zdaniach, dlaczego naiwne uczenie modelu roboczego bez TTT jest podatne na błąd ekspozycji i dlaczego zasilanie modelu własnymi predykcjami podczas uczenia ten błąd eliminuje. Odnieś to do literatury dotyczącej zaplanowanego próbkowania w architekturach seq2seq.

## Kluczowe terminy

| Termin | Co się mówi | Co to oznacza w praktyce |
|------|----------------|--------------------------------------|
| Reguła Lewiatana | „min(1, q przez p)" | Bernoulliowska akceptacja/odrzucenie z prawdopodobieństwem `min(1, q(d)/p(d))`; zachowuje rozkład weryfikatora dokładnie, o ile po odrzuceniu pobieramy próbkę z rozkładu resztkowego |
| Rozkład resztkowy | „(q minus p) plus, znormalizowany" | `(q - p)_+` obcięte do zera i znormalizowane — poprawny rozkład do próbkowania po odrzuceniu |
| Współczynnik akceptacji α | „jak często model roboczy ma rację" | Oczekiwane prawdopodobieństwo sukcesu Bernoulliego na token zgodnie z regułą odrzucenia; rządzi całą matematyką przyspieszenia |
| EAGLE-1 | „model roboczy z warunkowaniem stanu ukrytego" | Mały transformator uwarunkowany stanem ukrytym ostatniej warstwy weryfikatora (Li i in., 2024) |
| EAGLE-2 | „dynamiczne drzewo robocze" | EAGLE-1 wzbogacony o drzewo potencjalnych kontynuacji ocenianych w mechanizmie uwagi drzewa w jednym przebiegu weryfikatora |
| EAGLE-3 | „test czasu uczenia" | Eliminuje uczenie przewidywania cech, trenuje bezpośrednio przewidywanie tokenów, a model roboczy podczas uczenia jest zasilany własnymi wynikami |
| Test czasu uczenia (TTT) | „korekcja błędu ekspozycji" | Autoregresyjne uruchamianie modelu roboczego podczas uczenia, tak aby rozkłady danych wejściowych w fazie uczenia i testowania były zgodne — bezpośredni odpowiednik zaplanowanego próbkowania |
| Wycofywanie KV | „cofnij odrzucone tokeny robocze" | Procedura księgowa, która po odrzuceniu resetuje pamięć podręczną KV weryfikatora do zaakceptowanej długości prefiksu |
| Token bonusowy | „ten za darmo" | Gdy wszystkie `N` tokenów roboczych zostanie zaakceptowanych, losowany jest jeden dodatkowy token z `q_{N+1}` bez dodatkowego kosztu weryfikacji |
| Uwaga drzewa | „weryfikuj wielu kandydatów jednocześnie" | Uwaga z maską nieprzyczynoważną uwzględniającą topologię drzewa roboczego; oblicza `q_i` dla każdego węzła drzewa w jednym przebiegu |

## Dalsze czytanie

- [Lewiatan, Kalman, Matias — Fast Inference from Transformers via Speculative Decoding (arXiv:2211.17192, ICML 2023)](https://arxiv.org/abs/2211.17192) — artykuł podstawowy i twierdzenie o równoważności
- [Chen i in. — Accelerating Large Language Model Decoding with Speculative Sampling (arXiv:2302.01318)](https://arxiv.org/abs/2302.01318) — niezależne, równoległe wprowadzenie z przejrzystym dowodem
- [Li i in. — EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty (arXiv:2401.15077)](https://arxiv.org/abs/2401.15077) — EAGLE-1, model roboczy z warunkowaniem stanu ukrytego
- [Li i in. — EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees (arXiv:2406.16858)](https://arxiv.org/abs/2406.16858) — dynamiczne przeszukiwanie drzewa
- [Li i in. — EAGLE-3: Scaling up Inference Acceleration of LLMs via Training-Time Test (arXiv:2503.01840, NeurIPS 2025)](https://arxiv.org/abs/2503.01840) — domyślne rozwiązanie produkcyjne w 2026 roku
- [Cai i in. — Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads (arXiv:2401.10774)](https://arxiv.org/abs/2401.10774) — alternatywne podejście bez osobnego modelu roboczego
- [Dokumentacja spekulatywnego dekodowania vLLM](https://docs.vllm.ai/en/latest/features/spec_decode.html) — miarodajne odniesienie produkcyjne obejmujące wszystkie obsługiwane strategie
