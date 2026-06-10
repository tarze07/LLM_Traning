# Generowanie dźwięku

> Dźwięk to sygnał 1-D o częstotliwości 16–48 kHz. Pięciosekundowy klip to 80-240 tys. próbek. Żaden transformator nie obsługuje bezpośrednio tej sekwencji. Rozwiązanie dla każdego produkcyjnego modelu audio w roku 2026 jest takie samo: kodek neuronowy (Encodec, SoundStream, DAC) kompresuje dźwięk do dyskretnych tokenów przy częstotliwości 50–75 Hz, a transformator lub model dyfuzyjny generuje tokeny.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 02 (Funkcje audio), Faza 6 · 04 (ASR), Faza 8 · 06 (DDPM)
**Czas:** ~45 minut

## Problem

Trzy zadania generowania dźwięku:

1. **Zamiana tekstu na mowę.** Po podanym tekście utwórz mowę. Czysta mowa jest wąskopasmowa i ma silną strukturę fonetyczną – dobrze rozwiązaną za pomocą transformatora na tokenach. VALL-E (Microsoft), NaturalSpeech 3, ElevenLabs, OpenAI TTS.
2. **Generowanie muzyki.** Po otrzymaniu podpowiedzi (tekst, melodia, sekwencja akordów, gatunek) utwórz muzykę. Znacznie szersza dystrybucja. MusicGen (Meta), Stable Audio 2.5, Suno v4, Udio, Riffusion.
3. **Efekty dźwiękowe/projekt dźwięku.** Po wyświetleniu monitu wytwórz dźwięk otoczenia lub Foleya. AudioGen, AudioLDM 2, stabilne audio otwarte.

Wszystkie trzy działają na tym samym podłożu: neuronowy kodek audio + token-AR lub generator dyfuzyjny.

## Koncepcja

![Generowanie dźwięku: tokeny kodeków + transformator lub dyfuzja](../assets/audio-generacja.svg)

### Neuronowe kodeki audio

Encodec (Meta, 2022), SoundStream (Google, 2021), Descript Audio Codec (DAC, 2023). Koder splotowy kompresuje przebieg do wektora kroku czasowego; Kwantyzacja wektorów resztkowych (RVQ) przekształca każdy wektor w kaskadę K indeksów książki kodowej. Dekoder odwraca to. Dźwięk 24 kHz przy 2 kb/s przy użyciu 8 książek kodowych RVQ przy 75 Hz = 600 tokenów/s.

```
waveform (16000 samples/sec)
    └─ encoder conv ─┐
                     ├─ RVQ layer 1 → indices at 75 Hz
                     ├─ RVQ layer 2 → indices at 75 Hz
                     ├─ ...
                     └─ RVQ layer 8
```

### Dwa paradygmaty generatywne na górze

**Autoregresja tokenu.** Spłaszcz tokeny RVQ w sekwencję, uruchom transformator przeznaczony wyłącznie do dekodera. MusicGen wykorzystuje „opóźnione równoległe” do emisji K strumieni książki kodowej równolegle z przesunięciami na strumień. VALL-E generuje tokeny mowy na podstawie komunikatu tekstowego + 3-sekundowej próbki głosu.

**Rozpowszechnianie ukryte.** Pakuj tokeny kodeków jako ciągłe ukryte lub modeluj je za pomocą dyfuzji kategorycznej. Stable Audio 2.5 wykorzystuje dopasowanie przepływu do ciągłych utajonych dźwięków. AudioLDM 2 wykorzystuje dyfuzję tekstu na mel na audio.

Trend na lata 2024–2026: dopasowywanie przepływu wygrywa w przypadku muzyki (szybsze wnioskowanie, czystsze próbki), podczas gdy token-AR nadal dominuje w mowie, ponieważ jest naturalnie przyczynowy i dobrze przesyła strumieniowo.

## Krajobraz produkcyjny

| Systemu | Zadanie | Kręgosłup | Opóźnienie |
|------------|------|----------|--------|
| ElevenLabs V3 | TTS | Token-AR + wokoder neuronowy | Pierwszy token ~300ms |
| Dźwięk OpenAI GPT-4o | Mowa w trybie pełnego dupleksu | Kompleksowe multimodalne AR | ~200 ms |
| Naturalna Mowa 3 | TTS | Dopasowanie przepływu utajonego | Brak transmisji strumieniowej |
| Stabilny dźwięk 2.5 | Muzyka / Efekty | DiT + dopasowanie przepływu na utajonych dźwiękach | ~10 s dla 1-minutowego klipu |
| Suno v4 | Pełne utwory | nieujawnione; token-AR podejrzany | ~30 s na piosenkę |
| Udio v1.5 | Pełne utwory | Nieujawnione | ~30 s na piosenkę |
| MuzykaGen 3.3B | Muzyka | Token-AR na Encodec 32 kHz | W czasie rzeczywistym |
| AudioCraft 2 | Muzyka + efekty dźwiękowe | Dopasowanie przepływu | ~5s dla klipu 5s |
| Riffusion v2 | Muzyka | Dyfuzja spektrogramu | ~10 s |

