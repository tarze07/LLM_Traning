# Rodzina optymalizacji preferencji bezpośrednich

> Rafailov i in. (2023) wykazali, że optymalne RLHF ma postać zamkniętą pod względem danych preferencji, więc można pominąć jawny model nagrody i bezpośrednio zoptymalizować politykę. Ta wiedza dała początek rodzinie — IPO, KTO, SimPO, ORPO, BPO — z których każda naprawiała tryb awaryjny DPO. W 2026 r. algorytmy bezpośredniego dopasowywania dostarczają więcej granicznych przebiegów potreningowych niż PPO. Jednak krzywa nadmiernej optymalizacji z lekcji 2 nadal ma zastosowanie: DAA nie uciekają przed Goodhartem, po prostu poruszają się tam, gdzie dotknie.

**Typ:** Ucz się
**Języki:** Python (stdlib, sześciowariantowy komparator utraty preferencji)
**Wymagania wstępne:** Faza 18 · 01 (InstructGPT), Faza 18 · 02 (hakowanie nagród), Faza 10 · 08 (podstawy DPO)
**Czas:** ~75 minut

## Cele nauczania

- Wyprowadź zamkniętą postać DPO z optymalnego RLHF-z-KL.
- Podaj tryb awarii każdej z poprawek IPO, KTO, SimPO, ORPO, BPO w DPO.
- Odróżnij „ukrytą lukę w nagrodach” od „siły preferencji” i wyjaśnij, dlaczego mapowanie tożsamości w IPO ma znaczenie.
- Wyjaśnij, dlaczego Rafailov i in. (NeurIPS 2024) dowodzą, że DAA nadmiernie optymalizują pomimo braku wyraźnego RM.

## Problem

Cel RLHF (lekcja 1):

```
max_pi E_{x,y~pi} [ r(x, y) ] - beta * KL(pi || pi_ref)
```

ma znane maksimum:

```
pi*(y|x) = (1/Z(x)) * pi_ref(y|x) * exp(r(x, y) / beta)
```

Zatem nagroda jest domyślnie definiowana przez stosunek optymalnej polityki do odniesienia:

```
r(x, y) = beta * log(pi*(y|x) / pi_ref(y|x)) + beta * log Z(x)
```

Podstaw to do prawdopodobieństwa preferencji Bradleya-Terry'ego, a funkcja podziału `Z(x)` anuluje, ponieważ zależy tylko od `x`. Pozostaje jedynie strata w parametrach polityki – nie jest potrzebny model nagrody. Czyli DPO.

Wada: wyprowadzenie zakłada, że ​​optymalne jest osiągalne, dane dotyczące preferencji znajdują się w dystrybucji, a polityka referencyjna jest kotwicą trybu prawdziwego. Żadne z nich nie trzyma się dokładnie. Każdy członek rodziny naprawia inne naruszone założenie.

## Koncepcja

### DPO (Rafailov i in., 2023)

```
L_DPO = -log sigmoid(
  beta * log(pi(y_w | x) / pi_ref(y_w | x))
  - beta * log(pi(y_l | x) / pi_ref(y_l | x))
)
```

Co może pójść nie tak:

- Ukryta luka w nagrodach `beta * (log(pi/pi_ref)_w - log(pi/pi_ref)_l)` jest nieograniczona. Niewielka preferencja może spowodować dowolnie dużą lukę.
- Strata kieruje wybrane i odrzucone log-sondy w przeciwnych kierunkach. Może zepchnąć wybrany absolutny log-prob w dół, o ile odrzucony spada szybciej. Jest to zjawisko Zdegradowanej Wybranej Reakcji.
- Preferencje poza dystrybucją (rzadka rzadka para vs rzadka rzadka para) dają arbitralne ukryte nagrody.

### IPO (Azar i in., 2024)

Optymalizacja preferencji tożsamości zastępuje log-esigmoidę mapowaniem tożsamości na prawdopodobieństwie preferencji. Strata staje się błędem kwadratowym w przypadku ograniczonego celu:

```
L_IPO = (log(pi(y_w | x) / pi_ref(y_w | x)) - log(pi(y_l | x) / pi_ref(y_l | x)) - 1/(2 beta))^2
```

Margines jest ograniczony przez `1/(2 beta)`. Siła preferencji i ukryta różnica w nagrodach są proporcjonalne. Żadnego wybuchu.

### KTO (Ethayarajh i in., 2024)

