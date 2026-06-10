# Konsensus i bizantyjska tolerancja błędów dla agentów

> Klasyczne systemy rozproszone BFT spełniają stochastyczne LLM. W latach 2025-2026 wyłoniły się trzy kierunki badawcze: **CP-WBFT** (arXiv:2511.10400) ważenie każdego głosu sondą zaufania; **DecentLLM** (arXiv:2507.14928) nie posiada lidera, oferując równoległe propozycje pracowników i agregację geometryczno-medianową; **WBFT** (arXiv:2505.05103) łączy głosowanie ważone z grupowaniem struktur hierarchicznych w celu rozdzielenia węzłów rdzeniowych i brzegowych. Uczciwy wynik empiryczny z artykułu „Czy agenci AI mogą się zgodzić?” (arXiv:2603.01213) polega na tym, że nawet porozumienie skalarne jest dziś kruche — pojedynczy zwodniczy agent może zagrozić mieszance agentów. BFT jest konieczne, ale niewystarczające. Ta lekcja buduje minimalny protokół BFT, wprowadza trzy ataki specyficzne dla agenta (kłamstwo bizantyjskie, pochlebczy konformizm, monokultura błędów skorelowanych) i mierzy, jak radzi sobie każdy wariant konsensusu.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 07 (Społeczeństwo umysłu i debaty), Faza 16 · 13 (Wspólna pamięć)
**Czas:** ~75 minut

## Problem

Masz N agentów LLM, z których każdy udziela odpowiedzi. Nie zgadzają się. Większość głosów wybiera niewłaściwego, ponieważ dwaj agenci są skorelowani (ten sam model podstawowy, te same dane szkoleniowe, te same tryby awarii). Tak się składa, że ​​trzeci czynnik myli się w nowatorski sposób – więc większość to fałszywa większość.

Teraz dodaj zwodniczego agenta: kłamie celowo. Albo pochlebca: zgadza się z tym, kto mówił ostatni. W klasycznym BFT zakłada się, że węzły bizantyjskie są ułamkiem `f < n/3` i zachowują się arbitralnie. Rzeczywistość na rok 2026 jest taka, że ​​węzły LLM są stochastyczne, nawet jeśli są uczciwe, skorelowane między modelami i wpływają na siebie wzajemnie. Nie można ich traktować jak niezależnych wyborców Bernoulliego.

Klasyczna metoda BFT (PBFT, 1999) nie jest błędna — jest niekompletna. Obsługuje dowolne przerzucanie bitów. Nie dotyczy sytuacji, w której „trzech uczciwych agentów ma halucynacje, ponieważ dzielą się danymi szkoleniowymi”. Ta lekcja opiera się na podstawach PBFT i składa się z trzech adaptacji na lata 2025–2026.

## Koncepcja

### Co daje klasyczne BFT

Praktyczna tolerancja błędów bizantyjskich (Castro i Liskov, OSDI 1999) toleruje `f < n/3` węzły bizantyjskie. Protokół ma trzy fazy (przygotowanie wstępne, przygotowanie, zatwierdzenie) i dwie fazy podstawowe (podpisane wiadomości, certyfikaty kworum). Zgoda na pojedynczą wartość między `n >= 3f + 1` uczciwymi lub złośliwymi węzłami.

Gwarancje są mocne, ale zakładają:

1. **Niezależne błędy.** Bizantyjczycy nie koordynują.
2. **Uczciwe węzły są naprawdę uczciwe.** Poprawność uczciwych wyników nie stanowi problemu; protokół jedynie wyrównuje różnice zdań.
3. **Na to pytanie można odpowiedzieć zgodnie z prawdą.** Konsensus co do błędnego faktu jest nadal konsensusem.

Agenci LLM naruszają wszystkie trzy. Dwóch agentów korzystających z tego samego modelu podstawowego ma wspólne błędy. „Uczciwy” LLM wciąż ma halucynacje. A w kwestiach niejednoznacznych o „prawdzie” decydują agenci – nie ma zewnętrznej wyroczni.

