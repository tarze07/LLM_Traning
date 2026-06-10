# Rodzina optymalizacji preferencji bezpośrednich

> Rafailov i in. (2023) wykazali, że optymalne rozwiązanie problemu RLHF z regularyzacją KL ma postać analityczną (zamkniętą) w odniesieniu do prawdopodobieństwa preferencji. Oznacza to, że można pominąć jawny model nagrody i optymalizować bezpośrednio politykę. To odkrycie dało początek całej rodzinie algorytmów – takich jak IPO, KTO, SimPO, ORPO czy BPO – z których każdy próbuje wyeliminować konkretne tryby awarii (failure modes) klasycznego DPO. W 2026 roku algorytmy bezpośredniego wyrównania (Direct Alignment Algorithms - DAA) są częściej stosowane w potokach poszkoleniowych (post-training) niż klasyczne PPO. Niemniej jednak krzywa nadmiernej optymalizacji (opisana w temacie 2) wciąż ma tu zastosowanie: DAA nie eliminują problemu prawa Goodharta – zmieniają jedynie przestrzeń, w której się on objawia.

**Typ:** Teoria i koncepcje
**Języki:** Python (biblioteka standardowa, porównanie sześciu wariantów funkcji straty)
**Wymagania wstępne:** Faza 18 · 01 (InstructGPT), Faza 18 · 02 (hakowanie nagród), Faza 10 · 08 (podstawy DPO)
**Czas:** ~75 minut

## Cele nauczania

- Wyprowadź postać analityczną (zamkniętą) DPO z optymalnego sformułowania RLHF z karą KL.
- Zidentyfikuj tryby awarii klasycznego DPO, które próbują naprawić algorytmy IPO, KTO, SimPO, ORPO oraz BPO.
- Odróżnij pojęcie „ukrytej różnicy nagród” (implicit reward margin) od „siły preferencji” (preference strength) i wyjaśnij znaczenie mapowania tożsamościowego (identity mapping) w IPO.
- Wyjaśnij, dlaczego Rafailov i in. (NeurIPS 2024) wykazują, że algorytmy DAA podlegają nadmiernej optymalizacji pomimo braku jawnego modelu nagrody (RM).

## Problem

Cel optymalizacji RLHF (temat 1):

```
max_pi E_{x,y~pi} [ r(x, y) ] - beta * KL(pi || pi_ref)
```

ma znane rozwiązanie optymalne:

```
pi*(y|x) = (1/Z(x)) * pi_ref(y|x) * exp(r(x, y) / beta)
```

Z tego wynika, że funkcja nagrody może być wyrażona poprzez stosunek polityki optymalnej do referencyjnej:

```
r(x, y) = beta * log(pi*(y|x) / pi_ref(y|x)) + beta * log Z(x)
```

Po podstawieniu tej zależności do modelu preferencji Bradleya-Terry'ego, funkcja podziału (sumowania) `Z(x)` ulega skróceniu, ponieważ zależy wyłącznie od promptu `x`. W efekcie otrzymujemy funkcję straty zdefiniowaną bezpośrednio na parametrach polityki – model nagrody przestaje być potrzebny. Tak powstało DPO.

Główna słabość: wyprowadzenie to zakłada, że polityka optymalna jest w pełni osiągalna, dane preferencji pochodzą z tego samego rozkładu (in-distribution), a polityka referencyjna stabilnie kotwiczy rozkład prawdopodobieństwa. W rzeczywistości żadne z tych założeń nie jest w pełni spełnione. Kolejni przedstawiciele rodziny DAA modyfikują te uproszczenia.

## Koncepcja

### DPO (Rafailov i in., 2023)

```
L_DPO = -log sigmoid(
  beta * log(pi(y_w | x) / pi_ref(y_w | x))
  - beta * log(pi(y_l | x) / pi_ref(y_l | x))
)
```

Potencjalne problemy:

