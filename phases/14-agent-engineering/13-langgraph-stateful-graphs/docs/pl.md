# LangGraph: Wykresy stanowe i trwałe wykonanie

> LangGraph to punkt odniesienia na rok 2026 w zakresie orkiestracji stanowej niskiego poziomu. Agent jest maszyną stanu; węzły są funkcjami; krawędzie są przejściami; stan jest niezmienny i sprawdzany po każdym kroku. Kontynuuj pracę po awarii dokładnie tam, gdzie została przerwana.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (pętla agenta), faza 14 · 12 (wzorce przepływu pracy)
**Czas:** ~75 minut

## Cele nauczania

- Opisać podstawowy model LangGrapha: maszynę stanów z niezmiennym stanem, węzły funkcji, krawędzie warunkowe i punkty kontrolne po kroku.
- Wymień cztery możliwości, na które zwracają uwagę dokumenty: trwałe wykonanie, przesyłanie strumieniowe, działanie człowieka w pętli, wszechstronna pamięć.
- Wyjaśnij trzy topologie orkiestracji obsługiwane przez LangGraph: nadzorca, peer-to-peer (rój), hierarchiczny (zagnieżdżone podgrafy).
- Zaimplementuj wykres stanu stdlib z niezmiennym stanem, krawędziami warunkowymi i cyklem punktu kontrolnego/wznowienia.

## Problem

Agenci i przepływy pracy mają wspólny problem: jeśli 40-etapowy przebieg zakończy się niepowodzeniem w kroku 38, chcesz wznowić działanie od kroku 38, a nie zaczynać od nowa. Modele stanu drugiej klasy pozostawiają operatorom ponawianie prób włamywania się do biblioteki, która zakłada nowe uruchomienia.

Odpowiedź projektowa LangGrapha: stan jest obiektem pierwszej klasy, mutacje są jawne, a punkty kontrolne utrzymują się po każdym węźle. Wznów to połączenie `load_state(session_id)`.

## Koncepcja

### Wykres

Wykres jest zdefiniowany przez:

- **Typ stanu.** Wpisany słownik (lub model Pydantic), który każdy węzeł odczytuje i mutuje.
- **Węzły.** Funkcje czyste `(state) -> state_update`. Aktualizacje są łączone w stan po powrocie.
- **Krawędzie.** Przejścia warunkowe lub bezpośrednie pomiędzy węzłami.
- **Wejście i wyjście.** `START` i `END` węzły wartownicze wyznaczają granicę.

Przykład: agent z węzłami `classify`, `refund`, `bug`, `sales`, `done` — przepływ pracy routingu w postaci wykresu.

### Trwałe wykonanie

Po powrocie każdego węzła środowisko wykonawcze serializuje stan i zapisuje go do punktu kontrolnego (SQLite, Postgres, Redis, niestandardowe). W przypadku niepowodzenia w kroku N środowisko wykonawcze może `resume(session_id)` i wznowić działanie od kroku N+1 z dokładnym stanem.

Dokumenty LangGraph wyraźnie podkreślają użytkowników produkcyjnych tam, gdzie ma to znaczenie: Klarna, Uber, J.P. Morgan. Twierdzenie nie jest kształtem wykresu; chodzi o to, że kształt wykresu i punkty kontrolne sprawiają, że odzyskiwanie jest tanie.

### Transmisja strumieniowa

Każdy węzeł może dawać częściowy wynik. Wykres przesyła strumieniowo zdarzenia różnicowe dla poszczególnych węzłów do obiektu wywołującego, dzięki czemu interfejsy użytkownika są aktualizowane w miarę uruchamiania wykresu.

### Człowiek w pętli

Sprawdź i zmodyfikuj stan pomiędzy węzłami. Implementacje: przerwa przed węzłem krytycznym, stan powierzchni do człowieka, akceptacja modyfikacji, wznowienie. Wskaźnik kontrolny ułatwia to, ponieważ stan jest już serializowany.

### Pamięć

Krótkoterminowe (w ramach serii — stan historii konwersacji) i długoterminowe (w seriach — trwałe za pośrednictwem punktu kontrolnego oraz oddzielnego magazynu długoterminowego). LangGraph integruje się z zewnętrznymi systemami pamięci (Mem0, niestandardowe) za pomocą narzędzi.

### Trzy topologie

1. **Przełożony.** Centralny router LLM wysyła wysyłki do wyspecjalizowanych subagentów. `create_supervisor()` w `langgraph-supervisor` (chociaż zespół LangChain w 2026 r. zaleca robienie tego za pomocą bezpośrednich wywołań narzędzi, aby uzyskać większą kontrolę nad kontekstem).
2. **Rój / peer-to-peer.** Agenci przekazują informacje bezpośrednio za pośrednictwem współdzielonej powierzchni narzędziowej. Brak centralnego routera.
3. **Hierarchiczny.** Przełożeni zarządzający podległymi przełożonymi, zaimplementowani jako podgrafy zagnieżdżone.

