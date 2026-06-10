# Modele Omni: Qwen2.5-Omni i podział Thinker-Talker

> Demo produktu GPT-4o w maju 2024 r. było przełomowe nie ze względu na model, ale na kształt produktu — interfejs głosowy, w którym mówisz, model widzi to, co widzi kamera, i odpowiada w czasie krótszym niż 250 ms. W otwartym ekosystemie resztę lat 2024 i 2025 ścigano się, aby dotrzeć do powierzchni produktu. Qwen2.5-Omni (marzec 2025 r.) to referencyjny otwarty projekt: Thinker (duży transformator generujący tekst) plus Talker (równoległy transformator generujący mowę), połączone strumieniowymi tokenami mowy. Mini-Omni to uprościło, Moshi dopasował opóźnienie, GLM-4-Voice rozszerzył to na język chiński. W tej lekcji omówiono architekturę Thinker-Talker i budżet opóźnień, który sprawia, że ​​strumieniowanie dialogów w czasie rzeczywistym działa.

**Typ:** Kompilacja
**Języki:** Python (stdlib, symulator opóźnienia potoku strumieniowego + pętla VAD)
**Wymagania wstępne:** Faza 12 · 19 (audio-LLM), faza 12 · 16 (każdy z każdym)
**Czas:** ~180 minut

## Cele nauczania

- Podziel potok wnioskowania na Thinkera (wnioskowanie tekstu) i Talkera (synteza mowy) i wyjaśnij, dlaczego działa równoległe przesyłanie strumieniowe.
- Oblicz budżet czasu do pierwszego bajtu audio (TTFAB) dla interakcji konwersacyjnej, komponent po elemencie.
- Opisać kodowanie położenia wyrównanego w czasie w TMRoPE w obszarze obrazu, dźwięku i tekstu w Myślicielu.
- Wymień trzy wzorce konwersacji w czasie rzeczywistym: półdupleks, tura, pełny dupleks.

## Problem

Asystent głosowy działający w czasie rzeczywistym musi dużo i szybko:

1. Wysłuchaj użytkownika. Tokenizacja mowy w czasie rzeczywistym i wykrywanie aktywności głosowej (VAD), aby wiedzieć, kiedy ktoś skończy mówić.
2. Opcjonalnie zobacz. Sygnał wejściowy z kamery przy 2–4 kl./s przesyłany strumieniowo do Thinkera wraz z dźwiękiem.
3. Pomyśl. Skomponuj odpowiedź uzależnioną od historii rozmowy.
4. Mów. Syntezuj tokeny audio, dekoduj do postaci fali, przesyłaj strumieniowo do głośników użytkownika.

Każdy krok zwiększa opóźnienie. Komfort rozmowy wymaga całkowitego czasu podróży w obie strony < 500 ms — poniżej tego użytkownik przestaje zauważać opóźnienie. GPT-4o twierdzi ~250ms. Moshi ~160ms. Qwen2.5 – Omni ~350-500ms.

Każdy komponent musi być przesyłany strumieniowo. Nic nie może zostać „zgrupowane w całość, a następnie zdekodowane”.

## Koncepcja

### Myśliciel i mówca

Rozkład Qwen2.5-Omni:

- Thinker: transformator generujący tekst 7B-80B. Zużywa przeplatany tekst + obraz + tokeny audio. Wyświetla tokeny tekstowe reprezentujące to, co powiedzieć.
- Talker: mniejszy transformator generujący mowę (200M-1B). Zużywa żetony wyjściowego tekstu Myśliciela oraz ostatnie żetony kontekstu mowy. Wysyła dyskretne żetony mowy (indeksy rezydualne VQ).
- Dekoder mowy: dekoder strumieniowego przesyłania przebiegów (SNAC, rodzina MoVQGAN), który pobiera tokeny mowy do próbek audio w czasie rzeczywistym.

Rozstanie ma znaczenie. Myśliciel musi być duży, żeby móc dobrze rozumować. Talker może być mały, ponieważ jego zadanie jest lokalne — konwertuj tekst na tokeny mowy. Bigger Talker nie jest bardziej wyrazisty; jest wolniej.

