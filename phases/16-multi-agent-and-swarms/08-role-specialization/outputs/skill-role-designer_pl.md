---

name: role-designer
description: Utwórz listę ról dla systemu wieloagentowego, wymieniając planistę/wykonawcę/krytyka/weryfikatora dla danego zadania z jawnymi schematami we/wy.
version: 1.0.0
phase: 16
lesson: 08
tags: [multi-agent, role-specialization, metagpt, chatdev, verification]

---

Biorąc pod uwagę zadanie, utwórz wyspecjalizowaną listę ról ze schematami we/wy i deterministycznym weryfikatorem. Gotowy do mapowania na CrewAI, LangGraph, AutoGen lub niestandardowych pętlach.

Wyprodukuj:

1. **Wykaz ról.** 3–5 ról. Nazwij każdego. Minimum: planista, wykonawca, weryfikator. Krytyk opcjonalny.
2. **Schemat we/wy na rolę.** Dla każdej roli: co zużywa (z roli nadrzędnej) i co produkuje (schemat, nie proza). Użyj notacji w stylu klasy danych.
3. **Specyfikacja weryfikatora.** Nazwij kontrolę deterministyczną: zestaw testów, sprawdzanie typu, walidator schematu, linter. Opisać kryteria pozytywnego/niezaliczonego.
4. **Specyfikacja krytyka (opcjonalnie).** Jeśli jest uwzględniona, podaj, jaką subiektywną jakość ocenia. Konkretna lista kontrolna, a nie „dobry kod”.
5. **Zasady komunikacyjnej dehalucynacji.** Wymień pytania, które każda rola na niższym szczeblu łańcucha może wysłać w górę rzeki, gdy brakuje jakiegoś szczegółu, aby ich nie wymyślała.
6. **Budżet pętli rewizyjnej.** Maksymalna liczba rund przed eskalacją do człowieka. Domyślny 2.
7. **Mapowanie ramowe.** Po jednej linijce: jak wyrazić ten skład w CrewAI, LangGraph, AutoGen.

Twarde odrzucenia:

- Dowolny skład bez deterministycznego weryfikatora. Składy wszystkich LLM nie przechodzą kontroli MAST.
- Fuzzy I/O („executor zwraca wyjście”). Zawsze podawaj schemat.
- Połączenie krytyka i weryfikatora. Łapią różne robaki; oba muszą istnieć, jeśli oba są uzasadnione.

Zasady odmowy:

- Jeśli zadanie nie posiada deterministycznej kontroli poprawności (czysta praca generatywna, twórcze pisanie), odmów i zamiast tego zarekomenduj pętlę recenzenta lub debatę wieloagentową (lekcja 07).
- Jeżeli zadanie jest za małe na 3+ role (poniżej 10 minut pracy człowieka), odmów i polecam jednego agenta.

Wynik: jednostronicowy brief dotyczący projektowania ról. Zakończ sprawdzeniem luk w awariach MAST: potwierdź, że istnieje co najmniej jeden deterministyczny weryfikator.