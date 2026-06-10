---

name: parallel-call-safety-check
description: Przeprowadź audyt rejestru narzędzi pod kątem bezpiecznej równoległości. Oznacz każde narzędzie równolegle_bezpieczne, zanotuj zależności w kolejności i oznacz ryzyko związane z limitem stawki na dalszym etapie.
version: 1.0.0
phase: 13
lesson: 03
tags: [parallel-tool-calls, streaming, correlation, rate-limits]

---

Biorąc pod uwagę rejestr narzędzi (listę narzędzi z nazwami, opisami i wykonawcami), zwróć kopię z adnotacjami z dodanymi polami `parallel_safe: bool`, `ordering_deps: [tool_name]` i `rate_limit_group: name`.

Wyprodukuj:

1. Klasyfikacja według narzędzia. Dla każdego narzędzia zdecyduj: bezpieczne uruchamianie równolegle w tej samej turze (czyste odczyty, różne zasoby); niebezpieczne (mutacje, współdzielone zasoby, zewnętrzne limity szybkości).
2. Wykres zależności. Zidentyfikuj pary, w których wyniki jednego narzędzia powinny zasilać dane wejściowe innego. Nie można wykonać równoległego ruchu w zakręcie. Oznacz za pomocą `ordering_deps`.
3. Grupowanie z limitem stawek. Narzędzia, które trafiają do tego samego późniejszego interfejsu API, dzielą grupę. Host powinien ograniczać współbieżność dla poszczególnych grup, a nie poszczególnych narzędzi.
4. Zalecenia dotyczące bezpieczeństwa. Dla każdego niebezpiecznego narzędzia określ, czy wyłączyć połączenie równoległe dla tej tury, kolejki lub fragmentu według zasobu.
5. Flagi specyficzne dla dostawcy. Polecaj `parallel_tool_calls=false` na OpenAI lub `disable_parallel_tool_use=true` na Anthropic, jeśli w zestawie znajduje się jakieś niebezpieczne narzędzie.

Twarde odrzucenia:
- Dowolny rejestr bez klasyfikacji po audycie. Domyślna odmowa; nieznane oznacza niebezpieczne.
- Dowolne narzędzie ścieżki zapisu na współdzielonym zasobie oznaczonym `parallel_safe: true`. Warunki wyścigu.
- Każde narzędzie, które trafia do zewnętrznego API z ograniczoną szybkością bez `rate_limit_group`.

Zasady odmowy:
- Jeśli zostaniesz poproszony o oznaczenie wszystkich narzędzi jako równoległych bez kontroli, odmów.
- Jeśli rejestr zawiera narzędzia następcze w tym samym zasobie (`delete_file` i `write_file` w tej samej ścieżce), odmów równoległości i skierowania do fazy 14 · 09 w celu serializacji na poziomie piaskownicy.
- Jeśli użytkownik twierdzi, że jego narzędzia nigdy się nie ścigają, odmów i poproś o dowód (testy, logi lub formalny argument). Wyścigi odbywają się w trybie produkcyjnym po cichu.

Dane wyjściowe: poprawiony rejestr w postaci obiektu blob JSON z trzema nowymi polami na każde narzędzie, po którym następuje krótkie podsumowanie zawierające nazwę opcji równoległości o najwyższym ryzyku i zalecane środki zaradcze. Zakończ sugerowaną zmianą `tool_choice` na obecną turę.