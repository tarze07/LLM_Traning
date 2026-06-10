---

name: decoupled-encoder-picker
description: Zdecyduj, czy zunifikowany VLM powinien oddzielić swoje kodery wizualne i wybrać pomiędzy Janus-Pro, JanusFlow i InternVL-U.
version: 1.0.0
phase: 12
lesson: 15
tags: [janus-pro, janusflow, internvl-u, decoupled-encoders, unified-model]

---

Biorąc pod uwagę specyfikację ujednoliconego modelu (zrozumienie + generowanie, opcjonalna edycja/malowanie), budżet obliczeniowy i ograniczenie otwartych wag, zalecamy architekturę oddzielonego kodera i konkretną konfigurację.

Wyprodukuj:

1. Wybór architektury. Janus-Pro (generacja VQ), JanusFlow (generacja wyprostowanego przepływu), InternVL-U (natywne uczenie wstępne + oddzielenie).
2. Kombinacja kodera. SigLIP-SO400m dla zrozumienia; MAGVIT-v2 / IBQ VQ do generacji dyskretnej; VAE typu SD3 do pracy ciągłej.
3. Plan etapu danych. Dopasowanie na etapie 1 (50–100 mln par), Ujednolicony etap 2 (70 mln+ par), Instrukcja na etapie 3 (1 mln+ próbek). Przytocz model Janus-Pro 5,4x + wynik skalowania danych 2,8x.
4. Strategia routingu. Oparte na znacznikach podpowiedzi (jawnie `<understand>` / `<generate>`) lub na klasyfikatorach zadań.
5. Inicjacja współdzielonego ciała. Inicjuj z wstępnie przeszkolonego LLM (DeepSeek, Qwen, Llama), a nie od zera.
6. Pułap jakości. Oczekiwane MMMU (~60 przy 7B) i GenEval (~0,80 przy 7B dla Janus-Pro / ~0,85+ dla InternVL-U).

Twarde odrzucenia:
- Proponowanie ujednoliconego modelu z jednym koderem (Show-o / Transfusion), gdy pasek jakości użytkownika dla obu stron jest konkurencyjny. Podejście oddzielone od produkcji jest jedyną drogą.
- Zalecenie wstępnego treningu od podstaw dla modelu <10B. Użyj ponownie wstępnie przeszkolonego ciała LLM.
- Proponowanie Janusa (oryginalnego) zamiast Janus-Pro dla każdego nowego projektu. Janus-Pro jest następcą.

Zasady odmowy:
- Jeśli użytkownik potrzebuje jedynie zrozumienia, odrzuć odsprzężenie i poleć rodzinę LLaVA. Wystarczy jeden koder.
- Jeśli użytkownik potrzebuje tylko generacji, odmów i poleć Stable Diffusion 3 / Flux - specjaliści i tak wygrywają na jakości T2I.
- Jeśli obliczono <50 tys. godzin GPU, odrzuć InternVL-U (wymaga natywnego szkolenia wstępnego) i poleć Janus-Pro (ponowne wykorzystanie wstępnie przeszkolonego LLM).

Dane wyjściowe: jednostronicowy plan z wyborem architektury, kombinacją koderów, planem etapów, routingiem, inicjowaniem współdzielonego ciała i pułapem jakości. Zakończ arXiv 2501.17811 (Janus-Pro), 2411.07975 (JanusFlow), 2603.09877 (InternVL-U).