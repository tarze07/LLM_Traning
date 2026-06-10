---

name: primitive-splitter
description: Skategoryzuj każdą możliwość w wersji roboczej serwera MCP jako narzędzie, zasób lub podpowiedź, podając uzasadnienie.
version: 1.0.0
phase: 13
lesson: 10
tags: [mcp, primitives, resources, prompts]

---

Biorąc pod uwagę możliwości proponowanego serwera MCP (w postaci zwykłego języka angielskiego lub roboczej listy narzędzi), sklasyfikowaj każdy z nich jako narzędzie, zasób lub podpowiedź, uzasadniając to jednym zdaniem.

Wyprodukuj:

1. Kategoryzacja według zdolności. Dla każdego przedmiotu zwróć `{name, primitive: tool | resource | prompt, rationale}`.
2. Schemat URI zasobów. Jeśli jakiekolwiek możliwości staną się zasobami, zaproponuj schemat URI (`notes://`, `gh://`, `db://`) i wzorzec szablonu.
3. Szybkie szkielety argumentów. Jeśli jakiekolwiek możliwości staną się monitami, zaproponuj listę argumentów i wymagane/opcjonalne flagi.
4. Kandydaci na abonament. Oznacz zasoby, które często się zmieniają i które mogłyby skorzystać na zastosowaniu `resources/subscribe`.
5. Flagi antywzorcowe. Wskaż przypadki, w których stary projekt zawierał odczyt w narzędziu (np. `notes_read(id)`), gdy zasób działałby lepiej.

Twarde odrzucenia:
- Wszelkie możliwości sklasyfikowane jako „zarówno narzędzie, jak i zasób” bez podziału. Wybierz jeden lub stwórz parę.
- Dowolny monit bez wskazanych wymaganych argumentów. Pojawianie się w interfejsach użytkownika z poleceniami ukośnika wymaga schematów argumentów.
- Dowolny schemat URI zasobów, którego nie można adresować (ciągi znaków o dowolnej formie, a nie identyfikatory URI).

Zasady odmowy:
- Jeśli wszystkie możliwości wylądują jako narzędzia, odmów i zapytaj, czy serwer ma dane tylko do odczytu, które mogłyby stanowić zasób.
- Jeśli żadna funkcja nie pasuje do podpowiedzi, nie ma problemu; podpowiedzi są opcjonalne. Nie wymyślaj ich.
- Jeśli domena serwera jest lepiej obsługiwana przez A2A (współpraca między agentami, stan nieprzezroczysty), odmów i przekieruj do fazy 13 · 19.

Wynik: jednostronicowy raport decyzyjny z tabelą kategoryzacji, propozycją schematu URI, szkieletami podpowiedzi i flagami subskrypcji. Zakończ pojedynczym, najskuteczniejszym narzędziem -> konwersją zasobów dla tego serwera.