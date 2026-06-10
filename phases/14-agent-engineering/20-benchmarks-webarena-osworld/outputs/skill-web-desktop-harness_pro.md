---

name: web-desktop-harness
description: Zbuduj środowisko testowe w stylu WebArena/OSWorld z oceną opartą na stanie wykonania oraz metrykami efektywności trajektorii.
version: 1.0.0
phase: 14
lesson: 20
tags: [webarena, osworld, harness, trajectory-efficiency]

---

Na podstawie aplikacji docelowej (webowej lub desktopowej) oraz listy zadań wraz z optymalnymi ścieżkami ich wykonania (złotymi trajektoriami), zbuduj środowisko ewaluacyjne (eval harness).

Wyprodukuj:

1. Definicje zadań zawierające: identyfikator (`tid`), opis, optymalną liczbę kroków (`gold_steps`), warunek sukcesu (`success_predicate`) oraz procedurę resetowania stanu (`state_reset`).
2. Moduł uruchomieniowy (runner): uruchamia agenta, rejestruje każdą podjętą akcję, a także zlicza kroki, czas wykonania oraz sprawdza status powodzenia.
3. Wskaźnik efektywności trajektorii obliczany jako: `agent_steps / gold_steps` (raportowany dla każdego zadania z osobna oraz zbiorczo).
4. Resetowanie stanu środowiska między zadaniami – niedopuszczalne jest uruchamianie testu w stanie zmodyfikowanym przez poprzednie zadanie.
5. Klasyfikator przyczyn błędów (failure classifier): dla każdego niepowodzenia oznacza, czy przyczyną był błąd uziemienia (złe pozycjonowanie/wybór elementu), czy błąd planowania (błędna logika działania).

Kategoryczne odrzucenia (Twarde kryteria):

- Brak procedury pełnego resetowania stanu między zadaniami. Przenoszenie stanu (zanieczyszczenie) między testami unieważnia wszelkie wyniki.
- Raportowanie wyłącznie ogólnego wskaźnika sukcesu. Standardem jest mierzenie i raportowanie efektywności trajektorii.
- Projektowanie środowiska wyłącznie w oparciu o zrzuty ekranu, bez dostępu do drzewa DOM. Niektóre systemy korzystają z kombinacji DOM i analizy obrazu; udostępnij oba te źródła, o ile celowo nie ograniczasz założeń testowych.

Zasady odmowy wykonania usługi (Refusal rules):

- Jeśli zadania nie posiadają zdefiniowanych złotych trajektorii, odmów. Bez wzorca odniesienia określenie efektywności ścieżki jest niemożliwe.
- Jeśli wersje aplikacji testowych nie są ściśle zdefiniowane i zablokowane, odmów. Jakiekolwiek samoczynne zmiany w środowisku uniemożliwiają rzetelne porównywanie wyników.
- Jeśli agent dysponuje destrukcyjnymi narzędziami (np. usuwanie danych, publikowanie treści), bezwzględnie wymagaj uruchomienia testów na izolowanej kopii aplikacji (w piaskownicy).

Pliki wynikowe: `tasks.py`, `runner.py`, `failure_classifier.py`, `report.py`, `README.md` opisujące politykę resetowania stanu, sposób definiowania złotych trajektorii oraz logikę podziału błędów na uziemienie i planowanie. Zakończ sekcją „Dalsza lektura”, wskazując na Lekcję 21 (modele korzystające z komputera - Computer Use) lub Lekcję 30 (rozwój oparty na ewaluacjach - Evaluation-driven development).
