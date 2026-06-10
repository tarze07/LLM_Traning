---

name: codec-picker
description: Wybierz neuronowy kodek audio (EnCodec / DAC / SNAC / Mimi) dla danego zadania generatywnego lub kompresyjnego.
version: 1.0.0
phase: 6
lesson: 13
tags: [codec, encodec, dac, snac, mimi, rvq, semantic-tokens]

---

Biorąc pod uwagę zadanie (generatywny LM, kompresja, dialogi w trybie pełnego dupleksu, edycja muzyki, docelowa wierność), wynik:

1. Kodek. EnCodec-24k · EnCodec-48k · DAC-44.1k · SNAC-24k · Mimi · (rezerwa: Opus dla kompresji nieneuralnej). Powód w jednym zdaniu.
2. Liczba klatek na sekundę + książki kodowe. Budżet szybkości transmisji, liczba słowników (zwykle 4-12), długość sekwencji dla docelowego czasu trwania klipu.
3. Schemat tokenizacji. Płaskie vs hierarchiczne (SNAC) vs semantyczne + akustyczne (Mimi). Jak LM zużywa tokeny.
4. Dekoder. Dekoder w kodeku · Zewnętrzny wokoder (HiFi-GAN) · Tylko LM (bez wokodera, bezpośrednio przewiduje tokeny kodeka). Wyjaśnij dlaczego.
5. Implikacje szkoleniowe. Chcesz przeszkolić koder/dekoder? Dostroić dźwięk domeny (tylko mowa → muzyka specyficzna dla domeny)? Zamrożone z półki?

Odrzuć DAC dla obciążeń AR-LM przy napiętych budżetach opóźnień — częstotliwość klatek 86 Hz × 8 książek kodowych = 5504 tokenów na 10 s, za długo, aby zapewnić szybkie generowanie. Odrzuć Mimi w przypadku muzyki — jest dostosowana do mowy. Odrzuć EnCodec przy generowaniu semantyczno-warunkowym — brak semantycznego słownika kodów, niewyraźna mowa w tekście.

Przykładowe wejście: „Utwórz AR LM na potrzeby zamiany tekstu na mowę TTS. Docelowy TTFA 200 ms. Tylko w języku angielskim”.

Przykładowe wyjście:
- Kodek: Mimi. Podział semantyczny i akustyczny umożliwia faktoryzację tekstu → książki kodów 0 → książek kodów 1-7, która jest zarówno szybka, jak i obsługuje klonowanie głosu.
- Liczba klatek na sekundę + książki kodowe: 12,5 Hz · 8 książek kodowych · 4,4 kb/s. 10 s = 1000 żetonów.
- Tokenizacja: najpierw przewidź książkę kodową 0 na podstawie tekstu + odniesienia do mówiącego; następnie przewiduj książki kodowe 1-7, biorąc pod uwagę książkę kodową 0 + odniesienie do głośnika (wzór transformatora głębi).
- Dekoder: wbudowany dekoder Mimi, nie jest potrzebny zewnętrzny wokoder.
- Szkolenie: szkolenie tekstu na kodek LM; zamrozić Mimi.