# Generacja 3D

> 3D to moda, w której efekt dźwigni 2D do 3D jest najsilniejszy. Przełomem w roku 2023 było rozpryskiwanie gaussowskie 3D. Generacyjne warstwy push na lata 2024–2026 z wieloma widokami i rekonstrukcją 3D na górze w celu wytworzenia obiektów i scen z jednego monitu lub zdjęcia.

**Typ:** Ucz się
**Języki:** Python
**Wymagania:** Faza 4 (Wizja), Faza 8 · 07 (Utajona Dyfuzja)
**Czas:** ~45 minut

## Problem

Treści 3D są bolesne:

- **Reprezentacja.** Siatki, chmury punktów, siatki wokseli, pola odległości ze znakiem (SDF), neuronowe pola promieniowania (NeRF), Gaussa 3D. Każdy ma kompromisy.
- **Niedobór danych.** ImageNet ma 14 milionów obrazów. Największy czysty zbiór danych 3D (Objaverse-XL, 2023) zawiera około 10 milionów obiektów, większość o niskiej jakości.
- **Pamięć.** Siatka wokseli 512³ to 128M wokseli; przydatna scena NeRF potrzebuje 1M próbek/promień. Pokolenie jest trudniejsze niż rekonstrukcja.
- **Nadzór.** W przypadku obrazu 2D istnieją piksele. W przypadku 3D zwykle masz kilka widoków 2D i musisz przejść do 3D.

Stos 2026 oddziela te dwa problemy. Najpierw wygeneruj *obrazy 2D z wieloma widokami* z modelem dyfuzyjnym. Po drugie, dopasuj *reprezentację 3D* (zwykle rozpryski gaussowskie) do tych obrazów.

## Koncepcja

![Generacja 3D: rozproszenie wielu widoków + rekonstrukcja 3D](../assets/3d-generacja.svg)

### Reprezentacja: trójwymiarowe rozpryski gaussowskie (Kerbl et al., 2023)

Reprezentuj scenę jako chmurę ~1M Gaussów 3D. Każdy ma 59 parametrów: pozycja (3), kowariancja (6 lub kwaternion 4 + skala 3), nieprzezroczystość (1), kolor harmoniki sferycznej (48 na stopniu 3, 3 na stopniu 0).

Renderowanie = projekcja + kompozycja alfa. Szybki (~100 kl./s przy 1080p na 4090). Różniczkowalne. Dopasuj poprzez gradientowe zejście do zdjęć z ziemi. Scena mieści się w 5–30 minut na konsumenckim procesorze graficznym.

Na górze dwie innowacje na lata 2023–2024:
- **Generatywne plamy Gaussa.** Modele takie jak LGM, LRM, InstantMesh przewidują chmurę Gaussa bezpośrednio na podstawie jednego lub kilku obrazów.
- **Rozpryski gaussowskie 4D.** Gaussa z przesunięciem na klatkę dla dynamicznych scen.

### Rozpraszanie wielu widoków

Dostosuj wstępnie wytrenowany model dyfuzji obrazu, aby wygenerować wiele spójnych widoków tego samego obiektu na podstawie podpowiedzi tekstowej lub pojedynczego obrazu. Zero123 (Liu i in., 2023), MVDream (Shi i in., 2023), SV3D (Stability, 2024), CAT3D (Google, 2024). Zwykle generuje 4-16 widoków wokół obiektu, podniesionych do 3D za pomocą rozpryskiwania Gaussa lub NeRF.

### Potoki zamiany tekstu na 3D

| Modelka | Wejście | Wyjście | Czas |
|-------|-------|-------|------|
| DreamFusion (2022) | tekst | NeRF przez SDS | ~1 godzina na zasób |
| Magic3D | tekst | siatka + tekstura | ~40 minut |
| Shap-E (OpenAI, 2023) | tekst | ukryte 3D | ~1 minuta |
| SJC / ProlificDreamer | tekst | NeRF / siatka | ~30 minut |
| LRM (Meta, 2023) | obraz | trójpłatowiec | ~5 s |
| InstantMesh (2024) | obraz | siatka | ~10 s |
| SV3D (Stabilność, 2024) | obraz | nowatorskie poglądy | ~2 minuty |
| CAT3D (Google, 2024) | 1-64 obrazy | 3D NeRF | ~1 minuta |
| TripoSR (2024) | obraz | siatka | ~1 s |
| Siatka 4 (2025) | tekst + obraz | siatka PBR | ~30 s |
| Rodin Gen-1.5 (2025) | tekst + obraz | siatka PBR | ~60 s |
| Tencent Hunyuan3D 2.0 (2025) | obraz | siatka | ~30 s |

Kierunek 2025-2026: bezpośrednie modele tekstu na siatkę z materiałami PBR odpowiednimi dla silników gier. Pośredni etap dyfuzji z wieloma widokami jest nadal najskuteczniejszą receptą na obiekty ogólne.

