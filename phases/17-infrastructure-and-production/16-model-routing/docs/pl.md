# Routing modelowy jako prymitywna metoda redukcji kosztów

> Dynamiczny broker ocenia każde żądanie (typ zadania, długość tokena, podobieństwo osadzania, pewność) i wysyła proste zapytania do taniego modelu, eskalując złożone do modelu granicznego. Nazywany także modelowaniem kaskadowym. Studia przypadków produkcyjnych pokazują redukcję kosztów o 20–60% przy jakości ISO we wdrożeniach w USA, Wielkiej Brytanii i UE; poprawa wydajności routingu o 30% w przypadku SaaS o dużym wolumenie przekłada się na sześciocyfrowe roczne oszczędności. Kontekst na rok 2026 jest taki, że ceny wnioskowania LLM spadły ~10 razy w roku — token klasy GPT-4 wzrósł z $20/M to ~$0,40/M od końca 2022 r. do 2026 r. Większość spadku dotyczy lepszej obsługi stosów (faza 17 · 04-09), a nie sprzętu. Routing to sposób, w jaki przekształcasz spadek ceny w marżę bez regresji produktu. Tryb awarii to dryf taniego modelu: trasa przesuwa 40% do słabszego modelu, jakość zadań rozumowania spada o 3-5%, nikt tego nie zauważa przez kwartał. Bramuj trasy według wskaźników jakości online, a nie tylko zestawów ewaluacyjnych offline.

**Typ:** Ucz się
**Języki:** Python (stdlib, zabawkowy symulator routera kaskadowego)
**Wymagania wstępne:** Faza 17 · 01 (zarządzane platformy LLM), faza 17 · 19 (bramy AI)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnij model kaskadowy: najpierw tanio i sprawdzając pewność, eskaluj przy niskim poziomie pewności.
- Wymień cztery sygnały routingu (klasyfikacja zadania, długość podpowiedzi, osadzanie podobieństwa do znanego twardego zestawu, pewność siebie od pierwszego przejścia).
- Oblicz oczekiwany koszt mieszany przy docelowym podziale tras i tolerancji utraty jakości.
- Podaj nazwę metryki monitorowania dryfu (bramki jakości online), która wychwytuje pełzanie tanich modeli.

## Problem

Twoja usługa kosztuje 80 tys. USD miesięcznie na GPT-5. Twoje analizy pokazują, że 70% zapytań jest prostych: „która jest godzina w Paryżu?” „przeformułuj to zdanie”. Model klasy Haiku radzi sobie z nimi doskonale za 3% ceny. 30% potrzebuje rozumowania GPT-5 — kodowanie, matematyka, planowanie wieloetapowe.

Jeśli skierujesz 70% na produkty tanie i 30% na drogie, Twój rachunek spadnie o około 65% przy tej samej jakości produktu. To jest routing. Sztuka polega na zbudowaniu brokera bez pogorszenia jakości.

## Koncepcja

### Cztery sygnały routingu

1. **Klasyfikacja zadań**: proste/złożone/kodowanie/matematyka/czat. Może to być klasyfikator oparty na regułach, mały LLM (klasa Haiku za 0,25 USD/M) lub osadzający podobieństwo do oznaczonych segmentów. Wynik: trasa = tania / zrównoważona / granica.

2. **Długość podpowiedzi**: podpowiedzi >Tokeny 4K często wymagają granicy dla spójności. Podpowiedzi <500 tokenów zwykle tego nie robią.

3. **Osadzanie podobieństwa do znanego twardego zbioru**: jeśli zapytanie jest bliskie (cosinus > 0,88) znanego twardego zbioru, eskaluj bezpośrednio do granicy.

4. **Pewność siebie od pierwszego przejścia**: wyślij tanio; jeśli log-proby modelu wykazują niską pewność LUB odmawia LUB wyświetla język zabezpieczający, spróbuj ponownie na granicy. Dodaje opóźnienie P95 na ~10% ruchu, ale oszczędza ponad 50% na pozostałych 90%.

### Trzy wzory

**Przed trasą** (klasyfikator z przodu): dodano opóźnienie ~5–10 ms; najszybszy w sumie.

**Kaskada** (najpierw tanio, eskaluj przy niskim poziomie zaufania): ~1,2x średnie opóźnienie (tanie uruchomienie plus weryfikacja), ~2x przy eskalacji. Najlepsza jakość podłogi.

**Trasa zespołu** (bieżąca tania i graniczna równolegle dla próbki, wybór modelu w ramach nagrody): najwyższa jakość, najwyższy koszt; używać tylko dla krytycznych A/B.

### Implementacja

Bramy AI (faza 17 · 19) ujawniają routing. LiteLLM ma konfigurację `router` z rezerwą i routingiem kosztów. Świstoklik ma strażników i routing. Kong AI Gateway ma routing oparty na wtyczkach. Modelowy rynek OpenRouter udostępnia interfejs API rekomendacji.

