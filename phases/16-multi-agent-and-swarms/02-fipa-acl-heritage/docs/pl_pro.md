# Dziedzictwo FIPA-ACL i aktów mowy

> Przed MCP i A2A istniała FIPA-ACL. W 2000 roku Fundacja IEEE na rzecz Inteligentnych Agentów Fizycznych ratyfikowała język komunikacji agentów składający się z dwudziestu performatywów, dwóch języków treści i zestawu protokołów interakcji — takich jak sieć kontraktowa (Contract Net), subskrypcja/powiadomienie czy żądanie-kiedy (request-when). Standard ten zniknął z rynku, ponieważ narzut związany z utrzymaniem formalnych ontologii okazał się zbyt duży dla architektury sieciowej. Jednak obecne odrodzenie systemów wieloagentowych opartych na LLM po cichu wprowadza te same idee bez formalnej semantyki: kontrakty JSON zastępują performatywy, a język naturalny — ontologie. W tej lekcji przyjrzymy się poważnie FIPA-ACL, aby zobaczyć, które decyzje projektowe dotyczące protokołów na rok 2026 stanowią rzeczywistą nowość, a w których miejscach obecna fala na nowo odkrywa problemy rozwiązane już w pierwszej dekadzie XXI wieku.

**Typ:** Ucz się  
**Języki:** Python (stdlib)  
**Wymagania wstępne:** Faza 16 · 01 (Dlaczego wieloagentowy)  
**Czas:** ~60 minut  

## Problem

Krajobraz protokołów agentowych w roku 2026 jest bardzo zatłoczony: MCP dla narzędzi, A2A dla współpracy agentów, ACP dla audytu przedsiębiorstwa, ANP dla zdecentralizowanego zaufania, NLIP dla treści w języku naturalnym, a do tego CA-MCP i dziesiątki innych propozycji badawczych. Każda specyfikacja reklamuje się jako fundamentalna.

W rzeczywistości większość z nich odtwarza drzewo decyzyjne sprzed dwudziestu lat. Teoria aktów mowy Austina (1962) i Searle'a (1969) wprowadziła pogląd, że „wypowiedzi są działaniami”. KQML (1993) przekształcił to w protokół sieciowy. FIPA-ACL (ratyfikowana w 2000 r.) stworzyła standard referencyjny: dwadzieścia performatywów, języki treści SL0/SL1 oraz protokoły interakcji dla sieci kontraktowej i subskrypcji. JADE i JACK były referencyjnymi platformami napisanymi w Javie. Wysiłki te wygasły około 2010 roku, ponieważ narzut ontologiczny okazał się zbyt duży, a sieć WWW poszła w kierunku prostszych rozwiązań.

Analizując `tools/call` w MCP, cykl życia zadań w A2A czy współdzieloną pamięć kontekstu w CA-MCP, łatwo dostrzec lżejsze, natywne dla formatu JSON odpowiedniki decyzji projektowych z FIPA. Zrozumienie tego dziedzictwa pozwala dostrzec dwie kwestie: które z rzekomych innowacji są w istocie powtórzeniem starych koncepcji oraz jakie znane tryby awarii ujawnią się w nowych specyfikacjach.

## Koncepcja

### Akty mowy w jednym akapicie

Austin zauważył, że niektóre wypowiedzi nie tylko opisują świat, ale go zmieniają (np. „Obiecuję”, „Przepraszam”, „Ogłaszam”). Nazwał je wypowiedziami performatywnymi. Searle sformalizował pięć kategorii aktów mowy: asertywne, dyrektywne, komisywne, ekspresywne i deklaratywne. KQML (Finin i in., 1993) przeniósł to na grunt agentów programowych: komunikat składa się z performatywu (typu działania) oraz treści (przedmiotu działania). FIPA-ACL uzupełniła luki w KQML i ujednoliciła zestaw około dwudziestu performatywów.

### Dwadzieścia performatywów FIPA (częściowa lista)

