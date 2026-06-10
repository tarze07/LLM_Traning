# Generowanie muzyki — MusicGen, Stable Audio, Suno i licencyjne trzęsienie ziemi

> Generowanie muzyki w 2026 roku: w sektorze komercyjnym i reklamowym dominują platformy Suno v5 oraz Udio v4; w świecie rozwiązań otwartoźródłowych (open-source) czołowe miejsca zajmują MusicGen, Stable Audio Open oraz ACE-Step. O ile wyzwania technologiczne zostały w dużej mierze przezwyciężone, o tyle kwestie prawne i licencyjne (w tym głośne ugody wytwórni Warner Music i UMG opiewające na setki milionów dolarów) całkowicie przeobraziły branżę w latach 2025–2026.

**Typ:** Kompendium  
**Języki:** Python  
**Wymagania wstępne:** Faza 6 · 02 (spektrogramy i filtry melowe), Faza 4 · 10 (Modele dyfuzyjne)  
**Czas:** ~75 minut  

## Problem

Generowanie na podstawie promptu tekstowego spójnego utworu muzycznego o długości od 30 sekund do 4 minut, zawierającego wokal, tekst oraz odpowiednią strukturę (zwrotka, refren itd.). Problem ten dzieli się na trzy podzagadnienia:

1. **Synteza utworów instrumentalnych.** Przetwarzanie tekstowych opisów klimatu i instrumentarium (np. „upbeat synthwave with driving drums, 128 BPM”) bezpośrednio na sygnał audio. Modele: MusicGen, Stable Audio, AudioLDM.
2. **Synteza pełnych utworów (wokal + tekst).** Generowanie kompletnej piosenki (np. „ballada rockowa o podróżach kosmicznych”) zawierającej śpiewany tekst. Modele: Suno, Udio, YuE, ACE-Step.
3. **Generowanie warunkowe i edycja.** Wydłużanie istniejącego klipu (extending), regeneracja wybranych fragmentów (inpainting), zmiana gatunku muzycznego, rozdzielanie utworów na ścieżki (stems) czy dorysowywanie (outpainting). Funkcje te są kluczowe w profesjonalnej produkcji muzycznej w 2026 roku.

## Koncepcja

![Generowanie muzyki: podejście autoregresyjne LM vs modele dyfuzyjne](../assets/music-generacja.svg)

### Modele autoregresyjne (LM) na tokenach kodeków neuronowych

Modele takie jak **MusicGen** od Meta (2023, licencja MIT) opierają się na warunkowaniu wejściowym tekstem lub melodią w celu autoregresyjnego przewidywania tokenów kodeka EnCodec (częstotliwość 32 kHz, 4 książki kodowe - codebooks), które następnie są dekodowane do postaci fali dźwiękowej. Rozmiary modeli wahają się od 300M do 3.3B parametrów. Stanowią one silną linię bazową, choć często mają trudności przy generowaniu spójnych fraz dłuższych niż 30 sekund.

Model **ACE-Step** (wersja 4B XL wydana w kwietniu 2026 r.) rozszerza to podejście o możliwość generowania pełnych utworów muzycznych z wbudowanym wokalem warunkowanym tekstem piosenki, stając się najpoważniejszym otwartoźródłowym konkurentem platform komercyjnych.

### Modele dyfuzyjne w przestrzeni spektrogramów lub przestrzeni ukrytej

Modele **Stable Audio** oraz **Stable Audio Open** opierają się na dyfuzji w przestrzeni ukrytej (latent diffusion) na wysoce skompresowanym materiale audio. Rozwiązanie to wyśmienicie sprawdza się przy generowaniu pętli perkusyjnych (drum loops), efektów dźwiękowych (sound design) oraz tekstur ambientowych. Ma jednak trudności ze strukturyzacją pełnych, tradycyjnych utworów muzycznych.

Modele **AudioLDM** i **AudioLDM2** realizują zadanie Text-to-Audio za pomocą dyfuzji w przestrzeni ukrytej, znajdując uniwersalne zastosowanie w syntezie efektów dźwiękowych, muzyki oraz mowy.

### Rozwiązania hybrydowe (platformy SaaS) — Suno, Udio, Lyria

Są to systemy o zamkniętym kodzie źródłowym i wagach (proprietary). Najprawdopodobniej łączą one autoregresyjne generatory tokenów (LM) z wokoderami dyfuzyjnymi oraz dedykowanymi modułami dla wokalu i perkusji. **Suno v5** (2026) prowadzi w jakościowych testach porównawczych ELO. **Udio v4** oferuje dodatkowo zaawansowany inpainting oraz bezproblemowy eksport utworu z podziałem na osobne ścieżki (stems: wokal, perkusja, bas itp.).

### Ewaluacja modeli muzycznych

