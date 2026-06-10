# Konsensus i bizantyjska tolerancja błędów (BFT) w systemach wieloagentowych

> Klasyczne protokoły bizantyjskiej tolerancji błędów (BFT) z systemów rozproszonych spotykają się ze stochastycznym charakterem modeli LLM. W okresie 2025–2026 wyłoniły się trzy główne kierunki badawcze: **CP-WBFT** (arXiv:2511.10400), który waży głosy poszczególnych agentów za pomocą wskaźnika pewności (confidence probe); **DecentLLM** (arXiv:2507.14928), czyli architektura bezliderowa, w której agenty-wykonawcy równolegle generują propozycje, a ostateczny wynik wyliczany jest jako mediana geometryczna; oraz **WBFT** (arXiv:2505.05103), łączący głosowanie ważone z hierarchicznym grupowaniem w celu rozdzielenia węzłów rdzeniowych (Core) i brzegowych (Edge). Wnioski płynące z pracy empirycznej „Can AI Agents Agree?” (arXiv:2603.01213) są jednoznaczne: nawet proste porozumienie skalarne (co do wartości liczbowych) jest dziś bardzo podatne na zakłócenia — pojedynczy, celowo wprowadzający w błąd agent (adversarial agent) potrafi całkowcite zaburzyć konsensus w zespole. Klasyczne mechanizmy BFT są niezbędne, lecz niewystarczające. W tej lekcji zaimplementujemy minimalistyczny protokół BFT, przeanalizujemy trzy ataki specyficzne dla systemów agentowych (kłamstwo bizantyjskie, konformizm/potakiwanie, monokulturę skorelowanych błędów) i zbadamy, jak radzą sobie z nimi poszczególne warianty konsensusu.

**Typ:** Ucz się + Buduj
**Języki:** Python (biblioteka standardowa)
**Wymagania wstępne:** Faza 16 · 07 (Społeczeństwo umysłu i debaty), Faza 16 · 13 (Wspólna pamięć)
**Czas:** ~75 minut

## Problem

Masz N agentów LLM, z których każdy udziela odpowiedzi. Nie zgadzają się. Większość głosów wybiera niewłaściwego, ponieważ dwóch z nich popełnia ten sam błąd (ponieważ używają tego samego modelu bazowego, zostały wyszkolone na tych samych danych i posiadają te same cechy awarii). Trzeci agent myli się w zupełnie inny sposób, przez co większość przegłosowuje poprawną odpowiedź.

Teraz rozważ agenta złośliwego (adversarial), który kłamie celowo, lub agenta potakującego (sycophant), który po prostu zgadza się z przedmówcą. W klasycznej teorii BFT zakłada się, że złośliwe węzły stanowią ułamek $f < n/3$ i mogą zachowywać się w sposób całkowicie arbitralny. W rzeczywistości systemów agentowych LLM są stochastyczne (nawet te „uczciwe”), wykazują skorelowane błędy i podatność na wzajemne sugestie. Nie można ich traktować jak niezależnych zmiennych losowych (prób Bernoulliego).

Klasyczny protokół BFT (PBFT, 1999) nie jest błędny — jest po prostu niewystarczający w nowym kontekście. Zaprojektowano go do obsługi przypadkowej zmiany bitów (bit-flipping), a nie sytuacji, w której „trzech uczwiwych agentów ma tę samą halucynację, ponieważ korzysta z tego samego zbioru treningowego”. Ta lekcja bazuje na fundamentach PBFT, adaptując go do realiów systemów wieloagentowych.

## Koncepcja

### Założenia klasycznego BFT

Protokół PBFT (Practical Byzantine Fault Tolerance, Castro i Liskov, OSDI 1999) pozwala na tolerowanie złośliwych węzłów w liczbie $f < n/3$. Składa się z trzech faz (pre-prepare, prepare, commit) oraz bazuje na podpisach cyfrowych i certyfikatach kworum w celu wypracowania konsensusu co do pojedynczej wartości w systemie składającym się z $n \ge 3f + 1$ węzłów.

Gwarancje te są mocne, ale zakładają:

1. **Niezależność błędów.** Złośliwe węzły nie koordynują swoich działań.
2. **Uczciwość węzłów.** Prawdomówność uczciwych węzłów nie podlega dyskusji; protokół jedynie rozstrzyga rozbieżności zdań.
3. **Obiektywna prawda.** Wypracowanie konsensusu co do błędnego faktu wciąż jest traktowane jako sukces protokołu.

Agenty LLM naruszają wszystkie trzy założenia. Dwa modele bazujące na tej samej architekturze wykazują skorelowane błędy. Uczciwy model LLM wciąż może halucynować, a w przypadku pytań otwartych prawda jest pojęciem subiektywnym i nie istnieje żadna zewnętrzna wyrocznia (oracle).

