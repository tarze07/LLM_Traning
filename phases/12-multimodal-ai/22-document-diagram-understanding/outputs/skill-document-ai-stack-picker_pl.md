---

name: document-ai-stack-picker
description: Wybierz pomiędzy potokiem OCR, specjalistą bez OCR lub natywnym rozwiązaniem VLM dla projektu sztucznej inteligencji dokumentów opartego na domenie, skali i potrzebach regulacyjnych.
version: 1.0.0
phase: 12
lesson: 22
tags: [document-ai, ocr, donut, nougat, paligemma, vlm-native]

---

Biorąc pod uwagę projekt dokumentu-AI (domena: faktury/artykuły naukowe/formularze/mieszane; skala: strony dziennie; pasek jakości; potrzeby regulacyjne), wybierz stos i utwórz konfigurację referencyjną.

Wyprodukuj:

1. Wybór stosu. Era 1 (potok OCR + LayoutLMv3), Era 2 (bez OCR Donut / Nougat), Era 3 (natywny VLM) lub hybryda.
2. Szacunkowy koszt strony. Liczba tokenów i opóźnienie na wybranym stosie.
3. Oczekiwanie dokładności. DocVQA + ChartQA + testy porównawcze specyficzne dla domeny.
4. Strategia pisma ręcznego. Natywny dla VLM dla niewrażliwych na koszty; dedykowany TroCR + routing dla skali.
5. Dane wyjściowe matematyki/LaTeX-a. Nugat do prac naukowych; VLM dla innych.
6. Rozwiązanie regulacyjne. Hybrydowy z dziennikiem kontroli krzyżowej.

Twarde odrzucenia:
- Proponowanie natywnego rozwiązania VLM dla > 1 miliona stron dziennie bez analizy kosztów. Koszt tokena wynoszący 2576 pikseli na stronę jest znaczny.
- Rekomendowanie jednomodelowych rozwiązań dla regulowanych przepływów pracy bez ścieżek audytu.
- Twierdzenie Nougat obsługuje zeskanowane faktury. Tak nie jest — jest specjalistą od artykułów naukowych.

Zasady odmowy:
- Jeśli skala wynosi > 10 milionów stron dziennie, odrzuć Erę 3 i zaleć Erę 1 z Erą 3 jako walidatorem próbkowania.
- Jeśli w domenie jest dużo napisane odręcznie, odrzuć potok OCR i poleć VLM-native + specjalistę od pisma ręcznego (TrOCR).
- Jeśli w równaniach wymagana jest wierność LaTeX, w pętli wymagaj Nougata.

Wynik: jednostronicowy plan ze stosem, kosztem, dokładnością, charakterem pisma ręcznego, matematyką, przepisami. Zakończ arXiv 2308.13418 (Nougat), 2204.08387 (LayoutLMv3), 2111.15664 (Pączek).