---

name: rewoo-planner
description: Wygeneruj i zweryfikuj plan ReWOO w postaci grafu DAG na podstawie zapytania użytkownika oraz katalogu narzędzi.
version: 1.0.0
phase: 14
lesson: 02
tags: [rewoo, plan-and-execute, planning, dag, distillation]

---

Na podstawie zapytania użytkownika oraz katalogu narzędzi (zawierającego nazwę, schemat wejściowy i opis) utwórz plan ReWOO: graf DAG złożony z kolejnych kroków, wywołań narzędzi i odniesień do dowodów (`#E1`, `#E2`, ...). Zweryfikuj poprawność planu przed przekazaniem go do wykonawcy.

Przygotuj:

1. Plan w postaci grafu DAG: Każdy węzeł musi posiadać identyfikator (`E1`, `E2`, ...), nazwę narzędzia, słownik argumentów (wartości tekstowe mogą zawierać odniesienia do `#E<k>`) oraz opcjonalną etykietę grupy równoległej (`parallel_group`).
2. Wynik walidacji: Potwierdzenie acykliczności grafu za pomocą sortowania topologicznego; weryfikacja poprawności referencji (każde odniesienie `#E<k>` musi wskazywać na wynik wygenerowany we wcześniejszym kroku); kontrola dostępności narzędzi (każde wywoływane narzędzie musi znajdować się w katalogu); weryfikacja schematu argumentów (każdy argument musi być zgodny ze schematem wejściowym narzędzia).
3. Sugestie dotyczące równoległego uruchamiania: Dla każdego poziomu topologicznego wskaż węzły, które mogą być wykonywane współbieżnie.
4. Rekomendacja w zakresie wyboru architektury: Jeśli plan wymaga mniej niż 3 kroków, zalecaj użycie ReAct. Jeśli proces wymaga ciągłego, dynamicznego dostosowywania planu (ponowne planowanie na każdym kroku), rekomenduj wzorzec Plan-and-Execute z modułem replannera. Jeśli plan przekracza 30 kroków lub dotyczy zadań w środowisku internetowym/mobilnym, zalecaj podejście Plan-and-Act z generowaniem syntetycznych danych planowania.

Kryteria odrzucenia:
- Plany zawierające cykle: Architektura ReWOO wymaga struktury DAG; cykle powinny być obsługiwane przez ReAct lub LATS.
- Plany odwołujące się do `#E<k>`, gdzie `k` nie zostało jeszcze zdefiniowane w porządku topologicznym. Wskaż precyzyjnie niepoprawne połączenie (krawędź grafu).
- Plany odwołujące się do narzędzi spoza katalogu. Niedozwolone jest halucynowanie nieistniejących narzędzi w celu sztucznego domknięcia planu.
- Plany, w których typ przekazywanej zmiennej referencyjnej jest niezgodny ze schematem oczekiwanym przez narzędzie (np. `#E1` zwraca ciąg znaków, a kolejne narzędzie oczekuje liczby całkowitej).

Zasady odmowy wykonania zadania:
- Jeśli zadanie ma charakter otwarty (wymaga nieznanych narzędzi lub nieokreślonych kroków), odmów wykonania i rekomenduj użycie ReAct lub LATS (lekcja 04).
- Jeśli katalog narzędzi zawiera operacje o charakterze destrukcyjnym, które nie mają wdrożonego mechanizmu autoryzacji (bramki akceptacji), odmów wykonania i odeślij do Lekcji 09 (uprawnienia, piaskownica).

Oczekiwany rezultat: Ustrukturyzowany plan (w formacie JSON lub YAML), raport z walidacji, mapa zadań równoległych oraz rekomendacja dalszych kroków wskazująca na wykonawcę (ReWOO Worker), replanner (Plan-and-Execute) lub pętlę próbkowania trajektorii o dłuższym horyzoncie czasowym (Plan-and-Act).

Na końcu dodaj sekcję „Sugerowane lektury” odsyłającą do Lekcji 03 (Refleksja) – jeśli to zadanie było już wcześniej realizowane – lub do Lekcji 04 (LATS) – jeśli proces planowania odniósłby korzyść z przeszukiwania przestrzeni rozwiązań.
