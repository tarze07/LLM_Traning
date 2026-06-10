# Jamba — hybrydowy transformator SSM

> Modele przestrzeni stanów (SSM) i transformatory chcą różnych rzeczy. Transformatory kupują jakość poprzez uwagę po kosztach kwadratowych. SSM kupują wnioskowanie w czasie liniowym i stałą pamięć poprzez jakość powtarzania, ale z opóźnieniem. Jamba (marzec 2024 r.) i Jamba 1.5 (sierpień 2024 r.) AI21 umieszczają je w tym samym modelu: 1 warstwa transformatora na każde 7 warstw Mamby, MoE na co drugim bloku i okno kontekstowe o pojemności 256 tys., które mieści się na pojedynczym procesorze graficznym o pojemności 80 GB. Mamba-3 (ICLR 2026) wzmacnia stronę SSM za pomocą przestrzeni stanów o wartościach zespolonych i projekcji MIMO. W tej lekcji omówiono obie architektury od początku do końca i wyjaśniono, dlaczego receptura hybrydowa przetrwała trzy lata skalowania, podczas gdy próby długiego kontekstu wykorzystujące czysty SSM i czysty Transformer nie przetrwały.

**Typ:** Ucz się
**Języki:** Python (stdlib, kalkulator miksu warstw)
**Wymagania wstępne:** Faza 10 · 14 (architektury modelu otwartego), Faza 10 · 17 (natywna uwaga rzadka)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnij trzy elementy podstawowe w bloku Jamba — warstwy transformatora, warstwy Mamby, MoE — i przepis na przeplatanie parzyste 1:7.
- Określ, jak wygląda powtarzalność SSM na wysokim poziomie i dlaczego umożliwia wnioskowanie w oparciu o stałą pamięć.
- Oblicz wielkość pamięci podręcznej KV modelu Jamba w kontekście 256 KB i porównaj z potrzebami modelu opartego wyłącznie na Transformatorze.
- Wymień trzy innowacje Mamba-3 (dyskretyzacja wykładniczo-trapezoidalna, aktualizacja stanu o wartościach zespolonych, MIMO) i problem, którego dotyczy każda z nich.

## Problem

Uwaga ma kwadratową długość sekwencji. Modele przestrzeni stanów są liniowe. Ta różnica jest jeszcze większa: przy 256 tys. tokenów mapa uwagi Transformatora zawiera 65 miliardów wpisów na głowę; stan powtarzający się SSM ma stały rozmiar niezależnie od długości sekwencji.

Modele Pure-SSM (Mamba, Mamba-2) dorównują złożoności transformatora w małych skalach, ale opóźniają się w zadaniach śledzenia stanu i nie radzą sobie z niektórymi kategoriami wyszukiwania w kontekście. Intuicja: SSM kompresują historię do ustalonego stanu, a gdy historia jest długa, informacje wyciekają. Uwaga pamięta wszystko dokładnie, ale płaci kwadratowy koszt.

Oczywista poprawka: użyj obu. Umieść warstwy Transformera tam, gdzie liczy się dokładne przypomnienie. Użyj warstw SSM gdzie indziej. Dostosuj proporcje. Jamba to pierwszy model klasy produkcyjnej, który udostępnia tę hybrydową recepturę na dużą skalę (łącznie 52B, 12B aktywnych, 256 tys. kontekstu, pojedynczy procesor graficzny 80 GB). Jamba 1.5 rozszerza rodzinę do 398B łącznie / 94B aktywnych. Mamba-3 (ICLR 2026) to obecnie najlepszy punkt odniesienia oparty na czystym SSM, wokół którego można odbudować hybrydy.

Podczas tej lekcji czytane są wszystkie trzy artykuły i powstaje mentalny model „wybierania właściwych proporcji”.

## Koncepcja

### SSM na jednej stronie

Model przestrzeni stanów przetwarza sekwencję `x_1, ..., x_N` poprzez stan o stałym rozmiarze `h`:

