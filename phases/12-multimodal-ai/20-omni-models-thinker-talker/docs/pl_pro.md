# Modele klasy Omni: Qwen2.5-Omni i architektura Thinker-Talker

> Prezentacja GPT-4o w maju 2024 roku okazała się przełomowa nie tylko ze względu na sam model, ale przede wszystkim ze względu na formę interakcji: naturalny interfejs głosowy, w którym użytkownik mówi, model na bieżąco analizuje obraz z kamery i odpowiada w czasie krótszym niż 250 ms. W otwartym ekosystemie w latach 2024 i 2025 trwał wyścig, by osiągnąć podobną wydajność i płynność. Model Qwen2.5-Omni (marzec 2025) stał się referencyjną architekturą open-source opartą na podziale zadań: Thinker (duży transformator generujący tekst) oraz Talker (mniejszy, działający równolegle transformator generujący mowę), połączone strumieniowo przekazywanymi tokenami. Projekt Mini-Omni uprościł tę strukturę, Moshi zminimalizował opóźnienia, a GLM-4-Voice rozszerzył obsługę o język chiński. W tej lekcji przeanalizujemy architekturę Thinker-Talker oraz budżet opóźnień niezbędny do prowadzenia płynnego dialogu głosowego w czasie rzeczywistym.

**Typ:** Teoria / Wdrożenie
**Języki:** Python (biblioteka standardowa, symulator opóźnień potoku strumieniowego + pętla VAD)
**Wymagania wstępne:** Faza 12 · 19 (Modele audio-językowe), Faza 12 · 16 (MIO i multimodalne modele strumieniowe typu „any-to-any”)
**Czas:** ~180 minut

## Cele kształcenia

- Podział potoku wnioskowania na moduły Thinker (wnioskowanie tekstowe) oraz Talker (synteza mowy) i wyjaśnienie mechanizmu ich równoległego działania.
- Wyliczanie budżetu opóźnienia TTFAB (Time to First Audio Byte) dla interakcji głosowej z podziałem na poszczególne etapy.
- Opisanie działania mechanizmu TMRoPE (kodowanie pozycyjne wyrównane w czasie) dla obrazu, dźwięku i tekstu w module Thinker.
- Zestawienie trzech modeli konwersacji głosowej w czasie rzeczywistym: półdupleks (half-duplex), naprzemienna wymiana tur oraz pełny dupleks (full-duplex).

## Problem

Interaktywny asystent głosowy w czasie rzeczywistym musi realizować wiele wymagających zadań jednocześnie i z minimalnym opóźnieniem:

1. **Nasłuchiwanie:** Strumieniowa tokenizacja mowy i precyzyjne wykrywanie aktywności głosowej (VAD - Voice Activity Detection), aby natychmiast wykryć koniec wypowiedzi użytkownika.
2. **Analiza wizyjna:** Strumieniowanie klatek z kamery (2–4 FPS) do modułu Thinker równolegle z sygnałem audio.
3. **Wnioskowanie:** Generowanie odpowiedzi w oparciu o pełną historię konwersacji.
4. **Synteza mowy:** Przekładanie odpowiedzi na tokeny audio, dekodowanie ich do postaci fali dźwiękowej i natychmiastowe odtwarzanie.

Każdy z tych kroków wprowadza dodatkowe opóźnienie (latency). Aby rozmowa przebiegała naturalnie, łączne opóźnienie w obie strony (round-trip time) musi wynosić poniżej 500 ms – powyżej tej wartości człowiek zaczyna odczuwać dyskomfort i nienaturalne pauzy. GPT-4o osiąga opóźnienie na poziomie ok. 250 ms, Moshi schodzi do ok. 160 ms, natomiast Qwen2.5-Omni mieści się w przedziale 350–500 ms.

Wszystkie moduły w tym potoku muszą działać strumieniowo. Żaden etap nie może czekać na zebranie całego bloku danych (batching) przed przetworzeniem.

