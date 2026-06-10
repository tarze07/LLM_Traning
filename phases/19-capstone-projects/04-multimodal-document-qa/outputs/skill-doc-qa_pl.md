---

name: doc-qa
description: Zbuduj nowatorski system kontroli jakości dokumentów multimodalnych na 10 tys. stron z wyszukiwaniem na późnym etapie interakcji i cytowaniem obszarów dowodów.
version: 1.0.0
phase: 19
lesson: 04
tags: [capstone, multimodal, rag, colpali, colqwen, late-interaction, pdf]

---

Mając zbiór plików PDF (10-K, artykuły naukowe, zeskanowane dokumenty), utwórz potok, który indeksuje strony jako obrazy przy użyciu późnej interakcji w stylu ColPali i odpowiada na pytania za pomocą regionów dowodów na poziomie strony.

Plan budowy:

1. Renderuj każdą stronę PDF do formatu PNG o wymiarach 1536x2048 za pomocą PyMuPDF w rozdzielczości 180 DPI.
2. Osadź każdą stronę za pomocą ColQwen2.5-v0.2 lub ColQwen3-omni. Przechowuj osadzane poprawki wielowektorowe w Vespa, wielowektorowym Qdrant lub AstraDB.
3. Zastosuj przycinanie 50% łat w stylu DocPrunera. Sprawdź, czy spadek dokładności utrzymuje się poniżej 0,5% w przypadku ViDoRe v3.
4. W momencie zapytania: osadź tokeny zapytania; oblicz MaxSim na podstawie poprawek każdej strony; miejsce na górze-k.
5. Dokonaj syntezy za pomocą Qwen3-VL-30B lub Gemini 2.5 Pro, przekazując zapytanie i obrazy z 5 pierwszych stron. Wymagane kotwy `(doc_id, page, region)`.
6. W przypadku stron zawierających wiele równań lub tabel uruchom plik Nougat lub dots.ocr jako opcjonalny kanał tekstowy i podaj go obok obrazu.
7. Zbuduj przeglądarkę Next.js 15, która nakłada obszary dowodów jako ramki ograniczające na stronie źródłowej.
8. Oceń ViDoRe v3 i M3DocVQA. Utwórz macierz podejścia opartego na klasie treści ×, porównującą najpierw wizję z OCR, a następnie tekst na zwykłym tekście, tabelach, wykresach, piśmie odręcznym i równaniach.

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | Dokładność ViDoRe v3 / M3DocVQA | Test porównawczy a linia bazowa OCR, a następnie tekst na dopasowanych stronach |
| 20 | Uziemienie regionu dowodów | Część cytowanych regionów zawierających zakres odpowiedzi |
| 20 | Inżynieria przechowywania i opóźnień | Kompresja DocPruner, indeks p95, odpowiedź p95 poniżej 2s |
| 20 | Rozumowanie wielostronicowe | Dokładność w ręcznie oznaczonym, wielostronicowym zestawie zawierającym 100 pytań |
| 15 | Kontrola źródła UX | Wierność nakładki, narzędzia porównawcze, eksplorator strona po stronie |

Twarde odrzucenia:

- Potoki wykorzystujące najpierw OCR, przedstawiane jako „najpierw oparte na wizji” poprzez modernizację tekstu OCR do osadzania w jednym wektorze.
- Każdy system, który pomija ramki ograniczające na poziomie poprawki i dlatego nie może renderować nakładek dowodowych.
- Numery magazynów zgłaszane bez dokumentowania ustawień DocPrunera.

Zasady odmowy:

- Odmawiaj indeksowania zeskanowanych umów prawnych bez dedykowanej polityki redakcyjnej. Osadzanie ColQwen powoduje wyciek treści.
- Odmówić obsługi zapytań dotyczących korpusu, którego użytkownik nie ujawnił. Ścieżka audytu jest obowiązkowa w przypadku domen regulowanych.
- Odmawiaj porównywania z OCR-then-text bez uruchamiania obu potoków w tym samym korpusie.

Wynik: repozytorium zawierające potok pozyskiwania, konfigurację Vespa (lub wielowektorową Qdrant), wielostronicowy zestaw ewaluacyjny składający się ze 100 pytań, interfejs przeglądarki oraz opis z macierzą podejścia klasy treści x i konkretną rekomendacją, w przypadku których klasy treści nadal preferują OCR, a następnie tekst w 2026 r.