| Performatyw | Intencja |
|---|---|
| `inform` | „Mówię ci, że P jest prawdą” |
| `request` | „Proszę Cię o wykonanie X” |
| `query-if` | „Czy P jest prawdą?” |
| `query-ref` | „Jaka jest wartość X?” |
| `propose` | „Proponuję zrobić X” |
| `accept-proposal` | „Przyjmuję propozycję” |
| `reject-proposal` | „Odrzucam propozycję” |
| `agree` | „Zgadzam się zrobić X” |
| `refuse` | „Odmawiam wykonania X” |
| `confirm` | „Potwierdzam, że P jest prawdą” |
| `disconfirm` | „Zaprzeczam, że P jest prawdą” |
| `not-understood` | „Twoja wiadomość nie została prawidłowo zinterpretowana” |
| `cfp` | „Zaproszenie do składania ofert (Call for Proposal) w sprawie X” |
| `subscribe` | „Powiadom mnie, gdy zmieni się stan X” |
| `cancel` | „Anuluj trwające zadanie X” |
| `failure` | „Próbowałem wykonać X i nie udało mi się” |

Pełna lista znajduje się w specyfikacji `fipa00037.pdf` (FIPA ACL Message Structure). Nie chodzi o to, by zapamiętywać te nazwy – ważne jest to, że każdy z tych performatywów odpowiada prymitywom, które współczesne protokoły LLM muszą w ten czy inny sposób zaimplementować.

### Kanoniczny komunikat FIPA-ACL

```
(inform
  :sender       agent1@platform
  :receiver     agent2@platform
  :content      "((price IBM 83))"
  :language     SL0
  :ontology     finance
  :protocol     fipa-request
  :conversation-id   conv-42
  :reply-with   msg-17
)
```

Koperta protokołu zawiera siedem pól metadanych, a samo pole `content` przenosi ładunek. Pozostałe pola to dokładnie te elementy, które odtwarza się na nowo, projektując obsługę ponownych prób, wątkowania czy ontologii w formatach opartych na JSON.

### Dwie starsze platformy

**JADE** (Java Agent DEvelopment Framework, 1999–2020) był najpopularniejszym środowiskiem wykonawczym zgodnym z FIPA. Agenci rozszerzali klasę bazową, wymieniali komunikaty ACL, uruchamiali kontenery i koordynowali działania za pomocą struktur zachowań (behaviours). Wbudowana biblioteka protokołów wspierała sieć kontraktową, mechanizm subskrypcja-powiadomienie, żądanie-kiedy i propozycja-akceptacja.

**JACK** (Agent-Oriented Software, produkt komercyjny) kładł nacisk na model rozumowania BDI (Belief-Desire-Intention) jako uzupełnienie komunikacji FIPA. Był bardziej formalny, ale zyskał mniejszą popularność.

Oba systemy straciły na znaczeniu, gdy współczesne technologie sieciowe zdominowały architekturę systemów rozproszonych. MCP i A2A to środowiska uruchomieniowe roku 2026.

### Dlaczego FIPA straciła na znaczeniu

- **Narzut związany z ontologią.** FIPA wymagała wspólnej ontologii do analizy pola `content`. Uzgadnianie ontologii to wieloletni proces standaryzacji. W sieci WWW postawiono po prostu na HTTP + JSON.
- **Nikt nie stosował semantyki formalnej.** SL (Semantic Language) definiował rygorystyczne warunki logiczne, ale większość systemów produkcyjnych i tak przesyłała treść w dowolnej formie, ignorując formalizm.
- **Blokada narzędziowa.** JADE działało tylko w Javie, a JACK był oprogramowaniem komercyjnym. Zespoły korzystające z wielu języków programowania unikały obu tych rozwiązań.
- **Protokoły sieciowe przejęły transport.** REST, JSON-RPC, a później gRPC zastąpiły transport ACL.

### Odrodzenie LLM to w gruncie rzeczy „FIPA-lite”

Porównaj FIPA `request` z MCP `tools/call`:

```
(request                                {
  :sender  agent1                         "jsonrpc": "2.0",
  :receiver tool-server                   "method":  "tools/call",
  :content "(lookup stock IBM)"           "params":  {"name":"lookup_stock",
  :ontology finance                                   "arguments":{"symbol":"IBM"}},
  :conversation-id c42                    "id": 42
)                                        }
```

Ta sama koncepcja, inna składnia. Oba zapisy określają nadawcę, odbiorcę, intencję, ładunek oraz identyfikator korelacji. Żadne z nich nie jest rewolucją w stosunku do drugiego — stanowią po prostu inne kompromisy projektowe.

Badanie przeprowadzone w 2025 r. przez Liu i in. („A Survey of Agent Interoperability Protocols: MCP, ACP, A2A, ANP”, arXiv:2505.02279) wyraźnie wskazuje tę zależność: MCP odpowiada aktom mowy wykorzystującym narzędzia, A2A to akty mowy w relacjach partnerskich (peer-to-peer), ACP skupia się na aktach mowy ze ścieżką audytu, a ANP rozszerza tożsamość o zdecentralizowane mechanizmy. Nowe specyfikacje to w gruncie rzeczy uproszczone wersje ACL opaste na formacie JSON i charakteryzujące się luźniejszą semantyką.

### Podsumowanie kompromisów

**Co oferowała FIPA, a czego brakuje współczesnym specyfikacjom:**

- Semantyka formalna — pozwalała udowodnić logicznie, że nadawca wysyłający `inform` rzeczywiście wierzy w prawdziwość przekazywanej treści.
- Kanoniczny katalog performatywów — eliminował potrzebę ciągłego zastanawiania się: „czy powinniśmy dodać obsługę `cancel`?”.
- Dziesięciolecia sprawdzonych wzorców interakcji (sieć kontraktowa, subskrypcja, propozycja-akceptacja) o znanych właściwościach poprawności logicznej.

**Co oferują współczesne specyfikacje, czego nie miała FIPA:**

- Ładunki natywne w formacie JSON, bezpośrednio kompatybilne z nowoczesnymi narzędziami i bibliotekami.
- Treść w języku naturalnym, którą modele LLM mogą interpretować bez ręcznego definiowania skomplikowanych ontologii.
- Standardowy transport sieciowy (HTTP, SSE, WebSocket).
- Dynamiczne wykrywanie możliwości poprzez dokumenty samoopisujące (np. MCP `listTools`, karta agenta A2A).

Ceną za łatwiejszą implementację jest luźniejsza semantyka intencji. Na tym polega ten kompromis.

### Protokoły interakcji, które warto zaadaptować

FIPA dostarczyła około 15 protokołów interakcji. Trzy z nich warto przenieść bezpośrednio do systemów wieloagentowych LLM:

1. **Contract Net Protocol (CNP).** Menedżer wysyła `cfp` (zaproszenie do składania ofert); oferenci odpowiadają za pomocą `propose`; menedżer akceptuje lub odrzuca ofertę. To klasyczny wzorzec rynku zadań (faza 16 · 16 negocjacji).
2. **Subskrybuj/Powiadom (Subscribe/Notify).** Subskrybent wysyła `subscribe`, a wydawca wysyła `inform` przy każdej zmianie stanu. Na tym opiera się każda szyna zdarzeń (event bus) w 2026 roku.
3. **Zapytanie-Kiedy (Query-When).** „Wykonaj X, gdy zostanie spełniony warunek Y.” Opóźnione działanie z warunkami wstępnymi. Odpowiednikiem w roku 2026 są zadania odroczone w trwałych silnikach przepływu pracy (faza 16 · 22 skalowanie produkcji).

Każdy z tych wzorców bezpośrednio mapuje się na nowoczesne kolejki komunikatów, odpytywanie (polling) HTTP lub przesyłanie strumieniowe SSE.

### Co się psuje, gdy porzucisz ontologię

