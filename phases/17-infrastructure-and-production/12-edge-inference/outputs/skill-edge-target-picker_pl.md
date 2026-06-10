---

name: edge-target-picker
description: Wybierz cel wnioskowania brzegowego (Apple ANE, Qualcomm Hexagon, WebGPU/WebLLM, NVIDIA Jetson) i pasujący format kwantyzacji do danego urządzenia, modelu i budżetu opóźnień.
version: 1.0.0
phase: 17
lesson: 12
tags: [edge, ane, hexagon, webgpu, webllm, jetson, core-ml, qnn, nvfp4]

---

Biorąc pod uwagę platformę wdrożeniową (iOS, Android, przeglądarka, robotyka/motoryzacja/serwer brzegowy), model i budżet opóźnienia/pamięci, utwórz rekomendację celu brzegowego.

Wyprodukuj:

1. Cel. Nazwij konkretny NPU/GPU (ANE, Hexagon, WebGPU, Jetson Orin Nano / AGX / Thor). Uzasadnij platformą i pokryciem środowiska wykonawczego na rok 2026.
2. Pułap przepustowości. Oblicz teoretyczny pułap dekodowania: szerokość pasma_GB_s / model_size_GB. Porównaj z wymaganiami tok/s użytkownika. Jeśli pułap jest niższy od wymagań, odmów lub zaproponuj mniejszy model / ściślejszą kwantyzację.
3. Format kwantyzacji. Wybierz Q4 GGUF (procesor przeglądarki/edge), Core ML INT4 + FP16 (ANE), QNN INT8/INT4 (Hexagon) lub NVFP4 + FP8 KV (Jetson Thor / Edge-LLM).
4. Rurociąg konwersji. Nazwij dokładny konwerter (konwerter Core ML, Qualcomm AI Hub, MLC-LLM dla WebLLM, kompilator TensorRT-LLM Edge).
5. Budżet kontekstowy. Podaj maksymalny kontekst, który pasuje do wag w pamięci RAM urządzenia. W przypadku zastosowań o długim kontekście należy określić kwantyzację KV (Q4 KV) lub odmówić.
6. Powrót. Jeśli urządzenie nie działa lub WebGPU jest niedostępne (Firefox Android, starsze przeglądarki), określ zastępcze API po stronie serwera z tym samym interfejsem zgodnym z OpenAI.

Twarde odrzucenia:
- Obiecujący tok/s powyżej pułapu przepustowości. Odmówić — fizyka.
— Ukierunkowanie na ANE bezpośrednio za pośrednictwem środowiska wykonawczego ML innego niż Core w 2026 r. Tylko Core ML udostępnia natywnie ANE.
- Zakładając, że WebGPU jest w każdej przeglądarce. Zasięg w 2026 r. to ~70–75% urządzeń mobilnych; zawsze określaj rezerwę.

Zasady odmowy:
- Jeśli model ma > 6 GB, a celem jest telefon (4-8 GB RAM), odmów - najpierw zaproponuj mniejszy model lub agresywną kwantyzację.
- Jeśli żądanie dotyczy kontekstu 128 KB w modelu 7B na iPhonie, odmów — pamięć RAM urządzenia nie zmieści się bez Q4 KV plus uwaga dotycząca przesuwanego okna.
- Jeśli wdrożenie wymaga przesyłania strumieniowego w długim kontekście na Androidzie za pośrednictwem WebGPU, a użytkownik potrzebuje obsługi przeglądarki Firefox, odmów i wymagaj przeglądarki Chrome lub serwera rezerwowego.

Wynik: jednostronicowy plan nazewnictwa celu, pułapu, kwantyzacji, konwertera, budżetu kontekstowego i rezerwy. Zakończ pojedynczym wskaźnikiem: zaobserwowanym tok/s na najgorszym urządzeniu we flocie docelowej.