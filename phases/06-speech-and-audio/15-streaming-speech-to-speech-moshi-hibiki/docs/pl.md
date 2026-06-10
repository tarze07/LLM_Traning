# Przesyłanie strumieniowe mowy na mowę — Moshi, Hibiki i dialog pełnodupleksowy

> Lata 2024–2026 na nowo zdefiniowały sztuczną inteligencję głosową. Moshi dostarcza jeden model, który jednocześnie słucha i mówi z opóźnieniem 200 ms. Hibiki dokonuje tłumaczenia mowy na mowę fragment po fragmencie. Obydwa porzucają potok ASR → LLM → TTS na rzecz ujednoliconej architektury pełnego dupleksu w oparciu o tokeny kodeka Mimi. To jest nowy projekt referencyjny.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 6 · 13 (Neural Audio Codecs), Faza 6 · 11 (Dźwięk w czasie rzeczywistym), Faza 7 · 05 (Pełny transformator)
**Czas:** ~75 minut

## Problem

Każdy agent głosowy zbudowany na podstawie lekcji 11 + 12 ma podstawowy poziom opóźnienia wynoszący około 300–500 ms: uruchamia VAD, procesy STT, przyczyny LLM, generuje TTS. Każdy etap ma swoje własne minimalne opóźnienie. Możesz dostroić i zrównoleglić, ale kształt potoku Cię ogranicza.

Moshi (Kyutai, 2024-2026) zadaje inne pytanie: co, jeśli nie będzie gazociągu? A co jeśli jeden model pobiera dźwięk i emituje go bezpośrednio, w sposób ciągły, z tekstem jako pośrednim „monologiem wewnętrznym” zamiast wymaganej sceny?

Odpowiedź to **pełnodupleksowa zamiana mowy na mowę**. Teoretyczne opóźnienie 160 ms (ramka Mimi 80 ms + opóźnienie akustyczne 80 ms). Praktyczne opóźnienie 200 ms na pojedynczym procesorze graficznym L4. To połowa tego, co osiąga najlepszy w swojej klasie potokowy agent głosowy.

## Koncepcja

![Architektura Moshi: dwa równoległe strumienie Mimi + tekst wewnętrznego monologu](../assets/moshi-hibiki.svg)

### Architektura Moshi

**Wejścia.** Dwa strumienie kodeków Mimi, oba przy 12,5 Hz × 8 książek kodowych:

- Strumień 1: dźwięk użytkownika (kodowany w Mimi, stale napływający)
- Strumień 2: własny dźwięk Moshiego (wygenerowany przez Moshi)

**Transformator.** Transformator czasowy o parametrach 7B przetwarza zarówno strumienie, jak i strumień tekstowy „monologu wewnętrznego”. Przy każdym kroku 80 ms:

1. Zużywa najnowsze tokeny Mimi użytkownika (8 książek kodowych).
2. Zużywa najnowsze żetony Moshi Mimi (8 książeczek kodów, zgodnie z ich produkcją).
3. Generuje kolejny żeton tekstu Moshi (monolog wewnętrzny).
4. Generuje kolejne tokeny Moshi Mimi (8 książek kodowych za pomocą małego transformatora głębi).

Wszystkie trzy strumienie — dźwięk użytkownika, dźwięk Moshi i tekst Moshi — działają równolegle. Moshi słyszy użytkownika podczas mówienia; może przerwać się, gdy użytkownik przerwie; może przekazać kanał zwrotny („mhm”) bez przerywania głównej wypowiedzi.

**Transformator głębi.** W ramce 8 książek kodowych nie jest przewidywanych równolegle — mają one zależności między książkami kodowymi. Mały 2-warstwowy „transformator głębokości” przewiduje je sekwencyjnie w ciągu 80 ms. Jest to standardowa faktoryzacja dla kodeków AR LM (używana również przez VALL-E, VibeVoice).

### Dlaczego tekst w formie monologu wewnętrznego pomaga

Bez wyraźnego tekstu model musi pośrednio modelować język w jego strumieniu akustycznym. Spostrzeżenie Moshiego: zmuś go do emitowania żetonów tekstowych wraz z dźwiękiem. Strumień tekstu jest zasadniczo transkrypcją tego, co mówi Moshi. Poprawia to spójność semantyczną, ułatwia wymianę głowy modelu językowego i zapewnia bezpłatne transkrypcje.

