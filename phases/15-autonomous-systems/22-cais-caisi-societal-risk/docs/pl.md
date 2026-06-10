# CAIS, CAISI i ryzyko na skalę społeczną

> Centrum bezpieczeństwa sztucznej inteligencji (CAIS, San Francisco, założone w 2022 r. przez Hendrycksa i Zhanga) publikuje ramy czterech zagrożeń – złośliwe użycie, wyścigi sztucznej inteligencji, ryzyko organizacyjne, nieuczciwa sztuczna inteligencja – oraz oświadczenie z maja 2023 r. w sprawie ryzyka wyginięcia podpisane przez setki profesorów i liderów firm. Komunikaty CAIS z 2026 r.: Panel AI do oceny modelu pionierskiego, Indeks pracy zdalnej (ze skalą AI), Dokument strategiczny dotyczący superinteligencji, Biuletyn AI Frontiers. Odrębny podmiot: Centrum NIST ds. Standardów i Innowacji w zakresie AI (CAISI) – dobrowolne porozumienia zawierane z rządem USA i niesklasyfikowane oceny zdolności skupiające się na zagrożeniach związanych z cyberprzestrzenią, bronią biologiczną i chemiczną. CAIS klasyfikuje ryzyko organizacyjne jako jedno z czterech zagrożeń najwyższego poziomu: kultura bezpieczeństwa, rygorystyczne audyty, wielowarstwowe zabezpieczenia i bezpieczeństwo informacji to podstawowe elementy, ale rutynowo przekładane na szybkość wdrażania. Kalifornijska ustawa SB-53, jeśli zostanie podpisana, będzie pierwszą amerykańską regulacją dotyczącą ryzyka katastroficznego na szczeblu stanowym.

**Typ:** Ucz się
**Języki:** Python (stdlib, inwentarz z czterema rodzajami ryzyka i moduł dopasowujący mitygację)
**Wymagania wstępne:** Faza 15 · 19 (RSP), Faza 15 · 20 (PF + FSF)
**Czas:** ~45 minut

## Problem

Lekcje 19 i 20 dotyczyły wewnętrznych zasad skalowania laboratorium. Lekcja 21 dotyczyła niezależnej oceny zdolności. Ta lekcja obejmuje trzecią perspektywę: społeczeństwo obywatelskie i organizacje rządowe, które kształtują dyskusję publiczną i podstawy regulacyjne dotyczące katastrofalnego ryzyka związanego ze sztuczną inteligencją.

Liczą się dwa różne byty. CAIS to organizacja badawcza non-profit, która publikuje ramy myślenia o ryzyku związanym ze sztuczną inteligencją i koordynuje oświadczenia publiczne. CAISI to ośrodek rządowy USA w ramach NIST, który zawiera dobrowolne umowy z laboratoriami i prowadzi niesklasyfikowane oceny zdolności. Imiona się rymują; misje nie nakładają się na siebie. Praktykujący powinien znać jedno i drugie.

Treść praktyczna: Schemat czterech ryzyk CAIS jest najczęściej cytowaną w literaturze taksonomią ryzyka w skali społecznej. Kultura bezpieczeństwa i ryzyko organizacyjne należą do tych czterech i są najbardziej bezpośrednio kontrolowane przez praktyka. SB-53 (Kalifornia) byłaby pierwszą amerykańską regulacją dotyczącą ryzyka katastroficznego na szczeblu stanowym, gdyby została podpisana; Ramy projektu ustawy mają znaczenie, ponieważ w przeszłości regulacje na poziomie stanowym kierowały działaniami federalnymi w zakresie amerykańskiej polityki technologicznej.

## Koncepcja

### CAIS — Centrum Bezpieczeństwa AI

- Założona: 2022 w San Francisco przez Dana Hendrycksa i współpracowników (nazwa „Zhang” odnosi się do wczesnego współpracownika, a nie obecnego współzałożyciela; aktualne przywództwo można znaleźć na stronie internetowej CAIS).
- Status: 501(c)(3) organizacja non-profit.
- Godne uwagi wyniki za rok 2023: oświadczenie w sprawie ryzyka wyginięcia, podpisane przez setki badaczy i dyrektorów generalnych. Stwierdzono: „Ograniczenie ryzyka wyginięcia spowodowanego sztuczną inteligencją powinno być globalnym priorytetem, obok innych zagrożeń na skalę społeczną, takich jak pandemie i wojna nuklearna”.
- Wyniki na rok 2026: Panel sztucznej inteligencji do oceny modelu pionierskiego, Wskaźnik pracy zdalnej (wspólnie ze skalą AI), Dokument strategiczny dotyczący superinteligencji, biuletyn AI Frontiers.

### Schemat czterech ryzyk

Ramy CAIS grupują katastrofalne ryzyko związane ze sztuczną inteligencją w cztery główne kategorie:

