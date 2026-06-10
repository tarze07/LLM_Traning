# Modele audio-językowe: Szept do Audio Flamingo 3 Arc

> Whisper (Radford i in., grudzień 2022 r.) ustalił rozpoznawanie mowy — 680 tys. godzin słabo nadzorowanej wielojęzycznej mowy, prosty transformator kodera-dekodera, punkt odniesienia, który sprawił, że powoływano się na to w każdej kolejnej wersji ASR. Ale uznanie to nie rozumowanie. Pytanie „jakie instrumenty są w tym nagraniu” lub „jakie emocje wyraża mówca” lub „co wydarzyło się w 3. minucie” wymaga zrozumienia dźwięku, a nie transkrypcji. Qwen-Audio, SALMONN, LTU i NVIDIA Audio Flamingo 3 (AF3, lipiec 2025) stopniowo budowały ten stos: zachowaj kodery klasy Whisper, wykorzystaj Q-formery, trenuj na danych instrukcji audio-tekstowych, dodaj rozumowanie oparte na łańcuchu myślowym. Ta lekcja podąża łukiem.

**Typ:** Kompilacja
**Języki:** Python (stdlib, spektrogram log-Mel + szkielet audio Q-former)
**Wymagania wstępne:** Faza 6 (mowa i dźwięk), faza 12 · 03 (Q-Former)
**Czas:** ~180 minut

## Cele nauczania

- Oblicz spektrogram log-Mel z przebiegu: okienkowanie, FFT, banki filtrów, transformacja logarytmiczna.
- Porównaj opcje koderów: koder Whisper, BEAT, hybryda AF-Whisper. Kiedy każdy wygrywa.
- Zbuduj Q-former audio: N zapytań, które można się nauczyć, uwzględniających poprawki spektrogramu.
- Wyjaśnij szkolenie kaskadowe (Whisper-then-LLM) w porównaniu z kompleksowym szkoleniem audio-LLM: dlaczego kompleksowe szkolenie lepiej skaluje się w zakresie rozumowania.

## Problem

Rozpoznawanie mowy zostało rozwiązane przez firmę Whisper. OCR-of-audio jest towarem. Ale „towar” kończy się na transkrypcji. Jeśli model nie jest w stanie zrozumieć tego, co usłyszał – czasu, głośników, emocji, struktury muzycznej, dźwięków otoczenia – sama transkrypcja nie jest w stanie wpłynąć na cechy produktu.

Trzy oczywiste trasy:

1. Kaskada: Whisper dokonuje transkrypcji, LLM uzasadnia transkrypcję. Działa w scenariuszach wykorzystujących czystą mowę. Zawodzi w przypadku muzyki, dźwięku otoczenia, nakładania się wielu głośników i emocji.

2. Kompleksowe LLM audio: koder audio dostarcza tokeny audio bezpośrednio do LLM, pomijając transkrypcję. Zachowuje informacje akustyczne (emocje, głośnik, środowisko). Potrzebuje nowych danych treningowych.

3. Hybrydowy: koder audio + dekoder tekstu, który może zarówno transkrybować, jak i rozumować. Qwen-Audio i Audio Flamingo wybierają tę drogę.

## Koncepcja

### Spektrogram Log-Mel: funkcja wejściowa

Każdy koder audio zaczyna się od tej samej funkcji: spektrogramu log-Mel.

1. Próbkuj ponownie do 16 kHz.
2. Krótkoczasowa transformata Fouriera z oknami 25 ms, przeskokiem 10 ms.
3. Zmierz wielkość wyniku FFT.
4. Zastosuj banki filtrów Mel (zwykle 80 filtrów w odstępach logarytmicznych 0-8000 Hz), aby wypaczyć częstotliwość percepcyjną.
5. Kompresja logu (log(1 + x)) dla zakresu dynamicznego.

Wynik: dwuwymiarowa tablica kształtów (T, 80), gdzie T jest liczbą ramek czasowych. Dla 30-sekundowego klipu przy częstotliwości odświeżania 100 Hz: (3000, 80).

### Koder szeptu

Koder Whispera to 12-warstwowy transformator typu ViT przetwarzający spektrogram log-Mel jako sekwencję ramek czasowych. Dane wyjściowe: jeden wektor stanu ukrytego na ramkę czasową.

