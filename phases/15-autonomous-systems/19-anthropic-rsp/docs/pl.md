# Polityka odpowiedzialnego skalowania antropicznego v3.0

> RSP v3.0 weszło w życie 24 lutego 2026 r., zastępując politykę z 2023 r. Dwupoziomowe łagodzenie: to, co Anthropic zrobi jednostronnie, a to, co jest sformułowane jako zalecenie dla całej branży (w tym standardy bezpieczeństwa RAND SL-4). Dodaje plany działania dotyczące bezpieczeństwa granicznego i raporty dotyczące ryzyka jako dokumenty stałe, a nie jednorazowe produkty. Wycofuje zobowiązanie dotyczące pauzy na 2023 r. Wprowadza próg badań i rozwoju sztucznej inteligencji-4: po jego przekroczeniu firma Anthropic musi opublikować pozytywną opinię, identyfikującą ryzyko nieprawidłowego ustawienia i środki zaradcze. Claude Opus 4.6 tego nie przekracza. Anthropic stwierdza w ogłoszeniu wersji 3.0, że „z całą pewnością wykluczenie tej sytuacji staje się trudne”. SaferAI oceniło RSP na rok 2023 na 2,2; obniżyli wersję 3.0 do 1.9, umieszczając Anthropic w „słabej” kategorii RSP obok OpenAI i DeepMind. Progi jakościowe zastąpiły zobowiązania ilościowe na 2023 r.; usunięcie klauzuli pauzy jest najostrzejszą regresją.

**Typ:** Ucz się
**Języki:** Python (stdlib, silnik decyzyjny dotyczący progów RSP)
**Wymagania wstępne:** Faza 15 · 06 (AAR), Faza 15 · 07 (RSI)
**Czas:** ~45 minut

## Problem

Frontier Labs publikują zasady skalowania, które są częściowo dokumentami technicznymi, częściowo dokumentami dotyczącymi zarządzania, a częściowo sygnałami dla organów regulacyjnych. Aktualnym dokumentem Anthropic jest RSP v3.0. Uważne zapoznanie się z nim ma znaczenie nie dlatego, że zgodność z nim jest wiążąca (nie jest), ale dlatego, że ramy kształtują sposób, w jaki laboratorium postrzega ryzyko katastrofalne i sposób komunikowania opinii publicznej kompromisów.

Przydatną jednostką jest różnica v3.0 i v2.0. Co zostało dodane: plany działania w zakresie bezpieczeństwa granicznego, raporty dotyczące ryzyka, próg badań i rozwoju sztucznej inteligencji-4. Co zostało usunięte: zobowiązanie dotyczące pauzy na 2023 r. Co zostało przeformułowane: dwupoziomowy harmonogram działań łagodzących podzielony na jednostronne zalecenia antropiczne i zalecenia branżowe. Zewnętrzna recenzja — SaferAI — obniżyła ocenę z 2,2 (wersja 2) do 1,9 (wersja 3.0). W ten sposób polityka skalowania może stać się mniej rygorystyczna, a jednocześnie wyglądać na bardziej dopracowaną.

## Koncepcja

### Dwupoziomowy harmonogram łagodzenia skutków

- **Jednostronne działania Anthropic**: co zrobi Anthropic niezależnie od tego, co zrobią inne laboratoria. Szkolenia zatrzymują się powyżej progu, określone środki bezpieczeństwa, określone bramki wdrożeniowe.
- **Zalecenia dla całej branży**: co według Anthropic branża powinna zrobić wspólnie. Zawiera standardy bezpieczeństwa RAND SL-4. Nie są to zobowiązania ze strony Anthropic; są zwolennikami polityki.

Dwupoziomowa struktura nie była dostępna w wersji 2. Oznacza to, że czytelnik musi sprawdzić, w której kolumnie znajduje się każde zobowiązanie. Środek bezpieczeństwa w kolumnie „Zalecenia dla całej branży” nie jest obietnicą firmy Anthropic; to nadzieja Anthropic.

### Próg badań i rozwoju AI-4

Jest to poziom możliwości, który RSP v3.0 określa jako kolejny ważny próg. W szczególności: model, który mógłby zautomatyzować znaczną część badań nad sztuczną inteligencją po konkurencyjnych kosztach. Gdy firma Anthropic uzna, że ​​model ją spełnia, musi opublikować potwierdzenie potwierdzające, identyfikujące ryzyko nieprawidłowego dopasowania i środki zaradcze przed kontynuowaniem skalowania.

