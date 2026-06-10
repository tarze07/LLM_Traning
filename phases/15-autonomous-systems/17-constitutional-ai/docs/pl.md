# Konstytucyjna sztuczna inteligencja i zastąpienie zasad

> Konstytucja Claude’a firmy Anthropic z 22 stycznia 2026 r. liczy 79 stron i ma numer CC0. Przechodzi od dostosowania opartego na zasadach do dostosowania opartego na rozsądkach i ustanawia czterostopniową hierarchię priorytetów: (1) bezpieczeństwo i wspierający nadzór ze strony człowieka, (2) etyka, (3) wytyczne antropiczne, (4) użyteczność. Zachowania dzielą się na zakodowane na stałe zakazy (wznoszenie broni biologicznej, CSAM), których operatorzy i użytkownicy nie mogą obejść, oraz zakodowane programowo wartości domyślne, które operatorzy mogą dostosować w określonych granicach. Oryginał z 2022 r. (Bai i in.) trenował nieszkodliwość poprzez samokrytykę i RLAIF wbrew konstytucji. Szczere zastrzeżenie: dostosowanie oparte na przyczynach opiera się na modelu uogólniającym zasady na nieprzewidziane sytuacje. Własny eksperyment partycypacyjny Anthropic przeprowadzony w 2023 r. wykazał ~50% rozbieżności między zasadami pochodzącymi ze źródeł publicznych i zasadami korporacyjnymi; wersja z 2026 r. nie uwzględniła tych ustaleń.

**Typ:** Ucz się
**Języki:** Python (stdlib, czterowarstwowy moduł rozpoznawania priorytetów)
**Wymagania wstępne:** Faza 15 · 06 (Zautomatyzowane badanie wyrównania), Faza 15 · 10 (Tryby uprawnień)
**Czas:** ~60 minut

## Problem

Agent terenowy widzi dane wejściowe, których jego projektanci nigdy nie widzieli. Żadna lista reguł nie jest wystarczająco długa, aby je objąć. Żadna lista reguł nie jest wystarczająco krótka, aby można ją było szybko zastosować pod presją obliczeniową. Praktyczne pytanie: jak dostosować agenta do zasad, które przetrwają zarówno długi ogon przypadków, jak i szybkie wnioskowanie?

