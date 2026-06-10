# Pochodzenie danych i zarządzanie danymi szkoleniowymi

> Ustawa UE dotycząca sztucznej inteligencji wymaga odczytywalnych maszynowo standardów rezygnacji z GPAI do sierpnia 2025 r. (w drodze wyjątku TDM zawartego w dyrektywie UE dotyczącej praw autorskich). California AB 2013 (podpisano w 2024 r.) — Przejrzystość danych szkoleniowych dotyczących generowanej sztucznej inteligencji wymaga od programistów publikowania podsumowania zbiorów danych zawierających 12 obowiązkowych pól. Dostosowanie DPA do 2025 r. w sprawie uzasadnionego interesu: irlandzki DPC (21 maja 2025 r.) akceptuje organizowane przez Meta szkolenie LLM dotyczące własnych publicznych treści dla dorosłych z UE/EOG z zabezpieczeniami po opinii EROD; Wyższy Sąd Krajowy w Kolonii (23 maja 2025 r.) oddalił nakaz; Hamburg DPA rezygnuje w trybie pilnym; ICO w Wielkiej Brytanii (23 września 2025 r.) wydaje pozytywną odpowiedź regulacyjną na zabezpieczenia LinkedIn dotyczące szkoleń w zakresie sztucznej inteligencji (przejrzystość, uproszczona rezygnacja, wydłużone okna na sprzeciw) i kontynuuje monitorowanie – a nie formalne zezwolenie. Brazylijska ANPD (2 lipca 2024 r.) zawiesiła przetwarzanie przez Meta ze względu na niewystarczającą przejrzystość informacji; środek zapobiegawczy został zniesiony w dniu 30 sierpnia 2024 r. po przedłożeniu przez Meta planu zgodności. Kluczowy problem nieodwracalności: ramy dotyczące zgody na pliki cookie zostały zaprojektowane z myślą o odwracalnym śledzeniu w czasie rzeczywistym; gdy dane znajdą się w wagach modelu, chirurgiczne usunięcie jest niemożliwe – nie ma praktycznego prawa do usunięcia wynikającego z RODO w przypadku wytrenowanych sieci neuronowych. Okno zgodności przypada na moment odbioru. Inicjatywa Data Provenance (dataprovenance.org, Longpre, Mahari, Lee i in., „Consent in Crisis”, lipiec 2024 r.): zakrojony na szeroką skalę audyt pokazuje szybki spadek liczby wspólnych danych AI w miarę dodawania przez wydawców ograniczeń w pliku robots.txt.

**Typ:** Ucz się
**Języki:** Python (stdlib, 12-polowy generator rusztowań California AB 2013)
**Wymagania:** Faza 18 · 24 (regulacyjna), Faza 18 · 26 (karty)
**Czas:** ~60 minut

## Cele nauczania

- Opisz 12 wymaganych pól California AB 2013 w celu zapewnienia przejrzystości danych szkoleniowych w zakresie generowanej sztucznej inteligencji.
- Proszę przedstawić stanowisko DPA na rok 2025 w sprawie szkoleń LLM wynikających z uzasadnionego interesu (irlandzki DPC, brytyjskie ICO, Hamburg, Kolonia).
- Opisz problem nieodwracalności: dlaczego prawo do usunięcia danych wynikające z RODO nie ma praktycznego odpowiednika dla wytrenowanych sieci neuronowych.
- Proszę przedstawić ustalenia inicjatywy Data Provenance Initiative dotyczące zgody w sytuacji kryzysowej.

## Problem

Zarządzanie danymi szkoleniowymi jest podstawą każdej karty modelu (lekcja 26) i obowiązku regulacyjnego (lekcja 24). W latach 2024–2025 krajobraz regulacyjny skonsolidował się w oparciu o trzy zasady: infrastrukturę umożliwiającą rezygnację z dostępu, ujawnianie poszczególnych zbiorów danych oraz dostosowania wynikające z uzasadnionego interesu w przypadku danych publicznie dostępnych. Dostawcy, którzy nie przestrzegają zasad w momencie gromadzenia danych, nie mogą podjąć działań naprawczych na dalszym etapie łańcucha dostaw.

## Koncepcja

### Kalifornia AB 2013

