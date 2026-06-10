# Generowanie muzyki — MusicGen, Stable Audio, Suno i licencjonowane trzęsienie ziemi

> Generacja muzyki 2026: w reklamach dominują Suno v5 i Udio v4; MusicGen, Stable Audio Open i ACE-Step są wiodącymi rozwiązaniami typu open source. Problem techniczny w większości rozwiązany. Problem prawny (ugoda Warner Music na 500 mln dolarów, ugoda z UMG) zmienił dziedzinę w latach 2025–2026.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 02 (spektrogramy), Faza 4 · 10 (modele dyfuzyjne)
**Czas:** ~75 minut

## Problem

Tekst → klip muzyczny trwający od 30 sekund do 4 minut, zawierający teksty, wokale i strukturę. Trzy podproblemy:

1. **Generacja instrumentalna.** Tekst typu „bębny hip-hopowe lo-fi z ciepłymi klawiszami” → audio. MusicGen, stabilny dźwięk, AudioLDM.
2. **Generacja piosenek (z wokalem i tekstem).** „Pieśń country o deszczowych nocach w Teksasie” → pełny utwór. Suno, Udio, YuE, krok ACE.
3. **Warunkowe / kontrolowane.** Rozszerz istniejący klip, zregeneruj most, zamień gatunek, oddziel łodygę lub zamaluj. Malowanie Udio + separacja pni to funkcja, którą warto dopasować w 2026 roku.

## Koncepcja

![Generowanie muzyki: token-LM vs dyfuzja, mapa modelu na rok 2026](../assets/music-generacja.svg)

### Token LM przez tokeny kodeków neuronowych

Meta **MusicGen** (2023, MIT) i wiele pochodnych: warunek osadzania tekstu/melodii, autoregresyjne przewidywanie tokenów EnCodec (32 kHz, 4 książki kodowe), dekodowanie za pomocą EnCodec. Parametry 300M - 3,3B. Silna linia bazowa; walczy przez 30 sekund.

**ACE-Step** (open source, 4B XL wydany w kwietniu 2026 r.) rozszerza tę funkcję o generowanie pełnych utworów z uwarunkowanymi tekstami. Otwarta społeczność jest najbliższa Suno.

### Dyfuzja przez mele lub utajone

**Stable Audio (2023)** i **Stable Audio Open (2024)**: utajone rozpowszechnianie skompresowanego dźwięku. Doskonale radzi sobie z pętlami, projektowaniem dźwięku i teksturami otoczenia. Niezbyt dobrze radzi sobie z pełnymi utworami o określonej strukturze.

**AudioLDM / AudioLDM2**: zamiana tekstu na dźwięk poprzez utajoną dyfuzję w stylu T2I, uogólniona na muzykę, efekty dźwiękowe i mowę.

### Hybrid (produkcja) — Suno, Udio, Lyria

Zamknięte ciężary. Prawdopodobnie kodek AR LM + wokoder oparty na dyfuzji ze specjalistycznymi naciągami głosowymi/perkusyjnymi/melodyjnymi. Suno v5 (2026) jest liderem jakości ELO 1293. Udio v4 dodaje malowanie + separację pnia (bas, perkusja, wokale można pobrać osobno).

### Ocena

- **FAD (Fréchet Audio Distance).** Odległość na poziomie osadzania pomiędzy wygenerowaną a rzeczywistą dystrybucją dźwięku przy użyciu funkcji VGGish lub PANNs. Niżej jest lepiej. MusicGen small: 4,5 FAD na MusicCaps; SOTA ~3.0.
- **Muzyczność (subiektywna).** Preferencje ludzkie. Przewody Suno v5 ELO 1293.
- **Wyrównanie tekstu i dźwięku.** Wynik CLAP pomiędzy komunikatem a komunikatem wyjściowym.
- **Artefakty muzykalności.** Przejścia poza rytmem, przesunięcie frazy wokalnej, utrata struktury w ciągu ostatnich 30 s.

## Mapa modelu 2026

