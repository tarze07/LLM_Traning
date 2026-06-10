---

name: mcp-transport-migrator
description: Przygotuj plan migracji ze starszego protokołu HTTP+SSE do strumieniowego protokołu HTTP z ciągłością identyfikatora sesji i weryfikacją Origin.
version: 1.0.0
phase: 13
lesson: 09
tags: [mcp, streamable-http, sse-migration, session-id, origin]

---

Biorąc pod uwagę istniejący serwer MCP HTTP+SSE (starszy), przygotuj plan migracji do strumieniowego protokołu HTTP z jednym punktem końcowym.

Wyprodukuj:

1. Przepisanie punktu końcowego. Połącz `/messages` i `/sse` w jeden `/mcp`. Mapuj POST na obsługę żądania, GET na strumień SSE, DELETE na zakończenie sesji.
2. Ciągłość sesji. Wygeneruj nowy `Mcp-Session-Id` w pierwszym POST. Odrzuć identyfikatory dostarczone przez klienta. Zachowaj logikę pomostową, jeśli klient najpierw wyśle ​​plik cookie starszej sesji.
3. Sprawdzenie pochodzenia. Lista dozwolonych wyraźnych źródeł produkcji (`https://app.company.com`, `https://claude.ai`, warianty hosta lokalnego). Odrzuć wszystkie inne za pomocą 403.
4. Powtórka identyfikatora ostatniego zdarzenia. Zachowaj bufor pierścieniowy ostatnich zdarzeń na sesję, aby ponowne połączenia mogły zostać wznowione.
5. Okno wycofania. Udokumentuj datę przejścia i 60-dniowy okres karencji, w którym starsze punkty końcowe wskazują 301 na nowy, za pomocą nagłówka ostrzeżenia.

Twarde odrzucenia:
- Dowolny plan, który utrzymuje oba punkty końcowe przy życiu przez czas nieokreślony. Starsza wersja SSE zostanie usunięta w 2026 r.
- Dowolny plan, w którym identyfikatory sesji są generowane przez klienta. Łamie wymagania dotyczące losowości kryptograficznej.
- Dowolny plan bez weryfikacji Origin. Luka w zabezpieczeniach polegająca na ponownym wiązaniu DNS.

Zasady odmowy:
- Jeśli serwer jest serwerem lokalnym (stdio), odmów migracji do HTTP; stdio jest poprawne dla lokalnego.
- Jeśli serwer nie udostępnia jeszcze protokołu OAuth, ukończ fazę 13 · 16 przed udostępnieniem go publicznie.
- Jeśli docelowy hosting nie obsługuje długotrwałego protokołu HTTP (np. Bezpłatna warstwa Vercel), odmów i polecaj pracowników Cloudflare.

Dane wyjściowe: element Runbook migracji ze zmianami punktów końcowych, listą dozwolonych pochodzenia, planem identyfikatorów sesji, harmonogramem wycofywania i testową listą kontrolną obejmującą inicjowanie, narzędzia/listę, powiadomienia o przesyłaniu strumieniowym, ponowne połączenie z identyfikatorem ostatniego zdarzenia i jawne DELETE.