### Hibiki: strumieniowe tłumaczenie mowy na mowę

Ta sama architektura, przeszkolona w zakresie par tłumaczeniowych. Wejście źródła dźwięku, wyjście dźwięku języka docelowego, w sposób ciągły. Hibiki-Zero (luty 2026 r.) eliminuje potrzebę danych szkoleniowych dostosowanych na poziomie słów — wykorzystuje dane na poziomie zdań + uczenie się wzmacniające GRPO w celu optymalizacji opóźnień.

Początkowo obsługiwane były cztery pary językowe; można dostosować do nowego języka w ciągu ≈1000 godzin.

### Szerszy stos Kyutai (2026)

- **Moshi** — dialog w trybie pełnego dupleksu (najpierw francuski, dobrze obsługiwany angielski)
- **Hibiki / Hibiki-Zero** — tłumaczenie mowy symultanicznej
- **Kyutai STT** — przesyłanie strumieniowe ASR (wyprzedzenie 500 ms lub 2,5 s)
- **Kyutai Pocket TTS** — TTS o parametrach 100M działa na procesorze (styczeń 2026 r.)
- **Wyłącz wyciszenie** — pełny potok łączący je na serwerach publicznych

Przepustowość procesora graficznego L40S: 64 równoczesnych sesji w czasie rzeczywistym 3x.

### Sesame CSM — kuzyn

Sesame CSM (2025) wykorzystuje podobny pomysł — szkielet Llama-3 z głowicą kodeka Mimi. Ale CSM jest jednokierunkowy (pobiera kontekst + tekst, generuje mowę), a nie pełny dupleks. To najlepszy TTS z „obecnością głosu” na rynku; to nie to samo, co możliwości pełnego dupleksu Moshi.

### Wyniki z 2026 r

| Modelka | Opóźnienie | Przypadek użycia | Licencja |
|-------|--------|----------|---------|
| Moshi | 200 ms (L4) | pełny dupleks dialog angielski/francuski | CC-BY 4.0 |
| Hibiki | Liczba klatek na sekundę 12,5 Hz | Tłumaczenie strumieniowe z francuskiego ↔ angielskiego | CC-BY 4.0 |
| Hibiki-Zero | to samo | 5 par językowych, brak wyrównanych danych | CC-BY 4.0 |
| Sezam CSM-1B | 200 ms TTFA | kontekstowo TTS | Apache-2.0 |
| GPT-4o Czas rzeczywisty | ~300 ms | zamknięte, OpenAI API | komercyjny |
| Gemini 2.5 na żywo | ~350 ms | zamknięte, Google API | komercyjny |

## Zbuduj to

### Krok 1: interfejs

Moshi udostępnia serwer WebSocket, który pobiera fragmenty dźwięku zakodowanego w Mimi o długości 80 ms i zwraca fragmenty dźwięku zakodowanego w Mimi o długości 80 ms. Obydwa sposoby. Stale.

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

Obydwa kierunki kursują jednocześnie. Standardowym transportem są kontrakty terminowe Python asyncio lub Rust.

### Krok 3: cel szkolenia (koncepcyjny)

Dla każdej ramki 80 ms `t`:

- Dane wejściowe: `user_mimi[0..t]`, `moshi_mimi[0..t-1]`, `moshi_text[0..t-1]`
- Prognozuj: `moshi_text[t]`, następnie `moshi_mimi[t, codebook_0..7]`

Tekst jest przewidywany przed dźwiękiem (monolog wewnętrzny); dźwięk jest przewidywany sekwencyjnie w książce kodowej w transformatorze głębi.

### Krok 4: gdzie Moshi wygrywa, a gdzie nie

Moshi wygrywa:

- Mniej niż 250 ms od początku do końca na tanim sprzęcie.
- Naturalne kanały zwrotne i przerwy.
- Brak kodu kleju do rurociągów.

Moshi nie wygrywa:

