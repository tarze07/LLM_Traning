---

name: audio-evaluator
description: Wybierz wskaźniki, testy porównawcze, reguły normalizacji i format raportowania dla dowolnej wersji modelu audio.
version: 1.0.0
phase: 6
lesson: 17
tags: [evaluation, wer, mos, utmos, eer, der, fad, mmau, leaderboard]

---

Biorąc pod uwagę zadanie (ASR / TTS / klonowanie / weryfikacja głośników / diaryzacja / klasyfikacja / muzyka / LALM / przesyłanie strumieniowe S2S), wynik:

1. Podstawowy miernik. WER · MOS · UTMOS · SECS · EER · DER · MAP · FAD · Dokładność MMAU-Pro · opóźnienie P95. Jeden wybór.
2. Metryki wtórne. 1-3 dodatkowe osie (szybkość, różnorodność, solidność) i powód.
3. Reguła normalizacji. Małe litery, pasek interpunkcyjny, rozwijanie liczb, zwijanie białych znaków. Użyj normalizatora szeptów lub niestandardowego, udokumentuj to.
4. Punkt odniesienia publiczny. Kanoniczna tabela liderów, przeciwko której można raportować (Open ASR, TTS Arena, MMAU-Pro, VoxCeleb1-O, AudioSet, LongAudioBench itp.).
5. Zestaw własny. Wstrzymane dane domeny z N próbkami; podział demograficzny/akustyczny.
6. Forma raportowania. Dystrybucja (P50/P95/P99 dla opóźnienia; wycofanie według klasy w celu klasyfikacji; według kategorii dla MMAU). Szablon notatek o wersji.

Odrzuć ocenę jednoliczbową ze względu na opóźnienie (percentyle raportu). Odrzuć agregat tylko do celów klasyfikacji (raport według klasy). Odmawiaj wydań TTS bez MOS/UTMOS i SECS (podczas klonowania). Odmawiaj wydań ASR bez specyfikacji normalizacji WER. Odmawiaj wydań muzycznych za pomocą wyłącznie FAD — zawsze podłączaj do ludzkiego panelu MOS.

Przykładowy wpis: „Wydanie nowego angielsko-hiszpańskiego konwersacyjnego TTS. Trzeba przekonać zespół, że jest lepszy niż istniejąca wersja bazowa Cartesia-Sonic”.

Przykładowe wyjście:
- Podstawowy: UTMOS (sparowane próbki audio w 50 podpowiedziach na język) + MOS z panelem ludzkim (20 słuchaczy na język, ślepe A/B vs linia podstawowa).
- Drugorzędne: mediana TTFA i P95 (musi odpowiadać wartościom wyjściowym); SECS &gt; 0,80 w porównaniu do stałego odniesienia głosowego (bez regresji głośnika); CER w obie strony ASR (Whisper-large-v3-turbo) &lt; 2%.
- Normalizacja: normalizator szeptów w języku angielskim + wielojęzyczny normalizator przytulania twarzy w języku hiszpańskim dla podróży w obie strony WER.
- Publiczny benchmark: TTS Arena (w języku angielskim) i sztuczna analiza mowy dla względnego pozycjonowania ELO. Cel: w promieniu 50 ELO od najbliższego konkurenta.
- Własne: 200 podpowiedzi (100 w każdym języku) dotyczących pieniędzy, dat, nazw produktów, dwuzdaniowa narracja, emocjonalne czytanie, przełączanie kodów. 10 głosów demograficznych.
- Raportowanie: informacja o wersji z nagłówkiem (UTMOS + MOS), histogram P50/P95 TTFA, SECS CDF, podział CER według kategorii, objaśnienia dotyczące trybu awarii (wezwania o przełączenie kodu nie powiodły się w X%).