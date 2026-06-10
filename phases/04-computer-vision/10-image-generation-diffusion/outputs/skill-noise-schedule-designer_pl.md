---

name: skill-noise-schedule-designer
description: Stwórz liniowy, cosinusowy lub sigmoidalny harmonogram beta, biorąc pod uwagę T i docelowy poziom korupcji, a także wykres SNR
version: 1.0.0
phase: 4
lesson: 10
tags: [computer-vision, diffusion, noise-schedule, training]

---

# Projektant harmonogramu hałasu

Harmonogram beta kontroluje ilość sygnału zatrzymywanego na każdym etapie dyfuzji. Złe harmonogramy ograniczają efektywność szkolenia i jakość próbek przy każdej późniejszej decyzji.

## Kiedy używać

- Rozpoczęcie nowego treningu dyfuzyjnego i wybranie T i beta.
- Debugowanie modelu dyfuzji, który generuje rozmyte próbki (harmonogram zbyt agresywny) lub nie uczy się struktury (harmonogram zbyt łagodny).
- Porównywanie projektów w dokumentach przedstawiających różne harmonogramy.

## Wejścia

- `T`: liczba kroków czasowych, zazwyczaj 100-1000.
- `type`: liniowy | cosinus | esowaty.
- `target_alpha_bar_final`: część sygnału utrzymywana przy t=T, domyślnie 0,001 (uszkodzenie w 99,9%).
- Opcjonalny `image_resolution` — większe obrazy korzystają z harmonogramów, które wolniej uszkadzają (harmonogramy cosinusowe lub przesunięte).

## Zaplanuj formuły

### Liniowy
```
beta_t = beta_start + (beta_end - beta_start) * (t - 1) / (T - 1)
```
Wartości domyślne: beta_start=1e-4, beta_end=0.02 (papier DDPM).

### Cosinus (Nichol i Dhariwal, 2021)
```
alpha_bar_t = cos^2((t/T + s) / (1 + s) * pi/2)
beta_t = 1 - alpha_bar_t / alpha_bar_{t-1}
```
s = 0,008. Utrzymuje sygnał dłużej; lepiej przy małej liczbie kroków.

### Sigmoida
```
alpha_bar_t = 1 / (1 + exp(k * (t/T - 0.5)))
```
k = 6 do 12. Dobry środek; używany przez niektóre warianty SDXL.

## Kroki

1. Oblicz beta według formuły.
2. Oblicz wstępnie `alphas`, `alphas_cumprod`, `sqrt_alphas_cumprod`, `sqrt_one_minus_alphas_cumprod`.
3. Oblicz SNR_t = alfa_bar_t / (1 - alfa_bar_t); wygenerować podsumowanie SNR w czasie.
4. Sprawdź, czy wartość `alphas_cumprod[T-1]` mieści się w granicach 10% wartości `target_alpha_bar_final`; w przeciwnym razie dostrój beta_end (liniowy), s (cosinus) lub k (esigmoidalny) i spróbuj ponownie.
5. Zgłoś trzy punkty kontrolne:
   - `t=T*0.25` — wczesna korupcja
   - `t=T*0.5` — w połowie
   - `t=T*0.75` — prawie finał

## Zgłoś

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

## Zasady

- Nigdy nie emituj harmonogramu z jakimkolwiek `alpha_bar_t <= 0`; zacisnąć wartości poniżej 1e-5 i ostrzec.
- Cosinus jest domyślnym zaleceniem dla próbkowania z małą liczbą kroków (< 30 kroków).
- Liniowy jest ustawieniem domyślnym dla `quality_target == research` — wartości bazowe DDPM są raportowane w oparciu o harmonogramy liniowe.
– W przypadku `image_resolution > 256` zaleca się zmianę harmonogramu (Chen, 2023), aby zachować więcej sygnału w wysokich rozdzielczościach.