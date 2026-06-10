---

name: skill-debug-checklist
description: Lista kontrolna drzewa decyzyjnego do debugowania błędów uczenia sieci neuronowej
version: 1.0.0
phase: 3
lesson: 13
tags: [debugging, neural-networks, training, diagnostics, deep-learning]

---

# Lista kontrolna debugowania sieci neuronowej

Systematyczny protokół postępowania w przypadku problemów z uczeniem sieci. Realizuj poniższe kroki w podanej kolejności – większość typowych błędów udaje się wykryć w pierwszych 3 krokach.

## Przed rozpoczęciem treningu (zapobieganie błędom)

1. Wyświetl podsumowanie architektury modelu oraz liczbę parametrów. Czy pojemność sieci odpowiada złożoności Twoich danych?
2. Wykonaj pojedyncze przejście w przód (forward pass) z losowymi danymi wejściowymi. Czy kształt tensora wyjściowego jest zgodny ze specyfikacją celu (target)?
3. Upewnij się, że etykiety mają prawidłowy typ danych (dtype) – np. `CrossEntropyLoss` w PyTorch wymaga typu `Long`, natomiast `BCELoss` wymaga `Float`.
4. Sprawdź poprawność normalizacji danych wejściowych: wartości powinny mieć średnią bliską 0 i odchylenie standardowe bliskie 1.
5. Wyświetl w terminalu 5 losowych par (wejście, etykieta). Czy dane i przypisane do nich etykiety są poprawne?
6. Upewnij się, że zbiory treningowy oraz testowy nie zawierają identycznych przykładów (wyklucz zduplikowane próbki).

## Test przeuczenia na pojedynczej partii (Overfit One Batch)

1. Pobierz małą próbkę danych (od 8 do 32 przykładów) ze zbioru treningowego.
2. Trenuj na niej model przez około 200 kroków z domyślnym, bezpiecznym współczynnikiem uczenia się (LR).
3. Strata powinna spaść blisko zera, a dokładność treningowa (accuracy) osiągnąć 100%.
4. **Jeśli test zakończy się niepowodzeniem**: problem tkwi bezpośrednio w kodzie modelu, definicji funkcji straty lub w pętli treningowej (a nie w samych danych czy złych hiperparametrach).
5. **Jeśli test zakończy się sukcesem**: przejdź do pełnego procesu uczenia.

## Strata (loss) nie maleje

1. Dostosuj współczynnik uczenia się (LR). Przetestuj 3 warianty: $\text{bieżący LR} / 10$, $\text{bieżący LR}$ oraz $\text{bieżący LR} \times 10$.
2. Monitoruj normy gradientów dla każdej warstwy. Zerowe wartości oznaczają martwą sieć lub przerwany graf obliczeniowy autogradu.
3. Zweryfikuj parametry pod kątem flagi `requires_grad=True`. Upewnij się, że w pętli wywoływana jest metoda `loss.backward()`.
4. Upewnij się, że wywołanie `optimizer.zero_grad()` następuje przed instrukcją `loss.backward()`.
5. Upewnij się, że aktualizacja wag `optimizer.step()` jest wywoływana po kroku wstecznym `loss.backward()`.
6. Sprawdź, czy parametry modelu zostały poprawnie przekazane do optymalizatora: np. `optimizer = Adam(model.parameters())`.

## Strata przyjmuje wartości NaN lub Inf

1. Zmniejsz współczynnik uczenia się (LR) 10-krotnie.
2. Zapobiegaj błędom w operacjach logarytmowania przez dodanie małej stałej ($\epsilon$): np. `torch.log(x + 1e-7)`.
3. Dodaj $\epsilon$ do mianownika w operacjach dzielenia: np. `x / (y + 1e-8)`.
4. Ogranicz (clamp) wartości prawdopodobieństw wyjściowych przed obliczeniem straty BCELoss: `torch.clamp(pred, 1e-7, 1 - 1e-7)`.
5. Użyj narzędzia `torch.autograd.detect_anomaly()`, aby zlokalizować operację powodującą błąd numeryczny.
6. Dodaj asercję sprawdzającą obecność wartości NaN w danych wejściowych: `assert not torch.isnan(x).any()`.

## Strata gwałtownie oscyluje

