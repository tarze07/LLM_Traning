---

name: fm-tuner
description: Przekształć proces uczenia modelu dyfuzyjnego w konfigurację opartą na dopasowywaniu przepływu (Flow Matching) lub przepływach skorygowanych (Rectified Flows).
version: 1.0.0
phase: 8
lesson: 13
tags: [flow-matching, rectified-flow, diffusion]

---

Biorąc pod uwagę proces uczenia w stylu dyfuzyjnym (dane, zasoby obliczeniowe, harmonogram, docelowa liczba kroków, wymagania jakościowe), wygeneruj odpowiednik oparty na dopasowywaniu przepływu (Flow Matching):

1. Harmonogram + Interpolant. Liniowy (Rectified Flow), transport optymalny (Lipman OT-CFM), zachowujący wariancję (variance-preserving) lub cosinusowy. Podaj jednozdaniowe uzasadnienie wyboru.
2. Próbkowanie kroków czasowych. Jednorodne (uniform), o rozkładzie logit-normalnym (tak jak w SD3) lub ważone modami (mode-weighted). Ostrzegaj, gdy próbkowanie jednorodne marnuje moc obliczeniową na skrajnych punktach przedziału czasowego.
3. Cel predykcji. Prędkość v = x_1 - x_0 (dla Rectified Flow) lub alfa'(t)x_1 + sigma'(t)x_0 (dla CFM). Wskaż, który cel został wybrany.
4. Optymalizator + Rozgrzewka (Warmup) LR. Uwzględnij użycie AdamW z parametrem beta2 = 0.95 dla zapewnienia stabilności przy skalowaniu modeli typu Transformer.
5. Procedura Reflow (ponownego mapowania przepływu). Określ, czy należy uruchomić 0, 1 czy 2 iteracje procedury Reflow; budżet na jedną iterację odpowiada zazwyczaj pełnemu wnioskowaniu na wybranym podzbiorze danych.
6. Liczba kroków. Docelowa liczba kroków treningowych, oczekiwana liczba kroków podczas wnioskowania (np. 20, 4, 2, 1) oraz zakres skali naprowadzania (guidance scale).
7. Ewaluacja. Porównanie wskaźników FID/CLIP z modelem bazowym (dyfuzyjnym) oraz wykres zależności jakości od liczby kroków wnioskowania.

Odrzuć realizację procedury Reflow przed uzyskaniem zbieżności modelu bazowego v_1 (wykonywanie reflow na niedotrenowanym modelu utrwala błędne trajektorie). Odrzuć rekomendacje jednoetapowego wnioskowania (1-step inference) bez zastosowania dodatkowej destylacji spójności (consistency distillation). Oznacz flagą ostrzegawczą każdy model Flow Matching, który wymaga > 20 kroków wnioskowania – jeśli potrzebujesz tak wielu kroków, zalety sformułowania problemu jako przepływu zostały zaprzepaszczone.
