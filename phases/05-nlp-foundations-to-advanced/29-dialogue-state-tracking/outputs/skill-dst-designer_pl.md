---

name: dst-designer
description: Zaprojektuj narzędzie do śledzenia stanu dialogu — schemat, ekstraktor, polityka aktualizacji, ocena.
version: 1.0.0
phase: 5
lesson: 29
tags: [nlp, dialogue, task-oriented]

---

Biorąc pod uwagę przypadek użycia (dziedzina, języki, otwartość słownictwa, wymagania dotyczące zgodności), wynik:

1. Schemat. Lista domen, miejsca na domenę, słownictwo otwarte i zamknięte na miejsce.
2. Ekstraktor. Oparte na regułach / seq2seq / LLM-with-Pydantic. Powód.
3. Aktualizuj politykę. Regeneruj-cały stan / przyrostowo; obsługa korekt; obsługa negacji.
4. Ocena. Dokładność wspólnego celu w przypadku długich dialogów, precyzja/przypomnienie na poziomie automatu, zamieszanie w najtrudniejszym slocie.
5. Przepływ potwierdzenia. Kiedy wyraźnie poprosić użytkownika o potwierdzenie (działania destrukcyjne, ekstrakcja o niskim poziomie zaufania).

Odrzuć czas letni tylko dla LLM w przypadku przedziałów wrażliwych na zgodność bez dodatkowej kontroli opartej na regułach. Odrzuć każdy czas letni, który nie może cofnąć czasu po korekcie użytkownika. Oznacz schematy bez znaczników wersji.