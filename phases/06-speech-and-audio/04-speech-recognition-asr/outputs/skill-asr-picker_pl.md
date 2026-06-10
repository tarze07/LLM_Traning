---

name: asr-picker
description: Wybierz model ASR, strategię dekodowania, fragmentację i fuzję LM dla danego celu wdrożenia.
version: 1.0.0
phase: 6
lesson: 04
tags: [audio, asr, speech-recognition]

---

Biorąc pod uwagę cel wdrożenia (lista języków, domena, budżet opóźnień, sprzęt, tryb offline/streaming, czas trwania klipu), wynik:

1. Modelka. Whisper-large-v3-turbo / Parakeet-TDT / Canary-Flash / wav2vec 2.0 / Moonshine. Uzasadnienie w jednym zdaniu.
2. Dekodowanie. Chciwy / szerokość wiązki / spadek temperatury / masa fuzji LM. Powód związany z budżetem jakościowym.
3. Kawałki i VAD. Długość kawałka, krok, czy bramka z Silero-VAD, czy Whisper.
4. Polityka językowa. Wymuś język a auto-LID; jak obsługiwać ramki międzyjęzykowe.
5. Plan ewaluacyjny. WER na zestawie testowym domeny, zasięg na głośnik, częstość halucynacji w klipach ciszy.

Odrzuć jakiekolwiek długoterminowe wdrożenie Szeptu bez bramkowania VAD (podatność na halucynacje w ciszy). Odmów zgłoszenia WER bez normalizacji tekstu (dolny, punktowany pasek). Oznacz dowolną szerokość wiązki > 16 bez LM; surowe belki nad półfabrykatami nie pomagają.