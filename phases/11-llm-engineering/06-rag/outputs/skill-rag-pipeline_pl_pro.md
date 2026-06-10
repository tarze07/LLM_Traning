---

name: skill-rag-pipeline
description: Twórz i debuguj potoki RAG w oparciu o podstawowe zasady architektoniczne.
version: 1.0.0
phase: 11
lesson: 6
tags: [rag, retrieval, embeddings, vector-search, llm-engineering]

---

# Wzorzec potoku RAG

Każdy system RAG realizuje następujący schemat przepływu danych:

```
documents -> chunk -> embed -> store
query -> embed -> search(top_k) -> build_prompt -> generate
```

Proces indeksowania (indexing) odbywa się raz dla każdego dokumentu. Proces wyszukiwania (querying) wykonuje się dla każdego nowego zapytania użytkownika.

## Kiedy stosować RAG

- Model LLM potrzebuje dostępu do danych prywatnych lub stale aktualizowanych (np. najnowszych informacji).
- Dostrajanie (fine-tuning) jest zbyt kosztowne obliczeniowo lub zbyt wolne w procesie wdrażania zmian.
- Odpowiedzi modelu muszą być weryfikowalne i zawierać odsyłacze do źródeł (cytaty).
- Wewnętrzna baza wiedzy często ulega modyfikacji.

## Kiedy NIE stosować RAG

- Oczekiwana odpowiedź bazuje na wiedzy ogólnej, którą model LLM posiada już w swoich wagach.
- Zadanie ma charakter kreatywny (np. burza mózgów, pisanie opowiadań), a nie czysto faktograficzny.
- Wymagane jest, aby model przyjął specyficzny styl pisania lub unikalny schemat wnioskowania (wtedy zastosuj fine-tuning).

## Lista kontrolna wdrożenia

1. Podziel dokumenty źródłowe na segmenty (chunks) o wielkości 256–512 tokenów z nakładaniem się (overlap) wynoszącym 50 tokenów.
2. Wygeneruj wektor (embedding) dla każdego segmentu przy użyciu spójnego modelu osadzeń.
3. Zapisz wygenerowane wektory w bazie wektorowej wraz z przypisanym do nich oryginalnym tekstem źródłowym.
4. W momencie wyszukiwania wygeneruj wektor dla zapytania użytkownika za pomocą tego samego modelu.
5. Pobierz top-k (zazwyczaj 5–10) najbardziej podobnych segmentów na podstawie podobieństwa cosinusowego.
6. Zbuduj ostateczny prompt: instrukcja systemowa + pobrany kontekst źródłowy + właściwe zapytanie użytkownika.
7. Wygeneruj odpowiedź modelu, nakazując ścisłe opieranie się na dostarczonym kontekście.
8. Zwróć użytkownikowi odpowiedź wraz z odnośnikami do segmentów źródłowych (cytowania).

## Typowe błędy

- Używanie różnych modeli embeddingów do indeksowania oraz wyszukiwania (wektory należą do innych przestrzeni i są ze sobą niekompatybilne).
- Zbyt małe segmenty (utrata kontekstu) lub zbyt duże segmenty (rozmycie semantyczne).
- Brak nakładania się segmentów (ryzyko przecięcia zdań i utraty sensu na granicach podziału).
- Pomijanie procedury reindeksacji po modyfikacji dokumentów źródłowych.
- Zwracanie użytkownikowi surowych segmentów tekstu bez syntezy spójnej odpowiedzi przez LLM.
- Ustawianie temperatury > 0 dla zapytań czysto faktograficznych (wyższa temperatura znacznie zwiększa ryzyko halucynacji).

## Debugowanie wyszukiwania (Retrieval)

Jeśli system nie pobiera właściwych segmentów tekstowych:
1. Zweryfikuj, czy wygenerowany wektor zapytania nie składa się z samych zer.
2. Ręcznie oblicz i sprawdź podobieństwo cosinusowe dla dokumentu, który na pewno powinien pasować do zapytania.
3. Przetestuj przeformułowanie zapytania użytkownika, dopasowując je do terminologii użytej w dokumentach źródłowych.
4. Upewnij się, że ten sam model embeddingów został użyty przy indeksowaniu oraz przy wyszukiwaniu.
5. Sprawdź, czy kluczowe informacje nie zostały ucięte lub nienaturalnie rozdzielone na etapie podziału tekstu na segmenty.

## Parametry produkcyjne

- **Rozmiar segmentu**: 256–512 tokenów.
- **Nakładanie się segmentów (overlap)**: 50 tokenów (ok. 10–20% rozmiaru segmentu).
- **Wartość Top-K**: 5–10 dla większości zastosowań biznesowych.
- **Temperatura**: 0 dla odpowiedzi opartych wyłącznie na faktach.
- **Model embeddingów**: `text-embedding-3-small` (optymalny kosztowo) lub `text-embedding-3-large` (maksymalna precyzja).
