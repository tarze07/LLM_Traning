# RL dla gier — AlphaZero, MuZero i era rozumowania LLM

> 1992: TD-Gammon pokonuje ludzkich mistrzów w backgammonie za pomocą czystego TD. 2016: AlphaGo pokonało Lee Sedola. 2017: AlphaZero zdominowało szachy, shogi i Go od zera. 2024: DeepSeek-R1 sprawdził ten sam przepis, z GRPO zastępującym PPO i pracuje nad rozumowaniem. Gry są punktem odniesienia, który napędza każdy przełom w tej fazie.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 9 · 05 (DQN), Faza 9 · 08 (PPO), Faza 9 · 09 (RLHF), Faza 9 · 10 (MARL)
**Czas:** ~120 minut

## Problem

Gry mają wszystko, czego pragnie RL. Czysta nagroda (wygrana/przegrana). Nieskończone odcinki (resetowanie gry samodzielnej). Doskonała symulacja (gra *jest* symulatorem). Dyskretne lub małe ciągłe przestrzenie działania. Struktura wieloagentowa wymuszająca odporność na kontradyktoryjność.

A w grach testowano każdy większy przełom w dziedzinie RL. TD-Gammon (backgammon, 1992). Atari-DQN (2013). AlphaGo (2016). AlfaZero (2017). OpenAI Five (Dota 2, 2019). AlphaStar (StarCraft II, 2019). MuZero (wyuczony model, 2019). AlphaTensor (mnożenie macierzy, 2022). AlphaDev (algorytmy sortowania, 2023). DeepSeek-R1 (rozumowanie matematyczne, 2025) — najnowsza demonstracja, że ​​techniki gier RL działają na tekście.

W tym podsumowaniu przyjrzymy się trzem przełomowym architekturom — AlphaZero, MuZero i GRPO — z jednego, ujednolicającego punktu widzenia: **samodzielna gra + wyszukiwanie + ulepszanie zasad**. Każdy uogólnia poprzedni; W szczególności GRPO to przepis AlphaZero zastosowany do rozumowania LLM, z tokenami jako działaniami i matematyczną weryfikacją jako sygnałem wygranej.

## Koncepcja

![AlphaZero ↔ MuZero ↔ GRPO: ta sama pętla, różne środowiska](../assets/rl-games.svg)

**Pętla jednocząca.**

```
while True:
    trajectory = self_play(current_policy, search)     # play game against self
    policy_target = search.improved_policy(trajectory) # search improves raw policy
    policy_net.update(policy_target, value_target)     # supervised on search output
```

**AlphaZero (2017).** Silver i in. Biorąc pod uwagę grę (szachy, shogi, Go) ze znanymi zasadami:

- Sieć wartości polisy: jedna wieża `f_θ(s) → (p, v)`. `p` ma przewagę nad legalnymi ruchami. `v` to oczekiwany wynik gry.
- Wyszukiwanie drzewa Monte Carlo (MCTS): przy każdym ruchu rozwijaj drzewo możliwych kontynuacji. Użyj `(p, v)` jako wcześniejszego + bootstrapu. Wybierz węzły według UCB (PUCT): `a* = argmax Q(s, a) + c · p(a|s) · √N(s) / (1 + N(s, a))`.
- Gra samodzielna: graj w gry agent kontra agent. W momencie przeniesienia `t` rozkład wizyt MCTS `π_t` staje się celem szkolenia w zakresie zasad.
- Strata: `L = (v - z)² - π · log p + c · ||θ||²`. `z` to wynik gry (+1 / 0 / -1).

Zero wiedzy ludzkiej. Zero ręcznie robionej heurystyki. Pojedynczy przepis, który pozwolił opanować szachy, shogi i go po kilkudziesięciu milionach samodzielnych gier.

**MuZero (2019).** Schrittwieser i in. Usuwa wymóg znajomości zasad.

