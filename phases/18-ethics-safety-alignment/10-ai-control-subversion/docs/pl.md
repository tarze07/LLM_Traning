# Kontrola AI — bezpieczeństwo pomimo działalności wywrotowej

> Greenblatt, Shlegeris, Sachan, Roger (Redwood Research, arXiv:2312.06942, ICML 2024). Kontrola zmienia kwestię bezpieczeństwa: biorąc pod uwagę niezaufany, mocny model U, który może kontradyktoryjnie optymalizować przeciwko Tobie, jakie protokoły pozwalają wyodrębnić użyteczną pracę, ograniczając jednocześnie prawdopodobieństwo nieakceptowalnego wyniku? Zasoby to zaufany słabszy model T, budżet zaufanej pracy ludzkiej H i możliwość edycji wyników U. W tym kontekście Zaufana edycja Pareto dominuje nad niezaufanym monitorowaniem zadań związanych z backdoorami kodu. Rama dziedziczy najgorsze założenia z inżynierii bezpieczeństwa: bezpieczeństwo to prawdopodobieństwo, że przeciwstawnie wybrane U nie może spowodować konkretnego, nieakceptowalnego wyniku, mierzone pod presją drużyny czerwonych, która zastępuje U.

**Typ:** Ucz się
**Języki:** Python (stdlib, granica bezpieczeństwa a użyteczności w przypadku zadania backdoora kodu)
**Wymagania wstępne:** Faza 18 · 07 (uśpieni agenci), Faza 18 · 08 (knucie), Faza 18 · 09 (fałszowanie charakteru)
**Czas:** ~75 minut

## Cele nauczania

- Zdefiniuj model zagrożenia AI Control: niezaufany silny model U, zaufany słabszy model T, zaufany ludzki budżet H.
- Opisać protokół Trusted Editing i dlaczego dominuje on w Pareto nad niezaufanym monitorowaniem w zadaniu backdoora kodu ICML 2024.
- Wyjaśnij różnicę pomiędzy dostosowaniem (U jest godne zaufania) a kontrolą (U nie jest godne zaufania, a mimo to jesteśmy bezpieczni).
- Podaj trzy granice kontroli: ludzie nie skalują się, zaufane, słabe modele w końcu pozostają w tyle, kontrola nie tworzy godnych zaufania, silnych modeli.

## Problem

Z lekcji 7-9 wynika, że model graniczny może być zwodniczo ukierunkowany, intrygować lub udawać wyrównanie. Pytanie dotyczące bezpieczeństwa zmienia ramy: czy możemy wydobyć użyteczną pracę z modelu, któremu nie ufamy, nie dając mu możliwości spowodowania nieakceptowalnych wyników? Jest to problem kontroli, zorganizowany na wzór klasycznego bezpieczeństwa: załóżmy, że przeciwnik jest najgorszy, zaprojektuj protokół, zmierz skuteczność przeciwnika pod presją zespołu czerwonych.

## Koncepcja

### Model zagrożenia

Kontrola zakłada:
- U — niezaufany mocny model. Zdolny. Prawdopodobnie kontradyktoryjne (w ocenie traktuje się to tak, jakby było).
- T — zaufany słabszy model. Mniej zdolny, ale znany z tego, że nie jest wrogo nastawiony.
- H — zaufana praca ludzka. Mały budżet; nie skaluje się.

System musi generować użyteczne dane wyjściowe za pomocą U. Przeciwnik próbuje spowodować konkretny, nie do przyjęcia wynik (np. backdoor w dostarczonym kodzie), jednocześnie utrzymując ułamek uzasadnionej, użytecznej pracy, aby przekroczyć progi użyteczności.

Kontrola rezygnuje z zaufania U. Pyta, jakie protokoły zapewniają bezpieczeństwo w przypadku braku zaufania U.

### Zadanie backdoora ICML 2024

Podpowiedzi to problemy z kodowaniem na poziomie konkurencji. U tworzy rozwiązanie kandydujące. Ukryta wyrocznia oznacza, że ​​rozwiązanie zawiera backdoora (specyficzne dane wejściowe, które powodują, że kod generuje błędne dane wyjściowe). Zespół czerwony kontroluje U i może zobaczyć wszystkie elementy wewnętrzne protokołu. Protokół musi maksymalizować współczynnik rozwiązanych problemów, jednocześnie utrzymując wskaźnik wysyłania backdoorów poniżej progu.

