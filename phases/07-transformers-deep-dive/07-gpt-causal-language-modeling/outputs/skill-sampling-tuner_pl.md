---

name: sampling-tuner
description: Wybierz strategię dekodowania (zachłanny / temperatura / top-k / top-p / min-p / spekulatywna) dla danego zadania generacji.
version: 1.0.0
phase: 7
lesson: 7
tags: [gpt, sampling, decoding, inference]

---

Biorąc pod uwagę zadanie generowania (kod, twórcze pisanie, rozumowanie, dialog, ustrukturyzowany wynik) i docelowe opóźnienie/jakość, wynik:

1. Metoda pobierania próbek. Jeden z: zachłanny, tylko temperatura, top-k, top-p, min-p, belka-k, spekulacyjny. Powód w jednym zdaniu.
2. Wartości parametrów. Temperatura, górne-k, górne-p, min-p, kara za powtórzenie — konkretne liczby powiązane z typem zadania. (np. temperatura 0,2 + top-p 1,0 dla kodu; min-p 0,1 + temperatura 0,7 dla czatu.)
3. Warunki zatrzymania. `max_new_tokens`, lista tokenów zatrzymania, zatrzymanie oparte na wzorcu (np. zamknięcie `</tool_call>`).
4. Przełącznik determinizmu. Naprawiono materiał siewny zapewniający powtarzalność; zaznacz, czy wymaga tego przypadek użycia (eval, legal).
5. Kontrola jakości. Test jednowierszowy względem celu zadania (kompilacja/zaliczenie testów jednostkowych, rzeczowość, ważność formatu itp.).

Odmów zalecania temperatury > 1,0 w przypadku ustrukturyzowanych wyników lub uzupełniania kodu — ryzyko halucynacji gwałtownie wzrasta. Odmów polecania czystej chciwości do otwartego dialogu – model będzie się zapętlał. Odmów dostarczenia konfiguracji próbkowania bez określonej listy tokenów zatrzymujących, gdy model może generować szablony/narzędzia.