```
h_t = A h_{t-1} + B x_t
y_t = C h_t
```

Na każdym etapie stan ewoluuje poprzez dynamikę liniową `A`, pobiera dane wejściowe `B x_t` i emituje dane wyjściowe `C h_t`. `A, B, C` można się nauczyć. Zwróć uwagę na krytyczną właściwość: obliczenia `y_t` wymagają tylko `h_{t-1}` i `x_t`, a nie wcześniejszych `x`. Pamięć jest stała. Wnioskowanie wynosi O(1) na token.

Sekretem jakości modelowania jest struktura `A`. W S4 (Gu 2021) wykorzystano wysoce ustrukturyzowaną macierz, którą można było skutecznie ocenić jako długi splot podczas szkolenia. Mamba (Gu, Dao 2023) zastąpiła stałe `A, B, C` elementami zależnymi od danych („część „selektywna”). Mamba-2 (2024) dodatkowo uprościła konstrukcję. Mamba-3 (2026) ponownie dodaje złożoności w określonych miejscach.

Kluczowa właściwość: w przypadku dekodera LLM warstwa SSM jest zastępczym zamiennikiem warstwy uwagi, ze stanem każdej warstwy o stałym rozmiarze zamiast rosnącej pamięci podręcznej KV.

### Blok Jamby

Blok Jamba przeplata warstwy według dwóch liczb:

- `l`: stosunek uwagi do Mamby. Jamba używa `l = 8`, co oznacza 1 warstwę Transformatora na każde 7 warstw Mamby (7 Mamba + 1 Uwaga = 8 warstw na grupę).
- `e`: częstotliwość MoE. Jamba używa `e = 2`, co oznacza, że ​​każda inna warstwa stosuje MoE.

Kolejność warstw w bloku:

```
M  M  M  M  M  M  M  A    (7 Mamba + 1 Attention)
|  M  |  M  |  M  |  M    (where | marks MoE applied)
```

Każdy blok Jamba składa się z 8 warstw. Na głębokości 4 bloków (łącznie 32 warstwy) otrzymasz 28 warstw Mamba i 4 warstwy Uwaga. 16 z nich korzysta z MoE.

### Dlaczego współczynnik 1:7

AI21 przeprowadził ablacje: jaki stosunek uwagi do Mamby zapewnia najlepsze zakłopotanie na parametr ORAZ przypomnienie w kontekście w ich ocenach w długim kontekście?

- Za dużo uwagi (1:1): jakość wzrasta, ale pogarsza się pamięć i szybkość.
- Za mało uwagi (1:15): pamięć jest świetna, ale wyszukiwanie w kontekście nie udaje się.
- Najlepszy punkt: 1:7 lub 1:8.

Intuicja: warstwy Transformera obsługują dokładne przywoływanie i śledzenie stanu. Warstwy Mamby obsługują tanią większość przetwarzania.

### Kodowanie pozycyjne

Warstwy Mamby same rozpoznają położenie (poprzez powtarzanie). Warstwy uwagi w oryginalnych hybrydach opartych na Mambie nie korzystały z RoPE — warstwy SSM dostarczały informacji o pozycji. Jamba 1.5 dodaje RoPE do warstw uwagi w celu uogólnienia w dłuższym kontekście, udoskonalenia post-hoc w oparciu o empiryczną ocenę długiego kontekstu.

### Budżet pamięci

Dla kształtu Jamba-1 (32 warstwy: 28 Mamba + 4 Uwaga, ukryte 4096, 32 głowy uwagi):

- Pamięć podręczna KV (tylko warstwy uwagi): `2 * 4 * 32 * 128 * 256k * 2 = 8.4 GB` przy 256 tys. BF16. Tylko 4 warstwy uwagi przyczyniają się do tego.
- Stan SSM: `28 * hidden * state_size` na prefiks tokena, ale jest to stały rozmiar na warstwę, bez skalowania wraz z długością sekwencji. Typowy stan Mamby to 16 na funkcję, ukrytych 4096: łącznie `28 * 4096 * 16 * 2 = 3.7 MB`.

