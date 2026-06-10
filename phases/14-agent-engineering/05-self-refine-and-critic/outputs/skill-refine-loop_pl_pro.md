---

name: refine-loop
description: Skonfiguruj pętlę Evaluator-Optimizer (Self-Refine / CRITIC) na podstawie specyfiki zadania, dostępnych weryfikatorów oraz budżetu iteracji.
version: 1.0.0
phase: 14
lesson: 05
tags: [self-refine, critic, evaluator-optimizer, guardrails, iteration]

---

Na podstawie opisu zadania, limitu iteracji oraz typu dostępnego weryfikatora (oparty na narzędziach lub oparty na samoocenie LLM) przygotuj prompty i reguły zakończenia dla pętli Evaluator-Optimizer.

Przygotuj:

1. Prompt generatora: Instrukcja dla modułu wytwarzającego pierwszą wersję odpowiedzi. Must precyzyjnie określać zadanie, oczekiwany format wyjściowy oraz ograniczenia.
2. Prompt oceniającego (weryfikatora): Jeśli dostępne są narzędzia (wyszukiwarki, interpretery kodu, testy jednostkowe, kalkulatory, walidatory typów), opisz sposób ich wywoływania oraz schemat tworzenia ustrukturyzowanej krytyki (format JSON zawierający pola: wynik walidacji, lista naruszeń, sugerowane poprawki). W przypadku braku narzędzi (gdy dostępna jest tylko samoocena), wskaż ryzyko bezkrytycznej akceptacji własnych błędów (problem pieczątki) i zastosuj odmienny styl promptowania (np. podejście kontradyktoryjne: „znajdź co najmniej jedną wadę w wygenerowanym tekście”).
3. Prompt poprawiającego (Optimizer/Refiner): Musi odwoływać się do wcześniejszych wersji odpowiedzi oraz otrzymanych uwag krytycznych (historia). Niezbędne jest dodanie wyraźnej instrukcji: „nie powielaj błędów wskazanych w poprzednich iteracjach”.
4. Reguła zakończenia (Stop policy): Powinna stanowić alternatywę logiczną: pomyślny wynik weryfikacji LUB (brak uwag w samoocenie ORAZ liczba iteracji >= 2) LUB osiągnięcie limitu max_iterations. Nigdy nie polegaj na pojedynczym warunku.
5. Integracja z systemami obserwowalności: Rejestruj każdą iterację jako oddzielne spany w standardzie OpenTelemetry GenAI (jako operacje oceny i optymalizacji) zgodnie z zasadami z Lekcji 23, aby umożliwić szczegółowy audyt całej ścieżki poprawek.

Kryteria odrzucenia:
- Używanie tego samego promptu lub stylu promptowania dla generatora i krytyka (ryzyko automatycznego akceptowania własnych błędów przez model).
- Brak zdefiniowanego limitu iteracji. Nieskończone pętle poprawek generują ogromne koszty; domyślny limit powinien wynosić maksymalnie 4 iteracje.
- Promptowanie weryfikatora w sposób wymuszający odpowiedź w formie tekstu ciągłego (prozy). Wymagany jest wyłącznie ustrukturyzowany format JSON (wynik walidacji oraz precyzyjna lista naruszeń).
- Usuwanie historii dotychczasowych prób z promptu poprawiającego (badania wskazują, że bez kontekstu wcześniejszych wersji jakość wyników drastycznie spada).

Zasady odmowy wykonania zadania:
- Jeśli zadanie nie posiada dedykowanego weryfikatora i nie da się go zaimplementować, odmów wdrożenia wzorca CRITIC i wskaż, że Self-Refine jest gorszą alternatywą (ostrzeż użytkownika o ryzyku bezkrytycznej akceptacji błędów).
- Jeśli limit `max_iterations` wynosi 10 lub więcej, odmów wykonania i rekomenduj przebudowę architektury zadania. Konieczność wykonywania więcej niż 3–4 poprawek zazwyczaj świadczy o tym, że prompt wejściowy generatora jest błędnie sformułowany.
- Jeśli weryfikator korzysta z narzędzi o charakterze destrukcyjnym (np. bezpośrednie polecenia powłoki, zapis do repozytorium git), odmów wykonania i zażądaj uruchomienia środowiska w bezpiecznej piaskownicy (Lekcja 09).

Oczekiwany rezultat: Jednolity blok konfiguracyjny zawierający wszystkie prompty, reguły zakończenia pętli, wykaz narzędzi oraz sekcję „Sugerowane lektury” odsyłającą do Lekcji 16 (Output Guardrails w SDK OpenAI Agents), Lekcji 12 (Evaluator-Optimizer w ujęciu Anthropic) lub Lekcji 30 (Rozwój agentów oparty na ewaluacji) w zależności od docelowej platformy.
