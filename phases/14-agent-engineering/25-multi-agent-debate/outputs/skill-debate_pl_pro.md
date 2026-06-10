---

name: debate
description: Szablon debaty wieloagentowej z N uczestnikami, R rundami, konfigurowalną topologią komunikacji (pełna siatka, gwiazda, pierścień) oraz regułą konsensusu.
version: 1.0.0
phase: 14
lesson: 25
tags: [debate, multi-agent, society-of-minds, sparse-topology]

---

Biorąc pod uwagę klasę pytań oraz założony cel dokładności, przygotuj protokół debaty.

Zakres wdrożenia:

1. Klasa `Debater` z różnymi promptami (oraz opcjonalnie różnymi modelami LLM), aby uniknąć homogenizacji odpowiedzi.
2. Mechanizm komunikacji (rundy): topologia z pełną siatką (full mesh), gwiazdą (star/hub-and-spoke) lub pierścieniem (ring).
3. Reguła konsensusu (zbieżności): głosowanie większościowe ważone wskaźnikiem pewności lub większość kwalifikowana z opcją rezerwową (fallback).
4. Wymuszona rozbieżność opinii w 1. rundzie: każdy uczestnik debaty, o ile to możliwe, powinien przedstawić odmienną propozycję.
5. Analiza kosztów: całkowita liczba procesów krytyki oraz prognozowane zużycie tokenów na zapytanie.

Kryteria odrzucenia (Hard Rejects):

- Wszyscy uczestnicy debaty korzystają z tego samego promptu oraz z tego samego modelu LLM. Gwarantuje to zjawisko myślenia grupowego.
- Zastosowanie pełnej siatki przy liczbie uczestników N >= 6 bez wcześniejszej analizy kosztów. Złożoność operacji debaty wynosi O(N*R) lub nawet O(N^2 * R).
- Brak jasnej reguły zbieżności. Zwrócenie odpowiedzi pierwszego uczestnika z R-tej rundy nie jest faktycznym konsensusem.

Zasady odmowy (Refusal Rules):

- Jeśli system wymaga niskich opóźnień (budżet czasu < 1 s), odrzuć protokół debaty. Zamiast tego zastosuj metodę autokrytyki (lekcja 05) lub równoległe głosowanie (sekwencyjna orkiestracja, lekcja 12).
- Jeśli zapytania dotyczą prostego wyszukiwania faktów (np. nazwa stolicy, data wydarzenia, definicja), odrzuć debatę. Wyszukiwanie informacji (RAG) + weryfikacja CRITIC (lekcja 05) są znacznie tańsze.
- Jeśli w testach ewaluacyjnych po pierwszej rundzie uczestnicy debaty nie wykazują żadnych różnic zdań, odrzuć protokół. Konieczna jest większa różnorodność modeli lub promptów.

Dane wyjściowe: Pliki `debater.py`, `topology.py`, `convergence.py`, `runner.py`, `README.md` wyjaśniające dobór parametrów N i R, uzasadnienie wybranej topologii oraz analizę stosunku kosztów do dokładności w zestawie testowym. Zakończ sekcją „Co przeczytać dalej”, kierując do lekcji 12 (Wzorce przepływu pracy) w przypadku prostszych zadań lub do lekcji 28 (Wzorce orkiestracji) w celu wbudowania debaty w większy system.
