# Tryby awarii — MAST, myślenie grupowe, monokultura, błędy kaskadowe

> Taksonomia referencyjna na rok 2026 to **MAST** (Cemri et al., NeurIPS 2025, arXiv:2503.13657), wyprowadzona z 1642 śladów wykonania w 7 najnowocześniejszych MAS typu open source, wykazujących **wskaźnik awaryjności 41–86,7%**. Trzy główne kategorie: **Problemy ze specyfikacją** (41,77%) — niejednoznaczność roli, niejasne definicje zadań; **Błędy koordynacji** (36,94%) — awarie komunikacji, desynchronizacja stanu; **Luki w weryfikacji** (21,30%) — brak walidacji, brak kontroli jakości. Rodzina **Groupthink** (arXiv:2508.05687) dodaje: upadek monokultury (ten sam model podstawowy → skorelowane niepowodzenia), błąd konformistyczny (agenci wzmacniają wzajemne błędy), wadliwą teorię umysłu, dynamikę o mieszanych motywach, kaskadowe błędy w niezawodności. Przykład kaskadowy: burze ponownych prób, w przypadku których niepowodzenie płatności powoduje ponawianie zamówień, co powoduje ponowne próby inwentaryzacji, co przeciąża usługę magazynowania (10-krotne obciążenie w ciągu sekund — wymaga wyłączników automatycznych). Zatrucie pamięci: halucynacje jednego agenta przedostają się do pamięci wspólnej, agenci na dalszym planie traktują to jako fakt; Dokładność maleje stopniowo, co sprawia, że ​​diagnoza przyczyny źródłowej jest bolesna. **STRATUS** (NeurIPS 2025) raportuje 1,5-krotną poprawę skuteczności łagodzenia skutków dzięki wyspecjalizowanym agentom do wykrywania/diagnostyki/walidacji. W tej lekcji tryby awarii traktowane są jako pierwszorzędne cele inżynieryjne.

**Typ:** Ucz się
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 13 (pamięć współdzielona), faza 16 · 14 (konsensus i BFT), faza 16 · 15 (topologia głosowania i debaty)
**Czas:** ~75 minut

## Problem

Systemy wieloagentowe zawodzą w przypadku rzeczywistych zadań w 41–86,7% przypadków (Cemri i in. 2025 zmierzyli to na podstawie 7 MAS typu open source). Nie można tego debugować poprzez „po prostu dodaj więcej agentów”. Awarie mają przyczyny strukturalne. Taksonomia MAST podaje kategorie. W tej lekcji każdą kategorię przypisano do konkretnego wzorca wykrywania, diagnozowania i łagodzenia skutków, dzięki czemu liczby nie będą wyglądać na arbitralne.

Praktyka produkcyjna na rok 2026 polega na traktowaniu trybów awarii jako danych wejściowych do projektu. Twoja architektura nie jest „wystarczająco dobra”, dopóki nie będziesz w stanie wskazać każdej kategorii MAST i nazwać wdrożone środki zaradcze.

## Koncepcja

### Kategorie MASZTÓW

**Problemy ze specyfikacją (41,77% niepowodzeń).** Zadanie agenta nie zostało wystarczająco ściśle określone. Przykłady:

- Niejednoznaczność roli: obaj agenci myślą, że są recenzentami.
- Zadanie niedookreślone: ​​„podsumuj”, gdy użytkownik chciał określonego kąta.
- Kryteria sukcesu ukryte: agent nie jest w stanie stwierdzić, czy mu się udało.

Środki łagodzące:
- Napisz wyraźne umowy dotyczące ról. Podpowiedź każdego agenta określa, co robi *a czego nie robi*.
- Testy akceptacyjne dla każdego zadania. Przed uruchomieniem agenta zdefiniuj „gotowe wygląda jak X”.
- Kontrola specyfikacji przed lotem: oddzielny agent sprawdza definicję zadania przed wysyłką.

**Błędy koordynacji (36,94%).** Załamania komunikacji lub stanu.

Przykłady:
- Dwóch agentów aktualizuje stan współdzielony bez synchronizacji.
- Utrata wiadomości pomiędzy agentami (awaria kolejki, przekroczenie limitu czasu).
- Dryf stanu: agent A uważa, że ​​zadanie zostało wykonane; agent B nadal wykonuje.

