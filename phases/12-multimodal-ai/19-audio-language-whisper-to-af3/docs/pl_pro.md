# Modele audio-językowe: od modelu Whisper do Audio Flamingo 3

> Model Whisper (Radford i in., grudzień 2022) zrewolucjonizował rozpoznawanie mowy. Przeszkolony na 680 tysiącach godzin słabo nadzorowanych nagrań wielojęzycznych, oparty na prostej architekturze koder-dekoder (transformer), stał się punktem odniesienia dla każdego kolejnego systemu ASR. Jednak samo rozpoznawanie mowy (transkrypcja) to nie to samo co jej rozumienie. Pytania takie jak „jakie instrumenty słychać w tym nagraniu?”, „jakie emocje wyraża mówca?” lub „co wydarzyło się w 3. minucie?” wymagają głębokiej analizy sygnału audio, a nie tylko tekstu. Modele Qwen-Audio, SALMONN, LTU oraz NVIDIA Audio Flamingo 3 (AF3, lipiec 2025) stopniowo rozwijały te możliwości: łącząc enkodery klasy Whisper z modułami Q-former, szkoląc na parach instrukcja-dźwięk i dodając mechanizmy łańcucha myśli (Chain of Thought). Ta lekcja opisuje ewolucję tych technologii.

**Typ:** Teoria / Przegląd
**Języki:** Python (biblioteka standardowa, spektrogram log-Mel + szkielet audio Q-former)
**Wymagania wstępne:** Faza 6 (mowa i dźwięk), Faza 12 · 03 (Q-Former)
**Czas:** ~180 minut

## Cele kształcenia

- Obliczanie spektrogramu log-Mel z surowego przebiegu audio: okienkowanie, FFT, banki filtrów Mel oraz transformacja logarytmiczna.
- Porównanie enkoderów: Whisper, BEATs oraz hybrydowego AF-Whisper (wskazanie optymalnych scenariuszy dla każdego z nich).
- Implementacja modułu Audio Q-former: mapowanie spektrogramu na N wyuczonych zapytań (queries).
- Wyjaśnienie różnic między podejściem kaskadowym (Whisper + LLM) a w pełni zintegrowanym (end-to-end Audio-LLM) i uzasadnienie wyższości tego drugiego w złożonych zadaniach rozumowania.

## Problem

Dzięki modelowi Whisper automatyczne rozpoznawanie mowy (ASR) oraz transkrypcja („OCR dla dźwięku”) stały się powszechną technologią. Jednak na samej transkrypcji możliwości systemów kaskadowych się kończą. Jeśli model nie potrafi zrozumieć kontekstu akustycznego – czasu trwania zdarzeń, tożsamości mówców, ich emocji, struktury muzycznej czy dźwięków otoczenia – sama zamiana mowy na tekst nie wystarczy do zbudowania inteligentnego produktu.

Istnieją trzy główne podejścia:

1. **Podejście kaskadowe:** Whisper wykonuje transkrypcję mowy na tekst, a następnie model LLM analizuje ten tekst. Sprawdza się to w przypadku czystej wypowiedzi słownej, ale kompletnie zawodzi przy analizie muzyki, dźwięków tła, nakładających się głosów czy emocji mówcy.
2. **Zintegrowany model Audio-LLM (end-to-end):** Enkoder audio przekazuje tokeny dźwiękowe bezpośrednio do LLM, całkowicie omijając pośredni etap tekstowy. Pozwala to na pełne zachowanie informacji akustycznych (emocje, tożsamość mówcy, tło), ale wymaga dedykowanych danych szkoleniowych.
3. **Podejście hybrydowe:** Enkoder audio zintegrowany z dekoderem tekstowym, który potrafi zarówno generować transkrypcję, jak i prowadzić wnioskowanie. Tę drogę wybrały modele takie jak Qwen-Audio oraz Audio Flamingo.

## Koncepcja

### Spektrogram Log-Mel jako cecha wejściowa

