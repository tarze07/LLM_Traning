# Grafika ASCII i wizualne jailbreaki

> Jiang, Xu, Niu, Xiang, Ramasubramanian, Li, Poovendran, „ArtPrompt: ASCII Art-based Jailbreak Attacks Against Aligned LLMs” (ACL 2024, arXiv:2402.11753). Zamaskuj tokeny istotne dla bezpieczeństwa w szkodliwym żądaniu, zastąp je renderowaniami tych samych liter w formacie ASCII i wyślij zamaskowany monit. GPT-3.5, GPT-4, Gemini, Claude, Llama-2 nie rozpoznają dobrze tokenów graficznych ASCII. Atak omija PPL (filtry zakłopotania), obronę parafrazową i retokenizację. Powiązane: test porównawczy ViTC mierzy rozpoznawanie niesemantycznych podpowiedzi wizualnych; StructuralSleight uogólnia nietypowe struktury zakodowane w tekście (drzewa, wykresy, zagnieżdżony JSON) jako rodzinę ataków kodujących.

**Typ:** Kompilacja
**Języki:** Python (stdlib, uprząż do maskowania tokenów ArtPrompt)
**Wymagania wstępne:** Faza 18 · 12 (PARA), Faza 18 · 13 (MSJ)
**Czas:** ~60 minut

## Cele nauczania

- Opisz atak ArtPrompt: etap identyfikacji słowa, podstawienie grafiki ASCII, końcowy ukryty monit.
- Wyjaśnij, dlaczego standardowe mechanizmy obronne (PPL, parafraza, retokenizacja) zawodzą w ArtPrompt.
- Zdefiniuj ViTC i opisz, co mierzy.
- Opisać StructuralSleight jako uogólnienie dowolnych, nietypowych struktur zakodowanych tekstem.

## Problem

Ataki za pomocą parafrazy i odgrywania ról (lekcja 12) oraz długiego kontekstu (lekcja 13) działają na poziomie tekstu. ArtPrompt działa na poziomie rozpoznawania: model nie analizuje zabronionego tokena. Analizuje obraz renderowany w znakach. Filtr bezpieczeństwa widzi nieszkodliwe znaki interpunkcyjne. Modelka widzi słowo.

## Koncepcja

### ArtPrompt, dwa kroki

Krok 1. Identyfikacja słów. W odpowiedzi na szkodliwe żądanie atakujący używa LLM do identyfikacji słów istotnych dla bezpieczeństwa (np. „bomba” w „jak zrobić bombę”). 

Krok 2. Generowanie ukrytych podpowiedzi. Zastąp każde zidentyfikowane słowo jego renderingiem w formacie ASCII (blok znaków 7x5 lub 7x7 tworzący kształt litery). Model otrzymuje siatkę znaków interpunkcyjnych i spacji, które wystarczająco sprawny model może rozpoznać jako słowo; filtr bezpieczeństwa widzi tylko siatkę.

Wynik: GPT-4, Gemini, Claude, Lama-2, GPT-3.5 zawiodły. Wskaźnik skuteczności ataku powyżej 75% w ich podzbiorze porównawczym.

### Dlaczego standardowe mechanizmy obronne zawodzą

- **PPL (filtr zakłopotania).** Grafika ASCII charakteryzuje się dużym zakłopotaniem — ale tak samo jest z wszystkimi nowatorskimi danymi wejściowymi. Opcje progowe blokujące ArtPrompt blokują również prawidłowe, strukturalne wprowadzanie danych.
- **Parafraza.** Parafraza podpowiedzi niszczy grafikę ASCII. W praktyce parafrazując LLM często zachowuje się lub rekonstruuje sztukę.
- **Retokenizacja.** Odmienne dzielenie żetonów nie zmienia tego, że wizją modela jest rozpoznawanie kształtów liter.

Podstawowym problemem jest to, że filtry bezpieczeństwa działają na poziomie tokenu lub semantyki; ArtPrompt działa na poziomie rozpoznawania wizualnego.

### Test porównawczy ViTC

Rozpoznawanie niesemantycznych podpowiedzi wizualnych. Mierzy zdolność modelu do odczytywania grafiki ASCII, skrzydeł i innych treści wizualnych nietekstowo-semantycznych. Skuteczność ArtPrompt koreluje z dokładnością ViTC: im lepiej model odczytuje tekst wizualny, tym lepiej ArtPrompt na nim działa. Jest to kompromis w zakresie możliwości i bezpieczeństwa.

### Zręczność strukturalna

Uogólnia ArtPrompt: nietypowe struktury zakodowane tekstem (UTES). Drzewa, wykresy, zagnieżdżony JSON, CSV-in-JSON, bloki kodu w stylu różnicowym. Jeśli struktura jest rzadka w przypadku szkolenia danych dotyczących bezpieczeństwa, ale można ją analizować za pomocą modelu, może ukrywać szkodliwą zawartość.

