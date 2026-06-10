---

name: var-tokenizer-designer
description: Zaprojektuj wieloskalowy resztkowy tokenizer VQ do generowania wizualnych obrazów autoregresyjnych w następnej skali.
version: 1.0.0
phase: 8
lesson: 19
tags: [var, next-scale-prediction, vq-vae, residual-vq, image-generation, tokenizer]

---

Biorąc pod uwagę docelowy obraz (rozdzielczość, kanały, kolor a skala szarości, rozmiar zestawu danych, budżet obliczeniowy LM na dalszym etapie, docelowy FID), wynik:

1. Harmonogram skali. Wymień poziomy rozdzielczości K od 1x1 do (H/p) x (W/p). Domyślnie 10 skal dla 256x256, 14 dla 512x512. Uzasadnij K względem efektywnej długości sekwencji LM (suma obszarów skali) i budżetu na przejście równoległego w ramach skali.
2. Książka kodów. Pojedynczy wspólny rozmiar książki kodowej V we wszystkich skalach (typowo 4096/8192/16384). Wybierz V z rozmiaru zbioru danych i pojemności dekodera. Potwierdź, że użycie książki kodowej utrzymuje się na poziomie powyżej 50 procent w przypadku partii kalibracyjnej lub zmniejsz V.
3. Dzielenie się pozostałościami. Potwierdź, że skale 1..K wspólnie zrekonstruuj utajone elementy poprzez zsumowane osadzania w trybie upsamplingu (resztkowe VQ). Podaj rozmiar plastra p i szkielet VAE (włączenie/wyłączenie dyskryminatora typu VQGAN, percepcyjna utrata wagi).
4. Dekoder. Mapowanie dekodera VAE zsumowało utajone z powrotem do pikseli. Wybierz dekoder VQGAN, dekoder papierowy VAR lub lżejszy dekoder w stylu MAGVIT. Uzasadnij w stosunku do docelowej FID i pamięci VRAM dekodera.
5. Osadzenie pozycji. Potwierdź (scale_index, row, col) potrójnie z wyuczonym osadzaniem na skalę i dwuwymiarowym sin-cos w skali. Odrzuć płaskie pozycje 1D; LM potrzebuje etykiety skali, aby zastosować odpowiedni warunek.

Odrzuć nieresztkowy, wieloskalowy tokenizer dla VAR. Bez zsumowanych reszt warunek następnej skali staje się źle zdefiniowany, a LM optymalizuje inny cel, niż dowodzi artykuł. Odrzuć oddzielne książki kodowe dla każdej skali, chyba że V zostanie skalibrowane do liczby pikseli w mniejszej skali, a zapadnięcie się książki kodowej zostanie ograniczone. W ogóle odrzuć przewidywanie następnej skali, gdy K x obszar średniej skali przekracza maksymalną długość sekwencji LM pomniejszoną o rezerwę na warunkowanie tekstu.

Przykładowe dane wejściowe: „Rozdzielczość warunkowa klasy ImageNet 256 x 256, zbiór danych 1,2 mln, budżet LM 1,5 mld parametrów, docelowy FID poniżej 5,0”.

Przykładowe wyjście:
- Schemat skali: K=10, rozmiary 1, 2, 3, 4, 5, 6, 8, 10, 13, 16. Łącznie 671 żetonów.
- Książka kodowa: wspólna, V=4096. Spodziewaj się 70-80 procent użycia w ImageNet przy 256.
- Udostępnianie pozostałości: potwierdzone; p=16, szkielet VQGAN ze stratami percepcyjnymi i przeciwstawnymi, rekonstrukcja sumy rezydualnej f.
- Dekoder: dekoder VQGAN, 4 bloki upsamplingu, bez dodatkowego rafinera.
- Osadzanie pozycji: (skala, wiersz, kolumna) potrójny, wyuczony żeton skali + 2D sin-cos w obrębie skali.