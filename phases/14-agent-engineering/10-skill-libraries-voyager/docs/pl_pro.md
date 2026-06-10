# Biblioteki umiejętności i uczenie się przez całe życie (Voyager)

> Voyager (Wang i in., TMLR 2024) traktuje kod wykonywalny jako umiejętność. Umiejętności są nazywane, wyszukiwane, komponowane i udoskonalane na podstawie informacji zwrotnych ze środowiska. Jest to referencyjna architektura dla koncepcji umiejętności w Claude Agent SDK oraz ogólnych bibliotek umiejętności agentów w 2026 roku.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 07 (MemGPT), Faza 14 · 08 (Bloki Letta)
**Czas:** ~75 minut

## Cele nauczania

- Wymień trzy komponenty systemu Voyager — automatyczny program nauczania (curriculum), bibliotekę umiejętności oraz iteracyjne udoskonalanie podpowiedzi (prompts) — i opisz rolę każdego z nich.
- Wyjaśnij, dlaczego Voyager definiuje przestrzeń akcji jako kod wykonywalny, a nie jako pojedyncze polecenia.
- Zaimplementuj w Pythonie (przy użyciu biblioteki standardowej) bibliotekę umiejętności z mechanizmami rejestracji, pobierania, kompozycji i udoskonalania opartego na błędach wykonania.
- Dopasuj wzorzec Voyagera do umiejętności (skills) w Claude Agent SDK 2026 oraz ekosystemu narzędzi agentowych.

## Problem

Agenci, którzy w każdej sesji budują swoje zdolności od zera, popełniają trzy zasadnicze błędy:

1. **Marnowanie tokenów.** Każde zadanie wymaga powtarzania tego samego procesu wnioskowania.
2. **Utrata postępu.** Poprawki i wiedza zdobyte w sesji A nie przenoszą się do sesji B.
3. **Brak wsparcia dla złożonej kompozycji.** Długofalowe zadania wymagają hierarchii umiejętności; jednorazowe podpowiedzi (prompts) nie są w stanie ich efektywnie wyrazić.

Rozwiązanie Voyagera: traktuj każdą wielokrotnie używaną umiejętność jako nazwany fragment kodu przechowywany w bibliotece. Może on być wyszukiwany na podstawie podobieństwa semantycznego, łączony z innymi umiejętnościami i udoskonalany na podstawie informacji zwrotnych o błędach wykonania.

## Koncepcja

### Trzy elementy składowe

Projekt Voyager (arXiv:2305.16291) buduje agenta wokół trzech głównych modułów:

1. **Automatyczny program nauczania (Curriculum).** Moduł proponujący zadania (proposer) kieruje się ciekawością. Wybiera on kolejne cele w oparciu o aktualny zestaw umiejętności agenta oraz stan środowiska, promując eksplorację oddolną (bottom-up).
2. **Biblioteka umiejętności (Skill Library).** Każda umiejętność reprezentowana jest przez kod wykonywalny. Nowe umiejętności są dodawane do bazy po pomyślnym wykonaniu zadania. Umiejętności są wyszukiwane na podstawie podobieństwa zapytania do ich opisu.
3. **Iteracyjne udoskonalanie (Iterative Prompting).** W przypadku niepowodzenia agent analizuje błędy wykonania, informacje zwrotne ze środowiska oraz wyniki własnej weryfikacji (self-verification), a następnie modyfikuje i ulepsza kod umiejętności.

Wyniki uzyskane w środowisku Minecraft (Wang i in., 2024): 3,3 raza więcej odkrytych unikalnych przedmiotów, 8,5 raza szybsze tworzenie narzędzi kamiennych, 6,4 raza szybsze tworzenie narzędzi żelaznych oraz 2,3 raza dłuższe dystanse przemierzania mapy w porównaniu do klasycznych rozwiązań. Choć wartości te są specyficzne dla gry, sam wzorzec jest w pełni uniwersalny.

### Przestrzeń akcji jako kod

Zamiast wydawać pojedyncze polecenia, Voyager generuje funkcje w języku JavaScript. Przykładowa umiejętność wygląda następująco:

```javascript
async function craftIronPickaxe(bot) {
  await mineIron(bot, 3);
  await mineStick(bot, 2);
  await placeCraftingTable(bot);
  await craft(bot, 'iron_pickaxe');
}
```

Taka funkcja składa się z podumiejętności (sub-skills). Jest zapisywana wraz z opisem i powiązanym osadzeniem (embeddingiem), a następnie ładowana jako wykonywalny program, a nie tylko tekstowy prompt.

