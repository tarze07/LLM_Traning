# Ramy bezpieczeństwa granicznego – RSP, PF, FSF

> Trzy ramy głównych laboratoriów definiują zarządzanie branżowe w zakresie pionierskich zdolności w roku 2026. Polityka odpowiedzialnego skalowania firmy Anthropic w wersji 3.0 (luty 2026 r.) wprowadza wielopoziomowe poziomy bezpieczeństwa sztucznej inteligencji (ASL-1 do ASL-5+), wzorowane na poziomach bezpieczeństwa biologicznego, przy czym ASL-3 został aktywowany w maju 2025 r. dla modeli istotnych dla CBRN. OpenAI Readedness Framework v2 (kwiecień 2025 r.) definiuje pięć kryteriów śledzonych możliwości i oddziela raporty dotyczące możliwości od raportów zabezpieczeń. DeepMind Frontier Safety Framework w wersji 3.0 (wrzesień 2025 r.) wprowadza krytyczne poziomy zdolności, w tym nową CCL dotyczącą szkodliwej manipulacji. Wszystkie trzy zawierają teraz klauzule dotyczące dostosowania przez konkurencję, umożliwiające odroczenie, jeśli laboratoria równorzędne wysyłają produkty bez porównywalnych zabezpieczeń. Dostosowanie między laboratoriami pozostaje strukturalne, a nie terminologiczne: „Progi możliwości”, „Progi wysokiej wydajności” i „Krytyczne poziomy zdolności” oznaczają analogiczne konstrukcje.

**Typ:** Ucz się
**Języki:** brak
**Wymagania wstępne:** Faza 18 · 17 (WMDP), Faza 18 · 07-09 (niepowodzenia w oszustwie)
**Czas:** ~75 minut

## Cele nauczania

- Opisz strukturę poziomów ASL firmy Anthropic i co aktywowało ASL-3.
- Wymień pięć kryteriów OpenAI gotowości Framework v2 dla śledzonych możliwości.
- Opisać strukturę poziomu zdolności krytycznych DeepMind i CCL szkodliwej manipulacji.
- Wyjaśnij klauzule dotyczące dostosowania przez konkurenta i dlaczego mają one znaczenie dla dynamiki wyścigu.
- Zdefiniuj przypadek bezpieczeństwa i opisz strukturę składającą się z trzech filarów (monitorowanie, nieczytelność, niezdolność).

## Problem

Z lekcji 7-17 wynika, że możliwe jest oszustwo, istnieje możliwość podwójnego zastosowania, a ocena ma ograniczenia. Laboratorium dysponujące modelem o zasięgu pionierskim potrzebuje wewnętrznej struktury zarządzania, która:
- Określa progi, w przypadku których wymagane są nowe zabezpieczenia.
- Definiuje wymagane oceny przed skalowaniem.
- Opisuje, jak wygląda walizka bezpieczeństwa.
- Radzi sobie z problemem dynamiki wyścigu (jeśli konkurenci wysyłają bez zabezpieczeń, co robisz?).

Trzy ramy na lata 2025–2026 są najnowocześniejsze – są niedoskonałe, ewoluują i są na tyle dostosowane w poszczególnych laboratoriach, że obecnie pytanie dotyczące zarządzania dotyczy tego, czy ramy są odpowiednie, a nie tego, czy istnieją.

## Koncepcja

### Polityka odpowiedzialnego skalowania antropicznego wersja 3.0 (luty 2026 r.)

Struktura ASL:
- ASL-1: model niefrontowy (uwzględniony w punkcie bazowym słabszym niż granica).
- ASL-2: bieżąca granica bazowa; wdrażane przy zastosowaniu zwykłych zabezpieczeń.
- ASL-3: znacznie wyższe ryzyko katastrofalnego w skutkach niewłaściwego użycia; Możliwości istotne dla CBRN. Aktywowano w maju 2025 r.
- ASL-4: próg przekroczenia AI R&D-2; modele, które mogą zautomatyzować badania nad sztuczną inteligencją na poziomie podstawowym.
- ASL-5+: zaawansowane prace badawczo-rozwojowe w zakresie sztucznej inteligencji; modele, które znacznie przyspieszają efektywne skalowanie.

