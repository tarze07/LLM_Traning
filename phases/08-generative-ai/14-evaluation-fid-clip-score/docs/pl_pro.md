# Ocena — FID, wynik CLIP, preferencje ludzkie

> Każda tabela liderów modelu generatywnego podaje FID, wynik CLIP oraz współczynnik wygranych z obszaru preferencji ludzkich. Każda z tych liczb ma tryb awarii, który może wykorzystać zdeterminowany badacz. Bez znajomości tych trybów nie sposób ocenić, czy rzeczywiście nastąpiła poprawa.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 8 · 01 (taksonomia), faza 2 · 04 (metryki oceny)
**Czas:** ~45 minut

## Problem

Model generatywny jest oceniany na podstawie *jakości próbek* i *zgodności z warunkowaniem*. Żadna z tych właściwości nie ma miary w postaci zamkniętej. Aby cokolwiek zmierzyć, trzeba wyrenderować 10 000 obrazów, przypisać im wartości liczbowe i ufać tym liczbom — porównując różne rodziny modeli, rozdzielczości i architektury. Trzy wskaźniki przetrwały próbę lat 2014–2026:

- **FID (Fréchet Inception Distance).** Odległość między dwoma rozkładami — rzeczywistym i wygenerowanym — w przestrzeni cech sieci Inception. Im niżej, tym lepiej.
- **Wynik CLIP.** Podobieństwo cosinusowe między reprezentacją obrazu a reprezentacją tekstu polecenia w modelu CLIP. Im wyżej, tym lepiej. Mierzy zgodność z treścią polecenia.
- **Preferencje ludzkie.** Oba modele zestawia się bezpośrednio, używając tych samych poleceń. Ludzie lub model klasy GPT-4 wybierają lepszy wynik, a zbiorcze zwycięstwa przekształca się w ranking Elo.

Spotykane są również: IS (Inception Score — w dużej mierze wycofany), KID, CMMD, ImageReward, PickScore, HPSv2, MJHQ-30k. Każdy z nich koryguje jedną słabość poprzednika.

## Koncepcja

![FID, CLIP i preferencje: trzy osie, różne tryby awarii](../assets/evaluation.svg)

### FID — jakość próbek

Heusel i in. (2017). Kroki:

1. Wyodrębnij cechy Inception-v3 (2048-D) dla N obrazów rzeczywistych i N wygenerowanych.
2. Dopasuj rozkład Gaussa do każdej puli: oblicz średnią `μ_r, μ_g` i kowariancję `Σ_r, Σ_g`.
3. FID = `||μ_r - μ_g||² + Tr(Σ_r + Σ_g - 2 · (Σ_r · Σ_g)^0.5)`.

Interpretacja: odległość Frécheta między dwoma wielowymiarowymi rozkładami Gaussa w przestrzeni cech. Niższa wartość oznacza bardziej zbliżone rozkłady.

Tryby awarii:
- **Małe N.** FID opiera się na estymacji kowariancji — przy zbyt małej próbie kowariancja jest niedoszacowana, co daje fałszywie niski wynik. Zawsze używaj N ≥ 10 000.
- **Zależność od Inception.** Inception-v3 był trenowany na ImageNet. W domenach odległych od ImageNet (twarze, grafika, obrazy tekstowe) FID traci sens. Należy wtedy użyć ekstraktora cech dostosowanego do danej domeny.
- **Optymalizacja pod metrykę.** Nadmierne dostrojenie do konkretnej wersji Inception obniża FID bez rzeczywistej poprawy jakości obrazów. Jako zabezpieczenie warto stosować CMMD (opisany poniżej).

### Wynik CLIP — zgodność z poleceniem

Radford i in. (2021). Dla wygenerowanego obrazu i polecenia:

```
clip_score = cos_sim( CLIP_image(x_gen), CLIP_text(prompt) )
```

Średnia z 30 tys. wygenerowanych obrazów daje skalar porównywalny między modelami.

