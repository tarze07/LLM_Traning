# Dziedzictwo FIPA-ACL i aktów mowy

> Przed MCP, przed A2A, istniała FIPA-ACL. W 2000 roku Fundacja IEEE na rzecz Inteligentnych Agentów Fizycznych ratyfikowała język komunikacji agentów składający się z dwudziestu performatywów, dwóch języków treści i zestawu protokołów interakcji — sieć kontraktowa, subskrybuj/powiadamiaj, żądaj kiedy. Zniknęło z przemysłu, ponieważ narzut związany z ontologią był zbyt duży dla sieci, ale odrodzenie LLM systemów wieloagentowych po cichu wprowadza te same pomysły bez formalnej semantyki: kontrakty JSON zastępują performatywy, język naturalny za ontologie. W tej lekcji poważnie traktuje się FIPA-ACL, dzięki czemu można zobaczyć, które decyzje dotyczące protokołu na rok 2026 stanowią nowe rozwiązania, które stanowią nowość, a gdzie obecna fala ponownie odkryje problemy, które zostały już rozwiązane w pierwszej dekadzie XXI wieku.

**Typ:** Ucz się
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 01 (Dlaczego wieloagentowy)
**Czas:** ~60 minut

## Problem

Krajobraz protokołów agentów na rok 2026 jest zajęty: MCP dla narzędzi, A2A dla agentów, ACP dla audytu przedsiębiorstwa, ANP dla zdecentralizowanego zaufania, NLIP dla treści w języku naturalnym, a także CA-MCP i dwa tuziny propozycji badawczych. Każda specyfikacja reklamuje się jako podstawowa.

Szczerze mówiąc, większość z nich odkrywa na nowo bardzo specyficzne drzewo decyzyjne sprzed dwudziestu lat. Teoria aktów mowy Austina (1962) i Searle'a (1969) dała nam pogląd, że „wypowiedzi są działaniami”. KQML (1993) przekształcił to w protokół przewodowy. FIPA-ACL (ratyfikowana w 2000 r.) stworzyła standaryzację referencyjną: dwadzieścia performatywów, języki treści SL0/SL1, protokoły interakcji dla sieci kontraktów i powiadamiania o subskrypcji. JADE i JACK były platformami referencyjnymi Java. Wysiłki te osłabły około 2010 roku, ponieważ narzut związany z ontologią był zbyt duży, a sieć wygrywała.

Kiedy patrzysz na `tools/call` MCP, cykl życia zadań A2A lub magazyn kontekstu współdzielonego CA-MCP, widzisz bardziej miękką, natywną wersję JSON decyzji FIPA. Znajomość dziedzictwa mówi dwie rzeczy: które nowe „innowacje” są w rzeczywistości odkryciami na nowo i które stare tryby awarii zostaną ponownie odkryte w nowych specyfikacjach.

## Koncepcja

### Akty mowy w jednym akapicie

Austin zauważył, że niektóre zdania nie opisują świata – one go zmieniają. „Obiecuję.” – Proszę. „Oświadczam”. Nazwał te wypowiedzi performatywne. Searle sformalizował pięć kategorii: asertywna, dyrektywna, komisywna, ekspresyjna, deklaratywna. KQML (Finin i in., 1993) umożliwił to w przypadku agentów oprogramowania: wiadomość składa się z performatywu (działania) plus treść (o co chodzi w działaniu). FIPA-ACL uzupełniła luki w KQML i ujednoliciła około dwudziestu performatywów.

### Dwudziestu performatywów FIPA (częściowa lista)

| Performatywny | Zamiar |
|---|---|
| `inform` | „Mówię ci, że P jest prawdą” |
| `request` | „Proszę Cię o wykonanie X” |
| `query-if` | „Czy P jest prawdą?” |
| `query-ref` | „Jaka jest wartość X?” |
| `propose` | „Proponuję zrobić X” |
| `accept-proposal` | „Przyjmuję propozycję” |
| `reject-proposal` | „Odrzucam propozycję” |
| `agree` | „Zgadzam się zrobić X” |
| `refuse` | „Odmawiam zrobienia X” |
| `confirm` | „Potwierdzam, że P jest prawdą” |
| `disconfirm` | „Zaprzeczam P” |
| `not-understood` | „Twoja wiadomość nie została przeanalizowana” |
| `cfp` | „Nabór wniosków w sprawie X” |
| `subscribe` | „Powiadom mnie, gdy X się zmieni” |
| `cancel` | „Anuluj trwające X” |
| `failure` | „Próbowałem X i nie udało mi się” |

