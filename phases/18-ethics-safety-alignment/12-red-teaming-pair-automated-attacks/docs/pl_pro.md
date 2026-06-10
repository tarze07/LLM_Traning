# Red-Teaming: PAIR i ataki automatyczne

> Chao, Robey, Dobriban, Hassani, Pappas, Wong (NeurIPS 2023, arXiv:2310.08419). Protokół PAIR (Prompt Automatic Iterative Refinement) to kanoniczny przykład automatycznego ataku typu jailbreak w modelu czarnej skrzynki (black-box). Atakujący model LLM (wyposażony w odpowiedni prompt systemowy) iteracyjnie proponuje próby złamania zabezpieczeń (jailbreak) dla modelu docelowego, gromadząc historię prób i odmów we własnym kontekście jako sprzężenie zwrotne (in-context feedback). PAIR zazwyczaj osiąga cel w ciągu 20 zapytań, co czyni go o rząd wielkości bardziej wydajnym od metody GCG (przeszukiwanie gradientowe na poziomie tokenów autorstwa Zou i in.) i nie wymaga dostępu do wag modelu (white-box). PAIR stanowi obecnie standardowy punkt odniesienia (baseline) w benchmarkach JailbreakBench (arXiv:2404.01318) oraz HarmBench, obok metod GCG, AutoDAN, TAP oraz Persuasive Adversarial Prompts (PAP).

**Typ:** Koduj i testuj
**Języki:** Python (stdlib, symulacja pętli PAIR na uproszczonym modelu docelowym)
**Wymagania wstępne:** Faza 18 · 01 (przestrzeganie instrukcji), Faza 14 (inżynieria agentów)
**Czas:** ~75 minut

## Cele nauczania

- Opisz algorytm PAIR: prompt systemowy atakującego, proces iteracyjnego udoskonalania oraz wykorzystanie sprzężenia zwrotnego w kontekście.
- Wyjaśnij, dlaczego protokół PAIR charakteryzuje się znacznie wyższą wydajnością niż GCG w przypadku ataków na modele typu czarna skrzynka.
- Wymień cztery inne automatyczne metody ataków (GCG, AutoDAN, TAP, PAP) i wskaż po jednej cechy wyróżniającej każdą z nich.
- Opisz protokoły ewaluacyjne JailbreakBench oraz HarmBench i wyjaśnij znaczenie wskaźnika skuteczności ataku (ASR) w każdym z nich.

## Problem

W przeszłości red-teaming był procesem czysto manualnym. Nieliczni eksperci tworzyli wrogie prompty i ręcznie weryfikowali ich skuteczność. Podejście to jest jednak całkowicie nieskalowalne: rzetelna ocena skuteczności ataków wymaga odpowiedniej próby statystycznej, a sam cel zmienia się wraz z każdą nową wersją modelu. PAIR operacjonalizuje red-teaming jako problem optymalizacyjny z modelem docelowym traktowanym jako czarna skrzynka.

## Koncepcja

### Algorytm PAIR

Dane wejściowe:
- Docelowy model LLM (T) – model, na który przeprowadzany jest atak.
- Model oceniający LLM (J) – sędzia określający, czy odpowiedź docelowa stanowi jailbreak.
- Atakujący model LLM (A) – optymalizator po stronie zespołu czerwonych (red team).
- Cel ataku (G) – ciąg tekstowy (np. „odpowiedz instrukcją jak stworzyć [szkodliwy element]”).
- Maksymalny budżet zapytań (K) – zazwyczaj 20 zapytań.

Pętla iteracyjna dla każdego kroku k od 1 do K:
1. Model A otrzymuje cel G oraz dotychczasową historię par (wygenerowany prompt, uzyskana odpowiedź).
2. Model A generuje nową propozycję promptu p_k.
3. Prompt p_k jest wysyłany do modelu T; rejestrowana jest odpowiedź r_k.
4. Sędzia J ocenia parę (p_k, r_k) pod kątem realizacji celu G.
5. Jeśli ocena przekroczy próg krytyczny, następuje zatrzymanie procedury – znaleziono jailbreak.
6. W przeciwnym razie para (p_k, r_k) jest dołączana do historii konwersacji modelu A i następuje kolejna iteracja.

Wyniki empiryczne (NeurIPS 2023): skuteczność ataku (ASR) powyżej 50% dla modeli GPT-3.5-turbo oraz Llama-2-7B-chat przy średniej liczbie zapytań do sukcesu w przedziale 10-20.