## Zbuduj to

`code/main.py` symuluje podstawową ideę: uczenie małego transformatora następnego tokena na syntetycznych sekwencjach „tokenów audio” generowanych z dwóch różnych „stylów” (naprzemienne niskie i wysokie tokeny dla stylu A, monotoniczna rampa dla stylu B). Warunek dotyczący stylu i próbki.

### Krok 1: syntetyczne tokeny audio

```python
def make_tokens(style, length, vocab_size, rng):
    if style == 0:  # "speech-like": alternating
        return [i % vocab_size for i in range(length)]
    # "music-like": ramp
    return [(i * 3) % vocab_size for i in range(length)]
```

### Krok 2: naucz małego predyktora tokena

Predyktor w stylu bigramu uwarunkowany stylem. Chodzi o wzorzec: tokeny kodeków → trening między entropią → próbkowanie autoregresyjne.

### Krok 3: próbkuj warunkowo

Biorąc pod uwagę token stylu i token początkowy, wypróbuj następny token z przewidywanej dystrybucji. Kontynuuj przez 20-40 żetonów.

## Pułapki

- **Jakość kodeka ogranicza jakość wyjściową.** Jeśli kodek nie jest w stanie wiernie odtworzyć dźwięku, żadna jakość generatora nie pomoże. DAC jest aktualnie najlepszym otwartym rozwiązaniem.
- **Akumulacja błędów RVQ.** Każda warstwa RVQ modeluje resztę poprzedniej. Błędy w warstwie 1 propagują się. Pomaga pobieranie próbek w temperaturze 0 na wyższych warstwach.
- **Struktura muzyczna.** 30 sekund żetonów to ponad 20 tys. żetonów przy 75 Hz. Trudne dla transformatorów. MusicGen wykorzystuje przesuwane okno + szybką kontynuację; Stable Audio wykorzystuje krótsze klipy + przenikanie.
- **Artefakty na granicach.** Przenikanie pomiędzy wygenerowanymi klipami wymaga ostrożnego dodania nakładania się.
- **Apetyt na czyste dane.** Generatory muzyki potrzebują dziesiątek tysięcy godzin licencjonowanej muzyki. Pozew Suno / Udio RIAA (2024) ujawnił tę kwestię.
- **Etyka klonowania głosu.** 3-sekundowa próbka plus komunikat tekstowy wystarczy, aby VALL-E / XTTS / ElevenLabs sklonował głos. Każdy model produkcyjny wymaga wykrywania nadużyć + list rezygnacji.

## Użyj tego

| Zadanie | stos 2026 |
|------|------------|
| Komercyjny TTS | ElevenLabs, OpenAI TTS lub Azure Neural |
| Klonowanie głosu (potwierdzone zgodą) | XTTS v2 (otwarty) lub ElevenLabs Pro |
| Muzyka w tle, szybka | Stabilne API Audio 2.5, Suno lub Udio |
| Muzyka z tekstami | Suno v4 lub Udio v1.5 |
| Efekty dźwiękowe / Foley | AudioCraft 2, ElevenLabs SFX lub Stable Audio Open |
| Agent głosowy w czasie rzeczywistym | GPT-4o w czasie rzeczywistym lub Gemini Live |
| Badania muzyki z ciężarami otwartymi | MusicGen 3.3B, Stable Audio Open 1.0, AudioLDM 2 |
| Dubbing / tłumaczenie | Hej, Gen, dubbing ElevenLabs |

## Wyślij to

