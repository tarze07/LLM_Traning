---

name: token-gen-cost-analyzer
description: Oblicz liczbę tokenów, opóźnienia wnioskowania oraz granicę jakości dla modeli autoregresywnych w stylu Emu3 i dobierz optymalne podejście pomiędzy Emu3 a modelami dyfuzyjnymi.
version: 1.0.0
phase: 12
lesson: 12
tags: [emu3, next-token-prediction, video-gen, diffusion, cfg]

---

Na podstawie specyfikacji produktu generatywnego (synteza obrazu lub wideo, docelowa rozdzielczość, wymagania jakościowe oraz przepustowość), oblicz liczbę tokenów generowanych w stylu Emu3, oszacuj opóźnienia wnioskowania (latency) i zarekomenduj wybór pomiędzy rodziną Emu3 a dedykowanymi modelami dyfuzyjnymi.

Wymagane elementy:

1. Liczba tokenów. Wyliczenie liczby tokenów na obraz przy określonym stopniu kompresji tokenizera (zazwyczaj 8x dla każdego wymiaru obrazu). Wyliczenie liczby tokenów dla wideo przy użyciu trójwymiarowego tokenizera 3D VQ (zazwyczaj bloki czasoprzestrzenne 4x4x4).
2. Opóźnienie wnioskowania (latency). Zależność (liczba tokenów / przepustowość w tokenach na sekundę) dla rodziny Emu3; porównanie z czasem wnioskowania w modelach dyfuzyjnych (iloczyn: liczba kroków odszumiania * czas jednego kroku). Podaj szacunkowe dane dla kart klasy NVIDIA A100 i H100.
3. Limit jakościowy (sufit). Jakość rekonstrukcji tokenizera wyrażona w PSNR (30-32 dB dla klasy IBQ), oczekiwane wartości FID w benchmarku MJHQ-30K oraz wskaźnik FVD dla wideo.
4. Konfiguracja Classifier-Free Guidance (CFG). Sugerowana waga współczynnika naprowadzania (gamma) w zależności od zadania; standardowo 3.0 dla generowania domyślnego, 5.0-7.0 dla zadań wymagających ścisłego dopasowania do promptu (prompt adherence).
5. Wybór (rekomendacja). Wybierz rodzinę Emu3, jeśli system wymaga zunifikowanego rozumienia i generowania obrazów lub elastyczności modalnej; wybierz dedykowane modele dyfuzyjne (np. SDXL, SD3, Flux), jeśli celem jest wyłącznie synteza obrazów przy rygorystycznych ograniczeniach czasu odpowiedzi.

Bezwzględne odrzucenia:
- Twierdzenie, że model Emu3 jest szybszy przy wnioskowaniu niż modele dyfuzyjne. Autoregresywne dekodowanie sekwencji tysięcy tokenów obrazu zawsze niesie ze sobą wysoki koszt stały.
- Rekomendowanie modeli z rodziny Emu3 bez zdefiniowania parametrów współczynnika CFG. Bez wdrożenia tej techniki jakość generowania drastycznie spada.
- Sugerowanie stosowania Emu3 do syntezy obrazów w wysokiej rozdzielczości (np. 4K). Przetwarzanie liczby tokenów dla rozdzielczości 2048x2048 i większych przepełnia pamięć podręczną KV Cache i zajmuje zbyt wiele czasu.

Zasady odmowy wykonania usługi:
- Jeśli budżet opóźnienia wnioskowania wynosi poniżej 5 sekund na obraz, odrzuć Emu3 i rekomenduj modele SDXL lub SD3.
- Jeśli produkt wymaga jednoczesnego generowania obrazów, ich opisywania (captioning) oraz analizy obrazów zewnętrznych, rekomenduj rodzinę Emu3 (ze względu na zunifikowaną funkcję straty); modele dyfuzyjne nie są w stanie zrealizować tych zadań bez dołączania osobnego modelu VLM.
- Jeśli użytkownik wymaga wag na licencji pozwalającej na pełne komercyjne zastosowanie, odmów rekomendowania Emu3 bez uprzedniej weryfikacji warunków licencyjnych (niektóre edycje modeli BAAI są przeznaczone wyłącznie do celów badawczych).

Dane wyjściowe: Jednostronicowy raport zawierający liczbę tokenów, szacowane opóźnienia, limit jakościowy rekonstrukcji, konfigurację współczynnika CFG oraz ostateczną rekomendację z uzasadnieniem. Na końcu umieść odnośniki do publikacji arXiv: 2409.18869 (Emu3) oraz 2408.11039 (Transfusion).
