---

name: scaling-policy-review
description: Przejrzyj zasady skalowania w laboratorium pionierskim (Anthropic RSP, OpenAI Readedness, DeepMind FSF, wewnętrzne) pod kątem kształtu referencyjnego RSP v3.0.
version: 1.0.0
phase: 15
lesson: 19
tags: [rsp, scaling-policy, ai-rd-4, pause-commitment, saferai, governance]

---

Biorąc pod uwagę opublikowaną lub proponowaną politykę skalowania, przygotuj ustrukturyzowany przegląd, porównując ją z kształtem odniesienia RSP v3.0 (badania i rozwój AI, przypadek pozytywny, dwupoziomowe łagodzenie, plan działania dotyczący bezpieczeństwa granicznego, raport ryzyka, niezależny przegląd).

Wyprodukuj:

1. **Dwupoziomowa inwentaryzacja.** Oddzielne zobowiązania na „jednostronne laboratorium” i „rekomendacje dla całej branży”. Zobowiązania na poziomie rekomendacji to zachęta, a nie obietnica. Policz stosunek; polityka, w przypadku której większość zobowiązań znajduje się na poziomie rekomendacji, jest polityką słabą.
2. **Progi.** Wymień każdy próg możliwości i związane z nim środki zaradcze. Oznacz progi, które są jakościowe, gdzie v2 miało charakter ilościowy. Oznacz brakujące progi dla możliwości, które według zasad mają obejmować.
3. **Zobowiązanie do wstrzymania.** Potwierdź, że polityka określa klauzulę pauzy (przerwy w szkoleniach, wstrzymania wdrożeń itp.) przy określonych progach. wersja 3.0 usunęła to; polityki, które podążają ich śladem, dziedziczą regresję.
4. **Stałe artefakty.** Potwierdź, że zgodnie z polityką obowiązują stałe dokumenty dotyczące planu działania dotyczącego bezpieczeństwa granicznego i raportu dotyczącego ryzyka z zadeklarowaną częstotliwością. Artefakty jednorazowe opublikowane post hoc nie kwalifikują się.
5. **Niezależna recenzja.** Podaj nazwę mechanizmu przeglądu zewnętrznego. Przegląd przeprowadzany wyłącznie wewnętrznie („Grupa Doradcza ds. Bezpieczeństwa” składająca się z pracowników laboratorium) nie kwalifikuje się jako niezależny nadzór.

Twarde odrzucenia:
- Zasady bez nazwanego progu możliwości.
- Zasady, których wszystkie środki łagodzące znajdują się na poziomie rekomendacji branżowych.
- Zasady bez stałych artefaktów planu działania / raportu o ryzyku.
- Polityki bez niezależnego mechanizmu przeglądu.
- Polityki, które rzekomo mają „uczyć się na rzeczywistych doświadczeniach”, nie podając, w jaki sposób tekst polityki jest aktualizowany i z jaką częstotliwością.

Zasady odmowy:
- Jeśli dokument polityczny ma charakter marketingowy, a nie zarządczy (brak konkretnych zobowiązań, progów, rytmu), nie należy oceniać go jako polityki skalowania.
- Jeśli użytkownik traktuje istnienie polityki jako równoznaczne z jej przestrzeganiem, odmów. Polityka jest narzędziem zaangażowania; zgodność wymaga dowodów.
- Jeśli użytkownik powołuje się na starszą wersję zasad (np. 2023 Anthropic RSP) jako aktualną, odrzuć i zażądaj aktualnej wersji.

Format wyjściowy:

Zwróć recenzję dotyczącą zasad, podając:
- **Współczynnik dwupoziomowy** (jednostronny / rekomendacja / liczba całkowita)
- **Tabela progów** (nazwa, typ: ilościowy/jakościowy, czynnik wyzwalający, łagodzenie)
- **Wstrzymaj zobowiązanie** (obecne tak/nie, konkretna klauzula)
- **Stałe artefakty** (krotność planu działania, rytm raportowania ryzyka)
- **Niezależna recenzja** (mechanizm, tożsamość recenzenta, częstotliwość)
- **Ocena podsumowująca** (silna / umiarkowana / słaba, uzasadniona)