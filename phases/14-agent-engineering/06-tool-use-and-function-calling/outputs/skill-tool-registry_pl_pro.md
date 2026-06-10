---

name: tool-registry
description: Zaprojektuj katalog i rejestr narzędzi o standardzie produkcyjnym z walidacją schematów JSON, równoległą dystrybucją zadań oraz systemem obserwowalności.
version: 1.0.0
phase: 14
lesson: 06
tags: [function-calling, tools, schema, validation, bfcl, parallel-tools]

---

Na podstawie domeny zadaniowej utwórz katalog narzędzi, z których agent będzie mógł niezawodnie korzystać we wszystkich wymiarach ocenianych w BFCL V4 (zadania agentowe, interakcje wieloturowe, zapytania na żywo, testy syntetyczne oraz obsługa halucynacji).

Przygotuj:

1. Definicje narzędzi: Dla każdego narzędzia określ: `name` (w formacie snake_case), `description` (wskazujący modelowi, kiedy należy, a kiedy NIE należy z niego korzystać), schemat wejściowy JSON Schema ze zdefiniowanymi typami właściwości, polami wymaganymi, wartościami enum (wyliczeniami) – jeśli dotyczy, limitami min/max dla liczb, czasem życia (timeout) oraz zasadami izolacji (uprawnienia do systemu plików, sieci, limit pamięci).
2. Weryfikacja jakości opisów: Przeanalizuj opis każdego narzędzia pod kątem pytania: „czy te informacje pozwalają modelowi precyzyjnie rozróżnić to narzędzie od innych?”. Jeśli opisy dwóch narzędzi pokrywają się i mogą wprowadzać w błąd, odrzuć je i zredaguj na nowo.
3. Plan równoległego uruchamiania: Dla każdego scenariusza określ, które wywołania narzędzi są niezależne (mogą być wykonywane równolegle), a które muszą być procesowane sekwencyjnie. Wygeneruj graf przepływu zadań.
4. Polityka walidacji: Określ zasady weryfikacji wartości enum, reguły konwersji typów (np. „akceptuj int przekazany jako string, odrzucaj float jako string”) oraz wymagalność pól. Błąd walidacji musi skutkować zwróceniem ustrukturyzowanego komunikatu o błędzie (obserwacji) bezpośrednio do modelu, zamiast wywoływać błąd krytyczny aplikacji.
5. Obserwowalność: Skonfiguruj generowanie spanów OpenTelemetry GenAI typu `tool_call` zawierających atrybuty `gen_ai.tool.name`, `gen_ai.tool.call.id`, `gen_ai.tool.call.arguments` oraz `gen_ai.tool.call.result` (jako referencję, a nie wartość wbudowaną, jeśli wymagają tego polityki prywatności danych).

Kryteria odrzucenia:
- Definiowanie ogólnych narzędzi typu „Shell” lub „uruchom polecenie”. Odmawiaj takich implementacji i rozbijaj je na wyspecjalizowane akcje (np. `git_status`, `fs_read`, `npm_test`).
- Brak wartości enum w definicji parametrów, które przyjmują zamknięty zbiór wartości. Walidacja wyliczeń to najprostszy sposób na uniknięcie błędów wyboru.
- Zastosowanie identycznego opisu dla dwóch różnych narzędzi. Uniemożliwia to modelowi dokonanie poprawnego wyboru.
- Opisy (`description`) ograniczające się do samej nazwy lub prostej czynności (np. „Dodaje dwie liczby”). Zawsze określaj kontekst, czyli KIEDY model powinien wybrać to narzędzie w porównaniu z innymi.
- Brak zdefiniowanego limitu czasu wykonania (timeout). Każde wywołanie narzędzia musi mieć określony górny limit czasu działania.

Zasady odmowy wykonania zadania:
- Jeśli katalog przekracza 30 narzędzi przypisanych to jednego agenta, odmów realizacji i zalecaj delegowanie zadań do subagentów (Lekcja 17).
- Jeśli którekolwiek z narzędzi wykonuje operacje o charakterze destrukcyjnym bez wdrożonej bramki autoryzacyjnej, odmów wykonania i odeślij do Lekcji 09 (uprawnienia, piaskownica).
- Jeśli zadanie dotyczy bezpośredniego sterowania komputerem (kliknięcia, pisanie na klawiaturze, zrzuty ekranu), odmów i odeślij do Lekcji 21 (wymaga to odmiennego projektowania narzędzi opartego na analizie wizualnej).

Oczekiwany rezultat: Katalog narzędzi w formacie JSON (gotowy do bezpośredniego użycia w SDK Anthropic, OpenAI lub Gemini), graf przepływu zadań, dokument opisujący politykę walidacji oraz krótki scenariusz testowy w stylu BFCL do weryfikacji poprawności działania rejestru.

Na końcu dodaj sekcję „Sugerowane lektury” odsyłającą do Lekcji 09 (Piaskownica), Lekcji 23 (Spany w OpenTelemetry GenAI) lub Lekcji 30 (Rozwój oparty na ewaluacji).
