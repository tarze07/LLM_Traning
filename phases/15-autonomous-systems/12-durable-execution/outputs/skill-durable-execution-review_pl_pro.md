---

name: durable-execution-review
description: Przeprowadź weryfikację proponowanego wdrożenia długo działającego agenta pod kątem poprawności architektury trwałego wykonania (podział na aktywności, determinizm, baza danych punktów kontrolnych, obsługa decyzji człowieka, autoryzacja HITL przy wznawianiu sesji).
version: 1.0.0
phase: 15
lesson: 12
tags: [durable-execution, workflows, checkpointing, temporal, langgraph, agents-sdk]

---

Na podstawie proponowanej architektury długo działającego agenta (np. Temporal + OpenAI Agents SDK, LangGraph z bazą punktów kontrolnych PostgreSQL, Microsoft Agent Framework, Claude Code Routines, Cloudflare Durable Objects lub własne rozwiązanie) przeprowadź audyt projektu pod kątem wzorca trwałego wykonania (durable execution).

Przygotuj:

1. **Rejestr aktywności (Activities Inventory).** Sporządź listę wszystkich aktywności (wywołania LLM, uruchomienia narzędzi, żądania HTTP, zapisy plików). Dla każdego kroku potwierdź, czy został opakowany w aktywność posiadającą zdefiniowane zasady ponawiania (retry policy), limity czasowe (timeouts) oraz klucze idempotencji. Bezpośrednie wywoływanie LLM poza strukturą aktywności stanowi poważną lukę w stabilności systemu.
2. **Determinizm przepływu pracy (Workflow Determinism).** Zidentyfikuj wszelkie niedeterministyczne operacje w kodzie przepływu pracy (pobieranie czasu systemowego, liczby losowe, odczyty stanu zewnętrznego). Każda taka operacja must być zarejestrowana jako aktywność (skutek uboczny), aby podczas odtwarzania stanu (replay) zwracała dokładnie tę samą wartość. Ukryty niedeterminizm jest najczęstszą przyczyną rozbieżności stanów podczas odtwarzania sesji.
3. **Baza danych punktów kontrolnych (Checkpoint Backend).** Określ typ zastosowanej bazy danych (PostgreSQL, SQLite, Redis, Durable Objects). Potwierdź, czy przetrwa ona restarty środowiska i wdrożenia nowych wersji. SQLite nadaje się wyłącznie do celów deweloperskich. Redis wymaga włączenia mechanizmów AOF lub tworzenia migawek. Cloudflare Durable Objects są wygodne, lecz wymagają konsekwentnego zarządzania kluczami sesji.
4. **Status decyzji człowieka (Human-in-the-Loop State).** Potwierdź, czy wstrzymywanie pracy w celu uzyskania decyzji człowieka (HITL) jest natywnym stanem przepływu pracy, a nie pętlą odpytywania (polling loop). Przepływ pracy powinien blokować się, oczekując na zewnętrzny sygnał (kolejkę zatwierdzeń, wywołanie webhooka, natywną metodę `interrupt()`), i wznawiać działanie dokładnie po nadejściu autoryzacji.
5. **Autoryzacja przy wznawianiu sesji (HITL-on-resume).** Określ, czy w przypadku restartu procesu po awarii wymagane jest ponowne zatwierdzenie przez człowieka przed wykonaniem kolejnego kroku. Bez tego mechanizmu trwałe wykonanie w połączeniu z autoryzacją udzieloną przed awarią mogłoby uruchomić niebezpieczne działania w zmienionym kontekście środowiska. Jest to kluczowe przy długim horyzoncie zadań.

Kryteria odrzucenia (Hard Rejections):
- Stosowanie SDK agentów bez opakowywania wywołań LLM w dedykowane aktywności.
- Używanie baz danych dla punktów kontrolnych, które nie są odporne na restarty i wdrożenia nowej wersji kodu.
- Wykorzystywanie czasu systemowego lub generatorów liczb losowych bezpośrednio w przepływie pracy bez opakowania ich w aktywność.
- Projektowanie oczekiwania na decyzję człowieka jako pętli odpytywania (polling), zamiast architektury opartej na sygnałach/zdarzeniach.
- Uruchamianie długotrwałych zadań (ponad 1 godzina) bez wdrożonej polityki autoryzacji przy wznawianiu sesji (HITL-on-resume).
- Prowadzenie operacji bez mechanizmów ograniczania budżetu (budżetów bezpieczeństwa, patrz Lekcja 13) przy włączonym trwałym wykonaniu.

Zasady odmowy wykonania zadania (Denial Policies):
- Jeśli proponowany trwały przepływ pracy nie zapewnia idempotencji dla kroków wywołujących efekty uboczne, należy odmówić wykonania zadania i zażądać zdefiniowania kluczy idempotencji. W przeciwnym razie ponowienie próby może spowodować wielokrotne wykonanie tej samej operacji.
- Jeśli użytkownik nie potrafi przedstawić testu odtwarzania stanu (przebieg procesu -> wywołanie awarii w połowie -> wznowienie/replay -> weryfikacja braku powtórnych efektów ubocznych), należy odmówić i zażądać przeprowadzenia takiego testu przed wdrożeniem produkcyjnym.
- Jeśli użytkownik planuje uruchomić 24-godzinną, w pełni nienadzorowaną sesję bez punktów kontrolnych wymagających zatwierdzenia przez człowieka (HITL), należy odmówić. Zjawisko 35-minutowej degradacji (patrz Lekcja 12) powoduje drastyczny spadek niezawodności w tak długich procesach, nawet przy poprawnej architekturze trwałego wykonania.

Format danych wyjściowych:

Przedstaw raport z audytu projektu zawierający:
- **Tabelę aktywności** (aktywność, polityka ponawiania, limity czasowe, klucz idempotencji)
- **Audyt determinizmu** (wykryte operacje niedeterministyczne oraz sposób ich obsługi)
- **Baza danych punktów kontrolnych** (nazwa, odporność na restarty i wdrożenia [tak/nie], status testu odtwarzania stanu)
- **Model obsługi decyzji człowieka (HITL)** (stan natywny / odpytywanie / brak)
- **Polityka autoryzacji przy wznowieniu (HITL-on-resume)** (precyzyjne reguły wraz z uzasadnieniem)
- **Rekomendację wdrożeniową** (wdrożenie produkcyjne / staging / środowisko badawcze)
