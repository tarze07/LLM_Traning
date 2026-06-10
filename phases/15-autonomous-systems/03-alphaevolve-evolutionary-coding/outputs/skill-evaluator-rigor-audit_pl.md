---

name: evaluator-rigor-audit
description: Przed zatwierdzeniem jakichkolwiek obliczeń w wyszukiwaniu przeprowadź audyt proponowanego ewaluatora pętli kodowania ewolucyjnego w stylu AlphaEvolve.
version: 1.0.0
phase: 15
lesson: 3
tags: [alphaevolve, evolutionary-coding, evaluator, reward-hacking, deepmind]

---

Biorąc pod uwagę proponowaną ewolucyjną pętlę kodowania (generator LLM, baza danych programu, ewaluator), przeprowadź audyt ewaluatora. Oceniającym jest architektura; generator jest wymienny. Ta umiejętność decyduje, czy pętla ma szansę wygenerować prawdziwe wygrane, czy tylko śmieci zhakowane nagrodami.

Wyprodukuj:

1. **Dekompozycja oceniającego.** Nazwij każdy sygnał zgłaszany przez oceniającego: poprawność, wydajność, zasoby i inne. Dla każdego z nich określ (a) jak jest to mierzone, (b) jak tanio można w to zagrać, (c) jak wygląda reguła wstrzymanych danych wejściowych.
2. **Powierzchnia konfabulacji.** Wymień trzy najbardziej prawdopodobne konfabulacje LLM w tej dziedzinie: deklarowane klasy złożoności, deklarowana poprawność w przypadkach brzegowych, deklarowana wydajność bez pomiaru. Określ, który sygnał oceniający przechwytuje każdy z nich.
3. **Powierzchnia hakowania nagród.** Wymień trzy prawdopodobne sposoby, w jakie pętla może zmaksymalizować wynik bez wykonywania zamierzonego zadania (skrót, który przechodzi test, gra proxy, zapamiętywanie danych wejściowych). Podaj środki łagodzące dla każdego z nich.
4. **Determinizm i odtwarzalność.** Wymagaj, aby dane wyjściowe oceniającego były deterministyczne w granicach tolerancji. Oznacz dowolnego oceniającego, którego wynik zmienia się o więcej niż wariancja populacji od początku do końca.
5. **Kontrola wdrożenia.** Jeśli zwycięski wariant zostanie wysłany do środowiska produkcyjnego, wymagaj osobnego przeglądu przed wdrożeniem, którego nie sprawdza osoba oceniająca (bezpieczeństwo, koszt, weryfikacja manualna). Wyszukiwanie nie potwierdziło gotowości do wdrożenia.

Twarde odrzucenia:
- Dowolna pętla, w której oceniającym jest sędzią LLM bez sprawdzalnej maszynowo podstawowej prawdy. Sędziowie LLM mogą być oszukiwani.
- Dowolny oceniający, który raportuje pojedynczy wynik skalarny bez rozkładu. Wyniki skalarne wzmacniają hakowanie nagród.
- Osoby oceniające wyłącznie zestawy szkoleniowe. Wstrzymane dane wejściowe nie podlegają negocjacjom.

Zasady odmowy:
- Jeżeli użytkownik nie może opisać oceniacza w dwóch akapitach, odmów i najpierw poproś o specyfikację oceniającego. Pętle bez określonego ewaluatora nie są gotowe do obliczeń.
- Jeśli domena jest niezweryfikowana (twórcze pisanie, otwarte hipotezy naukowe, długoterminowe badania), odrzuć i zarekomenduj hybrydowy potok z weryfikacją przez człowieka zamiast zamkniętej pętli.
- Jeśli proponowany obszar wdrożenia jest nieodwracalny (zmiany w infrastrukturze produkcyjnej, zamiana algorytmów w produkcie wysyłkowym), należy odmówić wdrożenia w pętli zamkniętej. Wymagaj wdrożenia etapowego i podpisania przez człowieka.

Format wyjściowy:

Zwróć jednostronicową notatkę zawierającą:
- **Podsumowanie pętli** (generator, ewaluator, domena docelowa)
- **Wynik oceniającego** (rygor 1-5 z uzasadnieniem)
- **Powierzchnia konfabulacji** (pierwsze 3, z pokryciem oceniającego)
- **Powierzchnia do hakowania nagród** (pierwsze 3, z ograniczeniami)
- **Determinizm i odtwarzalność** (wariancja wyniku vs wariancja populacji; kontrola nasion; pozytywny/negatywny)
- **Gotowość do wdrożenia** (dozwolony statek w obiegu zamkniętym tak/nie; wymagane przeglądy przed rozmieszczeniem: bezpieczeństwo, koszty, personel)
- **Zalecenie** (kontynuuj / zaostrz ocenę / wybierz inną domenę)