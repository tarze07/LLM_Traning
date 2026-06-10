# InternVL3: Natywny multimodalny pretrening

> Każdy otwarty model VLM przed powstaniem InternVL3 bazował na tym samym, trzyetapowym przepisie: weź model tekstowy LLM wytrenowany na bilionach tokenów, dołącz do niego encoder wizyjny, a następnie dostrój warstwy łączące (adaptery). To podejście działa, ale generuje tzw. dług wyrównania (alignment debt) — model tekstowy zużył cały swój budżet pretreningu wyłącznie na czysty tekst i nie rozumie natywnie tokenów wizualnych. Gdy dodasz modalność wizualną na późniejszym etapie (post-hoc), LLM musi na nowo uczyć się powiązania danych wizualnych z wnioskowaniem tekstowym, starając się nie zapomnieć o bazowych kompetencjach tekstowych. Twórcy InternVL3 (Zhu et al., kwiecień 2025) porzucili podejście post-hoc na rzecz zintegrowanego pretreningu, w którym dane tekstowe i multimodalne są przeplatane od pierwszego kroku optymalizacji. W rezultacie model o rozmiarze 78B parametrów dorównuje komercyjnemu Gemini 2.5 Pro w benchmarku MMMU-Pro. W tej lekcji omówimy zalety natywnego pretreningu oraz zmiany architektoniczne, jakie ze sobą niesie.

**Typ:** Teoria / Zrozumienie
**Języki:** Python (biblioteka standardowa, mikser korpusów treningowych)
**Wymagania:** Faza 12 · Lekcja 05, Faza 12 · Lekcja 07 (receptury treningowe)
**Czas:** ~120 minut

## Cele nauczania

- Wyjaśnij, dlaczego pretrening post-hoc modeli VLM generuje dług wyrównania, podając trzy mierzalne objawy (katastrofalne zapominanie, dryf odpowiedzi, niespójność na linii obraz-tekst).
- Opisz strukturę natywnego korpusu przedtreningowego InternVL3 i wyjaśnij, dlaczego proporcje danych (tekst : dane przeplatane : opisy obrazów) mają kluczowe znaczenie.
- Porównaj mechanizm V2PE (Variable Visual Position Encoding) z M-RoPE stosowanym w Qwen2-VL.
- Omów metody optymalizacji wdrożeniowej: router rozdzielczości wizualnej (Visual Resolution Router - ViR) oraz rozdzielone wdrażanie modeli (Disaggregated Vision-Language Deployment - DvD).

## Problem

Pretrening post-hoc modeli VLM jest obecnie standardem rynkowym. Modele takie jak LLaVA, BLIP-2, Qwen-VL czy Idefics wykorzystują gotowe, wcześniej wytrenowane LLM (np. Llama, Vicuna, Qwen, Mistral) i dołączają do nich gałąź wizyjną. Etapy treningu wyglądają zazwyczaj tak:

1. Zamrożony LLM + zamrożony encoder wizyjny + trenowalny projektor; trening na parach obraz-opis w celu dopasowania przestrzeni embeddingów.
2. Odblokowanie wag LLM, trening na danych instruktażowych (np. LLaVA-Instruct, ShareGPT4V).
3. Opcjonalne dostrajanie pod specyficzne zadania.

Takie podejście prowadzi do trzech głównych objawów długu wyrównania:

- Katastrofalne zapominanie (Catastrophic forgetting). Model VLM traci sprawność w zadaniach czysto tekstowych. Wyniki w GSM8K spadają o 5-10 punktów procentowych. Pogorszeniu ulegają wyniki w Hellaswag oraz zadaniach agentowych opartych na tekście.
- Dryf odpowiedzi (Response drift). Niewielkie zmiany w sformułowaniu pytania dotyczącego obrazu prowadzą do zupełnie różnych odpowiedzi. Gałąź wizyjna łączy się z LLM znacznie słabszymi powiązaniami niż natywne tokeny tekstowe LLM.
- Niespójność wizualno-tekstowa (Visual-textual inconsistency). Model potrafi poprawnie opisać obraz, a następnie w odpowiedzi na pytanie zadać twierdzenie bezpośrednio sprzeczne z własnym opisem. Tokeny wizualne nie uczestniczą w wewnętrznych procesach kontroli spójności LLM w taki sam sposób jak tekst.

