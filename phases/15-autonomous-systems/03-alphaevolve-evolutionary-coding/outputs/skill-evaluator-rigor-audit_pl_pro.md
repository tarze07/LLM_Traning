---

name: evaluator-rigor-audit
description: Przed zatwierdzeniem jakichkolwiek obliczeń w wyszukiwaniu przeprowadź audyt proponowanego ewaluatora pętli kodowania ewolucyjnego w stylu AlphaEvolve.
version: 1.0.0
phase: 15
lesson: 3
tags: [alphaevolve, evolutionary-coding, evaluator, reward-hacking, deepmind]

---

Biorąc pod uwagę proponowaną ewolucyjną pętlę kodowania (generator LLM, baza danych programów, ewaluator), przeprowadź audyt ewaluatora. Ewaluator stanowi fundament architektury; generator jest wymienny. Ta umiejętność decyduje o tym, czy pętla ma szansę wygenerować wartościowe rezultaty, czy tylko bezużyteczny kod dostosowany do zhakowanych nagród.

Wyprodukuj:

1. **Dekompozycja ewaluatora.** Wskaż każdy sygnał zwracany przez ewaluator: poprawność, wydajność, zużycie zasobów i inne. Dla każdego z nich określ: (a) jak jest mierzony, (b) jak łatwo można nim manipulować / oszukać system (game the system), (c) jak wygląda reguła generowania wydzielonych danych wejściowych (holdout data).
2. **Powierzchnia konfabulacji.** Wymień trzy najbardziej prawdopodobne konfabulacje LLM w tej dziedzinie: deklarowane klasy złożoności obliczeniowej, deklarowana poprawność dla przypadków brzegowych, deklarowana wydajność bez rzeczywistego pomiaru. Określ, który z sygnałów ewaluatora przechwytuje poszczególne z nich.
3. **Powierzchnia hakowania nagród.** Wskaż trzy prawdopodobne metody, za pomocą których pętla może zmaksymalizować wynik bez poprawnego wykonania właściwego zadania (skrót przechodzący testy, manipulowanie wskaźnikiem zastępczym/proxy gaming, zapamiętywanie danych wejściowych). Zaproponuj środki zaradcze dla każdego przypadku.
4. **Determinizm i odtwarzalność.** Wymagaj, aby wyniki ewaluatora były deterministyczne w granicach określonej tolerancji. Zgłoś ostrzeżenie dla każdego ewaluatora, którego wyniki wykazują wariancję większą niż wariancja populacji w trakcie trwania procesu.
5. **Kontrola wdrożenia.** Jeśli zwycięski wariant ma trafić do środowiska produkcyjnego, wymagaj osobnego, niezależnego przeglądu przed wdrożeniem, oceniającego aspekty niekontrolowane przez ewaluator (bezpieczeństwo, koszty, ręczna weryfikacja). Samo pomyślne wyszukiwanie nie oznacza gotowości kodu do wdrożenia (search does not equal deployment-ready).

Kryteria bezwzględnego odrzucenia:
- Każda pętla, w której jako ewaluator występuje sędzia LLM pozbawiony weryfikowalnej maszynowo prawdy obiektywnej (ground truth). Sędziów LLM można łatwo oszukać.
- Każdy ewaluator zwracający pojedynczy wynik skalarny bez podania rozkładu wyników. Wyniki skalarne ułatwiają hakowanie nagród.
- Ewaluacja przeprowadzana wyłącznie na zestawach treningowych. Zastosowanie wydzielonych danych (holdouts) nie podlega negocjacjom.

Zasady odmowy:
- Jeśli użytkownik nie potrafi opisać ewaluatora w dwóch akapitach, odmów i poproś najpierw o szczegółową specyfikację ewaluatora. Pętle bez zdefiniowanego ewaluatora nie są gotowe do uruchomienia obliczeń.
- Jeśli domena jest niezweryfikowana (twórcze pisanie, otwarte hipotezy naukowe, długoterminowe badania), odrzuć projekt i zarekomenduj potok hybrydowy z weryfikacją przez człowieka zamiast zamkniętej pętli.
- Jeśli proponowany obszar wdrożenia jest nieodwracalny (krytyczne zmiany w infrastrukturze produkcyjnej, zamiana algorytmów w gotowym produkcie/shipped product), odmów wdrożenia w pętli zamkniętej. Wymagaj wdrożenia etapowego i zatwierdzenia przez człowieka.

Format wyjściowy:

Zwróć jednostronicową notatkę zawierającą:
- **Podsumowanie pętli** (generator, ewaluator, domena docelowa)
- **Ocena ewaluatora** (rygor w skali 1-5 wraz z uzasadnieniem)
- **Powierzchnia konfabulacji** (pierwsze 3 wraz z pokryciem przez ewaluator)
- **Powierzchnia hakowania nagród** (pierwsze 3 wraz ze środkami zaradczymi)
- **Determinizm i odtwarzalność** (wariancja wyniku vs wariancja populacji; kontrola ziarna generatora/seed control; werdykt pass/fail)
- **Gotowość do wdrożenia** (dozwolone wdrożenie w pętli zamkniętej: tak/nie; wymagane przeglądy przedwdrożeniowe: bezpieczeństwo, koszty, zasoby ludzkie)
- **Zalecenie** (kontynuuj / zaostrz kryteria oceny / wybierz inną domenę)
