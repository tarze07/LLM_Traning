---

name: fm-tuner
description: Przekształć plan szkolenia dyfuzyjnego w konfigurację dopasowania przepływu/rektyfikowanego przepływu.
version: 1.0.0
phase: 8
lesson: 13
tags: [flow-matching, rectified-flow, diffusion]

---

Biorąc pod uwagę plan szkolenia w stylu dyfuzji (dane, obliczenia, harmonogram, docelowa liczba kroków, pasek jakości), wyprowadź odpowiednik dopasowujący przepływ:

1. Harmonogram + interpolant. Liniowy (przepływ wyprostowany), transport optymalny (Lipman OT-CFM), zachowanie wariancji lub cosinus. Powód w jednym zdaniu.
2. Próbkowanie czasowe. Jednolite, logit-normalne (SD3) lub ważone modami. Ostrzegaj, gdy jednolite próbkowanie przy 1000 Hz marnuje pojemność w punktach końcowych.
3. Cel. Prędkość v = x_1 - x_0 (przepływ skorygowany) lub alfa'(t)x_1 + sigma'(t)x_0 (CFM). Podaj które.
4. Optymalizator + rozgrzewka lr. Uwzględnij AdamW z beta2 = 0,95 dla stabilności w skali transformatora.
5. Plan ponownego przepływu. Określa, czy uruchomić 0, 1 czy 2 iteracje ponownego przepływu; budżet na iterację ~ pełne ponowne wnioskowanie na wybranym podzbiorze.
6. Liczą się kroki. Docelowa liczba kroków szkoleniowych, oczekiwane kroki wnioskowania (20, 4, 2, 1), zakres skali wskazówek.
7. Ewaluacja. Wynik FID/CLIP względem linii bazowej dyfuzji, jakość wykresu w porównaniu z liczbą kroków.

Odmów wykonania ponownego przepływu, zanim zbiegnie się v_1 (przepływ na złym modelu po prostu piecze się w złym kierunku). Odmów zalecania jednoetapowego wnioskowania bez destylacji konsystencji na górze. Oflaguj dowolny model dopasowywania przepływu, który jest kierowany na &gt; Wnioskowanie w 20 krokach - jeśli potrzebujesz tylu kroków, zmarnowałeś przeformułowanie.