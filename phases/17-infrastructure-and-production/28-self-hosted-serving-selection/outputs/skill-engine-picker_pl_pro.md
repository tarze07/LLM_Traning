---

name: engine-picker
description: Dobierz silnik wnioskowania LLM do wdrożenia na własnej infrastrukturze (llama.cpp, Ollama, TGI, vLLM, SGLang) na podstawie sprzętu, skali oraz typu obciążenia. Wskazuj status konserwacji TGI jako powód migracji.
version: 1.0.0
phase: 17
lesson: 28
tags: [self-hosted, vllm, sglang, llama-cpp, ollama, tgi, trt-llm, engine-selection]

---

Na podstawie specyfikacji sprzętowej (CPU / Apple Silicon / AMD / NVIDIA Hopper / NVIDIA Blackwell), skali (pojedynczy użytkownik / mały zespół / produkcja / enterprise) oraz charakterystyki obciążenia (czat ogólny / scenariusze agentowe / RAG / długi kontekst / kod), przygotuj rekomendację silnika wnioskowania.

Wygeneruj:

1. Wybrany silnik: Wskaż konkretny silnik wnioskowania. Przedstaw schemat decyzyjny (drzewo wyboru): najpierw weryfikacja sprzętu, następnie skala wdrożenia, a na końcu typ obciążenia.
2. Odrzucenie alternatyw: Wyjaśnij, dlaczego pozostałe silniki nie zostały wybrane w tym scenariuszu (np. status konserwacji TGI, brak wsparcia TRT-LLM na układach AMD, przeznaczenie Ollamy wyłącznie do prac deweloperskich lokalnie).
3. Ścieżka wdrożeniowa: Zdefiniuj przepływ między środowiskami (lokalne dev: Ollama -> staging: llama.cpp -> produkcja: vLLM/SGLang) z zachowaniem spójnego formatu wag modeli (GGUF lub HF).
4. Architektura produkcyjna: Dla wdrożeń produkcyjnych opisz architekturę stosu (Faza 17 · Lekcja 18), opcjonalną dezagregację (Faza 17 · Lekcja 17) oraz dynamiczny router wykorzystujący cache (Faza 17 · Lekcja 11).
5. Migracja z TGI: Jeśli obecnie używanym silnikiem jest TGI, określ plan i harmonogram migracji (proces ten nie jest krytyczny natychmiastowo, ale powinien rozpocząć się w ciągu najbliższych 6 miesięcy).
6. Ograniczenia sprzętowe: Wskaż dwa bezwzględne warunki (środowisko tylko z CPU wymaga llama.cpp; platforma AMD wyklucza użycie TensorRT-LLM).

Kryteria odrzucenia planu (Hard rejects):
- Wybór TGI dla nowych projektów: Odrzuć – silnik jest w stanie konserwacji (maintenance mode).
- Stosowanie Ollamy w wielodostępnym środowisku produkcyjnym (> 1 użytkownik): Odrzuć – zbyt duży spadek przepustowości pod obciążeniem.
- Rekomendowanie TensorRT-LLM bez weryfikacji sprzętu NVIDIA: Odrzuć – na architekturach AMD i innych niż NVIDIA silnik ten nie zadziała.

Zasady odrzucenia:
- Jeśli środowisko sprzętowe jest mieszane (np. część AMD, część NVIDIA), dobierz dedykowane silniki dla poszczególnych klastrów – nie narzucaj jednego rozwiązania na cały system.
- Jeśli profil obciążenia produkcyjnego jest nieznany lub ogólny, wdroż domyślnie vLLM i zaplanuj ponowną ocenę po 3 miesiącach zbierania danych o ruchu.
- Jeśli zespół wymaga maksymalnej wydajności na układach Hopper (przy braku dostępności procesorów Blackwell), dopuszczalny jest wybór zarówno TensorRT-LLM, jak i vLLM.

Wynik: Jednostronicowa rekomendacja zawierająca wybrany silnik, uzasadnienie odrzucenia alternatyw, ścieżkę wdrożeniową, architekturę produkcyjną oraz plan migracji z TGI. Na końcu umieść zalecenie kwartalnego przeglądu: dokonaj ponownej ewaluacji wyboru silnika, jeśli charakterystyka obciążenia ulegnie istotnej zmianie.