Zjawiska te są szczegółowo opisane i udokumentowane w sekcji 4 publikacji MM1.5 oraz w badaniach ablacyjnych LLaVA-OneVision. Rozwiązaniem tego problemu jest natywny pretrening zintegrowany.

## Koncepcja

### Natywny pretrening zintegrowany

Model InternVL3 jest trenowany od podstaw na korpusie, który zawiera dane multimodalne od pierwszego kroku optymalizacji. Miks danych obejmuje:

- 40% danych tekstowych (FineWeb, Proof-Pile-2 itp.)
- 35% przeplatanych danych obraz-tekst (np. w stylu OBELICS, MMC4)
- 20% par obraz-opis (captions)
- 5% danych wideo-tekst

Tokeny wizualne, tokeny tekstowe oraz interakcje między nimi są optymalizowane tą samą funkcją straty od pierwszego kroku gradientu. Nie ma potrzeby wstępnego dopasowywania przestrzeni, zamrażania projektora ani odzyskiwania utraconych zdolności tekstowych.

Dla modelu bazowego (base model) trening jest jednoetapowy. Po nim następuje klasyczne dostrajanie instruktażowe, ale model bazowy traktuje już tokeny wizualne jako natywne elementy języka.

### V2PE (Variable Visual Position Encoding)

Podczas gdy Qwen2-VL wykorzystuje M-RoPE ze sztywnym podziałem osi, InternVL3 wprowadza V2PE: kodowanie pozycji różni się w zależności od modalności (tekst, obraz, wideo) i posiada trenowalne parametry skalowania:

- Tokeny tekstowe otrzymują pozycję 1D (indeks tekstu).
- Patche obrazu otrzymują pozycje 2D (wiersz, kolumna).
- Klatki wideo otrzymują pozycje 3D (czas, wiersz, kolumna).

Wszystkie trzy modalności korzystają z tej samej bazy częstotliwości RoPE, ale przydział wymiarów ukrytych (hidden dim) na poszczególne pasma jest parametrem wyuczanym w trakcie treningu, a nie sztywno zdefiniowanym. Daje to większą elastyczność przy zmianie rozdzielczości czasowej i przestrzennej w pretreningu.

Badania ablacyjne wykazują, że V2PE przynosi wzrost o 1-2 punkty w benchmarkach wideo w porównaniu do M-RoPE przy tych samych kosztach obliczeniowych.

### Visual Resolution Router (ViR)

Optymalizacja wdrożeniowa. Nie wszystkie obrazy wymagają kodowania w maksymalnej rozdzielczości. Kodowanie prostego zdjęcia z jednym obiektem w rozdzielczości 1280 pikseli marnuje tokeny okna kontekstowego. ViR to mały klasyfikator, który przed uruchomieniem encodera przewiduje minimalną rozdzielczość niezbędną do poprawnej odpowiedzi na pytanie.

Obrazy są kierowane do trzech poziomów rozdzielczości: niskiej (256 tokenów), średniej (576 tokenów) lub wysokiej (2048+ tokenów). Dla 60% typowych zapytań produkcyjnych rozdzielczość niska lub średnia okazuje się w pełni wystarczająca, co pozwala na 2-3 krotny wzrost przepustowości (throughput) przy zachowaniu tej samej jakości.

### Disaggregated Vision-Language Deployment (DvD)

Podczas serwowania dużych modeli VLM, encoder wizyjny jest uruchamiany tylko raz na obraz, natomiast LLM działa autoregresywnie dla każdego generowanego tokena wyjściowego. Oba te komponenty mają inne wąskie gardła (wizja: przepustowość pamięci GPU dla splotów i uwagi; LLM: rozmiar pamięci podręcznej KV Cache). DvD rozdziela te zadania na osobne procesory graficzne, przesyłając dane strumieniowo między nimi.

