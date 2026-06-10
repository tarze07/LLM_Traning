---

name: modality-bridge-picker
description: Dobierz optymalny adapter (Q-Former vs projektor MLP vs Perceiver Resampler) dla konfiguracji VLM, uwzględniając budżet tokenów, docelową jakość oraz zasoby obliczeniowe treningu.
version: 1.0.0
phase: 12
lesson: 03
tags: [blip2, qformer, vlm, modality-bridge, architecture]

---

Na podstawie podanej liczby tokenów encodera wizyjnego przypadających na obraz, budżetu kontekstu LLM, docelowej liczby obrazów w jednym prompcie oraz budżetu obliczeniowego na trening, zarekomenduj odpowiedni mostek modalny (adapter). Uzasadnij wybór liczbą parametrów oraz analizą zużycia tokenów.

Wymagane elementy:

1. Analiza budżetu tokenów. Podaj surową liczbę tokenów na obraz wygenerowanych przez encoder wizyjny, liczbę tokenów na obraz po zastosowaniu każdego z typów mostka oraz procent kontekstu LLM zużyty przy zadeklarowanej liczbie obrazów w prompcie.
2. Porównanie adapterów. Dla każdej opcji: Q-Former (32 tokeny, ~188M parametrów), projektor MLP (wszystkie patche, ~20M parametrów) oraz Perceiver Resampler (K trenowalnych zapytań poprzez N-warstwowy mechanizm cross-attention, zmienny rozmiar) — podaj liczbę parametrów, estymowaną jakość (proxy jakości) oraz szacunkowe koszty treningu.
3. Rekomendacja. Wskaż jedno optymalne rozwiązanie dla podanych ograniczeń wraz z krótkim uzasadnieniem. Wyraźnie zaznacz sytuacje, w których ograniczenia są sprzeczne (np. wysoka jakość + ograniczony budżet tokenów + małe zasoby obliczeniowe).
4. Przebieg uczenia dwuetapowego. Jeśli wybrano Q-Former, opisz działanie funkcji strat ITC + ITM + ITG dla Etapu 1 oraz stratę LM dla Etapu 2. Dla każdej z nich wskaż reprezentatywny zbiór danych (np. COCO, LAION, Visual Genome).
5. Lista kontrolna analizy wpływu (ablation checklist). Zaproponuj pięć eksperymentów, które użytkownik powinien przeprowadzić przed ostatecznym zamrożeniem architektury mostka (np. optymalizacja liczby zapytań, trening jedno- vs dwuetapowy, głębokość projektora, harmonogram zamrażania wag, dostrajanie podzbioru parametrów).

Bezwzględne odrzucenia:
- Rekomendacje ignorujące budżet tokenów (np. sugerowanie „użyj MLP” z 576 tokenami na obraz przy scenariuszu zakładającym 10 obrazów w kontekście o rozmiarze 4K).
- Twierdzenie, że Q-Former bezwzględnie przewyższa MLP. W zadaniach wysokiej jakości dotyczących pojedynczego obrazu przy braku ograniczeń okna kontekstowego MLP zazwyczaj wygrywa.
- Traktowanie Perceiver Resampler jako bezpośredniego odpowiednika Q-Formera w tej samej roli. Flamingo stosuje ten mechanizm w każdej warstwie LLM, natomiast BLIP-2 nakłada go tylko raz na wejściu.

Zasady odmowy wykonania usługi:
- Jeśli użytkownik poprosi o mostek dla danych wideo bez określenia liczby klatek oraz liczby klatek na sekundę (FPS), odmów — adaptery wideo różnią się od adapterów dla obrazów statycznych specyfikacją techniczną, a nie tylko skalą.
- Jeśli docelowy LLM jest trenowany od podstaw wspólnie z gałęzią wizyjną (early fusion, styl Chameleon), odmów i przekieruj do Lekcji 12.11, która omawia ten przypadek.
- Jeśli nie określono budżetu treningowego, odmów i zapytaj, czy użytkownik może pozwolić sobie na dwuetapowy trening w stylu BLIP-2 (rzędu kilkuset godzin na kartach A100), czy dopuszcza jedynie lekki trening samego projektora.

Dane wyjściowe: Jednostronicowa rekomendacja adaptera zawierająca wyliczenia tokenów, liczbę parametrów, sugerowaną architekturę, plan treningowy oraz listę kontrolną eksperymentów (ablation checklist). Na końcu umieść sekcję „Sugerowane lektury” odsyłającą do Lekcji 12.04 (Flamingo) o przeplataniu mechanizmów uwagi w warstwach LLM, Lekcji 12.05 (LLaVA) o projektorach MLP oraz Lekcji 12.07 o kompromisach między architekturą a danymi treningowymi.
