---

name: music-designer
description: Wybierz model generowania muzyki, strategię licencyjną, plan długości i metadane ujawniane na potrzeby wdrożenia.
version: 1.0.0
phase: 6
lesson: 09
tags: [music-generation, musicgen, stable-audio, suno, licensing]

---

Biorąc pod uwagę założenia (instrumentalne a piosenka, długość, reklama a badania, gatunek, budżet), wynik:

1. Modelka. MusicGen (rozmiar) · Stable Audio Open · ACE-Step XL · YuE · Suno (v5) · Udio (v4) · ElevenLabs Music · Google Lyria 3 / RealTime · MiniMax Music 2.5. Powód w jednym zdaniu.
2. Licencja i prawa. Licencja komercyjna na wygenerowany klip · Uznanie autorstwa (CC) · Niekomercyjna z ograniczeniami · Udoskonalanie posiadanego katalogu. Posiadacz praw do dokumentu i łańcuch.
3. Długość + konstrukcja. Pojedyncza generacja · fragmentacja + przenikanie · malowanie mostka · separacja pni, jeśli ścieżki wymagają edycji. Wyraźnie poradź sobie z 30-sekundową ścianą dryfującą.
4. Schemat podpowiedzi. Tonacja / BPM / gatunek / instrumentacja + (dla modeli wokalnych) teksty + znaczniki nastroju. Ogranicz nazwy gwiazd i znaczniki stylu będące znakami towarowymi.
5. Ujawnienie + metadane. Znak wodny (w stosownych przypadkach AudioSeal), znacznik metadanych `isAIGenerated`, nakładka ujawniająca sztuczną inteligencję w celu zapewnienia zgodności z ustawą UE o sztucznej inteligencji / CA SB 942.

Odmawiaj podpowiedzi w stylu celebrytów w otwartych modelach (filtr komercyjnych interfejsów API; własny host nie). Odrzuć generacje z licencją niekomercyjną (Stable Audio Open) na rzecz płatnych produktów. Odmawiaj rozpowszechniania muzyki wokalnej bez oznaczania ujawniającego. Oznacz potoki edycji pni, które zależą od łodyg Udio — te są objęte warunkami komercyjnymi, a nie darmowym użytkowaniem.

Przykładowe dane wejściowe: „Muzyka w tle do aplikacji do medytacji. Instrumentalna. Wymagane są pełne prawa komercyjne. Do 5 minut na utwór”.

Przykładowe wyjście:
- Model: MusicGen-large (MIT) na instrumenty z pełnymi prawami komercyjnymi. Brak stabilnego dźwięku (niekomercyjny).
- Licencja: MIT – prawa komercyjne zastrzeżone przez wdrażającego. Właściciel praw do utworu: firma tworząca aplikację.
- Długość: fragment na 30-sekundowe segmenty z 3-sekundowym przejściem; 10 pokoleń połączonych → 5 min. Dodaj subtelną otoczkę przyciemniającą/zanikającą, aby ukryć dryf.
- Podpowiedź: `"slow ambient meditation, 60 BPM, soft strings and low pad, in D minor, no drums"` — pin BPM, pin key, pin oprzyrządowanie, wyraźnie wyklucza elementy perkusyjne.
- Ujawnienie: tag `"AI-generated music"` w napisach końcowych aplikacji; metadane `creator=AI-Gen:MusicGen-large, date=<iso>`. Opcja AudioSeal (wersja instrumentalna ma mniejsze ryzyko fałszerstwa, ale zapewnia głęboką obronę).