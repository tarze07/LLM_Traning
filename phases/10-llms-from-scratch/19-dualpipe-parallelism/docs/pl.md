# Równoległość DualPipe

> DeepSeek-V3 został przeszkolony na 2048 procesorach graficznych H800 z udziałem ekspertów MoE rozproszonych po różnych węzłach. Ekspert ds. komunikacji międzywęzłowej typu „wszystko do wszystkich” kosztuje 1 godzinę komunikacji z procesorem graficznym na każdą godzinę obliczeń z procesorem graficznym. Przez połowę czasu procesory graficzne były bezczynne. DualPipe (DeepSeek, grudzień 2024 r.) to dwukierunkowy potok, który nakłada się na obliczenia do przodu i do tyłu w przypadku wyzwalanej przez nie komunikacji typu „wszyscy do wszystkich”. Bąbelki spadają, przepustowość rośnie, a utrzymywanie dwóch kopii parametrów modelu („podwójnego”, od którego pochodzi nazwa) jest tanie, skoro Równoległość Ekspertów i tak już rozdziela ekspertów między szeregi. Ta lekcja jest przewodnikiem po tym, co faktycznie robi DualPipe i dlaczego udoskonalenie DualPipeV firmy Sea AI Lab zmniejsza dwukrotnie koszt parametru kosztem nieznacznie węższej bańki.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulator harmonogramu)
**Wymagania wstępne:** Faza 10 · 05 (szkolenie rozproszone, FSDP, DeepSpeed), Faza 10 · 14 (architektury modelu otwartego i MoE)
**Czas:** ~60 minut

## Cele nauczania

- Nazwij cztery elementy fragmentu DualPipe do przodu i do tyłu i dlaczego każdy z nich ma własne okno nakładania się.
- Wyjaśnij na dużą skalę problem baniek w rurociągach i co oznacza „wolny od pęcherzyków” w praktyce i w marketingu.
- Prześledź ręcznie harmonogram DualPipe dla 8 szeregów PP i 16 mikropartii i potwierdź, że strumienie do przodu i do tyłu wypełniają nawzajem swoje bezczynne szczeliny.
- Podaj kompromis, jaki zapewnia DualPipeV (Sea AI Lab, 2025): usuwa replikację parametrów 2x kosztem nieco większego bąbelka, gdy równoległość eksperta jest nieaktywna.

## Problem

Uczenie modelu 671B MoE na procesorach graficznych 2K H800 napotyka trzy złożone wąskie gardła:

1. **Zajętość pamięci.** Każdy procesor graficzny przechowuje wycinek modelu. Pamięć aktywacji przy sekwencji 8k na 61 warstwach na 128 głowicach jest ogromna.
2. **Pęcherzyki potokowe.** Tradycyjna równoległość potoków (GPipe, 1F1B) pozostawia procesory graficzne bezczynne w oczekiwaniu na wejście lub gradient ze sceny. Na 8 etapach około 12% czasu GPU może być bąbelkowe, nawet przy harmonogramowaniu 1F1B.
3. **Wszystkie węzły między węzłami.** MoE z ekspercką równoległością rozprasza ekspertów między węzłami. Każde podanie w przód uruchamia opcję „wszyscy do wszystkich” w celu wysłania tokenów do swoich ekspertów, a drugą do połączenia. Przy procesorach graficznych 2K łatwo osiąga się stosunek mocy obliczeniowej do komunikacji wynoszący 1:1.

Każde z nich ma osobne rozwiązania: gradientowy punkt kontrolny dla pamięci, Zero Bubble (Sea AI Lab, 2023) dla bąbelków potokowych, specjalistyczne jądra komunikacji równoległej dla wszystkich. DualPipe sprawia, że ​​grają razem. Harmonogram nakłada się na obliczenia i komunikację w ramach pojedynczego fragmentu do przodu i do tyłu, wprowadza mikropartie z obu końców potoku jednocześnie i wykorzystuje powstały harmonogram do ukrywania wszystkich w oknach obliczeniowych.

