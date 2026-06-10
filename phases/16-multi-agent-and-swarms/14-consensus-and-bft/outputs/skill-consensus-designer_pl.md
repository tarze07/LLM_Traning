---

name: consensus-designer
description: Zaprojektuj protokół konsensusu uwzględniający BFT dla zestawu wielu agentów. Wybiera zasady grupowania, ważenia, progu i eskalacji; atak-testuje projekt pod kątem wzorców bizantyjskich, pochlebczych i monokulturowych.
version: 1.0.0
phase: 16
lesson: 14
tags: [multi-agent, consensus, BFT, voting, confidence]

---

Biorąc pod uwagę zbiór N agentów odpowiadających na częste pytania, zaprojektuj protokół konsensusu, który będzie odporny na trzy kanoniczne ataki agentów LLM: bizantyjskie kłamstwo, pochlebczy konformizm, monokultura skorelowanych błędów.

Wyprodukuj:

1. **Strategia grupowania.** Jak grupowane są odpowiedzi? Kanonizacja ciągów (małe litery + punktacja), osadzanie podobieństwa z progiem lub wyraźna kanonizacja strukturalna (schemat JSON). Podaj oczekiwany współczynnik błędów szczegółowości klastra.
2. **Strategia ważenia.** Wielość (zliczenia), ważona sondą ufności (CP-WBFT), jakość plus zaufanie (WBFT) lub oparta na wynikach z odpornością na medianę geometryczną (DecentLLM). Uzasadnij wybór z profilu ataku.
3. **Próg.** Jaki ułamek całkowitej masy powoduje akceptację? Co dzieje się poniżej progu: ponów próbę, eskaluj lub wstrzymaj się od głosu?
4. **Wymóg różnorodności.** Ile modeli podstawowych, rodzin podpowiedzi lub ustawień temperatury wymaga zestaw? Monokultura jest atakiem, po którym wielość nie może się otrząsnąć; różnorodność to łagodzenie strukturalne.
5. **Niezależny weryfikator.** Czy istnieje agent tylko do odczytu, który pobiera podstawową prawdę (jeśli jest dostępna) lub stosuje rubrykę? Gdzie trafiają dane wyjściowe weryfikatora? Nie może ponownie trafić do puli głosów.
6. **Ograniczenie rund.** Maksymalna liczba rund przed eskalacją. Domyślnie 2-3 dla większości zadań. Dłuższe rundy wzmacniają pochlebstwa.
7. **Tabela testu ataku.** Dla każdego z nich (bizantyjski, pochlebczy, monokulturowy) pokaż oczekiwane zachowanie protokołu i ryzyko szczątkowe. Jeżeli protokół dopuszcza znany tryb awaryjny, należy to opisać w jednym zdaniu.

Twarde odrzucenia:

- Każdy projekt, który obsługuje wiele - tylko na jednym modelu podstawowym. Monokultura sprawia, że ​​to po cichu się nie udaje.
- Dowolny projekt z nieograniczoną liczbą rund lub „dyskutuj aż do porozumienia”. To nagradza konformizm.
- Dowolny projekt, w którym wyniki weryfikatora trafiają z powrotem do puli głosów. To zatruwa weryfikatora.
- Twierdzenie, że BFT „rozwiązuje” spór. BFT wyrównuje wyniki; poprawność to osobny problem.

Zasady odmowy:

- Jeśli zadanie nie ma podstaw prawdziwych (opinia, synteza, twórczość), powiedz to i zarekomenduj „konsensus jako doradca, człowiek jako decydujący”.
- Jeżeli dostępnych jest mniej niż 3 agentów, konsensus nie ma zastosowania; Zamiast tego polecam jednego agenta i weryfikatora.
- Jeśli wszyscy agenci mają ten sam model podstawowy i użytkownik nie może tego zmienić, wyraźnie oznacz sufit monokultury.

Wynik: jednostronicowy opis projektu. Zacznij od podsumowania składającego się z jednego zdania („Głosowanie ważone zaufaniem na 5 agentach (3 modele podstawowe), próg klastra semantycznego 0,55, niezależny weryfikator ponownie pobiera źródła, maksymalnie 2 rundy”), a następnie siedem sekcji powyżej. Zakończ tabelą testów ataku.