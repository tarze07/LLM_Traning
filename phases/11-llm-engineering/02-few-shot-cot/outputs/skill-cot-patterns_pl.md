---

name: skill-cot-patterns
description: Ramy decyzyjne umożliwiające wybór właściwej techniki rozumowania w oparciu o złożoność zadania, wymagania dotyczące dokładności i ograniczenia kosztowe
version: 1.0.0
phase: 11
lesson: 02
tags: [chain-of-thought, few-shot, self-consistency, tree-of-thought, react, reasoning, prompting]

---

# Przewodnik po wyborze techniki rozumowania

Jeśli potrzebujesz LLM, aby przemyśleć problem, wybierz technikę przed napisaniem podpowiedzi. Technika określa architekturę rozumowania. Monit wypełnia go.

## Szybkie drzewo decyzyjne

1. Czy zadanie polega na prostym przeglądzie faktów czy na jednoetapowej klasyfikacji?
   - Tak: użyj **zero-shot**. CoT zwiększa koszty bez zwiększenia dokładności.
   - Nie: kontynuuj.

2. Czy zadanie wymaga wieloetapowego rozumowania (matematyka, logika, planowanie)?
   - Tak: użyj **Łańcucha Myśli**. Przejdź do kroku 3.
   - Nie: użyj **kilku zdjęć**, jeśli format ma znaczenie, lub zera, jeśli nie.

3. Czy dopuszczalny jest pojedynczy błąd w rozumowaniu?
   - Tak: użyj **kilkukrotnego CoT** (pojedyncza próbka, temperatura 0,0).
   - Nie: użyj **samospójności** (N=5, temperatura 0,7). Przejdź do kroku 4.

4. Czy problem dotyczy poszukiwania/planowania z wieloma możliwymi ścieżkami?
   - Tak: użyj **Drzewa Myśli**.
   - Nie: wystarczy samokonsekwentność.

5. Czy zadanie wymaga zewnętrznych informacji lub obliczeń?
   - Tak: użyj **ReAct** (rozumowanie + wywołania narzędzi).
   - Nie: wystarczą techniki czystego rozumowania.

## Matryca technik

| Technika | Podnoszenie dokładności | Mnożnik kosztów | Opóźnienie | Najlepsze dla |
|----------|--------------|--------------------------------|---------|--------------|
| Zerowy strzał | Linia bazowa | 1x | ~1s | Proste zadania, merytoryczne pytania i odpowiedzi |
| Kilka strzałów | +5-15% | 1,2x | ~1s | Dopasowanie formatu, klasyfikacja |
| Zero-shot CoT | +10-20% | 1,3x | ~1,5 s | Szybkie wzmocnienie rozumowania |
| CoT z kilkoma strzałami | +15-25% | 1,5x | ~2s | Matematyka, logika, wieloetapowa |
| Samokonsekwencja (N=5) | +2-5% ponad CoT | 5x | ~5 s | Rozumowanie o wysokiej stawce |
| Samokonsekwencja (N=10) | +1-2% w stosunku do N=5 | 10x | ~10 s | Tylko decyzje krytyczne |
| Drzewo Myśli | Zależne od zadania | 10-40x | ~30+ | Szukaj, planowanie, puzzle |
| Reaguj | Zależne od zadania | 3-10x | ~5-15 s | Zadania oparte na wiedzy |
| Szybkie łączenie | +5-10% w stosunku do pojedynczego | 2-5x | ~5-10 s | Złożone zadania wieloczęściowe |

## Wskazówki dotyczące konkretnego modelu

### GPT-4o / GPT-4.1
- Mocne uzasadnienie bazowe. Często wystarczający jest CoT z zerowym strzałem.
- Kilka strzałów CoT z 3 przykładami osiąga 95% w GSM8K.
- Spójność daje marginalne korzyści (95% do 97%) - warto tylko w przypadku zadań krytycznych.
- Natywnie obsługuje ustrukturyzowane wyniki w celu wyodrębnienia odpowiedzi.

### Sonet Claude'a 3,5 / Sonet Claude'a 3,7
- Doskonale radzi sobie z następującymi ustrukturyzowanymi formatami podpowiedzi (tagi XML).
- Najlepiej sprawdza się CoT z kilkoma strzałami z przykładami rozdzielanymi w formacie XML.
- Myślenie rozszerzone (Claude 3.7) to natywna CoT - nie ma potrzeby o to pytać.
- Własna spójność jest skuteczna, ponieważ rozumowanie Claude'a różni się znacznie w temperaturze 0,7.