Zgłoszony wynik: prawie wyeliminowanie pęcherzyków w rurociągach, ponad 95% wykorzystania procesora graficznego w przebiegu szkoleniowym DeepSeek-V3 z tokenem 14,8 T.

## Koncepcja

### Odświeżenie równoległości potoku

Podziel model N-warstwowy na urządzenia P. Urządzenie `i` przechowuje warstwy `i * N/P .. (i+1) * N/P - 1`. Mikropartia przepływa do przodu przez urządzenia od 0 do P-1, a następnie do tyłu od P-1 do 0. Każde urządzenie może rozpocząć swój etap do przodu tylko wtedy, gdy poprzednie urządzenie wyśle ​​swoje dane wyjściowe, i może rozpocząć się do tyłu tylko wtedy, gdy urządzenie znajdujące się poniżej wyśle ​​gradient w górę.

GPipe (Huang i in., 2019) planuje jedną mikropartię na raz, co marnuje większość czasu procesora graficznego. 1F1B (Narayanan i in., 2021) przeplata przejścia do przodu i do tyłu dla wielu mikropartii. Zero Bubble (Qi i in., 2023) dzieli przejście wstecz na dwie części — wstecz dla danych wejściowych (B) i wstecz dla wag (W) — i planuje ich wypełnienie bańki. Po Zero Bubble rurociąg jest prawie szczelny.

Następnym krokiem jest DualPipe. Dodaje dwa pomysły na górze:

### Pomysł 1: rozkład kawałków

Każdy fragment do przodu jest podzielony na cztery komponenty:

- **Uwaga.** Projekcje Q/K/V, uwaga, projekcja wyników.
- **Wysyłanie „wszystko do wszystkich”.** Komunikacja między węzłami, która wysyła tokeny do swoich ekspertów.
- **MLP.** Obliczenia ekspertów Ministerstwa Środowiska.
- **Łączenie typu „wszystko dla wszystkich”.** Komunikacja między węzłami, która zapewnia fachowe wyniki.

Kawałek wstecz dodaje wersje gradientowe każdego z nich. DualPipe planuje je tak, aby wysyłanie „wszystko do wszystkich” odbywało się równolegle z obliczaniem uwagi następnego fragmentu, a łączenie „wszystko do wszystkich” odbywało się równolegle z obliczaniem MLP następnego fragmentu.

### Pomysł 2: planowanie dwukierunkowe

Większość harmonogramów rurociągów wprowadza mikropartie z etapu 0 i przepływa do etapu P-1. DualPipe wtryskuje mikroporcje z OBU końcówek. Na etapie 0 powstają stamtąd mikropartie forward; Na etapie P-1 powstają także mikropartie przyszłe, które tam powstają. Obydwa strumienie spotykają się pośrodku.

Aby to zadziałało, urządzenie `i` musi obsługiwać ZARÓWNO wczesną warstwę potoku `i` ORAZ warstwę późnego potoku `P - 1 - i`. To jest „podwójna” część DualPipe: każde urządzenie przechowuje dwie kopie warstw modelu, które musi obsługiwać (po jednej dla każdego kierunku). W skali DeepSeek-V3 jest to dwukrotność kosztu replikacji parametrów. Jest niedrogi, ponieważ równoległość ekspercka już tak rozmieszcza ekspertów MoE, że dwukrotne replikowanie warstw innych niż eksperckie to drobnostka.

Co najważniejsze, strumień do przodu w jednym kierunku i strumień do tyłu w drugim kierunku nakładają się dokładnie tam, gdzie bąbelki znajdowałyby się w harmonogramie jednokierunkowym. Bąbelki znikają.

### Ręcznie sporządzony harmonogram

Rozważmy P = 4 szeregi, 8 mikropartii, podzielone 4 do przodu / 4 do tyłu. Czas płynie od lewej do prawej; wiersze to rangi urządzeń.

