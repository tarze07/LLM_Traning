# Dekodowanie spekulatywne i EAGLE-3

> Faza 7 · Lekcja 16 udowodniła matematykę: reguła odrzucenia Lewiatana dokładnie zachowuje rozkład weryfikatora. Ta lekcja przedstawia widok stosu szkoleniowego na spekulatywne dekodowanie produkcji w roku 2026. EAGLE-3 przekształcił model roboczy z taniego przybliżenia w specjalnie zbudowaną małą sieć wytrenowaną na własnych stanach ukrytych weryfikatora, a następnie dodał pętlę testową w czasie uczenia, która wyrównuje rozkład pociągu i wnioskowania. Wynik: przyspieszenie od 3× do 6,5× od początku do końca, akceptowane stawki za token powyżej 0,9 na czacie, brak kompromisów w zakresie dystrybucji. Każdy stos wnioskowania produkcyjnego w 2026 r. dostarcza go domyślnie.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 7 · 16 (dekodowanie spekulatywne), Faza 10 · 12 (optymalizacja wnioskowania)
**Czas:** ~75 minut

## Cele nauczania

- Podaj w jednym zdaniu twierdzenie Lewiatana i udowodnij, że pętla spekulacyjna generuje próbki identycznie rozmieszczone wśród weryfikatora.
- Przejdź dwuletni postęp od dekodowania specyfikacji standardowych (Lewiatan 2023) do programów EAGLE, EAGLE-2 i EAGLE-3 i podaj dokładne ograniczenia usuwane w każdym kroku.
- Oblicz oczekiwane przyspieszenie na podstawie współczynnika akceptacji `α` i stosunku kosztów wersji roboczej do weryfikatora `c` i wybierz optymalną długość wersji roboczej `N` dla każdego reżimu.
- Zaimplementuj od zera pełną pętlę spekulacyjną: szkic, weryfikacja, odrzucenie próbki z pozostałości, wycofanie pamięci podręcznej KV po odrzuceniu, wyemitowanie tokenu bonusowego po pełnej akceptacji.

## Problem

Dekodowanie autoregresyjne w modelu 70B działa z szybkością około 35 tokenów na sekundę na H100. Procesor graficzny nie jest w żadnym stopniu nasycony. Przepustowość pamięci to pułap: każdy token ładuje 70B ciężarów z HBM, wykonuje jeden krok arytmetyczny i generuje jeden float. Jednostki obliczeniowe pozostają w większości bezczynne.

Dekodowanie spekulatywne zamienia to w problem przepustowości, który można faktycznie rozwiązać. Tania wersja robocza proponuje tokeny `N` w `N` małych przejściach do przodu. Weryfikator uruchamia się raz na prefiksie i wszystkich wersjach roboczych `N`. Jeżeli rozkład weryfikatora na pozycji `i` zgadza się z projektem (w sensie statystycznym doprecyzujemy), akceptujemy; jeśli nie, odrzucamy i pobieramy korektę z rozkładu resztowego. Pojedynczy forward typu duży model generuje do `N+1` akceptowanych tokenów zamiast jednego.

Twierdzenie, które ma znaczenie, to Lewiatan, Kalman, Matias (ICML 2023): rozkład wyników jest identyczny z tym, co spowodowałoby pobieranie próbek bezpośrednio od weryfikatora. Nie w przybliżeniu. Identycznie. To jest cały powód, dla którego dekodowanie spekulatywne jest dopuszczalne w produkcji — jest to czysta optymalizacja opóźnień bez kompromisów w zakresie jakości.

Faza 7 · Lekcja 16 dała ci matematykę. To, co daje ci ta lekcja, to stos treningowy. Dobry draft jest wart 2 razy większe przyspieszenie niż tani draft. EAGLE, EAGLE-2 i EAGLE-3 (Li i in., 2024–2025) zamieniły „wersję roboczą = mniejszą wersję tego samego modelu” w precyzyjną dziedzinę inżynierii. Serwery wnioskowania produkcyjnego 2026 domyślnie korzystają z EAGLE-3.

## Koncepcja

### Niezmiennik: próbkowanie odrzucone przez Lewiatana

