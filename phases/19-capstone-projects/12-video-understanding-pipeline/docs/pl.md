# Capstone 12 — Potok zrozumienia wideo (scena, kontrola jakości, wyszukiwanie)

> Dwanaście laboratoriów wyprodukowało Marengo + Pegasus. VideoDB dostarczyło interfejs API CRUD-for-video. Molmo 2 AI2 opublikował otwarte punkty kontrolne VLM. Długi kontekst Gemini natywnie obsługuje godziny wideo. TimeLens-100K zdefiniował tymczasowe uziemienie na dużą skalę. Potok na rok 2026 jest ustalony: segmentacja scen, podpisy dla każdej sceny + osadzanie, wyrównanie transkrypcji, indeks wielowektorowy i zapytanie, które odpowiada znacznikami czasu (początku, końca) i podglądem klatek. Zwieńczeniem jest pochłonięcie 100 godzin, osiągnięcie publicznych standardów i pomiar halucynacji w kwestiach związanych z liczeniem i działaniem.

**Typ:** Zwieńczenie
**Języki:** Python (potok), TypeScript (UI)
**Wymagania wstępne:** Faza 4 (CV), Faza 6 (mowa), Faza 7 (transformatory), Faza 11 (inżynieria LLM), Faza 12 (multimodalność), Faza 17 (infrastruktura)
**Wykonywane fazy:** P4 · P6 · P7 · P11 · P12 · P17
**Czas:** 30 godzin

## Problem

Długoterminowa kontrola jakości wideo to multimodalny problem wymagający największej przepustowości w skali 2026 roku. Gemini 2.5 Pro może natywnie odczytać 2-godzinne wideo, ale przetworzenie 100 godzin wideo w korpusie, który można przeszukiwać, nadal wymaga indeksu na poziomie sceny. Kształt produkcji łączy segmentację scen (TransNetV2 lub PySceneDetect), podpisy dla każdej sceny za pomocą VLM (Gemini 2.5, Qwen3-VL-Max lub Molmo 2), wyrównanie transkrypcji (Whisper-v3-turbo ze znacznikami czasu słów) oraz indeks wielowektorowy, który przechowuje podpisy, osadzanie klatek i transkrypcję obok siebie. Potok zapytań odpowiada znacznikami czasu (początek, koniec) i podglądami klatek.

Testy porównawcze są publiczne (ActivityNet-QA, NeXT-GQA) plus Twój własny, niestandardowy zestaw 100 zapytań. Halucynacje związane z liczeniem i pytaniami dotyczącymi działania to znana, trudna klasa niepowodzeń; zwieńczenie wyraźnie to mierzy.

## Koncepcja

W momencie poboru trzy rurociągi biegną równolegle. **Segmentacja scen** dzieli wideo na sceny. **Napisy VLM** generują podpisy dla każdej sceny i osadzaną klatkę z klatki kluczowej. **Wyrównanie ASR** tworzy znaczniki czasu na poziomie słów. Trzy strumienie są połączone (id_sceny, zakres czasu). Każda scena otrzymuje trzy typy wektorów w indeksie wielowektorowym (Qdrant): osadzanie podpisów, osadzanie klatek kluczowych, osadzanie transkrypcji.

W czasie zapytania pytanie w języku naturalnym jest uruchamiane względem wszystkich trzech wektorów; wyniki łączą się z RRF; adapter uziemienia czasowego (w stylu TimeLens) udoskonala okno (początek, koniec) w górnej scenie. Syntezator VLM (Gemini 2.5 Pro lub Qwen3-VL-Max) pobiera zapytania + najlepsze sceny + przycięte klatki i odpowiedzi z cytowanymi znacznikami czasu i podglądem klatek.

Pomiar halucynacji ma znaczenie. Pytania dotyczące liczenia („ile osób wchodzi do pokoju?”) i rodzaju działania („czy szef kuchni nalewa przed mieszaniem?”) są notorycznie zawodne. Zgłaszaj dokładność oddzielnie od pytań opisowych.

## Architektura

