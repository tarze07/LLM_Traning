---

name: prompt-alignment-method-selector
description: Wybierz odpowiednią metodę dopasowania (SFT, RLHF, DPO, KTO, ORPO, SimPO) dla swojego przypadku użycia
version: 1.0.0
phase: 10
lesson: 8
tags: [alignment, dpo, rlhf, kto, orpo, simpo, preference-optimization, fine-tuning]

---

# Wybór metody dopasowania (Alignment Method Selector)

Wybierając metodę dopasowania (alignment) dla modelu językowego, skorzystaj z poniższego schematu do oceny zbioru danych, wymagań obliczeniowych i pożądanej jakości, aby wybrać podejście najlepiej dostosowane do Twoich zasobów.

## Wymagania wejściowe

Podaj (dane wejściowe):
- **Model podstawowy** (np. Llama 3 8B, Mistral 7B, Qwen 2.5 72B)
- **Punkt wyjścia** (model podstawowy czy już SFT?)
- **Dostępne dane** (pary instrukcji, pary preferencji, niesparowane oceny lub ich brak)
- **Budżet obliczeniowy** (liczba godzin pracy GPU, liczba procesorów graficznych)
- **Docelowa jakość** (zadowalający prototyp, poziom modeli open-source, stan wiedzy / state-of-the-art)
- **Horyzont czasowy** (dni, tygodnie, miesiące)

## Matryca decyzyjna

### Szybki wybór

| Twoja sytuacja | Zalecana metoda | Dlaczego |
|--------------|---------|-----|
| Brak danych preferencji, tylko pary instrukcji | Tylko SFT | Nie można wykonać dopasowania bez sygnału preferencji |
| < 5 000 par preferencji, ograniczone zasoby obliczeniowe | DPO | Prostszy potok przetwarzania, dobrze radzi sobie z małą ilością danych |
| Niesparowane informacje zwrotne (tylko łapka w górę/w dół) | KTO | Jedyna metoda działająca bez porównań parami |
| Chcesz dopasować model w jednym przebiegu treningowym | ORPO | Łączy SFT i dopasowanie, brak modelu referencyjnego |
| Ograniczenie pamięci (brak miejsca na model referencyjny) | SimPO | Nie wymaga modelu referencyjnego |
| Dopasowanie na dużą skalę, wielocelowe | RLHF (PPO) | Osobny model nagrody (RM) wychwytuje złożone preferencje |
| Interaktywne dopasowanie z danymi online | RLHF (PPO) | Pozwala na generowanie, ocenianie i uczenie w pętli |
| Dostrajanie po RLHF | DPO | Dostrajanie modelu po RLHF na specyficzne preferencje |

### Szczegółowe porównanie

| Metoda | Wymagania dotyczące danych | Modele w pamięci | Pętle treningowe | Stabilność | Optymalna skala |
|--------|-----------------|-----------------|----------------|-----------|------------|
| SFT | Pary instrukcji (10k+) | 1 | 1 | Wysoka | Dowolna |
| RLHF | Pary preferencji (20k+) | 3-4 | 3 | Niska | Duża (70B+) |
| DPO | Pary preferencji (5k+) | 2 | 2 (SFT + DPO) | Wysoka | Mała-Średnia (7B-70B) |
| KTO | Niesparowane oceny (5k+) | 2 | 2 (SFT + KTO) | Wysoka | Dowolna |
| ORPO | Pary preferencji (10k+) | 1 | 1 | Wysoka | Mała-Średnia |
| SimPO | Pary preferencji (5k+) | 1 | 2 (SFT + SimPO) | Wysoka | Mała-Średnia |

## Konfiguracja specyficzna dla danej metody

### SFT

