# Głębokie sieci Q (DQN)

> W 2013 roku Mnih wytrenował jedną sieć Q-learningową na surowych pikselach i pokonał wszystkich klasycznych agentów RL w siedmiu grach Atari. Dwa lata później rozszerzenie do 49 gier, opublikowane w Nature, zapoczątkowało erę głębokiego RL. DQN to Q-learning uzupełniony o trzy mechanizmy stabilizujące aproksymację funkcji.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 3 · 03 (propagacja wsteczna), Faza 9 · 04 (Q-learning, SARSA)
**Czas:** ~75 minut

## Problem

Tabelaryczny Q-learning wymaga osobnej wartości Q dla każdej pary (stan, akcja). Szachownica ma około 10⁴³ stanów. Pojedyncza klatka Atari ma wymiary 210×160×3 = 100 800 cech. Podejście tabelaryczne przestaje działać już przy tysiącach stanów — przy miliardach jest zupełnie bezużyteczne.

Rozwiązanie wydaje się oczywiste z perspektywy czasu: zastąp tabelę Q siecią neuronową, `Q(s, a; θ)`. Paradoksalnie jednak dotarcie do tego pomysłu zajęło kilkadziesiąt lat. Naiwna aproksymacja funkcji w połączeniu z Q-learningiem rozbiega się w ramach tzw. „śmiertelnej triady" — aproksymacja funkcji, bootstrapping i uczenie poza polityką. Mnih i in. (2013, 2015) zidentyfikowali trzy rozwiązania inżynieryjne stabilizujące uczenie:

1. **Powtórka doświadczeń** dekoreluje kolejne przejścia.
2. **Sieć docelowa** unieruchamia cel bootstrappingu.
3. **Obcinanie nagród** normalizuje skalę gradientu.

DQN na Atari był pierwszym przypadkiem, w którym pojedyncza architektura z jednym zestawem hiperparametrów poradziła sobie z dziesiątkami zadań sterowania na podstawie surowych pikseli. Wszystkie późniejsze metody głębokiego RL — DDQN, Rainbow, Dueling, Distributional, R2D2, Agent57 — wyrastają właśnie z tych trzech fundamentów.

## Koncepcja

![Pętla treningowa DQN: env, bufor powtórek, sieć online, sieć docelowa, strata Bellmana](../assets/dqn.svg)

**Cel.** DQN minimalizuje jednostopniową stratę TD dla neuronowej funkcji Q:

`L(θ) = E_{(s,a,r,s')~D} [ (r + γ max_{a'} Q(s', a'; θ^-) - Q(s, a; θ))² ]`

`θ` = sieć online, aktualizowana co krok przez stochastyczne opadanie gradientu. `θ^-` = sieć docelowa, kopiowana z `θ` co ~10 000 kroków. `D` = bufor odtwarzania wcześniejszych przejść.

**Trzy mechanizmy według ważności:**

**Powtórka doświadczeń.** Bufor cykliczny przechowuje do ~10⁶ przejść. Na każdym etapie treningu losowo i równomiernie pobierana jest minipartia. Mechanizm ten przerywa korelację czasową (kolejne klatki są niemal identyczne), umożliwia sieci wielokrotne uczenie się na rzadkich, wartościowych przejściach i dekoreluje kolejne aktualizacje gradientów. Bez niego uczenie metodą TD przy użyciu sieci neuronowej rozbiega się na Atari.

**Sieć docelowa.** Korzystanie z tej samej sieci `Q(·; θ)` po obu stronach równania Bellmana sprawia, że cel przesuwa się przy każdej aktualizacji — agent goni własny ogon. Rozwiązaniem jest utrzymywanie drugiej sieci `Q(·; θ^-)` z zamrożonymi wagami. Co `C` kroków kopiuje się `θ → θ^-`. Stabilizuje to cel regresji przez tysiące kroków gradientu. Miękkie aktualizacje `θ^- ← τ θ + (1-τ) θ^-` (stosowane w DDPG i SAC) stanowią łagodniejszy wariant tej samej idei.