- **FAD (Fréchet Audio Distance).** Miara odległości w przestrzeni osadzeń pomiędzy rozkładem próbek wygenerowanych a rzeczywistych (wykorzystuje modele VGGish lub PANNs). Im niższa wartość, tym lepsza jakość dźwięku. MusicGen-small osiąga wynik FAD na poziomie 4.5 na zbiorze MusicCaps; najlepsze współczesne modele osiągają wyniki bliskie 3.0.
- **Ocena subiektywna.** Oceny wystawiane przez ludzkich ekspertów i słuchaczy (Suno v5 jest liderem w rankingach ELO).
- **Spójność tekstu z dźwiękiem.** Obliczana przy użyciu modeli CLAP (współczynnik podobieństwa tekst-audio).
- **Detekcja artefaktów.** Automatyczne wykrywanie gwałtownych zmian tempa, przesunięć fazowych w wokalu oraz utraty spójności pod koniec utworu.

## Zestawienie modeli w 2026 r.

| Model | Liczba parametrów | Typowa długość | Wokal? | Licencja |
|-------|--------|--------|--------|-------------|
| MusicGen-Large | 3.3B | 30 s | Nie | MIT |
| Stable Audio Open | 1.2B | 47 s | Nie | Dedykowana (niekomercyjna) |
| ACE-Step XL (04.2026) | 4B | > 2 min | Tak | Apache-2.0 |
| YuE | 7B | > 2 min | Tak (wielojęzyczny) | Apache-2.0 |
| Suno v5 (zamknięty) | ? | 4 min | Tak | Komercyjna |
| Udio v4 (zamknięty) | ? | 4 min | Tak (+ stems) | Komercyjna |
| Google Lyria 3 (zamknięty)| ? | Czas rzeczywisty| Tak | Komercyjna |

## Aspekty prawne i regulacje (2025–2026)

- **Ugoda Warner Music Group z Suno.** Zawarta na kwotę 500 mln USD. WMG sprawuje obecnie nadzór nad wykorzystaniem wizerunku artystów, praw autorskich do muzyki i utworów tworzonych przez użytkowników na platformie Suno. Podobne porozumienie zawarło UMG z Udio.
- **Regulacje prawne (EU AI Act, California SB 942).** Wprowadzają obowiązek wyraźnego oznaczania i ujawniania treści audio generowanych przez sztuczną inteligencję.

Bezpieczne schematy wdrożeniowe (compliance-friendly):
1. Generowanie wyłącznie muzyki instrumentalnej z użyciem modeli o otwartych licencjach (np. MusicGen, Stable Audio Open).
2. Korzystanie z licencjonowanych, komercyjnych API (Suno, Udio, ElevenLabs Music) zezwalających na komercyjne użycie wygenerowanych utworów.
3. Trenowanie modeli wyłącznie na własnym, w pełni licencjonowanym katalogu muzycznym.
4. Zapewnienie, że każdy generowany plik zawiera cyfrowy znak wodny oraz metadane oznaczające pochodzenie AI.

## Implementacja krok po kroku

### Krok 1: Wnioskowanie z użyciem modelu MusicGen

```python
from audiocraft.models import MusicGen
import torchaudio

model = MusicGen.get_pretrained("facebook/musicgen-small")
model.set_generation_params(duration=10)
wav = model.generate(["upbeat synthwave with driving drums, 128 BPM"])
torchaudio.save("out.wav", wav[0].cpu(), 32000)
```

Dostępne są trzy rozmiary modeli: `small` (300M parametrów, szybki), `medium` (1.5B) oraz `large` (3.3B). Wersja `small` jest w zupełności wystarczająca do wdrożeń typu Proof-of-Concept.

### Krok 2: Warunkowanie za pomocą melodii (Chroma Conditioning)

```python
melody, sr = torchaudio.load("humming.wav")
wav = model.generate_with_chroma(
    ["jazz piano cover"],
    melody.squeeze(),
    sr,
)
```

Model `musicgen-melody` ekstrahuje chromatogram (chromagram) i zachowuje oryginalną melodię przy jednoczesnej zmianie instrumentarium. Niezwykle przydatne w scenariuszach typu „przekształć tę zanuconą melodię w partię kwartetu smyczkowego”.

### Krok 3: Obliczanie odległości FAD (koncepcyjnie)

```python
from frechet_audio_distance import FrechetAudioDistance
fad = FrechetAudioDistance()

# Obliczenie wskaźnika FAD między wygenerowanymi a referencyjnymi nagraniami
score = fad.get_fad_score("generated_folder/", "reference_folder/")
```

Wykorzystuje sieć VGGish do porównania statystyk rozkładu wektorów cech. Jest to standardowa metoda automatycznej oceny jakości i spójności stylistycznej w potokach CI/CD.

### Krok 4: Integracja muzycznego modelu z LLM (AI Agent)

```python
prompt = "Write a 30-second jazz loop. Describe the drums, bass, and piano voicing."
description = llm.complete(prompt)
music = musicgen.generate([description], duration=30)
```

## Sugerowane rozwiązania (2026)

