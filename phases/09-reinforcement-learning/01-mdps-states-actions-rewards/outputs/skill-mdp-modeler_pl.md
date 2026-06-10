---

name: mdp-modeler
description: Mając opis zadania, przed szkoleniem przygotuj specyfikację procesu decyzyjnego Markowa i oznacz ryzyko związane z formułowaniem ryzyka.
version: 1.0.0
phase: 9
lesson: 1
tags: [rl, mdp, modeling]

---

Biorąc pod uwagę zadanie (kontrola / gra / rekomendacja / dostrajanie LLM), wynik:

1. Stan. Dokładny wektor cech lub specyfikacja tensora. Uzasadnij własność Markowa.
2. Akcja. Zbiór dyskretny lub zakres ciągły. Wymiarowość.
3. Przejście. Deterministyczne, stochastyczne ze znanym modelem lub tylko próbki.
4. Nagroda. Funkcja i źródło. Rzadkie vs kształtne. Terminal vs na krok.
5. Rabat. Uzasadnienie wartości i horyzontu.

Odmawiaj wysyłania jakichkolwiek MDP, których stan nie jest markowski, bez wyraźnej wzmianki o układaniu ramek lub stanie powtarzającym się. Odrzuć jakąkolwiek nagrodę, która nie została zdefiniowana w kategoriach docelowego wyniku. Oflaguj dowolny `γ ≥ 1.0` w zadaniu o nieskończonym horyzoncie. Oznacz dowolny zakres nagród >100-krotność typowej nagrody za krok jako prawdopodobne źródło eksplozji gradientowej.