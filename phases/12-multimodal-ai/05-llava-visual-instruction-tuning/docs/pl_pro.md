# LLaVA i strojenie instrukcji wizualnych (Visual Instruction Tuning)

> LLaVA (kwiecień 2023) to najchętniej kopiowana architektura multimodalna na świecie. Autorzy zastąpili Q-Former z BLIP-2 dwuwarstwowym MLP, zrezygnowali z bramkowanego cross-attention znanego z Flamingo na rzecz zwykłej konkatenacji tokenów, i przeprowadzili trening na 158 tys. tur dialogów instruktażowych (instrukcji wizualnych) wygenerowanych przez GPT-4 na podstawie opisów tekstowych. Każdy inżynier budujący model VLM w latach 2023–2026 korzystał z jakiegoś wariantu LLaVA. LLaVA-1.5 dodała technikę AnyRes. LLaVA-NeXT zwiększyła rozdzielczość wejściową. LLaVA-OneVision zunifikowała przetwarzanie pojedynczych obrazów, wielu obrazów oraz wideo w ramach jednej procedury treningowej. W tej lekcji przeanalizujemy ten przepis treningowy, zaimplementujemy projektor i wyjaśnimy, dlaczego w tym przypadku „wygrała prostota”.

**Typ:** Projekt / Implementacja
**Języki:** Python (biblioteka standardowa, projektor + generator szablonów instrukcji)
**Wymagania wstępne:** Faza 12 · Lekcja 02 (CLIP), Faza 11 (Inżynieria LLM — strojenie instruktażowe)
**Czas:** ~180 minut

## Cele nauczania

- Zbuduj 2-warstwowy projektor MLP mapujący embeddingi patchy ViT (wymiar 1024) na przestrzeń embeddingów LLM (wymiar 4096).
- Przejdź przez dwuetapowy proces szkolenia LLaVA: (1) wyrównanie projektora na 558 tys. par obraz-opis, (2) dostrajanie instrukcji wizualnych (visual instruction tuning) na 158 tys. tur dialogowych wygenerowanych przez GPT-4.
- Skonstruuj prompt w formacie LLaVA z placeholderem tokena obrazu, promptem systemowym oraz turami użytkownika i asystenta.
- Wyjaśnij, dlaczego społeczność naukowa odeszła od Q-Formera na rzecz MLP, mimo wyższych kosztów w budżecie tokenów.

## Problem

Q-Former w BLIP-2 (Lekcja 12.03) kompresuje cechy obrazu do 32 tokenów. Jest to rozwiązanie eleganckie, wydajne i świetne do testów porównawczych. Niesie jednak ze sobą dwa poważne problemy.

Po pierwsze, choć Q-Former jest trenowalny, optymalizowana funkcja straty nie jest tożsama z końcowym zadaniem generowania. Etap 1 optymalizuje ITC + ITM + ITG. Etap 2 trenuje stratę modelowania języka (LM loss). Zapytania uczą się pośredniej reprezentacji, którą LLM musi następnie zdekodować. Informacje te ulegają częściowej utracie w tym wąskim gardle (bottleneck).

Po drugie, Q-Former ma 188 milionów parametrów i w realiach roku 2023 musiał być ściśle dostosowywany (wspólnie trenowany) z konkretnym, docelowym LLM. Zmiana LLM wymagała ponownego wytrenowania Q-Formera. Zmiana encodera wizyjnego również wymagała ponownego treningu. Każda taka kombinacja była osobnym, kosztownym projektem badawczo-rozwojowym.

Odpowiedź LLaVA była uderzająco prosta: pobierz wszystkie 576 tokenów patchy z ViT, przepuść każdy z nich przez 2-warstwowy MLP (`1024 → 4096 → 4096`) i wstaw całe 576 tokenów bezpośrednio do sekwencji wejściowej LLM. Bez wąskiego gardła. Bez skomplikowanego pretreningu pierwszego etapu z wieloma funkcjami strat. Po prostu trenuj MLP na bezpośredniej stracie LM.

Skąd wziąć dane instruktażowe? Druga innowacja LLaVA polegała na użyciu GPT-4 (pracującego wyłącznie na tekście) do generowania danych. Przekazano do GPT-4 opisy COCO oraz współrzędne ramek otaczających (bounding boxes) obiektów na obrazie, prosząc model o wygenerowanie na tej podstawie naturalnych konwersacji, szczegółowych opisów oraz złożonych pytań wymagających logicznego rozumowania. W ten sposób uzyskano 158 tys. tur instrukcja-odpowiedź praktycznie bezkosztowo, eliminując potrzebę ręcznego etykietowania przez ludzi.

