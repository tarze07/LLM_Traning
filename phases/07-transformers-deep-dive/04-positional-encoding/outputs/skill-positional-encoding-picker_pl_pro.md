---

name: positional-encoding-picker
description: Dobierz kodowanie pozycyjne (RoPE, ALiBi, sinusoidalne) oraz strategię skalowania w oparciu o długość kontekstu i budżet treningowy.
version: 1.0.0
phase: 7
lesson: 4
tags: [transformers, positional-encoding, rope, alibi]

---

Na podstawie specyfikacji modelu (docelowa długość kontekstu podczas wnioskowania, długość kontekstu podczas treningu bazowego, wymagania dotyczące ekstrapolacji, budżet tokenów na dostrojenie/fine-tuning) wygeneruj:

1. Podstawowe kodowanie pozycyjne: jedno z RoPE, ALiBi, sinusoidalne (sinusoidal), wyuczone absolutne (learned absolute). Podaj uzasadnienie w jednym zdaniu.
2. Hiperparametry: dla RoPE: wartość bazowa (`base`), podział wymiaru `d_head`. Dla ALiBi: wzór na nachylenia głowic (slopes). Dla sinusoidalnego: `max_len`.
3. Strategia rozszerzenia kontekstu: w przypadku, gdy docelowa długość jest większa niż długość treningowa – wskaż skalowanie zorientowane na NTK (NTK-aware), konfigurację YaRN, specyfikację LongRoPE lub interpolację pozycyjną (position interpolation). Podaj budżet tokenów wymagany do dostrojenia.
4. Plan testów: docelowy współczynnik skuteczności w teście NIAH (Needle In A Haystack) w maksymalnym kontekście oraz poziom perpleksyjności (perplexity) w odniesieniu do linii bazowej.
5. Plan awaryjny (fallback): kroki do podjęcia w przypadku niepowodzenia ewaluacji długiego kontekstu (np. ponowny trening z większą wartością bazową `base` w RoPE, przejście na ALiBi lub ograniczenie długości wdrożonego kontekstu).

Odmawiaj rekomendowania sinusoidalnego lub wyuczonego absolutnego kodowania pozycyjnego dla nowych modeli – nie pozwalają one na ekstrapolację, a nowoczesne implementacje opierają się na RoPE lub ALiBi. Odmawiaj skalowania RoPE powyżej 8x długości treningowej bez etapu dostrajania (fine-tuning). Odmawiaj zatwierdzenia konfiguracji długiego kontekstu bez uruchomienia testów NIAH na pełnej deklarowanej długości kontekstu.
