# Rozumienie dokumentów i diagramów

> Dokumenty to coś więcej niż zwykłe zdjęcia. Plik PDF, artykuł naukowy, faktura czy wypełniony odręcznie formularz posiadają określony układ (layout), tabele, wykresy, przypisy, nagłówki oraz głęboką strukturę semantyczną, której tradycyjny model obrazu nie potrafi w pełni zinterpretować. Przed erą modeli VLM standardowy stos technologiczny składał się z kaskady: Tesseract OCR + LayoutLMv3 + heurystyki do ekstrakcji tabel. Pojawienie się modeli VLM przyniosło rozwiązania typu OCR-free (bezpośrednio przetwarzające piksele) – takie jak Donut (2022), Nougat (2023) czy DocLLM (2023) – generujące ustrukturyzowany tekst wynikowy. Z kolei w 2026 roku standardem stało się bezpośrednie przesyłanie obrazu strony do zaawansowanych modeli takich jak Claude 4.7 w wysokiej rozdzielczości (np. 2576px) i odbieranie gotowego, ustrukturyzowanego formatu markdown/JSON. Ta lekcja opisuje trzy ery rozwoju technologii Document AI.

**Typ:** Teoria / Ewolucja
**Języki:** Python (biblioteka standardowa, szkielet parsera dokumentów uwzględniający układ - layout-aware)
**Wymagania wstępne:** Faza 12 · 05 (LLaVA), Faza 5 (NLP)
**Czas:** ~180 minut

## Cele kształcenia

- Wyjaśnienie trzech er rozwoju Document AI: potoki OCR, modele OCR-free oraz natywne modele VLM.
- Opisanie trzech strumieni wejściowych w LayoutLMv3 (tekst, współrzędne układu/bbox, patche obrazu) wraz z ujednoliconym mechanizmem maskowania.
- Porównanie modeli Donut (OCR-free, obraz → ustrukturyzowany format), Nougat (artykuł naukowy → LaTeX), DocLLM (generatywne uwzględnianie układu) oraz PaliGemma 2 (natywny model VLM).
- Dobór odpowiedniej architektury dla nowych zadań biznesowych (faktury, publikacje naukowe, formularze odręczne, paragony).

## Problem

„Rozumienie plików PDF” bywa zwodniczo trudne. Kluczowe informacje są bowiem zakodowane w:

- Treści tekstowej (stanowiącej 90% sygnału).
- Układzie graficznym (nagłówki, przypisy, kolumny, sekcje boczne).
- Tabelach (wiersze, kolumny, scalone komórki).
- Rysunkach, wykresach i schematach.
- Ręcznych dopiskach i adnotacjach.
- Typografii (wyróżnienia czcionki, tytuły).

Prosty mechanizm OCR wyodrębnia jedynie płaski ciąg znaków, tracąc całą strukturę geometryczną. System przetwarzający faktury musi wiedzieć, że wartość „Suma: 1245 USD” powiązana jest z konkretną tabelą w prawym dolnym rogu, a ze nie pochodzi np. z przypisu regulaminu.

## Koncepcja

### Era 1: Potoki OCR (przed rokiem 2021)

Typowy stos technologiczny:

1. PDF → renderowanie obrazu każdej strony.
2. Tesseract (lub komercyjny silnik OCR) wyodrębniający tekst wraz ze współrzędnymi ramek (bounding boxes - bbox) dla poszczególnych słów.
3. Analizator układu (Layout parser) dzielący stronę na bloki (nagłówki, tabele, akapity).
4. Moduł ekstrakcji tabel (Table structure recognizer).
5. Reguły biznesowe i wyrażenia regularne (regex) parsujące wyjściowy tekst.

Rozwiązanie to sprawdza się przy idealnie wydrukowanych dokumentach tekstowych. Pismo ręczne, przekrzywione skany, złożone struktury tabel czy znaki narodowe łatwo powodują błędy. Każda taka awaria wymaga pisania dedykowanych reguł obsługi wyjątków.

### TrOCR (2021)

Model TrOCR (Li i in., arXiv:2109.10282) zastąpił klasyczny moduł CNN-CTC (znany z Tesseract) architekturą transformerową typu koder-dekoder, wytrenowaną na zróżnicowanych rzeczywistych oraz syntetycznych próbkach tekstu. Zapewniło to ogromny zysk jakościowy przy analizie pisma ręcznego i tekstów wielojęzycznych. Wciąż był to jednak potok wieloetapowy (detektor linii → TrOCR → pozycjonowanie w układzie).

### Era 2: Modele OCR-free (2022–2023)

Pierwsze modele wolne od OCR (OCR-free) założyły całkowite pominięcie wstępnej detekcji tekstu i bezpośrednie mapowanie pikseli wejściowych na ustrukturyzowany format wyjściowy.