W przypadku ASR dekoder Whispera jest transformatorem krzyżowym, który generuje tokeny tekstowe uzależnione od sygnału wyjściowego kodera. Standardowy koder-dekoder.

W przypadku ALM (audio-LLM) chcesz, aby sygnał wyjściowy kodera był wejściem do innego LLM. Wzór: koder Whisper zamrożony, Q-former możliwy do wyszkolenia, LLM zamrożony lub dostrojony.

### BEAT-y i kodery specyficzne dla dźwięku

Szept został przeszkolony na danych dotyczących dominującej mowy. Jest słabszy w przypadku muzyki i dźwięku otoczenia.

BEATs (Chen i in., 2022) to samonadzorowany transformator przeszkolony w programie AudioSet. Przechwytuje muzykę i dźwięki otoczenia lepiej niż Whisper przy tej samej liczbie parametrów.

AF-Whisper (hybryda Audio Flamingo 3): funkcja concat Whisper + BEATs jako wejście audio. Szept niesie sygnał językowy, BEATs niesie sygnał akustyczny.

### Audio Q-Form

Ten sam wzór, co wizualny Q-former BLIP-2. Stała liczba możliwych do nauczenia się zapytań (często 32 lub 64) jest przesyłana krzyżowo przez ramki wyjściowe kodera audio. Zapytania stają się tokenami audio używanymi przez LLM.

Etap dostosowania szkolenia: sam Q-former, kontrastowo + straty w napisach w parach audio-tekst (AudioCaps, Clotho). Etap instrukcji: od końca do końca, odmrożenie LLM, trenowanie na danych instrukcji.

### Łuk — SALMONN, Qwen-Audio, AF3

SALMONN (Tang i in., 2023): Szept + BEATs + Q-former + LLaMA. Pierwszy otwarty audio-LLM z poważną zdolnością rozumowania. Testy porównawcze na MMAU pokazują kompozyt ~ 0,55.

Qwen-Audio (Chu et al., 2023): podobna architektura, wyszkolona na bogatszym zbiorze danych, dostrojona do wieloobrotowego dialogu. MMAU ~0,60.

LTU — Listen, Think, Understand (Gong i in., 2023): wyraźne dane dotyczące rozumowania, skupienie się na łańcuchu myślowym w klipach audio. Mniejszy, ale bardziej skupiony.

Audio Flamingo 3 (Goel et al., lipiec 2025): aktualna otwarta SOTA. Szkielet 8B LLM (Qwen2 7B), duży koder Whisper concat BEAT, moduł Q-former z 64 zapytaniami, trening na ponad 1 milionie par instrukcji audio-tekstowych. MMAU 0,72, odpowiada zastrzeżonej granicy w niektórych podzadaniach.

AF3 wprowadza także łańcuch myślowy na żądanie dotyczący dźwięku: model może opcjonalnie emitować żetony myślenia („najpierw pozwól mi zidentyfikować instrumenty:…”) przed ostateczną odpowiedzią. Dokładność w złożonych zadaniach związanych z rozumowaniem podnosi się o 3-5 punktów, gdy włączone jest myślenie.

### Kaskadowe a kompleksowe

Rurociąg kaskadowy:

1. Szept transkrybuje dźwięk → tekst.
2. Powody LLM dotyczące tekstu.

Doskonale sprawdza się w przypadku „podsumowania tego podcastu”. Nie powiodło się:
- „Jaki jest nastrój tej piosenki?” — nastrój tkwi w dźwięku, a nie w słowach.
- „Kto mówi, Alicja czy Bob?” — wymaga identyfikacji mówiącego.
- „W której sekundzie następuje eksplozja?” — tymczasowe uziemienie utracone w tekście.
- „Czy to jest dźwięk prawdziwy czy wygenerowany?” — wykrywanie deepfake'ów wymaga funkcji akustycznych.

Kompleksowo zachowuje sygnał akustyczny. Qwen-Audio i AF3 natywnie obsługują muzykę, środowisko i emocje.

### Przepis produkcyjny 2026

Nowy produkt rozumiejący dźwięk:

- Kaskadowo, jeśli: celem jest transkrypcja, brak muzyki, brak wnioskowania emocjonalnego.
- Rodzina AF3 / Qwen-Audio, jeśli: muzyka, emocje, obsługa wielu głośników lub złożone rozumowanie audio.

Kaskadowanie jest tańsze i prostsze. Rozwiązanie typu end-to-end ma większe możliwości.

