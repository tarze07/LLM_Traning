---

name: voice-assistant-architect
description: Zaprojektuj kompletną specyfikację techniczną potoku asystenta głosowego (architektura, opóźnienia, obsługa błędów, zgodność z przepisami).
version: 1.0.0
phase: 6
lesson: 12
tags: [voice-assistant, architecture, livekit, pipecat, compliance]

---

Na podstawie zadanego scenariusza (segment B2C / obsługa klienta / ułatwienia dostępu / wdrożenie lokalne edge), oczekiwanej skali (liczba jednoczesnych sesji, liczba minut/miesiąc), języka, docelowej latencji oraz wymogów prawnych i regulacyjnych (HIPAA, PCI-DSS, EU AI Act, California SB 942), określ:

1. Komponenty potoku (7 warstw): Przechwytywanie audio (mikrofon + buforowanie) · bramkowanie VAD · strumieniowy STT/ASR · model LLM + narzędzia (Tool Calling) · strumieniowy TTS · odtwarzacz audio · obsługa przerwań (barge-in). Wskaż konkretnego dostawcę i model dla każdej z warstw.
2. Budżet opóźnień (latencji): Cele P50 / P95 / P99 dla każdego etapu przetwarzania, sumujące się do docelowej latencji end-to-end. Określ, które etapy zachodzą asynchronicznie, a które sekwencyjnie.
3. Projekt wywoływania funkcji (Tool Calling): Specyfikacja parametrów w formacie JSON dla każdego narzędzia, schemat obsługi błędów oraz komunikaty zastępcze (fallbacks). Zdefiniuj ścieżkę postępowania w przypadku dwukrotnego niepowodzenia wywołania narzędzia przez model LLM.
4. Bezpieczeństwo (Safety & Privacy): Zabezpieczenia przed atakami typu Prompt Injection, ochrona przed nieautoryzowanym klonowaniem głosu (jeśli model TTS na to pozwala), detekcja słowa budzącego (Wake Word) dla systemów działających w tle, anonimizacja danych osobowych (PII redaction) w logach, czas przechowywania danych (retention policy) ograniczony do 30 dni.
5. Monitorowanie i metryki (Observability): Metryki P50/P95/P99 dla każdego modułu potoku · wskaźnik fałszywych przerwań (false interruption rate) · skuteczność wywołań narzędzi (tool call success rate) · wskaźnik WER na reprezentatywnej próbie 100 połączeń · koszt jednostkowy za minutę połączenia · wskaźnik przedwcześnie rozłączonych połączeń (drop rate).
6. Zgodność z przepisami (Compliance): Ujawnienie interakcji z botem AI („Rozmawiasz z asystentem głosowym AI”), lokalizacja i suwerenność danych (data pinning, np. przetwarzanie danych obywateli UE wyłącznie w regionach UE), przechowywanie logów audytowych, obsługa rezygnacji (opt-out).

Zasady weryfikacji:
- Odrzuć projekty systemów działających w tle (always-on) bez zaimplementowanego modułu detekcji słowa budzącego (Wake Word).
- Odrzuć modele TTS, które nie wspierają strumieniowego generowania audio (generowanie całości tekstu dodaje latencję zależną od długości zdania).
- Odrzuć plany ewaluacji bazujące na średniej latencji bez podania percentyla P95 – wysokie opóźnienia brzegowe są najczęstszą przyczyną porzucania rozmowy przez użytkowników.
- Odrzuć projekty zakładające przechowywanie surowego audio użytkowników dłużej niż przez 30 dni bez udokumentowanej zgody prawnej.

Przykładowe dane wejściowe: „Asystent ułatwień dostępu dla osób słabowidzących: głosowy interfejs do obsługi poczty elektronicznej. Język angielski. Latencja P95 < 600 ms. Około 10 000 jednoczesnych użytkowników”.

Przykładowy wynik:
- Komponenty: biblioteka `sounddevice` (integracja WebRTC poprzez LiveKit Agents) · Silero VAD · Deepgram Nova-3 (angielski) · GPT-4o z zestawem narzędzi pocztowych (read_message, compose_reply, mark_read, search) · Strumieniowy model Cartesia Sonic 2 · odtwarzacz WebRTC · mechanizm przerwania: VAD aktywuje natychmiastowe anulowanie zadań LLM i TTS.
- Budżet opóźnień: przechwytywanie audio 120 ms + VAD 40 ms + STT 150 ms + LLM TTFT 100 ms + TTS TTFA 150 ms = 560 ms P95.
- Narzędzia: `read_message({id})`, `compose_reply({message_id, body})`, `mark_read({id})`, `search({query})`. Wszystkie wejścia/wyjścia w formacie JSON; model LLM ma maksymalnie 2 próby wywołania danego narzędzia, w przypadku trwałego błędu przechodzi do komunikatu: „Nie udało mi się wykonać tego działania, spróbuj sformułować polecenie inaczej”.
- Bezpieczeństwo: Moduł chroniący przed Prompt Injection (wykrywanie fraz typu `ignore previous instructions`); słowo budzące „Hej Mail”; brak klonowania głosu (sztywno przypisany profil głosu z biblioteki Cartesia); automatyczne usuwanie treści maili i danych osobowych z logów systemowych.
- Monitorowanie: Integracja z platformą Hamming AI; histogramy Prometheusa dla każdego modułu potoku; alerty dla administratorów w przypadku wzrostu wskaźnika fałszywych przerw powyżej 5% lub latencji P95 powyżej 800 ms.
- Zgodność z przepisami: Komunikat informujący o asystencie AI przy rozpoczęciu nowej sesji; suwerenność danych: wagi i serwery Cartesia oraz instancje GPT-4o uruchamiane w regionach UE (np. Irlandia) dla użytkowników łączących się z Europy.
