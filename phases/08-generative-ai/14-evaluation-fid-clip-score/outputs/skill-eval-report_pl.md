---

name: eval-report
description: Zaplanuj pełną ocenę modelu generatywnego: jakość próbki, przestrzeganie, preferencje, audyt niepowodzeń.
version: 1.0.0
phase: 8
lesson: 14
tags: [evaluation, fid, clip, elo]

---

Biorąc pod uwagę nowy punkt kontrolny modelu generatywnego, linię bazową odniesienia i modalność (obraz/wideo/audio/3D), wygeneruj pełny plan ewaluacji:

1. Jakość próbki. FID / FD-DINO / CMMD na 10-30 tys. próbek vs zestaw rzeczywisty. Dopasowana rozdzielczość. Zgłoś średnią 3-rozstawioną +/- std.
2. Przestrzeganie. Wynik CLIP / CMMD dla par obrazów zachęty. Dołącz HPSv2 + ImageReward + PickScore do zamiany tekstu na obraz. W przypadku wideo dodaj wskaźniki dotyczące wizji i języka (V-Eval). Dla dźwięku CLAP + MOS.
3. Preferencje w parach. Zaślepiona A/B na 200-2000 podpowiedzi w porównaniu z wartością bazową. Relacja Human + LLM-sędzia + PartiPrompts.
4. Podział kategorii. Wydajność według kategorii podpowiedzi (ludzie, zwierzęta, renderowanie tekstu, kompozycja, styl). Oznacz regresje według kategorii, nawet jeśli poprawią się wskaźniki globalne.
5. Bezpieczeństwo/niewłaściwe użytkowanie. Klasyfikator NSFW, wykrywacz deepfake, sprawdzanie znaku wodnego, skanowanie podobieństwa praw autorskich w najlepszych generacjach K.
6. Podpisanie. Jawna bramka: FID w granicach +5% wartości bazowej LUB >55% współczynnika wygranych wśród ludzi LUB udokumentowana przewaga jakościowa. Żadnych roszczeń dotyczących pojedynczych wskaźników.

Odmowa zgłoszenia FID w N &lt; 5000. Odmów przesyłania testów porównawczych obliczonych na podstawie podpowiedzi, które model mógł zobaczyć podczas szkolenia. Odmów raportowania wyłącznie wyników sędziów LLM bez kontroli krzyżowej przez człowieka. Zgłaszaj wszelkie twierdzenia, że ​​wskaźnik „wzrósł o 20%”, bez podawania bezwzględnej wartości bazowej i zgłaszania pojedynczego źródła.