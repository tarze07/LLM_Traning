# Generacja 3D

> Trójwymiar (3D) to obszar, w którym efekt dźwigni metod 2D na 3D jest najbardziej widoczny. Kamieniem milowym w 2023 roku stała się technologia 3D Gaussian Splatting (reprezentacja sceny za pomocą plam gaussowskich). Z kolei trendy na lata 2024–2026 skupiają się wokół generowania wielu spójnych widoków (multi-view), na bazie których następuje szybka rekonstrukcja 3D, co pozwala na tworzenie całych obiektów i scen na podstawie jednego promptu tekstowego lub zdjęcia.

**Typ:** Teoria i praktyka
**Języki:** Python
**Wymagania:** Faza 4 (Wizja komputerowa), Faza 8 · Lekcja 07 (Utajona dyfuzja)
**Czas:** ~45 minut

## Wyzwania w grafice 3D

Tworzenie i reprezentacja treści 3D wiążą się z wieloma trudnościami:

- **Reprezentacja.** Siatki (meshes), chmury punktów, siatki wokseli (voxel grids), pola odległości ze znakiem (SDF), neuronowe pola promieniowania (NeRF) oraz 3D Gaussian Splatting (3DGS). Każda z tych metod wiąże się z określonymi kompromisami wydajnościowymi i jakościowymi.
- **Niedobór danych.** Podczas gdy ImageNet zawiera 14 milionów obrazów dwuwymiarowych, największy oczyszczony zbiór danych 3D (Objaverse-XL, 2023) liczy około 10 milionów obiektów, z czego większość stanowią modele o bardzo niskiej jakości.
- **Wymagania pamięciowe.** Siatka wokseli o rozdzielczości $512^3$ składa się ze 128 milionów wokseli. Z kolei renderowanie dobrej jakości sceny za pomocą NeRF wymaga pobrania około 1 miliona próbek na promień. Generowanie obiektów 3D od podstaw jest znacznie trudniejszym zadaniem niż ich rekonstrukcja z istniejących danych.
- **Nadzór (Supervision).** W przypadku obrazów 2D dysponujemy bezpośrednią informacją o pikselach. W przypadku 3D zazwyczaj mamy do czynienia jedynie z kilkoma rzutami 2D, z których musimy odtworzyć pełną geometrię trójwymiarową.

Współczesne podejście (stan na rok 2026) rozdziela te dwa problemy. Najpierw generowane są spójne obrazy z wielu widoków (multi-view) przy użyciu modelu dyfuzyjnego, a następnie na ich podstawie dopasowywana jest reprezentacja 3D (zazwyczaj przy użyciu Gaussian Splatting).

## Koncepcja działania

![Generacja 3D: dyfuzja wielowidokowa + rekonstrukcja 3D](../assets/3d-generacja.svg)

### Reprezentacja: 3D Gaussian Splatting (Kerbl i in., 2023)

Scena reprezentowana jest jako chmura około 1 miliona trójwymiarowych plam Gaussa (Gaussians). Każda plama opisana jest przez 59 parametrów: położenie (3), kowariancję (6 parametrów określanych przez kwaternion (4) oraz skalę (3)), nieprzezroczystość (1) oraz współczynniki harmonik sferycznych (Spherical Harmonics) odpowiedzialne za kolor w zależności od kąta patrzenia (48 parametrów dla stopnia 3., 3 dla stopnia 0.).

Renderowanie opiera się na projekcji plam na płaszczyznę obrazu oraz ich kompozycji alfa (alpha blending). Jest to proces niezwykle szybki (~100 kl./s w rozdzielczości 1080p na karcie RTX 4090) oraz w pełni różniczkowalny. Dopasowanie plam do zdjęć referencyjnych (ground truth) realizowane jest za pomocą metody spadku gradientu. Optymalizacja sceny zajmuje od 5 do 30 minut na konsumenckim procesorze graficznym.

Dwie kluczowe innowacje z lat 2023–2024 to:
- **Generatywne modele Gaussian Splatting.** Modele takie jak LGM, LRM czy InstantMesh potrafią przewidzieć chmurę plam Gaussa bezpośrednio na podstawie jednego lub kilku obrazów (single-shot/few-shot).
- **4D Gaussian Splatting.** Wprowadzenie przesunięć (offsetów) plam dla poszczególnych klatek czasowych w celu reprezentowania scen dynamicznych (ruchomych).

### Dyfuzja wielowidokowa (Multi-view Diffusion)

