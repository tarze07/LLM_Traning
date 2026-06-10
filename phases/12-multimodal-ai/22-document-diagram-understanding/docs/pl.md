# Zrozumienie dokumentu i diagramu

> Dokumenty to nie zdjęcia. Plik PDF, artykuł naukowy, faktura lub formularz odręczny ma układ, tabele, diagramy, przypisy, nagłówki i strukturę semantyczną, której nie można uchwycić zwykłym obrazem. Stos sprzed VLM był potokiem: Tesseract OCR + LayoutLMv3 + heurystyka wyodrębniania tabel. Fala VLM zastąpiła to modelami bez OCR — Donut (2022), Nougat (2023), DocLLM (2023) — które bezpośrednio emitują znaczniki strukturalne. Do roku 2026 granica będzie polegać jedynie na „przesyłaniu obrazu strony do Claude Opus 4.7 w natywnej rozdzielczości 2576 pikseli”, a wyniki w postaci znaczników strukturalnych będą dostępne bezpłatnie. W tej lekcji omówiono trzy ery dokumentu AI.

**Typ:** Kompilacja
**Języki:** Python (stdlib, szkielet analizatora dokumentów uwzględniający układ)
**Wymagania wstępne:** Faza 12 · 05 (LLaVA), Faza 5 (NLP)
**Czas:** ~180 minut

## Cele nauczania

- Wyjaśnij trzy epoki sztucznej inteligencji dokumentów: potok OCR, brak OCR, natywny VLM.
- Opisz trzy strumienie wejściowe LayoutLMv3: tekst, układ (bbox), poprawki obrazu, z ujednoliconym maskowaniem.
- Porównaj Donut (bez OCR, obraz → znaczniki), Nougat (artykuł naukowy → LaTeX), DocLLM (generatywny z uwzględnieniem układu), PaliGemma 2 (natywny dla VLM).
- Wybierz wzór dokumentu dla nowego zadania (faktury, artykuły naukowe, formularze odręczne, chińskie paragony).

## Problem

„Zrozumienie tego pliku PDF” jest zwodniczo trudne. Informacje znajdują się w:

- Treść tekstowa (90% sygnału).
- Układ (nagłówki, przypisy, paski boczne, format dwukolumnowy).
- Tabele (wiersze, kolumny, połączone komórki).
- Rysunki i diagramy.
- Odręczne adnotacje.
- Czcionki i typografia (tytuł vs treść).

Surowy OCR zrzuca tekst i traci resztę. System dbający o faktury musi wiedzieć, że informacja „Łącznie: 1245 USD” pochodzi z prawego dolnego rogu, a nie z przypisu.

## Koncepcja

### Era 1 – rurociąg OCR (przed 2021 r.)

Klasyczny stos:

1. PDF → obraz na stronę.
2. Tesseract (lub komercyjny OCR) wyodrębnia tekst z ramkami ograniczającymi poszczególne słowa.
3. Analizator układu identyfikuje bloki (nagłówek, tabela, akapit).
4. Moduł rozpoznawania struktury tabeli analizuje tabele.
5. Reguły domeny + pola wyodrębniania wyrażeń regularnych.

Działa w przypadku czystego drukowanego tekstu. Przerwy w pismie ręcznym, przekrzywione skany, złożone tabele, skrypty w języku innym niż angielski. Każdy tryb awarii wymaga niestandardowej ścieżki wyjątku.

### TroCr (2021)

TrOCR (Li et al., arXiv:2109.10282) zastąpił klasyczny CNN-CTC firmy Tesseract transformatorowym koderem-dekoderem wytrenowanym na syntetycznych i rzeczywistych obrazach tekstowych. Czysta wygrana dzięki odręcznemu i wielojęzycznemu tekstowi. To wciąż potok (detektor, potem TrOCR, a potem układ), ale etap OCR uległ znacznej poprawie.

### Era 2 — bez OCR (2022–2023)

Pierwsze modele wolne od OCR mówiły: całkowicie pomiń wykrywanie, mapuj piksele obrazu bezpośrednio na ustrukturyzowane wyjście.

Pączek (Kim i in., arXiv:2111.15664):
- Transformator enkoder-dekoder, enkoder to Swin-B.
- Dane wyjściowe to JSON w celu zrozumienia formularza, przeceny w celu podsumowania lub dowolnego schematu specyficznego dla zadania.
- Bez OCR, bez układu, bez wykrywania.