**Obcinanie nagród.** Nagrody w Atari wahają się od 1 do ponad 1000. Obcięcie do zbioru `{-1, 0, +1}` zapobiega zdominowaniu gradientu przez wyniki z jednej gry. Wadą jest utrata informacji o bezwzględnej skali nagrody — w Atari, gdzie liczy się wyłącznie znak, jest to akceptowalne.

**Double DQN.** Hasselt (2016) naprawia błąd nadmiernej estymacji: sieć online służy do *wyboru* akcji, a sieć docelowa do *jej oceny*.

`target = r + γ Q(s', argmax_{a'} Q(s', a'; θ); θ^-)`

To zamiennik bez modyfikacji architektury, który konsekwentnie daje lepsze wyniki. Warto stosować go domyślnie.

**Inne ulepszenia (Rainbow, 2017):** powtórka z priorytetami (częstsze próbkowanie przejść o dużym błędzie TD), architektura Dueling (osobne głowice `V(s)` i przewagi), sieci z szumem (wyuczona eksploracja), wielokrokowe zwroty, dystrybucyjne Q (C51/QR-DQN), wieloetapowy bootstrapping. Każde z nich przynosi kilka punktów procentowych poprawy, a zyski są w przybliżeniu addytywne.

## Zbuduj to

Poniższy kod nie korzysta z NumPy — używamy ręcznie zbudowanego jednowarstwowego MLP w miniaturowym, dyskretnym środowisku GridWorld, dzięki czemu każdy krok uczenia trwa mikrosekund. Algorytm jest identyczny z Atari DQN, różni się jedynie skalą.

### Krok 1: bufor odtwarzania

```python
class ReplayBuffer:
    def __init__(self, capacity):
        self.buf = []
        self.capacity = capacity
    def push(self, s, a, r, s_next, done):
        if len(self.buf) == self.capacity:
            self.buf.pop(0)
        self.buf.append((s, a, r, s_next, done))
    def sample(self, batch, rng):
        return rng.sample(self.buf, batch)
```

Pojemność ~50 000 dla Atari; 5000 wystarczy dla naszego środowiska testowego.

### Krok 2: mała sieć Q (ręczne MLP)

```python
class QNet:
    def __init__(self, n_in, n_hidden, n_actions, rng):
        self.W1 = [[rng.gauss(0, 0.3) for _ in range(n_in)] for _ in range(n_hidden)]
        self.b1 = [0.0] * n_hidden
        self.W2 = [[rng.gauss(0, 0.3) for _ in range(n_hidden)] for _ in range(n_actions)]
        self.b2 = [0.0] * n_actions
    def forward(self, x):
        h = [max(0.0, sum(w * xi for w, xi in zip(row, x)) + b) for row, b in zip(self.W1, self.b1)]
        q = [sum(w * hi for w, hi in zip(row, h)) + b for row, b in zip(self.W2, self.b2)]
        return q, h
```

Przepływ w przód: liniowy → ReLU → liniowy. To cała sieć.

### Krok 3: aktualizacja DQN

```python
def train_step(online, target, batch, gamma, lr):
    grads = zeros_like(online)
    for s, a, r, s_next, done in batch:
        q, h = online.forward(s)
        if done:
            y = r
        else:
            q_next, _ = target.forward(s_next)
            y = r + gamma * max(q_next)
        td_error = q[a] - y
        accumulate_grads(grads, online, s, h, a, td_error)
    apply_sgd(online, grads, lr / len(batch))
```

Struktura odpowiada Q-learningowi z lekcji 04, lecz z dwiema różnicami: (a) propagujemy gradient przez różniczkowalną `Q(·; θ)` zamiast indeksować tabelę, (b) cel korzysta z `Q(·; θ^-)`.

### Krok 4: pętla zewnętrzna

W każdym epizodzie działamy ε-zachłannie na `Q(·; θ)`, zapisujemy przejścia do bufora, pobieramy minipartię, wykonujemy krok gradientowy i okresowo synchronizujemy `θ^- ← θ`. Schemat:

```python
for episode in range(N):
    s = env.reset()
    while not done:
        a = epsilon_greedy(online, s, epsilon)
        s_next, r, done = env.step(s, a)
        buffer.push(s, a, r, s_next, done)
        if len(buffer) >= batch:
            train_step(online, target, buffer.sample(batch), gamma, lr)
        if steps % sync_every == 0:
            target = copy(online)
        s = s_next
```

