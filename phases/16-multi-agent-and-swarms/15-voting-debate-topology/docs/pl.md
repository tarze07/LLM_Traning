# Głosowanie, samospójność i topologia debaty

> Najtańsza agregacja: próbka N niezależnych agentów, głosowanie większościowe. Wang i in. Osiągnięto to w przypadku spójności wewnętrznej z 2022 r., w przypadku jednego modelu pobranego N razy. Multiagent rozszerza go o **heterogeniczne** środki, aby uniknąć monokultury — różne modele, różne podpowiedzi, różne temperatury, różne konteksty. Poza większością głosów, liczy się topologia debaty: MultiAgentBench (arXiv:2503.01935, ACL 2025) ocenił koordynację gwiazda/łańcuch/drzewo/wykres i znalazł **wykres najlepszy do badań**, z „podatkiem koordynacyjnym” obejmującym ~4 agentów. AgentVerse (ICLR 2024) dokumentuje dwa wyłaniające się wzorce — zachowania wolontariuszy i zachowania konformistyczne — a konformizm jest zarówno cechą (znajdowanie konsensusu), jak i ryzykiem (myślenie grupowe, lekcja 24). W tej lekcji mapujemy przestrzeń topologii, budujemy każdy wariant i mierzymy podatek koordynacyjny.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 07 (Społeczeństwo umysłu i debaty), Faza 16 · 14 (Konsensus i BFT)
**Czas:** ~75 minut

## Problem

Debata może poprawić dokładność (Du i in., arXiv:2305.14325). Może go również pogorszyć. To, czy debata pomoże, zależy od czterech wyborów strukturalnych:

1. Kto z kim rozmawia (topologia).
2. Ile rund (Du 2023: zarówno rundy, jak i agenci mają znaczenie niezależnie).
3. Czy agenci są heterogeniczni (różne modele podstawowe przełamują monokulturę).
4. Czy obecny jest głos przeciwnika (obsługa stali czy słoma).

Zespoły, które „uruchamiają 5 agentów i głosują” na dane zadanie, często popadają w regres w porównaniu z pojedynczym agentem. Awarie nie są przypadkowe. Śledzą topologię i heterogeniczność. Ta lekcja dotyczy mapy topologii.

## Koncepcja

### Spójność własna, podstawa pojedynczego modelu

Wang i in. 2022 („Samospójność poprawia łańcuch rozumowania”) pobrał próbki tego samego modelu N razy w temperaturze > 0 i większością głosów głosował nad odpowiedziami opartymi na ścieżce rozumowania. Wynik dla GSM8K: znaczny wzrost przy N=40 próbkach w pojedynczym zachłannym dekodowaniu. Własna spójność jest prekursorem głosowania wieloagentowego.

Limit: samospójność wykorzystuje jeden model podstawowy. Błędy są skorelowane przez konstrukcję. Jeśli model ma systematyczne obciążenie, wszystkie N próbek je podziela.

### Głosowanie wieloagentowe, rozszerzenie heterogeniczne

Zastąp N próbek N *różnymi* środkami. Różne modele podstawowe (Claude, GPT, Lama), różne podpowiedzi, inny dostęp do narzędzi. Korzyść: nieskorelowane błędy. Koszt: różni agenci kosztują różne kwoty; koordynowanie ich zwiększa obciążenie.

Kanoniczna nazwa debaty heterogenicznej na rok 2026 to **A-HMAD** – Adversarial Heterogeneous Multi-Agent Debate. Nie jest to powszechnie przyjęte, ale w artykułach używa się tego terminu na określenie „debaty o różnych modelach, co ogranicza skorelowane błędy wynikające z upadku monokultury”.

### Cztery topologie

```
star                chain               tree                graph

    ┌─A─┐           A─B─C─D         ┌──A──┐              A───B
    │   │                           │     │              │ × │
    B   C                           B     C              D───C
    │   │                          / \   / \
    D   E                         D   E F   G           (fully connected)
```

Gwiazda: jeden koncentrator, wszystkie inne komunikują się tylko z koncentratorem. Odpowiednik przełożonego-pracownika bez kanału zwrotnego.
Łańcuch: liniowy, każdy agent widzi wyniki poprzedniego. Podobnie jak rurociąg.
Drzewo: hierarchiczne, używane przez hierarchiczne systemy agentowe (Lekcja 06).
Wykres: każdy z każdym. Obejmuje w pełni połączoną klikę i dowolne DAG.

### Podatek koordynacyjny (MultiAgentBench)

MultiAgentBench (MARBLE, ACL 2025, arXiv:2503.01935) przeprowadził testy porównawcze gwiazdy, łańcucha, drzewa i wykresu w zestawie zadań obejmującym badania, kodowanie i planowanie. Kluczowe wyniki pomiarów:

- Topologia **Graph** wygrywa w zadaniach badawczych. Informacje przepływają od każdego do każdego; agenci mogą się wzajemnie krytykować.
- **Gwiazda** wygrywa w przypadku zadań opartych na faktach i szybkich odpowiedziach. Hub filtruje i konsoliduje.
- **Łańcuch** wygrywa w przypadku stopniowych rurociągów (stopniowe udoskonalanie).
- **Podatek koordynacyjny** pojawia się za ~4 agentami w topologii wykresu. Koszt zegara ściennego i tokena rośnie szybciej niż jakość.