### NeRF (dla kontekstu)

Pole promieniowania neuronowego (Mildenhall i in., 2020). Mały MLP pobiera `(x, y, z, view direction)` i generuje `(color, density)`. Renderuj poprzez całkowanie wzdłuż promieni. Jakość przewyższa syntezę nowego widoku opartą na siatce, ale renderowanie jest 100–1000 razy wolniejsze. Zastąpiony przez rozpryskiwanie Gaussa w większości zastosowań w czasie rzeczywistym, ale nadal dominujący w badaniach.

## Zbuduj to

`code/main.py` implementuje zabawkowe dopasowanie 2D „rozprysków gaussowskich”: przedstawia syntetyczny obraz docelowy (gładki gradient) jako sumę dwuwymiarowych ikon gaussowskich. Optymalizuj pozycje, kolory i kowariancje poprzez opadanie gradientu, aby dopasować je do celu. Widzisz dwie podstawowe operacje: renderowanie w przód (splat + alfa-kompozyt) i dopasowanie przez opadanie gradientu.

### Krok 1: ikona Gaussa 2D

```python
def gaussian_at(x, y, gaussian):
    px, py = gaussian["pos"]
    sigma = gaussian["sigma"]
    d2 = (x - px) ** 2 + (y - py) ** 2
    return math.exp(-d2 / (2 * sigma * sigma))
```

### Krok 2: renderuj przez zsumowanie ikon

```python
def render(image_size, gaussians):
    img = [[0.0] * image_size for _ in range(image_size)]
    for g in gaussians:
        for y in range(image_size):
            for x in range(image_size):
                img[y][x] += g["color"] * gaussian_at(x, y, g)
    return img
```

Prawdziwe rozpryskiwanie gaussowskie 3D sortuje Gaussa według głębokości i kolejności alfa-kompozytów. Nasza zabawka 2D po prostu podsumowuje.

### Krok 3: dopasowanie poprzez opadanie gradientowe

```python
for step in range(steps):
    pred = render(size, gaussians)
    loss = mse(pred, target)
    gradients = compute_grads(pred, target, gaussians)
    update(gaussians, gradients, lr)
```

## Pułapki

- **Niespójność widoku.** Jeśli niezależnie wygenerujesz 4 widoki i nie zgadzają się one co do struktury obiektu, dopasowanie 3D będzie rozmyte. Poprawka: rozpowszechnianie wielu widoków ze wspólną uwagą.
- **Halacynacja od tyłu.** Pojedynczy obraz → 3D musi wymyślić niewidzialną stronę. Jakość jest bardzo zróżnicowana.
- **Eksplozja plam Gaussa.** Nieograniczony trening wzrasta do 10 milionów ikon i przetrenowania. Niezbędne są heurystyki zagęszczania i przycinania (z oryginalnego papieru 3D-GS).
- **Problemy z topologią.** Siatki z pól ukrytych (SDF) często mają dziury lub samoprzecięcia. Przed wysyłką uruchom remesher (np. remesh woksela blendera).
- **Licencja na dane szkoleniowe.** Objaverse posiada licencje mieszane; zastosowanie komercyjne różni się w zależności od modelu.

## Użyj tego

| Zadanie | wybór 2026 |
|------|-----------|
| Rekonstrukcja sceny ze zdjęć | Rozpryskiwanie Gaussa (3DGS, Gsplat, Scaniverse) |
| Obiekt zamiany tekstu na 3D dla gier | Meshy 4 lub Rodin Gen-1.5 (wyjście PBR) |
| Obraz do 3D | Hunyuan3D 2.0, TripoSR, InstantMesh |
| Synteza nowatorskiego spojrzenia na kilka obrazów | CAT3D, SV3D |
| Rekonstrukcja sceny dynamicznej | Rozpryskiwanie Gaussa 4D |
| Awatar / ubrany człowiek | Awatar Gaussa, Uściski |
| Badania / SOTA | Cokolwiek spadło w zeszłym tygodniu |

Do wysyłki produkcyjnego 3D w potoku gry lub handlu elektronicznego: Meshy 4 lub Rodin Gen-1.5 wyjściowe siatki PBR, które trafiają bezpośrednio do Unity/Unreal.

## Wyślij to

