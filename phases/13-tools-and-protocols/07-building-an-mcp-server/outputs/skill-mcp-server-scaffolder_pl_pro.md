---

name: mcp-server-scaffolder
description: Wygeneruj szkielet dedykowanego serwera MCP dla określonej domeny z podziałem na narzędzia, zasoby i prompty oraz określ ścieżkę migracji do gotowych SDK.
version: 1.0.0
phase: 13
lesson: 07
tags: [mcp, server, fastmcp, scaffold]

---

Na podstawie określonej domeny biznesowej (np. notatki, zgłoszenia serwisowe, pliki, baza danych) utwórz architekturę serwera MCP: określ, które funkcjonalności udostępnić jako narzędzia, które jako zasoby, a które jako szablony promptów, oraz opisz ścieżkę migracji do oficjalnych SDK (Python/TypeScript).

Wygeneruj:

1. Lista narzędzi (Tools). Operacje atomowe, o których wykonanie wnioskuje użytkownik. Dla każdego narzędzia podaj nazwę, opis (zgodny z szablonem „Use when...”), schemat wejściowy (JSON Schema) oraz adnotacje (np. destructive, read-only).
2. Lista zasobów (Resources). Dane przeznaczone do odczytu przez model lub użytkownika. Podaj schemat adresowania URI, typ MIME oraz informację, czy wspierana jest subskrypcja zasobów (`resources/subscribe`).
3. Lista szablonów promptów (Prompts). Gotowe instrukcje, które host może udostępniać użytkownikowi (np. jako slash commands). Zdefiniuj parametry wejściowe szablonów.
4. Deklaracja możliwości (Capabilities). Zdefiniuj strukturę obiektu `capabilities` zwracanego przez serwer w odpowiedzi na żądanie `initialize`.
5. Wskazówki migracyjne (Graduation Notes). Wskaż odpowiedniki zaimplementowanych elementów w bibliotekach FastMCP (Python) lub TypeScript SDK. Wymień co najmniej jedną zaawansowaną funkcję SDK (np. `lifespan`, `context`), która zastępuje ręczną implementację w czystym Pythonie.

Kryteria odrzucenia (Twarde reguły):
- Udostępnienie „odpytywania bazy danych” wyłącznie jako narzędzia, a nie jako zasobu. Prawidłowa architektura powinna udostępniać listowanie i odczyt danych jako zasoby (odpowiednio dla operacji list i read), a samo dynamiczne wysyłanie zapytań oznaczonych parametrami jako narzędzie.
- Brak rozdzielenia lub odpowiedniego oznaczenia adnotacjami narzędzi przyjmujących dane od użytkownika (user input) oraz narzędzi posiadających wysokie uprawnienia (privileged tools) w ramach tej samej przestrzeni nazw.
- Deklarowanie obsługi subskrypcji zasobów (`resources/subscribe`) bez zaimplementowania mechanizmu trwałego monitorowania zmian i wysyłania powiadomień.

Zasady odmowy usługi:
- Jeśli domena nie zawiera danych przeznaczonych wyłącznie do odczytu, odmów definiowania zasobów i zaproponuj serwer oparty wyłącznie o narzędzia.
- Jeśli specyfika domeny nie wymaga stosowania gotowych szablonów instrukcji, nie definiuj szablonów promptów.
- Jeśli użytkownik poprosi o wdrożenie mechanizmów autoryzacji i uwierzytelniania, odmów i skieruj go do fazy 13 · 16 (OAuth 2.1).

Format wyjściowy: Jednostronicowa architektura serwera zawierająca wykazy trzech podstawowych komponentów, strukturę obiektu capabilities oraz krótki (około 10 linii) fragment kodu demonstrujący użycie gotowego SDK w stylu dekoratorów (`@app.tool()`). Na końcu określ jedną, najważniejszą flagę adnotacji (annotation flag), którą serwer powinien zdefiniować dla swoich narzędzi.
