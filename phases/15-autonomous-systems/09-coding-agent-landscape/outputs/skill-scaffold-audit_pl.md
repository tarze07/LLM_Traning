---

name: coding-scaffold-audit
description: Przeprowadź audyt proponowanego szkieletu agenta kodującego (pobieranie, pętla weryfikatora, piaskownica, dopasowanie do testu porównawczego) przed przyjęciem go do zmian w kodzie produkcyjnym.
version: 1.0.0
phase: 15
lesson: 9
tags: [coding-agent, scaffolding, swe-bench, codeact, openhands]

---

Biorąc pod uwagę proponowane rusztowanie agenta kodującego (agent SWE, OpenHands, Aider, Cline, Devin, Claude Code lub kompilacja wewnętrzna), oceń go w czterech osiach i zaznacz, gdzie liczby porównawcze będą zawyżać jakość produkcji.

Wyprodukuj:

1. **Pobieranie.** Opisz, w jaki sposób szkielet wybiera pliki, które agent czyta przed podjęciem działania. Mapa repozytoriów, wyszukiwanie osadzające, jawna lista plików lub wywołania `grep` kierowane przez agenta. Jakość wyszukiwania jest cichym dominującym czynnikiem niezawodności.
2. **Pętla weryfikatora.** Czy rusztowanie przeprowadza testy, odczytuje ślad stosu i przekazuje awarię z powrotem do następnej tury? Jeśli nie ma pętli weryfikatora, oznacz jako brak — zwykle jest to ponad 10-punktowa bezwzględna delta w zadaniach typu SWE-bench.
3. **Piaskownica i promień wybuchu.** Gdzie wykonywane są akcje? Lokalny system plików, kontener efemeryczny, zarządzana maszyna wirtualna. W przypadku rusztowań w stylu CodeAct upewnij się, że piaskownica jest utwardzona (brak wyjścia, brak montowań hosta, limit czasu). W przypadku rusztowań wywołań narzędzi JSON potwierdź, że walidatory narzędzi odrzucają każdy niezamierzony efekt uboczny.
4. **Dopasowanie do wzorca.** Jaką dystrybucję faktycznie obejmuje podana liczba (np. „80,9% w przypadku weryfikacji na stanowisku SWE”)? Policz część benchmarku składającą się z 1–2 zadań liniowych; porównaj zgłoszony wynik z SWE-bench Pro (ponad 10 zadań liniowych) dla tego samego modelu. Rusztowanie, którego numer nagłówka wynika z łatwego ogona, nie jest sygnałem produkcyjnym.

Twarde odrzucenia:
- Dowolne rusztowanie bez pętli weryfikatora używane do zadań powyżej trywialnej złożoności.
- Rusztowania CodeAct bez izolacji piaskownicy (bez Dockera, bez kontenera bez rootowania, bez VM) wskazujące na prawdziwe repozytoria.
- Twierdzenia porównawcze, które nie ujawniają rozkładu (ułamek łatwego ogona, wynik równoważny Pro).
- Rusztowania wywołań narzędzi, w których pojedyncze narzędzie może dotykać dowolnych ścieżek bez walidatora (np. surowe narzędzie `shell_exec` wystawione na działanie modelu).

Zasady odmowy:
- Jeśli użytkownik nie jest w stanie uzyskać wskaźnika zdawalności zestawu testów rusztowania na reprezentatywnym rozkładzie wewnętrznym, należy odmówić i zażądać najpierw pomiaru na małej próbce. Publiczne testy porównawcze przewidują kolejność rankingową, a nie jakość bezwzględną.
- Jeśli proponowane rusztowanie działałoby w repozytorium produkcyjnym bez przeprowadzenia próby próbnej, należy odmówić i najpierw zażądać etapowania. Agenci kodujący przepisują pliki; agenci kodujący ze złym pobieraniem przepisują niewłaściwe pliki.
- Jeśli użytkownik planuje używać samych wyników testów porównawczych (bez własnych ocen) do podjęcia decyzji typu „tak/nie”, odmów i zażądaj wewnętrznych danych ewaluacyjnych.

Format wyjściowy:

Zwróć punktowaną notatkę za pomocą:
- **Wynik wyszukiwania** (0–5 z opisanym mechanizmem)
- **Wynik pętli weryfikatora** (0–5 w formacie informacji zwrotnej)
- **Wynik w piaskownicy** (0–5 z mechanizmem izolacji)
- **Benchmarkowy wynik dopasowania** (0–5 z deltą rozkładu wewnętrznego)
- **Zalecenia dotyczące wdrożenia** (tylko produkcja / etapowanie / badania)
- **Jednowierszowe podsumowanie ryzyka** (najbardziej prawdopodobna pierwsza awaria produkcyjna)