---

name: horizon-interpretation
description: Przejrzyj twierdzenia dostawcy dotyczące horyzontu czasowego i sporządź analizę rozbieżności między twierdzeniami dotyczącymi testów porównawczych a rzeczywistością wdrożeniową.
version: 1.0.0
phase: 15
lesson: 21
tags: [metr, time-horizon, hcast, re-bench, eval-vs-deploy, external-evaluation]

---

Biorąc pod uwagę opublikowane przez dostawcę twierdzenie dotyczące horyzontu czasowego (np. „nasz model wykonuje 14-godzinne zadania przy 50% niezawodności”), przygotuj analizę luk, która ilościowo określi różnicę między rzeczywistością wdrożenia i zaznaczy wszelkie słabości metodologiczne.

Wyprodukuj:

1. **Audyt metodologii.** Identyfikacja zestawu zadań (HCAST, RE-Bench, SWAA lub zastrzeżony). Potwierdź, że ujawniono dopasowanie logistyczne (nachylenie, wielkość próbki, przedział ufności). Horyzont bez ujawnienia metodologii jest twierdzeniem marketingowym.
2. **Dopasowanie rozkładu zadań.** Odwzoruj wzorcowy rozkład zadań dostawcy na rozkład zadań produkcyjnych użytkownika. Jeśli różnią się one istotnie (dostawca mierzy zadania SWE, produkcja to przepływy obsługi klienta), liczba nie jest przenoszona.
3. **Luka w kontekście oceny.** Zastosuj lukę 10–40% między horyzontem odniesienia a rzeczywistością wdrożenia. Przytocz badanie Anthropic 2024 dotyczące fałszowania wyrównań i Międzynarodowy raport bezpieczeństwa sztucznej inteligencji z 2026 r. dotyczący gier z kontekstem ewaluacyjnym. Rzeczywista przerwa zależy od protokołu eval; gra jest wyższa w przypadku zadań nieustrukturyzowanych.
4. **Brak narzędzi.** Narzędzia wzorcowe są czyste i dobrze oprzyrządowane. Oprzyrządowanie produkcyjne jest bardziej bałaganiarskie. Oszacuj dodatkowy rabat za niezawodność wynoszący 5–30%.
5. **Założenie o zaangażowaniu człowieka w pętlę.** W testach porównawczych nie zakłada się HITL. Agenci produkcyjni z HITL działają z większą niezawodnością, ale mniejszą autonomią. Dostosuj odpowiednio interpretację horyzontu.

Twarde odrzucenia:
- Twierdzenia programu Horizon bez metodologii źródłowej i wielkości próby.
- Twierdzenie, że horyzont odniesienia pozwala przewidzieć niezawodność wdrożenia.
- Sprzedawcy podają jako aktualną liczbę prognozowaną na rok 2025 lub wcześniejszą (czas podwojenia wynosi ~7 miesięcy; liczby na rok 2025 są nieaktualne w ciągu roku).
- Traktowanie horyzontu 50% jako „będzie działać w większości przypadków” – 50% niezawodności to rzut monetą.

Zasady odmowy:
- Jeśli sprzedawca nie ujawni metodologii, odmów i żądaj artykułu źródłowego lub wpisu na blogu.
- Jeśli rozkład wzorcowy nie pokrywa się z rozkładem produkcji, odmów i żądaj oceny wewnętrznej.
- Jeśli sprzedawca podaje horyzonty bez audytu gier w ramach swojego konkretnego rurociągu ewaluacyjnego, odmów podawania liczby jako prognozy niezawodności.

Format wyjściowy:

Zwróć notatkę dotyczącą interpretacji horyzontu zawierającą:
- **Metodologia źródłowa** (zestaw, metoda dopasowania, wielkość próby, CI)
- **Pokrywanie się dystrybucji** (punkt odniesienia vs produkcja; mapowanie %)
- **Oszacowanie luki w kontekście oceny** (niskie/średnie/wysokie z uzasadnieniem)
- **Oszacowanie luki narzędziowej** (niska/średnia/wysoka)
- **Założenie HITL** (autonomiczny styl wzorcowy vs HITL produkcyjny)
- **Horyzont dostosowany do wdrożenia** (horyzont po uwzględnieniu rabatów na przerwy i narzędzia)
- **Ocena gotowości** (tylko produkcja / etapowanie / badania)