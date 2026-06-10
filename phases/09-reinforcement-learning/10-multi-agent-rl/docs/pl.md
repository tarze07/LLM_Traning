# Wieloagentowy RL

> Pojedynczy agent RL zakłada, że środowisko jest stacjonarne. Umieść dwóch agentów uczących się w tym samym świecie, a to założenie zostanie obalone: ​​każdy agent jest częścią środowiska drugiego i oba się zmieniają. Wieloagentowy RL to zestaw sztuczek zapewniających zbieżność uczenia się, gdy założenie Markowa już nie jest aktualne.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 9 · 04 (Q-learning), Faza 9 · 06 (WZMOCNIENIE), Faza 9 · 07 (aktor-krytyk)
**Czas:** ~45 minut

## Problem

Robot uczący się poruszania się po pokoju to problem RL pojedynczego agenta. Drużyna piłkarska nie. Przeciwnicy AlphaStar kontra StarCraft nie są. Rynek agentów licytacyjnych taki nie jest. Dwa samochody pokonujące przystanek w czterech kierunkach nie. Problemy występujące w świecie rzeczywistym nie są takie same.

W każdym środowisku wieloagentowym, z perspektywy jednego agenta, pozostali agenci *są* częścią środowiska. W miarę jak uczą się i zmieniają swoje zachowanie, środowisko staje się niestacjonarne. Właściwość Markowa — „następny stan zależy tylko od bieżącego stanu i mojego działania” — zostaje naruszona, ponieważ następny stan zależy również od tego, co wybrali *inni* agenci, a ich zasady są ruchomymi celami.

To łamie tabelaryczne dowody zbieżności (gwarancja Q-learningu zakłada środowisko stacjonarne). Przełamuje także naiwne głębokie RL: agenci gonią się nawzajem w pętli, nigdy nie dążąc do stabilnej polityki. Potrzebujesz technik specyficznych dla wielu agentów: scentralizowane szkolenie / zdecentralizowane wykonanie, alternatywne scenariusze bazowe, gra ligowa, gra samodzielna.

Zastosowania 2026: roje robotów, kierowanie ruchem, floty pojazdów autonomicznych, symulatory rynku, wieloagentowe systemy LLM (faza 16) i dowolna gra z więcej niż jednym inteligentnym graczem.

## Koncepcja

![Cztery reżimy MARL: niezależny, scentralizowany krytyk, gra własna, liga](../assets/marl.svg)

**Formalizm: gra Markowa.** Uogólnienie MDP: stany `S`, wspólne działanie `a = (a_1, …, a_n)`, przejście `P(s' | s, a)` i nagrody dla poszczególnych agentów `R_i(s, a, s')`. Każdy agent `i` maksymalizuje swój własny zwrot zgodnie z własną polityką `π_i`. Jeśli nagrody są identyczne, oznacza to **w pełni współpracę**. Jeśli ma sumę zerową, jest **kontradyktoryjny**. Jeśli jest mieszana, jest to **suma ogólna**.

**Główne wyzwania:**

- **Niestacjonarność.** `P(s' | s, a_i)` od agenta `i` zależy od `π_{-i}`, który się zmienia.
- **Przypisanie punktów.** W przypadku wspólnej nagrody, który agent ją spowodował?
- **Koordynacja eksploracji.** Agenci muszą eksplorować strategie uzupełniające, a nie powtarzać eksplorację tego samego stanu.
- **Skalowalność.** Wspólna przestrzeń działania rośnie wykładniczo w `n`.
- **Częściowa obserwowalność.** Każdy agent widzi tylko swoją własną obserwację; stan globalny jest ukryty.

**Cztery dominujące reżimy:**

**1. Niezależne Q-learning / niezależne PPO (IQL, IPPO).** Każdy agent uczy się swojej własnej Q lub polityki, traktując innych jako część środowiska. Proste, czasami to działa (szczególnie w przypadku powtórki doświadczenia działającej jako sztuczka polegająca na modelowaniu agenta wygładzającego). Zbieżność teoretyczna: brak. W praktyce: dobrze w przypadku zadań luźno powiązanych, źle w przypadku zadań ściśle powiązanych.