| Modelka | Parametry | Długość | Wokal | Licencja |
|-------|--------|--------|--------|-------------|
| MuzykaGen-duży | 3.3B | 30 s | nie | MIT |
| Stabilne audio otwarte | 1.2B | 47 s | nie | Stabilność niekomercyjna |
| ACE-Step XL (kwiecień 2026 r.) | 4B | > 2 minuty | tak | Apache-2.0 |
| YuE | 7B | > 2 minuty | tak, wielojęzyczny | Apache-2.0 |
| Suno v5 (zamknięte) | ? | 4 minuty | tak, ELO 1293 | komercyjny |
| Udio v4 (zamknięte) | ? | 4 minuty | tak + łodygi | komercyjny |
| Google Lyria 3 (zamknięte) | ? | w czasie rzeczywistym | tak | komercyjny |
| MiniMax Muzyka 2.5 | ? | 4 minuty | tak | komercyjne API |

## Krajobraz prawny (2025–2026)

- **Ugoda Warner Music kontra Suno.** 500 mln dolarów. WMG sprawuje teraz nadzór nad podobieństwem do sztucznej inteligencji, prawami do muzyki i utworami tworzonymi przez użytkowników w Suno. Podobne rozliczenie UMG na Udio.
- **Ustawa UE o sztucznej inteligencji** + **California SB 942**: Muzykę wygenerowaną przez sztuczną inteligencję należy ujawniać.
- **Riffusion / MusicGen** w ramach MIT nie mają bagażu zgodności, ale nie mają też komercyjnych wokali.

Wzory bezpieczne do wysyłki:

1. Generuj tylko instrumenty (MusicGen, Stable Audio Open, wyjścia MIT/CC0).
2. Korzystaj z komercyjnych API (Suno, Udio, ElevenLabs Music) z licencją na generację.
3. Trenuj na własnym lub licencjonowanym katalogu (większość przedsiębiorstw trafia tutaj).
4. Generacje tagów ze znakami wodnymi + metadanymi.

## Zbuduj to

### Krok 1: wygeneruj za pomocą MusicGen

```python
from audiocraft.models import MusicGen
import torchaudio

model = MusicGen.get_pretrained("facebook/musicgen-small")
model.set_generation_params(duration=10)
wav = model.generate(["upbeat synthwave with driving drums, 128 BPM"])
torchaudio.save("out.wav", wav[0].cpu(), 32000)
```

Trzy rozmiary: `small` (300M, szybki), `medium` (1,5B), `large` (3,3B). Mały wystarczy, aby „pomysł się sprawdził”.

### Krok 2: warunkowanie melodii

```python
melody, sr = torchaudio.load("humming.wav")
wav = model.generate_with_chroma(
    ["jazz piano cover"],
    melody.squeeze(),
    sr,
)
```

MusicGen-melody pobiera chromatogram i zachowuje melodię podczas zmiany barwy. Przydatne w przypadku „daj mi tę melodię jako kwartet smyczkowy”.

### Krok 3: Ocena FAD

```python
from frechet_audio_distance import FrechetAudioDistance
fad = FrechetAudioDistance()

fad.get_fad_score("generated_folder/", "reference_folder/")
```

Oblicza odległość osadzania VGGish. Przydatne do testów regresji na poziomie gatunku; nie zastępuje ludzkich słuchaczy.

### Krok 4: dodanie do przepływu pracy z muzyką LLM

Połącz z pomysłami z lekcji 7-8:

```python
prompt = "Write a 30-second jazz loop. Describe the drums, bass, and piano voicing."
description = llm.complete(prompt)
music = musicgen.generate([description], duration=30)
```

## Użyj tego

| Cel | Stos |
|------|-------|
| Projekt dźwięku instrumentalnego | Stabilne audio otwarte |
| Gra / muzyka adaptacyjna | Google Lyria RealTime (zamknięte) |
| Pełne utwory z wokalami (reklama) | Suno v5 lub Udio v4 z wyraźną licencją |
| Pełne utwory z wokalami (otwarte) | ACE-Step XL lub YuE |
| Krótki dżingiel reklamowy | Melodia MusicGen uzależniona od nuconego odniesienia |
| Tło teledysku | MusicGen + stabilna dyfuzja wideo |

