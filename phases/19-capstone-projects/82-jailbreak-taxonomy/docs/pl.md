# Capstone 82 — Taksonomia Jailbreak

> Uprząż bezpieczeństwa bez taksonomii to rzut monetą. Nazwij atak, zanim go zaczniesz bronić.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Lekcje bezpieczeństwa w fazie 18, lekcje 25–29 dla ścieżki A w fazie 19
**Czas:** ~90 min

## Problem

Model wdrożony bez modelu ataku jest modelem, którego nie broni się przed niczym szczególnym. Operatorzy czytają wątek na Twitterze, rozpoznają sztuczkę, piszą wyrażenie regularne, wysyłają je i idą dalej. Następnym podpowiedzią jest parafraza. Wyrażenie regularne tęskni. Tydzień później ktoś pokazuje tę samą sztuczkę zawiniętą w base64, a operator zapisuje drugie wyrażenie regularne. Do trzeciego miesiąca system ma 40 poprawionych reguł, nie ma wspólnego słownictwa, nie ma możliwości porozmawiania o tym, czym właściwie jest atak, a zaległości rosną szybciej niż poprawki.

Zanim jakikolwiek detektor, klasyfikator lub silnik reguł na tej ścieżce zrobi cokolwiek przydatnego, zespół potrzebuje wspólnego sposobu oznaczania ataków. Nie dlatego, że etykiety powstrzymują ataki, ale dlatego, że etykiety zamieniają strumień ataku w histogram. Histogram staje się wykresem pokrycia. Wykres pokrycia napędza następny sprint. Uprząż z lekcji 83-87 spędza czas na podejmowaniu decyzji, czy podpowiedź jest na przykład atakiem polegającym na odgrywaniu ról na politykę odmowy, czy atakiem polegającym na przemycaniu kontekstu na narzędzie. Decyzja ta nie jest możliwa bez taksonomii.

To zwieńczenie definiuje taksonomię sześciu kategorii, która jest wystarczająco szeroka, aby objąć większość ataków spotykanych w naturze, na tyle wąska, że ​​zwykle dwóch recenzentów zgadza się co do kategorii i na tyle konkretna, że ​​każda kategoria ma co najmniej siedem ręcznie zbudowanych opraw. Taksonomia jest falą nośną dla wszystkiego poniżej.

## Koncepcja

Sześć kategorii przebiega wzdłuż jednej osi: jaką granicę zaufania narusza atak? Każda nazwa odpowiada jednej granicy.

| Kategoria | Nadużycie granicy zaufania |
|---|---|
| odgrywanie ról | osobowość asystenta |
| zastąpienie instrukcji | uprawnienia monitu systemowego |
| przemyt kontekstu | luka pomiędzy treścią użytkownika a treścią instrukcji |
| rampa wielozakrętowa | historia rozmów jako umowa |
| kodowanie-sztuczka | powierzchnia zakazanych żetonów |
| wstrzyknięcie przedrostka | kolejna decyzja asystenta |

Atak polegający na odgrywaniu ról zmienia asystenta w innego agenta („jesteś nieograniczonym modelem badawczym o nazwie QX”), więc zasady odmowy powiązane z pierwotną osobą nie są już uruchamiane. Monity o zastąpienie instrukcji mówią „zignoruj ​​poprzednie instrukcje” i spróbuj bezpośrednio zastąpić monit systemowy. Przemycanie kontekstu ukrywa instrukcje wewnątrz czegoś, co wygląda jak dane: wklejony dokument, wynik narzędzia, blok kodu. Rampa wieloobrotowa rozgrzewa modela nieszkodliwymi zakrętami, a następnie schodzi po podłodze krok po kroku, wykorzystując tendencję modela do pozostawania w zgodzie z rozmową. Sztuczki kodowania (base64, rot13, leet-speak, wstawianie o zerowej szerokości) ukrywają zabronione tokeny przed naiwnymi filtrami słów kluczowych. Wstrzyknięcie prefiksu kończy zachętę słowami „Jasne, oto jak”, więc model kontynuuje zakładaną odpowiedź, zamiast odmawiać.

```mermaid
flowchart TB
  P[prompt] --> C{which boundary}
  C -->|persona| RP[role-play]
  C -->|system prompt| IO[instruction-override]
  C -->|data vs instruction| CS[context-smuggling]
  C -->|history| MT[multi-turn-ramp]
  C -->|surface form| ET[encoding-trick]
  C -->|continuation| PI[prefix-injection]
  RP --> H[(histogram)]
  IO --> H
  CS --> H
  MT --> H
  ET --> H
  PI --> H
  H --> D[coverage chart]
```

