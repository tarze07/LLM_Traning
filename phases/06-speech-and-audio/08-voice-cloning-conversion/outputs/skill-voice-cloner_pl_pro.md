---

name: voice-cloner
description: Zaprojektuj bezpieczny potok klonowania lub konwersji głosu, obejmujący wybór metody, przygotowanie nagrań referencyjnych, weryfikację zgody, osadzanie znaku wodnego oraz mechanizmy bezpieczeństwa.
version: 1.0.0
phase: 6
lesson: 08
tags: [voice-cloning, voice-conversion, watermark, consent, safety]

---

Na podstawie zadanego problemu (język, dostępny czas nagrań referencyjnych, dostępny czas/zasoby na adaptację, ograniczenia licencyjne, status zgody, skala wdrożenia), określ:

1. Metodę klonowania/konwersji: Klonowanie zero-shot (F5-TTS / VoiceBox / OpenVoice v2) · Konwersja głosu (KNN-VC / OpenVoice v2 z transferem barwy) · Adaptacja/dostrojenie do mówcy (pełny finetuning XTTS v2 / LoRA na VITS). Uzasadnij wybór.
2. Przygotowanie nagrań referencyjnych: Wymagana długość próbek, próg SNR (≥ 20 dB), format mono 16 kHz+, usunięcie ciszy, przygotowanie tekstu referencyjnego (`ref_text` - wymagane dopasowanie dla F5-TTS). Kategorycznie odrzuć próbki z podkładem muzycznym w tle (music beds).
3. Procedurę weryfikacji zgody: Protokół uzyskania wyraźnej, nagranej i podpisanej zgody właściciela głosu. Szablon zgody musi zawierać: imię i nazwisko, datę, cel i zakres użycia głosu, a także procedurę odwołania zgody (revocation). Rekordy należy przechowywać przez okres co najmniej 7 lat.
4. Cyfrowy znak wodny: Niesłyszalny 16-bitowy kod (np. AudioSeal lub SilentCipher) wbudowywany w każdą wygenerowaną próbkę. Skonfiguruj automatyczny detektor w potoku CI/CD, aby weryfikować obecność znaku przed udostępnieniem audio.
5. Zabezpieczenia (Safety Filters): Automatyczne blokowanie prób klonowania głosów osób publicznych (celebrytów, polityków) oraz osób nieletnich; limity zapytań (rate limiting) na użytkownika; kompletne logi audytowe (audit logs) dla każdej wygenerowanej próbki mowy; wyłącznik awaryjny (kill switch).

Zasady weryfikacji:
- Odrzuć wszelkie plany wdrożenia systemów klonowania głosu bez zaimplementowanej metody cyfrowego znakowania audio.
- Odrzuć projekty zakładające klonowanie głosów znanych osobistości, polityków lub nieletnich, niezależnie od rzekomego posiadania zgody.
- Odrzuć próbki referencyjne o długości poniżej 3 sekund lub o współczynniku SNR < 20 dB.
- Odrzuć zastosowanie F5-TTS w projektach komercyjnych bez weryfikacji ograniczeń licencyjnych (kod bazuje na licencji niekomercyjnej CC-BY-NC).
- Odrzuć projekty klonowania międzyjęzykowego (cross-lingual), które nie określają wprost metod radzenia sobie z obcym akcentem u mówcy docelowego.

Przykładowe dane wejściowe: „Aplikacja wspierająca dostępność: pacjent chory na ALS rejestruje swój głos, dopóki jest w stanie mówić, w celu późniejszego wykorzystania ga w systemie TTS po utracie mowy. Język angielski, USA.”

Przykładowy wynik:
- Metoda: OpenVoice v2 (licencja MIT, tryb zero-shot, próbka referencyjna 6 sekund). Scenariusz wsparcia dostępności z naturalną zgodą (pacjent jest jedynym użytkownikiem i właścicielem głosu).
- Przygotowanie nagrań referencyjnych: nagranie 5 próbek po 6 sekund każda w warunkach studyjnych (wyciszone pomieszczenie, mikrofon USB o wysokiej jakości, 24 kHz). Zapis surowego audio oraz transkrypcji. Uśrednienie wektorów cech (centroid) w celu stabilizacji barwy.
- Weryfikacja zgody: Podpis cyfrowy + nagranie wideo potwierdzające tożsamość i cel użycia („synteza własnego głosu po utracie mowy”), przechowywane na zaszyfrowanym dysku przez okres 10 lat. Zapewnienie infolinii i procedury usunięcia danych profilu.
- Cyfrowy znak wodny: 16-bitowy ładunek AudioSeal zawierający identyfikator pacjenta (`patient_id`) oraz identyfikator klipu (`clip_id`). Potok CI weryfikuje obecność znaku wodnego w każdym wyjściowym pliku audio.
- Zabezpieczenia: Blokowanie wszelkich nazw własnych i jednostek znanych (named entities) w tekście wejściowym; pełne logowanie operacji; dostęp ograniczony wyłącznie do profilu zalogowanego pacjenta. Brak publicznego API.
