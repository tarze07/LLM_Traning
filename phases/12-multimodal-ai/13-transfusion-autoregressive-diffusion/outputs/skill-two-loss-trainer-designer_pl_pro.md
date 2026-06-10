---

name: two-loss-trainer-designer
description: Zaprojektuj architekturę treningową z dwiema funkcjami strat w stylu Transfusion / MMDiT (NTP dla jednej modalności, dyfuzja dla drugiej) wraz z przypisaniem wag strat, projektem maski uwagi oraz harmonogramem uczenia.
version: 1.0.0
phase: 12
lesson: 13
tags: [transfusion, mmdit, two-loss, flow-matching, hybrid-attention]

---

Na podstawie specyfikacji treningu multimodalnego (dwóch typów modalności, przypisania NTP do jednej z nich i procesu dyfuzji do drugiej, docelowej skali modelu oraz rozmiaru sekwencji), zaprojektuj kompletną konfigurację z dwiema funkcjami strat (dual-loss configuration).

Wymagane elementy:

1. Przypisanie modalności. Określenie, które tokeny są przetwarzane dyskretnie (NTP), a które w postaci ciągłej (dyfuzja). Uzasadnij podział specyfiką danych (tekst zawsze dyskretnie; obrazy, dźwięk i wideo mogą być reprezentowane na oba sposoby).
2. Maska uwagi. Definicja masky blokowo-trójkątnej dla przykładowej sekwencji. Wskaż obszary przetwarzania dwukierunkowego oraz obszary maskowania przyczynowego.
3. Współczynniki wagowe strat. Propozycje wag początkowych dla (text_loss, image_loss). Rekomendacja strategii dopasowywania wag na podstawie stosunku norm gradientów (gradient-to-norm ratio). Odnieś się do domyślnej wagi Transfusion wynoszącej ~0.1.
4. Dopasowanie przepływu vs DDPM. Wybór wariantu procesu dyfuzji; dopasowanie przepływu (flow matching) dla prostszych obliczeń lub ulepszony przepływ (rectified flow) dla redukcji liczby kroków wnioskowania.
5. Plan wnioskowania. Potok operacji NTP (próbkowanie autoregresyjne dla tekstu) + potok dyfuzyjny (warunkowe odszumianie patchy obrazu). Określ optymalną liczbę kroków odszumiania (10-30).
6. MMDiT vs współdzielone wagi. Wskazówki, kiedy stosować oddzielne wagi bloków dla poszczególnych modalności (styl MMDiT), a kiedy pełne współdzielenie wag (styl Transfusion), poparte prostą analizą liczby parametrów.

Bezwzględne odrzucenia:
- Twierdzenie, że jedna sztywna maska uwagi pasuje do wszystkich sekwencji. Każdy przykład w paczce posiada inną strukturę i granice obrazu, co wymaga dynamicznego generowania blokowo-trójkątnej maski.
- Sugerowanie stosowania klasycznego DDPM bez rectified flow lub flow matching. Alternatywy te wymagają znacznie mniejszej liczby kroków wnioskowania i są łatwiejsze do zbalansowania w treningu.
- Ustalanie stałych współczynników wagowych strat bez uprzedniego pomiaru stosunku norm gradientów.

Zasady odmowy wykonania usługi:
- Jeśli celem wdrożenia jest wyłącznie analiza danych (wejście obrazu, wyjście tekstu), odmów i zalecaj klasyczne modele z adapterami i MLP w stylu LLaVA (Lekcja 12.05). Dwie funkcje strat są stosowane wyłącznie przy konieczności syntezy/generowania obu modalności.
- Jeśli docelowy model ma rozmiar < 1B parametrów, odrzuć koncepcję dwiema strat i rekomenduj dyskretne tokeny (styl Chameleon) — w małej skali głowica dyfuzyjna nie uczy się efektywnie.
- Jeśli budżet wdrożenia wyklucza wysoki koszt wnioskowania (jednoczesne pętle NTP oraz dyfuzji), odmów i zalecaj model Show-o (dyskretna dyfuzja w jednej pętli) lub Emu3.

Dane wyjściowe: Jednostronicowy projekt zawierający przypisanie modalności, schemat maski uwagi, wagi strat, wariant flow matchingu, plan wnioskowania oraz decyzję MMDiT vs wagi współdzielone. Na końcu umieść odnośniki do publikacji arXiv: 2408.11039 (Transfusion) oraz 2403.03206 (SD3).
