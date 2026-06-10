---

name: reviewer-agent
description: Wypełnij rolę agenta recenzenta dzięki pięciowymiarowej rubryce, która odczytuje artefakty konstruktora, tworzy ustrukturyzowany raport z recenzji i rozpoczyna recenzję ręcznie od zapisanej strony, a nie pustej.
version: 1.0.0
phase: 14
lesson: 39
tags: [reviewer, rubric, role-separation, second-loop, review-report]

---

Biorąc pod uwagę, że agent konstruktora już produkuje artefakty środowiska warsztatowego, postaw recenzenta, który je czyta i pisze ustrukturyzowane raporty.

Wyprodukuj:

1. `agents/reviewer.md` z monitem systemu recenzenta: dostęp tylko do odczytu, rubryka pięciowymiarowa, dla każdego wyniku należy podać ścieżkę artefaktu.
2. `tools/reviewer.py`, który ładuje `ReviewerInputs` ze stołu warsztatowego i uruchamia narzędzie punktacji LLM dla każdego wymiaru.
3. `outputs/review/<task_id>.json` jako ścieżka raportu z przeglądu kanonicznego.
4. `docs/reviewer-rubric.md` zawierający listę pięciu wymiarów, pytania, na które każdy z nich odpowiada, oraz opisy kotwic 0-1-2.
5. Krok CI, który publikuje raport z przeglądu jako komentarz PR po każdym zamknięciu zadania konstruktora.

Twarde odrzucenia:

- Recenzent z dostępem do zapisu w pliku różnicowym. Przepaść między twórcą a recenzentem jest całym sygnałem; zawalenie się niszczy niezawodność.
- Rubryka bez opisów kotwic na partyturę. „Wynik od 0 do 2” bez kotwic sprowadza się do wibracji.
- Przejrzyj raporty, które pomijają cytaty. Każdy wynik musi wskazywać plik lub wpis śledzenia.
- Udostępnianie monitu systemowego konstruktora. Ten sam model jest w porządku; ten sam monit nie jest.

Zasady odmowy:

- Jeśli konstruktor nie przedstawi raportu z weryfikacji, odmów uruchomienia recenzenta. Zanim warto będzie prosić o osąd, musi nastąpić akceptacja.
- Jeśli projekt ma mniej niż trzy zamknięte zadania, odmów twierdzenia, że ​​rubryka jest skalibrowana. Zapisz pierwsze raporty jako zestaw kalibracyjny.
- Jeśli recenzent zostanie poproszony o ocenę poniżej minimalnego poziomu ufności, odmów i ujawnij człowiekowi niepewny wymiar.

Struktura wyjściowa:

```
<repo>/
├── agents/reviewer.md
├── tools/reviewer.py
├── outputs/review/
│   └── <task_id>.json
├── docs/reviewer-rubric.md
└── .github/workflows/review.yml
```

Zakończ słowami „co przeczytać dalej”, wskazując:

- Lekcja 40 dotycząca pakietu przekazania, który łączy weryfikację + przegląd.
- Lekcja 41 dotycząca zadania w stylu rzeczywistym, które ćwiczy separację konstruktora od recenzenta od końca do końca.
- Lekcja 05 (Samodoskonalenie i KRYTYK) dla podstawy samooceny pojedynczego agenta, na której udoskonala się ta lekcja.