Tryby awarii:
- **Słabości modelu CLIP.** CLIP słabo radzi sobie z rozumowaniem kompozycyjnym — sformułowanie „czerwony sześcian na niebieskiej kuli" często zawodzi. Modele mogą uzyskiwać wysokie wyniki CLIP, nie realizując złożonych poleceń.
- **Długość polecenia.** Krótkie polecenia naturalnie uzyskują wyższe podobieństwo do obrazu. Dłuższe polecenia mechanicznie obniżają wynik CLIP, co utrudnia porównania.
- **Inflacja przez inżynierię polecenia.** Dodanie fraz w stylu „arcydzieło wysokiej jakości w rozdzielczości 4K" zawyża wynik CLIP bez poprawy faktycznej zgodności obrazu z treścią polecenia.

CMMD (Jayasumana i in., 2024) eliminuje część tych problemów: używa cech CLIP zamiast Inception oraz rozbieżności maksymalnej średniej (MMD) zamiast odległości Frécheta. Lepiej wykrywa subtelne różnice w jakości.

### Preferencje ludzkie — punkt odniesienia

Wybierz pulę poleceń. Wygeneruj obrazy modelem A i modelem B. Pokaż pary oceniającym — ludziom lub silnemu sędziemu LLM. Zbiorowe zwycięstwa przekształcane są w wynik Elo lub Bradley-Terry. Kluczowe punkty odniesienia:

- **PartiPrompts (Google)**: 1600 zróżnicowanych poleceń w 12 kategoriach.
- **HPSv2**: 107 tys. ludzkich adnotacji, powszechnie stosowany jako zautomatyzowany wskaźnik zastępczy.
- **ImageReward**: 137 tys. par preferencji obraz–polecenie, licencja MIT.
- **PickScore**: trenowany na 2,6 mln preferencji z zestawu Pick-a-Pic.
- **Areny obrazowe w stylu Chatbot Arena**: https://imagearena.ai/ i inne.

Tryby awarii:
- **Rozbieżność oceniających.** Laicy mają inne preferencje niż eksperci. Warto uwzględnić obie grupy.
- **Dobór poleceń.** Wyselekcjonowany zestaw poleceń może faworyzować określoną rodzinę modeli. Należy go zawsze dokumentować.
- **Podatność sędziego LLM.** Model GPT-4 w roli sędziego daje się zwieść estetycznie atrakcyjnym, lecz błędnym wynikom. Warto weryfikować wyniki oceną ludzką.

## Łączne stosowanie

Raport z oceny produkcyjnej powinien obejmować:

1. FID na 10–30 tys. próbkach względem ustalonego rozkładu referencyjnego (jakość próbek).
2. Wynik CLIP / CMMD na tych samych próbkach względem ich poleceń (zgodność z poleceniem).
3. Współczynnik wygranych na zaślepionej arenie w porównaniu z poprzednim modelem (ogólne preferencje).
4. Analizę trybów awarii: 50 losowo wybranych wyników, oznaczonych pod kątem znanych problemów (anatomia dłoni, renderowanie tekstu, liczba obiektów).

Pojedynczy wskaźnik to zbyt mało, by cokolwiek udowodnić. Trzy zgodne wskaźniki połączone z oceną jakościową tworzą wiarygodne twierdzenie.

## Implementacja

`code/main.py` implementuje agregację FID, wyniku podobnego do CLIP oraz rankingu Elo na syntetycznych wektorach cech (4-D jako zamienniki cech Inception). Kod demonstruje:

- Obliczenia FID dla małego i dużego N — widoczne odchylenie.
- Wynik podobny do CLIP jako podobieństwo cosinusowe między pulami cech.
- Regułę aktualizacji Elo na syntetycznym strumieniu preferencji.

### Krok 1: FID w czterech liniach

```python
def fid(real_features, gen_features):
    mu_r, cov_r = mean_and_cov(real_features)
    mu_g, cov_g = mean_and_cov(gen_features)
    mean_diff = sum((a - b) ** 2 for a, b in zip(mu_r, mu_g))
    trace_term = trace(cov_r) + trace(cov_g) - 2 * sqrt_cov_product(cov_r, cov_g)
    return mean_diff + trace_term
```

