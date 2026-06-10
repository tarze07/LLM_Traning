---

name: trtllm-blackwell-advisor
description: Zdecyduj, czy Blackwell + TensorRT-LLM + Dynamo jest warte blokady NVIDIA przy danym obciążeniu i budżecie.
version: 1.0.0
phase: 17
lesson: 07
tags: [tensorrt-llm, blackwell, b200, gb200, nvfp4, fp8, dynamo]

---

Biorąc pod uwagę obciążenie pracą (rozmiar modelu, aktywne parametry, roczny wolumen tokenów, wrażliwość na jakość — intensywne rozumowanie lub rutyna), obecną infrastrukturę (procesory graficzne H100/H200/B200, silnik obsługujący) i budżet, utwórz poradę dotyczącą migracji Blackwell + TRT-LLM.

Wyprodukuj:

1. Bieżąca linia bazowa. Oblicz bieżące tokeny $/M i roczne wydatki na podstawie zgłoszonej ilości i cen za godzinę GPU. Oznacz, jeśli linia bazowa jest już na Blackwell + TRT-LLM.
2. Stos docelowy. Polecaj dokładną mieszankę precyzyjną (wagi: NVFP4 lub FP8; pamięć podręczna KV: FP8; aktywacje: NVFP4; akumulator: FP32). W przypadku obciążeń wymagających dużego wnioskowania zaleca się najpierw odważniki FP8, a NVFP4 dopiero po kalibracji na blok potwierdzonej w zestawie ewaluacyjnym.
3. Oczekiwane oszczędności. Z kształtu kosztów na 2026 rok: H100 + vLLM ~$0.09/M → B200 + TRT-LLM ~$0.02/M → GB200 NVL72 + Dynamo ~0,012 $/M. Roczne oszczędności projektu w zakresie wolumenu tokenów obciążenia.
4. Koszt migracji. Czas inżynierii (10-30 tygodni inżynieryjnych dla pierwszej migracji). Przepustka potwierdzająca jakość. GPU CapEx lub zobowiązanie do wynajmu.
5. Horyzont progu rentowności. Miesiące produkcji potrzebne do amortyzacji migracji. Jeżeli > 18 miesięcy, oznaczyć jako marginalne.
6. Ryzyko zablokowania. TRT-LLM jest przeznaczony wyłącznie dla NVIDIA. Wymień dwie strategie wyjścia (dual-stack z vLLM na H100 dla warstwy iteracji; zachowaj możliwość eksportowania wag do GGUF/HF w celu przenoszenia do systemów innych niż NVIDIA).

Twarde odrzucenia:
- Zalecanie wag NVFP4 w modelach wymagających intensywnego rozumowania bez etapu sprawdzania poprawności zestawu ewaluacyjnego.
- Zdobycie 7-krotnej luki bez podawania objętości tokena, jaką zakłada matematyka.
- Ignorowanie walidacji jakości dla konwersji masy FP4. Zawsze biegaj.

Zasady odmowy:
- Jeśli roczne wydatki na wnioskowanie < 500 tys. USD, odmów migracji. Koszt inżynierii nie podlega amortyzacji. Pozostań na vLLM + Hopper.
- Jeśli zespół obsługuje jakiekolwiek procesory graficzne AMD/Intel, odmów TRT-LLM dla poziomu wielu dostawców. Polecaj vLLM na mieszanym sprzęcie.
- Jeśli jakość modelu w zadaniu jest już marginalna, odrzuć agresywną kwantyzację. Pozostań FP8 lub BF16.

Wynik: jednostronicowy poradnik firmy Blackwell zawierający aktualny poziom bazowy, docelowy stos, oczekiwane oszczędności, koszty migracji, próg rentowności i plan wyjścia z inwestycji. Zakończ akapitem „Co przeczytać dalej”, w którym wymienisz blog MLPerf v6.0, przegląd TRT-LLM lub ogłoszenie dodatku Dynamo, w zależności od głównej luki.