1. **Złośliwe użycie**: zły aktor wykorzystuje sztuczną inteligencję do wyrządzenia szkody (synteza broni biologicznej, dezinformacja, cyberataki).
2. **Wyścigi sztucznej inteligencji**: presja konkurencyjna między laboratoriami, firmami lub krajami powoduje, że wdrażanie przekracza punkt, w którym jest bezpieczne.
3. **Ryzyko organizacyjne**: dynamika wewnętrznego laboratorium (błędy w zakresie kultury bezpieczeństwa, niewystarczający audyt, niewystarczające zasoby w zakresie bezpieczeństwa) skutkują złym wdrożeniem.
4. **Nieuczciwa sztuczna inteligencja**: sztuczna inteligencja o wystarczających zdolnościach realizuje cele sprzeczne z dobrem człowieka.

Nie jest to jedyna taksonomia; jest najczęściej cytowany. Kategorie te nie wykluczają się wzajemnie — fałszywa sztuczna inteligencja stworzona przez organizację, która zamieniła audyt na prędkość w wyścigu, obejmuje wszystkie cztery.

### Gdzie kryje się ryzyko organizacyjne

Spośród czterech kategorii ryzyko organizacyjne jest najbardziej praktyczne dla praktyków. Kultura bezpieczeństwa laboratorium, rygorystyczność audytu, warstwy zabezpieczeń i bezpieczeństwo informacji decydują o tym, czy ich model jest dostarczany z elementami sterującymi z lekcji 10–18, czy też te elementy sterujące znajdują się na liście kontrolnej, której nikt nie zweryfikował.

Konkretne dźwignie ryzyka organizacyjnego:

- **Kultura bezpieczeństwa**: czy członkowie zespołu czują, że są w stanie eskalować problemy bez ponoszenia kosztów kariery? Badania CAIS wykazały, że jest to silny predyktor pozostałych dźwigni.
- **Rygorystyczne audyty**: zewnętrzne i wewnętrzne. Audyty wewnętrzne pozwalają uzyskać optymistyczne raporty.
- **Wielowarstwowa obrona**: żadna pojedyncza warstwa nie jest wystarczająca (temat przewodni Fazy 15).
- **Bezpieczeństwo informacji**: wycieki wag modeli, wycieki danych ewaluacyjnych, wycieki technik obejścia monitora. RAND SL-4 w Lekcji 19 to specyficzny standard.

### CAISI — Centrum Standardów i Innowacji AI

- Działa w ramach NIST.
- Prowadzi dobrowolne umowy z laboratoriami przygranicznymi.
- Publikuje niesklasyfikowane oceny zdolności skupiające się na zagrożeniach związanych z bronią cybernetyczną, biologiczną i chemiczną.
- Różni się od CAIS; akronimy zderzają się; sprawdź adres URL (nist.gov), aby potwierdzić, który z nich czytasz.

Rolą CAISI jest publiczny, skierowany do rządu odpowiednik prywatnych laboratoriów METR (lekcja 21). Raporty CAISI są jawne; Raporty METR są często bramkowane przez NDA. Osoba praktykująca czytająca oba uzyskuje pełniejszy obraz.

### Kalifornijski SB-53

Projekt ustawy Senatu Kalifornii (sesja 2025–2026) uwzględnia ryzyko katastrofalne wynikające z modeli granicznych. Kluczowe przepisy w brzmieniu:

- Określone progi zdolności, które powodują powstanie obowiązków na poziomie państwa.
- Ochrona sygnalistów dla pracowników laboratorium AI.
- Wymagania dotyczące zgłaszania incydentów w przypadku awarii katastrofalnych.

Jeśli zostanie podpisane, będzie to pierwsze amerykańskie rozporządzenie dotyczące ryzyka katastroficznego na szczeblu stanowym. Niezależnie od statusu podpisania, ramy ustawy kształtują sposób, w jaki inne legislatury stanowe podchodzą do problemu. Praktycy w Kalifornii powinni śledzić status projektu ustawy; praktycy z innych krajów powinni ją przeczytać, aby zrozumieć, jak prawdopodobnie będą wyglądać regulacje na poziomie stanowym w USA.

### Ryzyko na skalę społeczną nie jest problemem jednopoziomowym

Temat przewodni Etapu 15 – głęboka obrona – ma zastosowanie także w warstwie społecznej. Żadna pojedyncza organizacja, regulacja ani ramy nie eliminują ryzyka katastrofalnego. Ekosystem funkcjonuje tylko wtedy, gdy:

- Zasady skalowania statków w laboratorium (lekcje 19, 20).
- Zewnętrzni ewaluatorzy dokonują pomiarów (lekcja 21).
- Społeczeństwo obywatelskie śledzi i publikuje informacje (CAIS).
- Rząd prowadzi programy dobrowolne i podstawowe regulacje (CAISI, SB-53).
- Praktycy tworzą wielowarstwowe kontrole (lekcje 10–18).

