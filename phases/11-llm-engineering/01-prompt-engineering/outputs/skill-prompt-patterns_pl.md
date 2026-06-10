---

name: skill-prompt-patterns
description: Ramy decyzyjne umożliwiające wybór odpowiedniego wzorca podpowiedzi w oparciu o typ zadania, wymagania dotyczące niezawodności i model docelowy
version: 1.0.0
phase: 11
lesson: 01
tags: [prompt-engineering, patterns, llm, temperature, cross-model, few-shot, chain-of-thought]

---

# Przewodnik po wyborze wzoru podpowiedzi

Tworząc funkcję opartą na LLM, wybierz wzór podpowiedzi przed napisaniem podpowiedzi. Wzór określa strukturę. Treść je wypełnia.

## Wzorcowa macierz decyzyjna

| Typ zadania | Podstawowy wzór | Wzór wtórny | Temperatura | Potrzebujesz kilku strzałów? |
|--------------|----------------|--------------------------------|------------|----------------|
| Ekstrakcja danych | Wypełnienie szablonu | Kilka strzałów | 0,0 | Tak (2-3 przykłady) |
| Klasyfikacja | Kilka strzałów | Poręcz | 0,0 | Tak (3-5 przykładów) |
| Podsumowanie | Osoba + szablon | Dostosowanie publiczności | 0,3 | Nie |
| Generowanie kodu | Osoba | Łańcuch Myśli | 0,0 | Opcjonalne |
| Twórcze pisanie | Osoba | Krytyka | 0,7-1,0 | Nie |
| Rozumowanie wieloetapowe | Łańcuch Myśli | Rozkład | 0,3 | Opcjonalne |
| Odpowiedź na pytanie | Osoba + poręcz | Granica | 0,3 | Nie |
| Szybkie generowanie | Meta-podpowiedź | Krytyka | 0,7 | Tak (1-2 przykłady) |
| Moderacja treści | Poręcz + granica | Kilka strzałów | 0,0 | Tak (5+ przykładów) |
| Tłumaczenie/adaptacja | Dostosowanie publiczności | Kilka strzałów | 0,3 | Tak (2-3 przykłady) |

## Kiedy używać każdego wzorca

**Wzorzec osoby**: użyj w przypadku każdego monitu jako linii bazowej. Pytanie tylko, jak konkretna jest ta rola. W przypadku zadań ogólnych wystarczy szeroka rola. W przypadku zadań specyficznych dla domeny rola powinna zawierać nazwę domeny, poziom stażu pracy i kontekst.

**Wzorzec kilku zdjęć**: użyj, gdy format wyjściowy jest ważniejszy niż treść. Jeśli model musi wygenerować określony kształt JSON, format CSV lub etykietę klasyfikacyjną, przykłady są bardziej skuteczne niż instrukcje. Praktyczna zasada: 2-3 przykłady dla prostych formatów, 5+ dla formatów złożonych lub niejednoznacznych.

**Wzorzec łańcucha myślowego**: używaj do matematyki, logiki, analizy wieloetapowej i wszelkich zadań, w których model musi „pokazać, jak działa”. Poprawia dokładność zadań rozumowania o 10–40% (Wei i in., 2022). NIE używaj do prostego wyszukiwania lub ekstrakcji faktów – marnuje tokeny.

**Wzór wypełnienia szablonu**: użyj do wyodrębniania strukturalnego, gdzie każdy wynik musi mieć ten sam kształt. Działa najlepiej przy temperaturze = 0,0 i wyraźnej obsłudze „nie dotyczy” brakujących pól.

**Wzorzec krytyki**: użyj, gdy jakość jest ważniejsza niż szybkość. Model generuje, krytykuje i ulepsza. Mniej więcej podwaja koszt tokena, ale znacznie poprawia dokładność i kompletność. Najlepsze w przypadku wyników o wysokiej stawce (raporty, rekomendacje, treści dostępne publicznie).

**Wzór poręczy**: użyj w dowolnym systemie skierowanym do użytkownika. Zawsze uwzględniaj: granice zakresu, zachowanie odmowne w przypadku żądań spoza zakresu i wyraźną obsługę „nie wiem”. Połącz z walidacją danych wejściowych po stronie aplikacji.

**Wzorzec meta-podpowiedzi**: służy do generowania podpowiedzi dla nowych zadań. Zamiast pisać podpowiedź od zera, opisz zadanie i pozwól modelowi napisać podpowiedź. Następnie przetestuj i wykonaj iterację. Oszczędza czas na początkowym szybkim rozwoju.

