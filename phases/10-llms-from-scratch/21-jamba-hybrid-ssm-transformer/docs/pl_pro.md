# Jamba — hybrydowy transformator SSM

> Modele przestrzeni stanów (SSM) i transformatory realizują odmienne cele. Transformatory osiągają wysoką jakość dzięki mechanizmowi uwagi, lecz kosztem kwadratowej złożoności obliczeniowej. SSM zapewniają wnioskowanie w czasie liniowym i stałe zużycie pamięci, jednak kosztem utraty części jakości powtarzania. Jamba (marzec 2024 r.) oraz Jamba 1.5 (sierpień 2024 r.) firmy AI21 łączą oba podejścia w jednym modelu: 1 warstwa transformatora na każde 7 warstw Mamby, MoE co drugi blok i okno kontekstowe o pojemności 256 tys. tokenów, które mieści się na pojedynczym procesorze graficznym 80 GB. Mamba-3 (ICLR 2026) wzmacnia stronę SSM dzięki przestrzeniom stanów o wartościach zespolonych i projekcjom MIMO. Niniejsza lekcja omawia obie architektury od podstaw i wyjaśnia, dlaczego receptura hybrydowa przetrwała trzy lata skalowania, podczas gdy podejścia oparte na czystym SSM i czystym Transformerze nie sprawdziły się w długich kontekstach.

**Typ:** Ucz się
**Języki:** Python (stdlib, kalkulator miksu warstw)
**Wymagania wstępne:** Faza 10 · 14 (architektury modelu otwartego), Faza 10 · 17 (natywna uwaga rzadka)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnij trzy elementy składowe bloku Jamba — warstwy transformatora, warstwy Mamby, MoE — oraz zasadę przeplatania 1:7.
- Opisz na poziomie ogólnym zasadę działania rekurencji SSM i wyjaśnij, dlaczego umożliwia wnioskowanie przy stałym zużyciu pamięci.
- Oblicz rozmiar pamięci podręcznej KV modelu Jamba w kontekście 256 tys. tokenów i porównaj go z analogicznym modelem opartym wyłącznie na Transformerze.
- Wymień trzy innowacje Mamba-3 (dyskretyzacja wykładniczo-trapezoidalna, aktualizacja stanu o wartościach zespolonych, MIMO) i wskaż problem, który każda z nich rozwiązuje.

## Problem

Złożoność mechanizmu uwagi jest kwadratowa względem długości sekwencji, a modeli przestrzeni stanów — liniowa. Różnica ta jest ogromna: przy 256 tys. tokenów mapa uwagi Transformatora zawiera 65 miliardów wpisów na głowę, natomiast stan rekurencyjny SSM ma stały rozmiar niezależnie od długości sekwencji.

Modele Pure-SSM (Mamba, Mamba-2) dorównują Transformerom pod względem złożoności przy mniejszych rozmiarach, lecz ustępują im w zadaniach śledzenia stanu i zawodzą w niektórych kategoriach wyszukiwania w kontekście. Intuicja jest następująca: SSM kompresują historię do stałego stanu, a przy długich sekwencjach informacje się tracą. Uwaga przechowuje wszystko dokładnie, ale płaci za to kwadratową cenę obliczeniową.

Naturalne rozwiązanie polega na połączeniu obu podejść. Warstwy Transformera stosuje się tam, gdzie liczy się dokładne przywoływanie. Warstwy SSM obsługują pozostałą część przetwarzania. Proporcje dobiera się empirycznie. Jamba to pierwszy model klasy produkcyjnej, który wcielił tę hybrydową recepturę na dużą skalę (łącznie 52B, 12B aktywnych, kontekst 256 tys., pojedynczy procesor graficzny 80 GB). Jamba 1.5 rozszerza rodzinę do 398B łącznie i 94B aktywnych. Mamba-3 (ICLR 2026) wyznacza aktualnie najwyższy punkt odniesienia wśród architektur czystego SSM, wokół którego można budować kolejne hybrydy.

W trakcie tej lekcji omówione zostaną wszystkie trzy artykuły, a czytelnik wypracuje model myślowy dotyczący doboru właściwych proporcji.

## Koncepcja