### Dlaczego PAIR jest tak wydajny

Metoda GCG (Zou i in., 2023) wyszukuje optymalne wrogie tokeny (sufiksy) za pomocą informacji o gradientach; wymaga to pełnego dostępu do wag modelu (biała skrzynka) i generuje ciągi nieczytelne dla człowieka. PAIR działa w trybie czarnej skrzynki i generuje zapytania w języku naturalnym, co ułatwia ich przenoszenie (transferability) na inne modele. Ponadto, dzięki sprzężeniu w kontekście, atakujący model w PAIR uczy się na błędach z każdej odrzuconej próby; GCG nie posiada takiego mechanizmu (każda modyfikacja tokenów wymaga szukania optymalizacji od nowa).

### Powiązane metody automatycznych ataków

- **GCG (Zou i in., 2023, arXiv:2307.15043).** Wyszukiwanie gradientowe na poziomie tokenów w celu znalezienia wrogich sufiksów. Metoda białej skrzynki, o wysokiej przenoszalności, generująca nieczytelne ciągi znaków.
- **AutoDAN (Liu i in., 2023).** Ewolucyjne przeszukiwanie promptów oparte na hierarchicznej funkcji celu.
- **TAP (Mehrotra i in., 2024).** Algorytm drzewa ataków z przycinaniem (tree-of-attacks) – rozwija równolegle wiele ścieżek wyszukiwania w stylu PAIR.
- **PAP (Zeng i in., 2024).** Perswazyjne prompty wrogie (Persuasive Adversarial Prompts) – koduje techniki perswazji stosowane przez ludzi w formie szablonów promptów.

### JailbreakBench i HarmBench

Oba benchmarki (udostępnione w 2024 r.) standaryzują proces ewaluacji:

- **JailbreakBench (arXiv:2404.01318).** Zawiera 100 szkodliwych zachowań podzielonych na 10 kategorii zgodnych z politykami OpenAI. Główną metryką jest wskaźnik skuteczności ataku (ASR). Wymaga zastosowania automatycznego sędziego (np. GPT-4-turbo, Llama Guard lub StrongREJECT).
- **HarmBench (Mazeika i in., 2024).** Obejmuje 510 zachowań w 7 kategoriach z testami szkód semantycznych oraz funkcjonalnych. Porównuje skuteczność 18 typów ataków na 33 modelach.

Wskaźnik ASR podaje się zazwyczaj przy sztywno określonym budżecie zapytań. Porównywanie różnych metod wymaga zrównania tych budżetów; wynik ASR na poziomie 90% przy 200 zapytaniach nie jest bezpośrednio porównywalny z wynikiem 85% uzyskanym przy zaledwie 20 zapytaniach.

### Znaczenie praktyczne (stan na 2026 r.)

Każde wiodące laboratorium badawcze uruchamia obecnie procedury PAIR i TAP na modelach produkcyjnych przed ich oficjalnym udostępnieniem. Wykresy odporności ASR są standardowo dołączane do kart modeli (model cards, Lekcja 26) oraz uzasadnień bezpieczeństwa (Lekcja 18). Testy te nie są już traktowane jako akademicka nowinka, lecz jako podstawowy element potoku testowego.

### Miejsce w strukturze Fazy 18

Lekcja 12 stanowi wprowadzenie do automatyzacji ataków. Lekcja 13 (Many-Shot Jailbreaking) opisuje exploity wykorzystujące bardzo długi kontekst. Lekcja 14 (grafika ASCII / jailbreaki wizualne) skupia się na manipulacji kodowaniem danych. Lekcja 15 (pośrednie wstrzykiwanie promptów) opisuje kluczową powierzchnię ataków produkcyjnych. Lekcja 16 omawia mechanizmy obronne (Llama Guard, Garak, PyRIT).

## Użycie kodu

Plik `code/main.py` implementuje uproszczoną pętlę PAIR. Model docelowy to prosty klasyfikator odrzucający „oczywiste” szkodliwe prompty za pomocą filtra słów kluczowych. Atakujący to prosty generator regułowy próbujący stosować parafrazy, odgrywanie ról oraz alternatywne kodowanie znaków. Sędzia ocenia uzyskana odpowiedź. Możesz zaobserwować, jak atakujący z powodzeniem obchodzi prosty filtr słów kluczowych w ciągu 5-15 iteracji, podczas gdy filtr semantyczny skutecznie blokuje jego próby.