Podpisano w 2024 r. Dokumentację należy opublikować 1 stycznia 2026 r. lub wcześniej w przypadku systemów wydanych 1 stycznia 2022 r. lub później. Sekcja 3111 (a) wymaga od programistów publikowania ogólnego podsumowania zbiorów danych wykorzystywanych podczas szkoleń, zawierającego 12 elementów ustawowych:
1. Źródła lub właściciele zbiorów danych.
2. Opis, w jaki sposób zbiory danych służą realizacji zamierzonego celu systemu sztucznej inteligencji.
3. Liczba punktów danych w zbiorach danych (dopuszczalne zakresy ogólne; szacunki dla dynamicznych zbiorów danych).
4. Opis typów punktów danych (typy etykiet dla oznakowanych zbiorów danych; ogólna charakterystyka dla nieoznaczonych).
5. Czy zbiory danych zawierają jakiekolwiek dane chronione prawem autorskim, znakiem towarowym lub patentem, czy też stanowią w całości własność publiczną.
6. Czy zbiory danych zostały zakupione lub licencjonowane.
7. Czy zbiory danych zawierają dane osobowe (zgodnie z Kodeksem Cywilnym §1798.140(v)).
8. Czy zbiory danych zawierają zbiorcze informacje o konsumentach (zgodnie z Kodeksem Cywilnym §1798.140(b)).
9. Czyszczenie, obróbka lub inna modyfikacja przez dewelopera zgodnie z przeznaczeniem.
10. Okres gromadzenia danych, z powiadomieniem, jeśli gromadzenie jest w toku.
11. Daty pierwszego użycia zbiorów danych podczas opracowywania.
12. Czy system wykorzystuje lub stale wykorzystuje syntetyczne generowanie danych.

Pozycja 12 (dane syntetyczne) jest nowa w porównaniu z Gebru i in. Arkusze danych na rok 2018. Punkt 7 (dane osobowe) wiąże się z obowiązkami wynikającymi z ustawy o prawach prywatności (CPRA). Statut wyłącza bezpieczeństwo/integralność, eksploatację statków powietrznych i wyłącznie federalne systemy bezpieczeństwa narodowego (sekcja 3111 (b)).

### Ustawa UE o sztucznej inteligencji (lekcja 24) i rezygnacja z TDM

Wyjątek dotyczący eksploracji tekstów i danych zawarty w dyrektywie UE dotyczącej praw autorskich umożliwia szkolenia w zakresie treści publicznie dostępnych, chyba że podmiot praw autorskich zrezygnuje. Ustawa UE dotycząca sztucznej inteligencji Rozdział dotyczący kodeksu postępowania GPAI dotyczący praw autorskich wymaga od dostawców usług GPAI przestrzegania odczytywalnych maszynowo sygnałów rezygnacji (plik robots.txt, oświadczenie C2PA „No AI Training” itp.).

### Konwergencja organów ochrony danych w 2025 r. w zakresie uzasadnionego interesu

Irlandzki DPC (21 maja 2025 r.): Plan Meta dotyczący szkoleń w zakresie własnych, publicznych treści przeznaczonych dla dorosłych użytkowników z UE/EOG, zaakceptowanych z zabezpieczeniami po wydaniu opinii EROD. Wyższy Sąd Krajowy w Kolonii (23 maja 2025 r.) oddalił nakaz przeciwko Meta: wystarczy rezygnacja z umowy. Hamburg DPA rezygnuje z pilnej procedury w celu zapewnienia spójności w całej UE. ICO w Wielkiej Brytanii (23 września 2025 r.) wydało pozytywną odpowiedź organów regulacyjnych – a nie formalne zezwolenie – na wznowienie przez LinkedIn szkoleń w zakresie sztucznej inteligencji z podobnymi zabezpieczeniami i ciągłym monitorowaniem.

Zbieżna zasada: uzasadniony interes może uzasadniać szkolenie w zakresie publicznie dostępnych treści własnych z możliwością rezygnacji. Zgoda nie jest wymagana.

### Brazylijska ANPD (czerwiec 2024 r.)

Zawieszono przetwarzanie przez Meta brazylijskich danych użytkowników na potrzeby szkolenia AI ze względu na niewystarczającą przejrzystość informacji. Inny wynik niż unijne organy ochrony danych – ANPD przedkładała przejrzystość nad dopuszczalność wynikającą z uzasadnionego interesu.

### Problem nieodwracalności

Zgoda na pliki cookie została zaprojektowana w celu odwracalnego śledzenia w czasie rzeczywistym. Dane treningowe są inne: gdy dane zostaną wprowadzone do wag modelu, chirurgiczne usunięcie nie jest możliwe. Jedynym całkowitym rozwiązaniem jest przekwalifikowanie się od zera, a ponadto jest ono zbyt kosztowne.

Częściowe środki zaradcze:
- **Oduczenie się.** Przybliżone usunięcie; mierzone przez MIA (lekcja 22).
- **Wpływ na lokalizację opartą na funkcjach.** Zidentyfikuj wagi, na które dane mają największy wpływ; selektywnie aktualizować.
- **Dostrajanie tłumienia.** Trenuj model tak, aby odrzucał wyniki uzyskane na podstawie danych.

Żaden nie rozwiązuje w pełni problemu. Okno zgodności kończy się w momencie gromadzenia danych.