- Wywoływanie narzędzi (nie jest w tym przeszkolony; potrzebujesz osobnej ścieżki LLM).
- Długie rozumowanie (Moshi to model dialogu w stylu 8B, a nie Claude/GPT-4).
- Rzeczywista dokładność w tematach niszowych.
- Większość przypadków użycia w przedsiębiorstwach produkcyjnych (w 2026 r. nadal będą korzystać z rurociągów).

## Użyj tego

| Sytuacja | Wybierz |
|----------|------|
| Towarzysz głosowy o najniższym opóźnieniu | Moshi |
| Połączenie z tłumaczeniem na żywo | Hibiki |
| Demo głosu / badania | Moshi, CSM |
| Agent korporacyjny z narzędziami | Rurociąg (lekcja 12), a nie Moshi |
| TTS z niestandardowym głosem w kontekście | Sezam CSM |
| Zamiana mowy na mowę, dowolne języki | GPT-4o Realtime lub Gemini 2.5 Live (komercja) |

## Pułapki

- **Ograniczone wywoływanie narzędzi.** Moshi to model dialogu, a nie framework agenta. Połącz z rurociągiem na narzędzia.
- **Specyficzne warunkowanie głosu.** Moshi używa jednej wyszkolonej osoby; klonowanie to oddzielny proces szkoleniowy.
- **Zasięg językowy.** Francuski i angielski są doskonałe; inne ograniczone. Hibiki-Zero pomaga, ale nadal potrzebujesz danych treningowych.
- **Koszt zasobów.** Pełna sesja Moshi obejmuje gniazdo GPU; nie jest to tani wzorzec wdrażania ze współdzierżawą.

## Wyślij to

Zapisz jako `outputs/skill-duplex-pipeline.md`. W przypadku obciążenia agenta głosowego wybierz architekturę potokową zamiast architektury pełnego dupleksu, nie bez powodu.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Symuluje symbolicznie architekturę dwustrumieniową + monolog wewnętrzny.
2. **Średni.** Ściągnij Moshi z HuggingFace, uruchom serwer, przetestuj jedną rozmowę. Zmierz opóźnienie zegara ściennego od zakończenia mowy użytkownika do początku odpowiedzi Moshi.
3. **Trudne.** Weź agenta potokowego z lekcji 12 i porównaj opóźnienie P50 z Moshi w 20 dopasowanych wypowiedziach testowych. Zapisz, kiedy potok i tak wygrywa architektonicznie.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Pełny dupleks | Słuchaj i mów jednocześnie | Dwa strumienie audio aktywne jednocześnie w tym samym modelu. |
| Wewnętrzny monolog | Strumień tekstu modelki | Moshi emituje żetony tekstowe wraz ze swoim wyjściem audio. |
| Transformator głębokości | Predyktor między książkami kodowymi | Mały transformator, który przewiduje 8 słowników w jednej ramce 80 ms. |
| Mimi | Kodek Kyutai | Książki kodowe 12,5 Hz × 8; semantyczny+akustyczny; moc Moshiego. |
| Przesyłanie strumieniowe S2S | Audio → audio na żywo | Tłumaczenie/dialog fragment po fragmencie, bez etapów rurociągu. |
| Kanał zwrotny | Reakcje „Mhm” | Moshi może emitować małe potwierdzenia bez przerywania swojej tury. |

## Dalsze czytanie

- [Défossez i in. (2024). Moshi — model podstawy mowy i tekstu](https://arxiv.org/html/2410.00037v2) — artykuł.
- [Laboratoria Kyutai (2026). Hibiki-Zero](https://arxiv.org/abs/2602.12345) — tłumaczenie strumieniowe bez dopasowanych danych.
- [Sezam (2025). Przekraczanie niesamowitej doliny głosu](https://www.sesame.com/research/crossing_the_uncanny_valley_of_voice) — specyfikacja CSM.
- [Kyutai — repozytorium Moshi](https://github.com/kyutai-labs/moshi) — instalacja + serwer.
- [OpenAI — Realtime API](https://platform.openai.com/docs/guides/realtime) — zamknięty, komercyjny partner.
- [Kyutai — Delayed Streams Modeling](https://github.com/kyutai-labs/delayed-streams-modeling) — framework STT/TTS pod maską.