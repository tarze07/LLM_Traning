---

name: prompt-reward-model-designer
description: Projektuj potoki szkoleniowe modelu nagrody dla wyrównania RLHF
version: 1.0.0
phase: 10
lesson: 7
tags: [rlhf, reward-model, ppo, alignment, human-feedback, preference-learning]

---

# Projektant modeli nagród

Budując potok RLHF w celu dostosowania modelu językowego do docelowego zachowania (przydatność, umiejętność kodowania, bezpieczeństwo, uczciwość), użyj tej struktury do zaprojektowania protokołu gromadzenia danych, wyszkolenia modelu nagrody i skonfigurowania PPO.

## Wymagania wejściowe

Zapewnij:
- **Docelowe zachowanie** (np. „pomocny i nieszkodliwy asystent”, „ekspert w dziedzinie programowania w języku Python”, „medyczne pytania i odpowiedzi dotyczące bezpieczeństwa”)
- **Model podstawowy** (np. Lama 3 8B po SFT, Mistral 7B Czat)
- **Rozmiar modelu nagrody** (zazwyczaj ten sam rozmiar lub większy niż model polisy)
- **Budżet adnotacji** (dostępne godziny pracy lub pary porównawcze)
- **Oblicz budżet** (godziny GPU na szkolenie w zakresie modelu nagrody + PPO)

## Krok 1: Zbieranie danych o preferencjach

### Protokół adnotacji

1. **Wybór natychmiastowy**: Próbka z dystrybucji szkoleniowej SFT plus podpowiedzi spoza dystrybucji (10–20% nowości)
2. **Generowanie odpowiedzi**: Wygeneruj 2-4 odpowiedzi na monit, używając modelu SFT z różnymi temperaturami (0,3, 0,7, 1,0)
3. **Format porównania**: Pokaż komentatorom dokładnie 2 odpowiedzi i zapytaj „Która odpowiedź jest lepsza?”
4. **Rama kryteriów**: Zdefiniuj, co oznacza „lepszy” w Twoim przypadku użycia

### Szablon rubryk

| Kryterium | Waga | Opis |
|----------|--------|------------|
| Przydatność | 40% | Czy odpowiada na pytanie całkowicie i poprawnie? |
| Nieszkodliwość | 25% | Czy unika szkodliwych, stronniczych lub wprowadzających w błąd treści? |
| Uczciwość | 20% | Czy raczej uznaje niepewność niż halucynacje? |
| Zwięzłość | 15% | Czy odpowiedź ma odpowiednią długość w stosunku do pytania? |

Dostosuj wagi do swojego przypadku użycia. Asystent kodowania może ocenić poprawność na 60%, a zwięzłość na 20%.

### Wytyczne dotyczące rozmiaru danych

| Skala | Porównanie par | Godziny pracy adnotatorów | Oczekiwana dokładność RM |
|----------------|---|-----------------|---------------------------------|
| Minimalne wykonalne | 5 000-10 000 | 400-800 | 60-65% |
| Produkcja v1 | 20 000-50 000 | 1600-4000 | 65-72% |
| Produkcja v2 | 100 000-500 000 | 8 000-40 000 | 72-78% |

InstructGPT wykorzystał 33 000 porównań od 40 wykonawców. W pierwszym artykule Anthropic wykorzystano 22 000 spośród 20 komentatorów. Zgoda między komentatorami wynosi zazwyczaj 70–75% – model nagrody nie może przekraczać poziomu porozumienia międzyludzkiego.

### Kontrola jakości

- **Filtrowanie zgodności**: odrzuć pary, w przypadku których zgadza się mniej niż 70% komentatorów
- **Kalibracja adnotatora**: Przeprowadź rundy kalibracyjne ze znanymi dobrymi parami przed prawdziwą adnotacją
– **Wykrywanie stronniczości**: Monitoruj, czy autorzy komentarzy konsekwentnie preferują dłuższe odpowiedzi, język formalny lub określone wzorce
- **Przykłady kontradyktoryjne**: Dołącz 5–10% przykładów mających na celu wyłapanie komentatorów, którzy nie czytają uważnie

## Krok 2: Architektura modelu nagrody

### Decyzje dotyczące architektury

| Decyzja | Zalecenie | Uzasadnienie |
|---------|---------------|----------|
| Architektura bazowa | Ten sam transformator co polisa | Inicjalizacja masy z punktu kontrolnego SFT zapewnia mocne właściwości początkowe |
| Głowica wyjściowa | Pojedynczy rzut liniowy z ostatniego stanu ukrytego | Nagroda skalarna za najbardziej kompletną reprezentację pozycji |
| Rozmiar modelu | >= wielkość modelu polityki | Mniejsza RM wytwarza zawodne sygnały, które destabilizują PPO |
| Inicjalizacja | Punkt kontrolny SFT z nową głowicą wyjściową | Wstępnie wyszkolone funkcje już rejestrują jakość języka |

