# Budżety działań, limity iteracji i zarządcy kosztów

> Miesięczny koszt LLM średniej wielkości agenta handlu elektronicznego wzrósł z $1,200 to $4800 po tym, jak jego zespół włączył umiejętność „śledzenia zamówień”. To nie jest błąd cenowy. To agent, który znalazł nową pętlę i nadal w niej wydawał. Zestaw narzędzi Agent Governance Toolkit firmy Microsoft (2 kwietnia 2026 r.) kodyfikuje ochronę przed tą klasą: na żądanie `max_tokens`, token zadania i budżety w dolarach, limity dzienne/miesięczne, limity iteracji, warstwowy routing modelu, buforowanie podpowiedzi, okna kontekstowe, punkty kontrolne HITL dla kosztownych działań, wyłączniki awaryjne w przypadku naruszenia budżetu. Zestaw SDK Claude Code Agent firmy Anthropic dostarcza te same elementy podstawowe pod różnymi nazwami. Limity prędkości finansowej – m.in. zmniejsz dostęp do > 50 USD w 10 minut — pętle catch będą szybsze niż miesięczne limity.

**Typ:** Ucz się
**Języki:** Python (stdlib, warstwowy symulator zarządzania kosztami)
**Wymagania wstępne:** Faza 15 · 10 (Tryby uprawnień), Faza 15 · 12 (Trwałe wykonanie)
**Czas:** ~60 minut

## Problem

Autonomiczni agenci wydają prawdziwe pieniądze w każdej turze. Zły wynik chatbota jest złą odpowiedzią; Zła pętla agenta to rachunek. Udokumentowanym w branży terminem określającym tryb awarii jest „odmowa portfela” — agent kontynuuje rozumowanie, wywołuje narzędzia, utrzymuje rachunki i nic tego nie powstrzymuje, ponieważ nic nie zostało do tego zaprojektowane.

Rozwiązanie to nie jest jeden numer. Jest to zestaw limitów w różnych skalach czasowych i stopniach szczegółowości: na żądanie, na zadanie, na godzinę, na dzień, na miesiąc. Dobrze zaprojektowany stos wychwytuje niekontrolowaną pętlę w ciągu kilku minut, powolny wyciek w ciągu godzin, a nieprawidłowe wydanie w ciągu jednego dnia. Ten sam stos w ogóle utrzymuje budżet, gdy agent jest długoterminowy i autonomiczny.

To lekcja inżynierii: matematyka jest trywialna, dyscyplina jest tam, gdzie zespoły zawodzą. Wszystkie poniższe ograniczenia znajdują się w dokumentacji pakietu Microsoft Agent Governance Toolkit lub w dokumentacji pakietu Anthropic Claude Code Agent SDK.

## Koncepcja

### Stos administratora kosztów

