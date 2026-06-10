---

name: video-qa
description: Zbuduj potok zrozumienia wideo za pomocą segmentacji scen, indeksowania wielowektorowego, uziemienia czasowego i cytatów ze znacznikami czasu.
version: 1.0.0
phase: 19
lesson: 12
tags: [capstone, video, multimodal, gemini, qwen-vl, molmo, transnet, qdrant]

---

Mając 100 godzin materiału wideo, utwórz potok przetwarzania i system zapytań, który odpowiada na pytania w języku naturalnym, uwzględniając znaczniki czasu (początek i koniec) oraz podgląd klatek.

Plan budowy:

1. Pobieraj filmy (adresy URL YouTube lub MP4); W razie potrzeby obniż rozdzielczość do 720p.
2. Segmentacja scen za pomocą TransNetV2 lub PySceneDetect; emituj `[{scene_id, start_ms, end_ms, keyframe_path}]`.
3. ASR z Whisper-v3-turbo (szybszy szept) generujący znaczniki czasu na poziomie słów; kawałek na scenę.
4. Napisy VLM w Gemini 2.5 Pro lub Qwen3-VL-Max lub Molmo 2; emituj podpis + osadzanie ramki.
5. Indeks wielowektorowy Qdrant z trzema nazwanymi wektorami na scenę (caption_emb, ramka_emb, transkrypcja_emb) i ładunkiem {video_id, scene_id, start_ms, end_ms, keyframe_url}.
6. Zapytanie: trzy równoległe gęste zapytania; wzajemne połączenie rang w celu połączenia; top-k=5 scen.
7. Uziemienie czasowe (adapter TimeLens lub VideoITG) udoskonala (początek, koniec) w górnej scenie.
8. Synteza VLM (Gemini 2.5 Pro) z zapytaniem + klipy z 3 najlepszych scen + transkrypcja; wymagają cytatów `(video_id, start_ms, end_ms)`.
9. Eval na ActivityNet-QA, NeXT-GQA oraz ręcznie oznaczonym zestawem niestandardowym zawierającym 100 zapytań. Podaj dokładność ogólną i według klasy pytania (opisowe, zliczające, typu działania).

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | Tymczasowe uziemienie IoU | IoU na wyciągniętym zestawie uziemiającym |
| 20 | Dokładność kontroli jakości | Zestaw niestandardowy NeXT-GQA i 100 zapytań |
| 20 | Przepustowość pozyskiwania | Godziny filmów indeksowanych na dolara |
| 20 | Interfejs użytkownika i cytowanie UX | Linki do znaczników czasu, pasek miniatur, skok do klatki |
| 15 | Częstotliwość halucynacji | Dokładność liczenia i rodzaju akcji zgłaszana osobno |

Twarde odrzucenia:

- Potoki łączące jeden wektor na scenę. Aby różnice klas były widoczne, wymagany jest wielowektor.
- Odpowiedzi bez (początku i końca) cytatów.
- Raportowanie jednej ogólnej dokładności bez podziału na podzbiór zliczania/działań.
- Synteza VLM, która nie odbiera bezpośrednio klatek scen (wejścia tekstowe tracą wizualne uziemienie).

Zasady odmowy:

- Odmawiaj udostępniania filmów o niejasnym pochodzeniu licencji; wymagają tagu licencji na każdym video_id.
- Odmów żądania odpowiedzi „w czasie rzeczywistym” przy szybkościach przyjmowania przekraczających zmierzoną przepustowość.
- Odmawiaj ukrywania liczby halucynacji liczenia/akcji wewnątrz ogólnej wartości dokładności.

Dane wyjściowe: repozytorium zawierające segmentację sceny + ASR + potok napisów, wielowektorową kolekcję Qdrant, tymczasowy adapter uziemienia, przeglądarkę Next.js 15 z głębokimi linkami do sygnatury czasowej, wyniki oceny trzech testów porównawczych (ActivityNet-QA, NeXT-GQA, niestandardowe) oraz zapis wymieniający trzy zaobserwowane klasy błędów zliczania lub typu akcji oraz zmianę pobierania lub syntezy, która zmniejszyła każdą z nich.