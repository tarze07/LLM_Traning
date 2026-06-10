---

name: skill-debug-checklist
description: Lista kontrolna drzewa decyzyjnego do debugowania błędów uczenia sieci neuronowej
version: 1.0.0
phase: 3
lesson: 13
tags: [debugging, neural-networks, training, diagnostics, deep-learning]

---

# Lista kontrolna debugowania sieci neuronowej

Protokół systematycznego debugowania w przypadku niepowodzeń szkolenia. Pracuj nad nimi w odpowiedniej kolejności — większość błędów wyłapuje się w pierwszych 3 krokach.

## Przed szkoleniem (zapobieganie błędom)

1. Wydrukuj architekturę modelu i liczbę parametrów. Czy rozmiar ma sens dla Twoich danych?
2. Wykonaj pojedyncze przejście do przodu z losowymi danymi wejściowymi. Czy kształt wyjściowy odpowiada kształtowi docelowemu?
3. Sprawdź, czy etykiety mają poprawny typ d (CrossEntropyLoss potrzebuje Long, BCELoss potrzebuje Float)
4. Sprawdź normalizację danych: wartości wejściowe powinny mieć średnią bliską 0 i std bliską 1
5. Wydrukuj 5 losowych par (wejście, etykieta). Czy etykiety odpowiadają Twoim oczekiwaniom?
6. Potwierdź, że podział pociąg/test nie zawiera duplikatów próbek

## Test Overfit-one-batch (60 sekund, wyłapuje 80% błędów)

1. Pobierz 8-32 próbki ze swojego zbioru treningowego
2. Trenuj 200 kroków w rozsądnym tempie
3. Strata powinna zbliżać się do 0. Dokładność treningu powinna sięgać 100%
4. Jeśli się nie powiedzie: błąd tkwi w modelu, funkcji straty lub pętli szkoleniowej, a nie w danych lub hiperparametrach
5. Jeśli przejdzie: przejdź do pełnego treningu

## Strata nie maleje

1. Sprawdź tempo uczenia się. Wypróbuj 3 wartości: prąd/10, prąd, prąd*10
2. Wydrukuj normy gradientu dla każdej warstwy. Wszystkie zera oznaczają martwą sieć lub odłączony wykres
3. Sprawdź parametry `requires_grad=True`. Sprawdź, czy wywołano `loss.backward()`
4. Sprawdź, czy `optimizer.zero_grad()` jest wywoływany przed `loss.backward()`
5. Sprawdź, czy `optimizer.step()` jest wywoływany po `loss.backward()`
6. Sprawdź, czy parametry modelu zostały przesłane do optymalizatora: `optimizer = Adam(model.parameters())`

## Strata to NaN lub Inf

1. Zmniejsz tempo uczenia się 10x
2. Dodaj epsilon do wszystkich wywołań log(): `torch.log(x + 1e-7)`
3. Dodaj epsilon do wszystkich podziałów: `x / (y + 1e-8)`
4. Przewidywania zacisku: `torch.clamp(pred, 1e-7, 1 - 1e-7)` przed utratą p.n.e
5. Użyj `torch.autograd.detect_anomaly()`, aby znaleźć dokładną operację
6. Sprawdź obecność NaN w danych wejściowych: `assert not torch.isnan(x).any()`

## Strata oscylacyjna

1. Zmniejsz tempo uczenia się 3-10x
2. Zwiększ wielkość partii (zmniejsza szum gradientowy)
3. Dodaj obcinanie gradientu: `torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)`
4. Przełącz z SGD na Adama (adaptacyjny LR według parametru)
5. Dodaj rozgrzewkę w tempie uczenia się przez pierwsze 5-10% treningu

## Nadmierne dopasowanie (wysoka wydajność pociągu, niska wydajność testowa)

1. Dodaj spadek (zacznij od p=0,1, zwiększ do 0,5)
2. Dodaj spadek masy do optymalizatora: `Adam(params, weight_decay=1e-4)`
3. Zmniejsz rozmiar modelu (mniej warstw lub węższe warstwy)
4. Dodaj rozszerzenie danych
5. Użyj wcześniejszego zatrzymania: zatrzymaj, gdy utrata walidacji wzrasta przez ponad 5 epok
6. Sprawdź, czy nie ma wycieków danych pomiędzy pociągiem a zestawami testowymi

## Niedopasowanie (zarówno w trybie pociągowym, jak i testowym)

1. Zwiększ pojemność modelu (więcej warstw, szersze warstwy)
2. Trenuj przez więcej epok
3. Zwiększ tempo uczenia się (ostrożnie)
4. Usuń tymczasowo regularyzację, aby sprawdzić, czy model może się uczyć
5. Sprawdź, czy Twój model jest wystarczająco wyrazisty, aby sprostać zadaniu

## Martwe neurony ReLU

1. Sprawdź udział zerowych aktywacji na warstwę. >50% to problem
2. Przełącz na LeakyReLU(0.01) lub GELU
3. Użyj inicjalizacji Kaiminga dla wag
4. Zmniejsz tempo uczenia się (duże aktualizacje mogą wepchnąć neurony w martwą strefę)
5. Dodaj normalizację wsadową przed aktywacją funkcji

## Skrócona instrukcja: punkty początkowe szybkości uczenia się

| Optymalizator | Zadanie | Rozpoczęcie LR |
|--------------|------|------------|
| Adama | Szkolenie od podstaw | 1e-3 |
| Adama | Dostrajanie wstępnie przeszkolone | 1e-5 |
| SGD + dynamika | Szkolenie od podstaw | 1e-1 |
| SGD + dynamika | Dostrajanie wstępnie przeszkolone | 1e-3 |
| AdamW | Szkolenie transformatorowe | 3e-4 |

## Skrócona instrukcja: efekty wielkości partii

| Wielkość partii | Szum gradientowy | Pamięć | Uogólnienie |
|----------|---------------|--------|--------------|
| 8-16 | Wysoki (głośny) | Niski | Często lepiej |
| 32-64 | Umiarkowany | Umiarkowany | Dobre ustawienie domyślne |
| 128-256 | Niski (gładki) | Wysoki | Może potrzebować rozgrzewki |
| 512+ | Bardzo niski | Bardzo wysoki | Wymaga skalowania LR |

## Gdy nic nie działa

1. Uprość model do 1 ukrytej warstwy. Czy się uczy?
2. Uprość dane do 100 próbek. Czy to przesada?
3. Zastąp swoją stratę MSE. Czy to się zbiega?
4. Zamień optymalizator na SGD(lr=0,01). Czy powoduje postęp?
5. Zastąp swoje dane danymi syntetycznymi (np. y = x[0] > 0). Czy się uczy?
6. Jeśli żadne z powyższych nie zadziała: błąd występuje w kodzie, na który nie patrzysz (ładowanie danych, przetwarzanie wstępne, kształty tensora)