Otwarte oprogramowanie: RouteLLM (LMSYS), Not Diamond (komercyjny), Prompt Mule.

### Krzywa cen w 2026 r

| Klasa modelu | Koniec 2022 r. | 2026 | Zmień |
|------------|----------|------|-------|
| Jakość na poziomie GPT-4 | ~$20/M | ~$0,40/M | 50x taniej |
| Granica (GPT-5, Claude 4) | — | ~3-10 USD/M | nowy poziom |

Większość ulepszeń dotyczy efektywności — główne wnioski z fazy 17 · 04-09 przełożyły się na spadek kosztów po stronie dostawcy. Routing pozwala przechwytywać te korzyści w warstwie aplikacji, zamiast czekać, aż wszyscy użytkownicy przejdą na migrację do tańszej warstwy.

### Dryf to prawdziwe ryzyko

Twoja trasa wysyła 40% do taniego modelu. W ciągu sześciu miesięcy zmienia się rozkład zadań (użytkownicy stają się bardziej wyrafinowani, zadają dłuższe pytania). Router tego nie zauważa, ponieważ jego klasyfikator został przeszkolony na danych z pierwszego kwartału. Jakość spada po cichu. Nikt nie narzeka wystarczająco głośno. W teście konkurencji dowiadujesz się, że przegrałeś.

Trasy bramek według wskaźników jakości online:

- Kciuk w górę / kciuk w dół dla każdej trasy.
- Automatyczna ocena LLM na zatrzymanej próbie (5%) na trasę.
- Tempo eskalacji: jeśli kaskada przyspiesza na trasie >30%, tani model jest przekierowywany.
- Wskaźnik odmów na trasie.

### Liczby, które powinieneś zapamiętać

- Oszczędności w routingu w jakości ISO w 2026 r.: studia przypadków 20-60%.
- Spadek cen LLM 2022-2026: łącznie ~10x rocznie.
– Poziom GPT-4 2022 vs 2026: ~$20/M → ~$0,40/M.
- Wpływ opóźnienia kaskadowego: mediana ~1,2x, eskalacja ~2x (~10% ruchu).

## Użyj tego

`code/main.py` symuluje trasę przed trasą, kaskadę i zespół przy mieszanym obciążeniu. Raportuje koszty mieszane, utratę jakości i tempo eskalacji.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-router-plan.md`. Biorąc pod uwagę obciążenie pracą i budżet na jakość, wybiera wzorzec routingu i sygnały.

## Ćwiczenia

1. Uruchom `code/main.py`. Z jaką dokładnością kaskada pokonuje trasę przed trasą?
2. Twoja baza użytkowników to 30% dla przedsiębiorstw (zapytania złożone), 70% z poziomu bezpłatnego (proste). Zaprojektuj podział routingu. Jaki wskaźnik online to ogranicza?
3. Trasa obniża jakość o 2%, ale oszczędza 40%. Czy to jest statek? Zależy od produktu — spieraj się o jedno i drugie.
4. Zaimplementuj kontrolę zaufania za pomocą logprobs z interfejsów API OpenAI/Anthropic. Od jakiego progu zaczynasz?
5. W ciągu sześciu miesięcy wskaźnik eskalacji wzrasta z 8% do 22%. Zdiagnozuj trzy przyczyny i naprawę dla każdej.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Model routingu | „broker kosztów” | Dynamiczny wybór modelu na żądanie |
| Modelowa kaskada | „eskalacja przede wszystkim tania” | Działaj tanio, spadaj do granicy przy niskim poziomie zaufania |
| Przed trasą | „najpierw klasyfikuj” | Klasyfikator z przodu; bez powtórki |
| Trasa zespołu | „wybór równoległy” | Uruchom wiele najlepszych modeli z nagrodami |
| Tempo eskalacji | „wywyższony procent” | Odsetek żądań kaskadowych, które uległy eskalacji |
| TrasaLLM | „Router LMSYS” | Biblioteka routerów OSS |
| Nie Diament | „router komercyjny” | Produkt do routingu modelu SaaS |
| Dryf | „tani pełzacz” | Zmiana dystrybucji bez zauważenia routera |
| Brama jakości online | „czek na żywo” | Zautomatyzowany sędzia LLM próbkujący ruch na żywo |

## Dalsze czytanie

– [AbhyashSuchi — Najlepsze praktyki dotyczące modelu routingu LLM 2026] (https://abhyashsuchi.in/model-routing-llm-2026-best-practices/)
– [Lukas Brunner — Rise of Inference Optimization 2026](https://dev.to/lukas_brunner/the-rise-of-inference-optimization-the-real-llm-infra-trend-shaping-2026-4e4o)
- [Dokument / kod RouteLLM](https://github.com/lm-sys/RouteLLM)
- [Not Diamond — trasowanie modelu] (https://www.notdiamond.ai/)
- [OpenRouter](https://openrouter.ai/) — brama wielomodelowa z podstawowymi metodami routingu.