### Inicjatywa dotycząca pochodzenia danych

dataprovenance.org. Longpre, Mahari, Lee i in. „Consent in Crisis” (lipiec 2024 r.): zakrojony na szeroką skalę audyt wspólnych danych szkoleniowych dotyczących sztucznej inteligencji. Wynik: wydawcy dodają ograniczenia do pliku robots.txt w coraz szybszym tempie. Wspólne zasoby, które można łatwo trenować, szybko się kurczą. W latach 2023–2024 około 25% najlepszych źródeł szkoleniowych dodało pewne ograniczenia. Implikacja: przyszła dostępność danych szkoleniowych zależy od nowych paradygmatów pozyskiwania (licencjonowanie, wytwarzanie syntetyczne, uczestnictwo motywowane).

### Gdzie to pasuje do fazy 18

Lekcja 26 to dokumentacja na poziomie modelu. Lekcja 27. to zarządzanie na poziomie zbioru danych. Razem definiują warstwę przezroczystości. Lekcja 28 przedstawia ekosystem badawczy, który pracuje nad tymi pytaniami.

## Użyj tego

`code/main.py` generuje 12-polową strukturę podsumowującą zbiór danych zgodną z California AB 2013 dla zbioru danych zabawek. Możesz wypełnić pola i sprawdzić, które z nich powodują naruszenie prywatności lub praw autorskich.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-provenance-check.md`. Biorąc pod uwagę zbiór danych wykorzystany w szkoleniu, sprawdza on pokrycie 12 obszarów AB 2013, zgodność infrastruktury z możliwością rezygnacji, dostosowanie DPA i ocenę ryzyka nieodwracalności.

## Ćwiczenia

1. Uruchom `code/main.py`. Utwórz podsumowanie składające się z 12 pól dla zbioru danych zabawek i określ, które pola są niedoprecyzowane.

2. Dyrektywa UE dotycząca praw autorskich Rezygnacja z TDM jest możliwa do odczytu maszynowego. Zaproponuj standardowy format sygnału rezygnacji i porównaj go z plikami robots.txt i C2PA „No AI Training”.

3. Przeczytaj dokument „Consent in Crisis” organizacji Data Provenance Initiative (lipiec 2024 r.). Opisz trzy najszybciej ograniczające kategorie treści i przedstaw jedną z konsekwencji ekonomicznych.

4. W dostosowaniu dotyczącym DPA z 2025 r. uznano uzasadniony interes w szkoleniach o treści publicznej. Stwórz scenariusz, w którym uzasadniony interes nie wystarczy, i określ podstawę prawną, jakiej potrzebowałby dostawca.

5. Naszkicuj manifest pochodzenia danych szkoleniowych, który składa się z pól AB 2013 i łańcucha pochodzenia podpisanego C2PA dla każdego zestawu danych. Zidentyfikuj jedną barierę techniczną i jedną prawną.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| AB 2013 | „prawo kalifornijskie” | Przejrzystość danych szkoleniowych w zakresie generatywnej sztucznej inteligencji; 12 pól obowiązkowych |
| Wyjątek TDM | „eksploracja tekstów i danych” | Dyrektywa UE dotycząca praw autorskich – wyjątek dotyczący danych szkoleniowych z możliwością rezygnacji |
| Uzasadniony interes | „podstawa UE” | Podstawa art. 6 RODO, która może uzasadniać szkolenie w zakresie treści publicznych |
| Sygnał rezygnacji | „do odczytu maszynowego bez pociągu” | robots.txt, C2PA „Brak szkolenia AI”, TDM.Reservation |
| Nieodwracalność | „nie można cofnąć trenowania” | Dane w masach modeli nie są usuwalne chirurgicznie |
| Oduczenie się | „przybliżone usunięcie” | Interwencje poszkoleniowe mające na celu zmniejszenie zależności modelu od konkretnych danych |
| Zgoda w kryzysie | „audyt DPI” | Lipiec 2024 r. Ustalenie przyspieszających ograniczeń pliku robots.txt |

## Dalsze czytanie

– [California AB 2013](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202320240AB2013) – Ustawa o przejrzystości danych szkoleniowych dotyczących generatywnej sztucznej inteligencji
- [Ustawa UE o sztucznej inteligencji + Kodeks postępowania GPAI (lekcja 24)](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) — rozdział dotyczący praw autorskich
- [Longpre, Mahari, Lee i in. — Consent in Crisis (dataprovenance.org, lipiec 2024)](https://www.dataprovenance.org/consent-in-crisis-paper) — Audyt DPI
- [IAPP – zmiany EU Digital Omnibus RODO (2025)](https://iapp.org/news/a/eu-digital-omnibus-amendments-to-gdpr-to-facilitate-ai-training-miss-the-mark) – kontekst regulacyjny