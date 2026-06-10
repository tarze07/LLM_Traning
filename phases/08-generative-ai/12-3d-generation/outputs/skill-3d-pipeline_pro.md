---

name: 3d-pipeline
description: Wybierz potok (pipeline) generowania lub rekonstrukcji 3D, biorąc pod uwagę rodzaj danych wejściowych, format wyjściowy oraz docelowy przypadek użycia.
version: 1.0.0
phase: 8
lesson: 12
tags: [3d, gaussian-splatting, nerf, mesh]

---

Biorąc pod uwagę rodzaj danych wejściowych (prompt tekstowy / pojedynczy obraz / kilka obrazów / sekwencja zdjęć / wideo), docelowy format wyjściowy (siatka (mesh) / 3D Gaussian Splatting / NeRF / chmura punktów) oraz przypadek użycia (renderowanie w czasie rzeczywistym, silnik gry, AR/VR, produkcja filmowa), wygeneruj:

1. Potok przetwarzania (Pipeline). (a) generowanie wielu widoków + dopasowanie 3D (np. SV3D, CAT3D + 3DGS), (b) bezpośrednia rekonstrukcja z jednego zdjęcia (np. LRM, TripoSR, InstantMesh), (c) generowanie siatki z tekstu z mapowaniem PBR (np. Meshy 4, Rodin Gen-1.5, Hunyuan3D 2.0), (d) fotogrametria + 3DGS (np. gsplat, Postshot, Scaniverse).
2. Model bazowy + Hosting. Wskaż konkretny model (otwarty lub hostowany). Uwzględnij ograniczenia licencyjne przy zastosowaniu komercyjnym.
3. Budżet iteracji. Oczekiwany czas generowania wstępnego wyniku (first output), koszt iteracji oraz strategia optymalizacji (refinement strategy).
4. Topologia + Materiały. Czy wymagany jest krok ponownego siatkowania (remeshing)? Wymagania dotyczące kanałów PBR (albedo, chropowatość/roughness, metaliczność/metallic, mapy normalnych)? Czy układ UV (UV layout) ma być generowany automatycznie, czy ręcznie?
5. Ewaluacja. Metryka SSIM dla niewidzianych kątów kamery (held-out views), współczynnik CLIP, wodoszczelność siatki (watertightness), liczba wielokątów (polycount), rozdzielczość tekstur.
6. Docelowa platforma. Unity / Unreal Engine / Blender / przeglądarka internetowa (three.js / Babylon.js) / AR (formaty USDZ / GLB).

Odrzuć rekomendacje bezpośredniego przesyłania plików 3DGS (3D Gaussian Splatting) do silnika gry bez uprzedniego kroku konwersji do siatki wielokątów (większość silników nie wspiera natywnego renderowania chmur punktów Gaussians). Odrzuć projekty generowania modeli 3D z tekstu w przypadku skomplikowanych postaci z ruchomymi stawami (articulated) – zamiast tego zaproponuj potok wspierający automatyczny rigging. Oznacz flagą ostrzegawczą generowanie wyłącznie w formacie NeRF, jeśli docelowe oprogramowanie (np. narzędzia DCC) nie obsługuje natywnego renderowania NeRF.
