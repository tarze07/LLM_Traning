# Capstone 04 — Multimodalna kontrola jakości dokumentów (Vision-First PDF, tabele, wykresy)

> W 2026 r. granica kontroli jakości dokumentów odeszła od OCR, a następnie tekstu i skierowała się w stronę późnej interakcji opartej na wizji. ColPali, ColQwen2.5 i ColQwen3-omni traktują każdą stronę PDF jako obraz, osadzają ją z późną interakcją wielowektorową i pozwalają, aby zapytanie bezpośrednio zajmowało się poprawkami. W przypadku finansowych 10-K, artykułów naukowych i odręcznych notatek ten wzorzec z dużą przewagą przewyższa metodę OCR. Zbuduj potok od początku do końca na 10 tysiącach stron i opublikuj obok siebie w oparciu o OCR-potem-tekst.

**Typ:** Zwieńczenie
**Języki:** Python (potok), TypeScript (interfejs przeglądarki)
**Wymagania wstępne:** Faza 4 (wizja komputerowa), Faza 5 (NLP), Faza 7 (transformatory), Faza 11 (inżynieria LLM), Faza 12 (multimodalność), Faza 17 (infrastruktura)
**Wykonywane fazy:** P4 · P5 · P7 · P11 · P12 · P17
**Czas:** 30 godzin

## Problem

Przedsiębiorstwa korzystają z plików PDF, które manipulują procesami OCR: zeskanowanych plików 10-K z obróconymi tabelami, artykułów naukowych wypełnionych równaniami, wykresów, które mają sens tylko jako obrazy, odręcznych adnotacji. Traktowanie ich jako pierwszego tekstu oznacza utratę połowy sygnału. Odpowiedzią na rok 2026 jest pobieranie wielowektorowe późnej interakcji na surowych obrazach stron. Przedstawił go ColPali (Illuin Tech); ColQwen2.5-v0.2 i ColQwen3-omni zwiększyły dokładność. W ViDoRe v3 wyszukiwanie w pierwszej kolejności wizją osiąga lepsze wyniki niż OCR, a następnie tekst ze znaczącymi marginesami – a luka zwiększa się w przypadku wykresów, tabel i pisma odręcznego.

Kompromisem jest pamięć i opóźnienie. Osadzanie ColQwen to ~2048 wektorów wstawek na stronę, a nie pojedynczy wektor o 1024 przyciemnieniach. Balony do przechowywania surowego. DocPruner (2026) zapewnia 50% przycinanie bez mierzalnej utraty dokładności. Zindeksujesz 10 tys. stron, zmierzysz ViDoRe v3 nDCG@5, podasz odpowiedzi w czasie krótszym niż 2 s i porównasz bezpośrednio z bazową metodą OCR, a następnie tekstem.

## Koncepcja

Późna interakcja oznacza, że każdy token zapytania uzyskuje wyniki względem każdego tokenu łatki i sumowany jest maksymalny wynik na token zapytania. Otrzymujesz szczegółowe dopasowanie bez potrzeby stosowania pojedynczego wektora zbiorczego. Indeks wielowektorowy (Vespa, wielowektorowy Qdrant lub AstraDB) przechowuje osadzania poszczególnych poprawek i uruchamia MaxSim w momencie pobierania.

Odpowiedź to model języka wizyjnego, który przyjmuje zapytanie oraz k najczęściej pobieranych stron jako obrazy i zapisuje odpowiedź z obszarami dowodów (obramowaniami lub odniesieniami do stron). Qwen3-VL-30B, Gemini 2.5 Pro i InternVL3 to czołowe modele na rok 2026. W przypadku równań i notacji naukowej rezerwowy OCR (Nougat, kropki.ocr) jest dołączany jako opcjonalny kanał tekstowy.

Ocena jest macierzą dwuwymiarową. Jedna oś: typ treści (akapity zwykłego tekstu, gęste tabele, wykresy słupkowe/liniowe, notatki odręczne, równania). Inna oś: podejście do odzyskiwania (najpierw późna interakcja z wizją vs OCR, potem z tekstem vs hybryda). Każda komórka otrzymuje nDCG@5 i dokładność odpowiedzi. Raport jest efektem końcowym.

## Architektura

