# CAIS, CAISI i ryzyko na skalę społeczną

> Centrum Bezpieczeństwa AI (CAIS z siedzibą w San Francisco, założone w 2022 roku przez Hendrycksa i współpracowników) opracowało model czterech głównych zagrożeń: złośliwego użycia, wyścigu zbrojeń AI, ryzyka organizacyjnego oraz zwodniczych systemów autonomicznych (rogue AI). W maju 2023 roku organizacja skoordynowała podpisanie deklaracji w sprawie ryzyka egzystencjalnego ze strony setek naukowców oraz menedżerów wiodących firm technologicznych. Aktualne projekty CAIS na 2026 rok to m.in. Panel Ewaluacyjny Modeli Pionierskich (Frontier Model Eval Panel), Indeks Pracy Zdalnej (Remote Work Index), strategiczny dokument dotyczący superinteligencji oraz biuletyn AI Frontiers. Z kolei odrębnym podmiotem o charakterze rządowym jest działające w ramach NIST amerykańskie Centrum ds. Standardów i Innowacji w zakresie AI (CAISI) – koordynuje ono dobrowolne porozumienia z laboratoriami badawczymi oraz realizuje niejawne testy zdolności systemów pod kątem zagrożeń cybernetycznych, biologicznych i chemicznych. CAIS klasyfikuje ryzyko organizacyjne jako jedno z zagrożeń najwyższego poziomu. Obejmuje ono kulturę bezpieczeństwa, rygorystyczne audyty, wielowarstwowe zabezpieczenia oraz bezpieczeństwo informacji. Cechy te są jednak często zaniedbywane na rzecz szybszego wdrażania produktów. Kalifornijska ustawa SB-53 (o ile zostanie podpisana) będzie pierwszym amerykańskim aktem prawnym na poziomie stanowym regulującym ryzyko katastrofalne ze strony AI.

**Typ:** Ucz się
**Języki:** Python (stdlib, inwentarz z czterema rodzajami ryzyka i moduł dopasowujący mitygację)
**Wymagania wstępne:** Faza 15 · 19 (RSP), Faza 15 · 20 (PF + FSF)
**Czas:** ~45 minut

## Problem

Lekcje 19 i 20 dotyczyły wewnętrznych zasad odpowiedzialnego skalowania w laboratoriach badawczych. Lekcja 21 skupiała się na niezależnej, zewnętrznej ocenie zdolności modeli. Ta lekcja przedstawia trzeci punkt widzenia: rolę społeczeństwa obywatelskiego oraz agend rządowych, które kształtują debatę publiczną i tworzą podstawy prawne pod regulacje dotyczące katastrofalnych zagrożeń ze strony sztucznej inteligencji.

Kluczowe znaczenie mają tutaj dwa odrębne podmioty. CAIS to niezależna organizacja non-profit, opracowująca ramy analizy ryzyka i koordynująca wspólne oświadczenia środowisk naukowo-technicznych. Z kolei CAISI to agenda rządowa USA (podlegająca NIST), która zawiera dobrowolne porozumienia z laboratoriami technologicznymi i prowadzi oficjalne ewaluacje systemów AI. Choć nazwy obu instytucji brzmią podobnie, ich misje są zupełnie inne, a każdy analityk bezpieczeństwa powinien precyzyjnie je odróżniać.

Aspekty praktyczne: opracowana przez CAIS taksonomia czterech ryzyk to najczęściej cytowany schemat klasyfikacji zagrożeń o charakterze społecznym. Obszar ryzyka organizacyjnego i kultury bezpieczeństwa to czynniki, na które specjaliści techniczni mają najbardziej bezpośredni wpływ. Z kolei kalifornijska ustawa SB-53, w przypadku jej ostatecznego podpisania, stałaby się pierwszym stanowym aktem prawnym w USA regulującym ryzyko katastrofalne. Struktura tej ustawy ma duże znaczenie, ponieważ historycznie regulacje stanowe w Kalifornii wielokrotnie stanowiły punkt wyjścia dla federalnych przepisów technologicznych.

