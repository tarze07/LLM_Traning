---

name: ai-scientist-sandbox-review
description: Lista kontrolna dwuetapowego przeglądu wyników agenta badawczego przed ich eksportem z piaskownicy.
version: 1.0.0
phase: 15
lesson: 5
tags: [ai-scientist, research-agent, sandbox, peer-review, disclosure]

---

Biorąc pod uwagę autonomiczny wynik badania (hipotezę, kod, eksperymenty, wykresy, artykuł naukowy) wygenerowany przez pętlę w stylu AI-Scientist v2, przygotuj dwuetapową procedurę weryfikacji (dwubramkową): audyt piaskownicy (czy system nie został naruszony?) oraz audyt merytoryczny badań (czy praca jest rzetelna?).

Oba etapy odnoszą się bezpośrednio do poniższych kroków: **Bramka piaskownicy = punkt 1**; **Bramka badawcza = punkt 2 (audyt eksperymentu) + punkt 3 (audyt prezentacji/dopracowania)**. Punkty 4–5 definiują postępowanie po przejściu obu etapów.

Wyprodukuj:

1. **Bramka piaskownicy (Sandbox gate).** Zanim jakikolwiek artefakt opuści piaskownicę:
   - Stwórz listę wszystkich połączeń sieciowych nawiązanych w pętli i określ ich cele. Oznacz jako podejrzane te, które nie zostały wcześniej zatwierdzone.
   - Zinwentaryzuj każdy plik zapisany przez pętlę poza jej wyznaczonym katalogiem roboczym.
   - Potwierdź, że izolacja (Docker / seccomp / gVisor) była aktywna przez cały czas działania procesu.
   - Upewnij się, że żaden podproces nie wymknął się spod nadzoru piaskownicy.
   Jeśli jakakolwiek kontrola wykaże nieprawidłowości, zablokuj eksport i przekaż sprawę do weryfikacji przez człowieka.
2. **Audyt eksperymentu.** Przeanalizuj kod eksperymentu, a nie sam artykuł:
   - Sprawdź, czy każdy deklarowany eksperyment rzeczywiście się odbył, a jego raportowane wyniki są powtarzalne.
   - Upewnij się, że nieudane eksperymenty zostały uczciwie zgłoszone jako błędy/niepowodzenia, a nie zinterpretowane wstecznie jako „wyniki negatywne”.
   - Zweryfikuj, czy twierdzenie o nowatorstwie pomysłu wytrzymuje konfrontację z literaturą naukową ocenianą przez eksperta-człowieka.
3. **Audyt prezentacji (weryfikacja dopracowania formy).** Przeanalizuj dane i wykresy:
   - Upewnij się, że dane każdego wykresu pochodzą bezpośrednio z zarejestrowanego eksperymentu, a nie zostały zmanipulowane lub wygenerowane na etapie dopracowywania formy przez model wizyjny.
   - Potwierdź, że osie wykresów, skale i adnotacje są w 100% zgodne z danymi źródłowymi.
   - Oznacz każdy wykres lub rysunek, którego opis w tekście wykracza poza to, na co pozwalają zebrane dane.
4. **Plan ujawnienia autorstwa.** Jeśli artefakt ma trafić do dystrybucji zewnętrznej:
   - Wyraźnie zadeklaruj, że artykuł został wygenerowany przez autonomicznego agenta.
   - Wskaż użyte narzędzia (rodzina modeli, wersja pętli badawczej).
   - Podaj dane osoby weryfikującej, która zatwierdziła materiał, oraz zakres przeprowadzonego przez nią audytu.
5. **Decyzja o zablokowaniu publikacji/wydania.** Jeśli artefakt nie przejdzie pomyślnie dowolnego z etapów audytu, domyślnie nie może zostać wydany ani opublikowany. Zastąpienie tej reguły i wymuszenie publikacji wymaga pisemnej zgody wskazanego z nazwiska właściciela-człowieka.

Kryteria bezwzględnego odrzucenia:
- Przesłanie lub opublikowanie pracy z pominięciem dowolnego etapu weryfikacji.
- Brak kompletnych dzienników (logów) wykonania pętli badawczej dla weryfikowanego artefaktu.
- Dowolny wykres lub wynik, którego nie da się jednoznacznie powiązać z konkretnym, zarejestrowanym przebiegiem eksperymentu.
- Jakiekolwiek twierdzenie o nowości naukowej, które nie zostało zweryfikowane przez eksperta dziedzinowego.

Zasady odmowy:
- Jeśli w trakcie generowania artykułu brakowało izolacji w Dockerze (lub równoważnej piaskownicy), odmów weryfikacji i nakaż ponowne uruchomienie eksperymentu w bezpiecznym środowisku.
- Jeśli użytkownik nie jest w stanie dostarczyć kompletnych dzienników wykonania etapu eksperymentu, odmów – praca nie kwalifikuje się do recenzji.
- Jeśli planowany kanał publikacji to konferencja lub czasopismo recenzowane, a użytkownik nie zamierza ujawniać agenckiego pochodzenia tekstu, odmów i zażądaj dodania stosownej deklaracji.

Format wyjściowy:

Zwróć dwuetapowy raport z weryfikacji zawierający:
- **Werdykt bramki piaskownicy (Sandbox Gate)** (PASS / BLOCK, wraz z uzasadnieniem)
- **Werdykt bramki badawczej (Research Gate)** (obejmujący audyt eksperymentu (2) oraz audyt prezentacji (3)) (PASS / BLOCK / REQUIRES_EXPERT, wraz ze szczegółowymi uwagami do każdego punktu)
- **Plan ujawnienia autorstwa** (planowane miejsce publikacji, proponowany tekst deklaracji, nazwisko recenzenta weryfikującego)
- **Decyzja o publikacji** (publikacja / wstrzymanie / odrzucenie)
- **Następne kroki** (kto, co i do kiedy ma wykonać)
