---

name: memory-blocks
description: Zaimplementuj trójwarstwowy system pamięci w stylu Letta (bloki pamięci Core, Recall oraz Archival) z procesem konsolidacji danych w tle (sleep-time compute) realizowanym poza główną ścieżką wykonania.
version: 1.0.0
phase: 14
lesson: 08
tags: [memory, letta, blocks, sleep-time, consolidation]

---

Dla wybranego środowiska uruchomieniowego, modelu podstawowego oraz (potencjalnie mocniejszego) modelu przeznaczonego do pracy w tle zaimplementuj trójwarstwowy system pamięci ze zdefiniowanymi typami bloków oraz asynchroniczną konsolidacją danych.

Przygotuj:

1. Klasa `Block`: Reprezentująca pojedynczy blok pamięci z atrybutami: `label`, `value`, `limit`, `description`, `version` oraz `history`. Każda modyfikacja inkrementuje numer wersji i zapisuje poprzednią wartość w historii. Udostępnij funkcję `near_limit(threshold=0.8)` sprawdzającą zapełnienie.
2. Magazyn bloków `BlockStore`: Zdefiniuj co najmniej trzy domyślne bloki: `human` (dane o użytkowniku), `persona` (tożsamość agenta) oraz `task` (bieżący cel). Zapewnij możliwość tworzenia bloków zdefiniowanych przez użytkownika.
3. Magazyn `Recall`: Historia rozmów z podziałem na strony i sesje. Logi muszą być automatycznie zapisywane w każdej turze. Najstarsze wpisy (ogon konwersacji) są usuwane po przekroczeniu limitu rozmiaru, ale muszą pozostać dostępne dla modułów wyszukiwania.
4. Magazyn `Archival`: Wspierający co najmniej dwa silniki bazy danych (bazę wektorową oraz magazyn klucz-wartość KV). Operacja zapisu must zwracać identyfikator wpisu. W przypadku wykrycia sprzecznych faktów, wpisy należy oznaczać jako unieważnione (nieaktualne), zamiast fizycznie je usuwać.
5. Agent główny `PrimaryAgent`: Odpowiadający za interakcję z użytkownikiem i zapisywanie danych wejściowych w formie surowej. Niedozwolone jest uruchamianie procesów streszczania lub porządkowania na głównej ścieżce wykonania.
6. Agent czasu bezczynności `SleepTimeAgent`: Działający asynchronicznie poza głównym przepływem – streszcza bloki przekraczające limit rozmiaru, unieważnia sprzeczne informacje w archiwum oraz zapisuje wyciągnięte wnioski (`learned_context`) we wspólnych segmentach pamięci.

Kryteria odrzucenia:
- Wykonywanie jakichkolwiek operacji porządkowania pamięci synchronicznie w trakcie tury interakcji z użytkownikiem (wyjątkiem jest bezpośrednie odpytanie bazy). Procesy kompaktowania, trwałego zapisu oraz unieważniania faktów muszą być delegowane do agenta działającego w tle.
- Fizyczne usuwanie wpisów w przypadku wystąpienia sprzeczności danych. Wpisy należy oznaczać jako nieaktualne (unieważnione), aby zachować pełną ścieżkę audytu.
- Zapisywanie danych bezpośrednio do bloków Persona lub Safety bez procedury weryfikacyjnej. Bloki te decydują o globalnym zachowaniu agenta, a niekontrolowane zapisy mogą maskować błędy w jego logice.

Zasady odmowy wykonania zadania:
- Jeśli wybrane środowisko uruchomieniowe nie potrafi zapewnić trwałości bloków pamięci pomiędzy sesjami, odmów wdrożenia systemu reklamowanego jako posiadający „pamięć”. Należy wówczas skorygować opis i wymagania systemu.
- Jeśli proces działający w tle (SleepTimeAgent) nie generuje czytelnych logów z wykonanych operacji, odmów wdrożenia. Brak logowania uniemożliwia debugowanie procesów konsolidacji pamięci.
- Jeśli użytkownik żąda rezygnacji z unieważniania wpisów i bezkrytycznego nadpisywania danych najnowszymi informacjami, odmów wdrożenia w domenach, w których historia zmian jest krytyczna (np. finanse, medycyna, prawo, zgodność z normami prawnymi).

Oczekiwany rezultat: Osobny plik dla każdego komponentu oraz plik `README.md` określający nazwy domyślnych bloków, harmonogram zadań w tle (sleep-time) oraz reguły rozwiązywania konfliktów danych. Na końcu umieść sekcję „Sugerowane lektury” odsyłającą do Lekcji 09 (gdy wymagane jest wnioskowanie oparte na grafach wiedzy) lub Lekcji 23 (gdy zachodzi potrzeba instrumentacji operacji na pamięci za pomocą OpenTelemetry).