Oto ostateczna synteza tego etapu: każda poprzednia lekcja to jedna warstwa w stosie, którego kompletność jest ważniejsza niż siła jakiejkolwiek pojedynczej warstwy.

## Użyj tego

`code/main.py` implementuje małe narzędzie do inwentaryzacji ryzyka. Biorąc pod uwagę proponowane wdrożenie, oznacza je według czterech kategorii ryzyka i zwraca listę kontrolną środków łagodzących. Jest to pomoc w czytaniu frameworka, a nie substytut ludzkiego osądu.

## Wyślij to

`outputs/skill-societal-risk-review.md` sprawdza wdrożenie pod kątem ryzyka na skalę społeczną: których z czterech kategorii dotyczy, jakie środki zaradcze zastosowano, jakie jest narażenie na ryzyko organizacyjne.

## Ćwiczenia

1. Uruchom `code/main.py`. Podaj trzy syntetyczne wdrożenia w różnych skalach. Potwierdź, że cztery znaczniki ryzyka odpowiadają oczekiwaniom; zidentyfikuj jeden przypadek, w którym narzędzie ma niedostateczne lub nadmierne tagi.

2. Przeczytaj w całości dokument CAIS dotyczący czterech zagrożeń. Wybierz jedną kategorię ryzyka i napisz dwa akapity na temat tego, co Twoim zdaniem jest najważniejszym wydarzeniem w tej kategorii w roku 2026.

3. Przeczytaj aktualny projekt California SB-53. Wskaż jedno postanowienie, które Twoim zdaniem wzmacnia ryzyko katastrofalne i takie, które Twoim zdaniem je osłabia. Uzasadnij oba.

4. Wybierz znane Ci produkcyjne wdrożenie AI (własne lub opublikowane). Oceń to pod względem poddźwigni ryzyka organizacyjnego: kultury bezpieczeństwa, rygoru audytu, wielowarstwowych zabezpieczeń, bezpieczeństwa informacji. Który jest najsłabszy? Jaki byłby koszt doprowadzenia tego do normy?

5. Naszkicuj wersję ram czterech ryzyk na rok 2028, która odzwierciedla jeden rok dodatkowych możliwości i jeden rok dodatkowego doświadczenia w zakresie wdrażania. Co byś dodał, usunął lub przegrupował?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| CAIS | „Centrum Bezpieczeństwa AI” | Niedochodowy; ramy czterech ryzyk; Oświadczenie o wyginięciu z 2023 r. |
| CAISI | „Bezpieczeństwo sztucznej inteligencji rządu USA” | Centrum NIST; dobrowolne umowy; niesklasyfikowane ewaluacje |
| Ramy czterech ryzyk | „Taksonomia CAIS” | złośliwe użycie, wyścigi AI, ryzyko organizacyjne, nieuczciwe AI |
| Złośliwe użycie | „Zły aktor używa sztucznej inteligencji” | Broń biologiczna, dezinformacja, cyberataki |
| Wyścigi AI | „Presja konkurencyjna” | Laboratoria/firmy/kraje wypychają wdrożenie poza bezpieczeństwo |
| Ryzyko organizacyjne | „Wewnętrzna awaria laboratorium” | Kultura bezpieczeństwa, audyt, obrona, infosec |
| Zbuntowana sztuczna inteligencja | „Niewłaściwie ustawiony agent” | Zdolna sztuczna inteligencja realizująca cele sprzeczne z dobrem człowieka |
| Kalifornia SB-53 | „Regulacje na poziomie państwa” | ustawa na lata 2025–2026; pierwsze rozporządzenie stanu USA dotyczące ryzyka katastroficznego, jeśli zostanie podpisane |

## Dalsze czytanie

- [Centrum bezpieczeństwa sztucznej inteligencji](https://safe.ai/) — instytucjonalna siedziba struktury czterech ryzyk.
– [CAIS – Ryzyko związane ze sztuczną inteligencją, które może doprowadzić do katastrofy](https://safe.ai/ai-risk) – dokument dotyczący czterech zagrożeń.
- [CAIS – Oświadczenie w sprawie ryzyka wyginięcia z maja 2023 r.](https://safe.ai/statement-on-ai-risk) – krótkie wspólne oświadczenie.
– [NIST CAISI](https://www.nist.gov/caisi) — skierowane do rządu centrum standardów i innowacji w zakresie sztucznej inteligencji.
– [Anthropic — Pomiar autonomii agenta w praktyce](https://www.anthropic.com/research/measuring-agent-autonomimy) — łączy zobowiązania na poziomie laboratorium z ramami na skalę społeczną.