Niech `p(t)` będzie rozkładem wersji roboczej dla następnego tokenu z pewnym przedrostkiem, a `q(t)` będzie rozkładem weryfikatora. Przykładowy token wersji roboczej `d ~ p`. Zaakceptuj z prawdopodobieństwem `min(1, q(d) / p(d))`. Po odrzuceniu próbka z rozkładu resztkowego `(q - p)_+ / ||(q - p)_+||_1`. Powstałe próbki są rozdzielane zgodnie z `q`. Dzieje się tak niezależnie od tego, jak zły jest `p` — im gorzej, tym częściej odrzucasz, ale wynik pozostaje dokładny.

Połącz `N` tych wywołań jeden po drugim, używając jednego przekazania weryfikatora na `prefix + d_1 + ... + d_N`. Weryfikator zwraca jednocześnie wartość `q_1, q_2, ..., q_{N+1}`. Idź od lewej do prawej. Przy pierwszym odrzuceniu na pozycji `j` pobierz próbkę z `residual(q_j, p_j)` i zatrzymaj się. Po pełnej akceptacji wypróbuj jeden token bonusowy z `q_{N+1}`.

### Co decyduje o przyspieszeniu

Niech `α` będzie oczekiwanym współczynnikiem akceptacji na wygenerowany token. Niech `c = cost(draft) / cost(verifier)` będzie stosunkiem kosztów. Oczekiwana liczba zaakceptowanych tokenów na przekazanie weryfikatora wynosi:

```
E[accepted] = (1 - α^(N+1)) / (1 - α)
```

Oczekiwany całkowity czas trwania ściany na zaakceptowany token wynosi `(N * c + 1) / E[accepted]`. Zminimalizuj to w odniesieniu do `N`, a uzyskasz najlepszy punkt. Dla `α = 0.8, c = 0.05`: optymalna wartość `N` wynosi około 5–7, przyspieszenie wynosi 3,2×. Dla `α = 0.95, c = 0.02`: optymalna wartość `N` wynosi około 8–10, przyspieszenie zwiększa się 5×.

Największą pojedynczą dźwignią jest `α`. Przejście z `α = 0.6` (wersja robocza waniliowa) na `α = 0.9` (EAGLE-3) przy stałej `N = 5` powoduje przejście z 2,2 oczekiwanych zaakceptowanych tokenów na weryfikator do wersji 4.1. Prawie 2 razy większa przepustowość z tego samego weryfikatora.

### Dwuletnia progresja

**Waniliowy charakter spekulacyjny (Lewiatan, 2023).** Model roboczy to niezależnie przeszkolony mniejszy LLM z tej samej rodziny. Łatwe podłączenie, `α ≈ 0.6`, przyspieszenie w najlepszym wypadku około 2×.

**EAGLE-1 (Li et al., 2024).** Draft to niewielki transformator — zwykle jedno- lub dwuwarstwowy — który jako dane wejściowe przyjmuje stan ukryty ostatniej warstwy weryfikatora i bezpośrednio przewiduje następny token. Ponieważ projekt uwzględnia reprezentację cech weryfikatora, jej rozkład jest znacznie bliższy rozkładowi weryfikatora. `α` wzrasta do 0,7–0,8.

**EAGLE-2 (Li et al., 2024).** Dodaje dynamiczne drzewo robocze: zamiast proponować pojedynczą sekwencję tokenów `N`, zaproponuj małe drzewo kandydatów, oceń każdego z weryfikatorem w jednym przejściu do przodu (uwaga drzewa) i idź ścieżką o najwyższym prawdopodobieństwie. Długość zanurzenia dostosowuje się co krok. `α` na każdy token zaakceptowanej ścieżki wzrasta powyżej 0,85.

**EAGLE-3 (Li i in., 2025, NeurIPS).** Jeszcze dwie zmiany. Po pierwsze, całkowicie porzuć utratę przewidywania cech — EAGLE-1/2 wyszkolił wersję roboczą tak, aby pasowała do ukrytych stanów weryfikatora, co ogranicza ilość przydatnych danych. EAGLE-3 trenuje bezpośrednio na podstawie przewidywania tokenów. Po drugie, test czasu szkolenia (TTT): podczas szkolenia wersji roboczej należy przekazać własne, wcześniejsze przewidywania wersji roboczej jako dane wejściowe w wielu etapach, w taki sam sposób, w jaki działa przy wnioskowaniu. Wyrównuje to dystrybucję pociągu i testu oraz zatrzymuje akumulację błędów. Zmierzone przyspieszenie: do 6,5× na czacie, 38% poprawa przepustowości w partii 64 w SGLang na H100.

