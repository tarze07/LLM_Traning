---

name: var-tokenizer-designer
description: Zaprojektuj wieloskalowy, resztkowy tokenizer VQ na potrzeby autoregresyjnego generowania obrazów metodą VAR (Next-Scale Prediction).
version: 1.0.0
phase: 8
lesson: 19
tags: [var, next-scale-prediction, vq-vae, residual-vq, image-generation, tokenizer]

---

Biorąc pod uwagę specyfikację obrazu docelowego (rozdzielczość, kanały, kolor vs skala szarości, rozmiar zbioru danych, budżet obliczeniowy modelu językowego (LM) na dalszym etapie, docelowy FID), wygeneruj:

1. Harmonogram skal (Scale Schedule). Lista K poziomów rozdzielczości od 1x1 do (H/p) x (W/p). Domyślnie stosuje się K=10 skal dla rozdzielczości 256x256 oraz K=14 dla 512x512. Uzasadnij wybór parametru K w odniesieniu do efektywnej długości sekwencji LM (sumy powierzchni wszystkich skal) oraz budżetu na równoległe przetwarzanie w ramach jednej skali.
2. Książka kodowa (Codebook). Pojedyncza, wspólna książka kodowa o rozmiarze V dla wszystkich skal (zazwyczaj 4096/8192/16384). Wybierz wartość V na podstawie rozmiaru zbioru danych i pojemności dekodera. Upewnij się, że wykorzystanie książki kodowej na wsadzie kalibracyjnym przekracza 50% – w przeciwnym razie zmniejsz wartość V.
3. Resztkowe współdzielenie (Residual Sharing). Potwierdź, że skale od 1 do K wspólnie rekonstruują reprezentacje ukryte (latents) poprzez sumowanie embeddingów ze skalowaniem w górę (resztkowy VQ). Określ rozmiar płata (patch size) p oraz architekturę bazową VAE (np. zastosowanie dyskryminatora w stylu VQGAN, waga straty percepcyjnej).
4. Dekoder. Mapowanie zsumowanych reprezentacji ukrytych VAE z powrotem na piksele. Wybierz dekoder VQGAN, oryginalny dekoder VAR lub lżejszy dekoder w stylu MAGVIT. Uzasadnij wybór w oparciu o docelowy FID oraz zużycie pamięci VRAM dekodera.
5. Kodowanie pozycji (Position Embeddings). Zastosowanie potrójnego kodowania (scale_index, row, col) z wyuczonym embeddingiem dla każdej skali oraz dwuwymiarowym kodowaniem sinusoidalno-cosinusowym (2D sin-cos) wewnątrz danej skali. Odrzuć płaskie kodowanie 1D; model LM wymaga etykiety skali do poprawnego warunkowania.

Odrzuć nieresztkowe, wieloskalowe tokenizery dla modeli VAR. Bez sumowania reszt cel prognozowania kolejnej skali staje się źle zdefiniowany, a model LM optymalizuje inny cel matematyczny niż ten opisany w publikacji naukowej VAR. Odrzuć stosowanie oddzielnych książek kodowych dla każdej skali, chyba że rozmiar V zostanie dopasowany do liczby pikseli na mniejszych skalach, a zjawisko zapadania się książki kodowej (codebook collapse) zostanie ograniczone. Odrzuć koncepcję prognozowania kolejnej skali (next-scale prediction), jeśli iloczyn K i średniej powierzchni skali przekracza maksymalną długość sekwencji LM pomniejszoną o rezerwę na prompt tekstowy.

Przykładowe dane wejściowe: „Rozdzielczość 256 x 256, warunkowanie klasami ImageNet, zbiór danych 1.2M, budżet LM 1.5B parametrów, docelowy FID poniżej 5.0”.

Przykładowy wynik:
- Harmonogram skal: K=10, rozmiary: 1, 2, 3, 4, 5, 6, 8, 10, 13, 16. Łącznie 671 tokenów.
- Książka kodowa: wspólna, V=4096. Oczekiwane wykorzystanie na poziomie 70–80% na zbiorze ImageNet przy rozdzielczości 256.
- Resztkowe współdzielenie: potwierdzone; p=16, architektura bazowa VQGAN ze stratą percepcyjną i adwersarialną, rekonstrukcja za pomocą sumowania resztkowego.
- Dekoder: dekoder VQGAN, 4 bloki upsamplingu, bez dodatkowego modułu wygładzającego (refiner).
- Kodowanie pozycji: potrójne (skala, wiersz, kolumna), wyuczony token skali + 2D sin-cos w obrębie skali.
