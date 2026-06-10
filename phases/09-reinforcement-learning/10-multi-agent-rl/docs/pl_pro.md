# Wieloagentowy RL

> Pojedynczy agent RL zakłada, że środowisko jest stacjonarne. Gdy w tym samym świecie uczą się dwa agenty, założenie to przestaje obowiązywać: każdy z nich stanowi fragment środowiska drugiego, a oba nieustannie ewoluują. Wieloagentowy RL to zbiór technik zapewniających zbieżność uczenia się w sytuacji, gdy właściwość Markowa nie jest już spełniona.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 9 · 04 (Q-learning), Faza 9 · 06 (WZMOCNIENIE), Faza 9 · 07 (aktor-krytyk)
**Czas:** ~45 minut

## Problem

Robot uczący się poruszania po pokoju to klasyczny problem RL z pojedynczym agentem. Drużyna piłkarska już nim nie jest. Podobnie rywalizujące systemy AlphaStar w StarCraft II, rynek agentów przetargowych czy dwa samochody zbliżające się do skrzyżowania z czterech stron. Większość problemów rzeczywistych ma tę samą cechę: wiele działających jednocześnie podmiotów.

W środowiskach wieloagentowych, z perspektywy każdego agenta, pozostałe podmioty *są* częścią jego środowiska. W miarę jak się uczą i modyfikują swoje zachowanie, środowisko staje się niestacjonarne. Właściwość Markowa — „następny stan zależy wyłącznie od bieżącego stanu i mojego działania" — zostaje naruszona, ponieważ następny stan zależy również od decyzji *pozostałych* agentów, których strategie nieustannie się zmieniają.

To podważa tabelaryczne dowody zbieżności (gwarancja Q-learningu zakłada stacjonarne środowisko) i destabilizuje naiwne głębokie RL: agenci gonią się nawzajem w pętli, nie osiągając stabilnej polityki. Potrzebne są techniki właściwe dla systemów wieloagentowych: scentralizowane trenowanie z rozproszoną realizacją, kontrfaktyczne funkcje bazowe, rozgrywka ligowa oraz gra z samym sobą.

Zastosowania w 2026 r.: roje robotów, zarządzanie ruchem, floty pojazdów autonomicznych, symulatory rynku, wieloagentowe systemy LLM (faza 16) oraz wszelkie gry z więcej niż jednym inteligentnym uczestnikiem.

## Koncepcja

![Cztery tryby MARL: niezależny, scentralizowany krytyk, gra z samym sobą, liga](../assets/marl.svg)

**Formalizm: gra Markowa.** Uogólnienie MDP obejmujące: stany `S`, wspólne działanie `a = (a_1, …, a_n)`, przejście `P(s' | s, a)` oraz nagrody poszczególnych agentów `R_i(s, a, s')`. Każdy agent `i` maksymalizuje własny zwrot zgodnie ze swoją polityką `π_i`. Identyczne nagrody oznaczają **pełną współpracę**. Nagrody o sumie zerowej definiują środowisko **antagonistyczne**. Wszystkie inne przypadki to **suma ogólna**.

**Główne wyzwania:**

- **Niestacjonarność.** `P(s' | s, a_i)` z perspektywy agenta `i` zależy od `π_{-i}`, które się zmienia.
- **Przypisanie zasług.** Gdy nagroda jest wspólna, trudno wskazać, który agent się do niej przyczynił.
- **Koordynacja eksploracji.** Agenci powinni odkrywać uzupełniające się strategie, a nie wielokrotnie eksplorować te same stany.
- **Skalowalność.** Wspólna przestrzeń akcji rośnie wykładniczo względem `n`.
- **Częściowa obserwowalność.** Każdy agent dostrzega jedynie własną obserwację; stan globalny pozostaje ukryty.

**Cztery dominujące tryby:**

**1. Niezależne Q-learning / niezależne PPO (IQL, IPPO).** Każdy agent uczy się własnej funkcji Q lub własnej polityki, traktując pozostałych jako element środowiska. Proste podejście, niekiedy skuteczne — szczególnie gdy bufor powtórek pełni rolę mechanizmu wygładzającego zmiany w modelach innych agentów. Teoretyczna gwarancja zbieżności: brak. W praktyce: dobre wyniki przy luźno powiązanych zadaniach, złe przy silnie sprzężonych.