### Porównano cztery protokoły

- **Linia bazowa:** wysyłaj bezpośrednio dane wyjściowe U. Przydatność maksymalna. Bezpieczeństwo minimalne.
- **Kontrola z góry:** użyj H na wszystkich wynikach. Maksymalne bezpieczeństwo. Budżet szybko się wyczerpuje.
- **Monitorowanie niezaufane:** druga instancja U ocenia dane wyjściowe pierwszej instancji; H przeprowadza audyt oznaczonych wyników. Ryzyko: dwie instancje U mogą zmówić się.
- **Trusted Editing:** T edytuje dane wyjściowe U przy każdym zapytaniu. Jeśli T nie jest pewien, kieruj się do H.

Greenblatt i in. znajdź Zaufane edytowanie Dominuje Pareto Niezaufane monitorowanie: większa użyteczność na każdym poziomie bezpieczeństwa.

### Dlaczego zaufane edytowanie wygrywa

Niezaufane monitorowanie wymaga, aby druga instancja U nie mogła koordynować działania z pierwszą. Zmowa jest możliwa dzięki wskazówkom steganograficznym lub wspólnym wcześniejszym planom szkoleniowym. Protokół musi inwestować budżet w odporność na zmowy (parafrazowanie, zaciemnianie), które zmniejszają sygnał monitora. Zaufana edycja pozwala całkowicie uniknąć zmowy, ponieważ T jest zaufane — każda edycja zaproponowana przez T nie jest z założenia kontradyktoryjna. Kosztem jest to, że T ma mniejsze możliwości, więc może nadmiernie odrzucać lub pomijać subtelne tylne drzwi.

### Cztery osie protokołu

1. Którą rolę odgrywasz: tylko producenta, monitora czy obie.
2. Jaką rolę pełni T: redaktor, monitor czy resampler.
3. Sposób alokacji H: audyt jednolity, audyt wyrywkowy lub audyt ukierunkowany na flagę.
4. Ile obliczeń protokół wydaje na odporność na zmowy.

### Wyrównanie a kontrola

- Charakter: „Czy można Ci zaufać?” Lekcje 2, 4, 5, 6, 7, 8, 9 odnoszą się do tego.
- Kontrola: „Czy możemy używać Cię bezpiecznie, nie ufając mu?” Lekcja 10.

Wyrównanie jest właściwością modelu. Kontrola jest właściwością protokołu wdrażania. Kontrola nie tworzy dopasowanych modeli; zapewnia bezpieczne użycie potencjalnie niewyrównanych modeli. Obydwa programy są potrzebne.

### Trzy podstawowe ograniczenia

- Ludzie nie skalują się. Budżet H jest ograniczony liczbą osób chcących kontrolować wyniki twardej sztucznej inteligencji.
- Zaufane, słabe modele w końcu pozostają w tyle. Kiedy T jest znacznie słabsze niż U, sygnał edycyjny T staje się szumem.
- Kontrola to nie wyrównanie. Protokoły działające w ASL-3 (Lekcja 18) mogą nie działać w ASL-4 — jeśli U może manipulować T lub uzasadnić dystrybucję audytu H, kontrola kończy się niepowodzeniem.

### Rozwój na rok 2025

Brytyjskie AISI i Redwood współpracują w zakresie przypadków bezpieczeństwa kontroli (metr.org / redwoodresearch.org 2025): w przypadku bezpieczeństwa kontroli dowodzi się, że przy najgorszych założeniach dotyczących U protokół ogranicza prawdopodobieństwo nieakceptowalnego wyniku. Obudowy bezpieczeństwa (Lekcja 18) dziedziczą ramę sterującą.

### Gdzie to pasuje do fazy 18

Lekcje 6-9 opisują zagrożenie (oszustwo jest możliwe). Lekcja 10 opisuje paradygmat obronny przy założeniu, że zagrożenie jest realne. Lekcja 11 opisuje uzupełniający paradygmat ofensywny (uczynić U godnym zaufania poprzez skalowalny nadzór).

