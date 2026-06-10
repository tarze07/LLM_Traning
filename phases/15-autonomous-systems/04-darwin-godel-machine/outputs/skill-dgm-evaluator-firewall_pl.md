---

name: dgm-evaluator-firewall
description: Określ separację ewaluatorów, której potrzebuje pętla samomodyfikującego się agenta typu Darwin-Godel-Machine, aby uniknąć udokumentowanego hakowania nagród.
version: 1.0.0
phase: 15
lesson: 4
tags: [dgm, self-modification, reward-hacking, evaluator, sandbox]

---

Biorąc pod uwagę proponowaną samomodyfikującą się pętlę agenta (rusztowanie agenta, potok ewaluatora, cel wdrożenia), utwórz specyfikację zapory ogniowej, która utrzymuje ewaluatora poza zasięgiem agenta. Artykuł DGM udokumentował, że agent usuwał własne znaczniki bezpieczeństwa, aby podnieść wyniki; ta umiejętność to kontrola.

Wyprodukuj:

1. **Granica systemu plików.** Lista wszystkich plików, które agent może edytować. Wypisz każdy plik, który czyta osoba oceniająca. Skrzyżowanie musi być puste. Jeśli tak nie jest, określ dokładny ruch potrzebny do opróżnienia go.
2. **Granica procesu.** Ewaluator musi działać w procesie, którego agent nie kontroluje. Określ kontener lub piaskownicę. Jeśli agent ma dostęp do powłoki, może ominąć zabezpieczenia w procesie.
3. **Granica sieci i sekretu.** Agent nie może edytować kluczy tajnych CI, które pobierają dane wejściowe osoby oceniającej lub publikują wyniki. Wypisz, gdzie żyją sekrety i jak są montowane.
4. **Kontrakt na przesyłanie wyników.** Wyniki zwracane są od osoby oceniającej do archiwum pętli. Ta ścieżka jest jedynym kanałem. Wszystko, co agent może napisać i co ma wpływ na przyszłą punktację, zrywa umowę.
5. **Lista przeglądu mutacji.** Lista klas edycji agenta, które wymagają ręcznego przeglądu przed akceptacją: nowe zależności, zmiany w kodzie sąsiadującym ze scoringiem, zmiany w konfiguracji piaskownicy, zmiany w logowaniu lub monitorowaniu.

Twarde odrzucenia:
- Narzędzie oceniające w tym samym repozytorium co źródło agenta. Przesuń to.
- Narzędzie oceniające działające jako import Pythona w procesie agenta. Uruchom go w podprocesie.
- Jakakolwiek korekta wyniku zastosowana po stronie agenta. Wszelkie dostosowania muszą odbywać się po stronie serwera.
- Każde logowanie, które agent może wyciszyć, edytując swój własny kod.

Zasady odmowy:
- Jeśli użytkownik nie może nazwać każdego pliku, który agent może edytować, odmówi i zażąda najpierw audytu dostępu do zapisu na poziomie pliku.
- Jeśli oceniający nie ma żadnych zastrzeżeń, odmów – to warunek wstępny, audyt z Lekcji 3.
- Jeśli powierzchnia wdrożenia zawiera mutacje w samym ewaluatorze (nawet pośrednio poprzez proponowaną aktualizację zależności), odmów i wymagaj ręcznego przeglądu zapory ogniowej.

Format wyjściowy:

Zwróć jednostronicową specyfikację za pomocą:
- **Powierzchnia zapisu agenta** (ścieżki, globy)
- **Powierzchnia odczytu oceniającego** (ścieżki, punkty końcowe)
- **Przecięcie** (musi być puste; pokaż różnicę)
- **Model procesu** (sposób izolacji oceniającego)
- **Inwentarz tajemnic** (gdzie i jak zamontowany)
- **Klasy mutacji wymagane do przeglądu** (wypunktowane)
- **Linia podpisu** (kto jest właścicielem niezmiennika firewalla)