Pułap 4 agentów ma charakter empiryczny, a nie fundamentalny. Odzwierciedla pojemność kontekstu LLM na rok 2026: kontekst każdego agenta wypełnia się wynikami partnerów, a wartość krańcowa dodania agenta N+1 spada, gdy wszyscy mogą zobaczyć wszystkich.

### Strategie debat wieloagentowych („Czy powinniśmy popaść w szaleństwo?”)

arXiv:2311.17371 to badanie strategii MAD z 2023 r. Kluczowe ustalenie powtórzone przez innych: warianty MAD, które są *strukturalnie podobne* do samospójności (niezależne pobieranie próbek + agregacja), często osiągają gorsze wyniki w zakresie samospójności przy użyciu tego samego budżetu. MAD pomaga najbardziej, gdy agenci są rzeczywiście heterogeniczni, a debata ma strukturę kontradyktoryjną (jeden agent jest przeciwny).

### Pojawiające się wzorce AgentVerse

AgentVerse (ICLR 2024, https://proceedings.iclr.cc/paper_files/paper/2024/file/578e65cdee35d00c708d4c64bce32971-Paper-Conference.pdf) dokumentuje dwa zachowania, które wyłaniają się z debaty wielu agentów, nawet bez wyraźnego projektu:

- **Ochotnik.** Agent oferuje pomoc („Mogę zrobić następny krok”) bez podpowiedzi. Przydatne: przydziela pracę najbardziej zdolnemu agentowi do wykonania podzadania.
- **Zgodność.** Agent dostosowuje swoje stanowisko do krytyka, nawet jeśli ten się myli. Jest to odpowiednik pochlebstwa będący debatą (lekcja 14).

Konformizm jest powodem, dla którego debata aż do porozumienia nagradza prześladowców. Ograniczone rundy z oddzielnym sędzią łagodzą.

### Heterogeniczność: pokrętło wpływające na dokładność

Wzorzec na lata 2024–2026 w literaturze praktycznej: zamiana jednego z N agentów na inny model podstawowy zapewnia większy wzrost dokładności niż zwiększenie N o 1. Intuicja jest monokulturowa — każde nowe źródło niezależnych błędów jest warte więcej niż dodatkowa skorelowana próbka.

Na granicy heterogeniczność pokonuje liczebność. Trzy różne modele pokonują pięć kopii jednego modelu w większości zadań, które mają czystą podstawę.

### Metody jury

Struktura Sibyl (cytowana w literaturze Minsky-LLM) formalizuje „jury” — niewielki zestaw wyspecjalizowanych agentów, którzy udoskonalają odpowiedzi w drodze głosowania na każdym etapie. W odróżnieniu od głosowania zwykłą większością głosów, ława przysięgłych pełni role: jeden agent przesłuchuje, drugi dostarcza kontekst, trzeci ocenia wiarygodność. Metody jury stanowią środek pomiędzy zwykłym głosowaniem (tanim, podatnym na monokulturę) a pełnym MAD (drogim, podatnym na konformizm).

### Kiedy dominuje głosowanie z debatą

- Pytanie zawiera prawdę (fakt, matematyka, zachowanie kodu). Zbieżność głosów jest znacząca.
- Agenci mają dostęp do różnych źródeł lub narzędzi (dostępna jest heterogeniczność).
- Rundy są ograniczone (typowo 2-3) i istnieje oddzielny sędzia lub weryfikator.
- Budżet pozwala na zatrudnienie 3-5 agentów. Powyżej 5-7 w topologii grafów dominuje podatek koordynacyjny.

### Kiedy głosowanie z debatą boli

- Pytanie ma charakter opinii. Agenci wybierają tę odpowiedź, która wydaje się najbardziej pewna, a nie poprawna.
- Wszyscy agenci mają wspólny model podstawowy. Monokultura sprawia, że ​​konsensus traci znaczenie.
- Rundy są nieograniczone. Konformizm wygrywa za każdym razem.
- Zadanie jest proste. Pojedynczy agent o spójności wewnętrznej przy N=5 jest tańszy i równie dokładny.

## Zbuduj to

`code/main.py` implementuje:

- `run_star(agents, hub, question)` — centrum odpytuje każdego pracownika, agreguje.
- `run_chain(agents, question)` — udoskonalanie sekwencyjne.
- `run_tree(root, children, question)` — hierarchiczny z agregacją głębokości 2.
- `run_graph(agents, question, rounds)` — debata typu „wszyscy na wszystkich”, rundy ograniczone.
- Skryptowe wybieranie heterogeniczności: każdy agent ma `error_bias` wskazujący na jego systematyczną błędność.
- Wiązka pomiarowa obsługująca każdą topologię przy N=3, 5, 7 i raporty (dokładność, total_tokens, wallclock_simulated).

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik: tabela topologii × N → (dokładność, tokeny, opóźnienie). Wykres wygrywa przy N=3-5 w przypadku zadań typu badawczego; gwiazda wygrywa w szybkich, rzeczowych zadaniach; wykres przy N=7 pokazuje podatek koordynacyjny (opóźnienie rośnie szybciej niż dokładność).

## Użyj tego

`outputs/skill-topology-picker.md` to umiejętność polegająca na czytaniu opisu zadania i zalecaniu topologii (gwiazda/łańcuch/drzewo/wykres), N (liczba agentów), profilu heterogeniczności (modele podstawowe do użycia) i zaokrągleniu.

## Wyślij to

Dla dowolnego zespołu:

- Zacznij od **samodzielności przy N=5**, stosując jeden mocny model podstawowy. To tania baza.
- Jeśli dokładność ma znaczenie, przejdź na **głosowanie heterogeniczne przy N=3**. Zmierz deltę.
- Aktualizuj do **topologii debaty** tylko wtedy, gdy zadanie ma strukturę (badania, wieloetapowe) i możliwe są ograniczone rundy.
- Zawsze rejestruj klaster mniejszościowy. Kiedy mniejszość niezmiennie ma rację, masz sygnał różnorodności.
- Testuj zegar ścienny i żetony wraz z dokładnością. „Większa dokładność przy 10-krotnym koszcie” to decyzja biznesowa.

## Ćwiczenia

1. Uruchom `code/main.py`. Wykreśl krzywą podatku koordynacyjnego dla topologii grafów: dokładność vs N, tokeny vs N. Przy jakim N zmienia się krzywa?
2. Wdrożenie A-HMAD: trzech agentów o celowo różnych uprzedzeniach. Jak linia bazowa oparta na wszystkich tych samych uprzedzeniach wypada w porównaniu z A-HMAD w sprawie ataku monokulturowego z lekcji 14?
3. Dodaj rolę „sędziego” do topologii wykresu, która nie głosuje, a jedynie ocenia ostateczny konsensus. Czy zmienia to wyłaniające się zachowanie konformistyczne?
4. Przeczytaj artykuł AgentVerse (ICLR 2024). Zidentyfikuj, które zachowania pojawiające się w Twojej implementacji są najsilniej widoczne. Czy możesz wywołać odwrotne zachowanie poprzez szybką zmianę?
5. Przeczytaj MultiAgentBench (arXiv:2503.01935) Sekcję 4 (eksperymenty z topologią). Odtwórz wynik „wykresu wygrywającego badania” w jednym zadaniu z papieru, korzystając z uprzęży.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Samokonsekwencja | „Próbka N razy, głosuj” | Wang 2022. Pojedynczy model, temperatura N>0 próbek, głosowanie większościowe na ścieżkach rozumowania. |
| Heterogeniczność | „Różne modele” | Zespół różnych modeli podstawowych lub rodzin podpowiedzi. Przełamuje monokulturę. |
| ZŁY | „Debata wieloagentowa” | Ogólny termin określający agentów wymieniających uwagi krytyczne podczas rund. Zobacz Du 2023. |
| A-HMAD | „Kontrawersyjny heterogeniczny MAD” | Wariant MAD kładący nacisk na różne modele + struktura kontradyktoryjna. |
| Topologia | „Kto z kim rozmawia” | Gwiazda, łańcuch, drzewo, wykres. Determinuje przepływ informacji. |
| Podatek koordynacyjny | „Malejące zyski” | Powyżej ~4 agentów na wykresie koszt rośnie szybciej niż jakość. |
| Zachowanie wolontariusza | „Nieoczekiwana pomoc” | Wzorzec wyłaniający się z AgentVerse: agent oferuje wykonanie kroku. |
| Zachowanie zgodne | „Porozumienie pod presją” | Wzorzec wyłaniający się z AgentVerse: agent współpracuje z krytykiem. |
| Jury | „Mały panel specjalistyczny” | Zespół w stylu sybilli z rolami (egzaminator, kontekst, strzelec). |

## Dalsze czytanie

- [Wang i in. — Spójność własna poprawia łańcuch rozumowania](https://arxiv.org/abs/2203.11171) — punkt odniesienia dla jednego modelu
- [Du i in. — Poprawa faktów i rozumowania poprzez debatę wieloagentową](https://arxiv.org/abs/2305.14325) — obaj agenci ORAZ rundy liczą się niezależnie
- [MultiAgentBench / MARBLE](https://arxiv.org/abs/2503.01935) — test porównawczy topologii pokazujący najlepszy wykres do badań, łańcuch rurociągów
- [Czy powinniśmy przejść na MAD?](https://arxiv.org/abs/2311.17371) — ankieta dotycząca strategii MAD; stwierdza, że MAD często przegrywa z spójnością przy równym budżecie
- [AgentVerse (ICLR 2024)](https://proceedings.iclr.cc/paper_files/paper/2024/file/578e65cdee35d00c708d4c64bce32971-Paper-Conference.pdf) — wzorce wolontariatu i wyłaniania się zgodności
- [repozytorium MARBLE](https://github.com/ulab-uiuc/MARBLE) — referencyjna implementacja benchmarku