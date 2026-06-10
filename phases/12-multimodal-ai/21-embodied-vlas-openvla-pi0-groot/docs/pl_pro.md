# Ucieleśnione modele VLA (Embodied VLA): RT-2, OpenVLA, π0, GR00T

> Po raz pierwszy robot przeczytał przepis ze strony internetowej i samodzielnie wykonał go w kuchni dzięki modelowi RT-2 (Google DeepMind, lipiec 2023). Architektura RT-2 dyskretyzowała akcje robota do postaci tokenów tekstowych, co pozwoliło na dostrojenie modelu VLM (Vision-Language Model) na miksie danych internetowych oraz trajektorii robotycznych. Dowiodło to, że wiedza o świecie zakodowana w modelach językowo-wizyjnych na skalę internetową może być skutecznie przeniesiona (transfer learning) do sterowania robotami. Model OpenVLA (czerwiec 2024) dostarzył otwartoźródłowy model referencyjny o rozmiarze 7B. Seria π0 (pi-zero) firmy Physical Intelligence (2024–2025) wprowadziła ciągłe sterowanie ruchem oparte na dopasowaniu przepływu (Flow Matching). Z kolei NVIDIA GR00T N1 (marzec 2025) wdrożyła dwupoziomowy paradygmat sterowania (System 1 / System 2) dedykowany dla robotów humanoidalnych na dużą skalę. Modele klasy VLA (Vision-Language-Action) – czyli jeden zintegrowany system, który potrafi widzieć, interpretować tekst i działać – stanowią pomost między modelami rozumienia obrazu i wideo a systemami autonomicznymi w robotyce (omawianymi w Fazie 15).

**Typ:** Teoria / Przegląd
**Języki:** Python (biblioteka standardowa, tokenizer akcji + szkielet wnioskowania VLA)
**Wymagania wstępne:** Faza 12 · 05 (LLaVA), Faza 15 (Systemy autonomiczne - odniesienie)
**Czas:** ~180 minut

## Cele kształcenia

- Opisanie tokenizacji akcji robota: dyskretna kwantyzacja (RT-2), wydajne tokeny akcji FAST oraz sterowanie ciągłe oparte na dopasowaniu przepływu (π0).
- Wyjaśnienie, dlaczego wspólny trening na danych internetowych i robotycznych (co-fine-tuning) pozwala na transfer wiedzy ogólnej do nowych, nieznanych wcześniej zadań.
- Porównanie modeli OpenVLA (otwarty model 7B), π0 (Flow Matching) oraz GR00T N1 (podział System 1 / System 2) w tym samym zadaniu robotycznym.
- Omówienie znaczenia zbioru danych Open X-Embodiment jako uniwersalnego korpusu treningowego (RT-X).

## Problem

Robot wykonujący domowe obowiązki na polecenie w języku naturalnym to cel badawczy wyznaczony już w latach 70. XX wieku. Współczesną odpowiedzią są modele VLA (Vision-Language-Action). Korzystają one z tej samej architektury co modele VLM, ale zamiast tekstu generują akcje (momenty obrotowe stawów, pozycje i rotacje efektora końcowego czy komendy dyskretne).

Główne wyzwania w modelach VLA:

1. **Ciągłość i wielowymiarowość przestrzeni akcji:** Ruch robota opisują parametry ciągłe (kąty stawów, siły), często w wielu wymiarach jednocześnie (np. ramię 7-DOF + chwytak 3-DOF = 10 wymiarów próbkowanych przy częstotliwości 30 Hz).
2. **Niedobór danych robotycznych:** Zbiór Open X-Embodiment zawiera ok. 1 mln trajektorii, podczas gdy zbiory tekstowo-obrazowe w sieci liczą ponad 5 miliardów par.
3. **Rygorystyczne wymagania czasowe:** Pętla sterowania działająca przy 30 Hz oznacza, że model ma zaledwie 33 ms na wygenerowanie kolejnej akcji.
4. **Bezpieczeństwo fizyczne:** Błędna akcja wygenerowana przez model może doprowadzić do zniszczenia sprzętu, otoczenia lub zranienia ludzi.

## Koncepcja

### Tokenizacja akcji (RT-2)

