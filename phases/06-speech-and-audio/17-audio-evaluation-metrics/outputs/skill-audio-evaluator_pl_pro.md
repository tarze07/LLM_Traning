---

name: audio-evaluator
description: Wybierz metryki, benchmarki, reguły normalizacji tekstów oraz format raportowania na potrzeby ewaluacji i wydań modeli audio.
version: 1.0.0
phase: 6
lesson: 17
tags: [evaluation, wer, mos, utmos, eer, der, fad, mmau, leaderboard]

---

Na podstawie opisu zadania (ASR / TTS / klonowanie głosu / weryfikacja mówcy / diaryzacja / klasyfikacja / synteza muzyki / LALM / streaming S2S) wygeneruj:

1. Główna metryka: WER, MOS, UTMOS, SECS, EER, DER, MAP, FAD, dokładność MMAU-Pro lub opóźnienie P95. Wybierz jedną kluczową metrykę.
2. Metryki pomocnicze: od 1 do 3 dodatkowych wymiarów (np. szybkość, różnorodność, odporność) wraz z uzasadnieniem.
3. Reguły normalizacji tekstu: zmiana na małe litery, usuwanie interpunkcji, zamiana liczb na słowa, redukcja spacji. Wskaż użycie normalizatora Whisper (Whisper normalizer) lub rozwiązania autorskiego i dokładnie je opisz.
4. Publiczne benchmarki: kanoniczne tabele wyników (leaderboards) do porównania (np. Open ASR, TTS Arena, MMAU-Pro, VoxCeleb1-O, AudioSet, LongAudioBench itp.).
5. Własny zbiór testowy: wydzielony zbiór danych dziedzinowych o rozmiarze N próbek z uwzględnieniem zróżnicowania demograficznego i akustycznego.
6. Format raportowania: rozkład wyników (P50/P95/P99 dla opóźnień; czułość na klasę dla klasyfikacji; wyniki według kategorii dla MMAU). Szablon notatki do wydania (release notes).

Odrzucaj oceny opóźnienia oparte na pojedynczej wartości średniej (wymagaj raportowania percentyli). Odrzucaj wyłącznie zagregowane wyniki w zadaniach klasyfikacji (wymagaj raportowania wyników dla poszczególnych klas). Odmawiaj wydań modeli TTS bez podania metryk MOS/UTMOS oraz SECS (w przypadku klonowania głosu). Odmawiaj wydań modeli ASR bez dokładnego określenia reguł normalizacji tekstu do wyliczenia WER. Odmawiaj oceny modeli muzycznych wyłącznie za pomocą FAD – wymagane jest połączenie z testami odsłuchowymi na panelu ludzkim (MOS).

Przykładowe wejście: „Wydanie nowego angielsko-hiszpańskiego konwersacyjnego modelu TTS. Cel: wykazanie wyższości nad obecnym rozwiązaniem bazowym Cartesia-Sonic”.

Przykładowe wyjście:
- Główna metryka: UTMOS (porównanie par próbek audio na 50 promptach dla każdego języka) + MOS z panelem słuchaczy (20 osób na język, ślepe testy A/B w odniesieniu do linii bazowej).
- Metryki pomocnicze: mediana i percentyl P95 opóźnienia do pierwszego dźwięku (TTFA - Time to First Audio); SECS > 0,80 w porównaniu do stałego profilu głosowego (zapobieganie regresji cech mówcy); CER < 2% w teście round-trip z użyciem ASR (Whisper-large-v3-turbo).
- Normalizacja: Whisper normalizer dla języka angielskiego + normalizator z Hugging Face dla języka hiszpańskiego na potrzeby wyliczania WER w teście round-trip.
- Publiczny benchmark: TTS Arena (dla języka angielskiego) i ranking ELO sztucznej mowy do względnego pozycjonowania modelu. Cel: wynik w granicach 50 punktów ELO od najbliższego konkurenta.
- Własny zbiór: 200 promptów (po 100 na język) zawierających kwoty, daty, nazwy produktów, wypowiedzi dwuzdaniowe, czytanie z emocjami oraz mieszanie języków (code-switching). 10 zróżnicowanych głosów testowych.
- Format raportowania: metryki UTMOS + MOS w nagłówku, histogramy P50/P95 dla TTFA, wykres dystrybuanty (CDF) dla SECS, rozkład CER według kategorii oraz opis zidentyfikowanych błędów (np. „prompty z mieszaniem języków kończyły się niepowodzeniem w X% przypadków”).