Optymalizacja Kahnemana-Tversky'ego całkowicie pomija strukturę parami. Biorąc pod uwagę pojedyncze oznaczone wyjście i binarny „pożądany” lub „niepożądany” sygnał, odwzorowuje to użyteczność teorii perspektywy:

```
v(x, y) = sigma(beta * log(pi(y|x) / pi_ref(y|x)) - z_ref)
```

z różnymi wagami zysków i strat (awersja do strat). Korzyści: możesz używać niesparowanych danych, których jest znacznie więcej.

### SimPO (Meng i in., 2024)

Prosta optymalizacja preferencji dopasowuje sygnał treningowy do generacji. Usuń całkowicie politykę referencyjną i znormalizuj logarytm wiarygodności według długości:

```
L_SimPO = -log sigmoid(
  (beta / |y_w|) * log pi(y_w | x)
  - (beta / |y_l|) * log pi(y_l | x)
  - gamma
)
```

z marginesem `gamma` do stabilizacji. Normalizacja długości usuwa zachętę do wykorzystywania trybu błędu odchylenia długości DPO (dłuższy `y_w` daje z konstrukcji większą lukę log-prob).

### ORPO (Hong i in., 2024)

Optymalizacja preferencji ilorazu szans dodaje termin preferencji do standardowego ujemnego logarytmu wiarygodności SFT:

```
L_ORPO = L_NLL(y_w) + lambda * L_OR
L_OR = -log sigmoid(log(odds(y_w) / odds(y_l)))
```

Brak polityki referencyjnej – termin SFT jest regulatorem. Trenuj w jednym etapie od modelu podstawowego do modelu wyrównanego. Brak oddzielnego punktu kontrolnego SFT.

### BPO (zgłoszenie ICLR 2026, identyfikator OpenReview=b97EwMUWu7)

Identyfikuje problem z pogorszonymi wybranymi odpowiedziami: DPO zachowuje ranking `y_w > y_l`, ale bezwzględny log-prawdopodobny wynik `y_w` może spaść. BPO dodaje korektę jednowierszową, która karze ruchy w dół w ramach wybranej odpowiedzi. Zgłoszono +10,1% dokładności w Llama-3.1-8B-Instruktaż rozumowania matematycznego przez DPO.

### Uniwersalny wynik: DAA wciąż nadmiernie optymalizują

Rafailov i in. „Prawa skalowania dla nadmiernej optymalizacji modelu nagród w algorytmach bezpośredniego wyrównania” (NeurIPS 2024) przeszkoliły zasady z DPO, IPO, SLiC na wielu zbiorach danych w ramach budżetów KL. Krzywe nagrody w złocie w porównaniu z KL mają tego samego Gao i in. kształt szczytu i upadku. Ukryta nagroda odpytuje podczas szkolenia próbki spoza dystrybucji; Regularyzacja KL tego nie stabilizuje.

DAA nie umykają Goodhartowi. Zmieniają powierzchnię, w której pojawia się problem, z „nadmiernie zoptymalizowanego modelu wynagrodzeń” na „nadmiernie zoptymalizowany współczynnik polityki referencyjnej”. Uniwersalne rozwiązanie — lepsze dane, zespoły, wcześniejsze zatrzymanie — dotyczy obu.

### Wybierać spośród nich (2026)

- Jeśli masz duże dane dotyczące preferencji w parach: DPO z konserwatywną wersją beta, SimPO, jeśli oczywiste jest odchylenie związane z długością.
- Jeśli masz niesparowane sprzężenie binarne: KTO.
- Jeśli chcesz rurociąg jednostopniowy z modelu podstawowego: ORPO.
- Jeśli widzisz zdegradowane wybrane log-proby w logach DPO: BPO.
- Jeżeli preferencje są bardzo zróżnicowane, a DPO ulega nasyceniu: IPO.

Każde laboratorium uruchamia wszystkie pięć na baterii i wybiera zwycięzcę każdego zadania. Nie ma powodu, dla którego maksimum jest takie samo dla rozumowania matematycznego i bezpieczeństwa.

## Użyj tego