Kluczowy pomysł w RT-2: przedstawienie każdego celu ruchu (np. pozycji stawu) jako dyskretnego tokenu tekstowego. Znormalizowany przedział wartości $[-1, 1]$ jest dzielony na 256 kubełków (bins), z których każdy odpowiada konkretnemu identyfikatorowi (ID) ze słownika. Akcja sterująca ramieniem o 10 stopniach swobody (10-DOF) staje się sekwencją 10 tokenów tekstowych generowaną w każdym kroku sterowania.

Uczenie modelu PaLM-E / PaLM-X odbywa się na miksie danych:

- Par tekst-obraz z sieci (opisywanie obrazów, VQA).
- Trajektorii robotycznych, gdzie akcje zapisano jako tokeny.

Model otrzymuje instrukcję „podnieś czerwoną kostkę” (język) oraz klatkę z kamery (wizja) i generuje sekwencję 10 tokenów akcji (dyskretne pozycje docelowe). Dzięki wcześniejszemu uczeniu na danych internetowych model wykazuje zdolność generalizacji: RT-2 potrafi zareagować na polecenie „przesuń ramię w stronę szybko poruszającego się obiektu”, nawet jeśli w danych robotycznych nie było słowa „szybko”.

Szybkość wnioskowania w RT-2 wynosiła ok. 3–5 Hz, co było ograniczone narzutem autoregresywnego generowania tokenów.

### OpenVLA — otwarty model referencyjny 7B

OpenVLA (Kim i in., czerwiec 2024) to otwartoźródłowa alternatywa dla RT-2. Model opiera się na bazie Llama-7B, wykorzystuje podwójny enkoder wizyjny (DINOv2 + SigLIP) oraz kwantyzuje akcje do 256 przedziałów.

Trening bazowy przeprowadzono na zbiorze Open X-Embodiment (970 tys. trajektorii na 22 różnych platformach robotycznych). Model udostępnia skrypty do szybkiego dostrajania za pomocą LoRA pod kątem specyficznych ramion i chwytaków.

Częstotliwość wnioskowania wynosi ok. 4–5 Hz na karcie A100 (przy użyciu kwantyzacji). Jest to prędkość wystarczająca do wolnej manipulacji przedmiotami, ale zbyt niska do sterowania dynamicznego o wysokiej częstotliwości.

### Tokenizer FAST — szybsze dekodowanie akcji

Pertsch i in. (2024) wykazali, że prosta kwantyzacja na stałe przedziały jest mało wydajna, ponieważ większość rzeczywistych ruchów robota grupuje się w małych, specyficznych obszarach. Tokenizer FAST (Frequency-Domain Action Sequence Tokenizer) kompresuje całe sekwencje ruchów za pomocą dyskretnej transformaty kosinusowej (DCT) i kwantyzuje wynikowe współczynniki częstotliwościowe.

Dzięki temu 30-krokowy ruch robota można zapisać za pomocą ok. 10 tokenów FAST zamiast 300 tokenów klasycznych. Szybkość wnioskowania wzrasta 3–5 krotnie bez pogorszenia precyzji sterowania.

### π0 i sterowanie oparte na dopasowaniu przepływu (Flow Matching)

Model π0 (pi-zero) zaprezentowany przez Physical Intelligence (październik 2024) zastępuje generowanie dyskretnych tokenów ciągłym generowaniem akcji za pomocą głowicy opartej na Flow Matching (dopasowaniu przepływu):

- Mała sieć generująca akcje odczytuje ukryte stany (embeddings) z dużego modelu VLM i generuje ciągłą sekwencję 50 kroków ruchu za pomocą mechanizmu Rectified Flow.
- Głowica akcji uczy się na funkcji straty dopasowania przepływu, podczas gdy bazowy model VLM pozostaje zamrożony.
- Wnioskowanie: Pełna sekwencja 50 kroków akcji jest generowana w zaledwie ok. 5 krokach odszumiania (denoising), co pozwala na płynne sterowanie z częstotliwością 50 Hz.

Zaletą π0 jest to, że generuje gładkie, ciągłe ścieżki ruchu, eliminując drgania charakterystyczne dla sterowania opartego na tokenach dyskretnych.

Warianty π0.5 oraz π0-FAST rozwijają te pomysły, łącząc m.in. tokenizer FAST z ciągłym generowaniem Flow Matching.

