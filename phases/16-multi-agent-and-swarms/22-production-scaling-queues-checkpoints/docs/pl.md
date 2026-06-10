# Skalowanie produkcji — kolejki, punkty kontrolne, trwałość

> Skalowanie systemów wieloagentowych do tysięcy jednoczesnych uruchomień wymaga **trwałego wykonania**. Środowisko wykonawcze LangGraph zapisuje punkt kontrolny po każdym superkroku wprowadzonym przez `thread_id` (domyślnie Postgres); pracownik ulega awarii, zwalnia dzierżawę i inny pracownik wznawia pracę. Agenci mogą spać w nieskończoność, czekając na interwencję człowieka. **MegaAgent** (arXiv:2408.09955) uruchomił kolejkę producent-konsument dla każdego agenta z trzema stanami (bezczynność/przetwarzanie/odpowiedź) i koordynacją dwuwarstwową (czat wewnątrzgrupowy + czat administracyjny między grupami). **Fiber/async** przewyższa liczbę wątków na zadanie w przypadku przesyłania strumieniowego LLM: wątki pozostają bezczynne przez 99% czasu w oczekiwaniu na tokeny, włókna wspólnie poddają się we/wy. Kontrapunkt: „Scaling Agentic Software” Ashpreeta Bedi opowiada się za **FastAPI + Postgres + niczym więcej**, dopóki obciążenie nie udowodni inaczej — proste architektury idą dalej, niż oczekiwano. Ta lekcja tworzy trwały dziennik punktów kontrolnych, kolejkę roboczą dla poszczególnych agentów ze zmianami stanów, demonstrację asynchronizacji vs wątek i wprowadza pragmatyczną regułę „rozpocznij od prostego”.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib, `asyncio`, `sqlite3`)
**Wymagania wstępne:** Faza 16 · 09 (Równoległe sieci roju), Faza 16 · 13 (pamięć współdzielona)
**Czas:** ~75 minut

## Problem

Prototypowy system wieloagentowy działa na jednym laptopie z trzema agentami w pętli zdarzeń w pamięci. Przechodzisz do produkcji:

- Agenci czasami działają godzinami (długie badania, oczekiwanie przez człowieka).
- Awaria procesów roboczych. Ponowne uruchomienie powoduje utratę stanu.
- Obciążenie szczytowe wynosi średnio 10x; potrzebujesz skalowania poziomego.
- Użytkownicy płacą za uruchomienie agenta; potrzebujesz semantyki dokładnie jednorazowej do ładowania.

Pętla zdarzeń w pamięci nie wykonuje żadnego z nich. Pod spodem potrzebujesz trwałej warstwy wykonawczej. Opcje kanoniczne na rok 2026 to:

1. Silnik przepływu pracy z punktami kontrolnymi (Temporal, Runtime LangGraph).
2. Kolejka komunikatów z magazynem stanu (Postgres + SQS/RabbitMQ).
3. Ramy modelu aktora (producent-konsument MegaAgent na agenta).
4. Ręcznie zwijane FastAPI + Postgres (argument Bediego).

W tej lekcji budujemy miniaturę każdego z nich.

## Koncepcja

### Trwałe wykonanie, wzór

Silnik o trwałym wykonaniu utrzymuje pełny stan programu po każdym „kroku” (superkroku, w języku LangGraph). W przypadku awarii:

```
worker crashes mid-step
  -> lease timeout
  -> another worker picks up the thread_id
  -> resumes from last checkpoint
  -> no duplicate side effects
```

Wymagania aby to działało:

- **Stan możliwy do serializacji.** Cały stan agenta musi być trwały. Zamknięcia funkcji z aktywnymi połączeniami z bazą danych nie przetrwają.
- **Wznowienie deterministyczne.** Biorąc pod uwagę ten sam stan i te same dane wejściowe, agent wykonuje te same działania (lub odwołuje się do zewnętrznej deterministycznej wyroczni w przypadku wywołań LLM).
- **Idempotentne skutki uboczne.** Wywołania zewnętrzne (wywołania narzędzi, płatności) muszą być idempotentne lub używać klucza deduplikacji.

