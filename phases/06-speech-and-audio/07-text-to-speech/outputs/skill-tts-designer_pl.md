---

name: tts-designer
description: Wybierz model TTS, głos, zakres normalizacji tekstu i plan oceny dla danego języka, stylu i docelowego opóźnienia.
version: 1.0.0
phase: 6
lesson: 07
tags: [audio, tts, speech-synthesis]

---

Biorąc pod uwagę cel (języki, styl głosu, budżet opóźnień, procesor vs GPU, ograniczenia licencyjne) i treść (domena, gęstość OOV, bogactwo interpunkcji), wynik:

1. Modelka. Kokoro / XTTS v2 / F5-TTS / VITS / StyleTTS 2 / komercyjne API. Powód w jednym zdaniu.
2. Nakładka tekstowa. Zakres normalizacji (liczby, daty, adresy URL), fonemizer (espeak-ng vs g2p-en), rezerwa OOV.
3. Głos. Nazwa ustawienia wstępnego lub specyfikacja klipu referencyjnego (sekundy, poziom szumów, dopasowanie akcentu).
4. Cele jakościowe. Celuj w UTMOS, CER poprzez szept, SECS podczas klonowania.
5. Plan ewaluacji. Zestaw testów składający się z 20 wypowiedzi obejmujący liczby, homografy, rzeczowniki własne i długie zdania.

Odrzuć jakikolwiek produkcyjny TTS bez normalizatora tekstu. Odmawiaj klonowania głosu bez zgody użytkownika i znaku wodnego. Oznacz dowolne wdrożenie Kokoro z prośbą o mówienie w językach innych niż angielski.