### Trzy ataki specyficzne dla LLM

**Bizantyjskie kłamstwo (Byzantine lie).** Jeden z agentów celowo podaje błędną odpowiedź. Klasyczne BFT radzi sobie z tym pod warunkiem, że $f < n/3$.

**Potakiwanie (Sycophancy).** Agent analizuje wypowiedzi innych przed oddaniem głosu i zgadza się z ostatnim rozmówcą. Nie wynika to ze złej woli, ale tworzy silną korelację z najgłośniejszym lub ostatnim głosem. Klasyczne BFT przed tym nie chroni, ponieważ agent bez problemu przechodzi weryfikację podpisu cyfrowego.

**Monokultura skorelowanych błędów.** Trzej agenci korzystają z tego samego modelu bazowego. Generują tę samą halucynację, przez co większość głosuje na błędną odpowiedź. Klasyczne BFT nie rozwiązuje tego problemu, ponieważ wszyscy trzej agenci w pełni lojalnie i „uczciwie” zgadzają się ze sobą.

### Odpowiedzi na wyzwania (stan na lata 2025–2026)

**CP-WBFT** (arXiv:2511.10400) — wersja BFT z wagami przypisywanymi na podstawie wskaźnika pewności (Confidence-Probe Weighted BFT). Każdy agent dołącza do swojej odpowiedzi szacowany poziom pewności (confidence score — deklarowany przez model lub wyliczany przez zewnętrzny kalibrator). Głosy są ważone z uwzględnieniem tego wskaźnika. Rozwiązanie to wykazuje wzrost odporności BFT o 85,71% w grafach pełnych. Skutecznie ogranicza wpływ potakiwania (agenci ulegający sugestii zazwyczaj deklarują niską pewność swojego stanowiska).

**DecentLLM** (arXiv:2507.14928) — model bezliderowy. Agenty-wykonawcy proponują rozwiązania równolegle, a agenty-ewaluatorzy je oceniają. Ostateczny wynik jest wyliczany jako mediana geometryczna z punktowanych propozycji. Rozwiązanie zachowuje stabilność przy $f < n/2$. Skutecznie zapobiega kłamstwom bizantyjskim i skorelowanym błędom (mediana geometryczna jest odporna na wartości odstające i wskazuje najgęstszy klaster odpowiedzi zamiast prostej średniej).

**WBFT** (arXiv:2505.05103) — ważone BFT z hierarchicznym podziałem struktury. Wagi głosów są przydzielane dynamicznie na podstawie historycznej jakości odpowiedzi oraz deklarowanej pewności. Agenty są dzielone na rdzeń (Core) i brzeg (Edge). Węzły rdzenia muszą najpierw wypracować konsensus, który następnie jest przekazywany do węzłów brzegowych. Rozwiązanie to poprawia skalowalność (konsensus w rdzeniu jest szybki) oraz ogranicza ryzyko monokultury (węzły rdzeniowe mogą być celowo zróżnicowane).

### Wnioski empiryczne: „Can AI Agents Agree?” (arXiv:2603.01213)

W publikacji zbadano spójność skalarną (uzgadnianie wartości liczbowych przez agenty LLM) w różnych wiodących modelach. Wnioski są następujące:

- Nawet w przypadku braku złośliwych agentów (adversaries), modele LLM wykazują brak spójności w zadaniach skalarnych na poziomie przekraczającym 30% w wielu testach porównawczych.
- Wprowadzenie pojedynczego agenta o złośliwym profilu (adversarial persona) potrafi odchylić konsensus grupy o ponad 40 punktów procentowych od poprawnego wyniku bazowego.
- Wskaźnik braku zgody jest skorelowany z heterogenicznością grupy — zespoły zróżnicowane nie zgadzają się częściej (co jest pozytywne, gdyż oznacza nieskorelowane błędy), ale proces wypracowywania konsensusu trwa w nich dłużej.

Podsumowanie: protokoły BFT zapewniają mechanizm uzgadniania wyników, ale nie gwarantują ich poprawności merytorycznej. Dlatego należy łączyć je z weryfikacją (specjalizacja ról z Lekcji 16.08), dywersyfikacją modeli (Lekcja 16.15 na temat debat) oraz dedykowanymi agentami oceniającymi (Lekcja 16.24).

### Uproszczona runda BFT dla agentów LLM:

