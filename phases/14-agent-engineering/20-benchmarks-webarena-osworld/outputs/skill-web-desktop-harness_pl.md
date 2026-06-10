---

name: web-desktop-harness
description: Zbuduj uprząż w stylu WebArena/OSWorld z oceną opartą na wykonaniu i metrykami efektywności trajektorii.
version: 1.0.0
phase: 14
lesson: 20
tags: [webarena, osworld, harness, trajectory-efficiency]

---

Biorąc pod uwagę aplikację docelową (internetową lub komputerową) i listę zadań ze złotymi trajektoriami, zbuduj uprząż eval.

Wyprodukuj:

1. Definicje zadań: `(tid, description, gold_steps, success_predicate, state_reset)`.
2. Biegacz: uruchamia agenta, rejestruje każdą akcję, rejestruje liczbę kroków + czas, który upłynął + stan powodzenia.
3. Wskaźnik efektywności trajektorii: `agent_steps / gold_steps`. Raportuj według zadania i zbiorczo.
4. Resetowanie stanu pomiędzy zadaniami — nigdy nie uruchamiaj jednego zadania w stanie zanieczyszczonym przez inne.
5. Klasyfikator trybu awarii: dla każdej awarii oznacz, czy jest to błąd uziemienia (zły element), czy błąd planowania (złe działanie).

Twarde odrzucenia:

- Brak resetowania stanu pomiędzy zadaniami. Zanieczyszczenie między zadaniami unieważnia wszystkie wyniki.
- Raportowanie wyłącznie na temat wskaźnika sukcesu. Wydajność trajektorii to standard na rok 2026.
- Uprząż zawierająca tylko zrzuty ekranu, bez parzystości DOM. Niektórzy agenci korzystają z DOM+wizji; podaj oba, chyba że specjalnie ograniczasz powierzchnię.

Zasady odmowy:

- Jeśli zadania nie mają złotych trajektorii, odmów. Bez nich nie można zmierzyć efektywności.
- Jeśli aplikacja nie jest przypięta do konkretnej wersji, odmów. Dryft unieważnia porównania krzyżowe.
- Jeśli agent ma destrukcyjne narzędzia (usuwanie, publikowanie), wymagaj kopii aplikacji w piaskownicy.

Dane wyjściowe: `tasks.py`, `runner.py`, `failure_classifier.py`, `report.py`, `README.md` wyjaśniające politykę resetowania, pozyskiwanie złotej trajektorii oraz podział na uziemienie i planowanie. Zakończ słowami „Co dalej czytać”, wskazując Lekcję 21 (modele korzystania z komputera) lub Lekcję 30 (programowanie oparte na ewaluacji).