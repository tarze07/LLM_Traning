# InternVL3: Natywne multimodalne szkolenie wstępne

> Każdy otwarty VLM przed InternVL3 działał według tego samego, trzyetapowego przepisu: weź tekst LLM wyszkolony na bilionach tokenów tekstowych, przykręć koder wizyjny, a następnie dopracuj łączenia. To działa, ale ma dług związany z wyrównaniem — firma Text LLM wydała cały swój budżet na szkolenie wstępne na czysty tekst i natywnie nie rozumie tokenów wizualnych. Kiedy dodasz wizję post hoc, LLM musi ponownie nauczyć się, jak powiązać dane wizualne z rozumowaniem tekstowym, nie zapominając o tekście. InternVL3 (Zhu i in., kwiecień 2025) odrzuca podejście post-hoc: jeden przebieg szkolenia wstępnego, tekst i multimodalność przeplatane z kroku pierwszego. Wynik odpowiada Gemini 2.5 Pro na MMMU-Pro przy otwartych parametrach 78B. W tej lekcji omówiono przypadek natywnego uczenia wstępnego i zmiany, jakie zachodzą po jego wykonaniu.

**Typ:** Ucz się
**Języki:** Python (stdlib, mikser korpusów szkoleniowych)
**Wymagania:** Faza 12 · 05, Faza 12 · 07 (przepisy)
**Czas:** ~120 minut

## Cele nauczania

- Wyjaśnij, dlaczego post-hoc szkolenie VLM kumuluje dług w zakresie dopasowania, podając trzy mierzalne objawy (katastrofalne zapominanie, dryf odpowiedzi, niespójność obrazu i tekstu).
- Opisz natywną mieszankę korpusu przedtreningowego InternVL3 i dlaczego stosunek tekstu: przeplatany: podpis ma znaczenie.
- Porównaj V2PE (kodowanie zmiennej pozycji wizualnej) z M-RoPE Qwen2-VL.
- Podaj nazwę optymalizacji wdrażania routera rozdzielczości wizualnej (ViR) i oddzielonego języka wizyjnego (DvD).

## Problem

Szkolenie post-hoc VLM jest ustawieniem domyślnym. LLaVA, BLIP-2, Qwen-VL, Idefics — wszystkie wykorzystują już przeszkolony LLM (Llama, Vicuna, Qwen, Mistral) i dodają wizję. Etapy szkolenia zazwyczaj wyglądają następująco:

1. Zamrożony LLM + zamrożony koder wizyjny + projektor z możliwością szkolenia, przeszkolony na parach napisów w celu wyrównania osadzania.
2. Odblokuj LLM, trenuj na danych instrukcji (LLaVA-Instruct, ShareGPT4V).
3. Opcjonalne dostrojenie specyficzne dla zadania.

Pojawiają się trzy objawy długu wyrównawczego:

- Katastrofalne zapomnienie. VLM post-hoc zapomina o umiejętnościach związanych wyłącznie z tekstem. Wyniki GSM8K spadają o 5-10 punktów. Spadek wyników Hellaswag. Regresja agentów czystego tekstu.
- Odpowiedz na dryf. Drobne sformułowania tego samego pytania wizualnego dają różne odpowiedzi. Koder wizyjny łączy się z LLM za pomocą słabszych powiązań niż własne tokeny LLM.
- Niespójność wizualno-tekstowa. VLM może poprawnie opisać obraz, a następnie odpowiedzieć na pytanie sprzeczne z własnym opisem. Tokeny wizualne nie uczestniczą w wewnętrznych kontrolach spójności LLM w taki sam sposób, jak tekst.

Objawy te są dobrze udokumentowane. MM1.5 Sekcja 4 określa je ilościowo. Ablacje LLaVA-OneVision na to wskazują. Odpowiedzią jest natywne szkolenie wstępne.

## Koncepcja

### Natywne, multimodalne szkolenie wstępne

InternVL3 trenuje od zera w korpusie, który jest natywny multimodalny od pierwszego kroku. Mieszanka to:

- 40% danych tekstowych (FineWeb, Proof-Pile-2 itp.)
- 35% przeplatanych danych obrazowo-tekstowych (OBELICS, styl MMC4)
- 20% sparowanych danych podpisów obrazów
- 5% danych wideo-tekstowych

Żetony wizji, żetony tekstu i interakcje międzymodalne powodują tę samą stratę już od pierwszego kroku gradientu. Żadnych wstępnych treningów związanych z ustawieniem, żadnego etapu zawieszania się projektora, żadnych katastrofalnych zapomnień o regeneracji.

Trening jest pojedynczym etapem dla modelu podstawowego. Następuje dostrajanie instrukcji, ale model podstawowy już rozumie tokeny wizualne jako obywateli pierwszej klasy.

### V2PE (kodowanie zmiennej pozycji wizualnej)

