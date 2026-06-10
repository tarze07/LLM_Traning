# Uczenie przez wzmacnianie (RL) w grach – AlphaZero, MuZero oraz era wnioskowania w LLM

> 1992: TD-Gammon pokonuje ludzkich mistrzów w tryktraka (backgammon) przy użyciu klasycznej metody różnic temporalnych (TD). 2016: AlphaGo pokonuje Lee Sedola. 2017: AlphaZero bez żadnej wiedzy początkowej (from scratch) dominuje w szachach, shogi i Go. 2024: DeepSeek-R1 testuje tę samą formułę, zastępując algorytm PPO przez GRPO w celu rozwinięcia zdolności rozumowania. Gry stanowią kluczowy benchmark napędzający kolejne przełomy w tej dziedzinie.

**Typ:** Opracowanie  
**Języki:** Python  
**Wymagania wstępne:** Faza 9 · 05 (DQN), Faza 9 · 08 (PPO), Faza 9 · 09 (RLHF), Faza 9 · 10 (MARL)  
**Szacowany czas:** ~120 minut  

## Problem

Gry oferują wszystko, czego wymaga uczenie przez wzmacnianie (RL): jednoznaczny sygnał nagrody (wygrana/przegrana), nieskończoną liczbę epizodów dzięki możliwości rozgrywania partii z samym sobą (self-play), doskonałe środowisko symulacyjne (gra *jest* symulatorem) oraz dyskretne lub niewielkie ciągłe przestrzenie akcji. Co więcej, struktura wieloagentowa naturalnie wymusza odporność na strategie adwersarialne.

To właśnie na grach testowano każdy kluczowy przełom w dziedzinie RL: TD-Gammon (backgammon, 1992), Atari-DQN (2013), AlphaGo (2016), AlphaZero (2017), OpenAI Five (Dota 2, 2019), AlphaStar (StarCraft II, 2019), MuZero (z wyuczonym modelem świata, 2019), AlphaTensor (mnożenie macierzy, 2022), AlphaDev (algorytmy sortowania, 2023) oraz DeepSeek-R1 (rozumowanie matematyczne, 2025) – najnowszy dowód na to, że techniki RL stosowane w grach sprawdzają się również w przetwarzaniu tekstu.

W tym podsumowaniu przyjrzymy się trzem przełomowym architekturom — AlphaZero, MuZero i GRPO — z jednego, ujednoliconego punktu widzenia: **gra z samym sobą + wyszukiwanie + optymalizacja strategii (policy improvement)**. Każda z nich uogólnia poprzednią. W szczególności GRPO reprezentuje podejście AlphaZero zaadaptowane do wnioskowania w modelach LLM, gdzie tokeny pełnią rolę akcji, a automatyczna weryfikacja poprawności stanowi sygnał wygranej.

## Koncepcja

![AlphaZero ↔ MuZero ↔ GRPO: ta sama pętla, różne środowiska](../assets/rl-games.svg)

**Ujednolicona pętla treningowa.**

```
while True:
    trajectory = self_play(current_policy, search)     # rozgrywka z samym sobą
    policy_target = search.improved_policy(trajectory) # wyszukiwanie ulepsza podstawową politykę
    policy_net.update(policy_target, value_target)     # uczenie nadzorowane na wynikach wyszukiwania
```

**AlphaZero (2017).** Silver i in. Dla gier o znanych regułach (szachy, shogi, Go):

- **Wspólna sieć polityki i wartości (policy-value network):** pojedynczy szkielet (backbone) `f_θ(s) → (p, v)`. Wektor `p` reprezentuje rozkład prawdopodobieństwa nad dozwolonymi ruchami, a `v` to przewidywany wynik rozgrywki.
- **Przeszukiwanie drzew (Monte Carlo Tree Search - MCTS):** przy każdym ruchu rozwijane jest drzewo możliwych scenariuszy. Wartości `(p, v)` służą jako rozkład a priori (prior) i wartość początkowa (bootstrap). Wybór węzłów następuje według reguły UCB (a dokładniej PUCT): `a* = argmax Q(s, a) + c · p(a|s) · √N(s) / (1 + N(s, a))`.
- **Gra z samym sobą (self-play):** agent rozgrywa partie przeciwko sobie. Dla każdego kroku `t` rozkład odwiedzin stanów w MCTS `π_t` staje się celem (target) podczas trenowania polityki.
- **Funkcja straty:** `L = (v - z)² - π · log p + c · ||θ||²`, gdzie `z` oznacza ostateczny wynik gry (+1 / 0 / -1).

