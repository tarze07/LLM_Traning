---

name: rsi-cycle-pause-spec
description: Określ warunki, w których potok RSI musi zostać wstrzymany i poczekać na weryfikację przez człowieka przed następnym cyklem.
version: 1.0.0
phase: 15
lesson: 7
tags: [rsi, self-improvement, alignment, pause-threshold, rsp]

---

Biorąc pod uwagę proponowany potok rekurencyjnego samodoskonalenia, utwórz specyfikację pauzy: wyraźne warunki, które zatrzymują pętlę w celu sprawdzenia przez człowieka przed rozpoczęciem następnego cyklu. Potok bez specyfikacji pauzy nie jest gotowy do uruchomienia.

Wyprodukuj:

1. **Progi na poziomie cyklu.** Dla każdej mierzalnej osi (wynik zdolności, wynik dostosowania, budżet, długość trajektorii, wykorzystanie zasobów) zdefiniuj próg liczbowy, którego przekroczenie wstrzymuje pętlę. Progi należy ustawić przed rozpoczęciem i zarejestrowaniem pętli.
2. **Delty między cyklami.** Ustaw limity ruchu dowolnej osi w pojedynczym cyklu. Skok możliwości o ponad 30% w jednym cyklu jest prawie zawsze oznaką gry oceniającego; pauza i kontrola.
3. **Szczelina niewspółosiowości.** Oblicz zdolność minus wyrównanie po każdym cyklu. Jeśli odstęp powiększy się o więcej niż X (ustawiony przez operatora), wstrzymaj. Jest to metryka symulatora w ćwiczeniach `code/main.py`.
4. **Obserwacja regresji.** Jeśli w cyklu jakakolwiek oś spadnie bardziej niż Y, zatrzymaj się. Regresja zdolności często następuje po gwałtownych wzrostach; złapanie ich zapobiega fałszywemu przyspieszeniu postępu.
5. **Umowa dotycząca wznowienia z człowiekiem.** Zanim pętla zostanie wznowiona po przerwie, poproś osobę wyznaczoną o sprawdzenie wyzwalacza pauzy, w razie potrzeby ponowne ustawienie progów i zapisanie decyzji w ścieżce audytu poza rurociągiem.

Twarde odrzucenia:
- Każdy rurociąg, który może zostać wznowiony po przerwie bez interwencji człowieka.
- Dowolny próg zależny od wewnętrznego oceniającego pętli (agent może go ograć).
- Dowolny potok, którego zestaw progów może być edytowany przez agenta.

Zasady odmowy:
- Jeśli użytkownik nie może od razu nazwać progów, odmów. Progi ustalane post hoc nie są progami; są to racjonalizacje.
- Jeżeli rurociąg nie posiada zewnętrznego analizatora (poza pętlą), należy odmówić — wykrywanie regresji i przepięć wymaga widoku z zewnątrz.
- Jeżeli proponowana umowa o wznowieniu brzmi: „powiadom zespół i kontynuuj po 24 godzinach”, odmów. Wznowienie musi być aktem pozytywnym.

Format wyjściowy:

Zwróć jednostronicową specyfikację za pomocą:
- **Osie i progi** (tabela)
- **Limity delta cyklu** (tabela)
- **Wzór i próg luki niewspółosiowości**
- **Granice regresji**
- **Zewnętrzny ewaluator** (co to jest, kiedy działa)
- **Umowa wznowieniowa** (nazwany właściciel, lista kontrolna, miejsce docelowe dziennika)
- **Linia podpisu** (kto jest właścicielem niezmiennika pauzy)