Claude Opus 4.6 nie przekracza tego zgodnie z zapowiedzią wersji 3.0. W dokumencie dodaje się: „Z całą pewnością wykluczenie tej sytuacji staje się trudne”. To sformułowanie ma znaczenie; przyznaje, że próg jest wystarczająco blisko, aby stanowić istotne zagrożenie, a nie granicę spekulacyjną.

Lekcja 6 (badanie automatycznego dopasowania) i lekcja 7 (samodoskonalenie rekurencyjne) bezpośrednio wpływają na ten próg. Badacze zajmujący się automatycznym dopasowywaniem przekraczający poprzeczki jakości badań są dowodem na to, że zbliża się próg 4 w zakresie badań i rozwoju sztucznej inteligencji.

### Plany działania dotyczące bezpieczeństwa granicznego i raporty dotyczące ryzyka

Wersja 3.0 podnosi dwa typy artefaktów do stałych dokumentów:

- **Plan działania dotyczący bezpieczeństwa granicznego**: dokument wybiegający w przyszłość, opisujący planowane prace związane z bezpieczeństwem, oczekiwania w zakresie możliwości i badania łagodzące.
- **Raport o ryzyku**: dokument retrospektywny dotyczący konkretnych modeli po wydaniu, opisujący zaobserwowane możliwości i ryzyko szczątkowe.

Obydwa są publiczne. Obydwa są aktualizowane w zadeklarowanej kadencji. Narzędzie jest następujące: czytelnik może sprawdzić, jak to, co Anthropic obiecała zrobić w planie działania, ma się do tego, co podaje w raporcie ryzyka.

### Usunięcie klauzuli pauzy

RSP na 2023 r. zawierał wyraźne zobowiązanie dotyczące pauzy: jeśli model przekroczył określone progi możliwości, szkolenie zostanie wstrzymane do czasu wprowadzenia środków łagodzących. wersja 3.0 zastępuje wyraźną pauzę łagodniejszym sformułowaniem (opublikuj argument potwierdzający, kontynuuj, jeśli środki łagodzące są odpowiednie). SaferAI i inni analitycy bezpośrednio nazwali to najsilniejszą regresją w nowym dokumencie.

Argument polityczny przemawiający za zmianą: progi ilościowe na 2023 r. okazały się nieosiągalne w przypadku wskaźników odniesienia w zakresie zdolności na okres 2026 r., ponieważ same poziomy odniesienia zostały przeskalowane. Kontrargument: klauzula pauzy w polityce skalowania jest narzędziem zobowiązania; jej usunięcie pozbawia wiarygodności polityki.

### Obniżenie wersji SaferAI

SaferAI to niezależna organizacja oceniająca dokumenty w stylu RSP. Ich publiczna ocena: 2023 Anthropic RSP uzyskała wynik 2,2 (w skali, w której 4,0 to najlepszy aktualny RSP, a 1,0 to nominalny). wersja 3.0 uzyskała ocenę 1,9. To przesunęło Anthropic z „umiarkowanej” do „słabej”, dołączając do OpenAI i DeepMind w kategorii słabej.

Czynniki obniżenia wersji według SaferAI:
- Progi jakościowe zastąpiły progi ilościowe.
- Usunięto zobowiązanie do wstrzymania.
- Ograniczenia progowe badań i rozwoju AI w zakresie 4 są opisywane jako „przypadek potwierdzający”, a nie konkretne środki.
- Mechanizmy przeglądu zależą od Grupy Doradczej ds. Bezpieczeństwa firmy Anthropic, pod ograniczonym niezależnym nadzorem.

### Czym ta lekcja nie jest

To nie jest lekcja przestrzegania zasad. RSP v3.0 nie jest rozporządzeniem; nic nie zmusza Anthropic do pójścia za tym. Lekcja polega na tym, aby czytać dokument ze swoistością i sceptycyzmem, na jaki zasługuje. Polityka skalowania to główny publiczny sygnał, jaki laboratoria graniczne emitują na temat sytuacji stwarzającej ryzyko katastrofalne. Dobre ich odczytanie jest praktyczną umiejętnością dla każdego, którego praca zależy od możliwości granicznych.

## Użyj tego