## Pułapki, które nadal będą widoczne w 2026 r

- **Monity dotyczące prania praw autorskich.** „Piosenka w stylu Taylor Swift” — komercyjne Suno/Udio filtruje je teraz, otwarte modele nie. Dodaj własną listę filtrów.
- **Powtórzenie / przesunięcie powyżej 30 s.** Pętla modeli AR. Przenikaj wiele generacji lub użyj ACE-Step dla spójności strukturalnej.
- **Odchylenie tempa.** Modele odbiegają od BPM. Użyj tagów BPM w wierszu zachęty i filtrze końcowym za pomocą `beat_track` librosy.
- **Zrozumiałość głosu.** Suno jest doskonała; modele otwarte często nie dobierają słów. Jeśli teksty mają znaczenie, użyj komercyjnego interfejsu API lub dostosuj go.
- **Wyjście mono.** Modele otwarte generują dźwięk mono lub fałszywe stereo. Uaktualnij za pomocą odpowiedniej rekonstrukcji stereo (ezst, dyfuzja stereo Cartesii).

## Wyślij to

Zapisz jako `outputs/skill-music-designer.md`. Wybierz model, strategię licencyjną, plan długości/struktury i metadane dotyczące ujawnienia na potrzeby wdrożenia generatora muzycznego.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Tworzy „generatywną” progresję akordów + wzór perkusyjny w postaci symboli ASCII — kreskówkową kreację muzyczną. Jeśli chcesz, odtwórz go za pomocą dowolnego modułu renderującego MIDI.
2. **Średni.** Zainstaluj `audiocraft`, wygeneruj 10-sekundowe klipy w 4 podpowiedziach gatunkowych za pomocą MusicGen-small, zmierz FAD w odniesieniu do zestawu gatunków referencyjnych.
3. **Trudne.** Używając ACE-Step (lub MusicGen-melody), wygeneruj trzy odmiany tej samej melodii z różnymi podpowiedziami barwy. Oblicz podobieństwo CLAP do podpowiedzi, aby sprawdzić wyrównanie.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| MODA | FID audio | Odległość Frécheta pomiędzy rozkładami osadzania rzeczywistego i generowanego. |
| Chromagram | Melodia jako dźwięki | wektor 12 przyciemnień na klatkę; wejście do warunkowania melodii. |
| Pędy | Ścieżki instrumentów | Oddzielny bas/perkusja/wokal/melodia w formacie WAV. |
| Malarstwo | Regeneruj sekcję | Maskuj okno czasowe; model właśnie to regeneruje. |
| KLIKNIJ | KLIP tekstowo-audio | Kontrastowe osadzanie tekstu audio; eval wyrównanie tekstu i dźwięku. |
| Kodek | Kodek muzyczny | Kodek neuronowy Meta używany przez MusicGen; 32 kHz, 4 książki kodowe. |

## Dalsze czytanie

- [Copet i in. (2023). MusicGen](https://arxiv.org/abs/2306.05284) — otwarty test autoregresyjny.
- [Evans i in. (2024). Stable Audio Open](https://arxiv.org/abs/2407.14358) — domyślne ustawienie dźwięku.
– [ACE-Step](https://github.com/ace-step/ACE-Step) — otwórz generator pełnych utworów 4B, kwiecień 2026 r.
- [Dokumentacja platformy Suno v5](https://suno.com) — komercyjny lider jakości.
- [AudioLDM2](https://arxiv.org/abs/2308.05734) — utajone rozpowszechnianie muzyki + efekty dźwiękowe.
– [Zawartość ugody WMG-Suno](https://www.musicbusinessworldwide.com/suno-warner-music-settlement/) – precedens z listopada 2025 r.