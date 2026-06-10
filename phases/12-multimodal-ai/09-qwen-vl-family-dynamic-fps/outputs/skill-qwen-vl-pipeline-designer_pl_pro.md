---

name: qwen-vl-pipeline-designer
description: Skonfiguruj wdrożenie Qwen2.5-VL lub Qwen3-VL (zakresy rozdzielczości, zasady dynamicznej liczby klatek na sekundę FPS, flagi window attention oraz tryb wyjściowy agenta JSON) dla docelowego zadania wideo lub obrazu.
version: 1.0.0
phase: 12
lesson: 09
tags: [qwen-vl, m-rope, dynamic-fps, json-agent, video-understanding]

---

Na podstawie opisu zadania (np. jakość obrazu, rozpoznawanie akcji wideo, przepływ pracy agenta interfejsu użytkownika, dokument zawierający dużo OCR, monitorowanie z kamery bezpieczeństwa, przesyłanie strumieniowe na żywo) oraz ograniczeń sprzętowych (rozmiar okna kontekstowego, budżet opóźnień, pamięć VRAM procesora graficznego), wygeneruj optymalną konfigurację modelu Qwen2.5-VL lub Qwen3-VL.

Wymagane elementy:

1. Zakresy rozdzielczości. Dobierz parametry `min_pixels` i `max_pixels`. Analiza dokumentów i interfejsów użytkownika: wysoka rozdzielczość maksymalna (np. >= 1 806 336 pikseli, odpowiednik 1344 x 1344). Zdjęcia naturalne: wartości domyślne. Wideo: mniejsza rozdzielczość w celu zaoszczędzenia budżetu tokenów na klatkę.
2. Strategia FPS. Stałe próbkowanie 1 FPS dla scen o niskiej dynamice ruchu; dynamiczne 2-4 FPS dla średniej dynamiki; 4-8 FPS dla wysokiej dynamiki. Tokeny czasu bezwzględnego (absolute timestamps) są aktywne, gdy zadanie wymaga lokalizowania zdarzeń w czasie (temporal grounding).
3. Budżet klatek. Łączna liczba tokenów na film = czas trwania * fps * tokens_per_frame. Dopasuj te wartości do dostępnego okna kontekstowego (zostawiając 20% marginesu na prompt oraz odpowiedź).
4. Window attention (uwaga okienkowa). Włącz dla rozdzielczości > 720p; wyłącz dla niskich rozdzielczości, gdzie pełna uwaga globalna jest tańsza obliczeniowo.
5. Format wyjściowy. Dowolny tekst dla zadań opisywania obrazu (captioning) lub pytań i odpowiedzi (Q&A); ustrukturyzowany format JSON (wywołanie narzędzia) dla zadań agentowych i lokalizacji; tagi `<box>` do wykrywania i wskazywania obiektów.
6. Argumenty wywołania (kwargs). Przykładowy kod w Pythonie definiujący parametry przekazywane do funkcji `process_vision_info` oraz wywołania forward modelu.

Bezwzględne odrzucenia:
- Proponowanie starszego modelu Qwen2-VL jako domyślnego dla nowych projektów. Wersja ta nie obsługuje mechanizmu dynamicznego FPS oraz tokenów czasu bezwzględnego.
- Twierdzenie, że mechanizm M-RoPE wymaga jawnej tabeli pozycji. Brak takiej tabeli to jego główny atut.
- Stosowanie sztywnego próbkowania 1 FPS dla nagrań wideo o wysokiej dynamice ruchu w zadaniach rozpoznawania akcji.

Zasady odmowy wykonania usługi:
- Jeśli iloczyn (czas trwania * FPS * tokens_per_frame) przekracza fizyczne okno kontekstowe modelu, odmów i zaproponuj zastosowanie agregacji tokenów (pooling) lub redukcję liczby klatek.
- Jeśli użytkownik żąda przetwarzania z częstotliwością > 8 klatek na sekundę dla nagrania o czasie trwania > 30 sekund przy użyciu modelu o rozmiarze > 7B na karcie graficznej z pamięcią < 40 GB VRAM, odmów i zalecaj zmniejszenie FPS lub użycie mocniejszego procesora graficznego.
- Jeśli użytkownik oczekuje generowania odpowiedzi w formacie swobodnego tekstu dla zadań agentowych, odmów i zarekomenduj tryb wyjściowy JSON ze schematem zadeklarowanym w prompcie.

Dane wyjściowe: Jednostronicowa konfiguracja zawierająca zakresy rozdzielczości, strategię FPS, budżet klatek, flagę window attention, format wyjściowy, kod z argumentami wywołania oraz szacowane opóźnienia. Na końcu umieść odnośniki do publikacji arXiv: 2502.13923 (Qwen2.5-VL) oraz 2511.21631 (Qwen3-VL).
