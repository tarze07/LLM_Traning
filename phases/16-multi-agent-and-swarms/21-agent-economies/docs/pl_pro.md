# Ekonomia agentów, tokeny motywacyjne i reputacja

> Autonomiczni agenci działający w długich horyzontach czasowych (zgodnie z testami METR, mierzącymi zadania od 1 do 8 godzin) wymagają własnej podmiotowości ekonomicznej. Wyłaniający się **5-warstwowy stos technologiczny** (5-layer stack) obejmuje: **DePIN** (zdecentralizowana infrastruktura fizyczna) → **Tożsamość** (identyfikatory W3C DID + kapitał reputacji) → **Poznanie** (silnik LLM + RAG + MCP) → **Rozliczenia** (abstrakcja konta / account abstraction) → **Zarządzanie** (agentyczne DAO). Do kluczowych sieci motywacyjnych wdrożonych produkcyjnie zaliczają się **Bittensor** (w którym podsieci nagradzają tokenami TAO modele wyspecjalizowane w konkretnych zadaniach), **Fetch.ai / ASI Alliance** (wykorzystujący model ASI-1 Mini LLM oraz token FET) oraz **Gonka** (który stosuje oparty na transformatorach mechanizm Proof-of-Work do alokacji mocy obliczeniowej na produktywne zadania AI). W literaturze akademickiej: zdecentralizowany framework LaMAS (AAMAS 2025) wykorzystuje **atrybucję opartą na wartości Shapleya** do sprawiedliwego nagradzania agentów za ich wkład w realizację zadań; z kolei zespół Google Research w pracy „Mechanism Design for Large Language Models” proponuje **aukcje tokenowe drugiej ceny** z zachowaniem monotonicznej agregacji. W tej lekcji zbudujesz uproszczony rynek agentowy, zaimplementujesz podział nagród oparty na wartości Shapleya dla potoku wieloagentowego oraz przeprowadzisz aukcję drugiej ceny, co pozwoli na praktyczne przetestowanie mechanizmów teorii gier.

**Typ:** Ucz się
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 16 (Negocjacje i targowanie się), Faza 16 · 09 (Równoległe sieci roju)
**Czas:** ~75 minut

## Problem

Projektowanie systemów wieloagentowych staje się skomplikowane w sytuacjach, gdy agenci wspólnie wypracowują zysk, ale muszą zostać nagrodzeni indywidualnie. Klasyczne podejścia – takie jak równy podział zysków czy model „zwycięzca bierze wszystko” – są niesprawiedliwe i podatne na manipulacje (gameable). Podział zysków oparty na teorii gier kooperacyjnych z użyciem wartości Shapleya gwarantuje sprawiedliwość, lecz jest bardzo kosztowny obliczeniowo. Publikacje z lat 2025–2026 proponują praktyczne kompromisy: próbkowanie wartości Shapleya (Shapley sampling), aukcje oparte na monotonicznej agregacji oraz weryfikowalną reputację on-chain wyliczaną na podstawie udokumentowanego wkładu.

Poza kwestią podziału nagród, rynek dynamicznie rozwija się w kierunku pełnej samodzielności ekonomicznej agentów: Bittensor (TAO) nagradza minerów za dostarczanie wyspecjalizowanych modeli w ramach podsieci, Fetch.ai/ASI umożliwia opłacanie wnioskowania modelu ASI-1 Mini LLM za pomocą tokenów FET, a Gonka wdraża dowód pracy (Proof-of-Work) oparty na operacjach na transformatorach, zaprzęgając moc obliczeniową do realnych zadań AI. Autonomiczni agenci realizujący transakcje finansowe są już rzeczywistością; kluczowym wyzwaniem pozostaje właściwe zaprojektowanie systemów motywacyjnych.

W tej lekcji potraktujemy ekonomię agentów jako zbiór trzech konkretnych zagadnień: podziału nagród (credit assignment), projektowania mechanizmów (mechanism design) oraz zarządzania reputacją. Każde z nich przeanalizujemy od strony matematycznej, aby ugruntować te koncepcje.

## Koncepcja

### Pięciowarstwowy stos technologiczny ekonomii agentów

