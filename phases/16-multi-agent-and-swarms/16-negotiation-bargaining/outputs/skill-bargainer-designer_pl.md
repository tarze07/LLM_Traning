---

name: bargainer-designer
description: Zaprojektuj protokół negocjacji: który agent prowadzi narrację, który komponent generuje oferty, w jaki sposób prywatne zdrapki oddzielają się od wiadomości publicznych, jakie są granice rundy i w jaki sposób monitorowana jest stawka transakcji.
version: 1.0.0
phase: 16
lesson: 16
tags: [multi-agent, negotiation, bargaining, contract-net, OG-Narrator]

---

Biorąc pod uwagę scenariusz negocjacji lub rynku zadań (negocjacja dwustronna, aukcja N-stronna, alokacja zadań netto na podstawie umowy), zaprojektuj protokół.

Wyprodukuj:

1. **Mechanizm.** Umowa dwustronna, aukcja N-oferentów, transmisja w sieci kontraktowej lub koalicja wielopartyjna. Nazwij grę.
2. **Generator ofert.** Deterministyczny (koncesja w stylu Zeuthena, równowaga Rubinsteina, prosty harmonogram liniowy) lub podpowiadany przez LLM. Wartość domyślna: deterministyczna, chyba że oferta musi mieć strukturę jakościową (propozycja, przypisanie roli).
3. **Warstwa narracji.** Co wnosi LLM: przyjazne dla człowieka ramy, taktyki perswazji, osobowość. Określ wyraźnie, o czym LLM NIE decyduje.
4. **Kanały prywatne a publiczne.** Jak ślady rozumowania są oddzielane od kontekstu drugiej osoby. „Prywatny notatnik” + „wiadomość publiczna” jako dwa pola. Nie podlega to negocjacjom zgodnie z arXiv:2503.06416.
5. **Ograniczona runda.** Maksymalnie 3-5 rund w przypadku gry dwustronnej. Bez ograniczeń nie wchodzi w grę; nagradza konformizm i zachęca do emocjonalnych ofert.
6. **Rezerwacja i dyscyplina BATNA.** Obie strony muszą znać cenę rezerwacji. Jeśli druga strona docieka, narrator LLM nie może tego ujawnić. Zweryfikuj każdą wiadomość wychodzącą pod kątem tej reguły.
7. **Monitorowanie stawki transakcji.** Bazowa stopa transakcji oczekiwana dla tego protokołu (podaj liczbę z punktów odniesienia negocjacyjnych: zakres 27–89% w zależności od roli LLM). Próg alertu dla regresji.
8. **Eskalacja.** Rundy poniżej progu, naruszenia ZOPA lub złamanie zasad po stronie drugiej strony do agenta mediatora lub człowieka.

Twarde odrzucenia:

- Dowolny projekt, w którym LLM oblicza ofertę numeryczną bez deterministycznej wartości rezerwowej. arXiv:2402.15813 pokazuje, że daje to ~27% stawki transakcji.
- Dowolny projekt bez oddzielnych kanałów prywatnych i publicznych. Odpowiednicy przeczytają Twoje rozumowanie.
- Dowolny projekt z nieograniczoną liczbą rund. Gwarantuje wyniki oparte na zgodności.
- Projekty, które pozwalają jednemu agentowi utrzymać zarówno stan kupującego, jak i sprzedającego (negocjacje w odgrywaniu ról). Mechanizmem jest własność informacji prywatnych; łączenie ról usuwa to.

Zasady odmowy:

- Jeśli zadanie nie ma opłacalności liczbowej (negocjacje jakościowe, warunki umowy), rozkład OG-Narrator może nie mieć zastosowania. Zamiast tego polecam ustrukturyzowaną propozycję + weryfikację schematu.
- Jeśli użytkownik nie może zaimplementować oddzielnego notatnika (architektura z jednym wywołaniem LLM), wyraźnie oznacz ryzyko wycieku i zaleć architekturę z dwoma połączeniami.
- Jeśli negocjacje mają charakter kontradyktoryjny ze stroną, która może kłamać, zarekomenduj agenta mediatora oraz zarejestrowane oferty do audytu.

Wynik: jednostronicowy brief. Zacznij od podsumowania składającego się z jednego zdania („Okazja dwustronna: generator ofert Zeuthen + narrator LLM, oprawa na 5 rund, oddzielny notatnik, alert dotyczący stawki poniżej 85%)”, a następnie osiem sekcji powyżej. Zakończ przykładową wiadomością: to, co widzi rozmówca, a co kryje prywatny notatnik.