Polega na dostrojeniu wstępnie wytrenowanego modelu dyfuzji obrazu tak, aby generował zestaw spójnych widoków tego samego obiektu pod różnymi kątami na podstawie promptu tekstowego lub jednego zdjęcia. Rozwiązania takie jak Zero123 (Liu i in., 2023), MVDream (Shi i in., 2023), SV3D (Stability, 2024) czy CAT3D (Google, 2024) generują zazwyczaj od 4 do 16 widoków wokół obiektu, które następnie są rekonstruowane do postaci 3D za pomocą Gaussian Splatting lub NeRF.

### Potoki Text-to-3D i Image-to-3D

| Model | Wejście | Wyjście | Czas |
|---|---|---|---|
| DreamFusion (2022) | tekst | NeRF (optymalizowany przez SDS) | ~1 godzina na zasób |
| Magic3D | tekst | siatka + tekstura | ~40 minut |
| Shap-E (OpenAI, 2023) | tekst | niejawna reprezentacja 3D | ~1 minuta |
| SJC / ProlificDreamer | tekst | NeRF / siatka | ~30 minut |
| LRM (Meta, 2023) | obraz | triplane | ~5 s |
| InstantMesh (2024) | obraz | siatka | ~10 s |
| SV3D (Stability, 2024) | obraz | nowe widoki (novel views) | ~2 minuty |
| CAT3D (Google, 2024) | 1-64 obrazy | 3D NeRF | ~1 minuta |
| TripoSR (2024) | obraz | siatka | ~1 s |
| Meshy 4 (2025) | tekst + obraz | siatka PBR | ~30 s |
| Rodin Gen-1.5 (2025) | tekst + obraz | siatka PBR | ~60 s |
| Tencent Hunyuan3D 2.0 (2025) | obraz | siatka | ~30 s |

Kierunek rozwoju na lata 2025–2026 to bezpośrednie generowanie siatek (text-to-mesh/image-to-mesh) wraz z materiałami PBR dostosowanymi do silników gier. Niemniej jednak, potoki oparte na dyfuzji wielowidokowej jako etapie pośrednim pozostają najbardziej wszechstronnym i stabilnym rozwiązaniem dla obiektów o dowolnej geometrii.

### NeRF (dla kontekstu)

Neural Radiance Fields (Mildenhall i in., 2020) reprezentują scenę za pomocą małej sieci MLP, która przyjmuje współrzędne trójwymiarowe oraz kierunek patrzenia `(x, y, z, kierunek_patrzenia)`, a zwraca kolor i gęstość optyczną `(kolor, gęstość)`. Renderowanie odbywa się poprzez całkowe śledzenie promieni (ray marching). Jakość generowanych obrazów przewyższa tradycyjną syntezę widoków opartą na siatkach geometrycznych, lecz samo renderowanie jest od 100 do 1000 razy wolniejsze. W większości zastosowań czasu rzeczywistego technologia NeRF została wyparta przez Gaussian Splatting, ale wciąż pozostaje ważnym narzędziem w pracach badawczych.

## Praktyczna implementacja

Skrypt `code/main.py` implementuje uproszczoną, dwuwymiarową wersję dopasowywania plam Gaussa (Gaussian Splats). Reprezentuje on syntetyczny obraz docelowy (gładki gradient) jako sumę dwuwymiarowych plam gaussowskich. Parametry położenia, koloru oraz kowariancji plam są optymalizowane metodą spadku gradientu w celu jak najlepszego odwzorowania celu. Kod ilustruje dwie podstawowe operacje: renderowanie w przód (nakładanie plam i kompozycja alfa) oraz optymalizację gradientową.

### Krok 1: Definicja dwuwymiarowej plamy Gaussa

```python
def gaussian_at(x, y, gaussian):
    px, py = gaussian["pos"]
    sigma = gaussian["sigma"]
    d2 = (x - px) ** 2 + (y - py) ** 2
    return math.exp(-d2 / (2 * sigma * sigma))
```

### Krok 2: Renderowanie poprzez sumowanie plam

```python
def render(image_size, gaussians):
    img = [[0.0] * image_size for _ in range(image_size)]
    for g in gaussians:
        for y in range(image_size):
            for x in range(image_size):
                img[y][x] += g["color"] * gaussian_at(x, y, g)
    return img
```

W pełnym algorytmie 3D Gaussian Splatting plamy są sortowane według głębokości (odległości od kamery) i łączone zgodnie z kolejnością kompozycji alfa. Nasz uproszczony model 2D po prostu sumuje ich wartości.

### Krok 3: Optymalizacja metodą spadku gradientu

```python
for step in range(steps):
    pred = render(size, gaussians)
    loss = mse(pred, target)
    gradients = compute_grads(pred, target, gaussians)
    update(gaussians, gradients, lr)
```

## Typowe pułapki i wyzwania

