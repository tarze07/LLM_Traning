---

name: primitive-splitter
description: Dokonaj klasyfikacji funkcjonalności projektowanego serwera MCP, dzieląc je na narzędzia, zasoby oraz szablony promptów wraz z technicznym uzasadnieniem.
version: 1.0.0
phase: 13
lesson: 10
tags: [mcp, primitives, resources, prompts]

---

Na podstawie opisu funkcjonalności planowanego serwera MCP (zapisanego w języku naturalnym lub jako wstępna lista narzędzi) sklasyfikuj każdą z nich jako narzędzie (tool), zasób (resource) lub szablon promptu (prompt) wraz z jednozdaniowym uzasadnieniem technicznym.

Wygeneruj:

1. Klasyfikacja funkcjonalności. Dla każdego elementu wygeneruj obiekt `{name, primitive: tool | resource | prompt, rationale}`.
2. Struktura adresów URI zasobów. Jeśli funkcjonalność zostanie sklasyfikowana jako zasób, zaproponuj schemat adresowania URI (np. `notes://`, `gh://`, `db://`) oraz szablon adresu (URI template).
3. Struktura parametrów promptów. Jeśli funkcjonalność zostanie sklasyfikowana jako szablon promptu, zdefiniuj listę argumentów wejściowych wraz z flagami określającymi ich wymagalność.
4. Propozycje subskrypcji. Wskaż zasoby, których zawartość ulega częstym zmianom i które odniosłyby korzyść z wdrożenia mechanizmu subskrypcji (`resources/subscribe`).
5. Wykrywanie antywzorców. Wskaż elementy, w których wcześniejsła architektura implementowała odczyt danych jako narzędzie (np. `notes_read(id)`), mimo że w danym przypadku znacznie lepiej sprawdziłby się zasób.

Kryteria odrzucenia (Twarde reguły):
- Zaklasyfikowanie funkcjonalności jako „jednocześnie narzędzie i zasób” bez przeprowadzenia podziału. Należy wybrać jeden z tych komponentów lub zaprojektować powiązaną parę.
- Definiowanie szablonu promptu bez określenia wymaganych parametrów wejściowych (wyświetlanie promptów w interfejsie użytkownika jako slash commands wymaga zdefiniowania schematu parametrów).
- Proponowanie schematów URI, które nie spełniają standardu adresowania (np. dowolne ciągi tekstowe zamiast poprawnych adresów URI).

Zasady odmowy usługi:
- Jeśli wszystkie zgłoszone funkcjonalności zostaną sklasyfikowane jako narzędzia, odmów weryfikacji i zapytaj użytkownika, czy serwer nie przetwarza danych przeznaczonych wyłącznie do odczytu, które mogłyby zostać udostępnione jako zasoby.
- Jeśli domena nie wymaga stosowania szablonów promptów, pomiń ich definiowanie (prompty are komponentem opcjonalnym, nie należy ich tworzyć na siłę).
- Jeśli domena serwera powinna być obsłużona przez architekturę A2i/A2A (komunikacja agent-agent, stan nieprzejrzysty), odmów weryfikacji i skieruj użytkownika do fazy 13 · 19.

Format wyjściowy: Jednostronicowy raport z analizy zawierający tabelę klasyfikacji funkcjonalności, proponowane schematy URI, parametry szablonów promptów oraz konfigurację subskrypcji. Na końcu wskaż jedną, najbardziej kluczową zmianę polegającą na konwersji narzędzia w zasób na tym serwerze.
