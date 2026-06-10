---

name: dst-designer
description: Zaprojektuj system śledzenia stanu dialogu (DST) – schemat, moduł ekstrakcji, politykę aktualizacji i plan ewaluacji.
version: 1.0.0
phase: 5
lesson: 29
tags: [nlp, dialogue, task-oriented]

---

Na podstawie przypadku użycia (dziedzina, języki, otwartość słownika, wymagania dotyczące zgodności/compliance) wygeneruj:

1. Schemat: lista domen, sloty (atrybuty) przypisane do danej domeny, słownik otwarty lub zamknięty dla każdego slotu.
2. Ekstraktor: podejście oparte na regułach, model seq2seq lub LLM z walidacją Pydantic. Podaj uzasadnienie.
3. Polityka aktualizacji: generowanie pełnego stanu od nowa lub aktualizacja przyrostowa; obsługa korekt użytkownika; obsługa negacji.
4. Ewaluacja: dokładność wspólnego celu (Joint Goal Accuracy) dla długich dialogów, precyzja (precision) i czułość (recall) na poziomie slotów, analiza błędów dla najtrudniejszego slotu.
5. Przepływ potwierdzeń: zdefiniowanie sytuacji, w których należy jawnie poprosić użytkownika o potwierdzenie (np. działania destrukcyjne, ekstrakcja o niskim poziomie pewności/zaufania).

Odrzuć system DST oparty wyłącznie na LLM w przypadku slotów wrażliwych pod kątem zgodności (compliance) bez dodatkowej weryfikacji opartej na regułach. Odrzuć każdy system DST, który nie potrafi wycofać zmiany lub skorygować stanu po poprawce wniesionej przez użytkownika. Oznacz jako błąd schematy, które nie posiadają przypisanego numeru wersji.
