---

name: mt-evaluator
description: Oceń wynik tłumaczenia maszynowego do wysyłki.
version: 1.0.0
phase: 5
lesson: 11
tags: [nlp, translation, evaluation]

---

Biorąc pod uwagę tekst źródłowy i potencjalne tłumaczenie, wynik:

1. Automatyczne oszacowanie wyniku. Zakresy BLEU i chrF, których można się spodziewać. Podaj, czy dostępne jest odniesienie.
2. Pięciopunktowa lista kontrolna możliwa do sprawdzenia przez człowieka: zachowanie treści (bez halucynacji), poprawny język docelowy, zgodność rejestru/formalności, spójność terminologii ze słownikiem, jeśli jest dostępny, bez obcinania lub eksplozji długości.
3. Jeden problem specyficzny dla domeny do zbadania. Informacje prawne: wymienione podmioty, cytaty z ustaw. Medycyna: nazwy leków, dawkowanie. Interfejs użytkownika: zmienne zastępcze, takie jak `{name}`.
4. Flaga zaufania. „Wyślij” / „Wyślij z recenzją” / „Nie wysyłaj”. Powiąż z wagą znalezionych problemów.

Odmów wysyłki bez sprawdzenia identyfikatora języka na wyjściu. Odmów oceny bez referencji, chyba że użytkownik wyraźnie zgodzi się na scoring bez referencji (COMET-QE, BLEURT-QE). Oznacz dowolną treść powyżej 1000 tokenów jako prawdopodobnie wymagającą fragmentarycznego tłumaczenia.