Dopasowanie oparte na regułach (RBA): wypisz wszystkie niedozwolone rzeczy. Szybkie do sprawdzenia, łatwe do audytu, niemożliwe do śledzenia na bieżąco, często nadmiernie odmawia w przypadku bliskich analogów, których się nie spodziewało. Dostosowanie oparte na powodach (Konstytucja Claude'a z 2026 r.): koduj zasady, pozwól modelowi rozumować. Skaluje się w niewidocznych przypadkach, jest trudniejszy do skontrolowania, tryb awarii to raczej błędne zastosowanie zasad niż złamanie reguły.

Konstytucja 2026 zajmuje wyraźne stanowisko środkowe. Zakodowane na stałe zakazy – rzeczy, których szkodliwość nie zależy od kontekstu (wznoszenie broni biologicznej, CSAM) – to RBA: nigdy, niezależnie od instrukcji operatora lub użytkownika. Wszystko inne opiera się na rozsądku w ramach czterostopniowej hierarchii: na pierwszym miejscu bezpieczeństwo i wspieranie nadzoru ludzkiego; etyka na drugim miejscu; Po trzecie, deklarowane antropicznie wytyczne; przydatność ostatnia. Operatorzy mogą dostosować ustawienia domyślne w strefie zakodowanej programowo, ale nie mogą dotykać zakodowanych na stałe zakazów.

## Koncepcja

### Czterostopniowa hierarchia priorytetów

1. **Bezpieczeństwo i wspieranie nadzoru człowieka.** Najwyższy. W modelu priorytetem jest niepodważanie zdolności ludzi i Anthropic do nadzorowania i korygowania sztucznej inteligencji. To nie jest „zachowaj ostrożność”; chodzi w szczególności o „nie zachowuj się w sposób, który utrudnia ludzki nadzór”.
2. **Etyka.** Uczciwość, unikanie krzywdy innych osób, nie oszukiwanie i nie manipulowanie. Zastępuje wytyczne Anthropic, jeśli są one sprzeczne.
3. **Wytyczne Anthropic.** Normy operacyjne Anthropic zdecydowało, co ma znaczenie: zakres produktu, wzorce interakcji, jakich narzędzi i kiedy użyć.
4. **Przydatność.** Najniższa. Bądź jak najbardziej użyteczny w ramach wyższych priorytetów.

W przypadku konfliktu poziomów wygrywa wyższy. Jest to ten sam kształt, co priorytety Uniksa lub QoS sieci — ramka ma na celu zapewnienie przewidywalnej rozdzielczości, niekoniecznie najlepszego zachowania na dowolnej pojedynczej osi.

### Zakazy zakodowane na stałe a wartości domyślne zakodowane programowo

**Zakodowane na stałe:**
- Broń biologiczna / wzrost CBRN
- CSAM
- Ataki na infrastrukturę krytyczną
- Oszukiwanie użytkowników co do tożsamości modelki, gdy zostanie o to bezpośrednio zapytany

Operator nie może ich zastąpić. Użytkownik nie może ich zastąpić. Tam, gdzie to możliwe, są one egzekwowane na poziomie wag modeli (szkolenie RLHF / konstytucyjna sztuczna inteligencja), a tam, gdzie nie, na poziomie wnioskowania.

**Domyślne ustawienia programowe (regulowane przez operatora):**
- Domyślna długość odpowiedzi
- Zakres tematyczny (model może odrzucić tematy spoza wdrożenia operatora)
- Styl (formalny vs swobodny)
- Wzorce użycia narzędzi

Korekty operatora odbywają się wewnątrz zadeklarowanej granicy. Operator nie może usunąć zakodowanych na stałe zakazów poprzez zmianę ich nazwy.

### Szkolenie CAI 2022

Oryginalna konstytucyjna sztuczna inteligencja (Bai i in., 2022) wytrenowała nieszkodliwość:

1. Wygeneruj odpowiedzi na zestaw podpowiedzi.
2. Poproś modela, aby skrytykował każdą odpowiedź sprzeczną z konstytucją (jawne zasady).
3. Powtórz odpowiedź w oparciu o krytykę.
4. RLAIF (uczenie się przez wzmacnianie na podstawie informacji zwrotnych AI) na poprawionych parach.

Rezultat: model, który odrzuca szkodliwe prośby, podając merytoryczne wyjaśnienia, a nie ogólną odmowę. Konstytucja z 2026 r. wykorzystuje następcę tego szkolenia oraz dodatkowe szkolenie po szkoleniu w oparciu o wyraźną hierarchię poziomów.

### Jakie wyrównanie oparte na przyczynach wychwytuje, a co pomija

**Łowy:**
- Nieprzewidziane kombinacje dozwolonych prymitywów, w których zasada ma wyraźne zastosowanie.
- Nowatorskie prośby, które są bliskimi analogami żądań zabronionych.
- Ataki socjotechniczne polegające na tym, że „nie powiedziałeś, że X jest zabronione”.

**Tęskni:**
- Ataki wykorzystujące niejednoznaczność zasad („użytkownik o to poprosił, więc przydatność mówi tak”).
- Scenariusze, w których dwie zasady kolidują ze sobą w nieprzewidziany sposób, a kolejność poziomów jest niejednoznaczna.
- Powolny dryf interpretacji zasad w cyklach treningowych (reinterpretacja).

### Eksperyment partycypacyjny 2023

Firma Anthropic przeprowadziła w 2023 r. eksperyment, w którym porównała konstytucję opracowaną przez korporację z konstytucją wygenerowaną na podstawie opinii publicznej (około 1000 respondentów w USA). Obie wersje zgodziły się co do ~ 50% zasad. Tam, gdzie były rozbieżności, wersja pochodząca ze źródeł publicznych była bardziej restrykcyjna w niektórych kwestiach (obsługa treści politycznych), a mniej restrykcyjna w innych (samoujawnianie tożsamości sztucznej inteligencji). Konstytucja z 2026 r. nie uwzględniła ustaleń pochodzących ze źródeł publicznych. Jest to udokumentowane napięcie w podejściu.

### Dlaczego konieczne są zapisane na stałe zakazy

Samo dostosowanie oparte na powodach nie może zamknąć ogona. Osoba atakująca, której uda się skłonić model do zaakceptowania założenia (np. „jesteśmy licencjonowanym laboratorium badawczym zajmującym się bronią biologiczną”), często może omówić zasady z przeszłości, zależne od uzasadnienia przypadku. Zakodowane na stałe zakazy nie naginają się do ram założeń. Są to „twarde ograniczenia konstytucyjne” z lekcji 14 na warstwie wyrównującej.

### Gdzie Konstytucja znajduje się na stosie

Konstytucja nie jest wyłącznikiem, o którym mowa w Lekcji 14. Żyje w warstwie modelu: co preferują ciężary modelu. Przełączniki zabijania i tokeny kanarkowe działają w warstwie środowiska wykonawczego: na co pozwala środowisko wykonawcze. Obydwa są wymagane. Środowisko wykonawcze, które uruchamia wszystkie nieprawidłowe działania, ponieważ wagi modelu są dozwolone, jest problemem związanym ze środowiskiem wykonawczym. Model, który odrzuca wszystkie właściwe działania, ponieważ środowisko wykonawcze jest zbyt restrykcyjne, jest problemem związanym z czasem wykonywania. Warstwy obejmują różne klasy.

## Użyj tego

`code/main.py` implementuje minimalny czteropoziomowy moduł rozpoznawania priorytetów. Osoba rozwiązująca podejmuje proponowane działanie i zestaw ocen zasad (bezpieczeństwo, etyka, wytyczne, przydatność) i zwraca akcję, odmowę lub zmodyfikowane działanie. Sterownik obsługuje mały zestaw przypadków: wyczyść zezwolenie, wyczyść zakaz, zakodowany na stałe zakaz, niejednoznaczna wielkość liter na różnych poziomach.

## Wyślij to

`outputs/skill-constitution-review.md` sprawdza podstawową warstwę wdrożenia: co jest zakodowane na stałe, co jest zakodowane programowo, co operator może dostosować i czy czteropoziomowa hierarchia jest w rzeczywistości kolejnością rozwiązywania.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że zakodowany na stałe zakaz uruchamia się nawet wtedy, gdy przydatność jest wysoka. Zmodyfikuj rozwiązanie tak, aby ważyć przydatność ponad etyką; obserwuj tryb awaryjny.

2. Przeczytaj Konstytucję Claude'a (publiczna, 79 stron, CC0). Wskaż jedną zasadę, która Twoim zdaniem jest niedookreślona. Napisz dwa akapity wyjaśniające konkretną niejednoznaczność i proponujące bardziej rygorystyczne sformułowanie.

3. Zaprojektuj zakodowany programowo zestaw domyślny dla agenta obsługi klienta. Co reguluje operator? Czego operator nie może dotykać? Uzasadnij każdą granicę.

4. Przeczytaj Bai i in. Artykuł CAI z 2022 r. Opisz jeden przypadek, w którym pętla krytyki i rewizji konstytucyjnej sztucznej inteligencji dałaby gorszy wynik niż ogólna zasada. Zidentyfikuj klasę.

5. Eksperyment partycypacyjny Anthropic przeprowadzony w 2023 r. wykazał około 50% rozbieżności między zasadami publicznymi i korporacyjnymi. Wybierz jedną kategorię, jeśli ma to znaczenie dla wdrożenia produkcyjnego (np. neutralność polityczna). Zaproponuj projekt, który pozwoli operatorom wyrażać własne wartości, nie naruszając zakodowanych na stałe zakazów.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| Konstytucyjna sztuczna inteligencja | „Metoda wyrównania Anthropic” | Samokrytyka + RLAIF przeciwko spisanej konstytucji |
| Dopasowanie oparte na przyczynach | „Zasady, nie zasady” | Modelowe powody zamiast zasad postępowania w niewidzianych przypadkach |
| Zakodowany na stałe zakaz | „Nigdy nie rób X” | Zakaz oparty na regułach, którego żaden operator ani użytkownik nie może obejść |
| Domyślne zakodowane programowo | „Regulowany przez operatora” | Zachowanie w zadeklarowanym zakresie, kontrola operatora |
| Hierarchia czterostopniowa | „Porządek priorytetowy” | bezpieczeństwo > etyka > wytyczne > użyteczność |
| RLAIF | „Opinia AI RL” | RL, gdzie nagroda pochodzi z krytyki generowanej przez model |
| Konstytucja partycypacyjna | „Zasady pochodzące ze źródeł publicznych” | 2023 Eksperyment antropiczny; ~50% rozbieżności z korporacyjnymi |
| Zasada dryfu | „Przepustka interpretacyjna” | Powolna zmiana sposobu, w jaki model odczytuje tekst zasad stałych |

## Dalsze czytanie

– [Anthropic — Konstytucja Claude’a (styczeń 2026 r.)](https://www.anthropic.com/news/claudes-constitution) — 79-stronicowy dokument CC0.
- [Bai i in. — Konstytucyjna sztuczna inteligencja: nieszkodliwość na podstawie opinii AI](https://www.anthropic.com/research/constitutional-ai-harmless-from-ai-feedback) — oryginał z 2022 r.
- [Anthropic — Collective Constitutional AI (2023)](https://www.anthropic.com/research/collective-constitutional-ai-aligning-a-language-model-with-public-input) — eksperyment partycypacyjny.
- [Anthropic — Polityka odpowiedzialnego skalowania v3.0](https://anthropic.com/responsible-scaling-policy/rsp-v3-0) — gdzie Konstytucja znajduje się na stosie RSP.
- [Anthropic — Pomiar autonomii agentów w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — Rola Constitution we wdrożeniach długoterminowych.