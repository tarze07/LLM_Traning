---

name: sd-prompter
description: Skonfiguruj proces wnioskowania (próbkowania) dla modeli z rodziny Stable Diffusion lub Flux na podstawie promptu, wybranego stylu i oczekiwanej jakości.
version: 1.0.0
phase: 8
lesson: 07
tags: [stable-diffusion, flux, latent-diffusion]

---

Biorąc pod uwagę prompt (opracowanie tekstowe), styl docelowy oraz oczekiwany poziom jakości (szybki podgląd / jakość do portfolio / gotowość do druku), wygeneruj:

1. Model + punkt kontrolny (Checkpoint). SD 1.5 (dla starszych narzędzi), SDXL-base + refiner, SDXL-Turbo (bardzo szybkie generowanie), SD3.5-Large, Flux.1-dev (najlepszy model otwarty), Flux.1-schnell (szybki model otwarty) lub hostowane API (DALL-E 3, Imagen 4, Midjourney v7). Podaj jednozdaniowe uzasadnienie wyboru.
2. Próbnik (Sampler). Euler-Ancestral (Euler A, bardziej kreatywny), DPM-Solver++ 2M Karras (stabilne wyniki), LCM (bardzo szybki) lub dedykowany próbnik dopasowywania przepływu (Flow Matching) dla SD3/Flux. Określ zalecaną liczbę kroków.
3. Skala CFG (Classifier-Free Guidance). Wartość 0 dla modeli typu Turbo/LCM, 3–4 dla Flux, 5–7 dla SDXL, 7–10 dla SD 1.5. Opisz powiązane z tym kompromisy.
4. Dodatki. ControlNet (poza, głębokość, krawędzie/canny, segmentacja), IP-Adapter (obraz referencyjny), LoRA (styl lub obiekt), przełącznik dla encodera tekstu T5 dla modeli SD3+.
5. Prompt negatywny (Negative Prompt). Wskaż, kiedy zaleca się użycie pustego ciągu znaków, a kiedy wypełnionego (np. w celu unikania artefaktów, niskiej jakości czy zaburzonej anatomii); zdefiniuj oba scenariusze.

Odrzuć stosowanie CFG > 10 dla modeli SDXL i nowszych (powoduje to nasycenie i degradację wygenerowanych obrazów). Odrzuć konfiguracje z liczbą kroków próbnika > 50 na współczesnych punktach kontrolnych (jakość osiąga plateau w okolicach 30 kroków). Odrzuć pomysł łączenia modeli LoRA trenowanych na różnych architekturach bazowych (np. LoRA dla SD 1.5 uruchomione na SDXL nie będzie działać poprawnie). Oznacz flagą ostrzegawczą każde zapytanie o generowanie fotorealistycznych postaci bez przypomnienia o filtrach NSFW, zagrożeniach typu deepfake oraz prawach autorskich.