- **Niezgodność widoków (View Inconsistency).** Jeżeli model dyfuzyjny wygeneruje widoki, które są niespójne pod względem geometrii obiektu, dopasowana rekonstrukcja 3D będzie rozmyta. Rozwiązaniem jest generowanie widoków za pomocą modeli ze wspólnymi warstwami uwagi (shared attention).
- **Halucynowanie niewidocznych elementów (Backside Hallucination).** Przejście ze zdjęcia (2D) do modelu 3D wymaga odtworzenia niewidocznej strony obiektu. Jakość rekonstrukcji tych obszarów bywa bardzo zmienna.
- **Eksplozja liczby plam Gaussa.** Optymalizacja bez dodatkowych ograniczeń może doprowadzić do wygenerowania milionów drobnych plam i przeuczenia modelu (overfittingu). Niezbędne jest stosowanie heurystyk zagęszczania (densification) i usuwania (pruning) plam, zgodnie z oryginalną pracą o 3DGS.
- **Problemy z topologią siatki.** Siatki geometryczne rekonstruowane z pól SDF często zawierają błędy topologiczne, takie jak dziury czy samoprzecinające się wielokąty. Przed eksportem modelu należy zastosować algorytmy naprawcze (np. voxel remesher w Blenderze).
- **Licencjonowanie danych.** Zbiór Objaverse charakteryzuje się mieszanym licencjonowaniem obiektów. Możliwość komercyjnego wykorzystania modeli zależy bezpośrednio od licencji danych treningowych konkretnego modelu bazowego.

## Wybór technologii (Rekomendacje 2026)

| Zadanie | Wybór technologiczny |
|---|---|
| Rekonstrukcja sceny z serii zdjęć | 3D Gaussian Splatting (3DGS, Gsplat, Scaniverse) |
| Generowanie obiektów Text-to-3D dla gier | Meshy 4 lub Rodin Gen-1.5 (generowanie materiałów PBR) |
| Konwersja pojedynczego obrazu do 3D | Hunyuan3D 2.0, TripoSR, InstantMesh |
| Synteza nowych widoków z kilku zdjęć | CAT3D, SV3D |
| Rekonstrukcja sceny dynamicznej (ruchomej) | 4D Gaussian Splatting |
| Tworzenie cyfrowych awatarów i postaci | Gaussian Avatar, Hugs |
| Badania naukowe / SOTA | Najnowsze publikacje i repozytoria open-source |

Do wdrożeń produkcyjnych w grach komputerowych lub systemach e-commerce optymalnym wyborem są narzędzia takie jak Meshy 4 lub Rodin Gen-1.5, generujące gotowe siatki PBR kompatybilne z Unity/Unreal Engine.

## Zadanie wdrożeniowe

Zapisz plik `outputs/skill-3d-pipeline.md`. Zadaniem wdrożeniowym jest opracowanie potoku 3D na podstawie założeń projektowych (wejście: tekst / pojedynczy obraz / kilka obrazów; wyjście: siatka / plamy Gaussa / NeRF; zastosowanie: renderowanie / gra / VR). Dokument powinien określać: strukturę potoku (dyfuzja wielowidokowa + dopasowanie lub bezpośrednie generowanie siatki), model bazowy, budżet iteracji, przetwarzanie końcowe topologii (post-processing) oraz wymagane mapy (kanały) materiałowe.

## Ćwiczenia

1. **Łatwe.** Uruchom skrypt `code/main.py` z liczbą plam Gaussa równą odpowiednio 4, 16 i 64. Porównaj i opisz ostateczny błąd średniokwadratowy (MSE) w stosunku do obrazu docelowego.
2. **Średnie.** Rozszerz model o obsługę kolorowych plam Gaussa (RGB). Zweryfikuj, czy zrekonstruowany obraz odpowiada docelowemu wzorcowi kolorystycznemu.
3. **Trudne.** Wykorzystując bibliotekę gsplat lub pakiet Nerfstudio, zrekonstruuj trójwymiarowy model rzeczywistego obiektu na podstawie 50 zdjęć. Podaj czas potrzebny na optymalizację oraz końcowy wskaźnik SSIM (Structural Similarity Index) dla widoków testowych (test set).

## Słownik pojęć