- **Kiedy zakończyć**: Po 1–3 epokach lub gdy strata na zbiorze walidacyjnym przestaje spadać.
- **Kluczowy hiperparametr**: Współczynnik uczenia (learning rate: 1e-5 do 5e-5, niższy dla większych modeli).
- **Kluczowy szczegół**: Maskowanie tokenów instrukcji w obliczaniu straty (loss).
- **Uwaga (Gotcha)**: Trening trwający dłużej niż 3 epoki powoduje zapamiętywanie danych (overfitting); wymieszaj z 2–5% danych pre-trainingowych.

### RLHF (PPO)

- **Kiedy stosować**: Masz ponad 20k par porównawczych, potrzebujesz wielocelowego dopasowania lub zależy Ci na interaktywnym uczeniu online (online learning).
- **Kluczowe hiperparametry**: Współczynnik KL (0.01-0.05), współczynnik przycięcia PPO (0.1-0.3), learning rate (5e-6 do 3e-5).
- **Kluczowy szczegół**: Model nagrody (RM) powinien być większy lub równy rozmiarowi modelu polityki.
- **Uwaga (Gotcha)**: PPO charakteryzuje się dużą niestabilnością – stale monitoruj dywergencję KL oraz krzywe nagrody.

### DPO

- **Kiedy stosować**: Posiadasz pary preferencji i chcesz wdrożyć prostszy potok treningowy niż w przypadku RLHF.
- **Kluczowy hiperparametr**: Beta (0.1-0.5; niższa wartość dopuszcza większe odchylenie od modelu referencyjnego).
- **Kluczowy szczegół**: Model referencyjny musi być zamrożoną kopią checkpointu SFT.
- **Uwaga (Gotcha)**: Metoda bardzo wrażliwa na wartość hiperparametru beta; przetestuj wartości z zakresu [0.05, 0.1, 0.2, 0.5].

### KTO

- **Kiedy stosować**: Posiadasz jedynie niesparowane etykiety typu „dobre” lub „złe” odpowiedzi użytkowników, bez bezpośrednich porównań.
- **Kluczowy hiperparametr**: Beta (analogicznie do DPO) oraz mnożnik straty dla negatywnych odpowiedzi (zazwyczaj 1.33-1.5).
- **Kluczowy szczegół**: Wymaga zrównoważonego rozkładu pozytywnych i negatywnych przykładów w zbiorze (proporcja około 40-60%).
- **Uwaga (Gotcha)**: Bez bezpośrednich porównań parowych sygnał gradientu jest słabszy, co może wymagać większego zbioru danych niż w przypadku DPO.

### ORPO

- **Kiedy stosować**: Chcesz całkowicie pominąć etap SFT i przejść bezpośrednio od modelu bazowego do dopasowania.
- **Kluczowy hiperparametr**: Lambda (współczynnik określający wagę straty preferencji w stosunku do straty SFT).
- **Kluczowy szczegół**: Wymaga instrukcji oraz par preferencji połączonych w jednym zbiorze danych.
- **Uwaga (Gotcha)**: Złożona funkcja straty może być trudna do zoptymalizowania; jeśli zdominują ją składowe SFT, efekty dopasowania będą znikome.

### SimPO

- **Kiedy stosować**: Środowisko o ograniczonej pamięci VRAM, gdzie nie ma możliwości załadowania w tle modelu referencyjnego.
- **Kluczowy hiperparametr**: Beta oraz gamma (współczynnik regulujący wpływ długości generowanego tekstu).
- **Kluczowy szczegół**: Normalizacja długości (length normalization) zapobiega promowaniu przez model nadmiernie rozwlekłych odpowiedzi.
- **Uwaga (Gotcha)**: Bez kotwicy w postaci modelu referencyjnego, zachowanie modelu może ulec nadmiernemu dryfowi – należy uważnie śledzić proces treningu.

## Szablony potoków

### Szablon 1: Szybki prototyp (1-2 dni)

```
Base Model -> SFT (1 epoch, 10K examples) -> DPO (3 epochs, 5K pairs)
```

