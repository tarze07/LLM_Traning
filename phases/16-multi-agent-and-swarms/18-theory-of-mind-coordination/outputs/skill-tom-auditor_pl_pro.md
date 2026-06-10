---

name: tom-auditor
description: Przeprowadź audyt systemu wieloagentowego wymagającego „emergentnej koordynacji”. Narzędzie to oddziela rzeczywistą koordynację opartą na ToM od iluzji wywołanej promptowaniem, wykorzystując grupy kontrolne, testy statystyczne i miary komplementarności.
version: 1.0.0
phase: 16
lesson: 18
tags: [multi-agent, theory-of-mind, coordination, evaluation, emergence]

---

Biorąc pod uwagę system wieloagentowy wymagający emergentnej koordynacji, zweryfikuj, czy koordynacja ta jest rzeczywista, czy stanowi jedynie artefakt inżynierii promptów.

Opracuj następujące elementy:

1. **Wyszczególnienie deklaracji.** Jakie konkretnie zachowania koordynacyjne są przypisywane systemowi (np. podział pracy, antycypacja działań, komplementarność zachowań, osiąganie konsensusu)? Sformułuj je precyzyjnie.
2. **Inspekcja promptów.** Czy prompt systemowy dowolnego agenta jawnie nakazuje koordynację, wybór określonej roli lub dbanie o współpracę w zespole? Jeśli tak, oznacz taką deklarację jako wymuszoną przez prompt (prompt-engineered) i zaprojektuj warunek kontrolny.
3. **Warunek kontrolny.** Wariant systemu pozbawiony sformułowań wymuszających lub sugerujących koordynację. Określ dokładnie, jakie fragmenty tekstu w promptach należy zmodyfikować lub usunąć.
4. **Metryki.** Wybierz co najmniej jeden wskaźnik: zróżnicowanie powiązane z tożsamością, komplementarność działań lub synergię wyższego rzędu (według Riedla, 2025). Nie traktuj samych deklaracji agentów o chęci współpracy jako dowodu jej zaistnienia.
5. **Testy statystyczne.** Istotność statystyczna różnic metryk między systemem a wariantem kontrolnym. Określ rozmiar próby wymagany do osiągnięcia `p < 0.05`. W przypadku małych próbek (n < 50) jawnie oszacuj i podaj moc testu.
6. **Weryfikacja wpływu klasy modelu.** Powtórz badanie przy użyciu mniejszego modelu bazowego. Sprawdź, czy efekt koordynacji się utrzymuje, czy zanika. Publikacje Li i in. oraz Riedla wykazują silną zależność od możliwości intelektualnych (capacity) modelu.
7. **Analiza trybów awarii.** Gdy system zawodzi, zbadaj zarejestrowany stan ToM (o ile istnieje). Czy problemem jest błędne powiązanie tożsamości agenta z przekonaniem (confusion of identity - kto co myśli), czy też halucynacje dotyczące samej treści przekonania?

Kryteria twardego odrzucenia:

- Deklarowanie emergencji bez przeprowadzenia testów w warunkach kontrolnych. Same logi z wersji demonstracyjnej nie są dowodem.
- Twierdzenia o koordynacji, które nie wytrzymują analizy statystycznej (brak istotności przy p < 0.05 dla próby n >= 50). Są to iluzje koordynacji.
- Wyciąganie wniosków na podstawie tylko jednego modelu. Jeśli mniejszy, a zarazem silny model referencyjny również osiąga podobny efekt bez promptowania ToM, to mechanizm koordynacji nie wynika z Teorii Umysłu.
- Tłumaczenie mechanizmu koordynacji stwierdzeniem: „nasi agenci po prostu sami na to wpadli”. Wyjaśnienie mechanizmu wymaga udokumentowania i zweryfikowania stanów ToM w logach.

Zasady odmowy wykonania audytu (rekomendacje):

- Jeśli system nie rejestruje procesu wnioskowania poszczególnych agentów, audytor nie jest w stanie odróżnić rzeczywistej koordynacji od przypadkowych zbiegów okoliczności. Zaleć wdrożenie ustrukturyzowanych logów stanu ToM przed ponownym podejściem do audytu.
- Jeśli istnieje matematycznie wyznaczony stan optymalny (wyliczony przez wyrocznię/oracle), porównaj wyniki systemu z tym punktem odniesienia, a nie z warunkiem kontrolnym.
- Jeśli zakres audytu jest wąski (np. „koordynacja w zadaniu jednorundowym”), przeprowadź skróconą weryfikację: zmierz komplementarność w ramach jednej rundy, bez konieczności prowadzenia analizy długoterminowej.

Format wyjściowy: dwustronicowy raport z audytu. Rozpocznij od jednozdaniowego werdyktu (np. „Deklaracja koordynacji opiera się wyłącznie na promptowaniu: usunięcie sformułowania 'współpracuj' powoduje spadek wartości metryki z 0,82 do 0,31 względem grupy kontrolnej”), po czym przedstaw omówienie siedmiu powyższych punktów. Raport zakończ listą rekomendacji pozwalających przekształcić koordynację opartą na promptach w rzeczywistą koordynację: wprowadzenie jawnego stanu ToM, optymalizacja pod kątem długich horyzontów z logowaniem stanów oraz stosowanie zespołów złożonych z różnych modeli.
