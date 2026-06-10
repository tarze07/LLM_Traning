---

name: refine-loop
description: Skonfiguruj pętlę ewaluatora-optymalizatora (Self-Refine / CRITIC) dla danego zadania, dostępności weryfikatora i budżetu iteracji.
version: 1.0.0
phase: 14
lesson: 05
tags: [self-refine, critic, evaluator-optimizer, guardrails, iteration]

---

Biorąc pod uwagę zadanie, budżet iteracji i dostępny weryfikator (tylko oparty na narzędziach lub samoewaluujący), emituj podpowiedzi i zasady zatrzymywania dla pętli oceniający-optymalizator.

Wyprodukuj:

1. Podpowiedź generatora. Deterministyczny producent dla pierwszego wyjścia. Określ wyraźnie zadanie, format wyjściowy i ograniczenia.
2. Podpowiedź oceniającego/weryfikatora. Jeśli dostępne są narzędzia (wyszukiwanie, uruchamianie kodu, testy, kalkulator, sprawdzanie typu), określ, jak je wywołać i jak przygotować ustrukturyzowaną krytykę (JSON z: zaliczony/niezaliczony, naruszenia [], sugerowane_poprawki []). Jeśli dostępna jest tylko samoocena, wyraźnie oznacz ryzyko pieczątki związanej z samodoskonaleniem i użyj strukturalnie innego stylu podpowiedzi (np. kontradyktoryjnego „znajdź co najmniej jedną wadę”).
3. Monit dotyczący rafinacji. Musi odwoływać się do wcześniejszych wyników i krytyki (historia). Obowiązkowe jest stwierdzenie, że „nie powtarzaj trybu awarii oznaczonego w poprzednich iteracjach”.
4. Zatrzymaj politykę. Spójnik: weryfikator przechodzi OR (samoewaluacja mówi dobrze ORAZ iteracje >= 2) OR iteracje >= max_iterations. Nigdy z jednym warunkiem.
5. Haki obserwowalności. Rejestruj każdą iterację jako zakres OpenTelemetry GenAI (oceń, optymalizuj) zgodnie z Lekcją 23, aby możliwa była kontrola trajektorii pełnego udoskonalenia.

Twarde odrzucenia:

- Ten sam monit dla generatora i krytyka. Ryzyko pieczątki – model zgadza się sam ze sobą.
- Brak limitu iteracji. Nieskończone pętle udoskonalania spalają tokeny; zawsze domyślnie ograniczaj do 4.
- Monit weryfikatora z prośbą o opinię w formie dowolnej prozy. Tylko strukturalny JSON — wynik pozytywny/negatywny oraz szczegółowe naruszenia.
- Usunięcie historii z monitu rafinera. Papier pokazuje, że bez niego jakość się załamuje.

Zasady odmowy:

- Jeśli zadanie nie ma weryfikatora i nie ma możliwości jego zbudowania, odrzuć KRYTYKA i zwróć uwagę, że Self-Refine jest słabszą dostępną opcją - ostrzeż użytkownika o ryzyku pieczątki.
- Jeśli max_iterations >= 10, odmów i zaleć zmianę architektury zadania. Doprecyzowanie do zbieżności powyżej 3-4 przebiegów jest zwykle sygnałem, że komunikat generatora jest nieprawidłowy.
- Jeśli weryfikator wywołuje narzędzia destrukcyjne (Shell, git write), odrzuć i zażądaj granicy piaskownicy (Lekcja 09).

Dane wyjściowe: pojedynczy blok konfiguracyjny ze wszystkimi monitami, polityką zatrzymania i listą narzędzi oraz notatką „co dalej przeczytać” wskazującą lekcję 16 (poręcze SDK agentów OpenAI), lekcję 12 (optymalizator-optymalizator ewaluacji Anthropic) lub lekcję 30 (tworzenie agenta oparte na ewaluacji) w oparciu o cel wdrożenia.