## Użyj tego

`code/main.py` symuluje cztery protokoły w zabawkowym zadaniu backdoora. U produkuje wyjścia; część jest backdoorem (polityka drużyny czerwonych). T zatwierdza lub edytuje. H nazywa się budżetem. Możesz przesunąć budżet i parametr zmowy, aby odtworzyć granicę Pareto w Greenblatt i in. 2024 Rysunek 2 (kształt, nie liczby).

## Wyślij to

Ta lekcja przedstawia `outputs/skill-control-protocol-audit.md`. Mając opis protokołu wdrożenia, identyfikuje role U/T/H, nazywa wektory zmowy i szacuje pozycję protokołu na granicy użyteczności i bezpieczeństwa pod presją czerwonego zespołu.

## Ćwiczenia

1. Uruchom `code/main.py`. Odtwórz granicę bezpieczeństwa użyteczności i bezpieczeństwa dla zaufanej edycji i niezaufanego monitorowania. Zidentyfikuj reżim budżetowy, w którym założenie zmowy niezaufanego monitorowania staje się kluczowe.

2. Dodaj nowy protokół: „T ponownie próbkuje w niskiej temperaturze, a następnie U edytuje wyjście T”. Zmierz jego położenie na granicy. Dlaczego to kończy się niepowodzeniem bardziej katastrofalnie niż zaufane edytowanie?

3. W artykule z 2024 r. założono, że można zapoznać się z protokołem. Zaprojektuj protokół, który ukrywa przed U, które wyjścia są kontrolowane. Czego ten protokół wymaga od infrastruktury wdrożeniowej?

4. Przeczytaj Greenblatt i in. 2024 § 7 (zmowa). Zaproponuj środek zapewniający odporność na zmowy i wyjaśnij jego oczekiwany koszt użyteczności.

5. Przedstaw uzasadnienie bezpieczeństwa kontroli dla wdrożenia, które wykorzystuje U = klasa GPT-4, T = klasa GPT-3.5, H = 1% audytowanych wyników. Zidentyfikuj najsilniejsze założenie, od którego zależy dany przypadek.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Kontrola AI | „bezpieczeństwo w obliczu dywersji” | Projekt protokołu ograniczający niedopuszczalne wyniki w najgorszym przypadku U |
| Niezaufany model (U) | „silny model” | Zdolny model, z którego chcemy wydobyć pracę, ale nie ufamy |
| Zaufany model (T) | „słaby model” | Słabszy model, znany z tego, że nie jest kontradyktoryjny, używany jako edytor/monitor |
| Zaufany człowiek (H) | „budżet kontroli” | Ograniczona praca ekspertów; drogi; sygnał prawdy |
| Zaufana edycja | „T edytuje U” | Protokół, w którym T jest bramką na wyjściach U; H wywołał niejednoznaczne wyniki |
| Niezaufane monitorowanie | „U monitoruje Cię” | Protokół, w którym druga instancja U ocenia wyniki; odporny na zmowy tylko przy dodatkowej inwestycji |
| Sprawa bezpieczeństwa kontroli | „argument formalny” | Pisemny argument, że protokół ogranicza sukces przeciwnika w najgorszym przypadku U |

## Dalsze czytanie

– [Greenblatt, Shlegeris, Sachan, Roger – AI Control (arXiv:2312.06942)](https://arxiv.org/abs/2312.06942) – kanoniczny artykuł ICML 2024
– [Redwood Research — indeks najnowszych dokumentów dotyczących kontroli AI] (https://redwoodresearch.substack.com/) — dalsze działania w latach 2024–2025
– [UK AISI + METR – Kontroluj przypadki bezpieczeństwa](https://metr.org/blog/2025-03-26-common-elements-of-frontier-ai-safety-policies/) – operacjonalizacja dla laboratoriów granicznych
- [Hubinger i in. — Uśpieni agenci (Lekcja 7, arXiv:2401.05566)](https://arxiv.org/abs/2401.05566) — zakłada się kontrolę modelu zagrożenia