---

name: prompt-reward-model-designer
description: Zaprojektuj potok uczenia modelu nagrody (Reward Model) na potrzeby dopasowania metodą RLHF
version: 1.0.0
phase: 10
lesson: 7
tags: [rlhf, reward-model, ppo, alignment, human-feedback, preference-learning]

---

# Projektowanie modelu nagrody (Reward Modeling)

Projektując potok RLHF w celu dopasowania modelu językowego do oczekiwanych zachowań (użyteczność, kodowanie, bezpieczeństwo, szczerość), skorzystaj z poniższych wytycznych do zaplanowania procesu zbierania danych, uczenia modelu nagrody i konfiguracji algorytmu PPO.

## Wymagania wejściowe

Podaj (dane wejściowe):
- **Docelowe zachowanie** (np. „pomocny i nieszkodliwy asystent”, „ekspert w dziedzinie programowania w języku Python”, „medyczne pytania i odpowiedzi dotyczące bezpieczeństwa”)
- **Model podstawowy** (np. Llama 3 8B po SFT, Mistral 7B Czat)
- **Rozmiar modelu nagrody (RM)** (zazwyczaj taki sam lub większy niż model polityki)
- **Budżet adnotacji** (dostępne godziny pracy lub pary porównawcze)
- **Budżet obliczeniowy** (liczba godzin pracy GPU na trening modelu nagrody i PPO)

## Krok 1: Zbieranie danych o preferencjach

### Protokół adnotacji

1. **Wybór promptów**: Pobierz próbkę z rozkładu danych treningowych SFT oraz prompty spoza rozkładu (out-of-distribution, 10–20% nowości).
2. **Generowanie odpowiedzi**: Wygeneruj 2-4 odpowiedzi dla każdego promptu za pomocą modelu SFT przy użyciu różnych wartości temperatury (np. 0.3, 0.7, 1.0).
3. **Format porównania**: Zaprezentuj adnotatorom parę odpowiedzi i zadaj pytanie: „Która odpowiedź jest lepsza?”.
4. **Kryteria oceny**: Precyzyjnie zdefiniuj, co oznacza pojęcie „lepszej odpowiedzi” w kontekście danego zastosowania.

### Szablon wytycznych oceniania (Rubrics)

| Kryterium | Waga | Opis |
|----------|--------|------------|
| Przydatność | 40% | Czy odpowiada na pytanie całkowicie i poprawnie? |
| Nieszkodliwość | 25% | Czy unika szkodliwych, stronniczych lub wprowadzających w błąd treści? |
| Szczerość | 20% | Czy przyznaje się do niepewności zamiast halucynować? |
| Zwięzłość | 15% | Czy odpowiedź ma odpowiednią długość w stosunku do pytania? |

Dostosuj wagi do własnych potrzeb. W przypadku asystenta kodowania poprawność może stanowić 60% oceny, a zwięzłość 20%.

### Wytyczne dotyczące rozmiaru zbioru danych

| Skala | Liczba porównań par | Roboczogodziny adnotatorów | Oczekiwana dokładność RM |
|----------------|---|-----------------|---------------------------------|
| MVP (prototyp) | 5 000-10 000 | 400-800 | 60-65% |
| Produkcja v1 | 20 000-50 000 | 1600-4000 | 65-72% |
| Produkcja v2 | 100 000-500 000 | 8 000-40 000 | 72-78% |

InstructGPT wykorzystywał 33 000 porównań przygotowanych przez 40 adnotatorów. Pierwsza publikacja Anthropic opierała się na 22 000 porównań od 20 adnotatorów. Zgodność ocen między ludźmi (inter-annotator agreement) wynosi zazwyczaj 70–75% – dokładność modelu nagrody nie przekroczy naturalnej zgodności ocen ludzkich.

### Kontrola jakości

