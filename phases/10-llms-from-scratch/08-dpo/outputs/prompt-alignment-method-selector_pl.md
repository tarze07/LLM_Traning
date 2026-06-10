---

name: prompt-alignment-method-selector
description: Wybierz odpowiednią metodę dopasowania (SFT, RLHF, DPO, KTO, ORPO, SimPO) dla swojego przypadku użycia
version: 1.0.0
phase: 10
lesson: 8
tags: [alignment, dpo, rlhf, kto, orpo, simpo, preference-optimization, fine-tuning]

---

# Selektor metody wyrównania

Wybierając metodę dopasowania dla modelu języka, użyj tej struktury do oceny danych, wymagań obliczeniowych i jakości, a następnie wybierz metodę, która najlepiej pasuje do Twoich ograniczeń.

## Wymagania wejściowe

Zapewnij:
- **Model podstawowy** (np. Llama 3 8B, Mistral 7B, Qwen 2.5 72B)
- **Punkt wyjścia** (model podstawowy czy już SFT?)
- **Dostępne dane** (pary instrukcji, pary preferencji, niesparowane oceny lub brak)
- **Budżet obliczeniowy** (godziny GPU, liczba procesorów graficznych)
- **Docelowa jakość** (wystarczająco dobra dla prototypu, konkurencyjna w stosunku do oprogramowania typu open source, najnowocześniejsza)
- **Oś czasu** (dni, tygodnie, miesiące)

## Matryca decyzyjna

### Szybki wybór

