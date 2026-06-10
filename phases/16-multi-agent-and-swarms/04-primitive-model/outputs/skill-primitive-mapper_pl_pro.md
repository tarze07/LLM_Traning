---

name: primitive-mapper
description: Mapuj dowolny framework wieloagentowy lub bazę kodu na cztery osie prymitywów (agent, przekazanie, stan współdzielony, orkiestrator).
version: 1.0.0
phase: 16
lesson: 04
tags: [multi-agent, primitives, framework-comparison, architecture]

---

Na podstawie opisu frameworka wieloagentowego (lub bazy kodu korzystającej z takiego rozwiązania) utwórz mapowanie na cztery podstawowe prymitywy, aby czytelnik mógł zrozumieć jego architekturę w jednym zwięzłym akapicie.

Wygeneruj:

1. **Definicja agenta.** Jak definiowany jest agent? Jakie przyjmuje parametry? Jaki stan wewnętrzny przechowuje (jeśli w ogóle)? Podaj dokładną nazwę klasy lub funkcji fabrycznej.
2. **Mechanizm przekazywania (Handoff).** Który z trzech wzorców przekazywania jest stosowany — zwracanie obiektu (function return), krawędź grafu (graph edge) czy wybór mówcy (speaker selection)? W przypadku rozwiązań hybrydowych wskaż wiodący mechanizm. Pokaż minimalny fragment kodu realizujący pojedyncze przekazanie.
3. **Model stanu współdzielonego.** Pełna pula komunikatów (message pool) czy widok rzutowany/przefiltrowany (projected view)? Przechowywany w pamięci czy trwały (checkpointed)? Czy jest bezpieczny wątkowo w scenariuszach współbieżnego zapisu i kto odpowiada za rozwiązywanie konfliktów?
4. **Typ orkiestratora.** Statyczny, dynamiczny (wybierany przez LLM), sterowany przekazaniem (handoff-driven) czy sterowany kolejką (queue-driven)? Jeśli orkiestracja opiera się na decyzjach LLM, jaki model jest stosowany domyślnie? Jeśli jest statyczny, czy graf dopuszcza cykle, czy jest to DAG?
5. **Kompromisy architektoniczne.** Po jednym zdaniu na temat: determinizmu, granic skalowalności, łatwości debugowania oraz typowego trybu awarii.

Twarde kryteria odrzucenia:

- Odrzuć analizy opisujące abstrakcje jako „całkowicie nowe”, jeśli można je sprowadzić do jednego z czterech podstawowych prymitywów. Jeśli redukcja jest niemożliwa, precyzyjnie opisz tę lukę zamiast wymyślać piąty prymityw.
- Odrzuć porównania opierające się wyłącznie na materiałach marketingowych. Zawsze cytuj konkretny fragment kodu z oficjalnego repozytorium frameworka lub książki kucharskiej (cookbook).
- Odrzuć ogólne stwierdzenia typu „Framework X jest lepszy dla agentów” bez wskazania, które z czterech osi prymitywów optymalizuje dana platforma.

Zasady obsługi przypadków szczególnych:

- Jeśli kod źródłowy frameworka jest zamknięty, a publiczne dokumenty nie ujawniają szczegółów orkiestracji, przekazywania i zarządzania stanem agenta, zaznacz, że pełne mapowanie nie jest możliwe z powodu braku informacji wewnętrznych.
- Jeśli użytkownik dostarcza bazę kodu napisaną od zera bez użycia frameworków (agenci tworzeni ręcznie), zamapuj tę niestandardową implementację i wskaż, które elementy podstawowe są niedopracowane lub pominięte.
- Jeśli framework powstał przed rokiem 2024 (np. pierwotny AutoGen v0.2) i nie jest już wspierany, dołącz krótką informację, czy jego następca zachowuje tę samą strukturę mapowania.

Wynik: jednostronicowy opis struktury. Rozpocznij od jednozdaniowego podsumowania (np. „Framework X definiuje przekazywanie zadań jako krawędzie grafu, a stan współdzielony realizuje za pomocą reduktorów.”), przedstaw pięć wymaganych sekcji i zakończ akapitem określającym, dla jakiego typu projektu produkcyjnego te prymitywy są optymalne.