**2. Scentralizowane trenowanie, zdecentralizowana realizacja (CTDE).** Najpopularniejszy współczesny paradygmat. Każdy agent dysponuje własną *polityką* `π_i`, uwarunkowaną lokalną obserwacją `o_i` — standardowa zdecentralizowana realizacja podczas wdrożenia. W trakcie *trenowania* scentralizowany krytyk `Q(s, a_1, …, a_n)` ma dostęp do pełnego stanu globalnego i wspólnych działań. Przykłady:
- **MADDPG** (Lowe i in. 2017): DDPG ze scentralizowanym krytykiem dla każdego agenta.
- **COMA** (Foerster i in. 2017): kontrfaktyczna funkcja bazowa — odpowiada na pytanie „Jaką nagrodę otrzymałbym, gdybym wybrał działanie `a'`?" — pozwala wyodrębnić wkład konkretnego agenta.
- **MAPPO** / **IPPO** ze wspólnym krytykiem (Yu i in. 2022): PPO ze scentralizowaną funkcją wartości. Dominujące podejście w 2026 r. dla kooperacyjnego MARL.
- **QMIX** (Rashid i in. 2018): dekompozycja wartości — `Q_tot(s, a) = f(Q_1(s, a_1), …, Q_n(s, a_n))` z monotonicznym mieszaniem.

**3. Gra z samym sobą (self-play).** Dwie kopie tego samego agenta rywalizują ze sobą. Przeciwnikiem jest wcześniejsza wersja własnej polityki. Podejście stosowane w AlphaGo/AlphaZero/MuZero i OpenAI Five. Sprawdza się najlepiej w grach o sumie zerowej, gdzie sygnał treningowy jest symetryczny.

**4. Rozgrywka ligowa (league play).** Rozszerzenie gry z samym sobą na środowiska o sumie ogólnej lub antagonistyczne: utrzymywana jest populacja bieżących i historycznych polityk, a przeciwnicy losowani są z tej puli. Uzupełniają ją eksploitatorzy (specjalizujący się w pokonywaniu aktualnie najlepszej polityki) oraz meta-eksploitatorzy (pokonujący eksploitatorów). Metoda stosowana w AlphaStar (StarCraft II). Niezbędna, gdy gra dopuszcza cykle strategiczne w stylu „kamień-papier-nożyce".

**Komunikacja.** Agenci mogą wymieniać między sobą nauczone komunikaty `m_i`. Sprawdza się w warunkach kooperacyjnych. Foerster i in. (2016) wykazali, że zróżnicowaną komunikację między agentami można trenować metodą end-to-end. Współczesne wieloagentowe systemy oparte na LLM (faza 16) komunikują się zasadniczo w języku naturalnym.

## Zbuduj to

W tej lekcji wykorzystano GridWorld 6×6 z dwoma współpracującymi agentami. Startują z przeciwnych rogów siatki i muszą dotrzeć do wspólnego celu. Wspólna nagroda: `-1` za każdy krok, dopóki którykolwiek z agentów się porusza, oraz `+10`, gdy obaj dotrą do celu. Zob. `code/main.py`.

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

*Wspólna* przestrzeń akcji ma rozmiar `|A|² = 16`. Stan globalny to para pozycji obu agentów.

### Krok 2: niezależne Q-learning

Każdy agent prowadzi własną tablicę Q indeksowaną wspólnym stanem. Na każdym kroku obaj wybierają akcje metodą ε-zachłanną, rejestrują wspólne przejścia, a następnie każdy aktualizuje swoją tablicę Q na podstawie wspólnej nagrody.

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

Podejście to sprawdza się w tym zadaniu, ponieważ nagrody są gęste i spójne. Zawodzi jednak przy silnie sprzężonych zadaniach — na przykład gdy jeden agent musi *czekać* na drugiego.

### Krok 3: scentralizowane Q z dekompozycją wartości

