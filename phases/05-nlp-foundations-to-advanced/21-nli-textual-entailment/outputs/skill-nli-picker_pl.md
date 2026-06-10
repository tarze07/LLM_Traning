---

name: nli-picker
description: Wybierz model NLI, szablon etykiety i konfigurację oceny dla zadania klasyfikacji/wierności/zero-shot.
version: 1.0.0
phase: 5
lesson: 21
tags: [nlp, nli, zero-shot]

---

Biorąc pod uwagę przypadek użycia (sprawdzanie wierności, klasyfikacja zerowa, wnioskowanie na poziomie dokumentu), wynik:

1. Modelka. Nazwany punkt kontrolny NLI. Powód związany z domeną, długością, językiem.
2. Szablon (jeśli strzał zerowy). Wzór werbalizacji. Przykład.
3. Próg. Wartość odcięcia dla reguły decyzyjnej. Powód oparty na kalibracji.
4. Ocena. Dokładność w zbiorze oznaczonym, linia bazowa oparta wyłącznie na hipotezach, podzbiór kontradyktoryjny.

Odmów wysyłki kategorii zero-shot bez sprawdzenia poprawności 100 etykiet. Odmawiaj stosowania modelu NLI na poziomie zdania w przypadku przesłanek dotyczących długości dokumentu. Oznacz każde twierdzenie, że NLI rozwiązuje halucynacje — zmniejsza je; nie eliminuje tego.