- **Filtrowanie zgodności ocen**: Odrzuć pary, w przypadku których zgodność adnotatorów wynosi poniżej 70%.
- **Kalibracja adnotatorów**: Przed właściwym etapem adnotacji przeprowadź rundy kalibracyjne na parach o jednoznacznym werdykcie.
- **Detekcja skrzywień (bias)**: Sprawdź, czy adnotatorzy nie preferują bezwzględnie dłuższych wypowiedzi, stylu formalnego lub innych specyficznych wzorców (verbosity bias).
- **Przykłady kontrolne (attention checks)**: Wprowadź 5–10% oczywistych przykładów kontrolnych, aby wykryć adnotatorów, którzy nie czytają uważnie tekstu.

## Krok 2: Architektura modelu nagrody

### Decyzje dotyczące architektury

| Decyzja | Zalecenie | Uzasadnienie |
|---------|---------------|----------|
| Architektura bazowa | Taki sam model typu Transformer jak polityka | Inicjalizacja wag z checkpointu SFT zapewnia doskonały punkt wyjścia |
| Głowica wyjściowa | Pojedyncza projekcja liniowa z ostatniego stanu ukrytego (last hidden state) | Zwraca nagrodę skalarną (scalar reward) |
| Rozmiar modelu | $\ge$ rozmiar modelu polityki | Mniejszy model nagrody generuje niestabilny szum, co zakłóca proces PPO |
| Inicjalizacja | Checkpoint SFT z dodaną nową głowicą wyjściową | Wagi z etapu pre-trainingu i SFT zawierają już kluczowe cechy językowe |

### Konfiguracja treningu

| Parametr | Zalecany zakres | Uwagi |
|----------|-------|-------|
| Szybkość uczenia się | 1e-5 do 5e-5 | Niższa niż przy SFT, ponieważ zadanie regresji preferencji jest prostsze |
| Epoki | 1-3 | Głównym zagrożeniem jest overfitting (nadmierne dopasowanie) do małego zbioru preferencji |
| Wielkość partii | 64-256 | Ponieważ każdy przykład to para odpowiedzi, efektywny batch size jest dwukrotnie większy |
| Funkcja straty | Bradley-Terry: -log(sigmoid(r_preferred - r_rejected)) | Standardowa strata dla porównań parami |
| Podział walidacji | 10-20% | Monitorowanie dokładności klasyfikacji na zbiorze walidacyjnym (held-out) |

### Metryki ewaluacji

1. **Dokładność klasyfikacji preferencji (pairwise accuracy)**: Odsetek poprawnie sklasyfikowanych par ze zbioru walidacyjnego. Cel: > 65%.
2. **Rozkład marginesu (margin distribution)**: Wykres różnic score'ów ($r_{\text{preferred}} - r_{\text{rejected}}$). Rozkład powinien mieć średnią powyżej 0 z niewielką liczbą wartości ujemnych.
3. **Kalibracja**: Sprawdzenie, czy wartość $\sigma(r_{\text{preferred}} - r_{\text{rejected}})$ odpowiada rzeczywistemu prawdopodobieństwu ludzkiego wyboru.
4. **Generalizacja**: Testy na promptach spoza rozkładu treningowego. Spadek dokładności (accuracy drop) powinien wynosić mniej niż 10%.

## Krok 3: Konfiguracja PPO

### Hiperparametry

| Parametr | Typowa wartość | Skutki zbyt wysokiej wartości | Skutki zbyt niskiej wartości |
|-----------|--------------|-------------------------|------------------------|
| Współczynnik KL (beta) | 0.01-0.05 | Model słabo się uczy, pozostaje zbyt blisko modelu SFT | Reward hacking (hakowanie nagrody), zdegenerowane odpowiedzi |
| Współczynnik uczenia (learning rate) | 5e-6 do 3e-5 | Niestabilność treningu, dywergencja (rozbieżność) | Wolna zbieżność, zmarnowane zasoby obliczeniowe |
| Współczynnik przycięcia (epsilon) | 0.1-0.3 | Duże, potencjalnie destabilizujące aktualizacje wag | Bardzo konserwatywne aktualizacje, powolna nauka |
| Epoki PPO na partię danych | 1-4 | Nadmierne dopasowanie (overfitting) do bieżącej partii | Niewystarczające wykorzystanie każdej partii |
| Rozmiar partii generowania | 128-512 | Problemy z pamięcią (VRAM) | Szumne szacunki gradientu |
| Maksymalna długość odpowiedzi | 256-1024 | Wolna generacja, problemy z pamięcią | Obcinanie przydatnych odpowiedzi |

