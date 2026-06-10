---

name: provenance-check
description: Sprawdź zbiór danych szkoleniowych pod kątem obowiązków rezygnacji z California AB 2013 i EU TDM.
version: 1.0.0
phase: 18
lesson: 27
tags: [data-provenance, ab-2013, tdm-opt-out, legitimate-interest, dpa]

---

Biorąc pod uwagę zbiór danych szkoleniowych używany we wdrożeniu, sprawdź zgodność z California AB 2013 i rezygnacją z EU TDM.

Wyprodukuj:

1. Zakres AB 2013. Wypełnij 12 pól. Oznacz wszystkie brakujące pola lub pola zastępcze. Należy pamiętać, że podsumowanie staje się wiążące po opublikowaniu.
2. Zgodność z rezygnacją. Czy zbiór danych uwzględnia odczytywalne maszynowo sygnały rezygnacji (robots.txt, C2PA „No AI Training”, TDM.Reservation)? Filtr wstępnego zbierania musi być na swoim miejscu.
3. Mapowanie jurysdykcji DPA. Dla każdej jurysdykcji, do której należą osoby, których dane dotyczą, określ mający zastosowanie organ ochrony danych i stanowisko w sprawie uzasadnionego interesu na rok 2025 (irlandzki DPC, Wyższy Sąd Krajowy w Kolonii, DPA w Hamburgu, brytyjskie ICO, brazylijskie ANPD).
4. Audyt nieodwracalności. Jeżeli zbiór danych zawiera informacje umożliwiające identyfikację, jaka obowiązuje procedura usuwania uczenia się lub naprawy? Należy pamiętać, że żadna procedura nie przywraca w pełni danych szkoleniowych.
5. Kompletność łańcucha pochodzenia. Czy istnieje podpisany łańcuch od źródła danych do potoku szkoleniowego? Jeśli zbiór danych jest wyprowadzony (przeszukany i przefiltrowany), udokumentuj wyprowadzenie.

Twarde odrzucenia:
- Każde wdrożenie, które powołuje się na AB 2013 bez podsumowań obejmujących 12 pól dla każdego zestawu danych.
- Każde wdrożenie, które nie uwzględnia pliku robots.txt lub równoważnych sygnałów rezygnacji.
- Wszelkie roszczenia naprawcze, które zakładają chirurgiczne usunięcie danych z wytrenowanych ciężarów.

Zasady odmowy:
- Jeśli użytkownik zapyta, czy konkretny zbiór danych jest „bezpieczny do trenowania”, odmów bez analizy jurysdykcji po jurysdykcji.
- Jeśli użytkownik prosi o uniwersalną strategię zgodności, odmów – jurysdykcje znacznie się różnią.

Wynik: jednostronicowe sprawdzenie obejmujące pięć sekcji, identyfikujące luki w zakresie zgodności obarczone największym ryzykiem i wymieniające najpilniejsze środki zaradcze. Przytocz raz każdy wyjątek dotyczący ustawy California AB 2013 i dyrektywy UE dotyczącej praw autorskich TDM.