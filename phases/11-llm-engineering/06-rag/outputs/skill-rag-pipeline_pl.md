---

name: skill-rag-pipeline
description: Twórz i debuguj rurociągi RAG w oparciu o podstawowe zasady
version: 1.0.0
phase: 11
lesson: 6
tags: [rag, retrieval, embeddings, vector-search, llm-engineering]

---

# Wzór rurociągu RAG

Każdy system RAG ma następujący wzór:

```
documents -> chunk -> embed -> store
query -> embed -> search(top_k) -> build_prompt -> generate
```

Indeksowanie odbywa się raz na dokument. Zapytanie odbywa się na każde żądanie użytkownika.

## Kiedy używać RAG

- LLM potrzebuje dostępu do dokumentów prywatnych lub najnowszych
- Dostrajanie jest zbyt kosztowne lub zbyt wolne, aby je zaktualizować
- Aby uzyskać odpowiedzi, należy podać źródła
- Baza wiedzy często się zmienia

## Kiedy NIE używać RAG

- Odpowiedzią jest ogólna wiedza, którą LLM już posiada
- Zadanie ma charakter kreatywny (pisanie, burza mózgów), a nie opiera się na faktach
- Potrzebujesz, aby model przyjął określony styl rozumowania (użyj dostrajania)

## Lista kontrolna wdrożenia

1. Podziel dokumenty na segmenty o długości 256–512 tokenów z nakładaniem się 50 tokenów
2. Osadź każdą porcję, korzystając ze spójnego modelu osadzania
3. Przechowuj osadzenia w bazie danych wektorowych z oryginalnym tekstem
4. W momencie zapytania osadź pytanie użytkownika z tym samym modelem
5. Pobierz top-k (5-10) najbardziej podobnych fragmentów poprzez podobieństwo cosinus
6. Zbuduj zachętę: instrukcja systemowa + pobrany kontekst + pytanie użytkownika
7. Wygeneruj odpowiedź, opierając ją na uzyskanym kontekście
8. Prześlij odpowiedź wraz z odnośnikami do źródeł

## Typowe błędy

- Używanie różnych modeli osadzania do indeksowania i wykonywania zapytań (wektory są niezgodne)
– Kawałki są zbyt małe (utrata kontekstu) lub zbyt duże (rozmycie trafności)
- Nie obejmuje nakładania się fragmentów (dzieli zdania na granicach)
- Zapominanie o ponownym indeksowaniu w przypadku zmiany dokumentów
- Zwracanie pobranych fragmentów użytkownikowi bez generowania spójnej odpowiedzi
- Nie ustawianie temperatury = 0 dla faktycznych zapytań RAG (wyższa temperatura = więcej halucynacji)

## Pobieranie debugowania

Jeśli nie są pobierane właściwe fragmenty:
1. Wydrukuj osadzenie zapytania i sprawdź, czy jest niezerowe
2. Sprawdź ręcznie podobieństwa cosinusów dla znanego, odpowiedniego fragmentu
3. Spróbuj przeformułować zapytanie tak, aby pasowało do słownictwa dokumentu
4. Sprawdź zgodność modelu osadzania pomiędzy indeksem a czasem zapytania
5. Sprawdź, czy odpowiednia treść nie została utracona podczas fragmentowania

## Parametry produkcyjne

- Rozmiar porcji: 256-512 tokenów
- Nakładanie się: 50 tokenów (10-20% wielkości porcji)
- Top-k: 5-10 w większości przypadków użycia
- Temperatura: 0 dla odpowiedzi rzeczowych
- Model osadzania: osadzanie tekstu-3-małe (opłacalne) lub osadzanie tekstu-3-dużego (wyższa dokładność)