## Koncepcja

### CAIS — Center for AI Safety

- Założenie: 2022 rok w San Francisco przez Dana Hendrycksa i współpracowników.
- Status prawny: organizacja non-profit typu 501(c)(3).
- Kluczowa inicjatywa (2023 r.): koordynacja oświadczenia o ryzyku egzystencjalnym AI. Stwierdzono w nim: „Ograniczenie ryzyka wyginięcia ludzkości z powodu sztucznej inteligencji powinno stać się globalnym priorytetem, na równi z innymi zagrożeniami o charakterze społecznym, takimi jak pandemie czy wojna nuklearna”, pod którym podpisały się setki naukowców i menedżerów.
- Działalność w 2026 roku: Frontier Model Eval Panel, Remote Work Index (wraz z Scale AI), opracowania strategiczne dotyczące superinteligencji oraz publikacja biuletynu AI Frontiers.

### Model czterech głównych ryzyk CAIS

Model CAIS klasyfikuje katastrofalne zagrożenia w cztery główne grupy:

1. **Złośliwe użycie (Malicious use)**: wykorzystanie systemów AI przez niebezpieczne podmioty do celowych szkód (np. synteza broni biologicznej, masowa dezinformacja, zaawansowane cyberataki).
2. **Wyścig zbrojeń AI (AI race)**: presja rynkowa i geopolityczna zmuszająca laboratoria, korporacje lub państwa do wdrażania systemów przed upewnieniem się, że są one w pełni bezpieczne.
3. **Ryzyko organizacyjne (Organizational risk)**: dysfunkcje wewnątrz samych laboratoriów badawczych (np. słaba kultura bezpieczeństwa, powierzchowne audyty, brak inwestycji w systemy ochronne) prowadzące do awarii wdrożeniowych.
4. **Zbuntowane systemy (Rogue AI)**: zaawansowane autonomiczne systemy AI dążące do celów sprzecznych z dobrem ludzkości i wymykające się spod kontroli.

Taksonomia ta nie wyczerpuje wszystkich ujęć, ale stanowi najpowszechniejszy standard. Opisane kategorie mogą się przenikać – np. zbuntowany system stworzony w pośpiechu przez korporację zaniedbującą audyty pod presją konkurencji łączy w sobie wszystkie te ryzyka.

### Wpływ ryzyka organizacyjnego

Obszar ten jest najbardziej istotny dla inżynierów i specjalistów technicznych. Kultura bezpieczeństwa organizacji, rygorystyczne podejście do audytów, budowa wielowarstwowych zabezpieczeń oraz bezpieczeństwo informacji (infosec) decydują o tym, czy wdrożone modele rzeczywiście posiadają mechanizmy kontrolne opisane w Lekcjach 10–18, czy też zabezpieczenia te istnieją jedynie na papierze.

Kluczowe czynniki kształtujące ryzyko organizacyjne:

- **Kultura bezpieczeństwa**: stopień swobody pracowników w zgłaszaniu problemów technicznych i naruszeń procedur bez obawy o negatywne konsekwencje zawodowe. Badania CAIS wskazują ten czynnik jako kluczowy prognostyk dla pozostałych obszarów bezpieczeństwa.
- **Wiarygodność audytów**: realizacja zarówno audytów wewnętrznych, jak i niezależnych audytów zewnętrznych (te pierwsze mają tendencję do generowania nazbyt optymistycznych wniosków).
- **Strategia obrony w głąb (defense in depth)**: założenie, że żadne pojedyncze zabezpieczenie nie jest w pełni skuteczne (główna myśl Fazy 15).
- **Bezpieczeństwo informacji (infosec)**: ochrona przed wyciekami wag modeli, baz testowych oraz metod obchodzenia systemów monitorujących (np. standardy RAND SL-4 z Lekcji 19).