Środki łagodzące:
- Wersjonowany stan współdzielony z optymistyczną współbieżnością.
- Wyraźne potwierdzenie krytycznych wiadomości (ponów próbę do momentu potwierdzenia).
- Okresowe punkty kontrolne synchronizacji stanu; wcześnie wykryć dryf.

**Luki w weryfikacji (21,30%).** Brak niezależnej kontroli wyników.

Przykłady:
- Jeden agent twierdzi, że osiągnął sukces; nikt nie weryfikuje.
- Każdy z łańcuchów agentów ufa wynikom przeora.
- Brak pokrycia testowego w przypadku pojawiającego się złożonego zachowania.

Środki łagodzące:
- Niezależny agent weryfikujący (lekcja 13). Tylko do odczytu, niezależny dostęp do źródła.
- Jawna umowa przekazania: „Wyjście A musi przejść moduł sprawdzający C, zanim rozpocznie się B”.
- Rejestrowanie wyników do analizy post-hoc.

### Rodzina myślenia grupowego (arXiv:2508.05687)

Pięć powiązanych niepowodzeń, gdy środki homogenizują się lub naśladują nawzajem:

**Upadek monokultury.** Ten sam model podstawowy lub dane szkoleniowe → skorelowane błędy. Kiedy trzech agentów dzieli LLM, dzielą się swoimi halucynacjami.

**Stronniczość konformizmu.** Agenci dostosowują się do najgłośniejszego lub najbardziej pewnego siebie partnera, nawet jeśli się mylą.

**Niedostateczna ToM.** Agenci nie modelują wzajemnie swoich przekonań; koordynacja się rozpada (lekcja 18).

**Dynamika o mieszanych motywach.** Agenci z częściowo wyrównanymi motywacjami dryfują w stronę kompromisu pośrodku, co nikogo nie satysfakcjonuje.

**Kaskadowe awarie niezawodności.** Wzorzec błędów jednego komponentu wyzwala wzorce błędów w komponentach zależnych.

### Przykład kaskadowy — burza ponownych prób

Klasyczny wzorzec incydentów z 2026 r.:

```
payment service fails 10% of requests
   ↓
order agent retries payment (exponential backoff but naive)
   ↓
each retry is a new order-inventory check
   ↓
inventory service sees 2x normal load
   ↓
inventory service starts timing out
   ↓
every order retries inventory check
   ↓
inventory service sees 10x normal load
   ↓
cluster goes down
```

Rozwiązanie jest klasyczne: **wyłączniki**. Gdy poziom błędów w dalszej części transmisji przekracza próg, zwarcie z wynikami zapisanymi w pamięci podręcznej lub domyślnymi. Plus ograniczone budżety ponownych prób na każde żądanie.

Wyłączniki automatyczne to jedne z niewielu wieloagentowych rozwiązań łagodzących awarie, które można pożyczyć bezpośrednio z systemów rozproszonych, bez modyfikacji.

### Zatrucie pamięci (ponowne spojrzenie)

Z lekcji 13: halucynacje jednego agenta stają się faktem wynikającym z pamięci wspólnej; Agenci niższego szczebla opierają się na zatrutym fakcie. W kategoriach MAST jest to luka weryfikacyjna w warstwie pamięci współdzielonej.

Objawem jest stopniowy spadek dokładności. Nie dostaniesz awarii; otrzymujesz powolny dryf, który jest trudny do wykorzenienia.

Środki zaradcze: dziennik tylko do dodawania, pochodzenie, weryfikator niezapisywalny. Omówiono to już w lekcji 13.

### STRATUS — wyspecjalizowane agenty do wykrywania awarii

STRATUS (NeurIPS 2025) zgłasza 1,5-krotną poprawę skuteczności łagodzenia skutków po wdrożeniu:

- **Agent detekcyjny.** Obserwuje wzorce objawów (wysoki poziom niezgodności, skoki ponownych prób, dryf dokładności).
- **Agent diagnostyczny.** Biorąc pod uwagę objawy, wnioskuje prawdopodobną przyczynę pierwotną na podstawie taksonomii MAST.
- **Środek walidujący.** Po zastosowaniu środka łagodzącego sprawdza, czy objawy ustąpiły.