Brak wiedzy eksperckiej. Brak ręcznie projektowanych heurystyk. Uniwersalna metoda, która pozwoliła opanować szachy, shogi i Go po rozegraniu kilkudziesięciu milionów partii treningowych self-play.

**MuZero (2019).** Schrittwieser i in. Eliminuje konieczność znajomości reguł gry.

- Zamiast zakładać znane środowisko, model uczy się *ukrytego modelu dynamiki* (latent dynamics model) składającego się z trzech funkcji `(h, g, f)`:
  - `h(s)`: koduje wejściową obserwację do stanu ukrytego (latent state).
  - `g(s_latent, a)`: przewiduje kolejny stan ukryty oraz natychmiastową nagrodę.
  - `f(s_latent)`: przewiduje rozkład a priori polityki oraz wartość stanu.
- MCTS działa bezpośrednio w *wyuczonej przestrzeni ukrytej*. Schemat wyszukiwania oraz pętla treningowa pozostają bez zmian.
- Metoda działa w Go, szachach, shogi oraz grach Atari – jeden algorytm, bez wcześniejszej znajomości reguł środowiska.

**Stochastic MuZero (2022).** Wprowadza stochastyczną dynamikę i węzły losowe (chance nodes), co pozwala na obsługę gier takich jak tryktrak (backgammon).

**Muesli, Gumbel MuZero (2022-2024).** Ulepszenia w zakresie efektywności próbkowania (sample efficiency) oraz deterministycznego wyszukiwania.

**GRPO (Group Relative Policy Optimization, 2024-2025).** Metoda spopularyzowana przez DeepSeek-R1. Ta sama pętla wzorowana na AlphaZero, zaadaptowana do rozwijania zdolności rozumowania w modelach językowych:

- **„Gra”:** rozwiązanie zadania matematycznego, programistycznego lub logicznego. **„Wygrana”:** weryfikator (np. zaliczone testy jednostkowe, zgodność wyniku numerycznego) zwraca wartość 1.
- **Polityka:** LLM. **Akcje:** tokeny. **Stan:** prompt + dotychczas wygenerowana odpowiedź.
- **Brak sieci krytyka** (brak $V_\phi$ znanego z PPO). Zamiast tego dla każdego promptu generowana jest grupa $G$ niezależnych odpowiedzi (completions). Obliczana jest nagroda dla każdej z nich, a następnie wyznacza się **względną przewagę grupową** $A_i = (r_i - \text{mean}(r)) / \text{std}(r)$, która służy jako sygnał do aktualizacji w stylu algorytmu REINFORCE.
- **Kara dywergencji KL** względem polityki referencyjnej (reference policy), zapobiegająca nadmiernemu dryfowi parametrów (analogicznie do klasycznego RLHF).
- **Całkowita funkcja straty:**

  `L_GRPO(θ) = -E_{q, {o_i}} [ (1/G) Σ_i A_i · log π_θ(o_i | q) ] + β · KL(π_θ || π_ref)`

Brak osobnego modelu nagrody (reward model), brak sieci krytyka i brak przeszukiwania MCTS. Względna linia bazowa grupy (group baseline) zastępuje te elementy, co pozwala osiągnąć wyniki porównywalne lub lepsze od PPO-RLHF w zadaniach wnioskowania, wymagając znacznie mniejszego budżetu obliczeniowego.

**Pełna formuła R1.** Publikacja DeepSeek-R1 opisuje w istocie dwa modele:

