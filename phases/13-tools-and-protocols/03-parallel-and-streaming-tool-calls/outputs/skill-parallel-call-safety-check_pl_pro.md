---

name: parallel-call-safety-check
description: Przeprowadź audyt rejestru narzędzi pod kątem bezpieczeństwa wywołań równoległych. Oznacz każde narzędzie flagą parallel_safe, wskaż zależności kolejnościowe i określ ryzyko związane z limitami zapytań (rate limits) zewnętrznych usług.
version: 1.0.0
phase: 13
lesson: 03
tags: [parallel-tool-calls, streaming, correlation, rate-limits]

---

Na podstawie rejestru narzędzi (listy zawierającej nazwy, opisy i wykonawców narzędzi) wygeneruj jego kopię uzupełnioną o pola `parallel_safe: bool`, `ordering_deps: [tool_name]` oraz `rate_limit_group: name`.

Wygeneruj:

1. Klasyfikacja narzędzi. Dla każdego narzędzia określ, czy jest ono bezpieczne do uruchomienia równoległego w tej samej turze (operacje tylko do odczytu, brak konfliktów zasobów), czy niebezpieczne (modyfikacje danych, współdzielone zasoby, zewnętrzne limity zapytań).
2. Graf zależności. Zidentyfikuj pary narzędzi, w których dane wyjściowe jednego z nich stanowią dane wejściowe dla drugiego (co uniemożliwia ich równoległe uruchomienie w tej samej turze). Oznacz je w polu `ordering_deps`.
3. Grupowanie według limitów zapytań. Narzędzia korzystające z tego samego zewnętrznego API powinny należeć do tej samej grupy. Host powinien ograniczać współbieżność na poziomie całej grupy, a nie pojedynczego narzędzia.
4. Zalecenia dotyczące bezpieczeństwa. Dla każdego niebezpiecznego narzędzia określ, czy należy wyłączyć obsługę wywołań równoległych w danej turze, zastosować kolejkowanie, czy też podzielić zadania według zasobów.
5. Parametry specyficzne dla dostawców. Jeśli w zestawie znajduje się choć jedno niebezpieczne narzędzie, zaleć ustawienie `parallel_tool_calls=false` dla OpenAI lub `disable_parallel_tool_use=true` dla Anthropic.

Kryteria odrzucenia (Twarde reguły):
- Przekazanie rejestru bez przeprowadzenia klasyfikacji po audycie. Obowiązuje zasada domyślnej odmowy: nieznane narzędzia są traktowane jako niebezpieczne.
- Oznaczenie jako `parallel_safe: true` dowolnego narzędzia modyfikującego (ścieżka zapisu) współdzielone zasoby, co mogłoby wywołać stan wyścigu (race condition).
- Narzędzie odpytujące zewnętrzne API z limitem zapytań, które nie zostało przypisane do żadnej `rate_limit_group`.

Zasady odmowy usługi:
- Odmów, jeśli otrzymasz polecenie oznaczenia wszystkich narzędzi jako bezpiecznych do uruchomienia równoległego bez przeprowadzenia weryfikacji.
- Jeśli rejestr obejmuje narzędzia wykonujące sekwencyjne operacje na tym samym zasobie (np. `delete_file` i `write_file` na tej samej ścieżce), odmów możliwości ich równoległego uruchomienia i skieruj do fazy 14 · 09 w celu wdrożenia serializacji na poziomie piaskownicy.
- Jeśli użytkownik twierdzi, że w jego narzędziach nigdy nie dochodzi do konfliktów (wyścigów), odmów i poproś o dowody (testy, logi lub formalne uzasadnienie). W środowisku produkcyjnym stany wyścigu występują po cichu i są trudne do wykrycia.

Format wyjściowy: Zaktualizowany rejestr w postaci obiektu JSON z trzema nowymi polami dla każdego narzędzia, uzupełniony o krótkie podsumowanie wskazujące obszar najwyższego ryzyka przy współbieżności oraz zalecane środki zaradcze. Na końcu dodaj sugerowaną wartość parametru `tool_choice` dla bieżącej tury.
