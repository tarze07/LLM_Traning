# Polityka odpowiedzialnego skalowania firmy Anthropic v3.0

> Polityka RSP v3.0 weszła w życie 24 lutego 2026 roku, zastępując wersję z roku 2023. Wprowadza ona dwupoziomowy model łagodzenia ryzyka: podział na działania, które Anthropic podejmie jednostronnie, oraz zalecenia dla całej branży (w tym standardy bezpieczeństwa RAND SL-4). Plany działań w zakresie bezpieczeństwa systemów pionierskich (Frontier Safety Roadmaps) oraz raporty o ryzyku stają się dokumentami cyklicznymi, a nie jednorazowymi publikacjami. Usunięto zobowiązanie do wstrzymania prac (pause commitment) z 2023 roku. Wprowadzono próg „AI R&D-4” (badania i rozwój sztucznej inteligencji na poziomie 4): po jego przekroczeniu Anthropic musi opublikować uzasadnienie bezpieczeństwa (affirmative case), identyfikujące ryzyka niedopasowania (alignment risks) oraz odpowiednie środki zaradcze. Claude Opus 4.6 nie przekracza tego progu. W ogłoszeniu wersji 3.0 Anthropic przyznaje jednak, że „z całą pewnością wykluczenie tej sytuacji staje się trudne”. Organizacja SaferAI oceniła RSP z 2023 roku na 2,2; nową wersję 3.0 oceniono na 1,9, co plasuje Anthropic w kategorii „słabej” (weak RSP) obok OpenAI i DeepMind. Zobowiązania ilościowe z 2023 roku zastąpiono progami jakościowymi, a usunięcie klauzuli o wstrzymaniu prac uznawane jest za największy regres.

**Typ:** Ucz się
**Języki:** Python (stdlib, silnik decyzyjny dotyczący progów RSP)
**Wymagania wstępne:** Faza 15 · 06 (AAR), Faza 15 · 07 (RSI)
**Czas:** ~45 minut

## Problem

Laboratoria rozwijające modele pionierskie (Frontier Labs) publikują zasady skalowania, które łączą w sobie aspekty techniczne, zarządcze oraz sygnały dla organów regulacyjnych. Obecnym standardem Anthropic jest polityka RSP v3.0. Dokładna jej analiza jest kluczowa nie dlatego, że jej przestrzeganie jest prawnie wiążące (ponieważ nie jest), ale dlatego, że ramy te określają sposób, w jaki laboratorium definiuje ryzyko katastrofalne oraz jak komunikuje opinii publicznej niezbędne kompromisy.

Warto przyjrzeć się różnicom między wersjami v3.0 a v2.0. Do nowości należą: plany działań w zakresie bezpieczeństwa systemów pionierskich, raporty o ryzyku oraz próg AI R&D-4. Usunięto natomiast zobowiązanie do wstrzymania prac (pause commitment). Zmodyfikowano strukturę działań łagodzących, dzieląc je na jednostronne zobowiązania Anthropic i rekomendacje branżowe. Niezależny audyt przeprowadzony przez SaferAI obniżył ocenę dokumentu z 2,2 (dla wersji v2.0) do 1,9 (dla wersji v3.0). Pokazuje to, jak polityka bezpieczeństwa może ulec osłabieniu, mimo że zewnętrznie sprawia wrażenie bardziej dojrzałej.

## Koncepcja

### Dwupoziomowy model łagodzenia ryzyka

- **Jednostronne zobowiązania Anthropic**: działania, które firma podejmie niezależnie od zachowań innych laboratoriów (np. wstrzymanie treningu powyżej określonego progu, wdrożenie konkretnych procedur bezpieczeństwa i etapów wdrożeniowych).
- **Zalecenia dla całej branży**: wspólne standardy postępowania proponowane przez Anthropic (w tym standardy bezpieczeństwa RAND SL-4). Nie stanowią one zobowiązań samej firmy Anthropic, a jedynie promowane przez nią postulaty polityczne.

Taki podział nie występował w wersji v2. Oznacza to, że czytelnik musi dokładnie zweryfikować status każdego zadeklarowanego działania. Wszelkie środki bezpieczeństwa zaklasyfikowane jako „Zalecenia dla całej branży” nie są obietnicą realizacji ze strony Anthropic, lecz jedynie postulatem.

### Próg AI R&D-4

To poziom zaawansowania określony w RSP v3.0 jako kolejny kluczowy kamień milowy. Chodzi o model zdolny do opłacalnej automatyzacji znacznej części badań nad sztuczną inteligencją. Gdy Anthropic stwierdzi, że dany model osiągnął te możliwości, musi – przed dalszym skalowaniem – opublikować uzasadnienie bezpieczeństwa (affirmative case) opisujące ryzyko niedopasowania oraz planowane środki zaradcze.

