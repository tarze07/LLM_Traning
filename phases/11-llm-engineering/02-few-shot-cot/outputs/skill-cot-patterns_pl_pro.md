---

name: skill-cot-patterns
description: Ramy decyzyjne umożliwiające wybór właściwej techniki rozumowania w oparciu o złożoność zadania, wymagania dotyczące dokładności i ograniczenia kosztowe
version: 1.0.0
phase: 11
lesson: 02
tags: [chain-of-thought, few-shot, self-consistency, tree-of-thought, react, reasoning, prompting]

---

# Przewodnik po wyborze techniki rozumowania

Jeżeli potrzebujesz, aby LLM przeanalizował problem przed udzieleniem odpowiedzi, wybierz odpowiednią technikę przed przygotowaniem promptu. Technika definiuje architekturę wnioskowania, a prompt ją uzupełnia.

## Szybkie drzewo decyzyjne

1. Czy zadanie polega na prostym wyszukiwaniu faktów czy na jednoetapowej klasyfikacji?
   - Tak: użyj metody **zero-shot**. CoT zwiększa koszty (liczbę tokenów) bez poprawy dokładności.
   - Nie: przejdź do kroku 2.

2. Czy zadanie wymaga wieloetapowego rozumowania (matematyka, logika, planowanie)?
   - Tak: użyj techniki **Chain-of-Thought (CoT)**. Przejdź do kroku 3.
   - Nie: użyj metody **few-shot** (kilku przykładów), jeśli format danych wyjściowych ma znaczenie, lub **zero-shot**, jeśli nie ma znaczenia.

3. Czy dopuszczalny jest pojedynczy błąd w rozumowaniu w drodze do wyniku?
   - Tak: użyj **few-shot CoT** (pojedyncza ścieżka wnioskowania, temperatura 0.0).
   - Nie: użyj metody **self-consistency** (N=5, temperatura 0.7). Przejdź do kroku 4.

4. Czy problem polega na przeszukiwaniu przestrzeni stanów lub planowaniu z wieloma możliwymi ścieżkami?
   - Tak: użyj techniki **Tree-of-Thought (ToT)**.
   - Nie: wystarczy zastosowanie metody self-consistency.

5. Czy zadanie wymaga zewnętrznych informacji lub wykonywania obliczeń?
   - Tak: użyj wzorca **ReAct** (wnioskowanie + wywoływanie narzędzi).
   - Nie: wystarczą czyste techniki wnioskowania.

## Matryca technik

| Technika | Wzrost dokładności | Mnożnik kosztów | Opóźnienie (Latency) | Najlepsze dla |
|----------|--------------------|-----------------|----------------------|---------------|
| Zero-shot | Linia bazowa | 1x | ~1s | Proste zadania, faktograficzne Q&A |
| Few-shot | +5-15% | 1.2x | ~1s | Dopasowanie formatu, klasyfikacja |
| Zero-shot CoT | +10-20% | 1.3x | ~1.5s | Szybka poprawa zdolności rozumowania |
| Few-shot CoT | +15-25% | 1.5x | ~2s | Matematyka, logika, wnioskowanie wieloetapowe |
| Self-consistency (N=5) | +2-5% ponad CoT | 5x | ~5s | Krytyczne procesy wnioskowania |
| Self-consistency (N=10) | +1-2% w stosunku do N=5 | 10x | ~10s | Decyzje o krytycznym znaczeniu |
| Tree-of-Thought (ToT) | Zależny od zadania | 10-40x | ~30s+ | Przeszukiwanie, planowanie, zagadki logiczne |
| ReAct | Zależny od zadania | 3-10x | ~5-15s | Zadania oparte na wiedzy zewnętrznej i integracji narzędzi |
| Prompt chaining | +5-10% w stosunku do pojedynczego | 2-5x | ~5-10s | Złożone, wieloetapowe zadania |

## Wskazówki dla konkretnych modeli

### GPT-4o / GPT-4.1
- Silne bazowe zdolności rozumowania. Często wystarcza zero-shot CoT.
- Few-shot CoT z 3 przykładami osiąga 95% skuteczności w benchmarku GSM8K.
- Metoda self-consistency daje marginalne korzyści (poprawa z 95% do 97%) – warto ją stosować tylko w zadaniach o krytycznym znaczeniu.
- Natywnie obsługuje ustrukturyzowane formaty danych wyjściowych (Structured Outputs) w celu ekstrakcji odpowiedzi.

### Claude 3.5 Sonnet / Claude 3.7 Sonnet
- Doskonale radzi sobie ze śledzeniem ustrukturyzowanych formatów w promptach (tagi XML).
- Najlepiej sprawdza się few-shot CoT z przykładami wydzielonymi za pomocą tagów XML.
- Tryb rozszerzonego myślenia (Claude 3.7 Extended Thinking) to natywna funkcja CoT – nie ma potrzeby wymuszania jej w prompcie.
- Metoda self-consistency jest skuteczna, ponieważ ścieżki wnioskowania Claude'a wykazują dużą różnorodność przy temperaturze 0.7.