### Gdzie ten wzorzec jest błędny

- **Punkty kontrolne są zbyt małe.** Tylko konwersacja w punktach kontrolnych powoduje, że stan narzędzia i zapisy w pamięci są nie do odzyskania. Pełny stan musi być serializowany.
- **Węzły niedeterministyczne.** Wznów zakłada, że ​​dane wejściowe węzła powodują tę samą aktualizację stanu. Należy przechwycić losowe nasiona, zegar ścienny i zewnętrzne interfejsy API.
- **Nadużywanie krawędzi warunkowych.** Graf z każdą krawędzią warunkową jest maszyną stanów, której nie da się uzasadnić. Preferuj łańcuchy liniowe z okazjonalnymi rozgałęzieniami.

## Zbuduj to

`code/main.py` implementuje wykres stanowy stdlib:

- `State` — dyktando wpisane z `messages`, `step`, `route`, `output`, `human_approval`.
- `Node` — wywoływalne pobieranie stanu i zwracanie dyktatu aktualizacji.
- `StateGraph` — węzły + krawędzie + krawędzie warunkowe + uruchomienie + wznowienie.
- `SQLiteCheckpointer` (fałszywy w pamięci) — serializuje stan po każdym węźle; `load(session_id)` przywraca.
- Wykres demo: klasyfikacja -> oddział (zwrot pieniędzy / błąd / sprzedaż) -> ludzka brama -> wyślij.

Uruchom to:

```
python3 code/main.py
```

Ślad pokazuje, że pierwszy przebieg zakończył się niepowodzeniem przy ludzkiej bramie, trwałość, a następnie wznowiono wytwarzanie końcowego wyniku.

## Użyj tego

- **LangGraph** — referencja, gotowa do produkcji. Użyj `create_react_agent`, `create_supervisor` lub utwórz własny wykres.
- **AutoGen v0.4** (Lekcja 14) — alternatywny model aktora dla scenariuszy o dużej współbieżności.
- **Claude Agent SDK** (Lekcja 17) — zarządzana uprząż z wbudowanym magazynem sesji.
- **Niestandardowy** — gdy potrzebujesz dokładnej kontroli nad kształtem stanu lub zapleczem punktu kontrolnego.

## Wyślij to

`outputs/skill-state-graph.md` generuje wykres stanu w kształcie LangGraph w dowolnym docelowym środowisku wykonawczym z podłączonymi punktami kontrolnymi i wznowieniem.

## Ćwiczenia

1. Dodaj krawędź warunkową od `classify` do `end`, gdy pewność klasyfikacji jest poniżej progu. Wznów bieg po ręcznym ustawieniu przez człowieka `route`.
2. Zamień podróbkę przypominającą SQLite na prawdziwy punkt kontrolny SQLite. Zmierz narzut serializacji na krok.
3. Zaimplementuj równoległe krawędzie: dwa węzły działają jednocześnie, połącz za pomocą niestandardowego reduktora. Co tu kupuje stan niezmienny?
4. Przeczytaj `langgraph-supervisor` odnośnik. Przenieś zabawkę do `create_supervisor`. Porównaj kształty śladów.
5. Dodaj przesyłanie strumieniowe: każdy węzeł podczas działania generuje stan częściowy. Wydrukuj delty, gdy tylko się pojawią.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Wykres stanu | „Agent jako maszyna stanu” | Wpisany stan + węzły + krawędzie + reduktory |
| Punkt kontrolny | „Zaplecze trwałości” | Serializuje stan po każdym węźle; umożliwia wznowienie |
| Reduktor | „Połączenie państw” | Funkcja łącząca aktualny stan z aktualizacją węzła |
| Krawędź warunkowa | „Oddział” | Krawędź wybrana przez funkcję stanu |
| Podgraf | „Zagnieżdżony wykres” | Wykres używany jako węzeł wewnątrz innego wykresu |
| Trwałe wykonanie | „Wznów po porażce” | Uruchom ponownie od ostatniego pomyślnego węzła z dokładnym stanem |
| Nadzorca | „Router LLM” | Centralny dyspozytor dla wyspecjalizowanych subagentów |
| Rój | „Agenci P2P” | Agenci przekazują informacje za pośrednictwem wspólnych narzędzi; brak centralnego routera |

## Dalsze czytanie

- [Omówienie LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) — dokumentacja referencyjna
- [odniesienie do langgraph-supervisor](https://reference.langchain.com/python/langgraph/supervisor/) — API wzorca nadzorcy
- [AutoGen v0.4, Microsoft Research](https://www.microsoft.com/en-us/research/articles/autogen-v0-4-reimagining-the-foundation-of-agentic-ai-for-scale-extensibility-and-robustness/) — alternatywa dla modelu aktora
- [Omówienie zestawu SDK agenta Claude](https://platform.claude.com/docs/en/agent-sdk/overview) — sklep sesji i subagenci