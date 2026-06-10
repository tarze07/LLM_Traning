# LLaVA-OneVision: pojedynczy obraz, wiele obrazów i wideo w jednym modelu

> Przed powstaniem LLaVA-OneVision (Li et al., sierpień 2024) świat otwartych modeli VLM był podzielony na osobne gałęzie: LLaVA-1.5 dla pojedynczych obrazów, modele wieloobrazowe takie jak Mantis i VILA oraz modele dedykowane dla wideo (np. Video-LLaVA, Video-LLaMA). Każdy z nich osiągał świetne wyniki w swojej wąskiej specjalizacji, ale radził sobie słabo w pozostałych zadaniach. Autorzy LLaVA-OneVision wykazali, że odpowiednio zaprojektowany program nauczania (curriculum learning) pozwala na wytrenowanie jednego zunifikowanego modelu dominującego we wszystkich trzech scenariuszach. Ponadto model taki wykazuje pozytywne efekty transferu wiedzy (np. kompetencje z pojedynczego obrazu są przenoszone na analizę wideo, a wnioskowanie wieloobrazowe ulepsza analizę pojedynczych scen). Recepta na ten sukces jest zaskakująco prosta: utrzymanie stałego budżetu tokenów wizualnych niezależnie od scenariusza oraz precyzyjny program nauczania, który stopniowo przechodzi od pojedynczego obrazu do wielu obrazów (OneVision) oraz wideo. W tej lekcji przeanalizujemy ten budżet, program uczenia oraz nowo powstałe możliwości modelu.

**Typ:** Projekt / Implementacja
**Języki:** Python (biblioteka standardowa, kalkulator budżetu tokenów + planer programu nauczania)
**Wymagania wstępne:** Faza 12 · Lekcja 05 (LLaVA), Faza 12 · Lekcja 06 (wizja w dowolnej rozdzielczości)
**Czas:** ~180 minut

## Cele nauczania

- Zaprojektuj budżet tokenów wizualnych na stałym poziomie dla danych wejściowych w postaci pojedynczego obrazu, wielu obrazów oraz wideo.
- Zaplanuj program nauczania (curriculum), który przenosi umiejętności z analizy pojedynczych obrazów na wideo bez efektu katastrofalnego zapominania.
- Wyjaśnij, dlaczego pojedynczy model zunifikowany przewyższa modele specjalistyczne o tej samej liczbie parametrów przy właściwie dobranym programie nauczania.
- Wskaż trzy nowe umiejętności wprowadzone przez LLaVA-OneVision: rozumowanie na bazie wielu kamer, Set-of-Mark prompting (znaczniki na obrazie) oraz sterowanie interfejsem iPhone'a na podstawie zrzutów ekranu.

## Problem

Przetwarzanie pojedynczego obrazu, wielu obrazów oraz wideo stawia przed modelem zupełnie inne wymagania.

Pojedynczy obraz wymaga tokenów o wysokiej rozdzielczości (np. AnyRes, ~2880 tokenów wizualnych), aby poprawnie odczytywać tekst (OCR) i drobne detale. Budżet na przykład: jeden obraz, 2880 tokenów.

Analiza wielu obrazów wymaga podania kilku obrazów w umiarkowanej rozdzielczości (~576 tokenów każdy), aby relacje między nimi zmieściły się w kontekście modelu. Budżet na przykład: 4-8 obrazów po 576 tokenów, co daje 2300-4600 tokenów.

Dane wideo wymagają wielu klatek w niskiej rozdzielczości (~196 tokenów na klatkę po zastosowaniu poolingu), aby uchwycić dynamikę zmian w czasie. Budżet na przykład: 8-32 klatki po 196 tokenów każda, co daje 1600-6200 tokenów.

Jeśli trenujesz osobne modele dedykowane, dobierasz budżet pod konkretne zadanie. Jeśli jednak budujesz jeden model zunifikowany, potrzebujesz budżetu, który można skalować elastycznie w zależności od scenariusza bez ryzyka przepełnienia kontekstu LLM.

Przed powstaniem OneVision standardowym podejściem było „trenuj pod jeden scenariusz, ignoruj pozostałe”. Model Video-LLaVA był wersją modelu obrazowego z dodatkowymi etapami treningu. LLaVA-NeXT dodała obsługę wielu obrazów za pomocą kafelkowania. Żadne z tych rozwiązań nie radziło sobie jednak z trzema modalnościami w sposób w pełni spójny.