```
video file / URL
      |
      v
PySceneDetect / TransNetV2  (scene segmentation)
      |
      +--- per-scene keyframe --- VLM caption + frame embedding
      |                            (Gemini 2.5 Pro / Qwen3-VL-Max / Molmo 2)
      |
      +--- audio channel --- Whisper-v3-turbo ASR + word timestamps
      |
      v
multi-vector Qdrant: {caption_emb, keyframe_emb, transcript_emb}
      |
query:
  dense queries against all three -> RRF merge -> top-k scenes
      |
      v
TimeLens / VideoITG temporal grounding (refine start/end within scene)
      |
      v
VLM synth: query + top scenes + frame previews
      |
      v
answer + (start, end) timestamps + frame thumbs + citations
```

## Stos

- Segmentacja scen: TransNetV2 (najnowocześniejszy model 2024-26) lub PySceneDetect
- ASR: Whisper-v3-turbo poprzez szybszy szept ze znacznikami czasu słów
- Napis VLM + odpowiadający: Gemini 2.5 Pro lub Qwen3-VL-Max lub Molmo 2
- Uziemienie tymczasowe: adapter przeszkolony przez TimeLens-100K lub VideoITG
- Indeks: Qdrant z obsługą wielu wektorów (podpis / ramka / transkrypcja)
- Interfejs użytkownika: Next.js 15 z odtwarzaczem wideo HTML5 i miniaturami scen
- Eval: ActivityNet-QA, NeXT-GQA, niestandardowy, ręcznie oznaczony zestaw 100 pytań
- Test porównawczy halucynacji: podzbiory liczenia i działania z etykietami ręcznymi

## Zbuduj to

1. **Połknij walker.** Akceptuj adresy URL YouTube lub lokalne pliki MP4. W razie potrzeby obniż rozdzielczość do 720p. Utrzymaj `{video_id, file_path}`.

2. **Segmentacja sceny.** Uruchom TransNetV2 lub PySceneDetect, aby utworzyć `[{scene_id, start_ms, end_ms, keyframe_path}]`. Docelowe 100 godzin: ~6–8 tys. scen.

3. **ASR pass.** Uruchom Whisper-v3-turbo na audio; eksportuj znaczniki czasu na poziomie słów; podzielony na wycinki transkrypcji poszczególnych scen.

4. **Napisy VLM.** Dla każdej sceny wywołaj Gemini 2.5 Pro (lub Qwen3-VL-Max) z klatką kluczową i szablonem krótkich podpisów. Utwórz podpis + osadzenie ramki.

5. **Indeks wielowektorowy.** Kolekcja Qdrant z trzema nazwanymi wektorami. Ładunek: `{video_id, scene_id, start_ms, end_ms, keyframe_url}`.

6. **Zapytanie.** Pytanie w języku naturalnym powoduje uruchomienie trzech gęstych zapytań; połączyć się z wzajemną fuzją rang; top-k=5 scen.

7. **Tymczasowe uziemienie.** Uruchom adapter w stylu TimeLens na górnej scenie, aby udoskonalić okno (początek, koniec) w scenie.

8. **Syntyzator VLM** Zadzwoń do Gemini 2.5 Pro z zapytaniem + klipami z 3 najlepszych scen (w postaci obrazów lub krótkich klipów) + transkrypcjami. Wymagaj `(video_id, start_ms, end_ms)` cytatów.

9. **Eval.** Uruchom ActivityNet-QA i NeXT-GQA. Utwórz niestandardowy zestaw zawierający 100 zapytań. Zgłaszaj ogólną dokładność + podział na klasy (liczenie, działanie, opisowe).

## Użyj tego

```
$ video-qa ask --url=https://youtube.com/watch?v=X "how many cars pass the intersection in the first minute?"
[scene]    23 scenes detected
[asr]      transcript complete, 4m12s
[index]    69 vectors written (23 scenes x 3)
[query]    top scene: scene 3 [01:32-01:54], confidence 0.84
[ground]   refined window: [00:12-00:58]
[synth]    gemini 2.5 pro, 1.4s
answer:    5 cars pass the intersection between 00:12 and 00:58.
citations: [scene 3: 00:12-00:58]
          [frame preview at 00:14, 00:27, 00:44, 00:51, 00:57]
```

