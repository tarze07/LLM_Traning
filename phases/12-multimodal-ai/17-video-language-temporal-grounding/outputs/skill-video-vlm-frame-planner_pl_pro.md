---

name: video-vlm-frame-planner
description: Planuje próbkowanie i pooling klatek, format wyjściowy oraz cele benchmarkowe na potrzeby wdrożenia modeli wideo-językowych (Video VLM).
version: 1.0.0
phase: 12
lesson: 17
tags: [video-vlm, temporal-grounding, tmrope, dynamic-fps, benchmarks]

---

Na podstawie zadania wideo (detekcja akcji, temporal grounding, podsumowania, monitoring, analiza pracy agentów) oraz ograniczeń wdrożeniowych (okno kontekstowe modelu, budżet opóźnień, przepustowość), wygeneruj plan próbkowania klatek i formatowania danych wyjściowych.

Wygeneruj:

1. **Strategia próbkowania klatek:** Próbkowanie jednolite (Uniform) dla stabilnych nagrań, dynamiczny FPS dla ruchu o zmiennej intensywności, próbkowanie sterowane zdarzeniami (Event-driven) dla dynamicznych akcji, lub próbkowanie klatek kluczowych i kontekstu w przypadku filmów fabularnych.
2. **Pooling klatek:** Rozdzielczość 2x2 dla zadań wymagających wysokiej szczegółowości, 3x3 jako standard, oraz 4x4 lub 6x6 w zadaniach agencyjnych, gdzie szeroki kontekst jest ważniejszy niż precyzja przestrzenna.
3. **Kodowanie pozycyjne czasu:** TMRoPE dla modeli z rodziny Qwen2.5-VL, wyuczone osadzenia czasowe dla mniejszych modeli, lub brak kodowania czasowego dla zadań analizy pojedynczych, krótkich klipów.
4. **Format danych wyjściowych:** Format JSON ze strukturą `{"event", "start", "end", "confidence"}` do temporal groundingu, czysty tekst do podsumowań, lub specjalne tokeny wplecione w treść (rozdzielane tokenami) w zadaniach hybrydowych.
5. **Plan benchmarków:** VideoMME do ogólnej weryfikacji, TempCompass do temporal groundingu, EgoSchema do długiego kontekstu. Określ oczekiwane wyniki.
6. **Budżet kontekstu i opóźnień:** Łączna liczba tokenów obliczana jako: `czas_trwania * FPS * tokeny_na_klatkę`. Wygeneruj ostrzeżenie, jeśli wynik przekracza 40% dopuszczalnego okna kontekstowego modelu.

Kryteria odrzucenia (Twarde reguły):
- Proponowanie jednolitego próbkowania w nagraniach o wysokiej dynamice ruchu. Gubi to kluczowe, nagłe zdarzenia.
- Zakładanie, że wyjście oparte na tokenach specjalnych jest łatwiejsze w analizie programistycznej niż format JSON. JSON jest znacznie bardziej niezawodny w integracji systemowej.
- Rekomendowanie Video-LLaMA w nowych projektach rozpoczynających się w 2026 roku lub później. Te przestarzałe architektury nie są już konkurencyjne.

Zasady odmowy (Rezygnacja z projektu):
- Jeśli czas trwania wideo wynosi > 10 minut, a dostępne okno kontekstowe to < 32k tokenów, odmów realizacji i zarekomenduj hierarchiczne podsumowywanie lub wyszukiwanie agencyjne (Lekcja 12.18).
- Jeśli wymagana dokładność mieści się w granicach 2 punktów procentowych od Gemini 2.5 Pro w benchmarku VideoMME, odrzuć otwarte modele klasy 7B i zalecaj wersje 32B+ lub modele komercyjne.
- Jeśli docelowa częstotliwość próbkowania w trybie dynamicznego FPS wynosi > 8 klatek na sekundę dla wideo o długości > 30 s na modelu 7B, odmów ze względu na zbyt duże opóźnienia i zalecaj nałożenie niższego limitu.

Dane wyjściowe: Jednostronicowy plan obsługi klatek wideo zawierający opis próbnika, stopień poolingu, rodzaj kodowania czasowego, format danych wyjściowych, cele benchmarkowe oraz oszacowanie zużycia kontekstu. Na końcu dodaj odnośniki do prac: arXiv 2502.13923 (Qwen2.5-VL) oraz 2306.02858 (Video-LLaMA).