- **R1-Zero.** Punktem wyjścia jest model bazowy DeepSeek-V3. Brak etapu uczenia nadzorowanego (SFT). Bezpośrednie zastosowanie GRPO z dwoma komponentami nagrody: *nagrodą za poprawność* (opartą na regułach – np. czy ostateczna odpowiedź zawiera prawidłową liczbę, czy kod przechodzi testy jednostkowe) oraz *nagrodą za formatowanie* (czy wygenerowany tekst zawiera poprawnie wydzielony łańcuch myśli w znacznikach `<think>…</think>`). Po przeprowadzeniu tysięcy kroków optymalizacji, średnia długość generowanej odpowiedzi rośnie z ok. 100 do ok. 10 000 tokenów, a wyniki w testach matematycznych osiągają poziom zbliżony do o1-preview. Model uczy się samodzielnego wnioskowania od podstaw. Wadą tego podejścia jest to, że łańcuchy myśli (CoT) bywają nieczytelne, zawierają mieszankę językową (code-switching) i brakuje im dopracowania stylistycznego.
- **R1.** Rozwiązuje problemy z czytelnością R1-Zero za pomocą czteroetapowego potoku (pipeline):
  1. **SFT na etapie zimnego startu (Cold-start SFT):** zebranie kilku tysięcy przykładów (demonstrations) zawierających długie łańcuchy myśli (CoT) o przejrzystym formatowaniu. Przeprowadzenie na nich uczenia nadzorowanego (SFT) na modelu bazowym daje stabilny i czytelny punkt wyjściowy.
  2. **Trening GRPO ukierunkowany na rozumowanie:** zastosowanie GRPO z nagrodami za poprawność i formatowanie oraz dodatkową nagrodą za *spójność językową* (aby zapobiec mieszaniu języków).
  3. **Próbkowanie z odrzucaniem (Rejection sampling) + druga runda SFT:** wygenerowanie ok. 600 tys. trajektorii wnioskowania z modelu po etapie RL, zachowanie wyłącznie tych z poprawnym wynikiem i czytelnym CoT, a następnie połączenie ich z ok. 200 tys. ogólnych przykładów SFT (kreatywne pisanie, Q&A itp.). Na tak przygotowanym zbiorze ponownie dotraja się model bazowy.
  4. **GRPO o pełnym spektrum (All-round GRPO):** końcowa runda uczenia przez wzmacnianie (RL) obejmująca zarówno zadania logiczne (nagrody oparte na regułach), jak i ogólne wyrównanie (alignment) do ludzkich preferencji (przydatność, bezpieczeństwo i nieszkodliwość).

Wynikowy model dorównuje o1 w benchmarkach AIME i MATH-500, a jego wagi zostały udostępnione jako open-source. Ponadto autorzy przeprowadzili destylację wiedzy do mniejszych modeli (od Qwen-1.5B do Llama-70B) za pomocą SFT na śladach wnioskowania wygenerowanych przez R1 (bez stosowania RL na mniejszych modelach). Destylacja z silnego nauczyciela szkolonego za pomocą RL konsekwentnie przynosi lepsze efekty niż trenowanie mniejszego modelu metodą RL od zera.

**Dlaczego warto wybrać GRPO zamiast PPO w zadaniach rozumowania?** Trzy główne powody przedstawione w pracy DeepSeekMath (luty 2024): (1) brak konieczności trenowania sieci wartości (krytyka), co zmniejsza zużycie pamięci GPU niemal o połowę; (2) względna linia bazowa grupy naturalnie radzi sobie z rzadkimi nagrodami (sparse rewards) na końcu trajektorii; (3) normalizacja przewag wewnątrz grupy na bieżąco ujednolica skalę sygnału dla zadań o różnym stopniu trudności, co jest trudne do osiągnięcia dla pojedynczego krytyka w PPO.

**Metody bezprzeszukiwaniowe vs oparte na przeszukiwaniu (search-based):**
- **Gry o pełnej informacji z długim horyzontem czasowym** (np. Go, szachy): wciąż opierają się na przeszukiwaniu drzew (tutaj dominują AlphaZero/MuZero).
- **Wnioskowanie w LLM:** w rozwiązaniach produkcyjnych rzadko stosuje się pełny MCTS; dominuje GRPO w połączeniu z technikami takimi jak Best-of-N do generowania odpowiedzi. Modele oceny krokowej (Process Reward Models - PRM) wskazują jednak na kierunek powrotu do wyszukiwania na poziomie poszczególnych kroków rozumowania.

## Implementacja

Kod w pliku `code/main.py` implementuje uproszczoną wersję GRPO w postaci wieloramiennego bandyty z próbkowaniem grupowym. Matematyczny rdzeń algorytmu jest identyczny z wersją dla LLM, uproszczono jedynie politykę i środowisko. Umożliwia to łatwe prześledzenie obliczania straty (loss) oraz względnej przewagi grupowej (group relative advantage).

### Krok 1: Uproszczone środowisko weryfikatora

