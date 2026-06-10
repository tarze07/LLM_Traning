---

name: vad-tuner
description: Dobierz model VAD, próg czułości, parametry pre-roll i hangover oraz strategię detekcji tury dla zadanego scenariusza wdrożeniowego.
version: 1.0.0
phase: 6
lesson: 14
tags: [vad, silero, cobra, turn-detection, flush-trick]

---

Na podstawie zadanego scenariusza (konsumencki / call center / wbudowany edge / ułatwienia dostępu; charakterystyka szumów otoczenia; obsługiwane języki; budżet latencji), określ:

1. Model VAD: Silero VAD (domyślny) · Cobra VAD (rozwiązanie komercyjne) · pyannote.audio (na poziomie segmentacji/diaryzacji) · WebRTC VAD (legacy / dla mikrosystemów). Podaj jednozdaniowe uzasadnienie wyboru.
2. Parametry konfiguracyjne: Próg czułości (0.3–0.5), minimalny czas mowy (200–300 ms), czas podtrzymania ciszy / hangover (400–800 ms), bufor pre-roll (250–500 ms).
3. Semantyczny detektor tury (Semantic Turn Detector): Włączenie dodatkowego klasyfikatora (np. moduł detekcji tur LiveKit lub autorski model MLP). Uzasadnij potrzebę w oparciu o analizę stylu wypowiedzi użytkowników.
4. Technikę Flush (wymuszone czyszczenie bufora): Włączenie (jeśli silnik STT to wspiera, np. Kyutai lub Deepgram) lub wyłączenie. Oszacuj redukcję latencji end-to-end.
5. Zabezpieczenia (Guardrails): Ignorowanie nagrań o długości poniżej minimalnego progu; bezwzględne stosowanie bufora pre-roll; dynamiczne dostosowywanie czasu podtrzymania (hangover) per użytkownik; mechanizm awaryjny (fallback) na wypadek awarii usługi VAD (np. przejście na tryb ciągłego nasłuchu).

Zasady weryfikacji:
- Odrzuć projekty systemów produkcyjnych stosujące detektory VAD bazujące wyłącznie na energii sygnału (zbyt wysoka podatność na szumy otoczenia).
- Odrzuć konfiguracje ustawiające czas podtrzymania (hangover) na zero (prowadzi to do ciągłego przerywania wypowiedzi użytkowników).
- Odrzuć stosowanie modeli ASR (np. Whisper) bezpośrednio do zadań detekcji VAD, gdy dostępny jest dedykowany model Silero VAD (Whisper w tej roli jest wolniejszy i mniej precyzyjny).

Przykładowe dane wejściowe: „System IVR dla call center linii lotniczych służący do automatycznej zmiany rezerwacji biletów. Praca w zaszumionym otoczeniu (lotnisko). Język angielski i hiszpański. Latencja detekcji tury < 500 ms.”

Przykładowy wynik:
- VAD: Cobra VAD ze względu na najwyższą odporność na intensywny szum otoczenia. W przypadku ograniczeń budżetowych rozwiązaniem alternatywnym jest Silero VAD.
- Parametry konfiguracyjne: próg czułości 0.4 (z uwagi na wysoki poziom szumu tła); minimalny czas mowy 300 ms; czas podtrzymania ciszy (hangover) 600 ms (użytkownicy infolinii często robią pauzy na odczytanie numeru rezerwacji); bufor pre-roll 400 ms.
- Detektor semantyczny: Włączony detektor tur LiveKit – chroni przed przedwczesnym odcięciem użytkowników robiących pauzy na zastanowienie („Chciałbym zmienić lot... [pauza]... na jutro”).
- Technika Flush: Włączona (integracja ze strumieniowym API Deepgram). Oczekiwana redukcja latencji na końcu tury: z 400 ms do 150 ms.
- Zabezpieczenia: Automatyczne przełączenie na tryb ciągłego nasłuchu w przypadku braku odpowiedzi z serwera VAD; logowanie zdarzeń detekcji tury w celu późniejszego dostrajania parametrów.
