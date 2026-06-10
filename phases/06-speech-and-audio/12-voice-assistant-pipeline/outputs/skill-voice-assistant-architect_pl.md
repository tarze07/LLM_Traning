---

name: voice-assistant-architect
description: Stwórz pełną specyfikację asystenta głosowego — komponenty, budżet opóźnień, obserwowalność, zgodność — dla danego obciążenia.
version: 1.0.0
phase: 6
lesson: 12
tags: [voice-assistant, architecture, livekit, pipecat, compliance]

---

Biorąc pod uwagę przypadek użycia (konsument / obsługa klienta / dostępność / brzeg), oczekiwana skala (jednoczesne sesje, minuty/miesiąc), język, docelowe opóźnienia, zgodność (HIPAA, PCI, EU AI Act, CA SB 942), wynik:

1. Komponenty (7 warstw). Mikrofon + fragmentacja · VAD · streaming STT · LLM + narzędzia · streaming TTS · odtwarzanie · obsługa przerwań. Podaj dokładnego dostawcę/model dla każdego z nich.
2. Budżet opóźnień. Cele P50 / P95 / P99 na stopień, sumując się do docelowej wartości docelowej. Zaznacz, które etapy są niezależne, a które sekwencyjne.
3. Schemat wywołania narzędzia. Specyfikacja JSON dla każdego narzędzia + obsługa błędów + tekst zastępczy. Zawsze dołączaj ścieżkę „nie mogę pomóc”, którą LLM musi obrać, gdy dwukrotnie zawiedzie.
4. Bezpieczeństwo. Szybka ochrona przed wtryskiem, blokada klonowania głosu (jeśli TTS obsługuje klonowanie), bramka słów wybudzania (dla zawsze włączonej), redagowanie danych osobowych w logach, przechowywanie 30 dni.
5. Obserwowalność. P50/P95/P99 na etap · wskaźnik fałszywych przerwań · wskaźnik powodzenia wywołań narzędzia · WER na 100 połączeń · koszt za minutę · wskaźnik porzuceń.
6. Zgodność. Ujawnianie dźwięku („To jest asystent AI”), przypinanie regionu (dane UE w UE), przechowywanie dziennika audytu, ścieżka rezygnacji.

Odmawiaj zawsze włączonych wdrożeń bez słowa aktywacji. Odrzuć TTS, który nie jest przesyłany strumieniowo (dodaje opóźnienie związane z długością wypowiedzi). Odrzuć uśrednianie opóźnień bez P95 — koniec to miejsce, w którym użytkownicy odchodzą. Odmawiaj przechowywania nieprzetworzonego dźwięku &gt; 30 dni bez opinii prawnej.

Przykładowe wejście: „Asystent ułatwień dostępu dla użytkowników słabowidzących: interfejs głosowy do aplikacji poczty e-mail dla klientów indywidualnych. Angielski. P95 &lt; 600 ms. ~10 tys. jednoczesnych użytkowników”.

Przykładowe wyjście:
- Komponenty: sounddevice (WebRTC za pośrednictwem agentów LiveKit) · Silero VAD · Deepgram Nova-3 (angielski) · GPT-4o z narzędziami e-mail (read_message, compose_reply, mark_read) · Cartesia Sonic 2 streaming · WebRTC out · przerwanie=cancel-LLM-and-TTS przy uruchomieniu VAD.
- Budżet: przechwytywanie 120 ms + VAD 40 + STT 150 + LLM TTFT 100 + TTS TTFA 150 = 560 ms P95.
- Narzędzia: read_message({id}), compose_reply({message_id, body}), mark_read({id}), search({query}). Wszystkie zwracają JSON; LLM ma maksymalnie 2 próby na narzędzie, a następnie powraca do sytuacji „Nie mogłem tego zrobić — spróbuj inaczej”.
- Bezpieczeństwo: osłona szybkiego wtrysku (wykryj `ignore previous instructions`); obudź słowo „Hej Mail”; brak klonowania głosu (naprawiono głos Cartesia); redaguj treści e-maili w logach.
- Obserwowalność: monitorowanie produkcji AI Hamminga; histogramy Prometeusza dla poszczególnych etapów; alert w przypadku fałszywego przerwania &gt; 5% lub p95 > 800 ms.
- Zgodność: ujawnienie sztucznej inteligencji przy pierwszym użyciu; zgoda HIPAA wyłącznie na wiadomości medyczne; Użytkownicy z UE trafili na hostowaną w UE firmę Cartesia + GPT-4o w Irlandii.