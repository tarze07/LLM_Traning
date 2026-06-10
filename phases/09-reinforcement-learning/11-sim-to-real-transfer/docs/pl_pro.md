# Transfer z Sima do Realu

> Polityka wyszkolona w symulatorze, która zawodzi na sprzęcie, zapamiętała symulator — nie zadanie. Randomizacja domeny, adaptacja domeny i identyfikacja systemu to trzy narzędzia pozwalające wyuczonym kontrolerom pokonać lukę między symulacją a rzeczywistością.

**Typ:** Ucz się
**Języki:** Python
**Wymagania wstępne:** Faza 9 · 08 (PPO), Faza 2 · 10 (odchylenie/wariancja)
**Czas:** ~45 minut

## Problem

Szkolenie prawdziwego robota jest powolne, niebezpieczne i kosztowne. Robot dwunożny potrzebuje milionów epizodów treningowych, by nauczyć się chodzić — a każdy upadek grozi uszkodzeniem sprzętu. Symulacja oferuje nieograniczone resetowanie środowiska, deterministyczną odtwarzalność, równoległe instancje i brak ryzyka fizycznych zniszczeń.

Symulatory nie są jednak doskonałe. Łożyska wykazują większe tarcie niż przewidują modele MuJoCo. Kamery wprowadzają zniekształcenia optyczne, których symulator nie uwzględnia. Silniki mają opóźnienia, luzy i nasycenie, ignorowane przez większość modeli fizycznych. Wiatr, kurz i zmienne oświetlenie sabotują politykę wytrenowaną w sterylnym środowisku renderowania. **Luka rzeczywistości** — systematyczna rozbieżność między rozkładem symulacyjnym a rzeczywistym — jest główną przeszkodą przy wdrażaniu systemów RL w robotyce.

Potrzebna jest polityka *odporna na zmianę rozkładu między symulacją a rzeczywistością*. Stosuje się trzy podejścia: randomizacja parametrów symulatora (randomizacja domeny), dostosowanie polityki z użyciem niewielkiej ilości rzeczywistych danych (adaptacja domeny / dostrajanie) oraz identyfikacja parametrów rzeczywistego systemu i dopasowanie ich do symulatora (identyfikacja systemu). W roku 2026 dominuje podejście łączące wszystkie trzy techniki z masową symulacją równoległą (Isaac Sim, Isaac Lab, MuJoCo MJX na GPU).

## Koncepcja

![Trzy tryby sim-to-real: randomizacja domeny, adaptacja, identyfikacja systemu](../assets/sim-to-real.svg)

**Randomizacja domeny (DR).** Tobin i in. 2017, Peng i in. 2018. Podczas treningu losuje się każdy parametr symulatora, który może odbiegać od wartości rzeczywistych: masy, współczynniki tarcia, wzmocnienia sterownika PD, szum czujnika, położenie kamery, oświetlenie, tekstury, modele kontaktu. Polityka uczy się rozkładu warunkowego zależnego od bieżących parametrów symulatora i uogólnia go na cały zakres. Jeśli rzeczywisty robot mieści się w tym zakresie, polityka działa.

- **Zaleta:** nie są wymagane żadne rzeczywiste dane. Jeden przepis — wiele robotów.
- **Wada:** nadmierna randomizacja prowadzi do polityki uniwersalnej, lecz nazbyt zachowawczej. Zbyt duży szum działa jak zbyt silna regularyzacja.

**Identyfikacja systemu (SI).** Przed treningiem parametry symulatora dopasowuje się do danych rzeczywistych. Jeśli możliwy jest pomiar tarcia w stawach ramion robota, zmierzone wartości wprowadza się do symulatora. Następnie trenuje się politykę oczekującą tych konkretnych parametrów. Metoda wymaga dostępu do rzeczywistego systemu, ale bezpośrednio zmniejsza lukę rzeczywistości.

- **Zaleta:** precyzyjny cel treningowy z niskim poziomem szumu.
- **Wada:** resztkowy błąd modelu pozostaje niewidoczny dla polityki; drobne, niezidentyfikowane efekty (np. strefa nieczułości silnika) nadal zaburzają działanie po wdrożeniu.

**Adaptacja domeny.** Trening odbywa się w symulatorze, po czym politykę dostosowuje się z użyciem niewielkiej ilości rzeczywistych danych. Wyróżnia się dwa warianty:

- **Real2Sim2Real:** uczenie modelu resztkowego `f(s, a, z) - f_sim(s, a)` na podstawie rzeczywistych wdrożeń, a następnie trening w ulepszonym symulatorze. Metoda zamyka lukę bez konieczności gromadzenia dużej ilości danych rzeczywistych.
- **Adaptacja obserwacji:** trening polityki przekształcającej rzeczywiste obserwacje na obserwacje zbliżone do symulacyjnych za pomocą wyuczonego ekstraktora cech (np. GAN piksel po pikselu). Sterownik pozostaje w przestrzeni symulacyjnej.

**Uczenie z nauczycielem i uczniem.** Miki i in. 2022 (ANYmal). W symulacji trenuje się *nauczyciela* z dostępem do informacji uprzywilejowanych (tarcie podłoża, profil terenu, dryf IMU). Następnie destyluje się *ucznia*, który widzi wyłącznie obserwacje dostępne rzeczywistym czujnikom. Uczeń uczy się wnioskować o cechach uprzywilejowanych z historii obserwacji, co czyni go odpornym na zmienność parametrów fizycznych.

**Masowo równoległa symulacja.** 2024–2026. Isaac Lab, MuJoCo MJX i Brax obsługują tysiące równoległych robotów na jednej karcie graficznej. PPO z 4096 równoległymi humanoidami gromadzi lata doświadczeń w ciągu kilku godzin. Luka rzeczywistości maleje wraz z poszerzaniem rozkładu treningowego; randomizacja domeny staje się praktycznie bezkosztowa, gdy każde środowisko ma odmienne, losowe parametry.

**Sprawdzony przepis na rok 2026 (przykład: chodzenie czworonogów):**

1. Masowo równoległy symulator z losowanymi parametrami domeny: grawitacja, tarcie, wzmocnienia silników, ładunek.
2. Polityka nauczyciela trenowana z dostępem do informacji uprzywilejowanych (mapa terenu, prędkość ciała w układzie bezwzględnym).
3. Polityka ucznia destylowana od nauczyciela, korzystająca wyłącznie z propriocepcji (enkodery stawów).
4. Opcjonalna adaptacja obserwacji za pomocą autoenkodera na rzeczywistym IMU.
5. Wdrożenie. Zerowy transfer w ponad 10 środowiskach. Jeśli wyniki są niezadowalające, przeprowadza się kilka minut dostrajania w warunkach rzeczywistych za pomocą PPO z ograniczeniami bezpieczeństwa.

## Zbuduj to

Kod tej lekcji to zwięzła demonstracja randomizacji domeny w GridWorld z *zaszumionymi* przejściami. Trenujemy politykę, która podczas uczenia napotyka losowe prawdopodobieństwa poślizgu w „symulatorze", a następnie jest oceniana przy wartości poślizgu, której nie widziała w trakcie treningu. Schemat ten bezpośrednio odpowiada transferowi z MuJoCo na sprzęt fizyczny.

### Krok 1: sparametryzowany symulator

```python
def step(state, action, slip):
    if rng.random() < slip:
        action = random_perpendicular(action)
    ...
```

`slip` to parametr udostępniany przez symulator. W rzeczywistej robotyce może nim być tarcie, masa, wzmocnienie silnika — cokolwiek, co różni się między symulacją a rzeczywistością.

### Krok 2: trenuj z DR

Na początku każdego epizodu losuj `slip ~ Uniform[0.0, 0.4]`. Trenuj PPO, Q-learning lub inny wybrany algorytm przez wiele epizodów.

### Krok 3: oceń zerowy transfer na „rzeczywistych" wartościach poślizgu

Oceń politykę dla `slip ∈ {0.0, 0.1, 0.2, 0.3, 0.5, 0.7}`. Pierwsze cztery wartości mieszczą się w zakresie treningowym; `0.5` i `0.7` leżą poza nim. Polityka wytrenowana z DR powinna utrzymywać niemal optymalne wyniki wewnątrz zakresu i stopniowo degradować się poza nim. Polityka trenowana przy stałej wartości poślizgu będzie krucha poza swoim wąskim zakresem.

### Krok 4: porównaj z treningiem wąskozakresowym

