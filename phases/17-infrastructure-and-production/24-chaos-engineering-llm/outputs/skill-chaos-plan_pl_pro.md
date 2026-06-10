---

name: chaos-plan
description: Zaprojektuj plan inżynierii chaosu dla LLM – zweryfikuj warunki wstępne, zaprojektuj cztery warstwy architektury, wybierz odpowiednie narzędzie, określ trzy bezpieczne eksperymenty początkowe oraz wdroż zabezpieczenia warstwy bezpieczeństwa.
version: 1.0.0
phase: 17
lesson: 24
tags: [chaos-engineering, litmuschaos, chaosmesh, harness, llm-chaos, game-day]

---

Na podstawie stosu technologicznego (Kubernetes / maszyny wirtualne / usługi zarządzane), stopnia dojrzałości SLI/SLO, poziomu obserwowalności oraz dojrzałości zespołu dyżurnego (on-call), przygotuj plan testów chaosu.

Wygeneruj:

1. Weryfikacja warunków wstępnych: Sprawdź obecność zdefiniowanych SLI/SLO, zintegrowanego monitoringu (obserwowalności), automatycznego wycofywania zmian (rollbacks), ustrukturyzowanych procedur runbook oraz aktywnych dyżurów (on-call). Jeśli brakuje któregokolwiek elementu, zablokuj wdrażanie chaosu na produkcji.
2. Cztery warstwy architektury: Wskaż narzędzia i mechanizmy dla każdej z warstw (kontrolnej, docelowej, bezpieczeństwa, obserwowalności). Odnieś się do Lekcji 13 z Fazy 17 w obszarze obserwowalności.
3. Trzy eksperymenty początkowe: Rozpocznij od usunięcia kontenera (pod crash), następnie zasymuluj błędy 429 dostawcy API, a na koniec przeciążenie pamięci. Każdy test musi mieć określony limit promienia wybuchu, czas trwania oraz kryteria sukcesu.
4. Wyłączniki bezpieczeństwa: Tempo zużycia budżetu błędów (burn rate > 2x normy), limit promienia wybuchu (< 30% floty/instancji), tagowanie za pomocą Trace ID oraz okna wyciszania alertów (suppression windows).
5. Harmonogram: Cotygodniowe małe testy typu canary. Miesięczny dzień ćwiczeń (Game Day) z udziałem wielu zespołów. Kwartalny audyt odporności systemów.
6. Narzędzia: LitmusChaos (OSS, projekt CNCF graduated), Chaos Mesh (OSS, projekt CNCF sandbox), Harness Chaos (rozwiązanie komercyjne ze wsparciem AI), AWS FIS / Azure Chaos Studio (dedykowane usługi chmurowe).

Kryteria odrzucenia planu (Hard rejects):
- Uruchamianie testów chaosu na produkcji bez spełnienia 5 warunków wstępnych: Odrzuć plan – eksperyment przerodzi się w rzeczywistą awarię.
- Eksperymenty bez zdefiniowanego limitu promienia wybuchu: Odrzuć.
- Eksperymenty bez tagowania identyfikatorami Trace ID: Odrzuć – brak możliwości powiązania i deduplikacji alertów.

Zasady odrzucenia:
- Jeśli zespół nie przeprowadził pomyślnie ani jednego testu w środowisku stagingowym, zablokuj testy na produkcji do momentu uzyskania pozytywnego wyniku na stagingu.
- Jeśli liczba incydentów jest już wysoka (> 2 tygodniowo), odrzuć plan – dodawanie testów chaosu pogłębi problemy operacyjne; najpierw należy ustabilizować system.
- Jeśli zespół nie posiada zdefiniowanych celów SLO, wymagaj ich opracowania przed uruchomieniem jakichkichkolwiek testów.

Wynik: Jednostronicowy plan zawierający weryfikację warunków wstępnych, dobór narzędzi dla czterech warstw architektury, trzy eksperymenty początkowe, progi zabezpieczające oraz harmonogram testów. Na końcu dodaj zobowiązanie do kwartalnej aktualizacji mapy zależności.
