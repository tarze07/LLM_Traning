# Wspólna pamięć i wzory tablic

> W systemach wieloagentowych 2026 współistnieją dwa podejścia: **pula wiadomości** (każdy widzi wiadomości wszystkich, jak w AutoGen GroupChat lub MetaGPT) i **tablica z subskrypcją** (agenci subskrybują odpowiednie zdarzenia, jak w kontekstowym MCP lub frameworku Matrix). Obydwa stanowią jedyną stanową część systemu wieloagentowego — co oznacza, że ​​w obu występują interesujące błędy. Tryb awarii odniesienia to **zatrucie pamięci**: jeden agent halucynuje „fakt”, inni agenci traktują go jako zweryfikowany, a dokładność spada stopniowo w sposób znacznie trudniejszy do naprawienia niż natychmiastowa awaria. Ta lekcja buduje obie struktury ze stdlib, wprowadza atak zatruwający i pokazuje trzy rozwiązania, które faktycznie działają w środowisku produkcyjnym.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib, `threading`)
**Wymagania wstępne:** Faza 16 · 04 (model prymitywny), Faza 16 · 09 (Równoległe sieci roju)
**Czas:** ~75 minut

## Problem

Systemy wieloagentowe potrzebują miejsca, w którym agenci mogą dzielić się faktami. Dosłowną opcją jest „przekaż wszystko w wiadomościach” — ale to zmienia stan współdzielony z dodatkowym kopiowaniem. Innym jest „daj wszystkim dziennik globalny” — ale dzienniki globalne rosną nieograniczony i łatwo zatruwają. Trzeci to „projektowanie widoku na agenta” — skalowalny, ale wymagający dużej ilości schematów.

Kiedy jeden z agentów ma halucynacje i zapisuje halucynację do wspólnego stanu, każdy dalszy agent, który odczytuje ten stan, przyjmuje halucynację jako fakt. Zanim człowiek to zauważy, łańcuch rozumowania składa się z pięciu etapów, a podstawową przyczyną jest trzecia wiadomość, jaką kiedykolwiek napisano. Debugowanie spadku dokładności wielu agentów jest trudniejsze niż debugowanie awarii.

To zatrucie pamięci. Jest to druga najczęściej udokumentowana rodzina awarii w taksonomii MAST (Cemri et al., arXiv:2503.13657) i ma charakter strukturalny: każdy projekt pamięci współdzielonej bez pochodzenia i niezapisywalnego weryfikatora w końcu ją wykaże.

## Koncepcja

### Dwie główne topologie

**Pełna pula wiadomości.** Każdy agent czyta każdą wiadomość. Używają tego AutoGen GroupChat i MetaGPT. Prosty, przejrzysty, możliwy do sprawdzenia, ale nie skaluje się powyżej ~10 agentów, ponieważ kontekst każdego agenta wypełnia się pracą innych agentów.

```
agent-A ──write──▶ ┌────────────────┐ ◀──read── agent-D
                   │ message pool   │
agent-B ──write──▶ │                │ ◀──read── agent-E
                   │ (global log)   │
agent-C ──write──▶ └────────────────┘ ◀──read── agent-F
```

**Tablica w abonamencie.** Agenci deklarują zainteresowanie tematami; substrat przesyła tylko istotne wiadomości. Używają tego CA-MCP (arXiv:2601.11595) i zdecentralizowana struktura Matrix (arXiv:2511.21686). Skaluje się dalej, ale wymaga wstępnego zaprojektowania schematu, aby subskrypcje miały sens.

```
                   ┌─ topic: prices ──┐
agent-A ──pub────▶ │                  │ ──▶ agent-D (subscribed)
                   ├─ topic: orders ──┤
agent-B ──pub────▶ │                  │ ──▶ agent-E (subscribed)
                   ├─ topic: alerts ──┤
agent-C ──pub────▶ │                  │ ──▶ agent-F (subscribed)
                   └──────────────────┘
```

