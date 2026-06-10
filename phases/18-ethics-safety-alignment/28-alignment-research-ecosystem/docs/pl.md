# Ekosystem badań nad wyrównaniem — MATS, Redwood, Apollo, METR

> Pięć organizacji definiuje warstwę badań niezwiązanych z laboratorium na rok 2026. MATS (ML Alignment & Theory Scholars): ponad 527 badaczy od końca 2021 r., ponad 180 artykułów, ponad 10 tys. cytowań, indeks h 47; kohorta latem 2024 r. zarejestrowana jako 501(c)(3) z około 90 naukowcami i 40 mentorami; 80% absolwentów sprzed 2025 r. pracuje nad bezpieczeństwem w ponad 200 firmach Anthropic, DeepMind, OpenAI, UK AISI, RAND, Redwood, METR, Apollo. Redwood Research: stosowane laboratorium dopasowujące założone przez Bucka Shlegerisa; wprowadzono kontrolę AI (lekcja 10); współpracuje z brytyjską AISI w sprawach związanych z bezpieczeństwem sterowania. Apollo Research: oceny planów przed wdrożeniem dla laboratoriów przygranicznych; jest autorem In-Context Scheming (Lekcja 8) i W kierunku bezpieczeństwa dla AI Scheming. METR (Model Evaluation and Threat Research): oceny zdolności oparte na zadaniach, badania horyzontu czasowego w ramach zadań autonomicznych; „Wspólne elementy polityki bezpieczeństwa Frontier AI” porównuje ramy laboratoryjne. Badania Eleos AI: oceny dobrostanu modelu przed wdrożeniem (lekcja 19); przeprowadził ocenę dobrostanu Claude Opus 4.

**Typ:** Ucz się
**Języki:** brak
**Wymagania wstępne:** Faza 18 · 01-27 (poprzednie lekcje fazy 18)
**Czas:** ~45 minut

## Cele nauczania

- Zidentyfikować pięć organizacji ekosystemu badań nad dostosowaniem niezwiązanym z laboratorium i ich podstawowe wyniki.
- Opisać skalę projektu MATS (naukowcy, artykuły, indeks h) i jego rolę jako źródła talentów.
- Opisać program AI Control firmy Redwood i jej partnerstwo z brytyjską AISI.
- Opisać metodologię oceny opartą na zadaniach METR.

## Problem

Laboratoria graniczne (Lekcja 18) opracowują wewnętrznie oceny bezpieczeństwa i publikują wybrane wyniki. Ekosystem poza laboratoriami to miejsce, w którym weryfikowane są oceny, gdzie po raz pierwszy odkrywane są nowe tryby awarii i gdzie szkoli się talenty. Zrozumienie ekosystemu pomaga zinterpretować, którym wynikom badań ufa kto.

## Koncepcja

### MATS (naukowcy zajmujący się wyrównaniem i teorią ML)

Rozpoczęto pod koniec 2021 r. Program mentoringu badawczego; uczeni spędzają 10–12 tygodni ze starszym badaczem nad konkretnym problemem dopasowania.

Skala (2026):
- 527+ badaczy od samego początku.
- Opublikowano ponad 180 artykułów.
- Ponad 10 tys. cytatów.
- indeks h 47.
- Lato 2024: 90 stypendystów + 40 mentorów; zarejestrowana jako 501(c)(3).

Wyniki kariery: ~80% absolwentów, którzy ukończyli studia przed 2025 rokiem, pracuje nad bezpieczeństwem. Ponad 200 osób w Anthropic, DeepMind, OpenAI, UK AISI, RAND, Redwood, METR, Apollo.

### Badania sekwoi

Laboratorium osiowania stosowanego. Założona przez Bucka Shlegerisa. Wprowadzono program kontroli AI (lekcja 10). Współpracuje z brytyjską AISI w sprawach związanych z bezpieczeństwem sterowania. Doradza DeepMind i Anthropic w zakresie projektowania ewaluacji.

Artykuły kanoniczne: Greenblatt, Shlegeris i in., „AI Control” (arXiv:2312.06942, ICML 2024); Fałszowanie wyrównania (Greenblatt, Denison, Wright i in., arXiv:2412.14093, wspólne z Anthropic).

Styl: konkretne modele zagrożeń, najgorsi przeciwnicy, konkretne protokoły, które można poddać testom warunków skrajnych.

### Badania Apollo

Oceny schematów przed wdrożeniem dla laboratoriów granicznych. Autorskie schematy w kontekście (lekcja 8, arXiv:2412.04984). Partner we współpracy szkoleniowej dotyczącej przeciwdziałania intrygom OpenAI w 2025 r. Produkuje „W stronę przypadków bezpieczeństwa dla planowania sztucznej inteligencji” (2024).

Styl: oceny ustalające agenturę, w których może pojawić się oszustwo; rozkład na trzy filary (niedostosowanie, zorientowanie na cel, świadomość sytuacyjna).

### METR (ocena modelu i badanie zagrożeń)

Oceny zdolności oparte na zadaniach. Badania horyzontalne czasowe realizacji zadań autonomicznych. „Common Elements of Frontier AI Safety Policies” (metr.org/common-elements, 2025) porównuje ramy laboratoryjne.

