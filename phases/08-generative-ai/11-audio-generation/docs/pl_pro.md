# Generowanie dźwięku

> Dźwięk to sygnał jednowymiarowy o częstotliwości 16–48 kHz. Pięciosekundowy klip zawiera 80–240 tysięcy próbek. Żaden transformator nie obsługuje bezpośrednio tak długiej sekwencji. Rozwiązanie stosowane przez wszystkie produkcyjne modele audio w 2026 roku jest identyczne: kodek neuronowy (Encodec, SoundStream, DAC) kompresuje dźwięk do dyskretnych tokenów z częstotliwością 50–75 Hz, a transformator lub model dyfuzyjny generuje te tokeny.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 02 (Funkcje audio), Faza 6 · 04 (ASR), Faza 8 · 06 (DDPM)
**Czas:** ~45 minut

## Problem

Trzy zadania generowania dźwięku:

1. **Zamiana tekstu na mowę.** Na podstawie podanego tekstu system tworzy mowę. Czysta mowa jest wąskopasmowa i cechuje się silną strukturą fonetyczną — dobrze modelowaną przez transformator operujący na tokenach. Przykłady: VALL-E (Microsoft), NaturalSpeech 3, ElevenLabs, OpenAI TTS.
2. **Generowanie muzyki.** Na podstawie podpowiedzi (tekst, melodia, sekwencja akordów, gatunek) system tworzy muzykę. Rozkład danych jest tu znacznie szerszy. Przykłady: MusicGen (Meta), Stable Audio 2.5, Suno v4, Udio, Riffusion.
3. **Efekty dźwiękowe i projektowanie dźwięku.** Na podstawie opisu system syntetyzuje dźwięki otoczenia lub efekty Foleya. Przykłady: AudioGen, AudioLDM 2, Stable Audio Open.

Wszystkie trzy podejścia opierają się na tym samym fundamencie: neuronowy kodek audio połączony z generatorem autoregresywnym opartym na tokenach lub modelem dyfuzyjnym.

## Koncepcja

![Generowanie dźwięku: tokeny kodeków + transformator lub dyfuzja](../assets/audio-generacja.svg)

### Neuronowe kodeki audio

Encodec (Meta, 2022), SoundStream (Google, 2021), Descript Audio Codec (DAC, 2023). Koder splotowy kompresuje przebieg fali do wektora dla każdego kroku czasowego. Rezydualny kwantyzator wektorowy (RVQ) przekształca każdy taki wektor w kaskadę K indeksów słownika kodowego. Dekoder odwraca ten proces. Dźwięk 24 kHz przy 2 kb/s, z 8 warstwami RVQ przy 75 Hz, daje 600 tokenów na sekundę.

```
waveform (16000 samples/sec)
    └─ encoder conv ─┐
                     ├─ RVQ layer 1 → indices at 75 Hz
                     ├─ RVQ layer 2 → indices at 75 Hz
                     ├─ ...
                     └─ RVQ layer 8
```

### Dwa paradygmaty generatywne

**Autoregresja tokenów.** Tokeny RVQ są spłaszczane do jednej sekwencji, którą przetwarza transformator dekodujący. MusicGen stosuje mechanizm „opóźnionego przetwarzania równoległego" — K strumieni słownika kodowego jest emitowanych jednocześnie z przesunięciem na strumień. VALL-E generuje tokeny mowy na podstawie tekstu wejściowego oraz trzymynutowej próbki głosu.

**Dyfuzja ukryta.** Tokeny kodeków są traktowane jako ciągłe reprezentacje ukryte albo modelowane za pomocą dyfuzji kategorycznej. Stable Audio 2.5 wykorzystuje dopasowywanie przepływu na ciągłych przestrzeniach ukrytych dźwięku. AudioLDM 2 stosuje dyfuzję po ścieżce: tekst → mel-spektrogram → dźwięk.

Tendencja na lata 2024–2026: dopasowywanie przepływu dominuje w dziedzinie muzyki (szybsze wnioskowanie, wyraźniejsze próbki), natomiast autoregresja tokenów utrzymuje przewagę w syntezie mowy — ze względu na naturalną przyczynowość i łatwość przesyłania strumieniowego.

## Krajobraz produkcyjny