Pełna lista znajduje się w `fipa00037.pdf` (struktura komunikatów FIPA ACL). Nie chodzi o to, aby go zapamiętywać – chodzi o to, że każdy z nich odpowiada prymitywowi, który protokół LLM ostatecznie dodaje ponownie.

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

Kopertę protokołu zawiera siedem pól; jedno pole (`content`) zawiera ładunek. Pozostałe pola są dokładnie tym, co wymyślasz na nowo za każdym razem, gdy łączysz ponowne próby, wątki i ontologię w protokole JSON.

### Dwie starsze platformy

**JADE** (Java Agent DEvelopment Framework, 1999–2020) był najczęściej używanym środowiskiem wykonawczym zgodnym z FIPA. Agenci rozszerzali klasę bazową, wymieniali komunikaty ACL, uruchamiali kontenery i koordynowali działania za pomocą „zachowań”. Biblioteka protokołów interakcji dostarczana z siecią kontraktów, subskrybuj-powiadamiaj, żądaj-kiedy i proponuj-akceptuj.

**JACK** (oprogramowanie zorientowane na agenta, komercyjne) kładł nacisk na rozumowanie BDI (przekonanie-pragnienie-intencja) jako uzupełnienie komunikatów FIPA. Bardziej formalny, mniej przyjęty.

Obydwa spadły, gdy stos sieciowy pochłonął przypadki użycia wielu agentów. MCP i A2A to „kontenery” środowiska uruchomieniowego roku 2026.

### Dlaczego FIPA wyblakła

- **Narzut związany z ontologią.** FIPA wymagała wspólnej ontologii do analizy `content`. Uzgadnianie ontologii to wieloletni proces standaryzacji. W sieci właśnie użyto protokołu HTTP + JSON.
- **Nikt nie stosował semantyki formalnej.** SL (język semantyczny) podał rygorystyczne warunki prawdziwości, ale większość systemów produkcyjnych korzystała z treści w dowolnej formie i ignorowała formalizm.
- **Blokada narzędzi.** JADE działała tylko w Javie; JACK miał charakter komercyjny. Zespoły poliglotów rozchodziły się wokół obu.
- **Internet wygrał stos.** REST, następnie JSON-RPC, a następnie gRPC zastąpiły transport ACL.

### Odrodzenie LLM jest zgodne z FIPA-lite

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

Ta sama koperta, inna składnia. Obydwa zawierają: kto, kto, zamiar, ładunek, identyfikator korelacji. Żadne z nich nie jest rewolucją w stosunku do drugiego — są to różne kompromisy w zakresie tego samego projektu.

Badanie przeprowadzone w 2025 r. przez Liu i in. („A Survey of Agent Interoperability Protocols: MCP, ACP, A2A, ANP”, arXiv:2505.02279) wyraźnie wyjaśnia tę linię: MCP odpowiada aktom mowy wykorzystującym narzędzia, A2A odpowiada aktom mowy agenta-równego, ACP odpowiada aktom mowy ze ścieżką audytu, ANP odpowiada zdecentralizowanym rozszerzeniom tożsamości. Nowe specyfikacje są potomkami listy ACL ze składnią JSON i luźniejszą semantyką.

### Kompromis, jasno określony

**Co dała ci FIPA i spadek nowoczesnych specyfikacji:**

- Semantyka formalna — możesz udowodnić, że `inform` sugeruje, że nadawca wierzy w treść.
- Kanoniczny katalog performatywów — nie trzeba ponownie zastanawiać się, „czy powinniśmy mieć `cancel`?”.
- Dziesięciolecia wzorców protokołów interakcji - sieć kontraktowa, subskrypcja - powiadomienie, propozycja - akceptacja - ze znanymi właściwościami poprawności.

**Co dają nowoczesne specyfikacje, a FIPA nie:**

- Ładunki natywne w formacie JSON kompatybilne z każdym nowoczesnym narzędziem.
- Treści w języku naturalnym, które osoby LLM mogą interpretować bez ręcznie kodowanej ontologii.
- Transport stosu sieciowego (HTTP, SSE, WebSocket).
- Wykrywanie możliwości poprzez dokumenty samoopisujące (MCP `listTools`, karta agenta A2A).

Luźniejsza semantyka intencji dla łatwiejszej implementacji. To jest dokładny handel.

