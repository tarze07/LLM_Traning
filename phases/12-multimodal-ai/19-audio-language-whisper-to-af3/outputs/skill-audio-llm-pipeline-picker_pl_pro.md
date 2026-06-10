---

name: audio-llm-pipeline-picker
description: Ułatwia wybór między podejściem kaskadowym (Whisper + LLM) a zintegrowanym (AF3 / Qwen-Audio) dla zadań audio, określając konfigurację enkodera i mostka.
version: 1.0.0
phase: 12
lesson: 19
tags: [whisper, audio-flamingo-3, qwen-audio, cascaded, end-to-end]

---

Na podstawie zadania audio (transkrypcja, podsumowanie, diaryzacja, detekcja emocji, muzyka, odgłosy tła, wykrywanie deepfake'ów, temporal grounding) oraz ograniczeń wdrożeniowych, wybierz optymalny potok technologiczny i wygeneruj konfigurację.

Wygeneruj:

1. **Wybór potoku technologicznego:** Podejście kaskadowe (jeśli zadanie wymaga wyłącznie transkrypcji lub podsumowania czystej mowy) lub zintegrowane end-to-end (AF3 / Qwen-Audio) dla wszelkich analiz akustycznych.
2. **Stos enkoderów:** Whisper-large-v3 (optymalny dla mowy), BEATs (optymalny dla muzyki i tła) lub konkatenacja AF-Whisper (rozwiązanie zbalansowane).
3. **Konfiguracja adaptera (mostka):** 32–64 zapytania (queries) w adapterze Q-former lub tokeny RVQ dla strumieniowania danych.
4. **Wybór modelu LLM:** Qwen2.5-7B (optymalizacja kosztowa) lub Qwen2.5-72B / rdzeń AF3 (najwyższa jakość).
5. **Łańcuch myśli na żądanie (CoT):** Aktywuj w trudnych zadaniach wnioskowania (jak w MMAU), wyłącz dla maksymalizacji przepustowości w zadaniach czystej transkrypcji.
6. **Oczekiwane wyniki w benchmarku MMAU:** Podejście kaskadowe (~0,50), Qwen-Audio (~0,60), AF3 (~0,72), Gemini 2.5 Pro (~0,78).

Kryteria odrzucenia (Twarde reguły):
- Rekomendowanie potoków kaskadowych w zadaniach muzyki lub emocji. Sygnał akustyczny ulega bezpowrotnej utracie na etapie transkrypcji.
- Stosowanie adaptera Q-former z liczbą zapytań <32 w zadaniach wielozadaniowych. Prowadzi to do niedoreprezentowania informacji akustycznych we wnioskowaniu.
- Twierdzenie, że sam model Whisper wystarczy do poprawnej analizy muzyki. Whisper był trenowany głównie na danych głosowych.

Zasady odmowy (Rezygnacja z projektu):
- Jeśli użytkownik wymaga strumieniowania audio w konwersacji w czasie rzeczywistym (głosowe wejście/wyjście), odrzuć AF3 oparty na module Q-former i poleć modele Moshi lub Qwen-Omni (Lekcja 12.20).
- Jeśli wymagany budżet opóźnienia wynosi <500 ms dla prostego zadania transkrypcji, odrzuć pełne modele i poleć potok kaskadowy ze strumieniową wersją Whisper.
- Jeśli celem jest specyficzne zadanie audio (np. wykrywanie deepfake'ów lub anomalii kompresji), odrzuć domyślne konfiguracje i zaproponuj dostrojenie (finetuning) AF3 na dedykowanych danych syntetycznych.

Dane wyjściowe: Jednostronicowy raport zawierający wybór potoku technologicznego, konfigurację enkoderów, parametry mostka, wybór LLM, flagę CoT oraz prognozowaną dokładność. Na końcu dodaj odnośniki do prac: arXiv 2212.04356 (Whisper) oraz 2507.08128 (AF3).