Uruchamianie obu równolegle:

1. Myśliciel emituje token tekstowy t_i.
2. Talker zużywa t_i (poprzez streaming) i emituje tokeny mowy s_i, s_{i+1}, ..., s_{i+k}.
3. Dekoder mowy zużywa żetony mowy w miarę ich pojawiania się i emituje próbki audio.
4. Zanim Thinker dotrze do tokena tekstowego t_{i+3}, Talker już przesyła strumieniowo dźwięk dla t_0..t_{i+2}.

### TMRoPE — pozycje multimodalne wyrównane w czasie

Thinker musi zintegrować klatki obrazu (powiedzmy z szybkością 4 klatek na sekundę), klatki audio (z szybkością 50 klatek na sekundę) i tekst z historii rozmów. Naiwny porządek sekwencji (wszystkie obrazy, potem cały dźwięk, potem tekst) traci wyrównanie czasowe.

TMRoPE przypisuje bezwzględne znaczniki czasu do każdego tokena. Żeton wizji w czasie t=2,3 s. Token dźwiękowy w t=2,32 s. Token tekstowy od użytkownika „stop” o godzinie t=2,35 s. RoPE obraca uwagę według znacznika czasu; model postrzega je jako czasowo współbieżne.

Jest to infrastruktura umożliwiająca działanie w trybie „machał na powitanie” — model widzi klatkę wideo i dźwięk w tym samym momencie koncepcyjnym.

### Strumieniowa synteza mowy

Żetony mowy muszą być przesyłane strumieniowo. Mini-Omni (Xie i Wu, 2024) wprowadzili „modele językowe, które mogą słyszeć, mówić i myśleć podczas przesyłania strumieniowego”: żetony wyjściowe Myśliciela i tokeny wyjściowe Mówcy przeplatają się w tej samej kolejności. Mówca strzela, gdy tylko Myśliciel zatwierdzi następny żeton tekstu. Brak granic partii.

Moshi (Défossez i in., październik 2024) to najszybsza otwarta implementacja. 160 ms TTFAB na pojedynczym A100. Architektura: pojedynczy transformator 7B, który emituje tokeny tekstu i mowy w naprzemiennych pozycjach, z „monologiem wewnętrznym”, który oddziela strumień myślenia od strumienia mówienia. Jest to w rzeczywistości Myśliciel + Mówca połączony w jeden model po dokładnym przeszkoleniu.

### VAD i wykonywanie tur

Wykrywanie aktywności głosowej działa po stronie wejściowej. Dwa wzory:

- Półdupleks: użytkownik mówi, model słucha. Model mówi, użytkownik słucha. Wyczyść przekazanie poprzez wykrywanie ciszy VAD (~200 ms).
- Pełny dupleks: oba mogą rozmawiać jednocześnie. Model może przełączać kanał zwrotny („aha”) lub przerywać. Znacznie trudniej. Moshi to popiera.

Qwen2.5-Omni domyślnie obsługuje półdupleks, z przejmowaniem kolei poprzez próg ciszy. Pełny dupleks wymaga obsługi w warstwie aplikacji.

### Qwen3-Omni (listopad 2025)

Następca. Myśliciel Qwen3-80B, większy Talker, ulepszony TMRoPE-v2. Opóźnienie zbliżone do 250 ms GPT-4o. Otwarte ciężary. Testy porównawcze na OmniBench konkurencyjne z Gemini 2.0 Live.

### Budżet opóźnienia produkcyjnego

W przypadku typowej interakcji podczas przesyłania strumieniowego:

- Mikrofon -> tokeny audio: 40-80 ms.
- Wstępne wypełnienie (podpowiedź + historia): 100-200 ms przy 7B, znacznie więcej przy 70B.
- Żeton tekstu Pierwszego Myśliciela: 40 ms.
- Talker przetwarza pierwszy token tekstowy: 20 ms.
- Zatwierdzenie pierwszych żetonów mowy: 40 ms.
- Dekodowanie resztkowe VQ: 30 ms.
- Dekodowanie przebiegu mowy: 50-80ms.

