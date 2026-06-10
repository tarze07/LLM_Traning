---

name: card-audit
description: Sprawdź kartę modelu, arkusz danych lub kartę systemową pod kątem kompletności i możliwości sprawdzenia.
version: 1.0.0
phase: 18
lesson: 26
tags: [model-card, datasheet, system-card, transparency, mitchell-2019]

---

Mając kartę modelu, arkusz danych lub kartę systemową, przeprowadź audyt pod kątem kompletności, dezagregacji numerycznej i sprawdzalności.

Wyprodukuj:

1. Pokrycie sekcji. Sprawdź, czy każda sekcja kanoniczna jest wypełniona. Oznacz brakujące: Względy etyczne to najczęściej pomijane pole karty modelu (Oreamuno i in. 2023).
2. Dezagregacja ilościowa. W przypadku metryk oceny należy zgłosić, czy zapewniona jest dezagregacja według czynników demograficznych lub związanych z zadaniami. Metryki wyłącznie zbiorcze ukrywają szkody alokacyjne i reprezentacyjne.
3. Wyrównanie arkusza danych. Jeśli karta odwołuje się do danych szkoleniowych, czy istnieje towarzyszący arkusz danych (Gebru i in. 2018)? Twierdzenia dotyczące kart modeli są tak mocne, jak bazowy arkusz danych.
4. Sprawdzalne atesty. Czy jakiekolwiek roszczenia są poparte atestami kryptograficznymi (Laminator 2024, Duddu et al.) lub inną weryfikacją strony trzeciej? Niezweryfikowane twierdzenia są oznaczone etykietą „Zgłoszenie własne”.
5. Ślad zrównoważonego rozwoju. Czy raportowane jest zużycie węgla/wody/energii? Nowe wymagania ISO/regulacyjne w 2025 r.

Twarde odrzucenia:
- Dowolna karta modelu bez Względów Etycznych.
- Dowolna karta powołująca się na zbiór danych bez arkusza danych lub równoważnej dokumentacji.
- Dowolna karta twierdząca, że ​​została przetestowana pod kątem stronniczości i nie zawiera raportów ze zdezagregowanymi wskaźnikami.

Zasady odmowy:
- Jeśli użytkownik zapyta, czy karta jest „wystarczająco dobra”, odrzuć opcję binarną; „wystarczająco dobre” zależy od odbiorców i przypadków użycia.
- Jeśli użytkownik poprosi o kartę wygenerowaną automatycznie, odmów, chyba że używany jest system w stylu CardGen (Liu i in. 2024) z weryfikacją manualną.

Wynik: jednostronicowy audyt polegający na wypełnieniu pięciu sekcji, oznaczeniu brakujących treści i wskazaniu najpilniejszego uzupełnienia. Cytuj Mitchella i in. 2019 oraz Gebru i in. 2018, raz.