| Zastosowanie | Rekomendowany stos |
|---|---|
| Sound design i muzyka instrumentalna | Stable Audio Open |
| Dynamiczna / adaptacyjna ścieżka dźwiękowa w grach | Google Lyria RealTime API |
| Pełne utwory z wokalem do celów marketingowych | Suno v5 lub Udio v4 z wykupioną licencją |
| Pełne utwory z wokalem (rozwiązania open-source) | Model ACE-Step XL lub YuE |
| Krótkie jingle reklamowe | MusicGen-melody z warunkowaniem zanuconą melodią |

## Typowe pułapki (wciąż aktualne w 2026 r.)

- **Prompty naruszające prawa autorskie.** Zapytania typu „piosenka w stylu Taylor Swift” są automatycznie blokowane przez filtry komercyjnych platform Suno i Udio. W przypadku modeli otwartoźródłowych musisz zaimplementować własną listę zabronionych fraz.
- **Zapętlenia i degradacja jakości powyżej 30 s.** Autoregresyjne modele mają tendencję do powtarzania motywów w nieskończoność. Zastosuj technikę przenikania (cross-fading) kolejnych fragmentów lub skorzystaj z modelu ACE-Step, aby zachować spójność strukturalną.
- **Rozbieżności w tempie utworu (BPM drift).** Modele generatywne mogą nie trzymać idealnego tempa. Używaj jasnych tagów BPM w promptach i weryfikuj tempo na wyjściu za pomocą biblioteki Librosa.
- **Niska zrozumiałość wokalu.** W modelach open-source wokal potrafi być niewyraźny. Jeśli tekst piosenki jest kluczowy, stosuj sprawdzone API komercyjne.
- **Generowanie dźwięku mono.** Większość modeli open-source generuje dźwięk monofoniczny lub sztucznie poszerzone stereo. Do uzyskania pełnej panoramy stereofonicznej zastosuj modele rekonstrukcji stereo (np. ezst lub dyfuzję stereo Cartesii).

## Zadanie do wykonania

Zapisz jako `outputs/skill-music-designer.md`. Dobierz model, strategię licencyjną, strukturę i długość utworów oraz określ format metadanych oznaczających użycie sztucznej inteligencji.

## Ćwiczenia

1. **Łatwe.** Uruchom skrypt `code/main.py`. Generuje on prosty schemat akordów oraz sekwencję perkusyjną w postaci znaków ASCII. Wygenerowane MIDI możesz odtworzyć w dowolnym programie DAW.
2. **Średnie.** Zainstaluj bibliotekę `audiocraft`, wygeneruj 10-sekundowe próbki dla 4 różnych gatunków muzycznych z użyciem modelu MusicGen-small i oblicz ich wskaźniki FAD w odniesieniu do bazy próbek referencyjnych.
3. **Trudne.** Wykorzystując model ACE-Step XL, wygeneruj trzy różne aranżacje tej samej melodii wejściowej. Oblicz współczynniki podobieństwa CLAP, aby ocenić spójność zadanego promptu tekstowego z wygenerowanym plikiem audio.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to naprawdę oznacza |
|------|-----------------|----------------------|
| FAD | Audio FID | Fréchet Audio Distance; metryka oceny jakości audio bazująca na odległości statystycznej rozkładu cech wyodrębnionych przez sieć VGGish. |
| Chromagram | Profil harmoniczny | 12-wymiarowy wektor reprezentujący rozkład energii w poszczególnych półtonach skali muzycznej; służy do warunkowania melodią. |
| Stems | Ścieżki | Wyodrębnione, pojedyncze komponenty utworu (np. oddzielne pliki WAV dla wokalu, perkusji, gitary). |
| Inpainting | Lokalna regeneracja | Maskowanie wybranego okna czasowego w celu wygenerowania w tym miejscu nowej aranżacji lub wokalizacji. |
| CLAP | CLAP embedding | Contrastive Language-Audio Pretraining; model reprezentacji tekst-audio służący do weryfikacji zgodności promptu tekstowego z wygenerowaną muzyką. |
| Codec | Kodek neuronowy | Algorytm kompresji mowy/muzyki do postaci dyskretnych tokenów (np. EnCodec), stanowiący podstawę nowoczesnych generatorów audio. |

## Dalsze czytanie

- [Copet et al. (2023). Simple and Controllable Music Generation](https://arxiv.org/abs/2306.05284) — publikacja opisująca model MusicGen.
- [Evans et al. (2024). Stable Audio Open](https://arxiv.org/abs/2407.14358) — specyfikacja modelu Stable Audio Open.
- [ACE-Step Project Repository](https://github.com/ace-step/ACE-Step) — repozytorium otwartoźródłowego modelu do generowania pełnych utworów muzycznych.
- [Suno v5 Platform Documentation](https://suno.com) — oficjalne materiały i przewodniki po platformie Suno.
- [AudioLDM 2: Learning a General Single-Text-to-Audio-Generation Model](https://arxiv.org/abs/2308.05734) — praca wprowadzająca uniwersalną architekturę AudioLDM 2.
- [Warner Music Group and Suno Settlement News](https://www.musicbusinessworldwide.com/suno-warner-music-settlement/) — szczegóły precedensowego porozumienia w branży muzycznej generowanej przez AI.