Qwen2-VL wykorzystuje M-RoPE ze stałym przydziałem osi. InternVL3 wprowadza V2PE: kodowanie pozycji różni się w zależności od typu modalności (tekst, obraz, wideo) z możliwością nauczenia się skalowania. W praktyce:

- Żetony tekstowe otrzymują pozycję 1D (indeks tekstowy).
- Poprawki obrazu otrzymują pozycję 2D (wiersz, kolumna).
- Klatki wideo uzyskują pozycję 3D (czas, wiersz, kolumna).

Wszystkie trzy korzystają z tej samej bazy częstotliwości RoPE, ale przydział ukrytego przyciemnienia na pasmo jest parametrem wyuczonym, a nie stałym podziałem. Swoboda przełączania rozdzielczości czasowej i przestrzennej częstotliwości podczas treningu wstępnego.

Twierdzenie V2PE dotyczące ablacji: 1-2 punkty w testach porównawczych wideo przez M-RoPE przy tym samym obliczeniu. Nie rewolucja, ale czyściej.

### Router rozdzielczości wizualnej (ViR)

Optymalizacja wdrożenia. Nie wszystkie obrazy wymagają kodowania w pełnej rozdzielczości. Zdjęcie z jednym obiektem o niskiej szczegółowości marnuje tokeny, gdy jest zakodowane w natywnej rozdzielczości 1280 pikseli. ViR to mały klasyfikator, który przewiduje minimalną rozdzielczość potrzebną do udzielenia odpowiedzi na pytanie przed kodowaniem.

Trasowanie ma trzy poziomy: niska rozdzielczość (256 tokenów), średnia (576) i wysoka (2048+). Dla 60% zapytań w ruchu produkcyjnym wystarczy niski lub średni. Efekt netto: 2-3x przepustowość przy tej samej jakości.

### Oddzielne wdrożenie języka wizyjnego (DvD)

Gdy obsługujesz duży VLM, koder wizyjny działa raz na obraz, ale LLM działa autoregresywnie dla każdego tokena wyjściowego. Te dwa komponenty mają różne wąskie gardła (wizja = przepustowość pamięci GPU dla konwersji + uwaga; LLM = pamięć podręczna KV). DvD dzieli je na oddzielne procesory graficzne, przesyłając strumieniowo pomiędzy nimi.

W przypadku modelu kodera 8B + 400M, przepustowość DvD w przybliżeniu podwaja się na węzeł w porównaniu z przepustowością wspólną.

### Jakość jednoetapowa a wieloetapowa

Główne twierdzenie dotyczące testu porównawczego InternVL3: przy parametrach 78B dorównuje MMMU-Pro Gemini 2.5 Pro. W 38B dopasuj GPT-4o. Na poziomie 8B poprowadź ranking open-8B. Wszystko w oparciu o jednoetapowy przepis na wstępne szkolenie i dostrojenie instrukcji.

Hipoteza długu dopasowania jest mierzalna: InternVL3-8B traci mniej punktów odniesienia dla tekstu (MMLU, GSM8K) niż Qwen2.5-VL-7B na jednostkę wzmocnienia wzorca widzenia. Model jest bardziej ogólny, ponieważ szkolenie składało się z jednego elementu, a nie dwóch.

### InternVL3.5 i InternVL-U

InternVL3.5 (sierpień 2025) skaluje przepis. To samo podejście do wstępnego uczenia natywnego, więcej danych, więcej parametrów. Ulepszenia MMMU są stopniowe.

InternVL-U (2026) dodaje ujednoliconą generację — obraz wyjściowy za pośrednictwem głowic MMDiT na tym samym szkielecie. „U” oznacza „Zrozumienie + generacja” i podąża za zunifikowanymi modelami w stylu transfuzji (lekcja 12.13). Ten sam szkielet z natywnym przygotowaniem obsługuje zarówno umysły rozumiejące, jak i generujące.

### Kompromisy natywnego szkolenia wstępnego

Natywne szkolenie wstępne nie jest bezpłatne:

- Oblicz. Szkolenie nowego VLM od podstaw kosztuje tyle samo, co szkolenie tekstowego LLM — miliony godzin GPU. Adaptacja post-hoc ponownie wykorzystuje istniejące wagi LLM, oszczędzając większość kosztów.
- Dane. Przeplatane korpusy obrazu i tekstu na dużą skalę są rzadkie. OBELICS to 141 mln dokumentów; MMC4 to 571M. Sam tekst jest dostarczany po 15 tonach tokenów. Niedobór danych dotyczących multimodalnego szkolenia wstępnego stanowi twarde ograniczenie.
- Ponowne wykorzystanie Base-LLM. Natywne szkolenie wstępne rezygnuje z możliwości późniejszego dołączenia do nowego LLM. Post-hoc pozwala zamienić Lamę-3.1 na Lamę-4, przekwalifikowując tylko adapter.

