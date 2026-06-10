# Studia przypadków i stan wiedzy na rok 2026

> Trzy źródła referencyjne dotyczące produkcji, umożliwiające kompleksowe przestudiowanie, a każde z nich ilustruje inny wycinek inżynierii wieloagentowej. **System badawczy Anthropic** (orkiestrator-pracownik, 15x tokenów, +90,2% w porównaniu z Opus 4 z jednym agentem, wdrożenia tęczowe) to kanoniczny przypadek nadzorcy. **MetaGPT / ChatDev** (specjalizacja ról w inżynierii oprogramowania zakodowana w SOP; „komunikatywna dehalucynacja” ChatDev; rozszerzenie MacNet do > 1000 agentów za pośrednictwem DAG, arXiv:2406.07155) to kanoniczny przypadek rozkładu ról. **OpenClaw / Moltbook** (pierwotnie Clawdbot autorstwa Petera Steinbergera, listopad 2025 r.; dwukrotnie zmieniona nazwa; 247 tys. gwiazd GitHub do marca 2026 r.; lokalni agenci z pętlą ReAct; Moltbook jako sieć społecznościowa przeznaczona wyłącznie dla agentów z ~2,3 mln kont agentów w ciągu kilku dni od uruchomienia, nabyta przez Meta 2026-03-10) ilustruje, co dzieje się w skali populacji: wschodzące ekonomie aktywność, ryzyko szybkiego wstrzyknięcia, regulacje na poziomie stanowym (Chiny ograniczyły OpenClaw na komputerach rządowych, marzec 2026 r.). **Krajobraz ramowy, kwiecień 2026 r.:** Główna produkcja LangGraph i CrewAI; AG2 jest kontynuacją społeczności AutoGen; Microsoft AutoGen znajduje się w trybie konserwacji (połączony z Microsoft Agent Framework, RC, luty 2026 r.); OpenAI Agents SDK jest produkcyjnym następcą Swarma; Google ADK (kwiecień 2025 r.) to nowy uczestnik rynku A2A. Każdy większy framework obsługuje teraz MCP; większość statków A2A. W tej lekcji szczegółowo analizujemy każdy przypadek i wyodrębniamy typowe wzorce, dzięki czemu można wybrać odpowiednie odniesienie dla następnego systemu produkcyjnego.

**Typ:** Dowiedz się (zwieńczenie)
**Języki:** —
**Wymagania wstępne:** cała faza 16 (lekcje 01-24)
**Czas:** ~90 minut

## Problem

Inżynieria wieloagentowa to młoda dyscyplina. Odniesień do produkcji jest niewiele, a każde dotyczy innego fragmentu przestrzeni. Przydatne jest czytanie ich pojedynczo; porównywanie ich jako zestawu jest bardziej przydatne. W tej lekcji trzy kanoniczne studia przypadków z 2026 r. potraktowano jako kompleksową listę lektur, przypięto wspólne wzorce i odwzorowano krajobraz ram, dzięki czemu można dokonywać wyborów ramowych na podstawie wiedzy, a nie marketingu.

## Koncepcja

### System badań antropicznych

Sprawa kierownik produkcji-pracownik. Claude Opus 4 planuje i syntetyzuje; Claude Sonnet 4 równoległe badania subagentów. Opublikowany post inżynierski: https://www.anthropic.com/engineering/multi-agent-research-system.

Kluczowe wyniki pomiarów:

- **+90,2%** poprawa w porównaniu z Opus 4 z jednym agentem w wewnętrznych ocenach badań.
- **80% wariancji BrowseComp** wyjaśnione **tylko użyciem tokena** — wieloagent wygrywa głównie dlatego, że każdy podagent otrzymuje nowe okno kontekstowe.
- **15x tokenów na zapytanie** w porównaniu z pojedynczym agentem.
- **Wdrożenie Rainbow**, ponieważ agenci działają długo i są stanowe.

Skodyfikowane lekcje projektowania:

1. **Skaluj wysiłek, aby uzyskać złożoność zapytań.** Prosty → 1 agent z 3–10 wywołaniami narzędzi. Średni → 3 agentów. Kompleksowe badania → 10+ subagentów.
2. **Najpierw szerokie, potem wąskie.** Subagenci przeprowadzają szerokie wyszukiwania; ołów syntetyzuje; następni subagenci wykonują ukierunkowane głębiny.
3. **Wdrożenie Rainbow.** Zachowaj stare wersje środowiska wykonawczego, dopóki ich agenci w locie nie zakończą pracy.
4. **Weryfikacja nie jest opcjonalna.** Zaobserwowano, że system ma halucynacje bez wyraźnej roli weryfikatora.

Jest to przypadek odniesienia dla topologii przełożony-pracownik (faza 16 · 05) w skali produkcyjnej.

### MetaGPT/ChatDev