Przetwarzanie w każdym enkoderze audio rozpoczyna się od wyliczenia spektrogramu log-Mel:

1. Resampling sygnału do częstotliwości 16 kHz.
2. Obliczenie krótkoczasowej transformaty Fouriera (STFT) przy długości okna 25 ms i kroku (hop size) 10 ms.
3. Wyznaczenie modułu (amplitudy) wyniku FFT.
4. Zastosowanie banku filtrów w skali Mel (najczęściej 80 filtrów w przedziale 0–8000 Hz) w celu odwzorowania nieliniowej percepcji ludzkiego ucha.
5. Logarytmowanie wartości (np. `log(1 + x)`) w celu skomprymowania zakresu dynamicznego.

Wynik: Dwuwymiarowa tablica o kształcie `(T, 80)`, gdzie `T` to liczba ramek czasowych. Dla 30-sekundowego nagrania przy kroku 10 ms (częstotliwość 100 Hz) daje to macierz o wymiarach `(3000, 80)`.

### Enkoder Whisper (Whisper Encoder)

Enkoder Whisper to 12-warstwowy transformator przetwarzający spektrogram log-Mel jako sekwencję klatek czasowych. Na wyjściu generuje po jednym ukrytym wektorze reprezentacji (hidden state) dla każdej klatki czasowej.

W klasycznych systemach ASR dekoder Whisper jest transformatorem powiązanym atencją krzyżową (cross-attention) z wyjściem enkodera, generującym tokeny tekstowe. Jest to standardowy układ koder-dekoder.

W modelach klasy Audio-LLM (ALM) wyjście enkodera Whisper służy jako dane wejściowe dla innego, większego modelu LLM. Typowy wzorzec implementacji to: zamrożony enkoder Whisper → trenowany adapter typu Q-former → zamrożony lub strojony model LLM.

### Enkoder BEATs i detektory zdarzeń akustycznych

Model Whisper był trenowany głównie na nagraniach mowy, dlatego radzi sobie słabiej z analizą muzyki czy ogólnych dźwięków tła.

Model BEATs (Chen i in., 2022) to transformator trenowany w sposób samonadzorowany (self-supervised) na zbiorze AudioSet. Pozwala on znacznie lepiej wychwytywać charakterystykę muzyczną oraz odgłosy otoczenia niż Whisper przy zachowaniu podobnej liczby parametrów.

AF-Whisper (hybrydowy moduł w Audio Flamingo 3) łączy reprezentacje (konkatenacja) z enkodera Whisper oraz BEATs. Whisper dostarcza informacji o warstwie językowej (semantyka mowy), natomiast BEATs odpowiada za cechy akustyczne i tło.

### Audio Q-Former

Działa analogicznie do wizualnego modułu Q-former znanego z BLIP-2. Stała liczba możliwych do nauczenia się zapytań (queries, najczęściej 32 lub 64) przetwarza za pomocą atencji krzyżowej ramki wyjściowe z enkodera audio. Wynikowe reprezentacje stanowią bezpośrednie tokeny wejściowe dla LLM.

Proces szkolenia adaptera Q-former składa się z etapu dopasowania (szkolenie atencją kontrastową oraz generowaniem opisów na parach audio-tekst, np. AudioCaps, Clotho) oraz etapu strojenia instrukcyjnego (SFT), gdzie odmraża się model LLM i uczy cały system kompleksowo na instrukcjach głosowych.

### Ewolucja modeli: SALMONN, Qwen-Audio, Audio Flamingo 3