- **Donut** (Kim i in., arXiv:2111.15664): Wykorzystuje transformator koder-dekoder (z enkoderem Swin-B). Wyjściem modelu jest bezpośrednio JSON (dla formularzy i faktur) lub markdown (do podsumowań).
- **Nougat** (Blecher i in., arXiv:2308.13418): Model wyszkolony specjalnie pod kątem publikacji naukowych. Wyjściem modelu jest format LaTeX / markdown. Radzi sobie ze skomplikowanymi równaniami, dwukolumnowym układem tekstu oraz wykresami.
- **DocLLM** (Wang i in., arXiv:2401.00908): Generatywny odpowiednik serii LayoutLM. Generuje odpowiedzi na pytania w oparciu o geometrię i układ dokumentu, lecz wciąż wymaga dostarczenia cech z OCR na wejściu.

Były to modele wyspecjalizowane: Donut zawodzi na artykułach naukowych, a Nougat nie nadaje się do faktur.

### LayoutLMv3 (2022)

Inna linia rozwoju. LayoutLMv3 (Huang i in., arXiv:2204.08387) zachowuje etap OCR, ale łączy go głęboko z geometrią układu strony:

- Trzy strumienie wejściowe: tokeny tekstowe z OCR, ramki geometryczne 2D (bbox) dla każdego tokenu oraz patche (fragmenty) obrazu.
- Ujednolicone maskowanie (masked language modeling) na wszystkich trzech modalnościach.
- Zastosowanie: klasyfikacja dokumentów, ekstrakcja danych klucz-wartość, QA na tabelach.

LayoutLMv3 stanowi szczytowe osiągnięcie systemów opartych na OCR. Wykazuje się najwyższą dokładnością w standardowych benchmarkach faktur i formularzy, lecz wymaga uprzedniego uruchomienia silnika OCR.

### Era 3: Natywne modele VLM (2024+)

Modele VLM po 2024 roku rozwinęły się na tyle, że zaczęły eliminować potrzebę stosowania skomplikowanych potoków Document AI. Wystarczy przesłać obraz strony w wysokiej rozdzielczości bezpośrednio do VLM, aby uzyskać dokładną odpowiedź.

- Mechanizm AnyRes w LLaVA-NeXT (kafelkowanie obrazu) ułatwił czytanie drobnego tekstu.
- Qwen2.5-VL ze swoją dynamiczną rozdzielczością natywnie obsługuje obrazy powyżej 2048px.
- Claude 4.7 bez problemu przetwarza obrazy stron o rozdzielczości 2576px.
- PaliGemma 2 (Google, 2025) jest dodatkowo dotrenowana na dokumentach i piśmie ręcznym.

Różnica jakościowa między natywnym VLM a tradycyjnym potokiem OCR uległa zatarciu. W 2026 roku natywne modele VLM wygrywają w zadaniach takich jak:
- Teksty pisane odręcznie i mieszane czcionki.
- Złożone tabele o nieregularnej strukturze (scalone komórki).
- Wzory i równania matematyczne wplecione w tekst.
- Opisy wykresów i schematów.

Klasyczne potoki OCR wciąż zachowują przewagę w:
- Przetwarzaniu masowym o bardzo niskim budżecie czasowym (koszt/opóźnienie na stronę).
- Determinizmie działania (VLM mogą halucynować, podczas gdy OCR daje dosłowne odczytanie).
- Zastosowaniach regulowanych prawnie, wymagających łatwo audytowalnej transkrypcji znak w znak.

### Wyniki wiodących modeli (Claude 4.7 / GPT-5)

Dzięki obsłudze rozdzielczości rzędu 2576px modele komercyjne osiągają w zadaniach Document AI dokładność bliską ludzkiej. Wyniki w benchmarkach (stan na 2026 rok):
- **DocVQA:** Claude 4.7 ~95.1%, PaliGemma 2 ~88.4%, Nougat ~77.3%, tradycyjny potok LayoutLMv3 ~83%.
- **ChartQA:** Claude 4.7 ~92.2%, GPT-4V ~78%.
- **VisualMRC:** Claude 4.7 ~94%.

Kluczowa przewaga modeli zamkniętych wynika głównie z gigantycznej skali parametrów oraz zaawansowanej obsługi wysokich rozdzielczości wejściowych.

### Równania matematyczne i format LaTeX

Artykuły naukowe wymagają bezbłędnej transkrypcji wzorów do formatu LaTeX. Do tego celu stworzono model Nougat. Nowsze modele VLM dotrenowane matematycznie (np. Qwen2.5-VL-Math) również dobrze radzą sobie z tym zadaniem. Standardowe modele VLM bez takiego przygotowania mogą generować nieprecyzyjne lub zniekształcone wzory.

W zaawansowanych systemach wydawniczych stosuje się podejście hybrydowe: Nougat do transkrypcji równań, a ogólny model VLM do interpretacji schematów i wykresów.

### Analiza pisma ręcznego

Teksty z odręcznymi dopiskami (np. dokumentacja medyczna) to wciąż trudne zadanie. Wysoce wyspecjalizowane systemy OCR radzą sobie z tym dobrze pod względem kosztowym, ale nowoczesne modele VLM (Claude 4.7, PaliGemma 2) szybko nadrabiają dystans, oferując znacznie lepszą interpretację semantyczną brzydkiego charakteru pisma.