## Koncepcja

### Budżet tokenów OneVision

LLaVA-OneVision przyjmuje zunifikowany budżet tokenów wizualnych na poziomie około 3000–4000 tokenów na przykład (sample), rozdzielany w zależności od wejścia:

- Pojedynczy obraz: AnyRes-9 (kafelki 3x3 + miniatura globalna), każdy kafelek o rozdzielczości 384x384 generuje 729 patchy, które są agresywnie agregowane (pooling dwuliniowy 2x2) do 182 tokenów na kafelek. Razem: 9 * 182 + 182 = 1820 tokenów. (Lub AnyRes-4 przy 729 tokenach na kafelek = 2916 + 729).
- Wiele obrazów: każdy obraz w umiarkowanej rozdzielczości (384x384, bez kafelkowania) generuje 729 tokenów bez dodatkowego poolingu. Budżet dla 6 obrazów wynosi: 6 * 729 = 4374 tokenów.
- Wideo: 32 klatki w rozdzielczości 384x384 z agresywnym poolingiem dwuliniowym 3x3 → 81 tokenów na klatkę. Razem: 32 * 81 = 2592 tokenów.

Taki podział pozwala zachować zbliżoną łączną liczbę tokenów. Model LLM nigdy nie otrzymuje paczki, która przekracza jego okno kontekstowe. Encoder generuje inną liczbę tokenów w zależności od geometrii wejścia, ale model LLM operuje w ramach tego samego budżetu.

### Trzystopniowy program nauczania (Curriculum)

Trening LLaVA-OneVision składa się z trzech etapów:

1. Single-Image SFT (etap SI). Wszystkie dane wejściowe to pojedyncze obrazy z tekstem. Trening odbywa się przy użyciu AnyRes w wysokiej rozdzielczości. Model uczy się percepcji, zadań OCR oraz szczegółowej analizy scen. Wykorzystuje dane z LLaVA-NeXT oraz dedykowane zbiory dla OneVision.
2. OneVision SFT (etap OV). Miksowanie danych: pojedyncze obrazy + wiele obrazów + wideo (klatki próbkowane równomiernie). Trening odbywa się przy zachowaniu zunifikowanego budżetu tokenów. Model uczy się obsługi zróżnicowanych kształtów wejściowych. Trening jest kontynuacją etapu SI (wagi nie są resetowane).
3. Task Transfer SFT (etap TT). Dostrajanie na docelowym zestawie zadań, zazwyczaj zorientowanym bardziej na wiele obrazów lub wideo, w zależności od wymagań wdrożeniowych.

Kluczowy wniosek: kolejność etapów ma fundamentalne znaczenie. Rozpoczęcie treningu od danych wideo lub wielu obrazów prowadzi do gorszych wyników w analizie pojedynczych obrazów niż w przypadku wdrożenia programu rozpoczynającego się od pojedynczego obrazu (nawet przy użyciu tych samych danych treningowych). Zostało to wyraźnie wykazane w badaniach ablacyjnych.

### Dlaczego program nauczania przynosi rezultaty

Trening na pojedynczych obrazach buduje solidną bazę percepcyjną. Tokeny patchy zawierają precyzyjne szczegóły wizualne, a LLM uczy się łączyć je z tekstem. Analiza wielu obrazów oraz wideo wprowadza dodatkowe wyzwania strukturalne (np. identyfikacja, który obraz jest który, kolejność zdarzeń w czasie), których opanowanie jest niezwykle trudne bez uprzednio wykształconych silnych podstaw percepcyjnych.

Jeśli trenujemy wszystkie scenariusze od początku wspólnie, model nie nadąża z nauką dokładnej percepcji (ze względu na ograniczoną liczbę obrazów w paczce) i zbyt mocno dopasowuje się do samej struktury (ze względu na dużą liczbę danych wideo i wielu obrazów). W efekcie powstaje model, który rozumie relacje przestrzenne, ale ma bardzo powierzchowną percepcję szczegółów.

Programowanie nauczania (curriculum learning) gwarantuje wysoką jakość percepcji z etapu SI, a następnie dodaje zdolności wnioskowania relacyjnego i czasowego w etapie OV, bez negatywnego wpływu na bazowe możliwości.