1. Zmniejsz współczynnik uczenia się 3-10-krotnie.
2. Zwiększ rozmiar partii (batch size) w celu wygładzenia gradientów.
3. Zastosuj przycinanie gradientów (gradient clipping): `torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)`.
4. Zmień optymalizator z SGD na Adam (który dostosowuje LR dla każdego parametru).
5. Wprowadź fazę rozgrzewki (warmup) dla LR obejmującą pierwsze 5-10% całego procesu treningowego.

## Przeuczenie (wysoka skuteczność na treningu, słaba na teście)

1. Zastosuj warstwy Dropout (zacznij od prawdopodobieństwa $p=0,1$, zwiększając je w razie potrzeby do $0,5$).
2. Włącz regularyzację L2 (weight decay) w optymalizatorze: `Adam(params, weight_decay=1e-4)`.
3. Zmniejsz pojemność modelu (zredukuj liczbę warstw lub zmniejsz liczbę neuronów w warstwach ukrytych).
4. Zastosuj techniki augmentacji danych (data augmentation).
5. Wdróż wczesne zatrzymanie (early stopping) – przerwij uczenie, gdy strata na zbiorze walidacyjnym rośnie przez ponad 5 epok.
6. Zweryfikuj, czy nie występuje wyciek danych (data leakage) między zbiorem treningowym a testowym.

## Niedopasowanie (słabe wyniki zarówno na treningu, jak i teście)

1. Zwiększ pojemność modelu (dodaj warstwy lub zwiększ szerokość warstw ukrytych).
2. Wydłuż proces uczenia (zwiększ liczbę epok).
3. Ostrożnie zwiększ współczynnik uczenia się (LR).
4. Wyłącz tymczasowo wszelkie techniki regularyzacyjne (Dropout, weight decay), aby upewnić się, że model jest w stanie dopasować się do danych.
5. Upewnij się, czy wybrana architektura modelu jest odpowiednio wyrazista (expressive power) dla danego problemu.

## Martwe neurony ReLU

1. Monitoruj odsetek zerowych aktywacji na poziomie każdej warstwy. Wartości powyżej 50% sygnalizują problem.
2. Zmień funkcję aktywacji na `LeakyReLU(0.01)` lub `GELU`.
3. Zastosuj poprawną inicjalizację wag He (Kaiming).
4. Obniż współczynnik uczenia się (zbyt duże aktualizacje wag mogą zepchnąć parametry neuronów w strefę ujemną ReLU).
5. Dodaj warstwy BatchNorm przed funkcjami aktywacji.

## Ściągawka: Początkowe wartości współczynnika uczenia się (LR)

| Optymalizator | Scenariusz / Architektura | Rekomendowany początkowy LR |
| :--- | :--- | :--- |
| **Adam** | Uczenie od zera | 1e-3 |
| **Adam** | Dostrajanie (fine-tuning) | 1e-5 |
| **SGD + momentum** | Uczenie od zera | 1e-1 |
| **SGD + momentum** | Dostrajanie (fine-tuning) | 1e-3 |
| **AdamW** | Uczenie Transformerów | 3e-4 |

## Ściągawka: Wpływ rozmiaru partii (Batch Size)

| Rozmiar partii | Szum gradientu | Zużycie pamięci | Zdolność generalizacji |
| :--- | :--- | :--- | :--- |
| **8 - 16** | Wysoki (szum stochastyczny) | Niskie | Często lepsza |
| **32 - 64** | Umiarkowany | Umiarkowane | Bezpieczna opcja domyślna |
| **128 - 256** | Niski (gładki gradient) | Wysokie | Może wymagać rozgrzewki (warmup) |
| **512+** | Bardzo niski | Bardzo wysokie | Wymaga dostosowania i skalowania LR |

## Kiedy nic nie działa (metoda ostateczna)

1. Uprość architekturę modelu do jednej warstwy ukrytej. Sprawdź, czy strata zacznie spadać.
2. Zredukuj zbiór danych do zaledwie 100 próbek. Czy model potrafi go przeuczyć (overfit)?
3. Zmień funkcję straty na prostą stratę średniokwadratową (MSELoss). Czy strata maleje?
4. Zastąp optymalizator klasycznym algorytmem SGD(lr=0.01). Czy model wykazuje postępy w nauce?
5. Zastąp dane rzeczywiste prostymi danymi syntetycznymi (np. regułą decyzyjną $y = x[0] > 0$). Czy model uczy się tej zależności?
6. Jeśli nawet powyższe kroki nie pomogą: błąd leży w kodzie, którego nie brałeś pod uwagę (np. w logice ładowania danych, preprocessingu lub w cichym rozgłaszaniu kształtów tensorów).
