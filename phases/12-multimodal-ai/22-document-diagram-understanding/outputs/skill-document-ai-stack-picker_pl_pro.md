---

name: document-ai-stack-picker
description: Ułatwia wybór między tradycyjnym potokiem OCR, modelami OCR-free (jak Donut/Nougat) a natywnym VLM do zadań Document AI.
version: 1.0.0
phase: 12
lesson: 22
tags: [document-ai, ocr, donut, nougat, paligemma, vlm-native]

---

Na podstawie specyfikacji projektu Document AI (domena: faktury, publikacje naukowe, formularze, dokumenty mieszane; skala: liczba stron na dobę; wymagana dokładność; wymogi prawne), dobierz optymalny stos technologiczny i zaproponuj konfigurację referencyjną.

Wygeneruj:

1. **Wybór stosu technologicznego:** Era 1 (potok OCR + LayoutLMv3), Era 2 (OCR-free Donut / Nougat), Era 3 (natywny VLM) lub system hybrydowy.
2. **Szacunkowy koszt i wydajność:** Liczba tokenów oraz opóźnienie (latency) na stronę dla wybranego rozwiązania.
3. **Prognoza dokładności:** Spodziewane wyniki w benchmarkach DocVQA, ChartQA oraz testach specyficznych dla danej domeny.
4. **Strategia obsługi pisma ręcznego:** Natywny model VLM (w scenariuszach o elastycznym budżecie) lub dedykowany moduł TrOCR ze schematem routingu (przy dużym wolumenie danych).
5. **Obsługa wzorów i równań:** Model Nougat dla publikacji naukowych (wyjście LaTeX), natywny model VLM w pozostałych przypadkach.
6. **Zgodność z regulacjami prawnymi:** Wdrożenie systemu hybrydowego z automatycznym logowaniem weryfikacji krzyżowej (cross-check).

Kryteria odrzucenia (Twarde reguły):
- Proponowanie natywnego modelu VLM dla skali >1 mln stron na dobę bez szczegółowego kosztorysu. Narzut tokenowy dla obrazu strony w rozdzielczości 2576px jest bardzo wysoki.
- Rekomendowanie systemów opartych na pojedynczym modelu w procesach regulowanych prawnie, bez zapewnienia ścieżek audytowych (audit trails).
- Twierdzenie, że model Nougat sprawdzi się w przetwarzaniu skanów faktur. Nougat to wysoce wyspecjalizowane narzędzie wyłącznie do publikacji naukowych.

Zasady odmowy (Rezygnacja z projektu):
- Jeśli wolumen danych przekracza 10 mln stron na dobę, odrzuć projekty oparte wyłącznie na Erze 3 (natywne VLM) i zalecaj Erę 1 (potok OCR) z wykorzystaniem Ery 3 jedynie do wybiórczej walidacji próbnej.
- Jeśli dokumenty zawierają dużą ilość pisma ręcznego, odrzuć tradycyjne potoki OCR i poleć natywne modele VLM w połączeniu z dedykowanym koderem do pisma ręcznego (np. TrOCR).
- Jeśli kluczowym wymaganiem jest precyzja zapisu wzorów matematycznych w LaTeX, wymagaj wdrożenia modelu Nougat w pętli przetwarzania.

Dane wyjściowe: Jednostronicowy raport z planu wdrożenia zawierający wybór stosu, analizę kosztów, szacowaną dokładność, strategię dla pisma ręcznego, obsługę wzorów matematycznych oraz kwestie regulacyjne. Na końcu dodaj odnośniki do prac: arXiv 2308.13418 (Nougat), 2204.08387 (LayoutLMv3) oraz 2111.15664 (Donut).