### CAISI — U.S. AI Safety Institute (NIST)

- Działa w ramach amerykańskiego Narodowego Instytutu Standardów i Technologii (NIST).
- Koordynuje dobrowolne porozumienia i wytyczne z laboratoriami rozwijającymi modele pionierskie.
- Opracowuje jawne, publiczne ewaluacje zdolności systemów AI pod kątem zagrożeń cybernetycznych, biologicznych i chemicznych.
- Uwaga: to zupełnie inny podmiot niż CAIS; akronimy są podobne, dlatego należy weryfikować źródła (nist.gov).

CAISI pełni rolę rządowego, publicznego odpowiednika organizacji takich jak METR (Lekcja 21). Raporty publikowane przez CAISI są w pełni jawne, podczas gdy wyniki szczegółowych ewaluacji METR są często objęte klauzulami NDA. Analiza dokumentów z obu tych źródeł pozwala na uzyskanie kompletnego obrazu.

### Kalifornijska ustawa SB-53

Ustawa ta (zgłoszona w sesji legislacyjnej 2025–2026) wprost odnosi się do ryzyk katastrofalnych ze strony modeli pionierskich. Kluczowe zapisy obejmują:

- Określenie konkretnych progów wydajności i zdolności modeli, których przekroczenie nakłada na twórców formalne obowiązki prawne.
- Zagwarantowanie ochrony sygnalistów (whistleblower protection) dla pracowników laboratoriów AI.
- Wprowadzenie obowiązku raportowania incydentów w przypadku wystąpienia poważnych awarii systemowych.

Ustawa ta stanowi krok w kierunku pierwszej stanowej regulacji ryzyk katastrofalnych w USA. Niezależnie od ostatecznego kształtu procesu legislacyjnego, ramy te określają kierunek, w jakim zmierzać będą inne parlamenty stanowe oraz federalne organy regulacyjne.

### Ryzyko społeczne to problem wielopoziomowy

Nadrzędna idea Fazy 15 – obrona w głąb (defense in depth) – ma pełne zastosowanie również w skali makrospołecznej. Żadna pojedyncza regulacja, organizacja ani ramy prawne nie są w stanie samodzielnie wyeliminować ryzyka katastrofalnego. Spójny ekosystem bezpieczeństwa wymaga współdziałania wielu warstw:

- Laboratoria muszą wdrażać i przestrzegać zasad odpowiedzialnego skalowania (Lekcje 19 i 20).
- Niezależne podmioty zewnętrzne muszą realizować obiektywne ewaluacje systemów (Lekcja 21).
- Organizacje społeczeństwa obywatelskiego muszą monitorować sytuację i nagłaśniać nadużycia (np. CAIS).
- Rządy muszą tworzyć standardy, programy współpracy oraz twarde ramy regulacyjne (np. CAISI, ustawa SB-53).
- Inżynierowie i specjaliści techniczni muszą wdrażać wielowarstwowe mechanizmy kontrolne w codziennej praktyce (Lekcje 10–18).

Oto najważniejsza synteza całej Fazy 15: każda z omówionych lekcji stanowi jedną, niezbędną warstwę w całym stosie zabezpieczeń. Kompletność i spójność wszystkich warstw ma kluczowe znaczenie – o wiele większe niż skuteczność jakiegokolwiek pojedynczego mechanizmu.

## Jak tego użyć

Skrypt `code/main.py` implementuje proste narzędzie do inwentaryzacji ryzyka. Na podstawie parametrów planowanego wdrożenia system identyfikuje potencjalne zagrożenia w ramach czterech kategorii CAIS i generuje odpowiednią listę kontrolną środków łagodzących. Narzędzie ma charakter pomocniczy i nie zastępuje samodzielnej oceny ryzyka.

## Wynik zadania

