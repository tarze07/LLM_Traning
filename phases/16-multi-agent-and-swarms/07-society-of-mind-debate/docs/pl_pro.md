# Społeczeństwo umysłu (Society of Mind) i debata wieloagentowa

> Koncepcja Marvina Minsky'ego z 1986 roku, traktująca inteligencję jako społeczeństwo współpracujących, wyspecjalizowanych procesów (agentów), jest w inżynierii AI odkrywana na nowo co dekadę. W 2023 roku Du i in. przełożyli ten pomysł na konkretny algorytm: wiele instancji LLM generuje odpowiedzi na to samo pytanie, analizuje nawzajem swoje argumenty, krytykuje je i aktualizuje własne stanowiska. W ciągu N rund agenci wypracowują konsensus, który w testach logicznych i faktograficznych deklasuje tradycyjne podejścia, takie jak zero-shot Chain-of-Thought (CoT) czy autorefleksja. Kluczowe są dwa wnioski: zarówno **zwiększanie liczby agentów**, jak i **prowadzenie debaty wielorundowej** wnoszą niezależny wkład w końcowy sukces. Współpraca agentów przewyższa monolog jednej instancji, a wielorundowa wymiana zdań daje znacznie lepsze rezultaty niż pojedyncze, bezpośrednie głosowanie.

**Typ:** Ucz się + Buduj  
**Języki:** Python (stdlib)  
**Wymagania wstępne:** Faza 16 · 04 (Model prymitywny)  
**Czas:** ~60 minut  

## Problem

Spójność wewnętrzna (Self-Consistency) — czyli wielokrotne generowanie odpowiedzi przez ten sam model i wybór opcji większościowej — to najprostszy sposób na poprawę jakości wnioskowania. Metoda ta jednak szybko osiąga swój limit (plateau). Zwiększanie liczby próbek powyżej pewnego poziomu nie przynosi już dalszych skoków wydajności.

Debata wieloagentowa pozwala przełamać to ograniczenie. Zamiast generować N niezależnych i niepowiązanych próbek z jednego modelu, pozwalamy N agentom na analizę procesów myślowych pozostałych uczestników i nanoszenie poprawek. Dzięki temu korelacja błędów między próbkami spada, a wypracowany punkt zbieżności często okazuje się poprawny nawet wtedy, gdy zwykłe głosowanie większościowe wskazywało błędną odpowiedź.

## Koncepcja

### Algorytm Du i in. (2023)

Na podstawie publikacji arXiv:2305.14325 (zaprezentowanej na ICML 2024):

1. Każdy z N agentów generuje niezależnie swoją wstępną odpowiedź na zadane pytanie.
2. W każdej kolejnej rundzie r = 2..R: każdemu agentowi prezentuje się odpowiedzi pozostałych uczestników z rundy r-1 i zadaje pytanie: „Biorąc pod uwagę powyższe argumenty, sformułuj swoją zaktualizowaną odpowiedź”.
3. Po zakończeniu R rund następuje głosowanie większościowe w celu wyłonienia ostatecznej odpowiedzi.

W testach takich jak MMLU, GSM8K, MATH oraz weryfikacji faktów, debata wieloagentowa konsekwentnie osiągała lepsze wyniki niż Chain-of-Thought oraz metody oparte na autorefleksji (Self-Reflection).

### Dwa niezależne parametry

Analiza ablacji z tej samej publikacji wykazuje:

- **Samo zwiększanie liczby agentów** (1 runda, głosowanie większościowe z N agentów) poprawia wyniki w większości zadań, ale szybko osiąga plateau.
- **Samo zwiększanie liczby rund dla jednego agenta** (jeden agent analizujący swoje własne, wcześniejsze odpowiedzi) daje znikome korzyści — co jest znaną słabością autorefleksji.
- **Połączenie obu tych podejść** (wielu agentów debatujących w wielu rundach) przynosi skokowy wzrost jakości.

### Dlaczego to działa

Decydują o tym dwa mechanizmy:

1. **Konfrontacja z odmiennymi opiniami.** Gdy agent widzi, że inny uczestnik wyciągnął odmienne wnioski na podstawie tego samego pytania, jest zmuszony do zweryfikowania swojego toku myślenia. Sprawia to, że kontekst w rundzie r+1 jest znacznie bogatszy informacyjnie niż w rundzie r.
2. **Redukcja skorelowanych błędów.** Przy zwykłym próbkowaniu z jednego modelu błędy są silnie skorelowane — średnia z prób może wskazać błędną odpowiedź. Zastosowanie różnych modeli, odmiennych nasion losowości (seeds) lub po prostu konfrontacja różnych punktów widzenia pozwala na skuteczną dekorelację tych błędów.

### Debata heterogeniczna

Warianty tego algorytmu (np. A-HMAD) wykorzystują *różne modele bazowe* dla poszczególnych agentów. Debata, w której uczestniczą np. Llama, Claude oraz GPT, minimalizuje ryzyko wpadnięcia w monokulturę błędów, ponieważ rodziny te rzadko powielają te same potknięcia logiczne.

Ograniczenie: udział słabszego modelu w debacie może czasami ściągnąć konsensus w kierunku błędnej odpowiedzi (zob. „Should We Respect LLMs' Opinions?”, arXiv:2311.17371).

### NLSOM — skalowanie do 129 agentów

Zhuge i in. („Mindstorms in Natural Language-Based Societies of Mind”, arXiv:2305.17066) rozszerzyli tę koncepcję na struktury liczące aż 129 agentów. Wykazano, że wraz ze skalą pojawiają się mechanizmy specjalizacji i samoorganizacji, a system deklasuje pojedyncze modele w zadaniach takich jak wizualne odpowiadanie na pytania (VQA).

### Typowe tryby awarii

- **Kaskadowe potakiwanie (Flattery Cascade / konformizm).** Agenci zaczynają ślepo zgadzać się z uczestnikiem, który wyraża swoje zdanie z największą pewnością siebie. Debata załamuje się i sprowadza do najgłośniejszego głosu. Rozwiązaniem jest stosowanie instrukcji wymuszających krytykę (np. „jeden agent musi bronić zdania przeciwnego”).
- **Dryf tematyczny.** W debatach trwających wiele rund agenci mogą stopniowo zbaczać z tematu głównego. Rozwiązanie: przypominaj pierwotne pytanie na początku każdej rundy.
- **Eksplozja kosztów obliczeniowych (Compute inflation).** N agentów × R rund = N·R wywołań LLM, z których każde niesie rosnący kontekst. Debata 5 agentów w 5 rundach to 25 wywołań modeli na rosnącej historii wiadomości. Koszt pojedynczego zapytania może wzrosnąć ponad 10-krotnie w porównaniu do standardowego CoT.

## Zbuduj to

W pliku `code/main.py` zaimplementowano uproszczoną debatę (3 agenci × 3 rundy) nad zadaniem matematycznym, w której każdy agent rozpoczyna proces z inną (potencjalnie błędną) odpowiedzią. Agenci są sterowani skryptem — aktualizują swoje stanowiska na bazie średniej ważonej zaufaniem odpowiedzi swoich sąsiadów. Proces zbieżności jest logowany runda po rundzie.

Demo obrazuje dwa kluczowe efekty:
- Już pierwsza runda wymiany zdań przybliża agentów do poprawnego wyniku.
- Kolejne rundy po rundzie 2 wykazują szybko malejące przyrosty jakości (zgodnie z plateau opisanym przez Du i in.).

Uruchomienie:

```
python3 code/main.py
```

## Użyj tego

W pliku `outputs/skill-debate-configurator.md` zdefiniowano umiejętność służącą do konfiguracji debaty dla nowego zadania: dobór liczby agentów, liczby rund, struktury modeli (homogeniczna vs heterogeniczna) oraz ról (symetryczne vs rola oponenta). Narzędzie szacuje również koszty tokenowe przed uruchomieniem systemu.

## Wyślij to

Zasady wdrażania systemów opartych na debacie:

- **Ograniczenie liczby rund do maksymalnie 3.** Badania wykazują, że 3 rundy pozwalają pozyskać zdecydowaną większość przyrostu jakości. Dalsze rundy generują koszty, nie przynosząc korzyści.
- **Ograniczenie liczby agentów do maksymalnie 5.** Powyżej tej liczby koszty kontekstu i wywołań zaczynają dominować nad zyskiem jakościowym.
- **Stosowanie modeli heterogenicznych.** Używaj co najmniej dwóch różnych rodzin modeli bazowych w jednym panelu debatującym.
- **Wdrożenie roli oponenta.** Przynajmniej jeden z agentów powinien być instruowany, aby za wszelką cenę kwestionować zdanie większości. To zabezpiecza system przed kaskadowym potakiwaniem.
- **Logowanie każdej rundy.** Zapisuj stany pośrednie debaty; bez tego audyt i debugowanie zachowań agentów są niemożliwe.

## Ćwiczenia

1. Uruchom `code/main.py`, a następnie zwiększ liczbę rund do 5. Zaobserwuj zjawisko malejących zysków. W której rundzie proces zbieżności całkowicie się zatrzymuje?
2. Dodaj czwartego agenta pełniacego rolę oponenta, który zawsze kwestionuje stanowisko większości. Czy obecność oponenta poprawia stabilność i poprawność ostatecznego konsensusu?
3. Zaimplementuj logowanie wskaźnika spójności (ułamek agentów popierających opcję większościową) w każdej rundzie. Czy wskaźnik równy 1.0 jest tożsamy z poprawnością merytoryczną odpowiedzi?
4. Przeanalizuj sekcję 4 (Ablations) w artykule Du i in. Odtwórz scenariusze „tylko agenci”, „tylko rundy” oraz „oba” na bazie zaimplementowanego kodu.
5. Zapoznaj się z publikacją „Should We Respect LLMs' Opinions?” (arXiv:2311.17371) i wskaż dwa alternatywne sposoby prowadzenia debaty wykraczające poza klasyczny schemat round-robin (np. debata z sędzią, debata hierarchiczna).

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Społeczeństwo umysłu | „Koncepcja Minsky'ego” | Teoria traktująca inteligencję jako system wyspecjalizowanych procesów. Podstawa debaty wieloagentowej LLM. |
| Debata wieloagentowa | „Agenci dyskutują” | Proces, w którym N agentów generuje, ocenia i modyfikuje odpowiedzi w R rundach, kończący się głosowaniem. |
| Konsensus | „Zgodność agentów” | Stan większościowej zgody w panelu, który nie gwarantuje poprawności logicznej (agenci mogą zgodnie się mylić). |
| Runda debaty | „Krok wymiany zdań” | Jeden pełen cykl, w którym każdy agent zapoznaje się z opiniami innych i aktualizuje swoją odpowiedź. |
| Debata heterogeniczna | „Mieszanie modeli” | Wykorzystanie różnych modeli (np. Claude i GPT) w celu eliminacji skorelowanych błędów tej samej rodziny. |
| Kaskadowe potakiwanie | „Efekt konformizmu” | Błąd polegający na tym, że agenci przyjmują zdanie najbardziej pewnego siebie uczestnika debaty, ignorując błędy. |
| Eksplozja kosztów | „Compute inflation” | Skokowy wzrost liczby zużywanych tokenów wynikający z wielokrotnego przesyłania rosnącej historii debaty. |

## Dalsze czytanie

- [Du i in. — Improving Factuality and Reasoning in Language Models through Multi-Agent Debate](https://arxiv.org/abs/2305.14325) — bazowa publikacja naukowa z ICML 2024.
- [Zhuge i in. — Mindstorms in Natural Language-Based Societies of Mind](https://arxiv.org/abs/2305.17066) — opis eksperymentu NLSOM ze 129 agentami.
- [Should We Respect LLMs' Opinions?](https://arxiv.org/abs/2311.17371) — analiza porównawcza różnych strategii prowadzenia debaty wieloagentowej.
- [Strona projektu Debate](https://composable-models.github.io/llm_debate/) — oficjalne kody źródłowe, prezentacje i dane z analiz ablacyjnych autorów.