### Krok 2: Podobieństwo cosinusowe w stylu CLIP

```python
def clip_like(image_feat, text_feat):
    dot = sum(a * b for a, b in zip(image_feat, text_feat))
    norm = math.sqrt(dot_self(image_feat) * dot_self(text_feat))
    return dot / max(norm, 1e-8)
```

### Krok 3: Agregacja Elo

```python
def elo_update(r_a, r_b, winner, k=32):
    expected_a = 1 / (1 + 10 ** ((r_b - r_a) / 400))
    actual_a = 1.0 if winner == "a" else 0.0
    r_a_new = r_a + k * (actual_a - expected_a)
    r_b_new = r_b - k * (actual_a - expected_a)
    return r_a_new, r_b_new
```

## Pułapki

- **FID przy N=1000.** Heurystyka jest zawodna poniżej N=10k. Artykuły raportujące niski FID przy małym N stosują nierzetelną metodologię.
- **Porównywanie FID przy różnych rozdzielczościach.** Zmiana rozmiaru do 299×299 (wymaganego przez Inception) zmienia rozkład cech. Porównania należy przeprowadzać wyłącznie przy tej samej rozdzielczości.
- **Raportowanie jednego uruchomienia.** Należy przeprowadzać co najmniej 3 uruchomienia i podawać odchylenie standardowe.
- **Inflacja wyniku CLIP przez podpowiedzi negatywne.** Niektóre potoki przetwarzania sztucznie zawyżają CLIP przez nadmierne dopasowanie polecenia. Warto sprawdzić nasycenie wizualne wyników.
- **Błąd Elo wynikający z nakładania się poleceń.** Jeśli oba modele widziały dane polecenie podczas treningu, wynik Elo traci wiarygodność. Należy stosować wydzielone zestawy poleceń.
- **Zróżnicowanie oceniających crowdsourcingowych.** Anonimowi oceniający (np. z MTurk) mają inne preferencje niż eksperci. Warto łączyć oba podejścia, angażując rekrutowanych specjalistów z obszaru sztuki i projektowania.

## Protokół oceny

Protokół oceny produkcyjnej na rok 2026:

| Filar | Minimum | Zalecane |
|--------|---------|------------|
| Jakość próbek | FID na 10 tys. vs. utrzymywany zestaw rzeczywisty | + CMMD na 5 tys. + FID na podzbiorze per kategoria |
| Zgodność z poleceniem | Wynik CLIP na 30 tys. | + HPSv2 + ImageReward + pytania VQA |
| Preferencje | 200 zaślepionych par vs. punkt odniesienia | + 2000 par ludzkich + sędzia LLM + Chatbot Arena |
| Analiza awarii | 50 ręcznie oznaczonych | 500 ręcznie oznaczonych + automatyczny klasyfikator bezpieczeństwa |

Wszystkie cztery filary w jednym raporcie to rzetelna ocena. Każdy z osobna — to marketing.

## Zadanie do wykonania

Zapisz `outputs/skill-eval-report.md`. Skrypt przyjmuje nowy punkt kontrolny modelu oraz linię bazową i generuje pełny plan oceny: rozmiary próbek, metryki, sondy trybów awarii, kryteria akceptacji.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Porównaj FID przy N=100 i N=1000 na tych samych rozkładach syntetycznych. Podaj wielkość odchylenia.
2. **Średnie.** Zaimplementuj CMMD na syntetycznych cechach w stylu CLIP (wzór w Jayasumana i in., 2024). Porównaj czułość na różnice w jakości z wynikami FID.
3. **Trudne.** Odtwórz konfigurację HPSv2: pobierz 1000 par polecenie–obraz z podzbioru Pick-a-Pic, wytrenuj mały klasyfikator oparty na CLIP pod kątem preferencji i zmierz jego zgodność na wydzielonym zestawie testowym.

## Słownik pojęć