### SSM na jednej stronie

Model przestrzeni stanów przetwarza sekwencję `x_1, ..., x_N` poprzez stan o stałym rozmiarze `h`:

```
h_t = A h_{t-1} + B x_t
y_t = C h_t
```

Na każdym kroku stan ewoluuje zgodnie z liniową dynamiką `A`, pobiera wejście `B x_t` i emituje wyjście `C h_t`. Macierze `A, B, C` są wyuczalne. Kluczowa właściwość: obliczenie `y_t` wymaga wyłącznie `h_{t-1}` i `x_t`, nie zaś wcześniejszych tokenów `x`. Pamięć jest stała, a wnioskowanie ma złożoność O(1) na token.

Jakość modelowania zależy od struktury `A`. W S4 (Gu 2021) zastosowano wysoce ustrukturyzowaną macierz, którą można było efektywnie obliczać jako długi splot podczas treningu. Mamba (Gu, Dao 2023) zastąpiła stałe parametry `A, B, C` elementami zależnymi od danych — stąd pochodzi określenie „selektywna". Mamba-2 (2024) uprościła tę konstrukcję, natomiast Mamba-3 (2026) ponownie wprowadza złożoność w wybranych miejscach.

Zasadnicze znaczenie ma następująca właściwość: w dekoderze LLM warstwa SSM stanowi bezpośredni zamiennik warstwy uwagi, przy czym każda warstwa dysponuje stanem o stałym rozmiarze zamiast rosnącej pamięci podręcznej KV.

### Blok Jamby

Blok Jamba przeplata warstwy według dwóch parametrów:

- `l`: stosunek uwagi do Mamby. Jamba używa `l = 8`, co oznacza 1 warstwę Transformatora na każde 7 warstw Mamby (7 Mamba + 1 Uwaga = 8 warstw na grupę).
- `e`: częstotliwość MoE. Jamba używa `e = 2`, co oznacza, że MoE stosuje się co drugą warstwę.

Kolejność warstw w bloku:

```
M  M  M  M  M  M  M  A    (7 Mamba + 1 Attention)
|  M  |  M  |  M  |  M    (where | marks MoE applied)
```

Jeden blok Jamba składa się z 8 warstw. Przy głębokości 4 bloków (łącznie 32 warstwy) otrzymuje się 28 warstw Mamba i 4 warstwy uwagi, z czego 16 korzysta z MoE.

### Dlaczego współczynnik 1:7

AI21 przeprowadził ablacje, szukając stosunku uwagi do Mamby, który zapewnia najlepsze wyniki pod względem perplexity na parametr oraz zdolności do przywoływania informacji w długim kontekście.

- Za dużo uwagi (1:1): jakość rośnie, ale pamięć i szybkość się pogarszają.
- Za mało uwagi (1:15): pamięć jest dobra, ale wyszukiwanie w kontekście zawodzi.
- Optimum: 1:7 lub 1:8.

Intuicja jest prosta: warstwy Transformera obsługują dokładne przywoływanie i śledzenie stanu, a warstwy Mamby — tańszą większość przetwarzania.

### Kodowanie pozycyjne

Warstwy Mamby kodują pozycję implicite, przez rekurencję. Warstwy uwagi w pierwotnych hybrydach opartych na Mambie nie korzystały z RoPE — informację o pozycji dostarczały warstwy SSM. Jamba 1.5 dodaje RoPE do warstw uwagi w celu lepszej generalizacji na dłuższe konteksty; zmiana ta wynikła z empirycznej oceny zachowania modelu w długim kontekście.

### Budżet pamięci

Dla konfiguracji Jamba-1 (32 warstwy: 28 Mamba + 4 Uwaga, wymiar ukryty 4096, 32 głowy uwagi):

- Pamięć podręczna KV (tylko warstwy uwagi): `2 * 4 * 32 * 128 * 256k * 2 = 8.4 GB` przy 256 tys. tokenów w formacie BF16. Jedynie 4 warstwy uwagi ją zasilają.
- Stan SSM: `28 * hidden * state_size` na prefiks tokena, przy czym rozmiar jest stały dla każdej warstwy i nie rośnie wraz z długością sekwencji. Typowy stan Mamby wynosi 16 na cechę, wymiar ukryty 4096: łącznie `28 * 4096 * 16 * 2 = 3.7 MB`.