1. **`max_tokens` na żądanie.** Proste. Uniemożliwia emitowanie nieograniczonego zakończenia przez dowolne wywołanie.
2. **Budżet tokenów na zadanie.** W całym cyklu nie przekraczaj N tokenów. Twardy przystanek na czapce.
3. **Budżet w dolarach na zadanie.** To samo co tokeny, ale w walucie. `max_budget_usd` w kodzie Claude'a.
4. **Limit wywołań na narzędzie.** Nie więcej niż N wywołań `WebFetch`, N `shell_exec` wywołań itp.
5. **Limit iteracji (`max_turns`).** Całkowita liczba iteracji pętli agenta; zapobiega nieskończonym pętlom rozumowania.
6. **Ograniczenie na minutę / godzinę / dzień / miesiąc.** Okna ruchome. Wyłapuje wycieki w różnych skalach czasowych.
7. **Ograniczenie prędkości finansowej.** Np. „jeśli wydatki przekroczą 50 USD w ciągu 10 minut, ogranicz dostęp”. Wychwytuje spalanie oparte na pętli przed uruchomieniem miesięcznych limitów.
8. **Warstwowe trasowanie modelu.** Domyślnie mniejszy model; eskalować do większego tylko wtedy, gdy klasyfikator uzna, że ​​zadanie to uzasadnia.
9. **Buforowanie podpowiedzi.** Podpowiedź systemowa i stabilny kontekst przechowywany w pamięci podręcznej dostawcy; symboliczny koszt ponownej wysyłki jest bliski zeru.
10. **Okna kontekstowe.** Kompaktowanie/podsumowywanie w celu utrzymania aktywnego kontekstu poniżej progu; bezpośrednia redukcja kosztów symbolicznych.
11. **Punkty kontrolne HITL dotyczące kosztownych działań.** Przed działaniem, o którym wiadomo, że jest kosztowne (długie wywoływanie narzędzi, pobieranie dużych ilości plików, kosztowna aktualizacja modelu), wymagane jest dotknięcie człowieka.
12. **Wyłącznik awaryjny w przypadku naruszenia budżetu.** Sesja zostaje przerwana po uruchomieniu dowolnego limitu. Czapka jest rejestrowana; wymaga osobnej ścieżki ponownego włączenia.

### Dlaczego stos, a nie jedna czapka

Pojedynczy miesięczny limit łapie uciekającego agenta dopiero wtedy, gdy portfel zniknie. Pojedynczy limit na żądanie nie powoduje niczego na poziomie sesji. Różne tryby awarii wymagają różnych skal czasowych:

- **Pętla ucieczki** (agent utknął w 5-sekundowej ponawianej próbie): złapany przez ograniczenie prędkości.
- **Powolny wyciek** (agent wykonuje ~2x oczekiwaną pracę na zadanie): przekroczony dzienny limit.
- **Złe wydanie** (nowa wersja używa 5x tokenów): złapana przez limit tygodniowy/miesięczny.
- **Uzasadniony wzrost** (rzeczywisty popyt, a nie błąd): złapany według limitu godzin/dni z przejrzystym logiem.

### Powierzchnia budżetowa Claude’a Code

Zestaw SDK Claude Code Agent udostępnia (dokumenty publiczne):

- `max_turns` — limit iteracji.
- `max_budget_usd` — limit dolara; sesja zostaje przerwana w przypadku naruszenia.
- `allowed_tools` / `disallowed_tools` — lista dozwolonych i zabronionych narzędzi.
- Punkty zaczepienia przed użyciem narzędzia w celu niestandardowego kalkulacji kosztów.

Połącz z drabiną trybu uprawnień (Lekcja 10). Sesja `autoMode` bez `max_budget_usd` to autonomia nieregulowana. Anthropic wyraźnie określa tryb automatyczny jako wymagający kontroli budżetu; klasyfikator jest ortogonalny do kosztu.

### Ustawa UE o sztucznej inteligencji, OWASP Agentic Top 10

Zestaw narzędzi do zarządzania agentami firmy Microsoft obejmuje 10 najlepszych agentów OWASP i wymagania art. 14 ustawy UE o sztucznej inteligencji (nadzór ludzki). W przypadku produkcji w UE pozyskiwanie drewna i egzekwowanie ograniczeń nie są opcjonalne.

### Zaobserwowano $1,200 → $4800 przypadków

Prawdziwy przypadek z dokumentacji Microsoftu: agent e-commerce, którego miesięczny koszt wzrósł trzykrotnie po dodaniu nowego narzędzia. Narzędzie umożliwiało agentowi odpytywanie statusu zamówienia podczas każdej sesji. Brak wykrywania pętli. Brak nasadki na narzędzie. Brak alertów dotyczących wzrostu z tygodnia na tydzień. Rozwiązaniem był limit przypadający na narzędzie oraz codzienny alert dotyczący wzrostu. To jest szablon: każda nowa powierzchnia narzędzia to nowa pętla potencjału; każde nowe narzędzie potrzebuje własnego limitu i własnego alertu.

