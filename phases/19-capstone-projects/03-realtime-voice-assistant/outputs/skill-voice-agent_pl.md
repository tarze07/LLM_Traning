---

name: voice-agent
description: Zbuduj agenta głosowego działającego w czasie rzeczywistym z pierwszym wyjściem audio poniżej 800 ms, obsługą wtrącania się i wykorzystaniem narzędzi w połowie rozmowy.
version: 1.0.0
phase: 19
lesson: 03
tags: [capstone, voice, webrtc, livekit, pipecat, asr, tts, streaming]

---

Biorąc pod uwagę domenę (obsługa klienta, planowanie, asystent sprzedaży detalicznej), wdróż agenta głosowego WebRTC, który utrzymuje kompleksowe pierwsze wyjście audio w czasie krótszym niż 800 ms podczas obsługi wtrącenia, wywołań narzędzi i utraty pakietów.

Plan budowy:

1. Stwórz pokój LiveKit Agents 1.0 z klientem internetowym, który przesyła strumieniowo dźwięk z mikrofonu. Dodaj bramę Twilio PSTN, aby zapewnić zasięg telefonu.
2. Uruchom streaming ASR (hostowany Deepgram Nova-3 lub szybszy Whisper-v3-turbo na g5.xlarge). Subskrybuj transkrypcje częściowe i końcowe.
3. Uruchom Silero VAD v5 na klatkach 20 ms. Po zakończeniu mowy oceń ostatnią część za pomocą detektora skrętu LiveKit; zobowiąż się do zakończenia tury tylko wtedy, gdy wyciszenie VAD >= 500 ms i wynik ukończenia >= 0,6.
4. Przesyłaj strumieniowo LLM (GPT-4o-realtime, Gemini 2.5 Flash Live lub kaskadowo Claude Haiku 4.5). Przekaż pierwszy token TTS w ciągu 200 ms.
5. Przesyłaj strumieniowo TTS (Cartesia Sonic-2 lub ElevenLabs Flash v3). Pierwsza porcja audio musi opuścić serwer w ciągu 200 ms od pierwszego tokena LLM.
6. Wtargnięcie: gdy VAD wykryje mowę nowego użytkownika podczas MÓWIENIA lub MYŚLENIA, anuluj TTS, wyłącz pozostałe wyjście LLM, ponownie uzbrój ASR. Opublikuj zakres `tts_canceled`.
7. Kanał boczny narzędzia: jednoczesne uruchamianie wywołań funkcji; jeśli opóźnienie > 300 ms, wyemituj wypełniacz potwierdzający, aby strumień audio nigdy się nie zatrzymywał.
8. Nagraj 100 rozmów. Zmierz WER względem wstrzymanych transkryptów, współczynnika fałszywych odcięć w teście porównawczym Hamming VAD, pierwszego wyjścia audio p50, NISQA MOS i zachowania poniżej 3% spadku pakietów.
9. Przetestuj obciążenie 50 jednoczesnych wywołań na pojedynczym g5.xlarge z wywołaniem syntetycznym; zgłoś trwałe pierwsze wyjście audio s. 95.

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | Opóźnienie od końca do końca | p50 pierwsze wyjście audio poniżej 800 ms w 100 nagranych rozmowach |
| 20 | Jakość zwrotna | Wskaźnik fałszywej granicy poniżej 3% w porównaniu z benchmarkiem Hamming VAD |
| 20 | Poprawność użycia narzędzia | Wywołania narzędzi w trakcie rozmowy zwracają prawidłowe dane bez zatrzymywania dźwięku |
| 20 | Niezawodność w przypadku utraty pakietów | WER i stabilność wykonywania skrętów po wstrzyknięciu 3% spadku pakietów |
| 15 | Kompletność uprzęży Eval | Powtarzalne pomiary z konfiguracją publiczną |

Twarde odrzucenia:

— Potoki inne niż przesyłanie strumieniowe (wsadowe ASR, wsadowe TTS) nie mogą osiągnąć docelowego opóźnienia.
- Wszelkie zasady wtrącania się, które nie anulują natychmiast bufora TTS. Opóźnione anulowanie powoduje najgorszy spadek komfortu użytkownika.
- Wywołania narzędzi, które synchronicznie blokują strumień LLM. Muszą działać bocznym kanałem.

Zasady odmowy:

- Odmówić rozmieszczenia bez VAD lub detektora skrętu. Wykonywanie tur po ustalonym limicie czasu powoduje niedopuszczalne współczynniki odcięcia.
- Odmawiaj zgłaszania MOS bez udokumentowania, czy jest to dane oceniane przez człowieka, czy przez proxy NISQA.
- Odmowa zgłoszenia „opóźnienia p50 pod X” bez co najmniej 100 nagranych rozmów i opublikowania śladów połączeń.

Dane wyjściowe: repozytorium zawierające agenta LiveKit, konfigurację bramy PSTN, wiązkę ewaluacyjną obejmującą 100 połączeń, publiczny pulpit głosowy Langfuse, bezpośrednie porównanie z jednym hostowanym konkurentem (bezpośrednio Retell, Vapi lub OpenAI Realtime API) oraz opis trzech największych zaobserwowanych przez Ciebie błędów związanych z przejmowaniem kolei oraz dostrojenie detektora, które naprawiło każdy z nich.