**Wzorzec rozkładu**: używaj w przypadku złożonych problemów, które korzystają na zasadzie dziel i zwyciężaj. Model dzieli problem na części, rozwiązuje każdą z nich i łączy. Najbardziej skuteczny w przypadku zadań składających się z 3-7 podproblemów.

**Wzorzec adaptacji odbiorców**: użyj, gdy ta sama treść ma służyć różnym odbiorcom. Określ wyraźnie odbiorców — nie polegaj na zgadywaniu modelu na podstawie kontekstu.

**Wzorzec graniczny**: użyj w systemach produkcyjnych, które NIGDY nie mogą odpowiadać na określone typy pytań. Silniejszy niż poręcze, ponieważ definiuje twardy zakres z dokładnym komunikatem o odmowie. Niezbędne w przypadku domen wrażliwych na zgodność.

## Zgodność między modelami

Wzorce uszeregowane według spójności działania w GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro i Llama 3:

| Wzór | Spójność między modelami | Notatki |
|--------|----------------------------|-------|
| Kilka strzałów | Bardzo wysoki | Przykłady dobrze sprawdzają się we wszystkich modelach |
| Wypełnienie szablonu | Bardzo wysoki | Wyraźna struktura pozostawia niewiele miejsca na rozbieżności |
| Łańcuch Myśli | Wysoki | Wszystkie główne modele obsługują „myśl krok po kroku” |
| Osoba | Wysoki | Działa wszędzie, ale różne modele odpowiadają różnym poziomom specyfiki roli |
| Poręcz | Umiarkowany | Claude najściślej przestrzega poręczy; GPT-4o czasami dryfuje w długich rozmowach |
| Krytyka | Umiarkowany | Jakość samokrytyki różni się znacznie w zależności od modelu
| Meta-podpowiedź | Umiarkowany | GPT-4o i Claude tworzą różne style podpowiedzi |
| Granica | Niski-Umiarkowany | Zachowanie odmowy jest różne; test na model |

## Typowe błędy

1. **Używanie łańcucha myślenia do wszystkiego**: CoT dodaje tokeny i opóźnienia. Używaj go tylko wtedy, gdy potrzebne są kroki uzasadniające.
2. **Zbyt wiele ograniczeń**: więcej niż 5-7 ograniczeń i model zaczyna tracić niektóre. Priorytetowo 3 najważniejsze.
3. **Sprzeczna osobowość + ograniczenia**: „Jesteś kreatywnym pisarzem” + „Nigdy nie używaj metafor” dezorientuje model.
4. **Brak specyfikacji temperatury**: pozostawienie temperatury domyślnej (zwykle 1,0), gdy potrzebne jest wyjście deterministyczne.
5. **Monity o kopiowaniu i wklejaniu pomiędzy modelami**: zawsze testuj. Podpowiedź dostrojona do GPT-4o może działać gorzej na Claude i odwrotnie.
6. **Ignorowanie komunikatu systemowego**: umieszczenie wszystkiego w komunikacie użytkownika zamiast korzystania z komunikatu systemowego w przypadku trwałych reguł.
7. **Nadmierne poleganie na negatywnych ograniczeniach**: „NIE rób X, Y, Z, A, B, C” jest mniej skuteczne niż „Rób TYLKO W”. Pozytywne kadrowanie daje modelowi wyraźny cel.

## Cele niezawodności

| Przypadek użycia | Kombinacja wzorów | Oczekiwana dokładność | Koszt tokena |
|---------|----------------------|--------------------------------|------------|
| Ekstrakcja produkcji | Szablon + Kilka strzałów | 95%+ | Niski (500-1 tys.) |
| Pytania i odpowiedzi skierowane do użytkowników | Osoba + poręcz + granica | 90%+ | Średni (1-2 tys.) |
| Generowanie kodu | Persona + Łańcuch Myśli | 85%+ | Średni (1-3 tys.) |
| Generowanie treści | Osoba + Krytyka | 90%+ jakość | Wysoka (2-4 tys., podwójne przejście) |
| Klasyfikacja | Kilka strzałów + poręcz | 95%+ | Niski (300-800) |
| Kompleksowa analiza | Rozkład + Łańcuch Myśli | 85%+ | Wysoka (3-5 tys.) |