Dla porównania — czysty Transformer z 32 warstwami, tym samym wymiarem ukrytym i pełnym MHA przy 32 głowach: `2 * 32 * 32 * 128 * 256k * 2 = 128 GB` przy 256 tys. tokenów w BF16. Oznacza to 8-krotne zmniejszenie pamięci podręcznej KV. Nawet w porównaniu z bazowym GQA(8), z którego korzysta większość modeli z roku 2024 (`2 * 32 * 8 * 128 * 256k * 2 = 32 GB`), hybryda Jamby w stosunku 1:7 przy 16 GB jest dwukrotnie oszczędniejsza.

Właśnie to ma na myśli AI21, mówiąc o „kontekście 256 tys. na pojedynczym procesorze graficznym 80 GB". Pamięć podręczna KV czystego Transformatora z pełnym MHA nie zmieściłaby się w tej pamięci; nawet wariant GQA nie zostawiałby miejsca na wagi i aktywacje. Jamba mieści się.

### Mamba-3: punkt odniesienia czystego SSM w 2026 r.

Mamba-3 (ICLR 2026, arXiv:2603.15569) wprowadza trzy innowacje po stronie czystego SSM:

1. **Dyskretyzacja wykładniczo-trapezowa.** Zastępuje dyskretyzację metodą Eulera z Mamba-2 bardziej ekspresywną rekurencją. Operacja przypominająca splot jest stosowana na wejściu stanu w ramach rekurencji rdzeniowej, a nie jako zewnętrzny splot na `x_t`.

2. **Aktualizacja stanu o wartościach zespolonych.** Poprzednie warianty Mamby stopniowo upraszczały macierz stanu: od zespolonej (S4), przez rzeczywistą przekątną (Mamba), po tożsamość skalowaną (Mamba-2). Mamba-3 przywraca wartości zespolone, co odpowiada zależnemu od danych osadzaniu obrotowemu stanu. Dzięki temu odzyskuje się zdolności śledzenia stanu utracone w wyniku wcześniejszych uproszczeń.

3. **Projekcje MIMO (wielowejściowe i wielowyjściowe).** Zamiast skalarnych projekcji dla poszczególnych cech stosuje się projekcje oparte na macierzach. Zwiększa to moc modelowania i efektywność sprzętową podczas wnioskowania bez wzrostu opóźnień dekodowania.

Przy 1,5B parametrów Mamba-3 poprawia średnią dokładność odczytu o 0,6 punktu w porównaniu z bramkowaną siecią DeltaNet; wariant MIMO dodaje kolejne 1,2 punktu, co daje łączny wzrost o 1,8 punktu. Przy tym samym rozmiarze stanu Mamba-3 dorównuje Mambie-2 korzystającej z dwukrotnie większego stanu.

Mamba-3 nie jest jeszcze dostępna w produkcyjnym wariancie hybrydowym na dużą skalę, ale jest oczywistym kandydatem na stronę SSM w kolejnym modelu klasy Jamba.

### Kiedy sięgnąć po hybrydę

Hybrydy wygrywają, gdy:

- Kontekst jest na tyle długi, że czysta pamięć podręczna KV Transformatora staje się problematyczna (64 tys. tokenów i więcej).
- Zadania łączą przetwarzanie krótkich zależności (dobre dla SSM) z przywoływaniem informacji z odległych pozycji (wymaga Transformatora).
- Wdrożenie musi zmieścić się w budżecie pamięci jednego procesora graficznego, w którym sama pamięć podręczna KV Transformatora by nie weszła.

Hybrydy przegrywają, gdy:

- Kontekst jest krótki (poniżej 16 tys. tokenów). Narzut SSM jest wówczas zbędny; czysty Transformer sprawdza się lepiej.
- Zadania wymagają uwagi globalnej (głębokie rozumowanie, odsyłacze między wieloma dokumentami). Niedobór warstw uwagi w hybrydzie staje się wtedy odczuwalny.
- Model skaluje się do bilionów parametrów. W takim przypadku architektura Pure-Transformer + MLA + MoE (wzorowana na DeepSeek-V3) aktualnie dominuje w wyścigu możliwości.