### Llama 3.1/3.3 70B
- Największe korzyści przynosi few-shot CoT (znaczna poprawa dokładności w porównaniu do zero-shot).
- Zaleca się stosowanie self-consistency z N=5 w zadaniach wymagających wnioskowania.
- Wymaga bardziej precyzyjnych instrukcji dotyczących formatowania niż modele komercyjne.
- ToT jest kosztowne przy lokalnym wnioskowaniu (local inference) – warto je rozważyć tylko przy przetwarzaniu wsadowym (batch processing).

### Gemini 2.5 Pro
- Doskonałe wyniki w wieloetapowym rozumowaniu bez dodatkowej optymalizacji (out-of-the-box).
- Tryb myślenia (thinking mode) zapewnia wbudowane CoT bez potrzeby zaawansowanego prompt engineeringu.
- Krótkie przykłady few-shot bardziej pomagają w utrzymaniu spójności formatu niż w poprawie dokładności.
- Szerokie okno kontekstowe (1M tokenów) sprawia, że stosowanie wielu przykładów (few-shot) jest wysoce praktyczne.

## Antywzorce

**CoT dla prostych zadań**: dodawanie instrukcji typu „Pomyślmy krok po kroku” do prostych pytań (np. „Ile to jest 2+2?”) marnuje tokeny. Model wykonuje prostą arytmetykę bezpośrednio. CoT przynosi realne korzyści dopiero przy zadaniach wymagających co najmniej 3 kroków.

**Self-consistency przy temperaturze 0.0**: wszystkie generowane próbki N będą identyczne. Aby uzyskać zróżnicowane ścieżki rozumowania, należy ustawić temperaturę > 0 (zalecany zakres to 0.5–0.8).

**ToT do każdego zadania**: Tree-of-Thought wymaga wywołań LLM rzędu O(b^d), gdzie b to współczynnik rozgałęzienia (branching factor), a d to głębokość drzewa (depth). Drzewo o parametrach b=3, d=3 generuje aż do 39 wywołań API. Tę technikę należy rezerwować wyłącznie dla problemów, przy których tańsze metody zawodzą.

**Błędne przykłady few-shot**: podawanie przykładów zawierających błędy w rozumowaniu uczy model powielania tych błędów. Każdy przykład w prompcie musi być zweryfikowany. Pojedynczy błędny przykład może obniżyć dokładność bardziej niż całkowity brak przykładów (zero-shot).

**Ekstrakcja odpowiedzi bez spójnego formatu**: self-consistency wymaga porównywania odpowiedzi z różnych prób (majority voting). Jeśli formaty odpowiedzi się różnią (np. „18 USD”, „$18”, „osiemnaście”), algorytm votingowy nie zadziała. Zawsze wymuszaj jednolity format, np.: „Ostateczna odpowiedź to: [liczba]”.

## Optymalizacja kosztów

Dla systemu produkcyjnego obsługującego 10 000 zapytań dziennie przy cenniku GPT-4o (wejście: 2.50 USD / 1M tokenów, wyjście: 10.00 USD / 1M tokenów):

| Technika | Średnia liczba tokenów na zapytanie | Koszt dzienny | Dokładność |
|----------|-------------------------------------|---------------|------------|
| Zero-shot | ~200 | ~5 USD | 78% |
| Few-shot CoT | ~600 | ~15 USD | 95% |
| Self-consistency (N=5) | ~3000 | ~75 USD | 97% |
| ToT (b=3, d=2) | ~6000 | ~150 USD | Zależna od zadania |

Optymalna pod kątem kosztów strategia dla większości zastosowań: zacznij od few-shot CoT. Dodaj self-consistency tylko dla zapytań o niskim poziomie pewności modelu (wzorzec eskalacji z sekcji Compile).

## Integracja z łańcuchami promptów (Prompt Chaining)

Techniki wnioskowania można łączyć w ramach prompt chainingu:

**Krok 1 łańcucha** (ekstrakcja): zero-shot, temperatura 0.0
**Krok 2 łańcucha** (wnioskowanie): few-shot CoT, temperatura 0.0
**Krok 3 łańcucha** (weryfikacja): self-consistency przy N=3, temperatura 0.7

Taki trzyetapowy łańcuch kosztuje ok. 3-krotnie więcej niż pojedyncze wywołanie CoT, ale pozwala wykryć błędy ekstrakcji oraz błędy w rozumowaniu, a także dostarcza wskaźnik pewności (confidence score) na etapie weryfikacji.

## Kiedy wyjść poza prompt engineering

Jeśli spędzasz więcej czasu na projektowaniu promptów niż na pisaniu kodu aplikacji, rozważ następujące rozwiązania:

1. **Fine-tuning (dostrajanie)**: jeśli dysponujesz ponad 500 etykietowanymi przykładami, a zadanie ma wąski zakres.
2. **Kompilacja za pomocą DSPy**: jeśli potrzebujesz zautomatyzowanej optymalizacji promptów.
3. **Frameworki agentowe**: jeśli zadanie wymaga wieloetapowej interakcji z narzędziami (multi-turn tool usage, faza 14).
4. **RAG**: jeśli model wymaga dostępu do prywatnych lub dynamicznie aktualizowanych baz wiedzy (lekcje 06-07).

Techniki promptowania stanowią fundament. Działają z dowolnym modelem i dostawcą oraz nie wymagają danych treningowych, mają jednak swoje ograniczenia. Wiedza o tym, kiedy przejść na kolejny poziom zaawansowania, jest równie ważna jak opanowanie samych technik projektowania promptów.
