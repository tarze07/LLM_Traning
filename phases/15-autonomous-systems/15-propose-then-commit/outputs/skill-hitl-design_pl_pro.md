---

name: hitl-design
description: Przeprowadź audyt proponowanego przepływu pracy Human-in-the-Loop (HITL) pod kątem zgodności ze wzorcem „zaproponuj, a następnie zatwierdź” (Propose-then-Commit) i wskaż braki w metadanych, idempotencji, weryfikacji lub procedurze Challenge-Response.
version: 1.0.0
phase: 15
lesson: 15
tags: [hitl, propose-then-commit, idempotency, langgraph, cloudflare, agent-framework, eu-ai-act]

---

Dla proponowanego przepływu pracy HITL przeprowadź audyt zgodności z referencyjnym wzorcem „zaproponuj, a następnie zatwierdź” (Propose-then-Commit). Wskaż obszary brakujące, niedostatecznie zdefiniowane lub niezgodne z wymogami regulacyjnymi.

Przygotuj:

1. **Metadane propozycji.** Zweryfikuj, czy każda zgłaszana propozycja zawiera: intencję (cel), pochodzenie danych (źródło inputu), wymagane uprawnienia, zakres szkód (blast radius – najgorszy scenariusz) oraz plan wycofania zmian. Brak któregokolwiek z tych pól dyskwalifikuje propozycję; komunikat typu „Agent chce wykonać X” jest niewystarczający.
2. **Idempotencja.** Określ strukturę (skład) klucza idempotencji. Klucz musi być generowany bezpośrednio na podstawie parametrów i treści samej propozycji, dzięki czemu ponowne uruchomienie kroku odwoła się do tego samego wpisu w bazie. Klucze zawierające aktualny czas systemowy (zegar systemowy) nie zapewniają idempotencji, a jedynie rejestrują znaczniki czasu.
3. **Trwałość zapisu (Persistence).** Wskaż bazę danych lub magazyn (PostgreSQL, Redis, Durable Objects, chmura z kontrolą integralności). Potwierdź, czy zapisane stany przetrwają restarty agenta, awarie serwera oraz wdrożenia nowych wersji. Kolejki w pamięci operacyjnej (in-memory queues) są niedozwolone.
4. **Interfejs autoryzacji.** Zwykłe zatwierdzanie jednym kliknięciem (rubber-stamping) nie spełnia kryteriów bezpieczeństwa. Wymagane jest wdrożenie interaktywnej listy kontrolnej Challenge-Response z wymogiem potwierdzenia zrozumienia celu operacji, oceny potencjalnych szkód oraz dostępności planu wycofania zmian. Lista pytań musi być dostosowana do konkretnego typu działania, a nie generyczna.
5. **Weryfikacja po wykonaniu (Post-action Verification).** Potwierdź, czy przepływ pracy ponownie odczytuje docelowy zasób po sfinalizowaniu operacji i generuje alerty w razie niepowodzenia. Informacja typu „narzędzie zwróciło kod statusu 200” nie stanowi poprawnej weryfikacji stanu systemu.

Kryteria odrzucenia (Hard Rejections):
- Systemy HITL, które nie zapisują trwale propozycji w bazie danych.
- Przepływy autoryzacji, w których recenzentem jest sam agent lub inny model językowy.
- Jakiekolwiek nieodwracalne operacje produkcyjne przeprowadzane bez procedury Challenge-Response.
- Klucze idempotencji bazujące na czasie systemowym (zegarze ściennym).
- Przepływy pracy pozbawione mechanizmu weryfikacji efektów ubocznych po wykonaniu akcji.

Zasady odmowy wykonania zadania (Denial Policies):
- Jeśli użytkownik opisuje interfejs zatwierdzania, ale nie potrafi wskazać trwałej bazy danych, która przechowuje jego stan, należy odmówić wykonania zadania i zażądać najpierw wdrożenia bazy.
- Jeśli użytkownik traktuje parametry `max_budget_usd` oraz proste okno zatwierdzenia jako wystarczający mechanizm HITL, należy odmówić. Budżety kontrolują wydatki, a nie poprawność i bezpieczeństwo logiczne.
- Jeśli wdrożenie dotyczy systemów wysokiego ryzyka na terenie UE i wciąż stosuje się uproszczone zatwierdzanie jednym kliknięciem (rubber-stamping), należy odmówić na podstawie wymagań Artykułu 14 AI Act.

Format danych wyjściowych:

Przedstaw raport z audytu wzorca Propose-then-Commit zawierający:
- **Tabelę pól propozycji** (intencja, pochodzenie danych, zakres szkód, plan wycofania, uprawnienia – wymagana obecność wszystkich pięciu)
- **Analizę idempotencji** (struktura klucza, wynik testu ponownego uruchomienia)
- **Charakterystykę bazy danych** (typ bazy, odporność na restarty [tak/nie])
- **Model autoryzacji** (jednokrotne kliknięcie vs lista kontrolna; w przypadku listy kontrolnej podaj dokładne pytania)
- **Mechanizm weryfikacji** (status [tak/nie], specyfikacja odczytywanych zasobów)
- **Rekomendacją wdrożeniową** (wdrożenie produkcyjne / staging / środowisko badawcze)
