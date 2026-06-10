---

name: issue-to-pr
description: Zbuduj asynchronicznego agenta ds. zgłoszeń do PR w GitHub, który działa w piaskownicy w chmurze, odtwarza kompilację, weryfikuje testy i otwiera PR gotowe do przeglądu w ramach ścisłych budżetów na repo.
version: 1.0.0
phase: 19
lesson: 16
tags: [capstone, async-agent, github, fargate, daytona, swe-bench, budget, safety]

---

Mając repozytorium GitHub ze zgłoszeniami oznaczonymi jako `@agent fix this`, możesz dostarczyć hostowanego na własnym serwerze agenta w chmurze, który zamieni każdy oznaczony problem w gotowy do przeglądu raport PR z określonym zakresem danych uwierzytelniających i ograniczonymi kosztami.

Plan budowy:

1. Aplikacja GitHub z precyzyjnym tokenem: problemy rw, zapisywanie PR, zawartość rw, odczytywanie przepływów pracy. Żadnego pchania na siłę. Ochrona gałęzi na głównej uniemożliwia bezpośrednie zapisy.
2. Odbiornik webhooka (Lambda lub Fly.io) filtruje zdarzenia związane z etykietami/komentarzami PR i kolejkuje do SQS.
3. Dyspozytor egzekwuje maksymalne dzienne limity $ i liczby PR w przeliczeniu na repo; uruchamia zadanie ECS Fargate na każde dozwolone zadanie.
4. Wnioskowanie o środowisku: wykryj język + menedżer pakietów + środowisko wykonawcze na podstawie zawartości repozytorium. Syntezuj plik Dockerfile na bieżąco, jeśli go nie ma.
5. Piaskownica Daytona lub E2B na zadanie. Sklonuj repozytorium do świeżej gałęzi agenta `git worktree` +.
6. Pętla agenta (mini-swe-agent lub SWE-agent v2 na Claude Opus 4.7 lub GPT-5.4-Codex). Narzędzia: ripgrep, mapa repozytorium drzewa, plik_odczytu, plik_edycji, testy_run, git. Czapki: 20 $, 30 tur, 30 min.
7. Zweryfikuj: pełny CI w piaskownicy; delta zasięgu przez jacoco / zasięg.py; etykieta `needs-review`, jeśli delta < -2%; zatrzymaj, jeśli CI czerwony.
8. PR otwarty poprzez API GitHub z uzasadnieniem, podsumowaniem różnic, adresem URL śledzenia, kosztem, zwrotami.
9. Obserwowalność: ślad Langfuse’a na PR; kłoda szoruje w poszukiwaniu tajemnic; Panel budżetu na repo.
10. Ocena 30 rozstawionych kwestii wewnętrznych; porównaj z agentami w tle kursora i zdalnymi agentami AWS SWE w współdzielonym podzbiorze trzech problemów.

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | Zdawalność w 30 wydaniach | Kompleksowy sukces (CI zielony + zasięg OK) |
| 20 | Jakość PR | Rozmiar różnicy, delta pokrycia, zgodność ze stylem |
| 20 | Koszt i opóźnienie na rozwiązany problem | $/PR i zegar ścienny/PR |
| 20 | Bezpieczeństwo | Token o określonym zakresie, budżet na repo, brak wymuszania, higiena poświadczeń |
| 15 | UX operatora | Komentarze uzasadniające, możliwość ponownej próby, śledzenie @wzmianek |

Twarde odrzucenia:

- Każdy agent, który może wymusić pchnięcie. Twarde wykluczenie.
- Dyspozytorzy, którzy pomijają kontrolę budżetu. Niekontrolowane pętle to klasyczna porażka.
- PR zostały otwarte bez przejścia pełnego CI w piaskownicy.
- Śledź archiwa zawierające niezredagowane tokeny lub informacje umożliwiające identyfikację.

Zasady odmowy:

- Odmów instalacji bez zabezpieczenia gałęzi na głównej.
- Odmawiaj działania bez dziennego budżetu na repo (liczą się dolary i PR).
- Automatycznie odmawiaj ponawiania nieudanych prób; wszystkie ponowne próby wymagają ponownego nałożenia etykiety przez człowieka.

Dane wyjściowe: repozytorium zawierające aplikację GitHub, odbiornik webhooka, dyspozytor + księga budżetowa, definicja zadania Fargate, menedżer cyklu życia piaskownicy, pętla mini-swe-agent, przebieg ewaluacji 30 problemów, bezpośrednie porównanie z agentami tła kursora i zdalnymi agentami SWE AWS oraz zapis wymieniający trzy główne błędy wnioskowania kompilacji i zmianę syntezy pliku Dockerfile, która zmniejszyła każdy z nich.