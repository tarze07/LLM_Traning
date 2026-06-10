---

name: video-vlm-frame-planner
description: Zaplanuj próbkowanie klatek, łączenie klatek, format wyjściowy i cele testów porównawczych na potrzeby wdrożenia modelu języka wideo.
version: 1.0.0
phase: 12
lesson: 17
tags: [video-vlm, temporal-grounding, tmrope, dynamic-fps, benchmarks]

---

Biorąc pod uwagę zadanie wideo (rozpoznawanie akcji, uziemienie tymczasowe, podsumowanie, monitorowanie, odtwarzanie przepływu pracy agenta) i ograniczenie wdrożenia (kontekst modelu, budżet opóźnień, przepustowość), wyemituj plan próbkowania klatek i plan wyjściowy.

Wyprodukuj:

1. Wybór próbnika klatek. Jednolity dla stałych treści, dynamiczny FPS dla ruchu mieszanego, sterowany zdarzeniami dla intensywnych akcji, klatka kluczowa + kontekst dla filmów.
2. Łączenie na klatkę. 2x2 dla dużej szczegółowości, 3x3 domyślnie, 4x4 lub 6x6 dla przepływów pracy agentów, gdzie gęstość treści ma mniejsze znaczenie niż pokrycie.
3. Kodowanie czasowe. TMRoPE dla rodziny Qwen2.5-VL; nauczone osadzanie czasowe dla mniejszych modeli; brak kodowania dla zadań pojedynczego klipu.
4. Format wyjściowy. JSON z `{event, start, end, confidence}` do uziemienia; dowolny tekst podsumowujący; rozdzielane tokenami dla przepływów mieszanych.
5. Plan porównawczy. VideoMME dla celów ogólnych, TempCompass dla uziemienia, EgoSchema dla długiego horyzontu. Określ oczekiwany poziom dokładności.
6. Budżet kontekstowy/opóźnieniowy. Łączna liczba tokenów = czas trwania * fps * tokens_per_frame. Ostrzegaj, jeśli przekracza 40% kontekstu.

Twarde odrzucenia:
- Proponowanie jednolitego próbkowania w przypadku filmów zawierających akcję. Traci szczytowe wydarzenia.
— Żądanie danych wyjściowych rozdzielanych tokenami odpowiada dokładności JSON na potrzeby analizowania dalszych danych. JSON jest bardziej niezawodny.
- Rekomendowanie Video-LLaMA dla dowolnego projektu rozpoczynającego się w 2026 roku. Starsze architektury nie są już konkurencyjne.

Zasady odmowy:
- Jeśli czas trwania > 10 minut i kontekst < 32k, refuse and recommend hierarchical summarization or agentic retrieval (Lesson 12.18).
- If target accuracy is frontier (within 2 points of Gemini 2.5 Pro on VideoMME), refuse open 7B models and require 32B+ or proprietary.
- If dynamic-FPS target > 8 w klipie trwającym > 30 s przy 7B, odmów ze względu na opóźnienia i zalecaj niższy limit.

Dane wyjściowe: jednostronicowy plan klatek z próbnikiem, łączeniem, kodowaniem tymczasowym, formatem wyjściowym, celami porównawczymi, oszacowaniem kontekstu. Zakończ arXiv 2502.13923 (Qwen2.5-VL) i 2306.02858 (Video-LLaMA) do odczytu porównawczego.