| System | Zadanie | Architektura | Opóźnienie |
|------------|------|----------|--------|
| ElevenLabs V3 | TTS | Token-AR + wokoder neuronowy | Pierwszy token ~300 ms |
| OpenAI GPT-4o Audio | Mowa w trybie pełnego dupleksu | Kompleksowe multimodalne AR | ~200 ms |
| NaturalSpeech 3 | TTS | Dopasowywanie przepływu ukrytego | Brak przesyłania strumieniowego |
| Stable Audio 2.5 | Muzyka / efekty | DiT + dopasowywanie przepływu na ukrytych reprezentacjach | ~10 s dla klipu 1-minutowego |
| Suno v4 | Pełne utwory | Nieujawnione; podejrzewane token-AR | ~30 s na piosenkę |
| Udio v1.5 | Pełne utwory | Nieujawnione | ~30 s na piosenkę |
| MusicGen 3.3B | Muzyka | Token-AR na Encodec 32 kHz | W czasie rzeczywistym |
| AudioCraft 2 | Muzyka + efekty dźwiękowe | Dopasowywanie przepływu | ~5 s dla klipu 5-sekundowego |
| Riffusion v2 | Muzyka | Dyfuzja na spektrogramie | ~10 s |

## Zbuduj to

`code/main.py` symuluje podstawową ideę: trenuje mały transformator przewidujący kolejny token na syntetycznych sekwencjach „tokenów audio", wygenerowanych z dwóch różnych „stylów" (naprzemienne niskie i wysokie tokeny dla stylu A, monotoniczne narastanie dla stylu B). Model jest warunkowany stylem i próbką.

### Krok 1: syntetyczne tokeny audio

```python
def make_tokens(style, length, vocab_size, rng):
    if style == 0:  # "speech-like": alternating
        return [i % vocab_size for i in range(length)]
    # "music-like": ramp
    return [(i * 3) % vocab_size for i in range(length)]
```

### Krok 2: trenowanie małego predyktora tokenów

Predyktor w stylu bigramowym, warunkowany stylem. Kluczowy wzorzec: tokeny kodeków → trening z entropią krzyżową → próbkowanie autoregresywne.

### Krok 3: próbkowanie warunkowe

Na podstawie tokenu stylu i tokenu początkowego kolejny token jest losowany z przewidywanego rozkładu. Proces trwa przez 20–40 kroków.

## Pułapki

- **Jakość kodeka ogranicza jakość wyjścia.** Jeśli kodek nie odtwarza wiernie dźwięku, żaden generator tego nie nadrobi. Spośród otwartych rozwiązań DAC osiąga obecnie najlepsze wyniki.
- **Kumulacja błędów RVQ.** Każda warstwa RVQ modeluje resztę z poprzedniej. Błędy w warstwie 1 propagują się w górę. Próbkowanie z niską temperaturą na wyższych warstwach łagodzi ten problem.
- **Struktura muzyczna.** 30 sekund dźwięku to ponad 20 tysięcy tokenów przy 75 Hz. Stanowi to poważne wyzwanie dla transformatorów. MusicGen stosuje przesuwane okno z szybkim kontynuowaniem; Stable Audio operuje na krótszych klipach z przenikaniem.
- **Artefakty na granicach klipów.** Łączenie wygenerowanych fragmentów wymaga ostrożnego nakładania z przenikaniem.
- **Zapotrzebowanie na czyste dane.** Generatory muzyki wymagają dziesiątek tysięcy godzin licencjonowanej muzyki. Pozew RIAA przeciwko Suno i Udio (2024) wyraźnie to uwidocznił.
- **Etyka klonowania głosu.** Trzymynutowa próbka połączona z tekstem wystarczy, by VALL-E, XTTS lub ElevenLabs sklonowały głos. Każdy produkcyjny model wymaga mechanizmów wykrywania nadużyć i list rezygnacji.

## Użyj tego

| Zadanie | Zalecany stos 2026 |
|------|------------|
| Komercyjny TTS | ElevenLabs, OpenAI TTS lub Azure Neural |
| Klonowanie głosu (za zgodą) | XTTS v2 (otwarty) lub ElevenLabs Pro |
| Szybka muzyka w tle | Stable Audio 2.5 API, Suno lub Udio |
| Muzyka z tekstami | Suno v4 lub Udio v1.5 |
| Efekty dźwiękowe / Foley | AudioCraft 2, ElevenLabs SFX lub Stable Audio Open |
| Agent głosowy w czasie rzeczywistym | GPT-4o Realtime lub Gemini Live |
| Badania muzyczne z otwartymi wagami | MusicGen 3.3B, Stable Audio Open 1.0, AudioLDM 2 |
| Dubbing / tłumaczenie | HeyGen, ElevenLabs Dubbing |

## Wyślij to

