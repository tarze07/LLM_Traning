---

name: unified-gen-model-picker
description: Dobierz architekturę spośród rodzin Show-o / Transfusion / Emu3 / Janus-Pro dla systemu wymagającego zarówno multimodalnego rozumienia, jak i generowania przy użyciu modeli open-weight.
version: 1.0.0
phase: 12
lesson: 14
tags: [show-o, masked-diffusion, unified, t2i, inpainting]

---

Na podstawie specyfikacji systemu produkcyjnego wymagającego zunifikowanego rozumienia i syntezy (np. zadania VQA, generowanie opisów, T2I oraz inpainting) przy ograniczeniu do modeli open-weight oraz określonym budżecie opóźnień (latency), wybierz optymalną rodzinę modeli i wygeneruj konfigurację referencyjną.

Wymagane elementy:

1. Rekomendacja rodziny modeli (werdykt). Wybór pomiędzy: Show-o (maskowana dyfuzja dyskretna), Transfusion / MMDiT (dyfuzja ciągła), Emu3 / Chameleon (dyskretna autoregresyjna) lub Janus-Pro (rozdzielone encodery).
2. Budżet kroków wnioskowania. 16 kroków dla Show-o, 20 kroków dla Transfusion, 1024+ kroków dla Emu3. Uzasadnij wybór budżetem opóźnień zadeklarowanym przez użytkownika.
3. Obsługa inpaintingu. Wyjaśnij łatwość wdrożenia: w Show-o funkcja ta jest dostępna bez dodatkowego treningu; Transfusion wymaga dodania kanału maski; Emu3 wymaga dedykowanego dostrajania.
4. Wybór tokenizatora. Dla modeli dyskretnych rekomenduj IBQ / MAGVIT-v2 / SBER-MoVQGAN; dla modeli operujących na reprezentacji ciągłej rekomenduj VAE z SD3.
5. Stabilność treningu. Uzasadnij, dlaczego trening z dwiema stratami w Transfusion wymaga precyzyjnego strojenia wag, podczas gdy pojedyncza strata w Show-o jest łatwiejsza w optymalizacji.
6. Ścieżka migracji. Plan przejścia z architektury Show-o na Transfusion w sytuacji, gdy wymagania jakościowe wizerunków produktu staną się priorytetem wdrożeniowym.

Bezwzględne odrzucenia:
- Proponowanie Emu3 / Chameleon w systemach, w których budżet opóźnień wnioskowania wynosi poniżej 10 sekund na obraz. Autoregresywne generowanie sekwencji ~1024 tokenów jest zbyt powolne.
- Twierdzenie, że Show-o oferuje jakość syntezy obrazów w pełni porównywalną do modeli Transfusion. Wierność rekonstrukcji w Show-o jest ograniczona kompresją tokenizera.
- Rekomendowanie tradycyjnych modeli dyfuzyjnych (np. Stable Diffusion) w systemach wymagających jednoczesnej obsługi zadań VQA.

Zasady odmowy wykonania usługi:
- Jeśli użytkownik wymaga czasu syntezy obrazu poniżej 2 sekund, odrzuć Show-o i rekomenduj wdrożenie Stable Diffusion oraz osobnego modelu VLM do zadań rozumienia (zaakceptuj konieczność utrzymywania wielu modeli jednocześnie).
- Jeśli użytkownik wymaga najwyższej jakości syntezy przy użyciu modeli open-weight, odrzuć Show-o / Emu3 i rekomenduj rodzinę Transfusion (MMDiT) lub JanusFlow.
- Jeśli użytkownik wyklucza stosowanie tokenizerów wizualnych (ze względu na ograniczenia licencyjne lub limity jakościowe rekonstrukcji), odrzuć modele dyskretne i rekomenduj Transfusion.

Dane wyjściowe: Jednostronicowa rekomendacja zawierająca werdykt, budżet kroków, analizę obsługi inpaintingu, rekomendację tokenizatora, plan stabilności treningu oraz ścieżkę migracji. Na końcu umieść odnośniki do publikacji arXiv: 2408.12528 (Show-o), 2408.11039 (Transfusion) oraz 2501.17811 (Janus-Pro).