1. **DePIN (Infrastruktura fizyczna):** zdecentralizowana sieć dostawców mocy GPU, pamięci dyskowej i przepustowości (np. podsieci Bittensor, Render Network, Akash). Nie jest to komponent dedykowany dla konkretnego agenta, ale stanowi dla nich bazowe środowisko uruchomieniowe.
2. **Tożsamość (Identity):** zdecentralizowane identyfikatory W3C (Decentralized Identifiers – DID) zapewniające agentom trwałą tożsamość niezależną od dostawców chmurowych. Reputacja agenta jest bezpośrednio przypisana do jego DID. Protokół Agent Network Protocol (ANP) wykorzystuje DID jako warstwę wyszukiwania i autoryzacji.
3. **Poznanie (Cognition):** pętla wnioskowania agenta: model LLM + RAG + protokół MCP. To kluczowe elementy systemu tworzone w pozostałych fazach nauki.
4. **Rozliczenia (Settlement):** abstrakcja konta (np. standard ERC-4337) umożliwiająca agentom pokrywanie kosztów transakcyjnych (gas) bezpośrednio z ich własnych sald kryptowalutowych, bez konieczności bezpośredniego posiadania ETH przez użytkownika. Ułatwia to mikropłatności między agentami.
5. **Zarządzanie (Governance):** agentyczne DAO – struktury decyzyjne, w których ludzie oraz autonomiczni agenci wspólnie głosują nad zmianami w protokołach, a siła głosu jest często skorelowana z poziomem wypracowanej reputacji.

Nie każdy system produkcyjny korzysta ze wszystkich pięciu warstw. Bittensor opiera się na warstwach 1 i 2, częściowo wykorzystując 3 i 4, natomiast całkowicie pomija 5. Agenci w ekosystemie OpenAI korzystają wyłącznie z warstwy 3. Przedstawiony stos to model referencyjny, a nie sztywne wymaganie.

### Wdrożenia rynkowe: Bittensor, Fetch.ai, Gonka

**Bittensor (TAO):** podsieci są zoptymalizowane pod kątem konkretnych zadań (np. generowanie tekstu, obrazów, prognozowanie finansowe). Minerzy dostarczają wyniki działania swoich modeli, a walidatorzy oceniają ich jakość. Dystrybucja nagród w tokenach TAO opiera się na punktacji ważonej wielkością zabezpieczenia (stake-weighted scoring). Kluczowy wniosek: system płaci za jakość wygenerowanych danych (output) dopasowaną do specyfiki zadania, a nie za sam fakt zużycia mocy obliczeniowej.

**Fetch.ai / ASI Alliance:** model ASI-1 Mini LLM działa bezpośrednio w sieci Fetch.ai; opłaty za zapytania (wnioskowanie) są pobierane w tokenach FET. W tym ekosystemie bardzo silnie zarysowana jest koncepcja agentów jako równorzędnych podmiotów gospodarczych (peer-to-peer): agent może zlecić wykonanie podzadania innemu agentowi w sieci i automatycznie rozliczyć się z nim w tokenach FET.

**Gonka:** realizuje koncepcję Proof-of-Work (PoW) opartą na operacjach na transformatorach. „Praca” (work) polega na wykonywaniu przejść w przód (forward passes) modeli językowych. Minerzy uzyskują nagrody za realizację zadań wnioskowania o znanych, referencyjnych wynikach (pochodzących ze zbiorów treningowych). Jest to mechanizm PoW oparty na użytecznej alokacji zasobów obliczeniowych, w przeciwieństwie do tradycyjnego PoW opartego na bezużytecznym haszowaniu.

Wszystkie trzy projekty osiągnęły dojrzałość produkcyjną w 2026 roku, jednak różnią się sposobem dystrybucji środków. Bittensor nagradza jakość wyjścia ocenianą przez walidatorów podsieci, Fetch.ai opiera się na bezpośrednich opłatach od użytkowników, a Gonka nagradza za dostarczenie matematycznie weryfikowalnych obliczeń.

### Podział nagród za pomocą wartości Shapleya

Załóżmy, że trzech agentów współpracuje przy realizacji jednego projektu, a końcowy rezultat uzyskuje ocenę 0,8. Jak sprawiedliwie ocenić wkład każdego z nich?

Wartość Shapleya to jedyny matematyczny sposób podziału nagrody, który spełnia cztery podstawowe aksjomaty teorii gier kooperacyjnych (efektywność, symetria, liniowość oraz gracz zerowy). Wkład agenta `i` wylicza się ze wzoru:

```
shapley(i) = (1/N!) * sum over all orderings O of (v(S_i_O ∪ {i}) - v(S_i_O))
```

