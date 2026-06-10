---

name: clip-zero-shot
description: Przeprowadź klasyfikację obrazów typu zero-shot za pomocą punktu kontrolnego CLIP/SigLIP, tworząc rankingowe prognozy z wynikami podobieństwa.
version: 1.0.0
phase: 12
lesson: 02
tags: [clip, siglip, zero-shot, vision-language]

---

Mając listę obrazów (ścieżki plików lub adresy URL) i listę nazw klas kandydatów, utwórz rankingową klasyfikację zerową, korzystając z zadeklarowanego punktu kontrolnego CLIP lub SigLIP. Umiejętność polega na czystym przewidywaniu; nie ćwiczy ani nie doskonali.

Wyprodukuj:

1. Szybka konstrukcja. Dla każdej klasy utwórz N szablonów tekstowych (domyślnie: `a photo of a {class}`, `a picture of a {class}`, `an image of a {class}`). Osadź każdy monit za pomocą kodera tekstu i średniej, aby utworzyć prototyp klasy.
2. Osadzanie obrazu. Osadź każdy obraz wejściowy za pomocą podanego kodera wizyjnego. Normalizuj obie strony do długości jednostkowej.
3. Prognozy rankingowe. Oblicz podobieństwo cosinus między każdym osadzeniem obrazu a prototypem każdej klasy. Zwróć top-1 i top-5 z wynikami.
4. Metadane punktu kontrolnego. Nazwij dokładny punkt kontrolny Przytulonej Twarzy (np. `openai/clip-vit-large-patch14` lub `google/siglip2-so400m-patch14-384`) i oczekiwaną rozdzielczość.
5. Powiadomienie o uczciwości. Stwierdzić, że zero-shot na zajęciach poza rozkładem przedszkoleniowym jest niewiarygodny; wykaż najwyższy wynik jako wskaźnik zaufania i ostrzegaj, gdy spadnie on poniżej 0,2.

Twarde odrzucenia:
- Każde użycie, które wyznacza wyjście jako ostateczną etykietę dla klas, których nie ma na liście dostarczonej przez osobę wywołującą.
- Twierdzenia dotyczące porównywalności wyników w różnych punktach kontrolnych; Wynik SigLIP i CLIP w różnych skalach.
- Działa na obrazach, o których wiadomo, że przedstawiają osoby, bez polityki dotyczącej zgody dalszych osób.

Zasady odmowy:
- Jeśli osoba dzwoniąca poprosi o zaklasyfikowanie do kategorii medycznych, prawnych lub kluczowych dla bezpieczeństwa (diagnoza, tożsamość, chronione atrybuty), odmów i przekieruj do nadzorowanych modeli ze ścieżkami audytu.
- Jeśli rozmówca poda jedną nazwę klasy (klasyfikacja jednokierunkowa bez alternatyw), odmów – zero-shot wymaga co najmniej dwóch kandydatów, aby był znaczący.
- Jeśli punkt kontrolny nie jest określony, odmów i zapytaj, który z (CLIP, OpenCLIP, SigLIP, SigLIP 2) plus jaka skala.

Dane wyjściowe: rankingowa lista 5 najlepszych przewidywań na obraz z wynikami podobieństwa cosinus, nazwą punktu kontrolnego, zastosowanymi szablonami podpowiedzi i flagą zaufania. Zakończ akapitem „co dalej czytać” wskazującym na lekcję 12.06 dotyczącą NaFlex (obsługa zmiennych proporcji) lub artykuł SigLIP 2 dotyczący głębszego nurkowania.