Zakład InternVL3 stawia: dług wyrównawczy jest większy niż strata związana z ponownym wykorzystaniem. Benchmarki potwierdzają tę tezę. Koszt produkcji uniemożliwia przyszłym laboratoriom tanie replikowanie. VLM post-hoc pozostaną istniejące, ponieważ w przypadku większości projektów pozostają tańsze.

## Użyj tego

`code/main.py` to mikser korpusów szkoleniowych i symulator routera ViR. To:

- Pobiera docelowy miks korpusu (%tekst,%przeplot,%podpis,%wideo) i oblicza oczekiwane kroki dla każdej modalności.
- Symuluje routing ViR w partii zapytań (dystrybucja: 50% o małej liczbie szczegółów, 30% o średniej, 20% o dużej liczbie szczegółów) i raportuje średnią liczbę tokenów.
- Raportuje szacunkową przepustowość DvD dla danego kodera w porównaniu z FLOPami LLM.
— Drukuje obok siebie post-hoc i natywne szkolenie wstępne w zakresie parametrów, obliczeń, danych i oczekiwanych objawów długu wyrównania.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-native-vs-posthoc-auditor.md`. Biorąc pod uwagę proponowany plan szkolenia VLM, sprawdza, czy przejść na wersję natywną, czy post-hoc, zaznacza ryzyko dostosowania do zadłużenia i zaleca połączenie korpusu. Użyj go, gdy ustalasz rozmiar nowego projektu otwartego VLM i musisz wybrać strategię szkoleniową.

## Ćwiczenia

1. Oszacuj różnicę obliczeniową pomiędzy InternVL3-8B (natywne uczenie wstępne) i LLaVA-OneVision-7B (post-hoc). Stosunek godzin GPU w przybliżeniu? Co wyjaśnia lukę?

2. InternVL3 raportuje 40% tekstu / 35% przeplatanego / 20% podpisów / 5% wideo. Jeśli Twoje docelowe zadanie obejmuje dużą ilość materiałów wideo, zaproponuj nowy współczynnik i uzasadnij, dlaczego model podstawowy nadal potrzebuje znacznych ilości tekstu i podpisów.

3. Przeczytaj rozdział 4 MM1.5 na temat zapominania. Podaj dokładny punkt odniesienia, w którym szkolenie post-hoc wykazało największą regresję. Ile kosztowała regresja?

4. ViR kieruje 60% ruchu do kodowania o niskiej rozdzielczości. Jakiego rodzaju zapytania błędnie kieruje (wysyła do niskiej rozdzielczości, gdy potrzebna była wysoka rozdzielczość)? Zaproponuj trzy tryby awarii routera.

5. DvD dzieli wizję i LLM na oddzielne procesory graficzne. W jakim schemacie ruchu DvD szkodzi przepustowości, zamiast pomagać?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Natywne multimodalne szkolenie wstępne | „Wspólnie od zera” | Tekst + obraz + tokeny wideo uczestniczą w stracie z kroku 1, nie są później przykręcane |
| Wyrównanie długu | „Kara post-hoc” | Wymierny regres w umiejętnościach tekstowych i spójności odpowiedzi wynikający z przeniesienia wizji na zamrożony LLM |
| V2PE | „Zmienne kodowanie wizualne pos” | Przydzielanie kodowania pozycji z możliwością uczenia się według modalności; Następca M-RoPE firmy InternVL3 |
| ViR | „Router rozdzielczości” | Mały klasyfikator, który wybiera minimalną rozdzielczość wymaganą na zapytanie przed kodowaniem, zapisując tokeny wnioskowania |
| DVD | „Oddzielne wdrożenie” | Koder wizyjny na jednym procesorze graficznym, LLM na innym, z przełączaniem strumienia; podwaja przepustowość dla dużych VLM |
| StażystaVL-U | „Jednolite zrozumienie + pokolenie” | Kontynuacja z 2026 r. polegająca na dodaniu głowic generujących obrazy do natywnego szkieletu wstępnego uczenia |
| Korpus przeplatany | „OBELIKI / MMC4” | Dokumenty zawierające tekst i obrazy w naturalnej kolejności czytania; surowiec do natywnego treningu wstępnego |

## Dalsze czytanie

- [Chen i in. — InternVL 1 (arXiv:2312.14238)](https://arxiv.org/abs/2312.14238)
- [Zhu i in. — InternVL3 (arXiv:2504.10479)](https://arxiv.org/abs/2504.10479)
- [InternVL3.5 (arXiv:2508.18265)](https://arxiv.org/abs/2508.18265)
- [InternVL-U (arXiv:2603.09877)](https://arxiv.org/abs/2603.09877)
- [Zhang i in. — MM1.5 (arXiv:2409.20566)](https://arxiv.org/abs/2409.20566)