## Użyj tego

`code/main.py` symuluje działanie agenta z warstwowym stosem zarządzającym kosztami i bez niego. Symulowany agent po kilku turach wpada w pętlę odpytywania; warstwowy stos łapie go w oknie prędkości, podczas gdy pojedynczy miesięczny limit zostanie uruchomiony dopiero po kilku dniach.

## Wyślij to

`outputs/skill-agent-budget-audit.md` sprawdza stos zarządzający kosztami proponowanego wdrożenia agenta i oznacza brakujące warstwy.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że ograniczenie prędkości jest uruchamiane przed limitem iteracji na trajektorii pętli odpytywania. Teraz wyłącz ograniczenie prędkości i zmierz, ile agent „wydaje”, zanim limit iteracji go przechwyci.

2. Zaprojektuj zestaw nasadek dla poszczególnych narzędzi dla agenta przeglądarki (Lekcja 11). Które narzędzie wymaga najciaśniejszej nasadki? Które narzędzie może działać bez ograniczeń i bez ryzyka?

3. Przeczytaj dokumentację zestawu narzędzi Microsoft Agent Governance Toolkit. Wypisz nazwy wszystkich zestawów narzędzi. Przypisz każdy z trybów awarii (niekontrolowana pętla, powolny wyciek, nieprawidłowe uwolnienie, przepięcie).

4. Wyceń nocną pracę bez nadzoru za realistyczne zadanie (np. „segreguj 50 problemów w repozytorium”). Ustaw `max_budget_usd` na dwukrotność szacunkowej wartości punktowej. Uzasadnij 2x.

5. Uruchamia `max_budget_usd` Claude Code na podstawie łącznego kosztu sesji. Zaprojektuj uzupełniające ograniczenie prędkości, które będziesz egzekwować zewnętrznie. Co powoduje odcięcie i jak wygląda ponowne włączenie?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| Odmowa portfela | „Uciekający rachunek” | Pętla agenta generująca wydatki bez ograniczenia, które mogłoby je zatrzymać |
| max_tokens | „Limit na żądanie” | Sufit na wymiar pojedynczego wykończenia |
| max_turns | „Limit iteracji” | Ograniczanie iteracji pętli agenta w sesji |
| max_budżet_usd | „Wyłącznik dolara” | Limit kosztów sesji; przerywa w przypadku naruszenia |
| Ograniczenie prędkości | „Limit stawki” | Limit wydatków na krótkie okno (np. 50 USD / 10 min) |
| Warstwowe routing | „Najpierw mały model” | Tani model domyślny; eskalować tylko wtedy, gdy klasyfikator na to pozwala |
| Natychmiastowe buforowanie | „Podpowiedź systemowa w pamięci podręcznej” | Pamięć podręczna po stronie dostawcy zmniejsza koszt tokenu ponownego wysłania prawie do zera |
| Punkt kontrolny HITL | „Brama akceptacji człowieka” | Przed kosztowną akcją wymagane jest ludzkie dotknięcie |

## Dalsze czytanie

– [Anthropic Claude Code Agent SDK — pętla agenta i budżety](https://code.claude.com/docs/en/agent-sdk/agent-loop) — `max_turns`, `max_budget_usd`, listy dozwolonych narzędzi.
- [Microsoft Agent Framework — działanie człowieka w pętli i zarządzanie] (https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) — punkty kontrolne odpowiedzialne za zarządzanie kosztami.
- [Anthropic — przegląd agentów zarządzanych przez Claude](https://platform.claude.com/docs/en/managed-agents/overview) — kontrola kosztów po stronie dostawcy.
- [Anthropic — Prompt caching (dokumentacja API Claude)](https://platform.claude.com/docs/en/prompt-caching) — mechanika buforowania.
- [Anthropic — Pomiar autonomii agentów w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — profil kosztów agentów dalekiego horyzontu.