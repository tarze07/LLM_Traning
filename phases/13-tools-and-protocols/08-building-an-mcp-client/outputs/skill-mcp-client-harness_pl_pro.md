---

name: mcp-client-harness
description: Na podstawie deklaratywnej listy serwerów MCP (nazwy, polecenia, parametry) wygeneruj kod klienta wieloserwerowego obsługującego inicjalizację, scalanie przestrzeni nazw i routing.
version: 1.0.0
phase: 13
lesson: 08
tags: [mcp, client, multi-server, routing, namespace]

---

Na podstawie dostarczonej konfiguracji serwerów MCP do uruchomienia utwórz strukturę klienta, która uruchamia każdy proces, przeprowadza inicjalizację (handshake), scala listy narzędzi w jedną wspólną przestrzeń nazw oraz realizuje routing wywołań do właściwych serwerów.

Wygeneruj:

1. Parser konfiguracji serwerów. Słownik mapujący `name -> {command, args, env}`. Dodaj weryfikację dostępności plików wykonywalnych w zmiennej PATH.
2. Zarządzanie procesami. Wykorzystaj `subprocess.Popen` ze strumieniami stdin/stdout/stderr, parametrem `bufsize=1` oraz włączonym trybem tekstowym. Uruchom po jednym wątku czytnika w tle dla każdego serwera.
3. Przepływ inicjalizacji. Dla każdej sesji: wyślij żądanie `initialize`, oczekuj na odpowiedź, zapisz zadeklarowane możliwości i wyślij powiadomienie `notifications/initialized`.
4. Scalanie przestrzeni nazw. Zdefiniuj strategię rozwiązywania konfliktów nazw: `prefix-on-collision` (domyślna), `reject-on-collision` lub `silent-overwrite` (strategia zabroniona). Wypisz scaloną listę narzędzi przy starcie aplikacji.
5. Funkcja routingu. Metoda `client.call(canonical_name, arguments)` wyszukuje powiązaną sesję i wysyła zapytanie `tools/call`. Oczekiwanie na odpowiedź z pasującym identyfikatorem `id` zrealizuj przy użyciu obiektów Future/Promise zapisanych w tabeli oczekujących żądań.

Kryteria odrzucenia (Twarde reguły):
- Uruchomienie wielu serwerów w ramach tego samego procesu. Brak uruchomienia każdego serwera w osobnym procesie potomnym łamie zasadę izolacji środowisk.
- Użycie strategii `silent-overwrite` (ciche nadpisywanie) jako domyślnej polityki rozwiązywania konfliktów nazw (ryzyko bezpieczeństwa).
- Zablokowanie głównego wątku aplikacji na odczycie strumienia stdout serwerów (blokuje to asynchroniczne powiadomienia).

Zasady odmowy usługi:
- Jeśli komenda uruchomieniowa serwera nie znajduje się na liście zaufanych poleceń (lista dozwolonych / whitelist), odmów uruchomienia procesu i skieruj użytkownika do fazy 13 · 15 w celu przeprowadzenia audytu bezpieczeństwa.
- Jeśli konfiguracja obejmuje ponad 10 serwerów bez uzasadnienia biznesowego, wyświetl ostrzeżenie i zasugeruj zastosowanie bramy routującej (gateway, faza 13 · 17).
- Jeśli zostaniesz poproszony o implementację protokołu OAuth bezpośrednio w kodzie klienta, odmów i skieruj użytkownika do fazy 13 · 16.

Format wyjściowy: Kompletny kod w języku Python (~150 linii) implementujący strukturę klienta z definicjami sesji, logiką scalania, routingiem oraz pętlą główną testującą każdy z serwerów. Na końcu dodaj jednowierszowe podsumowanie zawierające informację o wybranej strategii rozwiązywania konfliktów oraz liczbie scalonych narzędzi.