```
1. task arrives; each agent i produces answer a_i
2. each agent attaches confidence probe c_i in [0, 1]
3. aggregator collects (a_i, c_i) from all n agents
4. aggregator groups by semantic cluster (equivalent answers)
5. aggregator computes weight for each cluster C:
     w(C) = sum_{i in C} c_i
6. winner = cluster with max weight, if max > threshold * sum(c_i)
    else: retry or escalate
7. minority clusters logged with provenance for post-hoc audit
```

Etap grupowania semantycznego jest specyficznym elementem dla systemów LLM. Przykładowo, odpowiedzi „badanie wskazuje na poprawę o 4,2%” oraz „odnotowano wzrost o 4,2%” powinny trafić do tego samego klastra. Zwykłe porównywanie ciągów znaków (string matching) nie wykryłoby tej zbieżności. W środowisku produkcyjnym należy użyć taniego modelu osadzania (embeddings) lub jawnej kanonizacji tekstu.

### Dostrajanie progu akceptacji

Parametr `threshold` decyduje o tym, kiedy wynik zostaje zaakceptowany, a kiedy następuje ponowienie próby. Zbyt niska wartość prowadzi do akceptowania słabej większości. Zbyt wysoka sprawia, że konsensus nigdy nie zostanie osiągnięty. W praktyce stosuje się wartości z zakresu 0,5–0,67 dla grup `n=5-7` agentów (wyższe dla mniejszych grup). W przypadku braku konsensusu sterowanie należy przekazać operatorowi (human-in-the-loop) lub alternatywnej grupie agentów.

### Gdzie mechanizm konsensusu nie pomaga

- **Zapytania niejednoznaczne.** Jeśli zadanie nie ma obiektywnej prawdy (ground truth), konsensus staje się jedynie dominującą opinią.
- **Zadania złożone.** Np. „napisz kod i go wyjaśnij” — wygenerowanie dwóch zróżnicowanych odpowiedzi wymaga niezależnego głosowania nad każdym z tych aspektów.
- **Konflikty wielorundowe.** Gdy agenty mogą observarować odpowiedzi innych uczestników z poprzednich rund i ulegać ich wpływom (jak w pracy Du 2023), szybko dochodzi do konformizmu niezależnie od obiektywnej prawdy. Dlatego należy ograniczać liczbę rund (zazwyczaj do 2-3).

## Zbuduj to

Plik `code/main.py` implementuje:

- `AgentVoter` — konfiguracja agenta z określonymi odpowiedziami i poziomem pewności.
- `MajorityVote` — klasyczny mechanizm większościowy.
- `CPWBFT` — głosowanie ważone pewnością z grupowaniem semantycznym.
- `DecentLLMs` — agregacja mediany geometrycznej dla ocenianych propozycji.
- `Scenario` — uruchomienie symulacji ataku dla każdego z agregatorów.

Zaimplementowane scenariusze ataków:

1. `byzantine`: jeden złośliwy agent z deklarowanym wysokim wskaźnikiem pewności.
2. `sycophancy`: agent potakujący, kopiujący pierwszą zaobserwowaną odpowiedź wraz z jej wskaźnikiem pewności.
3. `monoculture`: trzech agentów generujących tę samą błędną odpowiedź (skorelowany błąd) ze średnim poziomem pewności.

Uruchomienie:

```bash
python3 code/main.py
```

Oczekiwany wynik: tabela (atak, agregator) -> ostateczna odpowiedź z wyróżnioną poprawną wersją. Standardowe głosowanie większościowe (Majority Vote) zawodzi przy monokulturze. Ważenie pewności w CPWBFT skutecznie ogranicza wpływ potakiwania. Z kolei mediana geometryczna w DecentLLM pozwala zbliżyć się do poprawnej odpowiedzi, o ile monokultura błędów obejmuje mniej niż połowę populacji.

## Zastosowanie

Plik `outputs/skill-consensus-designer.md` definiuje procedurę projektowania protokołu konsensusu dla systemów wieloagentowych: metody grupowania, wyznaczanie wag, progi akceptacji oraz procedury eskalacji w sytuacjach podprogowych.

## Wdrożenie produkcyjne

Przed wdrożeniem produkcyjnym dowolnego mechanizmu konsensusu:

- **Przetestuj odporność na co najmniej trzy opisane wyżej scenariusze ataków.** Protokół powinien w takich sytuacjach zgłaszać błędy w kontrolowany sposób, a nie cicho akceptować błędny wynik.
- **Loguj dane wejściowe klastrów mniejszościowych** wraz z ich pochodzeniem. Analiza głosów mniejszościowych stanowi doskonały system wczesnego ostrzegania przed występowaniem skorelowanych błędów.
- **Stosuj sztywne limity rund.** Unikaj schematów „dyskutujcie aż do osiągnięcia porozumienia” — sprzyjają one potakującym zachowaniom.
- **Rozdziel proces wypracowywania konsensusu od walidacji merytorycznej.** Wyjściowy wynik konsensusu powinien być weryfikowany przez niezależnego agenta audytowego, który nie uczestniczył w głosowaniu.
- **Monitoruj wskaźnik zgodności (agreement rate).** Nagły wzrost zgodności może sygnalizować problem potakiwania; nagły spadek może oznaczać dryf modeli.