### Protokoły interakcji, które warto przenieść

FIPA dostarczyła ~15 protokołów interakcji. Trzy z nich warto przenieść do systemów wieloagentowych LLM:

1. **Contract Net Protocol (CNP).** Menedżer wystawia `cfp` (zaproszenie do składania wniosków); licytanci odpowiadają `propose`; menadżer akceptuje/odrzuca. Jest to kanoniczny wzorzec rynku zadań (faza 16 · 16 negocjacji).
2. **Subskrybuj/Powiadom.** Abonent wysyła `subscribe`; wydawca wysyła `inform` za każdym razem, gdy zmienia się temat. To jest każdy autobus eventowy w 2026 roku.
3. **Zapytanie-Kiedy.** „Wykonaj X, gdy spełniony jest warunek Y.” Opóźnione działanie z warunkami wstępnymi. Analogiem 2026 są zadania odroczone w trwałych silnikach przepływu pracy (faza 16 · 22 skalowanie produkcji).

Każdy z nich jest bezpośrednio mapowany na nowoczesne kolejki komunikatów, odpytywanie HTTP + lub przesyłanie strumieniowe SSE.

### Co się psuje, gdy porzucisz ontologię

Bez wspólnej ontologii agenci wnioskują o znaczeniu z treści języka naturalnego. Udokumentowany tryb awarii 2026 to **dryf semantyczny**: dwóch agentów używa tego samego słowa (`"customer"`) dla nieznacznie różnych koncepcji, agent odbiorcy działa na podstawie błędnej interpretacji, żaden walidator schematu tego nie wyłapuje. Wymóg ontologii FIPA spowodowałby odrzucenie wiadomości w czasie analizy.

Ograniczenia bez przechodzenia do pełnej ontologii:

- Schemat JSON na `content` — odrzuca błędy strukturalne na przewodzie.
- Artefakty wpisane (A2A) — odrzuca błędną modalność.
- Wyraźny performatywny w kopercie - sprawia, że ​​intencja jest jednoznaczna, nawet jeśli treść jest językiem naturalnym.

### Specyfikacje na rok 2026 odwzorowane na podstawie aktów mowy

| Nowoczesna specyfikacja | Analog FIPA | Co trzyma | Co spada |
|---|---|---|---|
| MCP `tools/call` | `request` | wyraźny zamiar, identyfikator korelacji | semantyka formalna, ontologia |
| MCP `resources/read` | `query-ref` | wyraźny zamiar, identyfikator korelacji | semantyka formalna |
| Cykl życia zadania A2A | umowa-net + żądanie-kiedy | cykl życia asynchronicznego, przejścia stanów | formalne gwarancje kompletności |
| Wydarzenia strumieniowe A2A | subskrybuj/powiadom | asynchroniczne push | subskrypcja z predykatem typu |
| Wspólny kontekst CA-MCP | tablica (Hayes-Roth 1985) | pamięć współdzielona z wieloma zapisami | model spójności logicznej |
| NLIP | treści w języku naturalnym | Natywny LLM | schemat |

Czytając tabelę od góry do dołu, wzór jest następujący: zachowaj prymitywność strukturalną, porzuć formalizm, pozwól LLM zatuszować niejednoznaczność.

## Zbuduj to

`code/main.py` implementuje tłumacz FIPA-ACL oparty na czystym stdlib. Koduje i dekoduje kanoniczną obwiednię ACL i pokazuje, jak każdy kształt wiadomości MCP/A2A sprowadza się do tych samych siedmiu pól. Wersja demonstracyjna:

- Koduje pięć wiadomości w stylu MCP i A2A jako FIPA-ACL.
- Dekoduje FIPA-ACL z powrotem do współczesnego odpowiednika.
- Prowadzi negocjacje dotyczące umowy na zabawki pomiędzy jednym menedżerem a trzema licytantami przy użyciu `cfp`, `propose`, `accept-proposal`, `reject-proposal`.

Uruchom:

```
python3 code/main.py
```

Dane wyjściowe to równoległe śledzenie przedstawiające każdy nowoczesny komunikat zarówno w formacie JSON 2026, jak i w formacie FIPA-ACL, a następnie obydwie oferty w ramach umowy netto. Te same elementy podstawowe protokołu przetrwają podróż w obie strony; różni się tylko składnia.

## Użyj tego