### Krajobraz konkurencyjny

| Model | Rodzina | Skala | Wyróżnik |
|-------|-------|------|------------|
| Mamba-2 | czysty SSM | 3B | czas liniowy, stała pamięć |
| Jamba | hybrydowy | 52B/12B | 256 tys. tokenów na 80 GB |
| Jamba 1.5 Large | hybrydowy | 398B/94B | długi kontekst klasy korporacyjnej |
| Mamba-3 | czysty SSM | 1,5B (artykuł) | przywrócone śledzenie stanu |
| DeepSeek-V3 | czysty Transformer + MoE | 671B/37B | możliwości na poziomie granicy |

Stan na rok 2026: na granicy dominują architektury MoE oparte wyłącznie na Transformerach, jednak nisza długich kontekstów powyżej 256 tys. tokenów pozostaje domeną hybryd. Sukcesy Mamba-3 w śledzeniu stanu mogą przesunąć proporcje hybrydowe w kierunku większego udziału SSM i mniejszego udziału uwagi w kolejnej generacji.

## Użyj tego

`code/main.py` to kalkulator pamięci dla architektur hybrydowych. Na podstawie zadanego współczynnika SSM-Transformer oraz konfiguracji wymiaru ukrytego i liczby warstw oblicza:

- rozmiar pamięci podręcznej KV przy docelowej długości kontekstu,
- rozmiar stanu SSM,
- łączne zużycie pamięci w kontekście N dla różnych konfiguracji modeli.

Kalkulator obsługuje trzy warianty:

- Bazowy Pure-Transformer (pamięć podręczna KV rośnie liniowo z N).
- Hybryda 1:7 w stylu Jamba.
- Pure-SSM (brak pamięci podręcznej KV).

Wartości liczbowe pochodzą bezpośrednio z artykułów Jamba-1 i Jamba-1.5 dla opublikowanych konfiguracji i zostały ekstrapolowane dla hipotetycznych wariantów.

Uwagi dotyczące integracji przy rzeczywistym wdrożeniu:

- Większość produkcyjnych serwerów wnioskowania (vLLM, SGLang) obsługuje Jambę i Mambę. Należy zweryfikować konkretną wersję.
- W kontekście 256 tys. tokenów przewaga pamięciowa Jamby ujawnia się w przepustowości przy równoległych żądaniach. W tej samej puli VRAM mieści się więcej sekwencji Jamba niż sekwencji Transformer.
- Mamba-3 jako samodzielny model nie jest jeszcze dostępna produkcyjnie — to wersja badawcza na poziomie 1,5B parametrów.

## Wyślij to

Wynikiem tej lekcji jest plik `outputs/skill-hybrid-picker.md`. Na podstawie specyfikacji obciążenia (profil długości kontekstu, zestaw zadań, budżet pamięci) należy zarekomendować wybór pomiędzy czystym Transformerem, hybrydą w stylu Jamba i czystym SSM, uzasadniając decyzję kompromisami dotyczącymi pamięci i jakości.

## Ćwiczenia

1. Uruchom `code/main.py`, aby obliczyć pamięć podręczną KV w kontekście 256 tys. tokenów dla 32-warstwowego czystego Transformatora (wymiar ukryty 4096, 32 głowy) oraz dla hybrydy Jamba-1 o tym samym kształcie. Zweryfikuj deklarowaną przez AI21 redukcję pamięci rzędu ~8x.

2. Zmodyfikuj kalkulator tak, aby modelował hybrydę 1:3 (4 Mamba: 1 Uwaga) i hybrydę 1:15 (14 Mamba: 1 Uwaga). Wykreśl rozmiar pamięci podręcznej KV w funkcji stosunku. Przy jakim stosunku pamięć podręczna KV jest równa pamięci stanu SSM?

3. Przeczytaj sekcję 3 artykułu Jamba (arXiv:2403.19887). Wyjaśnij, dlaczego AI21 używa Mamby-1 zamiast Mamby-2, mimo że Mamba-2 jest szybsza. Wskazówka: odpowiedź zawiera sekcja dotycząca ablacji hybrydowych.

