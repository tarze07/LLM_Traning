# Równoległość DualPipe

> DeepSeek-V3 został wytrenowany na 2048 procesorach graficznych H800 z ekspertami MoE rozmieszczonymi w różnych węzłach. Komunikacja all-to-all między węzłami pochłaniała tyle czasu, co same obliczenia — przez połowę czasu procesory graficzne stały bezczynnie. DualPipe (DeepSeek, grudzień 2024) to dwukierunkowy potok, który nakłada obliczenia przepływu przedniego i wstecznego na wywoływaną przez nie komunikację all-to-all. Bąbelki znikają, przepustowość rośnie. Utrzymywanie dwóch kopii parametrów modelu (stąd nazwa „dual") jest tanie, ponieważ równoległość ekspercka i tak już rozdziela ekspertów między rangi. Niniejsza lekcja omawia, co faktycznie robi DualPipe i dlaczego udoskonalenie DualPipeV opracowane przez Sea AI Lab zmniejsza koszt replikacji parametrów o połowę, kosztem nieznacznie szerszego bąbelka.

**Typ:** Uczenie się
**Języki:** Python (stdlib, symulator harmonogramu)
**Wymagania wstępne:** Faza 10 · 05 (uczenie rozproszone, FSDP, DeepSpeed), Faza 10 · 14 (architektury modeli otwartych i MoE)
**Czas:** ~60 minut

## Cele nauczania

- Wymień cztery komponenty fragmentu DualPipe w przepływie przednim i wstecznym oraz wyjaśnij, dlaczego każdy z nich ma własne okno nakładania.
- Omów problem bąbelków w potokach oraz wyjaśnij, co „wolność od bąbelków" oznacza w praktyce, a co w materiałach marketingowych.
- Prześledź ręcznie harmonogram DualPipe dla 8 rang PP i 16 mikropartii i potwierdź, że strumienie przepływu przedniego i wstecznego wypełniają nawzajem swoje szczeliny bezczynności.
- Opisz kompromis oferowany przez DualPipeV (Sea AI Lab, 2025): rezygnacja z dwukrotnej replikacji parametrów kosztem nieco większego bąbelka, gdy równoległość ekspercka jest wyłączona.

## Problem

Uczenie modelu 671B MoE na 2048 procesorach graficznych H800 napotyka trzy poważne wąskie gardła:

1. **Zajętość pamięci.** Każdy procesor graficzny przechowuje wycinek modelu. Pamięć aktywacji dla sekwencji 8k, 61 warstw i 128 głowic jest ogromna.
2. **Bąbelki potokowe.** Tradycyjna równoległość potokowa (GPipe, 1F1B) pozostawia procesory graficzne bezczynne w oczekiwaniu na dane wejściowe lub gradient z sąsiedniego etapu. Na 8 etapach nawet przy harmonogramowaniu 1F1B około 12% czasu GPU może być zmarnowane.
3. **All-to-all między węzłami.** W modelu MoE z równoległością ekspercką eksperci są rozproszeni między węzłami. Każdy przepływ przedni wywołuje operację all-to-all wysyłającą tokeny do odpowiednich ekspertów, a następnie drugą operację scalającą wyniki. Przy 2048 procesorach graficznych stosunek czasu obliczeń do czasu komunikacji łatwo osiąga wartość 1:1.

Każde z tych wąskich gardeł ma osobne rozwiązania: gradient checkpointing dla pamięci, Zero Bubble (Sea AI Lab, 2023) dla bąbelków potokowych oraz wyspecjalizowane jądra komunikacji dla all-to-all. DualPipe sprawia, że wszystkie te mechanizmy działają spójnie. Harmonogram nakłada obliczenia i komunikację w obrębie pojedynczego fragmentu przepływu przedniego i wstecznego, wprowadza mikropartie z obu końców potoku jednocześnie i wykorzystuje ten układ do ukrywania opóźnień komunikacyjnych w oknach obliczeniowych.

Zgłoszony wynik: niemal całkowite wyeliminowanie bąbelków potokowych i ponad 95% wykorzystania procesorów graficznych podczas uczenia DeepSeek-V3 na 14,8 T tokenów.

## Koncepcja

### Odświeżenie: równoległość potokowa

Model N-warstwowy jest dzielony między P urządzeń. Urządzenie `i` przechowuje warstwy `i * N/P .. (i+1) * N/P - 1`. Mikropartia przepływa do przodu przez urządzenia od 0 do P-1, a następnie wstecz od P-1 do 0. Każde urządzenie może rozpocząć swój etap przepływu przedniego dopiero po otrzymaniu danych wyjściowych od poprzedniego urządzenia, a przepływ wsteczny — dopiero po otrzymaniu gradientu od urządzenia znajdującego się dalej w potoku.

GPipe (Huang i in., 2019) przetwarza jedną mikropartię na raz, marnując większość czasu procesorów graficznych. 1F1B (Narayanan i in., 2021) przeplata przepływy przednie i wsteczne dla wielu mikropartii. Zero Bubble (Qi i in., 2023) dzieli przepływ wsteczny na dwie części — wsteczny dla danych wejściowych (B) i wsteczny dla wag (W) — i planuje je tak, aby wypełniały bąbelki. Po Zero Bubble potok jest niemal szczelny.

DualPipe idzie o krok dalej i dodaje dwa nowe pomysły.

### Pomysł 1: rozkład fragmentów

Każdy fragment przepływu przedniego jest dzielony na cztery komponenty:

- **Uwaga (Attention).** Projekcje Q/K/V, obliczenie uwagi, projekcja wyjściowa.
- **Wysyłanie all-to-all.** Komunikacja między węzłami rozsyłająca tokeny do ich ekspertów.
- **MLP.** Obliczenia ekspertów MoE.
- **Scalanie all-to-all.** Komunikacja między węzłami gromadząca wyniki ekspertów.

Fragment wsteczny zawiera gradientowe wersje każdego z tych komponentów. DualPipe planuje ich wykonanie tak, aby wysyłanie all-to-all odbywało się równolegle z obliczaniem uwagi dla kolejnego fragmentu, a scalanie all-to-all — równolegle z obliczaniem MLP kolejnego fragmentu.

### Pomysł 2: dwukierunkowe planowanie

Większość harmonogramów potokowych wprowadza mikropartie z etapu 0, skąd przepływają do etapu P-1. DualPipe wstrzykuje mikropartie z obu końców potoku jednocześnie. Na etapie 0 powstają mikropartie przepływające w kierunku etapu P-1; na etapie P-1 powstają mikropartie przepływające w kierunku etapu 0. Oba strumienie spotykają się pośrodku.

Aby to działało, urządzenie `i` musi obsługiwać zarówno wczesną warstwę potoku `i`, jak i późną warstwę `P - 1 - i`. Stąd właśnie bierze się słowo „dual" w nazwie DualPipe: każde urządzenie przechowuje dwie kopie obsługiwanych przez siebie warstw modelu — po jednej dla każdego kierunku. W skali DeepSeek-V3 oznacza to dwukrotny koszt replikacji parametrów, jednak jest on niewielki, ponieważ równoległość ekspercka i tak rozmieszcza ekspertów MoE między rangi — dwukrotna replikacja warstw niebędących ekspertami to przy tym drobnostka.

Co najważniejsze, strumień przepływu przedniego w jednym kierunku i strumień wsteczny w przeciwnym kierunku nakładają się dokładnie w tych miejscach, gdzie w harmonogramie jednokierunkowym pojawiałyby się bąbelki. Bąbelki znikają.

### Ręcznie sporządzony harmonogram

Rozważmy P = 4 rangi i 8 mikropartii, podzielonych na 4 przepływy przednie i 4 wsteczne. Czas płynie od lewej do prawej; wiersze reprezentują rangi urządzeń.

```
           Time →
rank 0:  F1 F2 F3 F4  F5R F6R F7R F8R  B1 B2 B3 B4  ...
rank 1:     F1 F2 F3  F4/F5R F6R F7R   B1 B2 ...
rank 2:        F1 F2  F3/F5R F4/F6R    B1 ...
rank 3:           F1  F2/F5R F3/F6R    ...
```

Zapis „F4/F5R" oznacza, że dana ranga wykonuje jednocześnie przepływ przedni mikropartii 4 (biegnącej od lewej do prawej) oraz przepływ przedni mikropartii 5 (biegnącej od prawej do lewej) w tym samym przedziale czasowym. Na tym polega operacyjny sens „dwukierunkowości".

Na randze 2 strumienie krzyżują się wcześniej, na rangach 0 i P-1 — najpóźniej. W stabilnej fazie środkowej każda ranga wykonuje przepływ przedni w jednym kierunku i nakłada na niego przepływ wsteczny w przeciwnym. Procesory graficzne są stale zajęte. Operacje all-to-all przepływu przedniego są ukrywane w obliczeniach wstecznych; operacje all-to-all przepływu wstecznego — w obliczeniach przednich. Bąbelki zostają wyeliminowane.

### Analiza bąbelków

Standardowy bąbelek potokowy w harmonogramie 1F1B (czas stracony na rangę):

```
bubble_1F1B = (P - 1) * forward_chunk_time
```

Zero Bubble redukuje tę wartość, lecz nie do zera. DualPipe w fazie stabilnej osiąga zerowy bąbelek, gdy liczba mikropartii jest podzielna przez dwukrotność głębokości potoku. Poza fazą stabilną (rozgrzewanie i wychładzanie) bąbelek pojawia się, ale nie rośnie wraz z liczbą mikropartii — to kluczowa właściwość podkreślana w artykule.

W ujęciu marketingowym: „bez bąbelków". W ujęciu technicznym: bąbelki nie rosną wraz z liczbą mikropartii. Szczegółowa analiza Sea AI Lab (DualPipeV) pokazuje, że pełne zerowanie bąbelka jest możliwe wyłącznie wtedy, gdy wąskim gardłem nie jest równoległość ekspercka; przy komunikacji all-to-all opartej na EP zawsze pojawia się pewien kompromis harmonogramowy.

### DualPipeV — udoskonalenie

Sea AI Lab (2025) zauważył, że dwukrotna replikacja parametrów jest marnotrawstwem, gdy nie służy ukrywaniu komunikacji EP. Ich harmonogram DualPipeV składa dwukierunkowe wstrzykiwanie w harmonogram w kształcie litery V, który działa na pojedynczej kopii parametrów. Bąbelek jest nieco większy niż w DualPipe, jednak oszczędność pamięci jest znaczna. DeepSeek zastosował DualPipeV w swoim opublikowanym kodzie open source jako tryb EP-off.

Podsumowanie kompromisów:

| Właściwość | DualPipe | DualPipeV | 1F1B | Zero Bubble |
|------------|----------|-----------|------|-------------|
| Kopie parametrów na urządzenie | 2 | 1 | 1 | 1 |
| Bąbelek a liczba mikropartii | stały | nieznaczny wzrost | rośnie | rośnie |
| Nakładanie obliczeń i komunikacji | pełne | częściowe | minimalne | częściowe |
| Zastosowanie | MoE z dużym EP | gęsty lub lekki EP | wariant bazowy | dowolny potok |

### Co to oznacza dla 14,8 T tokenów

Wstępne uczenie DeepSeek-V3 obejmowało 14,8 T tokenów na 2048 procesorach graficznych H800, pochłaniając około 2,8 mln godzin GPU. Przy naiwnym harmonogramie 1F1B stracono by 12–15% tego czasu na bąbelki potokowe — od 340 do 420 tys. godzin GPU, co wystarczyłoby do wytrenowania pełnego modelu 70B. Większość tych zasobów odzyskano dzięki DualPipe. Precyzyjne określenie jego wkładu bez dostępu do wewnętrznych logów jest trudne, jednak w artykule podano, że średnie wykorzystanie procesorów graficznych podczas uczenia przekroczyło 95%.

Przy mniejszych klastrach (poniżej 1000 procesorów graficznych) DualPipe jest zwykle nadmiarowy — bąbelki potokowe stanowią mniejszą część całkowitego kosztu, a uczenie gęstych modeli rzadko trafia w wąskie gardło all-to-all. Przy pionierskim uczeniu MoE w skali tysięcy procesorów graficznych jest to jednak rozwiązanie faktycznie niezbędne.

### Miejsce w stosie technologicznym

- Uzupełnienie **FSDP** (Faza 10 · 05). FSDP dzieli parametry modelu między rangi; DualPipe planuje obliczenia według rang. Oba mechanizmy współdziałają.
- Zgodność z fragmentowaniem gradientów **ZeRO-3**. Rozliczanie replikacji na dwóch kopiach musi być spójne z fragmentowanymi gradientami ZeRO.
- Wymaga **niestandardowych jąder all-to-all** dostosowanych do topologii konkretnego klastra. Jądra DeepSeek opublikowane jako open source stanowią implementację referencyjną.

## Jak z tego korzystać

`code/main.py` to symulator harmonogramu potokowego. Przyjmuje parametry `(P, n_micro_batches, schedule)` i wypisuje wykorzystanie fazy stabilnej dla każdego z harmonogramów: 1F1B, Zero Bubble, DualPipe i DualPipeV. Jest to narzędzie dydaktyczne — uzyskane wartości odpowiadają jakościowym twierdzeniom z artykułów, nie są mierzonymi przyspieszeniami produkcyjnymi.

Wartość symulatora polega na możliwości uruchamiania go z różnymi wartościami P i liczby mikropartii oraz obserwowania, jak frakcja bąbelków rośnie dla 1F1B, lecz nie dla DualPipe.

Uwagi dotyczące integracji w rzeczywistym przebiegu uczenia:

- Wybierz głębokość równoległości potokowej, która dzieli bez reszty liczbę mikropartii.
- Upewnij się, że siatka równoległości eksperckiej obsługuje dwukierunkową komunikację all-to-all. Jądra DeepSeek są tu punktem odniesienia.
- Licz się z tym, że samo debugowanie harmonogramu zajmie za pierwszym razem tydzień. Rozliczanie jest podatne na błędy.
- Monitoruj wykorzystanie procesorów graficznych według rang, a nie tylko zbiorczo. Korzyści z DualPipe wynikają z eliminacji opóźnień najwolniejszych uczestników.

## Wynik uczenia

Ta lekcja produkuje `outputs/skill-dualpipe-planner.md`. Na podstawie specyfikacji klastra treningowego (liczba procesorów graficznych, topologia, połączenia wzajemne, kształt modelu) narzędzie rekomenduje strategię równoległości potokowej, właściwy algorytm harmonogramowania oraz oczekiwaną frakcję bąbelków w docelowej skali.

## Ćwiczenia

1. Uruchom `code/main.py` dla `(P=8, micro_batches=16, schedule=dualpipe)` i `(P=8, micro_batches=16, schedule=1f1b)`. Oblicz różnicę w wykorzystaniu procesorów graficznych i wyraź ją jako odzyskane godziny GPU na milion tokenów uczenia.

2. Naszkicuj ręcznie tabelę harmonogramu dla `(P=4, micro_batches=8, schedule=dualpipe)`. Oznacz każdy przedział czasowy identyfikatorem mikropartii i kierunkiem przepływu. Wskaż pierwszy przedział czasowy, w którym nie ma bąbelków.

3. Przeczytaj rysunek 5 z raportu technicznego DeepSeek-V3 (arXiv:2412.19437). Zidentyfikuj okno nakładania dla wysyłania all-to-all w fragmencie przepływu przedniego DualPipe. Wyjaśnij, w jaki sposób harmonogram obliczeń ukrywa tę komunikację.

4. Oblicz narzut dwukrotnej replikacji parametrów DualPipe dla gęstego modelu 70B z P=8 stopniami potoku oraz dla modelu 671B MoE z P=16 stopniami. Wykaż, dlaczego narzut jest proporcjonalnie mniejszy w przypadku MoE (większość parametrów to eksperci rozdzieleni między wiele rang EP).

5. Porównaj DualPipe z Chimerą (konkurencyjny dwukierunkowy harmonogram z 2021 r.). Korzystając z sekcji 3.4 artykułu jako odniesienia, wskaż dwie konkretne właściwości DualPipe nieobecne w Chimerze.

## Kluczowe terminy

| Termin | Potoczne określenie | Właściwe znaczenie |
|--------|--------------------|--------------------|
| Bąbelek potokowy | „Czas bezczynności na rangę" | Cykle GPU marnowane podczas oczekiwania etapu potoku na dane wejściowe lub gradient |
| 1F1B | „Domyślny harmonogram potokowy" | Harmonogram z przeplataniem jednego przepływu przedniego i jednego wstecznego; wariant bazowy, który DualPipe przewyższa |
| Zero Bubble | „Sea AI Lab 2023" | Dzieli przepływ wsteczny na B (gradient wejściowy) i W (gradient wag); niemal całkowicie uszczelnia potok |
| DualPipe | „Harmonogram DeepSeek-V3" | Dwukierunkowy potok z nakładaniem komunikacji na obliczenia; bąbelki nie rosną wraz z liczbą mikropartii |
| DualPipeV | „Cut-in-half" | Udoskonalenie w kształcie litery V eliminujące dwukrotną replikację parametrów kosztem nieco większych bąbelków |
| Fragment (chunk) | „Jednostka pracy potoku" | Przepływ przedni lub wsteczny jednej mikropartii przez jeden etap potoku |
| Wysyłanie all-to-all | „Rozsyłanie tokenów do ekspertów" | Komunikacja między węzłami kierująca tokeny do przypisanych im ekspertów MoE |
| Scalanie all-to-all | „Zbieranie wyników ekspertów" | Komunikacja między węzłami gromadząca wyniki ekspertów po warstwie MLP |
| Równoległość ekspercka (EP) | „Eksperci na różnych GPU" | Rozproszenie ekspertów MoE między rangi, tak że różne procesory graficzne przechowują różnych ekspertów |
| Równoległość potokowa (PP) | „Warstwy na różnych GPU" | Podział warstw modelu między rangi; wymiar harmonogramowania DualPipe |
| Frakcja bąbelkowa | „Zmarnowany czas GPU" | (czas_bąbelka / czas_całkowity); wartość, którą DualPipe dąży do zera |

## Dalsza lektura

- [DeepSeek-AI — raport techniczny DeepSeek-V3 (arXiv:2412.19437), sekcja 3.3.2 i rysunek 5](https://arxiv.org/abs/2412.19437) — podstawowe źródło dotyczące DualPipe
- [DeepSeek — repozytorium DualPipe na GitHub](https://github.com/deepseek-ai/DualPipe) — referencyjna implementacja open source, w tym tryb DualPipeV (Cut-in-half)
- [Qi i in. — Zero Bubble Pipeline Parallelism (arXiv:2401.10241, Sea AI Lab 2023)](https://arxiv.org/abs/2401.10241) — poprzednik DualPipe oparty na Zero Bubble
- [Sea AI Lab — DualPipe mógłby być lepszy bez Dual](https://sail.sea.com/blog/articles/63) — analiza DualPipeV, która wpłynęła na tryb EP-off w implementacji DeepSeek
- [Narayanan i in. — PipeDream / 1F1B (arXiv:1806.03377, 2018-2021)](https://arxiv.org/abs/1806.03377) — harmonogram 1F1B, z którym porównuje się DualPipe
- [Huang i in. — GPipe (arXiv:1811.06965, 2018)](https://arxiv.org/abs/1811.06965) — oryginalny artykuł o równoległości potokowej i problemie bąbelków
