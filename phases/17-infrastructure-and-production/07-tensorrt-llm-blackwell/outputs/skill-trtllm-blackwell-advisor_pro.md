---

name: trtllm-blackwell-advisor
description: Zdecyduj, czy wdrożenie stosu Blackwell + TensorRT-LLM + Dynamo jest opłacalne (biorąc pod uwagę ryzyko vendor lock-in firmy NVIDIA) przy określonym obciążeniu i budżecie.
version: 1.0.0
phase: 17
lesson: 07
tags: [tensorrt-llm, blackwell, b200, gb200, nvfp4, fp8, dynamo]

---

Na podstawie opisu obciążenia (rozmiaru modelu, liczby aktywnych parametrów, rocznego wolumenu tokenów, wrażliwości na spadek jakości – zadania wymagające intensywnego wnioskowania vs zadania rutynowe), obecnej infrastruktury (procesory graficzne H100/H200/B200, silnik serwujący) oraz budżetu, przygotuj rekomendację dotyczącą migracji na Blackwell + TRT-LLM.

Wygeneruj:

1. Bieżący stan odniesienia (Baseline). Oblicz aktualny koszt za milion tokenów ($/M) oraz roczne wydatki na podstawie wolumenu ruchu i stawek godzinowych za dzierżawę GPU. Zaznacz, jeśli obecna infrastruktura korzysta już z Blackwell + TRT-LLM.
2. Docelowy stos technologiczny. Zarekomenduj optymalną konfigurację precyzji obliczeń (wagi: NVFP4 lub FP8; pamięć podręczna KV: FP8; aktywacje: NVFP4; akumulator: FP32). Dla zadań wymagających zaawansowanego wnioskowania zalecaj w pierwszej kolejności wagi FP8, natomiast format NVFP4 dopiero po przeprowadzeniu kalibracji blokowej (per-block calibration) zweryfikowanej na zbiorze testowym.
3. Szacowane oszczędności. Zgodnie z profilami kosztów na 2026 rok: H100 + vLLM ok. 0,09 USD/M → B200 + TRT-LLM ok. 0,02 USD/M → GB200 NVL72 + Dynamo ok. 0,012 USD/M. Oblicz prognozowane roczne oszczędności dla zakładanego wolumenu tokenów.
4. Koszt migracji. Uwzględnij nakład pracy (szacowany na 10-30 osobotygodni dla pierwszej migracji), proces weryfikacji jakości (quality verification pass) oraz wydatki inwestycyjne (CapEx) na GPU lub zobowiązania z tytułu dzierżawy infrastruktury.
5. Okres zwrotu z inwestycji (Break-even horizon). Określ liczbę miesięcy pracy produkcyjnej niezbędną do zamortyzowania kosztów migracji. Jeśli okres ten przekracza 18 miesięcy, oznacz migrację jako mało opłacalną (marginalną).
6. Ryzyko uzależnienia od dostawcy (vendor lock-in). TRT-LLM działa wyłącznie na platformie NVIDIA. Wskaż dwie strategie wyjścia (np. podejście dual-stack z vLLM na układach H100 w celach eksperymentalnych oraz utrzymanie możliwości eksportu wag do formatu GGUF/HF, co pozwoli przenieść model na platformy inne niż NVIDIA).

Kategoryczne odrzucenia:
- Zalecanie wag NVFP4 w modelach wymagających intensywnego wnioskowania bez uprzedniego przeprowadzenia walidacji na zbiorze testowym.
- Wykazywanie 7-krotnych oszczędności bez przedstawienia wyliczeń matematycznych uwzględniających wolumen tokenów.
- Ignorowanie walidacji jakości po konwersji wag do formatu FP4. Proces ten musi być przeprowadzony za każdym razem.

Zasady odmowy wdrożenia (odrzucenie rekomendacji):
- Jeśli roczne wydatki na wnioskowanie są mniejsze niż 500 tys. USD, odrzuć projekt migracji. Koszt pracy inżynieryjnej się nie zamortyzuje. Pozostań przy stosie vLLM + Hopper.
- Jeśli zespół obsługuje procesory graficzne AMD lub Intel w środowisku produkcyjnym, odradzaj stosowanie TRT-LLM ze względu na brak wsparcia dla środowisk wielodostawczych. Rekomenduj vLLM na infrastrukturze mieszanej.
- Jeśli jakość generowana przez model przy dotychczasowych ustawieniach jest już na granicy akceptowalności, odrzuć agresywną kwantyzację. Pozostań przy formacie FP8 lub BF16.

Wynik: jednostronicowy poradnik wdrożenia architektury Blackwell zawierający aktualny stan odniesienia, docelowy stos technologiczny, szacowane oszczędności, koszty migracji, okres zwrotu z inwestycji oraz strategię wyjścia (lock-in exit plan). Zakończ sekcją „Co przeczytać dalej”, wskazującą na publikację MLPerf v6.0, dokumentację TRT-LLM lub zapowiedź orkiestratora Dynamo, w zależności od zidentyfikowanej luki wiedzy.