LangGraph zapisuje punkt kontrolny po każdym superkroku; Temporal zapisuje po każdej czynności; Restate korzysta z dzienników pochodzących ze zdarzeń. Wszystkie trzy implementują ten sam wzór.

### Środowisko wykonawcze LangGraph

Każdy agent ma `thread_id`; stan jest dyktatem wpisanym na maszynie; każdy superkrok zapisuje wiersz do tabeli punktów kontrolnych. Po wznowieniu środowisko wykonawcze odtwarza od ostatniego punktu kontrolnego, a nie od zera. Agenci mogą `interrupt()` czekać na wkład człowieka; środowisko wykonawcze będzie się utrzymywać i zwalnia pracownika. Po nadejściu danych wejściowych każdy pracownik może wznowić pracę.

To jest referencyjny projekt produkcyjny w kwietniu 2026 r.

### Kolejka MegaAgent dla poszczególnych agentów

arXiv:2408.09955 opisuje eksperyment skali: tysiące równoczesnych agentów w jednym klastrze. Architektura:

```
agent i:
  state ∈ {Idle, Processing, Response}
  in_queue   <- messages addressed to agent i
  out_queue  -> replies + side effects

coordinators:
  intra-group chat  (agents in the same group)
  inter-group admin chat  (high-level routing)
```

Koordynacja dwuwarstwowa umożliwia gęstą konwersację wewnątrz grupy, podczas gdy rozmowy międzygrupowe pozostają rzadkie — jest to wzorzec używany do utrzymywania liniowych kosztów tysięcy agentów.

### Asynchronizacja vs wątek na zadanie

Wywołania LLM są powiązane z operacjami we/wy. Wątek oczekujący na następny token jest w 99% przypadków bezczynny. Każdy wątek kosztuje ~1MB RAM; przy 10 000 jednoczesnych połączeń, czyli 10 GB na same stosy.

Włókna (Python `asyncio`, Go goroutines, Rust `tokio`) wspólnie wykonują operacje we/wy. Te same 10 000 połączeń mieści się wygodnie w procesie. W skali agenta LLM asynchronizacja nie jest optymalizacją — jest to architektura.

Wyjątek: przetwarzanie końcowe związane z procesorem (osadzanie, sztuczki tokenizatora) nadal wymaga wątków lub procesów. Oddziel warstwę we/wy od warstwy procesora.

### Kontrapunkt Bediego

„Scaling Agentic Software” (Ashpreet Bedi, 2026) dowodzi, że większość zespołów przesadza z inżynierią, zanim zmierzy obciążenie. Pragmatyczne ustawienie domyślne:

- FastAPI + Postgres.
- Każde uruchomienie agenta to rząd; stan aktualizowany lokalnie z optymistyczną współbieżnością.
- Zadania w tle za pośrednictwem `pg_notify` lub prostego procesu roboczego Celery.
- Zasady ponawiania prób w kodzie aplikacji.

W przypadku obciążeń poniżej ~100 równoczesnych uruchomień agentów w ramach możliwych do zarządzania zadań często jest to wszystko, czego potrzebujesz. Uaktualnij, gdy zmierzysz jego niepowodzenie.

Zasada: wdrażaj frameworki o trwałym wykonaniu, gdy napotkasz konkretny problem, którego proste architektury nie są w stanie rozwiązać. Przedwczesna adopcja marnuje czas na ceremonie, które się nie opłacają.

### Semantyka „dokładnie raz”.

W przypadku płatnych agentów potrzebujesz „dokładnie raz skutecznego” (dostawa co najmniej raz + idempotentny konsument). Inżynieria porusza się:

