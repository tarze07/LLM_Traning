---

name: prompt-sft-data-curator
description: Projektuj i zarządzaj zbiorami danych instrukcji w celu nadzorowanego dostrajania
version: 1.0.0
phase: 10
lesson: 6
tags: [sft, instruction-tuning, fine-tuning, data-curation, alignment]

---

# Kurator danych SFT

Projektując zestaw danych dostrajający instrukcje dla określonej możliwości (generowanie kodu, matematyka, konwersacja, bezpieczeństwo), użyj tej struktury do planowania gromadzenia danych, definiowania kryteriów jakości i strukturyzowania potoku szkoleniowego.

## Wymagania wejściowe

Zapewnij:
- **Możliwości docelowe** (np. „generowanie kodu w języku Python”, „medyczne pytania i odpowiedzi”, „rozmowa wieloobrotowa”)
- **Model podstawowy** (np. Llama 3 8B, Mistral 7B, Qwen 2.5 72B)
- **Budżet** (godziny adnotacji, koszty API dla generowania syntezy)
- **Preferencje formatu** (Alpaca, ShareGPT, ChatML)

## Krok 1: Projekt zbioru danych

### Wytyczne dotyczące rozmiaru

| Poziom jakości | Potrzebne przykłady | Oczekiwany wynik |
|-------------|----------------|--------------------------------|
| Prototyp badawczy | 1000-5000 | Jakość LIMA: porównywalna z większymi zbiorami danych, jeśli przykłady są napisane przez ekspertów |
| Produkcja v1 | 10 000-50 000 | Poziom Stanford Alpaca: solidne instrukcje dotyczące typowych zadań |
| Produkcja v2 | 50 000-200 000 | Vicuna/Llama 2 Poziom czatu: solidny wieloobrotowy, zasięg domeny |

Jakość zawsze przewyższa ilość. 1000 przykładów napisanych przez ekspertów (LIMA, maj 2023 r.) dopasowanych modeli przeszkolonych na ponad 50 000 przykładów. Ustal priorytety:

1. **Różnorodność** – obejmuje pełen zakres możliwości celu
2. **Dokładność** – każda odpowiedź musi być zgodna ze stanem faktycznym
3. **Przejrzystość** – odpowiedzi powinny być zwięzłe i dobrze ustrukturyzowane
4. **Stopień trudności** – zawiera przykłady łatwe, średnie i trudne

### Lista kontrolna różnorodności

W przypadku asystenta ogólnego przeznaczenia:
- Pytania otwarte (20%)
- Rzeczowe pytania i odpowiedzi (20%)
- Kreatywne pisanie (10%)
- Generowanie kodu (15%)
- Rozumowanie i matematyka (15%)
- Podsumowanie (10%)
- Wykonywanie instrukcji z ograniczeniami (10%)

Dostosuj wartości procentowe dla modeli specyficznych dla domeny. Asystent kodowania może przeznaczyć 60% na generowanie kodu i 20% na jego wyjaśnianie.

## Krok 2: Format danych

### Format Alpaki (jednoobrotowy)

```json
{
  "instruction": "Write a function that reverses a string in Python.",
  "input": "",
  "output": "def reverse_string(s):\n    return s[::-1]"
}
```

Używaj, gdy: zadania jednoetapowe, proste pary instrukcja-odpowiedź, szybkie prototypowanie.

### Udostępnij format GPT (wieloobrotowy)

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

Stosuj, gdy: aplikacje konwersacyjne, ważny jest kontekst wieloobrotowy.

### Format ChatML (ze specjalnymi tokenami)

```
<|im_start|>system
You are a Python expert.<|im_end|>
<|im_start|>user
How do I reverse a string?<|im_end|>
<|im_start|>assistant
Use slicing: s[::-1]<|im_end|>
```

Użyj, gdy: kierowanie na modele korzystające natywnie z ChatML (Qwen, Yi).

## Krok 3: Kryteria jakości

### Kontrole na przykładach

1. **Istotność odpowiedzi**: Czy odpowiedź faktycznie odpowiada instrukcji?
2. **Dokładność faktów**: Czy wszystkie twierdzenia są weryfikowalne i prawidłowe?
3. **Kompletność**: Czy odpowiedź w pełni odnosi się do instrukcji?
4. **Zwięzłość**: Czy tę samą informację można przekazać mniejszą liczbą słów?
5. **Spójność formatu**: Czy odpowiedź jest zgodna z oczekiwanym stylem?

### Czerwone flagi (odrzuć przykład)

- Odpowiedź sama w sobie jest sprzeczna
- Odpowiedź zawiera szkodliwe treści bez odmowy
- Odpowiedź wywołuje halucynacje faktów lub cytatów
- Instrukcja jest niejednoznaczna, a odpowiedź nie wyjaśnia
- Odpowiedź jest kopią przeformułowanej instrukcji

### Kontrole na poziomie zbioru danych

- Nie więcej niż 5% przykładów z jednego źródła/szablonu
- Co najmniej 80% żetonów odpowiedzi ma znaczenie (nie wypełnia)
- Średnia długość odpowiedzi wynosi 50-200 tokenów (unikaj bardzo krótkich lub bardzo długich)
- Różnorodność podpowiedzi systemowych: reprezentowanych jest co najmniej 10 różnych podpowiedzi systemowych

## Krok 4: Konfiguracja treningu

| Parametr | Zalecany zakres | Notatki |
|----------|--------------------------------|-------|
| Szybkość uczenia się | 1e-5 do 5e-5 | Niższe dla większych modeli (1e-5 dla 70B, 5e-5 dla 7B) |
| Epoki | 1-3 | Monitoruj utratę walidacji, zatrzymaj się przy pierwszych oznakach wzrostu |
| Wielkość partii | 32-128 | Skaluj z akumulacją gradientu, jeśli jest ograniczona przez GPU |
| Rozgrzewka | 0-5% kroków | Mniej krytyczne niż przedtreningowe |
| Spadek wagi | 0,0-0,1 | Opcjonalnie w przypadku krótkich serii dostrajających |
| Maskowanie strat | Tylko tokeny odpowiedzi | Instrukcja maski i tokeny podpowiedzi systemu |
| Mieszanie danych przedtreningowych | 2-5% | Mieszaj surowy tekst, aby zapobiec katastrofalnemu zapomnieniu |

## Krok 5: Protokół oceny

Po szkoleniu oceń:

1. **Wskaźnik podążania za instrukcją**: Procent podpowiedzi testowych, w przypadku których model generuje odpowiednią, pełną odpowiedź
2. **Wynik zapomnienia**: Zakłopotanie na wyciągniętym korpusie tekstu ogólnego w porównaniu z modelem podstawowym
3. **Zgodność z formatem**: Procent odpowiedzi zgodnych z oczekiwanym formatem czatu
4. **MT-Bench lub AlpacaEval**: standardowe testy porównawcze dla modeli dostosowanych do instrukcji
5. **Ocena specyficzna dla domeny**: Niestandardowa ocena docelowych możliwości

### Znaki ostrzegawcze

- Utrata walidacji wzrasta po epoce 1: przesadzasz, skracasz epoki lub zwiększasz dane
- Wzrost wyniku w zapominaniu > 15%: wskaźnik uczenia się jest zbyt wysoki lub zbyt wiele epok
- Model dosłownie odtwarza przykłady szkoleniowe: poważne nadmierne dopasowanie, wymaga bardziej zróżnicowanych danych
- Model odmawia łagodnych instrukcji: przeszkolony w zakresie danych dotyczących bezpieczeństwa, przywróć równowagę zbioru danych