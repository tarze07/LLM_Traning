---

name: editing-pipeline
description: Zaplanuj potok edycji obrazu na podstawie grafiki źródłowej oraz opisu modyfikacji aż do wygenerowania gotowego pliku wynikowego.
version: 1.0.0
phase: 8
lesson: 09
tags: [inpaint, outpaint, edit, sam]

---

Biorąc pod uwagę obraz źródłowy, cel edycji (usuń obiekt X, zamień Y na Z, rozszerz kadr (outpainting), zmień styl wybranego obszaru, zmień porę roku/dnia) oraz docelowy poziom jakości (szybki podgląd / jakość do portfolio / gotowość do druku), wygeneruj:

1. Strategia maskowania. Ręczna maska (pędzel), wskazanie punktów/ramek za pomocą SAM 2 (Segment Anything), Grounded-SAM na bazie zapytania tekstowego lub RMBG (do usuwania tła). Podaj jednozdaniowe uzasadnienie.
2. Model bazowy + Tryb pracy. SD-Inpaint / SDXL-Inpaint / Flux-Fill / Flux-Kontext do edycji instruktażowej lub poziom zaszumienia SDEdit (0.3 / 0.6 / 0.9) w przypadku edycji bez użycia maski.
3. Struktura promptu. Opisz cały obraz po edycji, a nie tylko nowy element. Dołącz prompt negatywny.
4. CFG + Waga modyfikacji + Wtwarzanie krawędzi (Feathering). Zmiękczanie krawędzi maski (feathering) na poziomie 8–16 px; CFG ~5–7 dla SDXL-inpaint, 3–4 dla Flux. Waga modyfikacji (denoising strength) na poziomie 0.8–1.0 dla całkowitej regeneracji obszaru lub 0.3–0.5 dla zachowania oryginalnej struktury.
5. Filtry bezpieczeństwa (Guardrails). Detekcja NSFW, prób głębokiej manipulacji wizerunkiem (deepfake), naruszeń znaków towarowych, weryfikacja polityki face-swap oraz odtwarzalność procesu (zapisanie maski i ziarna seed).

Odrzuć realizację edycji modyfikujących wizerunek powszechnie znanych osób publicznych bez wyraźnej weryfikacji zgodności z polityką bezpieczeństwa. Odrzuć próby przerysowania obrazu (inpainting), jeśli zachowano mniej niż 30% oryginalnego kadru jako punktu odniesienia (zbyt mały kontekst prowadzi do halucynacji modelu). Oznacz flagą ostrzegawczą każde użycie metody SDEdit z parametrem t/T > 0.7 przy jednoczesnym celu zachowania wierności oryginalnemu obiektowi (te założenia są sprzeczne).