```
PDFs -> page renderer (PyMuPDF, 180 DPI)
           |
           v
  ColQwen2.5-v0.2 embed (multi-vector per page, ~2048 patches)
           |
           +------> DocPruner 50% compression
           |
           v
   multi-vector index (Vespa or Qdrant multi-vector)
           |
query ----+----> retrieve top-k pages (MaxSim)
           |
           v
  VLM answerer: Qwen3-VL-30B | Gemini 2.5 Pro | InternVL3
    inputs: query + top-k page images + optional OCR text
           |
           v
  answer with cited page numbers + evidence regions
           |
           v
  Streamlit / Next.js viewer: highlighted boxes on source page
```

## Stos

- Renderowanie strony: PyMuPDF (fitz) przy 180 DPI, normalizacja pionowa
- Model późnej interakcji: ColQwen2.5-v0.2 lub ColQwen3-omni (zespół vidore w Hugging Face)
- Indeks: Vespa z polem wielowektorowym lub wielowektorowym Qdrant lub AstraDB z MaxSim
- Przycinanie: polityka DocPruner 2026 (zachowaj poprawki o dużej rozbieżności, kompresja 50% przy utracie dokładności < 0,5%)
- OCR zastępczy (równania / gęste tabele): dots.ocr lub Nougat
- Odpowiedź VLM: host Qwen3-VL-30B lub host Gemini 2.5 Pro; InternVL3 jako rozwiązanie awaryjne
- Ocena: test porównawczy ViDoRe v3, M3DocVQA do wnioskowania wielostronicowego
- Interfejs przeglądarki: Next.js 15 z nakładką płótna dla obszarów dowodów

## Zbuduj to

1. **Przeczytaj.** Przeglądaj zbiór 10 tys. stron PDF w 10-K, artykułach naukowych i zeskanowanych dokumentach. Renderuj każdą stronę do pliku PNG o wymiarach 1536x2048. Utrzymaj `{doc_id, page_num, image_path}`.

2. **Osadź.** Uruchom ColQwen2.5-v0.2 na każdym obrazie strony. Kształt wyjściowy ~2048 osadzania poprawek o przyciemnieniu 128. Zastosuj DocPruner, aby zachować połowę najwyższego sygnału. Zapis do pola wielowektorowego Vespa lub wielowektorowego Qdrant.

3. **Zapytanie.** Dla każdego przychodzącego zapytania osadzaj w wieży zapytań (osadzanie na poziomie tokena). Uruchom MaxSim względem indeksu: dla każdego tokenu zapytania weź maksymalny iloczyn skalarny w stosunku do osadzania poprawek na stronie, suma. Zwróć górne k stron.

4. **Synteza.** Wywołaj Qwen3-VL-30B z zapytaniem i obrazami 5 najlepszych stron. Podpowiedź: „Odpowiedz, korzystając wyłącznie z podanych stron. Zacytuj każde twierdzenie według (doc_id, page) i nazwij region (rysunek, tabela, akapit).”

5. **Regiony dowodów.** Przetwórz odpowiedź w celu wyodrębnienia cytowanych regionów. Jeśli VLM emituje ramki ograniczające (tak robi Qwen3-VL), renderuj je jako nakładki w przeglądarce.

6. **Zastępczy OCR.** W przypadku stron o dużej gęstości równań (heurystyka wariancji obrazu) uruchom plik Nougat lub dots.ocr i przekaż tekst OCR jako dodatkowy kanał obok obrazu.

7. **Eval.** Uruchom ViDoRe v3 (pobieranie nDCG@5) i M3DocVQA (dokładność wielostronicowej kontroli jakości). Uruchom także potok OCR-then-text w tym samym korpusie z tym samym syntezatorem. Utwórz macierz podejścia × typ treści.

8. **UI.** Najpierw uproszczony prototyp; Przeglądarka produkcyjna Next.js 15 z nakładką regionu dowodowego strona po stronie.

## Użyj tego

```
$ doc-qa ask "what was the 2024 operating margin change for segment EMEA?"
[retrieve]   top-5 pages in 320ms (ColQwen2.5, MaxSim, Vespa)
[synth]      qwen3-vl-30b, 1.4s, cited (form-10k-2024, p. 88) + (..., p. 92)
answer:
  EMEA operating margin moved from 18.2% to 16.8%, a 140bp decline.
  cited: 10-K-2024.pdf p.88 (Table 4, Segment Operating Margin)
         10-K-2024.pdf p.92 (MD&A, Operating Performance)
[viewer]     open with highlighted bounding boxes overlaid on p.88 Table 4
```

