---

name: token-gen-cost-analyzer
description: Oblicz liczbę tokenów, opóźnienie wnioskowania i pułap jakości dla generacji następnego tokenu w stylu Emu3 i wybierz pomiędzy rodziną Emu3 a dyfuzją.
version: 1.0.0
phase: 12
lesson: 12
tags: [emu3, next-token-prediction, video-gen, diffusion, cfg]

---

Biorąc pod uwagę specyfikację produktu generacji (obraz lub wideo, docelowa rozdzielczość, poziom jakości, wymagania dotyczące przepustowości), oblicz liczbę tokenów dla generacji następnego tokenu w stylu Emu3, oszacuj koszt wnioskowania i wybierz pomiędzy rodziną Emu3 a dyfuzją.

Wyprodukuj:

1. Liczba żetonów. Tokeny na obraz przy wybranej redukcji tokenizera (zwykle 8x na przyciemnienie obrazu). Tokeny dla poszczególnych filmów z VQ 3D (zwykle 4x4x4 czasoprzestrzenne).
2. Opóźnienie wnioskowania. Tokeny/przepustowość (tokeny na sekundę) dla rodziny Emu3; kroki odszumiania * czas kroku dla dyfuzji. Przytocz konkretne serie A100 / H100.
3. Pułap jakości. Rekonstrukcja tokenizera PSNR (30-32 dB dla klasy IBQ), oczekiwania FID na MJHQ-30K, FVD dla wideo.
4. Konfiguracja CFG. Zalecana waga wskazówek (gamma) na zadanie; typowy 3,0 dla standardowej generacji, 5-7 dla silnej, szybkiej przyczepności.
5. Wybierz. Rodzina Emu3, jeśli produkt wymaga ujednoliconego zrozumienia + generowania lub elastyczności dowolnej modalności; dyfuzja (SDXL / SD3 / Flux), jeśli produkt generuje wyłącznie obrazy ze ścisłym opóźnieniem.

Twarde odrzucenia:
- Twierdzenie, że Emu3 jest szybsze niż rozpowszechnianie przy wnioskowaniu. Tak nie jest; dekodowanie autoregresyjne na tysiącach tokenów obrazu to koszt stały.
- Rekomendowanie rodziny Emu3 bez podawania wagi CFG. Bez tego jakość upada.
- Proponowanie Emu3 do generowania obrazu w ścisłej rozdzielczości 4K. Liczenie tokenów przy rozdzielczości 2048+ niszczy pamięć podręczną KV i zajmuje kilka minut.

Zasady odmowy:
- Jeśli budżet opóźnienia wynosi <5 s na obraz, odrzuć Emu3 i poleć SDXL lub SD3.
- Jeśli produkt musi emitować obrazy ORAZ je opisywać ORAZ ze względu na obrazy stron trzecich, poleć rodzinę Emu3 (ważna jest jednolita strata); dyfuzja nie może tego zrobić bez oddzielnego VLM.
- Jeśli użytkownik chce otwartych ciężarków z licencją zezwalającą do użytku komercyjnego, odmów Emu3 — najpierw sprawdź jego licencję; niektóre wersje mają charakter wyłącznie badawczy.

Dane wyjściowe: jednostronicowa analiza zawierająca liczbę tokenów, szacunki opóźnień, pułap jakości, konfigurację CFG i wybór z uzasadnieniem. Zakończ arXiv 2409.18869 (Emu3) i 2408.11039 (Transfusion) jako alternatywę.