```
           Time →
rank 0:  F1 F2 F3 F4  F5R F6R F7R F8R  B1 B2 B3 B4  ...
rank 1:     F1 F2 F3  F4/F5R F6R F7R   B1 B2 ...
rank 2:        F1 F2  F3/F5R F4/F6R    B1 ...
rank 3:           F1  F2/F5R F3/F6R    ...
```

Odczytując notację „F4/F5R”: pozycja 1 biegnie do przodu mikropartii 4 (przechodząc od lewej do prawej w rurociągu) ORAZ do przodu mikropartii 5 (przechodząc od prawej do lewej) w tym samym przedziale czasowym. To właśnie oznacza operacyjnie „dwukierunkowość”.

Na poziomie 2 strumienie krzyżowe nakładają się na siebie wcześniej, na poziomie 0 i P-1 najpóźniej. W stabilnej środkowej fazie harmonogramu każda ranga biegnie do przodu w kierunku X i nakłada się na tył w kierunku Y. Obliczenia są zajęte. Wysyłki typu „wszystko do wszystkich” w przypadku przebiegu do przodu są ukrywane w obliczeniach wstecznych. Kombinacje typu „wszystko do wszystkich” ukrywają się w obliczeniach do przodu. Bąbelki zostają wyciśnięte.

### Rachunkowość bąbelkowa

Standardowa bańka rurociągu 1F1B (czas stracony na rangę):

```
bubble_1F1B = (P - 1) * forward_chunk_time
```

Udoskonalenie Zero Bubble obniża to, ale nie do zera. DualPipe w fazie stabilnej ma zerowe pęcherzyki, jeśli liczba mikroporcji jest podzielna przez 2-krotność głębokości rurociągu. Poza fazą stabilną (rozgrzewanie i schładzanie) pojawia się bąbelek, ale nie rośnie on wraz z liczbą mikropartii – jest to kluczowa właściwość, na którą zwraca się uwagę w artykule.

W ujęciu marketingowym: „bez bąbelków”. Z technicznego punktu widzenia: pęcherzyki nie rosną wraz z liczbą mikropartii. Dalsza analiza przeprowadzona przez Sea AI Lab (DualPipeV / przecięcie na pół) pokazuje pełną bańkę zerową tylko wtedy, gdy wąskim gardłem nie jest równoległość ekspercka; w przypadku rozwiązań typu „wszystko dla wszystkich” opartych na EP, zawsze występuje pewien kompromis w harmonogramie.

### DualPipeV — wyrafinowanie

Sea AI Lab (2025) zaobserwowało, że replikacja parametrów 2x jest marnotrawstwem, gdy nie ma na celu nakładania się komunikatów EP. Ich harmonogram DualPipeV składa dwukierunkowy wtrysk w harmonogram w kształcie litery V, który działa na kopii pojedynczego parametru. Bańka jest nieco większa niż w przypadku DualPipe, ale oszczędność pamięci jest znaczna. DeepSeek zastosował DualPipeV w swojej implementacji DualPipe typu open source jako tryb EP-off.

Kompromis:

| Funkcja | Podwójna rura | DualPipeV | 1F1B | Zerowa bańka |
|---------|---------|------|------|------------|
| Kopie parametrów na urządzenie | 2 | 1 | 1 | 1 |
| Bańka vs mikropartie | stała | mały wzrost | rośnie | rośnie |
| Nakładanie się obliczeń i komunikacji | pełny | częściowe | minimalne | częściowe |
| Użyj, gdy | MoE ciężkie w PE | gęsty lub EP-lekki | linia bazowa | dowolny rurociąg |

### Co to oznacza dla runu tokenów o wartości 14,8 T

Wstępne szkolenie DeepSeek-V3 zużyło 14,8 T tokenów na 2048 procesorach graficznych H800 w ciągu około 2,8 mln godzin pracy procesora graficznego. W przypadku naiwnego 1F1B straciliby 12–15% tej wartości z powodu baniek w rurociągach — 340–420 tys. godzin pracy procesora graficznego, co wystarczy do wytrenowania pełnego modelu 70B. Większość z tego odzyskała DualPipe. Bezpośrednie ilościowe określenie wkładu bez wewnętrznych dzienników jest trudne, ale w artykule podano, że wykorzystanie procesora graficznego wynosi ponad 95% uśrednione podczas treningu.

