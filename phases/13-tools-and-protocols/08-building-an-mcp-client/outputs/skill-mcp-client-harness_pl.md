---

name: mcp-client-harness
description: Mając deklaratywną listę serwerów MCP (nazwa, polecenie, argumenty), utwórz szkielet klienta wieloserwerowego z uzgadnianiem, łączeniem przestrzeni nazw i routingiem.
version: 1.0.0
phase: 13
lesson: 08
tags: [mcp, client, multi-server, routing, namespace]

---

Biorąc pod uwagę konfigurację serwerów MCP do uruchomienia, utwórz wiązkę klienta, która odradza każdy z nich, uzgadnia każdy z nich, łączy ich listy narzędzi w jedną przestrzeń nazw i kieruje każde wywołanie do serwera będącego właścicielem.

Wyprodukuj:

1. Parser konfiguracji serwera. Mapa `name -> {command, args, env}`. Sprawdź, czy w ścieżce znajdują się polecenia.
2. Plan odrodzenia. Użyj subprocess.Popen z potokami stdin/stdout/stderr, `bufsize=1`, tryb tekstowy. Jeden wątek czytnika w tle na serwer.
3. Potok uzgadniania. Dla każdej sesji: wyślij `initialize`, poczekaj na odpowiedź, utrzymuj możliwości, wyślij `notifications/initialized`.
4. Scalanie przestrzeni nazw. Wybierz politykę kolizyjną: `prefix-on-collision` (domyślna), `reject-on-collision` lub `silent-overwrite` (zabroniona). Wydrukuj połączoną listę narzędzi przy uruchomieniu.
5. Funkcja routingu. `client.call(canonical_name, arguments)` wyszukuje sesję będącą właścicielem i zapisuje wiadomość `tools/call`. Poczekaj na odpowiedź o pasującym identyfikatorze za pośrednictwem przyszłości w tabeli oczekujących żądań.

Twarde odrzucenia:
- Dowolna wiązka, która nie powoduje odrodzenia każdego serwera w jego własnym procesie. Multipleksowanie w procesie pokonuje model izolacji.
- Dowolna uprząż z domyślną polityką kolizyjną `silent-overwrite`. Ryzyko bezpieczeństwa.
- Dowolna wiązka blokująca główny wątek na stdout odczytuje. Powiadomienia przestaną działać.

Zasady odmowy:
- Jeśli polecenie serwera jest niezaufane (nie znajduje się na przypiętej liście dozwolonych), odmów spawnowania i przejścia do fazy 13 · 15 w celu kontroli bezpieczeństwa.
- Jeśli użytkownik bez powodu konfiguruje więcej niż 10 serwerów, ostrzeż i zasugeruj bramę (faza 13 · 17).
- Jeśli zostaniesz poproszony o obsługę OAuth w tym miejscu, odmów i przejdź do fazy 13 · 16.

Dane wyjściowe: kompletny plik Pythona z wiązką klienta (~150 linii) z sesją, logiką scalania, routingiem i główną pętlą, która ćwiczy każdy skonfigurowany serwer. Zakończ jednowierszowym podsumowaniem, podając nazwę polityki kolizyjnej i liczbę scalonych narzędzi.