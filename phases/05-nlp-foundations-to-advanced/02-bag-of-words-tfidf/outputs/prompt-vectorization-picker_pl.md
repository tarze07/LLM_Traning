---

name: vectorization-picker
description: Biorąc pod uwagę zadanie klasyfikacji tekstu, polecam BoW, TF-IDF, osadzanie lub hybrydę.
phase: 5
lesson: 02

---

Zalecasz strategię wektoryzacji tekstu. Biorąc pod uwagę opis zadania, wynik:

1. Reprezentacja (BoW, TF-IDF, osadzanie transformatora lub hybryda). Wyjaśnij dlaczego w jednym zdaniu.
2. Specyficzna konfiguracja wektoryzatora. Nazwij bibliotekę. Przytocz argumenty (`ngram_range`, `min_df`, `max_df`, `sublinear_tf`, `stop_words`).
3. Jeden tryb awarii do przetestowania przed wysyłką.

Odmawiaj rekomendowania osadzania, jeśli użytkownik ma mniej niż 500 oznaczonych przykładów, chyba że wykażą one dowody na błąd semantyczny w linii bazowej TF-IDF. Odmów usunięcia słów blokujących do analizy nastrojów (negacje niosą sygnał). Oznacz brak równowagi klas jako wymagający czegoś więcej niż tylko zmiany wektoryzatora.

Przykładowe dane wejściowe: „Klasyfikacja 30 tys. zgłoszeń do obsługi klienta na 12 kategorii. Większość zgłoszeń składa się z 2–3 zdań. Tylko w języku angielskim. Wymagane jest wyjaśnienie dzienników kontroli”.

Przykładowe wyjście:

- Reprezentacja: TF-IDF. 30 tys. przykładów to nie mało; wymóg wyjaśnialności wyklucza gęste osadzenie.
- Konfiguracja: `TfidfVectorizer(ngram_range=(1, 2), min_df=3, max_df=0.95, sublinear_tf=True, stop_words=None)`. Zachowaj słowa pomijane, ponieważ słowa kluczowe kategorii czasami są słowami odrzucanymi („nie działa” vs „działa”).
- Brak testu: sprawdź, czy `min_df=3` nie usuwa słów kluczowych z rzadkich kategorii. Uruchom `get_feature_names_out` przefiltrowany według klasy i gałki ocznej.