Dla modelu z encoderem o rozmiarze 8B + 400M parametrów, wdrożenie DvD w przybliżeniu podwaja przepustowość na węzeł obliczeniowy w porównaniu z wdrożeniem zunifikowanym.

### Jakość: pretrening jednoetapowy vs wieloetapowy

Kluczowy wniosek z testów InternVL3: model o rozmiarze 78B parametrów dorównuje Gemini 2.5 Pro na benchmarku MMMU-Pro. Wersja 38B osiąga wyniki zbliżone do GPT-4o, a model o rozmiarze 8B jest liderem w klasie małych modeli open-source. Wszystko to osiągnięto za pomocą jednoetapowego pretreningu oraz dostrajania instruktażowego.

Zredukowanie długu wyrównania jest mierzalne: InternVL3-8B traci znacznie mniej punktów w benchmarkach czysto tekstowych (MMLU, GSM8K) niż Qwen2.5-VL-7B przy podobnej sprawności w zadaniach wizualnych. Model zachowuje bardziej ogólne kompetencje, ponieważ jego proces uczenia stanowił spójną całość.

### InternVL3.5 oraz InternVL-U

InternVL3.5 (sierpień 2025) to skalowanie udanego przepisu treningowego: to samo podejście do zintegrowanego pretreningu, większa skala danych i parametrów.

InternVL-U (2026) dodaje możliwość zunifikowanego generowania obrazów za pomocą głowic MMDiT osadzonych na tym samym szkieletowym modelu. Litera „U” oznacza „Understanding + Generation” (Zrozumienie + Generowanie) i nawiązuje do zunifikowanych modeli w stylu Transfusion (Lekcja 12.13). Ten sam zintegrowany model obsługuje zarówno zadania rozumienia obrazu, jak i jego syntezy.

### Kompromisy natywnego pretreningu

Natywny pretrening wiąże się jednak z istotnymi wyzwaniami:

- Koszt obliczeniowy. Trening nowego modelu VLM od podstaw kosztuje tyle samo co trening bazowego LLM — wymaga milionów godzin GPU. Podejście post-hoc pozwala na ponowne użycie gotowych wag LLM, oszczędzając większość budżetu badawczo-rozwojowego.
- Dane. Zbiory danych z przeplatanymi obrazami i tekstami na dużą skalę są trudne do pozyskania. OBELICS to 141 milionów dokumentów, a MMC4 to 571 milionów. Dla porównania, dane tekstowe liczy się w dziesiątkach bilionów tokenów. Niedobór danych multimodalnych do pretreningu stanowi fizyczny limit.
- Brak możliwości wymiany LLM. Natywny pretrening uniemożliwia łatwą podmianę modelu tekstowego na nowszą wersję. W podejściu post-hoc można podmienić model Llama-3.1 na Llama-4, dotrenowując jedynie sam projektor.

Twórcy InternVL3 wykazali, że zyski z redukcji długu wyrównania przewyższają te ograniczenia. Niemniej jednak, wysoki koszt treningu sprawia, że modele post-hoc nadal będą powszechnie stosowane w większości projektów ze względów ekonomicznych.

## Użycie praktyczne

Skrypt `code/main.py` zawiera:

- Moduł miksowania danych treningowych obliczający optymalne proporcje dla poszczególnych modalności.
- Symulator działania routera rozdzielczości ViR dla paczki zapytań (dystrybucja: 50% proste obrazy, 30% średnie, 20% szczegółowe) szacujący średnie zużycie tokenów.
- Analizator szacunkowej przepustowości wdrożenia DvD w porównaniu z wdrożeniem klasycznym.
- Porównanie parametrów, kosztów i ryzyka długu wyrównania dla pretreningu natywnego oraz post-hoc.

## Zadanie zaliczeniowe