## Co otrzymasz

Ta lekcja przygotowuje plik `outputs/skill-attack-audit.md`. Na podstawie raportu z ewaluacji bezpieczeństwa (red-teaming) dokument ten weryfikuje: jakie ataki zostały przeprowadzone (PAIR, GCG, TAP, AutoDAN, PAP), przy jakim budżecie zapytań, z użyciem jakiego sędziego oraz na jakim zbiorze szkodliwych zachowań (JailbreakBench, HarmBench czy wewnętrzne zestawy testowe).

## Ćwiczenia

1. Uruchom `code/main.py`. Zmierz średnią liczbę zapytań potrzebną do przełamania filtra dla trzech wbudowanych strategii atakującego. Wyjaśnij, jakie założenia dotyczące mechanizmów obronnych docelowego modelu wykorzystuje każda z tych strategii.

2. Dodaj czwartą strategię ataku (np. tłumaczenie na inny język lub kodowanie Base64). Przedstaw uzyskane średnie liczby zapytań dla prostego filtra słów kluczowych oraz filtra semantycznego.

3. Przeczytaj sekcję dotyczącą porównania PAIR i GCG w pracy Chao i in. (2023, rysunek 5). Opisz dwa scenariusze, w których zastosowanie GCG jest preferowane mimo niższej wydajności w porównaniu do PAIR.

4. Benchmark JailbreakBench mierzy wskaźnik ASR względem konkretnego zestawu celów. Zaproponuj dodatkową metrykę, która mierzyłaby różnorodność wygenerowanych pomyślnych ataków (stopień zróżnicowania skutecznych promptów). Wyjaśnij, dlaczego różnorodność ta jest kluczowa z punktu widzenia oceny odporności modelu.

5. Algorytm TAP (Mehrotra, 2024) rozbudowuje mechanizm PAIR o drzewiaste rozgałęzianie i przycinanie ścieżek. Naszkicuj modyfikację w stylu TAP dla skryptu `code/main.py` i opisz zależność między narzutem obliczeniowym a uzyskanym wskaźnikiem skuteczności ataku.

## Kluczowe terminy

| Termin | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|--------------------------------------|
| PAIR | „automatyczny jailbreak” | Metoda automatycznego i iteracyjnego udoskonalania promptów; wykorzystuje pętlę modelu atakującego i modelu oceniającego (sędziego) |
| GCG | „jailbreak oparty na gradientach” | Metoda białej skrzynki wykorzystująca przeszukiwanie na poziomie tokenów w celu wygenerowania wrogich sufiksów |
| Wskaźnik skuteczności ataku (ASR) | „% udanych prób przy k zapytaniach” | Podstawowa metryka skuteczności ataku; musi być podawana wraz z budżetem zapytań oraz typem sędziego |
| Sędzia LLM (Judge LLM) | „klasyfikator sukcesu” | Model oceniający, czy wygenerowana odpowiedź realizuje szkodliwy cel ataku |
| JailbreakBench | „standardowy benchmark” | Ustandaryzowany zbiór szkodliwych zachowań z przypisanymi kategoriami bezpieczeństwa |
| HarmBench | „rozszerzony benchmark” | Zestaw 510 zachowań testujący szkodliwość funkcjonalną i semantyczną na dużą skalę |
| TAP | „drzewo ataków” | Rozwinięcie metody PAIR o mechanizmy rozgałęziania i przycinania ścieżek (tree-of-attacks); wyższy ASR kosztem większych obliczeń |

## Dalsze czytanie

- [Chao et al. — Jailbreaking Black Box LLMs in Twenty Queries (arXiv:2310.08419)](https://arxiv.org/abs/2310.08419) – publikacja opisująca algorytm PAIR (NeurIPS 2023)
- [Zou et al. — Universal and Transferable Adversarial Attacks on Aligned Language Models (arXiv:2307.15043)](https://arxiv.org/abs/2307.15043) – publikacja dotycząca metody GCG
- [Chao et al. — JailbreakBench (arXiv:2404.01318)](https://arxiv.org/abs/2404.01318) – dokumentacja standardowego benchmarku oceny odporności
- [Mazeika et al. — HarmBench (ICML 2024)](https://arxiv.org/abs/2402.04249) – dokumentacja rozszerzonego benchmarku ewaluacyjnego