Nugat (Blecher i in., arXiv:2308.13418):
- Przeszkolony specjalnie w oparciu o artykuły naukowe.
- Dane wyjściowe to LaTeX / przecena.
- Obsługuje równania, układ wielokolumnowy, liczby.
- Model wywoływany przez każdy parser arXiv.

To są specjaliści, a nie generaliści. Pączek w artykule naukowym kończy się niepowodzeniem; Nugat na fakturze kończy się niepowodzeniem.

### UkładLMv3 (2022)

Inny utwór. LayoutLMv3 (Huang i in., arXiv:2204.08387) zachowuje OCR, ale dodaje zrozumienie układu:

- Trzy strumienie wejściowe: tokeny tekstowe OCR, ramki ograniczające 2D na token, poprawki obrazu.
- Zamaskowany cel szkoleniowy we wszystkich trzech modalnościach (zamaskowany tekst, zamaskowane łaty, zamaskowany układ).
- Dalszy ciąg: klasyfikacja, ekstrakcja jednostek, tabela QA.

LayoutLMv3 to szczyt zrozumienia dokumentów w oparciu o OCR. Mocny w kwestii formularzy i faktur. Wymaga wcześniejszego OCR. Najlepsza dokładność przed wprowadzeniem VLM w standardowych testach porównawczych dokumentów.

### DokumentLLM (2023)

DocLLM (Wang i in., arXiv:2401.00908) to generatywne rodzeństwo LayoutLM. Generuje odpowiedzi w dowolnej formie uzależnione od tokenów układu. Lepiej dla kontroli jakości dokumentów; nadal zależy od danych wejściowych OCR.

### Era 3 — natywna dla VLM (2024+)

VLM z 2024 r. stały się na tyle dobre, że całkowicie zastąpiły rurociąg. Prześlij obraz całej strony w wysokiej rozdzielczości do VLM, zadaj pytanie i uzyskaj odpowiedź.

- LLaVA-NeXT 336-kafelkowa AnyRes sprawdza się w przypadku małych dokumentów.
- Dynamiczna rozdzielczość Qwen2.5-VL obsługuje natywnie ponad 2048 pikseli.
- Claude Opus 4.7 obsługuje dokumenty o rozdzielczości 2576 pikseli.
- PaliGemma 2 (kwiecień 2025) szkoli się specjalnie w zakresie dokumentów + pisma ręcznego.

Luka pomiędzy natywnym systemem VLM a potokiem OCR szybko się zmniejszyła. Do 2026 r. natywne rozwiązania VLM będą wygrywać na:

- Tekst sceny (pisany odręcznie + drukowany, pisma mieszane).
- Złożone tabele z połączonymi komórkami.
- Równania matematyczne osadzone w tekście.
- Ryciny z adnotacjami tekstowymi.

Potoki OCR nadal wygrywają na:

- Obciążenia związane z czystym skanowaniem na masową skalę, gdzie liczy się opóźnienie przypadające na stronę.
- Niezawodność rurociągu (deterministyczne awarie vs halucynacje VLM).
- Środowiska regulowane wymagające kontrolowanych wyników OCR.

### Granica Claude 4.7 / GPT-5

Przy natywnej rozdzielczości wejściowej 2576 pikseli, pionierskie VLM dokumentują zrozumienie z niemal ludzką dokładnością. Wartości referencyjne z początku 2026 r.:

- DocVQA: Claude 4.7 ~95.1, PaliGemma 2 ~88.4, Nougat ~77.3, potokowy LayoutLMv3 ~83.
- WykresQA: Claude 4,7 ~92,2, GPT-4V ~78.
- VisualMRC: Claude 4.7 ~ 94.

Luka w modelu zamkniętym to głównie rozdzielczość i podstawowa skala LLM. Modele otwarte na poziomie 7B mają kilka punktów straty, ale nadrabiają zaległości.

### Równania matematyczne i dane wyjściowe LaTeX

Artykuły naukowe wymagają dokładnych wyników LaTeX dla równań. Nougat został w tym przeszkolony. VLM przeszkolone z celami LaTeX (Qwen2.5-VL-Math, pochodne Nougat) tworzą użyteczny LaTeX. Bez wyraźnego szkolenia LaTeX, VLM tworzą czytelne, ale nieprecyzyjne transkrypcje.

