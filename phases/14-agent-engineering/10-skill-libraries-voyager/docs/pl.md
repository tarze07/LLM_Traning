# Biblioteki umiejętności i uczenie się przez całe życie (Voyager)

> Voyager (Wang i in., TMLR 2024) traktuje kod wykonywalny jako umiejętność. Umiejętności są nazywane, możliwe do odzyskania, komponowania i udoskonalania na podstawie informacji zwrotnych z otoczenia. To jest architektura referencyjna dla umiejętności Claude Agent SDK, zestawu umiejętności i wzorca biblioteki umiejętności 2026.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 07 (MemGPT), Faza 14 · 08 (Bloki Letta)
**Czas:** ~75 minut

## Cele nauczania

- Wymień trzy komponenty Voyagera — automatyczny program nauczania, bibliotekę umiejętności, podpowiedzi iteracyjne — i rolę każdego z nich.
- Wyjaśnij, dlaczego Voyager tworzy kod przestrzeni akcji, a nie prymitywne polecenia.
- Zaimplementuj bibliotekę umiejętności stdlib z rejestracją, pobieraniem, kompozycją i udoskonalaniem opartym na awariach.
- Mapuj wzór Voyagera na umiejętności SDK Agenta Claude'a 2026 i ekosystem zestawu umiejętności.

## Problem

Agenci, którzy w każdej sesji odbudowują każdą zdolność od zera, robią trzy rzeczy źle:

1. **Zmarnowane żetony.** Każde zadanie ponownie wywołuje to samo rozumowanie.
2. **Utrata postępu.** Korekta wyuczona w sesji A nie jest przenoszona do sesji B.
3. **Niepowodzenie w przypadku kompozycji długoterminowej.** Złożone zadania wymagają hierarchii możliwości; podpowiedzi jednorazowe nie mogą ich wyrazić.

Odpowiedź Voyagera: traktuj każdą możliwość wielokrotnego użytku jako nazwany fragment kodu przechowywany w bibliotece, który można odzyskać na podstawie podobieństwa, połączyć z innymi umiejętnościami i udoskonalić na podstawie informacji zwrotnych o wykonaniu.

## Koncepcja

### Trzy elementy

Voyager (arXiv:2305.16291) tworzy agenta wokół:

1. **Automatyczny program nauczania.** Osoba proponująca kierowana ciekawością wybiera kolejne zadanie w oparciu o aktualny zestaw umiejętności agenta i stan środowiska. Eksploracja odbywa się od dołu do góry.
2. **Biblioteka umiejętności.** Każda umiejętność jest kodem wykonywalnym. Nowe umiejętności są dodawane, gdy zadanie się powiedzie. Umiejętności są pobierane na podstawie podobieństwa zapytania do opisu.
3. **Iteracyjny mechanizm monitowania.** W przypadku niepowodzenia agent otrzymuje informacje o błędach wykonania, informacje zwrotne ze środowiska i wyniki samoweryfikacji, a następnie udoskonala umiejętności.

Ocena gry Minecraft (Wang i in., 2024): 3,3 razy więcej unikalnych przedmiotów, 8,5 razy szybsze narzędzia kamienne, 6,4 razy szybsze narzędzia żelazne, 2,3 razy dłuższe przemierzanie mapy w porównaniu z liniami bazowymi. Liczby są specyficzne dla Minecrafta, ale wzór jest przenoszony.

### Miejsce akcji = kod

Większość agentów wydaje prymitywne polecenia. Voyager emituje funkcje JavaScript. Umiejętność to:

```
async function craftIronPickaxe(bot) {
  await mineIron(bot, 3);
  await mineStick(bot, 2);
  await placeCraftingTable(bot);
  await craft(bot, 'iron_pickaxe');
}
```

Złożone z podumiejętności. Przechowywane z kluczem przy opisie i osadzaniu. Pobrano jako program, a nie jako monit.

To jest umiejętność Claude Agent SDK 2026: nazwany, możliwy do odzyskania fragment kodu oraz instrukcje, które agent ładuje na żądanie.

### Odzyskiwanie umiejętności

Nowe zadanie „zrób diamentowy kilof”. Agent:

1. Osadza opis zadania.
2. Wysyła zapytanie do biblioteki umiejętności o podobne umiejętności z najwyższej półki.
3. Pobiera `craftIronPickaxe`, `mineDiamond`, `placeCraftingTable` itd.
4. Tworzy nową umiejętność z odzyskanych prymitywów + nową logikę.

Jest to wzorzec wykorzystania zasobów MCP (faza 13) i umiejętności agenta SDK: pobieranie na powierzchni wiedzy/kodu, w zakresie bieżącego zadania.

### Iteracyjne udoskonalanie

Pętla sprzężenia zwrotnego Voyagera:

1. Agent zapisuje umiejętność.
2. Umiejętności działają przeciwko środowisku.
3. Zwraca jeden z trzech sygnałów: `success`, `error` (ze śladem stosu), `self-verification failure`.
4. Agent przepisuje umiejętność, wykorzystując sygnał jako kontekst.
5. Pętla aż do sukcesu lub maksymalnej liczby rund.

To samodoskonalenie (lekcja 05) zastosowane do generowania kodu z weryfikacją opartą na środowisku. KRYTYK (lekcja 05) to ten sam wzorzec z narzędziami zewnętrznymi, co weryfikator.

### Program nauczania i eksploracja

Moduł programu nauczania Voyagera proponuje zadania typu „zbuduj schronienie w pobliżu jeziora” w oparciu o to, co agent ma, a czego jeszcze nie zrobił. Osoba proponująca korzysta ze stanu środowiska i zasobów umiejętności, aby wybrać zadanie nieco powyżej bieżących możliwości — optymalny punkt eksploracji.

