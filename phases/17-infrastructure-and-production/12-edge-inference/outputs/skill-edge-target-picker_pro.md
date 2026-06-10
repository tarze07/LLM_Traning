---

name: edge-target-picker
description: Zaproponuj docelową platformę wnioskowania brzegowego (Apple ANE, Qualcomm Hexagon, WebGPU/WebLLM, NVIDIA Jetson) wraz z optymalnym formatem kwantyzacji dla danego urządzenia, modelu i budżetu opóźnień.
version: 1.0.0
phase: 17
lesson: 12
tags: [edge, ane, hexagon, webgpu, webllm, jetson, core-ml, qnn, nvfp4]

---

Na podstawie środowiska wdrożeniowego (iOS, Android, przeglądarka, robotyka/motoryzacja/serwery brzegowe), modelu oraz ograniczeń dotyczących opóźnień i pamięci, przygotuj rekomendację wyboru platformy brzegowej.

Wygeneruj:

1. Platforma docelowa. Wskaż konkretny procesor NPU/GPU (np. Apple ANE, Qualcomm Hexagon, WebGPU, Jetson Orin Nano / AGX / Thor). Uzasadnij wybór specyfiką platformy oraz pokryciem rynku przez wybrane środowisko uruchomieniowe w 2026 roku.
2. Teoretyczny limit wydajności (bandwidth ceiling). Oblicz maksymalną przepustowość fazy dekodowania przy użyciu wzoru: `przepustowość_pamięci_GB_s / rozmiar_modelu_GB`. Porównaj wynik z wymaganiami użytkownika dotyczącymi szybkości generowania tokenów (tokenów/s). Jeśli limit jest zbyt niski, odrzuć konfigurację lub zaproponuj mniejszy model/agresywniejszą kwantyzację.
3. Format kwantyzacji. Dobierz optymalny format: GGUF Q4 (dla CPU / przeglądarek / urządzeń brzegowych), Core ML INT4 + FP16 (dla Apple ANE), QNN INT8/INT4 (dla Qualcomm Hexagon) lub NVFP4 + FP8 KV (dla Jetson Thor / Edge-LLM).
4. Potok konwersji (conversion pipeline). Określ właściwe narzędzie konwertujące (np. Core ML Converter, Qualcomm AI Hub, pakiet MLC-LLM dla WebLLM, kompilator TensorRT-LLM Edge).
5. Budżet kontekstu. Określ maksymalną długość kontekstu, która pozwoli na zmieszczenie modelu wraz z pamięcią podręczną w pamięci RAM urządzenia. W przypadku wymagań dotyczących długiego kontekstu, zalecaj kwantyzację KV (np. Q4 KV) lub odrzuć projekt.
6. Mechanizm rezerwowy (Fallback). Zdefiniuj procedurę awaryjną na wypadek, gdyby urządzenie było zbyt słabe lub interfejs WebGPU był niedostępny (np. w przeglądarce Firefox na Androidzie lub w starszych wersjach oprogramowania). Określ serwerowe API rezerwowe, udostępniające ten sam interfejs zgodny ze standardem OpenAI.

Kategoryczne odrzucenia:
- Deklarowanie szybkości generowania tokenów przekraczającej teoretyczny limit wynikający z przepustowości pamięci (fizyczne ograniczenia sprzętowe).
- Próby odwoływania się do Apple ANE za pośrednictwem środowisk uruchomieniowych innych niż Core ML w 2026 roku. Core ML jest jedynym frameworkiem udostępniającym natywny dostęp do ANE.
- Zakładanie, że standard WebGPU jest dostępny w każdej przeglądarce mobilnej. Zasięg rynkowy tej technologii w 2026 r. wynosi ok. 70-75% urządzeń mobilnych – zawsze definiuj mechanizm rezerwowy.

Zasady odmowy wdrożenia (odrzucenie rekomendacji):
- Jeśli rozmiar modelu przekracza 6 GB, a urządzeniem docelowym jest smartfon o pojemności 4-8 GB RAM, odrzuć wdrożenie. Zaproponuj mniejszy model lub agresywniejszą kwantyzację.
- Jeśli projekt zakłada obsługę kontekstu o długości 128k tokenów dla modelu klasy 7B na urządzeniu iPhone, odrzuć projekt – pamięć RAM urządzenia nie pomieści struktur danych bez użycia formatu Q4 KV oraz mechanizmu przesuwnego okna uwagi (sliding window attention).
- Jeśli wdrożenie zakłada obsługę długiego kontekstu na systemie Android za pomocą WebGPU, a jednym z wymagań jest wsparcie dla przeglądarki Firefox, odrzuć projekt i zażądaj stosowania przeglądarki Chrome lub wdrożenia serwera rezerwowego.

Wynik: jednostronicowy plan wdrożenia zawierający: nazwę wybranej platformy docelowej, wyliczenie limitu przepustowości, format kwantyzacji, wskazanie konwertera, budżet kontekstu oraz definicję mechanizmu rezerwowego. Na końcu podaj kluczowy wskaźnik: zmierzona prędkość generowania tokenów (tokenów/s) na najsłabszym urządzeniu z docelowej floty.
