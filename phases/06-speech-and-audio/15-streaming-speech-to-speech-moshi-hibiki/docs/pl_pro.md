# Przesyłanie strumieniowe mowy na mowę — Moshi, Hibiki i dialog pełnodupleksowy

> Lata 2024–2026 na nowo zdefiniowały sztuczną inteligencję głosową. Moshi to jeden model, który jednocześnie słucha i mówi z opóźnieniem 200 ms. Hibiki tłumaczy mowę na mowę fragment po fragmencie. Obydwa rozwiązania porzucają potok ASR → LLM → TTS na rzecz zunifikowanej architektury pełnego dupleksu opartej na tokenach kodeka Mimi. To nowy projekt referencyjny.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 13 (Neural Audio Codecs), Faza 6 · 11 (Dźwięk w czasie rzeczywistym), Faza 7 · 05 (Pełny transformator)
**Czas:** ~75 minut

## Problem

Każdy agent głosowy zbudowany na podstawie lekcji 11 i 12 ma bazowe opóźnienie rzędu 300–500 ms: kolejno uruchamia VAD, przetwarza STT, wnioskuje przez LLM i generuje TTS. Każdy etap wnosi własne minimalne opóźnienie. Można je dostrajać i zrównoleglać, lecz kształt potoku wyznacza nieprzekraczalne granice.

Moshi (Kyutai, 2024–2026) stawia inne pytanie: co, jeśli potok w ogóle nie istnieje? Co jeśli jeden model pobiera dźwięk i bezpośrednio go emituje — w sposób ciągły, traktując tekst jako pośredni „monolog wewnętrzny" zamiast obowiązkowego etapu przetwarzania?

Odpowiedzią jest **pełnodupleksowa zamiana mowy na mowę**. Teoretyczne opóźnienie wynosi 160 ms (ramka Mimi 80 ms + opóźnienie akustyczne 80 ms). W praktyce, na pojedynczym procesorze graficznym L4, osiąga się 200 ms — czyli połowę tego, co uzyskuje najlepszy potokowy agent głosowy.

## Koncepcja

![Architektura Moshi: dwa równoległe strumienie Mimi + tekst wewnętrznego monologu](../assets/moshi-hibiki.svg)

### Architektura Moshi

**Wejścia.** Dwa strumienie kodeków Mimi, oba przy 12,5 Hz × 8 książkach kodowych:

- Strumień 1: dźwięk użytkownika (kodowany przez Mimi, stale napływający)
- Strumień 2: własny dźwięk Moshi (generowany przez Moshi)

**Transformator.** Transformator czasowy o 7B parametrach przetwarza oba strumienie audio oraz strumień tekstowy „monologu wewnętrznego". Przy każdym kroku 80 ms:

1. Pobiera najnowsze tokeny Mimi użytkownika (8 książek kodowych).
2. Pobiera najnowsze tokeny Mimi Moshi (8 książek kodowych, zgodnie z ich wcześniejszą produkcją).
3. Generuje kolejny token tekstowy Moshi (monolog wewnętrzny).
4. Generuje kolejne tokeny Mimi Moshi (8 książek kodowych za pomocą małego transformatora głębi).