Gdzie `S_i_O` reprezentuje zbiór agentów, którzy znaleźli się przed agentem `i` w danej permutacji (kolejności) `O`. W praktyce proces ten polega na wygenerowaniu wszystkich możliwych permutacji kolejności graczy, obliczeniu wkładu krańcowego (marginal contribution) każdego agenta w każdym scenariuszu i wyciągnięciu średniej z tych wartości.

Dla N=3 agentów musimy przeanalizować tylko 6 permutacji. Jednak dla N=10 liczba permutacji rośnie do ponad 3,6 miliona. Z tego powodu w rzeczywistych systemach stosuje się próbkowanie stochastyczne (Shapley sampling) zamiast pełnego wyliczania wszystkich kombinacji.

### Aukcje drugiej ceny in agregacji wyników

Naukowcy z Google Research (w pracy „Mechanism Design for Large Language Models”) proponują wykorzystanie aukcji drugiej ceny (Vickreya) do agregowania wyników generowanych przez różne modele LLM. Scenariusz: N agentów składa oferty na wykonanie zadania, wyceniając je na podstawie własnych kosztów (wartości prywatnych). Organizator aukcji wybiera ofertę o najwyższej deklarowanej użyteczności, ale rozlicza się ze zwycięzcą po **drugiej najwyższej cenie**. Przy założeniu monotonicznej agregacji (gdzie końcowy zysk rośnie wraz z jakością wybranego rozwiązania) mechanizm ten gwarantuje zgodność z prawdą (truthfulness) – agentom najbardziej opłaca się licytować zgodnie ze swoimi rzeczywistymi kosztami.

Dlaczego jest to przydatne w systemach LLM: pozwala na zlecanie zadań wielu agentom o różnych kosztach operacyjnych. Mechanizm aukcyjny wybiera najlepsze jakościowo rozwiązanie, gwarantuje uczciwą zapłatę i eliminuje pokusę manipulowania ofertami cenowymi przez agentów.

### Kapitał reputacji (Reputation Capital)

Wskaźnik reputacji jest na stałe przypisany do tożsamości DID agenta i aktualizowany na podstawie oceny dostarczanych przez niego wyników według wzoru:

```
rep(i, t+1) = alpha * rep(i, t) + (1 - alpha) * contribution_quality(i, t)
```

Gdzie współczynnik retencji (decay factor) `alpha` ma wartość bliską 1. Tak zaprojektowana reputacja:

- **Jest tania w odczycie** podczas podejmowania decyzji o routingu (np. „kieruj skomplikowane zapytania wyłącznie do agentów o wysokiej reputacji”).
- **Jest trudna do sfałszowania** (wymaga czasu i sukcesywnego budowania wiarygodności, będąc trwale przypisaną do DID).
- **Może podlegać karom (slashing):** wykrycie błędnego lub celowo wprowadzającego w błąd wkładu skutkuje gwałtownym obniżeniem wskaźnika reputacji.

### Decentralizacja LaMAS (AAMAS 2025)

Projekt LaMAS (Large-scale Multi-Agent Systems) zaprezentowany na AAMAS 2025 łączy zdecentralizowaną tożsamość DID, podział nagród oparty na wartości Shapleya oraz mechanizmy aukcyjne. Kluczowy wniosek: decentralizacja procesu podziału zysków sprawia, że system jest łatwy w audytowaniu oraz odporny na manipulacje ze strony pojedynczych, dominujących węzłów.

### Kiedy mechanizmy rynkowe zawodzą (tryby awarii)

- **Manipulowanie funkcją oceny (oracle exploitation):** jeśli funkcja wyliczająca wartość wkładu posiada luki, agenci szybko nauczą się je wykorzystywać. Każdy algorytm wyceny wymaga weryfikacji pod kątem podatności na nadużycia.
- **Ataki Sybil:** jeden podmiot może uruchomić N fałszywych agentów w celu sztucznego zawyżenia swojego udziału w projekcie. Zdecentralizowana tożsamość DID utrudnia ten proceder, ale go nie eliminuje. Główną barierą staje się tu konieczność poniesienia kosztów na wypracowanie reputacji.
- **Koszt weryfikacji (verification cost):** rzetelność podziału zysków zależy od jakości weryfikatora. Tani proces weryfikacji (np. małym modelem LLM) jest podatny na manipulacje, natomiast drogi (np. z udziałem panelu ekspertów) drastycznie ogranicza skalowalność systemu.
- **Uwarunkowania prawne:** agentyczne rynki ekonomiczne wchodzą w interakcję z przepisami finansowymi. W 2026 roku platformy takie jak Bittensor, Fetch czy Gonka wciąż mierzą się z niejednoznacznością przepisów prawnych w niektórych jurysdykcjach.