Plik `outputs/skill-societal-risk-review.md` służy do weryfikacji wdrożeń systemów AI pod kątem ryzyka społecznego: bada podatność na poszczególne kategorie zagrożeń CAIS, analizuje wdrożone środki zaradcze oraz ocenia ekspozycję na ryzyka organizacyjne.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Przetestuj działanie na trzech wdrożeniach o różnej skali. Upewnij się, że generowane tagi ryzyka są spójne z założeniami, i wskaż sytuację, w której algorytm wykazuje nadmierną lub zbyt niską czułość.

2. Zapoznaj się z pełnym raportem CAIS na temat czterech głównych zagrożeń. Wybierz jedną z kategorii i napisz dwa akapity analizujące najważniejsze wydarzenia i trendy w tym obszarze z perspektywy roku 2026.

3. Przeczytaj aktualną wersję California SB-53. Wskaż jeden zapis, który Twoim zdaniem realnie zmniejsza ryzyko katastrofalne, oraz jeden, który uważasz za nieskuteczny lub wadliwy, uzasadniając swoje stanowisko.

4. Wybierz dowolny rzeczywisty system AI wdrożony produkcyjnie (własny lub opisany w literaturze). Oceń go pod kątem ryzyka organizacyjnego: kultury bezpieczeństwa, rygorystyczności audytów, wielowarstwowości obrony i ochrony informacji. Wskaż najsłabszy punkt i oszacuj nakłady niezbędne do jego eliminacji.

5. Zaproponuj zaktualizowaną strukturę modelu czterech ryzyk na rok 2028, uwzględniając postęp technologiczny i nowe doświadczenia wdrożeniowe z ostatnich lat. Co należy dodać, usunąć lub przeorganizować?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| CAIS | „Centrum Bezpieczeństwa AI” | Organizacja non-profit; twórcy modelu czterech ryzyk oraz inicjatorzy deklaracji o ryzyku egzystencjalnym z 2023 roku |
| CAISI | „Rządowy Instytut Bezpieczeństwa AI” | Agenda NIST; koordynuje dobrowolne porozumienia z laboratoriami i jawne ewaluacje rządowe |
| Model czterech ryzyk | „Taksonomia CAIS” | Struktura podziału zagrożeń: złośliwe użycie, wyścig zbrojeń AI, ryzyko organizacyjne, zbuntowane systemy (rogue AI) |
| Złośliwe użycie | „Celowe szkodzenie” | Wykorzystanie modeli do generowania cyberataków, broni biologicznej lub masowej dezinformacji |
| Wyścig zbrojeń AI | „Presja konkurencyjna” | Pogoń za pozycją lidera zmuszająca do skracania procedur bezpieczeństwa |
| Ryzyko organizacyjne | „Dysfunkcje wewnętrzne” | Zagrożenia wynikające ze słabej kultury bezpieczeństwa, braku audytów lub wycieków danych |
| Zbuntowane systemy (Rogue AI) | „Utrata kontroli” | Sytuacja, w której autonomiczny agent dąży do celów niezgodnych z intencją człowieka |
| California SB-53 | „Regulacja stanowa w USA” | Ustawa z lat 2025–2026; pierwsza próba uregulowania ryzyk katastrofalnych na poziomie stanowym |

## Dalsza lektura

- [Centrum bezpieczeństwa sztucznej inteligencji](https://safe.ai/) — instytucjonalna siedziba struktury czterech ryzyk.
- [CAIS — Ryzyko związane ze sztuczną inteligencją, które może doprowadzić do katastrofy](https://safe.ai/ai-risk) — dokument dotyczący czterech zagrożeń.
- [CAIS — Oświadczenie w sprawie ryzyka wyginięcia z maja 2023 r.](https://safe.ai/statement-on-ai-risk) — krótkie wspólne oświadczenie.
- [NIST CAISI](https://www.nist.gov/caisi) — rządowe centrum standardów i innowacji w zakresie sztucznej inteligencji.
- [Anthropic — Pomiar autonomii agenta w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — łączy zobowiązania na poziomie laboratorium z ramami na skalę społeczną.