Wytrenuj drugą politykę wyłącznie przy `slip = 0.0`. Oceń ją w tym samym zestawie wartości. Powinien być widoczny gwałtowny spadek wydajności, gdy tylko rzeczywisty poślizg przekroczy 0.

## Pułapki

- **Zbyt duża randomizacja.** Trening przy `slip ∈ [0, 0.9]` sprawia, że polityka staje się tak zachowawcza, iż nigdy nie próbuje optymalnej ścieżki. Zakres treningowy powinien odpowiadać *spodziewanemu* rozkładowi wartości w rzeczywistości, a nie zasadzie „wszystko możliwe".
- **Zbyt mała randomizacja.** Wąski zakres treningowy uniemożliwia uogólnianie. Warto zastosować program adaptacyjny (automatyczna randomizacja domeny), który poszerza rozkład w miarę poprawy polityki.
- **Błędnie dobrana przestrzeń parametrów.** Losowanie nieistotnych czynników (np. odcień kamery, gdy kluczowe jest opóźnienie silnika) sprawia, że DR nie przynosi efektów. Przed treningiem należy sprofilować rzeczywistego robota.
- **Wyciek informacji uprzywilejowanych.** Jeśli nauczyciel opiera decyzje na stanie globalnym zamiast na obserwacjach, uczeń może nie być w stanie go naśladować. Polityka nauczyciela musi być realizowalna przez ucznia dysponującego tylko historią obserwacji.
- **Błąd transferu między wariantami symulatora.** Polityka nieodporna na trudniejszy wariant symulatora nie będzie odporna w warunkach rzeczywistych. Przed wdrożeniem zawsze należy testować na wariancie wyciągniętym poza zakres treningowy.
- **Brak osłony bezpieczeństwa.** Polityka działająca w symulatorze i wdrożona w świecie rzeczywistym bez niskopoziomowych zabezpieczeń może uszkodzić sprzęt. Niezbędne jest dodanie ograniczeń prędkości, momentu obrotowego i zakresów stawów w niezależnym sterowniku.

## Użyj tego

Typowy stos sim-to-real na rok 2026:

| Domena | Stos |
|------------|-------|
| Lokomocja na nogach (ANYmal, Spot, humanoid) | Isaac Lab + DR + nauczyciel/uczeń z informacjami uprzywilejowanymi |
| Manipulacja (dłonie, pick-and-place) | Isaac Lab + DR + DR-GAN dla wizji |
| Jazda autonomiczna | CARLA / NVIDIA DRIVE Sim + DR + dostrajanie na danych rzeczywistych |
| Wyścigi dronów | RotorS / Flightmare + DR + adaptacja online |
| Manipulacja palcami/dłonią | OpenAI Dactyl (DR w bezprecedensowej skali) |
| Manipulatory przemysłowe | MuJoCo-Warp + SI + niewielkie dostrajanie na danych rzeczywistych |

Przepływ pracy jest spójny niezależnie od skali: dopasuj symulator najdokładniej jak to możliwe, losuj to, czego nie możesz dopasować, wytrenuj rozbudowaną politykę, przeprowadź destylację, wdróż z osłoną bezpieczeństwa.

## Wyślij to

Zapisz jako `outputs/skill-sim2real-planner.md`:

```markdown
---
name: sim2real-planner
description: Plan a sim-to-real transfer pipeline for a given robot + task, covering DR, SI, and safety.
version: 1.0.0
phase: 9
lesson: 11
tags: [rl, sim2real, robotics, domain-randomization]
---

Given a robot platform, a task, and access to real hardware time, output:

1. Reality gap inventory. Suspected sources ranked by expected impact (contact, sensing, actuation delay, vision).
2. DR parameters. Exact list, ranges, distribution. Justify each range against real measurements.
3. SI steps. Which parameters to measure; measurement method.
4. Teacher/student split. What privileged info the teacher uses; what obs the student uses.
5. Safety envelope. Low-level limits, emergency stops, backup controller.

Refuse to deploy without (a) a zero-shot sim-variant test, (b) a safety shield, (c) a rollback plan. Flag any DR range wider than 3× measured real variability as likely over-randomized.
```

## Ćwiczenia

