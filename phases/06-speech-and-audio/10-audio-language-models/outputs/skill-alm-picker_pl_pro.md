---

name: alm-picker
description: Dobierz odpowiedni model LALM, zestaw testowy (benchmark) oraz format wyjściowy (tekst vs. mowa) dla zadanego zadania analizy audio.
version: 1.0.0
phase: 6
lesson: 10
tags: [alm, lalm, qwen-omni, audio-flamingo, gemini-audio, mmau]

---

Na podstawie zadanego zadania (mowa / dźwięk / muzyka / wiele plików / długie nagranie, format wyjściowy, budżet opóźnień, licencja), określ:

1. Model: Qwen2.5-Omni-7B · Qwen3-Omni · SALMONN · Audio Flamingo 3 · Audio Flamingo Next · LTU · GAMs · Gemini 2.5 Pro (API) · GPT-4o Audio (API). Podaj jednozdaniowe uzasadnienie wyboru.
2. Zestaw testowy (benchmark): MMAU-Pro (mowa / dźwięk / muzyka / wiele plików) · LongAudioBench · AudioCaps · Clotho-AQA. Dobierz zbiór testowy bezpośrednio pod specyfikę zadania.
3. Format wyjściowy: Tylko tekst · tekst + mowa (np. Qwen-Omni, GPT-4o Audio). Uwzględnij budżet obliczeniowy dla dekodera mowy, jeśli jest wymagany.
4. Zabezpieczenia (Guardrails): Odrzucenie promptów wymagających porównywania wielu plików audio, jeśli dokładność modelu w tym podzbiorze wynosi < 30% (wynik bliski losowemu). Wymaganie diaryzacji przed przekazaniem nagrania do modelu LALM dla plików dłuższych niż 10 minut.
5. Reguły eskalacji: Kiedy zadanie powinno zostać przekierowane do modeli specjalistycznych (np. Whisper do transkrypcji, BEATs do klasyfikacji, pyannote do diaryzacji). Pamiętaj, że modele LALM nie są najlepsze w pojedynczych zadaniach cząstkowych.

Zasady weryfikacji:
- Odrzuć projekty wymagające porównywania wielu plików audio bez udokumentowanego wyniku modelu powyżej 40% w podzbiorze multi-audio MMAU-Pro.
- Odrzuć plany analizy długich nagrań (> 10 minut) bez uprzedniego przeprowadzenia diaryzacji mówców.
- Oznacz jako błąd każdą architekturę, która bazuje wyłącznie na wynikach ewaluacji podawanych przez twórców modelu (dostawców), bez przeprowadzenia niezależnej weryfikacji.

Przykładowe dane wejściowe: „Audyt zgodności (compliance): transkrypcja 10-minutowych nagrań rozmów bankowych z klientami + weryfikacja, czy doradca przedstawił obowiązkowe informacje o ryzyku”.

Przykładowy wynik:
- Model: Whisper-large-v3-turbo do generowania transkrypcji + Gemini 2.5 Pro (przez API) do weryfikacji zgodności na podstawie tekstu transkrypcji. Bezpośrednie zastosowanie modelu LALM na surowym audio brzmi zachęcająco, ale dokładność LALM drastycznie spada na nagraniach powyżej 10 minut.
- Benchmark: Podzbiór mowy (speech) w MMAU-Pro (Gemini 2.5 Pro osiąga tu 73,4%) – idealnie pokrywa obszar rozumowania nad mową. Dodatkowo przygotuj własny zbiór referencyjny (golden set) złożony z 50 nagrań testowych.
- Format wyjściowy: Tylko tekst. Odpowiedź głosowa nie jest wymagana w raportach z audytu.
- Zabezpieczenia: Wstępna diaryzacja za pomocą `pyannote.audio` 3.1; przesyłanie tekstu z podziałem na wypowiedzi poszczególnych mówców; logowanie poziomu pewności (confidence score) dla każdej decyzji.
- Reguły eskalacji: Rozmowy sklasyfikowane jako niezgodne z wymogami (brak przedstawienia ryzyka) powinny być automatycznie przekazywane do weryfikacji przez człowieka (audytora), zamiast podejmowania automatycznych decyzji.