### GR00T N1: Dwupoziomowa kontrola robotów humanoidalnych

Model NVIDIA GR00T N1 (marzec 2025) został zaprojektowany z myślą o robotach humanoidalnych (skala powyżej 30 stopni swobody, sterowanie całym ciałem):

- **System 2 (Wolny/Planujący):** Duży model VLM analizujący scenę i instrukcje, generujący cele wysokiego poziomu (subgoals) przy częstotliwości ok. 1 Hz.
- **System 1 (Szybki/Reaktywny):** Mały transformator (głowica akcji) generujący komendy niskiego poziomu dla silników stawów z częstotliwością 50–100 Hz, uwarunkowany celami z Systemu 2.

Podział ten odzwierciedla koncepcję szybkiego i powolnego myślenia Kahnemana: System 2 odpowiada za planowanie strategiczne, a System 1 za natychmiastowe działanie. Zaletą jest to, że powolne wnioskowanie dużego VLM nie blokuje pętli sprzężenia zwrotnego silników robota.

Model GR00T N1.7 (koniec 2025) wprowadza dodatkowo masowe generowanie danych treningowych w symulacjach fizycznych platformy NVIDIA Omniverse.

### Zbiór danych Open X-Embodiment

Projekt RT-X (październik 2023) zjednoczył społeczność robotyczną, tworząc wspólny zbiór danych:
- Zawiera 1 milion trajektorii zebranych z 22 różnych typów robotów.
- Obejmuje m.in. dane z platform ALOHA, Bridge V2, Droid czy Language Table.
- Prace nad zbiorem wymagały ujednolicenia opisów przestrzeni akcji, normalizacji zakresów ruchu stawów oraz standaryzacji formatów wideo z kamer.

Modele takie jak OpenVLA czy π0 są trenowane na Open X-Embodiment. Różnice konstrukcyjne docelowego robota są następnie kompensowane przez szybkie dostrojenie za pomocą LoRA na małej próbie (100–1000 demonstracji).

### Wspólny trening (Co-fine-tuning) zamiast uczenia wyłącznie na danych robotycznych

Co-fine-tuning polega na mieszaniu w procesie uczenia ogólnych par tekst-obraz (VQA) z rzeczywistymi trajektoriami robotycznymi. Proporcja tych danych ma kluczowe znaczenie: zbyt duży udział danych internetowych sprawi, że model nie nauczy się precyzyjnie poruszać ramieniem; zbyt duży udział danych robotycznych zniszczy ogólną wiedzę o świecie.

W RT-2 stosunek ten wynosił ok. 1:1, w OpenVLA ok. 0,5:1 (sieć do robota). Właściwy miks jest kluczowym hiperparametrem strojenia.

Szkolenie wyłącznie na ruchach robota prowadzi do przeuczenia i braku odporności na komendy spoza rozkładu treningowego. Wspólny trening pozwala modelowi zrozumieć polecenia takie jak „podnieś trzeci obiekt od lewej”, nawet jeśli dane robotyczne zawierały jedynie proste instrukcje typu „podnieś czerwoną kostkę”.

### Ograniczenia bezpieczeństwa w pętli sterowania

Każde produkcyjne wdrożenie modelu VLA musi być zabezpieczone przez zewnętrzne filtry w warstwie sterownika:
- Sztywne limity kątowe i momentów obrotowych stawów (zabezpieczenie mechaniczne).
- Ograniczenia maksymalnej prędkości ruchu.
- Zdefiniowanie bezpiecznej przestrzeni roboczej (tzw. geofencing – np. chwytak nie może opuścić obrysu stołu).
- Weryfikacja nowych lub skomplikowanych zadań przez człowieka (human-in-the-loop).

Decyzje generowane przez model VLA są traktowane jako sugestie ruchu, które sterownik niskopoziomowy filtruje pod kątem bezpieczeństwa przed wysłaniem sygnału do silników.

## Zastosowanie w kodzie

Plik `code/main.py` zawiera:
- Implementację tokenizacji i detokenizacji akcji robota do 256 kubełków (bins).
- Zarys działania tokenizera FAST opartego na transformacie DCT i kwantyzacji.
- Porównanie liczby generowanych tokenów dla różnych strategii (dyskretne przedziały, FAST, ciągłe dopasowanie przepływu).
- Przegląd linii rozwojowej modeli: RT-2 → OpenVLA → π0 → GR00T.