### Konfiguracja treningu

| Parametr | Zakres | Notatki |
|----------|-------|-------|
| Szybkość uczenia się | 1e-5 do 5e-5 | Niższe niż SFT, ponieważ zadanie jest prostsze |
| Epoki | 1-3 | Nadmierne dopasowanie stanowi główne ryzyko przy ograniczonych danych porównawczych
| Wielkość partii | 64-256 | Każdy „przykład” to para, więc efektywne dane to 2x |
| Funkcja straty | Bradley-Terry: -log(esigmoid(r_preferred - r_rejected)) | Standard porównań parami |
| Podział walidacji | 10-20% | Monitoruj dokładność zatrzymanych par |

### Metryki oceny

1. **Dokładność par**: Jaka część utrzymywanych par preferencji ma poprawną rangę RM? Cel: > 65%
2. **Rozkład marży**: Wykreśl rozkład (r_preferred - r_rejected). Powinien być wyśrodkowany powyżej 0 z kilkoma negatywami.
3. **Kalibracja**: Czy sigmoid(r_preferred - r_rejected) jest bliskie rzeczywistemu prawdopodobieństwu preferencji człowieka?
4. **Dobre uogólnienie**: Testuj na podpowiedziach z innej dystrybucji niż treningowa. Dokładność powinna spadać do < 10%.

## Step 3: PPO Configuration

### Hyperparameters

| Parameter | Typical Value | Effect of Being Too High | Effect of Being Too Low |
|-----------|--------------|-------------------------|------------------------|
| KL coefficient (beta) | 0.01-0.05 | Model barely learns, stays too close to SFT | Reward hacking, degenerate outputs |
| Learning rate | 5e-6 to 3e-5 | Training instability, divergence | Slow convergence, wasted compute |
| Clip ratio (epsilon) | 0.1-0.3 | Large, potentially destabilizing updates | Very conservative updates, slow learning |
| PPO epochs per batch | 1-4 | Overfitting to current batch | Underutilizing each batch |
| Generation batch size | 128-512 | Memory issues | Noisy gradient estimates |
| Max response length | 256-1024 | Slow generation, memory issues | Truncates useful responses |

### Monitoring Dashboard

Track these metrics during PPO training:

1. **Mean reward**: Should increase over training. Plateau is fine; decrease means instability.
2. **KL divergence**: Should stay below 10-20 nats. Spike = reward hacking.
3. **Response length**: Should stay stable. Monotonic increase = verbosity reward hacking.
4. **Entropy**: Token distribution entropy should decrease slowly. Rapid decrease = mode collapse.
5. **Reward model agreement**: Score PPO responses with the reward model; agreement should improve.

### Red Flags During PPO

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Reward increases but outputs degrade | Reward hacking | Increase KL coefficient, retrain RM on adversarial examples |
| KL divergence explodes | Learning rate too high or KL coefficient too low | Reduce lr, increase beta |
| Response length grows monotonically | RM rewards verbosity | Add length penalty to reward, retrain RM with length-controlled pairs |
| All responses become identical | Mode collapse | Increase generation temperature, reduce PPO epochs |
| Reward oscillates wildly | PPO instability | Reduce learning rate, increase clip ratio |

## Step 4: End-to-End Validation

Before deploying an RLHF-trained model:

1. **A/B test vs SFT**: Run the SFT and RLHF models on 200+ test prompts. Have 3+ evaluators compare responses. The RLHF model should win > w 60% przypadków.
2. **Ocena bezpieczeństwa**: Testuj na znanych monitach przeciwnika (jailbreaki, szkodliwe żądania). Model RLHF powinien odpowiednio odmówić.
3. **Sprawdzanie regresji**: Przeprowadź standardowe testy porównawcze (MMLU, HumanEval, MT-Bench), aby upewnić się, że model RLHF nie utracił podstawowych możliwości.
4. **Kontrola zapomnienia**: Zmierz stopień zakłopotania w korpusie tekstu ogólnego. Zwiększenie powinno być < 10% vs the SFT model.
5. **Length analysis**: Compare average response length between SFT and RLHF models. If RLHF is > o 50% dłuższe, model nagrody prawdopodobnie ma tendencję do gadatliwości.