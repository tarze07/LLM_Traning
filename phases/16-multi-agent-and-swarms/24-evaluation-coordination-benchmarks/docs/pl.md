# Punkty odniesienia w zakresie oceny i koordynacji

> Pięć testów porównawczych na lata 2025–2026 obejmuje przestrzeń oceny wieloagentowej. **MultiAgentBench / MARBLE** (ACL 2025, arXiv:2503.01935) ocenia topologie gwiazdy/łańcucha/drzewa/wykresu za pomocą kluczowych wskaźników wydajności (KPI); **wykres najlepiej nadaje się do badań**, planowanie poznawcze dodaje ~3% osiągnięć kamieni milowych. **COMMA** ocenia wielomodalną koordynację informacji asymetrycznej; najnowocześniejsze modele, w tym GPT-4o, mają trudności z pokonaniem losowej wartości bazowej. **MedAgentBoard** (arXiv:2505.12371) obejmuje cztery kategorie zadań medycznych i często stwierdza, że ​​wielu agentów nie dominuje w przypadku pojedynczego LLM. **AgentArch** (arXiv:2509.10769) porównuje architektury agentów korporacyjnych łączące wykorzystanie narzędzi, pamięć i orkiestrację. **SWE-bench Pro** ([arXiv:2509.16941](https://arxiv.org/abs/2509.16941)) zawiera 1865 problemów w 41 repozytoriach obejmujących aplikacje biznesowe, usługi B2B i narzędzia programistyczne; modele frontier uzyskują wynik ~23% w wersji Pro w porównaniu z ponad 70% w wersji Verified — rzeczywisty test zanieczyszczenia. Claude Opus 4.7 (kwiecień 2026 r.) jest zgłaszany na poziomie **64,3%** w wersji Pro z wyraźną koordynacją agentów i zespołów (nie opublikowano jeszcze żadnego głównego źródła Anthropic — traktuj jako wstępne); Verdent (rusztowanie agenta) osiąga **76,1% pass@1** w Verified ([raport techniczny Verdent](https://www.verdent.ai/blog/swe-bench-verified-technical-report)). **AAAI 2026 Bridge Program WMAC** (https://multiagents.org/2026/) to punkt kontaktowy społeczności w 2026 roku. Ta lekcja opiera się na metrykach MARBLE, przeprowadza analizę topologii i metryki i przypina zasadę „tylko przejście zweryfikowane przez SWE-bench nie jest dowodem uogólnienia”.

**Typ:** Ucz się
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 15 (Topologia głosowania i debaty), Faza 16 · 23 (Tryby awarii)
**Czas:** ~75 minut

## Problem

Kiedy w jakiejś gazecie stwierdza się, że „nasz system wieloagentowy jest lepszy”, pojawia się pytanie: lepszy od czego, na podstawie czego i w jaki sposób mierzony? W erze ewaluacji wieloagentowej w latach 2023–2024 panował chaos — każdy wybierał własne wskaźniki, własne wartości bazowe i własne zestawy zadań. Punkty odniesienia na lata 2025–2026 narzuciły strukturę.

Bez wspólnych testów porównawczych nie można w znaczący sposób porównać dwóch systemów wieloagentowych. Co gorsza, bez solidnych wzorców odniesienia modele pionierskie mogą zanieczyścić. Do połowy 2025 r. ławka SWE Verified została częściowo skażona w korpusach szkoleniowych; zawyżone wyniki graniczne; Pro został zaprojektowany jako niezanieczyszczony test rzeczywistości.

W tej lekcji wymieniono pięć kanonicznych wskaźników referencyjnych na rok 2026, wymieniono, co mierzy każdy z nich, i nauczono sceptycznego odczytywania twierdzeń dotyczących wskaźników referencyjnych.

## Koncepcja

### MultiAgentBench (MARBLE) — ACL 2025

arXiv:2503.01935. Ocenia cztery topologie koordynacji (gwiazda, łańcuch, drzewo, wykres) w zakresie zadań badawczych, kodowania i planowania. Wskaźniki KPI oparte na kamieniach milowych śledzą częściowy postęp, a nie tylko końcowy sukces.

Zmierzone wyniki:

- Topologia **Wykresu** najlepsza dla scenariuszy badawczych; wspiera wszelką krytykę.
- **Łańcuch** najlepszy do kodowania stopniowego udoskonalania.
- **Gwiazdka** najlepsza do szybkiej konsolidacji opartej na faktach.
- **Podatek koordynacyjny** pojawia się na wykresie za ~4 agentami.
- **Planowanie kognitywne** dodaje ~3% osiągnięć kluczowych w różnych topologiach.

Użyj, gdy: chcesz porównać topologie koordynacyjne „jabłka z jabłkami”. Repozytorium MARBLE (https://github.com/ulab-uiuc/MARBLE) udostępnia narzędzie oceniające.

### PRZECINKA — multimodalna informacja asymetryczna

Obejmuje zadania, w przypadku których agenci mają różne sposoby obserwacji i muszą koordynować działania bez pełnego udostępniania informacji. Podany wynik jest niewygodny: pionierskie modele, w tym GPT-4o, mają trudności z przekroczeniem **losowego poziomu bazowego** w zakresie współpracy agent-agent w COMMA. Sygnałem jest to, że modalności wieloagentowe są niedostatecznie przeszkolone i niedoceniane – LLM rozsądnie radzą sobie ze współpracą w ramach jednej modalności; koordynacja multimodalności załamuje się.

Użyj, gdy: Twój system ma koordynację informacji multimodalnych lub asymetrycznych. Wynik zerowy COMMA jest ostrzeżeniem, które należy zmierzyć przed złożeniem wniosku.

### MedAgentBoard — test obciążenia domeny

arXiv:2505.12371. Cztery kategorie zadań medycznych: diagnoza, planowanie leczenia, generowanie raportów, komunikacja z pacjentem. Porównuje systemy wieloagentowe, jedno-LLM i konwencjonalne systemy oparte na regułach.

Wniosek: wieloagentowy NIE dominuje w przypadku pojedynczego LLM w większości kategorii. Przewaga wieloagentowa jest wąska — dekompozycja zadań pomaga, gdy podzadania można wyraźnie oddzielić (diagnoza + leczenie); boli, gdy narzut na koordynację przekracza przyrost specjalizacji (generowanie raportów).

Użyj, gdy: Twoja domena ma jasne linie bazowe z pojedynczym LLM. Jeśli można wyciągnąć wniosek MedAgentBoard w sposób uogólniający, wiele proponowanych systemów wieloagentowych jest przeprojektowanych.

### AgentArch — architektury korporacyjne

arXiv:2509.10769. Ustawienia korporacyjne obejmujące użycie narzędzi, pamięć i orkiestrację nałożone na siebie. Benchmark wyodrębnia wkład każdej warstwy: w jakim stopniu dodanie narzędzi pomaga? Dodawanie pamięci? Dodajesz orkiestrację wieloagentową?

Użyj, gdy: projektujesz stos agentów dla przedsiębiorstwa i musisz uzasadnić każdą warstwę. AgentArch pomaga uniknąć kupowania funkcji, których wartości nie można zmierzyć.

### SWE-bench Pro — sprawdzenie rzeczywistości

arXiv:2509.16941. 1865 problemów w 41 repozytoriach obejmujących aplikacje biznesowe, usługi B2B i narzędzia programistyczne. Zaprojektowany tak, aby był **nieskażony** w przypadku późniejszych przerw w treningu. Modele Frontier uzyskują wynik ~23% w wersji Pro w porównaniu z ponad 70% w wersji Verified. Luka jest sygnałem zanieczyszczenia.

Wyniki z kwietnia 2026 r.:
- Claude Opus 4.7 na Pro: **64,3%** (zgłoszone przy wyraźnej koordynacji agentów i zespołów; nie opublikowano jeszcze żadnego głównego źródła Anthropic — traktuj jako wstępne).
- Verdent (rusztowanie agenta) na Verified: **76,1% pass@1** ([raport techniczny](https://www.verdent.ai/blog/swe-bench-verified-technical-report)).
- Frontierowe surowe wyniki w Pro bez rusztowania agentowego: ~23-35% ([artykuł SWE-bench Pro](https://arxiv.org/abs/2509.16941)).

Wniosek na wynos: „pokonaliśmy zweryfikowaną wersję SWE” nie jest już dowodem możliwości. Pro to aktualny test bramkowania. Rusztowanie agent-zespół przynosi wymierne korzyści w wersji Pro (~30–40 punktów delta), co jest jednym z najsilniejszych argumentów empirycznych przemawiających za koordynacją wielu agentów w roku 2026.

### AAAI 2026 WMAC

Program pomostowy AAAI 2026 — warsztaty na temat koordynacji wieloagentowej (https://multiagents.org/2026/). Punkt kontaktowy społeczności w 2026 r. zajmujący się wieloagentowymi badaniami nad sztuczną inteligencją. Zaakceptowane artykuły i materiały warsztatowe są kanonicznym miejscem oceny nowych metod; odroczyć zaakceptowane przez WMAC roszczenia dotyczące wydruków arXiv w celu podjęcia decyzji produkcyjnych.

### Czytaj sceptycznie oświadczenia dotyczące testów porównawczych – lista kontrolna na rok 2026

Gdy ktoś twierdzi, że uzyskał wynik obejmujący wiele agentów:

1. **Który test porównawczy, który podział?** SWE-bench Verified vs Pro ma duże znaczenie. Liczba zgłoszona w przypadku niewłaściwego podziału jest bezwartościowa.
2. **Kontrola skażenia.** Czy benchmark został wydany po zakończeniu treningu modelu? Jeśli nie, należy zachować ostrożność.
3. **Porównanie wartości wyjściowych.** W porównaniu z wartością wyjściową pojedynczego LLM, w porównaniu z losowością, w porównaniu z wcześniejszą pracą z wieloma agentami. Nie „w porównaniu z niedostrojoną wersją tego samego systemu”.
4. **Istotność statystyczna.** N badań, wartość p, przedział ufności. Modele graniczne charakteryzują się dużą wariancją; pojedyncze biegi wprowadzają w błąd.
5. **Różnorodność zadań.** Jedno zadanie czy wiele? Generalizacja ma znaczenie dla produkcji.
6. **Ujawnienie kosztów.** Żetony za zadanie, zegar ścienny. Rozwiązanie 90% przy 20-krotnym koszcie to decyzja biznesowa, a nie deklaracja możliwości.

### Czego żaden z testów porównawczych nie mierzy dobrze

- **Koordynacja długohoryzontalna.** Dni interakcji zegara ściennego. Wszystkie obecne benchmarki wypadają słabo.
- **Odporność na ataki.** Co się dzieje, gdy jeden z agentów jest złośliwy lub zagrożony?
- **Drift w trakcie wdrażania.** Testy porównawcze są statyczne; zmiana dystrybucji produkcji.
- **Wydajność znormalizowana pod względem kosztów.** Większość testów porównawczych podaje samą dokładność, a nie dokładność w przeliczeniu na dolara.

Zbudowanie własnego wewnętrznego benchmarku dla osi, na której naprawdę Ci zależy, jest często właściwym posunięciem.

## Zbuduj to

`code/main.py` to nieinteraktywny przewodnik:

- Symuluje 3 systemy wieloagentowe w zadaniu zabawkowym.
- Oblicza parametry kamieni milowych w stylu MARBLE dla każdego.
- Przeprowadza kontrolę zanieczyszczenia, wstrzymując zadania ze zbioru „szkolącego”.
- Wyraźne porównanie z losową wartością bazową.
- Drukuje kartę wyników oświadczeń porównawczych.

Uruchom:

```bash
python3 code/main.py
```

Oczekiwany wynik: karta wyników systemu z surową dokładnością, osiągnięcia kamieni milowych, koszt zadania, delta bazowa w porównaniu z losową wartością bazową oraz notatka dotycząca kontroli zanieczyszczeń.

## Użyj tego

`outputs/skill-benchmark-reader.md` odczytuje wszelkie twierdzenia dotyczące wieloagentowego testu porównawczego i stosuje listę kontrolną kontroli. Wynik: ocena i zastrzeżenia.

## Wyślij to

Dyscyplina oceny produkcji:

- **Stwórz wewnętrzny benchmark**, który odzwierciedla rzeczywistą dystrybucję produkcji. Publiczne benchmarki informują, ale nie zastępują.
- **Do każdego porównania dołącz losową linię bazową**. Jeśli w zadaniu koordynacyjnym nie można pokonać losowości z dużą przewagą, zadanie może być źle postawione.
- **Raportuj koszt wraz z dokładnością.** Koszt tokena i zegar ścienny. Zespoły operacyjne potrzebują obu.
- **Odbuduj benchmark co kwartał.** Zmiany w dystrybucji produkcji; nieaktualne benchmarki wprowadzają w błąd.
- **Unikaj nadmiernego dopasowania do opublikowanych testów porównawczych.** Jeśli Twój zespół optymalizuje specjalnie pod kątem wyników SWE-bench Pro, produkcja ulegnie regresowi.

## Ćwiczenia

1. Uruchom `code/main.py`. Określ, który z trzech symulowanych systemów ma najlepszy koszt w przeliczeniu na kamień milowy. Czy pasuje do systemu o najwyższej dokładności?
2. Przeczytaj MultiAgentBench (arXiv:2503.01935). W przypadku własnej dziedziny zadań zdecyduj, którą z czterech topologii poleciłby MARBLE. Uzasadnij na podstawie wyników pracy.
3. Przeczytaj artykuł dotyczący SWE-bench Pro. Co konkretnie sprawia, że ​​jest on odporny na zanieczyszczenia? Czy tę samą technikę można zastosować w przypadku innych benchmarków, na których Ci zależy?
4. Przeczytaj ustalenia COMMA dotyczące koordynacji multimodalnej. Zaprojektuj proste zadanie koordynacji multimodalnej, które możesz dodać do swojego wewnętrznego punktu odniesienia. Co liczyłoby się jako użyteczny sygnał?
5. Zastosuj listę kontrolną oświadczeń porównawczych do nagłówka jednego z ostatnich artykułów wieloagentowych. Jaką ocenę przyznałbyś roszczeniu?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| MARMUR | „MultiAgentBench” | lista ACL 2025; topologie gwiazdy/łańcucha/drzewa/wykresu z kluczowymi wskaźnikami wydajności. |
| PRZECINKA | „Multimodalny benchmark” | Multimodalna koordynacja informacji asymetrycznej; Walka modeli granicznych vs losowość. |
| Tablica MedAgent | „Test warunków skrajnych domeny” | Cztery kategorie medyczne; często stwierdza, że ​​wielu agentów nie dominuje w przypadku pojedynczego LLM. |
| AgentArch | „Porównanie porównawcze przedsiębiorstw” | Narzędzia + pamięć + warstwowa orkiestracja. |
| SWE-bench Pro | „Odporny na zanieczyszczenia” | 1865 problemów, 41 repozytoriów; ~23% vs 70%+ w trybie Verified (sygnał skażenia). |
| Osiągnięcie kamienia milowego | „Częściowy kredyt” | Benchmarki nagradzające postęp, a nie tylko końcowy sukces. |
| Zanieczyszczenie | „Benchmark wyciekł do szkoleń” | Po wydaniu benchmarki trafiają do korpusów szkoleniowych; wyniki zawyżają. |
| WMAC | „Program pomostowy AAAI 2026” | Warsztaty na temat koordynacji wieloagentowej; punkt kontaktowy społeczności. |

## Dalsze czytanie

- [MultiAgentBench / MARBLE](https://arxiv.org/abs/2503.01935) — test porównawczy topologii z kluczowymi wskaźnikami KPI
- [Repozytorium MARBLE](https://github.com/ulab-uiuc/MARBLE) — implementacja referencyjna
- [MedAgentBoard](https://arxiv.org/abs/2505.12371) — test warunków skrajnych domeny; multiagent często nie dominuje
- [AgentArch](https://arxiv.org/abs/2509.10769) — architektury agentów korporacyjnych
- [Tabele liderów SWE-bench](https://www.swebench.com/) — Wyniki zweryfikowane i profesjonalne dla pionierskich modeli
– [AAAI 2026 WMAC](https://multiagents.org/2026/) — punkt kontaktowy społeczności w 2026 r.