### Rekomendowane podejście w 2026 roku

- **Masowe faktury o stałej strukturze:** LayoutLMv3 + reguły parsera (najniższy koszt jednostkowy).
- **Dokumenty różnorodne (pismo ręczne, schematy, tabele):** Natywne modele VLM (PaliGemma 2 lub Qwen2.5-VL).
- **Przetwarzanie publikacji naukowych:** Nougat do tekstu i matematyki, VLM do interpretacji rycin.
- **Systemy o wysokim rygorze prawnym:** Klasyczny potok OCR do transkrypcji + weryfikacja (cross-check) za pomocą VLM w celu detekcji anomalii semantycznych.

## Zastosowanie w kodzie

Plik `code/main.py` zawiera:
- Szkic parsera dokumentów w stylu LayoutLMv3 (generowanie danych wejściowych tekst + bbox).
- Przykład szablonu JSON dla wyjścia z modelu Donut.
- Porównanie zużycia tokenów oraz kosztu obliczeniowego na stronę dla potoków OCR, Donut, Nougat oraz natywnych modeli VLM.

## Rezultat

Do tej lekcji dołączono dokument `outputs/skill-document-ai-stack-picker.md`. Pomaga on wybrać optymalne rozwiązanie (klasyczny potok OCR, model OCR-free czy natywny model VLM) na podstawie parametrów projektu (domena, skala przetwarzania, wymogi dokładności oraz regulacje prawne).

## Ćwiczenia

1. Projekt zakłada procesowanie 10 milionów faktur na dobę. Jaki stos technologiczny pozwoli zminimalizować koszt operacyjny na stronę przy zachowaniu wymaganej precyzji?
2. Wyjaśnij, dlaczego LayoutLMv3 przewyższa czyste modele CLIP-VLM w zadaniach Document QA, ale ustępuje im w interpretacji tekstu w scenach naturalnych (scene text). Co wnosi geometryczna reprezentacja ramki bbox?
3. Zaproponuj scenariusz testowy, w którym ogólny model VLM wygeneruje wierniejszy kod LaTeX niż wyspecjalizowany Nougat, oraz przypadek, w którym to Nougat okaże się zwycięzcą.
4. Przeczytaj publikację o modelu PaliGemma 2 (Google, 2024). Jaka modyfikacja w miksie danych treningowych przyniosła największy wzrost dokładności w zadaniach Document AI w porównaniu do pierwszej wersji PaliGemma?
5. Zaprojektuj architekturę systemu hybrydowego: klasyczny silnik OCR służy jako baza, a VLM jako niezależny audytor poprawności semantycznej. Jak zaimplementujesz automatyczne rozstrzyganie konfliktów (gdy odczyty się różnią)?

## Kluczowe pojęcia

| Termin | Potoczne określenie | Co to dokładnie oznacza |
| :--- | :--- | :--- |
| **Potok OCR** | „Klasyczny OCR” | Tradycyjny wieloetapowy stos: detekcja tekstu → OCR → parser układu → reguły biznesowe; deterministyczny, lecz podatny na błędy etapowe. |
| **OCR-free** | „Metoda pikselowa (Donut)” | Architektura mapująca obraz strony bezpośrednio na tekst ustrukturyzowany (np. JSON/markdown), pomijająca klasyczny etap OCR. |
| **Layout-aware** | „Model LayoutLM” | Model przyjmujący na wejściu geometryczne współrzędne 2D (bbox) dla każdego tokenu tekstowego w celu ułatwienia analizy przestrzennej. |
| **Natywny VLM** | „Bezpośrednie VLM” | Przekazanie obrazu strony w wysokiej rozdzielczości bezpośrednio do LLM z modułem wizyjnym (np. Claude, GPT, Qwen-VL). |
| **DocVQA** | „Benchmark dokumentowy” | Standardowy zestaw testowy do oceny dokładności udzielania odpowiedzi na pytania na podstawie obrazów dokumentów. |
| **Ustrukturyzowany tekst** | „Format LaTeX/Markdown” | Wynik działania modelu zapisany w postaci sformatowanej (np. tabele w markdown, wzory w LaTeX) ułatwiający automatyczne parsowanie. |

## Literatura uzupełniająca

- [Li i in. — TrOCR (arXiv:2109.10282)](https://arxiv.org/abs/2109.10282)
- [Blecher i in. — Nougat (arXiv:2308.13418)](https://arxiv.org/abs/2308.13418)
- [Huang i in. — LayoutLMv3 (arXiv:2204.08387)](https://arxiv.org/abs/2204.08387)
- [Kim i in. — Donut (arXiv:2111.15664)](https://arxiv.org/abs/2111.15664)
- [Wang i in. — DocLLM (arXiv:2401.00908)](https://arxiv.org/abs/2401.00908)