- Zamiast stałego środowiska naucz się *modelu dynamiki ukrytej* `(h, g, f)`:
  - `h(s)`: zakoduj obserwację do stanu utajonego.
  - `g(s_latent, a)`: przewidź następny stan ukryty + nagroda.
  - `f(s_latent)`: przewidywanie zasady przed + wartość.
- MCTS działa w *wyuczonej przestrzeni ukrytej*. To samo wyszukiwanie, ta sama pętla treningowa.
- Działa na Go, szachach, shogi *i* Atari — jeden algorytm, brak znajomości reguł.

**Stochastic MuZero (2022).** Dodaje dynamikę stochastyczną i węzły przypadkowe; rozciąga się na gry klasy backgammon.

**Muesli, Gumbel MuZero (2022-2024).** Ulepszenia wydajności próbek i wyszukiwania deterministycznego.

**GRPO (2024-2025).** Przepis DeepSeek-R1. Ta sama pętla w kształcie AlphaZero, zastosowana do rozumowania modelu językowego:

- „Gra”: rozwiąż problem matematyczny / kodowanie / rozumowanie. „Win” = weryfikator (zaliczony przypadek testowy, dopasowanie odpowiedzi numerycznych) zwraca 1.
- Polityka: LLM. Akcje: żetony. Stan: monit + dotychczasowa odpowiedź.
- Brak krytyki (V_φ w stylu PPO). Zamiast tego dla każdego monitu pobierz przykładowe `G` uzupełnienia z zasady. Oblicz nagrodę dla każdego. Użyj **przewagi względnej grupy** `A_i = (r_i - mean_r) / std_r` jako sygnału do aktualizacji w stylu REINFORCE.
- Kara KL za politykę referencyjną zapobiegającą dryfowaniu (np. RLHF).
- Całkowita strata:

  `L_GRPO(θ) = -E_{q, {o_i}} [ (1/G) Σ_i A_i · log π_θ(o_i | q) ] + β · KL(π_θ || π_ref)`

Żadnego modelu nagrody, żadnego krytyka, żadnego MCTS. Linia bazowa względna dla grupy zastępuje wszystkie trzy. Dorównuje lub przewyższa jakość PPO-RLHF w testach wnioskowania przy ułamku obliczeń.

**Pełny przepis R1.** DeepSeek-R1 (DeepSeek 2025) to dwa modele w jednym artykule:

- **R1-Zero.** Zacznij od podstawowego modelu DeepSeek-V3. Żadnego SFT-a. Zastosuj GRPO bezpośrednio z dwoma składnikami nagrody: *nagroda za dokładność* (oparta na regułach — czy ostateczna odpowiedź została przeanalizowana pod kątem prawidłowej liczby / czy kod przeszedł testy jednostkowe) i *nagroda w formacie* (czy ukończenie zawinęło łańcuch myślowy w tagach `<think>…</think>`). Po tysiącach kroków średnia długość odpowiedzi rośnie z ~100 do ~10 000 tokenów, a wyniki testów matematycznych wznoszą się do poziomu bliskiego o1 podglądowi. Modelka uczy się rozumowania od podstaw. Wadą: łańcuchy myślowe są często nieczytelne, mieszają się języki i brakuje im dopracowania stylistycznego.
- **R1.** Napraw problemy z czytelnością R1-Zero za pomocą czterostopniowego potoku:
  1. **SFT zimnego startu.** Zbierz kilka tysięcy demonstracji o długim CoT przy czystym formatowaniu. Nadzorowany - dopracuj na nich model podstawowy. Daje to czytelny punkt wyjścia.
  2. **GRPO zorientowane na rozumowanie.** Stosuj GRPO z nagrodami za dokładność i format oraz nagrodą za *spójność językową*, aby zapobiec przełączaniu kodów.
  3. **Próbkowanie odrzucenia + runda SFT 2.** Próbuj ~600 tys. trajektorii wnioskowania z punktu kontrolnego RL, zachowaj tylko te z poprawnymi odpowiedziami końcowymi i czytelnym CoT i połącz z ~200 tys. nierozsądnych przykładów SFT (pisanie, kontrola jakości, samopoznanie). Ponownie dostrój bazę.
  4. **GRPO o pełnym spektrum.** Jeszcze jedna runda RL obejmująca zarówno rozumowanie (nagrody oparte na regułach), jak i ogólne dostosowanie (nagrody oparte na preferencjach przydatności/nieszkodliwości).