Nowości w wersji 3.0:
- Plany działania dotyczące bezpieczeństwa granicznego (publiczne w zredagowanej formie).
- Raporty dotyczące ryzyka (kwartalnie, niektóre przeglądane zewnętrznie).
- Działalność badawczo-rozwojowa w zakresie sztucznej inteligencji jest podzielona na prace badawczo-rozwojowe w zakresie sztucznej inteligencji-2 oraz prace badawczo-rozwojowe w zakresie sztucznej inteligencji-4.
- Po przekroczeniu AI B+R-4 wymagane jest pozytywne uzasadnienie bezpieczeństwa, identyfikujące ryzyko rozbieżności w modelach realizujących rozbieżne cele.

### Ramy gotowości OpenAI wersja 2 (15 kwietnia 2025 r.)

Pięć kryteriów śledzonych możliwości:
- **Prawdopodobne.** Istnieje uzasadniony model zagrożenia.
- **Mierzalne.** Możliwa ocena empiryczna.
- **Poważne.** Szkoda jest duża.
- **Nowość netto.** Nie jest to zwiększone ryzyko istniejące wcześniej.
- **Natychmiastowe lub nieodwracalne.** Szkoda pojawia się szybko i nie można jej cofnąć.

Śledzone są możliwości spełniające wszystkie pięć. Inni nie.

Inna struktura PF v2:
- Oddzielne raporty dotyczące możliwości (co potrafi model) od raportów zabezpieczeń (jakie istnieją elementy sterujące).
- Przeglądy Grupy Doradczej ds. Bezpieczeństwa.
- Przywództwo zatwierdza; Komitet ds. Bezpieczeństwa i Ochrony Zarządu nadzoruje.
- „Klauzula dostosowawcza”: OpenAI może zmniejszyć wymagania, jeśli inne laboratorium dostarczy rozwiązanie bez porównywalnych zabezpieczeń.

### Ramy bezpieczeństwa DeepMind Frontier wersja 3.0 (wrzesień 2025 r.)

Poziomy zdolności krytycznych (CCL) według domeny:
- Wzmocnienie broni biologicznej
- Cyberpoprawa
- Przyspieszenie badań i rozwoju ML
- Szkodliwa manipulacja (nowość w wersji 3.0): modele, które mogą znacząco zmienić przekonania/zachowania w kontekstach o dużej stawce.

Wersja 2.0 (luty 2025 r.) dodała sekcję Zwodnicze dostosowanie i wyższe poziomy bezpieczeństwa dla list CCL dotyczących badań i rozwoju w obszarze ML.

### Dopasowanie międzylaboratoryjne

- Antropiczne „progi zdolności”.
- DeepMind „Krytyczne poziomy zdolności”.
- OpenAI „Progi wysokiej wydajności”.

Brak terminologii branżowej. Dopasowane strukturalnie: trzy poziomy potencjału granicznego z opublikowanymi kryteriami oceny. Wszystkie trzy zawierają klauzule dotyczące dostosowania do konkurencji (od 2025 r.).

### Futerały zabezpieczające

Argument bezpieczeństwa to pisemny argument potwierdzający, że wdrożenie jest akceptowalnie bezpieczne przy najgorszych założeniach. Standardowa struktura skupia się na trzech filarach:

- **Monitorowanie.** Czy możemy wykryć złe zachowanie, jeśli wystąpi?
- **Nieczytelność.** Czy modelowi brakuje umiejętności wykonania spójnego planu wyrządzenia szkody?
- **Niezdolność.** Czy model nie ma zdolności do wyrządzenia danej szkody?

Różne przypadki bezpieczeństwa dotyczą różnych filarów. W przypadku ASL-3 CBRN głównym celem jest niezdolność (poprzez oduczenie się). W przypadku zwodniczego dostosowania celem jest monitorowanie i nieczytelność. W przypadku poprawy cyberbezpieczeństwa wszystkie trzy są istotne.

### Problem dynamiki wyścigu

Klauzule dotyczące dostosowania ze strony konkurencji są kontrowersyjne. Krytycy twierdzą, że prowadzi to do wyścigu w dół: jeśli wszystkie trzy laboratoria zmniejszą wymagania w przypadku wady konkurenta, równowaga przesunie się w stronę dezercji. Obrońcy twierdzą, że alternatywa (jednostronne zabezpieczenia) daje gorsze wyniki, jeśli laboratorium, które zdradza, jest mniej świadome bezpieczeństwa.

Brytyjskie AISI, US CAISI i EU AI Office (lekcja 24) to zewnętrzne odpowiedniki w zakresie zarządzania. Ramy laboratorium są dobrowolne; pojawiają się ramy regulacyjne.

### Gdzie to pasuje do fazy 18

