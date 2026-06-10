---

name: sd-toolkit-composer
description: Skomponuj sieci ControlNet, LoRA i adaptery IP na bazie SD/Flux dla danego zestawu wejść.
version: 1.0.0
phase: 8
lesson: 08
tags: [controlnet, lora, ip-adapter, diffusion]

---

Biorąc pod uwagę zadanie (obraz docelowy), dane wejściowe (podpowiedź, obraz referencyjny, poza / głębokość / bazgroły / seg, tożsamość podmiotu) i model podstawowy (SDXL, SD3.5, Flux.1-dev), wynik:

1. Stos ControlNet. Które ControlNets (super / otwarta poza / głębia / bazgroły / seg / lineart / płytka), przy jakiej wadze i w jakiej kolejności. Maksymalna suma wag <= 1,5.
2. Stos LoRA. Nazwane LoRA, ranga, alfa. Ostrzegaj, gdy alfa &gt; 1.5 lub wiele LoRA ma na celu tę samą koncepcję.
3. Adapter IP. Brak, zwykły lub wariant FaceID; waga 0,4-0,8 typowo.
4. Podpowiedź tekstowa + podpowiedź negatywna. Kolejność słów kluczowych, budżet tokenów, rusztowanie negatywne.
5. Próbnik + CFG + nasiona. Euler A / DPM-Solver++ / LCM; Skala CFG przymocowana do podstawy. Powtarzalny protokół nasion.
6. Lista kontrolna kontroli jakości. Wizualna kontrola pod kątem dryfu ControlNet, nadmiernego nasycenia LoRA, wycieku tożsamości adaptera IP, problemów anatomicznych.

Odmów układania SD 1.5 LoRA na podstawie SDXL (niedopasowanie wymiarów). Odmów uruchomienia 3+ sieci kontrolnych o wadze 1,0 każda (kolizja funkcji). Oznacz dowolne zalecenie SD 1.5, jeśli użytkownik ma budżet GPU na SDXL lub Flux. Oznacz szkolenie dotyczące tożsamości LoRA na stronie &lt; 10 obrazów, które prawdopodobnie przerosną.