---

name: positional-encoding-picker
description: Wybierz kodowanie pozycyjne (RoPE, ALiBi, sinusoidalne) + strategię skalowania, biorąc pod uwagę długość kontekstu i budżet szkoleniowy.
version: 1.0.0
phase: 7
lesson: 4
tags: [transformers, positional-encoding, rope, alibi]

---

Biorąc pod uwagę specyfikację transformatora (długość kontekstu docelowego w momencie wnioskowania, długość wyuczonego kontekstu, wymagania ekstrapolacji, dostrojenie budżetu w tokenach), wynik:

1. Kodowanie podstawowe. Jeden z: RoPE, ALiBi, sinusoidalny, wyuczony-absolutny. Powód w jednym zdaniu.
2. Hiperparametry. Jeśli RoPE: wartość `base`, wymaganie `d_head` dla równego podziału. Jeśli ALiBi: wzór na nachylenie. Jeśli sinusoidalny: `max_len`.
3. Strategia rozszerzenia. Jeśli cel > przeszkolony: współczynnik skalowania uwzględniający NTK, konfiguracja YaRN, specyfikacja LongRoPE lub współczynnik interpolacji pozycji. Podaj dokładny budżet tokena.
4. Plan testów. NIAH (igła w stogu siana) docelowy współczynnik zdawalności w maksymalnym kontekście, zakłopotanie w obrębie X wyszkolonej długości linii bazowej.
5. Powrót. Co zrobić, jeśli ocena w długim kontekście nie powiedzie się: przeszkol się ponownie z większym `base`, przełącz się na ALiBi lub ogranicz długość wdrożonego kontekstu.

Odmów rekomendowania sinusoidalnego lub wyuczonego absolutu dla nowych modeli w 2026 r. – nie ekstrapolują i każdy nowoczesny stos zakłada RoPE lub ALiBi. Odmawiaj skalowania RoPE powyżej 8× wyszkolonej długości bez etapu dostrajania. Odmów dostarczenia konfiguracji o długim kontekście bez uruchomienia NIAH na pełnej wdrożonej długości.