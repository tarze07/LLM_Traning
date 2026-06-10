---

name: simulation-designer
description: Zaprojektuj symulację agenta generatywnego (w stylu Smallville) dla danego scenariusza. Określa schemat pamięci, częstotliwość refleksji, horyzont planu, ograniczenia przestrzenne/społeczne i metryki oceny.
version: 1.0.0
phase: 16
lesson: 17
tags: [multi-agent, simulation, generative-agents, emergence, memory]

---

Biorąc pod uwagę scenariusz, który wymaga wyłaniającego się zachowania populacji agentów (symulacja społeczna, NPC w grach, próba polityki, dynamika rynku), zaprojektuj symulację.

Wyprodukuj:

1. **Wielkość i heterogeniczność populacji.** N agentów; które mają ten sam model podstawowy i inny; szybkie rodziny; podział ról. Smallville wykorzystało 25 jednorodnych agentów o zindywidualizowanych osobowościach; większe populacje czerpią korzyści z heterogeniczności.
2. **Schemat pamięci.** Pola na wpis: `(ts, kind, content, importance, embedding_ref, source_ids)`. Stała zaniku świeżości; procedura punktacji ważności; metryka istotności (cosinus z osadzeniem modelu X). Polityka przechowywania w celu zagęszczenia.
3. **Częstość refleksji.** Wyzwalacz: suma nieprzetworzonej ważności > próg lub każde N obserwacji lub okresowe zaznaczenie. Liczba odbić na wyzwalacz. Szablon zachęty do refleksji.
4. **Horyzont planu.** Dzień/godzina/poziomy działań. Które są obowiązkowe; które opcjonalne. Wyzwalacz rewizji: nowa obserwacja o znaczeniu > progu, która jest sprzeczna z aktywnym planem.
5. **Model świata.** Siatka przestrzenna, wykres społeczny, ograniczenia zasobów. Co stanowi obserwację (linia widzenia, rozmowa, powiadomienie). Jakich ograniczeń normatywnych architektura NIE uczy się i musi być jawnie zakodowana (limity przepustowości, godziny zamknięcia, przestrzenie prywatne).
6. **Cele początkowe.** Którzy agenci mają określone priorytety. Nakładające się cele, które mogą ze sobą konkurować; niekonkurencyjne cele, które powinny współistnieć.
7. **Budżet.** Wezwania LLM per tik na agenta (obserwacja + odzyskanie + refleksja + plan + działanie). Oczekiwane tokeny na znacznik na agenta. Całkowity koszt symulacji dla znaczników T.
8. **Miernik oceny.** Wiarygodność (ocena przez człowieka), wskaźnik osiągnięcia celów, zliczone zdarzenia koordynacyjne, naruszenia norm przestrzennych jako sygnał niepowodzenia.

Twarde odrzucenia:

- Projekty bez wyraźnego kodowania norm przestrzennych/społecznych. Architektura je naruszy (awaria zamkniętego sklepu, pojedynczej łazienki z Parku 2023).
- Projekty ze zmienną pamięcią. Pamięć musi być przeznaczona tylko do dodawania; poprawki są nowymi wpisami.
- Projekty, które odzwierciedlają każdy tik. Jest to nieefektywne budżetowo; refleksja jest kosztowna, a wyzwalacze powinny opierać się na progach.
- Symulacje przy dużych N (> 50) bez strategii zagęszczania pamięci. Koszt odzyskiwania rośnie wraz z długością strumienia.

Zasady odmowy:

- Jeśli scenariusz wymaga wyłaniającego się *wykonania zadania*, a nie wyłaniającego się *zachowania społecznego*, zamiast tego zarekomenduj przełożonego/role/pierwotne wzorce (Faza 16 · 05-08). Smallville służy do symulacji społecznej.
- Jeśli budżet pozwala na < 100 LLM calls per tick total, recommend N = 3-5 with dense interactions rather than larger populations.
- If the scenario does not benefit from emergence (tightly-scripted task), recommend single-agent + tools.

Output: a one-page design brief. Start with a single-sentence summary ("Smallville-style simulation: 15 heterogeneous agents, reflection at importance sum > 120, 3-poziomowy horyzont planu, siatka przestrzenna z ograniczeniami wydajności, mierzona wiarygodnością + zdarzenia koordynacyjne.”), wówczas osiem sekcji powyżej. Zakończ oczekiwanymi zachowaniami wschodzącymi i pierwszymi trzema trybami awarii, na które należy zwrócić uwagę.