```python
QUESTIONS = [
    {"prompt": "q1", "correct": 3},
    {"prompt": "q2", "correct": 1},
]

def verify(prompt_idx, answer_token):
    return 1.0 if answer_token == QUESTIONS[prompt_idx]["correct"] else 0.0
```

W pełnoskalowym GRPO weryfikator (verifier) automatycznie uruchamia testy jednostkowe lub sprawdza poprawność matematyczną odpowiedzi.

### Krok 2: Polityka: rozkład softmax nad K tokenami odpowiedzi dla danego promptu

```python
def policy_probs(theta, p_idx):
    return softmax(theta[p_idx])
```

Jest to bezpośredni odpowiednik logitsów z ostatniej warstwy LLM warunkowanych wejściowym promptem.

### Krok 3: Próbkowanie grupowe i względna przewaga

```python
def grpo_step(theta, p_idx, G=8, beta=0.01, lr=0.1, rng=None):
    probs = policy_probs(theta, p_idx)
    samples = [sample(probs, rng) for _ in range(G)]
    rewards = [verify(p_idx, s) for s in samples]
    mean_r = sum(rewards) / G
    std_r = stddev(rewards) + 1e-8
    advs = [(r - mean_r) / std_r for r in rewards]

    for a, A in zip(samples, advs):
        grad = onehot(a) - probs
        for i in range(len(probs)):
            theta[p_idx][i] += lr * A * grad[i]
    # KL penalty: pull theta toward reference
    for i in range(len(probs)):
        theta[p_idx][i] -= beta * (theta[p_idx][i] - reference[p_idx][i])
```

Względna przewaga grupowa (group relative advantage) to kluczowy element metody DeepSeek. Eliminuje ona potrzebę stosowania sieci krytyka. Wartością bazową (baseline) staje się średnia nagroda w grupie, a rolę normalizacji pełni odchylenie standardowe nagród w grupie.

### Krok 4: Porównanie z klasycznym REINFORCE z linią bazową

Przy tej samej konfiguracji i budżecie obliczeniowym GRPO wykazuje szybszą zbieżność i większą stabilność w porównaniu do standardowego algorytmu REINFORCE.

### Krok 5: Monitorowanie entropii oraz dywergencji KL

Stosuje się te same metryki diagnostyczne co w klasycznym RLHF: średnia dywergencja KL względem modelu referencyjnego, entropia polityki oraz średnia nagroda w czasie. Stabilizacja tych wartości sygnalizuje zakończenie procesu treningowego.

## Pułapki

- **Hakowanie nagrody (reward hacking):** GRPO dziedziczy podatności klasycznego RLHF. Jeśli weryfikator ma luki lub błędy, LLM szybko znajdzie sposób na ich eksploatację (exploit). Niezbędne jest projektowanie odpornych weryfikatorów (np. pokrycie wieloma przypadkami testowymi, formalna weryfikacja).
- **Zbyt mały rozmiar grupy:** szum szacowania względnej przewagi skaluje się jako $1/\sqrt{G}$. Dla grup mniejszych niż $G = 4$ sygnał staje się zbyt zaszumiony. W praktyce stosuje się zazwyczaj rozmiary grup od $G = 8$ do $64$.
- **Błąd faworyzowania długości (length bias):** wygenerowane teksty o różnej liczbie tokenów mają drastycznie różne wartości logarytmu prawdopodobieństwa. Należy normalizować te wartości przez długość sekwencji lub stosować ograniczenia maksymalnej liczby generowanych tokenów.
- **Pętle w grze z samym sobą (self-play cycles):** uczenie w stylu AlphaZero może utknąć w cyklach wzajemnej dominacji (non-transitive dynamics). Zapobiega się temu poprzez utrzymywanie zróżnicowanej puli przeciwników (trening ligowy - League Training).
- **Niezgodność pojemności sieci z wyszukiwaniem (policy-search capacity mismatch):** AlphaZero trenuje sieć polityki tak, aby dopasować ją do rozkładu wizyt z MCTS. Jeśli pojemność sieci (capacity) jest zbyt mała w stosunku do złożoności wyszukiwania, proces uczenia utknie w martwym punkcie.
- **Wysoki próg obliczeniowy (compute floor):** MuZero i AlphaZero wymagają ogromnych zasobów. Pojedynczy eksperyment (ablation study) potrafi zająć setki godzin GPU. Do celów edukacyjnych warto korzystać z mniejszych środowisk (np. Connect Four / Czwórki).
- **Niewystarczające pokrycie weryfikatora:** sytuacja, w której błędny kod zalicza testy jednostkowe, utrwala nieprawidłowe zachowania modelu. Należy projektować testy uwzględniające przypadki brzegowe (edge cases).