### Nowo powstałe umiejętności cross-modalne (Emerging Skills)

W publikacji o LLaVA-OneVision opisano trzy interesujące, nowe kompetencje modelu:

1. Rozumowanie wielokamerowe (Multi-camera reasoning). Mimo że model był trenowany na osobnych obrazach i wideo, potrafi poprawnie analizować i łączyć nagrania z jazdy samochodem rejestrowane przez wiele kamer jednocześnie, bez wcześniejszego treningu na dokładnie takim formacie.
2. Set-of-Mark prompting. Użytkownik nakłada na obraz numeryczne znaczniki; model potrafi precyzyjnie odpowiedzieć na pytania typu: „porównaj zachowanie obiektu oznaczonego jako 3 z obiektem 7”. Model nie był bezpośrednio trenowany na tym zadaniu — umiejętność ta powstała z połączenia zdolności lokalizacji przestrzennej oraz wnioskowania wieloobrazowego.
3. Analiza interfejsów (iPhone Screen Agent). Model potrafi przeanalizować zrzut ekranu z telefonu iPhone i zaplanować kolejne kroki użytkownika. Zdolność ta wyłoniła się z połączenia treningu na zrzutach ekranu UI, nagraniach wideo z interfejsów oraz parach obrazów przed/po wykonaniu akcji.

Umiejętności te nie były bezpośrednio programowane — wyłoniły się jako efekt kompozycji programu nauczania.

### Agregacja tokenów wizualnych (Token Pooling)

Zarządzanie budżetem tokenów wymaga ich agregacji. W OneVision stosuje się interpolację dwuliniową na dwuwymiarowej siatce patchy (2D patch grid): wejściowa siatka 24x24 (576 patchy) jest redukowana do formatu 12x12 (144 tokeny przy współczynniku 2x) lub 8x8 (64 tokeny przy współczynniku 3x). Aby zachować relacje przestrzenne, agregacja odbywa się bezpośrednio na siatce patchy przed spłaszczeniem do sekwencji.

Wybór współczynnika agregacji dla danego scenariusza to kluczowy hiperparametr. Mniejsza agregacja oznacza więcej tokenów i bogatszą reprezentację, natomiast większa agregacja redukuje liczbę tokenów, pozwalając na przetworzenie większej liczby klatek lub obrazów.

### LLaVA-OneVision-1.5

Wersja z 2025 roku (LLaVA-OneVision-1.5, arXiv 2509.23661) została w pełni udostępniona w formacie open-source (zarówno wagi, kod, jak i kompletne dane treningowe). Eliminuje ona różnice jakościowe w stosunku do modeli komercyjnych w benchmarkach. Wykorzystuje ten sam program nauczania, większy wolumen danych oraz silniejszy model bazowy LLM bez zmian w samej architekturze.

### Porównanie z Qwen2.5-VL

Model Qwen2.5-VL (Lekcja 12.09) opiera się na innych założeniach. Wykorzystuje mechanizm M-RoPE oraz dynamiczny dobór liczby klatek na sekundę (dynamic FPS) zamiast stałego współczynnika agregacji. Budżet tokenów rośnie tam proporcjonalnie do wejścia — minuta wideo zużywa znacznie więcej tokenów niż 5 sekund nagrania. LLaVA-OneVision stawia z kolei na sztywny budżet i odpowiednio skaluje stopień agregacji tokenów. Obie strategie są skuteczne, wymieniając przewidywalność kosztów na elastyczność reprezentacji.

## Użycie praktyczne

Skrypt `code/main.py` implementuje planer budżetu tokenów i programu uczenia dla modelu typu OneVision. Przy zadanym limicie tokenów na przykład (sample) oraz profilu zadań (np. 40% pojedyncze obrazy, 30% wiele obrazów, 30% wideo):

- Przydziela rozdzielczość, stopień agregacji (pooling factor) oraz liczbę klatek dla każdego scenariusza.
- Weryfikuje, czy każdy ze scenariuszy mieści się w zadanym budżecie.
- Raportuje oczekiwaną liczbę tokenów, obciążenie obliczeniowe LLM FLOPs oraz wskazuje potencjalnie niedoreprezentowane scenariusze.
- Generuje szczegółowy harmonogram treningu krok po kroku.

Skrypt ten jest przydatny do planowania precyzyjnego dostrajania modeli zunifikowanych lub szacowania kosztów wnioskowania produkcyjnego.