Porównanie z czystym transformatorem przy 32 warstwach, tym samym ukrytym, pełnym MHA przy 32 głowicach: `2 * 32 * 32 * 128 * 256k * 2 = 128 GB` przy 256 tys. BF16. 8-krotne zmniejszenie pamięci podręcznej KV. Nawet w porównaniu z wartością bazową GQA(8), z której korzysta większość modeli na rok 2024 (`2 * 32 * 8 * 128 * 256k * 2 = 32 GB`), hybryda Jamby 1:7 przy 16 GB jest wciąż 2 razy mniejsza.

To właśnie rozumie AI21, mówiąc „kontekst 256 tys. na pojedynczym procesorze graficznym 80 GB”. Pamięć podręczna KV transformatora z pełnym MHA nie zmieściłaby się; nawet linia bazowa GQA nie pozostawia miejsca na wagi i aktywacje; Jamba tak.

### Mamba-3: poziom bazowy czystego SSM w 2026 r

Mamba-3 (ICLR 2026, arXiv:2603.15569) wprowadza trzy innowacje po stronie czystego SSM:

1. ** Dyskretyzacja wykładniczo-trapezowa. ** Zastępuje dyskretyzację metodą Eulera w Mamba-2 bardziej wyrazistym powtórzeniem. Operacja przypominająca splot zastosowana na wejściu stanu w ramach powtarzania rdzenia, a nie jako splot zewnętrzny na `x_t`.

2. **Aktualizacja stanu o wartościach zespolonych.** Poprzednie Mamby redukowały macierz stanu ze złożonej (S4) do rzeczywistej przekątnej (Mamba) do tożsamości skalowanej (Mamba-2). Mamba-3 ponownie dodaje wartości zespolone — co odpowiada obrotowemu osadzaniu stanu w zależności od danych. Przywraca to możliwości śledzenia stanu, które kosztowały poprzednie uproszczenia o rzeczywistej wartości.

3. **Projekcje MIMO (wielowejściowe i wielowyjściowe).** Zamiast projekcji skalarnych dla poszczególnych cech, należy stosować projekcje oparte na wartościach macierzowych. Poprawia moc modelowania i wykorzystanie sprzętu w czasie wnioskowania bez zwiększania opóźnień dekodowania.

Przy parametrach 1,5B Mamba-3 poprawia średnią dokładność pobierania danych o 0,6 punktu w porównaniu z bramkowaną siecią DeltaNet; wariant MIMO dodaje 1,2 więcej, co daje całkowity wzrost o 1,8 punktu. Przy tej samej wielkości stanu Mamba-3 odpowiada Mambie-2 z połową stanu.

Mamba-3 nie jest jeszcze dostępna w wersji produkcyjnej hybrydy na dużą skalę, ale jest oczywistym kandydatem na stronę SSM w kolejnym modelu klasy Jamba.

### Kiedy sięgnąć po hybrydę

Hybrydy wygrywają, gdy:

- Kontekst jest na tyle długi, że czysta pamięć podręczna Transformer KV staje się bolesna (64 tys.+).
- Zadania łączą strukturę krótkiego zasięgu (dobrą dla SSM) z przywołaniem dalekiego zasięgu (wymaga Transformera).
— Chcesz wdrożyć rozwiązanie w oparciu o budżety pamięci obejmujące jeden procesor graficzny, gdzie sama pamięć podręczna Transformer KV nie zmieściłaby się.

Hybrydy przegrywają, gdy:

- Kontekst jest krótki (poniżej 16 tys.). Koszty ogólne SSM są marnowane; czysty transformator jest w porządku.
- Zadania wymagają uwagi ze wszystkich stron (głębokie rozumowanie, odsyłacze do wielu dokumentów). Niedobór warstw uwagi w hybrydzie boli.
- Skalujesz do modeli granicznych o bilionach parametrów. Pure-Transformer + MLA + MoE (styl DeepSeek-V3) wygrywa obecnie wyścig możliwości.

