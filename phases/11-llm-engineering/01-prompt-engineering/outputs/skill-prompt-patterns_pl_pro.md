---

name: skill-prompt-patterns
description: Ramy decyzyjne umożliwiające wybór odpowiedniego wzorca promptu w oparciu o typ zadania, wymagania dotyczące niezawodności i model docelowy.
version: 1.0.0
phase: 11
lesson: 01
tags: [prompt-engineering, patterns, llm, temperature, cross-model, few-shot, chain-of-thought]

---

# Przewodnik po wyborze wzorców promptów

Projektując funkcjonalności oparte na LLM, wybierz odpowiedni wzorzec (pattern) przed napisaniem samego promptu. Wzorzec określa strukturę, którą następnie wypełniasz konkretną treścią.

## Macierz decyzyjna wyboru wzorców

| Typ zadania | Wzorzec główny | Wzorzec pomocniczy | Temperatura | Wymaga few-shot? |
|--------------|----------------|--------------------------------|------------|----------------|
| Ekstrakcja danych | Szablonowanie | Few-shot | 0.0 | Tak (2-3 przykłady) |
| Klasyfikacja | Few-shot | Guardrail | 0.0 | Tak (3-5 przykładów) |
| Podsumowanie | Persona + Szablon | Dostosowanie do odbiorcy | 0.3 | Nie |
| Generowanie kodu | Persona | Chain of Thought (CoT) | 0.0 | Opcjonalnie |
| Pisanie kreatywne | Persona | Krytyka/Samokrytyka | 0.7-1.0 | Nie |
| Wnioskowanie wieloetapowe | Chain of Thought (CoT) | Dekompozycja | 0.3 | Opcjonalnie |
| Odpowiedzi na pytania | Persona + Guardrail | Granica (boundary) | 0.3 | Nie |
| Generowanie promptów | Meta-prompting | Krytyka/Samokrytyka | 0.7 | Tak (1-2 przykłady) |
| Moderacja treści | Guardrail + Granica | Few-shot | 0.0 | Tak (5+ przykładów) |
| Tłumaczenie / Adaptacja | Dostosowanie do odbiorcy | Few-shot | 0.3 | Tak (2-3 przykłady) |

## Kiedy stosować poszczególne wzorce

**Wzorzec Persona (Rola)**: Stosuj go jako punkt wyjściowy dla każdego promptu. Kluczowe jest dopasowanie szczegółowości roli do zadania. W przypadku prostych problemów wystarczy rola ogólna. Dla zadań specjalistycznych rola powinna precyzować dziedzinę, poziom doświadczenia oraz kontekst.

**Wzorzec Few-shot (kilku przykładów)**: Stosuj, gdy format wyjściowy jest ważniejszy niż sama treść. Jeśli model musi wygenerować dane w specyficznym schemacie JSON, formacie CSV lub przypisać etykietę klasyfikacyjną, przykłady zadziałają lepiej niż same instrukcje opisowe. Zasada ogólna: 2-3 przykłady dla prostych struktur, 5+ dla struktur złożonych lub niejednoznacznych.

**Wzorzec Chain of Thought (CoT / Łańcuch Myśli)**: Stosuj w zadaniach matematycznych, logicznych, wieloetapowych analizach oraz wszędzie tam, gdzie model powinien przedstawić proces wnioskowania. Zwiększa to dokładność zadań wnioskowania o 10–40% (Wei et al., 2022). NIE stosuj do zwykłego wyszukiwania faktów lub ekstrakcji danych – marnuje to tokeny i czas generacji.

**Wzorzec Szablonowania (Template filling)**: Stosuj do strukturyzowanej ekstrakcji danych, gdzie każda odpowiedź musi posiadać identyczny format. Najlepiej sprawdza się przy temperaturze = 0.0 oraz jasnej instrukcji obsługi pól brakujących (np. wstawienie wartości „N/D”).

**Wzorzec Krytyki/Samokrytyki (Critic/Self-correction)**: Stosuj, gdy jakość ma priorytet nad prędkością generacji. Model najpierw generuje odpowiedź, potem ją krytykuje, a na koniec poprawia. Zwiększa to koszty tokenów dwukrotnie, ale znacząco podnosi poprawność i kompletność. Idealne do kluczowych zastosowań biznesowych (raporty, rekomendacje, publikacje).

**Wzorzec Guardrail (Barier ochronnych)**: Niezbędny w każdym systemie produkcyjnym wchodzącym w interakcję z użytkownikiem. Powinien zawierać: zdefiniowanie granic tematycznych, instrukcję odmowy dla zapytań spoza zakresu oraz jasną obsługę braku wiedzy (np. „nie wiem”). Łącz ten wzorzec z walidacją danych po stronie aplikacji.