Wynik odpowiada o1 na AIME i MATH-500 przy otwartych masach i jest wystarczająco mały, aby go destylować. W tym samym artykule opublikowano także sześć destylowanych gęstych modeli (Qwen-1,5B do Lamy-70B) uzyskanych metodą SFT na śladach rozumowania R1 — brak RL u ucznia. Destylacja silnego nauczyciela RL konsekwentnie bije RL od zera w skali ucznia.

**Dlaczego GRPO zamiast PPO do rozumowania.** Trzy powody opisane w artykule DeepSeekMath (luty 2024 r.): (1) brak sieci wartości do trenowania, zmniejszenie pamięci o połowę; (2) linia bazowa grupy w naturalny sposób radzi sobie z rzadką nagrodą na końcu trajektorii, jaką wytwarzają zadania polegające na rozumowaniu; (3) normalizacja na bieżąco sprawia, że ​​korzyści są porównywalne w przypadku problemów o bardzo różnym stopniu trudności, czego nie może zrobić pojedynczy krytyk PPO.

**Bez wyszukiwania a oparte na wyszukiwaniu.** Gry się rozgałęziły:

- *Gry z doskonałą informacją i długimi horyzontami* (Go, szachy): nadal oparte na wyszukiwaniu. Dominują AlphaZero/MuZero.
- *Rozumowanie LLM*: żaden MCTS nie jest jeszcze w produkcji; GRPO przy pełnych wdrożeniach, najlepsze z N do obliczeń wnioskowania. Modele nagradzania procesów (PRM) wskazują na ponowne dodanie wyszukiwania na poziomie kroku.

## Zbuduj to

Kod w `code/main.py` implementuje **GRPO w miniaturze** — bandytę z wieloma grupami próbek. Algorytm jest taki sam jak w LLM; tylko polityka i środowisko są prostsze. Uczy *straty* i *przewagi względnej grupy*, co jest innowacją na rok 2025.

### Krok 1: małe środowisko weryfikatora

```python
QUESTIONS = [
    {"prompt": "q1", "correct": 3},
    {"prompt": "q2", "correct": 1},
]

def verify(prompt_idx, answer_token):
    return 1.0 if answer_token == QUESTIONS[prompt_idx]["correct"] else 0.0
```

W prawdziwym GRPO weryfikator przeprowadza testy jednostkowe lub sprawdza równość matematyczną.

### Krok 2: zasada: softmax ponad K tokenów odpowiedzi na monit

```python
def policy_probs(theta, p_idx):
    return softmax(theta[p_idx])
```

Odpowiednik wyniku ostatniej warstwy LLM uwarunkowanego monitem.

### Krok 3: próbkowanie grupowe i przewaga względna grupy

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

Przewagą względną grupy jest sztuczka DeepSeek 2024. Nie potrzeba krytyka. „Linia bazowa” to średnia grupowa, a normalizacja wykorzystuje standard grupowy.

### Krok 4: porównanie z wartością bazową REINFORCE (bez wartości)

Ta sama konfiguracja, te same obliczenia, zwykłe WZMOCNIENIE. GRPO łączy się szybciej i stabilniej.

### Krok 5: obserwuj entropię i KL

Taka sama diagnostyka jak w przypadku RLHF: średnia KL do odniesienia, entropia polityki, nagroda w czasie. Po ustabilizowaniu się, trening jest zakończony.

## Pułapki

