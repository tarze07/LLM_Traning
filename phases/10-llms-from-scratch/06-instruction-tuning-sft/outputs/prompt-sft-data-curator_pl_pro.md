---

name: prompt-sft-data-curator
description: Projektuj i zarządzaj zbiorami danych instrukcji w celu nadzorowanego dostrajania (SFT)
version: 1.0.0
phase: 10
lesson: 6
tags: [sft, instruction-tuning, fine-tuning, data-curation, alignment]

---

# Kurator danych dla SFT (Supervised Fine-Tuning)

Projektując zbiór danych do instruction tuningu dla konkretnych umiejętności (generowanie kodu, matematyka, konwersacja, bezpieczeństwo), użyj poniższego schematu do zaplanowania gromadzenia danych, zdefiniowania kryteriów jakości oraz ustrukturyzowania potoku uczenia.

## Wymagania wejściowe

Podaj:
- **Docelowe umiejętności** (np. „generowanie kodu w języku Python”, „medyczne pytania i odpowiedzi”, „wieloturowa konwersacja”)
- **Model podstawowy** (np. Llama 3 8B, Mistral 7B, Qwen 2.5 72B)
- **Budżet** (roboczogodziny adnotatorów, koszty API dla generowania danych syntetycznych)
- **Preferencje formatu** (Alpaca, ShareGPT, ChatML)

## Krok 1: Projekt zbioru danych

### Wytyczne dotyczące rozmiaru zbioru

| Poziom / Cel | Liczba przykładów | Oczekiwany rezultat |
|-------------|----------------|--------------------------------|
| Prototyp badawczy | 1000-5000 | Poziom LIMA: jakość porównywalna z większymi zbiorami danych, pod warunkiem że przykłady są przygotowane przez ekspertów |
| Produkcja v1 | 10 000-50 000 | Poziom Stanford Alpaca: solidne instrukcje dla typowych zadań |
| Produkcja v2 | 50 000-200 000 | Poziom Llama 2 Chat / Vicuna: zaawansowane konwersacje wieloturowe, szeroki zakres dziedzinowy |

Jakość zawsze przewyższa ilość. 1000 przykładów napisanych przez ekspertów (LIMA, maj 2023 r.) pozwoliło uzyskać wyniki dorównujące modelom wytrenowanym na ponad 50 000 przykładach. Nadaj priorytet następującym aspektom:

1. **Różnorodność** – pokrycie pełnego zakresu docelowych umiejętności
2. **Poprawność** – każda odpowiedź musi być merytorycznie poprawna
3. **Klarowność** – odpowiedzi powinny być zwięzłe i dobrze ustrukturyzowane
4. **Zróżnicowany poziom trudności** – uwzględnienie zadań łatwych, średnich i trudnych

### Struktura różnorodności danych

W przypadku asystenta ogólnego przeznaczenia:
- Pytania otwarte (20%)
- Rzeczowe pytania i odpowiedzi (20%)
- Kreatywne pisanie (10%)
- Generowanie kodu (15%)
- Rozumowanie i matematyka (15%)
- Podsumowanie (10%)
- Wykonywanie instrukcji z narzuconymi ograniczeniami (constraint-following) (10%)

Dostosuj proporcje dla modeli specyficznych dla danej dziedziny. Na przykład asystent kodowania może wymagać 60% danych przeznaczonych na generowanie kodu i 20% na jego objaśnianie.

## Krok 2: Format danych

### Format Alpaca (jednoturowy - single-turn)

```json
{
  "instruction": "Write a function that reverses a string in Python.",
  "input": "",
  "output": "def reverse_string(s):\n    return s[::-1]"
}
```

Zastosowanie: zadania jednostopniowe, proste pary instrukcja-odpowiedź, szybkie prototypowanie.

### Format ShareGPT (wieloturowy - multi-turn)

```json
{
  "conversations": [
    {"from": "system", "value": "You are a Python expert."},
    {"from": "human", "value": "How do I reverse a string?"},
    {"from": "gpt", "value": "Use slicing: s[::-1]"},
    {"from": "human", "value": "What about for a list?"},
    {"from": "gpt", "value": "Same syntax works: my_list[::-1]"}
  ]
}
```

Zastosowanie: aplikacje konwersacyjne, gdzie kluczowe jest utrzymanie kontekstu wieloturowego.

### Format ChatML

```
<|im_start|>system
You are a Python expert.<|im_end|>
<|im_start|>user
How do I reverse a string?<|im_end|>
<|im_start|>assistant
Use slicing: s[::-1]<|im_end|>
```