**Wzorzec Meta-promptingu**: Służy do automatycznego generowania promptów dla nowych zadań. Zamiast pisać prompt od zera, opisz zadanie i pozwól modelowi wygenerować optymalną instrukcję. Następnie przetestuj ją i iteracyjnie poprawiaj. Znacznie skraca czas prototypowania.

**Wzorzec Dekompozycji (Decomposition)**: Stosuj do złożonych problemów, które można rozwiązać metodą „dziel i rządź”. Model dzieli zagadnienie na mniejsze części, rozwiązuje każdą z nich osobno, a następnie scala wyniki. Najbardziej efektywny dla problemów składających się z 3–7 podzadań.

**Wzorzec dostosowania do odbiorcy (Audience adaptation)**: Stosuj, gdy ta sama treść ma być przedstawiona różnym grupom odbiorców. Precyzyjnie zdefiniuj profil odbiorcy — nie polegaj na domysłach modelu na podstawie kontekstu.

**Wzorzec Granicy (Boundary)**: Stosuj w systemach produkcyjnych, które kategorycznie nie mogą udzielać odpowiedzi na określone tematy. Jest silniejszy niż Guardrail, ponieważ definiuje twarde limity z gotowymi szablonami odmowy. Kluczowy w domenach podlegających ścisłym regulacjom (compliance).

## Spójność rozwiązań między modelami

Zgodność wzorców w testach na modelach GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro i Llama 3:

| Wzorzec | Zgodność między modelami | Uwagi |
|--------|----------------------------|-------|
| Few-shot | Bardzo wysoka | Przykłady (few-shot) działają stabilnie na wszystkich modelach |
| Szablonowanie | Bardzo wysoka | Sztywna struktura minimalizuje rozbieżności |
| Chain of Thought (CoT) | Wysoka | Wszystkie wiodące modele dobrze radzą sobie z myśleniem krok po kroku |
| Persona | Wysoka | Działa wszędzie, choć stopień wrażliwości na szczegóły roli różni się między modelami |
| Guardrail | Umiarkowana | Claude najdokładniej trzyma się wytycznych; GPT-4o potrafi zbaczać z kursu w długich konwersacjach |
| Krytyka/Samokrytyka | Umiarkowana | Jakość samokrytyki silnie zależy od możliwości modelu |
| Meta-prompting | Umiarkowana | GPT-4o i Claude generują prompty o odmiennej stylistyce |
| Granica (Boundary) | Niska - Umiarkowana | Zachowanie przy odmowie zależy od modelu; wymaga testowania |

## Typowe błędy

1. **Stosowanie Chain of Thought (CoT) do każdego zadania**: CoT zwiększa zużycie tokenów i opóźnienia (latency). Używaj go tylko wtedy, gdy zadanie wymaga logicznego wnioskowania.
2. **Przeładowanie ograniczeniami**: zdefiniowanie ponad 5–7 ograniczeń sprawia, że model zaczyna pomijać niektóre z nich. Skup się na 3 najważniejszych.
3. **Sprzeczna persona i ograniczenia**: połączenie roli typu „Jesteś kreatywnym pisarzem” z zakazem „Nigdy nie używaj metafor” dezorientuje model.
4. **Brak jawnego zdefiniowania temperatury**: pozostawienie domyślnej wartości (zwykle 1.0) przy zadaniach wymagających powtarzalnych, deterministycznych wyników.
5. **Kopiowanie i wklejanie promptów bez modyfikacji między różnymi modelami**: zawsze przeprowadzaj testy. Prompt zoptymalizowany pod kątem GPT-4o może dawać gorsze wyniki na Claude i na odwrót.
6. **Ignorowanie System Promptu**: umieszczanie stałych reguł i instrukcji systemowych w sekcji User Message zamiast w System Message.
7. **Nadmierne opieranie się na zakazach**: instrukcje typu „NIE rób X, Y, Z...” są mniej efektywne niż sformułowania pozytywne typu „Wykonaj TYLKO X”. Pozytywne definiowanie zadań daje modelowi jasne wytyczne.

## Cele niezawodności dla konfiguracji produkcyjnych

| Przypadek użycia | Kombinacja wzorców | Oczekiwana dokładność | Zużycie tokenów |
|---------|----------------------|--------------------------------|------------|
| Produkcyjna ekstrakcja | Szablonowanie + Few-shot | 95%+ | Niskie (500-1000) |
| Q&A dla użytkowników | Persona + Guardrail + Granica | 90%+ | Średnie (1000-2000) |
| Generowanie kodu | Persona + CoT | 85%+ | Średnie (1000-3000) |
| Generowanie treści | Persona + Krytyka | 90%+ (jakość) | Wysokie (2000-4000, 2-pass) |
| Klasyfikacja | Few-shot + Guardrail | 95%+ | Niskie (300-800) |
| Złożona analiza | Dekompozycja + CoT | 85%+ | Wysokie (3000-5000) |