- **Hakowanie nagród poprzez grę weryfikatora.** GRPO dziedziczy ryzyko RLHF: jeśli weryfikator jest błędny lub można go wykorzystać, LLM znajdzie exploit. Liczą się solidne weryfikatory (wiele przypadków testowych, dowody formalne).
- **Wielkość grupy jest zbyt mała.** Odchylenie od wartości bazowej grupy wygląda następująco: `1/√G`. Poniżej `G = 4` sygnał przewagi jest zaszumiony; standardowy wybór to `G = 8` do `64`.
- ** Błąd długości. ** Ukończenia LLM o różnych długościach mają różne logarytmiczne prawdopodobieństwa. Normalizuj według liczby tokenów lub użyj log-prob na poziomie sekwencji lub obetnij do maksymalnej długości.
- **Cykli czystej gry samodzielnej.** Trening w stylu AlphaZero może utknąć w pętlach dominacji w grach o sumie ogólnej. Łagodzone przez różnorodne grupy przeciwników (gra ligowa, lekcja 10).
- **Niezgodność zasad wyszukiwania.** AlphaZero szkoli zasady tak, aby naśladowały wyniki wyszukiwania. Jeśli siatka zasad jest zbyt mała, aby reprezentować rozkład wyszukiwania, szkolenie utknie w martwym punkcie.
- **Podłoga obliczeniowa.** MuZero / AlphaZero wymagają ogromnych obliczeń. Pojedyncza ablacja to często setki godzin GPU. Istnieją miniaturowe wersje demonstracyjne (np. AlphaZero w Connect Four) służące do nauki.
- **Pokrycie weryfikatora.** Testy jednostkowe, które zaliczają się do błędnych rozwiązań, wzmacniają błąd. Weryfikatory projektu, które wychwytują przypadki Edge.

## Użyj tego

Krajobraz gier RL w 2026 r. według domeny:

| Domena | Metoda dominująca |
|------------|--------------------------------|
| Gry planszowe dla dwóch graczy o sumie zerowej (Go, szachy, shogi) | AlphaZero / MuZero / KataGo |
| Niedoskonałe informacje o grach karcianych (poker) | CFR + głębokie uczenie się (DeepStack, Libratus, Pluribus) |
| Atari / gry pikselowe | Musli / MuZero / IMPALA-PPO |
| Duża strategia dla wielu graczy (Dota, StarCraft) | PPO + gra własna + liga (OpenAI Five, AlphaStar) |
| Rozumowanie matematyczne/kodowe LLM | GRPO (DeepSeek-R1, Qwen-RL, otwarte replikacje) |
| Wyrównanie LLM | DPO / RLHF-PPO (nie GRPO; weryfikator ma charakter nieweryfikowalny) |
| Robotyka | PPO + DR (nie gra-RL, ale używa tych samych narzędzi do gradientu polityki) |
| Problemy kombinatoryczne | Warianty AlphaZero (AlphaTensor, AlphaDev) |

*Przepis* — gra na własną rękę, usprawnienie wyszukiwania, destylacja zasad — obejmuje tekst, piksele i kontrolę fizyczną. GRPO jest najmłodszą instancją; nadchodzi więcej.

## Wyślij to

Zapisz jako `outputs/skill-game-rl-designer.md`:

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