## Użyj tego

Krajobraz metod RL w grach według dziedzin:

| Dziedzina | Dominująca metoda |
|------------|--------------------------------|
| Dwuosobowe gry planszowe o sumie zerowej (Go, szachy, shogi) | AlphaZero / MuZero / KataGo |
| Gry karciane z niepełną informacją (poker) | CFR + głębokie uczenie (DeepStack, Libratus, Pluribus) |
| Atari / gry z grafiką pikselową | Muesli / MuZero / IMPALA-PPO |
| Wieloosobowe gry strategiczne (Dota 2, StarCraft II) | PPO + self-play + liga (OpenAI Five, AlphaStar) |
| Wnioskowanie matematyczne/kodowe LLM | GRPO (DeepSeek-R1, Qwen-RL, otwarte replikacje) |
| Wyrównanie LLM (Alignment) | DPO / PPO-RLHF (nie GRPO, z uwagi na brak łatwo weryfikowalnego sygnału) |
| Robotyka | PPO + Domain Randomization (to nie gra, lecz wykorzystuje te same metody gradientu polityki) |
| Optymalizacja kombinatoryczna | Warianty AlphaZero (AlphaTensor, AlphaDev) |

Uniwersalny schemat – gra z samym sobą, wzmocnienie procesu wyszukiwania oraz destylacja polityki – sprawdza się w przypadku tekstu, pikseli i sterowania fizycznego. GRPO to najnowsze ogniwo w tej ewolucji; kolejne z pewnością nadejdą.

## Wyślij to

Zapisz pod ścieżką `outputs/skill-game-rl-designer.md`:

```markdown
---
name: game-rl-designer
description: Design a game-RL or reasoning-RL training pipeline (AlphaZero / MuZero / GRPO) for a given domain.
version: 1.0.0
phase: 9
lesson: 12
tags: [rl, alphazero, muzero, grpo, self-play]
---

Given a target (perfect-info game / imperfect-info / Atari / LLM reasoning / combinatorial), output:

1. Environment fit. Known rules? Markov? Stochastic? Multi-agent? Informs AlphaZero vs MuZero vs GRPO.
2. Search strategy. MCTS (PUCT with learned prior), Gumbel-sampled, best-of-N, or none.
3. Self-play plan. Symmetric self-play / league / offline data / verifier-generated.
4. Target signal. Game outcome / verifier reward / preference / learned model. Include robustness plan.
5. Diagnostics. Win rate vs baseline, ELO curve, verifier pass rate, KL to reference.

Refuse AlphaZero on imperfect-info games (route to CFR). Refuse GRPO without a trusted verifier. Refuse any game-RL pipeline without a fixed baseline opponent set (self-play ELO is uncalibrated otherwise).
```

## Ćwiczenia

1. **Łatwe:** Zaimplementuj uproszczone GRPO w pliku `code/main.py`. Przetrenuj model na 2 promptach z 4 możliwymi tokenami odpowiedzi. Zbieżność powinna zostać osiągnięta w mniej niż 1000 aktualizacjach przy rozmiarze grupy $G=8$.
2. **Średnie:** Podłącz algorytm PPO (w wersji clipped) oraz klasyczny REINFORCE. Porównaj efektywność próbkowania (sample efficiency) i wariancję nagrody z wynikami GRPO w tym samym środowisku.
3. **Trudne:** Rozszerz środowisko o dwuetapowy łańcuch wnioskowania (agent generuje dwa kolejne tokeny, a weryfikator ocenia całą parę). Przeanalizuj, jak GRPO radzi sobie z przypisywaniem kredytu (credit assignment) w takich sekwencjach. (Wskazówka: oblicz przewagę grupy dla *całej sekwencji* i rozpropaguj ją na obie pozycje tokenów).

## Kluczowe terminy

