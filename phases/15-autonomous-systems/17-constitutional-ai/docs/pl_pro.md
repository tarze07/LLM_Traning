# Konstytucyjna sztuczna inteligencja i wnioskowanie oparte na zasadach

> Konstytucja Claude'a stworzona by firmy Anthropic i opublikowana 22 stycznia 2026 r. liczy 79 stron i jest udostępniona na licencji CC0. Przechodzi ona od dopasowania opartego na sztywnych regułach (rule-based alignment) do dopasowania opartego na wnioskowaniu (reason-based alignment) oraz ustanawia czterostopniową hierarchię priorytetów: (1) bezpieczeństwo i wspieranie nadzoru ze strony człowieka, (2) etyka, (3) wytyczne Anthropic, (4) użyteczność. Zachowania modelu dzielą się na zakodowane na stałe zakazy (np. tworzenie broni biologicznej, CSAM), których operatorzy ani użytkownicy nie mogą obejść, oraz programowo definiowane wartości domyślne, które operatorzy mogą dostosowywać w określonych granicach. Oryginalna metoda z 2022 r. (Bai i in.) trenowała nieszkodliwość modelu poprzez samokrytykę i RLAIF w odniesieniu do konstytucji. Istotne zastrzeżenie: dopasowanie oparte na wnioskowaniu opiera się na zdolności modelu do uogólniania zasad na nieprzewidziane sytuacje. Własny eksperyment partycypacyjny Anthropic z 2023 r. wykazał około 50% rozbieżności między zasadami opracowanymi społecznościowo a regułami korporacyjnymi; wersja z 2026 r. nie uwzględniła jednak tych wniosków.

**Typ:** Ucz się
**Języki:** Python (stdlib, czterowarstwowy moduł rozpoznawania priorytetów)
**Wymagania wstępne:** Faza 15 · 06 (Zautomatyzowane badanie wyrównania), Faza 15 · 10 (Tryby uprawnień)
**Czas:** ~60 minut

## Problem

Agent w środowisku produkcyjnym napotyka dane wejściowe, których jego projektanci nigdy nie przewidzieli. Żadna lista reguł nie jest na tyle długa, by objąć wszystkie przypadki, ani na tyle krótka, by można ją było szybko przetworzyć przy ograniczonych zasobach obliczeniowych. Praktyczne pytanie brzmi: jak dostosować agenta do zasad, które sprawdzą się zarówno w nietypowych sytuacjach (tzw. długim ogonie), jak i podczas szybkiego wnioskowania?