Zasoby obliczeniowe: ~4 godziny pracy GPU A100 dla modelu 7B
Jakość: Dobre podążanie za instrukcjami, podstawowe dopasowanie preferencji

### Szablon 2: Jakość produkcji (1-2 tygodnie)

```
Base Model -> SFT (2 epochs, 50K examples) -> DPO (5 epochs, 20K pairs) -> Eval -> Iterate
```

Zasoby obliczeniowe: ~40 godzin GPU dla modelu 7B, ~200 godzin GPU dla 70B
Jakość: konkurencyjna w stosunku do wiodących modeli open-source po RLHF

### Szablon 3: Najnowocześniejszy (1–3 miesiące)

```
Base Model -> SFT (2 epochs, 100K+ examples) -> RLHF (PPO, 50K+ pairs) -> DPO (targeted refinement) -> Eval -> Iterate
```

Zasoby obliczeniowe: $\ge$ 500 godzin GPU dla modelu 70B
Jakość: Zbliżona do komercyjnych modeli frontier (np. GPT-4)

### Szablon 4: Minimalne dane (1–2 dni)

```
Base Model -> SFT (1 epoch, 5K examples) -> KTO (unpaired thumbs up/down from users)
```

Zasoby obliczeniowe: ~2 godziny GPU dla modelu 7B
Jakość: lepsza niż samo SFT przy minimalnym nakładzie na zbieranie danych preferencji

## Protokół ewaluacji

Po dopasowaniu oceń model w następujących wymiarach:

1. **Wskaźnik wygranych (preference win rate)**: Porównanie modelu po dopasowaniu z modelem bazowym SFT na zestawie ponad 200 testowych promptów z udziałem sędziów (np. GPT-4). Cel: > 60% wygranych.
2. **Stabilność benchmarków**: Testy na MMLU, HumanEval lub benchmarkach specyficznych dla domeny. Spadek w stosunku do modelu SFT nie powinien przekraczarzać 5%.
3. **MT-Bench lub AlpacaEval**: Standardowe benchmarki jakości dopasowania (alignment). Porównaj wyniki z oficjalnymi danymi referencyjnymi.
4. **Ewaluacja bezpieczeństwa**: Testy z użyciem promptów jailbreak oraz zapytań z kategorii zabronionych.
5. **Różnorodność odpowiedzi**: Zmierz entropię rozkładu odpowiedzi na bazie 100 promptów testowych. Niska entropia oznacza wystąpienie problemu mode collapse.

## Typowe tryby awarii

| Objaw | Przyczyna | Poprawka specyficzna dla metody |
|--------|-------|----------------------|
| Przegadane, zbyt długie odpowiedzi | Model nagrody (jawny lub niejawny) faworyzuje długość tekstu (verbosity bias) | DPO: zwiększ wartość beta. RLHF: dodaj karę za długość. SimPO: dostosuj parametr gamma. |
| Model zgadza się ze wszystkimi tezami użytkownika (pochlebstwo) | Skrzywienie w zbiorze preferencji (sycophancy bias) | Dodaj pary preferencji, w których poprawna odpowiedź koryguje błędne założenia użytkownika. |
| Model odrzuca neutralne zapytania | Nadmierne dopasowanie do reguł bezpieczeństwa (oversafety) | Zmniejsz udział przykładów dotyczących bezpieczeństwa w zbiorze treningowym i dodaj bezpieczne wzorce odpowiedzi. |
| Wyniki są niemal identyczne jak w modelu SFT | Zbyt wysoka beta (DPO/KTO) lub zbyt wysoki współczynnik KL (PPO) | Zmniejsz beta / współczynnik KL – model słabo się uczy. |
| Strata treningowa silnie oscyluje | Zbyt wysoki współczynnik uczenia lub niewystarczająca ilość danych | Zmniejsz learning rate 2-3 krotnie, zwiększ wolumen danych preferencji. |