Konsekwencje obronne: bezpieczeństwo musi być uogólnione na ustrukturyzowane reprezentacje, które model może przeanalizować. Zestaw jest duży i rośnie.

### Analog modalności obrazu

Visual LLM (GPT-5.2, Gemini 3 Pro, Claude Opus 4.5, Grok 4.1) zwiększają powierzchnię ataku. Ataki w stylu ArtPrompt z użyciem rzeczywistych obrazów są silniejsze niż analogi w formacie ASCII, ponieważ kodery obrazu wytwarzają bogatszy sygnał.

### Gdzie to pasuje do fazy 18

W lekcjach 12-14 opisano trzy ortogonalne wektory ataku: udoskonalanie iteracyjne (PAIR), długość kontekstu (MSJ) i kodowanie (ArtPrompt/StructuralSleight). Lekcja 15 przechodzi od ataków skoncentrowanych na modelu do ataków na granice systemu (pośrednie wstrzykiwanie natychmiastowe). Lekcja 16 opisuje reakcję na narzędzia obronne.

## Użyj tego

`code/main.py` buduje zabawkę ArtPrompt. Możesz zamaskować określone słowa w szkodliwym zapytaniu za pomocą glifów w formacie ASCII, sprawdzić, czy zamaskowany ciąg przechodzi filtr słów kluczowych i (opcjonalnie) zdekodować zamaskowany ciąg za pomocą prostego modułu rozpoznawania.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-encoding-audit.md`. Biorąc pod uwagę raport dotyczący obrony przed jailbreakiem, wylicza on objęte rodziny ataków kodowania (sztuka ASCII, base64, leet-speak, homoglif UTF-8, UTES) i warstwę obrony, która przechwytuje każdą z nich.

## Ćwiczenia

1. Uruchom `code/main.py`. Sprawdź, czy zamaskowany ciąg przechodzi przez prosty filtr słów kluczowych. Zgłoś wymaganą zmianę poziomu postaci.

2. Zaimplementuj drugie kodowanie: base64 dla tego samego słowa docelowego. Porównaj współczynnik obejścia filtra z ArtPrompt i trudnością odzyskiwania.

3. Przeczytaj Jiang i in. 2024, sekcja 4.3 (wyniki pięciu modeli). Zaproponuj powód, dla którego odporność Claude'a na ArtPrompt jest wyższa niż w przypadku Gemini w tym samym teście.

4. Zaprojektuj ochronę przed generacją, która wykrywa w wierszu poleceń regiony w kształcie grafiki ASCII. Zmierz odsetek wyników fałszywie dodatnich w prawidłowym kodzie, tabelach i zapisie matematycznym.

5. StructuralSleight wyświetla listę 10 struktur kodowania. Naszkicuj uogólnioną obronę, która obsługuje wszystkie 10, i oszacuj koszt obliczeniowy na obroniony monit.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| ArtPodpowiedź | „atak z grafiką ASCII” | Dwuetapowy jailbreak, który maskuje słowa bezpieczeństwa za pomocą renderingów w formacie ASCII |
| Maskowanie | „ukryj słowo” | Zastąp zabroniony token wizualną reprezentacją, którą czyta model, ale filtr nie |
| UTES | „niezwykła struktura” | Nietypowa struktura zakodowana tekstowo — drzewo, wykres, zagnieżdżony JSON itp. używana do przemycania treści |
| ViTC | „możliwość tekstu wizualnego” | Test porównawczy zdolności modelu do odczytu niesemantycznego kodowania wizualnego |
| Filtr zakłopotania | „Obrona PPL” | Odrzucaj podpowiedzi z dużym zakłopotaniem; kończy się niepowodzeniem, ponieważ uzasadnione, strukturyzowane dane wejściowe również uzyskują wysoką ocenę |
| Retokenizacja | „obrona przed zmianą tokenizera” | Wstępnie przetwórz monit za pomocą innego tokenizera; kończy się niepowodzeniem, ponieważ rozpoznawanie jest wizualne |
| Homoglif | „podobne postacie” | Znaki Unicode wyglądające identycznie jak litery łacińskie; pominąć sprawdzanie podciągów |

## Dalsze czytanie

- [Jiang i in. — ArtPrompt (ACL 2024, arXiv:2402.11753)](https://arxiv.org/abs/2402.11753) — dokument ASCII-art jailbreak
- [Li i in. — StructuralSleight (arXiv:2406.08754)](https://arxiv.org/abs/2406.08754) — Uogólnienie UTES
- [Chao i in. — PARA (Lekcja 12, arXiv:2310.08419)](https://arxiv.org/abs/2310.08419) — uzupełniający atak iteracyjny
- [Anil i in. — Many-shot Jailbreaking (lekcja 13)](https://www.anthropic.com/research/many-shot-jailbreaking) — atak o uzupełniającej długości