`outputs/skill-fipa-mapper.md` to umiejętność, która odczytuje dowolną specyfikację protokołu agenta i tworzy mapowanie FIPA-ACL. Użyj go przed przyjęciem nowego protokołu, aby odpowiedzieć: „Czy to jest naprawdę nowe, czy jest to `inform` ze składnią JSON?”

## Wyślij to

Nie przywracaj FIPA-ACL. Przywróć listę kontrolną:

- Jaka jest intencja prymitywna (performatywna) każdego komunikatu?
- Czy istnieje identyfikator korelacji dla żądania-odpowiedzi i anulowania?
- Czy istnieje wyraźny język treści (JSON-RPC, zwykły tekst, artefakt o typie strukturalnym)?
- Czy protokoły interakcji są na najwyższym poziomie, czy też wdrażasz sieć kontraktów od zera?
- Co się dzieje, gdy dwóch agentów nie zgadza się co do znaczenia treści (dryf semantyczny)?

Udokumentuj te pięć pytań dotyczących każdego nowego protokołu przed wysłaniem go do produkcji.

## Ćwiczenia

1. Uruchom `code/main.py`. Obserwuj kodowanie w obie strony. Określ, który performatywny FIPA odpowiada `tools/call`, `resources/read` i tworzeniu zadań A2A.
2. Rozszerz demonstrację sieci kontraktowej o performatyw `cancel`, który pozwala menedżerowi wycofać zadanie w połowie oferty. Jaki przypadek niepowodzenia rozwiązuje `cancel`, którego nie rozwiązują same ponowne próby?
3. Przeczytaj strukturę komunikatów FIPA ACL (http://www.fipa.org/specs/fipa00037/) sekcje 4.1–4.3. Wybierz jeden performatywny, który nie jest omówiony w tej lekcji i opisz jego nowoczesny odpowiednik JSON-RPC.
4. Przeczytaj Liu i in., arXiv:2505.02279. Dla każdego z MCP, A2A, ACP, ANP wypisz rodziny performatywne FIPA, które zachowują i usuwają.
5. Zaprojektuj minimalny schemat JSON dla pola `content` performatywu `request` w swoim własnym systemie. Co daje ten schemat, czego nie daje czysty język naturalny, i ile to kosztuje?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Akt mowy | „Wypowiedź, która coś robi” | Austin/Searle: wypowiedzi jako czyny. Teoretyczny rodzic ACL. |
| FIPA | „Ta stara rzecz XML” | Fundacja IEEE na rzecz Inteligentnych Agentów Fizycznych. Standaryzowany ACL w 2000 r. |
| ACL | „Język komunikacji agenta” | Format koperty FIPA: performatywny + treść + metadane. |
| Performatywny | „Czasownik” | Klasa intencji wiadomości: `inform`, `request`, `propose`, `cfp` itd. |
| KQML | „Poprzednik FIPA” | Zapytanie o wiedzę i język manipulacji (1993). Prostsze, węższe. |
| Ontologia | „Wspólne słownictwo” | Formalna definicja pojęć, o których mówi język treści. |
| SL0 / SL1 | „Języki treści FIPA” | Poziomy języka semantycznego 0 i 1 — rodzina języków treści formalnych. |
| Kontrakt Netto | „Rynek zadań” | Menedżer wydaje cfp; oferenci proponują; menadżer akceptuje. Kanoniczny protokół interakcji. |
| Protokół interakcji | „Wzór wiadomości” | Sekwencja performatywów o znanej poprawności: żądanie-kiedy, subskrybowanie-powiadomienie itp. |

## Dalsze czytanie

- [Liu i in. — Ankieta dotycząca protokołów interoperacyjności agentów: MCP, ACP, A2A, ANP](https://arxiv.org/html/2505.02279v1) — kanoniczna ankieta na rok 2025 łącząca nowoczesne specyfikacje z dziedzictwem FIPA
- [Specyfikacja struktury komunikatów FIPA ACL (fipa00037)](http://www.fipa.org/specs/fipa00037/) — ratyfikowany format koperty 2000
- [Specyfikacja biblioteki aktu komunikacyjnego FIPA (fipa00037)](http://www.fipa.org/specs/fipa00037/) — pełny katalog performatywny
- [Specyfikacja MCP 25.11.2025](https://modelcontextprotocol.io/specification/2025-11-25) — nowoczesny odpowiednik `request`/`query-ref`
- [Specyfikacja A2A](https://a2a-protocol.org/latest/specification/) — nowoczesny odpowiednik kontraktu-net i subskrypcji-notify