Zapisz `outputs/skill-3d-pipeline.md`. Umiejętność wykonuje brief 3D (wejście: tekst / jeden obraz / kilka obrazów; wynik: siatka / ikona / NeRF; użycie: render / gra / VR) i wyniki: potok (rozproszenie w wielu widokach + dopasowanie lub bezpośredni model siatki), model podstawowy, budżet iteracji, przetwarzanie końcowe topologii, potrzebne kanały materiałowe.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py` z 4, 16, 64 Gaussami. Zgłoś końcowe MSE w porównaniu do wartości docelowej.
2. **Średni.** Rozszerzony do kolorowych Gaussów (RGB). Potwierdź, że rekonstrukcja odpowiada docelowemu wzorowi kolorów.
3. **Trudne.** Używając gsplat lub Nerfstudio, zrekonstruuj prawdziwy obiekt na podstawie 50 zdjęć. Zgłoś czas dopasowania i końcowy SSIM na zatrzymanych widokach.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Rozpryski gaussowskie 3D | „3DGS” | Scena w postaci chmury trójwymiarowych Gaussów; różniczkowalny render alfa-kompozytowy. |
| NeRF | „Nerwowe pole promieniowania” | MLP generujący kolor + gęstość w punkcie 3D; renderowanie poprzez integrację promieni. |
| Trójpłatowiec | „Trzy płaszczyzny 2-D” | Rozłóż 3D na trzy siatki obiektów 2D, wyrównane do osi; tańsze niż wolumetryczne. |
| SDS | „Pobieranie próbek metodą destylacji punktowej” | Trenuj model 3D, używając wyniku dyfuzji 2D jako pseudogradientu. |
| Rozproszenie wielu widoków | „Wiele wyświetleń na raz” | Model dyfuzyjny generujący partię spójnych widoków z kamer. |
| PBR | „Renderowanie oparte na fizyce” | Materiał z albedo, chropowatością, metalicznym, normalnymi kanałami. |
| Zagęszczenie | „Rosną plamy” | Heurystyka szkoleniowa 3DGS: dzielenie/klonowanie ikon w obszarach o wysokim gradiencie. |

## Notatka produkcyjna: 3D nie ma jeszcze udostępnionego podłoża

W przeciwieństwie do obrazu (utajona dyfuzja + DiT) i wideo (przestrzenno-czasowa DiT), w 2026 r. 3D nie będzie miało jednego dominującego czasu działania. Drzewo decyzyjne produkcji rozwidla się w zależności od reprezentacji:

- **NeRF / trójpłatowiec.** Wnioskowanie to marsz promieni + MLP do przodu na próbkę. Renderowanie 512² wymaga milionów plików przesyłanych dalej w formacie MLP. Agresywnie dodawaj próbki promieni; Obowiązuje SDPA/xformers.
- **Rozpowszechnianie wielu widoków + rekonstrukcja LRM.** Rurociąg dwuetapowy. Etap 1 (DiT z wieloma widokami) to serwer dyfuzyjny, taki sam jak Lekcja 07. Etap 2 (transformator LRM) to jednorazowe przejście do przodu przez widoki. Ogólny profil opóźnienia to „rozproszenie + jednorazowy” — wybierz odpowiednio elementy podstawowe obsługujące każdy etap.
- **SDS / DreamFusion.** Optymalizacja poszczególnych zasobów, a nie wnioskowanie. Twórz zadania, a nie osoby zajmujące się obsługą żądań.

W przypadku większości produktów na rok 2026 prawidłowa odpowiedź brzmi: „uruchom na żądanie model dyfuzyjny z wieloma widokami, asynchronicznie zrekonstruuj do formatu 3DGS, udostępnij 3DGS do oglądania w czasie rzeczywistym”. Spowoduje to przejrzysty podział obciążenia pomiędzy serwerem wnioskowania GPU (szybki) i optymalizatorem offline (wolnym).

## Dalsze czytanie

- [Mildenhall i in. (2020). NeRF: Reprezentowanie scen jako neuronowych pól promieniowania](https://arxiv.org/abs/2003.08934) — NeRF.
- [Kerbl i in. (2023). Rozpryski gaussowskie 3D do renderowania pola promieniowania w czasie rzeczywistym](https://arxiv.org/abs/2308.04079) — 3DGS.
- [Poole i in. (2022). DreamFusion: zamiana tekstu na 3D przy użyciu dyfuzji 2D](https://arxiv.org/abs/2209.14988) — SDS.
- [Liu i in. (2023). Zero-1-to-3: Zero-shot jednego obrazu do obiektu 3D](https://arxiv.org/abs/2303.11328) — Zero123.
- [Shi i in. (2023). MVDream](https://arxiv.org/abs/2308.16512) — rozpowszechnianie w wielu widokach.
- [Hong i in. (2023). LRM: duży model rekonstrukcji pojedynczego obrazu do postaci 3D](https://arxiv.org/abs/2311.04400) — LRM.
- [Gao i in. (2024). CAT3D: Twórz wszystko w 3D za pomocą modeli dyfuzyjnych z wieloma widokami](https://arxiv.org/abs/2405.10314) — CAT3D.
- [Stabilna sztuczna inteligencja (2024). Stabilne wideo 3D (SV3D)](https://stability.ai/research/sv3d) — SV3D.