`code/main.py` implementuje mały silnik decyzyjny, który odzwierciedla kształt oceny progu RSP: biorąc pod uwagę model kandydujący i zestaw pomiarów zdolności, zwróć informację, czy próg badań i rozwoju sztucznej inteligencji-4 został przekroczony, wymagane sekcje przypadków potwierdzających i czy wdrożenie może być kontynuowane. To celowo proste; chodzi o to, aby logika dokumentu była jasna.

## Wyślij to

`outputs/skill-scaling-policy-review.md` sprawdza politykę skalowania (Anthropic, OpenAI, DeepMind lub wewnętrzną) pod kątem odniesienia do wersji 3.0: struktura dwupoziomowa, progi, zobowiązania do wstrzymania, niezależny przegląd.

## Ćwiczenia

1. Uruchom `code/main.py`. Podaj trzy syntetyczne modele o różnych poziomach możliwości. Potwierdź, że oceniający próg zachowuje się zgodnie z oczekiwaniami i tworzy właściwy szablon przypadku twierdzącego.

2. Przeczytaj w całości RSP v3.0 (32 strony). Zidentyfikuj każde zobowiązanie znajdujące się na poziomie „rekomendacji dla całej branży”. Które z tych zobowiązań byłoby „jednostronne antropiczne” w wersji 2?

3. Przeczytaj metodologię oceniania RSP SaferAI. Odtwórz ich ocenę 1,9 dla wersji 3.0, stosując ich rubryki w dokumencie. Który wiersz rubryk najbardziej spowodował obniżenie oceny?

4. Usunięto zobowiązanie dotyczące pauzy na 2023 r. Zaproponować zobowiązanie zastępcze, które zachowa wiarygodność polityki, jednocześnie uznając problem związany ze zmianą skali poziomu referencyjnego na 2026 r.

5. Porównaj RSP v3.0 z OpenAI gotowości Framework v2 (lekcja 20). Wybierz jeden obszar, w którym wersja 3.0 jest silniejsza. Wybierz jeden obszar, w którym ramy gotowości są silniejsze.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| RSP | „Polityka skalowania Anthropic” | Polityka odpowiedzialnego skalowania; wersja 3.0 obowiązuje od 24 lutego 2026 r. |
| Badania i rozwój sztucznej inteligencji-4 | „Próg automatyzacji badań” | Możliwość automatyzacji znacznych badań nad sztuczną inteligencją po konkurencyjnych kosztach |
| Sprawa twierdząca | „Uzasadnienie bezpieczeństwa” | Opublikowany argument, że ryzyko zostało zidentyfikowane, a środki zaradcze odpowiednie |
| Plan działania w zakresie bezpieczeństwa granicznego | „Plan na przyszłość” | Stały dokument dotyczący planowanych prac związanych z bezpieczeństwem i oczekiwanych możliwości |
| Raport ryzyka | „Retrospektywa o modelu” | Stały dokument dotyczący zaobserwowanych zdolności i ryzyka szczątkowego po zwolnieniu |
| Łagodzenie dwupoziomowe | „Jednostronne kontra przemysł” | Zobowiązania antropiczne a zalecenia branżowe, rozdzielone |
| Wstrzymaj zaangażowanie | „Klauzula 2023” | Wyraźna obietnica wstrzymania szkolenia; usunięto w wersji 3.0 |
| Ocena SaferAI | „Niezależny stopień RSP” | Rubryka strony trzeciej; wersja 3.0 uzyskała wynik 1,9 (wersja 2 wynosiła 2,2) |

## Dalsze czytanie

- [Anthropic — Polityka odpowiedzialnego skalowania v3.0](https://anthropic.com/responsible-scaling-policy/rsp-v3-0) — pełna 32-stronicowa polityka.
- [Anthropic — ogłoszenie RSP v3.0](https://www.anthropic.com/news/responsible-scaling-policy-v3) — podsumowanie zmian od v2.
- [Anthropic — Frontier Safety Roadmap](https://www.anthropic.com/research/frontier-safety) — stały dokument, do którego link znajduje się w RSP v3.0.
- [Anthropic — Raport o ryzyku: Claude Opus 4.6](https://www.anthropic.com/research/risk-report-claude-opus-4-6) — retrospektywa dotycząca obecnego modelu granicznego.
- [Anthropic — Pomiar autonomii agenta w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — łączy prace badawczo-rozwojowe nad sztuczną inteligencją w praktyce mierzoną autonomią.