## Koncepcja

### Podział na Thinkera i Talkera

Architektura Qwen2.5-Omni opiera się na dwóch modułach:

- **Thinker:** Duży model LLM (7B-80B), który przetwarza przeplatane sekwencje tekstu, obrazu oraz tokenów audio. Na wyjściu generuje tokeny tekstowe reprezentujące treść odpowiedzi.
- **Talker:** Mały transformator (200M-1B) dedykowany do syntezy mowy. Przyjmuje tokeny tekstowe generowane przez Thinkera oraz kontekst audio i generuje dyskretne tokeny mowy (indeksy kwantyzacji RVQ).
- **Dekoder mowy:** Szybki, strumieniowy dekoder (np. SNAC lub rodzina MoVQGAN), przekształcający tokeny mowy na surowy sygnał audio.

Podział ten ma kluczowe znaczenie wydajnościowe. Thinker musi być dużą siecią, aby zachować wysokie zdolności rozumowania i analizy. Talker może być bardzo lekki, ponieważ jego zadanie jest czysto lokalne: przekształcić gotowy tekst na reprezentację mowy. Zwiększanie rozmiaru Talkera nie poprawia ekspresji, a jedynie spowalnia generowanie dźwięku.

Równoległe przetwarzanie w potoku:

1. Thinker generuje token tekstowy $t_i$.
2. Talker natychmiast strumieniowo odczytuje $t_i$ i generuje powiązane z nim tokeny mowy $s_i, s_{i+1}, \dots, s_{i+k}$.
3. Dekoder mowy na bieżąco odbiera tokeny mowy i generuje próbki audio.
4. Zanim Thinker wygeneruje kolejny token $t_{i+3}$, Talker z dekoderem odtwarzają już dźwięk dla wcześniejszej frazy $t_0 \dots t_{i+2}$.

### TMRoPE — pozycje multimodalne wyrównane w czasie

Moduł Thinker musi spójnie interpretować klatki obrazu (np. z częstotliwością 4 FPS), ramki audio (50 FPS) oraz tekst z historii konwersacji. Proste, liniowe ułożenie tych modalności w sekwencję (obrazy, następnie audio, następnie tekst) niszczy korelację czasową między nimi.

TMRoPE rozwiązuje ten problem, przypisując bezwzględne znaczniki czasu (timestamps) do każdego tokenu. Token wizyjny z momentu $t=2,3$ s, token audio z $t=2,32$ s i token tekstowy „stop” z $t=2,35$ s są powiązane czasowo. Mechanizm atencji RoPE obraca klucze i wartości na podstawie tych znaczników, dzięki czemu model naturalnie postrzega je jako zdarzenia współbieżne.

Jest to kluczowa innowacja pozwalająca na reakcję np. na gest machania ręką – model rejestruje klatkę wideo i powiązany z nią okrzyk w tym samym momencie fizycznym.

### Strumieniowa synteza mowy

Tokeny mowy muszą być generowane i odtwarzane w sposób ciągły. W projekcie Mini-Omni (Xie i Wu, 2024) pokazano model potrafiący jednocześnie słyszeć, myśleć i mówić strumieniowo: tokeny tekstowe z Thinkera i tokeny mowy z Talkera przeplatają się w tym samym potoku. Mówca rozpoczyna pracę natychmiast po wygenerowaniu kolejnego tokenu tekstowego przez Thinkera. Brak narzutu związanego z pakowaniem w paczki (batching).

Model Moshi (Défossez i in., październik 2024) to jedna z najszybszych otwartych implementacji tego typu, osiągająca TTFAB na poziomie 160 ms na pojedynczej karcie A100. Moshi opiera się na jednym modelu 7B, który generuje tekst i mowę w naprzemiennych krokach czasowych, korzystając z „wewnętrznego monologu” (inner monologue) do odseparowania procesu myślenia od syntezy głosu. Jest to w istocie zintegrowanie ról Thinkera i Talkera w jednej spójnej sieci.