- Ukryta różnica nagród `beta * (log(pi/pi_ref)_w - log(pi/pi_ref)_l)` jest nieograniczona. Słaba preferencja może wygenerować dowolnie dużą różnicę wartości nagrody.
- Funkcja straty optymalizuje prawdopodobieństwa odpowiedzi wygranej i przegranej w przeciwnych kierunkach. Może to prowadzić do obniżenia bezwzględnego prawdopodobieństwa odpowiedzi wygranej (log-prob), o ile prawdopodobieństwo odpowiedzi przegranej spada jeszcze szybciej. Jest to zjawisko degradacji odpowiedzi wygranej (Degraded Chosen Response).
- Pary preferencji spoza rozkładu treningowego (out-of-distribution) generują nieprzewidywalne, arbitralne wartości nagrody ukrytej.

### IPO (Azar i in., 2024)

Identity Preference Optimization zastępuje funkcję log-sigmoid mapowaniem tożsamościowym dla prawdopodobieństwa preferencji. Funkcja straty sprowadza się do błędu średniokwadratowego względem ograniczonego celu:

```
L_IPO = (log(pi(y_w | x) / pi_ref(y_w | x)) - log(pi(y_l | x) / pi_ref(y_l | x)) - 1/(2 beta))^2
```

Różnica ta jest ograniczona wartością `1/(2 beta)`. Rzeczywista siła preferencji oraz ukryta różnica nagród pozostają proporcjonalne, co zapobiega niekontrolowanemu wzrostowi wartości.

### KTO (Ethayarajh i in., 2024)

Kahneman-Tversky Optimization całkowicie rezygnuje ze struktury porównań parzystych. Wykorzystując pojedyncze odpowiedzi z binarnym sygnałem („pożądana” / „niepożądana”), modeluje użyteczność zgodnie z teorią perspektywy:

```
v(x, y) = sigma(beta * log(pi(y|x) / pi_ref(y|x)) - z_ref)
```

z uwzględnieniem asymetrii między zyskami a stratami (awersja do strat). Zaletą tej metody jest możliwość trenowania na danych niesparowanych, które są znacznie łatwiejsze do pozyskania.

### SimPO (Meng i in., 2024)

Simple Preference Optimization dopasowuje sygnał treningowy bezpośrednio do prawdopodobieństwa generacji. Rezygnuje z polityki referencyjnej, wprowadzając normalizację log-prawdopodobieństwa względem długości sekwencji:

```
L_SimPO = -log sigmoid(
  (beta / |y_w|) * log pi(y_w | x)
  - (beta / |y_l|) * log pi(y_l | x)
  - gamma
)
```

gdzie `gamma` to margines stabilizujący. Normalizacja długości eliminuje podatność na verbosity bias (generowanie długich tekstów), będący częstym trybem awarii DPO (gdzie dłuższa odpowiedź `y_w` z definicji matematycznej prowadziła do większych wartości log-prob).

### ORPO (Hong i in., 2024)

Odds Ratio Preference Optimization dodaje człon preferencji (odds ratio) bezpośrednio do standardowej straty SFT (ujemnego log-prawdopodobieństwa - NLL):

```
L_ORPO = L_NLL(y_w) + lambda * L_OR
L_OR = -log sigmoid(log(odds(y_w) / odds(y_l)))
```

Metoda ta nie wymaga polityki referencyjnej – człon SFT pełni rolę regularyzatora. Umożliwia to wyrównanie modelu bazowego w jednym etapie treningowym, eliminując potrzebę tworzenia osobnego punktu kontrolnego (checkpointu) SFT.

### BPO (zgłoszenie na ICLR 2026, OpenReview ID: b97EwMUWu7)

Metoda ta rozwiązuje problem degradacji wybranej odpowiedzi: DPO gwarantuje relację `y_w > y_l`, ale bezwzględne prawdopodobieństwo `y_w` może ulec obniżeniu. BPO wprowadza poprawkę penalizującą spadek prawdopodobieństwa wybranej odpowiedzi. Wykazano poprawę dokładności o +10.1% w zadaniach rozumowania matematycznego na modelu Llama-3.1-8B-Instruct w porównaniu do standardowego DPO.

### Uniwersalny wniosek: algorytmy DAA również ulegają nadmiernej optymalizacji