Rezultat: model VLM, którego trening na 8 kartach A100 zajął zaledwie jeden dzień, pokonał Flamingo na benchmarku MMMU i dostarczył społeczności otwarty checkpoint do dalszego rozwoju. Do końca 2023 roku powstało ponad 50 jego forków.

## Koncepcja

### Architektura

LLaVA-1.5 w wersji 13B:
- Encoder wizyjny: CLIP ViT-L/14 @ 336 (zamrożony w Etapie 1, opcjonalnie odblokowany w Etapie 2).
- Projektor: 2-warstwowy MLP z aktywacją GELU, `1024 → 4096 → 4096`.
- LLM: Vicuna-13B (w późniejszych wersjach Llama-3.1-8B).

Przebieg forward dla obrazu i promptu tekstowego:

```
img -> ViT -> 576 patchy o wymiarze 1024
patches -> MLP -> 576 tokenów o wymiarze 4096
prompt: system + placeholder "<image>" + pytanie użytkownika
zastąp token <image> przez 576 rzutowanych tokenów wizualnych
podaj całą sekwencję do LLM
dekoduj odpowiedź
```

Obraz zajmuje 576 tokenów z okna kontekstowego LLM. Przy kontekście o rozmiarze 2048 pozostawia to 1472 tokeny na tekst. W przypadku współczesnych kontekstów o rozmiarze 32k lub większym jest to pomijalny koszt.

### Etap 1: Strojenie projektora (Alignment)

Zamrażamy ViT. Zamrażamy LLM. Trenujemy wyłącznie 2-warstwowy MLP. Zbiór danych: 558 tys. par obraz-opis (LAION-CC-SBU). Funkcja straty: modelowanie języka (LM loss) na opisie tekstowym, uwarunkowane rzutowanymi tokenami obrazu.

Przy wielkości paczki (batch size) równej 128 trening ten zajmuje zaledwie kilka godzin w ramach jednej epoki. Projektor uczy się mapować reprezentacje z przestrzeni ViT do przestrzeni LLM bez nadzoru pod konkretne zadanie.

### Etap 2: Strojenie instrukcji wizualnych (Visual Instruction Tuning)

Odblokowujemy wagi projektora (pozostaje trenowalny). Odblokowujemy wagi LLM (zazwyczaj w pełni, czasami stosując LoRA). Trenujemy model na 158 tys. tur dialogowych z instrukcjami wizualnymi.

Kluczem jest tu sposób generowania danych instruktażowych przez Liu et al.:
1. Pobrano obraz ze zbioru COCO.
2. Wyodrębniono jego opis tekstowy (5 opisów stworzonych przez ludzi + lista współrzędnych ramek otaczających).
3. Przekazano te informacje do GPT-4 z prośbą o wygenerowanie danych w trzech kategoriach:
   - Konwersacja: „Stwórz spójny dialog pomiędzy użytkownikiem a asystentem na temat tego obrazu”.
   - Szczegółowy opis: „Podaj wyczerpujący, szczegółowy opis tego, co widać na obrazie”.
   - Złożone rozumowanie: „Zadaj pytanie wymagające logicznego wnioskowania na temat obrazu, a następnie napisz odpowiedź”.
4. Podzielono wyjście z GPT-4 na pary (instrukcja, odpowiedź).

Co ważne, GPT-4 nie widział samego obrazu, a jedynie jego tekstowe opisy, na podstawie których generował wiarygodne dialogi. Mimo drobnych szumów w danych, ta metoda okazała się niezwykle skuteczna — 158 tys. tur wystarczyło do opanowania swobodnej konwersacji o obrazach.

### Dlaczego ten projekt zdominował społeczność

- Brak skomplikowanych funkcji strat w 1. etapie. Cały proces optymalizuje standardową stratę LM.
- Trening projektora trwa godziny, a nie dni.
- Bazowy LLM można łatwo wymienić (np. LLaVA-Llama2, LLaVA-Mistral, LLaVA-Llama3), trenując od nowa jedynie sam projektor.
- Proces generowania danych za pomocą GPT-4 jest tani i łatwy do powtórzenia dla dowolnej nowej domeny.

### LLaVA-1.5 oraz LLaVA-NeXT

LLaVA-1.5 (październik 2023):
- Wprowadzono dane z akademickich benchmarków (VQA, OKVQA, RefCOCO) do etapu strojenia instrukcji.
- Ulepszono prompt systemowy.
- Zwiększono okno kontekstowe z 2048 do 32k tokenów.