W przypadku mniejszych serii (poniżej 1 tys. procesorów graficznych) DualPipe jest przesadą — bąbelki potokowe są mniejsze w stosunku do całkowitego kosztu, a szkolenie w oparciu o gęste modele rzadko trafia w wąskie gardło wszystkich. W przypadku pionierskich szkoleń MoE na skalę obejmującą wiele tysięcy procesorów graficznych jest to faktycznie wymagane.

### Gdzie znajduje się na stosie

- Uzupełnienie **FSDP** (faza 10 · 05). FSDP dzieli parametry modelu na szeregi; DualPipe planuje obliczenia według rang. Łączą.
- Kompatybilny z fragmentowaniem gradientowym **ZeRO-3**. Księgowość dla replikacji w dwóch kopiach musi współpracować z gradientami fragmentowanymi ZeRO.
- Wymaga **niestandardowych jąder typu „wszystko do wszystkich”** dostosowanych do określonej topologii klastra. Jądra DeepSeek o otwartym kodzie źródłowym są implementacją referencyjną.

## Użyj tego

`code/main.py` to symulator harmonogramu rurociągu. Pobiera `(P, n_micro_batches, schedule)` i wypisuje wykorzystanie fazy stabilnej dla każdego z 1F1B, Zero Bubble, DualPipe i DualPipeV. Jest to narzędzie dydaktyczne — liczby odpowiadają twierdzeniom jakościowym zawartym w artykułach, a nie twierdzeniu o mierzonym przyspieszeniu produkcji.

Wartość symulatora: uruchom go z różnymi liczbami P i mikropartii i obserwuj, jak rośnie frakcja pęcherzyków w przypadku 1F1B, ale nie DualPipe.

Rozważania integracyjne dla prawdziwego biegu treningowego:

