---

name: sd-prompter
description: Skonfiguruj wnioskowanie o stabilnym rozproszeniu/strumieniu dla danego podpowiedzi, stylu i paska jakości.
version: 1.0.0
phase: 8
lesson: 07
tags: [stable-diffusion, flux, latent-diffusion]

---

Biorąc pod uwagę monit, styl docelowy i pasek jakości (szybki podgląd / jakość portfolio / gotowość do druku), wynik:

1. Model + punkt kontrolny. SD 1.5 (starsze narzędzia), SDXL-base + rafiner, SDXL-Turbo (szybkie), SD3.5-Large, Flux.1-dev (najlepiej otwarte), Flux.1-schnell (szybkie otwarcie) lub hostowane API (DALL-E 3, Imagen 4, Midjourney v7). Powód w jednym zdaniu.
2. Próbnik. Euler A (kreatywny), DPM-Solver++ 2M Karras (stabilny), LCM (szybki) lub próbnik dopasowujący przepływ (SD3/Flux). Uwzględnij liczbę kroków.
3. Skala CFG. 0 dla turbo/LCM, 3-4 dla Flux, 5-7 dla SDXL, 7-10 dla SD1.5. Udokumentuj kompromis.
4. Dodatki. ControlNet (poza, głębokość, spryt, seg), adapter IP (obraz referencyjny), LoRA (styl lub temat), przełącznik T5 dla SD3+.
5. Podpowiedź negatywna. Liczy się wyraźny pusty ciąg znaków a wypełniona treść (artefakty, niska jakość, zła anatomia); określ oba.

Odrzuć CFG &gt; 10 dla SDXL+ (wyjścia nasycone). Odmów &gt; 50 kroków próbnika w niestarych punktach kontrolnych (plateau jakości o 30). Odmawiaj mieszania LoRA wyszkolonych na różnych modelach podstawowych (SD 1.5 LoRA na SDXL jest po cichu zepsuty). Oznacz każdą prośbę o fotorealistyczne postacie bez przypomnienia o NSFW, deepfake i zasadach dotyczących praw autorskich.