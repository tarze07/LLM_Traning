---

name: spoof-defender
description: Wybierz model detekcji fałszerstw (anti-spoofing), metodę znakowania wodnego, manifest pochodzenia danych oraz procedury operacyjne (playbook) dla systemów syntezy lub autoryzacji głosowej.
version: 1.0.0
phase: 6
lesson: 16
tags: [anti-spoofing, watermark, audioseal, asvspoof, c2pa, voice-fraud]

---

Na podstawie profilu obciążenia (generowanie głosu vs uwierzytelnianie głosowe, skala wdrożenia, wymogi zgodności/compliance w danym regionie, profil potencjalnego atakującego) wygeneruj:

1. Detekcja fałszerstw (Countermeasures - CM): AASIST, RawNet2, NeXt-TDNN + WavLM lub rozwiązania komercyjne (np. Pindrop, Validsoft). Dane treningowe: ASVspoof 2019 / ASVspoof 5 / zbiory dziedzinowe. Docelowa wartość EER (Equal Error Rate).
2. Znakowanie wodne (dla generowanego strumienia wychodzącego): 16-bitowe kodowanie ładunku AudioSeal `(model_id, user_id, generation_ts)`, WaveVerify (alternatywnie) lub brak (z uzasadnieniem). Detektor uruchamiany w potoku CI dla każdego generowanego pliku przed jego wysłaniem.
3. Pochodzenie danych (provenance): manifest C2PA podpisany kluczem instalatora, metadane IPTC lub brak (dla zastosowań innych niż konsumenckie).
4. Zabezpieczenia autoryzacji głosowej (jeśli dotyczy): testy żywotności (liveness challenge - np. losowa fraza wygenerowana przez TTS do powtórzenia + transkrypcja), detekcja ataków typu replay (model AASIST + PA), kalibracja progów biometrycznych dla poszczególnych kanałów transmisyjnych.
5. Procedury operacyjne: przechowywanie logów audytowych, przechowywanie zgód użytkowników (zgodnie z wymogami prawnymi, np. przez 7+ lat), wskaźniki nadużyć (nagłe skoki natężenia ruchu, podejrzane frazy w promptach), procedura natychmiastowego wyłączenia (kill-switch).

Odmawiaj wdrażania systemów generowania głosu bez integracji AudioSeal (lub równoważnego rozwiązania do znakowania wodnego). Odmawiaj wdrażania biometrii głosowej bez systemów detekcji fałszerstw (anti-spoofing) – klonowanie głosu sprawia, że samo porównanie podobieństwa cosinusowego (cosine similarity) jest łatwe do ominięcia. Odrzucaj projekty opierające się wyłącznie na manifestach pochodzenia (są one łatwe do usunięcia). Odmawiaj stosowania progów detekcji wytrenowanych na ASVspoof 2019 w rzeczywistych systemach produkcyjnych bez uprzedniej kalibracji dla docelowego kanału transmisyjnego.

Przykładowe wejście: „System IVR w bankowości detalicznej. Odblokowanie konta biometrią głosową + agent głosowy generowany przez AI. 10 mln połączeń miesięcznie. Obszar USA i UE”.

Przykładowe wyjście:
- Detekcja fałszerstw: komercyjne rozwiązanie Pindrop (rekomendowane) lub NeXt-TDNN + WavLM. Trening na ASVspoof 5 + 100 tys. nagrań specyficznych dla kanału bankowego. Docelowy EER < 0,5% na danych dziedzinowych.
- Znakowanie wodne: 16-bitowy ładunek AudioSeal dodawany do każdej wychodzącej frazy TTS; ładunek koduje `identyfikator_banku + identyfikator_sesji + znacznik_czasu`. Detektor sprawdza audio przed transmisją.
- Pochodzenie danych: manifest C2PA dodawany przy eksporcie plików audio wysyłanych do klientów; pomijany w wewnętrznych połączeniach telefonicznych.
- Autoryzacja głosowa: test żywotności (liveness test) przy każdej próbie autoryzacji (losowy 4-cyfrowy kod generowany przez TTS; powtórzenie kodu przez użytkownika -> detektor spoofingu + transkrypcja ASR). Blokada spoofingu aktywna przy każdym połączeniu przychodzącym. Próg biometryczny skalibrowany na FAR 0,1%, FRR 1%.
- Procedury operacyjne: przechowywanie zgód użytkowników przez 7 lat + logi audytowe w regionie (dane użytkowników z UE przetwarzane i przechowywane w UE). Alerty przy skokach liczby żądań klonowania głosu > 2σ; wdrożony wyłącznik awaryjny (kill-switch) w przypadku wykrycia nadużyć.