### Kiedy każdy wygrywa

- **Full Pool** wygrywa, gdy agentów jest niewielu (< 10), są niejednorodni, a rozmowa jest krótkotrwała. Rozumowanie o tym, kto powiedział co, jest trywialne, skoro wszyscy wszystko widzą.
- **Tablica** wygrywa, gdy agentów jest wielu, mają jednorodną rolę, ale są liczni (roje), a rozmowa trwa długo. Routing pozwala zaoszczędzić na kosztach tokenów i zanieczyszczeniu kontekstu.

Systemy produkcyjne często się mieszają: na górze mały, pełny basen (warstwa planowania), na dole tablice (warstwa pracownika).

### Zatrucie pamięci w jednym ze scenariuszy

Trzej agenci pracują nad zadaniem badawczym. Agent A jest agentem odzyskiwania. Agent B jest podsumowującym. Agent C jest analitykiem.

1. A pobiera stronę i zapisuje wiadomość do udostępnionego stanu: „Badanie wykazało poprawę dokładności o 42%”.
2. Na pobranej stronie w rzeczywistości widniała informacja „Poprawa o 4,2%”. Halucynacja dziesiętna.
3. B, czytając stan współdzielony, pisze: „Zgłoszono duży wzrost dokładności o 42% (źródło: A).”
4. C, czytając wspólny stan, pisze: „Polecam adopcję — wzrost o 42% ma charakter transformacyjny”.
5. W raporcie końcowym przytacza się liczbę 42%, która nigdy nie istniała.

Żaden agent się nie zawiesił. Żaden test się nie udał. System „zadziałał”. Halucynacja przeszła z kontekstu jednego agenta do rozumowania każdego kolejnego agenta poprzez wspólny stan.

### Dlaczego to ma charakter strukturalny

Bez wspólnego stanu halucynacje agenta A pozostają w kontekście A. Agenci podrzędni pobieraliby ponownie lub ponownie pobierali i mogliby wyłapać błąd. W przypadku naiwnego stanu wspólnego kontekst A staje się kontekstem wszystkich, a halucynacje zostają zamienione w fakty.

Problemem nie jest stan wspólny jako taki — jest to stan wspólny **bez pochodzenia i niezależnego weryfikatora**. Rozwiązują ten problem trzy środki zaradcze:

1. **Przy każdym zapisie należy podać pochodzenie.** Każdy wpis w stanie udostępnionym rejestruje, kto go napisał, kiedy, pod jakim monitem i (jeśli dotyczy) jakie źródło cytował agent. Agenci niższego szczebla czytają ze sceptycyzmem, kierując się pochodzeniem.
2. ** Wersja pisze; traktuj je jako przeznaczone tylko do dołączenia.** Korekta to nowy wpis, który zastępuje starą, a nie aktualizację lokalną. Ścieżka audytu zostaje zachowana.
3. **Zachowaj co najmniej jednego agenta, który nie może zapisywać danych w stanie współdzielonym.** Agent weryfikujący tylko do odczytu próbkuje wpisy, ponownie pobiera źródła i flaguje niespójności. Ponieważ nie może zapisywać do puli, nie może zostać zatruty przez pulę.

### Tablica precedensowa (Hayes-Roth, 1985)

Wzór tablicy jest starszy o cztery dekady od agentów LLM. Hayes-Roth (1985, „A Blackboard Architecture for Control”) opisał specjalistyczne źródła wiedzy, które obserwują globalną tablicę, dostarczają częściowych rozwiązań i uruchamiają inne źródła. Tablica 2026 (CA-MCP, Matrix) ma ten sam wzór z agentami LLM jako źródłami wiedzy i obiektami blob JSON jako rozwiązaniami częściowymi. W starej literaturze udokumentowano rozwiązania w zakresie pisania rywalizacji, kontroli oportunistycznej i spójności, które współczesne systemy odkrywają na nowo.

### Projekcja a pełny widok