W naszym miniaturowym GridWorld z 16 polami agent uczy się niemal optymalnej polityki w około 500 epizodach. Na Atari należy przeskalować to do 200 milionów klatek i dodać ekstraktor cech oparty na CNN.

## Pułapki

- **Śmiertelna triada.** Połączenie aproksymacji funkcji, uczenia poza polityką i bootstrappingu może prowadzić do rozbieżności. DQN łagodzi ten problem dzięki sieci docelowej i powtórce doświadczeń — nie usuwaj żadnego z tych elementów.
- **Eksploracja.** Wartość ε powinna maleć — zazwyczaj od 1,0 do 0,01 w ciągu pierwszych ~10% treningu. Bez wystarczającej eksploracji na wczesnym etapie sieć Q zbiega się do lokalnego minimum.
- **Nadmierna estymacja.** Operator `max` na zaszumionych wartościach Q jest obciążony w górę. W zastosowaniach produkcyjnych zawsze używaj Double DQN.
- **Skala nagród.** Przycinaj lub normalizuj nagrody — skala gradientu jest proporcjonalna do skali nagrody.
- **Zimny start bufora.** Nie zaczynaj treningu, dopóki bufor nie zgromadzi kilku tysięcy przejść. Wczesne gradienty obliczone na ~20 próbkach prowadzą do przeuczenia.
- **Częstotliwość synchronizacji sieci docelowej.** Zbyt częsta synchronizacja znosi stabilizujące działanie sieci docelowej; zbyt rzadka powoduje, że cele stają się przestarzałe. Atari DQN stosuje interwał 10 000 kroków środowiska. Ogólna zasada: synchronizuj co ~1/100 całkowitego horyzontu treningu.
- **Wstępne przetwarzanie obserwacji.** Atari DQN składa 4 kolejne klatki, tworząc przybliżony stan Markowa. W każdym środowisku, gdzie informacja o prędkości jest istotna, wymagane jest układanie klatek lub jawny stan rekurencyjny.

## Kiedy stosować

W 2026 roku DQN rzadko jest algorytmem z najwyższymi wynikami, lecz pozostaje standardowym punktem odniesienia dla metod uczenia poza polityką:

| Zadanie | Preferowana metoda | Dlaczego nie DQN? |
|------|----------------------|------------|
| Dyskretna przestrzeń akcji w stylu Atari | Rainbow DQN lub MuZero | Ten sam framework, więcej mechanizmów. |
| Ciągłe sterowanie | SAC / TD3 (faza 9 · 07) | DQN nie ma sieci polityki. |
| Uczenie zgodne z polityką / wysoka przepustowość | PPO (faza 9 · 08) | Brak bufora odtwarzania; łatwiej skalować. |
| Offline RL | CQL / IQL / Decision Transformer | Konserwatywne cele Q, bez niestabilności bootstrappingu. |
| Duże dyskretne przestrzenie akcji (systemy rekomendacji) | DQN z osadzaniem akcji lub IMPALA | Reprezentacja akcji ma kluczowe znaczenie. |
| RL dla LLM | PPO / GRPO | Operacje na poziomie sekwencji, nie kroku; inna funkcja straty. |

Idee z DQN przenikają do późniejszych metod. Bufory odtwarzania i sieci docelowe pojawiają się w SAC, TD3, DDPG, SAC-X, buforze samoodtwarzania AlphaZero oraz w każdej metodzie offline RL. Obcinanie nagród przetrwało jako normalizacja przewagi w PPO. Architektura DQN jest planem budowy dla szerszego ekosystemu.

## Wyślij to

Zapisz jako `outputs/skill-dqn-trainer.md`:

```markdown
---
name: dqn-trainer
description: Produce a DQN training config (buffer, target sync, ε schedule, reward clipping) for a discrete-action RL task.
version: 1.0.0
phase: 9
lesson: 5
tags: [rl, dqn, deep-rl]
---

Given a discrete-action environment (observation shape, action count, horizon, reward scale), output:

1. Network. Architecture (MLP / CNN / Transformer), feature dim, depth.
2. Replay buffer. Capacity, minibatch size, warmup size.
3. Target network. Sync strategy (hard every C steps or soft τ).
4. Exploration. ε start / end / schedule length.
5. Loss. Huber vs MSE, gradient clip value, reward clipping rule.
6. Double DQN. On by default unless explicit reason to disable.

Refuse to ship a DQN with no target network, no replay buffer, or ε held at 1. Refuse continuous-action tasks (route to SAC / TD3). Flag any reward range > 10× per-step mean as needing clipping or scale normalization.
```

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Wykreśl krzywą zwrotu na epizod. Po ilu epizodach średnia krocząca przekroczy -10?
2. **Średni.** Wyłącz sieć docelową (użyj sieci online po obu stronach celu Bellmana). Zmierz niestabilność treningu — czy zwroty oscylują, czy całkowicie rozbiegają się?
3. **Trudne.** Zaimplementuj Double DQN: użyj sieci online do wyznaczenia `argmax a'`, a sieci docelowej do oceny wartości. Porównaj odchylenie `Q(s_0, best_a)` od prawdziwego `V*(s_0)` po 1000 epizodów — z Double DQN i bez niego, w zaszumionym GridWorld.

## Kluczowe terminy

| Termin | Co się mówi | Co to rzeczywiście oznacza |
|------|-----------------|----------------------|
| DQN | „Głębokie Q-learning" | Q-learning z neuronową funkcją Q, buforem odtwarzania i siecią docelową. |
| Powtórka doświadczeń | „Przetasowane przejścia" | Bufor cykliczny próbkowany równomiernie na każdym kroku gradientu; dekoreluje dane. |
| Sieć docelowa | „Zamrożony bootstrapping" | Periodyczna kopia sieci Q używana jako cel w równaniu Bellmana; stabilizuje trening. |
| Śmiertelna triada | „Dlaczego RL rozbiega się" | Aproksymacja funkcji + bootstrapping + uczenie poza polityką = brak gwarancji zbieżności. |
| Double DQN | „Korekta błędu zawyżania" | Sieć online wybiera akcję, sieć docelowa ocenia jej wartość. |
| Dueling DQN | „Głowice V i A" | Rozkład Q = V + A - mean(A); ta sama moc predykcyjna, lepszy przepływ gradientu. |
| Rainbow | „Wszystkie techniki razem" | DDQN + PER + Dueling + n-krok + szum + Q dystrybucyjne w jednym modelu. |
| PER | „Priorytetowa powtórka" | Próbkowanie przejść proporcjonalne do wartości błędu TD. |

## Dalsze czytanie

- [Mnih i in. (2013). Playing Atari with Deep Reinforcement Learning](https://arxiv.org/abs/1312.5602) — artykuł warsztatowy NeurIPS 2013, który zapoczątkował głęboki RL.
- [Mnih i in. (2015). Human-level control through deep reinforcement learning](https://www.nature.com/articles/nature14236) — artykuł w Nature, DQN na 49 grach.
- [Hasselt, Guez, Srebro (2016). Deep Reinforcement Learning with Double Q-learning](https://arxiv.org/abs/1509.06461) — DDQN.
- [Wang i in. (2016). Dueling Network Architectures for Deep Reinforcement Learning](https://arxiv.org/abs/1511.06581) — Dueling DQN.
- [Hessel i in. (2018). Rainbow: Combining Improvements in Deep Reinforcement Learning](https://arxiv.org/abs/1710.02298) — artykuł łączący wszystkie techniki.
- [OpenAI Spinning Up — DQN](https://spinningup.openai.com/en/latest/algorithms/dqn.html) — przejrzyste, aktualne omówienie.
- [Sutton i Barto (2018). Ch. 9 — On-policy Prediction with Approximation](http://incompleteideas.net/book/RLbook2020.pdf) — podręcznikowe ujęcie „śmiertelnej triady" (aproksymacja funkcji + bootstrapping + uczenie poza polityką), którą sieć docelowa DQN i bufor odtwarzania mają neutralizować.
- [CleanRL DQN Implementation](https://docs.cleanrl.dev/rl-algorithms/dqn/) — referencyjna, jednoplikowa implementacja DQN stosowana w badaniach ablacyjnych; warto czytać równolegle z wersją od podstaw z tej lekcji.