| Termin | Potoczna nazwa / Skrót | Co to oznacza w praktyce |
|---|---|---|
| 3D Gaussian Splatting | 3DGS | Reprezentacja sceny za pomocą chmury trójwymiarowych plam gaussowskich; wykorzystuje różniczkowalny proces renderowania i kompozycji alfa. |
| NeRF | Neuronowe pola promieniowania | Sieć MLP zwracająca kolor i gęstość optyczną dla dowolnego punktu w przestrzeni 3D i kierunku patrzenia; renderowanie odbywa się metodą śledzenia promieni (ray marching). |
| Triplane | Trójpłaszczyzna | Reprezentacja przestrzeni 3D zrzutowana na trzy prostopadłe płaszczyzny 2D; rozwiązanie znacznie tańsze obliczeniowo niż reprezentacja wolumetryczna (voxel grid). |
| SDS | Score Distillation Sampling | Metoda trenowania modelu 3D, w której jako funkcja straty (lub źródło pseudogradientów) wykorzystywany jest dwuwymiarowy model dyfuzyjny. |
| Dyfuzja wielowidokowa | Multi-view diffusion | Model dyfuzyjny generujący zestaw geometrycznie spójnych obrazów z różnych kamer jednocześnie. |
| PBR | Physically Based Rendering | Metoda renderowania oparta na fizycznych właściwościach światła i materiałów, definiowanych przez mapy takie jak albedo, chropowatość (roughness), metaliczność (metalness) oraz mapę normalnych (normal map). |
| Zagęszczanie | Densification | Heurystyka stosowana podczas uczenia 3DGS, polegająca na podziale lub klonowaniu plam Gaussa w obszarach charakteryzujących się wysokimi wartościami gradientów. |

## Uwagi produkcyjne: Brak jednolitego standardu w grafice 3D

W przeciwieństwie do generowania obrazów (utajona dyfuzja + DiT) oraz wideo (przestrzenno-czasowe sieci DiT), w 2026 roku w obszarze 3D nadal nie wypracowano jednego dominującego standardu środowiska uruchomieniowego. Architektura produkcyjna zależy bezpośrednio od wybranej reprezentacji:

- **NeRF / Triplane.** Proces inferencji opiera się na metodzie śledzenia promieni (ray marching) i wyznaczaniu wartości przez sieć MLP dla każdej próbki. Renderowanie obrazu o rozdzielczości $512^2$ wymaga milionów przejść w przód (forward pass) przez sieć MLP. Wymaga to agresywnego próbkowania promieni; zalecane jest stosowanie SDPA (Scaled Dot-Product Attention) oraz bibliotek takich jak xformers.
- **Dyfuzja wielowidokowa + rekonstrukcja LRM.** Potok dwuetapowy. Etap 1 (wielowidokowy model DiT) to serwer obsługujący model dyfuzyjny, analogicznie jak w Lekcji 7. Etap 2 (transformator LRM) wykonuje pojedyncze przejście w przód (feed-forward) w celu wygenerowania geometrii na podstawie widoków. Profil opóźnień (latency) ma charakter dwufazowy („dyfuzja + szybka rekonstrukcja”) – należy odpowiednio dobrać infrastrukturę obliczeniową do każdego z tych etapów.
- **SDS / DreamFusion.** Jest to proces optymalizacji konkretnego obiektu, a nie klasyczna inferencja modelu. Architektura powinna opierać się na systemie zadań asynchronicznych (kolejkowanie), a nie na synchronicznej obsłudze żądań HTTP (request-response).

Dla większości projektów w 2026 roku optymalnym podejściem jest: generowanie spójnych widoków za pomocą modelu dyfuzyjnego na żądanie, asynchroniczna rekonstrukcja do formatu 3DGS, a następnie serwowanie pliku 3DGS do renderowania w czasie rzeczywistym u klienta. Taka architektura pozwala na wyraźny podział obciążenia na szybki serwer inferencji GPU oraz asynchroniczny optymalizator pracujący w tle.

## Literatura uzupełniająca

- [Mildenhall i in. (2020). NeRF: Reprezentowanie scen jako neuronowych pól promieniowania](https://arxiv.org/abs/2003.08934) — oryginalna praca o NeRF.
- [Kerbl i in. (2023). Rozpryski gaussowskie 3D do renderowania pola promieniowania w czasie rzeczywistym](https://arxiv.org/abs/2308.04079) — oryginalna praca o 3DGS.
- [Poole i in. (2022). DreamFusion: zamiana tekstu na 3D przy użyciu dyfuzji 2D](https://arxiv.org/abs/2209.14988) — metoda SDS.
- [Liu i in. (2023). Zero-1-to-3: Zero-shot jednego obrazu do obiektu 3D](https://arxiv.org/abs/2303.11328) — Zero123.
- [Shi i in. (2023). MVDream](https://arxiv.org/abs/2308.16512) — dyfuzja wielowidokowa.
- [Hong i in. (2023). LRM: duży model rekonstrukcji pojedynczego obrazu do postaci 3D](https://arxiv.org/abs/2311.04400) — model LRM.
- [Gao i in. (2024). CAT3D: Twórz wszystko w 3D za pomocą modeli dyfuzyjnych z wieloma widokami](https://arxiv.org/abs/2405.10314) — CAT3D.
- [Stable AI (2024). Stable Video 3D (SV3D)](https://stability.ai/research/sv3d) — SV3D.