Czysta tablica daje każdemu abonentowi taką samą projekcję (w zakresie tematycznym). Bardziej agresywny projekt to **projekcja na agenta**: każdy agent otrzymuje widok dostosowany do swojej roli. Reduktory stanu LangGrapha są kanoniczną implementacją 2026 — funkcja reduktora składa stan globalny w wycinek specyficzny dla roli.

Projekcja na agenta skaluje się dalej, ale wymaga schematu. Bez niego odbudujesz projekcję ad hoc w wierszu poleceń każdego agenta.

### Wzorce rywalizacji o zapis

Wielu agentów piszących jednocześnie jest problemem współbieżności, a nie tylko problemem LLM. Działają trzy wzory:

- **Sekwencyjny zapis (jeden producent).** Wszystkie zapisy przechodzą przez jednego agenta koordynującego, który serializuje. Proste, ale wąskie gardło.
- **Optymistyczna zbieżność z wersjonowaniem.** Każdy wpis ma wersję; autorzy nie powiedzie się w przypadku niezgodności wersji i spróbują ponownie. Klasyczna technika baz danych.
- **Podział tematów.** Różni agenci mają różne tematy. Żadnych sporów między tematycznych. Wymaga zaprojektowanych granic partycji.

Większość frameworków 2026 domyślnie korzysta z modułu zapisu sekwencyjnego, ponieważ wywołania LLM są na tyle wolne, że rywalizacja jest rzadka, a wąskie gardło nie szkodzi.

### Niezapisywalny weryfikator

Najbardziej obciążającym rozwiązaniem jest weryfikator tylko do odczytu. Zasady wdrożenia:

- Weryfikator dzieli się stanem z zespołem (czyta z tablicy lub basenu).
- Weryfikator nie ma uchwytu zapisu do stanu współdzielonego - tylko do osobnego kanału weryfikacji.
- Weryfikator samodzielnie pobiera źródła cytowane w zapisach. Flaga niezgody.
- Wyniki własne weryfikatora są kierowane do człowieka lub oddzielnego agenta decyzyjnego i nigdy nie są wprowadzane z powrotem do puli.

Bez tego oddzielenia wyniki weryfikatora stają się nowymi wpisami w puli, co oznacza, że ​​zatruta pula zatruwa weryfikator, co zatruwa jego weryfikacje.

## Zbuduj to

`code/main.py` implementuje obie topologie w stdlib Python, a także atak polegający na zatruciu zabawką i trzy rozwiązania łagodzące.

- `MessagePool` — bezpieczny dla wątków dziennik tylko do dołączania i z pełnym odczytem.
- `Blackboard` — pub/subskrypcja tematyczna z subskrypcjami dla poszczególnych agentów.
- `ProvenanceEntry` — każdy rekord zapisu (zapis, znacznik czasu, Prompt_hash, source_uri).
- `PoisoningScenario` — wykonuje zadanie badawcze z udziałem trzech agentów, podczas którego agent A ma halucynacje ułamka dziesiętnego. Drukuje raport końcowy.
- `Verifier` — agent tylko do odczytu, który ponownie pobiera źródła i sygnalizuje niespójności. Uruchamia ten sam scenariusz z obecnym weryfikatorem.

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik:
- Runda 1 (bez weryfikatora): halucynowane 42% przechodzi do raportu końcowego.
- Badanie 2 (z weryfikatorem): weryfikator zaznacza niespójność, pula jest oznaczona jako „oflagowana”, raport końcowy zawiera wycofanie.

## Użyj tego

`outputs/skill-memory-auditor.md` to umiejętność umożliwiająca audytowanie projektu pamięci współdzielonej dowolnego systemu wieloagentowego pod kątem pochodzenia, wersji i separacji weryfikatorów. Uruchom go na nowych architekturach wieloagentowych przed rozpoczęciem produkcji.

## Wyślij to

W przypadku dowolnego projektu pamięci współdzielonej:

