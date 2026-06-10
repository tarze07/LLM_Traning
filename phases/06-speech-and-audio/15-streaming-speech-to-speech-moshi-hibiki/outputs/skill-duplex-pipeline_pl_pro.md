---

name: duplex-pipeline
description: Wybierz architekturę pełnego dupleksu (Moshi) lub potoku kaskadowego (VAD + STT + LLM + TTS) dla głosowego agenta AI.
version: 1.0.0
phase: 6
lesson: 15
tags: [moshi, hibiki, full-duplex, voice-agent, streaming]

---

Na podstawie profilu obciążenia (docelowe opóźnienie, potrzeba wywoływania narzędzi, pokrycie językowe, budżet sprzętowy, chmura vs urządzenia brzegowe/edge) wygeneruj:

1. Architektura: pełny dupleks (Moshi / GPT-4o Realtime / Gemini Live) vs potok kaskadowy (LiveKit + STT + LLM + TTS, lekcja 12). Podaj uzasadnienie w jednym zdaniu.
2. Wybór modelu: Moshi, Hibiki, Hibiki-Zero, Sesame CSM, GPT-4o Realtime, Gemini 2.5 Live lub tradycyjny potok kaskadowy. Podaj uzasadnienie.
3. Skala i wydajność: koszt GPU na sesję (zapotrzebowanie pamięciowe Moshi), maksymalna liczba jednoczesnych sesji, wpływ zimnego startu.
4. Mechanizm wywoływania narzędzi (tool calling): w razie potrzeby – potok hybrydowy (dupleks + zewnętrzny LLM do obsługi wywołań narzędzi) lub czysty potok kaskadowy. Wyjaśnij kompromisy.
5. Pokrycie językowe: modele pełnego dupleksu często mają ograniczone wsparcie dla mniej popularnych języków; potoki kaskadowe dziedziczą szerokie możliwości wielojęzyczne z modeli LLM.

Odrzuć architekturę opartą wyłącznie na pełnym dupleksie dla agentów korporacyjnych wymagających wywoływania narzędzi (tool calling) lub wyszukiwania informacji (RAG) – Moshi to model konwersacyjny, a nie szkielet aplikacyjny agenta. Odrzuć architekturę czysto kaskadową dla agentów konwersacyjnych wymagających opóźnień poniżej 250 ms – czasy przetwarzania poszczególnych etapów sumują się i przekroczą ten limit. Odrzuć konfiguracje Moshi z liczbą jednoczesnych sesji na jedno GPU większą niż 4 ze względu na rywalizację o zasoby.

Przykładowe wejście: „Asystent głosowy do nauki języków – ćwiczenie płynności konwersacyjnej. Angielski + francuski. Czas reakcji < 250 ms. 10 tys. aktywnych użytkowników dziennie”.

Przykładowe wyjście:
- Architektura: pełny dupleks (full-duplex) za pomocą Moshi. Wymóg opóźnienia poniżej 250 ms oraz płynność konwersacji idealnie wpisują się w możliwości Moshi.
- Model: Moshi. Języki angielski (EN) i francuski (FR) są dobrze obsługiwane. Licencja CC-BY 4.0.
- Skala: jedno GPU L4 obsługuje 4-6 jednoczesnych sesji → ~1500 GPU w szczycie przy 10 tys. aktywnych użytkowników dziennie (DAU) i 10% współbieżności. Zaplanuj lekki tryb na urządzeniu (on-device) przy użyciu Kyutai Pocket TTS oraz lokalnego modelu Whisper na wypadek braku połączenia.
- Wywoływanie narzędzi: minimalne – funkcje takie jak „pokaż wskazówkę gramatyczną” lub „przetłumacz to zdanie” mogą być przekierowywane do małego modelu pomocniczego (sidecar LLM); większość interakcji to swobodny dialog, w którym Moshi sprawdza się najlepiej.
- Pokrycie językowe: EN + FR (wsparcie natywne); ES / DE / JP za pomocą adaptacji Hibiki-Zero (wymaga dostarczenia 1000 godzin nagrań audio dla każdego nowego języka).
