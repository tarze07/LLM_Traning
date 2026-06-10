---

name: omni-streaming-budget
description: Rozmiar strumieniowego potoku głosowego Thinker-Talker (Qwen-Omni / Moshi / Mini-Omni) dla docelowego TTFAB i zestawu funkcji.
version: 1.0.0
phase: 12
lesson: 20
tags: [qwen-omni, moshi, mini-omni, streaming, ttfab, thinker-talker]

---

Biorąc pod uwagę specyfikację produktu skupiającą się na głosie (docelowy TTFAB, częstotliwość próbkowania mikrofonu, obraz w trybie tak/nie, dwujęzyczność, pełny dupleks) i ograniczenia obliczeniowe (klasa GPU, budżet), zwymiaruj potok Thinker-Talker.

Wyprodukuj:

1. Wybór rodziny modeli. Moshi (największe opóźnienie), Qwen2.5-Omni (najlepsze otwarte funkcje), Qwen3-Omni (jakość graniczna), Mini-Omni (najprostsza).
2. Rozmiary myśliciela i mówcy. Myśliciel 7B + rozmówca 200-300M dla <400ms TTFAB. 70B+ Myśliciel jakości, zaakceptuj wyższy TTFAB.
3. Podział TTFAB. Szacowanie opóźnienia komponent po komponencie.
4. Tryb dwustronny. Półdupleks z domyślną obsługą zwrotną VAD; pełny dupleks, jeśli produkt wymaga kanału zwrotnego.
5. Integracja wizji. TMRoPE z bezwzględnymi znacznikami czasu dla przeplatanych klatek wideo.
6. Kształt wdrożenia. Pojedyncza karta graficzna vs podział (Myśliciel na A, Talker na B) w zależności od potrzeb w zakresie przepustowości.

Twarde odrzucenia:
- Proponowanie Talkera 70B. Mówca musi być mały, aby nadążyć za szybkością tokenów mowy.
- Korzystanie z dekodera mowy niestrumieniowego. TTFAB eksploduje.
- Zamawianie pełnego dupleksu jest typu plug-and-play. Wymaga specjalistycznych danych szkoleniowych.

Zasady odmowy:
- Jeśli docelowy TTFAB <200ms, odrzuć wszystko większe niż klasa Moshi (połączone 7B) na pojedynczym A100.
- Jeśli produkt wymaga generowania muzyki w strumieniu, odrzuć tę architekturę i zaleć oddzielny potok muzyczny.
- Jeśli częstotliwość próbkowania mikrofonu wynosi 48 kHz przy ścisłej jakości, zaznacz potrzebę zastosowania silniejszego kodera mowy; nie próbkuj na ślepo.

Dane wyjściowe: jednostronicowy plan przesyłania strumieniowego z wyborem modelu, rozmiarami, podziałem TTFAB, trybem dupleksu, strategią wizji, wdrożeniem. Zakończ arXiv 2503.20215 (Qwen2.5-Omni), 2410.00037 (Moshi).