Bez wspólnej ontologii agenci muszą wnioskować o znaczeniu na podstawie języka naturalnego. Powszechnym problemem w roku 2026 jest **dryf semantyczny**: dwóch agentów używa tego samego słowa (`"customer"`) w nieznacznie różnych znaczeniach, agent odbiorcy działa na podstawie błędnej interpretacji i żaden walidator schematu tego nie wyłapuje. Formalna ontologia FIPA pozwalała odrzucić takie komunikaty już na etapie parsowania.

Sposoby na ograniczenie dryfu bez przechodzenia do pełnej ontologii:

- Schematy JSON dla pola `content` — pozwalają odrzucać błędy strukturalne na poziomie protokołu.
- Typowane artefakty (A2A) — zapobiegają błędom modalności danych.
- Wyraźne performatywy w kopercie wiadomości — czynią intencję jednoznaczną, nawet jeśli sama treść jest zapisana językiem naturalnym.

### Specyfikacje na rok 2026 w odniesieniu do aktów mowy FIPA

| Nowoczesna specyfikacja | Analog FIPA | Co zostaje zachowane | Co zostaje odrzucone |
|---|---|---|---|
| MCP `tools/call` | `request` | wyraźna intencja, identyfikator korelacji | semantyka formalna, ontologia |
| MCP `resources/read` | `query-ref` | wyraźna intencja, identyfikator korelacji | semantyka formalna |
| Cykl życia zadania A2A | Contract Net + Request-When | asynchroniczny cykl życia, przejścia stanów | formalne gwarancje kompletności |
| Wydarzenia strumieniowe A2A | Subscribe/Notify | asynchroniczne wypychanie (push) | subskrypcja z predykatem typu |
| Wspólny kontekst CA-MCP | Tablica (Blackboard - Hayes-Roth 1985) | pamięć współdzielona z wieloma zapisami | model spójności logicznej |
| NLIP | Treści w języku naturalnym | bezpośrednie przetwarzanie przez LLM | schemat struktury |

Główny wniosek z powyższej tabeli jest następujący: zachować podstawy strukturalne, odrzucić formalizm i pozwolić modelom LLM radzić sobie z niejednoznacznością.

## Zbuduj to

W pliku `code/main.py` znajduje się implementacja parsera/tłumacza FIPA-ACL napisanego w czystym Pythonie (biblioteka standardowa). Koduje on i dekoduje kanoniczną kopertę ACL oraz pokazuje, jak wiadomości w formatach MCP/A2A sprowadzają się do tych samych siedmiu pól. Wersja demonstracyjna:

- Koduje pięć wiadomości w stylu MCP i A2A jako komunikaty FIPA-ACL.
- Dekoduje FIPA-ACL z powrotem do współczesnych formatów.
- Prowadzi uproszczone negocjacje w sieci kontraktowej (Contract Net) pomiędzy jednym menedżerem a trzema oferentami przy użyciu performatywów `cfp`, `propose`, `accept-proposal` i `reject-proposal`.

Uruchomienie:

```
python3 code/main.py
```

Dane wyjściowe pokazują równoległe śledzenie każdego nowoczesnego komunikatu w formacie JSON 2026 oraz jako FIPA-ACL, a także przebieg ofert w protokole Contract Net. Podstawowe elementy protokołu pozostają niezmienne; różni się wyłącznie składnia zapisu.

## Użyj tego

W pliku `outputs/skill-fipa-mapper.md` zdefiniowano umiejętność, która analizuje specyfikację dowolnego nowego protokołu agentowego i tworzy jego mapowanie na FIPA-ACL. Użyj jej przed wdrożeniem nowego protokołu, aby odpowiedzieć na pytanie: „Czy to naprawdę coś nowego, czy tylko performatyw `inform` zapisany w JSON?”.

## Wyślij to

Nie przywracaj samego formatu FIPA-ACL. Wykorzystaj jednak jego listę kontrolną przy projektowaniu systemów:

- Jaka jest pierwotna intencja (performatyw) każdego komunikatu?
- Czy istnieje identyfikator korelacji powiązany z mechanizmem żądanie-odpowiedź i anulowaniem?
- Czy określono format i język treści (JSON-RPC, zwykły tekst, strukturyzowany artefakt)?
- Czy protokoły interakcji są zdefiniowane na najwyższym poziomie, czy piszesz sieć kontraktową od zera?
- Co się dzieje, gdy dwóch agentów różnie interpretuje treść (dryf semantyczny)?