## Ćwiczenia

1. Uruchom `code/main.py`. Upewnij się, że standardowe głosowanie większościowe zawodzi w scenariuszu monokultury, podczas gdy CPWBFT częściowo go ogranicza, o ile pewność monokultury wynosi poniżej 0,7.
2. Zaimplementuj czwarty typ zachowania: **ciche wstrzymanie się od głosu (silent abstention)** — jeden z agentów zwraca odpowiedź typu „nie wiem”. W jaki sposób każdy z agregatorów powinien obsłużyć wstrzymanie się od głosu? Zaimplementuj to rozwiązanie.
3. Zastąp semantyczne grupowanie oparte na prostej kanonizacji tekstu porównywaniem wektorowym (wykorzystaj dowolny lekki model osadzania open-source). Zaobserwuj, jak zmiana ta wpływa na odporność na atak potakiwania.
4. Przeanalizuj publikację CP-WBFT (arXiv:2511.10400). Zaimplementuj etap kalibracji wskaźnika pewności (zewnętrzny model kalibrujący ocenia prawdopodobieństwo zgłoszone przez poszczególne agenty). Zmierz przyrost dokładności w scenariuszu monokultury.
5. Przeanalizuj publikację „Can AI Agents Agree?” (arXiv:2603.01213). Zreplikuj uproszczony eksperyment dotyczący konsensusu skalarnego: trzy agenty, jedno pytanie o wartość liczbową, wprowadzenie profilu złośliwego (adversarial). Sprawdź, czy CPWBFT lub DecentLLM potrafią wykryć tę manipulację.

## Kluczowe terminy

| Termin | Obiegowe określenie | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| BFT | „Bizantyjska tolerancja błędów” | Klasyczny protokół Castro-Liskov (1999) wypracowywania konsensusu przy założeniu $f < n/3$ błędów bizantyjskich. |
| Bizantyjski | „Dowolne błędne zachowanie” | Klasa błędów węzła: kłamstwo, gubienie pakietów, ciche wyłączenie — wszelkie zachowania poza bezpieczną awarią (fail-stop). |
| Wskaźnik pewności (Confidence probe) | „Określenie stopnia pewności” | Wartość prawdopodobieństwa (deklarowana przez agenta lub szacowana przez kalibrator) dołączana do głosu. |
| Grupowanie semantyczne | „Tożsamość znaczeniowa odpowiedzi” | Agregacja semantycznie równoważnych odpowiedzi przed przystąpieniem do zliczania głosów. |
| Mediana geometryczna | „Stabilny środek geometryczny” | Punkt minimalizujący sumę odległości do pozostałych punktów w przestrzeni. W przeciwieństwie do średniej jest odporny na wartości odstające. |
| Monokultura | „Ten sam model, te same błędy” | Skorelowane błędy występujące u agentów korzystających z tych samych danych treningowych lub tego samego modelu bazowego. |
| Potakiwanie (Sycophancy) | „Zgadzanie się z większością/przedmówcą” | Zjawisko, w którym głos agenta jest zniekształcony przez wypowiedzi, które padły wcześniej. |
| Rdzeń/Brzeg (Core/Edge) | „Hierarchiczne BFT” | Architektura WBFT dzieląca sieć na mały, szybki konsensus w rdzeniu oraz węzły brzegowe w celu redukcji opóźnień. |

## Literatura uzupełniająca

- [Castro i Liskov — Practical Byzantine Fault Tolerance (OSDI 1999)](https://pmg.csail.mit.edu/papers/osdi99.pdf) — podstawowa praca naukowa.
- [CP-WBFT — Confidence-Probe Weighted BFT](https://arxiv.org/abs/2511.10400) — publikacja wprowadzająca wagowanie głosów pewnością.
- [DecentLLMs — Leaderless Multi-Agent Consensus](https://arxiv.org/abs/2507.14928) — koncepcja agregacji za pomocą mediany geometrycznej.
- [WBFT — Weighted BFT with Hierarchical Structure Clustering](https://arxiv.org/abs/2505.05103) — koncepcja podziału na rdzeń i brzeg.
- [Can AI Agents Agree?](https://arxiv.org/abs/2603.01213) — badania nad podatnością konsensusu skalarnego na manipulacje i ataki.
