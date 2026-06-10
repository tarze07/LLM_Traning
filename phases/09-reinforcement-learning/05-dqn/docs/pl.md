# Głębokie sieci Q (DQN)

> 2013: Mnih przeszkolił jedną sieć Q-learningową na surowych pikselach, pokonał każdego klasycznego agenta RL w siedmiu grach Atari. 2015: rozszerzenie do 49 gier, opublikowane w Nature, zapoczątkowało erę głębokiego RL. DQN to Q-learning plus trzy sztuczki, które sprawiają, że aproksymacja funkcji jest stabilna.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 3 · 03 (propagacja wsteczna), Faza 9 · 04 (Q-learning, SARSA)
**Czas:** ~75 minut

## Problem

Tabelaryczne Q-learning wymaga oddzielnej wartości Q dla każdej pary (stan, akcja). Szachownica ma ~10⁴³ stanów. Ramka Atari ma wymiary 210×160×3 = 100 800 funkcji. Tabelaryczny RL umiera w tysiącach stanów, nie mówiąc już o miliardach.

Poprawka jest oczywista z perspektywy czasu: zastąp tabelę Q siecią neuronową, `Q(s, a; θ)`. Jednak patrząc z perspektywy czasu, zajęło to dziesięciolecia. Naiwne przybliżenie funkcji za pomocą Q-learningu rozbiega się w ramach „zabójczej triady” — przybliżenie funkcji + ładowanie + uczenie się poza polityką. Mnih i in. (2013, 2015) zidentyfikowali trzy sztuczki inżynieryjne stabilizujące proces uczenia się:

1. **Powtórka doświadczenia** dekoreluje przejścia.
2. **Sieć docelowa** blokuje cel ładowania początkowego.
3. **Przycinanie nagrody** normalizuje wielkość gradientu.

DQN na Atari było pierwszym przypadkiem, w którym pojedyncza architektura z jednym zestawem hiperparametrów rozwiązała dziesiątki problemów ze sterowaniem na podstawie surowych pikseli. Wszystko, co zbudowano od tego czasu w stylu „deep-RL” – DDQN, Rainbow, Dueling, Distributional, R2D2, Agent57 – jest ułożone na tej bazie trzech trików.

## Koncepcja

![Pętla treningowa DQN: env, bufor powtórek, sieć online, sieć docelowa, utrata niszczyciela czołgów Bellman](../assets/dqn.svg)

**Cel.** DQN minimalizuje jednostopniową utratę TD w neuronowej funkcji Q:

`L(θ) = E_{(s,a,r,s')~D} [ (r + γ max_{a'} Q(s', a'; θ^-) - Q(s, a; θ))² ]`

`θ` = sieć online, aktualizowana co krok poprzez opadanie gradientu. `θ^-` = sieć docelowa, okresowo kopiowana z `θ` (co ~10 000 kroków). `D` = bufor odtwarzania poprzednich przejść.

**Trzy triki, według ważności:**

**Powtórka doświadczenia.** Bufor pierścieniowy zawierający przejścia `~10⁶`. Na każdym etapie szkolenia losowo i równomiernie pobierana jest minipartia. Przerywa to korelację czasową (kolejne klatki są prawie identyczne), pozwala sieci wielokrotnie uczyć się na rzadkich, satysfakcjonujących przejściach i dekoreluje kolejne aktualizacje gradientów. Bez tego TD zgodny z polityką z siecią neuronową różni się na Atari.

**Sieć docelowa.** Korzystanie z tej samej sieci `Q(·; θ)` po obu stronach równania Bellmana powoduje, że cel porusza się przy każdej aktualizacji — „goniąc własny ogon”. Rozwiązanie: zachowaj drugą sieć `Q(·; θ^-)` z zamrożonymi ciężarkami. Co `C` kroki kopiuj `θ → θ^-`. Stabilizuje to cel regresji przez tysiące kroków gradientu na raz. Miękkie aktualizacje `θ^- ← τ θ + (1-τ) θ^-` (używane w DDPG, SAC) są płynniejszą wersją.

**Przycinanie nagród.** Wielkość nagród Atari waha się od 1 do 1000+. Przycięcie do `{-1, 0, +1}` uniemożliwia jakiejkolwiek pojedynczej grze zdominowanie gradientu. Źle, gdy liczy się wielkość nagrody; w porządku dla Atari, gdzie liczy się tylko znak.