| Termin | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|----------------------|
| MCTS | „Przeszukiwanie drzew w oparciu o wyuczoną sieć” | Algorytm przeszukiwania drzew Monte Carlo (Monte Carlo Tree Search); selekcja oparta o PUCT z prawdopodobieństwami a priori i wartościami z sieci `(p, v)`. |
| AlphaZero | „Gra z samym sobą + MCTS” | Sieć polityki i wartości trenowana tak, aby odzwierciedlać rozkład wizyt MCTS oraz ostateczny wynik gry. |
| MuZero | „Wersja AlphaZero z wyuczonym modelem” | Ten sam schemat treningowy, ale realizowany w przestrzeni ukrytej dzięki wyuczonemu modelowi dynamiki środowiska. |
| GRPO | „PPO bez sieci krytyka” | Optymalizacja polityki oparta o względną przewagę grupową (Group Relative Policy Optimization); algorytm typu REINFORCE wykorzystujący średnią z grupy jako linię bazową i karę KL. |
| PUCT | „Wariant UCB stosowany w AlphaZero” | Formuła $Q + c \cdot p \cdot \frac{\sqrt{N}}{1 + N_a}$ balansująca szacowaną wartość z prawdopodobieństwem a priori. |
| Gra z samym sobą (Self-play) | „Rozgrywka agenta przeciwko własnym historycznym wersjom” | Standardowa metoda w grach o sumie zerowej, zapewniająca symetryczny sygnał treningowy. |
| Trening ligowy (League training) | „Gra z samym sobą z użyciem populacji agentów” | Przeciwnicy dobierani z puli obejmującej wersje historyczne, bieżące oraz wyspecjalizowane modele (exploiters). |
| Nagroda weryfikatora (Verifier reward) | „Uczenie ze wzmacnianiem z automatyczną weryfikacją” | Sygnał nagrody pochodzący z deterministycznego weryfikatora reguł (np. testy jednostkowe, kompilacja, poprawność matematyczna). |
| Nagroda za proces (Process reward) | „Procesowe modele nagrody (PRM)” | Ocena poprawności każdego pojedynczego kroku wnioskowania, a nie tylko wyniku końcowego. |

## Bibliografia i literatura uzupełniająca

- [Silver i in. (2017). Mastering the game of Go without human knowledge (AlphaGo Zero)](https://www.nature.com/articles/nature24270).
- [Silver i in. (2018). A general reinforcement learning algorithm that masters chess, shogi, and Go through self-play (AlphaZero)](https://www.science.org/doi/10.1126/science.aar6404).
- [Schrittwieser i in. (2020). Mastering Atari, Go, chess and shogi by planning with a learned model (MuZero)](https://www.nature.com/articles/s41586-020-03051-4).
- [Vinyals i in. (2019). Grandmaster level in StarCraft II using multi-agent reinforcement learning (AlphaStar)](https://www.nature.com/articles/s41586-019-1724-z).
- [DeepSeek-AI (2024). DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models (GRPO)](https://arxiv.org/abs/2402.03300) – praca wprowadzająca algorytm GRPO oraz względną przewagę grupową.
- [DeepSeek-AI (2025). DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948) – opis pełnego czterostopniowego procesu treningowego R1 oraz analiza modelu R1-Zero.
- [Brown i in. (2019). Superhuman AI for multiplayer poker (Pluribus)](https://www.science.org/doi/10.1126/science.aay2400) – CFR + głębokie uczenie na dużą skalę.
- [Tesauro (1995). Temporal difference learning and TD-Gammon](https://dl.acm.org/doi/10.1145/203330.203343) – pionierska praca, od której rozpoczęły się sukcesy RL w grach.
- [Hugging Face TRL — GRPOTrainer](https://huggingface.co/docs/trl/main/en/grpo_trainer) – dokumentacja biblioteki do produkcyjnych zastosowań GRPO z niestandardowymi funkcjami nagrody.
- [Zespół Qwen (2024). Qwen2.5-Math — replikacja GRPO](https://github.com/QwenLM/Qwen2.5-Math) – otwarta replikacja formuły treningowej R1 w różnych skalach modeli.
- [Sutton i Barto (2018). Ch. 17 — Granice uczenia się przez wzmacnianie](http://incompleteideas.net/book/RLbook2020.pdf) – teoretyczny i podręcznikowy opis metod self-play, przeszukiwania oraz projektowania nagród, które R1 skaluje do poziomu LLM.
