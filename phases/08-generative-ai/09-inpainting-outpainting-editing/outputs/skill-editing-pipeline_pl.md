---

name: editing-pipeline
description: Zaplanuj proces edycji obrazu od źródła + opis edycji do gotowego do wysyłki wyjścia.
version: 1.0.0
phase: 8
lesson: 09
tags: [inpaint, outpaint, edit, sam]

---

Biorąc pod uwagę obraz źródłowy, edycję docelową (usuń X, zamień Y na Z, rozszerz płótno, zmień styl regionu, zmień porę roku/porę dnia) i pasek jakości (wersja robocza/portfolio/druk), wynik:

1. Strategia maski. Wyraźna maska ​​pędzla, monit o kliknięcie/pole SAM 2, Grounded-SAM na frazie tekstowej lub RMBG (do usuwania tła). Powód w jednym zdaniu.
2. Model podstawowy + tryb. SD-Inpaint / SDXL-Inpaint / Flux-Fill / Flux-Kontext do edycji instrukcji lub poziom szumu SDEdit (0,3 / 0,6 / 0,9) w przypadku braku maski.
3. Szybkie montaż rusztowania. Opisz cały obraz po edycji, a nie tylko nową zawartość. Dołącz negatywną zachętę.
4. CFG + siła + pióro. Maska piórkowa 8-16 px; CFG ~5-7 dla SDXL-inpaint, 3-4 dla Flux. Siła 0,8-1,0 dla pełnej regeneracji, 0,3-0,5 dla konserwacji.
5. Poręcze. Hak do wykrywania NSFW / deepfake / znaku towarowego, bramka polityczna typu face-swap, odwracalność (zapisz maskę + materiał siewny).

Odmawiaj przesyłania zmian w tożsamości rozpoznawalnej osoby publicznej bez wyraźnego sprawdzenia zasad. Odmawiaj przemalowania obrazu bez co najmniej 30% oryginalnego płótna jako kotwicy (zbyt mały kontekst powoduje halucynacje modela). Oznacz dowolne uruchomienie SDEdit za pomocą t/T &gt; 0.7 i cel wierności „zachowaj temat” jako prawdopodobną niezgodność.