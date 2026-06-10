---

name: duplex-pipeline
description: Wybierz architekturę pełnego dupleksu (Moshi) lub potoku (VAD + STT + LLM + TTS) dla obciążenia agenta głosowego.
version: 1.0.0
phase: 6
lesson: 15
tags: [moshi, hibiki, full-duplex, voice-agent, streaming]

---

Biorąc pod uwagę obciążenie (docelowe opóźnienie, potrzeby wywoływania narzędzi, pokrycie językowe, budżet sprzętowy, chmura a brzeg), dane wyjściowe:

1. Architektura. Pełny dupleks (Moshi / GPT-4o Realtime / Gemini Live) vs potok (LiveKit + STT + LLM + TTS, lekcja 12). Powód w jednym zdaniu.
2. Modelka. Moshi · Hibiki · Hibiki-Zero · Sesame CSM · GPT-4o Realtime · Gemini 2.5 Live · tradycyjny potok. Powód.
3. Skala. Koszt procesora graficznego na sesję (Moshi posiada miejsce), maksymalna liczba jednoczesnych sesji, wpływ na zimny start.
4. Ścieżka wywołania narzędzia. W razie potrzeby — potok hybrydowy (dupleks + zewnętrzny LLM dla wywołań narzędzi) lub czysty potok. Wyjaśnij kompromis.
5. Zasięg językowy. Modele z pełnym dupleksem obsługują wąskie języki; rurociągi dziedziczą wielojęzyczne możliwości LLM.

Odrzuć architekturę obsługującą wyłącznie pełny dupleks w przypadku agentów korporacyjnych, którzy wymagają wywoływania/odzyskiwania narzędzi — Moshi to model dialogu, a nie struktura agenta. Odmów tylko potoku dla agentów konwersacyjnych poniżej 250 ms — etapy sumują się. Odrzuć Moshi dla &gt; 4 równoczesne sesje na jednym procesorze graficznym — bezkonkurencyjne.

Przykładowe wejście: „Asystent głosowy do nauki języków — ćwiczenie płynności konwersacyjnej. Angielski + francuski. Czas reakcji < 250 ms. 10 tys. aktywności dziennie”.

Przykładowe wyjście:
- Architektura: full-duplex (Moshi). Wymóg opóźnienia poniżej 250 ms + płynność konwersacji pasują do mocnych stron Moshi.
- Modelka: Moshi. EN + FR oba dobrze obsługiwane. Licencja CC-BY 4.0.
- Skala: jeden procesor graficzny L4 na 4-6 równoczesnych sesji → ~1500 procesorów graficznych w szczycie dla 10 tys. DAU przy współbieżności 10%. Zaplanuj tryb oświetlenia na urządzeniu, korzystając z Kyutai Pocket TTS i lokalnego szeptu, aby uzyskać cichą ścieżkę.
- Wywołanie narzędzia: minimalne — „pokaż wskazówkę gramatyczną” i „przetłumacz to zdanie” można przekierować za pomocą małego wózka bocznego LLM; większość interakcji to otwarty dialog, w którym Moshi błyszczy.
- Zakres języków: EN + FR (ojczysty); ES / DE / JP poprzez adaptację Hibiki-Zero (wymagane 1000 godzin dźwięku na nowy język).