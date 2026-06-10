---

name: tts-designer
description: Zaprojektuj kompletny potok TTS, obejmujący wybór modelu, normalizację tekstu, wybór głosu referencyjnego oraz plan ewaluacji.
version: 1.0.0
phase: 6
lesson: 07
tags: [audio, tts, speech-synthesis]

---

Na podstawie zadanego celu (obsługiwane języki, ekspresja/styl głosu, budżet opóźnień, platforma sprzętowa CPU vs. GPU, ograniczenia licencyjne) oraz specyfiki treści (domena tekstowa, gęstość wyrazów spoza słownika OOV, bogactwo interpunkcji), określ:

1. Model: Kokoro / XTTS v2 / F5-TTS / VITS / StyleTTS 2 / komercyjne API. Podaj jednozdaniowe uzasadnienie wyboru.
2. Moduł przetwarzania tekstu (front-end): zakres normalizacji tekstu (liczby, daty, adresy URL), fonemizer (np. espeak-ng vs. g2p-en) oraz mechanizm rezerwowy (fallback) dla słów OOV.
3. Głos: nazwa gotowego profilu (preset) lub szczegółowe wymagania dotyczące nagrania referencyjnego do klonowania (czas trwania w sekundach, dopuszczalny poziom szumów, dopasowanie akcentu).
4. Parametry jakościowe: docelowe wartości UTMOS, dopuszczalny wskaźnik CER (mierzony modelem Whisper) oraz wskaźnik SECS w przypadku klonowania głosu.
5. Plan ewaluacji: Zbiór testowy składający się z co najmniej 20 wypowiedzi zawierających liczby, homografy, nazwy własne i zdania o złożonej strukturze.

Zasady weryfikacji:
- Odrzuć projekty wdrożenia systemów TTS w środowisku produkcyjnym, które nie zawierają dedykowanego modułu normalizacji tekstu.
- Odrzuć projekty klonowania głosu, które nie posiadają udokumentowanej zgody właściciela głosu oraz wbudowanego mechanizmu nakładania znaków wodnych (audio watermarking).
- Oznacz jako błąd próby wdrożenia modelu Kokoro dla języków nieobsługiwanych przez wybrane wagi (w oryginalnej wersji model ten wspiera wyłącznie język angielski).