**Podwójne DQN.** Hasselt (2016) naprawia błąd maksymalizacji: użyj sieci online, aby *wybrać* działanie, a sieci docelowej, aby *ocenić* ją.

`target = r + γ Q(s', argmax_{a'} Q(s', a'; θ); θ^-)`

Wymiana typu drop-in, stale lepsza. Używaj go domyślnie.

**Inne ulepszenia (Rainbow, 2017):** powtarzanie z priorytetem (więcej próbek przejść o wysokim poziomie TD), architektura pojedynków (oddzielne `V(s)` i przewagi), sieci z szumami (eksploracja wyuczona), zwroty n-etapowe, Q dystrybucyjne (C51/QR-DQN), wieloetapowe ładowanie. Każdy dodaje kilka procent; zyski są w przybliżeniu addytywne.

## Zbuduj to

Kod tutaj jest wolny od numpy tylko przy stdlib — używamy ręcznie tworzonego jednowarstwowego MLP z ukrytą warstwą w maleńkim, ciągłym GridWorld, więc każdy krok uczenia trwa w mikrosekundach. Algorytm jest identyczny z Atari DQN w skali.

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

Pojemność ~50 000 dla Atari; 5000 wystarczy na nasze środowisko zabawek.

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

Przejście w przód: liniowe → ReLU → liniowe. To jest cała sieć.

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

Kształt to Q-learning z lekcji 04 z dwiema różnicami: (a) wspieramy poprzez różniczkowalną `Q(·; θ)` zamiast indeksować tabelę, (b) cel używa `Q(·; θ^-)`.

### Krok 4: pętla zewnętrzna

W przypadku każdego odcinka działaj ε-chciwie na `Q(·; θ)`, wypychaj przejścia do bufora, próbkuj minibatch, wykonaj krok gradientowy, okresowo synchronizuj `θ^- ← θ`. Wzór:

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

W naszym maleńkim GridWorld, w którym panuje 16 przyciemnień i jest gorąco, agent uczy się niemal optymalnej polityki w około 500 odcinkach. Na Atari przeskaluj to do 200 milionów klatek i dodaj ekstraktor funkcji CNN.

## Pułapki

- **Zabójcza triada.** Przybliżenie funkcji + niezgodność z zasadami + ładowanie początkowe mogą się różnić. DQN łagodzi za pomocą siatki docelowej + powtórka; też nie usuwaj.
- **Eksploracja.** ε musi spadać, zazwyczaj od 1,0 do 0,01 w ciągu pierwszych ~10% treningu. Bez odpowiednio wczesnej eksploracji sieć Q zbiega się do lokalnego basenu.
- **Przeszacowanie.** `max` w przypadku zaszumionego Q jest przesunięte w górę. Zawsze używaj Double DQN w produkcji.
- **Skala nagród.** Przycinaj lub normalizuj nagrody; wielkość gradientu jest proporcjonalna do wielkości nagrody.
- **Zimny ​​start bufora powtórzeń.** Nie trenuj, dopóki bufor nie będzie zawierał kilku tysięcy przejść. Wczesne gradienty na ~20 próbkach są nadmiernie dopasowane.
- **Częstotliwość synchronizacji celu.** Zbyt często ≈ brak siatki celu; zbyt rzadkie ≈ nieaktualne cele. Atari DQN wykorzystuje 10 000 kroków env. Ogólna zasada: synchronizuj co ~1/100 horyzontu treningowego.
- **Wstępne przetwarzanie obserwacji.** Atari DQN układa 4 klatki, aby utworzyć stan Markowa. Każde środowisko env z informacją o prędkości wymaga układania ramek lub stanu cyklicznego.

## Użyj tego

W 2026 r. DQN rzadko jest najnowocześniejszym algorytmem, ale pozostaje algorytmem referencyjnym niezgodnym z polityką:

| Zadanie | Metoda wyboru | Dlaczego nie DQN? |
|------|----------------------|------------|
| Dyskretna akcja w stylu Atari | Tęczowy DQN lub Musli | Ten sam framework, więcej sztuczek. |
| Ciągła kontrola | SAC / TD3 (faza 9 · 07) | DQN nie ma sieci polis. |
| Zgodnie z zasadami / wysoka przepustowość | PPO (faza 9 · 08) | Brak bufora odtwarzania; łatwiej skalować. |
| Nieaktywny RL | CQL / IQL / Transformator decyzyjny | Konserwatywne cele Q, bez wybuchów typu bootstrap. |
| Duże, dyskretne przestrzenie akcji (rekomendujący) | DQN z osadzaniem akcji, czyli IMPALA | Cienki; dekoracja ma znaczenie. |
| LLM RL | PPO / GRPO | Poziom sekwencji, a nie krok; inna strata. |

