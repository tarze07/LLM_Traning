---

name: dgm-evaluator-firewall
description: Określ izolację ewaluatorów, której wymaga pętla samomodyfikującego się agenta typu Darwin-Gödla-Machine, aby uniknąć udokumentowanego hakowania nagród.
version: 1.0.0
phase: 15
lesson: 4
tags: [dgm, self-modification, reward-hacking, evaluator, sandbox]

---

Biorąc pod uwagę proponowaną samomodyfikującą się pętlę agenta (szkielet/rusztowanie agenta, potok ewaluatora, cel wdrożenia), utwórz specyfikację zapory ewaluacyjnej (firewall), która utrzymuje ewaluator poza zasięgiem agenta. W publikacji o DGM udokumentowano, że agent usuwał własne znaczniki bezpieczeństwa w celu podwyższenia wyników – wdrożenie tej umiejętności stanowi kluczową kontrolę bezpieczeństwa.

Wyprodukuj:

1. **Granica systemu plików.** Zdefiniuj listę wszystkich plików, które agent może edytować. Wskaż każdy plik odczytywany przez ewaluator. Ich część wspólna (skrzyżowanie) musi być absolutnie pusta. Jeśli tak nie jest, określ dokładnie kroki niezbędne do wyeliminowania nakładania się uprawnień.
2. **Granica procesu.** Ewaluator musi być uruchamiany w procesie, na który agent nie ma wpływu (nie kontroluje go). Określ konfigurację kontenera lub piaskownicy (sandbox). Jeśli agent uzyska dostęp do powłoki systemowej (shell) hosta, może omijać zabezpieczenia procesów.
3. **Granica sieci i kluczy tajnych.** Agent nie może mieć możliwości edycji kluczy tajnych systemu CI/CD, które służą do pobierania danych wejściowych ewaluatora lub publikowania wyników scoringu. Wypisz, gdzie przechowywane są te sekrety i jak są one montowane w środowisku.
4. **Kontrakt przesyłania wyników.** Wyniki są przekazywane z ewaluatora bezpośrednio do archiwum pętli. Ta ścieżka musi być jedynym dopuszczalnym kanałem komunikacji. Jakakolwiek możliwość zapisu po stronie agenta, która wpływa na przyszłą punktację, łamie ten kontrakt.
5. **Lista kontrolna przeglądu mutacji.** Stwórz listę klas edycji kodu agenta, które bezwzględnie wymagają ręcznego zatwierdzenia przez człowieka przed akceptacją: dodanie nowych zależności, modyfikacje kodu sąsiadującego ze strukturą scoringową, zmiany konfiguracji piaskownicy, modyfikacje logowania i systemów monitoringu.

Kryteria bezwzględnego odrzucenia:
- Umieszczenie narzędzia oceniającego (ewaluatora) w tym samym repozytorium, w którym znajduje się kod źródłowy agenta. Należy je bezwzględnie odizolować.
- Uruchamianie ewaluatora jako importu Pythona wewnątrz procesu agenta. Ewaluator musi działać w osobnym podprocesie.
- Jakakolwiek korekta wyniku (scoringu) aplikowana po stronie kodu agenta. Wszelkie korekty muszą odbywać się po stronie serwera ewaluacji.
- Dowolna logika logowania, którą agent może wyciszyć poprzez modyfikację własnego kodu.

Zasady odmowy:
- Jeśli użytkownik nie jest w stanie wskazać każdego pliku, do którego agent ma uprawnienia zapisu, odmów i zażądaj najpierw pełnego audytu dostępu do plików.
- Jeśli ewaluator nie korzysta z wydzielonych danych (holdouts), odmów – to warunek konieczny (zgodnie z audytem z Lekcji 3).
- Jeśli potok wdrożeniowy zawiera mutacje w samym ewaluatorze (nawet pośrednio poprzez aktualizację konfiguracji zależności), odmów i wymagaj ręcznego przeglądu zapory.

Format wyjściowy:

Zwróć jednostronicową specyfikację zawierającą:
- **Obszar zapisu agenta** (ścieżki, wyrażenia glob)
- **Obszar odczytu ewaluatora** (ścieżki, punkty końcowe)
- **Część wspólna** (musi być pusta; wskaż ewentualne różnice)
- **Model procesu** (sposób izolacji procesu ewaluatora)
- **Wykaz sekretów/kluczy** (miejsce i sposób ich montowania)
- **Klasy mutacji wymagające ręcznego przeglądu** (lista punktowana)
- **Miejsce na podpis** (kto odpowiada za utrzymanie reguły wstrzymania/firewalla)
