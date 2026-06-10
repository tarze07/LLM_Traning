---

name: mcp-server-scaffolder
description: Zbuduj serwer MCP specyficzny dla domeny z odpowiednim podziałem narzędzi/zasobów/podpowiedzi i ścieżką stopniowania pakietu SDK.
version: 1.0.0
phase: 13
lesson: 07
tags: [mcp, server, fastmcp, scaffold]

---

Biorąc pod uwagę domenę (notatki, bilety, pliki, bazę danych, cokolwiek), utwórz plan serwera MCP: które możliwości udostępnić jako narzędzia, które jako zasoby, które jako podpowiedzi, a także ścieżkę stopniowania do zestawu SDK języka Python lub TypeScript.

Wyprodukuj:

1. Lista narzędzi. Operacje atomowe, o wykonanie których użytkownik wyraźnie prosi. Dołącz nazwę, opis (wzorzec „Użyj, kiedy”), schemat wejściowy i wskazówki dotyczące adnotacji.
2. Lista zasobów. Dane, które użytkownik chce przeczytać. Schemat URI, typ MIME i możliwość włączenia `resources/subscribe`.
3. Lista podpowiedzi. Szablony wielokrotnego użytku, które host powinien udostępniać jako polecenia ukośnika. Lista argumentów.
4. Deklaracja zdolności. Dokładny obiekt `capabilities`, który serwer zwraca w `initialize`.
5. Notatki maturalne. Odpowiedniki FastMCP (Python) lub TypeScript SDK dla każdego elementu. Wymień jedną funkcję SDK (np. `lifespan`, `context`), która zastępuje ręcznie wykonany wzór stdlib z rusztowania.

Twarde odrzucenia:
- Każde „zapytanie do bazy danych” ujawniane tylko jako narzędzie, a nie jako zasób. Prawidłowy podział to zasoby dla `/list` i `/read`, narzędzie dla `/query` z parametrami.
- Dowolny serwer, który łączy narzędzia wprowadzania danych przez użytkownika z narzędziami uprzywilejowanymi w tej samej przestrzeni nazw, bez adnotacji.
- Dowolne rusztowanie serwerowe obsługujące standard `resources/subscribe` bez trwałego mechanizmu powiadamiania.

Zasady odmowy:
- Jeśli domena nie ma powierzchni tylko do odczytu, odmów korzystania z zasobów; polecam serwer składający się wyłącznie z narzędzi.
- Jeśli domena nie ma naturalnych szablonów poleceń z ukośnikiem, nie stosuj podpowiedzi.
- Jeśli użytkownik poprosi o schemat autoryzacji, odmów i przejdź do fazy 13 · 16 (OAuth 2.1).

Dane wyjściowe: jednostronicowy plan serwera z trzema listami pierwotnymi, obiektem możliwości i 10-wierszowym przykładowym fragmentem kodu stopniowania w stylu dekoratora `@app.tool()`. Zakończ pojedynczą, najważniejszą flagą adnotacji, którą serwer powinien ustawić.