Całkowity TTFAB: 320–510 ms przy 7 B, 600–900 ms przy 70 B. Jakość graniczna zwykle oznacza 70B+; stąd graniczna luka w opóźnieniu.

### Matematyka dotycząca stawek tokenów

W przypadku mowy 16 kHz z podstawowymi tokenami mowy o częstotliwości 50 Hz potrzeba 50 tokenów mowy na sekundę sygnału wyjściowego. Talker musi emitować ≥50 tok/s, aby dotrzymać kroku. Przy typowej przepustowości LLM wynoszącej 30-80 tok/s na H100, mały (200-300M) Talker jest wystarczająco szybki; Talker 7B pozostałby w tyle.

Właśnie dlatego istnieją małe, dedykowane modele Talkerów, zamiast „tylko używać modelu głównego”.

## Użyj tego

`code/main.py`:

- Symuluje potok Thinker-Talker z próbnymi wskaźnikami emisji tokenów.
- Oblicza TTFAB dla konfigurowalnych rozmiarów modeli i częstotliwości próbkowania mikrofonu.
- Demonstruje wykonywanie skrętów w trybie półdupleksu z progiem ciszy VAD.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-omni-streaming-budget.md`. Biorąc pod uwagę docelowy TTFAB produktu głosowego w czasie rzeczywistym i zestaw funkcji (wizja, dwujęzyczność, pełny dupleks), wybiera Qwen2.5-Omni, Qwen3-Omni, Moshi lub Mini-Omni i dopasowuje rozmiar Thinkera/Talkera.

## Ćwiczenia

1. Twój docelowy TTFAB to 300ms. W przypadku Thinkera 7B i Talkera 300M zapisz opóźnienie każdego komponentu.

2. Qwen2.5-Omni wykorzystuje TMRoPE. Opisz, co widzi model w przypadku podpowiedzi, w której użytkownik zaczyna mówić w chwili t=1 s, a kamera rejestruje gest w chwili t=1,2 s.

3. Obsługa pełnego dupleksu wymaga, aby model emitował dźwięk podczas słuchania. Zaproponuj format danych szkoleniowych, który tego uczy.

4. Przeczytaj artykuł Moshiego, Część 4. Opisz separację „monologu wewnętrznego” i dlaczego pozwala ona uniknąć rozłamu Myśliciel – Mówca.

5. Oblicz budżet przepustowości: jak szybko Talker musi emitować tokeny, aby nadążać za mową 16 kHz przy 50 tokenach warstwy podstawowej/s?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Myśliciel | „Rozumny mózg” | Duży transformator generujący tekst, produkujący to, co powiedzieć |
| Mówca | „Usta wytwarzające mowę” | Mały transformator wytwarzający dyskretne żetony mowy z tekstu Myśliciela |
| TTFAB | „Budżet opóźnień” | Czas do pierwszego bajtu audio: od zakończenia mowy użytkownika do pierwszej próbki audio |
| TMRoPE | „Lina dostosowana do czasu” | Kodowanie pozycji przy użyciu bezwzględnych znaczników czasu w obrazie, dźwięku i tekście |
| Półdupleks | „Wykonywanie zakrętów” | Alternatywny użytkownik i model; Cisza VAD wykrywa wykonanie użytkownika |
| Pełny dupleks | „Jednoczesne” | Modelka potrafi jednocześnie mówić i słuchać; obsługa kanału zwrotnego |
| Wewnętrzny monolog | „Separacja Moshiego” | Projekt jednomodelowy, w którym strumień myślenia i strumień mówienia przeplatają się |

## Dalsze czytanie

- [Xu i in. — Qwen2.5-Omni (arXiv:2503.20215)](https://arxiv.org/abs/2503.20215)
- [Zespół Qwen — Qwen3-Omni (arXiv:2509.17765)](https://arxiv.org/html/2509.17765v1)
– [Xie i Wu — Mini-Omni (arXiv:2408.16725)](https://arxiv.org/abs/2408.16725)
- [Défossez i in. — Moshi (arXiv:2410.00037)](https://arxiv.org/abs/2410.00037)
- [Zeng i in. — GLM-4-Głos (arXiv:2412.02612)](https://arxiv.org/abs/2412.02612)