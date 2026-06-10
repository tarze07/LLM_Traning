---

name: summary-picker
description: Wybierz podejście ekstrakcyjne lub abstrakcyjne, wskaż odpowiednią bibliotekę i dodaj weryfikację faktów.
version: 1.0.0
phase: 5
lesson: 12
tags: [nlp, summarization]

---

Na podstawie opisu zadania (typ dokumentu, wymagania dotyczące zgodności, oczekiwana długość, budżet obliczeniowy) wygeneruj:

1. Rekomendowane podejście: ekstrakcyjne lub abstrakcyjne. Wyjaśnij powód wyboru w jednym zdaniu.
2. Implementację modelu/biblioteki: podaj nazwę konkretnego rozwiązania (np. `sumy.TextRankSummarizer`, `facebook/bart-large-cnn`, `google/pegasus-pubmed` lub odpowiedni prompt dla LLM).
3. Plan ewaluacji: metryki ROUGE-1, ROUGE-2, ROUGE-L (użyj biblioteki `rouge-score` z włączonym stemowaniem). W przypadku podejścia abstrakcyjnego dodaj weryfikację zgodności faktów (fact-checking).
4. Jeden krytyczny scenariusz błędu do zweryfikowania. W abstrakcyjnych podsumowaniach wiadomości najczęstszym błędem jest mylenie lub zamiana podmiotów (np. osób, organizacji, wartości liczbowych); oznacz próbki, w których kluczowe jednostki z tekstu źródłowego nie pojawiają się w podsumowaniu.

Odmawiaj generowania abstrakcyjnych podsumowań dla tekstów medycznych, prawnych, finansowych lub objętych ścisłymi regulacjami bez zastosowania mechanizmu weryfikacji faktów (fact-checking gate). Jeśli tekst wejściowy przekracza okno kontekstowe modelu, oznacz go jako wymagający podsumowania metodą map-reduce (fragmentarycznego), zamiast zwykłego ucięcia tekstu.