**2. Scentralizowane szkolenie, zdecentralizowane wykonanie (CTDE).** Najpopularniejszy nowoczesny paradygmat. Każdy agent ma swoją własną *politykę* `π_i`, która warunkuje lokalną obserwację `o_i` — standardowe zdecentralizowane wykonanie podczas wdrażania. Podczas *szkolenia* scentralizowany krytyk `Q(s, a_1, …, a_n)` stawia warunki pełnego stanu globalnego i wspólnego działania. Przykłady:
- **MADDPG** (Lowe i in. 2017): DDPG ze scentralizowanym krytykiem dla każdego agenta.
– **COMA** (Foerster et al. 2017): alternatywny scenariusz bazowy — zapytaj „Jaka byłaby moja nagroda, gdybym zamiast tego podjął działanie `a'`?” — wyodrębnia mój wkład.
- **MAPPO** / **IPPO** ze wspólnym krytykiem (Yu i in. 2022): PPO ze scentralizowaną funkcją wartości. Dominujący w 2026 roku dla spółdzielni MARL.
- **QMIX** (Rashid et al. 2018): rozkład wartości — `Q_tot(s, a) = f(Q_1(s, a_1), …, Q_n(s, a_n))` z mieszaniem monotonicznym.

**3. Gra własna.** Dwie kopie tego samego agenta grają ze sobą. Polityka przeciwnika *jest* moją polityką z przeszłości. AlphaGo/AlphaZero/MuZero. OpenAI Pięć. Działa najlepiej w grach o sumie zerowej; sygnał treningowy jest symetryczny.

**4. Gra ligowa.** Rozszerzenie gry własnej na środowiska o sumie ogólnej/kontradyktoryjności: przechowuj populację przeszłych i obecnych polityk, próbuj przeciwnika z ligi, trenuj przeciwko nim. Dodaje exploity (specjalizują się w pokonywaniu aktualnych najlepszych) i główne exploity (specjalizują się w pokonywaniu exploitów). AlphaStar (StarCraft II). Potrzebne, gdy gra dopuszcza cykle strategiczne „kamień-papier-nożyce”.

**Komunikacja.** Zezwalaj agentom na wysyłanie między sobą nauczonych wiadomości `m_i`. Działa w warunkach kooperacyjnych. Foerstera i in. (2016) wykazali, że zróżnicowaną komunikację między agentami można trenować od początku do końca. Dzisiejsze systemy wieloagentowe oparte na LLM (faza 16) komunikują się zasadniczo w języku naturalnym.

## Zbuduj to

W tej lekcji wykorzystano GridWorld 6×6 z dwoma współpracującymi agentami. Zaczynają z przeciwnych rogów i muszą osiągnąć wspólny cel. Wspólna nagroda: `-1` za krok, gdy którykolwiek z agentów wciąż się porusza, `+10`, gdy obaj przybędą. Zobacz `code/main.py`.

### Krok 1: środowisko wieloagentowe

```python
class CoopGridWorld:
    def __init__(self):
        self.size = 6
        self.goal = (5, 5)

    def reset(self):
        return ((0, 0), (5, 0))  # two agents

    def step(self, state, actions):
        a1, a2 = state
        new1 = move(a1, actions[0])
        new2 = move(a2, actions[1])
        done = (new1 == self.goal) and (new2 == self.goal)
        reward = 10.0 if done else -1.0
        return (new1, new2), reward, done
```

*wspólna* przestrzeń akcji to `|A|² = 16`. Państwo globalne to dwie pozycje.

### Krok 2: niezależne Q-learning

Każdy agent uruchamia własną tabelę Q z kluczem na wspólnym stanie. Na każdym kroku: obaj wybierają ε-chciwe działania, zbierają wspólne przejścia, każdy aktualizuje swoje własne Q za pomocą wspólnej nagrody.

```python
def independent_q(env, episodes, alpha, gamma, epsilon):
    Q1, Q2 = defaultdict(default_q), defaultdict(default_q)
    for _ in range(episodes):
        s = env.reset()
        while not done:
            a1 = epsilon_greedy(Q1, s, epsilon)
            a2 = epsilon_greedy(Q2, s, epsilon)
            s_next, r, done = env.step(s, (a1, a2))
            target1 = r + gamma * max(Q1[s_next].values())
            target2 = r + gamma * max(Q2[s_next].values())
            Q1[s][a1] += alpha * (target1 - Q1[s][a1])
            Q2[s][a2] += alpha * (target2 - Q2[s][a2])
            s = s_next
```

Sprawdza się przy tym zadaniu, ponieważ nagrody są gęste i wyrównane. Zawodzi w przypadku ściśle powiązanych zadań (np. gdy jeden agent musi *czekać* na drugiego).