### VAD i zarządzanie turami konwersacji

Moduł detekcji aktywności głosowej (VAD) zarządza stroną wejściową systemu. Stosuje się dwa główne schematy:
- **Półdupleks (naprzemienny):** Gdy użytkownik mówi, model słucha. Gdy model odpowiada, użytkownik słucha. Przełączanie tur następuje na podstawie detekcji ciszy przez moduł VAD (zazwyczaj próg wynosi ok. 200 ms).
- **Pełny dupleks (ciągły):** Obie strony mogą mówić jednocześnie. Model potrafi wtrącać krótkie potwierdzenia (np. „mhm”, „rozumiem”) oraz przerywać swoją wypowiedź, gdy użytkownik wejdzie mu w słowo. Jest to znacznie trudniejsze w realizacji. Moshi wspiera ten tryb natywnie.

Domyślnie Qwen2.5-Omni obsługuje tryb półdupleksu z przejmowaniem tur na podstawie progu ciszy. Obsługa pełnego dupleksu leży po stronie warstwy aplikacyjnej.

### Qwen3-Omni (listopad 2025)

Nowsza generacja modelu przynosi Thinkera opartego na Qwen3-80B, większy model Talker oraz ulepszony algorytm TMRoPE-v2. Pozwala to na skrócenie opóźnienia TTFAB do poziomu ok. 250 ms (zbliżonego do GPT-4o) przy zachowaniu otwartych wag modelu. W testach OmniBench model wykazuje wydajność porównywalną z komercyjnym Gemini 2.0 Live.

### Budżet opóźnień w środowisku produkcyjnym

W typowym scenariuszu interakcji głosowej rozkład opóźnień prezentuje się następująco:
- Konwersja sygnału z mikrofonu na tokeny audio: 40–80 ms.
- Przetwarzanie promptu i historii (prefill): 100–200 ms dla modeli 7B (znacznie więcej dla 70B).
- Generowanie pierwszego tokenu tekstu przez Thinkera: 40 ms.
- Przetworzenie tego tokenu przez Talkera: 20 ms.
- Wygenerowanie pierwszych tokenów mowy: 40 ms.
- Dekodowanie resztkowe RVQ: 30 ms.
- Synteza sygnału audio (Waveform decoding): 50–80 ms.

Łączny czas TTFAB wynosi ok. 320–510 ms dla modeli klasy 7B oraz 600–900 ms dla modeli 70B. Najwyższa jakość odpowiedzi wymaga modeli większych, co bezpośrednio przekłada się na wyższe opóźnienia początkowe.

### Matematyka prędkości generowania tokenów

Dla sygnału mowy 16 kHz przy podstawowej częstotliwości tokenów 50 Hz, system musi generować 50 tokenów audio na każdą sekundę wypowiedzi. Oznacza to, że moduł Talker musi osiągać przepustowość $\ge 50$ tok/s, aby odtwarzanie przebiegało płynnie i bez przerw. Podczas gdy duży model na karcie H100 generuje średnio 30–80 tok/s, zastosowanie małego, dedykowanego transformatora Talker (200M-300M) pozwala na bezproblemowe i tanie dotrzymanie tego kroku. Próba uruchomienia syntezy bezpośrednio na modelu klasy 7B mogłaby powodować zacinanie się generowanego głosu.

## Zastosowanie w kodzie

Plik `code/main.py` zawiera:
- Symulację potoku przetwarzania Thinker-Talker z wizualizacją tempa generowania tokenów.
- Kalkulator opóźnienia TTFAB dla różnych rozmiarów modeli i parametrów sprzętowych.
- Demonstrację zarządzania turami konwersacji w trybie półdupleksu przy użyciu prostego detektora aktywności głosowej (VAD).

## Rezultat

