---

name: mast-auditor
description: Narzędzie do przeprowadzania audytów trybów awarii systemów wieloagentowych (MAS) w standardzie taksonomii MAST. Pozwala na klasyfikację błędów na problemy ze specyfikacją, koordynacją i weryfikacją oraz badanie zjawiska myślenia grupowego, ułatwiając priorytetyzację poprawek.
version: 1.0.0
phase: 16
lesson: 23
tags: [multi-agent, failure-modes, MAST, groupthink, circuit-breaker, audit]

---

Na podstawie danych z systemu wieloagentowego oraz próbki śladów wykonania (execution traces), przeprowadź audyt stabilności i trybów awarii.

Opracuj następujące elementy:

1. **Konstrukcja próby badawczej.** Dobór co najmniej 200 śladów z produkcji, próbkowanych równomiernie pod kątem różnych typów zadań oraz okien czasowych. Udokumentuj metodę próbkowania oraz przeanalizuj ryzyko wystąpienia błędów systematycznych (bias).
2. **Karta klasyfikacji błędów.** Dla każdego śladu określ wynik: `success | failure`. W przypadku awarii przypisz jej jedną główną kategorię MAST (specyfikacja / koordynacja / weryfikacja) oraz, jeśli dotyczy, jeden lub więcej znaczników ze zjawisk Groupthink (monokultura / konformizm / ToM / konflikt interesów / kaskada).
3. **Macierz rozkładu.** Liczba i udział procentowy awarii według kategorii MAST i zjawisk Groupthink. Zestaw wyniki z rozkładem referencyjnym Cemriego z 2025 roku (41,77% / 36,94% / 21,30%). Wyraźne odchylenia od tego profilu wskazują na konkretne słabości architektoniczne badanego systemu.
4. **Kluczowe wzorce awarii.** Zidentyfikuj 3 najczęściej powtarzające się scenariusze awarii (np. konflikt ról przy recenzowaniu przez dwóch agentów). Udokumentuj kroki niezbędne do zreplikowania tych błędów.
5. **Priorytetyzacja akcji zaradczych.** Dla każdego zidentyfikowanego wzorca błędu zaproponuj odpowiednie środki zaradcze: jednoznaczne kontrakty ról, wersjonowany stan współdzielony, niezależny weryfikator, wyłącznik sieciowy (circuit breaker) lub trio nadzorcze w standardzie STRATUS. Uszereguj rekomendacje według szacowanego poziomu redukcji awarii (zwrotu z inwestycji - ROI), uwzględniając częstotliwość występowania danego błędu.
6. **Analiza ryzyka cichych awarii.** Porównaj liczbę awarii generujących prawdopodobne, lecz błędne wyniki z twardymi błędami systemowymi. Wysoki wskaźnik cichych błędów uzasadnia inwestycje w dodatkowe warstwy weryfikacyjne.
7. **Wskaźniki pomocnicze (proxy metrics).** Zaproponuj 2–3 metryki przydatne do wczesnego wykrywania dryfu systemu (zanim przełoży się on na krytyczną awarię), takie jak: współczynnik zgodności odpowiedzi, współczynnik ponownych prób, rozkład długości generowanego tekstu lub odległość edycyjna między wersjami wypowiedzi agentów.

Kryteria twardego odrzucenia:

- Przeprowadzanie audytów na bazie niereprezentatywnych próbek (brak losowości lub próbkowania warstwowego). Cherry-picking dramatycznych błędów z logów zniekształca statystyki i uniemożliwia wykrycie powolnego dryfu.
- Proponowanie środków zaradczych bez określenia punktu odniesienia (baseline). Rekomendacja „wdrożenia weryfikatora” jest bezużyteczna, jeśli nie określono aktualnego wskaźnika awaryjności.
- Wymuszanie przypisywania błędów do niepasujących kategorii taksonomii MAST. Jeśli ślad wykonania nie odpowiada żadnej definicji, zaproponuj rozszerzenie taksonomii zamiast naginania faktów.
- Traktowanie kwartalnych audytów jako substytutu dla bieżącego monitorowania wskaźników pomocniczych. Kwartalny audyt nie zapobiegnie awariom w okresach między badaniami.

Zasady odmowy (rekomendacje alternatywne):

- Jeśli ślady wykonania nie rejestrują autorstwa akcji (kto zapisał dane, a kto je odczytał), audytor nie jest w stanie odróżnić błędów koordynacji od konfliktów ról. Zaleć wdrożenie ustrukturyzowanego logowania z przypisaniem akcji do konkretnych tożsamości agentów przed ponownym audytem.
- Jeśli całkowita liczba zidentyfikowanych błędów w logach wynosi mniej niż 50, próba jest zbyt mała, aby rzetelnie oszacować rozkład statystyczny. Zaleć wydłużenie okna obserwacji.
- Jeśli analizowane logi zawierają dane osobowe lub wrażliwe (PII), należy przeprowadzić ich anonimizację przed przystąpieniem do analizy.

Format wyjściowy: trzystronicowy raport z audytu. Rozpocznij od jednozdaniowego podsumowania (np. „Wskaźnik awaryjności: 41% błędy specyfikacji, 12% błędy koordynacji, 39% luki w weryfikacji, 8% przyczyny niezidentyfikowane; główny wzorzec awarii to konflikt ról recenzentów; wdrożenie precyzyjnych reguł odpowiedzialności zapewnia najwyższy zwrot z inwestycji (ROI)”), po którym następuje omówienie siedmiu powyższych punktów. Raport zakończ priorytetyzowaną listą działań obejmującą trzy rekomendowane środki zaradcze z szacowanym kosztem ich wdrożenia i prognozowanym poziomem redukcji awaryjności.