Zapisz `outputs/skill-audio-brief.md`. Umiejętność obejmuje krótki opis audio (zadanie, czas trwania, styl, głos, licencja) i wyniki: model + hosting, format podpowiedzi (tagi gatunku, deskryptory stylu, znaczniki strukturalne), kodek + generator + łańcuch wokodera, protokół początkowy i plan ewaluacji (wynik MOS / CLAP / CER dla TTS / użytkownik A/B).

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py` i jawnie ustaw styl. Sprawdź, czy wygenerowane sekwencje odpowiadają wzorcowi stylu.
2. **Średni.** Dodaj opóźnione dekodowanie równoległe: symuluj 2 strumienie tokenów, które muszą pozostać przesunięte o 1 krok. Wytrenuj wspólny predyktor.
3. **Trudne.** Użyj transformatorów HuggingFace, aby lokalnie uruchomić MusicGen-small. Wygeneruj 10-sekundowy klip z trzema różnymi podpowiedziami; A/B dla trzymania się stylu.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Kodek | „Kompresja neuronowa” | Koder/dekoder audio; typowe wyjście to żetony 50-75 Hz. |
| RVQ | „Resztkowe VQ” | Kaskada kwantyzatorów K; każdy modeluje resztę poprzedniego. |
| Znak | „Jeden symbol kodeka” | Dyskretny indeks do książki kodów; Typowo 1024 lub 2048. |
| Opóźnione równolegle | „Offsetowe książki kodowe” | Emituj K strumieni tokenów z przesuniętymi przesunięciami, aby zmniejszyć długość sekwencji. |
| Dopasowanie przepływu | „Zwycięstwo w dziedzinie audio w roku 2024” | Prostsza ścieżka, alternatywa dla dyfuzji; szybsze próbkowanie. |
| Komunikat głosowy | „3-sekundowa próbka” | Osadzanie głośnika lub prefiks tokena, który steruje sklonowanym głosem. |
| Spektrogram Mela | „Wizualność” | Spektrogram percepcyjny logarytmiczny; używany przez wiele systemów TTS. |
| Wokoder | „Mel machać” | Składnik neuronowy, który konwertuje spektrogramy mel z powrotem na dźwięk. |

## Uwaga produkcyjna: problem z dźwiękiem wynika z przesyłania strumieniowego

Dźwięk to jedyna metoda wyjściowa, której użytkownicy oczekują *w miarę jego generowania*, a nie wszystko na raz. Z punktu widzenia produkcyjnego oznacza to, że liczy się TPOT (czas na token wyjściowy), ponieważ prędkość słuchania użytkownika jest docelową przepustowością, a nie szybkością odczytu. W przypadku dźwięku 16 kHz tokenizowanego z szybkością ~75 tokenów/sekundę (kodek) serwer musi generować ≥75 tokenów/s na użytkownika, aby zapewnić płynne odtwarzanie.

Dwie konsekwencje architektoniczne:

- **Modele audio dopasowujące się do przepływu nie mogą przesyłać strumieniowo w trywialny sposób.** Stable Audio 2.5 i AudioCraft 2 renderują klip o stałej długości w jednym przebiegu. Aby przesyłać strumieniowo, dzielisz klip i nakładasz granice – pomyśl o dyfuzji w przesuwanym oknie – dodając 100–300 ms narzutu opóźnienia w porównaniu z modelem AR z kodekiem.

Jeśli produktem jest „czat głosowy na żywo” lub „kontynuacja muzyki w czasie rzeczywistym”, wybierz ścieżkę AR kodeka. Jeśli jest to „renderuj 30-sekundowy klip po przesłaniu”, dopasowanie przepływu wygrywa pod względem jakości i całkowitego opóźnienia.

## Dalsze czytanie

- [Défossez i in. (2022). Encodec: High Fidelity Neural Audio Compression](https://arxiv.org/abs/2210.13438) — standard kodeka.
- [Zeghidur i in. (2021). SoundStream](https://arxiv.org/abs/2107.03312) — pierwszy powszechnie używany neuronowy kodek audio.
- [Kumar i in. (2023). Kompresja dźwięku o wysokiej wierności z ulepszonym RVQGAN (DAC)](https://arxiv.org/abs/2306.06546) — DAC.
- [Wang i in. (2023). Modele języka kodeków neuronowych to syntezatory tekstu na mowę typu zero-shot (VALL-E)](https://arxiv.org/abs/2301.02111) — VALL-E.
- [Copet i in. (2023). Proste i kontrolowane generowanie muzyki (MusicGen)](https://arxiv.org/abs/2306.05284) — MusicGen.
- [Liu i in. (2023). AudioLDM 2: Nauka holistycznego generowania dźwięku dzięki samonadzorowanemu szkoleniu wstępnemu](https://arxiv.org/abs/2308.05734) — AudioLDM 2.
- [Stabilna sztuczna inteligencja (2024). Stable Audio 2.5](https://stability.ai/news/introducing-stable-audio-2-5) — zamiana tekstu na muzykę na rok 2025 z dopasowaniem przepływu.