4. Oblicz narzut parametrów MoE dla co drugiej warstwy w Jamba 1.5 Large (398B łącznie, 94B aktywnych). Porównaj współczynnik aktywności z DeepSeek-V3 (37B/671B) i wyjaśnij, dlaczego architektura Jamby osiąga wyższy współczynnik aktywności.

5. Przeczytaj sekcję 3 artykułu Mamba-3 (arXiv:2603.15569). Wyjaśnij w trzech zdaniach, dlaczego aktualizacja stanu o wartościach zespolonych jest równoważna zależnemu od danych osadzaniu obrotowemu. Powiąż odpowiedź z wyprowadzeniem RoPE z lekcji Fazy 7 · 04.

## Kluczowe terminy

| Termin | Co mówią praktycy | Co to faktycznie oznacza |
|------|----------------|--------------------------------------|
| Model przestrzeni stanów (SSM) | „Rekurencja o stałym stanie" | Warstwa z wyuczoną rekurencją `h_t = A h_{t-1} + B x_t`; stała pamięć na token |
| Selektywny SSM | „Sztuczka Mamby" | Parametry A, B, C zależne od danych, które nadają modelowi selektywność bramkującą przy liniowej złożoności |
| Stosunek uwagi do Mamby | „Ile warstw uwagi" | W Jambie `l = 8` oznacza 1 warstwę uwagi na 7 warstw Mamby |
| Blok Jamby | „Grupa 8-warstwowa" | Jedna uwaga + siedem Mamb + MoE na przemiennych pozycjach |
| Stan SSM | „Ukryty bufor" | Stan warstwy o stałym rozmiarze, który zastępuje pamięć podręczną KV dla warstw Mamba |
| Kontekst 256 tys. | „Flagowa liczba Jamby" | Długość sekwencji Jamba-1, która mieści się na pojedynczym procesorze graficznym 80 GB; czysty Transformer przy tej długości nie wchodzi w grę |
| Mamba-3 | „Czysty SSM 2026" | Wiodąca architektura czystego SSM ze stanem zespolonym i MIMO; podstawa nowych hybryd |
| MIMO | „Wiele wejść, wiele wyjść" | Innowacja Mamba-3 polegająca na macierzowych projekcjach zamiast skalarnych na cechę |
| Dyskretyzacja wykładniczo-trapezowa | „Powrót Mamby-3" | Bardziej ekspresywna rekurencja, obejmująca dyskretyzację metodą Eulera z Mamby-2 |
| Architektura hybrydowa | „Połączenie uwagi i SSM" | Każdy model przeplatający warstwy Transformatora i SSM; Jamba to wzorcowy przykład produkcyjny |

## Dalsze czytanie

- [Lieber i in. — Jamba: A Hybrid Transformer-Mamba Language Model (arXiv:2403.19887)](https://arxiv.org/abs/2403.19887) — oryginalny artykuł o Jambie, ablacje współczynników, wyniki dla kontekstu 256 tys. tokenów
- [AI21 — Jamba 1.5: Hybrid Transformer-Mamba at Scale (arXiv:2408.12570)](https://arxiv.org/abs/2408.12570) — rozszerzona rodzina, publiczne warianty 398B/94B i 12B/52B
- [Gu, Dao — Mamba: Linear-Time Sequence Modeling with Selective State Spaces (arXiv:2312.00752)](https://arxiv.org/abs/2312.00752) — artykuł o selektywnym SSM, na którym opiera się Jamba
- [Dao, Gu — Mamba-2 (arXiv:2405.21060)](https://arxiv.org/abs/2405.21060) — uproszczony następca z przestrzeniami strukturalnymi
- [Lahoti i in. — Mamba-3 (arXiv:2603.15569, ICLR 2026)](https://arxiv.org/abs/2603.15569) — stan zespolony, MIMO, granica czystego SSM w 2026 r.
- [Gu i in. — Efficiently Modeling Long Sequences with Structured State Spaces (arXiv:2111.00396)](https://arxiv.org/abs/2111.00396) — artykuł S4, punkt wyjścia genealogii SSM dla LLM