- Wybierz głębokość równoległą do rurociągu, która wyraźnie dzieli się na liczbę mikropartii.
- Upewnij się, że Twoja specjalistyczna siatka równoległa obsługuje dwukierunkową komunikację „wszyscy do wszystkich”. Jądra DeepSeek są punktem odniesienia.
— Spodziewaj się, że za pierwszym razem spędzisz tydzień na debugowaniu według samego harmonogramu. Księgowość jest zawodna.
- Monitoruj wykorzystanie procesora graficznego według rangi, a nie tylko zbiorczo. Korzyści z DualPipe wynikają z dokręcania maruderów.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-dualpipe-planner.md`. Biorąc pod uwagę specyfikację klastra szkoleniowego (liczba procesorów graficznych, topologia, wzajemne połączenia, kształt modelu), zaleca strategię równoległości potoku, algorytm planowania do użycia i oczekiwaną część bąbelków w skali docelowej.

## Ćwiczenia

1. Uruchom `code/main.py` na `(P=8, micro_batches=16, schedule=dualpipe)` i `(P=8, micro_batches=16, schedule=1f1b)`. Oblicz różnicę w wykorzystaniu procesora graficznego i wyraź ją jako odzyskane godziny procesora graficznego na milion tokenów szkolenia.

2. Naszkicuj ręcznie tabelę zestawień dla `(P=4, micro_batches=8, schedule=dualpipe)`. Oznacz każdy przedział czasowy identyfikatorem mikropartii i kierunkiem. Zidentyfikuj pierwszy przedział czasowy, w którym nie ma bąbelków.

3. Przeczytaj rysunek 5 raportu technicznego DeepSeek-V3 (arXiv:2412.19437). Zidentyfikuj okno nakładania się dla wysyłki „wszystko do wszystkich” w fragmencie przesyłania dalej DualPipe. Wyjaśnij, w jaki sposób harmonogram obliczeń to ukrywa.

4. Oblicz 2x narzut parametrów DualPipe dla gęstego modelu 70B z P=8 stopniami rurociągu i modelu 671B MoE z P=16 stopniami rurociągu. Proszę wykazać, dlaczego koszty ogólne sprawy Ministerstwa Środowiska są proporcjonalnie mniejsze (większość parametrów to eksperci podzieleni na dużą grupę PE).

5. Porównaj DualPipe z Chimerą (konkurencyjnym dwukierunkowym harmonogramem od 2021 r.). Zidentyfikuj dwie specyficzne właściwości dodane przez DualPipe, których nie posiada Chimera, korzystając z sekcji 3.4 artykułu jako odniesienia.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Bańka rurociągowa | „Czas bezczynności na rangę” | Cykle GPU są marnowane, ponieważ etap potoku oczekuje na dane wejściowe lub gradient |
| 1F1B | „Domyślny harmonogram rurociągu” | Jedno planowanie z przeplataniem do przodu / jedno do tyłu; podstawowy DualPipe bije |
| Zerowa bańka | „Morskie laboratorium sztucznej inteligencji 2023” | Dzieli wstecz na B (gradient wejściowy) i W (gradient wagowy); prawie całkowicie uszczelnia rurociąg |
| Podwójna rura | „Harmonogram DeepSeek-V3” | Dwukierunkowy potok + nakładanie się połączeń obliczeniowych; pęcherzyki nie rosną wraz z liczbą mikropartii |
| DualPipeV | „Przecięcie na pół” | Udoskonalenie kształtu litery V, które zmniejsza replikację parametrów 2x kosztem nieco większych bąbelków |
| Kawałek | „Jednostka pracy rurociągu” | Przejście do przodu lub do tyłu jednej mikropartii przez jeden etap rurociągu |
| Wysyłka od wszystkich do wszystkich | "Wyślij tokeny do ekspertów" | Komunikacja międzywęzłowa, która kieruje tokeny do przypisanych do nich ekspertów Ministerstwa Środowiska |
| Łączenie wszystkich z wszystkimi | „Przywróć wyniki ekspertów” | Komunikacja międzywęzłowa, która gromadzi wyniki ekspertów po MLP |
| Równoległość ekspercka (EP) | „Eksperci od procesorów graficznych” | Odłamki ekspertów MoE w różnych rangach, więc różne procesory graficzne mają różnych ekspertów |
| Równoległość rurociągów (PP) | „Warstwy na procesorach graficznych” | Odłamki modelują warstwy w różnych rangach; wymiar Zestawienia DualPipe |
| Frakcja bąbelkowa | „Zmarnowany czas GPU” | (czas_bubble'a / czas_całkowity); ułamek DualPipe zmierza do zera |

## Dalsze czytanie

- [DeepSeek-AI — raport techniczny DeepSeek-V3 (arXiv:2412.19437), sekcja 3.3.2 i rysunek 5](https://arxiv.org/abs/2412.19437) — podstawowe odniesienie do DualPipe
- [DeepSeek — repozytorium DualPipe GitHub] (https://github.com/deepseek-ai/DualPipe) — referencyjna implementacja typu open source, w tym tryb DualPipeV (Cut-in-half)
- [Qi i in. — Parallelizm rurociągów Zero Bubble (arXiv:2401.10241, Sea AI Lab 2023)](https://arxiv.org/abs/2401.10241) — poprzednik Zero Bubble
– [Sea AI Lab — DualPipe mógłby być lepszy bez Dual](https://sail.sea.com/blog/articles/63) — analiza DualPipeV, która wpłynęła na tryb EP-off DeepSeek
- [Narayanan i in. — PipeDream / 1F1B (arXiv:1806.03377, 2018-2021)](https://arxiv.org/abs/1806.03377) — porównanie harmonogramu 1F1B DualPipe z
- [Huang i in. — GPipe (arXiv:1811.06965, 2018)](https://arxiv.org/abs/1811.06965) — oryginalny dokument dotyczący równoległości rurociągu i problemu pęcherzyków