### Trzy ataki specyficzne dla LLM

**Bizantyjskie kłamstwo.** Jeden z agentów celowo podaje błędną odpowiedź. Klasyczny BFT radzi sobie z tym, jeśli `f < n/3`.

**Pochlebczy konformizm.** Jeden agent czyta odpowiedzi innych przed głosowaniem i przyłącza się do tego, kto wypowiadał się jako ostatni. Nie złośliwy, ale koreluje z najgłośniejszym głosem. Klasyczny BFT temu nie zapobiega, ponieważ agent przechodzi każdą kontrolę podpisu.

**Monokultura ze skorelowanymi błędami.** Trzech agentów ma ten sam model podstawowy. Mają halucynacje z tą samą błędną odpowiedzią. Większość się myli. Klasyczne BFT nie pomaga, bo cała trójka „uczciwie” się z tym zgadza.

### Odpowiedzi na lata 2025–2026

**CP-WBFT** (arXiv:2511.10400) — BFT ważony z sondą zaufania. Każdy wyborca ​​dołącza do swojej odpowiedzi sondę zaufania (prawdopodobieństwo zgłaszane przez siebie lub przewidywanie oddzielnego modelu kalibracyjnego). Głosuj na skali wagowej z pewnością. Zgłoszono poprawę BFT o +85,71% na pełnych wykresach. Łagodzenie: pochlebczego konformizmu (agenci dostosowujący się do wymagań mają zwykle niskie zaufanie do swojego dobrowolnego stanowiska).

**PrzyzwoiteLLM** (arXiv:2507.14928) — Bez przywódcy. Agenci-pracownicy proponują równolegle, agenci oceniający oceniają propozycje, ostateczną odpowiedzią jest mediana geometryczna punktowanych pozycji. Solidny, gdy `f < n/2`. Łagodzenie: kłamstw bizantyjskich i skorelowanych błędów (mediana geometryczna jest odporna na wartości odstające i przyciąga gęste skupienie, a nie średnią wynikającą z modelu).

**WBFT** (arXiv:2505.05103) — ważony BFT z grupowaniem struktury hierarchicznej. Wagi głosów są przypisywane na podstawie jakości odpowiedzi oraz wyniku zaufania wyciągniętego z historii. Grupuj agentów w Core i Edge; Agenci główni muszą najpierw osiągnąć konsensus, a następnie agenci brzegowi. Łagodzenie dla: skalowalności (konsensus rdzenia jest mały i szybki) i częściowo dla monokultury (rdzeń można wybrać ze względu na różnorodność).

### Empiryczne: „Czy agenci AI mogą się zgodzić?” (arXiv:2603.01213)

W artykule mierzy się zgodność skalarną (agenci LLM uzgadniają pojedynczą wartość liczbową) w wielu modelach granicznych. Odkrycie jest niewygodne:

- Nawet nie mając przeciwników, agenci LLM nie zgadzają się w kwestiach skalarnych przy wskaźnikach przekraczających 30% w wielu benchmarkach.
- Pojedynczy agent, który przyjmuje zwodniczą osobowość, może odciągnąć konsensus dotyczący mieszanki agentów o ponad 40 punktów procentowych od uczciwego poziomu bazowego.
- Wskaźniki niezgodności korelują ze różnorodnością modelu — zespoły heterogeniczne nie zgadzają się częściej niż zespoły jednorodne (dobrze: nieskorelowane błędy), ale także dryfują wolniej (źle: dłuższy czas do osiągnięcia porozumienia).

Wniosek na wynos: BFT zapewnia maszynę do wyrównywania wyników, ale nie mówi, czy wyrównane wyniki są prawidłowe. Połącz z weryfikacją (specjalizacja ról 16 · 08), różnorodnością (faza 16 · 15 wariantów debaty) i agentami oceniającymi (faza 16 · 24 punkty odniesienia).

### Podstawowy protokół, okrojony