1. **Łatwo.** Zaimplementuj bandytę GRPO w `code/main.py`. Trenuj na 2 podpowiedziach po 4 żetony odpowiedzi. Zbierz się w < 1000 aktualizacjach dzięki `G=8`.
2. **Średni.** Podłącz PPO (przycięty) i waniliowe WZMOCNIENIE. Porównaj wydajność próbki i wariancję nagrody z GRPO na tym samym bandycie.
3. **Trudne.** Rozszerzenie do „łańcucha rozumowania” o długości 2: agent emituje dwa żetony, a weryfikator nagradza parę. Zmierz, jak GRPO obsługuje przypisanie punktów w dwuetapowych sekwencjach. (Wskazówka: oblicz przewagę grupy na *pełną sekwencję*, propaguj do obu pozycji żetonów.)

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| MCTS | „Wyszukiwanie drzew za pomocą wyuczonej sieci” | Wyszukiwanie drzew w Monte Carlo; Wybór UCB1/PUCT z poznanymi `(p, v)` priorytetami. |
| AlfaZero | „Zabawa własna + MCTS” | Sieć o wartości polisy wyszkolona tak, aby pasowała do wizyt MCTS i wyników gry. |
| MuZero | „Wyuczony model AlphaZero” | Ta sama pętla, ale w przestrzeni utajonej, dzięki wyuczonej dynamice. |
| GRPO | „PPO wolne od krytyków” | Optymalizacja polityki względnej grupy; WZMOCNIJ średnią bazową grupy + KL. |
| PUKT | „UCB AlphaZero” | `Q + c · p · √N / (1 + N_a)` — równoważy szacunkową wartość z wcześniejszą. |
| Samodzielna gra | „Agent kontra ja z przeszłości” | Standard dla sumy zerowej; symetryczny sygnał treningowy. |
| Gra ligowa | „Gra własna w oparciu o populację” | Przeszłość + obecni + wyzyskiwacze próbowani jako przeciwnicy. |
| Nagroda weryfikatora | „Weryfikowalny RL” | Nagroda pochodzi z deterministycznego sprawdzania (zaliczenie testów, dopasowanie odpowiedzi). |
| Nagroda za proces | "PRM" | Oceniany jest każdy krok rozumowania, a nie tylko ostateczna odpowiedź. |

## Dalsze czytanie

- [Silver i in. (2017). Opanowanie gry Go bez wiedzy człowieka (AlphaGo Zero)](https://www.nature.com/articles/nature24270).
- [Silver i in. (2018). Ogólny algorytm uczenia się przez wzmacnianie, który pozwala opanować szachy, shogi i grę samodzielną (AlphaZero)](https://www.science.org/doi/10.1126/science.aar6404).
- [Schrittwieser i in. (2020). Opanuj Atari, Go, szachy i shogi poprzez planowanie na wyuczonym modelu (MuZero)](https://www.nature.com/articles/s41586-020-03051-4).
- [Vinyals i in. (2019). Poziom arcymistrzowski w StarCraft II (AlphaStar)](https://www.nature.com/articles/s41586-019-1724-z).
- [DeepSeek-AI (2024). DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models (GRPO)](https://arxiv.org/abs/2402.03300) — artykuł, w którym przedstawiono GRPO i punkt odniesienia względny dla grupy.
- [DeepSeek-AI (2025). DeepSeek-R1: Zachęcanie do umiejętności rozumowania w LLM poprzez uczenie się przez wzmacnianie](https://arxiv.org/abs/2501.12948) — pełna czteroetapowa receptura R1 plus ablacja R1-Zero.
- [Brown i in. (2019). Nadludzka sztuczna inteligencja do pokera wieloosobowego (Pluribus)](https://www.science.org/doi/10.1126/science.aay2400) — CFR + głębokie uczenie się na dużą skalę.
- [Tesauro (1995). Uczenie się różnic temporalnych i TD-Gammon](https://dl.acm.org/doi/10.1145/203330.203343) – artykuł, od którego wszystko się zaczęło.
- [Hugging Face TRL — GRPOTrainer] (https://huggingface.co/docs/trl/main/en/grpo_trainer) — odniesienie do produkcji dotyczące stosowania GRPO z niestandardowymi funkcjami nagradzania.
- [Zespół Qwen (2024). Qwen2.5-Math — replikacja GRPO](https://github.com/QwenLM/Qwen2.5-Math) — otwarta replikacja receptury R1 w wielu skalach.
- [Sutton i Barto (2018). Ch. 17 — Granice uczenia się przez wzmacnianie] (http://incompleteideas.net/book/RLbook2020.pdf) — podręcznikowy opis samodzielnej zabawy, wyszukiwania i „zaprojektowanej nagrody”, którą R1 tworzy w skali LLM.