Współautor szkicu przypadku bezpieczeństwa AI Scheming wraz z Apollo.

Styl: długoterminowe oceny zadań, empiryczny pomiar możliwości, synteza ram.

### Badania nad sztuczną inteligencją Eleosa

Oceny dobrostanu modelu przed wdrożeniem. Przeprowadzono ocenę dobrostanu Claude Opus 4 udokumentowaną w sekcji 5.3 karty systemowej. Zapewnia zewnętrzną kontrolę metodologii dla twierdzeń dotyczących dobrostanu z Lekcji 19.

### Przepływ

MATS szkoli badaczy. Absolwenci trafiają do Anthropic, DeepMind, OpenAI (zespoły bezpieczeństwa laboratoryjnego) lub do Redwood, Apollo, METR, Eleos (ocena zewnętrzna). Zewnętrzni ewaluatorzy współpracują z laboratoriami i brytyjską organizacją AISI/CAISI. Publikacje dostarczają ekosystemowi materiału do MATS dla następnej kohorty.

### Dlaczego ta warstwa ma znaczenie

Oceny pochodzące z jednego źródła są zawodne: w laboratoriach oceniających własne modele występuje strukturalny konflikt interesów. Zewnętrzni oceniający mogą zgłaszać i weryfikować tryby awarii, które laboratorium może zaniżać. Artykuł uśpionych agentów z 2024 r. (lekcja 7) brzmiał: Anthropic + Redwood; Fałszowanie charakteru było Antropiczne + Sekwoi; Planowanie kontekstowe to Apollo; Anti-Scheming to Apollo + OpenAI. Struktura wieloorganizacyjna to kontrola jakości.

### Gdzie to pasuje do fazy 18

Odniesienia do lekcji 7-11 Praca Redwood i Apollo; Lekcja 18 odnosi się do porównania ram METR; Lekcja 19 nawiązuje do Eleosa. Lekcja 28 to wyraźna mapa organizacyjna ekosystemu, na którym opiera się reszta fazy.

## Użyj tego

Brak kodu. Przeczytaj „Wspólne elementy polityki bezpieczeństwa Frontier AI” firmy METR jako przykład tego, jak zewnętrzna synteza wnosi wartość dodaną do prac nad polityką wewnętrzną laboratorium.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-ecosystem-map.md`. Biorąc pod uwagę wniosek lub ocenę dotyczącą dostosowania, identyfikuje organizację, miejsce publikacji i styl metodologiczny, a także przeprowadza kontrole krzyżowe ze znanymi organizacjami-odpowiednikami.

## Ćwiczenia

1. Wybierz jeden artykuł z lekcji 7-15 i wskaż zaangażowane organizacje. Porównaj autorów z absolwentami MATS i obecnymi powiązaniami z ekosystemami.

2. Przeczytaj „Wspólne elementy polityki bezpieczeństwa granicznej sztucznej inteligencji” METR. Zidentyfikuj trzy zbieżności między laboratoriami, na które zwracają uwagę, oraz dwie największe rozbieżności.

3. Wyniki kariery MATS to ~80% bezpieczeństwa. Omów, czy ta presja selekcyjna ma charakter adaptacyjny (trenuje pole), czy stronniczy (odfiltrowuje pozycje heterodoksyjne).

4. Redwood i Apollo zajmują się kontrolą/planowaniem, ale w różnych stylach. Wybierz tryb awarii i opisz, w jaki sposób każdy z nich miałby go zbadać.

5. Eleos AI jest jedyną organizacją o charakterze czysto modelowym. Zaprojektuj hipotetyczną drugą organizację skupioną na innej kwestii związanej z dobrostanem (wolność poznawcza, wcielenie robotów itp.) i przedstaw jej metodologię.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| MATY | „program mentorski” | Naukowcy zajmujący się wyrównaniem i teorią ML; 527+ badaczy od 2021 r. |
| Badania sekwoi | „laboratorium kontrolne” | Zastosowane wyrównanie; Autorzy AI Control; Brytyjski partner AISI |
| Badania Apollo | „podstępne ewaluacje” | Oceny planów przed wdrożeniem dla laboratoriów przygranicznych |
| METR | „ocena horyzontu zadań” | oceny zdolności oparte na zadaniach; synteza ram |
| Eleos AI | „laboratorium dobrostanu” | Oceny dobrostanu modeli przed wdrożeniem |
| Kanał talentów | „MATA -> laboratoria” | Absolwenci MATS napływają do Anthropic, DM, OpenAI, Redwood, Apollo, METR |
| Ocena zewnętrzna | „kontrola nielaboratoryjna” | Ocena nie została przeprowadzona przez producenta modelu; dodaje wiarygodności |

## Dalsze czytanie

- [MATS (ML Alignment & Theory Scholars)](https://www.matsprogram.org/) — program mentorski
– [Redwood Research](https://www.redwoodresearch.org/) – dokumenty dotyczące kontroli AI
- [Apollo Research] (https://www.apolloresearch.ai/) — planowanie ocen
- [METR — Common Elements of Frontier AI Safety Policies](https://metr.org/blog/2025-03-26-common-elements-of-frontier-ai-safety-policies/) — porównanie ram
- [Eleos AI Research](https://www.eleosai.org/research) — metodologia modelowego dobrostanu