W przypadku publikacji artykułów naukowych w 2026 r.: łańcuch Nougat w pliku PDF, a następnie VLM na trudnych stronach.

### Pismo ręczne

Wciąż najtrudniejsze podzadanie. Druk mieszany i pismo odręczne (zapisy lekarskie, wypełnione formularze) to obszary, w których systemy OCR wciąż pokonują VLM pod względem kosztów. Poprawiają się pliki VLM pisane wyłącznie odręcznie (Claude 4.7, PaliGemma 2).

### Przepis z 2026 r

W przypadku nowego projektu AI dotyczącego dokumentów:

- Faktury drukowane w dużej skali: LayoutLMv3 + reguły, ekonomiczne.
- Dokumenty mieszane (naukowe + odręczne + formularze): natywne dla VLM (PaliGemma 2 lub Qwen2.5-VL).
- Pełne wykorzystanie arXiv: Nougat dla matematyki, VLM dla liczb.
- Przepisy: rurociąg OCR + walidator VLM do kontroli krzyżowej.

## Użyj tego

`code/main.py`:

- Tokenizator obsługujący układ zabawek: podane pary (tekst, bbox) generują dane wejściowe w stylu LayoutLMv3.
- Generator schematów zadań w stylu pączka: szablon JSON dla formularzy.
- Porównanie budżetów tokenów na stronę w potoku OCR, Donut, Nougat i natywnym VLM.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-document-ai-stack-picker.md`. Biorąc pod uwagę projekt AI oparty na dokumentach (domena, skala, jakość, regulacje), wybiera pomiędzy potokiem OCR, specjalistą bez OCR i natywnym VLM.

## Ćwiczenia

1. Twój projekt to 10 milionów faktur dziennie. Który stos minimalizuje koszt strony bez utraty dokładności?

2. Dlaczego LayoutLMv3 przewyższa czyste CLIP-VLM w formularzu kontroli jakości, ale słabiej radzi sobie z tekstem sceny? Co daje strumień bbox?

3. Nougat generuje LaTeX. Zaproponuj przypadek testowy, w którym natywne dane wyjściowe VLM przewyższają Nougat pod względem wierności LaTeX, oraz przypadek, w którym Nougat wygrywa.

4. Przeczytaj artykuł PaliGemma 2 (Google, 2024). Jaki był kluczowy dodatek do danych szkoleniowych, który podniósł dokładność dokumentu w porównaniu z PaliGemma 1?

5. Zaprojektuj hybrydę bezpieczną pod względem regulacyjnym: rurociąg OCR jako podstawowy, VLM jako dodatkowa kontrola krzyżowa. Jak rozwiązać spór?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Rurociąg OCR | „W stylu Tesseraktu” | Stos etapowy: wykrywanie -> OCR -> układ -> reguły; deterministyczny, kruchy |
| Bez OCR | „W stylu pączka” | Transformator obrazu na wyjście, który pomija jawne OCR; pojedynczy model |
| Obsługuje układ | „UkładLM” | Dane wejściowe obejmują współrzędne bbox dla każdego tokenu; ujednolicone maskowanie we wszystkich modalnościach |
| Natywny VLM | „Granica VLM” | Prześlij obraz strony bezpośrednio do Claude/GPT/Qwen VLM w wysokiej rozdzielczości; brak rurociągu |
| DokumentVQA | „Porównanie dokumentacyjne” | Dokument standardu VQA; najczęściej cytowany wynik |
| Dane wyjściowe znaczników | „LaTeX/MD” | Ustrukturyzowany format wyjściowy zamiast tekstu w dowolnej formie; umożliwia dalszą automatyzację |

## Dalsze czytanie

- [Li i in. — TrOCR (arXiv:2109.10282)](https://arxiv.org/abs/2109.10282)
- [Blecher i in. — Nugat (arXiv:2308.13418)](https://arxiv.org/abs/2308.13418)
- [Huang i in. — UkładLMv3 (arXiv:2204.08387)](https://arxiv.org/abs/2204.08387)
- [Kim i in. — Pączek (arXiv:2111.15664)](https://arxiv.org/abs/2111.15664)
- [Wang i in. — DocLLM (arXiv:2401.00908)](https://arxiv.org/abs/2401.00908)