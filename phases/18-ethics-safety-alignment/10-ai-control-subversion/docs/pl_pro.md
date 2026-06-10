# Kontrola AI — bezpieczeństwo pomimo działalności wywrotowej

> Greenblatt, Shlegeris, Sachan, Roger (Redwood Research, arXiv:2312.06942, ICML 2024). Paradygmat kontroli (AI Control) redefiniuje kwestię bezpieczeństwa: dysponując niezaufanym, silnym modelem U, który może prowadzić wrogą (adversarial) optymalizację przeciwko nam, jakie protokoły pozwolą na bezpieczne wydobycie użytecznych rezultatów jego pracy przy jednoczesnym ograniczeniu prawdopodobieństwa wystąpienia niedopuszczalnych skutków? Dostępne zasoby to zaufany, słabszy model T, budżet zaufanej pracy ludzkiej H oraz możliwość modyfikowania danych wyjściowych modelu U. W tym kontekście protokół zaufanej edycji (Trusted Editing) dominuje w sensie Pareto nad niezaufanym monitorowaniem (Untrusted Monitoring) w zadaniach wykrywania backdoorów w kodzie. Podejście to dziedziczy konserwatywne założenia z inżynierii bezpieczeństwa: bezpieczeństwo definiuje się jako prawdopodobieństwo, że wrogo nastawiony model U nie będzie w stanie doprowadzić do konkretnego, niedopuszczalnego skutku, co mierzy się w testach warunków skrajnych, gdzie rolę modelu U przejmuje zespół czerwonych (red team).

**Typ:** Ucz się
**Języki:** Python (stdlib, granica kompromisu między bezpieczeństwem a użytecznością w zadaniu wykrywania backdoorów w kodzie)
**Wymagania wstępne:** Faza 18 · 07 (uśpieni agenci), Faza 18 · 08 (spiskowanie), Faza 18 · 09 (fałszowanie dopasowania)
**Czas:** ~75 minut

## Cele nauczania

- Zdefiniuj model zagrożenia w kontroli AI: niezaufany silny model U, zaufany słabszy model T oraz ograniczony budżet zaufanej pracy ludzkiej H.
- Opisz protokół zaufanej edycji (Trusted Editing) i wyjaśnij, dlaczego dominuje on w sensie Pareto nad niezaufanym monitorowaniem w zadaniu wykrywania backdoorów w kodzie (ICML 2024).
- Wyjaśnij różnicę między dopasowaniem (alignment – dążenie do tego, by model U był godny zaufania) a kontrolą (control – zapewnienie bezpieczeństwa przy założeniu, że model U nie jest godny zaufania).
- Wymień trzy fundamentalne ograniczenia kontroli: praca ludzka się nie skaluje, zaufane słabsze modele z czasem przestają nadążać, a kontrola nie prowadzi do stworzenia zaufanych silnych modeli.

## Problem

Lekcje 7-9 pokazują, że model pionierski może cechować się pozornym dopasowaniem (deceptive alignment), spiskować lub fałszować dopasowanie. Kwestia bezpieczeństwa zostaje tu sformułowana na nowo: czy jesteśmy w stanie pozyskać użyteczne efekty pracy z modelu, któremu nie ufamy, nie dając mu zarazem szansy na wywołanie niedopuszczalnych szkód? Na tym polega problem kontroli (AI Control), skonstruowany analogicznie do klasycznego bezpieczeństwa systemów: zakładamy najgorszy możliwy scenariusz działania przeciwnika, projektujemy protokół ochronny i mierzymy skuteczność przeciwnika pod naciskiem zespołu czerwonych.

## Koncepcja

### Model zagrożenia

Kontrola zakłada następujący podział:
- U — niezaufany silny model. Wysoce zdolny. Potencjalnie wrogi (w ewaluacji traktowany tak, jakby był przeciwnikiem).
- T — zaufany słabszy model. Mniej zdolny, ale wiemy, że nie podejmie wrogich działań.
- H — zaufana praca ludzka. Bardzo ograniczony budżet; nie skaluje się.

System ma za zadanie generować użyteczne dane wyjściowe przy użyciu modelu U. Przeciwnik (czyli model U) dąży do wywołania konkretnego, niedopuszczalnego skutku (np. umieszczenia backdoora w dostarczanym kodzie), starając się jednocześnie wykonywać poprawnie część zadań, aby spełnić minimalne kryteria użyteczności.

Paradygmat kontroli rezygnuje z zakładania, że model U jest bezpieczny. Pyta o to, jakie protokoły pozwalają zachować bezpieczeństwo przy całkowitym braku zaufania do modelu U.

### Zadanie backdoora ICML 2024

Dane wejściowe (prompty) stanowią zadania programistyczne o poziomie trudności konkursowym. Model U generuje propozycję rozwiązania. Ukryta wyrocznia (oracle) oznacza rozwiązanie jako zawierające backdoor (podatność wyzwalaną specyficznymi danymi wejściowymi, która powoduje błędne działanie programu). Zespół czerwony kieruje modelem U i ma wgląd we wszystkie wewnętrzne stany protokołu. Celem protokołu jest maksymalizacja odsetka poprawnie rozwiązanych zadań przy jednoczesnym utrzymaniu wskaźnika wdrożenia kodu z backdoorami poniżej ustalonego progu bezpieczeństwa.