Przypadek SOP produkcji – rozkład ról. Okładka arXiv:2308.00352 (MetaGPT) i arXiv:2307.07924 (ChatDev).

MetaGPT koduje SOP w zakresie inżynierii oprogramowania jako podpowiedzi dotyczące ról: Menedżer produktu, Architekt, Kierownik projektu, Inżynier, Inżynier ds. kontroli jakości. Obramowanie artykułu: `Code = SOP(Team)`. Każda rola ma wąski, wyspecjalizowany monit; przekazy między rolami niosą ze sobą ustrukturyzowane artefakty (dokumentacja PRD, dokumentacja architektury, kod).

Wkład ChatDev: **dehalucynacja komunikacyjna**. Agenci proszą o szczegóły przed udzieleniem odpowiedzi — agent projektanta pyta programistę, jaki język jest zamierzony przed naszkicowaniem interfejsu użytkownika, zamiast zgadywać. W artykule podano, że zmniejsza to w wymierny sposób halucynacje w potokach wieloagentowych.

MacNet (arXiv:2406.07155) rozszerza ChatDev do **>1000 agentów poprzez DAG**. Każdy węzeł DAG jest specjalizacją roli; krawędzie kodują umowy przekazania. Skala jest możliwa, ponieważ routing jest jawny i można go obliczyć w trybie offline.

Lekcje projektowania:

1. **Struktura ma większe znaczenie niż wielkość.** Zgrany, 5-osobowy zespół SOP pokonuje nieustrukturyzowaną grupę składającą się z 50 agentów.
2. **Umowy o przekazaniu na piśmie.** Artefakty przekazywane pomiędzy rolami podlegają schematowi.
3. **Dehalucynacja komunikacyjna** jest tanim i nośnym zjawiskiem.
4. **DAG skaluje się dalej niż czat.** Kiedy przepływ jest rozpoznawalny, zakoduj go.

Jest to przypadek odniesienia dla specjalizacji ról (faza 16 · 08) i topologii strukturalnej (faza 16 · 15).

### Ekosystem OpenClaw / Moltbook

Przypadek skali populacyjnej produkcji. Oś czasu:

- **Listopad 2025 r.:** Clawdbot (lokalny agent Petera Steinbergera zajmujący się kodowaniem pętli ReAct-loop).
- **grudzień 2025 r. – marzec 2026 r.:** dwukrotnie zmieniono nazwę (Clawdbot → OpenClaw → kontynuacja w ramach OpenClaw).
- **luty 2026 r.:** Moltbook zostaje uruchomiony jako sieć społecznościowa przeznaczona wyłącznie dla agentów, działająca na tych samych podstawach; ~2,3 mln kont agentów w ciągu kilku dni.
- **Marzec 2026 (10.03.2026):** Meta przejmuje Moltbook.
- **Marzec 2026:** Chiny ograniczają OpenClaw na komputerach rządowych.
- **Marzec 2026:** OpenClaw przekracza 247 tys. gwiazd GitHub.

Tak wygląda wieloagentowość, gdy umieścisz miliony agentów na współdzielonym podłożu:

- **Wschodząca działalność gospodarcza.** Agenci kupują, sprzedają i obsługują się nawzajem za pomocą płatności tokenami.
- **Ryzyko wstrzyknięcia podpowiedzi w skali populacji.** Jedna złośliwa zachęta w profilu agenta wirusowego rozprzestrzenia się na tysiące interakcji między agentami w ciągu godzin.
- **Reakcja organów regulacyjnych na poziomie stanu.** W ciągu kilku tygodni od uruchomienia regulacje docierają do ekosystemu.

Wnioski dotyczące projektowania wyciągnięte z tego przypadku mają charakter częściowo techniczny, częściowo dotyczący zarządzania:

1. **Wieloagentowy system w skali populacji to nowy system.** Najlepsze praktyki dotyczące poszczególnych systemów (weryfikacja, przejrzystość ról) nadal mają zastosowanie, ale nie są wystarczające.
2. **Wstrzykiwanie podpowiedzi to nowy XSS.** Profile agentów i wiadomości międzyagentowe są domyślnie traktowane jako niezaufane dane wejściowe.
3. **Regulacja jest szybsza niż cykle projektowe.** Zaplanuj to.
4. **Open source + związki na skalę wirusową.** 247 tys. gwiazd w ~4 miesiące to coś niezwykłego; projekt dla wdrożenia-burst-load.