W przypadku agentów produkcyjnych oznacza to operator „czego brakuje”: biorąc pod uwagę obecną bibliotekę umiejętności i domenę, jakich umiejętności jeszcze nie omawiamy? Zespoły zazwyczaj wdrażają to ręcznie w ramach przeglądu programu nauczania.

### Gdzie ten wzorzec jest błędny

- **Zniszczona biblioteka umiejętności.** Ta sama umiejętność dodana 10 razy z nieco innymi opisami. Dodaj deduplikację przy zapisie; pobieranie zwraca tylko jeden.
- **Dryf umiejętności skomponowanych.** Umiejętności rodzica zależą od udoskonalonego dziecka. Umiejętności wersji; rodzic przypięty do wersji 1 nie pobiera magicznie wersji 3.
- **Jakość wyszukiwania.** Pobieranie wektorów z opisów umiejętności pogarsza się, gdy biblioteka przekracza kilkaset. Uzupełnij filtrami tagów i twardymi ograniczeniami („tylko umiejętności z `category=tooling`”).

## Zbuduj to

`code/main.py` implementuje bibliotekę umiejętności stdlib:

- `Skill` — nazwa, opis, kod (jako ciąg znaków), wersja, tagi, zależności.
- `SkillLibrary` — zarejestruj, wyszukuj (nakładanie się tokenów), twórz (topologiczny rodzaj deps) i udoskonalaj (aktualizacja wersji).
- Agent skryptowy, który rejestruje trzy prymitywne umiejętności, tworzy czwartą, trafia w błąd i udoskonala.

Uruchom to:

```
python3 code/main.py
```

Ślad pokazuje zapisy w bibliotece, pobieranie, kompozycję, nieudane wykonanie i udoskonalenie wersji 2 – od końca do końca pętli Voyagera.

## Użyj tego

- **Umiejętności Claude Agent SDK** (antropiczne) — odniesienie z 2026 r.: każda umiejętność ma opis, kod i instrukcje; ładowane na żądanie podczas sesji agenta.
- **skillkit** (npm: Skillkit) — zarządzanie umiejętnościami między agentami dla ponad 32 agentów kodujących AI.
- **Niestandardowe biblioteki umiejętności** — specyficzne dla domeny (umiejętności SQL dla agentów danych, umiejętności Terraform dla agentów infrastruktury). Wzór Voyagera zmniejsza się.
- **OpenAI Agents SDK `tools`** — na najniższym poziomie; każde narzędzie to lekka umiejętność.

## Wyślij to

`outputs/skill-skill-library.md` generuje bibliotekę umiejętności w kształcie Voyagera z rejestracją, wyszukiwaniem, wersjonowaniem i udoskonalaniem podłączonymi do dowolnego docelowego środowiska wykonawczego.

## Ćwiczenia

1. Dodaj detektor cykli zależności do `compose()`. Co się dzieje, gdy umiejętność A zależy od B, które zależy od A? Błąd czy ostrzeżenie?
2. Zaimplementuj przypinanie wersji dla poszczególnych umiejętności. Kiedy umiejętność nadrzędna tworzy element podrzędny `crafting@1`, udoskonalenie `crafting@2` nie może po cichu uaktualniać elementu nadrzędnego.
3. Zastąp pobieranie nakładających się tokenów osadzeniem transformatorów zdań (lub impl stdlib BM25). Zmierz odzyskanie @ 5 w bibliotece zabawek z 50 umiejętnościami.
4. Dodaj agenta „programu nauczania”: biorąc pod uwagę aktualną bibliotekę i opis domeny, zaproponuj 5 brakujących umiejętności. Dzwoń co tydzień.
5. Przeczytaj dokumentację umiejętności pakietu SDK Claude Agent firmy Anthropic. Przenieś bibliotekę zabawek do schematu umiejętności pakietu SDK. Jakie zmiany dotyczą wykrywalności?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Umiejętność | „Możliwość ponownego użycia” | Nazwany fragment kodu + opis, możliwy do odzyskania na podstawie podobieństwa |
| Biblioteka umiejętności | „Pamięć agenta z instrukcjami” | Trwały zasób umiejętności, który można przeszukiwać i komponować |
| Program nauczania | „Proponujący zadanie” | Generator celów oddolnych napędzany obecną luką w możliwościach |
| Skład | „Umiejętność DAG” | Umiejętności odwołujące się do umiejętności; posortowane topologicznie podczas wykonywania |
| Udoskonalanie iteracyjne | „Pętla samokorygująca” | Informacje zwrotne Env + błędy + samoweryfikacja złóż z powrotem do następnej wersji |
| Przestrzeń akcji jako kod | „Działania programowe” | Emituj funkcje, a nie prymitywne polecenia, dla czasowo przedłużonego zachowania |
| Deduplikacja przy zapisie | „Upadek umiejętności” | Prawie zduplikowane opisy sprowadzają się do jednej kanonicznej umiejętności |

## Dalsze czytanie

- [Wang i in., Voyager (arXiv:2305.16291)](https://arxiv.org/abs/2305.16291) — oryginalna praca z biblioteki umiejętności
- [Omówienie zestawu SDK Claude Agent](https://platform.claude.com/docs/en/agent-sdk/overview) — umiejętności jako produktyzacja 2026
- [Anthropic, Agenci budowlani z pakietem Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) — umiejętności i subagenci w praktyce
- [Madaan i in., Self-Refine (arXiv:2303.17651)](https://arxiv.org/abs/2303.17651) — pętla udoskonalania pod Voyagerem