Według komunikatu towarzyszącego wersji 3.0, model Claude Opus 4.6 nie przekracza jeszcze tej granicy. Dokument zaznacza jednak, że „z całą pewnością wykluczenie tej sytuacji staje się trudne”. Sformułowanie to jest istotne – potwierdza, że próg ten jest na tyle bliski, iż stanowi realny punkt odniesienia, a nie czysto spekulacyjną wizję.

Lekcja 6 (zautomatyzowane badanie dopasowania) oraz Lekcja 7 (rekurencyjne samodoskonalenie) bezpośrednio wiążą się z tym progiem. Automatyzacja badań nad dopasowaniem i osiąganie wysokiej jakości wyników w tym obszarze są bezpośrednim dowodem na zbliżanie się do poziomu AI R&D-4.

### Plany bezpieczeństwa i raporty o ryzyku

Wersja v3.0 wprowadza dwa typy cyklicznych dokumentów:

- **Plan działań w zakresie bezpieczeństwa systemów pionierskich (Frontier Safety Roadmap)**: dokument o charakterze prospektywnym, opisujący planowane prace nad bezpieczeństwem, prognozowane możliwości i badania nad łagodzeniem zagrożeń.
- **Raport o ryzyku (Risk Report)**: dokument o charakterze retrospektywnym, sporządzany po wydaniu konkretnego modelu, opisujący zaobserwowane zdolności i ryzyko szczątkowe.

Oba dokumenty są jawne i cyklicznie aktualizowane. Pozwala to na porównanie obietnic zawartych w planach z rzeczywistymi wynikami przedstawionymi w raportach o ryzyku.

### Usunięcie klauzuli o wstrzymaniu prac (pause commitment)

Polityka RSP z 2023 roku zawierała jasne zobowiązanie: w przypadku przekroczenia określonych progów zdolności modelu, proces szkoleniowy miał zostać wstrzymany do czasu wdrożenia odpowiednich środków bezpieczeństwa. W wersji v3.0 to zobowiązanie zastąpiono łagodniejszą procedurą (publikacja uzasadnienia bezpieczeństwa i kontynuacja prac, o ile wdrożono właściwe zabezpieczenia). Analitycy z SaferAI i innych organizacji uznali to za największy regres w nowej polityce.

Argumentem za tą zmianą była trudność w określeniu sztywnych progów ilościowych ze względu na szybkie skalowanie benchmarków. Z kolei kontrargument wskazuje, że klauzula wstrzymania prac była kluczowym elementem uwiarygodniającym politykę bezpieczeństwa; jej usunięcie drastycznie osłabiło to zaangażowanie.

### Ocena organizacji SaferAI

SaferAI to niezależna organizacja analizująca dokumenty typu RSP. W ich publicznej ocenie polityka RSP Anthropic z 2023 roku otrzymała ocenę 2,2 (w skali, gdzie 4,0 to poziom optymalny, a 1,0 to podstawowy). Wersja v3.0 otrzymała jedynie 1,9, co spowodowało spadek Anthropic z poziomu „umiarkowanego” do „słabego” (weak), plasując firmę na równi z OpenAI i DeepMind.

Główne powody obniżenia oceny przez SaferAI:
- Zastąpienie progów ilościowych trudniejszymi do weryfikacji progami jakościowymi.
- Usunięcie sztywnego zobowiązania do wstrzymania prac.
- Opisanie działań po przekroczeniu progu AI R&D-4 w formie ogólnego „uzasadnienia bezpieczeństwa” (affirmative case) zamiast konkretnych kroków zaradczych.
- Oparcie mechanizmów kontrolnych na wewnętrznej grupie doradczej Anthropic (Safety Advisory Group) przy minimalnym udziale niezależnych audytorów.

### Czym ta lekcja nie jest

Nie jest to lekcja poświęcona zgodności z przepisami. RSP v3.0 nie jest regulacją prawną – żadne przepisy nie zmuszają firmy Anthropic do jej przestrzegania. Cel tej lekcji to wyrobienie nawyku wnikliwej i krytycznej analizy podobnych dokumentów. Zasady odpowiedzialnego skalowania są kluczowym sygnaąem wysyłanym przez wiodące laboratoria w kwestiach ryzyka katastrofalnego, a ich właściwa interpretacja to niezbędna kompetencja w pracy z nowoczesnymi systemami AI.

## Jak tego użyć

