---

name: video-brief
description: Przełóż zarys scenariusza wideo na wybór modelu, strukturę promptów oraz plan ujęć dla generatorów wideo (stan na 2026 rok).
version: 1.0.0
phase: 8
lesson: 10
tags: [video, diffusion, sora, veo, kling]

---

Biorąc pod uwagę krótki opis (brief) wideo (czas trwania, proporcje obrazu, styl, temat, ruch kamery, potrzeby dźwiękowe, kryteria wierności, budżet), wygeneruj:

1. Model + Hosting. Sora, Veo 3, Kling 2.1, Runway Gen-3, Pika 2.0, CogVideoX, HunyuanVideo, WAN 2.2 lub Mochi-1. Podaj jednozdaniowe uzasadnienie wyboru powiązane z czasem trwania, jakością i licencją.
2. Struktura promptu. (a) ruch kamery (ujęcie ustanawiające, śledzące, jazda kamery/dolly, ujęcie z kranu, kamera z ręki), (b) obiekt + akcja, (c) oświetlenie + stylistyka, (d) prompt negatywny lub parametry stylu. Celuj w 50–150 tokenów dla modelu Sora oraz 20–60 tokenów dla Runway.
3. Plan ujęć. Pojedynczy klip kontra montaż wielu ujęć (multi-shot), zakotwiczenie klatek kluczowych lub pierwszej klatki, wybór między generowaniem z obrazu (I2V - Image-to-Video) a z tekstu (T2V - Text-to-Video) dla każdego ujęcia.
4. Ziarno (Seed) + Odtwarzalność. Ziarno seed dla każdego ujęcia, wersja modelu (version pin), repozytorium użytych narzędzi.
5. Lista kontrolna jakości (QA). Weryfikacja klatka po klatce pod kątem migotania (flickering), spójności tożsamości postaci (identity consistency), błędów fizyki (physics violations) oraz zgodności ze znakami wodnymi.
6. Dźwięk. Natywny dźwięk w Veo 3; w innych przypadkach zewnętrzne systemy (np. ElevenLabs, Suno lub licencjonowane banki dźwięków + synchronizacja ruchu warg/lip-sync).

Odrzuć obietnicę wygenerowania >10 sekund ciągłego, spójnego ruchu w rozdzielczości 1080p na darmowych planach taryfowych (Pika, Kling i Runway ograniczają długość generacji do 10 sekund, dłuższe sekwencje są montowane/szyte z kilku klipów). Odrzuć zlecenia na generowanie wizerunku rzeczywistych osób bez ich zgody. Oznacz flagą ostrzegawczą wszelkie wymagania dotyczące generowania wideo 4K w czasie rzeczywistym w 2026 roku – obecnie standardowy czas generowania 6-sekundowego klipu 1080p na chmurowych końcówkach wynosi około 30 sekund.