| Termin | Potoczne znaczenie | Właściwe znaczenie |
|------|-----------------|----------------------|
| FID | „Odległość Frécheta Inception" | Odległość Frécheta między rozkładami Gaussa dopasowanymi do cech Inception obrazów rzeczywistych i generowanych. |
| Wynik CLIP | „Podobieństwo tekstu do obrazu" | Podobieństwo cosinusowe między reprezentacją obrazu a reprezentacją tekstu w modelu CLIP. |
| CMMD | „Zamiennik FID" | MMD z cechami CLIP; mniej stronniczy, nie zakłada rozkładu Gaussa. |
| IS | „Inception Score" | Exp KL(p(y|x) || p(y)); słabo koreluje z nowoczesnymi modelami, w dużej mierze wycofany. |
| HPSv2 / ImageReward / PickScore | „Wyuczone wskaźniki preferencji" | Małe modele wytrenowane na ludzkich preferencjach, pełniące rolę automatycznych sędziów. |
| Elo | „Ranking szachowy" | Agregacja parowanych zwycięstw metodą Bradley-Terry. |
| PartiPrompts | „Wzorcowy zestaw poleceń" | 1600 poleceń wybranych przez Google w 12 kategoriach. |
| FD-DINO | „Samouczący się zamiennik FID" | Odległość Frécheta z cechami DINOv2; lepsza dla domen spoza ImageNet. |

## Uwaga produkcyjna: ocena wymaga wnioskowania

Uruchomienie FID na 10 tys. próbkach oznacza wygenerowanie 10 tys. obrazów. Dla 50-krokowego SDXL przy rozdzielczości 1024² na pojedynczej karcie L4 to około 11 godzin wnioskowania w jednym zadaniu. Budżety ewaluacyjne są jak najbardziej realne. Ocena dokładnie odpowiada scenariuszowi wnioskowania wsadowego (maksymalizacja przepustowości, opóźnienie nie ma znaczenia):

- **Przetwarzanie wsadowe, bez optymalizacji opóźnienia.** Ocena offline to statyczne przetwarzanie wsadowe przy największym rozmiarze wsadu mieszczącym się w pamięci. Wywołanie `pipe(...).images` z `num_images_per_prompt=8` na 80 GB H100 działa 4–6 razy szybciej niż przy pojedynczym żądaniu.
- **Buforowanie cech referencyjnych.** Ekstrakcję cech Inception (FID) lub CLIP (wynik CLIP, CMMD) na rzeczywistym zbiorze referencyjnym wykonuje się *raz* i zapisuje jako `.npz`. Nie należy przeliczać przy każdej ewaluacji.

Dla bramek CI i testów regresji: przeprowadź ocenę FID + CLIP na podzbiorze 500 próbek przy każdym PR (~30 min); pełne 10 tys. FID + HPSv2 + Elo uruchamiaj co wieczór.

## Literatura

- [Heusel i in. (2017). GAN wytrenowane przez regułę aktualizacji w dwóch skalach czasowych zbiegają się do lokalnej równowagi Nasha (FID)](https://arxiv.org/abs/1706.08500) — artykuł oryginalny FID.
- [Jayasumana i in. (2024). Nowe podejście do FID: w stronę lepszego miernika oceny generowania obrazu (CMMD)](https://arxiv.org/abs/2401.09603) — CMMD.
- [Radford i in. (2021). Uczenie się przenoszalnych modeli wizualnych z nadzoru językowego (CLIP)](https://arxiv.org/abs/2103.00020) — CLIP.
- [Wu i in. (2023). HPSv2: kompleksowy wynik preferencji ludzkich](https://arxiv.org/abs/2306.09341) — HPSv2.
- [Xu i in. (2023). ImageReward: uczenie się i ocena ludzkich preferencji w generowaniu tekstu na obraz](https://arxiv.org/abs/2304.05977) — ImageReward.
- [Yu i in. (2023). Skalowanie modeli autoregresywnych do generowania bogatego tekstu na obraz (Parti + PartiPrompts)](https://arxiv.org/abs/2206.10789) — PartiPrompts.
- [Stein i in. (2023). Ujawnianie wad metryk oceny modeli generatywnych](https://arxiv.org/abs/2306.04675) — przegląd trybów awarii.