Rafailov i in. w pracy „Prawa skalowania dla nadmiernej optymalizacji modelu nagrody w algorytmach bezpośredniego wyrównania” (NeurIPS 2024) przeanalizowali polityki trenowane za pomocą DPO, IPO oraz SLiC na różnych zbiorach danych przy zmiennym budżecie KL. Uzyskane krzywe rzeczywistej nagrody (gold) w funkcji odległości KL miały identyczny przebieg (wzrost i spadek) jak te opisane przez Gao i in. Ukryta funkcja nagrody zaczyna faworyzować próbki spoza rozkładu treningowego (out-of-distribution), czego regularyzacja KL nie jest w stanie powstrzymać.

Algorytmy bezpośredniego wyrównania nie chronią przed prawem Goodharta. Zmieniają jedynie obszar występowania problemu: zamiast „nadmiernej optymalizacji modelu nagrody” mamy do czynienia z „nadmierną optymalizacją stosunku prawdopodobieństw względem polityki referencyjnej”. Klasyczne metody przeciwdziałania – lepsza jakość danych treningowych, zespoły modeli oraz wczesne zatrzymywanie – pozostają kluczowe w obu przypadkach.

### Wybór metody (stan na 2026 rok)

- Jeśli dysponujesz dużym zbiorem sparowanych preferencji: klasyczne DPO z konserwatywną wartością parametru beta lub SimPO (jeśli występuje silne zniekształcenie odpowiedzi długością - verbosity bias).
- Jeśli posiadasz niesparowane etykiety binarne: KTO.
- Jeśli dążysz do jednoetapowego potoku bezpośrednio z modelu bazowego: ORPO.
- Jeśli logi DPO wykazują degradację prawdopodobieństwa wybranej odpowiedzi: BPO.
- Jeśli dane preferencji są mocno zaszumione lub zróżnicowane, a DPO szybko ulega nasycemu: IPO.

W praktyce produkcyjnej laboratoria testują cały zestaw tych algorytmów i dobierają optymalny pod kątem konkretnego zadania. Rozwiązanie optymalne dla rozumowania matematycznego może się znacząco różnić od optymalnego dla kwestii bezpieczeństwa.

## Uruchomienie kodu

Skrypt `code/main.py` porównuje sześć funkcji straty (DPO, IPO, KTO, SimPO, ORPO, BPO) na uproszczonym zbiorze danych preferencji, w którym rzeczywista siła preferencji różni się w zależności od pary. Każda funkcja straty jest optymalizowana na tej samej próbie 500 par z użyciem prostej polityki softmax. Program wizualizuje ostateczny współczynnik wygranych (win rate), dryf prawdopodobieństwa wybranej odpowiedzi (log-prob) oraz rozkład ukrytych nagród dla każdej z metod.

## Generowane pliki wyjściowe

Ta lekcja tworzy plik `outputs/skill-preference-loss-selector.md`. Narzędzie to, na podstawie statystyk zbioru danych (dane sparowane/niesparowane, zróżnicowana/jednolita siła preferencji, rozkład długości odpowiedzi) oraz celu wdrożenia (potok jednoetapowy lub sekwencyjny SFT-preferencje), rekomenduje optymalną funkcję straty i wskazuje tryb awarii, przed którym dane rozwiązanie ma zabezpieczać.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Porównaj ostateczny spadek prawdopodobieństwa (log-prob) wybranej odpowiedzi dla metod DPO i BPO. Sprawdź, czy BPO rzeczywiście zachowuje wyższe bezwzględne prawdopodobieństwo odpowiedzi wygranej.

2. Zmodyfikuj dane preferencji tak, aby wszystkie pary miały identyczną siłę. Która z sześciu metod wykazuje największą stabilność? W przypadku której metody następuje degradacja wyników? Wyjaśnij matematyczne korzyści stosowania IPO w tym scenariuszu.

3. Skonfiguruj dane tak, aby odpowiedzi odrzucone były średnio dwukrotnie dłuższe od wybranych. Zachowując pozostałe parametry bez zmian, wykaż numerycznie podatność DPO na verbosity bias oraz skuteczność poprawki SimPO.

