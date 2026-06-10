---

name: summary-picker
description: Wybierz ekstraktywny lub abstrakcyjny, nazwij bibliotekę i dodaj weryfikację faktów.
version: 1.0.0
phase: 5
lesson: 12
tags: [nlp, summarization]

---

Biorąc pod uwagę zadanie (typ dokumentu, wymagania dotyczące zgodności, długość, budżet obliczeniowy), wynik:

1. Podejście. Ekstrakcyjne lub abstrakcyjne. Wyjaśnij w jednym zdaniu dlaczego.
2. Uruchomienie modelu/biblioteki. Nazwij to. `sumy.TextRankSummarizer`, `facebook/bart-large-cnn`, `google/pegasus-pubmed` lub monit LLM.
3. Plan ewaluacji. ROUGE-1, ROUGE-2, ROUGE-L (użyj `rouge-score` z łodygą). Plus sprawdzenie faktów, jeśli są abstrakcyjne.
4. Jeden tryb awarii do sprawdzenia. Zamiana jednostek jest najczęstsza w abstrakcyjnych podsumowaniach wiadomości; Oznacz próbki, w których elementy źródłowe nie pojawiają się w podsumowaniu.

Odmawiaj abstrakcyjnych podsumowań treści medycznych, prawnych, finansowych lub regulowanych bez bramki opartej na faktach. Oznacz dane wejściowe w oknie kontekstowym modelu jako wymagające fragmentarycznego podsumowania mapy, a nie tylko obcięcia.