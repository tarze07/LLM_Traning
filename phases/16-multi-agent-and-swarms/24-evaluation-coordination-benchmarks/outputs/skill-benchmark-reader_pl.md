---

name: benchmark-reader
description: Przeczytaj sceptycznie oświadczenie dotyczące testu porównawczego dotyczącego wielu agentów. Ocenia wniosek dotyczący wyboru punktu odniesienia, zanieczyszczenia, wartości bazowych, istotności statystycznej, różnorodności zadań i ujawnienia kosztów.
version: 1.0.0
phase: 16
lesson: 24
tags: [multi-agent, benchmarks, evaluation, SWE-bench, MARBLE]

---

Biorąc pod uwagę opublikowane lub wewnętrzne twierdzenie dotyczące wydajności testów porównawczych wielu agentów, oceń to twierdzenie i wykaż zastrzeżenia.

Wyprodukuj:

1. **Benchmark + identyfikacja podziału.** Który test porównawczy (MARBLE, COMMA, MedAgentBoard, AgentArch, SWE-bench Pro, SWE-bench Verified, niestandardowy)? Który podział (pełny, wstrzymany, oczyszczony z zanieczyszczeń)? Nieznane podziały są dyskwalifikujące.
2. **Stan skażenia.** Czy punkt odniesienia po treningu dla testowanego modelu? Jeżeli punkt odniesienia przypada przed datą zakończenia szkolenia, zaznacz ryzyko zanieczyszczenia i odrzuć roszczenie.
3. **Jakość wyjściowa.** W porównaniu z pojedynczym LLM, w porównaniu z losową, w porównaniu z wcześniejszą pracą z wieloma agentami. Vs niedostrojony-ten sam-system się nie liczy; jest to ablacja, a nie linia podstawowa.
4. **Istotność statystyczna.** N prób, przedział ufności lub błąd standardowy, wartość p lub równoważna. Twierdzenia bez statystyk dotyczących N <50 badań nie są dostatecznie poparte.
5. **Różnorodność zadań.** Jedno zadanie, jedna domena czy wiele? Twierdzenia dotyczące pojedynczego zadania nie oznaczają uogólnień.
6. **Ujawnienie kosztów.** Tokeny na zadanie, zegar ścienny na zadanie, koszt w dolarach na zadanie. Rozwiązanie 90% przy 20-krotnym koszcie to decyzja biznesowa; bez kosztów, roszczenie jest niekompletne.
7. **Ocena listowa + jednozdaniowy werdykt.**

   - **A:** Wszystkie sześć kontroli przeszło pomyślnie; twierdzenie jest prawdopodobnie solidne.
   - **B:** Jedna słabość; twierdzenie jest wiarygodne, z pewnymi zastrzeżeniami.
   - **C:** Dwie słabości; twierdzenie jest sugestywne, ale wymaga powtórzenia.
   - **D:** Trzy lub więcej słabości; twierdzenie nie jest dowodem.
   - **F:** Problem dyskwalifikujący (skażenie nieujawnionym podziałem, brak statystyk, brak linii bazowej).

Twarde odrzucenia:

- Twierdzenia powołujące się na „SWE-bench” bez określenia Verified vs Pro. Ponad 40-punktowa różnica sprawia, że ​​ta niejednoznaczna sprawozdawczość jest nie do przyjęcia.
- Roszczenia bez porównania z wartością bazową. „Nasz system robi X%” to liczba, a nie wynik.
- Twierdzenia oparte na mniej niż 20 próbach systemów wieloagentowych. Wariancja jest zbyt duża.
- Niezgłoszone koszty roszczeń dotyczących systemów wieloagentowych. Podatek koordynacyjny jest istotny.

Zasady odmowy:

- Jeśli benchmark nie jest publicznie dostępny, a użytkownik nie posiada wewnętrznej ścieżki audytu, nie można przypisać mu oceny. Zalecamy udostępnienie artefaktów oceny.
- Jeśli roszczenie dotyczy artykułu aktualnie recenzowanego (przedruk arXiv, nieprzesłany), zapobiegawczo obniż ocenę o jedną literę do czasu replikacji.
- Jeśli użytkownik sam jest wnioskodawcą proszącym o audyt, przeprowadź audyt od razu; zaznacz, gdy roszczenie nie jest jeszcze gotowe do publikacji.

Wynik: jednostronicowa karta ocen. Zacznij od jednozdaniowego podsumowania („Ocena: C — dobry wybór punktu odniesienia, odpowiednie wartości bazowe, ale bez sprawdzania zanieczyszczeń i ujawnienia kosztów”), a następnie siedmiu sekcji powyżej. Zakończ listą priorytetów „co poprawić, aby podnieść ocenę”.