4. Nawiązując do tezy Rafailova i in. (NeurIPS 2024) o nadmiernej optymalizacji metod DAA, wykreśl różnicę prawdopodobieństw (wybrana minus odrzucona) i zaobserwuj zjawisko nadmiernej optymalizacji w DPO przy wysokich wartościach parametru beta.

5. Przeczytaj streszczenie pracy wprowadzającej BPO (OpenReview b97EwMUWu7). Zidentyfikuj i zapisz jednowierszową korektę, którą BPO wprowadza do klasycznej straty DPO. Zweryfikuj jej implementację w skrypcie `code/main.py`.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| DPO | „RLHF bez modelu nagrody” | Funkcja straty wyprowadzona wprost z analitycznego rozwiązania optymalizacji RLHF; trenuje politykę bezpośrednio na preferencjach |
| Ukryta nagroda | „stosunek log” | `beta * log(pi(y\|x) / pi_ref(y\|x))` — wartość nagrody dla danej odpowiedzi wyznaczana niejawnie przez stosunek logarytmu prawdopodobieństwa polityki trenowanej i referencyjnej |
| IPO | „ograniczony DPO” | Wariant DPO zastępujący log-sigmoid mapowaniem tożsamościowym, co ogranicza różnicę ukrytych nagród wartością `1/(2 beta)` |
| KTO | „niesparowany DPO” | Kahneman-Tversky Optimization; modeluje preferencje na niesparowanych danych binarnych przy użyciu teorii perspektywy z awersją do strat |
| SimPO | „DPO bez referencji” | Optymalizacja preferencji z normalizacją log-prawdopodobieństwa długością sekwencji i dodatkowym marginesem; nie wymaga polityki referencyjnej |
| ORPO | „jednoetapowy DPO” | Odds Ratio Preference Optimization; łączy stratę SFT z członem ilorazu szans (odds ratio), umożliwiając wyrównanie modelu bazowego w jednym etapie |
| BPO | „wybrany DPO zachowujący” | Behavior Preservation Optimization; modyfikacja DPO o człon zapobiegający degradacji bezwzględnego prawdopodobieństwa odpowiedzi wygranej |
| Zdegradowany Wybrany | „wybrany idzie w dół” | Zjawisko, w którym algorytm DPO obniża prawdopodobieństwo wygenerowania poprawnej odpowiedzi, pod warunkiem szybszego spadku prawdopodobieństwa odpowiedzi błędnej |
| DAA | „algorytm bezpośredniego dopasowania” | Direct Alignment Algorithm; klasa algorytmów wyrównywania preferencji rezygnująca z jawnego modelowania nagrody |

## Polecana literatura

- [Rafailov i in. — Bezpośrednia optymalizacja preferencji (NeurIPS 2023, arXiv:2305.18290)](https://arxiv.org/abs/2305.18290)
- [Azar i in. — Ogólny paradygmat teoretyczny umożliwiający zrozumienie uczenia się na podstawie ludzkich preferencji (AISTATS 2024, arXiv:2310.12036)](https://arxiv.org/abs/2310.12036) — IPO
- [Ethayarajh i in. — KTO: Dopasowanie modelu jako teoretyczna optymalizacja perspektywy (arXiv:2402.01306)](https://arxiv.org/abs/2402.01306)
- [Meng, Xia, Chen – SimPO (NeurIPS 2024, arXiv:2405.14734)](https://arxiv.org/abs/2405.14734)
- [Hong, Lee, Thorne – ORPO (EMNLP 2024, arXiv:2403.07691)](https://arxiv.org/abs/2403.07691)
- [BPO — Optymalizacja zachowania zachowania (ICLR 2026 OpenReview b97EwMUWu7)](https://openreview.net/forum?id=b97EwMUWu7)
- [Rafailov i in. — Prawa skalowania dla nadmiernej optymalizacji RM w DAA (NeurIPS 2024, arXiv:2406.02900)](https://arxiv.org/abs/2406.02900)