### Konkurencyjny krajobraz

| Modelka | Rodzina | Skala | Unikalne roszczenie |
|-------|-------|------|------------|
| Mamba-2 | czysty SSM | 3B | czas liniowy, pamięć stała |
| Jamba | hybrydowy | 52B/12B | 256 tys. na 80 GB |
| Jamba 1.5 duża | hybrydowy | 398B/94B | długi kontekst klasy korporacyjnej |
| Mamba-3 | czysty SSM | 1,5B (papier) | przywrócono śledzenie stanu |
| DeepSeek-V3 | czysty transformator + MoE | 671B/37B | zdolność graniczna |

Krajobraz na rok 2026: na granicy dominuje MoE oparty wyłącznie na transformatorach, ale niszę kontekstową obejmującą ponad 256 tys. Zwycięstwa Mamby-3 w śledzeniu stanu mogą obniżyć wskaźniki hybrydowe (więcej SSM, mniej uwagi) w następnej generacji.

## Użyj tego

`code/main.py` to kalkulator pamięci dla architektur hybrydowych. Biorąc pod uwagę współczynnik SSM-Transformer i konfigurację ukrytego rozmiaru/liczby warstw, oblicza:

- Pamięć podręczna KV w kontekście docelowym.
- Pamięć stanu SSM.
- Całkowita pamięć w kontekście N dla szeregu kształtów modeli.

Kalkulator obsługuje:

- Wartość bazowa Pure-Transformer (pamięć podręczna KV rośnie wraz z N).
- Hybryda 1:7 w stylu Jamby.
- Pure-SSM (brak pamięci podręcznej KV).

Liczby pochodzą bezpośrednio z artykułów Jamba-1 i Jamba-1.5 dla opublikowanych kształtów i zostały ekstrapolowane dla hipotetycznych wariantów.

Uwagi dotyczące integracji w przypadku rzeczywistego wdrożenia:

