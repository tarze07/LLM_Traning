---

name: durable-execution-review
description: Przejrzyj proponowane długoterminowe wdrożenie agenta pod kątem prawidłowego kształtu trwałego wykonania (działania, determinizm, zaplecze punktu kontrolnego, stan wprowadzania danych przez człowieka, HITL po wznowieniu).
version: 1.0.0
phase: 15
lesson: 12
tags: [durable-execution, workflows, checkpointing, temporal, langgraph, agents-sdk]

---

Biorąc pod uwagę proponowane długotrwałe wdrożenie agenta (Temporal + OpenAI Agents SDK, LangGraph ze wskaźnikiem kontrolnym PostgreSQL, Microsoft Agent Framework, Claude Code Routines, Cloudflare Durable Objects lub wewnętrzny odpowiednik), przeprowadź audyt projektu pod kątem wzorca trwałego wykonania.

Wyprodukuj:

1. **Inwentarz aktywności.** Lista wszystkich aktywności (wywołanie LLM, wywołanie narzędzia, żądanie HTTP, zapis pliku). Dla każdego z nich potwierdź, że jest opakowany jako działanie z zasadami ponawiania prób, limitem czasu i kluczem idempotencji. Surowe wywołania LLM poza zakresem działalności są luką w niezawodności.
2. **Determinizm przepływu pracy.** Zidentyfikuj każdy niedeterministyczny odczyt w kodzie przepływu pracy (zegar ścienny, losowy, stan zewnętrzny). Każde musi być zarejestrowane jako działanie uboczne, więc powtórka zwraca tę samą wartość. Ukryty niedeterminizm jest najczęstszą przyczyną dryfowania powtórek.
3. **Backend punktu kontrolnego.** Nazwij backend (PostgreSQL, SQLite, Redis, Durable Objects). Potwierdź, że przetrwa wdrożenie. SQLite jest przeznaczony tylko dla deweloperów. Redis wymaga konfiguracji AOF lub migawki. Obiekty trwałe Cloudflare są przezroczyste, ale wymagają unikalnej, kluczowej dyscypliny.
4. **Stan wywołany przez człowieka.** Potwierdź, że przerwy dla HITL są pierwszorzędnym stanem przepływu pracy, a nie pętlą odpytywania. Przepływ pracy powinien blokować sygnał zewnętrzny (kolejka zatwierdzenia, element webhook, element podstawowy `interrupt()`), który zostanie wznowiony dokładnie po nadejściu zatwierdzenia.
5. **Zasady dotyczące HITL-on-resume.** W przypadku każdego wznowienia po awarii należy określić, czy wymagane jest nowe HITL przed wykonaniem następnej czynności. Bez tego trwałe wykonanie plus zatwierdzenie wydane przed awarią może ponownie uruchomić zatwierdzoną akcję, gdy kontekst się zmieni. Krytyczne dla długich horyzontów.

Twarde odrzucenia:
- Użycie pakietu SDK agenta, gdy wywołania LLM nie są opakowane jako działania.
- Backendy punktu kontrolnego, które nie przetrwają wdrożenia.
- Przepływy pracy, które osadzają zegar ścienny lub losowe, bez zawijania aktywności.
- Dane wejściowe człowieka modelowane jako pętla odpytywania, a nie sygnał.
- Przebiegi długoterminowe (powyżej jednej godziny) bez polityki HITL-on-resume.
- Działa bez wyłącznika budżetowego (lekcja 13), a dodatkowo zapewnia trwałość.

Zasady odmowy:
- Jeśli użytkownik proponuje trwały przepływ pracy bez wyraźnej idempotencji w przypadku działań ubocznych, odmów i najpierw zażądaj kluczy idempotencji. W przeciwnym razie ponowne próby zostaną wykonane dwukrotnie.
- Jeśli użytkownik nie może pokazać testu powtórki (przebieg pracy, awaria w połowie, powtórka, zapewnienie braku podwójnych skutków ubocznych), odmów i zażądaj tego testu przed rozpoczęciem produkcji.
- Jeśli użytkownik zaproponuje 24-godzinny bieg bez nadzoru bez punktu kontrolnego HITL, odmów. Degradacja trwająca 35 minut (notatki z lekcji 12) sprawia, że ​​jest to problem z niezawodnością, nawet jeśli trwałość jest prawidłowa.

Format wyjściowy:

Zwróć notatkę z przeglądu projektu zawierającą:
- **Tabela aktywności** (aktywność, zasady ponawiania prób, limit czasu, klucz idempotencji)
- **Audyt determinizmu** (odczyty niedeterministyczne i sposób obsługi każdego z nich)
- **Zaplecze punktu kontrolnego** (nazwa, przetrwanie-wdrożenie tak/nie, status testu powtórki)
- **Kształt stanu HITL** (stan pierwszej klasy / odpytywanie / brak)
- **Zasady HITL dotyczące wznowienia** (wyraźne, z uzasadnieniem)
- **Gotowość** (tylko produkcja / etapowanie / badania)