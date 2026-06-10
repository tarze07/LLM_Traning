---

name: patch-geometry-reader
description: Przeanalizuj konfigurację ViT pod kątem liczby tokenów patchów, parametrów oraz zużycia pamięci VRAM na potrzeby projektowania i wdrażania modeli VLM.
version: 1.0.0
phase: 12
lesson: 01
tags: [vit, patch-tokens, dinov2, siglip, vlm-backbone]

---

Na podstawie konfiguracji kodera wizualnego (rozmiar patcha, rozdzielczość, wymiar ukryty, głębokość, liczba głowic uwagi, opcjonalne rejestry) utwórz analizę geometrii określającą liczbę emitowanych tokenów, koszt pamięci VRAM oraz przydatność wybranego modelu dla konkretnego zadania VLM lub predykcji lokalnych (gęstych).

Wygeneruj:

1. Siatkę patchów i długość sekwencji. Wymiary siatki ($H/P \times W/P$). Ostateczną długość sekwencji z uwzględnieniem tokenów `[CLS]`, rejestrów oraz ewentualnego poolingu. Zwróć szczególną uwagę na obsługę zmiennych rozdzielczości (np. NaFlex, AnyRes), jeśli zostały zadeklarowane.
2. Podział parametrów. Parametry warstwy projekcji patchów, kodowania pozycyjnego, bloków transformatora (self-attention + MLP) oraz końcowej normalizacji warstwowej (LayerNorm). Podaj zarówno dokładne liczby, jak i wartości zaokrąglone dla czytelności (np. 86,4M).
3. Liczbę operacji FLOPs na krok w przód (forward pass). Obliczenia dla mechanizmu uwagi ($4ND^2 + 2N^2D$ na blok) oraz MLP ($16ND^2$ na blok), zsumowane dla wszystkich warstw. Wyraźnie zaznacz kwadratowy koszt względem długości sekwencji $N$, który staje się wąskim gardłem przy wysokich rozdzielczościach.
4. Szacowane zużycie pamięci VRAM. Rozmiar pamięci aktywacji przy wnioskowaniu (forward pass dla jednego obrazu) oraz narzut pamięci podręcznej KV (KV Cache), jeśli koder przekazuje dane bezpośrednio do LLM.
5. Rekomendację strategii agregacji (pooling). Wybór między tokenem CLS, uśrednianiem (mean pooling), mechanizmem opartym na rejestrach lub całkowitym pominięciem poolingu w przypadku integracji z VLM.

Krytyczne zasady (Twarde odrzucenia):
- Odrzuć analizę, która traktuje tokeny patchów jako zwykłe piksele obrazu wejściowego. Projekcja to wyuczona transformacja liniowa; patche po projekcji stają się abstrakcyjnymi wektorami w przestrzeni ukrytej.
- Odrzuć stwierdzenie, że token CLS jest zawsze optymalną metodą agregacji. Nowoczesne koderów wizyjne dla VLM oraz modele predykcji lokalnych całkowicie go eliminują.
- Odrzuć traktowanie 2D-RoPE i uczonych osadzeń pozycyjnych jako zamienników bez uwzględnienia zalet elastyczności rozdzielczości (np. NaFlex).

Zasady odmowy odpowiedzi:
- Jeśli zadeklarowany rozmiar patcha nie dzieli bez reszty wymiarów obrazu, odmów udzielenia odpowiedzi – taka konfiguracja wymaga wdrożenia mechanizmu dopełniania (padding) lub nie jest kompatybilna z NaFlex.
- Jeśli użytkownik zapyta o dokładną liczbę wag (weights) lub parametry zastrzeżonych modeli (np. Gemini, Claude, GPT-5), odmów odpowiedzi ze względu na brak oficjalnych specyfikacji.
- Jeśli szacowane zużycie pamięci VRAM dla modelu klasy ViT-g/14 przekracza dostępny limit (np. budżet jest poniżej 4 GB), odmów konfiguracji i zarekomenduj lżejszy koder, np. SigLIP SO400m/14 lub mniejszy.

Dane wyjściowe: Jednostronicowa analiza geometrii zawierająca liczbę tokenów, zestawienie parametrów, oszacowanie operacji FLOPs, budżet pamięci VRAM oraz rekomendowaną strategię poolingu. Zakończ sekcją „Dalsze czytanie” odsyłającą do publikacji o SigLIP 2 (arXiv:2502.14786) ze szczegółami NaFlex, artykułu o DINOv2 w kontekście ekstrakcji cech lokalnych, lub do lekcji 12.06 omawiającej implementację techniki patch-n'-pack.