Ten sam wzorzec stosuje Claude Agent SDK w 2026 roku: umiejętność to nazwany, możliwy do pobrania fragment kodu wraz z instrukcjami, które agent importuje w razie potrzeby.

### Pobieranie umiejętności (Retrieval)

Kiedy pojawia się nowe zadanie, np. „stwórz diamentowy kilof”, agent:

1. Tworzy osadzenie (embedding) dla opisu zadania.
2. Odpytuje bibliotekę o najbardziej podobne i przydatne umiejętności.
3. Pobiera np. `craftIronPickaxe`, `mineDiamond`, `placeCraftingTable`.
4. Tworzy nową umiejętność, łącząc pobrane komponenty z nową logiką.

Przypomina to wzorzec używania zasobów MCP (faza 13) oraz mechanizm umiejętności w SDK – pobieranie kodu/wiedzy odbywa się dynamicznie w kontekście realizowanego zadania.

### Iteracyjne udoskonalanie (Iterative Refinement)

Pętla sprzężenia zwrotnego (feedback loop) w Voyagerze:

1. Agent generuje lub modyfikuje kod umiejętności.
2. Umiejętność jest uruchamiana w środowisku.
3. Środowisko zwraca jeden z trzech sygnałów: sukces (`success`), błąd (`error` ze śladem stosu) lub niepowodzenie autoweryfikacji (`self-verification failure`).
4. Agent poprawia kod umiejętności, wykorzystując te informacje jako kontekst.
5. Proces powtarza się do momentu osiągnięcia sukcesu lub wyczerpania limitu prób.

Jest to koncepcja samodoskonalenia (Lekcja 05) zastosowana do generowania kodu i połączona z weryfikacją w rzeczywistym środowisku. Działa analogicznie do wzorca CRITIC (Lekcja 05), gdzie rolę krytyka pełni zewnętrzne środowisko uruchomieniowe.

### Program nauczania i eksploracja

Moduł programu nauczania proponuje zadania o stopniu trudności nieco przewyższającym aktualne możliwości agenta (np. „zbuduj schronienie w pobliżu jeziora” na podstawie posiadanych zasobów i historii działań). Zapewnia to optymalny punkt eksploracji (Zone of Proximal Development).

W systemach produkcyjnych przekłada się to na analizę braków kompetencyjnych: „biorąc pod uwagę obecną bibliotekę umiejętności i wymagania domeny, jakich funkcji nam brakuje?”. Zespoły zazwyczaj realizują ten etap poprzez okresowy przegląd wymagań i rozbudowę biblioteki.

### Potencjalne problemy i wady wzorca

- **Zaśmiecenie biblioteki umiejętności (bloat).** Ta sama lub bardzo podobna umiejętność może zostać dodana wielokrotnie z nieznacznie różniącymi się opisami. Należy wdrożyć mechanizm deduplikacji przy zapisie, tak aby wyszukiwanie zwracało tylko jedną unikalną, kanoniczną pozycję.
- **Dryf umiejętności złożonych.** Umiejętność nadrzędna (parent skill) zależy od kodu umiejętności podrzędnej (child skill). Jeśli kod podrzędny zostanie zmodyfikowany, może to uszkodzić rodzica. Konieczne jest wersjonowanie umiejętności (np. rodzic zablokowany na wersji 1 nie powinien automatycznie przejmować wersji 3).
- **Spadek jakości wyszukiwania.** Pobieranie wektorowe na podstawie samych opisów staje się mniej dokładne, gdy biblioteka przekracza kilkaset pozycji. Należy uzupełnić wyszukiwanie o filtry tagów i sztywne reguły (np. „tylko umiejętności z kategorii `tooling`”).

## Zbuduj to

Plik `code/main.py` implementuje prostą bibliotekę umiejętności w bibliotece standardowej Pythona:

- `Skill` – reprezentuje umiejętność: zawiera nazwę, opis, kod (jako ciąg tekstowy), wersję, tagi oraz zależności.
- `SkillLibrary` – umożliwia rejestrację, wyszukiwanie (na podstawie nakładania się tokenów), budowanie (sortowanie topologiczne zależności) oraz udoskonalanie (aktualizację wersji).
- Agent skryptowy, który rejestruje trzy podstawowe umiejętności, tworzy czwartą, napotyka błąd wykonania i poprawia ją w kolejnej wersji.

Uruchomienie:

```
python3 code/main.py
```