LLaVA-NeXT (styczeń 2024):
- Technologia AnyRes: obraz o wysokiej rozdzielczości jest dzielony na siatkę kafelków (np. 2x2 lub 1x3) o wymiarach 336x336 każdy, plus jedna globalna miniatura w niskiej rozdzielczości. Każdy wycinek (crop) generuje 576 tokenów, co daje łącznie około 2880 tokenów wizualnych na obraz. Znacząco poprawiło to wyniki w zadaniach OCR i analizie wykresów.
- Ulepszono zestaw danych instruktażowych za pomocą ShareGPT4V (wysokiej jakości opisy z GPT-4V).
- Zastosowano silniejsze modele bazowe LLM (Mistral-7B, Yi-34B).

### LLaVA-OneVision

Lekcja 12.08 szczegółowo omawia architekturę OneVision. W uproszczeniu: wykorzystuje ten sam projektor, ale model jest trenowany na ujednoliconych danych (obrazy statyczne, serie wielu obrazów oraz wideo) z dynamicznym zarządzaniem budżetem tokenów wizualnych.

### Porównanie: Q-Former vs MLP

| Cecha | Q-Former (BLIP-2) | MLP (LLaVA) |
|---|---|---|
| Tokeny wizualne na obraz | 32 | 576 (bazowo) lub 2880 (AnyRes) |
| Trenowalne parametry | 188M + LLM | 40M + LLM |
| Strata w 1. etapie | ITC + ITM + ITG | Tylko strata LM |
| Wymiana LLM | Wymaga pełnego treningu adaptera | Wymaga minimalnego dotrenowania |
| Obsługa wielu obrazów | Skomplikowana | Naturalna (konkatenacja tokenów) |
| Obsługa wideo | Skomplikowana | Naturalna (konkatenacja klatek) |
| Budżet tokenów | Bardzo mały | Duży |

Projektor MLP wygrywa prostotą i elastycznością reprezentacji. Q-Former wygrywa pod kątem minimalnego zużycia kontekstu. Pod koniec 2023 roku, gdy okna kontekstowe LLM urosły do 32k-128k+ tokenów, budżet przestał być wąskim gardłem i prostota MLP zdominowała rynek.

### Format promptu

```
A chat between a curious human and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the human's questions. USER: <image> Describe this image in detail. ASSISTANT: The image shows ...
```

`<image>` to token zastępczy (placeholder). Przed procesem tokenizacji jest on podmieniany na 576 tokenów wizualnych (lub 2880 w przypadku AnyRes). Tokenizer przetwarza nieco dłuższą sekwencję niż zazwyczaj, ale LLM bez problemu radzi sobie z tym wejściem dzięki dopasowaniu zrealizowanemu w Etapie 1.

### Podział parametrów

Struktura modelu LLaVA-1.5-7B:
- CLIP ViT-L/14 @ 336: 303M parametrów (zamrożone w Etapie 1, często odblokowane w Etapie 2).
- Projektor (2 warstwy liniowe): ~22M parametrów (trenowalny).
- Llama-7B: 7B parametrów.
- Łącznie: 7,3B parametrów. W Etapie 2 trenowany jest cały model (7B LLM + 22M projektor).

Koszt treningu Etapu 2: ~20 godzin na 8 kartach A100. Ta powtarzalność na jednym węźle obliczeniowym w dobę zdecydowała o ogromnej popularności projektu LLaVA.

## Użycie praktyczne

Skrypt `code/main.py` zawiera:

1. Implementację 2-warstwowego projektora MLP (wymiary demonstracyjne: 16 → 32 → 32) w czystym Pythonie.
2. Generator formatowania promptów: łączenie promptu systemowego z placeholderem `<image>` zastępowanym przez N tokenów wizualnych, turą użytkownika i nagłówkiem asystenta.
3. Narzędzie do wizualizacji zajętości okna kontekstowego LLM przez blok 576 tokenów wizualnych (procentowe zużycie dla kontekstów 2k / 32k / 128k).

## Zadanie zaliczeniowe

W ramach tej lekcji należy stworzyć dokument `outputs/skill-llava-vibes-eval_pro.md`. Na podstawie dostarczonego checkpointu z rodziny LLaVA, przeprowadź jakościowy test diagnostyczny (vibes eval) składający się z 10 promptów (3 opisy obrazu, 3 zadania VQA, 2 zadania logicznego rozumowania, 2 przypadki odmowy) i wygeneruj przejrzystą kartę wyników. Test ten ma charakter dymny (smoke test) i służy do potwierdzenia poprawnego połączenia projektora z modelem LLM.

## Ćwiczenia

1. Oblicz dokładną liczbę trenowalnych parametrów dla projektora MLP o strukturze `1024 → 4096 → 4096` (uwzględniając warstwę GELU oraz wektory bias). Jaki procent modelu LLaVA-13B stanowią te parametry?