Skrypt `code/main.py` implementuje prosty moduł ewaluacyjny, który odzwierciedla logikę oceny progów RSP. Na podstawie parametrów modelu oraz uzyskanych wyników w benchmarkach zwraca informację, czy przekroczono próg AI R&D-4, generuje wymagane szablony uzasadnienia bezpieczeństwa (affirmative case) oraz określa, czy wdrożenie może być kontynuowane. Ten uproszczony model ma na celu zilustrowanie założeń logicznych dokumentu.

## Wynik zadania

Plik `outputs/skill-scaling-policy-review.md` służy do weryfikacji dowolnej polityki skalowania (w tym Anthropic, OpenAI, DeepMind lub rozwiązań wewnętrznych) pod kątem zgodności z kryteriami wersji v3.0 (np. dwupoziomowa struktura, progi, zobowiązanie do wstrzymania prac, niezależny audyt).

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Przetestuj działanie na trzech modelach o różnych parametrach. Upewnij się, że moduł prawidłowo identyfikuje przekroczenie progów i generuje odpowiednie szablony dokumentacji.

2. Przeczytaj pełny tekst RSP v3.0 (32 strony). Wskaż wszystkie działania zaklasyfikowane jako „Zalecenia dla całej branży”. Które z nich miałyby status „jednostronnych zobowiązań Anthropic” w wersji v2.0?

3. Zapoznaj się z metodologią oceny RSP opracowaną przez SaferAI. Spróbuj odtworzyć ocenę 1,9 dla wersji v3.0 na podstawie kryteriów w niej zawartych. Który z wskaźników miał największy wpływ na obniżenie oceny?

4. Zaproponuj alternatywne rozwiązanie dla usuniętej klauzuli o wstrzymaniu prac z 2023 roku, które pozwoli zachować wiarygodność deklaracji bezpieczeństwa, jednocześnie rozwiązując problem zdezaktualizowanych benchmarków ilościowych.

5. Porównaj RSP v3.0 z ramami gotowości OpenAI (Preparedness Framework v2, Lekcja 20). Wskaż jeden obszar, w którym polityka Anthropic v3.0 jest bardziej rygorystyczna, oraz jeden, w którym lepiej wypada propozycja OpenAI.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| RSP (Responsible Scaling Policy) | „Polityka skalowania Anthropic” | Dokument określający zasady odpowiedzialnego skalowania; wersja 3.0 weszła w życie 24 lutego 2026 roku |
| AI R&D-4 | „Próg automatyzacji badań” | Poziom rozwoju AI umożliwiający opłacalną automatyzację znaczącej części prac badawczych nad sztuczną inteligencją |
| Uzasadnienie bezpieczeństwa (Affirmative case) | „Uzasadnienie bezpieczeństwa” | Oficjalny dokument wykazujący, że ryzyka zostały zidentyfikowane i wdrożono odpowiednie środki zaradcze |
| Frontier Safety Roadmap | „Plan bezpieczeństwa systemów pionierskich” | Cykliczny dokument opisujący planowane prace nad bezpieczeństwem oraz prognozowane parametry modeli |
| Raport o ryzyku (Risk Report) | „Retrospektywa modelu” | Cykliczny dokument podsumowujący zaobserwowane możliwości i ryzyko szczątkowe po wydaniu modelu |
| Dwupoziomowe łagodzenie (Two-tier mitigation) | „Działania własne a zalecenia branżowe” | Podział na jednostronne zobowiązania firmy Anthropic oraz ogólne zalecenia dla branży |
| Zobowiązanie do wstrzymania prac (Pause commitment) | „Zobowiązanie do pauzy” | Zobowiązanie do przerwania treningu modelu w przypadku przekroczenia progów ryzyka (usunięte w v3.0) |
| Ocena SaferAI | „Niezależna ocena RSP” | Ocena wystawiana przez zewnętrzny podmiot; wersja v3.0 otrzymała wynik 1,9 (spadek z 2,2 w v2.0) |

## Dalsza lektura

- [Anthropic — Polityka odpowiedzialnego skalowania v3.0](https://anthropic.com/responsible-scaling-policy/rsp-v3-0) — pełna 32-stronicowa polityka.
- [Anthropic — ogłoszenie RSP v3.0](https://www.anthropic.com/news/responsible-scaling-policy-v3) — podsumowanie zmian od v2.
- [Anthropic — Frontier Safety Roadmap](https://www.anthropic.com/research/frontier-safety) — stały dokument, do którego link znajduje się w RSP v3.0.
- [Anthropic — Raport o ryzyku: Claude Opus 4.6](https://www.anthropic.com/research/risk-report-claude-opus-4-6) — retrospektywa dotycząca obecnego modelu granicznego.
- [Anthropic — Pomiar autonomii agenta w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — rola autonomii w badaniach nad sztuczną inteligencją.
