---

name: skill-noise-schedule-designer
description: Generowanie liniowych, cosinusowych lub sigmoidalnych harmonogramów beta dla zadanej liczby kroków T oraz docelowego poziomu degradacji sygnału, wraz z obliczeniem wskaźnika SNR
version: 1.0.0
phase: 4
lesson: 10
tags: [computer-vision, diffusion, noise-schedule, training]

---

# Projektowanie harmonogramu szumu (Noise Schedule Designer)

Harmonogram wariancji szumu (beta schedule) kontroluje poziom zachowania sygnału oryginalnego obrazu na każdym etapie dyfuzji. Nieoptymalne dobranie harmonogramu znacząco obniża efektywność uczenia modelu oraz jakość generowanych próbek.

## Zastosowanie

- Rozpoczynanie procesu uczenia nowego modelu dyfuzyjnego (dobór parametrów T oraz wartości progowych beta).
- Diagnozowanie problemów z modelem generującym rozmyte obrazy (zbyt agresywny harmonogram szumowania) lub trudnościami z nauką geometrii i struktury obiektów (zbyt łagodny harmonogram).
- Porównywanie i analiza różnych wariantów harmonogramów opisywanych w publikacjach naukowych.

## Dane wejściowe

- `T`: całkowita liczba kroków czasowych, zazwyczaj w przedziale 100-1000.
- `type`: liniowy (`linear`) | cosinusowy (`cosine`) | sigmoidalny (`sigmoid` / `esowaty`).
- `target_alpha_bar_final`: odsetek oryginalnego sygnału zachowany w ostatnim kroku $t=T$ (domyślnie: 0.001, co oznacza degradację sygnału na poziomie 99.9%).
- Opcjonalny `image_resolution`: rozdzielczość obrazu. Większe obrazy wymagają harmonogramów wolniej degradujących sygnał (np. harmonogramy cosinusowe lub z przesunięciem – offset schedules).

## Wzory matematyczne harmonogramów

### Liniowy (Linear)
```
beta_t = beta_start + (beta_end - beta_start) * (t - 1) / (T - 1)
```
Wartości domyślne (z pracy naukowej wprowadzającej DDPM): `beta_start = 1e-4`, `beta_end = 0.02`.

### Cosinusowy (Cosine – Nichol i Dhariwal, 2021)
```
alpha_bar_t = cos^2((t/T + s) / (1 + s) * pi/2)
beta_t = 1 - alpha_bar_t / alpha_bar_{t-1}
```
gdzie $s = 0.008$. Pozwala na dłuższe zachowanie oryginalnego sygnału; sprawdza się znacznie lepiej przy małej liczbie kroków próbkowania.

### Sigmoidalny (Sigmoid)
```
alpha_bar_t = 1 / (1 + exp(k * (t/T - 0.5)))
```
gdzie $k$ wynosi zazwyczaj od 6 do 12. Stanowi kompromis; stosowany m.in. w niektórych wariantach modelu SDXL.

## Etapy projektowania

1. Oblicz wartości $\beta_t$ na podstawie wybranego wzoru.
2. Wyznacz wartości pomocnicze: $\alpha_t$, skumulowany iloczyn $\bar{\alpha}_t$ (`alphas_cumprod`), a także ich pierwiastki kwadratowe.
3. Oblicz stosunek sygnału do szumu w każdym kroku: $SNR_t = \bar{\alpha}_t / (1 - \bar{\alpha}_t)$ i wygeneruj zestawienie wartości SNR w czasie.
4. Zweryfikuj, czy wartość $\bar{\alpha}_T$ (ostatni element `alphas_cumprod`) różni się o mniej niż 10% od zdefiniowanego `target_alpha_bar_final`. Jeśli odchylenie jest większe, skoryguj parametry (`beta_end` dla harmonogramu liniowego, $s$ dla cosinusowego lub $k$ dla sigmoidalnego) i powtórz obliczenia.
5. Przedstaw parametry dla trzech punktów kontrolnych:
   - $t = 0.25T$ (początkowy etap degradacji)
   - $t = 0.50T$ (połowa procesu)
   - $t = 0.75T$ (końcowy etap)

## Format raportu

```
[schedule]
  type:   <name>
  T:      <int>
  beta_start: <float>   beta_end: <float>

[signal retention]
  t=0.25T:  alpha_bar=<X>  SNR=<X>
  t=0.5T:   alpha_bar=<X>  SNR=<X>
  t=0.75T:  alpha_bar=<X>  SNR=<X>
  t=T:      alpha_bar=<X>  SNR=<X>

[warnings]
  - <if alpha_bar collapses before 0.75T>
  - <if beta_end produces NaN in log-SNR>
```

## Reguły

- Nigdy nie generuj harmonogramu, w którym $\bar{\alpha}_t \le 0$; przytnij wartości poniżej $10^{-5}$ do tej granicy i zgłoś ostrzeżenie.
- Harmonogram cosinusowy jest zalecany jako domyślny przy małej liczbie kroków próbkowania (< 30).
- Harmonogram liniowy stanowi punkt odniesienia (np. dla eksperymentów badawczych i replikacji oryginalnego DDPM).
- Dla rozdzielczości obrazów powyżej 256x256 zaleca się przesunięcie harmonogramu (np. zgodnie z Chen, 2023) w celu dłuższego zachowania informacji o strukturze obrazu.