### Krok 3: scentralizowane Q z aktualizacją wartości rozłożonych

Użyj jednego Q w stosunku do wspólnych działań `Q(s, a_1, a_2)`. Aktualizacja udostępnionej nagrody. Decentralizacja podczas wykonywania poprzez marginalizację: `π_i(s) = argmax_{a_i} max_{a_{-i}} Q(s, a_1, a_2)`. Zamienia wykładniczą przestrzeń wspólnego działania na *poprawny* pogląd globalny.

### Krok 4: prosta gra własna (kontra 2-agent)

Ten sam agent, dwie role. Szkolić agenta A przeciwko agentowi B; po `K` odcinkach skopiuj ciężary A do B. Trening symetryczny, stały postęp. Przepis AlphaZero w miniaturze.

## Pułapki

- **Powtórka niestacjonarna.** Powtórka doświadczenia z niezależnymi agentami jest gorsza niż z jednym agentem, ponieważ stare przejścia zostały wygenerowane przez przestarzałych już przeciwników. Poprawka: zmień etykietę lub wagę według aktualności.
- **Niejednoznaczność przypisania punktów.** Wspólna nagroda po długim odcinku; nie ma jasnego sposobu na określenie, który agent przyczynił się do tego. Poprawka: alternatywne wartości bazowe (COMA) lub kształtowanie nagród dla każdego agenta.
- **Dryfowanie/pogoń za polityką.** Najlepsza odpowiedź każdego agenta zmienia się wraz z aktualizacją innego agenta. Poprawka: scentralizowany krytyk, wolne tempo uczenia się lub blokowanie pojedynczo.
- **Hakowanie nagród poprzez koordynację.** Agenci znajdują skoordynowane exploity, których projektant nie przewidywał. Agenci aukcyjni zbliżają się do stawki zerowej. Poprawka: ostrożny projekt nagrody, ograniczenia behawioralne.
- **Nadmiarowość eksploracji.** Obaj agenci eksplorują te same pary stan-akcja. Poprawka: premie entropijne na agenta lub warunkowanie roli.
- **Cykle ligowe.** Czysta gra własna może utknąć w cyklu dominacji. Poprawka: rozgrywka ligowa z różnymi przeciwnikami.
- **Przykładowa eksplozja.** `n` agenci × przestrzeń stanów × wspólne działania. Przybliżenie z przybliżeniem funkcji; rozłożone przestrzenie akcji (jedna głowa wyjściowa polityki na agenta).

## Użyj tego

Mapa zastosowań MARL 2026:

| Domena | Metoda | Notatki |
|--------|--------|-------|
| Kooperacyjna nawigacja / manipulacja | MAPPO / QMIX | CTDE; wspólny krytyk + zdecentralizowani aktorzy. |
| Gry dla dwóch graczy (szachy, Go, poker) | Samodzielna gra z MCTS (AlphaZero) | Suma zerowa; trening symetryczny. |
| Złożony tryb wieloosobowy (Dota, StarCraft) | Rozgrywka ligowa + imitacja treningu wstępnego | OpenAI Five, AlphaStar. |
| Floty pojazdów autonomicznych | CTDE MAPPO / PPO z uwagą | Częściowe obs; zmienna wielkość zespołu. |
| Rynki aukcyjne | Równowaga teorii gier + RL | Pole średnie RL gdy `n` → ∞. |
| Systemy wieloagentowe LLM (faza 16) | Komunikacja w języku naturalnym + warunkowanie roli | Pętla RL w warstwie planowania agentów. |

W 2026 r. największy obszar wzrostu MARL będzie oparty na LLM: roje agentów zajmujących się modelami językowymi negocjujących, debatujących i tworzących oprogramowanie. RL pojawia się jako optymalizacja preferencji na wynikach *na poziomie trajektorii*, a nie na poziomie tokena (faza 16 · 03).

## Wyślij to

Zapisz jako `outputs/skill-marl-architect.md`:

```markdown
---
name: marl-architect
description: Pick the right multi-agent RL regime (IPPO, CTDE, self-play, league) for a given task.
version: 1.0.0
phase: 9
lesson: 10
tags: [rl, multi-agent, marl, self-play]
---

Given a task with `n` agents, output:

1. Regime classification. Cooperative / adversarial / general-sum. Justify.
2. Algorithm. IPPO / MAPPO / QMIX / self-play / league. Reason tied to coupling tightness and reward structure.
3. Information access. Centralized training (what global info goes to the critic)? Decentralized execution?
4. Credit assignment. Counterfactual baseline, value decomposition, or reward shaping.
5. Exploration plan. Per-agent entropy, population-based training, or league.

Refuse independent Q-learning on tightly-coupled cooperative tasks. Refuse to recommend self-play for general-sum with cycle risks. Flag any MARL pipeline without a fixed-opponent eval (cherry-picked self-play numbers are common).
```

