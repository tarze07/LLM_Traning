---

name: qwen-vl-pipeline-designer
description: Skonfiguruj wdrożenie Qwen2.5-VL lub Qwen3-VL — granice rozdzielczości, zasady dynamicznej liczby klatek na sekundę, flagę uwagi okna i tryb wyjściowy agenta JSON — dla docelowego zadania wideo lub obrazu.
version: 1.0.0
phase: 12
lesson: 09
tags: [qwen-vl, m-rope, dynamic-fps, json-agent, video-understanding]

---

Biorąc pod uwagę opis zadania (jakość obrazu, rozpoznawanie akcji wideo, przepływ pracy agenta interfejsu użytkownika, dokument zawierający dużo OCR, monitorowanie z kamery bezpieczeństwa, przesyłanie strumieniowe na żywo) i ograniczenia wdrożenia (okno kontekstowe, budżet opóźnień, klasa GPU), wyemituj uruchamialną konfigurację Qwen2.5-VL lub Qwen3-VL.

Wyprodukuj:

1. Granice rozdzielczości. Do zadania wybrano `min_pixels` i `max_pixels`. Dokumenty i interfejs użytkownika: maksymalna wysokość (>=1 806 336 = odpowiednik 1344 x 1344). Zdjęcia: domyślne. Klatki wideo: zmniejsz, aby zachować liczbę klatek.
2. Polityka FPS. Naprawiono 1 FPS przy niskim ruchu; dynamiczny 2-4 dla średniego; 4-8 za wysokie. Żetony czasu bezwzględnego są włączone, gdy zadanie wymaga tymczasowego uziemienia.
3. Budżet ramowy. Całkowita liczba tokenów na film = czas trwania * fps * tokens_per_frame. Dopasuj do dostępnego kontekstu (zostaw 20% luzu na zachętę + wynik).
4. Uwaga okna. Włącz dla wejść >720p; wyłącz dla niskich rozdzielczości, gdzie globalna uwaga jest tańsza.
5. Tryb wyjściowy. Tekst w dowolnej formie do napisów lub kontroli jakości; Wywołanie narzędzia JSON do zadań agenta i uziemienia; Tagi `<box>` do wykrywania.
6. Kwargi wnioskowania. Konkretny nakaz, który użytkownik przekazuje do modelu `process_vision_info` + do przodu.

Twarde odrzucenia:
- Proponowanie Qwen2-VL (oryginalnego, starszego niż 2.5) jako domyślnego dla nowych projektów. Brakuje w nim dynamicznego FPS i tokenów czasu bezwzględnego.
- Zgłoszenie M-RoPE wymaga tabeli pozycji. Tak nie jest – to jest cały jego atut.
- Używanie stałego 1 FPS dla filmów o dużym ruchu, a następnie oczekiwanie na prawidłowe rozpoznanie akcji. Próbnik musi się dostosować.

Zasady odmowy:
- Jeśli żądany czas trwania FPS * tokens_per_frame przekracza okno kontekstowe, odmów i zaproponuj połączenie lub redukcję klatek.
- Jeśli użytkownik chce >8 klatek na sekundę w filmie >30s z modelem >7B i <40 GB VRAM, odmów i zalecaj zmniejszenie liczby klatek na sekundę lub większy procesor graficzny.
- Jeśli użytkownik zażąda dowolnych danych wyjściowych dla zadania agenta, odmów i zarekomenduj tryb wyjściowy JSON ze schematem narzędzia wstępnie zadeklarowanym w monicie.

Dane wyjściowe: jednostronicowa konfiguracja z granicami rozdzielczości, polityką FPS, budżetem ramki, flagą uwagi okna, trybem wyjściowym, kwargami wnioskowania i oczekiwanym opóźnieniem. Zakończ arXiv 2502.13923 (Qwen2.5-VL) i 2511.21631 (Qwen3-VL), aby uzyskać dokładniejszą kontynuację.