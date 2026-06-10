# Red-Teaming: PARA i ataki automatyczne

> Chao, Robey, Dobriban, Hassani, Pappas, Wong (NeurIPS 2023, arXiv:2310.08419). PAIR — Natychmiastowe automatyczne udoskonalanie iteracyjne — to kanoniczny, automatyczny jailbreak czarnej skrzynki. Osoba atakująca LLM z monitem systemu czerwonej drużyny iteracyjnie proponuje jailbreak dla docelowego LLM, gromadząc próby i odpowiedzi we własnej historii czatów jako informacje zwrotne w kontekście. PAIR zwykle kończy się sukcesem w ciągu 20 zapytań, czyli o rząd wielkości bardziej wydajnie niż GCG (przeszukiwanie gradientowe na poziomie tokena autorstwa Zou i in.) i bez konieczności dostępu do białej skrzynki. PAIR jest teraz standardową bazą w JailbreakBench (arXiv:2404.01318) i HarmBench, obok GCG, AutoDAN, TAP i Persuasive Adversarial Prompt.

**Typ:** Kompilacja
**Języki:** Python (stdlib, próbna pętla PAIR w odniesieniu do celu zabawki)
**Wymagania wstępne:** Faza 18 · 01 (przestrzeganie instrukcji), Faza 14 (inżynieria agenta)
**Czas:** ~75 minut

## Cele nauczania

- Opisz algorytm PAIR: monit systemowy atakującego, udoskonalanie iteracyjne, informacja zwrotna w kontekście.
- Wyjaśnij, dlaczego PAIR jest zdecydowanie bardziej wydajny niż GCG, gdy celem jest czarna skrzynka.
- Wymień cztery inne linie bazowe ataku automatycznego (GCG, AutoDAN, TAP, PAP) i podaj jedną wyróżniającą cechę każdego z nich.
- Opisz protokoły ewaluacyjne JailbreakBench i HarmBench oraz znaczenie każdego z nich pod kątem „wskaźnika powodzenia ataku”.

## Problem

Tworzenie drużyny czerwonych było kiedyś czynnością ręczną. Niewielka liczba doświadczonych testerów stworzyła przeciwstawne podpowiedzi i sprawdzała, które z nich zadziałały. To nie podlega skali: skuteczność ataku wymaga próbki statystycznej, a cel jest celem ruchomym przy każdym wydaniu modelu. PAIR operacjonalizuje tworzenie zespołów czerwonych jako problem optymalizacji z celem czarnej skrzynki.

## Koncepcja

### Algorytm PAIR

Wejścia:
- Celuj w LLM T (model, który atakujemy).
- Sędzia LLM J (ocenia, czy odpowiedź stanowi ucieczkę z więzienia).
- Atakujący LLM A (optymalizator drużyny czerwonej).
- Ciąg celu G: „odpowiedz [szkodliwą instrukcją]”.
- Budżet K (zwykle 20 zapytań).

Pętla dla k w 1..K:
1. A zostaje poproszony o podanie celu G i dotychczasowej historii par (podpowiedź, odpowiedź).
2. A emituje nowy znak zachęty p_k.
3. Prześlij p_k do T; otrzymaj odpowiedź r_k.
4. J zdobywa bramkę (p_k, r_k).
5. Jeśli wynik >= próg, zatrzymaj — znaleziono jailbreak.
6. W innym przypadku dodaj (p_k, r_k) do historii A; Kontynuować.

Wynik empiryczny (NeurIPS 2023): >50% skuteczność ataku przeciwko GPT-3.5-turbo, Llama-2-7B-chat; oznaczają zapytania o sukces w zakresie 10-20.

### Dlaczego PAIR jest skuteczny

GCG (Zou i in. 2023) przeszukuje sufiksy tokenów kontradyktoryjnych według gradientu; wymaga dostępu do modelu białej skrzynki i generuje nieczytelne przyrostki. PAIR działa w oparciu o czarną skrzynkę i generuje ataki w języku naturalnym, które są przenoszone między modelami. Informacje zwrotne w kontekście PAIR pozwalają atakującemu uczyć się na każdym odrzuceniu; GCG nie ma odpowiednika (każda nowa aktualizacja tokena musi na nowo odkryć wcześniejszy postęp).

### Powiązane ataki automatyczne

- **GCG (Zou et al. 2023, arXiv:2307.15043).** Wyszukiwanie gradientowe na poziomie tokena w poszukiwaniu sufiksów kontradyktoryjnych. Biała skrzynka, przenośna, generuje nieczytelne ciągi znaków.
- **AutoDAN (Liu et al. 2023).** Ewolucyjne wyszukiwanie podpowiedzi, kierowane hierarchicznym celem.
- **TAP (Mehrotra et al. 2024).** Drzewo ataków z przycinaniem — rozgałęzia wiele wdrożeń w stylu PAIR.
- **PAP (Zeng et al. 2024).** Perswazyjne kontradyktoryjne podpowiedzi — koduje ludzkie techniki perswazji jako szablony podpowiedzi.

### JailbreakBench i HarmBench

Obydwa (2024) standaryzują ocenę:

- JailbreakBench (arXiv:2404.01318). 100 szkodliwych zachowań w 10 kategoriach zasad OpenAI. Wskaźnik skuteczności ataku (ASR) jako główny wskaźnik. Wymaga sędziego (GPT-4-turbo, Llama Guard lub StrongREJECT).
- HarmBench (Mazeika i in. 2024). 510 zachowań w 7 kategoriach, z semantycznymi i funkcjonalnymi testami szkód. Porównuje 18 ataków z 33 modelami.

