---

name: elicitation-form-designer
description: Zaprojektuj schemat formularza pozyskiwania klientów i szablon wiadomości dla narzędzia, które wymaga potwierdzenia lub ujednoznacznienia użytkownika w trakcie rozmowy.
version: 1.0.0
phase: 13
lesson: 12
tags: [mcp, elicitation, user-input, forms]

---

Biorąc pod uwagę narzędzie, którego zachowanie może wymagać wprowadzenia danych przez użytkownika w trakcie rozmowy, zaprojektuj schemat wywoływania i komunikat.

Wyprodukuj:

1. Warunek wyzwalania. Podaj dokładne dane wejściowe lub niejednoznaczność, które powinny spowodować, że narzędzie wywoła `elicitation/create`.
2. Szablon wiadomości. Jedno zdanie, które host pokazuje użytkownikowi. Prosto, konkretnie, bez żargonu.
3. Schemat. Płaski schemat JSON z wpisanymi właściwościami i listą `enum` (dla ujednoznacznienia) lub `boolean` (dla potwierdzenia). Nie gniazduj.
4. Obsługa oddziałów. Mapuj `accept` / `decline` / `cancel` na zachowania narzędzi.
5. Reguła limitu stawki. Limit wywołań na wywołanie narzędzia; nigdy nie wywoływaj wewnątrz pętli.

Twarde odrzucenia:
- Dowolny schemat zagnieżdżający obiekty. Wywoływanie v1 jest płaskie.
- Wszelkie zachęty użyte do uzupełnienia brakującego argumentu, o który LLM mógł poprosić w prozie.
- Wszelkie wywołania o wysokiej częstotliwości (więcej niż raz na wywołanie narzędzia).

Zasady odmowy:
- Jeśli narzędzie jest tylko do odczytu i wiąże się z niskim ryzykiem, odmów jego wywołania i po prostu zwróć wynik.
- Jeśli narzędzie jest destrukcyjne, a host obsługuje adnotacje `destructiveHint`, zasugeruj użycie adnotacji i pozwolenie klientowi na natywną obsługę potwierdzeń.
— Jeśli potrzebne jest logowanie OAuth, zalecij wywoływanie w trybie adresu URL i oznacz ryzyko dryfowania SEP-1036.

Dane wyjściowe: jednostronicowy projekt z warunkiem wyzwalającym, szablonem wiadomości, schematem, obsługą gałęzi, regułą limitu szybkości i informacją, czy lepiej pasuje tryb formularza czy tryb adresu URL.