## Wyślij to

`outputs/skill-doc-qa.md` opisuje produkt końcowy: oparty na wizji multimodalny system kontroli jakości dokumentów dostrojony do konkretnego korpusu i oceniony na podstawie linii bazowej OCR-pot-text w ViDoRe v3.

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | Dokładność ViDoRe v3 / M3DocVQA | Liczby porównawcze a wartość bazowa tekstu OCR i opublikowana tabela wyników |
| 20 | Uziemienie regionu dowodów | Część cytowanych regionów, które faktycznie zawierają zakres odpowiedzi |
| 20 | Inżynieria przechowywania i opóźnień | Współczynnik kompresji DocPruner, indeks p95, odpowiedź p95 |
| 20 | Rozumowanie wielostronicowe | Dokładność w ręcznie oznaczonym, wielostronicowym zestawie zawierającym 100 pytań |
| 15 | Kontrola źródła UX | Przejrzystość przeglądarki, wierność nakładek, narzędzia do porównywania obok siebie |
| **100** | | |

## Ćwiczenia

1. Zmierz ColQwen2.5-v0.2 vs ColQwen3-omni w tym samym korpusie. Które strony jeden robi dobrze, a drugi pomija? Dodaj tag „klasa treści” do indeksu, aby kierować według typu.

2. Przycinaj agresywnie sadzonki (75%, 90%). Znajdź klif kompresji: punkt, w którym ViDoRe nDCG@5 spada poniżej linii bazowej OCR.

3. Zbuduj hybrydę: uruchom równolegle OCR-then-text i ColQwen, połącz z RRF, zmień rangę za pomocą cross-enkodera. Czy hybryda pokona którykolwiek z nich w pojedynkę? Gdzie najbardziej pomaga?

4. Zamień Qwen3-VL-30B na mniejszy VLM (Qwen2.5-VL-7B). Zmierz krzywą dokładności w przeliczeniu na dolara.

5. Dodaj obsługę odręcznych notatek. Renderuj korpus pisma ręcznego, osadzaj w ColQwen, pobieraj pomiary. Porównanie z potokiem OCR pisma ręcznego.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Późna interakcja | „Odzyskiwanie w stylu ColPali” | Tokeny zapytań niezależnie oceniają poprawki stron; Agregaty MaxSim |
| Wielowektorowy | „Osadzanie poszczególnych poprawek” | Każdy dokument ma wiele wektorów, a nie jeden wektor zbiorczy |
| MaxSim | „Ocena późnej interakcji” | Dla każdego tokena zapytania przyjmij maksymalne podobieństwo wektorów dokumentów; suma |
| DocPruner | „Kompresja łatki” | Przycinanie 2026, które utrzymuje 50% poprawek przy znikomej utracie dokładności |
| ViDoRe v3 | „Porównanie wyszukiwania dokumentów” | Standard pomiaru wyszukiwania dokumentów wizualnych z 2026 r. |
| Region dowodów | „Cytowana ramka ograniczająca” | Bbox na stronie źródłowej, który lokalizuje zakres odpowiedzi |
| Rozwiązanie awaryjne OCR | „Kanał równania” | Potok tekstowy używany wraz z wizją stron zawierających wiele równań lub tabel |

## Dalsze czytanie

- [Repozytorium ColPali (Illuin Tech)](https://github.com/illuin-tech/colpali) — odniesienie do pobierania dokumentów po późnej interakcji
- [Artykuł ColPali (arXiv:2407.01449)](https://arxiv.org/abs/2407.01449) — dokument dotyczący podstawowych metod
– [Rodzina ColQwen na Hugging Face](https://huggingface.co/vidore) — punkty kontrolne gotowe do produkcji
- [M3DocRAG (Adobe)](https://arxiv.org/abs/2411.04952) — wielostronicowy, wielomodalny poziom bazowy RAG
- [Poradnik dotyczący wielu wektorów Vespa](https://docs.vespa.ai/en/colpali.html) — stos referencyjny do serwowania
- [Obsługa wielu wektorów Qdrant](https://qdrant.tech/documentation/concepts/vectors/#multivectors) — alternatywny indeks
- [Wielowektorowy AstraDB](https://docs.datastax.com/en/astra-db-serverless/databases/vector-search.html) — alternatywny indeks zarządzany
- [Nougat OCR](https://github.com/facebookresearch/nougat) — rezerwowy OCR obsługujący równania