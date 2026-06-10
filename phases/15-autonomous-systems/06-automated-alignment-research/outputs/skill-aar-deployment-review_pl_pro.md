---

name: aar-deployment-review
description: Przegląd przed wdrożeniem potoku zautomatyzowanych badań nad dopasowaniem (AAR), w tym izolacja piaskownicy i nienaruszalność logów.
version: 1.0.0
phase: 15
lesson: 6
tags: [aar, alignment-research, sandbox, log-integrity, rsp]

---

Biorąc pod uwagę proponowane wdrożenie zautomatyzowanych badań nad dopasowaniem AI (model, konfiguracja piaskownicy, kolejka zadań, baza danych forum), przygotuj audyt przedwdrożeniowy, pod którym podpisałby się zespół ds. bezpieczeństwa wiodącego laboratorium (frontier lab).

Wyprodukuj:

1. **Izolacja piaskownicy (sandbox).** Zweryfikuj ograniczenia systemu plików, sieci oraz procesów dla każdej instancji agenta AAR. Upewnij się, że żaden agent nie może odczytywać ani modyfikować środowiska innego AAR. Potwierdź, że żaden agent AAR nie ma bezpośredniego prawa zapisu do bazy danych forum (wszystkie posty muszą przechodzić przez zewnętrzną, odizolowaną usługę pośredniczącą).
2. **Nienaruszalność logów forum.** Forum musi działać w trybie tylko do zapisu/dołączania (append-only) i być odporne na manipulacje (tamper-proof). Określ technologię przechowywania danych (np. S3 z blokadą Object Lock, niezmienna księga/immutable ledger, plik WAL z prawem wyłącznie do dołączania). Zdefiniuj częstotliwość automatycznych weryfikacji spójności logów oraz protokół reakcji w przypadku wykrycia prób sabotażu.
3. **Zasady przydzielania zadań.** Określ reguły kolejkowania zadań: kto je tworzy, kto zatwierdza, czy agenci AAR mogą samodzielnie generować zadania uzupełniające i na jakich warunkach. Pamiętaj, że swobodna dekompozycja zadań podnosi wydajność systemu, podczas gdy sztywny przepływ pracy ułatwia audytowanie. Dokładnie udokumentuj ten kompromis.
4. **Bramka weryfikacji przez człowieka (Human review gate).** Zanim jakikolwiek wynik wygenerowany przez AAR wpłynie na rzeczywiste kierunki badań, dane treningowe lub publikacje naukowe, wyznaczony ekspert-człowiek musi wydać formalną zgodę. Zdefiniuj listę kontrolną weryfikacji: powtarzalność eksperymentów, kompletność logów systemowych, zgodność wyciąganych wniosków z zebranymi danymi.
5. **Monitorowanie progów bezpieczeństwa.** Śledź wskaźniki sugerujące, że system AAR zbliża się do progów określonych w RSP v3.0 AI R&D-4: gwałtowny wzrost złożoności zadań, autonomiczne tworzenie nowych podzadań, transfer wiedzy między odrębnymi problemami. Zdefiniuj limity wartości, których przekroczenie wymaga natychmiastowego wdrożenia zaostrzonych procedur kontrolnych.

Kryteria bezwzględnego odrzucenia:
- Brak mechanizmu zapisu logów poza środowiskiem piaskownicy (out-of-sandbox logging).
- Bezpośrednie wdrażanie wyników AAR do baz treningowych lub produkcyjnych konfiguracji bez wcześniejszej manualnej weryfikacji i akceptacji.
- Uprawnienia pojedynczego agenta AAR pozwalające na jednoczesną modyfikację wielu systemów podrzędnych.

Zasady odmowy:
- Jeśli izolacja piaskownicy nie została precyzyjnie zdefiniowana lub opiera się na pojedynczej warstwie zabezpieczeń (np. wyłącznie Docker bez seccomp/gVisor), odmów wdrożenia i zażądaj głębokiej obrony systemowej (defense-in-depth).
- Jeśli jakikolwiek użytkownik (w tym administrator/operator) posiada uprawnienia do edycji lub usuwania istniejących wpisów w logach, odmów i zażądaj nośnika typu WORM (write once, read many).
- Jeśli celem wdrożenia jest automatyzacja potoku rozwoju ogólnych zdolności modeli (capabilities), a nie wyłącznie badań nad bezpieczeństwem/dopasowaniem (alignment), odmów i skieruj sprawę do pilnego przeglądu pod kątem polityki RSP.

Format wyjściowy:

Zwróć notatkę z audytu zawierającą:
- **Podsumowanie potoku** (jeden akapit)
- **Ocena poziomu izolacji** (dla każdego wymiaru: system plików, sieć, procesy, izolacja między agentami)
- **Ocena nienaruszalności logów** (wraz z planem weryfikacji ich spójności)
- **Decyzja o sposobie przydziału zadań** (sztywny / swobodny / hybrydowy wraz z uzasadnieniem)
- **Bramka weryfikacji manualnej** (nazwisko recenzenta, lista kontrolna)
- **Wskaźniki monitorowania progów** (lista sygnałów, limity, procedury reakcji)
- **Werdykt dotyczący wdrożenia** (uruchom / wstrzymaj / blokuj - go / hold / no-go)