## Rezultat

Do tej lekcji dołączono dokument `outputs/skill-vla-action-format-picker.md`. Pomaga on dobrać optymalną strategię reprezentacji ruchu (klasyczna kwantyzacja RT-2, tokenizer FAST z OpenVLA, Flow Matching z π0 lub architektura dwupoziomowa z GR00T) w zależności od specyfiki robota (manipulator, robot mobilny, humanoidalny sterowany całym ciałem).

## Ćwiczenia

1. Rozważ ramię o 10 stopniach swobody (10-DOF) przy częstotliwości pętli sterowania 30 Hz. Ile tokenów na sekundę generuje dyskretna tokenizacja (klasy 256 kubełków)? Czy model VLM o rozmiarze 7B będzie w stanie przetworzyć taki strumień w czasie rzeczywistym?
2. Tokenizer FAST kompresuje 30 kroków ruchu do ok. 10 tokenów. Jakie informacje o trajektorii mogą ulec zatraceniu, jeśli ruch robota ma charakter szybkozmienny o wysokiej częstotliwości (np. szybkie pukanie chwytakiem w stół)?
3. Głowica Flow Matching w modelu π0 generuje sekwencję akcji w ok. 5 krokach odszumiania. Porównaj tę wydajność z autoregresywnym generowaniem w OpenVLA działającym z prędkością 4–5 Hz.
4. Architektura dwupoziomowa GR00T (System 1 i System 2) odnosi się do koncepcji Kahnemana. Zaproponuj, jak mógłby wyglądać pomocniczy „System 3” dedykowany do stabilizacji chodu robota dwunożnego.
5. Przeczytaj sekcję 4 publikacji o Open X-Embodiment poświęconą weryfikacji zbiorów danych. Wymień trzy reguły walidacji, które zapobiegają wyciekowi danych między domenami testowymi a treningowymi.

## Kluczowe pojęcia

| Termin | Potoczne określenie | Co to dokładnie oznacza |
| :--- | :--- | :--- |
| **VLA (Vision-Language-Action)** | „Model sterowania robotem” | Model multimodalny przyjmujący obraz i instrukcję tekstową, a na wyjściu generujący bezpośrednie komendy ruchu robota. |
| **Tokenizacja akcji** | „Kubełkowanie akcji” | Metoda podziału ciągłych wartości pozycji/siły stawów na 256 dyskretnych kubełków, z których każdy odpowiada konkretnemu tokenowi tekstowemu. |
| **FAST tokenizer** | „Kompaktor akcji” | Algorytm kompresji trajektorii za pomocą transformaty DCT, drastycznie zmniejszający liczbę tokenów potrzebnych do zapisu ruchu. |
| **Co-fine-tuning** | „Wspólne trenowanie” | Trening modelu na mieszance danych internetowych (tekst, obrazy) oraz robotycznych w celu zachowania ogólnych zdolności rozumowania. |
| **Głowica Flow Matching** | „Ciągła generacja π0” | Moduł generujący ciągłe wartości trajektorii ruchu bezpośrednio z reprezentacji ukrytych VLM przy użyciu dopasowania przepływu. |
| **System 1 / System 2** | „Dwusystemowe sterowanie” | Podział zadań na powolne planowanie strategiczne (VLM - System 2) i szybkie, reaktywne generowanie ruchu (System 1). |
| **Open X-Embodiment** | „Zbiór RT-X” | Uniwersalny zbiór danych zawierający 1 milion trajektorii z różnych platform robotycznych, będący standardem uczenia modeli VLA. |

## Literatura uzupełniająca

- [Brohan i in. — RT-2 (arXiv:2307.15818)](https://arxiv.org/abs/2307.15818)
- [Kim i in. — OpenVLA (arXiv:2406.09246)](https://arxiv.org/abs/2406.09246)
- [Black i in. — π0 (arXiv:2410.24164)](https://arxiv.org/abs/2410.24164)
- [NVIDIA — GR00T N1 (arXiv:2503.14734)](https://arxiv.org/abs/2503.14734)
- [Open X-Embodiment Collab — RT-X (arXiv:2310.08864)](https://arxiv.org/abs/2310.08864)