Zastosowanie: modele natywnie korzystające z ChatML (np. Qwen, Yi).

## Krok 3: Kryteria jakości danych

### Walidacja pojedynczych przykładów

1. **Relewantność odpowiedzi**: Czy odpowiedź stanowi bezpośrednią i trafną reakcję na instrukcję?
2. **Poprawność merytoryczna**: Czy wszystkie zawarte w odpowiedzi fakty są prawdziwe i weryfikowalne?
3. **Kompletność**: Czy odpowiedź w pełni wyczerpuje zagadnienie postawione w instrukcji?
4. **Zwięzłość**: Czy te same informacje można przekazać w prostszy i krótszy sposób bez utraty jakości?
5. **Spójność formatu**: Czy odpowiedź jest zgodna z oczekiwanym stylem i szablonem?

### Czerwone flagi (odrzuć przykład, jeśli):

- Odpowiedź jest wewnętrznie sprzeczna
- Odpowiedź zawiera szkodliwe treści (brak prawidłowej odmowy)
- Odpowiedź zawiera halucynacje faktów, źródeł lub cytatów
- Instrukcja jest niejednoznaczna, a model nie prosi o wyjaśnienie lub przyjmuje błędne założenia
- Odpowiedź jest jedynie sparafrazowaną instrukcją

### Walidacja na poziomie zbioru danych

- Maksymalnie 5% przykładów pochodzi z jednego źródła/szablonu
- Co najmniej 80% tokenów odpowiedzi niesie treść (brak niepotrzebnych zapychaczy)
- Średnia długość odpowiedzi wynosi 50-200 tokenów (unikaj skrajnie krótkich lub skrajnie długich odpowiedzi)
- Różnorodność promptów systemowych: zbiór zawiera co najmniej 10 unikalnych promptów systemowych

## Krok 4: Konfiguracja treningu (SFT Hyperparameters)

| Parametr | Zalecany zakres | Uwagi |
|----------|--------------------------------|-------|
| Szybkość uczenia się | 1e-5 do 5e-5 | Niższe wartości dla większych modeli (np. 1e-5 dla 70B, 5e-5 dla 7B) |
| Epoki | 1-3 | Monitoruj stratę na zbiorze walidacyjnym; zatrzymaj trening przy pierwszych oznakach overfittingu |
| Wielkość partii | 32-128 | Global batch size. Skaluj z akumulacją gradientów przy ograniczeniach VRAM |
| Rozgrzewka | 0-5% kroków | Warmup steps. Mniej krytyczne niż podczas pre-trainingu |
| Spadek wagi | 0,0-0,1 | Weight decay. Opcjonalne w przypadku krótkich procesów dostrajania |
| Maskowanie strat | Tylko tokeny odpowiedzi | Wyliczaj stratę (loss) tylko na tokenach odpowiedzi asystenta; maskuj prompty użytkownika i systemowe |
| Mieszanie danych przedtreningowych | 2-5% | Dodatek danych pre-trainingowych zapobiega zjawisku katastrofalnego zapominania |

## Krok 5: Protokół ewaluacji

Po zakończeniu treningu oceń:

1. **Wskaźnik podążania za instrukcjami (instruction-following rate)**: Procent promptów testowych, na które model wygenerował poprawną, kompletną odpowiedź.
2. **Spadek wiedzy ogólnej (forgetting score)**: Wzrost perplexity na wydzielonym korpusie tekstów ogólnych (held-out) w porównaniu z modelem bazowym.
3. **Zgodność z formatem**: Odsetek odpowiedzi ściśle pasujących do wybranego formatu czatu.
4. **MT-Bench lub AlpacaEval**: Standardowe benchmarki dla modeli po procesie instruction tuningu.
5. **Ewaluacja dziedzinowa**: Dedykowane testy sprawdzające docelowe umiejętności.

### Sygnały ostrzegawcze (niepokojące objawy)

- Strata walidacyjna (validation loss) zaczyna rosnąć po pierwszej epoce: overfitting (przetrenowanie) – należy zmniejszyć liczbę epok lub dostarczyć więcej zróżnicowanych danych.
- Wzrost perplexity w testach zapominania > 15%: współczynnik uczenia (learning rate) jest za wysoki lub wykonano zbyt wiele epok.
- Model dosłownie kopiuje przykłady ze zbioru treningowego: silny overfitting – wymagane są bardziej zróżnicowane i sparafrazowane dane.
- Model odrzuca neutralne instrukcje (oversafety): zbyt duży udział danych dotyczących bezpieczeństwa w treningu – należy przywrócić odpowiednie proporcje w zbiorze.
