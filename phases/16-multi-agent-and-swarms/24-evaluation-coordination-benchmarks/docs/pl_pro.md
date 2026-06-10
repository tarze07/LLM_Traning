# Benchmarki oceny i koordynacji wieloagentowej

> Pięć wiodących benchmarków z lat 2025–2026 definiuje współczesną przestręń ewaluacji systemów wieloagentowych. **MultiAgentBench / MARBLE** (ACL 2025, arXiv:2503.01935) ocenia topologie komunikacji typu gwiazda, łańcuch, drzewo oraz graf na podstawie kluczowych wskaźników wydajności (KPI) – wykazując, że **struktura grafu najlepiej sprawdza się w zadaniach badawczych**, a planowanie poznawcze zwiększa o ~3% odsetek zrealizowanych kamieni milowych. **COMMA** ocenia multimodalną koordynację w warunkach asymetrii informacji; najnowsze modele, w tym GPT-4o, mają problem z pokonaniem losowego wyniku referencyjnego (baseline). **MedAgentBoard** (arXiv:2505.12371) obejmuje cztery kategorie zadań medycznych i często wykazuje, że systemy wieloagentowe nie przewyższają pojedynczego modelu LLM. **AgentArch** (arXiv:2509.10769) porównuje architektury agentów korporacyjnych łączące wykorzystanie narzędzi, pamięć i orkiestrację. **SWE-bench Pro** ([arXiv:2509.16941](https://arxiv.org/abs/2509.16941)) zawiera 1865 problemów w 41 repozytoriach obejmujących aplikacje biznesowe, usługi B2B i narzędzia deweloperskie; wiodące modele osiągają w nim skuteczność na poziomie ~23% w wersji Pro, podczas gdy w wersji Verified przekraczają 70% – co jest wyraźnym dowodem na skażenie (data contamination) danych testowych. Skuteczność modelu Claude Opus 4.7 (kwiecień 2026 r.) w wersji Pro jest szacowana na **64,3%** przy zastosowaniu zaawansowanej koordynacji agentowej (wynik ten nie został jeszcze oficjalnie opublikowany przez Anthropic i należy go traktować jako wstępny); framework Verdent (rusztowanie agentowe / agent scaffolding) osiąga **76,1% pass@1** w wersji Verified ([raport techniczny Verdent](https://www.verdent.ai/blog/swe-bench-verified-technical-report)). Najważniejszym wydarzeniem branżowym w 2026 roku jest **AAAI 2026 Bridge Program WMAC** (https://multiagents.org/2026/). W tej lekcji przeanalizujesz topologie i metryki MARBLE oraz zrozumiesz, dlaczego sam wysoki wynik w teście SWE-bench Verified nie jest wystarczającym dowodem na zdolność modelu do uogólniania wiedzy.

**Typ:** Ucz się
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 15 (Topologia głosowania i debaty), Faza 16 · 23 (Tryby awarii)
**Czas:** ~75 minut

## Problem

Gdy w publikacji naukowej pojawia się teza: „nasz system wieloagentowy osiąga wyższą skuteczność”, natychmiast nasuwają się pytania: w porównaniu z czym, na jakiej podstawie i za pomocą jakich metryk? W latach 2023–2024 w obszarze ewaluacji panował chaos – autorzy dobierali autorskie wskaźniki, własne modele referencyjne i dogodne zbiory zadań. Dopiero standaryzowane benchmarki wprowadziły tu spójność.

Bez powszechnie akceptowanych testów porównawczych rzetelne zestawienie dwóch systemów wieloagentowych jest niemożliwe. Co gorsza, brak ochrony przed skażeniem danych (data contamination) sprawia, że wiodące modele LLM mogą uczyć się na zadaniach testowych. Do połowy 2025 roku zbiór zadań SWE-bench Verified został częściowo ujawniony w danych treningowych modeli, co sztucznie zawyżyło ich wyniki. Wersja SWE-bench Pro została zaprojektowana jako wolny od skażenia sprawdzian rzeczywistych możliwości.

W tej lekcji omówimy pięć najważniejszych benchmarków ewaluacyjnych, wyjaśnimy, co dokładnie mierzy każdy z nich, i nauczymy Cię krytycznej oceny deklarowanych wyników testów.

## Koncepcja

### MultiAgentBench (MARBLE) – ACL 2025

Praca arXiv:2503.01935. Ewaluuje cztery topologie koordynacji (gwiazda, łańcuch, drzewo, graf) w zadaniach badawczych, programistycznych i planowania. Metryki oparte na kamieniach milowych (milestones) pozwalają śledzić stopień realizacji zadań cząstkowych, a nie tylko końcowy sukces.

Wnioski z badań:
- **Graf (Graph):** najlepsza topologia do zadań badawczych; ułatwia wzajemną krytykę rozwiązań.
- **Łańcuch (Chain):** optymalny do iteracyjnego ulepszania i refaktoryzacji kodu.
- **Gwiazda (Star):** najlepiej sprawdza się przy szybkiej agregacji informacji faktograficznych.
- **Koszt koordynacyjny (coordination tax):** zaczyna gwałtownie rosnąć w topologii grafu przy populacji powyżej 4 agentów.
- **Planowanie poznawcze (cognitive planning):** zwiększa wskaźnik realizacji celów o ~3% niezależnie od wybranej topologii.

Zastosowanie: gdy chcesz precyzyjnie porównać skuteczność różnych topologii koordynacyjnych. Repozytorium kodu MARBLE (https://github.com/ulab-uiuc/MARBLE) udostępnia gotowe skrypty ewaluacyjne.

### COMMA – Multimodalna koordynacja w asymetrii informacji

Wprowadza zadania, w których agenci dysponują różnymi kanałami obserwacji (modalnościami) i muszą koordynować działania bez pełnej wymiany informacji. Wyniki testów są zaskakujące: czołowe modele komercyjne, w tym GPT-4o, mają trudności z osiągnięciem wyników wyższych niż losowe (random baseline) w zadaniach kooperacji wieloagentowej w ramach COMMA. Wskazuje to, że koordynacja multimodalna w systemach agentowych pozostaje wyzwaniem – modele LLM dobrze radzą sobie z kooperacją w tekście, ale ich koordynacja na danych multimodalnych zawodzi.

Zastosowanie: gdy system wymaga koordynacji danych multimodalnych lub decyzji w warunkach asymetrii informacji.

### MedAgentBoard – Specjalistyczny benchmark dziedzinowy

Praca arXiv:2505.12371. Ewaluuje cztery kategorie zadań medycznych: diagnozę, planowanie terapii, generowanie raportów medycznych oraz komunikację z pacjentem. Porównuje systemy wieloagentowe z architekturami jednoagentowymi i klasycznymi systemami regułowymi.

Kluczowe wnioski: systemy wieloagentowe **nie dominują** nad pojedynczym, zaawansowanym modelem LLM w większości badanych kategorii. Przewaga struktur wieloagentowych jest niewielka: dekompozycja pomaga wyłącznie wtedy, gdy zadania składowe można precyzyjnie od siebie odseparować (np. podział na diagnozę i planowanie leczenia). W zadaniach spójnych (jak generowanie raportu) narzut komunikacyjny przewyższa zyski z podziału ról.

Zastosowanie: gdy tworzysz systemy dla wysoce wyspecjalizowanych dziedzin i potrzebujesz jednoznacznego punktu odniesienia względem architektury jednoagentowej.

### AgentArch – Architektury dla przedsiębiorstw

Praca arXiv:2509.10769. Koncentruje się na scenariuszach biznesowych, analizując wpływ nakładania się na siebie warstw orkiestracji, pamięci oraz integracji z narzędziami. Benchmark pozwala wyizolować realny wkład każdego z tych komponentów (np. o ile skuteczność wzrasta dzięki dodaniu narzędzi, pamięci długoterminowej lub wieloagentowej orkiestracji).

Zastosowanie: gdy projektujesz system klasy Enterprise i chcesz ocenić zasadność wdrażania poszczególnych warstw technologicznych.

### SWE-bench Pro – Prawdziwy sprawdzian możliwości

Praca arXiv:2509.16941. Zawiera 1865 problemów programistycznych z 41 rzeczywistych repozytoriów kodu (aplikacje biznesowe, usługi B2B, biblioteki programistyczne). Został zaprojektowany w sposób zapobiegający skażeniu danych treningowych modeli (data contamination). Czołowe modele osiągają w nim zaledwie ~23% skuteczności, podczas gdy w klasycznej wersji Verified ich wyniki przekraczają 70%. Różnica ta dowodzi skażenia wersji Verified.

Stan wyników na kwiecień 2026 roku:
- **Claude Opus 4.7 (wersja Pro):** 64,3% (wynik uzyskany przy zastosowaniu zaawansowanej orkiestracji agentowej; dane niepotwierdzone oficjalnym raportem Anthropic).
- **Verdent (wersja Verified):** 76,1% pass@1 przy użyciu rusztowania agentowego (agent scaffolding).
- **Wiodące modele bez rusztowania (wersja Pro):** wyniki w granicach ~23-35%.

Kluczowy wniosek: deklaracja „pobiliśmy wyniki na SWE-bench Verified” przestała być wyznacznikiem realnych możliwości modelu. Wersja Pro stanowi obecnie standard ewaluacyjny. Zastosowanie orkiestracji wieloagentowej (agent scaffolding) pozwala podnieść wyniki w wersji Pro o 30–40 punktów procentowych, co stanowi jeden z najsilniejszych dowodów empirycznych na korzyść systemów wieloagentowych w 2026 roku.

### Jak sceptycznie analizować wyniki benchmarków – lista kontrolna

Gdy autorzy deklarują przełomowe wyniki swojego systemu wieloagentowego, sprawdź:

1. **Jaki benchmark i jaka wersja zbioru danych zostały użyte?** Różnica między SWE-bench Verified a Pro jest fundamentalna. Agregowanie wyników z różnych wersji jest bezwartościowa.
2. **Czy wykluczono ryzyko skażenia danych (data contamination)?** Czy zadania testowe zostały opublikowane po zakończeniu treningu modelu? Jeśli nie, wyniki mogą być zawyżone.
3. **Z czym porównywano wyniki (baselines)?** Rzetelne porównanie powinno odnosić się do pojedynczego modelu LLM, losowego routingu oraz dotychczasowych wiodących systemów wieloagentowych – a nie do celowo osłabionej wersji własnego systemu.
4. **Czy wyniki są istotne statystycznie?** Zweryfikuj liczbę prób (N), wartość `p` oraz przedziały ufności. Modele komercyjne wykazują dużą zmienność wyników w pojedynczych uruchomieniach.
5. **Czy zbiór testowy jest zróżnicowany?** Czy testy przeprowadzono na jednym typie zadań, czy na wielu? Zdolność do uogólniania (generalization) jest kluczowa na produkcji.
6. **Jaki jest realny koszt wykonania?** Liczba zużytych tokenów na zadanie oraz czas odpowiedzi (latency). Rozwiązanie dające 90% skuteczności, ale generujące 20-krotnie wyższe koszty, rzadko nadaje się do wdrożenia biznesowego.

### Czego obecne benchmarki nie potrafią poprawnie zmierzyć

- **Interakcji w długich horyzontach czasowych:** zadań trwających wiele dni czasu rzeczywistego.
- **Odporności na zagrożenia bezpieczeństwa (security resilience):** zachowania systemu, gdy jeden z agentów zostanie przejęty lub zacznie działać złośliwie.
- **Dryfu rozkładu danych w czasie (data drift):** benchmarki mają charakter statyczny i nie odzwierciedlają zmian w produkcji.
- **Opłacalności rozwiązań (cost-efficiency):** większość testów podaje sam wskaźnik skuteczności, ignorując koszty tokenowe.

Często najlepszym rozwiązaniem jest zaprojektowanie własnego, wewnętrznego benchmarku (internal evaluation pipeline) zorientowanego na kluczowe wskaźniki biznesowe.

## Zbuduj to

Skrypt `code/main.py` implementuje uproszczony przewodnik demonstracyjny:

- Symuluje 3 architektury wieloagentowe realizujące syntetyczne zadanie.
- Oblicza wskaźniki realizacji celów w stylu MARBLE.
- Przeprowadza testy skażenia danych poprzez odrzucenie zadań z rzekomej „bazy treningowej”.
- Zestawia wyniki z losowym routingiem (random baseline).
- Generuje raport podsumowujący deklarowaną skuteczność systemu.

Uruchom:

```bash
python3 code/main.py
```

Oczekiwany wynik: zestawienie zawierające surową skuteczność modeli, wskaźniki realizacji kamieni milowych (milestones), koszt jednostkowy zadania, różnicę względem losowej linii bazowej oraz raport z analizy skażenia danych.

## Użyj tego

Plik `outputs/skill-benchmark-reader.md` definiuje umiejętność krytycznej analizy i weryfikacji deklaracji autorów o skuteczności systemów wieloagentowych na podstawie przedstawionej listy kontrolnej.

## Wdrożenie produkcyjne

- **Zbuduj wewnętrzny potok ewaluacji (internal benchmark)** odzwierciedlający strukturę zapytań z produkcji. Standardowe benchmarki publiczne powinny służyć jedynie jako ogólna wskazówka.
- **Zawsze zestawiaj wyniki z losowym routingiem (random baseline).** Jeśli system wieloagentowy w zadaniach koordynacyjnych nie potrafi wyraźnie pokonać losowego przydziału zadań, struktura systemu może być wadliwa.
- **Raportuj wskaźnik kosztów (token budget) i opóźnienia równolegle ze skutecznością.** Zespoły operacyjne potrzebują obu tych wskaźników.
- **Aktualizuj zbiory testowe co kwartał.** Zapobiega to przeuczeniu systemu pod statyczny zbiór zadań i uwzględnia zmiany profilu zapytań produkcyjnych.
- **Unikaj optymalizacji pod konkretne publiczne benchmarki.** Nadmierne dopasowanie rozwiązań do kryteriów SWE-bench Pro doprowadzi do pogorszenia stabilności systemu na produkcji.

## Ćwiczenia

1. Uruchom `code/main.py`. Przeanalizuj, który z symulowanych systemów charakteryzuje się najniższym kosztem w przeliczeniu na zrealizowany kamień milowy. Czy jest to system o najwyższej precyzji?
2. Przeczytaj publikację MARBLE (arXiv:2503.01935). Dla wybranego typu zadań biznesowych określ, którą z czterech topologii rekomendują autorzy i uzasadnij ten wybór na podstawie ich wniosków.
3. Przeczytaj publikację SWE-bench Pro. Jakie konkretnie mechanizmy wprowadzili autorzy w celu zabezpieczenia testu przed skażeniem danych treningowych? Czy te same zasady można zastosować do Twoich wewnętrznych zbiorów testowych?
4. Przeanalizuj wnioski z badań COMMA nad multimodalną koordynacją. Zaprojektuj uproszczone zadanie wymagające koordynacji danych asymetrycznych (multimodalnych), które można wdrożyć do wewnętrznego benchmarku.
5. Zastosuj listę kontrolną weryfikacji benchmarków do dowolnej niedawno opublikowanej pracy z zakresu systemów wieloagentowych (np. z arXiv). Jak oceniasz rzetelność przedstawionych w niej deklaracji o skuteczności?

## Kluczowe terminy

| Termin | Co się potocznie mówi | Co to właściwie oznacza |
|---|---|---|
| MARBLE (MultiAgentBench) | „Benchmark topologii” | Opublikowany na ACL 2025 zbiór testowy oceniający topologie gwiazdy, łańcucha, drzewa i grafu na podstawie kamieni milowych (KPI). |
| COMMA | „Multimodalny benchmark” | Benchmark badający koordynację w warunkach asymetrii informacji i multimodalności danych; modele pionierskie często osiągają w nim wyniki na poziomie losowym. |
| MedAgentBoard | „Benchmark medyczny” | Zbiór zadań medycznych wykazujący, że w większości scenariuszy struktury wieloagentowe nie przewyższają pojedynczych, zaawansowanych modeli LLM. |
| AgentArch | „Benchmark Enterprise” | Narzędzie ewaluacyjne analizujące wkład poszczególnych warstw (narzędzia, pamięć, orkiestracja) w systemach korporacyjnych. |
| SWE-bench Pro | „Nieskażony SWE-bench” | Zbiór 1865 problemów programistycznych zaprojektowany tak, aby zapobiegać skażeniu danych treningowych modeli (data contamination). |
| Kamienie milowe (Milestones) | „Częściowe punkty” | Metryki ewaluacyjne oceniające stopień zaawansowania realizacji zadania, zamiast zero-jedynkowego sukcesu. |
| Skażenie danych (Contamination) | „Wyciek testów” | Sytuacja, w której zadania z benchmarku testowego trafiają do zbioru treningowego modelu LLM, sztucznie zawyżając jego wyniki. |
| WMAC | „AAAI 2026 Bridge Program” | Wiodące warsztaty naukowe poświęcone tematyce koordynacji systemów wieloagentowych, wyznaczające trendy badawcze w 2026 roku. |

## Dalsze czytanie

- [MultiAgentBench / MARBLE](https://arxiv.org/abs/2503.01935) – benchmark topologii komunikacyjnych systemów wieloagentowych
- [Repozytorium kodu MARBLE](https://github.com/ulab-uiuc/MARBLE) – oficjalna implementacja ewaluacyjna
- [MedAgentBoard](https://arxiv.org/abs/2505.12371) – benchmark wykazujący granice opłacalności systemów wieloagentowych w medycynie
- [AgentArch](https://arxiv.org/abs/2509.10769) – analiza architektur agentowych klasy Enterprise
- [Rankingi SWE-bench](https://www.swebench.com/) – oficjalne rankingi skuteczności modeli na zbiorach Verified oraz Pro
- [AAAI 2026 WMAC](https://multiagents.org/2026/) – oficjalna strona programu i warsztatów AAAI 2026
