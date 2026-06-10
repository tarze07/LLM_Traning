---

name: 3d-pipeline
description: Wybierz potok generowania lub rekonstrukcji 3D, biorąc pod uwagę typ danych wejściowych, format wyjściowy i przypadek użycia.
version: 1.0.0
phase: 8
lesson: 12
tags: [3d, gaussian-splatting, nerf, mesh]

---

Biorąc pod uwagę dane wejściowe (podpowiedź tekstowa / jeden obraz / kilka obrazów / przechwytywanie zdjęć / wideo), wynik docelowy (siatka / ikona Gaussa / NeRF / chmura punktów) i przypadek użycia (renderowanie w czasie rzeczywistym, silnik gry, AR / VR, kino), dane wyjściowe:

1. Rurociąg. (a) Rozpraszanie wielu widoków + dopasowanie 3D (SV3D, CAT3D + 3DGS), (b) bezpośrednie pojedyncze zdjęcie (LRM, TripoSR, InstantMesh), (c) zamiana tekstu na siatkę z PBR (Meshy 4, Rodin Gen-1.5, Hunyuan3D 2.0), (d) przechwytywanie zdjęć + 3DGS (Gsplat, Postshot, Scaniverse).
2. Model podstawowy + hosting. Nazwany model + otwarty / hostowany. Uwzględnij znaczenie licencji do użytku komercyjnego.
3. Budżet iteracji. Oczekiwany czas uzyskania pierwszego wyniku, koszt iteracji, strategia udoskonalenia.
4. Topologia + materiały. Czy potrzebna jest przepustka Remesh? Wymagania dotyczące kanału PBR (albedo, chropowatość, metaliczny, normalny)? Układ UV zautomatyzowany czy ręczny?
5. Ewaluacja. SSIM na widokach odsuniętych, wynik CLIP, wodoszczelność siatki, liczba poli, rozdzielczość tekstur.
6. Cel platformy. Unity / Unreal / Blender / web (three.js / Babylon) / AR (USDZ / glb).

Odmawiaj wysyłania 3DGS bezpośrednio do silnika gry bez przepustki konwersji siatki (większość silników nie renderuje natywnie ikon). Zrezygnuj z zamiany tekstu na 3D w przypadku skomplikowanych, artykułowanych znaków — zamiast tego użyj potoku obsługującego olinowanie. Oznacz dowolne wyjście tylko NeRF, gdy narzędzie podrzędne nie może renderować NeRF (większość narzędzi DCC).