Szczegółowe informacje na temat ekosystemu można znaleźć w [Wikipedii OpenClaw](https://en.wikipedia.org/wiki/OpenClaw) i raportach CNBC/Palo Alto Networks. Ze względów technicznych repozytoria Clawdbot/OpenClaw udostępniają lokalną pętlę ReAct; Publiczne posty Moltbooka ujawniają architekturę wykresów społecznościowych na górze.

### Krajobraz ramowy, kwiecień 2026 r

| Ramy | Stan | Najlepsze dla | Notatki |
|---|---|---|---|
| **LangGraf** (LangChain) | Lider produkcji | wykres strukturalny + punkty kontrolne + człowiek w pętli | zalecane ustawienie domyślne dla produkcji |
| **ZałogaAI** | Lider produkcji | zespoły oparte na rolach z procesami sekwencyjnymi/hierarchicznymi | silny dla rozkładu ról |
| **AG2** | Społeczność utrzymana | GroupChat + wybór prelegentów | Kontynuacja AutoGen v0.2 |
| **Microsoft AutoGen** | Tryb konserwacji (luty 2026 r.) | — | połączone z Microsoft Agent Framework RC |
| **Microsoft Agent Framework** | RC (luty 2026 r.) | wzorce orkiestracji + integracja przedsiębiorstwa | nowy uczestnik; oglądaj |
| **SDK dla agentów OpenAI** | Produkcja | Następca roju | wzór przekazania zwrotu narzędzia |
| **ADK Google** | Produkcja (kwiecień 2025) | Natywny A2A | Integracja z Google Cloud |
| **Antropiczny pakiet SDK dla agenta Claude’a** | Produkcja | pojedynczy agent + Rozszerzenie badawcze | zobacz wpis System badawczy |

Każdy większy framework obsługuje teraz **MCP**; większość statków **A2A**. Zgodność protokołów nie jest już wyróżnikiem.

### Wspólne wzorce we wszystkich trzech przypadkach

1. **Orkiestrator + pracownicy** (wyraźny przełożony antropiczny, kierownik MetaGPT jako przełożony, indywidualni agenci OpenClaw + efekty sieciowe).
2. **Strukturalne umowy o przekazaniu** (opisy zadań subagenta Anthropic, dokumentacja MetaGPT PRD/architektura, artefakty OpenClaw A2A).
3. **Weryfikacja jako pierwszorzędna rola** (weryfikator Anthropic, inżynier ds. kontroli jakości MetaGPT, walidatorzy wewnątrz sieci OpenClaw).
4. **Skalowanie to topologia + podłoże, a nie tylko więcej agentów** (wdrożenia Rainbow, DAG MacNet, substraty w skali populacji).
5. **Koszt jest istotny i ujawniony** (15x tokenów, budżet na rolę w MetaGPT, ceny za interakcję w Moltbook).
6. **Stan bezpieczeństwa jest wyraźnie określony** (piaskownica Anthropic, ograniczenia ról MetaGPT, natychmiastowe wprowadzenie OpenClaw jako znanej powierzchni ataku).

### Wybór referencji do następnego projektu

- **Badania produkcyjne / zadanie wiedzy → Badania antropiczne.** Wygrywają subagenci świeżego kontekstu.
- **Przepływ prac inżynieryjnych / łańcucha narzędzi → MetaGPT / ChatDev.** Role + SOP + umowy o przekazaniu.
- **Produkt społeczny o działaniu sieciowym → OpenClaw / Moltbook.** Substrat + gospodarka wschodząca.
- **Klasyczna automatyzacja dla przedsiębiorstw → CrewAI lub LangGraph** (lider produkcji, stabilne środowisko wykonawcze).

### Podsumowanie najnowocześniejszego roku 2026

Gdzie jest pole w kwietniu 2026 r.:

- **Ramy są zbieżne.** Obsługa MCP + A2A to stawka w tabeli. Pozostałym wyborem projektowym jest semantyka przekazywania.
- **Ocena jest coraz trudniejsza.** Testy porównawcze SWE-bench Pro, MARBLE, STRATUS. Pro to aktualny, odporny na zanieczyszczenia tester rzeczywistości.
- **Wskaźniki awaryjności produkcji są mierzalne** (Cemri 2025 MAST; 41-86,7% na rzeczywistym MAS). Pole to wyszło z ery „świetnie wygląda w wersji demonstracyjnej”.
- **Koszt jest głównym ograniczeniem inżynieryjnym.** Koszt symboliczny na zadanie, zegar ścienny na interakcję, narzut związany z wdrażaniem Rainbow. Multiagent wygrywa pod względem dokładności, ale traci na kosztach — a decyzja biznesowa to handel.
- **Regulacje mają charakter krótkoterminowy, a nie problem drugoplanowy.** Jurysdykcje zmieniają się szybciej niż poszczególne cykle wdrażania.

## Użyj tego

`outputs/skill-case-study-mapper.md` to umiejętność polegająca na odczytywaniu proponowanego projektu systemu wieloagentowego i mapowaniu go na najbliższe studium przypadku, ujawniając decyzje projektowe już przetestowane w tym studium przypadku.

## Wyślij to

Zasady startowe dla multiagenta produkcyjnego w 2026 roku:

- **Zacznij od studium przypadku, a nie od zera.** Wybierz najbliższy Anthropic Research / MetaGPT / OpenClaw i dostosuj się.
- **Zastosuj MCP + A2A.** Przenośność między platformami jest cenna; obsługa protokołów jest bezpłatna.
- **Porównaj z SWE-bench Pro lub wewnętrznym odpowiednikiem Pro.** Sprawdzono, czy jest zanieczyszczony.
- **Zapłać podatek weryfikacyjny.** Niezależny weryfikator kosztuje ~20-30% Twojego budżetu tokena i kupuje mierzalną poprawność.
- **Rainbow wdraża długotrwałych agentów.** Należy spodziewać się, że wielogodzinne uruchamianie agentów będzie rutynowe.
- **Przeczytaj WMAC 2026 i kontynuacje MAST.** Dyscyplina szybko się zmienia.

## Ćwiczenia

1. Przeczytaj cały system badań Anthropic. Wskaż trzy decyzje projektowe, które zmieniłyby się, gdybyś zastąpił Opus 4 mniejszym modelem (np. Haiku 4).
2. Przeczytaj sekcje MetaGPT 3-4 (arXiv:2308.00352). Zakoduj jedną SOP z własnej domeny (nie oprogramowania) jako monity roli. Ile ról zakłada SPO?
3. Przeczytaj ChatDev (arXiv:2307.07924). Zidentyfikuj mechanizm „komunikatywnej dehalucynacji”. Zaimplementuj go w jednym z istniejących systemów wieloagentowych.
4. Przeczytaj o OpenClaw i Moltbook. Wybierz jeden konkretny tryb awarii, który pojawił się w skali populacji i który nie pojawiłby się w systemie z 5 agentami. Jak byś przeciwko temu zaprojektował?
5. Wybierz swój aktualny projekt wieloagentowy. Które z trzech studiów przypadku jest najbliższym odniesieniem? Których decyzji projektowych z tego studium przypadku jeszcze NIE podjąłeś? Zapisz jedno, które przyjmiesz w tym kwartale.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Badania antropiczne | „Referencja przełożonego” | Claude Opus 4 + Sonnet 4 podagentów; 15x żetonów; +90,2% w porównaniu z jednym agentem. |
| MetaGPT | „SOP jako podpowiedzi” | Dekompozycja ról w inżynierii oprogramowania; `Code = SOP(Team)`. |
| ChatDev | „Agenci jako role” | Projektant / programista / recenzent / tester; dehalucynacja komunikacyjna. |
| MacNet | „Skaluj ChatDev poprzez DAG” | arXiv:2406.07155; Ponad 1000 agentów za pośrednictwem jawnego routingu DAG. |
| OpenClaw | „Lokalni agenci pętli ReAct” | projekt Steinbergera; 247 tys. gwiazd do marca 2026 r. |
| Moltbook | „Sieć społecznościowa tylko dla agentów” | 2,3 mln kont agentów; przejęty przez Meta w marcu 2026 r. |
| Tęcza wdrażana | „Wiele wersji jednocześnie” | Zachowaj przy życiu stare wersje środowiska wykonawczego dla długotrwałych agentów. |
| Odhalucynacja komunikacyjna | „Zapytaj zanim odpowiesz” | Agenci żądają konkretów od rówieśników, zamiast zgadywać. |
| WMAC 2026 | „Warsztaty AAAI” | Kwiecień 2026 r. Punkt kontaktowy społeczności ds. koordynacji wieloagentowej. |

## Dalsze czytanie

- [Anthropic — Jak zbudowaliśmy nasz wieloagentowy system badawczy](https://www.anthropic.com/engineering/multi-agent-research-system) — odniesienie do produkcji przełożonego-pracownika
- [MetaGPT — Meta Programming for Multi-Agent Collaborative Framework](https://arxiv.org/abs/2308.00352) — Dekompozycja ról SOP
- [ChatDev — Agenci komunikatywni do tworzenia oprogramowania](https://arxiv.org/abs/2307.07924) — dehalucynacja komunikacyjna
- [MacNet — skalowanie agentów opartych na rolach do ponad 1000](https://arxiv.org/abs/2406.07155) — skalowanie oparte na DAG
- [OpenClaw na Wikipedii](https://en.wikipedia.org/wiki/OpenClaw) — przegląd ekosystemu
- [WMAC 2026](https://multiagents.org/2026/) — Warsztaty programu pomostowego AAAI 2026 na temat koordynacji wieloagentowej
- [Dokumentacja LangGraph](https://docs.langchain.com/oss/python/langgraph/workflows-agents) — lider produkcji
- [Dokumentacja CrewAI](https://docs.crewai.com/en/introduction) — framework oparty na rolach