### Kiedy warto wdrażać mechanizmy ekonomiczne

- **W otwartych sieciach o heterogenicznej strukturze właścicielskiej:** gdy agenci należą do różnych podmiotów i brak jest centralnego zarządcy.
- **Przy weryfikowalnych wynikach:** gdy jakość pracy da się obiektywnie zmierzyć.
- **W długoterminowych procesach przepływu pracy:** zadania jednorazowe nie zyskują na obecności systemów reputacyjnych.
- **Gdy transakcje tokenowe są zgodne z lokalnymi regulacjami prawnymi.**

W zamkniętych systemach wewnątrzfirmowych tradycyjne mechanizmy rynkowe zazwyczaj ustępują miejsca prostszym metodom alokacji (centralny przydział zadań, wewnętrzne wskaźniki wydajności). Zaawansowane mechanizmy ekonomiczne są domeną sieci otwartych.

## Zbuduj to

Skrypt `code/main.py` implementuje:

- `shapley(value_fn, agents)` – dokładne wyliczanie wartości Shapleya poprzez pełną permutację dla małych wartości N.
- `second_price_auction(bids)` – mechanizm aukcji Vickreya, w którym zwycięzca płaci drugą najwyższą stawkę.
- `Reputation` – klasę obsługującą reputację przypisaną do DID z wykładniczym zanikiem oraz mechanizmem kar (slashing).
- Scenariusz 1: kooperacja trzech agentów ze sprawiedliwym podziałem nagrody za pomocą wartości Shapleya.
- Scenariusz 2: pięciu agentów licytuje udział w zadaniu; aukcja drugiej ceny wybiera zwycięzcę i określa wysokość zapłaty.
- Scenariusz 3: symulacja 100 rund przydziału zadań do agentów o zróżnicowanej charakterystyce; routing zapytań uwzględniający reputację przewyższa routing losowy.

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik: wartości Shapleya obliczone dla poszczególnych agentów; logi z aukcji pokazujące zachowanie równowagi (szczere licytowanie); porównanie wykazujące 10-20% wzrost jakości routingu opartego na reputacji w zestawieniu z wyborem losowym po zakończeniu fazy początkowej.

## Użyj tego

Plik `outputs/skill-economy-designer.md` zawiera projekt uproszczonej ekonomii agentowej: definiuje warstwę tożsamości, metodę podziału nagród, mechanizmy płatnicze oraz reguły zarządzania reputacją.

## Wdrożenie produkcyjne

Wskazówki dotyczące wdrażania mechanizmów rynkowych w systemach agentowych:

- **Zacznij od wskaźników reputacji, a nie od tokenów.** Systemy reputacji są znacznie prostsze we wdrożeniu i generują realną wartość użytkową bez wprowadzania problemów prawno-podatkowych związanych z emisją tokenów.
- **Weryfikuj przed nagrodzeniem.** Nigdy nie przydzielaj nagród wyłącznie na podstawie deklaracji agenta o jakości wykonanej przez niego pracy. Brak niezależnej weryfikacji szybko doprowadzi do nadużyć i ataków Sybil.
- **Stosuj próbkowanie wartości Shapleya.** W rzeczywistych wdrożeniach próbkuj od 100 do 1000 permutacji; pełne wyliczanie wartości Shapleya nie skaluje się przy większej liczbie agentów.
- **Dobierz optymalne parametry parowania reputacji.** Zbyt szybkie zerowanie reputacji zniechęca stałych, rzetelnych dostawców; zbyt powolne sprawia, że system nagradza agentów o przestarzałym profilu działania.
- **Przeprowadzaj audyty podatności mechanizmów (red-teaming).** Przed upublicznieniem sieci poddaj mechanizmy rynkowe testom bezpieczeństwa pod kątem prób manipulacji cenowych i strategicznej gry. Chcesz wykryć luki w teorii gier na etapie projektowania, a nie po wdrożeniu.

## Ćwiczenia