`code/main.py` porównuje sześć strat (DPO, IPO, KTO, SimPO, ORPO, BPO) w zbiorze danych dotyczących preferencji zabawek, gdzie rzeczywista siła preferencji różni się w zależności od pary. Każda strata jest optymalizowana w oparciu o tę samą próbkę 500 par przy zastosowaniu małej polityki softmax. Wykresuje ostateczny współczynnik wygranych, dryf wybranego logarytmu prawdopodobieństwa i ukryty rozkład nagród według metody.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-preference-loss-selector.md`. Biorąc pod uwagę statystyki zbioru danych (sparowany vs niesparowany, zmienna vs jednolita siła preferencji, rozkład długości) i cel (jednostopniowy lub SFT-to-preferencja), zarekomenduj utratę preferencji i zgłoś tryb awarii, przed którym chroni.

## Ćwiczenia

1. Uruchom `code/main.py`. Zgłoś ostateczny wybrany spadek log-prob dla DPO i BPO. BPO powinno zachować wyższe wybrane prawdopodobieństwo bezwzględne — sprawdź to.

2. Zmodyfikuj dane preferencji tak, aby wszystkie pary miały równą siłę. Która z sześciu metod jest najbardziej niezawodna? Które degraduje? Wyjaśnij tutaj zalety IPO.

3. Niech odrzucone odpowiedzi będą średnio 2x dłuższe od wybranych. Nie zmieniając niczego innego, pokaż numerycznie wykorzystanie długości DPO i poprawkę SimPO.

4. Rafailov i in. (NeurIPS 2024) twierdzą, że DAA są nadmiernie zoptymalizowane. Odtwórz wersję jednopunktową: wykreśl rozbieżność KL wybrana-minus-odrzucona i obserwuj nadmierną optymalizację w DPO przy dużej wersji beta.

5. Przeczytaj streszczenie artykułu BPO (OpenReview b97EwMUWu7). Zapisz jednowierszową korektę, którą BPO dodaje do DPO. Potwierdź implementację w `code/main.py`.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| IOD | „RLHF bez modelu nagrody” | Strata wyprowadzona z optymalnego RLHF w postaci zamkniętej; tylko parametry polityki |
| Ukryta nagroda | „stosunek log” | `beta * log(pi(y\|x) / pi_ref(y\|x))` — nagroda sugerowana przez DPO |
| IPO | „ograniczony DPO” | Zastępuje log-esigmoid tożsamością; ukryta luka w nagrodach ograniczona przez `1/(2 beta)` |
| KTO | „niesparowany DPO” | Użyteczność teorii perspektyw w przypadku pojedynczych etykiet z niechęcią do strat |
| SimPO | „DPO bez referencji” | Logarytm wiarygodności znormalizowanej długości + margines; brak polityki referencyjnej |
| ORPO | „jednoetapowy IOD” | NLL + termin preferencji ilorazu szans; pociągi z modelu podstawowego w jednym przejeździe |
| BPO | „wybrany IOD zachowujący” | DPO plus kara za zmniejszenie bezwzględnego log-prawdopodobieństwa wybranej odpowiedzi |
| Zdegradowany Wybrany | „wybrany idzie w dół” | DPO zmniejsza wybrany log-prob, o ile odrzucony spada szybciej |
| DAA | „algorytm bezpośredniego dopasowania” | Dowolna metoda utraty preferencji, która pomija jawne RM |

## Dalsze czytanie

- [Rafailov i in. — Bezpośrednia optymalizacja preferencji (NeurIPS 2023, arXiv:2305.18290)](https://arxiv.org/abs/2305.18290)
- [Azar i in. — Ogólny paradygmat teoretyczny umożliwiający zrozumienie uczenia się na podstawie ludzkich preferencji (AISTATS 2024, arXiv:2310.12036)](https://arxiv.org/abs/2310.12036) — IPO
- [Ethayarajh i in. — KTO: Dopasowanie modelu jako teoretyczna optymalizacja perspektywy (arXiv:2402.01306)](https://arxiv.org/abs/2402.01306)
– [Meng, Xia, Chen – SimPO (NeurIPS 2024, arXiv:2405.14734)](https://arxiv.org/abs/2405.14734)
– [Hong, Lee, Thorne – ORPO (EMNLP 2024, arXiv:2403.07691)](https://arxiv.org/abs/2403.07691)
- [BPO — Optymalizacja zachowania zachowania (ICLR 2026 OpenReview b97EwMUWu7)](https://openreview.net/forum?id=b97EwMUWu7)
- [Rafailov i in. — Prawa skalowania dla nadmiernej optymalizacji RM w DAA (NeurIPS 2024, arXiv:2406.02900)](https://arxiv.org/abs/2406.02900)