### Panel monitorowania (Monitoring Dashboard)

Śledź poniższe metryki podczas treningu PPO:

1. **Średnia nagroda (Mean reward)**: Powinna rosnąć w trakcie treningu. Stabilizacja (plateau) jest w porządku; spadek oznacza niestabilność.
2. **Dywergencja KL**: Powinna utrzymywać się poniżej 10-20 natów. Gwałtowny wzrost (spike) oznacza hakowanie nagrody (reward hacking).
3. **Długość odpowiedzi**: Powinna pozostać stabilna. Monotoniczny wzrost oznacza hakowanie nagrody poprzez gadatliwość (verbosity reward hacking).
4. **Entropia**: Entropia rozkładu tokenów powinna powoli spadać. Gwałtowny spadek oznacza zapadnięcie rozkładu (mode collapse).
5. **Spójność modelu nagrody (Reward model agreement)**: Oceniaj odpowiedzi PPO za pomocą modelu nagrody – spójność powinna rosnąć.

### Sygnały ostrzegawcze (czerwone flagi) podczas PPO

| Objaw | Prawdopodobna przyczyna | Rozwiązanie |
|---------|-------------|-----|
| Nagroda rośnie, ale jakość odpowiedzi spada | Hakowanie nagrody (reward hacking) | Zwiększ współczynnik KL, dotrenuj model nagrody (RM) na przykładach kontradyktoryjnych |
| Dywergencja KL eksploduje | Współczynnik uczenia za wysoki lub współczynnik KL za niski | Zmniejsz learning rate (lr), zwiększ współczynnik beta |
| Długość odpowiedzi monotonicznie rośnie | Model nagrody premiuje gadatliwość | Dodaj karę za długość (length penalty) do nagrody, dotrenuj model nagrody z kontrolowaną długością par |
| Wszystkie odpowiedzi stają się identyczne | Zapadnięcie rozkładu (mode collapse) | Zwiększ temperaturę generowania, zmniejsz liczbę epok PPO |
| Nagroda gwałtownie oscyluje | Niestabilność algorytmu PPO | Zmniejsz learning rate, zwiększ współczynnik przycięcia (clip ratio) |

## Krok 4: Kompleksowa walidacja (End-to-End)

Przed wdrożeniem modelu wytrenowanego za pomocą RLHF:

1. **Testy A/B w porównaniu do SFT**: Uruchom model SFT oraz model po RLHF na ponad 200 promptach testowych. Zleć porównanie odpowiedzi co najmniej 3 oceniającym. Model po RLHF powinien wygrać w ponad 60% przypadków.
2. **Ewaluacja bezpieczeństwa**: Przetestuj model na znanych promptach kontradyktoryjnych (próby jailbreaku, szkodliwe zapytania). Model po RLHF powinien konsekwentnie odmawiać wykonania szkodliwych poleceń.
3. **Weryfikacja regresji**: Uruchom standardowe benchmarki (np. MMLU, HumanEval, MT-Bench), aby upewnić się, że model po RLHF nie utracił swoich podstawowych zdolności.
4. **Weryfikacja zapominania**: Zmierz wartość perplexity na ogólnym korpusie tekstowym. Wzrost perplexity powinien być mniejszy niż 10% w porównaniu z modelem SFT.
5. **Analiza długości**: Porównaj średnią długość odpowiedzi modelu SFT i modelu po RLHF. Jeśli odpowiedzi po RLHF są o ponad 50% dłuższe, oznacza to prawdopodobną tendencję modelu nagrody do premiowania gadatliwości.
