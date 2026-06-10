---

name: stylegan-inversion
description: Wybierz potok inwersji i edycji dla wstępnie wytrenowanego modelu StyleGAN na podstawie rzeczywistego zdjęcia.
version: 1.0.0
phase: 8
lesson: 05
tags: [stylegan, inversion, editing]

---

Biorąc pod uwagę rzeczywiste zdjęcie, gotowy punkt kontrolny (checkpoint) StyleGAN (np. FFHQ-1024, StyleGAN-XL, model dostrojony do własnych danych) oraz cel edycji (wiek, uśmiech, poza, fryzura, zachowanie tożsamości), wygeneruj:

1. Metoda inwersji (Inversion Method). e4e (szybka, ale o niższej wierności), ReStyle (koder iteracyjny), HyperStyle (oparty na architekturze HyperNetwork), PTI (Pivot Tuning Inversion) lub bezpośrednia optymalizacja w przestrzeni W. Podaj jednozdaniowe uzasadnienie uwzględniające kompromis między wiernością odwzorowania a szybkością działania.
2. Przestrzeń ukryta (Latent Space). W, W+ lub StyleSpace. Kompromisy: W = najbardziej rozplątana (disentangled), ale o najniższej wierności; W+ = wektory w na każdą warstwę; StyleSpace = kontrola na poziomie pojedynczych kanałów.
3. Kierunek edycji (Editing Direction). Źródło kierunku edycji: InterFaceGAN (oparty na klasyfikatorach SVM), kanały StyleSpace, GANSpace (analiza PCA) lub wytrenowany klasyfikator.
4. Budżet wierności (Fidelity Budget). Maksymalny próg odległości LPIPS zapobiegający utracie tożsamości; reguła wycofania (fallback heuristic) w przypadku zbyt głębokich modyfikacji.
5. Ewaluacja. Podobieństwo tożsamości (odległość cosinusowa ArcFace), wskaźnik LPIPS względem oryginału, siła edycji (wynik klasyfikatora dla docelowego atrybutu).

Odrzuć każdy potok (pipeline), który próbuje edytować wektor bezpośrednio w przestrzeni Z (ze względu na silne splątanie cech - entanglement). Odrzuć próby wprowadzania dużych zmian (>1.5 odchylenia standardowego sigma w przestrzeni W) bez jednoczesnej kontroli zachowania tożsamości. Oznacz flagą ostrzegawczą zapytania wymagające edycji w otwartej domenie (np. „zrób z tego postać z kreskówki”) – takie operacje wymagają modeli dyfuzyjnych z adapterem IP-Adapter, a nie architektury StyleGAN.