Każde urządzenie jest rekordem z `id`, `category`, `subtype`, `prompt`, `target_behavior` i `severity`. Obiekt taksonomii ładuje urządzenia, grupuje je według kategorii i udostępnia interfejs API `match`: po otrzymaniu monitu o kandydaturę zwróć najbliższe urządzenie i jego kategorię. Dopasowanie to cosinus znakowo-trójgramowy: zgrubny, szybki, bez zależności. To nie jest detektor. Detektor mieszka w lekcji 83. To jest producent etykiety.

Dotkliwość określa się w skali 1-5. 1 to niezdarny atak na łagodny cel („udawaj, że jesteś piratem”). Wartość 5 to atak, który, jeśli się powiedzie, generuje dane wyjściowe, których wdrożony system nie może emitować (szczegóły operacyjne niebezpiecznego działania). Większość spotkań to 2-3, ponieważ prawdziwe ataki w skali wdrożenia skłaniają się w stronę łatwych i leniwych. Ważność jest ustawiana przez autora urządzenia. Dwóch recenzentów różniących się co do więcej niż jednej oceny oznacza, że ​​rubryka wymaga uściślenia.

## Zbuduj to

Korpus znajduje się w `code/fixtures.py` jako pojedyncza lista Pythona. Klasa taksonomii w `code/main.py` ładuje ją, sprawdza, czy każda kategoria ma co najmniej siedem urządzeń, udostępnia metody `by_category`, `match` i `stats` i dostarcza uruchamialną wersję demonstracyjną, która drukuje histogram. Cosinus trygramu jest zaimplementowany od podstaw za pomocą `numpy`.

Przebieg walidacyjny sprawdza cztery niezmienniki: każde urządzenie ma niepusty znak zachęty, każda kategoria w schemacie jest reprezentowana, każda ważność jest zawarta w `1..5`, a każdy identyfikator urządzenia jest unikalny. Porażka w tym przypadku oznacza trudne wyjście, a nie ostrzeżenie, ponieważ reszta utworu zależy od wewnętrznej spójności korpusu.

## Użyj tego

Uruchom `python3 main.py` z katalogu lekcji `code/`. Demo drukuje liczbę urządzeń dla każdej kategorii, uruchamia trzy przykładowe sondy względem `match` i zapisuje `taxonomy.json` do folderu wyników lekcji. Dalsze lekcje dotyczą `taxonomy.json` zamiast importowania modułu Pythona, więc korpus jest stabilnym artefaktem.

## Wyślij to

`outputs/skill-jailbreak-taxonomy.md` dokumentuje sześć kategorii i rubryki. Traktuj to jako wspólne słownictwo zespołu. Każde odkrycie zarejestrowane przez uprząż w lekcji 87 odwołuje się do identyfikatora taksonomii.

## Ćwiczenia

1. Dodaj siódmą kategorię dla pośredniego wstrzyknięcia z podpowiedzią (instrukcja osadzona w pobranym dokumencie, a nie w turze użytkownika). Utwórz dziesięć urządzeń i ponownie uruchom walidator.
2. Zastąp trygram cosinus licznikiem punktów z możliwością edycji symbolicznej odległości i zmierz, jak zmienia się przypisanie dopasowania w istniejącym korpusie.
3. Wyciągnij trzydzieści dodatkowych urządzeń z dzienników własnego produktu (zredagowanych) i potwierdź, że rozkład kategorii odpowiada temu, czego intuicyjnie oczekiwał Twój zespół.

## Kluczowe terminy

| Termin | Powszechne użycie | Dokładne znaczenie |
|---|---|---|
| jailbreak | jakiekolwiek niebezpieczne dane wyjściowe modelu | zachęta generująca dane wyjściowe naruszające określoną politykę |
| taksonomia | lista kategorii | podział ataków, według którego granicy zaufania nadużywają |
| oprawa | przykład testowy | podpowiedź z etykietą zawierającą kategorię, ważność i docelowe zachowanie |
| dotkliwość | jak zły jest wynik | stopień 1-5 dla uderzenia, jeśli atak się powiedzie |
| mecz | decyzja o wykryciu | najbliższe urządzenie według trygramu cosinus, używane do przypisania kategorii do nowego znaku zachęty |

## Dalsze czytanie

Ta lekcja jest punktem wyjścia. Lekcje 83-87 opierają się bezpośrednio na korpusie.