Dopasowanie oparte na regułach (RBA): polega na wypisaniu wszystkich niedozwolonych kwestii. Jest ono szybkie w weryfikacji i łatwe do audytu, ale niemożliwe do utrzymania na bieżąco. Często też skutkuje nadmiernymi odmowami w przypadku sytuacji podobnych do zabronionych, których wcześniej nie przewidziano. Dopasowanie oparte na wnioskowaniu (Konstytucja Claude'a z 2026 r.): polega na zakodowaniu ogólnych zasad i pozwoleniu modelowi na samodzielne rozumowanie. Dobrze skaluje się w nieprzewidzianych przypadkach, ale jest trudniejsze do skontrolowania. W tym podejściu błędy wynikają raczej z niewłaściwego zastosowania zasad niż z bezpośredniego złamania konkretnej reguły.

Konstytucja z 2026 roku zajmuje kompromisowe stanowisko pośrodku. Zakodowane na stałe zakazy – czyli kwestie, których szkodliwość nie zależy od kontekstu (np. rozwijanie broni biologicznej, CSAM) – opierają się na podejściu RBA: są bezwzględnie blokowane, niezależnie od instrukcji operatora lub użytkownika. Wszystkie inne decyzje opierają się na wnioskowaniu w ramach czterostopniowej hierarchii priorytetów: na pierwszym miejscu stawia się bezpieczeństwo i wspieranie ludzkiego nadzoru; na drugim etykę; na trzecim wytyczne operacyjne Anthropic; a na ostatnim – użyteczność. Operatorzy mogą modyfikować wartości domyślne w wyznaczonym obszarze programowym, ale nie mają możliwości zmiany zakodowanych na stałe zakazów.

## Koncepcja

### Czterostopniowa hierarchia priorytetów

1. **Bezpieczeństwo i wspieranie nadzoru człowieka.** Priorytet najwyższy. Model nie może podważać zdolności ludzi oraz firmy Anthropic do nadzorowania i korygowania sztucznej inteligencji. Nie chodzi tu o ogólne zalecenie typu „zachowaj ostrożność”, ale o konkretną zasadę: „nie podejmuj działań utrudniających ludziom kontrolę”.
2. **Etyka.** Uczciwość, unikanie wyrządzania szkody innym, zakaz oszukiwania i manipulowania. W przypadku konfliktu etyka ma pierwszeństwo przed wytycznymi Anthropic.
3. **Wytyczne Anthropic.** Standardy operacyjne zdefiniowane przez firmę Anthropic: zakres produktu, wzorce interakcji oraz zasady dotyczące tego, jakich narzędzi używać i w jakich sytuacjach.
4. **Użyteczność.** Priorytet najniższy. Zapewnienie jak największej pomocy użytkownikowi, o ile nie narusza to priorytetów wyższego rzędu.

W przypadku konfliktu między poziomami pierwszeństwo ma poziom wyższy. Działa to podobnie jak priorytety w systemie Unix lub mechanizmy QoS w sieciach – ta struktura ma na celu zapewnienie przewidywalnego rozwiązywania konfliktów, a nie optymalizacji zachowania pod kątem jednego wybranego kryterium.

### Zakazy zakodowane na stałe a wartości domyślne zakodowane programowo

**Zakodowane na stałe (hardcoded):**
- Broń biologiczna / rozprzestrzenianie CBRN
- CSAM (materiały przedstawiające seksualne wykorzystywanie dzieci)
- Ataki na infrastrukturę krytyczną
- Oszukiwanie użytkowników co do tożsamości modelu (np. udawanie człowieka), gdy zostanie o to bezpośrednio zapytany

Ani operator, ani użytkownik nie mogą ich nadpisać. Tam, gdzie to możliwe, są one wdrażane bezpośrednio w wagach modelu (poprzez trening RLHF / konstytucyjną sztuczną inteligencję), a w innych przypadkach na poziomie filtrów czasu wykonywania (inference).

**Wartości domyślne definiowane programowo (konfigurowalne przez operatora):**
- Domyślna długość odpowiedzi
- Zakres tematyczny (model może odrzucać tematy wykraczające poza obszar wdrożenia określony przez operatora)
- Styl (formalny vs swobodny)
- Schematy korzystania z narzędzi

Modyfikacje wprowadzane przez operatora muszą mieścić się w ściśle określonych granicach. Operator nie może obejść zakodowanych na stałe zakazów, na przykład zmieniając ich nazwy.

### Szkolenie CAI 2022

Oryginalna metoda konstytucyjnej sztucznej inteligencji (Bai i in., 2022) trenowała nieszkodliwość w następujący sposób:

1. Generowanie odpowiedzi na zestaw promptów.
2. Nakłonienie modelu do skrytykowania każdej odpowiedzi, która narusza zasady konstytucyjne.
3. Poprawienie odpowiedzi na podstawie wygenerowanej krytyki.
4. Zastosowanie metody RLAIF (Reinforcement Learning from AI Feedback) na parach poprawionych odpowiedzi.

Rezultat: model, który odrzuca szkodliwe zapytania, podając merytoryczne uzasadnienie zamiast lakonicznej odmowy. Konstytucja z 2026 roku opiera się na udoskonalonej wersji tego procesu oraz na dodatkowym dostrajaniu (post-training) z uwzględnieniem wyraźnej hierarchii priorytetów.

### Co obejmuje, a czego nie wykrywa dopasowanie oparte na wnioskowaniu (reason-based)

**Co wykrywa:**
- Nieprzewidziane wcześniej kombinacje dopuszczalnych operacji elementarnych, w których dana zasada ma jasne zastosowanie.
- Nietypowe zapytania, które są bardzo zbliżone do zabronionych działań.
- Ataki socjotechniczne oparte na argumencie „przecież nie było wprost napisane, że X jest zabronione”.

**Czego nie wykrywa (słabe punkty):**
- Ataków wykorzystujących wieloznaczność zasad (np. „użytkownik o to poprosił, więc ze względu na użyteczność należy odpowiedzieć twierdząco”).
- Scenariuszy, w których dwie zasady wchodzą ze sobą w konflikt w nieprzewidziany sposób, a priorytetyzacja poziomów staje się niejasna.
- Stopniowego dryfu interpretacyjnego zasad w kolejnych cyklach treningowych modelu.

### Eksperyment partycypacyjny z 2023 roku

W 2023 roku firma Anthropic przeprowadziła eksperyment, w którym porównano konstytucję opracowaną przez korporację z zasadami wygenerowanymi na podstawie opinii publicznej (około 1000 respondentów z USA). Obie wersje były spójne w około 50% zasad. W obszarach rozbieżności wersja społecznościowa okazała się bardziej restrykcyjna w niektórych kwestiach (np. moderowanie treści politycznych), a mniej wymagająca w innych (np. ujawnianie tożsamości AI). Konstytucja z 2026 roku nie uwzględniła jednak wniosków z tego eksperymentu społecznego, co uwypukla istniejący konflikt interesów w tym podejściu.

### Dlaczego zakodowane na stałe zakazy są niezbędne

Dopasowanie oparte wyłącznie na wnioskowaniu nie jest w stanie w pełni zabezpieczyć nietypowych przypadków (długiego ogona). Jeśli napastnik skłoni model do zaakceptowania określonego założenia (np. „jesteśmy licencjonowanym laboratorium badawczym opracowującym broń biologiczną”), model może zacząć relatywizować ogólne zasady bezpieczeństwa na rzecz rzekomo uzasadnionego wyjątku. Zakodowane na stałe zakazy nie ulegają wpływom takich założeń kontekstowych. Stanowią one „twarde ograniczenia konstytucyjne” (omówione w lekcji 14 na poziomie warstwy dopasowania).

### Miejsce konstytucji w stosie bezpieczeństwa

Konstytucja nie pełni roli wyłącznika awaryjnego (kill switch), o którym mowa w Lekcji 14. Działa ona bezpośrednio w warstwie modelu, wpływając na preferencje zapisane w jego wagach. Wyłączniki awaryjne oraz tokeny kanarkowe (canary tokens) działają natomiast w warstwie środowiska uruchomieniowego (runtime), kontrolując dopuszczalne zachowania podczas działania aplikacji. Oba te mechanizmy są niezbędne. Środowisko uruchomieniowe, które pozwala na szkodliwe operacje tylko dlatego, że wagi modelu na nie przyzwoliły, jest wadliwe. Z kolei model odrzucający prawidłowe działania przez zbyt restrykcyjne reguły uruchomieniowe stwarza problemy z użytecznością. Te warstwy odpowiadają za zupełnie inne klasy zagrożeń.

## Jak tego użyć

Skrypt `code/main.py` zawiera uproszczoną implementację czteropoziomowego modułu ustalania priorytetów. Analizuje on proponowane działanie wraz z oceną zgodności z zasadami (bezpieczeństwo, etyka, wytyczne, użyteczność), a następnie zwraca decyzję: zatwierdzenie działania, jego odmowę lub wersję zmodyfikowaną. Sterownik obsługuje kilka testowych przypadków: jednoznaczne zezwolenie, jednoznaczny zakaz, zakodowany na stałe zakaz oraz sytuację niejednoznaczną z konfliktami na różnych poziomach hierarchii.

## Wynik zadania

Plik `outputs/skill-constitution-review.md` weryfikuje bazową architekturę wdrożenia: definiuje elementy zakodowane na stałe, reguły programowe, zakres dopuszczalnych modyfikacji dla operatora oraz sprawdza, czy czteropoziomowa hierarchia rzeczywiście prawidłowo rozstrzyga konflikty.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Upewnij się, że zakodowany na stałe zakaz działa nawet przy wysokim priorytecie użyteczności. Zmodyfikuj mechanizm decyzyjny tak, aby stawiać użyteczność ponad etyką, i zaobserwuj zachowanie systemu w trybie awaryjnym.

2. Zapoznaj się z Konstytucją Claude'a (dokument publiczny, 79 stron, licencja CC0). Wskaż jedną regułę, która Twoim zdaniem jest zbyt ogólna lub niedookreślona. Napisz dwa akapity wyjaśniające tę niejednoznaczność i zaproponuj bardziej precyzyjne sformułowanie.

3. Zaprojektuj programowy zestaw wartości domyślnych dla agenta obsługi klienta. Które parametry może regulować operator, a których nie wolno mu modyfikować? Przedstaw uzasadnienie dla każdej z wyznaczonych granic.

4. Przeczytaj publikację na temat CAI autorstwa Bai i in. z 2022 roku. Opisz scenariusz, w którym pętla krytyki i korekty w konstytucyjnej sztucznej inteligencji przyniosłaby gorsze rezultaty niż zastosowanie ogólnej reguły. Zdefiniuj tę klasę problemów.

5. Eksperyment partycypacyjny Anthropic z 2023 roku wykazał blisko 50% rozbieżności między zasadami opracowanymi społecznościowo a korporacyjnymi. Wybierz jedną kluczową kategorię dla środowiska produkcyjnego (np. neutralność polityczna) i zaproponuj rozwiązanie pozwalające operatorom na wdrażanie własnych wartości bez naruszania zakodowanych na stałe zakazów.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| Konstytucyjna sztuczna inteligencja (Constitutional AI) | „Metoda dopasowania stosowana przez Anthropic” | Proces samokrytyki i treningu RLAIF w oparciu o spisaną konstytucję |
| Dopasowanie oparte na wnioskowaniu (Reason-based alignment) | „Ogólne zasady zamiast sztywnych reguł” | Poleganie na zdolności modelu do interpretacji zasad w nowych, nieznanych sytuacjach |
| Zakodowany na stałe zakaz (Hardcoded prohibition) | „Bezwzględny zakaz wykonywania X” | Reguła bezpieczeństwa, której ani operator, ani użytkownik nie są w stanie pominąć |
| Wartości domyślne definiowane programowo | „Możliwość konfiguracji przez operatora” | Zachowania i parametry podlegające kontroli operatora w wyznaczonych granicach |
| Hierarchia czterostopniowa | „Kolejność priorytetów” | bezpieczeństwo i nadzór > etyka > wytyczne Anthropic > użyteczność |
| RLAIF | „Uczenie przez wzmacnianie na podstawie opinii AI” | Proces RL, w którym sygnał nagrody pochodzi z krytyki wygenerowanej przez model pomocniczy |
| Konstytucja partycypacyjna (Participatory constitution) | „Zasady współtworzone przez społeczność” | Eksperyment Anthropic z 2023 roku; wykazał ok. 50% rozbieżności z zasadami korporacyjnymi |
| Dryf zasad (Rule drift) | „Ewolucja interpretacyjna” | Powolna zmiana sposobu, w jaki model rozumie i stosuje zapisane reguły |

## Dalsza lektura

- [Anthropic — Konstytucja Claude’a (styczeń 2026 r.)](https://www.anthropic.com/news/claudes-constitution) — 79-stronicowy dokument na licencji CC0.
- [Bai i in. — Konstytucyjna sztuczna inteligencja: nieszkodliwość na podstawie opinii AI](https://www.anthropic.com/research/constitutional-ai-harmless-from-ai-feedback) — oryginalna publikacja z 2022 r.
- [Anthropic — Collective Constitutional AI (2023)](https://www.anthropic.com/research/collective-constitutional-ai-aligning-a-language-model-with-public-input) — opis eksperymentu partycypacyjnego.
- [Anthropic — Polityka odpowiedzialnego skalowania v3.0](https://anthropic.com/responsible-scaling-policy/rsp-v3-0) — umiejscowienie konstytucji w strukturze RSP.
- [Anthropic — Pomiar autonomii agentów w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — rola konstytucji we wdrożeniach długoterminowych.
