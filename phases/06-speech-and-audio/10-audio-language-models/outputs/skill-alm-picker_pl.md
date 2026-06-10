---

name: alm-picker
description: Wybierz model języka audio, podzbiór testów porównawczych, modalność wyjściową (tekst kontra mowa) i poręcze dla zadania rozumienia dźwięku.
version: 1.0.0
phase: 6
lesson: 10
tags: [alm, lalm, qwen-omni, audio-flamingo, gemini-audio, mmau]

---

Biorąc pod uwagę zadanie (mowa/dźwięk/muzyka/multi-audio/długie audio, modalność wyjściowa, opóźnienie, licencja), wynik:

1. Modelka. Qwen2.5-Omni-7B · Qwen3-Omni · SALMONN · Audio Flamingo 3 · AF-Next · LTU · GAMA · Gemini 2.5 Pro (API) · GPT-4o Audio (API). Powód w jednym zdaniu.
2. Podzbiór testu porównawczego do sprawdzenia. MMAU-Pro mowa / dźwięk / muzyka / multi-audio · LongAudioBench · AudioCaps · ClothoAQA. Wybierz oś pasującą do zadania użytkownika.
3. Modalność wyjściowa. Tylko tekst · tekst + mowa (Qwen-Omni, GPT-4o Audio). W razie potrzeby budżet na dodatkowy dekoder mowy.
4. Poręcze. Odrzuć monity wymagające porównania wielu dźwięków, jeśli wynik Twojego modelu w trybie wielu dźwięków wynosi &lt; 30% (prawie losowo). Diarizuj przed LALM dla &gt; 10-minutowe wpisy.
5. Eskalacja. Kiedy to zadanie powinno wrócić do wyspecjalizowanego modelu — szept do transkrypcji, BEAT do klasyfikacji, pyannote do diaryzacji. LALM nie jest najlepszy z każdego z nich.

Odmawiaj wysyłania zadań porównywania wielu plików audio bez sprawdzenia wyników modelu &gt; 40% w podzbiorze multi-audio MMAU-Pro. Odrzuć długi dźwięk (> 10 min) bez diaryzacji w górę. Oznacz każde wdrożenie, które korzysta z numerów zgłoszonych przez dostawcę, bez niezależnej ponownej weryfikacji.

Przykładowe dane wejściowe: „Audyt zgodności: transkrypcja 10-minutowych nagrań rozmów bankowych + sprawdzenie, czy agent zapoznał się z obowiązkowymi ujawnieniami”.

Przykładowe wyjście:
- Model: Whisper-large-v3-turbo do transkrypcji + Gemini 2.5 Pro (przez API) do ujawniania informacji - kontrola jakości transkrypcji. LALM bezpośrednio na surowym dźwięku jest kuszący, ale dokładność LALM w przypadku długiego dźwięku spada powyżej 10 minut.
- Podzbiór wzorcowy: podzbiór mowy MMAU-Pro (Gemini 2.5 Pro = 73,4%) — obejmuje oś rozumowania mowy. Sprawdź także na miejscu swój własny złoty zestaw za 50 połączeń.
- Tryb wyjściowy: tylko tekst. Mowa nie jest potrzebna do raportu z audytu.
- Poręcze: najpierw wykonaj diarize za pomocą pyannote 3.1; wysyłaj oddzielnie segmenty dla każdego głośnika; rejestruj wynik zaufania na połączenie.
- Eskalacja: jeśli połączenie nie przejdzie kontroli ujawnienia, kieruj je do osoby sprawdzającej zamiast do flagi autonomicznej.