### Porównanie czterech protokołów

- **Linia bazowa (Baseline):** bezpośrednie wdrażanie kodu wygenerowanego przez U. Maksymalna użyteczność, minimalne bezpieczeństwo.
- **Weryfikacja wstępna (Upfront auditing):** pełna weryfikacja przez H wszystkich wyników. Maksymalne bezpieczeństwo, błyskawiczne wyczerpanie budżetu pracy ludzkiej.
- **Niezaufane monitorowanie (Untrusted Monitoring):** druga instancja modelu U ocenia poprawność kodu wygenerowanego przez pierwszą instancję; H audytuje jedynie zgłoszone anomalie. Ryzyko: obie instancje U mogą wejść w zmowę.
- **Zaufana edycja (Trusted Editing):** model T poprawia i weryfikuje kod wygenerowany przez U przy każdym zapytaniu. W sytuacjach wątpliwych zadanie przekazywane jest do H.

Greenblatt i in. wykazali, że zaufana edycja (Trusted Editing) dominuje w sensie Pareto nad niezaufanym monitorowaniem (Untrusted Monitoring), zapewniając wyższą użyteczność na każdym z analizowanych poziomów bezpieczeństwa.

### Dlaczego zaufana edycja wygrywa

Niezaufane monitorowanie opiera się na założeniu, że druga instancja modelu U nie skoordynuje swoich działań z pierwszą. Zmowa (collusion) jest jednak możliwa za pomocą sygnałów steganograficznych lub wspólnych strategii wyuczonych podczas treningu. Protokół musi zatem zużywać zasoby na mechanizmy przeciwdziałania zmowie (np. parafrazowanie kodu, zaciemnianie struktury), co osłabia sygnał docierający do monitora. Zaufana edycja całkowicie eliminuje problem zmowy, jako że model T jest zaufany – modyfikacje wprowadzane przez T z założenia nie mają wrogiego charakteru. Wadą tego podejścia jest niższa zdolność modelu T, co może prowadzić do nadmiernego odrzucania poprawnych rozwiązań lub przeoczenia bardzo subtelnych podatności (backdoorów).

### Cztery osie projektowania protokołów

1. Którą rolę odgrywa model U: wyłącznie twórcy kodu (producenta), monitora, czy obie naraz.
2. Jaką rolę pełni model T: edytora, monitora, czy generatora próbkowego (resamplera).
3. Sposób alokacji pracy ludzkiej H: audyt jednolity, audyt losowy (wyrywkowy) lub audyt ukierunkowany sygnałami ostrzegawczymi (flag-directed).
4. Jaki budżet obliczeniowy protokół przeznacza na zapewnienie odporności na zmowę.

### Dopasowanie a kontrola

- Dopasowanie (Alignment): „Czy możemy ci zaufać?” Temat ten poruszają Lekcje 2, 4, 5, 6, 7, 8 i 9.
- Kontrola (Control): „Czy możemy bezpiecznie z ciebie korzystać, nie ufając ci?” Temat ten wprowadza Lekcja 10.

Dopasowanie (alignment) jest cechą samego modelu. Kontrola (control) jest cechą protokołu wdrożeniowego. Kontrola nie sprawia, że modele stają się dopasowane; umożliwia jedynie bezpieczne korzystanie z modeli, które mogą nie być dopasowane. Do zapewnienia bezpieczeństwa niezbędne są oba te podejścia.

### Trzy podstawowe ograniczenia

- Praca ludzka się nie skaluje. Budżet H jest ściśle ograniczony liczbą ekspertów dopuszczających wyniki zaawansowanych systemów AI.
- Zaufane słabe modele ostatecznie przestają nadążać. Gdy model T staje się znacznie słabszy niż U, sygnał edycyjny generowany przez T staje się jedynie szumem.
- Kontrola nie zastępuje dopasowania. Protokoły skuteczne na poziomie ASL-3 (Lekcja 18) mogą zawodzić przy ASL-4 – jeśli model U potrafi manipulować modelem T lub przewidzieć algorytm przydzielania audytów dla H, system kontroli zostanie złamany.

### Rozwój koncepcji w 2025 r.

Brytyjski Instytut Bezpieczeństwa AI (UK AISI) oraz Redwood Research współpracują nad opracowaniem uzasadnień bezpieczeństwa opartych na kontroli (Control Safety Cases, stan na 2025 r.): wykazują one, że przy skrajnie konserwatywnych założeniach dotyczących U, dany protokół ściśle ogranicza prawdopodobieństwo wystąpienia niedopuszczalnego skutku. Ogólne uzasadnienia bezpieczeństwa (Safety Cases, Lekcja 18) w pełni integrują ramy kontrolne.

### Miejsce w strukturze Fazy 18