W ramach tej lekcji należy stworzyć dokument `outputs/skill-native-vs-posthoc-auditor_pro.md`. Na podstawie planowanego budżetu i specyfikacji projektu VLM, przeprowadź audyt oceniający opłacalność wdrożenia pretreningu natywnego w stosunku do post-hoc, wskaż ryzyka związane z długiem wyrównania i zaproponuj optymalne proporcje miksu danych. Korzystaj z tej umiejętności na etapie planowania nowych projektów badawczo-rozwojowych VLM.

## Ćwiczenia

1. Oszacuj różnicę w kosztach obliczeniowych (roboczogodzinach GPU) pomiędzy natywnym pretreningiem InternVL3-8B a treningiem post-hoc LLaVA-OneVision-7B. Z czego wynika ta różnica?

2. InternVL3 stosuje proporcje: 40% tekst, 35% dane przeplatane, 20% opisy obrazów, 5% wideo. Zaproponuj modyfikację tych proporcji dla modelu dedykowanego do zaawansowanej analizy wideo. Wyjaśnij, dlaczego model wciąż będzie wymagał znacznego udziału danych tekstowych i opisów obrazów.

3. Przeczytaj sekcję 4 w publikacji MM1.5 dotyczącą utraty kompetencji tekstowych (zapominania). Wskaż benchmark, w którym trening post-hoc zanotował największy spadek jakości i określ skalę tej regresji.

4. Klasyfikator ViR kieruje 60% ruchu do niskiej rozdzielczości. Jakie typy zapytań mogą zostać błędnie sklasyfikowane przez router (skierowane do niskiej rozdzielczości pomimo potrzeby wysokiej)? Zaproponuj trzy scenariusze błędów routera.

5. Wdrożenie DvD rozdziela encoder wizyjny i LLM na osobne procesory graficzne. W jakim profilu ruchu takie rozdzielenie może pogorszyć ogólną przepustowość systemu zamiast ją poprawić?

## Słownik pojęć

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|-----------------|--------------------------------------|
| Natywny pretrening zintegrowany | „Wspólny trening od zera” | Proces optymalizacji wag modelu na danych tekstowych i wizualnych jednocześnie od pierwszego kroku optymalizacji. |
| Dług wyrównania (Alignment debt) | „Kara za post-hoc” | Pogorszenie sprawności językowej oraz spójności odpowiedzi wynikające z prób dołączania gałęzi wizyjnej do gotowego, zamrożonego LLM. |
| V2PE | „Zmienne kodowanie pozycji” | Metoda kodowania pozycji z trenowalnym parametrem podziału wymiarów w zależności od modalności (tekst/obraz/wideo). |
| ViR | „Router rozdzielczości” | Moduł klasyfikacyjny decydujący o minimalnej rozdzielczości wejściowej obrazu przed jego przetworzeniem przez encoder. |
| DvD | „Rozdzielone wdrażanie” | Architektura serwowania modeli, w której encoder wizyjny i LLM są hostowane na osobnych GPU i komunikują się strumieniowo. |
| InternVL-U | „Zrozumienie + generowanie” | Wariant modelu InternVL z zaimplementowaną możliwością syntezy obrazów za pomocą głowic MMDiT. |
| Korpus przeplatany | „OBELICS / MMC4” | Zbiory danych zawierające naprzemiennie występujące obrazy i bloki tekstu w ich naturalnej kolejności występowania na stronach www. |

## Dalsze czytanie

- [Chen et al. — InternVL 1 (arXiv:2312.14238)](https://arxiv.org/abs/2312.14238)
- [Zhu et al. — InternVL3 (arXiv:2504.10479)](https://arxiv.org/abs/2504.10479)
- [InternVL3.5 (arXiv:2508.18265)](https://arxiv.org/abs/2508.18265)
- [InternVL-U (arXiv:2603.09877)](https://arxiv.org/abs/2603.09877)
- [Zhang et al. — MM1.5 (arXiv:2409.20566)](https://arxiv.org/abs/2409.20566)