Lekcje 17-18 to warstwa pomiaru i zarządzania, oprócz oszustw i analiz zespołu czerwonego. Lekcje 19–24 dotyczą dobrostanu, uprzedzeń, prywatności, znaków wodnych i struktury regulacyjnej. Lekcja 28 przedstawia ekosystem badawczy (MATS, Redwood, Apollo, METR), który operacjonalizuje ewaluacje.

## Użyj tego

Brak kodu do tej lekcji. Przeczytaj trzy główne źródła: RSP v3.0, PF v2, FSF v3.0. Przyporządkuj strukturę poziomów każdego laboratorium do pozostałych i zidentyfikuj jeden próg, który każde laboratorium definiuje, a którego nie mają pozostałe.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-framework-diff.md`. Biorąc pod uwagę ramy bezpieczeństwa lub informację o wersji, porównuje definicje progów platformy, wymagane oceny i strukturę uzasadnienia bezpieczeństwa z RSP v3.0, PF v2, FSF v3.0 i zaznacza luki między laboratoriami.

## Ćwiczenia

1. Przeczytaj RSP v3.0, PF v2 i FSF v3.0. Skompiluj tabelę progów CBRN każdego laboratorium, progów badań i rozwoju sztucznej inteligencji każdego laboratorium oraz wymaganej oceny przed wdrożeniem każdego laboratorium.

2. Klauzula dostosowania do konkurencji znajduje się we wszystkich trzech ramach (2025+). Napisz jeden akapit, w którym to uzasadnisz; napisz jeden akapit, w którym się sprzeciwiasz. Zidentyfikuj założenia, od których zależy każde stanowisko.

3. Zaprojektuj obudowę bezpieczeństwa dla modelu przekraczającego próg 4 badań i rozwoju sztucznej inteligencji firmy Anthropic. Wymień dowody wymagane przez każdy z trzech filarów (monitorowanie, nieczytelność, niezdolność).

4. W wersji 3.0 oprogramowania FSF firmy DeepMind wprowadzono funkcję CCL dotyczącą szkodliwej manipulacji. Zaproponuj trzy pomiary empiryczne, które wskazywałyby, że model przekroczył ten próg.

5. Przeczytaj dokument METR „Wspólne elementy polityki bezpieczeństwa granicznej sztucznej inteligencji” (2025). Wymień trzy najsilniejsze zbieżności między laboratoriami i dwie największe rozbieżności.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| RSP | „Ramy antropiczne” | Polityka odpowiedzialnego skalowania; poziomy ASL; v3.0 luty 2026 |
| PF | „Framework OpenAI” | ramy gotowości; pięć kryteriów; wersja 2 kwietnia 2025 r. |
| FSF | „Struktura DeepMind” | Ramy bezpieczeństwa granicznego; CCL; wersja 3.0 wrzesień 2025 |
| ASL-3 | „poziom bezpieczeństwa biologicznego 3-analogowy” | Poziom antropiczny w zakresie zdolności związanych z CBRN; aktywowano maj 2025 |
| CCL | „krytyczny poziom zdolności” | Konstrukcja progowa DeepMind; na domenę |
| Sprawa bezpieczeństwa | „argument formalny” | Pisemny argument stwierdzający, że wdrożenie jest akceptowalnie bezpieczne w najgorszym przypadku U |
| Klauzula dostosowawcza | „dodatek za ucieczkę konkurenta” | Przepis ramowy dotyczący ograniczenia wymogów w przypadku, gdy konkurenci dostarczają statki bez porównywalnych zabezpieczeń |

## Dalsze czytanie

– [Anthropic — Polityka odpowiedzialnego skalowania, wersja 3.0 (luty 2026 r.)](https://www.anthropic.com/responsible-scaling-policy) — poziomy ASL, plany działania, dezagregacja badań i rozwoju AI
- [OpenAI — Aktualizacja ram gotowości (15 kwietnia 2025 r.)](https://openai.com/index/updating-our-preparedness-framework/) — pięć kryteriów, klauzula dostosowawcza
– [DeepMind — Wzmocnienie naszych ram bezpieczeństwa na granicach (wrzesień 2025 r.)](https://deepmind.google/blog/strengthening-our-frontier-safety-framework/) — CCL v3.0, szkodliwa manipulacja
- [METR – Common Elements of Frontier AI Safety Policies (2025)](https://metr.org/blog/2025-03-26-common-elements-of-frontier-ai-safety-policies/) – porównanie między laboratoriami