Odpowiedz na te pięć pytań przy projektowaniu każdego nowego protokołu przed wdrożeniem go na produkcję.

## Ćwiczenia

1. Uruchom `code/main.py`. Przeanalizuj proces kodowania i dekodowania. Określ, które performatywy FIPA odpowiadają `tools/call`, `resources/read` oraz tworzeniu zadań w A2A.
2. Rozszerz demonstrację sieci kontraktowej o performatyw `cancel`, pozwalający menedżerowi wycofać zadanie w trakcie zbierania ofert. Jaki problem obsługi błędów rozwiązuje `cancel`, którego nie da się obsłużyć samymi ponownymi próbami (retries)?
3. Przeczytaj sekcje 4.1–4.3 specyfikacji struktury komunikatów FIPA ACL (http://www.fipa.org/specs/fipa00037/). Wybierz jeden performatyw niewymieniony w tej lekcji i opisz jego współczesny odpowiednik w standardzie JSON-RPC.
4. Przeczytaj publikację Liu i in., arXiv:2505.02279. Dla każdego z protokołów (MCP, A2A, ACP, ANP) wypisz, które rodziny performatywów FIPA są zachowywane, a które odrzucane.
5. Zaprojektuj minimalny schemat JSON dla pola `content` performatywu `request` we własnym systemie. Co daje taki schemat w porównaniu do czystego języka naturalnego i jaki wiąże się z nim koszt?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Akt mowy (Speech Act) | „Wypowiedź, która coś realizuje” | Koncepcja Austina/Searle'a traktująca wypowiedzi jako czyny. Podstawa teoretyczna dla ACL. |
| FIPA | „Stary standard XML” | IEEE Foundation for Intelligent Physical Agents. Organizacja, która standaryzowała ACL w 2000 roku. |
| ACL | „Język komunikacji agentów” | Format koperty FIPA: performatyw + treść + metadane. |
| Performatyw | „Czasownik wiadomości” | Klasa intencji komunikatu: `inform`, `request`, `propose`, `cfp` itp. |
| KQML | „Poprzednik FIPA” | Knowledge Query and Manipulation Language (1993). Prostszy, węższy protokół. |
| Ontologia | „Wspólny słownik” | Formalna definicja pojęć, do których odnosi się treść wiadomości. |
| SL0 / SL1 | „Języki treści FIPA” | Semantic Language poziomu 0 i 1 — rodzina formalnych języków zapisu treści. |
| Sieć kontraktowa (Contract Net) | „Rynek zadań” | Protokół interakcji: menedżer wysyła cfp, oferenci składają propozycje (propose), menedżer wybiera ofertę. |
| Protokół interakcji | „Wzór komunikacji” | Sekwencja komunikatów o zdefiniowanym przepływie (np. request-when, subscribe-notify). |

## Dalsze czytanie

- [Liu i in. — Ankieta dotycząca protokołów interoperacyjności agentów: MCP, ACP, A2A, ANP](https://arxiv.org/html/2505.02279v1) — przekrojowy przegląd z 2025 roku łączący nowoczesne specyfikacje z dziedzictwem FIPA.
- [Specyfikacja struktury komunikatów FIPA ACL (fipa00037)](http://www.fipa.org/specs/fipa00037/) — oficjalna specyfikacja koperty z 2000 roku.
- [Specyfikacja biblioteki aktów komunikacyjnych FIPA (fipa00037)](http://www.fipa.org/specs/fipa00037/) — kompletny katalog performatywów.
- [Specyfikacja MCP 25.11.2025](https://modelcontextprotocol.io/specification/2025-11-25) — współczesny odpowiednik `request`/`query-ref`.
- [Specyfikacja A2A](https://a2a-protocol.org/latest/specification/) — współczesny odpowiednik sieci kontraktowej i subskrypcji.