- **SALMONN** (Tang i in., 2023): Łączy enkodery Whisper + BEATs + Q-former + LLaMA. Jest to jeden z pierwszych otwartych modeli Audio-LLM o dużych zdolnościach wnioskowania. Wynik w benchmarku MMAU wynosi ok. 0,55.
- **Qwen-Audio** (Chu i in., 2023): Podobna architektura, wyszkolona na bogatszym zbiorze danych i dostosowana do wieloturowych konwersacji głosowych. Wynik MMAU wynosi ok. 0,60.
- **LTU — Listen, Think, Understand** (Gong i in., 2023): Skupia się na danych dedykowanych do wnioskowania i wdraża łańcuch myśli (Chain of Thought) dla klipów dźwiękowych. Model mniejszy, lecz wysoce wyspecjalizowany.
- **Audio Flamingo 3** (Goel i in., lipiec 2025): Aktualny stan techniki (SOTA) wśród modeli otwartych. Wykorzystuje LLM o skali 8B (Qwen2 7B), połączone enkodery Whisper + BEATs oraz Q-former z 64 zapytaniami. Model był trenowany na ponad 1 milionie instrukcji audio-tekstowych. Wynik MMAU to aż 0,72, co w wielu podzadaniach dorównuje modelom komercyjnym.

AF3 wprowadza także mechanizm „myślenia na żądanie” (on-demand thinking) dla audio: model może wygenerować tokeny pomocnicze (np. `najpierw pozwól mi zidentyfikować instrumenty: ...`) przed podaniem ostatecznej odpowiedzi. Aktywacja tego trybu podnosi dokładność w trudnych zadaniach o 3–5 punktów procentowych.

### Podejście kaskadowe vs zintegrowane (end-to-end)

W systemie kaskadowym:
1. Whisper transkrybuje dźwięk na tekst.
2. LLM analizuje wynikowy tekst.

Podejście to sprawdza się wyśmienicie w zadaniach typu „streść ten podcast”. Zawodzi jednak całkowicie w pytaniach:
- „Jaki jest nastrój tego utworu muzycznego?” – nastrój tkwi w brzmieniu, a nie w tekście.
- „Kto teraz mówi, Alicja czy Bob?” – wymaga to analizy tożsamości głosowej (speaker ID).
- „W której sekundzie następuje wybuch?” – w tekście zatracona zostaje precyzyjna informacja czasowa.
- „Czy ten głos to deepfake?” – detekcja anomalii syntetycznych wymaga analizy cech akustycznych.

Zintegrowany model (end-to-end) zachowuje pełną informację akustyczną. Zarówno Qwen-Audio, jak i AF3 natywnie wspierają analizę muzyki, tła dźwiękowego oraz emocji.

### Rekomendacja produkcyjna na rok 2026

Projektując nowy system do analizy audio:
- Wybierz **podejście kaskadowe**, jeśli kluczowa jest wyłącznie transkrypcja tekstu, a system nie musi interpretować muzyki ani emocji. Jest to tańsze i prostsze wdrożeniowo rozwiązanie.
- Wybierz **rodzinę AF3 / Qwen-Audio**, jeśli produkt wymaga interpretacji muzyki, emocji, detekcji wielu mówców lub zaawansowanego wnioskowania o dźwiękach otoczenia.

### Benchmark MMAU (Massive Multimodal Audio Understanding)

Benchmark MMAU to standard ewaluacyjny w latach 2024–2025:
- Zawiera 10 000 par testowych audio-tekst obejmujących mowę, muzykę i dźwięki tła.
- Ocenia klasyfikację, rozumowanie czasowe i przyczynowo-skutkowe.
- Bada aspekty, które są systematycznie pomijane w systemach kaskadowych.

Najlepszy model otwarty (AF3) osiąga w nim wynik 0,72, podczas gdy modele komercyjne (Gemini 2.5 Pro, Claude 4.7) plasują się na poziomie ~0,78. Ta niewielka różnica pokazuje dynamiczny rozwój otwartych technologii Audio-LLM.

## Zastosowanie w kodzie

Plik `code/main.py` zawiera:
- Standardową implementację obliczania spektrogramu log-Mel (okienkowanie, DFT, bank filtrów Mel).
- Szkielet adaptera Audio Q-former: przyjmuje wyjście z enkodera i za pomocą atencji generuje N tokenów wejściowych dla LLM.
- Symulację porównawczą działania potoku kaskadowego oraz modelu end-to-end w przykładowym zadaniu.