### Lama 3.1/3.3 70B
- Największe korzyści daje CoT z kilkoma strzałami (większa luka w celności w porównaniu do strzału zerowego).
- Wzajemna spójność z N=5 zalecana do zadań związanych z rozumowaniem.
- Wymaga bardziej wyraźnych instrukcji dotyczących formatu niż modele komercyjne.
- ToT jest kosztowne w przypadku wnioskowania lokalnego - należy rozważyć tylko w przypadku przetwarzania wsadowego.

### Gemini 2.5 Pro
- Mocny w wieloetapowym rozumowaniu od razu po wyjęciu z pudełka.
- Tryb myślenia zapewnia wbudowaną CoT bez konieczności szybkiego projektowania.
- Kilka krótkich przykładów pomaga bardziej w zachowaniu spójności formatu niż dokładności.
- Duże okno kontekstowe (1M) sprawia, że ​​kilka strzałów jest praktycznych.

## Anty-wzorce

**CoT dla prostych zadań**: pytanie „Co to jest 2+2? Pomyślmy krok po kroku” marnuje żetony. Model wykonuje prostą arytmetykę bez śladów rozumowania. CoT pomaga, gdy są co najmniej 3 kroki.

**Samospójność w temperaturze 0,0**: wszystkie N próbek będzie identycznych. Aby uzyskać różnorodne ścieżki rozumowania, należy zastosować temperaturę > 0 (zalecane 0,5–0,8).

**ToT do wszystkiego**: ToT wymaga wywołań O(b^d) LLM, gdzie b=współczynnik rozgałęzienia i d=głębokość. Drzewo z b=3, d=3 potrzebuje do 39 wywołań. Zarezerwuj na problemy tam, gdzie zawodzą tańsze techniki.

**Niewiele złych przykładów**: przykłady z błędami w rozumowaniu uczą model popełniania tych błędów. Każdy przykład trzeba zweryfikować. Jeden zły przykład może zmniejszyć dokładność o więcej niż zero przykładów.

**Wyodrębnianie odpowiedzi bez spójnego formatu**: spójność wymaga porównywania odpowiedzi w różnych próbach. Jeśli format odpowiedzi jest różny („18 dolarów”, „18 dolarów”, „osiemnaście”), głosowanie kończy się niepowodzeniem. Zawsze wymuszaj: „Odpowiedź to [liczba]”.

## Optymalizacja kosztów

Dla systemu produkcyjnego obsługującego 10 000 zapytań dziennie w cenie GPT-4o (wyjście $2.50/1M input, $10/1M):

| Technika | Średnia liczba tokenów/zapytanie | Dzienny koszt | Dokładność |
|----------|-----------------|------------|--------------|
| Zerowy strzał | ~200 | ~5 dolarów | 78% |
| CoT z kilkoma strzałami | ~600 | ~15 dolarów | 95% |
| Samokonsekwencja (N=5) | ~3000 | ~75 dolarów | 97% |
| ToT (b=3, d=2) | ~6000 | ~150 dolarów | Zależne od zadania |

Optymalna kosztowo strategia dla większości zastosowań: zacznij od kilkukrotnego CoT. Dodaj spójność własną tylko w przypadku zapytań, w których poziom pewności jest niski (wzorzec eskalacji z sekcji Kompiluj).

## Integracja z szybkim łańcuchem

Techniki rozumowania łączą się z szybkim łączeniem w łańcuchy:

**Etap łańcucha 1** (ekstrakt): strzał zerowy, temperatura 0,0
**Krok łańcucha 2** (Przyczyna): kilka strzałów CoT, temperatura 0,0
**Łańcuch Krok 3** (Sprawdź): samospójność przy N=3, temperatura 0,7

Ten trzyetapowy łańcuch kosztuje ~3 razy pojedyncze wywołanie CoT, ale wychwytuje błędy ekstrakcji, błędy w rozumowaniu i zapewnia poziom pewności na etapie weryfikacji.

## Kiedy wyjść poza monitowanie

Jeśli spędzasz więcej czasu na projektowaniu monitów niż na pisaniu kodu aplikacji, rozważ:

1. **Dostrajanie**: jeśli masz ponad 500 oznaczonych przykładów, a zadanie jest wąskie
2. **Kompilacja DSPy**: jeśli chcesz zautomatyzowanej optymalizacji
3. **Struktury agentowe**: jeśli zadanie wymaga użycia narzędzia wieloobrotowego (faza 14)
4. **RAG**: jeśli model potrzebuje dostępu do wiedzy prywatnej/aktualnej (lekcje 06-07)

Techniki podpowiadania są podstawą. Działają z dowolnym modelem, dowolnym dostawcą i nie wymagają żadnych danych szkoleniowych. Ale mają ograniczenia. Wiedza o tym, kiedy przejść na następny poziom, jest równie ważna, jak opanowanie samych technik.