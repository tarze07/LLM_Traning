---

name: ner-picker
description: Wybierz odpowiednie podejście NER dla danego zadania ekstrakcji.
version: 1.0.0
phase: 5
lesson: 06
tags: [nlp, ner, extraction]

---

Biorąc pod uwagę opis zadania (domena, zestaw etykiet, język, opóźnienie, ilość danych), wynik:

1. Podejście. Oparte na regułach + gazeter, CRF, BiLSTM-CRF lub dostrajanie transformatora.
2. Model początkowy. Nazwij to (identyfikator modelu spaCy, taki jak `en_core_web_sm` / `en_core_web_trf`, identyfikator punktu kontrolnego Hugging Face, taki jak `dslim/bert-base-NER` lub „niestandardowy, przeszkolony od podstaw”).
3. Strategia etykietowania. BIO, BILOU lub oparte na rozpiętościach. Uzasadnij jednym zdaniem.
4. Ocena. Użyj `seqeval`. Zawsze zgłaszaj F1 na poziomie jednostki, nigdy na poziomie tokena.

Odmów zalecania dostrajania transformatora dla mniej niż 500 oznaczonych przykładów, chyba że użytkownik ma już wstępnie wyszkolony model domeny (np. BioBERT dla medycyny). Oznacz zagnieżdżone elementy jako wymagające modeli opartych na rozpiętościach lub modeli wieloprzebiegowych. Wymagaj audytu gazetera, jeśli użytkownik wspomni o „skali produkcji” podczas korzystania z gotowych etykiet CoNLL-2003.