## Rezultat

Do tej lekcji dołączono dokument `outputs/skill-audio-llm-pipeline-picker.md`. Ułatwia on wybór między podejściem kaskadowym, modelem end-to-end (klasy AF3) a architekturą hybrydową na podstawie specyfikacji zadania (transkrypcja, tagowanie muzyki, interpretacja emocji, diaryzacja, klasyfikacja tła).

## Ćwiczenia

1. Oblicz wymiary spektrogramu log-Mel dla 30-sekundowego klipu przy częstotliwości 16 kHz, szerokości okna 25 ms, kroku 10 ms i 80 filtrach Mel. Jak zmienią się te wymiary, jeśli zmienimy częstotliwość próbkowania na 48 kHz?
2. Dlaczego Whisper radzi sobie gorzej z analizą muzyki? Jakie cechy dźwięku potrafi wychwycić model BEATs, których brakuje w reprezentacji Whisper?
3. Porównaj działanie Audio Q-former z 32 oraz 64 zapytaniami. W jakiego typu zadaniach większa liczba zapytań (64) przyniesie wymierną korzyść, a kiedy lepiej pozostać przy 32, oszczędzając zasoby obliczeniowe?
4. Przeczytaj sekcję 4 pracy o AF3 poświęconą myśleniu na żądanie (on-demand thinking). Zaproponuj trzy konkretne zadania audio, w których zastosowanie łańcucha myśli przyniesie największy zysk jakościowy.
5. Zaproponuj uproszczony schemat diaryzacji (speaker diarization) z użyciem wyjścia z modelu AF3. W jaki sposób model powinien sygnalizować zmianę mówców?

## Kluczowe pojęcia

| Termin | Potoczne określenie | Co to dokładnie oznacza |
| :--- | :--- | :--- |
| **Spektrogram Log-Mel** | „Cechy Mela” | Dwuwymiarowa macierz (reprezentująca czas i częstotliwość) logarytmicznych wartości energii dźwięku przefiltrowanych w skali Mel. |
| **Audio Q-Former** | „Adapter audio” | Moduł agregujący czasowe ramki z enkodera audio do stałej liczby tokenów wejściowych (zapytań) dla modelu LLM. |
| **Podejście kaskadowe** | „ASR + LLM” | Dwuetapowy potok: najpierw Whisper generuje tekst, a następnie model LLM przetwarza ten tekst; traci informacje akustyczne. |
| **End-to-End Audio-LLM** | „Zintegrowany model audio” | Architektura, w której cechy akustyczne trafiają bezpośrednio do LLM poprzez adapter, bez pośrednictwa transkrypcji tekstowej. |
| **BEATs** | „Enkoder AudioSet” | Model samonadzorowany trenowany na zbiorze AudioSet, wykazujący wysoką skuteczność w analizie muzyki i odgłosów tła. |
| **MMAU** | „Benchmark audio” | Zbiór 10 000 wymagających zadań testowych z zakresu rozumienia mowy, muzyki i tła akustycznego. |
| **Myślenie na żądanie** | „Audio CoT” | Opcjonalny proces generowania przez model kroków pośrednich (rozumowania) przed sformułowaniem ostatecznej odpowiedzi tekstowej. |

## Literatura uzupełniająca

- [Radford i in. — Whisper (arXiv:2212.04356)](https://arxiv.org/abs/2212.04356)
- [Chu i in. — Qwen-Audio (arXiv:2311.07919)](https://arxiv.org/abs/2311.07919)
- [Goel i in. — Audio Flamingo 3 (arXiv:2507.08128)](https://arxiv.org/abs/2507.08128)
- [Tang i in. — SALMONN (arXiv:2310.13289)](https://arxiv.org/abs/2310.13289)
- [Gong i in. — LTU (arXiv:2305.10790)](https://arxiv.org/abs/2305.10790)
