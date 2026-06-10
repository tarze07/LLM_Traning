---

name: hybrid-memory
description: Wygeneruj trójskładnikowy system pamięci w stylu Mem0 (wektor + KV + graf) z fuzją ocen, taksonomią zakresów i unieważnianiem czasowym.
version: 1.0.0
phase: 14
lesson: 09
tags: [memory, mem0, vector, graph, kv, fusion, scope]

---

W oparciu o wskazane środowisko uruchomieniowe stwórz zintegrowany system pamięci łączący backend wektorowy (Qdrant, pgvector, Chroma, sqlite-vec), backend KV (Postgres, Redis, słownik) oraz backend grafowy (Neo4j, krawędzie w pamięci).

Wygeneruj:

1. Trzy klasy magazynów ukryte za fasadą `add(text, user_id, session_id, scope, importance, tags)`. Podczas zapisu ekstraktor rozkłada `text` na rekordy wektorowe, trójki KV i trójki grafowe. Żaden z magazynów nie jest opcjonalny.
2. Mechanizm fuzji ocen (scoringowy): `score = w_rel * relevance + w_imp * importance + w_rec * recency`. Udostępnij wszystkie trzy wagi w konfiguracji. Powinny być one dostrajane globalnie dla całego rozwiązania, a nie na poziomie pojedynczych wywołań.
3. Taksonomia zakresów (scopes): `user`, `session`, `agent`. Wyszukiwanie MUST bezwzględnie respektować te zakresy. Zapytanie jednego użytkownika nigdy nie może doprowadzić do wycieku danych innego użytkownika.
4. Unieważnianie czasowe (temporal invalidation). W przypadku sprzeczności stare krawędzie/zapisy powinny być oznaczane jako nieważne; nie wolno ich usuwać. Udostępnij metodę `search(query, as_of=timestamp)` na potrzeby zapytań historycznych.
5. Interfejs ekstraktora. Domyślna implementacja może korzystać z LLM; na potrzeby testów dopuść deterministyczny ekstraktor oparty na wyrażeniach regularnych (regex). Ograniczaj liczbę dodawanych krawędzi grafu w wywołaniu `add()`, aby zapobiec ich eksplozji.

Kryteria odrzucenia (Hard rejects):

- Rozwiązania jednomagazynowe opisywane jako „w stylu Mem0”. Systemy oparte wyłącznie na wektorach, KV lub grafach są dopuszczalne w innych scenariuszach, ale nie stanowią pamięci hybrydowej. Nie należy ich tak nazywać.
- Wyszukiwanie międzyzakresowe bez określonych wag dla poszczególnych zakresów lub bez jawnego filtra `scope=`. Naruszenie izolacji zakresów stanowi poważny incydent bezpieczeństwa i prywatności.
- Usuwanie rekordów w przypadku wykrycia sprzeczności. Zamiast tego należy stosować unieważnienie i znacznik czasu. Usuwanie danych utrudnia audyt i ukrywa błędy.

Zasady odmowy (Guardrails):

- Jeśli użytkownik poprosi o rezygnację z ważenia ocen (brak wag), odmów. Płaski ranking trafności przy bazie liczącej ponad milion rekordów nieuchronnie prowadzi do degradacji jakości wyszukiwania.
- Jeśli backend grafowy nie posiada detektora konfliktów, nie pozwalaj na nazywanie systemu „w stylu Mem0”. Zmień nazwę.
- Jeśli rozwiązanie przetwarza wrażliwe dane osobowe lub specyficzne dane branżowe (medyczne, prawne, kadrowe), zablokuj wdrożenie produkcyjne ekstraktora, dopóki nie zostanie on zweryfikowany i zaakceptowany przez właściciela biznesowego produktu (Product Ownera).

Wygenerowana struktura: po jednym pliku dla każdego magazynu oraz `memory.py` (fasada), `config.py` (konfiguracja wag) i `README.md` wyjaśniające wagi fuzji, reguły zakresów, kontrakt ekstraktora oraz semantykę unieważniania danych. Zakończ sekcją „Co czytać dalej”, odsyłając do Lekcji 10 (jeśli agent musi uczyć się nowych umiejętności), Lekcji 23 (jeśli operacje na pamięci wymagają zakresów OTel) lub Lekcji 27 (w temacie obsługi niezaufanych danych wejściowych przy pobieraniu).
