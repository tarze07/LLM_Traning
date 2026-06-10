---

name: skill-frame-sampler-auditor
description: Narzędzie do audytu próbników klatek w potokach wideo pod kątem obsługi krótkich klipów, poprawności indeksowania i spójności kadrowania (cropping)
version: 1.0.0
phase: 4
lesson: 12
tags: [computer-vision, video, sampling, debugging]

---

# Audyt próbników klatek wideo (Frame Sampler Auditor)

Próbkowanie klatek jest newralgicznym punktem w potokach przetwarzania wideo. Błędy na tym etapie propagują się na wszystkie kolejne metryki i jakość uczenia.

## Zastosowanie

- Tworzenie nowego modułu ładującego dane wideo (DataLoader).
- Replikacja wyników z prac naukowych, gdy uzyskiwana dokładność uczenia jest niższa od deklarowanej.
- Diagnozowanie niestabilności wyników ewaluacji modelu w kolejnych uruchomieniach (runs).

## Dane wejściowe

- `sampler_code`: kod funkcji w języku Python przyjmujący parametry `(num_frames_total, T)` i zwracający listę `T` indeksów klatek.
- `T`: docelowa długość klipu (liczba klatek).
- Opcjonalne przypadki testowe: wybrane wartości `num_frames_total` do przetestowania (np. `[3, T-1, T, T+1, 30, 300, 3000]`).

## Zakres weryfikacji

### 1. Obsługa zbyt krótkich nagrań (Short-clip handling)
Test dla warunku `num_frames_total < T`. Wszystkie zwrócone indeksy muszą należeć do przedziału `[0, num_frames_total - 1]`. Standardową metodą dopełniania (padding) jest wielokrotne powielenie ostatniej dostępnej klatki w celu wypełnienia pozostałych miejsc.

### 2. Warunki brzegowe (Boundary check)
Test dla warunku `num_frames_total == T`. Zwrócona lista indeksów powinna mieć dokładnie postać `[0, 1, ..., T-1]`.

### 3. Równomierność próbkowania (Uniform spacing)
Test dla warunku `num_frames_total == 10 * T`. Zwrócone indeksy powinny rosnąć monotonicznie i być rozmieszczone w zbliżonych odstępach czasowych.

### 4. Ciągłość próbkowania gęstego (Dense window check)
Test dla próbkowania gęstego przy warunku `num_frames_total == 3 * T`. Zwrócone indeksy muszą tworzyć ciągły blok (np. `[5, 6, 7]`), a zakres nie może wykraczać poza koniec nagrania.

### 5. Determinizm
Kilkukrotne wywołanie próbnika z identycznymi parametrami wejściowymi (oraz tym samym ziarnem generatora liczb losowych – seedem) musi zwrócić dokładnie takie same sekwencje indeksów.

### 6. Spójność kadrowania przestrzennego (Crop consistency)
Jeżeli potok wykonuje operacje kadrowania przestrzennego (cropping), należy zweryfikować, czy dla wszystkich klatek w obrębie jednego wyciętego klipu stosowany jest dokładnie ten sam obszar kadrowania (te same współrzędne `(x, y, w, h)`). Zmienność kadrowania w obrębie jednego klipu zaburza spójność czasową i jest klasycznym ukrytym błędem (silent bug). Uzasadniona praktyka: augmentacja danych (np. RandomCrop) jest stosowana spójnie *dla całego klipu*, a nie indywidualnie dla każdej klatki.

## Format raportu

```
[sampler audit]
  name: <function name>
  T:    <int>

[short-clip handling]
  passed | failed (<details>)

[boundary]
  passed | failed

[uniform spacing]
  passed | failed (<stddev of gaps>)

[dense window]
  passed | failed (<details>)

[determinism]
  passed | failed

[crop consistency]
  passed | failed (<per-frame crop varies: yes/no>)

[verdict]
  ok | fix required
```

## Reguły

- Nigdy nie zatwierdzaj próbnika jako poprawnego (`ok`), jeśli obsługa krótkich nagrań powoduje generowanie indeksów spoza dopuszczalnego zakresu.
- Próbniki gęste (dense) nie mogą generować okien, których górna granica wykracza poza indeks `num_frames_total - 1`.
- W przypadku próbników losowych (stochastycznych), determinizm działania należy testować wyłącznie przy użyciu jawnie określonego generatora losowości (seed/RNG).
- Sugeruj (ale nie wprowadzaj bez wiedzy użytkownika) sprawdzone reguły: powielanie ostatniej klatki w paddingu, przycinanie okna próbkowania do końca klipu lub zaokrąglanie przedziałów.
