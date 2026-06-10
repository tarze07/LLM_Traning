---

name: aar-deployment-review
description: Przegląd przed wdrożeniem potoku automatycznego badania dopasowania, w tym izolacja piaskownicy i integralność dzienników.
version: 1.0.0
phase: 15
lesson: 6
tags: [aar, alignment-research, sandbox, log-integrity, rsp]

---

Biorąc pod uwagę proponowane wdrożenie w ramach badań zautomatyzowanego dostosowania (model, piaskownica, kolejka zadań, forum), przygotuj przegląd przed wdrożeniem, pod którym podpisałby się zespół ds. bezpieczeństwa z laboratorium granicznego.

Wyprodukuj:

1. **Izolacja piaskownicy.** Sprawdź ograniczenia systemu plików, sieci i procesów dla każdej instancji AAR. Upewnij się, że żaden AAR nie może czytać ani modyfikować piaskownicy innego AAR. Upewnij się, że żaden AAR nie może dotrzeć bezpośrednio do punktu końcowego zapisu w magazynie forum (wszystkie posty przechodzą przez oddzielną usługę).
2. **Integralność logów forum.** Forum musi być przeznaczone wyłącznie do dodawania i zabezpieczone przed manipulacją. Określ magazyn (np. S3 z blokadą obiektu, niezmienną księgą, WAL z możliwością dołączenia). Określ częstotliwość weryfikacji i reakcję w przypadku wykrycia sabotażu.
3. **Polityka przydzielania zadań.** Określ sposób przydzielania zadań: kto je pisze, kto je zatwierdza, czy AAR mogą proponować własne zadania uzupełniające i na jakich warunkach. Swobodny rozkład wygrywa pod względem wydajności; zalecany przepływ pracy wygrywa pod względem audytowalności. Udokumentuj kompromis wyraźnie.
4. **Brama przeglądu przez człowieka.** Zanim jakikolwiek wynik AAR wpłynie na rzeczywisty kierunek badań, dane szkoleniowe lub opublikowaną pracę, wyznaczony recenzent musi się podpisać. Określ listę kontrolną przeglądu: powtarzalność eksperymentu, kompletność dziennika, mapowanie twierdzeń na dowody.
5. **Monitorowanie progów.** Śledź sygnały, że system AAR zbliża się do terytorium RSP v3.0 AI R&D-4: delta złożoności zadań, autonomiczne pojawianie się podzadań, transfer informacji między zadaniami. Zdefiniuj progi wymagające podwyższonego przeglądu.

Twarde odrzucenia:
- Dowolne wdrożenie AAR bez widocznych naruszeń dzienników spoza piaskownicy.
- Dowolny potok, w którym wyniki AAR są bezpośrednio wprowadzane do danych szkoleniowych lub polityki produkcyjnej bez nazwanego przeglądu ręcznego.
- Dowolny rurociąg, w przypadku którego pojedynczy AAR ma wystarczające uprawnienia, aby wpływać na wiele systemów dalszych.

Zasady odmowy:
- Jeśli izolacja piaskownicy jest nieokreślona lub opiera się na pojedynczej warstwie (tylko Docker, bez seccomp/gVisor), odmów i wymagaj dogłębnej obrony.
- Jeśli ktokolwiek (nawet operatorzy) może edytować zapis dziennika, należy odmówić i zażądać nośnika jednorazowego zapisu.
- Jeśli celem wdrożenia jest automatyzacja części rurociągu zdolności – a nie tylko badań nad dostosowaniem – odmów i eskaluj do przeglądu RSP.

Format wyjściowy:

Zwróć notatkę z recenzją zawierającą:
- **Podsumowanie rurociągu** (jeden akapit)
- **Wynik izolacji** (na wymiar: fs, netto, proc, peer)
- **Wynik integralności dziennika** (z planem weryfikacji)
- **Decyzja o przydziale zadań** (stała / bezpłatna / hybrydowa, z uzasadnieniem)
- **Brama przeglądu ręcznego** (nazwisko recenzenta, lista kontrolna)
- **Monitory progowe** (lista sygnałów, progów, reakcja)
- **Werdykt dotyczący wdrożenia** (włącz / wstrzymaj / nie idź)