Stosuje się jedną tablicę Q indeksowaną wspólnymi akcjami: `Q(s, a_1, a_2)`, aktualizowaną na podstawie wspólnej nagrody. Podczas realizacji polityka jest decentralizowana przez marginalizację: `π_i(s) = argmax_{a_i} max_{a_{-i}} Q(s, a_1, a_2)`. Zastępuje wykładniczo rosnącą wspólną przestrzeń akcji spójnym globalnym spojrzeniem.

### Krok 4: prosta gra z samym sobą (wariant 2-agentowy)

Ten sam agent, dwie role. Agent A trenuje przeciwko agentowi B; co `K` epizodów wagi A są kopiowane do B. Symetryczny trening zapewnia stopniowy postęp. To przepis AlphaZero w miniaturze.

## Pułapki

- **Niestacjonarny bufor powtórek.** W przypadku niezależnych agentów bufor powtórek jest mniej wiarygodny niż w scenariuszu jednoagentowym — dawne przejścia zostały wygenerowane przez poprzednie wersje przeciwników. Rozwiązanie: ważenie lub ponowne etykietowanie próbek według aktualności.
- **Niejednoznaczność przypisania zasług.** Wspólna nagroda pojawia się dopiero po długim epizodzie; trudno wskazać, który agent się do niej przyczynił. Rozwiązanie: kontrfaktyczne funkcje bazowe (COMA) lub kształtowanie nagród dla każdego agenta osobno.
- **Dryf polityki.** Optymalna odpowiedź każdego agenta zmienia się, gdy inny agent aktualizuje swoją politykę. Rozwiązanie: scentralizowany krytyk, niskie tempo uczenia lub naprzemienne zamrażanie polityk.
- **Eksploatacja nagród przez koordynację.** Agenci mogą odkryć skoordynowane strategie nieprzewidziane przez projektanta — na przykład agenci aukcyjni zbliżający się do stawek zerowych. Rozwiązanie: staranny projekt funkcji nagrody i ograniczenia behawioralne.
- **Redundantna eksploracja.** Obaj agenci eksplorują te same pary stan-akcja. Rozwiązanie: premie entropijne naliczane per agent lub warunkowanie na podstawie roli.
- **Cykle ligowe.** Czysta gra z samym sobą może utknąć w pętli dominacji. Rozwiązanie: rozgrywka ligowa z zróżnicowaną pulą przeciwników.
- **Eksplozja kombinatoryczna.** `n` agentów × przestrzeń stanów × wspólne akcje. Rozwiązanie: aproksymacja funkcją i rozdzielone przestrzenie akcji (osobna głowa wyjściowa polityki dla każdego agenta).

## Użyj tego

Mapa zastosowań MARL w 2026 r.:

| Domena | Metoda | Notatki |
|--------|--------|-------|
| Kooperacyjna nawigacja / manipulacja | MAPPO / QMIX | CTDE; wspólny krytyk + zdecentralizowani aktorzy. |
| Gry dwuosobowe (szachy, Go, poker) | Gra z samym sobą + MCTS (AlphaZero) | Suma zerowa; symetryczny trening. |
| Złożone gry wieloosobowe (Dota, StarCraft) | Rozgrywka ligowa + imitacyjny pre-training | OpenAI Five, AlphaStar. |
| Floty pojazdów autonomicznych | CTDE MAPPO / PPO z mechanizmem uwagi | Częściowa obserwowalność; zmienna liczebność zespołu. |
| Rynki aukcyjne | Równowaga teorii gier + RL | RL pola średniego dla `n` → ∞. |
| Wieloagentowe systemy LLM (faza 16) | Komunikacja w języku naturalnym + warunkowanie roli | Pętla RL w warstwie planowania agentów. |

W 2026 r. najszybciej rozwijającym się obszarem MARL są systemy oparte na LLM: roje agentów językowych negocjujących, debatujących i wspólnie tworzących oprogramowanie. RL pojawia się tu jako optymalizacja preferencji na poziomie *trajektorii*, a nie pojedynczych tokenów (faza 16 · 03).

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

