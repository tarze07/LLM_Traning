---

name: long-video-strategy-planner
description: Wybierz kontekst brutalny, uwagę pierścieniową, kompresję tokenów lub pobieranie agenta, aby uzyskać zadanie zrozumienia długiego wideo i obliczyć opóźnienie + oczekiwania dotyczące przypomnienia.
version: 1.0.0
phase: 12
lesson: 18
tags: [long-video, gemini, ring-attention, videoagent, retrieval]

---

Biorąc pod uwagę czas trwania filmu, złożoność zapytania (pojedyncze zdarzenie lub całościowe podsumowanie) oraz ograniczenia otwarte i zamknięte, wybierz strategię długiego wideo i wyemituj konfigurację.

Wyprodukuj:

1. Wybór strategii. Kontekst brutalny, uwaga pierścieniowa (LongVILA), kompresja tokenów (Video-XL) lub pobieranie agentów (VideoAgent).
2. Budżet tokenowy. Czas trwania * FPS * tokeny na klatkę. Ostrzegaj, jeśli > kontekst LLM.
3. Oczekiwane wycofanie. Przypominanie igły w stogu siana na percentylach długości wideo. W stosownych przypadkach cytuj raporty Gemini 1.5.
4. Opóźnienie. Czas wstępnego wypełnienia dla kontekstu brutalnego; pobieranie + VLM dla agenta.
5. Ścieżka inżynierska. Rusztowanie fragmentu kodu dla wybranej strategii.
6. Plan awaryjny. Hybryda: globalne podsumowanie w kontekście brutalnym + lokalne szczegóły agenta.

Twarde odrzucenia:
- Proponowanie brutalnego kontekstu dla 2-godzinnego filmu na otwartym modelu 72B. Kontekst nie pasuje.
- Żądanie odzyskania agenta zawsze wygrywa. W przypadku pytań o charakterze całościowym traci się brutalny kontekst.
- Zalecanie kompresji tokenów bez oznaczania podatku od wycofania.

Zasady odmowy:
- Jeśli celem jest 90-minutowy film wideo na granicy wycofania (>95%), odrzuć opcje otwarte i poleć Gemini 2.5 Pro.
- Jeśli użytkownika nie stać na pętle wywoływania narzędzi, odmów odzyskiwania agenta i zaproponuj skompresowany kontekst brutalny.
- Jeśli użytkownik potrzebuje transmisji w czasie rzeczywistym (strumieniowanie w trakcie odtwarzania), odmów pobierania (zbyt wolne) i zalecaj przesyłanie strumieniowe Qwen2.5-VL.

Wynik: jednostronicowy plan ze strategią, budżetem, wycofaniem, opóźnieniem, ścieżką inżynieryjną i rezerwą. Zakończ na arXiv 2403.05530 (Gemini 1.5) i 2403.10517 (VideoAgent) dla porównania.