## Ćwiczenia

1. **Łatwe.** Trenuj niezależne Q-learning w spółdzielni GridWorld dla 2 agentów. Ile odcinków do średniego powrotu > 0? Wykreśl wspólną krzywą uczenia się.
2. **Średni.** Dodaj zadanie „koordynacji”: cel zostanie osiągnięty tylko wtedy, gdy obaj agenci wejdą na niego w tej samej turze. Czy niezależne Q nadal jest zbieżne? Co się psuje?
3. **Trudne.** Wdrożenie scentralizowanego krytyka dla szkolenia w stylu MAPPO i porównanie szybkości konwergencji z niezależnym PPO w zadaniu koordynacji.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| Gra Markowa | „Wieloagentowy MDP” | `(S, A_1, …, A_n, P, R_1, …, R_n)`; każdy agent ma swoją własną nagrodę. |
| CTDE | „Scentralizowane szkolenie, zdecentralizowana realizacja” | Wspólny krytyk w czasie szkolenia; Polityka każdego agenta wykorzystuje tylko lokalne obs. |
| IPPO | „Niezależny PPO” | Każdy agent uruchamia PPO osobno. Prosta linia bazowa; często niedoceniany. |
| MAPPO | „Wieloagentowy PPO” | PPO ze scentralizowaną funkcją wartości uwarunkowaną stanem globalnym. |
| QMIX | „Monotoniczny rozkład wartości” | `Q_tot = f_monotone(Q_1, …, Q_n)` umożliwia zdecentralizowaną argmax. |
| KOMA | „Kontrfaktyczny multiagent” | Przewaga = moje Q minus oczekiwane Q marginalizujące moje działanie. |
| Samodzielna gra | „Agent kontra ja z przeszłości” | Jeden agent, dwie role; Standard gier o sumie zerowej. |
| Gra ligowa | „Szkolenie ludności” | Buforuj przeszłe zasady, próbuj przeciwników z puli; obsługuje cykle strategiczne. |

## Dalsze czytanie

- [Lowe i in. (2017). Wieloagentowy aktor-krytyk w mieszanych środowiskach kooperatywno-konkurencyjnych (MADDPG)](https://arxiv.org/abs/1706.02275) — CTDE ze scentralizowanym krytykiem.
- [Foerster i in. (2017). Kontrfaktyczne wieloagentowe gradienty polityki (COMA)](https://arxiv.org/abs/1705.08926) — alternatywne podstawy przypisywania punktów.
- [Rashid i in. (2018). QMIX: Faktoryzacja funkcji wartości monotonicznej](https://arxiv.org/abs/1803.11485) — rozkład wartości z monotonicznością.
- [Yu i in. (2022). Zaskakująca skuteczność PPO w kooperacyjnych grach wieloagentowych (MAPPO)](https://arxiv.org/abs/2103.01955) — PPO jest zaskakująco silne dla MARL.
- [Vinyals i in. (2019). Poziom arcymistrzowski w StarCraft II przy użyciu wieloagentowego uczenia się przez wzmacnianie (AlphaStar)](https://www.nature.com/articles/s41586-019-1724-z) — gra ligowa na dużą skalę.
- [Silver i in. (2017). Opanowanie gry Go bez wiedzy człowieka (AlphaGo Zero)](https://www.nature.com/articles/nature24270) — czysta gra własna w grach o sumie zerowej.
- [Sutton i Barto (2018). Ch. 15 — Neuronauka i rozdz. 17 – Frontiers](http://incompleteideas.net/book/RLbook2020.pdf) – zawiera krótkie omówienie w podręczniku ustawień wieloagentowych i problemu niestacjonarności, do rozwiązania którego ma służyć CTDE.
- [Zhang, Yang i Basar (2021). Uczenie się przez wieloagentowe wzmocnienie: selektywny przegląd](https://arxiv.org/abs/1911.10635) — ankieta obejmująca MARL oparty na współpracy, rywalizacji i mieszanym, a wyniki były zbieżne.