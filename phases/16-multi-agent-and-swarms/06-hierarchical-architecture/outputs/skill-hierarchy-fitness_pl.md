---

name: hierarchy-fitness
description: Zdecyduj, czy zadanie wieloagentowe pasuje do zadania hierarchicznego, płaskiego czy sekwencyjnego. Wyróżnij istotne tryby awarii.
version: 1.0.0
phase: 16
lesson: 06
tags: [multi-agent, hierarchy, crewai, langgraph, decomposition-drift]

---

Mając opis zadania i opcjonalną strukturę organizacyjną, zarekomenduj wzorzec koordynacji (płaski przełożony, hierarchiczny, sekwencyjny) i wypisz konkretne tryby awarii, przed którymi należy się chronić.

Wyprodukuj:

1. **Analiza kształtu zadania.** Czy zadanie ma charakter liniowy, jest podzielone na niezależne oddziały, czy też zespoły zagnieżdżone z własnymi podzespołami? Uzasadniać.
2. **Werdykt wzorcowy.** Przełożony sekwencyjny, płaski lub hierarchiczny. Jeśli jest to hierarchia, określ głębokość (zdecydowanie preferowane 2 poziomy; 3 tylko w przypadku silnej potrzeby audytu).
3. **Plan rozkładu.** Dokładny podział, jaki powinien dokonać najwyższy menedżer. Dla każdego oddziału nazwij podrzędnego menedżera i ograniczony zakres.
4. **Budżet uzgodnieniowy.** Liczba rund dozwolonych, zanim menedżer najwyższego szczebla będzie musiał podjąć decyzję. Domyślny 2.
5. **Poręcze.** Trzy minimalne poręcze: pracownik kanarkowy na poziom, łańcuch pochodzenia przy każdej syntezie, alarm w przypadku dryfu rozkładu.
6. **Lista kontrolna trybu awaryjnego.** Które z {błąd przydziału zadań, błędna interpretacja wyników, pętla konsensusu} najprawdopodobniej ma dany kształt zadania? Opisz jeden konkretny objaw i jedno rozwiązanie łagodzące dla każdego trybu.

Twarde odrzucenia:

- Wszelkie zalecenia proponujące głębokość > 2 bez podawania konkretnego audytu lub wymagania organizacji, które tego wymagają.
- Hierarchiczny dla zadań o pojedynczym przepływie liniowym. To powinny być rurociągi sekwencyjne.
- Projekty bez wyraźnego budżetu uzgodnieniowego.

Zasady odmowy:

- Jeśli zadanie jest na tyle proste, że mieści się w nim jeden agent (poniżej ~10 wywołań narzędzi), odrzuć hierarchię i zaleć jednego agenta.
- Jeśli zadanie nie ma naturalnych granic zespołu (każdy podetap jest od siebie zależny), odmów i zamiast tego zaproponuj schemat czatu grupowego.
- Jeśli użytkownik chce hierarchii ze względu na „realizm” (ponieważ organizacja ludzka jest głęboka), zaznacz, że hierarchia ludzka nie jest mapowana na hierarchię LLM i zalecij bardziej płaską.

Wynik: jednostronicowy brief. Otwórz werdyktem dotyczącym wzoru, zamknij trzema największymi zagrożeniami i ich barierami.