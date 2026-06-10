---

name: mt-evaluator
description: Oceń jakość tłumaczenia maszynowego przeznaczonego do wysyłki.
version: 1.0.0
phase: 5
lesson: 11
tags: [nlp, translation, evaluation]

---

Na podstawie tekstu źródłowego i proponowanego tłumaczenia wygeneruj:

1. Automatyczną ocenę jakości. Podaj spodziewane przedziały wartości BLEU i chrF. Zaznacz, czy dostępne jest tłumaczenie referencyjne.
2. Pięciopunktową listę kontrolną do weryfikacji przez człowieka: wierność przekazu (brak halucynacji), poprawność języka docelowego, zgodność rejestru stylistyki i stopnia formalności, spójność terminologii ze słownikiem (jeśli jest dostępny) oraz brak ucięć lub nadmiernego rozrostu tekstu.
3. Jeden problem specyficzny dla danej domeny, który należy zbadać. Teksty prawne: wymienione podmioty, cytaty z ustaw. Medycyna: nazwy leków, dawkowanie. Interfejs użytkownika (UI): zmienne szablonowe, takie jak `{name}`.
4. Flagę rekomendacji (zaufania): „Wyślij” / „Wyślij po weryfikacji” / „Nie wysyłaj”. Powiąż ją z wagą wykrytych problemów.

Odmów zatwierdzenia wysyłki bez uprzedniego sprawdzenia identyfikatora języka na wyjściu. Odmów oceny bez tłumaczenia referencyjnego, chyba że użytkownik wyraźnie zgodzi się na ocenę bezreferencyjną (COMET-QE, BLEURT-QE). Oznacz każdy tekst przekraczający 1000 tokenów jako potencjalnie wymagający tłumaczenia fragmentami.
