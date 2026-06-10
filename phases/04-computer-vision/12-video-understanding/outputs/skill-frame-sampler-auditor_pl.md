---

name: skill-frame-sampler-auditor
description: Przeprowadź audyt próbnika klatek potoku wideo pod kątem fragmentacji, obsługi krótkich klipów i spójności kadrowania
version: 1.0.0
phase: 4
lesson: 12
tags: [computer-vision, video, sampling, debugging]

---

# Audytor próbnika klatek

Próbkowanie klatek ma miejsce w przypadku przerwania potoków wideo. Błędy rozprzestrzeniają się na wszystkie dalsze wskaźniki.

## Kiedy używać

- Napisanie nowego modułu ładującego dane wideo.
- Odtwarzanie liczb z papieru i dokładność szkolenia są niższe niż podawane.
- Debugowanie modelu wideo, którego dokładność oceny jest niestabilna w różnych seriach.

## Wejścia

- `sampler_code`: Funkcja Pythona, która pobiera (num_frames_total, T) i zwraca indeksy T.
- `T`: docelowa długość klipu.
- Opcjonalne przypadki testowe: wartości `num_frames_total` do ćwiczenia (np. `[3, T-1, T, T+1, 30, 300, 3000]`).

## Kontrole

### 1. Obsługa krótkich klipów
Podaj `num_frames_total < T`. Każdy zwrócony indeks musi być w formacie `[0, num_frames_total - 1]`. Standardową polityką dopełniania jest powtarzanie ostatniej klatki dla pozostałych pozycji.

### 2. Wskaźniki brzegowe
Kanał `num_frames_total == T`. Zwracane indeksy powinny mieć dokładnie wartość `[0, 1, ..., T-1]`.

### 3. Równomierny rozkład
Kanał `num_frames_total == 10 * T`. Zwracane indeksy powinny rosnąć monotonicznie i być mniej więcej równomiernie rozmieszczone.

### 4. Gęste granice okien
W przypadku gęstego pobierania próbek należy podać `num_frames_total == 3 * T`. Zwracane indeksy powinny tworzyć ciągłe okno, nigdy nie przecinające końca klipu.

### 5. Determinizm
Wywołaj próbnik dwa razy z tymi samymi danymi wejściowymi i (w przypadku próbników deterministycznych) tym samym RNG. Indeksy powinny się zgadzać.

### 6. Konsystencja plonu
Jeśli potok zwraca również przycięcie przestrzenne na klatkę, dwukrotnie uruchom próbnik dla tego samego klipu z tym samym materiałem źródłowym i upewnij się, że w każdej klatce używane jest to samo pole przycinania (ten sam `(x, y, w, h)`). Różne kadrowanie na klatkę w jednym klipie niszczy spójność czasową i jest klasycznym cichym błędem. Dopuszczalna odmiana: wzmocnienie stosowane *na klip*, spójne w obrębie klipu.

## Zgłoś

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

## Zasady

- Nigdy nie oznaczaj samplera jako „ok”, jeśli obsługa krótkich klipów powoduje zwrócenie wskaźników poza zakresem.
- Gęste próbniki nigdy nie powinny zwracać okna przecinającego `num_frames_total - 1`.
- Jeśli próbnik jest stochastyczny (gęsty), testuj determinizm tylko za pomocą jawnie zaszczepionego RNG.
- Sugeruj, ale nie ustalaj po cichu, kanonicznych zasad: dopasuj ostatnią klatkę, zaciśnij okno do końca, zaokrąglij półotwarte odstępy.