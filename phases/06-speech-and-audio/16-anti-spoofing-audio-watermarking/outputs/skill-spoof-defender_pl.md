---

name: spoof-defender
description: Wybierz model wykrywania, znak wodny, manifest pochodzenia i podręcznik operacyjny na potrzeby wdrożenia generowania głosu/uwierzytelniania głosowego.
version: 1.0.0
phase: 6
lesson: 16
tags: [anti-spoofing, watermark, audioseal, asvspoof, c2pa, voice-fraud]

---

Biorąc pod uwagę obciążenie (generowanie głosu a uwierzytelnianie głosowe, skala wdrożenia, region zgodności, profil przeciwnika), wynik:

1. Wykrywanie (CM). AASIST · RawNet2 · NeXt-TDNN + WavLM · komercyjne (Pindrop, Validsoft). Dane szkoleniowe: ASVspoof 2019 / ASVspoof 5 / specyficzne dla domeny. Docelowy EER.
2. Znak wodny (gen wychodzący). AudioSeal 16-bitowe kodowanie ładunku `(model_id, user_id, generation_ts)` · WaveVerify (alt) · brak (z uzasadnieniem). Detektor działa w CI na każdym wyjściu przed statkiem.
3. Pochodzenie. Manifest C2PA podpisany kluczem instalatora · Metadane IPTC · brak (dla dźwięku innego niż konsumencki).
4. Strażnicy autoryzacji głosowej (jeśli dotyczy). Wyzwanie dotyczące żywotności (losowa fraza TTS + transkrypcja), wykrywanie ataku poprzez powtórzenie (model AASIST + PA), kalibracja progu biometrycznego na kanał.
5. Operacyjny. Przechowywanie dziennika audytu, przechowywanie artefaktów zgody (ponad 7 lat), sygnały wykrywania nadużyć (nagły wzrost wolumenu, monity o nazwanych podmiotach), procedura „kill-switch”.

Odmawiaj wdrażania generatorów głosu bez AudioSeal (lub równoważnego znaku wodnego). Odmawiaj wdrażania biometrii głosowej bez wykrywania fałszowania — klonowanie głosu sprawia, że ​​uwierzytelnianie tylko cosinusem jest łatwe do ominięcia. Odmów wdrożenia, które zależą wyłącznie od manifestu pochodzenia (możliwe do usunięcia). Progi wykrywania odmów przeszkolone w programie ASVspoof 2019 dla wdrożeń w świecie rzeczywistym bez konieczności przeprowadzania kalibracji kanału.

Przykładowe dane wejściowe: „IVR obsługi klienta banku. Odblokowanie biometryczne głosowe + agent głosowy generowany przez sztuczną inteligencję. 10 mln połączeń miesięcznie. USA + UE”.

Przykładowe wyjście:
- Wykrywanie: otwarta reklama Pindrop (preferowana) lub NeXt-TDNN + WavLM. Szkolenie z ASVspoof 5 + 100 tys. próbek połączeń specyficznych dla banku. Docelowy EER &lt; 0,5% na dane w domenie.
- Znak wodny: 16-bitowy ładunek AudioSeal na każdej wychodzącej wypowiedzi TTS; ładunek koduje identyfikator_banku + identyfikator_sesji + znacznik czasu. Detektor sprawdza przed transmisją.
- Pochodzenie: manifest C2PA dotyczący procesów eksportu plików audio do klientów; Połączenia tylko wewnętrzne są pomijane.
- Autentyka głosowa: wyzwanie na żywo przy każdym autoryzacji (losowa 4-cyfrowa fraza TTS; powtórzenia użytkownika + detektor + transkrypcja). Funkcja zapobiegania fałszowaniu działa przy każdej próbie uwierzytelnienia przychodzącego. Próg biometryczny na poziomie FAR 0,1%, FRR 1%.
- Operacyjne: 7-letnie przechowywanie zgody + dziennik audytu w regionie (dane UE – mieszkaniec UE). Powiadomienie o nagłej liczbie żądań klonowania &gt; 2σ; wyłącznik awaryjny po wykryciu nadużycia.