Minimalna runda BFT dla agentów LLM:

```
1. task arrives; each agent i produces answer a_i
2. each agent attaches confidence probe c_i in [0, 1]
3. aggregator collects (a_i, c_i) from all n agents
4. aggregator groups by semantic cluster (equivalent answers)
5. aggregator computes weight for each cluster C:
     w(C) = sum_{i in C} c_i
6. winner = cluster with max weight, if max > threshold * sum(c_i)
   else: retry or escalate
7. minority clusters logged with provenance for post-hoc audit
```

Etap grupowania semantycznego jest zwrotem specyficznym dla LLM. Dwie odpowiedzi „z badania wynika, że ​​4,2%” i „4,2% poprawy” dotyczą tego samego skupienia. Naiwna kontrola równości ciągów mogłaby to pominąć. W środowisku produkcyjnym użyj taniego modelu osadzania lub jawnej kanonizacji.

### Strojenie progu

Parametr `threshold` decyduje, kiedy zaakceptować, a kiedy ponowić próbę. Zbyt niski: akceptujesz słabą większość. Za wysoko: nigdy niczego nie akceptujesz. Zakres empiryczny: 0,5-0,67 dla agentów `n=5-7`, wyższy dla mniejszych `n`. Poniżej progu eskaluj do człowieka lub do innego zespołu agentów.

### Gdzie konsensus nie pomaga

- **Pytania niejednoznaczne.** Jeśli w pytaniu nie ma podstaw, konsensus jest opinią. Nazwij to tak.
- **Pytania złożone.** „Napisz kod i wyjaśnij go” — dwie odpowiedzi. Głosujcie na każdego niezależnie.
- **Wielorundowy konflikt.** Jeśli agenci potrafią obserwować poprzednie rundy i naśladować (debata Du 2023), zaczynają się ze sobą zgadzać niezależnie od prawdy. Związałem rundy (zwykle 2-3).

## Zbuduj to

`code/main.py` implementuje:

- `AgentVoter` — polityka skryptowa z (odpowiedzią, pewnością).
- `MajorityVote` — klasyczna mnogość.
- `CPWBFT` — głosowanie ważone pewnością siebie z grupowaniem semantycznym.
- `DecentLLMs` — agregacja mediany geometrycznej dla ocenionych propozycji.
- `Scenario` — uruchamia każdy agregator w oparciu o trzy wzorce ataków.

Zaimplementowane wzorce ataków:

1. `byzantine`: jeden agent ma dużą pewność.
2. `sycophancy`: jeden agent kopiuje pierwszą odpowiedź, którą widzi, z dopasowaną pewnością.
3. `monoculture`: trzech agentów podaje błędną odpowiedź (skorelowany błąd) z umiarkowaną pewnością.

Uruchom:

```
python3 code/main.py
```

Oczekiwany wynik: tabela (atak, agregator) -> ostateczna odpowiedź z podświetloną poprawną odpowiedzią. Wielość nie sprawdza się w przypadku monokultury. Waga zaufania CPWBFT łagodzi pochlebstwa. Mediana geometryczna przyzwoitych LLM zbliża się do klastra uczciwego, gdy monokultura obejmuje mniej niż połowę populacji.

## Użyj tego

`outputs/skill-consensus-designer.md` projektuje protokół konsensusu dla zestawu składającego się z wielu agentów: metoda grupowania, ważenie, próg i polityka eskalacji dla rund podprogowych.

## Wyślij to

Przed wysyłką jakiegokolwiek mechanizmu konsensusu:

- **Test ataku z co najmniej trzema wzorami** powyżej. Twój protokół powinien zawieść w przewidywalny sposób, a nie po cichu.
- **Zaloguj każdą grupę mniejszościową** z pochodzeniem. Klastry mniejszościowe to system wczesnego ostrzegania o skorelowanych błędach.
- **Egzekwuj ograniczone rundy.** Nie „dyskutuj aż do porozumienia” – to nagradza pochlebstwo.
- **Oddziel zgodę od poprawności.** Wynik konsensusu trafia do weryfikatora; weryfikator jest niezależny od zespołu.
- **Monitoruj wskaźnik zgodności.** Gwałtowny wzrost oznacza stronniczość konformistyczną; gwałtowny spadek oznacza dryf modelu.