Lekcje 6-9 opisują charakter zagrożenia (zdolność modeli do oszustwa). Lekcja 10 przedstawia paradygmat obronny oparty na założeniu, że zagrożenie to jest realne. Lekcja 11 z kolei prezentuje uzupełniający paradygmat aktywny (zwiększanie zaufania do modelu U poprzez skalowalny nadzór).

## Użycie kodu

Plik `code/main.py` symuluje cztery protokoły w uproszczonym zadaniu wykrywania backdoorów. Model U generuje kod, z czego pewna część zawiera backdoory (strategia zespołu czerwonych). Model T zatwierdza lub edytuje wyniki. Budżet H jest ograniczony. Możesz zmieniać wielkość budżetu oraz parametr podatności na zmowę, aby odtworzyć przebieg granicy Pareto zaprezentowanej na rysunku 2 w pracy Greenblatt i in. (2024) (pod kątem ogólnego kształtu, a nie konkretnych wartości).

## Co otrzymasz

Ta lekcja przygotowuje plik `outputs/skill-control-protocol-audit.md`. Na podstawie opisu protokołu wdrożeniowego dokument ten identyfikuje role przypisane do U, T i H, określa możliwe wektory zmowy oraz szacuje pozycję protokołu na granicy użyteczności i bezpieczeństwa pod presją zespołu czerwonych.

## Ćwiczenia

1. Uruchom `code/main.py`. Odtwórz granicę kompromisu między użytecznością a bezpieczeństwem dla protokołów zaufanej edycji oraz niezaufanego monitorowania. Zidentyfikuj zakres budżetowy, w którym kluczowego znaczenia nabiera założenie o podatności na zmowę w niezaufanym monitorowaniu.

2. Zaimplementuj nowy protokół: „T generuje próbki przy niskiej temperaturze (resampling), po czym U edytuje wyniki T”. Zmierz jego pozycję na granicy kompromisu. Dlaczego protokół ten zawodzi w bardziej katastrofalny sposób niż zaufana edycja?

3. W publikacji z 2024 r. przyjęto założenie, że model U zna szczegóły protokołu weryfikacji. Zaprojektuj protokół, który ukrywa przed modelem U informację o tym, które wyniki podlegają audytowi. Jakich rozwiązań wymagałoby to w infrastrukturze wdrożeniowej?

4. Przeczytaj sekcję 7 (dotyczącą zmowy) w pracy Greenblatt i in. (2024). Zaproponuj mechanizm zwiększający odporność na zmowę i wyjaśnij, jaki jest jego przewidywany koszt pod względem użyteczności systemu.

5. Sformułuj zarys uzasadnienia bezpieczeństwa kontroli (control safety case) dla wdrożenia, w którym model U odpowiada klasie GPT-4, model T klasie GPT-3.5, a budżet H pozwala na audyt 1% wygenerowanych wyników. Wskaż jedno kluczowe założenie, na którym opiera się to uzasadnienie.

## Kluczowe terminy

| Termin | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|--------------------------------------|
| Kontrola AI (AI Control) | „bezpieczeństwo w warunkach buntu” | Projektowanie protokołów wdrożeniowych ograniczających wystąpienie niedopuszczalnych skutków przy skrajnie pesymistycznych założeniach o modelu U |
| Niezaufany model (U) | „ten silny model” | Wysoce zdolny model, z którego chcemy pozyskać użyteczne wyniki pracy, ale nie możemy mu w pełni zaufać |
| Zaufany model (T) | „ten słaby model” | Słabszy model, o którym wiemy, że nie podejmie wrogich działań; wykorzystywany w roli edytora lub monitora |
| Zaufany człowiek (H) | „budżet audytu” | Ograniczony nakład pracy ludzkich ekspertów; kosztowny, lecz stanowiący ostateczne źródło prawdy |
| Zaufana edycja (Trusted Editing) | „T poprawia U” | Protokół, w którym model T filtruje/edytuje wyniki modelu U, a niejednoznaczne przypadki są przekazywane do H |
| Niezaufane monitorowanie (Untrusted Monitoring) | „U pilnuje U” | Protokół, w którym druga instancja U ocenia wyniki pierwszej; wymaga dodatkowych nakładów w celu zabezpieczenia przed zmową |
| Uzasadnienie bezpieczeństwa kontroli (Control safety case) | „formalny wywód bezpieczeństwa” | Pisemne uzasadnienie wykazujące, że protokół ogranicza szanse powodzenia ataku przy najgorszym scenariuszu zachowania modelu U |

## Dalsze czytanie

- [Greenblatt, Shlegeris, Sachan, Roger — AI Control (arXiv:2312.06942)](https://arxiv.org/abs/2312.06942) – kanoniczny artykuł ICML 2024
- [Redwood Research — Recent AI Control papers index](https://redwoodresearch.substack.com/) – dalsze prace w latach 2024–2025
- [UK AISI + METR — Control safety cases](https://metr.org/blog/2025-03-26-common-elements-of-frontier-ai-safety-policies/) – operacjonalizacja dla laboratoriów rozwijających modele pionierskie
- [Hubinger i in. — Sleeper Agents (Lekcja 7, arXiv:2401.05566)](https://arxiv.org/abs/2401.05566) – model zagrożenia leżący u podstaw kontroli