Wygenerowane logi pokazują proces zapisu w bibliotece, pobieranie, składanie (kompozycję), nieudane wykonanie oraz udoskonalenie do wersji 2 – pełną pętlę Voyagera.

## Użyj tego

- **Claude Agent SDK Skills** (Anthropic) – standard na rok 2026: każda umiejętność zawiera opis, kod i instrukcje, i jest ładowana na żądanie podczas sesji agenta.
- **skillkit** (npm: skillkit) – współdzielone zarządzanie umiejętnościami dla wielu agentów kodujących AI.
- **Własne biblioteki umiejętności** – dostosowane do konkretnej domeny (np. umiejętności SQL dla agentów danych, Terraform dla agentów infrastruktury). Wzorzec Voyagera świetnie się tu skaluje.
- **Narzędzia (tools) w OpenAI Agents SDK** – na niskim poziomie każde narzędzie funkcjonuje jako uproszczona umiejętność.

## Wyślij to

Plik `outputs/skill-skill-library.md` tworzy szkielet biblioteki umiejętności zgodnej z architekturą Voyager, zawierającej rejestrację, wyszukiwanie, wersjonowanie i mechanizmy udoskonalania kodu dla dowolnego środowiska uruchomieniowego.

## Ćwiczenia

1. Dodaj detektor cykli zależności w metodzie `compose()`. Co powinno się stać, gdy umiejętność A zależy od B, a B zależy od A? Czy powinien to być błąd, czy tylko ostrzeżenie?
2. Zaimplementuj przypinanie wersji dla poszczególnych umiejętności. Kiedy umiejętność nadrzędna deklaruje zależność `crafting@1`, późniejsze wdrożenie wersji `crafting@2` nie powinno automatycznie aktualizować zależności rodzica.
3. Zastąp wyszukiwanie oparte na nakładaniu się tokenów osadzeniami sentence-transformers (lub własną implementacją BM25 w stdlib). Zmierz wskaźnik recall@5 w uproszczonej bibliotece zawierającej 50 umiejętności.
4. Zaimplementuj agenta „programu nauczania”: na podstawie analizy obecnej biblioteki i specyfikacji domeny, powinien on co tydzień proponować 5 nowych, brakujących umiejętności do zaimplementowania.
5. Przeczytaj dokumentację umiejętności w pakiecie SDK Claude Agent od Anthropic. Przepisz przykładową bibliotekę tak, aby była zgodna ze schematem Claude SDK. Jakie zmiany wpływają na wykrywalność i rejestrację narzędzi?

## Kluczowe terminy

| Termin | Co mówią ludzie | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Umiejętność | „Możliwość wielokrotnego użytku” | Nazwany fragment kodu wraz z opisem, wyszukiwany na podstawie podobieństwa |
| Biblioteka umiejętności | „Magazyn instrukcji agenta” | Przechowywany w sposób trwały zbiór umiejętności, który można przeszukiwać i składać |
| Program nauczania | „Moduł proponujący zadania” | Generator celów oddolnych bazujący na analizie brakujących kompetencji agenta |
| Kompozycja | „DAG umiejętności” | Umiejętności odwołujące się do innych umiejętności; uporządkowane topologicznie przed wykonaniem |
| Iteracyjne udoskonalanie | „Pętla samokorygująca” | Informacje zwrotne ze środowiska, błędy oraz samoweryfikacja przekazywane do procesu tworzenia kolejnej wersji kodu |
| Przestrzeń akcji jako kod | „Działania programowe” | Generowanie funkcji zamiast pojedynczych poleceń w celu realizacji długoterminowych działań |
| Deduplikacja przy zapisie | „Konsolidacja umiejętności” | Sprowadzanie bardzo podobnych opisów do jednej kanonicznej wersji umiejętności w celu uniknięcia nadmiarowości |

## Dalsze czytanie

- [Wang i in., Voyager (arXiv:2305.16291)](https://arxiv.org/abs/2305.16291) — oryginalna publikacja dotycząca uczenia się z biblioteką umiejętności
- [Omówienie pakietu SDK Claude Agent](https://platform.claude.com/docs/en/agent-sdk/overview) — wykorzystanie umiejętności w praktycznych wdrożeniach (rok 2026)
- [Anthropic, Budowanie agentów z pakietem Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) — praktyczne zastosowanie umiejętności i subagentów
- [Madaan i in., Self-Refine (arXiv:2303.17651)](https://arxiv.org/abs/2303.17651) — podstawy teoretyczne pętli udoskonalania leżącej u podstaw Voyagera