| Twoja sytuacja | Zalecana metoda | Dlaczego |
|--------------|---------|-----|
| Brak danych preferencji, tylko pary instrukcji | Tylko SFT | Nie można wyrównać bez sygnału preferencji |
| < 5,000 preference pairs, limited compute | DPO | Simpler pipeline, works well with small data |
| Unpaired feedback (thumbs up/down only) | KTO | Only method that works without pairwise comparisons |
| Want alignment in a single training run | ORPO | Combines SFT + alignment, no reference model |
| Memory-constrained (can't fit reference model) | SimPO | No reference model needed |
| Large-scale, multi-objective alignment | RLHF (PPO) | Separate reward model captures complex preferences |
| Iterative alignment with online data | RLHF (PPO) | Can generate, rate, and retrain in a loop |
| Post-RLHF refinement | DPO | Fine-tune an RLHF model on targeted preferences |

### Detailed Comparison

| Method | Data Requirement | Models in Memory | Training Loops | Stability | Best Scale |
|--------|-----------------|-----------------|----------------|-----------|------------|
| SFT | Instruction pairs (10K+) | 1 | 1 | High | Any |
| RLHF | Preference pairs (20K+) | 3-4 | 3 | Low | Large (70B+) |
| DPO | Preference pairs (5K+) | 2 | 2 (SFT + DPO) | High | Small-Medium (7B-70B) |
| KTO | Unpaired ratings (5K+) | 2 | 2 (SFT + KTO) | High | Any |
| ORPO | Preference pairs (10K+) | 1 | 1 | High | Small-Medium |
| SimPO | Preference pairs (5K+) | 1 | 2 (SFT + SimPO) | High | Small-Medium |

## Method-Specific Configuration

### SFT

- **When to stop**: After 1-3 epochs or when validation loss stops decreasing
- **Key hyperparameter**: Learning rate (1e-5 to 5e-5, lower for bigger models)
- **Critical detail**: Mask instruction tokens in the loss
- **Gotcha**: More than 3 epochs causes memorization; mix in 2-5% pre-training data

### RLHF (PPO)

- **When to use**: You have 20K+ comparison pairs, need multi-objective alignment, or want iterative online learning
- **Key hyperparameters**: KL coefficient (0.01-0.05), PPO clip ratio (0.1-0.3), learning rate (5e-6 to 3e-5)
- **Critical detail**: Reward model should be > = rozmiar modelu polityki
- **Rozumiem**: PPO jest niestabilne; stale monitoruj dywergencję KL i krzywe nagrody

### IOD

- **Kiedy używać**: Masz pary preferencji i chcesz prostszego potoku niż RLHF
- **Kluczowy hiperparametr**: Beta (0,1-0,5; niższy = dozwolone większe odchylenie od wartości odniesienia)
- **Szczegóły krytyczne**: Model referencyjny musi być zamrożoną kopią punktu kontrolnego SFT
- **Mam **: Bardzo wrażliwy na wersję beta; przeszukaj [0,05, 0,1, 0,2, 0,5]

### KTO

- **Kiedy używać**: Masz tylko „dobre” lub „złe” etykiety bez porównań parami
- **Kluczowy hiperparametr**: Beta (taki sam jak DPO), mnożnik niechęci do strat (1,5x w przypadku złych odpowiedzi)
- **Krytyczne szczegóły**: Wymaga mniej więcej zrównoważonych dobrych/złych przykładów (podział 40–60%)
- **Rozumiem**: Bez par sygnał gradientu jest słabszy; może potrzebować więcej danych niż DPO

### ORPO

- **Kiedy używać**: Chcesz całkowicie pominąć SFT i przejść od razu od bazy do wyrównania
- **Kluczowy hiperparametr**: Lambda (waga terminu preferencyjnego vs terminu SFT)
- **Krytyczny szczegół**: Wymaga etykiet instrukcji ORAZ par preferencji w jednym zbiorze danych
- **Mam problem**: Połączony cel może być trudny do zrównoważenia; jeśli dominuje utrata SFT, wyrównanie jest słabe

### SimPO

- **Kiedy używać**: Konfiguracja z ograniczoną pamięcią, w której nie można przechowywać modelu referencyjnego
- **Kluczowy hiperparametr**: Beta, gamma (wykładnik normalizacji długości)
- **Krytyczny szczegół**: Normalizacja długości zapobiega faworyzowaniu przez model krótkich odpowiedzi
- **Rozumiem**: Bez zakotwiczenia modelu referencyjnego model może dryfować dalej; uważnie monitoruj

## Szablony potoków

### Szablon 1: Szybki prototyp (1-2 dni)

```
Base Model -> SFT (1 epoch, 10K examples) -> DPO (3 epochs, 5K pairs)
```

Obliczenia: ~4 godziny GPU dla modelu 7B na A100
Jakość: Solidne przestrzeganie instrukcji, podstawowe dostosowanie preferencji

### Szablon 2: Jakość produkcji (1-2 tygodnie)

```
Base Model -> SFT (2 epochs, 50K examples) -> DPO (5 epochs, 20K pairs) -> Eval -> Iterate
```

Obliczenia: ~40 godzin GPU dla 7B, ~200 godzin GPU dla 70B
Jakość: konkurencyjna w stosunku do modeli RLHF typu open source

### Szablon 3: Najnowocześniejszy (1–3 miesiące)

```
Base Model -> SFT (2 epochs, 100K+ examples) -> RLHF (PPO, 50K+ pairs) -> DPO (targeted refinement) -> Eval -> Iterate
```

Obliczenia: ~500+ godzin GPU dla 70B
Jakość: Zbliżamy się do wyrównania modelu granicznego

### Szablon 4: Minimalne dane (1–2 dni)

```
Base Model -> SFT (1 epoch, 5K examples) -> KTO (unpaired thumbs up/down from users)
```

Obliczenia: ~2 godziny GPU dla 7B
Jakość: lepsza niż tylko SFT przy minimalnym nakładzie związanym z gromadzeniem danych

## Protokół oceny

Po wyrównaniu oceń w następujących wymiarach:

1. **Wskaźnik wygranych preferencji**: Porównaj dopasowany model z modelem SFT na ponad 200 monitach testowych z udziałem sędziów. Cel: > 60% współczynnika wygranych.
2. **Przechowywanie testów porównawczych**: MMLU, HumanEval lub testy porównawcze specyficzne dla domeny. Nie powinien spaść o > 5% w stosunku do wartości bazowej SFT.
3. **MT-Bench lub AlpacaEval**: standardowe wzorce jakości osiowania. Porównaj z opublikowanymi wartościami bazowymi.
4. **Ocena bezpieczeństwa**: Testuj pod kątem monitów, jailbreaków i kategorii szkodliwych żądań.
5. **Różnorodność odpowiedzi**: Zmierz entropię odpowiedzi w 100 podpowiedziach. Niska entropia = załamanie trybu.

## Typowe tryby awarii

| Objaw | Przyczyna | Poprawka specyficzna dla metody |
|--------|-------|----------------------|
| Pełne, doprecyzowane odpowiedzi | Model nagrody / ukryta nagroda faworyzuje długość | DPO: zwiększ wersję beta. RLHF: dodaj karę za długość. SimPO: dostosuj gamma. |
| Modelka zgadza się ze wszystkim | Pochlebstwo z powodu stronniczości danych preferencji | Dodaj pary preferencji, w których poprawna odpowiedź nie zgadza się z użytkownikiem |
| Odrzuca łagodne prośby | Nadmierne dopasowanie danych dotyczących bezpieczeństwa | Zmniejsz odsetek przykładów bezpieczeństwa, dodaj więcej par łagodnych odmów |
| Dane wyjściowe są prawie identyczne z SFT | Beta za wysoka (DPO/KTO) lub współczynnik KL za wysoki (PPO) | Niższy współczynnik beta / KL; model się nie uczy |
| Strata treningowa oscyluje | Szybkość uczenia się jest zbyt wysoka lub niewystarczające dane | Zmniejsz lr o 2-3x; zwiększyć dane dotyczące preferencji |