- **Klucz deduplikacji na przebieg.** Dołącz go do każdego wywołania efektu ubocznego.
- **Wzorzec skrzynki nadawczej.** Efekty uboczne najpierw zapisują się w tabeli, a następnie wykonują je oddzielny proces. Oba kroki idempotentne.
- **Transakcje kompensujące.** Jeśli efekt uboczny się powiedzie, ale zapis śledzenia nie powiedzie się, zaplanuj kompensację.

Są to wzorce inżynierii baz danych, a nie specyficzne dla LLM. Podatek LLM polega tylko na tym, że połączenia LLM są powolne; cała reszta to standardowe systemy rozproszone.

### Wdrożenie Rainbow

Wieloagentowy system badawczy firmy Anthropic wykorzystuje „wdrożenia tęczowe”: wiele wersji środowiska wykonawczego agentów działa jednocześnie, więc długo działający agenci nie muszą być zabijani przy każdym wdrażaniu kodu. Nowe wersje Canary na fragmencie ruchu; wycofaj stare wersje, gdy ich agenci zakończą pracę.

Jest to standard w przypadku długotrwałych systemów stanowych; adaptacja na rok 2026 polega na tym, że agenci mogą żyć godzinami, dlatego cykle wdrażania muszą uwzględniać.

### Lista kontrolna produkcji kanonicznej

- Stan trwały (punkty kontrolne, migawki lub skrzynka nadawcza + dziennik do odtwarzania).
- Idempotentne skutki uboczne.
- Warstwa asynchronicznego we/wy dla wywołań LLM.
- Co najmniej jednorazowa dostawa z dedupem.
- Wdrożenie Rainbow/Canary dla obciążeń stanowych.
- Obserwowalność: ślady poszczególnych agentów, audyt superetapowy, licznik ponownych prób.

## Zbuduj to

`code/main.py` implementuje:

- `CheckpointStore` — dziennik punktu kontrolnego oparty na SQLite z kluczami identyfikatora wątku. Każdy super-krok dołącza wiersz.
- `run_with_checkpoint(agent, thread_id)` — symuluje awarię w trakcie działania; drugi pracownik wznawia pracę od ostatniego punktu kontrolnego.
- `AgentQueue` — maszyna stanu bezczynności/przetwarzania/odpowiedzi dla poszczególnych agentów z małą kolejką roboczą.
- `demo_async_vs_threads()` — uruchamia 500 symulowanych jednocześnie „wywołań LLM” poprzez asyncio i wątki; podaje zegar ścienny i pamięć szczytową (w przybliżeniu).

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik: wznowienie punktu kontrolnego powiodło się po symulowanej awarii; wersja asynchroniczna obsługuje 500 jednoczesnych wywołań w czasie <1 s; wersja wątku zajmuje kilka sekund i zużywa o rząd wielkości więcej pamięci na współbieżną jednostkę.

## Użyj tego

`outputs/skill-scaling-advisor.md` doradza w wyborze trwałego wykonania: FastAPI + Postgres, środowisko wykonawcze LangGraph, Temporal lub niestandardowe. Kalibrowane według obciążenia, potrzeb w zakresie przechowywania stanu i częstotliwości wdrażania.

## Wyślij to

Hartowanie produkcyjne kanoniczne:

- **Zacznij od prostego (reguła Bediego).** FastAPI + Postgres, dopóki nie zmierzysz niepowodzenia.
- **Przed optymalizacją zmierz wszystko.** Histogram opóźnienia dla poszczególnych przebiegów, czas trwania poszczególnych kroków, liczba ponownych prób, kategoryzacja błędów.
- **Wzór skrzynki nadawczej dotyczący skutków ubocznych.** Zwłaszcza płatności i zewnętrzne wywołania API.
- **Wdrażanie Rainbow.** Nigdy nie zabijaj agentów w locie podczas wdrażania.
- **Zastosuj silniki o trwałym wykonaniu (Temporal / LangGraph / Restate), gdy** napotkasz określone problemy: godzinne oczekiwanie w pętli, koordynacja między regionami, złożone zasady ponownych prób/kompensacji.
- **Asynchronizacja dla warstwy we/wy.** Wątki tylko do przetwarzania końcowego powiązanego z procesorem.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że wznowienie punktu kontrolnego działa; zmierzyć różnicę współbieżności asynchronicznej i wątku.
2. Zaimplementuj tabelę **skrzynki nadawczej**: każde wywołanie narzędzia najpierw zapisuje dane w skrzynce nadawczej, a następnie wykonywana jest oddzielna procedura/zadanie. Sprawdź idempotencję, dwukrotnie uruchamiając wywołanie narzędzia.
3. Symuluj **wdrożenie tęczy**: dwie równoczesne wersje środowiska wykonawczego; skieruj do każdego połowę nowych identyfikatorów wątków; potwierdź, że wątki w starej wersji nie są przerywane.
4. Przeczytaj dokument wykonawczy LangGraph (link poniżej). Zidentyfikuj, które funkcje środowiska wykonawczego będą najdłużej replikowane w ręcznie tworzonej wersji FastAPI + Postgres. Czy to powód do adopcji, czy można odłożyć?
5. Przeczytaj MegaAgent (arXiv:2408.09955) Sekcja 3. Koordynacja dwuwarstwowa (czat administracyjny wewnątrz grupy + między grupami) jest wyraźna. Naszkicuj sposób odwzorowania tego na kolejkę komunikatów z dwiema rodzinami kolejek.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Trwałe wykonanie | „Utrzymaj stan programu” | Silnik zapisuje stan po każdym superetapie; odzyskiwanie po awarii jest deterministyczne. |
| Super-krok | „Granica transakcyjna” | Jednostka pracy pomiędzy punktami kontrolnymi. Termin LangGraph. |
| identyfikator_wątku | „Identyfikator uruchomienia agenta” | Klucz wiążący punkty kontrolne i wznawiający logikę. |
| Idempotencja | „Można bezpiecznie spróbować ponownie” | Powtórzenie efektu ubocznego daje taki sam rezultat jak jedna próba. |
| Wzór skrzynki nadawczej | „Oddziel skutki uboczne” | Zapisz intencję w tabeli; wykonuje oddzielny executor i zaznacza wykonanie. |
| Dostawa przynajmniej raz | „Możliwe duplikaty” | Semantyka kolejki komunikatów; Klucz dedup sprawia, że ​​konsument jest skuteczny jednorazowo. |
| Tęcza wdrażana | „Nakładające się wersje” | Wiele wersji środowiska wykonawczego współbieżnych podczas długotrwałych obciążeń. |
| Światłowód asynchroniczny | „Spółdzielnia plonująca” | Współbieżność trybu użytkownika; tanie w porównaniu do wątków dla obciążeń związanych z we/wy. |
| Punkt kontrolny | „Migawka stanu” | Stan serializowany na granicy superkroku; klucz do wznowienia. |

## Dalsze czytanie

- [LangChain — Środowisko wykonawcze za głębokimi agentami produkcyjnymi](https://www.langchain.com/conceptual-guides/runtime-behind-production-deep-agents) — Projektowanie środowiska wykonawczego LangGraph
- [MegaAgent](https://arxiv.org/abs/2408.09955) — kolejka producenta-konsumenta na agenta; dwupoziomowa koordynacja z udziałem tysięcy równoczesnych agentów
- [Matrix](https://arxiv.org/abs/2511.21686) — zdecentralizowany framework z kolejkami komunikatów jako podłożem koordynacyjnym
- [Temporal docs](https://docs.temporal.io/) — referencyjny silnik przepływu pracy zapewniający trwałe wykonanie
- [Anthropic — wieloagentowy system badawczy](https://www.anthropic.com/engineering/multi-agent-research-system) — lekcje produkcyjne, w tym wdrażanie tęczy