Jest to reakcja na incydenty w stylu SRE, stosowana w systemach agentów. Wszystkie trzy role mogą być agentami LLM ze specjalistycznymi podpowiedziami.

### Audyt trybu awaryjnego

Najlepszą praktyką na rok 2026 jest coroczny (lub dla każdej wersji głównej) audyt trybu awaryjnego:

1. **Próbka śledzenia.** Zbierz ~1000 rzeczywistych śladów wykonania.
2. **Kategoryzuj.** W przypadku niepowodzeń każdego śladu przyporządkuj je kategoriom MAST + Groupthink.
3. **Oblicz współczynnik awaryjności według kategorii.** Które kategorie dominują w Twoim systemie?
4. **Ograniczenia rang.** Która poprawka wyeliminuje najwięcej błędów?
5. **Wybierz 2-3 środki łagodzące.** Wdrożyć; ponowny audyt w następnym kwartale.

Dyscyplina jest ważniejsza niż konkretne wybory. Bez audytów awarie zamieniają się w hałas i nigdy nie są systematycznie usuwane.

### Kiedy systemy ulegają cichej awarii

Najbardziej niebezpieczną kategorią awarii jest cicha awaria poprawności. Można monitorować system, który ulega głośnej awarii (awaria, wyjątek, alarm). System generujący prawdopodobne, ale błędne wyniki nie może zostać wykryty w dziennikach wyjątków. Właśnie dlatego luki weryfikacyjne są najdroższą kategorią w przeliczeniu na awarię, chociaż w przeliczeniu wynoszą jedynie 21,30%.

Zainwestuj w:
- Przegląd człowieka na podstawie próbki.
- Testy regresji złotego zbioru danych.
- Międzyagentowa kontrola krzyżowa ważnych wyników.

### Awaria vs powolna awaria

Niektóre awarie są natychmiastowe; niektóre są powolne. Natychmiastowe awarie (przekroczenie limitu czasu, niezgodność schematu, błąd uwierzytelnienia) są tanie do wykrycia. Powolne awarie (zatrucie pamięci, dryf monokultury, niejednoznaczność ról) są kosztowne w wykrywaniu i zapobieganiu.

Posunięcie inżynieryjne na rok 2026: instrumenty zastępcze o powolnej awaryjności, umożliwiające wychwytywanie dryftu, zanim stanie się on widocznym błędem. Współczynnik uzgadniania, współczynnik ponownych prób, rozkład długości danych wyjściowych i odległość edycji pomiędzy kolejnymi wersjami agenta to przydatne wskaźniki zastępcze.

## Zbuduj to

`code/main.py` implementuje:

- `FailureTaxonomy` — kategoryzuje symulowane zdarzenia w kategorie MAST + Groupthink.
- `CircuitBreaker` — wzór klasyczny; otwiera się, gdy poziom błędów przekracza próg.
- `RetryStormSimulator` — pokazuje awarię kaskadową; włącza/wyłącza wyłącznik automatyczny.
- `DetectionAgent` — skrypt dopasowujący objawy w stylu STRATUS.

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik:
- ponów próbę burzy bez wyłącznika automatycznego: pojawiają się błędy w inwentarzu (symulowane).
- z wyłącznikiem: czapka na progu; obsługiwane odpowiedzi w trybie awaryjnym.
- agent detekcyjny flaguje wzorzec i nadaje nazwę kategorii MAST.

## Użyj tego

`outputs/skill-mast-auditor.md` uruchamia audyt trybu awaryjnego w stylu MAST w systemie wieloagentowym. Ślady → kategoryzacja → ranking łagodzenia.

## Wyślij to

Dyscyplina awaryjna w produkcji:

