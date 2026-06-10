---

name: rewoo-planner
description: Wygeneruj zatwierdzony DAG planu ReWOO na podstawie żądań użytkownika i katalogu narzędzi.
version: 1.0.0
phase: 14
lesson: 02
tags: [rewoo, plan-and-execute, planning, dag, distillation]

---

Biorąc pod uwagę żądanie użytkownika i katalog narzędzi (nazwa, schemat wejściowy, opis), utwórz plan ReWOO: DAG kroków z wywołaniami narzędzi i odniesieniami do dowodów (`#E1`, `#E2`, ...). Zatwierdź plan przed przekazaniem go wykonawcy.

Wyprodukuj:

1. Plan DAG. Każdy węzeł ma identyfikator (`E1`, `E2`, ...), nazwę narzędzia, argument dict (ciągi mogą zawierać odniesienia do `#E<k>`) i opcjonalną etykietę `parallel_group`.
2. Dane wyjściowe walidacji. Kontrola acykliczności poprzez sortowanie topologiczne; sprawdzenie rozdzielczości referencyjnej (każdy `#E<k>` ma poprzedniego producenta); sprawdzenie istnienia narzędzia (każda nazwa narzędzia znajduje się w katalogu); sprawdzenie schematu arg (każdy argument pasuje do schematu wejściowego narzędzia).
3. Wskazówka dotycząca równoległości. Dla każdego poziomu topologicznego wypisz węzły, które mogą być wykonywane współbieżnie.
4. Zalecenie podziału planisty/solvera. Jeśli plan składa się z mniej niż 3 kroków, polecam zamiast tego ReAct. Jeśli plan wymaga nieograniczonej pętli (ponowne planowanie na każdym kroku), zalecamy zaplanowanie i wykonanie z osobą ponownie planującą. Jeśli plan przekracza 30 kroków lub jest ukierunkowany na Internet/mobile, zalecamy Planuj i Działaj z syntetycznymi danymi planu.

Twarde odrzucenia:

- Plany z cyklami. ReWOO zakłada DAG; cykle są problemem ReAct lub LATS.
- Plany odwołujące się do `#E<k>`, gdzie `k` jeszcze nie istnieje w porządku topologicznym. Emituj konkretną krawędź, która kończy się niepowodzeniem.
- Plany wywołujące narzędzia, których nie ma w katalogu. Nie wymyślaj narzędzi, dzięki którym plan zadziała.
- Plany, w których typ argumentu odwołania nie jest zgodny ze schematem narzędzia (np. `#E1` zastępuje ciąg znaków, ale narzędzie oczekuje liczby typu int).

Zasady odmowy:

- Jeśli zadanie ma charakter otwarty (potrzebne nieznane narzędzia, nieznane kroki), odmów i polecam ReAct lub LATS (lekcja 04).
- Jeśli katalog narzędzi zawiera destrukcyjne narzędzia bez narzędzia do zatwierdzania bramkowania, odrzuć i przejdź do Lekcji 09 (uprawnienia, piaskownica).

Dane wyjściowe: ustrukturyzowany plan (JSON lub YAML), raport z walidacji, mapa równoległości i akcja uzupełniająca wskazująca wykonawcę (ReWOO Worker), osobę ponownie planującą (Planuj i wykonaj) lub większą pętlę próbkowania trajektorii (Planuj i działaj).

Zakończ notatką „co dalej czytać” wskazującą na Lekcję 03 (Refleksja), jeśli próbowano już wykonać tę klasę zadań, lub Lekcję 04 (LATS), jeśli wyszukiwanie przyniesie korzyści dla planu.