## Zadanie zaliczeniowe

W ramach tej lekcji należy stworzyć dokument `outputs/skill-onevision-budget-planner_pro.md`. Na podstawie zadanego profilu zadań oraz limitu tokenów na przykład (sample), oblicz optymalny współczynnik AnyRes, stopień agregacji na klatkę, liczbę klatek wideo oraz wagi dla poszczególnych etapów programu uczenia (curriculum). Korzystaj z tej umiejętności przy każdym treningu lub dostrajaniu wielomodalnych modeli zunifikowanych.

## Ćwiczenia

1. Twój system produkcyjny obsługuje: 80% pojedyncze obrazy, 10% serie obrazów (2-4 obrazy) i 10% wideo (8-16 klatek). Zaprojektuj budżet tokenów. Na co przeznaczysz zasoby zaoszczędzone dzięki ograniczeniu analizy wielu obrazów?

2. Przeczytaj sekcję 4.3 w artykule o LLaVA-OneVision dotyczącą nowo wykształconych umiejętności (emerging capabilities). Zaproponuj czwartą potencjalną kompetencję, którą model może opanować dzięki temu programowi uczenia, a która nie została wprost wymieniona w publikacji.

3. Przeanalizuj modyfikację kolejności programu uczenia: najpierw trening na wielu obrazach, potem na pojedynczych, a na końcu na wideo. Przewiduj, które benchmarki odnotują spadek jakości i wyjaśnij dlaczego.

4. W artykule testy wideo były trenowane na zaledwie 8 klatkach na przykład. Czy to rozwiązanie sprawdzi się w przypadku 30-sekundowych nagrań? Co ulegnie pogorszeniu w pierwszej kolejności — budżet tokenów czy zdolność modelowania zależności czasowych?

5. Agregacja (pooling) patchy o wymiarze 24x24 do formatu 12x12 oznacza 4-krotną redukcję liczby elementów. Zaimplementuj tę operację w Pythonie i zweryfikuj, czy średnia wartość z każdego bloku 2x2 odpowiada wynikowi interpolacji dwuliniowej.

## Słownik pojęć

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|-----------------|--------------------------------------|
| Scenariusz OneVision | „Zunifikowane wejście” | Przetwarzanie przez jeden model VLM trzech różnych formatów: pojedynczego obrazu, wielu obrazów oraz wideo przy stałym budżecie tokenów. |
| Budżet tokenów | „Liczba tokenów na przykład” | Łączny limit tokenów wizualnych przekazywany do LLM dla jednego przykladu treningowego lub zapytania (zazwyczaj 3000–4000). |
| Program nauczania | „Curriculum learning” | Etapowa procedura treningowa (najpierw pojedynczy obraz → potem wiele obrazów → na końcu wideo) optymalizująca transfer wiedzy. |
| Agregacja dwuliniowa | „Bilinear pooling” | Interpolacja dwuliniowa na dwuwymiarowej siatce patchy w celu zmniejszenia liczby tokenów przy zachowaniu ich zależności przestrzennych. |
| Umiejętności wschodzące | „Emerging capabilities” | Nowe kompetencje modelu ujawniające się podczas wnioskowania, na których model nie był bezpośrednio trenowany. |
| AnyRes-k | „Kafelkowanie multi-crop” | Metoda podziału obrazu na k kafelków podrzędnych o stałej rozdzielczości oraz miniaturę globalną (zazwyczaj k ∈ {4, 9}). |
| Transfer zadań | „Cross-scenario generalization” | Przenoszenie cech i umiejętności wyuczonych w jednym scenariuszu (np. obraz) na inny (np. wideo) dzięki współdzielonym wagom. |

## Dalsze czytanie

- [Li et al. — LLaVA-OneVision (arXiv:2408.03326)](https://arxiv.org/abs/2408.03326)
- [LLaVA-OneVision-1.5: A Fully Open-Source Framework (arXiv:2509.23661)](https://arxiv.org/abs/2509.23661)
- [Lin et al. — Video-LLaVA (arXiv:2311.10122)](https://arxiv.org/abs/2311.10122)
- [Lin et al. — VILA (arXiv:2312.07533)](https://arxiv.org/abs/2312.07533)
- [Wang et al. — Qwen2-VL (arXiv:2409.12191)](https://arxiv.org/abs/2409.12191)
