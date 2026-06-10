---

name: stylegan-inversion
description: Wybierz potok inwersji i edycji dla wstępnie wyszkolonego StyleGAN zamiast prawdziwego zdjęcia.
version: 1.0.0
phase: 8
lesson: 05
tags: [stylegan, inversion, editing]

---

Biorąc pod uwagę prawdziwe zdjęcie + wstępnie wytrenowany punkt kontrolny StyleGAN (FFHQ-1024, StyleGAN-XL, niestandardowe dostrojenie) i edycję celu (wiek, uśmiech, poza, włosy, zachowanie tożsamości), wynik:

1. Metoda inwersji. e4e (szybki, niski poziom wierności), ReStyle (koder iteracyjny), HyperStyle (hipernet), PTI (strojenie obrotowe) lub bezpośrednia optymalizacja W. Powód w jednym zdaniu powiązany z wiernością a szybkością.
2. Pole docelowe. W, W+ lub StyleSpace. Kompromisy: W = najbardziej rozplątany, ale najniższa wierność, W+ = na warstwę w, StyleSpace = na poziomie kanału.
3. Kierunek edycji. Nazwane źródło kierunku: InterFaceGAN (oparty na SVM), kanały StyleSpace, GANSpace PCA lub wyuczony klasyfikator.
4. Budżet wierności. Próg LPIPS przed dryfem tożsamości; heurystyka wycofywania.
5. Ewaluacja. Podobieństwo identyfikatora (cosinus ArcFace), LPIPS do oryginału, siła edycji (wynik klasyfikatora atrybutów docelowych).

Odrzuć każdy potok, który edytuje bezpośrednio w Z (splątany). Odmawiaj dużych zmian (>1,5 sigma w W) bez sprawdzania tożsamości. Oznacz żądania wymagające edycji w otwartej domenie (np. „zrób z niego kreskówkę”) – wymagają one rozpowszechnienia + adaptera IP, a nie StyleGAN.