Do tej lekcji dołączono dokument `outputs/skill-omni-streaming-budget.md`. Na podstawie wymagań dotyczących opóźnienia TTFAB oraz zestawu funkcji (obsługa wideo, wielojęzyczność, pełny dupleks), ułatwia on dobór modelu (Qwen2.5-Omni, Qwen3-Omni, Moshi, Mini-Omni) oraz optymalizację rozmiaru modułów Thinker/Talker.

## Ćwiczenia

1. Zakładając cel TTFAB na poziomie 300 ms, rozpisz dopuszczalne limity opóźnień dla poszczególnych komponentów przy konfiguracji: Thinker 7B + Talker 300M.
2. Wyjaśnij na przykładzie mechanizmu TMRoPE, w jaki sposób model Qwen2.5-Omni interpretuje sytuację, gdy użytkownik zaczyna mówić w sekundzie $t=1$,0, a kamera rejestruje jego gest w sekundzie $t=1,2$.
3. Implementacja pełnego dupleksu wymaga, aby model potrafił analizować głos użytkownika w tym samym czasie, gdy sam generuje wypowiedź. Zaproponuj strukturę danych treningowych, która pozwala nauczyć model takiego zachowania.
4. Przeczytaj sekcję 4 publikacji o modelu Moshi. Wyjaśnij, czym jest „wewnętrzny monolog” (inner monologue) i dlaczego eliminuje on potrzebę fizycznego rozdzielania modelu na osobne moduły Thinker i Talker.
5. Oblicz budżet przepustowości: jak szybko Talker musi generować tokeny mowy, aby nadążyć za odtwarzaniem audio 16 kHz przy 50 tokenach bazowych na sekundę?

## Kluczowe pojęcia

| Termin | Potoczne określenie | Co to dokładnie oznacza |
| :--- | :--- | :--- |
| **Thinker (Myśliciel)** | „Mózg systemu” | Duży transformator tekstu odpowiedzialny za wnioskowanie, analizę wejścia i formułowanie treści odpowiedzi. |
| **Talker (Mówca)** | „Głos systemu” | Mały, szybki transformator generujący tokeny mowy na podstawie tekstu wyjściowego z Thinkera. |
| **TTFAB (Time to First Audio Byte)** | „Opóźnienie odpowiedzi” | Czas mierzony od momentu zakończenia wypowiedzi przez użytkownika do usłyszenia pierwszego fragmentu odpowiedzi audio. |
| **TMRoPE** | „Czasowe RoPE” | Kodowanie pozycyjne uwzględniające bezwzględny czas rejestracji danych dla tokenów wideo, audio i tekstu. |
| **Półdupleks (Half-duplex)** | „Wymiana tur” | Tryb naprzemienny, w którym użytkownik i model nie mówią jednocześnie; tury są przełączane przez detektor VAD. |
| **Pełny dupleks (Full-duplex)** | „Dialog ciągły” | Tryb, w którym model potrafi jednocześnie mówić i nasłuchiwać użytkownika (obsługuje przerywanie i wtrącenia). |
| **Wewnętrzny monolog** | „Metoda Moshi” | Podejście jednomodelowe, w którym reprezentacja myśli i mowy jest generowana w przeplatanych krokach tego samego transformatora. |

## Literatura uzupełniająca

- [Xu i in. — Qwen2.5-Omni (arXiv:2503.20215)](https://arxiv.org/abs/2503.20215)
- [Zespół Qwen — Qwen3-Omni (arXiv:2509.17765)](https://arxiv.org/html/2509.17765v1)
- [Xie i Wu — Mini-Omni (arXiv:2408.16725)](https://arxiv.org/abs/2408.16725)
- [Défossez i in. — Moshi (arXiv:2410.00037)](https://arxiv.org/abs/2410.00037)
- [Zeng i in. — GLM-4-Voice (arXiv:2412.02612)](https://arxiv.org/abs/2412.02612)
