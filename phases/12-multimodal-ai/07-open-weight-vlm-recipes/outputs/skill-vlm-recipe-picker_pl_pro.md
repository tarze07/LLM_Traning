---

name: vlm-recipe-picker
description: Dobierz kompletną konfigurację modelu VLM open-weight (encoder, adapter, LLM, miks danych, harmonogram rozdzielczości) wraz z powołaniem się na odpowiednie badania ablacyjne dla każdego elementu.
version: 1.0.0
phase: 12
lesson: 07
tags: [vlm, mm1, idefics2, molmo, cambrian, prismatic, ablation]

---

Na podstawie zadanego profilu zadań (np. OCR, analizowanie wykresów, agenci interfejsu użytkownika, logiczne rozumowanie, lokalizacja obiektów), budżetu treningowego (rozmiar LLM, zasoby GPU w roboczogodzinach lub docelowe opóźnienie) oraz ograniczeń sprzętowych wdrożenia (urządzenia brzegowe, chmura, smartfony), wygeneruj optymalną konfigurację modelu VLM wraz z uzasadnieniem i odnośnikami do badań ablacyjnych.

Wymagane elementy:

1. Wybór encodera. Domyślnie SigLIP 2 SO400m/14; w przypadku zadań lokalizacji i segmentacji połącz go z DINOv2 ViT-g/14; powołaj się na Tabelę 3 w MM1 oraz wyniki porównania encoderów w Cambrian-1.
2. Wybór adaptera (złącza). Domyślnie 2-warstwowy MLP, chyba że budżet tokenów jest bardzo ograniczony (wtedy wybierz Q-Former z 32 zapytaniami); powołaj się na badania ablacyjne z Prismatic VLMs wykazujące różnice poniżej 1 punktu procentowego w wynikach.
3. Wybór LLM. Dobór pod budżet: Qwen2.5-7B dla budżetów poniżej 10B parametrów; Llama-3.1-70B lub Qwen2.5-72B dla budżetów powyżej 30B parametrów. Wyraźnie zaznacz punkt nasycenia (plateau) wyników w benchmarku MMMU powyżej 70B parametrów.
4. Miks danych treningowych. Domyślnie PixMo + ShareGPT4V + Cauldron; powołaj się na wyniki Molmo wykazujące wyższość szczegółowych opisów ludzkich nad danymi syntetycznymi (zysk o 2-3 punkty w MMMU przy tym samym budżecie tokenów).
5. Harmonogram rozdzielczości. Domyślnie dynamiczna rozdzielczość (256–1280 pikseli) z wyrównaniem w Etapie 1 na stałej rozdzielczości 384; powołaj się na badania rozdzielczości w Idefics2 (wzrost o 3-5 punktów w DocVQA po wdrożeniu AnyRes) oraz dynamiczny mechanizm M-RoPE w Qwen2.5-VL.
6. Etapy uczenia. Etap 1 (trening samego projektora), Etap 2 (pełny trening wszystkich wag), Etap 3 (dostrajanie pod specyficzne zadania).

Bezwzględne odrzucenia:
- Sugerowanie CLIP ViT-L/14 jako domyślnego encodera bez wyraźnego zaznaczenia, że w nowych projektach został on wyparty przez SigLIP 2.
- Prezentowanie Q-Formera jako rozwiązania poprawiającego jakość odpowiedzi w stosunku do MLP. Q-Former służy wyłącznie optymalizacji budżetu tokenów, a nie poprawie jakości.
- Sugerowanie opisów syntetycznych z GPT-4V jako głównego źródła danych treningowych w sytuacji, gdy dostępne są zbiory opisów stworzonych przez ludzi. Powołaj się na Molmo.
- Twierdzenie, że to specyficzna architektura adaptera (złącza) decyduje o jakości generowania, podczas gdy w rzeczywistości wynika ona z samej liczby tokenów wizualnych.

Zasady odmowy wykonania usługi:
- Jeśli użytkownik oczekuje obsługi zadań wymagających zaawansowanego wnioskowania logicznego przy użyciu modeli LLM o rozmiarze 1-3B, odmów i rekomenduj większy model LLM — możliwości wnioskowania wizualnego są ściśle ograniczone przez kompetencje językowe LLM.
- Jeśli użytkownik nie posiada zasobów na pozyskanie szczegółowych opisów stworzonych przez ludzi, wyraźnie wskaż spodziewany spadek jakości o 2-3 punkty w MMMU i zaproponuj użycie destylacji syntetycznej jako rozwiązanie zastępcze (best-effort).
- Jeśli przetwarzane dane obejmują obrazy dokumentów w rozdzielczościach rzędu 4K+ przy wdrożeniu o zamrożonym encoderze, odrzuć AnyRes ze względu na zbyt wysoki koszt tokenów i zarekomenduj encoder z natywną obsługą dynamicznej rozdzielczości przez M-RoPE, taki jak Qwen2.5-VL.

Dane wyjściowe: Jednostronicowa karta konfiguracji z wyborem parametrów dla poszczególnych osi projektowych, odnośnikami do badań ablacyjnych (identyfikatory arXiv), planem etapów uczenia oraz prognozowanymi wynikami w benchmarkach. Na końcu umieść listę trzech kluczowych publikacji: arXiv 2403.09611 (MM1), 2405.02246 (Idefics2), 2409.17146 (Molmo).
