---

name: rollback-rehearsal
description: Zaprojektuj scenariusz testowy dla procedury wycofania zmian (Rollback Rehearsal) w proponowanym przepływie pracy agenta oraz przeprowadź audyt bazy danych punktów kontrolnych pod kątem trwałości ścieżki audytu.
version: 1.0.0
phase: 15
lesson: 16
tags: [checkpointing, rollback, idempotency, eu-ai-act-article-14, durable-execution]

---

Dla proponowanego autonomicznego przepływu pracy o długim horyzoncie zaprojektuj scenariusz testowy wycofania zmian (Rollback Rehearsal). Test ten ma potwierdzić poprawność działania całego łańcucha zabezpieczeń: idempotencja + weryfikacja warunków wstępnych + weryfikacja po wykonaniu + procedura wycofania zmian. Następnie przeprowadź audyt bazy danych punktów kontrolnych pod kątem zgodności z wymogami regulacyjnymi (audytowalności).

Przygotuj:

1. **Scenariusz testowy (Rehearsal Script).** Zdefiniuj test typu end-to-end, który: (a) uruchamia przepływ pracy, (b) wstrzymuje go w połowie fazy autoryzacji (commit), (c) wznawia proces, (d) weryfikuje, czy akcja wykonała się dokładnie raz, (e) symuluje błąd weryfikacji po akcji, (f) potwierdza poprawne uruchomienie procedury wycofania zmian (rollback) i przywrócenie spójności danych. Żadne wdrożenie produkcyjne nie powinno mieć miejsca bez pomyślnego zaliczenia tego testu.
2. **Audyt idempotencji.** Potwierdź, czy klucz idempotencji jest generowany na podstawie parametrów samej propozycji (patrz Lekcja 15), a logika zapisu statusów korzysta z jawnych stanów (`pending` -> `executing` -> `committed`/`failed`). Upewnij się, że blokada kluczem idempotencji następuje *przed* wywołaniem efektu ubocznego, a status `committed` jest zapisywany *dopiero po* pomyślnej weryfikacji końcowej.
3. **Weryfikacja warunków wstępnych (Pre-conditions).** Wskaż wszystkie warunki wstępne, które system musi powtórnie sprawdzić bezpośrednio przed wykonaniem fizycznej operacji (faza commit). Najczęstszą przyczyną awarii na produkcji są błędy synchronizacji (race conditions) typu TOCTOU (Time-of-Check to Time-of-Use); warunki wstępne muszą być oceniane bezpośrednio przed wykonaniem akcji, a nie w momencie zgłaszania propozycji.
4. **Rejestr weryfikacji (Verification Inventory).** Dla każdej operacji wywołującej skutki uboczne określ konkretne zapytanie odczytujące, które potwierdza wprowadzenie zmian. Informacja typu „odebrano kod statusu HTTP 200” jest niewystarczająca.
5. **Rejestr procedur wycofania zmian (Rollback Inventory).** Dla każdego działania zdefiniuj i sklasyfikuj procedurę wycofania (wycofanie bezpośrednie, transakcja kompensacyjna, obsługa ręczna). Brak możliwości wycofania zmian (operacje nieodwracalne) must być jawnie określony w metadanych propozycji (patrz Lekcja 15).

Kryteria odrzucenia (Hard Rejections):
- Przepływy pracy bez przetestowanych i przećwiczonych procedur wycofania zmian.
- Bazy danych dla punktów kontrolnych, które tracą dane podczas restartów lub wdrożeń nowej wersji kodu.
- Przepływy autoryzacji, w których rejestracja statusu w locie (in-flight) następuje po wykonaniu akcji, a nie przed nią.
- Uznawanie akcji za zweryfikowaną wyłącznie na podstawie kodu zwrotnego wywołania API/narzędzia.
- Weryfikacja warunków wstępnych wyłącznie na etapie generowania propozycji, zamiast bezpośrednio przed wykonaniem operacji (commit).

Zasady odmowy wykonania zadania (Denial Policies):
- Jeśli użytkownik nie przeprowadził testu wycofania zmian (rollback rehearsal) przynajmniej raz w środowisku stagingowym, należy odmówić wdrożenia produkcyjnego.
- Jeśli użytkownik nie potrafi przedstawić schematu bazy danych dla punktów kontrolnych, należy odmówić i zażądać specyfikacji schematu. Organy regulacyjne wymagają możliwości audytu i przeszukiwania zapisanego stanu procesów.
- Jeśli punkty kontrolne są przechowywane wyłącznie w pamięci operacyjnej (brak trwałego zapisu stanu), należy odmówić wykonania zadania.

Format danych wyjściowych:

Przedstaw plan testów (Rehearsal Plan) zawierający:
- **Scenariusz testowy** (kroki testu wraz z asercjami)
- **Tabelę idempotencji** (struktura klucza, kolejność rejestracji statusów)
- **Tabelę warunków wstępnych** (sprawdzany warunek, czas oceny, konsekwencje niepowodzenia)
- **Tabelę weryfikacji po akcji** (działanie, metoda odczytu, kryteria weryfikacji)
- **Tabelę wycofania zmian** (akcja, typ procedury, stan docelowy)
- **Charakterystykę bazy danych** (typ magazynu, odporność na restarty [tak/nie], możliwość przeszukiwania stanu [tak/nie])
- **Rekomendacją wdrożeniową** (wdrożenie produkcyjne / staging / środowisko badawcze)
