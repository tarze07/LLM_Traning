---

name: skill-llm-evaluation
description: Schemat decyzyjny dotyczący wyboru właściwej strategii ewaluacji modeli LLM w oparciu o rodzaj zadania, budżet i wymagania
version: 1.0.0
phase: 10
lesson: 10
tags: [evaluation, evals, benchmarks, llm-as-judge, elo, metrics]

---

# Strategia oceny LLM

Oceniając system oparty na LLM, kieruj się poniższym schematem decyzyjnym, aby wybrać odpowiednie podejście.

## Kiedy używać każdego typu eval

**Benchmarki (np. MMLU, HumanEval, SWE-bench):** Przydatne przy wstępnej selekcji modeli. Gdy musisz zawęzić wybór z 10 potencjalnych modeli do 3, benchmarki dają szybki i darmowy pogląd na ich ogólne zdolności. Nie traktuj ich jednak jako ostatecznej oceny wdrożeniowej.

**Dedykowane zestawy ewaluacyjne (custom evals):** Niezbędne przy wdrażaniu systemu na produkcję. Każde specyficzne zadanie niesie ze sobą unikalne tryby błędów (failure modes). Dedykowane testy to jedyny sposób na rzetelne przewidzenie zachowania modelu w rzeczywistych warunkach. Przygotuj minimum 50 przypadków testowych dla prototypu oraz ponad 200 dla wersji produkcyjnej.

**LLM-as-a-judge:** Najlepsze do zadań o charakterze otwartym (np. podsumowania, kreatywne pisanie, konwersacje). Metryki oparte na dokładnym dopasowaniu tekstu lub nakładaniu się tokenów są w tych przypadkach zbyt restrykcyjne. LLM-as-a-judge kosztuje ok. 0,01 USD za pojedynczą ocenę, a jego zgodność z ocenami ludzi wynosi ok. 80%. Zawsze stosuj precyzyjne kryteria oceniania (rubrics), unikaj niejasnych promptów.

**Ocena przez ludzi (human evaluation):** Stosuj, gdy stawka jest wysoka, a automatyczne wskaźniki okazują się niewiarygodne. Ocena człowieka stanowi ostateczny punkt odniesienia (ground truth), jednak jej koszt wynosi od 0,10 USD do 2,00 USD za przypadek. Zarezerwuj ją for skomplikowanych, niejednoznacznych przypadków oraz do okresowej kalibracji metryk automatycznych.

**Wskaźnik ELO (na podstawie porównań parami):** Stosowany do porównywania ze sobą wielu modeli realizujących to samo zadanie. Ewaluacja parami (pairwise evaluation) jest znacznie bardziej wiarygodna niż bezwzględna punktacja, ponieważ zarówno ludzie, jak i modele w roli sędziów (LLM-as-a-judge) znacznie lepiej radzą sobie z ocenianiem względnym.

## Wybór metryk oceny (scorers)

- **Dokładne dopasowanie (Exact Match)**: klasyfikacja, ekstrakcja danych/encji, dane strukturyzowane z jedną poprawną odpowiedzią
- **F1-score na poziomie tokenów**: zadania ekstrakcji, w których kluczowa jest poprawność częściowa
- **ROUGE-L**: streszczenia (podsumowania), tłumaczenia
- **BLEU**: tłumaczenie maszynowe
- **LLM-as-a-judge**: generowanie tekstów otwartych, ocena jakości konwersacji, ogólna użyteczność
- **Ewaluacja uruchomieniowa (execution-based)**: generowanie kodu (uruchomienie wygenerowanego kodu i weryfikacja wyników testów jednostkowych)
- **Zgodność ze schematem (Schema validation)**: generowanie danych strukturyzowanych (weryfikacja poprawności formatu JSON/XML względem zadanego schematu)

## Sygnały ostrzegawcze (czerwone flagi) w procesie ewaluacji

- Zbiór ewaluacyjny mniejszy niż 50 przypadków: wyniki są statystycznie nieistotne.
- Brak przypadków skrajnych (edge cases): mierzysz wydajność jedynie dla standardowej ścieżki (happy path), która jest zawsze znacznie wyższa niż w warunkach produkcyjnych.
- Opieranie się na jednej metryce: różne metryki mogą pokazywać skrajnie odmienne wyniki – zawsze stosuj co najmniej dwie niezależne oceny.
- Brak wersjonowania: śledzenie postępu i regresji modeli jest niemożliwe bez wersjonowania zestawów testowych.
- Wyciek danych (evaluation leakage): pod żadnym pozorem nie dołączaj przykładów testowych do zbioru treningowego (fine-tuning) ani do few-shot promptów.
- Testowanie tylko jednego modelu: do rzetelnej oceny zawsze potrzebujesz punktu odniesienia (baseline – np. poprzednia wersja modelu lub prosta heurystyka).

## Lista kontrolna procesu ewaluacji

1. Precyzyjnie zdefiniuj zadanie (np. zamiast ogólnego „odpowiadaj na zapytania”, zdefiniuj: „klasyfikuj zgłoszenia klientów do 5 kategorii”).
2. Stwórz zrównoważony zbiór testowy zawierający ścieżkę standardową (happy path), przypadki skrajne (edge cases) oraz dawne błędy (regresje).
3. Wybierz 2-3 metryki oceny (scorers) dopasowane do specyfiki zadania.
4. Zdefiniuj progi zaliczenia (Pass/Fail) w oparciu o kryteria biznesowe i wymagania produkcyjne.
5. Zautomatyzuj wykonanie: jedno polecenie uruchamia cały pakiet testowy.
6. Wersjonuj wszystkie elementy: przypadki testowe, metryki, prompty i wersje modeli.
7. Uruchamiaj testy przy każdej zmianie kodu, modyfikacji promptu lub aktualizacji modelu.
8. Śledź trendy: pojedynczy wynik pomiaru może być szumem, dopiero linia trendu z wielu prób daje jasny sygnał.
9. Cyklicznie (np. co kwartał) kalibruj automatyczne oceny z opiniami ludzkich adnotatorów.
10. Dodawaj nowe przypadki do bazy testów regresyjnych natychmiast po wykryciu każdego błędu na produkcji.