2. Skonstruuj prompt testowy dla scenariusza odmowy generowania odpowiedzi (np. gdy obraz przedstawia osobę prywatną bez jej zgody). Zapisz oczekiwaną odpowiedź asystenta. Dlaczego bazowa LLaVA mogłaby nie odrzucić takiego zapytania bezpośrednio i jakich danych treningowych należałoby użyć, aby poprawić skuteczność takich odmów?

3. Przeczytaj sekcję dotyczącą AnyRes na blogu LLaVA-NeXT. Oblicz liczbę tokenów wizualnych wygenerowanych dla obrazu o rozdzielczości 1344 x 672. Porównaj ten wynik z bazowymi 576 tokenami dla rozdzielczości 336 x 336.

4. Projektor LLaVA w Etapie 1 jest trenowany na zadaniu modelowania języka na opisach obrazów. Co się stanie, jeśli pominiemy Etap 1 i przejdziemy bezpośrednio do Etapu 2 (strojenie instrukcji wizualnych)? Uzasadnij odpowiedź, powołując się na analizy z publikacji Prismatic VLMs (arXiv:2402.07865).

5. Zbiór LLaVA-Instruct-150k powstał przy użyciu GPT-4 na podstawie opisów COCO. Zaproponuj 4-etapowy proces generowania podobnych danych instruktażowych dla nowej, specjalistycznej domeny (np. zdjęcia satelitarne, diagnostyka medyczna). Wskaż potencjalne błędy i ryzyka na każdym z tych etapów.

## Słownik pojęć

| Termin | Potoczne określenie | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| Projektor | „Mostek MLP” | 2-warstwowa sieć MLP z aktywacją GELU mapująca wymiar cech ViT na wymiar embeddingów LLM. |
| Token obrazu | „Placeholder <image>” | Znacznik w prompcie tekstowym zastępowany przed wnioskowaniem przez N rzutowanych tokenów wizualnych. |
| Strojenie instrukcji wizualnych | „LLaVA Etap 2” | Dostrajanie modelu (SFT) na trójkach (obraz, instrukcja, odpowiedź) wygenerowanych za pomocą GPT-4. |
| Wyrównanie w Etapie 1 | „Pretrening projektora” | Trening samego projektora przy zamrożonych wagach ViT i LLM na zadaniu modelowania języka (opisy obrazów). |
| AnyRes | „Siatka kafelków (multi-crop)” | Metoda polegająca na podziale obrazu wysokiej rozdzielczości na kafelki o mniejszym rozmiarze i łączeniu ich tokenów wizualnych wraz z obrazem globalnym. |
| LLaVA-Instruct | „Instrukcje z GPT-4” | Zestaw 158 tys. par instrukcja-odpowiedź wygenerowany syntetycznie przez GPT-4 na podstawie tekstowych metadanych z COCO. |
| Zamrożony encoder wizyjny | „Frozen vision backbone” | Wagi modelu CLIP nie są modyfikowane w Etapie 1 (oraz opcjonalnie w Etapie 2). |
| ShareGPT4V | „Opisy wysokiej jakości” | Zbiór 1 miliona szczegółowych opisów wygenerowanych za pomocą GPT-4V, służący do lepszego dopasowania modalności. |
| VQA | „Visual Question Answering” | Zadanie polegające na udzieleniu odpowiedzi tekstowej na pytanie dotyczące załączonego obrazu. |
| Prismatic VLMs | „Praca o przestrzeni projektowej” | Publikacja (Karamcheti et al., 2024) systematycznie badająca wpływ doboru projektorów i danych treningowych na jakość VLM. |

## Dalsze czytanie

- [Liu et al. — Visual Instruction Tuning (arXiv:2304.08485)](https://arxiv.org/abs/2304.08485) — oryginalny artykuł o LLaVA.
- [Liu et al. — Improved Baselines with Visual Instruction Tuning (arXiv:2310.03744)](https://arxiv.org/abs/2310.03744) — publikacja wprowadzająca LLaVA-1.5.
- [Chen et al. — ShareGPT4V (arXiv:2311.12793)](https://arxiv.org/abs/2311.12793) — artykuł o zbiorze ShareGPT4V.
- [Karamcheti et al. — Prismatic VLMs (arXiv:2402.07865)](https://arxiv.org/abs/2402.07865) — systematyczne badanie konfiguracji VLM.
- [Li et al. — LLaVA-OneVision (arXiv:2408.03326)](https://arxiv.org/abs/2408.03326) — zunifikowany model dla obrazów i wideo.
