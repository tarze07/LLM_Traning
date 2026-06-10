---

name: sampling-tuner
description: Wybierz strategię dekodowania (greedy, temperature, top-k, top-p, min-p, speculative decoding) dla danego zadania generacji tekstu.
version: 1.0.0
phase: 7
lesson: 7
tags: [gpt, sampling, decoding, inference]

---

Na podstawie zadania generowania (kod, pisanie kreatywne, wnioskowanie, dialog, ustrukturyzowany format wyjściowy) oraz wymagań dotyczących opóźnienia i jakości wygeneruj:

1. Strategia dekodowania (próbkowania): jedna z metod: greedy, tylko ze zmienioną temperaturą, top-k, top-p, min-p, beam search lub dekodowanie spekulatywne. Podaj jednozdaniowe uzasadnienie.
2. Wartości parametrów: temperatura, top-k, top-p, min-p, kara za powtórzenia (repetition penalty) – konkretne wartości liczbowe powiązane z typem zadania (np. temperatura 0.2 + top-p 1.0 dla generowania kodu; min-p 0.1 + temperatura 0.7 dla czatu).
3. Warunki zatrzymania: `max_new_tokens`, lista tokenów zatrzymania (stop tokens), zatrzymanie oparte na wzorcu (np. tag zamykający `</tool_call>`).
4. Determinizm: ustawienie stałego ziarna generatora (seed) dla zapewnienia powtarzalności; wskaż, czy przypadek użycia tego wymaga (np. testy ewaluacyjne, zastosowania prawne).
5. Weryfikacja jakości: prosty test sprawdzający poprawność wyniku w odniesieniu do celu zadania (np. kompilacja/zaliczenie testów jednostkowych kodu, poprawność faktograficzna, poprawność formatu strukturalnego).

Odmawiaj rekomendowania temperatury > 1.0 dla zadań generowania ustrukturyzowanego formatu lub kodu – ryzyko halucynacji i błędów składniowych gwałtownie wzrasta. Odmawiaj rekomendowania wyłącznie dekodowania zachłannego (greedy) do swobodnego dialogu – model ma wtedy tendencję do zapętlania się. Odmawiaj zatwierdzania konfiguracji próbkowania bez zdefiniowanej listy tokenów stop (stop tokens), gdy model ma generować wywołania narzędzi lub szablony.