Wszystkie trzy strumienie — dźwięk użytkownika, dźwięk Moshi i tekst Moshi — działają równolegle. Moshi słyszy użytkownika podczas mówienia, może się zatrzymać, gdy rozmówca przerwie, i potrafi wydać sygnał zwrotny („mhm") bez przerywania głównej wypowiedzi.

**Transformator głębi.** Osiem książek kodowych w ramce nie jest przewidywanych równolegle — istnieją między nimi zależności. Mały, dwuwarstwowy transformator głębi przewiduje je sekwencyjnie w ciągu 80 ms. To standardowy sposób faktoryzacji w autoregesywnych modelach językowych operujących na kodekach (stosowany też przez VALL-E i VibeVoice).

### Dlaczego tekst w formie monologu wewnętrznego pomaga

Bez jawnego strumienia tekstowego model musi kodować język pośrednio w strumieniu akustycznym. Kluczowe spostrzeżenie twórców Moshi: warto wymusić na modelu emisję tokenów tekstowych równolegle z dźwiękiem. Strumień tekstu jest w istocie transkrypcją wypowiedzi Moshi. Poprawia to spójność semantyczną, upraszcza wymianę warstwy językowej modelu i dostarcza transkrypcji bez dodatkowych kosztów.

### Hibiki: strumieniowe tłumaczenie mowy na mowę

Ta sama architektura, wytrenowana na parach tłumaczeniowych. Na wejściu przyjmuje dźwięk w języku źródłowym, na wyjściu produkuje dźwięk w języku docelowym — w sposób ciągły. Hibiki-Zero (luty 2026) eliminuje potrzebę danych treningowych wyrównanych na poziomie słów: korzysta z danych na poziomie zdań oraz uczenia przez wzmacnianie GRPO w celu optymalizacji opóźnień.

Początkowo obsługiwano cztery pary językowe; dostosowanie do nowego języka wymaga około 1000 godzin danych.

### Szerszy stos Kyutai (2026)

- **Moshi** — dialog w trybie pełnego dupleksu (najpierw francuski, dobre wsparcie dla angielskiego)
- **Hibiki / Hibiki-Zero** — symultaniczne tłumaczenie mowy
- **Kyutai STT** — strumieniowe ASR (wyprzedzenie 500 ms lub 2,5 s)
- **Kyutai Pocket TTS** — 100M-parametrowy TTS działający na procesorze (styczeń 2026)
- **Unmute** — pełny potok łączący powyższe komponenty na serwerach publicznych

Przepustowość procesora graficznego L40S: 64 równoczesne sesje w czasie rzeczywistym przy 3-krotnym przyspieszeniu.

### Sesame CSM — model pokrewny

Sesame CSM (2025) opiera się na podobnym pomyśle — szkielet Llama-3 z głowicą kodeka Mimi. Jednak CSM działa jednostronnie (przyjmuje kontekst i tekst, generuje mowę) i nie obsługuje pełnego dupleksu. To najlepszy dostępny system TTS pod względem „obecności głosu", lecz jego możliwości są zasadniczo różne od pełnodupleksowych funkcji Moshi.

### Wyniki z 2026 r.

| Model | Opóźnienie | Zastosowanie | Licencja |
|-------|--------|----------|---------|
| Moshi | 200 ms (L4) | pełnodupleksowy dialog angielski/francuski | CC-BY 4.0 |
| Hibiki | 12,5 Hz | strumieniowe tłumaczenie francuski ↔ angielski | CC-BY 4.0 |
| Hibiki-Zero | j.w. | 5 par językowych, bez wyrównanych danych | CC-BY 4.0 |
| Sesame CSM-1B | 200 ms TTFA | kontekstowy TTS | Apache-2.0 |
| GPT-4o Realtime | ~300 ms | zamknięty, OpenAI API | komercyjny |
| Gemini 2.5 Live | ~350 ms | zamknięty, Google API | komercyjny |

## Zbuduj to

### Krok 1: interfejs

Moshi udostępnia serwer WebSocket, który przyjmuje 80-milisekundowe fragmenty dźwięku zakodowanego przez Mimi i odsyła 80-milisekundowe fragmenty zakodowanego dźwięku — w obu kierunkach, nieprzerwanie.

```python
import asyncio
import websockets
from moshi.client_utils import encode_audio_mimi, decode_audio_mimi

async def moshi_chat():
    async with websockets.connect("ws://localhost:8998/api/chat") as ws:
        mic_task = asyncio.create_task(stream_mic_to(ws))
        spk_task = asyncio.create_task(stream_from_to_speaker(ws))
        await asyncio.gather(mic_task, spk_task)
```

### Krok 2: pętla pełnego dupleksu

```python
async def stream_mic_to(ws):
    async for chunk_80ms in mic_stream_at_12_5_hz():
        mimi_tokens = encode_audio_mimi(chunk_80ms)
        await ws.send(serialize(mimi_tokens))

async def stream_from_to_speaker(ws):
    async for msg in ws:
        mimi_tokens, text_token = deserialize(msg)
        audio = decode_audio_mimi(mimi_tokens)
        await play(audio)
```

Oba kierunki działają jednocześnie. Standardowym mechanizmem transportu są futures asyncio w Pythonie lub Rust.

### Krok 3: cel treningu (koncepcyjny)

Dla każdej ramki 80 ms `t`:

- Dane wejściowe: `user_mimi[0..t]`, `moshi_mimi[0..t-1]`, `moshi_text[0..t-1]`
- Przewiduj: `moshi_text[t]`, następnie `moshi_mimi[t, codebook_0..7]`

Tekst jest przewidywany przed dźwiękiem (monolog wewnętrzny); dźwięk jest przewidywany sekwencyjnie według książek kodowych w transformatorze głębi.

### Krok 4: gdzie Moshi wygrywa, a gdzie nie

Moshi wygrywa:

- Opóźnienie poniżej 250 ms od wejścia do wyjścia na niedrogim sprzęcie.
- Naturalne sygnały zwrotne i obsługa przerywania.
- Brak kodu kleju integrującego kolejne etapy potoku.

Moshi nie wygrywa:

- Wywoływanie narzędzi (model nie jest w tym zakresie trenowany; potrzebna jest osobna ścieżka LLM).
- Długie wnioskowanie (Moshi to model dialogu klasy 8B, nie Claude czy GPT-4).
- Dokładność w tematach niszowych.
- Większość produkcyjnych zastosowań korporacyjnych (w 2026 r. nadal opierają się na potokach).

## Kiedy to stosować

| Sytuacja | Wybór |
|----------|------|
| Asystent głosowy z najniższym opóźnieniem | Moshi |
| Połączenie z tłumaczeniem na żywo | Hibiki |
| Demo głosu / badania | Moshi, CSM |
| Agent korporacyjny z narzędziami | Potok (lekcja 12), nie Moshi |
| TTS z niestandardowym głosem w kontekście | Sesame CSM |
| Zamiana mowy na mowę, dowolne języki | GPT-4o Realtime lub Gemini 2.5 Live (komercyjne) |

## Pułapki

- **Ograniczone wywoływanie narzędzi.** Moshi to model dialogu, nie framework agentowy. Narzędzia należy podłączyć przez osobny potok.
- **Specyficzne warunkowanie głosu.** Moshi używa jednej wytrenowanej osobowości głosowej; klonowanie głosu to odrębny proces treningowy.
- **Zasięg językowy.** Francuski i angielski są obsługiwane wzorcowo; pozostałe języki — ograniczenie. Hibiki-Zero pomaga, lecz nadal wymaga danych treningowych.
- **Koszt zasobów.** Pełna sesja Moshi zajmuje gniazdo GPU; nie jest to tani wzorzec wdrożenia przy wielu współdzierżawcach.

## Wyślij to

Zapisz jako `outputs/skill-duplex-pipeline.md`. Wybierając architekturę dla agenta głosowego, świadomie zdecyduj między podejściem potokowym a pełnodupleksowym — każde ma swoje uzasadnienie.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Symuluje symbolicznie architekturę dwustrumieniową z monologiem wewnętrznym.
2. **Średnie.** Pobierz Moshi z HuggingFace, uruchom serwer i przeprowadź jedną rozmowę testową. Zmierz opóźnienie zegarowe od zakończenia wypowiedzi użytkownika do początku odpowiedzi Moshi.
3. **Trudne.** Weź agenta potokowego z lekcji 12 i porównaj medianowe opóźnienie P50 z Moshi na 20 dopasowanych wypowiedziach testowych. Udokumentuj sytuacje, w których potok i tak wygrywa pod względem architektonicznym.

## Kluczowe terminy

| Termin | Popularne rozumienie | Właściwe znaczenie |
|------|-----------------|----------------------|
| Pełny dupleks | Słuchaj i mów jednocześnie | Dwa aktywne strumienie audio działające równolegle w tym samym modelu. |
| Monolog wewnętrzny | Strumień tekstowy modelu | Moshi emituje tokeny tekstowe równolegle z wyjściem audio. |
| Transformator głębi | Predyktor między książkami kodowymi | Mały transformator przewidujący 8 słowników w jednej ramce 80 ms. |
| Mimi | Kodek Kyutai | 12,5 Hz × 8 książek kodowych; semantyczno-akustyczny; fundament Moshi. |
| Strumieniowe S2S | Audio → audio na żywo | Tłumaczenie lub dialog fragment po fragmencie, bez etapów potoku. |
| Kanał zwrotny | Reakcje „Mhm" | Moshi może emitować krótkie potwierdzenia bez przerywania swojej tury. |

## Dalsze czytanie

- [Défossez i in. (2024). Moshi — model podstawy mowy i tekstu](https://arxiv.org/html/2410.00037v2) — artykuł naukowy.
- [Laboratoria Kyutai (2026). Hibiki-Zero](https://arxiv.org/abs/2602.12345) — strumieniowe tłumaczenie bez wyrównanych danych.
- [Sesame (2025). Crossing the Uncanny Valley of Voice](https://www.sesame.com/research/crossing_the_uncanny_valley_of_voice) — specyfikacja CSM.
- [Kyutai — repozytorium Moshi](https://github.com/kyutai-labs/moshi) — instalacja i serwer.
- [OpenAI — Realtime API](https://platform.openai.com/docs/guides/realtime) — zamknięte, komercyjne rozwiązanie.
- [Kyutai — Delayed Streams Modeling](https://github.com/kyutai-labs/delayed-streams-modeling) — framework STT/TTS używany wewnętrznie.
