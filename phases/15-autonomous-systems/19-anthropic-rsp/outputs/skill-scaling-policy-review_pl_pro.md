---

name: scaling-policy-review
description: Dokonaj przeglądu zasad odpowiedzialnego skalowania w laboratoriach rozwijających modele pionierskie (Anthropic RSP, OpenAI Preparedness, DeepMind FSF, wewnętrzne) w odniesieniu do standardu referencyjnego RSP v3.0.
version: 1.0.0
phase: 15
lesson: 19
tags: [rsp, scaling-policy, ai-rd-4, pause-commitment, saferai, governance]

---

Na podstawie opublikowanej lub proponowanej polityki skalowania przygotuj ustrukturyzowany przegląd, porównując ją ze standardem referencyjnym RSP v3.0 (pod kątem: badań i rozwoju AI, uzasadnienia bezpieczeństwa, dwupoziomowego modelu łagodzenia ryzyka, planów bezpieczeństwa systemów pionierskich, raportów o ryzyku oraz niezależnego audytu).

Przygotuj:

1. **Dwupoziomowy wykaz.** Podziel zobowiązania na „jednostronne zobowiązania laboratorium” oraz „rekomendacje dla całej branży”. Te drugie stanowią jedynie postulaty, a nie twarde obietnice wdrożenia. Oblicz proporcję między nimi; polityka, w której większość zapisów to zalecenia branżowe, jest uznawana za słabą.
2. **Progi bezpieczeństwa.** Wymień zdefiniowane progi zdolności modeli oraz przypisane do nich środki zaradcze. Wskaż progi jakościowe (szczególnie tam, gdzie wersja v2.0 stosowała kryteria ilościowe). Oznacz brakujące progi dla obszarów, które zgodnie z założeniami powinny być objęte ochroną.
3. **Zobowiązanie do wstrzymania prac (pause commitment).** Sprawdź, czy polityka przewiduje procedurę wstrzymania prac (np. przerwanie treningu, zablokowanie wdrożenia) po osiągnięciu określonych progów ryzyka. Wersja v3.0 usunęła ten zapis; polityki wzorowane na niej dziedziczą ten regres.
4. **Cykliczne dokumenty.** Upewnij się, że polityka nakłada obowiązek regularnego publikowania planów bezpieczeństwa systemów pionierskich (Frontier Safety Roadmaps) oraz raportów o ryzyku (Risk Reports) z określoną częstotliwością. Jednorazowe publikacje wydane post hoc są niewystarczające.
5. **Niezależny audyt.** Wskaż zewnętrzny podmiot lub mechanizm weryfikacji. Ocena prowadzona wyłącznie przez wewnętrzne struktury (np. grupę doradczą ds. bezpieczeństwa złożoną z pracowników danego laboratorium) nie spełnia kryteriów niezależnego nadzoru.

Kryteria bezwzględnego odrzucenia (Hard rejects):
- Polityki bezpieczeństwa niezdefiniowane za pomocą progów możliwości modeli.
- Dokumenty, w których wszystkie działania ochronne zaklasyfikowano jedynie jako rekomendacje dla branży.
- Brak zobowiązania do cyklicznego publikowania planów bezpieczeństwa i raportów o ryzyku.
- Brak niezależnego, zewnętrznego mechanizmu audytowego.
- Ogólne deklaracje o „uczeniu się na podstawie doświadczeń” bez precyzyjnego określenia trybu i częstotliwości aktualizacji polityki.

Zasady odmowy zatwierdzenia:
- Jeśli dokument ma charakter wyłącznie wizerunkowy/marketingowy, a nie operacyjno-zarządczy (brak konkretnych progów, terminów i zobowiązań), zablokuj proces i odrzuć go jako politykę skalowania.
- Jeśli użytkownik traktuje sam fakt opublikowania polityki jako gwarancję jej przestrzegania, odrzuć wniosek. Zasady są jedynie deklaracją intencji – ich wdrożenie wymaga twardych dowodów.
- Jeśli użytkownik powołuje się na nieaktualne wersje zasad (np. Anthropic RSP z 2023 roku) jako na obecnie obowiązujące, odrzuć wniosek i zażądaj aktualnego dokumentu.

Format raportu z oceny:

Raport z oceny polityki skalowania musi zawierać:
- **Proporcja dwupoziomowa** (liczba zobowiązań własnych / liczba zaleceń branżowych / suma)
- **Tabela progów** (nazwa progu, typ: ilościowy/jakościowy, warunek wyzwalający, wdrożone środki bezpieczeństwa)
- **Zobowiązanie do wstrzymania prac** (obecne: tak/nie, treść klauzuli)
- **Cykliczne dokumenty** (częstotliwość publikowania planów bezpieczeństwa i raportów o ryzyku)
- **Niezależny audyt** (mechanizm kontroli, podmiot weryfikujący, częstotliwość audytów)
- **Ocena ogólna** (silna / umiarkowana / słaba wraz z uzasadnieniem)
