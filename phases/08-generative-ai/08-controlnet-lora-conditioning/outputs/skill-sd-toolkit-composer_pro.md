---

name: sd-toolkit-composer
description: Skomponuj potok składający się z sieci ControlNet, adapterów IP-Adapter oraz modeli LoRA bazujących na architekturze SD lub Flux dla zadanych danych wejściowych.
version: 1.0.0
phase: 8
lesson: 08
tags: [controlnet, lora, ip-adapter, diffusion]

---

Biorąc pod uwagę zadanie (docelowy obraz), dane wejściowe (prompt tekstowy, obraz referencyjny, pozy / głębokość / szkic (scribble) / segmentację, tożsamość postaci) oraz model bazowy (SDXL, SD3.5, Flux.1-dev), wygeneruj:

1. Konfiguracja ControlNet. Wskaż, które modele ControlNet (np. OpenPose, depth, scribble, segmentation, lineart, tile) należy zastosować, z jakimi wagami oraz w jakiej kolejności. Maksymalna suma wag powinna wynosić <= 1.5.
2. Konfiguracja LoRA. Nazwy modeli LoRA, parametry rank oraz alpha. Ostrzegaj, gdy wartość alpha wynosi > 1.5 lub gdy wiele modeli LoRA odnosi się do tego samego pojęcia/koncepcji.
3. IP-Adapter. Brak, standardowy lub wariant FaceID; zalecany zakres wag to zazwyczaj 0.4–0.8.
4. Prompt tekstowy + prompt negatywny. Kolejność słów kluczowych, limit tokenów, struktura promptu negatywnego.
5. Próbnik (Sampler) + CFG + Seed. Euler A / DPM-Solver++ / LCM; skala CFG dobrana do modelu bazowego. Powtarzalny protokół generowania ziarna (seed).
6. Lista kontrolna jakości (QA). Wizualna weryfikacja pod kątem deformacji spowodowanych przez ControlNet, nadmiernego nasycenia przez LoRA (over-saturation), wycieku tożsamości z IP-Adaptera lub problemów z anatomią.

Odrzuć próby łączenia modeli LoRA z SD 1.5 z bazą SDXL (niezgodność wymiarów). Odrzuć konfiguracje uruchamiające 3 lub więcej sieci ControlNet z wagami 1.0 każda (powoduje to kolizje cech). Oznacz flagą ostrzegawczą rekomendowanie SD 1.5, jeśli użytkownik posiada budżet GPU pozwalający na uruchomienie SDXL lub Flux. Oznacz ostrzeżeniem trenowanie LoRA do odwzorowania tożsamości na zbiorze liczącym mniej niż 10 obrazów ze względu na wysokie ryzyko przeuczenia (overfitting).