## Ćwiczenia

1. Uruchom `code/main.py`. Potwierdź, że mnogość nie udaje się atakowi monokultury, ale CPWBFT częściowo łagodzi go, gdy pewność monokultury jest niższa niż 0,7.
2. Dodaj czwarty wzór ataku: **ciche wstrzymanie się** – jeden agent odmawia odpowiedzi („nie wiem”). Jak każdy agregator powinien traktować wstrzymanie się od głosu? Realizuj swój wybór.
3. Zamień grupowanie semantyczne z kanonizacji ciągów na podobieństwo osadzania (użyj dowolnego modelu osadzania typu open source). Co się stanie z atakiem pochlebstwa?
4. Przeczytaj CP-WBFT (arXiv:2511.10400). Wdrożyć etap kalibracji sondy zaufania (oddzielny model kalibracji sprawdza pewność zgłaszaną przez każdego agenta). Zmierz przyrost dokładności w scenariuszu monokultury.
5. Przeczytaj „Czy agenci AI mogą się zgodzić?” (arXiv:2603.01213). Odtwórz uproszczony eksperyment dotyczący zgodności skalarnej: trzech agentów, jedno pytanie skalarne, podpowiedź dotycząca osoby zwodniczej. Czy CPWBFT lub DecentLLM to wyłapują?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| BFT | „Bizantyjska tolerancja na błędy” | Protokół Castro-Liskov 1999 dotyczący konsensusu z `f < n/3` arbitralnymi błędami. |
| bizantyjski | „Każde złe zachowanie” | Węzeł, który może kłamać, upuszczać wiadomości, awaryjnie działać po cichu – wszystko z wyjątkiem bezpiecznej awarii. |
| Sonda zaufania | – Jak pewien jesteś? | Prawdopodobieństwo zgłaszane samodzielnie lub przewidywane przez kalibrator dołączone do głosowania. |
| Grupowanie semantyczne | „Ta sama odpowiedź, inne słowa” | Grupowanie równoważnych odpowiedzi przed zliczeniem głosów. |
| Mediana geometryczna | „Solidne centrum” | Punkt minimalizujący sumę odległości do punktów próbkowania. Odporny na wartości odstające, w przeciwieństwie do średniej. |
| Monokultura | „Ten sam model, te same awarie” | Skorelowane błędy, gdy agenci udostępniają dane szkoleniowe lub model podstawowy. |
| Pochlebczy konformizm | „Zgadzam się z donośnym głosem” | Głos agenta faworyzuje tego, kto przemówił pierwszy/najgłośniej. |
| Rdzeń/krawędź | „Hierarchiczny BFT” | Podział WBFT: najpierw mały konsensus rdzenia, następnie węzły brzegowe. Ogranicza opóźnienie. |

## Dalsze czytanie

- [Castro i Liskov — Praktyczna tolerancja błędów bizantyjskich (OSDI 1999)] (https://pmg.csail.mit.edu/papers/osdi99.pdf) — podstawa
- [CP-WBFT — Confidence-Probe Weighted BFT](https://arxiv.org/abs/2511.10400) — ważenie głosów według zaufania
- [DecentLLMs — konsensus wieloagentowy bez lidera](https://arxiv.org/abs/2507.14928) — agregacja geometryczno-mediana
- [WBFT — ważony BFT z klastrowaniem struktury hierarchicznej] (https://arxiv.org/abs/2505.05103) — podział na rdzeń/krawędź w celu ograniczenia opóźnień
— [Czy agenci AI mogą się zgodzić?](https://arxiv.org/abs/2603.01213) — kruchość porozumienia skalarnego i atak na osobę zwodniczą