Lekcje wciąż podróżują. Sieci powtórkowe i docelowe pojawiają się w SAC, TD3, DDPG, SAC-X, buforze samoodtwarzania AlphaZero i każdej metodzie RL offline. Obcinanie nagród jest nadal kontynuowane jako normalizacja przewagi w PPO. Architektura jest planem.

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

1. **Łatwe.** Uruchom `code/main.py`. Wykreśl krzywą zwrotu na odcinek. Po ilu odcinkach średnia krocząca przekroczy -10?
2. **Średni.** Wyłącz sieć docelową (użyj sieci online po obu stronach celu Bellman). Zmierz niestabilność treningu – czy zwroty oscylują czy różnią się?
3. **Trudne.** Dodaj Double DQN: użyj sieci online, aby wybrać `argmax a'`, sieć docelową do oceny. Porównaj odchylenie `Q(s_0, best_a)` z prawdziwym `V*(s_0)` po 1000 odcinków z i bez podwójnego DQN w hałaśliwym świecie GridWorld.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| DQN | „Głębokie Q-learning” | Q-learning z neuronową funkcją Q, buforem odtwarzania i siecią docelową. |
| Powtórka doświadczenia | „Przetasowane przejścia” | Bufor pierścieniowy próbkowany równomiernie w każdym etapie gradientu; dekoreluje dane. |
| Sieć docelowa | „Zamrożony bootstrap” | Okresowa kopia Q używana w tarczy Bellmana; stabilizuje trening. |
| Zabójcza triada | „Dlaczego RL się różni” | Przybliżenie funkcji + ładowanie + odchylenie od polityki = brak gwarancji zbieżności. |
| Podwójne DQN | „Poprawka błędu maksymalizacji” | Sieć internetowa wybiera akcję, sieć docelowa ją ocenia. |
| Pojedynek DQN | „Główki V i A” | Rozłóż Q = V + A - średnia(A); ta sama moc wyjściowa, lepszy przepływ gradientowy. |
| Tęcza | „Wszystkie sztuczki” | DDQN + PER + pojedynkowanie + n-krok + szum + dystrybucja w jednym. |
| ZA | „Priorytetowa powtórka” | Przykładowe przejścia proporcjonalne do wielkości błędu TD. |

## Dalsze czytanie

- [Mnih i in. (2013). Gra na Atari z funkcją Deep Reinforcement Learning](https://arxiv.org/abs/1312.5602) — artykuł warsztatowy NeurIPS z 2013 r., który zapoczątkował głębokie RL.
- [Mnih i in. (2015). Kontrola na poziomie ludzkim poprzez uczenie się przez głębokie wzmacnianie](https://www.nature.com/articles/nature14236) — artykuł w Nature, DQN z 49 grami.
- [Hasselt, Guez, Srebro (2016). Uczenie się przez głębokie wzmacnianie z podwójnym Q-learningiem](https://arxiv.org/abs/1509.06461) — DDQN.
- [Wang i in. (2016). Pojedynki na architektury sieciowe](https://arxiv.org/abs/1511.06581) — pojedynki DQN.
- [Hessel i in. (2018). Rainbow: Łączenie ulepszeń w głębokim RL](https://arxiv.org/abs/1710.02298) – artykuł na temat trików stosowych.
- [OpenAI Spinning Up — DQN](https://spinningup.openai.com/en/latest/algorithms/dqn.html) — przejrzysta, nowoczesna ekspozycja.
- [Sutton i Barto (2018). Ch. 9 — Przewidywanie na podstawie polityki z przybliżeniem] (http://incompleteideas.net/book/RLbook2020.pdf) — podręcznikowe podejście do „zabójczej triady” (przybliżenie funkcji + ładowanie + wyłączenie polityki), którą sieć docelowa DQN i bufor odtwarzania mają oswoić.
- [Implementacja CleanRL DQN](https://docs.cleanrl.dev/rl-algorithms/dqn/) — referencyjny jednoplikowy DQN stosowany w badaniach ablacyjnych; warto przeczytać razem z od podstaw wersją tej lekcji.