1. Uruchom `code/main.py`. Zweryfikuj, czy suma wartości Shapleya poszczególnych agentów odpowiada wartości globalnej (aksjomat efektywności). Zmodyfikuj kryteria funkcji oceniającej wkład i przeanalizuj, czy alokacja nagród zmienia się zgodnie z oczekiwaniami.
2. Zaimplementuj próbkowanie stochastyczne wartości Shapleya (metoda Monte Carlo z określoną liczbą prób K). Jak wielkość parametru K wpływa na błąd aproksymacji? Zrób porównanie z wynikami dokładnymi dla N=4.
3. Rozbuduj mechanizm aukcyjny o możliwość budowania koalicji: agenci mogą łączyć się w grupy i składać wspólne oferty. Jakie zespoły się zawiązują? Czy końcowy podział jest optymalny w sensie Pareto w porównaniu do ofert indywidualnych?
4. Przeczytaj wpis Google Research na temat projektowania mechanizmów (mechanism design). Wskaż jedno założenie, którego niespełnienie narusza regułę szczerości ofert. Jak ten błąd objawia się w systemie opartym na modelach LLM?
5. Przeczytaj publikację LaMAS z AAMAS 2025. Spróbuj wyliczyć dokładne wartości Shapleya dla populacji 10 agentów w syntetycznym zadaniu. Ile czasu zajmują te obliczenia? Porównaj uzyskany wynik z próbkowaniem opartym na 100 losowych permutacjach.

## Kluczowe terminy

| Termin | Co się potocznie mówi | Co to właściwie oznacza |
|---|---|---|
| DePIN (Decentralized Physical Infrastructure Networks) | „Zdecentralizowana infrastruktura” | Rozliczane w tokenach sieci dostawców mocy obliczeniowej GPU, dysków i łączy (np. Bittensor, Akash, Render Network). |
| DID (Decentralized Identifier) | „Zdecentralizowana tożsamość” | Standard W3C określający niezależne tożsamości cyfrowe. Reputacja agenta jest powiązana z jego identyfikatorem DID, a nie z dostawcą platformy. |
| ERC-4337 | „Abstrakcja konta” | Standard Ethereum umożliwiający tworzenie portfeli inteligentnych kontraktów, które pozwalają agentom na automatyczne opłacanie transakcji. |
| Wartość Shapleya (Shapley Value) | „Sprawiedliwy podział nagrody” | Koncepcja z kooperacyjnej teorii gier określająca optymalny i sprawiedliwy podział nagród w zespole. |
| Aukcja drugiej ceny (Vickrey Auction) | „Aukcja z ceną drugiego oferenta” | Mechanizm licytacji, w którym zwycięzca płaci stawkę zadeklarowaną przez drugą w kolejności ofertę, co zachęca do szczerości ofert. |
| Kapitał reputacji (Reputation Capital) | „Wskaźnik reputacji” | Przypisana do DID ocena jakości wkładu agenta w realizację zadań, podlegająca stopniowemu parowaniu w czasie. |
| Agentyczne DAO (Agentic DAO) | „DAO zarządzane przez agenty” | Zdecentralizowane organizacje, w których agenci posiadają równe z ludźmi prawa decyzyjne, a ich siła głosu zależy od wypracowanej reputacji. |
| TAO / FET | „Tokeny agentowe” | Natywne tokeny ekosystemów odpowiednio Bittensor oraz Fetch.ai / ASI Alliance. |

## Dalsze czytanie

- [Gospodarka agentów](https://arxiv.org/abs/2602.14219) – przegląd badań z 2026 roku nad 5-warstwowym stosem ekonomicznym systemów agentowych
- [Google Research – Mechanism Design for Large Language Models](https://research.google/blog/mechanism-design-for-large-language-models/) – zastosowanie aukcji Vickreya w agregacji wyników modeli językowych
- [AAMAS 2025 – Zdecentralizowany LaMAS](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p2896.pdf) – atrybucja nagród za pomocą wartości Shapleya w systemach wieloagentowych
- [Dokumentacja Bittensor TAO](https://docs.bittensor.com/) – specyfikacja techniczna podsieci oraz dystrybucji nagród
- [Fetch.ai / ASI Alliance](https://fetch.ai/) – informacje o integracji modelu ASI-1 Mini LLM oraz tokenie FET
- [Specyfikacja zdecentralizowanych identyfikatorów W3C (DID)](https://www.w3.org/TR/did-core/) – oficjalny standard tożsamości DID