Zapisz `outputs/skill-audio-brief.md`. Dokument powinien zawierać krótki opis zadania audio (zadanie, czas trwania, styl, głos, licencja) oraz wyniki: model i hosting, format podpowiedzi (tagi gatunku, deskryptory stylu, znaczniki strukturalne), łańcuch kodek → generator → wokoder, protokół inicjalizacji oraz plan ewaluacji (wynik MOS / CLAP / CER dla TTS / testy A/B z użytkownikami).

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py` i jawnie ustaw styl. Sprawdź, czy wygenerowane sekwencje odpowiadają wzorcowi danego stylu.
2. **Średnie.** Dodaj opóźnione dekodowanie równoległe: zasymuluj 2 strumienie tokenów przesunięte o 1 krok względem siebie. Wytrenuj wspólny predyktor.
3. **Trudne.** Użyj biblioteki Transformers z HuggingFace, aby lokalnie uruchomić MusicGen-small. Wygeneruj 10-sekundowy klip na podstawie trzech różnych podpowiedzi i przeprowadź test A/B pod kątem zgodności ze stylem.

## Kluczowe terminy

| Termin | Potoczne określenie | Właściwe znaczenie |
|------|-----------------|----------------------|
| Kodek | „Kompresja neuronowa" | Koder-dekoder audio; typowe wyjście to tokeny 50–75 Hz. |
| RVQ | „Residual VQ" | Kaskada K kwantyzatorów; każdy modeluje resztę z poprzedniego. |
| Token | „Jeden symbol kodeka" | Dyskretny indeks w słowniku kodowym; typowo 1024 lub 2048 wpisów. |
| Opóźnione przetwarzanie równoległe | „Przesunięte słowniki kodowe" | Emisja K strumieni tokenów z wzajemnymi przesunięciami, redukująca długość sekwencji. |
| Dopasowywanie przepływu | „Zwycięzca audio 2024" | Uproszczona alternatywa dla dyfuzji; zapewnia szybsze próbkowanie. |
| Próbka głosowa | „Trzymynutowa próbka" | Osadzenie głośnika lub prefiks tokena sterujący sklonowanym głosem. |
| Mel-spektrogram | „Wizualizacja dźwięku" | Logarytmiczny spektrogram percepcyjny; stosowany przez wiele systemów TTS. |
| Wokoder | „Konwerter mel" | Neuronowy komponent przekształcający mel-spektrogramy z powrotem na przebieg fali. |

## Uwaga produkcyjna: dźwięk a problem przesyłania strumieniowego

Dźwięk jest jedynym rodzajem wyjścia, którego użytkownicy oczekują *w trakcie generowania*, a nie po jego zakończeniu. Z perspektywy produkcyjnej oznacza to, że kluczowym wskaźnikiem jest TPOT (czas na wyjściowy token) — prędkość słuchania użytkownika wyznacza wymaganą przepustowość, nie prędkość odczytu. Dla dźwięku 16 kHz tokenizowanego z częstotliwością ~75 tokenów/sekundę serwer musi generować co najmniej 75 tokenów/s na użytkownika, aby zapewnić płynne odtwarzanie.

Dwie konsekwencje architektoniczne:

- **Modele oparte na dopasowywaniu przepływu nie obsługują przesyłania strumieniowego w prosty sposób.** Stable Audio 2.5 i AudioCraft 2 renderują klip o stałej długości w jednym przebiegu. Przesyłanie strumieniowe wymaga podziału klipu i nakładania fragmentów na granicach — mechanizm przypominający dyfuzję w przesuwanym oknie — co dodaje 100–300 ms narzutu w porównaniu z modelem AR opartym na kodeku.

Jeśli produktem jest „czat głosowy na żywo" lub „kontynuacja muzyki w czasie rzeczywistym", właściwą ścieżką jest autoregresja tokenów kodeków. Jeśli zadanie polega na „wyrenderowaniu 30-sekundowego klipu po przesłaniu żądania", dopasowywanie przepływu wygrywa pod względem jakości i całkowitego opóźnienia.

## Dalsze czytanie

- [Défossez i in. (2022). Encodec: High Fidelity Neural Audio Compression](https://arxiv.org/abs/2210.13438) — standard kodeka.
- [Zeghidur i in. (2021). SoundStream](https://arxiv.org/abs/2107.03312) — pierwszy szeroko stosowany neuronowy kodek audio.
- [Kumar i in. (2023). Kompresja dźwięku o wysokiej wierności z ulepszonym RVQGAN (DAC)](https://arxiv.org/abs/2306.06546) — DAC.
- [Wang i in. (2023). Modele języka kodeków neuronowych to syntezatory tekstu na mowę typu zero-shot (VALL-E)](https://arxiv.org/abs/2301.02111) — VALL-E.
- [Copet i in. (2023). Proste i kontrolowane generowanie muzyki (MusicGen)](https://arxiv.org/abs/2306.05284) — MusicGen.
- [Liu i in. (2023). AudioLDM 2: Nauka holistycznego generowania dźwięku dzięki samouczącemu wstępnemu treningowi](https://arxiv.org/abs/2308.05734) — AudioLDM 2.
- [Stability AI (2024). Stable Audio 2.5](https://stability.ai/news/introducing-stable-audio-2-5) — zamiana tekstu na muzykę z dopasowywaniem przepływu, stan na 2025 rok.