- Zapisz pochodzenie przy każdym zapisie: `(writer, timestamp, prompt_hash, tool_calls_cited, source_uri)`.
- Ustaw dziennik jako tylko do dołączania. Korekty to nowe wpisy, które odwołują się do zastąpionego.
- Wdróż co najmniej jednego agenta weryfikującego tylko do odczytu z niezależnym dostępem do źródła.
- Kieruj dane wyjściowe weryfikatora do osobnego kanału, a nie z powrotem do wspólnej puli.
- Zapisz współczynnik zapisów stanowiących zastąpienia — rosnący współczynnik jest wczesnym dowodem wzorców halucynacji.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że bieg 1 propaguje halucynację, a bieg 2 go wychwytuje.
2. Dodaj drugą halucynację: agent B wymyśla rozmiar zbioru danych. Weryfikator powinien wychwycić oba bez ręcznego dostrajania żadnego z nich.
3. Przełącz całą pulę na tablicę z podziałami tematycznymi (`prices`, `summaries`, `analyses`). W jakich sytuacjach zatrucia podział tematów utrudnia, a w jakich nie pomaga?
4. Przeczytaj Hayes-Roth (1985, „Architektura tablicowa zapewniająca kontrolę”). Wskaż dwa wzorce kontroli z artykułu nieomówionego w tej lekcji, z których skorzystają systemy w roku 2026.
5. Przeczytaj CA-MCP (arXiv:2601.11595). Zamapuj jego magazyn wspólnego kontekstu na klasę MessagePool lub Blackboard w `code/main.py`. Jakie elementy podstawowe dodaje CA-MCP na wierzchu?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Pula wiadomości | „Wspólna historia czatów” | Dziennik z możliwością dołączenia, który czyta każdy agent. Pełna przezroczystość, słabe skalowanie. |
| Tablica | „Wspólna przestrzeń robocza” | Pub/sub z kluczem tematycznym. Agenci subskrybują odpowiednie tematy. Wagi dalej. |
| Pochodzenie | „Kto co napisał” | Metadane przy każdym zapisie: zapis, znacznik czasu, zachęta, źródła. |
| Zatrucie pamięci | „Rozprzestrzeniające się halucynacje” | Błąd jednego agenta przechodzi w stan wspólny, agenci dalszych działań przyjmują to jako fakt. |
| Tylko dołączanie | „Brak aktualizacji na miejscu” | Korekty to nowe wpisy, które zastępują. Zachowuje ścieżkę audytu. |
| Niezapisywalny weryfikator | „Niezależny audytor” | Agent tylko do odczytu, który ponownie pobiera źródła i sygnalizuje niespójności. |
| Projekcja | „Widok w zakresie” | Widok na agenta obliczony na podstawie stanu globalnego. Reduktory LangGrapha są przypadkiem kanonicznym. |
| Źródło wiedzy | „Agent specjalistyczny” | Określenie Hayesa-Rotha z 1985 r. na uczestnika tablicy. |

## Dalsze czytanie

- [Cemri i in. — Dlaczego wieloagentowe systemy LLM zawodzą?](https://arxiv.org/abs/2503.13657) — taksonomia MAST; zatrucie pamięci to podrodzina zaburzeń koordynacji
- [CA-MCP — Context-Aware Multi-Server MCP](https://arxiv.org/abs/2601.11595) — Shared Context Store dla skoordynowanych serwerów MCP
- [Matrix — zdecentralizowana platforma wieloagentowa] (https://arxiv.org/abs/2511.21686) — tablica oparta na kolejce wiadomości bez centralnego koordynatora
- [Stan LangGraph i reduktory](https://docs.langchain.com/oss/python/langgraph/workflows-agents) — wzorzec projekcji dla poszczególnych agentów w produkcji
- [Anthropic — Jak zbudowaliśmy nasz wieloagentowy system badawczy](https://www.anthropic.com/engineering/multi-agent-research-system) — notatki dotyczące pochodzenia i weryfikacji z wdrożenia produkcyjnego