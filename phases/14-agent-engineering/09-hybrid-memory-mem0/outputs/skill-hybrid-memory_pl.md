---

name: hybrid-memory
description: Wygeneruj trzy składowy system pamięci w kształcie Mem0 (wektor + KV + wykres) ze wskaźnikiem fuzji, taksonomią zakresu i unieważnieniem czasowym.
version: 1.0.0
phase: 14
lesson: 09
tags: [memory, mem0, vector, graph, kv, fusion, scope]

---

Biorąc pod uwagę docelowy czas wykonania, backend wektorowy (Qdrant, pgvector, Chroma, sqlite-vec), backend KV (Postgres, Redis, dict) i backend graficzny (Neo4j, krawędzie w pamięci), tworzą połączony system pamięci.

Wyprodukuj:

1. Trzy klasy sklepów za fasadą `add(text, user_id, session_id, scope, importance, tags)`. Podczas zapisu ekstraktor rozkłada `text` na rekordy, trójki KV i trójki wykresów. Żaden sklep nie jest opcjonalny.
2. Punktator fuzyjny `score = w_rel * relevance + w_imp * importance + w_rec * recency`. Udostępnij wszystkie trzy wagi jako konfigurację. Dostrój według produktu, a nie połączenia.
3. Taksonomia zakresu: `user`, `session`, `agent`. Wyszukiwanie MUSI uwzględniać zakres. Zapytanie użytkownika nie może nigdy spowodować wycieku danych innego użytkownika.
4. Unieważnienie czasowe. Sprzeczności oznaczają, że stare krawędzie/zapisy są nieważne; nigdy nie usuwaj. Ujawnij `search(query, as_of=timestamp)` dla zapytań historycznych.
5. Interfejs ekstraktora. Wartość domyślna może być oparta na LLM; zezwalaj na deterministyczne zastępcze wyrażenie regularne dla testów. Zakryj krawędzie wykresu zgodnie z `add()`, aby zapobiec eksplozji.

Twarde odrzucenia:

- Pamięć jednomagazynowa opisana jako „w kształcie Mem0”. Produkty obsługujące tylko wektory, tylko KV i tylko wykresy są w porządku, ale nie są pamięcią hybrydową. Nie błędnie ich nazywaj.
- Wyszukiwanie międzyzakresowe bez wag poszczególnych zakresów lub jawnego filtra `scope=`. Wyciek zakresu to incydent dotyczący zgodności i prywatności.
- Usunięcie w przypadku sprzeczności. Unieważnienie i znacznik czasu. Usunięcie ukrywa błędy i przerywa audyty.

Zasady odmowy:

- Jeśli użytkownik poprosi o „brak ważenia”, odmów. Płaski ranking trafności ponad milion rekordów to awaria pobierania, która może się zdarzyć.
- Jeśli backend wykresu nie ma detektora konfliktów, odmów nazywania powstałego systemu „w kształcie Mem0”. Zmień nazwę.
- Jeżeli produkt wymaga informacji umożliwiających identyfikację (medyczną, prawną, kadrową), odmów wysyłki za pomocą ekstraktora, który nie został skontrolowany przez właściciela produktu.

Dane wyjściowe: jeden plik na sklep plus `memory.py` (fasada), `config.py` (wagi), `README.md` wyjaśniające ciężary zgrzewania, zasady zakresu, umowę na ekstraktor i semantykę unieważnienia. Zakończ słowami „Co dalej czytać”, wskazując Lekcję 10, jeśli agent musi nauczyć się nowych umiejętności, Lekcję 23, jeśli w operacjach pamięci wymagane są zakresy OTel, lub Lekcję 27 dotyczącą obsługi niezaufanych danych wejściowych podczas pobierania.