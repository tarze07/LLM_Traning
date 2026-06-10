---

name: ai-scientist-sandbox-review
description: Lista kontrolna przeglądu dwóch bramek dla wyników agenta pętli badawczej, zanim cokolwiek opuści piaskownicę.
version: 1.0.0
phase: 15
lesson: 5
tags: [ai-scientist, research-agent, sandbox, peer-review, disclosure]

---

Biorąc pod uwagę autonomiczny wynik badania (hipotezę, kod, eksperymenty, liczby, wersję papierową) wygenerowany przez pętlę w stylu AI-Scientist v2, przygotuj recenzję z dwoma bramkami: audyt piaskownicy (czy coś zostało?) plus audyt badań (czy praca jest solidna?).

Obie bramki odnoszą się bezpośrednio do poniższych audytów: **Brama piaskownicy = pozycja 1**; **Brama badawcza = pozycje 2 (audyt eksperymentu) + 3 (audyt polski)**. Pozycje 4–5 określają, co dzieje się po przejściu obu bram.

Wyprodukuj:

1. **Brama piaskownicy.** Zanim jakikolwiek artefakt opuści piaskownicę:
   - Lista wszystkich połączeń sieciowych wykonanych w pętli i ich celów. Oznacz te, które nie zostały wcześniej zatwierdzone.
   - Zinwentaryzuj każdy plik, który pętla zapisała poza swoim katalogiem roboczym.
   - Potwierdź, że zamknięcie Docker / seccomp / gVisor utrzymane jest przez cały czas działania.
   - Potwierdź, że żaden podproces nie wymknął się spod nadzoru piaskownicy.
   Jeśli jakakolwiek kontrola zakończy się niepowodzeniem, zablokuj eksport; podnieść do człowieka.
2. **Audyt eksperymentu.** Przeczytaj kod eksperymentu, a nie artykuł:
   - Sprawdź, czy każdy deklarowany eksperyment rzeczywiście został przeprowadzony, a jego raportowane liczby są odtwarzalne.
   - Sprawdź, czy nieudane eksperymenty zostały zgłoszone jako niepowodzenia, a nie po fakcie ponownie sformułowane jako wyniki negatywne.
   - Sprawdź, czy etykieta „nowości” na pomyśle wytrzymuje przeszukanie literatury przez eksperta w dziedzinie ludzkiej.
3. **Polski audyt.** Przeczytaj liczby:
   - Upewnij się, że dane każdej figury pochodzą z zarejestrowanego eksperymentu, a nie z przepisywania na etapie polskim.
   - Potwierdź, że osie, skale i adnotacje są zgodne z danymi źródłowymi.
   - Oznacz dowolną figurę, której podpis twierdzi więcej, niż pozwalają na to dane.
4. **Plan ujawnień.** Jeśli artefakt jest przeznaczony do dystrybucji zewnętrznej:
   - Ujawnij, że artefakt jest autorstwa agenta.
   - Ujawnij użyte narzędzia (rodzina modeli, wersja pętli).
   - Ujawnij osobę weryfikującą, która to sprawdziła i co sprawdziła.
5. **Decyzja o negatywnym zwolnieniu.** Jeśli artefakt nie przejdzie dowolnego etapu audytu, domyślnie nie zostanie zwolniony. Zastąpienie tego ustawienia domyślnego wymaga nazwanego właściciela-człowieka.

Twarde odrzucenia:
- Każde zgłoszenie, które pomija którąkolwiek bramkę.
- Wszelkie artefakty, w przypadku których brakuje dzienników wykonania pętli lub są one niekompletne.
- Wszelkie liczby, których nie można powiązać z konkretnym przebiegiem eksperymentu.
- Wszelkie twierdzenia dotyczące nowości, których nie zweryfikował ekspert domenowy.

Zasady odmowy:
- Jeśli w przebiegu brakuje Dockera lub równoważnej izolacji, odmów i wymagaj ponownego uruchomienia w izolowanej piaskownicy.
- Jeśli użytkownik nie może sporządzić dzienników wykonania na etapie eksperymentu, odmów – praca nie nadaje się do recenzji.
- Jeśli proponowany kanał dystrybucji jest miejscem recenzowanym, a użytkownik proponuje nieujawnianie autorstwa agenta, odmów i żądaj ujawnienia.

Format wyjściowy:

Zwróć raport z dwiema bramkami:
- **Werdykt dotyczący bramy piaskownicy** (PASS / BLOK, z uzasadnieniem)
- **Werdykt bramki badawczej** (obejmuje audyt eksperymentu (2) i audyt polski (3)) (PASS / BLOCK / REQUIRES_EXPERT, z uwagami dotyczącymi każdej kontroli)
- **Plan ujawnienia** (miejsce, tekst, nazwisko recenzenta)
- **Decyzja o zwolnieniu** (zwolnienie / wstrzymanie / odrzucenie)
- **Następna akcja** (kto, co i kiedy robi)