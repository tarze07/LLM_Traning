---

name: codec-picker
description: Dobierz optymalny kodek dla zadanego zadania syntezy generatywnej lub kompresji audio.
version: 1.0.0
phase: 6
lesson: 13
tags: [codec, encodec, dac, snac, mimi, rvq, semantic-tokens]

---

Na podstawie zadanego zadania (autoregresywny model językowy LM, kompresja sygnału, konwersacje dwukierunkowe full-duplex, edycja i aranżacja muzyki, docelowa wierność rekonstrukcji), określ:

1. Kodek: EnCodec (24k/48k) · DAC (44.1k) · SNAC (24k) · Mimi · (rozwiązanie rezerwowe: Opus dla kompresji klasycznej/nieneuronowej). Podaj jednozdaniowe uzasadnienie wyboru.
2. Częstotliwość ramek (frame rate) oraz liczbę książek kodowych: Budżet przepływności (bitrate), liczba książek kodowych (zazwyczaj 4–12) oraz całkowita długość sekwencji tokenów dla docelowego czasu nagrania.
3. Strukturę tokenów: Płaska vs. hierarchiczna (SNAC) vs. semantyczno-akustyczna (Mimi). Określ, w jaki sposób model LLM przetwarza tokeny.
4. Dekoder: Dekoder wbudowany w kodek · zewnętrzny wokoder (np. HiFi-GAN) · brak wokodera (bezpośrednie generowanie tokenów audio). Uzasadnij wybór.
5. Proces uczenia (Training Strategy): Czy trenujesz koder/dekoder od zera? Czy dostrajasz model do konkretnej domeny (np. ze specyfikacją na mowę lub instrumenty)? Czy korzystasz z gotowych wag (off-the-shelf)?

Zasady weryfikacji:
- Odrzuć model DAC w zadaniach autoregresywnych modeli językowych (AR-LM) z napiętym budżetem opóźnień (częstotliwość klatek 86 Hz x 8 książek kodowych daje aż 5504 tokenów na 10 sekund audio, co uniemożliwia generowanie o niskiej latencji).
- Odrzuć model Mimi w projektach generowania muzyki (Mimi jest zoptymalizowany pod kątem mowy).
- Odrzuć model EnCodec w zadaniach syntezy mowy z tekstu (generowanie warunkowane semantyką) bez dodatkowych warstw semantycznych (brak dedykowanej książki semantycznej prowadzi do bełkotliwej wymowy).

Przykładowe dane wejściowe: „Uczenie autoregresywnego modelu językowego (AR-LM) na potrzeby systemu TTS (Text-to-Speech). Docelowy czas do wygenerowania pierwszego dźwięku (TTFA) < 200 ms. Język angielski.”

Przykładowy wynik:
- Kodek: Mimi. Podział semantyczno-akustyczny pozwala na faktoryzację: tekst → codebook 0 → codebooks 1-7, co zapewnia bardzo szybkie generowanie i naturalne klonowanie głosu.
- Częstotliwość ramek + książki kodowe: 12.5 Hz · 8 książek kodowych · przepływność 4.4 kbps. 10 sekund audio przekłada się na zaledwie 1000 tokenów.
- Tokenizacja: Najpierw przewidywany jest token z pierwszej książki (codebook 0) na podstawie tekstu i profilu mówcy; następnie generowane są tokeny z książek 1-7 na podstawie wygenerowanej semantyki (codebook 0) oraz profilu mówcy (struktura hierarchiczna lub auto-regressive delay).
- Dekoder: Wbudowany dekoder modelu Mimi, nie ma potrzeby stosowania zewnętrznych wokoderów.
- Proces uczenia: Uczenie modelu LLM mapującego tekst na tokeny kodeka; wagi modelu Mimi pozostają zamrożone.
