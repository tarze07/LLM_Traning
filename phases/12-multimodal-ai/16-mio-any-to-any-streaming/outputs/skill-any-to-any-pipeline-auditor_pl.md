---

name: any-to-any-pipeline-auditor
description: Przeprowadź audyt konwersacyjnego projektu „każdy do dowolnego” i oblicz budżet opóźnień dla stosu z rodziny MIO / AnyGPT / Moshi.
version: 1.0.0
phase: 12
lesson: 16
tags: [mio, anygpt, moshi, any-to-any, streaming, ttfab]

---

Biorąc pod uwagę produkt konwersacyjny (mowa wejściowa / wymowa, opcjonalny obraz, opcjonalna muzyka), rozmiar modelu i docelowe opóźnienie, przeprowadź audyt projektu „każdy do dowolnego” i utwórz realną konfigurację.

Wyprodukuj:

1. Mieszanka modalności. Jakie moda w, jakie na zewnątrz. Wybierz rodzinę: MIO / AnyGPT (oddzielne tokeny, 4 modalności), Moshi (skoncentrowany na mowie i tekście, monolog wewnętrzny), Unified-IO 2 (bogaty w wizję).
2. Wspólny plan słownictwa. Zakresy identyfikatorów tekstu + obrazu + mowy + muzyki + separatorów. Całkowity rozmiar zazwyczaj 40-50 tys.
3. Stos tokenizerów. BPE + SEED + SpeechTokenizer-RVQ + Enkoder. Podkreśl, które nadal stanowią wąskie gardła (zazwyczaj jakość mowy).
4. Program szkolenia. Czteroetapowa receptura MIO lub dwuetapowa dla Moshi skoncentrowanego na mowie.
5. Budżet opóźnień TTFAB. Koder mikrofonu + wstępne wypełnienie + pierwszy token + dekodowanie resztkowe + dekoder mowy. Porównaj z paskiem konwersacyjnym ~500 ms.
6. Porównanie jakości i opóźnienia. Mniejszy model zapewniający małe opóźnienia, większy zapewniający wyższą jakość; przybliżone liczby na A100/H100.

Twarde odrzucenia:
- Proponowanie oddzielnych modeli dla każdej modalności, gdy wymagana jest płynność konwersacji. Opóźnienie potoku kumuluje się i jest gorsze.
- Używanie tokenizatora mowy z tylko 1 warstwą książki kodowej. Jakość będzie zautomatyzowana dla każdego głosu produkcyjnego.
- Twierdzenie, że TTFAB MIO odpowiada GPT-4o. Jeszcze nie; Moshi 160ms to najbliższy otwarty numer.

Zasady odmowy:
- Jeśli docelowy TTFAB <200 ms, odrzuć skalę MIO (8B+) i zaleć klasę Moshi (7B, dostrojoną do mowy) lub mniejszy model wyspecjalizowany w mowie.
- Jeśli użytkownik chce dźwięku o studyjnej jakości, odrzuć otwarte resztkowe VQ i polecaj ElevenLabs / chained-TTS, dopóki nie dogoni otwarta jakość (Qwen3-Omni / Moshi2).
- Jeśli użytkownik chce generować obraz podczas połączenia głosowego, odrzuć najpierw przesyłanie strumieniowe mowy i zaproponuj podzielony potok z przełączaniem trybów.

Dane wyjściowe: jednostronicowy audyt z mieszanką modalności, planem słownictwa, stosem tokenizatora, programem nauczania, opóźnieniem TTFAB, pareto opóźnienia jakościowego. Zakończ na arXiv 2409.17692 (MIO), 2410.00037 (Moshi), 2402.12226 (AnyGPT).