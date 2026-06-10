---

name: music-designer
description: Zaprojektuj potok generowania muzyki, obejmujący wybór modelu, strategię licencyjną, strukturę i długość utworów oraz format metadanych oznaczających użycie AI.
version: 1.0.0
phase: 6
lesson: 09
tags: [music-generation, musicgen, stable-audio, suno, licensing]

---

Na podstawie zadanego celu (utwór instrumentalny vs. piosenka z wokalem, długość utworu, zastosowanie komercyjne vs. badawcze, gatunek muzyczny, budżet), określ:

1. Model: MusicGen (rozmiar) · Stable Audio Open · ACE-Step XL · YuE · Suno (v5) · Udio (v4) · ElevenLabs Music · Google Lyria 3 / RealTime · MiniMax Music 2.5. Podaj jednozdaniowe uzasadnienie wyboru.
2. Licencję i prawa autorskie: Licencja komercyjna na wygenerowany klip · licencje Creative Commons (CC) · licencje niekomercyjne z ograniczeniami · douczanie na własnym katalogu utworów. Określ łańcuch praw autorskich i podmiot posiadający prawa.
3. Długość i strukturę utworu: Pojedyncza generacja · podział na fragmenty (chunking) i przenikanie (cross-fading) · inpainting mostka (bridge) · eksport i separacja ścieżek (stems) w przypadku edycji poszczególnych partii instrumentów. Zaproponuj rozwiązanie radzące sobie z degradacją spójności i rozbieżnościami tempa po 30 sekundach generacji.
4. Schemat promptu (Prompt Engineering): Tonacja / BPM / gatunek / instrumentarium + (dla modeli wokalnych) tekst utworu oraz znaczniki nastroju. Wyklucz nazwy znanych artystów oraz chronione znaki towarowe określające styl muzyczny.
5. Ujawnianie pochodzenia i metadane: Osadzanie cyfrowego znaku wodnego (np. AudioSeal), znacznik metadanych `isAIGenerated`, oraz sposób ujawniania generowania przez AI w celu zachowania zgodności z regulacjami EU AI Act oraz California SB 942.

Zasady weryfikacji:
- Odrzuć zapytania (prompty) naśladujące znanych artystów w modelach otwartoźródłowych (brak wbudowanych automatycznych filtrów, które posiadają komercyjne API).
- Odrzuć generowanie utworów na licencjach niekomercyjnych (np. Stable Audio Open) do celów płatnych produktów/usług.
- Odrzuć plany dystrybucji muzyki wokalnej bez wyraźnego oznaczenia jej pochodzenia (AI disclosure label).
- Oznacz jako błąd potoki produkcyjne oparte na separacji ścieżek (stems) z platformy Udio do celów komercyjnych bez wykupienia odpowiedniego planu komercyjnego (plany darmowe zabraniają takiego użycia).

Przykładowe dane wejściowe: „Muzyka w tle do aplikacji do medytacji. Instrumentalna. Wymagane są pełne prawa komercyjne. Do 5 minut na utwór”.

Przykładowy wynik:
- Model: MusicGen-large (licencja MIT) do syntezy utworów instrumentalnych z pełnymi prawami komercyjnymi. Odrzucenie Stable Audio Open z uwagi na licencję wyłącznie niekomercyjną.
- Licencja: MIT – pełne prawa komercyjne zachowane przez wdrażającego. Właścicielem praw autorskich do wygenerowanego utworu jest firma tworząca aplikację.
- Długość i strukturę: Podział na 30-sekundowe segmenty połączone 3-sekundowym przenikaniem (cross-fade); łącznie 10 połączonych segmentów daje utwór o długości 5 minut. Zastosowanie subtelnego wyciszania/podgłaśniania (fade-in/fade-out) w celu ukrycia rozbieżności tempa.
- Prompt: `"slow ambient meditation, 60 BPM, soft strings and low pad, in D minor, no drums"` — sztywno określone BPM, tonacja oraz instrumentarium, a także jawne wykluczenie perkusji.
- Ujawnianie: Oznaczenie `"AI-generated music"` w sekcji informacji o autorach aplikacji; metadane pliku audio: `creator=AI-Gen:MusicGen-large, date=<iso>`. Zastosowanie AudioSeal jako dodatkowe zabezpieczenie.
