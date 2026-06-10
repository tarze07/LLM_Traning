---

name: voice-cloner
description: Wybierz podejście do klonowania (zero-shot / konwersja / adaptacja), artefakt zgody, znak wodny i filtry bezpieczeństwa do wdrożenia klonowania głosu.
version: 1.0.0
phase: 6
lesson: 08
tags: [voice-cloning, voice-conversion, watermark, consent, safety]

---

Biorąc pod uwagę zadanie (język, dostępna długość referencyjna, budżet adaptacyjny, ograniczenia licencyjne, status zgody, skala wdrożenia), wynik:

1. Podejście. Klon zerowego strzału (F5-TTS / VibeVoice / Orpheus / OpenVoice V2) · Konwersja głosu (kNN-VC / OpenVoice V2 ton-kolor) · Adaptacja głośników (pełne dostrojenie XTTS v2 + LoRA / VITS).
2. Przygotowanie referencji Wymagana długość, SNR (≥ 20 dB), mono 16 kHz+, przycinanie ciszy, `ref_text` (musi dokładnie pasować do F5-TTS). Odrzuć odniesienia do łóżka muzycznego.
3. Artefakt zgody. Wyraźna nagrana zgoda właściciela głosu. Szablon: nazwa + data + cel + zakres + procedura unieważnienia. Przechowuj ponad 7 lat.
4. Znak wodny. Wbudowany 16-bitowy ładunek AudioSeal na każdym wyjściu. Skonfiguruj detektor w CI, aby zweryfikować obecność przed opublikowaniem dźwięku.
5. Filtry bezpieczeństwa. Natychmiastowa odmowa w przypadku określonej osoby (celebryty / polityka / osoby niepełnoletniej); limit stawek na użytkownika na godzinę; dziennik audytu każdej generacji klonów; wyłącznik awaryjny.

Odmawiaj klonowania statków bez strategii znaku wodnego. Odmawiaj klonowania znanych osobistości/polityków/nieletnich, niezależnie od wyrażonej zgody. Odrzuć referencje poniżej 3 s lub SNR &lt; 20dB. Odrzuć F5-TTS w przypadku wdrożeń komercyjnych (CC-BY-NC). Odrzuć klonowanie międzyjęzykowe bez wyraźnego zaznaczenia luki w przeniesieniu akcentu.

Przykładowe dane wejściowe: „Aplikacja ułatwiająca dostęp: pozwól pacjentowi z ALS zablokować głos, gdy jeszcze mówi, a następnie mów przez TTS po utracie głosu. Angielski, USA.”

Przykładowe wyjście:
- Podejście: OpenVoice V2 (MIT, zero-shot, 6 s odniesienia). Przypadek użycia dostępności z nieodłączną zgodą; pacjent jest właścicielem głosu.
- Przygotowanie referencyjne: nagraj klipy 5 × 6 s w warunkach jakości studyjnej (cichy pokój, mikrofon USB, 24 kHz). Przechowuj surowe + transkrypcje. Zbuduj odniesienie do środka ciężkości dla zapewnienia stabilności.
- Zgoda: podpis cyfrowy + potwierdzenie wideo potwierdzające cel („ponowne wykorzystanie głosu po diagnozie”), przechowywane na zaszyfrowanym wolumenie z okresem przechowywania 10 lat. Infolinia dotycząca odwołań.
- Znak wodny: 16-bitowe kodowanie ładunku AudioSeal `patient_id` + `clip_id`; detektor działa na każdej generacji w CI.
- Bezpieczeństwo: twarde filtrowanie monitów o nazwanych jednostkach; rejestruj każde pokolenie; ROI ograniczony do instancji aplikacji zalogowanej przez pacjenta. Brak ekspozycji API.