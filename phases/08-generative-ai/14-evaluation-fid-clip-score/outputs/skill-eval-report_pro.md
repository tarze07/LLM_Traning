---

name: eval-report
description: Zaplanuj kompleksową ewaluację modelu generatywnego: jakość próbek, zgodność z promptami, preferencje użytkowników oraz audyt błędów.
version: 1.0.0
phase: 8
lesson: 14
tags: [evaluation, fid, clip, elo]

---

Biorąc pod uwagę nowy punkt kontrolny (checkpoint) modelu generatywnego, model referencyjny (baseline) oraz modalność (obraz / wideo / audio / 3D), wygeneruj pełny plan ewaluacji:

1. Jakość próbek. Obliczanie wskaźników FID / FD-DINO / CMMD na próbie 10k–30k wygenerowanych obrazów w porównaniu do zbioru rzeczywistego. Dopasuj rozdzielczości obrazów. Zgłoś średnią z 3 przebiegów (random seeds) wraz z odchyleniem standardowym.
2. Zgodność z promptami. Wynik CLIP / CMMD dla par obraz-prompt. Dodaj metryki HPSv2 + ImageReward + PickScore dla zadań generowania obrazów z tekstu (text-to-image). W przypadku wideo dodaj wielomodalne wskaźniki wizyjno-językowe (np. V-Eval). Dla audio zastosuj współczynnik CLAP + ocenę MOS.
3. Preferencje w parach (Pairwise Preferences). Ślepe testy A/B na zestawie 200–2000 promptów w porównaniu do modelu bazowego. Uwzględnij ocenę ludzką, ocenę automatyczną (LLM-sędzia) oraz testy na bazie zbioru PartiPrompts.
4. Analiza kategorii. Ocena jakości w podziale na kategorie promptów (np. ludzie, zwierzęta, renderowanie tekstu, kompozycja, styl). Wskaż pogorszenie wyników (regresję) w poszczególnych kategoriach, nawet jeśli ogólne wskaźniki uległy poprawie.
5. Bezpieczeństwo i nadużycia. Klasyfikatory treści NSFW, detektory wizerunku generowanego (deepfake), weryfikacja cyfrowych znaków wodnych oraz skanowanie podobieństwa praw autorskich dla top-K wygenerowanych próbek.
6. Kryteria akceptacji. Warunek dopuszczenia modelu: wskaźnik FID w granicach +5% od poziomu bazowego LUB współczynnik wygranych (win rate) w ocenie ludzkiej > 55% LUB udokumentowana przewaga jakościowa. Zakaz opierania decyzji na pojedynczych wskaźnikach.

Odrzuć raportowanie wskaźnika FID liczonego na próbie N < 5000. Odrzuć przeprowadzanie testów porównawczych na promptach, które mogły wchodzić w skład zbioru treningowego modelu. Odrzuć poleganie wyłącznie na ocenach LLM-sędziów bez weryfikacji krzyżowej z udziałem ludzi. Oznacz flagą ostrzegawczą wszelkie twierdzenia, że wskaźnik „wzrósł o 20%” bez podania bezwzględnej wartości bazowej lub gdy podano wyniki tylko z jednego źródła.