## Wyślij to

Elementem dostarczanym jest `outputs/skill-video-qa.md`. Biorąc pod uwagę adres URL YouTube lub przesłany film, potok indeksuje sceny i odpowiada na pytania z cytatami ze znacznikiem czasu.

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | Tymczasowe uziemienie IoU | Złącze krzyżowe na wyciągniętym zestawie uziemiającym |
| 20 | Dokładność kontroli jakości | NeXT-GQA i niestandardowe 100 zapytań |
| 20 | Przepustowość pozyskiwania | Godziny filmów na jednego wydanego dolara |
| 20 | Interfejs użytkownika i cytowanie UX | Linki do znaczników czasu, pasek miniatur, skok do klatki |
| 15 | Częstotliwość halucynacji | Dokładność liczenia i działania oddzielnie |
| **100** | | |

## Ćwiczenia

1. Zamień Gemini 2.5 Pro na Qwen3-VL-Max na karcie napisów. Zgłoś różnicę jakości napisów na próbce 50 scen ocenionych przez ludzi.

2. Zmniejsz osadzanie klatek na scenę do jednego wektora zbiorczego zamiast wielu wektorów. Zmierz regresję odzyskiwania.

3. Zbuduj tryb „ścisłego liczenia”: syntezator wyodrębnia każdą zliczoną instancję ze znacznikiem czasu, a użytkownik klika, aby to sprawdzić. Zmierz, czy weryfikacja użytkownika zmniejsza halucynacje.

4. Benchmarkowy koszt wykorzystania: liczba godzin wideo za dolara w przypadku trzech opcji VLM. Wybierz najsłodszy punkt.

5. Dodaj transkrypcję z diaryzacją mówcy: uruchom diaaryzację mówcy w programie pyannote w dźwięku i osadź transkrypcje poszczególnych mówców. Zademonstruj „co Alicja powiedziała o X?” zapytania.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Segmentacja sceny | „Wykrywanie strzału” | Cięcie wideo na sceny na granicach ujęcia |
| Indeks wielowektorowy | „Podpis + ramka + transkrypcja” | Kolekcja Qdrant z nazwanymi wektorami na reprezentację |
| Uziemienie tymczasowe | „Kiedy to się dokładnie stało” | Udoskonalenie okna (początku, końca) odpowiedzi na zapytanie |
| Osadzanie ramek | „Reprezentacja wizualna” | Wektorowe osadzanie klatki kluczowej; używany do podobieństwa wizualnego sceny |
| Fuzja RRF | „Wzajemna fuzja rang” | Połącz strategię na wielu listach rankingowych; klasyczna sztuczka polegająca na odzyskaniu hybrydy |
| Liczenie halucynacji | „Błąd w liczeniu” | Znany tryb awarii VLM na pytania „ile X” |
| ActivityNet-QA | „Porównanie jakości wideo” | Test porównawczy dokładności kontroli jakości wideo w formie długiej |

## Dalsze czytanie

- [AI2 Molmo 2](https://allenai.org/blog/molmo2) — otwieranie punktów kontrolnych VLM
– [TimeLens (CVPR 2026)](https://github.com/TencentARC/TimeLens) — tymczasowe uziemienie na dużą skalę
– [Długi kontekst filmu Gemini](https://deepmind.google/technologies/gemini) — hostowane odniesienie
- [VideoDB](https://videodb.io) — informacje o interfejsie API CRUD-for-video
- [Twelve Labs Marengo + Pegasus](https://www.twelvelabs.io) — odniesienie komercyjne
- [TransNetV2](https://github.com/soCzech/TransNetV2) — model segmentacji sceny
- [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) — klasyczna otwarta alternatywa
- [ActivityNet-QA](https://arxiv.org/abs/1906.02467) — referencyjny test porównawczy eval