- **Audyt MAST kwartalny.** Nie roczny. Kategorie zmieniają się wraz z rozwojem systemu.
- **Wszędzie wyłączniki automatyczne.** Każde połączenie wychodzące do dowolnej zależnej usługi. Domyślny próg otwarcia przy poziomie błędu 5–10%.
- **Złote zbiory danych.** Małe, wysokiej jakości, ręcznie kontrolowane. Test regresyjny przeciwko nim co tydzień.
- **STRATUS trio.** Detekcja + Diagnoza + Walidacja Agenci monitorujący produkcję. Zacznij od samego środka wykrywającego; dodaj diagnozę, gdy objawy są głośne.
- **Budżet awarii.** Jawny docelowy poziom usług dla wskaźnika awaryjności według kategorii. Przekroczenie budżetu powoduje rozmowę o wstrzymaniu wysyłki.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że wyłącznik automatyczny zamyka burzę ponownej próby. Zmieniaj próg awarii i obserwuj kompromis.
2. Zaimplementuj **wolno działający serwer proxy**: współczynnik zgodności pomiędzy 3 równoległymi agentami. Gdy gwałtownie spadnie, uruchom alert. Symuluj dryf monokultury, stopniowo korelując wyniki agentów.
3. Przeczytaj Cemri i in. (arXiv:2503.13657). Wybierz jeden z 7 systemów MAS i zmapuj jego 3 główne kategorie awarii. Jak mają się one do przewidywań MAST?
4. Przeczytaj artykuł Groupthink (arXiv:2508.05687). Określ, który z pięciu wzorców jest najtrudniejszy do wykrycia w środowisku produkcyjnym. Zaproponuj metrykę zastępczą.
5. Zaprojektuj trio w stylu STRATUS dotyczące wykrywania, diagnozy i walidacji dla konkretnego, znanego Ci systemu wieloagentowego. Na jakie objawy zwraca uwagę detekcja? Jakie środki łagodzące zaleca diagnostyka? W jaki sposób walidacja potwierdza ich działanie?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| MASZT | „Taksonomia 2026” | Cemri 2025; 3 kategorie główne + 14 podtypów awarii. |
| Problem ze specyfikacją | „Niejednoznaczność roli” | Niedodefiniowane zadanie lub rola; agenci nie wiedzą, co robić. |
| Błąd koordynacji | „Dryf stanu” | Awaria komunikacji lub synchronizacji pomiędzy agentami. |
| Luka w weryfikacji | „Nikt nie sprawdzał” | Wyniki zaakceptowane bez niezależnej walidacji. |
| Rodzina myślenia grupowego | „Zaburzenia jednorodności” | Monokultura, konformizm, brak ToM, motyw mieszany, kaskada. |
| Upadek monokultury | „Ten sam model, te same halucynacje” | Skorelowane błędy ze wspólnego modelu podstawowego lub danych szkoleniowych. |
| Ponów próbę burzy | „Kaskadowe wzmocnienie błędu” | Jedna awaria wyzwala ponowne próby, które zwiększają obciążenie w dalszej części procesu. |
| Wyłącznik | „Szybka awaria przy wskaźniku błędów” | Otwarte, gdy poziom błędów przekracza próg; zwarcie z domyślnym. |
| STRAT | „Trio reakcji na incydenty” | Detekcja + diagnostyka + środki walidacyjne. 1,5-krotny sukces w łagodzeniu. |
| Zatrucie pamięci | „Halucynacje się rozprzestrzeniają” | Fakt skażony pamięcią współdzieloną; dalsi agenci twierdzą, że są trucizną. |

## Dalsze czytanie

- [Cemri i in. — Dlaczego wieloagentowe systemy LLM zawodzą?](https://arxiv.org/abs/2503.13657) — taksonomia MAST, NeurIPS 2025
- [Niepowodzenia myślenia grupowego w wieloagentowych LLM](https://arxiv.org/abs/2508.05687) — monokultura, konformizm i taksonomia pięciu rodzin
- [STRATUS — wyspecjalizowani agenci reagowania na incydenty MAS](https://neurips.cc/) — Wpis postępowania NeurIPS 2025 (wykrywanie + diagnoza + walidacja)
- [Uwolnij to! — wzorce stabilności (Nygard)](https://pragprog.com/titles/mnee2/release-it-drugie-edition/) — kanoniczne odniesienie do wyłącznika
- [Anthropic — wieloagentowy system badawczy](https://www.anthropic.com/engineering/multi-agent-research-system) — uwagi dotyczące trybu awarii produkcyjnej