ASR jest zwykle raportowany przy stałym budżecie zapytań. Porównywanie ataków wymaga dopasowania budżetów; 90% ASR przy 200 zapytaniach nie jest porównywalne z 85% ASR przy 20.

### Powód, dla którego ma to znaczenie w przypadku wdrożeń w 2026 r

Każde pionierskie laboratorium uruchamia teraz PAIR i TAP w odniesieniu do modeli produkcyjnych przed ich wypuszczeniem na rynek. Trajektorie ASR pojawiają się na kartach modeli (lekcja 26) i załącznikach dotyczących bezpieczeństwa (lekcja 18). Atak nie jest egzotyczny — jest to standardowa infrastruktura.

### Gdzie to pasuje do fazy 18

Lekcja 12 to podstawy ataku automatycznego. Lekcja 13 (Many-Shot Jailbreaking) to uzupełniający exploit związany z długością. Lekcja 14 (sztuka ASCII / obraz wizualny) to atak na kodowanie. Lekcja 15 (Wstrzykiwanie pośrednie) to powierzchnia ataku produkcyjnego w roku 2026. Lekcja 16 omawia odpowiedniki defensywne (Llama Guard, Garak, PyRIT).

## Użyj tego

`code/main.py` tworzy zabawkową pętlę PAIR. Celem jest próbny klasyfikator, który odrzuca „oczywiste” szkodliwe podpowiedzi (filtr słów kluczowych). Osoba atakująca to udoskonalacz oparty na regułach, który próbuje parafrazować, odgrywać role i kodować. Sędzia ocenia odpowiedź. Obserwujesz, jak atakujący odnosi sukces w ~5-15 iteracjach przeciwko filtrowi słów kluczowych i porażce w przypadku filtru semantycznego.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-attack-audit.md`. Mając raport z oceny zespołu czerwonego, sprawdza: jakie ataki zostały przeprowadzone (PAIR, GCG, TAP, AutoDAN, PAP), przy jakim budżecie każdy z nich, przy pomocy jakiego sędziego, jaki zestaw szkodliwych zachowań (JailbreakBench, HarmBench, wewnętrzne).

## Ćwiczenia

1. Uruchom `code/main.py`. Mierz średnią liczbę zapytań do sukcesu dla trzech wbudowanych strategii atakującego. Wyjaśnij, które założenie dotyczące obrony celu wykorzystuje każde z nich.

2. Zastosuj czwartą strategię atakującego (np. tłumaczenie na inny język, kodowanie base64). Zgłoś nowe średnie zapytania do sukcesu w odniesieniu do celu filtra słów kluczowych i celu filtra semantycznego.

3. Przeczytaj Chao i in. 2023 Rysunek 5 (porównanie PAIR vs GCG). Opisz dwa scenariusze, w których preferowany jest GCG pomimo przewagi w zakresie wydajności PAIR.

4. JailbreakBench raportuje ASR względem ustalonego celu. Zaprojektuj dodatkową metrykę mierzącą różnorodność ataków (różnicę w pomyślnych podpowiedziach). Wyjaśnij, dlaczego różnorodność ma znaczenie dla oceny obronności.

5. TAP (Mehrotra 2024) rozszerza PAIR o rozgałęzianie + przycinanie. Naszkicuj rozszerzenie w stylu TAP do `code/main.py` i opisz stosunek kosztów obliczeniowych do współczynnika sukcesu.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| PARA | „automatyczny jailbreak” | Szybkie automatyczne iteracyjne udoskonalanie; atakujący-LLM + pętla sędziego-LLM |
| GCG | „gradientowe jailbreak” | Wyszukiwanie gradientowe na poziomie tokena metodą białej skrzynki dla sufiksów kontradyktoryjnych |
| Wskaźnik skuteczności ataku (ASR) | „% jailbreaków przy k zapytaniach” | Metryka podstawowa; należy zgłosić z budżetem zapytania i tożsamością sędziego |
| Sędzia LLM | „strzelec” | LLM oceniający, czy reakcja spełnia szkodliwy cel |
| Ławka Jailbreak | "ocena" | Ustandaryzowany zestaw szkodliwych zachowań z oznaczonymi kategoriami |
| HarmBench | „szersza ławka” | 510 zachowań, testy szkody funkcjonalnej i semantycznej |
| KLIKNIJ | „drzewo ataków” | PARA z rozgałęzianiem + przycinaniem; lepszy ASR przy większej mocy obliczeniowej |

## Dalsze czytanie

- [Chao i in. — Jailbreaking Black Box LLMs in Twenty Queries (arXiv:2310.08419)](https://arxiv.org/abs/2310.08419) — Artykuł PAIR, NeurIPS 2023
- [Zou i in. — Uniwersalne i przenaszalne ataki kontradyktoryjne na wyrównane LLM (arXiv:2307.15043)](https://arxiv.org/abs/2307.15043) — artykuł GCG
- [Chao i in. — JailbreakBench (arXiv:2404.01318)](https://arxiv.org/abs/2404.01318) — standardowa ocena
- [Mazeika i in. — HarmBench (ICML 2024)](https://arxiv.org/abs/2402.04249) — szersza ocena