### MMAU — punkt odniesienia w zakresie rozumowania audio

MMAU (Massive Multimodal Audio Understanding) to punkt odniesienia w zakresie rozumowania audio na lata 2024–2025:

- 10 000 par audio-tekstowych zapewniających kontrolę jakości mowy, muzyki i dźwięków otoczenia.
- Obejmuje klasyfikację, rozumowanie temporalne, rozumowanie przyczynowe, otwartą kontrolę jakości.
- Testuje, czego systematycznie brakuje w rurociągach kaskadowych.

Otwórz SOTA (AF3) przy 0,72; zastrzeżona granica ~0,78 (Gemini 2.5 Pro, Claude Opus 4.7). Różnica jest mniejsza niż delta otwarcia i zamknięcia VideoMME, co wskazuje na dojrzewanie audio-LLM.

## Użyj tego

`code/main.py`:

- Implementuje obliczenia spektrogramu log-Mel w stdlib: okienkowanie, naiwny DFT, bank filtrów Mel.
- Szkielet audio Q-former: podane ramki wyjściowe kodera, oblicz Q, K, V, uwagę i wyemituj N tokenów.
- Porównanie kaskadowe i kompleksowe w przypadku zadania związanego z zabawką.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-audio-llm-pipeline-picker.md`. Biorąc pod uwagę zadanie audio (transkrypcja, tagowanie muzyki, wnioskowanie o emocjach, diaryzacja wielu głośników, klasyfikacja środowiska), wybiera kaskadowy, kompleksowy AF3 lub hybrydowy.

## Ćwiczenia

1. Oblicz wymiar spektrogramu log-Mel dla 30-sekundowego klipu przy 16 kHz, oknie 25 ms, przeskoku 10 ms, 80 przedziałach Mel. Jak to się zmienia przy 48 kHz?

2. Dlaczego Whisper radzi sobie gorzej z muzyką? Jakie funkcje audio przechwytuje BEATs, a jakich nie Whisper?

3. Audio Q-former z 64 zapytaniami vs 32: przy jakiej złożoności zadania opłaca się 64? 32. Po co zapisywać obliczenia?

4. Przeczytaj AF3 Sekcję 4 dotyczącą myślenia na żądanie. Zaproponuj trzy zadania audio, w których łańcuch myślowy jest najbardziej pomocny.

5. Zaimplementuj potok minimalnej diaryzacji, korzystając z danych wyjściowych AF3. Jak sygnalizujesz zmianę głośników?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Spektrogram Log-Mel | „Funkcje Mela” | Tablica 2D (czas, częstotliwość) wartości logarytmicznej po bankach filtrów Mel |
| Audio Q-były | „Odbiornik dźwięku” | Wąskie gardło skupiające uwagę na wyjściu kodera audio do zapytań o stałej długości zasilających LLM |
| Kaskadowe | „ASR-wtedy-LLM” | Rurociąg, w którym Whisper dokonuje transkrypcji i tekst z uzasadnieniem LLM; traci informację akustyczną |
| Od końca do końca | „Audio-LLM” | Funkcje audio wprowadzane są do LLM bezpośrednio przez Q-former; zachowuje sygnał akustyczny |
| BITY | „Koder AudioSet” | Transformator SSL przeszkolony na AudioSet; mocny w muzyce + dźwiękach otoczenia |
| MMAU | „Ławka do rozumowania audio” | 10 tys. par kontroli jakości mowy, muzyki i środowiska; Standard ewaluacji 2024 |
| Myślenie na żądanie | „Audio CoT” | Model może opcjonalnie emitować żetony rozumowania przed ostateczną odpowiedzią, podnosi dokładność o 3-5 punktów |

## Dalsze czytanie

- [Radford i in. — Szept (arXiv:2212.04356)](https://arxiv.org/abs/2212.04356)
- [Chu i in. — Qwen-Audio (arXiv:2311.07919)](https://arxiv.org/abs/2311.07919)
- [Goel i in. — Audio Flamingo 3 (arXiv:2507.08128)](https://arxiv.org/abs/2507.08128)
- [Tang i in. — ŁOSOŚ (arXiv:2310.13289)](https://arxiv.org/abs/2310.13289)
- [Gong i in. — LTU (arXiv:2305.10790)](https://arxiv.org/abs/2305.10790)