- Większość serwerów wnioskowania produkcyjnego (vLLM, SGLang) obsługuje Jambę i Mambę. Sprawdź konkretną wersję.
— W kontekście 256 kB przewaga pamięci Jamby ujawnia się w przepustowości współbieżnych żądań. W tej samej pamięci VRAM mieści się więcej sekwencji Jamba niż sekwencji Transformer.
- Mamba-3 jako samodzielny model nie jest jeszcze dostępna w produkcji — podgląd badań na poziomie 1,5B.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-hybrid-picker.md`. Biorąc pod uwagę specyfikację obciążenia (profil długości kontekstu, zestaw zadań, budżet pamięci), zaleca się wybór pomiędzy czystym Transformerem, hybrydą w stylu Jamba i czystym SSM, z wyraźnym uzasadnieniem dotyczącym kompromisów w zakresie pamięci i jakości.

## Ćwiczenia

1. Uruchom `code/main.py`, aby obliczyć pamięć podręczną KV w kontekście 256 tys. dla 32-warstwowego czystego transformatora (ukryte 4096, 32 głowice) i dla hybrydy Jamba-1 o tym samym kształcie. Sprawdź redukcję pamięci ~8x, o której twierdzi dokument AI21.

2. Zmodyfikuj kalkulator tak, aby modelował hybrydę 1:3 (4 Mamba: 1 Uwaga) i hybrydę 1:15 (14 Mamba: 1 Uwaga). Wykreśl pamięć podręczną KV w funkcji stosunku. W jakim stosunku pamięć podręczna KV jest równa pamięci stanu SSM?

3. Przeczytaj sekcję 3 artykułu Jamba (arXiv:2403.19887). Wyjaśnij, dlaczego AI21 używa Mamby-1 zamiast Mamby-2, mimo że Mamba-2 jest szybsza. Wskazówka: dokumentuje to sekcja poświęcona ablacji hybrydowej.

4. Oblicz narzut parametrów MoE dla każdej innej warstwy w Jamba 1.5 Large (łącznie 398B, 94B aktywnych). Porównaj współczynnik aktywności z DeepSeek-V3 (37B/671B) i wyjaśnij, dlaczego architektura Jamby zwiększa współczynnik aktywności.

5. Przeczytaj sekcję 3 artykułu Mamba-3 (arXiv:2603.15569). Wyjaśnij w trzech zdaniach, dlaczego aktualizacja stanu o wartościach zespolonych jest równoważna osadzaniu obrotowemu zależnemu od danych. Powiąż odpowiedź z fazą 7. · Wyprowadzenie RoPE z lekcji 04.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Model przestrzeni stanów (SSM) | „Nawrót o ustalonym stanie” | Warstwa z wyuczoną powtarzalnością `h_t = A h_{t-1} + B x_t`; stała pamięć na token |
| Selektywny SSM | „Sztuczka Mamby” | Zależne od danych parametry A, B, C, które dają modelowi selektywność bramkującą w czasie liniowym |
| Stosunek uwagi do mamby | „Ile warstw uwagi” | W Jambie `l = 8` oznacza 1 warstwę uwagi na 7 warstw Mamby |
| Blok Jamby | „Grupa 8-warstwowa” | Jedna uwaga + siedem Mamb + MoE na alternatywnych pozycjach |
| Stan SSM | „Ukryty bufor” | Stan warstwy o stałym rozmiarze, który zastępuje pamięć podręczną KV dla warstw Mamba |
| kontekst 256 tys. | „Flagowy numer Jamby” | Długość sekwencji Jamba-1 mieści się na pojedynczym procesorze graficznym o pojemności 80 GB; czysty Transformer nie może mieć tego rozmiaru |
| Mamba-3 | „Czysty SSM 2026” | Najlepsza obecnie architektura oparta na czystym SSM ze złożonym stanem + MIMO; podstawowe hybrydy odbudowują się wokół |
| MIMO | „Wiele wejść, wiele wyjść” | Innowacja Mamba-3 wykorzystująca projekcje oparte na wartościach macierzowych zamiast skalarnych na cechy |
| Dyskretyzacja wykładniczo-trapezowa | „Powrót Mamby-3” | Bardziej wyrazista rekurencja, która obejmuje dyskretyzację metody Eulera Mamby-2 |
| Architektura hybrydowa | „Połącz uwagę i SSM” | Dowolny model, który przeplata warstwy Transformatora i SSM; Jamba to archetyp produkcji |

## Dalsze czytanie

- [Lieber i in. — Jamba: A Hybrid Transformer-Mamba Language Model (arXiv:2403.19887)](https://arxiv.org/abs/2403.19887) — oryginalny artykuł w Jambie, ablacje współczynników, 256 tys. twierdzeń kontekstowych
— [AI21 — Jamba 1.5: Hybrid Transformer-Mamba at Scale (arXiv:2408.12570)](https://arxiv.org/abs/2408.12570) — powiększona rodzina, wersje publiczne 398B/94B i 12B/52B
- [Gu, Dao — Mamba: Linear-Time Sequence Modeling with Selective State Spaces (arXiv:2312.00752)](https://arxiv.org/abs/2312.00752) — selektywny artykuł SSM, na którym opiera się Jamba
- [Dao, Gu — Mamba-2 (arXiv:2405.21060)](https://arxiv.org/abs/2405.21060) — uproszczony następca przestrzeni strukturalnych
- [Lahoti i in. — Mamba-3 (arXiv:2603.15569, ICLR 2026)](https://arxiv.org/abs/2603.15569) — stan o wartościach zespolonych, MIMO, granica czystego SSM w 2026 r.
- [Gu i in. — Efektywne modelowanie długich sekwencji za pomocą ustrukturyzowanych przestrzeni stanów (arXiv:2111.00396)](https://arxiv.org/abs/2111.00396) — artykuł S4, punkt wyjścia genealogii SSM dla LLM