### Wycofanie pamięci podręcznej KV

Weryfikacja rozszerza pamięć podręczną KV weryfikatora o wpisy `N` w jednym przebiegu. Jeśli odrzucenie nastąpi w pozycji `j`, zawartość pamięci podręcznej za pozycją `j-1` jest teraz błędna. Dwie typowe implementacje: zapisz w buforze magazynującym i zatwierdź po akceptacji (vLLM, TensorRT-LLM) lub przechowuj fizyczną pamięć podręczną KV wraz z długością logiczną i obcinaj po odrzuceniu. Tak czy inaczej, koszt wycofywania wynosi bajtów na warstwę na głowicę, co jest nieistotne w porównaniu z kosztem przejścia w przód.

W przypadku wyszukiwania drzewa EAGLE-2 weryfikator zwraca uwagę na maskę nieprzyczynową, która uwzględnia topologię drzewa. Konstrukcja jest skomplikowana, ale obliczenia to standardowe wezwanie do natychmiastowej uwagi z niestandardową maską.

### Projekty architektur w 2026 r

| Strategia | Typ projektu | `α` | Przyspieszenie | Koszt szkolenia |
|--------------|-----------|-----|---------|---------------|
| Wanilia | Oddzielny mały LLM | 0,55-0,70 | 1,8-2,3× | Brak (wykorzystaj ponownie istniejący mały model) |
| Meduza | Dodatkowe głowy LM na weryfikatorze | 0,65-0,75 | 2-3× | ~1B tokenów SFT |
| ORZEŁ-1 | Transformator 1-warstwowy na stany ukryte | 0,70-0,80 | 2,5-3× | ~60 miliardów tokenów |
| ORZEŁ-2 | EAGLE-1 + dynamiczne drzewo ciągu | 0,80-0,88 | 3-4× | ~60 miliardów tokenów |
| ORZEŁ-3 | Fuzja funkcji wielowarstwowych + TTT | 0,88-0,92 | 3,5-6,5× | ~60-200B tokenów |
| Wyprzedzenie | Brak wersji roboczej (iteracja Jacobiego) | Nie dotyczy | 1,3-1,6× | Brak |

W produkcji 2026: vLLM i SGLang domyślnie EAGLE-3, jeśli są dostępne, EAGLE-2 w przeciwnym razie. TensorRT-LLM ma najszybszą ścieżkę Medusa dla modeli publicznych Meta i NVIDIA. llama.cpp dostarcza wersję roboczą waniliową do wdrożeń procesora.

## Zbuduj to

Zobacz `code/main.py`. Jest to pełna pętla spekulacyjna Lewiatana ze wszystkimi elementami: draft-of-N, przejście równoległe weryfikatora, odrzucenie według pozycji, próbkowanie rezydualne, token bonusowy, wycofywanie KV i empiryczna weryfikacja, czy rozkład wyjściowy odpowiada bezpośredniemu próbkowaniu z `q`.

### Krok 1: reguła odrzucenia

```python
def accept(q_prob, p_prob, u):
    if p_prob <= 0:
        return True
    return u < min(1.0, q_prob / p_prob)
```

### Krok 2: dystrybucja rezydualna

```python
def residual(q, p):
    raw = [max(0.0, qi - pi) for qi, pi in zip(q, p)]
    s = sum(raw)
    if s == 0:
        return list(q)
    return [r / s for r in raw]
```

### Krok 3: pełny krok spekulacyjny

Funkcja `spec_step` pobiera `N` tokeny z `p`, a następnie weryfikuje je wszystkie w jednej równoległej ocenie `q`. Do każdego wystawionego tokena stosuje regułę odrzucenia i przy pierwszym odrzuceniu pobiera korektę z reszty. Jeśli wszystko się zgodzi, emituje token bonusowy od `q_{N+1}`.

### Krok 4: Księgowanie wycofania KV

Symulator śledzi logiczną `kv_length` na pracownika. Po zaakceptowaniu wersji roboczych `k` `kv_length += k`. W przypadku odrzucenia na pozycji `j` pamięć podręczna jest już zapisana poza `j`, ale długość logiczna jest ustawiona na `prefix_length + j + 1` — jedną za tokenem korekty. Kolejne odczyty są obcinane do długości logicznej.

### Krok 5: test Lewiatana