1. **Łatwe.** Wytrenuj niezależne Q-learning w kooperacyjnym GridWorld dla 2 agentów. Ile epizodów potrzeba, by średni zwrot przekroczył 0? Narysuj wspólną krzywą uczenia się.
2. **Średnie.** Dodaj zadanie wymagające ścisłej koordynacji: cel zostaje osiągnięty tylko wtedy, gdy obaj agenci wejdą na nie w tej samej turze. Czy niezależne Q nadal osiąga zbieżność? Co się psuje?
3. **Trudne.** Zaimplementuj scentralizowanego krytyka do trenowania w stylu MAPPO i porównaj szybkość zbieżności z niezależnym PPO na zadaniu koordynacyjnym.

## Kluczowe terminy

| Termin | Co się mówi | Co to naprawdę oznacza |
|------|-----------------|----------------------|
| Gra Markowa | „Wieloagentowy MDP" | `(S, A_1, …, A_n, P, R_1, …, R_n)`; każdy agent ma własną nagrodę. |
| CTDE | „Scentralizowane trenowanie, zdecentralizowane wykonanie" | Wspólny krytyk podczas trenowania; polityka każdego agenta korzysta wyłącznie z lokalnych obserwacji. |
| IPPO | „Niezależny PPO" | Każdy agent uruchamia PPO oddzielnie. Prosta linia bazowa, często niedoceniana. |
| MAPPO | „Wieloagentowy PPO" | PPO ze scentralizowaną funkcją wartości uwarunkowaną stanem globalnym. |
| QMIX | „Monotoniczna dekompozycja wartości" | `Q_tot = f_monotone(Q_1, …, Q_n)` umożliwia zdecentralizowane argmax. |
| COMA | „Kontrfaktyczny wieloagentowy" | Przewaga = moje Q minus oczekiwane Q po marginalizacji mojego działania. |
| Gra z samym sobą | „Agent kontra własna przeszłość" | Jeden agent, dwie role; standard w grach o sumie zerowej. |
| Rozgrywka ligowa | „Trening populacyjny" | Buforowanie historycznych polityk i losowanie przeciwników z puli; obsługuje cykle strategiczne. |

## Dalsze czytanie

- [Lowe i in. (2017). Wieloagentowy aktor-krytyk w mieszanych środowiskach kooperatywno-konkurencyjnych (MADDPG)](https://arxiv.org/abs/1706.02275) — CTDE ze scentralizowanym krytykiem.
- [Foerster i in. (2017). Kontrfaktyczne wieloagentowe gradienty polityki (COMA)](https://arxiv.org/abs/1705.08926) — kontrfaktyczne funkcje bazowe do przypisania zasług.
- [Rashid i in. (2018). QMIX: faktoryzacja funkcji wartości z monotonicznym mieszaniem](https://arxiv.org/abs/1803.11485) — dekompozycja wartości z ograniczeniem monotoniczności.
- [Yu i in. (2022). Zaskakująca skuteczność PPO w kooperacyjnych grach wieloagentowych (MAPPO)](https://arxiv.org/abs/2103.01955) — PPO jako zaskakująco silna metoda dla MARL.
- [Vinyals i in. (2019). Poziom arcymistrzowski w StarCraft II przy użyciu wieloagentowego uczenia przez wzmacnianie (AlphaStar)](https://www.nature.com/articles/s41586-019-1724-z) — rozgrywka ligowa na dużą skalę.
- [Silver i in. (2017). Opanowanie Go bez wiedzy ludzkiej (AlphaGo Zero)](https://www.nature.com/articles/nature24270) — czysta gra z samym sobą w grach o sumie zerowej.
- [Sutton i Barto (2018). Rozdz. 15 — Neuronauka i rozdz. 17 — Frontiers](http://incompleteideas.net/book/RLbook2020.pdf) — skrótowe omówienie środowisk wieloagentowych i problemu niestacjonarności, któremu CTDE ma zaradzić.
- [Zhang, Yang i Basar (2021). Uczenie przez wieloagentowe wzmacnianie: przegląd selektywny](https://arxiv.org/abs/1911.10635) — przegląd obejmujący kooperacyjny, antagonistyczny i mieszany MARL wraz z wynikami dotyczącymi zbieżności.
