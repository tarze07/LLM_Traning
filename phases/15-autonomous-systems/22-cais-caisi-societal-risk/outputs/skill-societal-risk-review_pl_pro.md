---

name: societal-risk-review
description: Dokonaj przeglądu wdrożenia pod kątem ryzyka społecznego, wykorzystując model czterech głównych zagrożeń CAIS oraz kontekst regulacyjny CAISI i kalifornijskiej ustawy SB-53.
version: 1.0.0
phase: 15
lesson: 22
tags: [cais, caisi, four-risk-framework, organizational-risk, sb-53, societal-risk]

---

Na podstawie planowanego lub działającego wdrożenia systemu AI przygotuj analizę ryzyka społecznego. Powinna ona identyfikować zagrożenia w ramach czterech kategorii CAIS, oceniać poszczególne czynniki ryzyka organizacyjnego oraz definiować obszary podlegające regulacjom prawnym.

Przygotuj:

1. **Klasyfikacja czterech zagrożeń.** Dla każdej z kategorii (złośliwe użycie, wyścig zbrojeń AI, ryzyko organizacyjne, zbuntowane systemy) określ stopień i charakter ekspozycji wdrożenia. System może podlegać pod wiele kategorii; ewentualne oznaczenie „nie dotyczy” wymaga przedstawienia uzasadnienia w jednym zdaniu.
2. **Ocena ryzyka organizacyjnego.** Przeanalizuj wdrożenie pod kątem czterech kluczowych czynników: kultury bezpieczeństwa, rygorystyczności audytów, wielowarstwowości obrony oraz bezpieczeństwa informacji. Każdy z tych obszarów oceniony jako niewystarczający należy oznaczyć jako lukę bezpieczeństwa.
3. **Zgodność z regulacjami prawnymi (compliance).** Wskaż mające zastosowanie akty prawne i wytyczne (np. unijny akt o sztucznej inteligencji, ustawa California SB-53, dobrowolne porozumienia z CAISI). Zgodność z prawem stanowi bezwzględny warunek dopuszczenia systemu do eksploatacji, a nie opcjonalną cechę.
4. **Ewaluacja zewnętrzna.** Wymień audyty zewnętrzne, którym poddano system lub jego model bazowy (np. METR, CAISI, Apollo, Gray Swan). Brak zewnętrznych ewaluacji w przypadku systemów autonomicznych o długim horyzoncie działania jest traktowany jako krytyczna luka.
5. **Wpływ presji rynkowej.** Oszacuj poziom presji konkurencyjnej wywieranej na organizację w celu szybkiego wdrożenia systemu i określ, jak wpływa to na czynniki ryzyka organizacyjnego. Zgodnie z analizami CAIS zespoły działające pod presją czasu w pierwszej kolejności rezygnują z rygorystycznych audytów.

Kryteria bezwzględnego odrzucenia (Hard rejects):
- Projekty dotykające obszarów o wysokim stopniu zagrożenia bez wdrożonej warstwy zakodowanych na stałe zakazów (Lekcja 17).
- Udostępnianie systemów pod presją rynkową bez przeprowadzenia niezależnego audytu zewnętrznego.
- Wdrożenia autonomiczne o długim horyzoncie działania bez przeprowadzenia zewnętrznej ewaluacji możliwości.
- Wdrożenia na rynku europejskim bez spełnienia wymogów Artykułu 14 (nadzór ludzki HITL, Lekcja 15).
- Wdrożenia w Kalifornii bez zaimplementowanych procedur raportowania poważnych incydentów (w przypadku wejścia w życie ustawy SB-53).

Zasady odmowy zatwierdzenia:
- Jeśli nie wskazano zewnętrznego podmiotu oceniającego dla modelu bazowego, zablokuj proces (wewnętrzna samoocena jest niewystarczająca).
- Jeśli użytkownik zakłada, że posiadanie polityki skalowania zwalnia go z wymogów regulacji ryzyk katastrofalnych, odrzuć projekt i zażądaj mapowania zgodności prawnej.
- Jeśli wdrożenie pod presją konkurencji ma być realizowane bez audytu, odrzuć wniosek, powołując się na analizy CAIS dotyczące ryzyka organizacyjnego.

Format raportu z analizy ryzyka społecznego:

Raport musi zawierać:
- **Tabela czterech ryzyk CAIS** (kategoria zagrożenia, podatność: tak/nie, opis charakteru ekspozycji)
- **Ocena ryzyka organizacyjnego** (kultura bezpieczeństwa / audyty / struktura obronna / bezpieczeństwo informacji)
- **Powierzchnia regulacyjna** (wykaz mających zastosowanie przepisów wraz ze statusem zgodności)
- **Status ewaluacji zewnętrznej** (podmiot wykonujący testy, zakres ewaluacji, częstotliwość)
- **Ekspozycja na presję strukturalną** (niska/średnia/wysoka wraz z uzasadnieniem)
- **Status gotowości wdrożeniowej** (produkcja / środowisko przejściowe / badania)