Wykonaj 50 000 kroków spekulacyjnych. Policz empiryczny rozkład zaakceptowanych tokenów. Porównaj z 50 000 bezpośrednich próbek z `q`. Statystyka chi-kwadrat powinna znajdować się znacznie poniżej wartości krytycznej. Twierdzenie sprawdza się w praktyce.

### Krok 6: przyspieszenie vs. α

Popraw jakość przeciągu, zakłócając `p` od `q` przy różnych amplitudach. Zmierz `α`, a następnie wykreśl oczekiwane tokeny na wywołanie weryfikatora jako funkcję `α` i `N`. Kod wyświetla tabelę pokazującą, jak jakość wersji roboczej klasy EAGLE-3 (`α ≈ 0.9`) odblokowuje 4–5 tokenów na wywołanie weryfikatora.

## Użyj tego

Poziom produkcyjny `vllm serve` z EAGLE-3:

```bash
vllm serve meta-llama/Llama-3.3-70B-Instruct \
  --speculative-config '{
    "model": "yuhuili/EAGLE3-LLaMA3.3-Instruct-70B",
    "num_speculative_tokens": 5,
    "method": "eagle3"
  }'
```

SGLang z EAGLE-3 w partii 64 na H100: około 1,38 razy większa przepustowość niż dekodowanie waniliowe w partii 64, według artykułu EAGLE-3.

Kiedy sięgnąć po dekodowanie spekulatywne:

- Każde obciążenie interaktywnym czatem, w którym opóźnienie p50 ma większe znaczenie niż szczytowa przepustowość.
- Generowanie kodu i ustrukturyzowane wyjście (JSON, SQL). Wartość `α` wynosi powyżej 0,9, ponieważ rozkład docelowy jest wysoce przewidywalny.
- Generowanie długich formularzy (tysiące tokenów). Amortyzowane przyspieszenie wciąż się opłaca.

Kiedy nie:

- Bardzo małe modele (< 3B). Wersja robocza nie jest dużo tańsza od weryfikatora.
- Małe wdrożenia procesora wsadowego 1. Narzut pamięci w wersji roboczej modelu może nie być tego wart.
- Próbkowanie kreacji w bardzo wysokiej temperaturze, podczas którego zapada się `α`.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-eagle3-tuner.md`. Biorąc pod uwagę obciążenie wnioskowaniem (model, rozmiar partii, docelowe opóźnienie, profil zadania), zaleca strategię dekodowania spekulatywnego i parametry dostrajania (rodzina wersji roboczej, `N`, głębokość drzewa, przełączanie uwzględniające temperaturę).

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że statystyka chi-kwadrat w kontroli rozkładu Lewiatana pozostaje poniżej wartości krytycznej 95% w 50 000 próbek.

2. Przesuń `N` od 1 do 10 przy użyciu `α` utrzymywanego na poziomie 0,9 i `c` utrzymywanego na poziomie 0,04. Wykreśl oczekiwane tokeny na wywołanie weryfikatora i rzeczywisty czas trwania ściany na token. Znajdź `N`, który minimalizuje czas potrzebny na ścianie. Wyjaśnij kształt krzywej.

3. Zmodyfikuj kod, aby symulował przeszukiwanie drzewa EAGLE-2: na każdym kroku wersja robocza proponuje drzewo o kształcie `[2, 2, 2]` (osiem kandydujących ścieżek). Weryfikator uruchamia się raz i wygrywa zaakceptowana ścieżka o najwyższym prawdopodobieństwie. Oblicz `α` na liść i całkowitą liczbę tokenów na wywołanie weryfikatora. Porównanie z dekodowaniem specyfikacji w łańcuchu liniowym przy równoważnych obliczeniach.

4. Zaimplementuj wsadowy symulator wycofywania wartości KV dla dwóch współbieżnych sekwencji. W sekwencji A zaakceptowano wszystkie wersje robocze; sekwencja B odrzuca na pozycji 2. Pokaż, że poprawny `kv_length` jest aktualizowany w każdej sekwencji i że żadna praca nie jest marnowana.

5. Przeczytaj sekcję 4 artykułu EAGLE-3 (Test czasu szkolenia). Wyjaśnij w dwóch zdaniach, dlaczego naiwne szkolenie w trybie draft bez TTT jest podatne na błąd związany z ekspozycją i dlaczego naprawianie projektu własnymi przewidywaniami podczas szkolenia go naprawia. Połącz to z literaturą dotyczącą zaplanowanego próbkowania w seq2seq.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Rządy Lewiatana | „min(1, q przez p)” | Bernoulli akceptuje/odrzuca z prawdopodobieństwem `min(1, q(d)/p(d))`, zachowuje rozkład weryfikatorów dokładnie wtedy, gdy pobierasz próbkę z reszty po odrzuceniu |
| Pozostała dystrybucja | „(q minus p) plus, znormalizowany” | `(q - p)_+` zawężony do zera i znormalizowany — prawidłowy rozkład do próbki po odrzuceniu |
| Stopień akceptacji α | „jak często projekt jest słuszny” | Oczekiwane prawdopodobieństwo sukcesu Bernoulliego na token zgodnie z regułą odrzucenia; reguluje całą matematykę przyspieszenia |
| ORZEŁ-1 | „przeciąg w stanie ukrytym” | Mały ciąg transformatora uwarunkowany stanem ukrytym ostatniej warstwy weryfikatora (Li i in., 2024) |
| ORZEŁ-2 | „dynamiczne drzewo wersji roboczej” | EAGLE-1 plus drzewo potencjalnych kontynuacji, które zdobyły uwagę drzewa w jednym przejściu weryfikatora |
| ORZEŁ-3 | „test czasu szkolenia” | Eliminuje utratę przewidywania funkcji, trenuje na podstawie bezpośredniego przewidywania tokenów, a wersja robocza zasilana jest własnymi wynikami podczas szkolenia |
| Test czasu treningu (TTT) | „poprawka błędu ekspozycji” | Uruchom wersję roboczą autoregresywnie podczas uczenia, aby rozkłady danych wejściowych uczenia i testowania były zgodne — bezpośredni odpowiednik zaplanowanego próbkowania |
| Cofnięcie KV | „cofnij odrzucone wersje robocze” | Księgowość, która po odrzuceniu resetuje pamięć podręczną KV weryfikatora do zaakceptowanej długości prefiksu |
| Żeton bonusowy | "ten darmowy" | Kiedy wszystkie wersje robocze `N` zostaną zaakceptowane, wypróbuj jedną dodatkową z `q_{N+1}` bez dodatkowych kosztów weryfikatora |
| Uwaga drzewa | "weryfikuj wielu kandydatów na raz" | Uwaga z maską nieprzyczynową, która uwzględnia topologię drzewa przeciągu; oblicza `q_i` dla każdego węzła w drzewie w jednym przebiegu |

## Dalsze czytanie

- [Lewiatan, Kalman, Matias — Fast Inference from Transformers via Speculative Decoding (arXiv:2211.17192, ICML 2023)](https://arxiv.org/abs/2211.17192) — artykuł podstawowy i twierdzenie o równoważności
- [Chen i in. — Przyspieszanie dekodowania modelu wielkojęzykowego za pomocą próbkowania spekulatywnego (arXiv:2302.01318)](https://arxiv.org/abs/2302.01318) — jednoczesne niezależne wprowadzenie z czystym dowodem
- [Li i in. — EAGLE: Próbkowanie spekulatywne wymaga ponownego przemyślenia niepewności funkcji (arXiv:2401.15077)](https://arxiv.org/abs/2401.15077) — EAGLE-1, wersja robocza z warunkowaniem stanu ukrytego
- [Li i in. — EAGLE-2: Szybsze wnioskowanie modeli językowych za pomocą dynamicznych drzew roboczych (arXiv:2406.16858)](https://arxiv.org/abs/2406.16858) — dynamiczne wyszukiwanie drzewa
- [Li i in. — EAGLE-3: Zwiększanie przyspieszania wnioskowania za pomocą testu czasu uczenia (arXiv:2503.01840, NeurIPS 2025)](https://arxiv.org/abs/2503.01840) — ustawienie domyślne w wersji produkcyjnej na rok 2026
- [Cai i in. — Meduza: wiele głowic dekodujących (arXiv:2401.10774)](https://arxiv.org/abs/2401.10774) — alternatywne podejście bez przeciągów
- [Dokumentacja spekulatywnego dekodowania vLLM](https://docs.vllm.ai/en/latest/features/spec_decode.html) — kanoniczne odniesienie do produkcji ze wszystkimi podłączonymi strategiami