---

name: mcp-apps-spec
description: Przygotuj pełną umowę dotyczącą aplikacji MCP dla narzędzia wymagającego interaktywnego zasobu interfejsu użytkownika.
version: 1.0.0
phase: 13
lesson: 14
tags: [mcp, apps, ui-resources, csp, iframe-sandbox]

---

Mając narzędzie, które skorzystałoby na interaktywnym interfejsie użytkownika (oś czasu, formularz, pulpit nawigacyjny, mapa, wykres), utwórz umowę dotyczącą aplikacji MCP.

Wyprodukuj:

1. URI `ui://`. Jedna nazwa kanoniczna zasobu interfejsu użytkownika (np. `ui://notes/timeline`).
2. Kształt wyniku narzędzia. `content[]` z preambułą `text` i blokiem `ui_resource`; Zapełniony `_meta.ui`.
3. CSP. Minimalna lista dozwolonych dla `default-src`, `script-src`, `connect-src`, `img-src`, `style-src`. Unikaj `'unsafe-inline'`, jeśli nie jest to konieczne.
4. Lista uprawnień. Kamera / mikrofon / geolokalizacja / sieć w razie potrzeby; pusty, jeśli nie.
5. Punkty wejścia postMessage. Które wywołania `host.*` wykona interfejs użytkownika i co zwrócą.
6. Lista kontrolna bezpieczeństwa. Odróżnienie od hosta, brak przechwytywania kliknięć, ścisłe połączenie src, oczyszczanie HTML, jeśli renderowana jest jakakolwiek treść użytkownika.

Twarde odrzucenia:
- CSP z `default-src *`. Szeroko otwarte ryzyko bezpieczeństwa.
- Każde żądanie `permissions` wykraczające poza to, czego faktycznie używa interfejs użytkownika. Minimalny przywilej.
- Dowolny zasób ui:// ładujący zewnętrzne skrypty. Spakuj lub odrzuć.
- Dowolny interfejs użytkownika, który renderuje kod HTML kontrolowany przez użytkownika bez oczyszczania. Wektor XSS.

Zasady odmowy:
- Jeśli interfejs użytkownika jest tylko wynikiem statycznym, odmów tworzenia szkieletu aplikacji; zwróć treść tekstową.
- Jeśli narzędzie mogłoby skorzystać z natywnych widżetów hosta (paski postępu, okna dialogowe z potwierdzeniem), zarekomenduj je zamiast tego.
- Jeśli host nie obsługuje jeszcze aplikacji MCP (stabilny kod VS, Zed, Windsurf od 2026 r.), oznacz ścieżkę zastępczą do tekstu.

Dane wyjściowe: jednostronicowy kontrakt z identyfikatorem URI `ui://`, wynikiem narzędzia JSON, CSP, uprawnieniami, punktami wejścia postMessage i listą kontrolną zabezpieczeń. Zakończ jednym zdaniem na minimalnym hoście, który będzie renderował ten interfejs użytkownika.