1. **Łatwe.** Wytrenuj agenta Q-learning w GridWorld przy stałym poślizgu (slip = 0,0). Oceń go przy slip ∈ {0,0; 0,1; 0,3; 0,5}. Wykreśl zwrot epizodyczny w funkcji poślizgu.
2. **Średni.** Wytrenuj agenta Q-learning z DR, próbkując `slip ~ Uniform[0, 0.3]`. Porównaj wyniki z poprzednim agentem. O ile DR poprawia wyniki przy slip = 0,5 (poza zakresem treningowym)?
3. **Trudne.** Zaimplementuj program nauczania: zacznij od slip = 0,0 i poszerzaj zakres DR za każdym razem, gdy polityka osiągnie 90% wartości optymalnej. Zmierz łączną liczbę kroków potrzebnych do osiągnięcia zerowego transferu przy slip = 0,3 i porównaj ze stałą linią bazową DR.

## Kluczowe terminy

| Termin | Potoczne określenie | Właściwe znaczenie |
|------|-----------------|----------------------|
| Luka rzeczywistości | „Różnica między symem a prawdziwym" | Zmiana rozkładu między fizyką i percepcją podczas treningu a podczas wdrożenia. |
| Randomizacja domeny (DR) | „Trenuj na losowych symulatorach" | Losowanie parametrów symulatora podczas treningu w celu uogólnienia polityki. |
| Identyfikacja systemu (SI) | „Zmierz rzeczywistość i dopasuj symulator" | Estymacja rzeczywistych parametrów fizycznych; dostrojenie symulatora do zmierzonych wartości. |
| Adaptacja domeny | „Dostraj na danych rzeczywistych" | Niewielkie dostrajanie po treningu w symulatorze; może obejmować adaptację obserwacji lub dynamiki. |
| Informacje uprzywilejowane | „Prawda absolutna dla nauczyciela" | Dane dostępne tylko w symulatorze; uczeń musi je wnioskować z historii obserwacji. |
| Nauczyciel/uczeń | „Destyluj uprzywilejowane do obserwowalnych" | Nauczyciel trenowany ze skrótami; uczeń uczy się go naśladować bez dostępu do nich. |
| ADR | „Automatyczna randomizacja domeny" | Program nauczania poszerzający zakres DR w miarę poprawy polityki. |
| Real2Sim | „Wypełnij lukę danymi rzeczywistymi" | Uczenie modelu resztkowego, by symulator naśladował rzeczywiste wdrożenia. |

## Dalsze czytanie

- [Tobin i in. (2017). Randomizacja domeny w celu przeniesienia głębokich sieci neuronowych z symulacji do świata rzeczywistego](https://arxiv.org/abs/1703.06907) — oryginalny artykuł o DR (wizja w robotyce).
- [Peng i in. (2018). Transfer kontroli robotycznej z Sim-to-Real z randomizacją dynamiki](https://arxiv.org/abs/1710.06537) — DR dla dynamiki, lokomocja czworonogów.
- [OpenAI i in. (2019). Układanie kostki Rubika ręką robota](https://arxiv.org/abs/1910.07113) — Dactyl, ADR w dużej skali.
- [Miki i in. (2022). Nauka odpornej percepcyjnej lokomocji czworonożnych robotów w naturalnym środowisku](https://www.science.org/doi/10.1126/scirobotics.abk2822) — metoda nauczyciela-ucznia na ANYmal.
- [Makoviychuk i in. (2021). Isaac Gym: wysokowydajna symulacja fizyki na GPU do uczenia robotów](https://arxiv.org/abs/2108.10470) — masowo równoległy symulator napędzający wdrożenia w latach 2025–2026.
- [Akkaya i in. (2019). Automatyczna randomizacja domeny](https://arxiv.org/abs/1910.07113) — metoda programu nauczania ADR.
- [Sutton i Barto (2018). Rozdz. 8 — Planowanie i uczenie się metodami tabelarycznymi](http://incompleteideas.net/book/RLbook2020.pdf) — paradygmat Dyna (użyj modelu do planowania i wdrożenia), stanowiący podstawę nowoczesnych potoków sim-to-real.
- [Zhao, Queralta i Westerlund (2020). Transfer sim-to-real w uczeniu głębokim ze wzmocnieniem w robotyce: przegląd](https://arxiv.org/abs/2009.13303) — taksonomia metod sim-to-real z wynikami benchmarków.
