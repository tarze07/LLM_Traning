# Ocena — FID, wynik CLIP, preferencje ludzkie

> Każda tabela liderów modelu generatywnego podaje FID, wynik CLIP i współczynnik wygranych z obszaru preferencji ludzkich. Każda liczba ma tryb niepowodzenia, w który może zagrać zdeterminowany badacz. Jeśli nie znasz trybów awarii, nie możesz stwierdzić prawdziwej poprawy po uruchomieniu gry.

**Typ:** Kompilacja
**Języki:** Python
**Wymagania wstępne:** Faza 8 · 01 (taksonomia), faza 2 · 04 (metryki oceny)
**Czas:** ~45 minut

## Problem

Model generatywny jest oceniany na podstawie *jakości próbki* i *przylegania kondycjonowania*. Żaden z nich nie ma miary w formie zamkniętej. Twój model musi wyrenderować 10 000 obrazów; coś musi przypisać im numery; musisz ufać liczbom w rodzinach modeli, w różnych rozdzielczościach i w różnych architekturach. Trzy wskaźniki przetrwały wyzwanie lat 2014–2026:

- **FID (Fréchet Inception Distance).** Odległość pomiędzy dwoma rozkładami — rzeczywistym i wygenerowanym — w przestrzeni cech sieci Incepcji. Niżej jest lepiej.
- **Wynik CLIP.** Podobieństwo cosinusowe pomiędzy osadzeniem obrazu CLIP wygenerowanego obrazu a osadzeniem tekstu CLIP podpowiedzi. Wyżej jest lepiej. Mierzy szybkie przyleganie.
- **Preferencje ludzkie.** Zestaw dwa modele bezpośrednio w tym samym wierszu poleceń, poproś ludzi (lub model klasy GPT-4) o wybranie lepszego, a następnie zagreguj i uzyskaj wynik Elo.

Zobaczysz także: IS (wynik początkowy, w większości na emeryturze), KID, CMMD, ImageReward, PickScore, HPSv2, MJHQ-30k. Każdy koryguje jedną awarię poprzedniego.

## Koncepcja

![FID, CLIP i preferencje: trzy osie, różne tryby awarii](../assets/evaluation.svg)

### FID — jakość próbki

Heusel i in. (2017). Kroki:

1. Wyodrębnij funkcje Inception-v3 (2048-D) dla N rzeczywistych obrazów i N wygenerowanych.
2. Dopasuj Gaussa do każdej puli: oblicz średnią `μ_r, μ_g` i kowariancję `Σ_r, Σ_g`.
3. FID = `||μ_r - μ_g||² + Tr(Σ_r + Σ_g - 2 · (Σ_r · Σ_g)^0.5)`.

Interpretacja: Odległość Frécheta pomiędzy dwoma wielowymiarowymi Gaussami w przestrzeni cech. Niższy = więcej podobnych rozkładów.

Tryby awarii:
- **Oparte na małym N.** FID jest średnią kwadratową rozkładu cech — małe N nie docenia kowariancji, daje fałszywie niski FID. Zawsze używaj N ≥ 10 000.
- **Zależne od Incepcji.** Inception-v3 zostało przeszkolone w ImageNet. Domeny oddalone od ImageNet (twarze, grafika, obrazy tekstowe) generują bezsensowny FID. Użyj ekstraktora funkcji specyficznego dla domeny.
- **Gry.** Nadmierne dopasowanie do wersji Inception zapewnia niski FID bez poprawy jakości obrazu. Pokonaj go za pomocą CMMD (poniżej).

### Wynik CLIP — szybkie przestrzeganie zaleceń

Radford i in. (2021). Dla wygenerowanego obrazu + zachęta:

```
clip_score = cos_sim( CLIP_image(x_gen), CLIP_text(prompt) )
```

Średnia z 30 tys. wygenerowanych obrazów → skalar porównywalny między modelami.

Tryby awarii:
- **Własne słabe punkty CLIP.** CLIP ma słabe rozumowanie kompozycyjne („czerwony sześcian na niebieskiej kuli” często zawodzi). Modele mogą osiągać dobre pozycje w wynikach CLIP bez konieczności wykonywania skomplikowanych poleceń.
- **Błąd w przypadku krótkich podpowiedzi.** Krótkie podpowiedzi zawierają więcej dopasowań obrazu CLIP w środowisku naturalnym. Dłuższe podpowiedzi mają mechanicznie niższe wyniki CLIP.
- **Szybka gra.** Dodanie „arcydzieła wysokiej jakości w rozdzielczości 4K” w monicie zawyża wynik CLIP bez poprawy powiązania obrazu z tekstem.

CMMD (Jayasumana i in., 2024) naprawia niektóre z nich: wykorzystuje funkcje CLIP zamiast Incepcji, rozbieżność maksymalnej średniej zamiast Frécheta. Lepiej wykrywa subtelne różnice w jakości.

### Ludzkie preferencje — podstawowa prawda

Wybierz pulę podpowiedzi. Generuj za pomocą modelu A i modelu B. Pokaż pary ludziom (lub silnemu sędziemu LLM). Łączne zwycięstwa przekładają się na wynik Elo lub Bradley-Terry. Punkty odniesienia:

- **PartiPrompts (Google)**: 1600 różnorodnych podpowiedzi, 12 kategorii.
- **HPSv2**: 107 tys. adnotacji ludzkich, powszechnie używanych jako zautomatyzowany serwer proxy.
- **ImageReward**: 137 tys. par preferencji obrazu zachęty, licencja MIT.
- **PickScore**: przeszkolony w zakresie preferencji Pick-a-Pic 2,6 mln.
- **Areny wizerunkowe w stylu Chatbot-Arena**: https://imagearena.ai/ i inne.

Tryby awarii:
- **Oceniaj rozbieżności.** Osoby niebędące ekspertami mają inne preferencje niż eksperci. Użyj obu.
- **Szybka dystrybucja.** Wyselekcjonowane podpowiedzi faworyzują jedną rodzinę. Zawsze dokumentuj.
- **Hakowanie nagród dla sędziów LLM.** Sędzia GPT-4 daje się zwieść ładnym, ale błędnym wynikom. Trianguluj z człowiekiem.

## Używajcie razem

Raport z oceny produkcji powinien zawierać:

1. FID na 10-30 tys. próbek w porównaniu z ustalonym rozkładem rzeczywistym (jakość próbki).
2. Wynik CLIP / CMMD na tych samych próbkach w porównaniu z ich podpowiedziami (przestrzeganie).
3. Współczynnik wygranych na zaślepionej arenie w porównaniu z poprzednim modelem (ogólne preferencje).
4. Analiza trybu awarii: 50 losowo wybranych wyników, oznaczonych pod kątem znanych problemów (anatomia dłoni, renderowanie tekstu, stała liczba obiektów).

Każdy pojedynczy wskaźnik jest kłamstwem. Trzy potwierdzające wskaźniki + ocena jakościowa to twierdzenie.

## Zbuduj to

`code/main.py` implementuje agregację FID, CLIP-score-like i Elo na syntetycznych „wektorach cech” (używamy wektorów 4-D jako zamienników cech Incepcji). Widzisz:

- Obliczenia FID dla małego N i dużego N — obciążenie.
- „Wynik CLIP” jako cosinus podobieństwa pomiędzy pulami cech.
- Reguła aktualizacji Elo z syntetycznego strumienia preferencji.

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

- **FID przy N=1000.** Heurystyka jest zawodna poniżej N=10k. Artykuły opisujące niski FID N to gra.
- **Porównanie FID w różnych rozdzielczościach.** Zmiana rozmiaru 299×299 Incepcji zmienia rozkład funkcji. Porównaj tylko w dopasowanej rozdzielczości.
- **Zgłaszanie jednego rozstawienia.** Uruchom minimum 3 rozstawienia. Zgłoś st.
- **CLIP ocenia inflację poprzez negatywne podpowiedzi.** Niektóre rurociągi wzmacniają CLIP poprzez nadmierne dopasowanie podpowiedzi. Sprawdź nasycenie wizualne.
- **Błąd Elo wynikający z nakładania się podpowiedzi.** Jeśli oba modele zobaczyły monit wzorcowy podczas treningu, Elo nie ma znaczenia. Użyj wstrzymanych zestawów podpowiedzi.
- **Ewaluacja płacowego tłumu jest zróżnicowana.** Płodni, MTurk komentatorzy uważają, że są młodsi/przyjazni technologii. Połącz się z rekrutowanymi ekspertami w dziedzinie sztuki/projektu.

## Użyj tego

Protokół oceny produkcji w 2026 roku:

| Filar | Minimalna | Polecane |
|--------|---------|------------|
| Jakość próbki | FID na 10 tys. vs utrzymywana realność | + CMMD na 5 tys. + FID na podzbiorze na kategorię |
| Szybkie przestrzeganie | Wynik CLIP na 30 tys. | + HPSv2 + ImageReward + Odpowiedzi na pytania w stylu VQA |
| Preferencje | 200 zaślepionych par w porównaniu z wartością wyjściową | + 2000 sparowanych ludzi + sędzia LLM + Chatbot Arena |
| Analiza awarii | 50 ręcznie oflagowanych | 500 ręcznie oflagowanych + automatyczny klasyfikator bezpieczeństwa |

Wszystkie cztery filary w jednym raporcie = roszczenie. Każdy sam = marketing.

## Wyślij to

Zapisz `outputs/skill-eval-report.md`. Skill przyjmuje nowy punkt kontrolny modelu + linię bazową i generuje pełny plan oceny: rozmiary próbek, metryki, sondy dotyczące trybu awarii, kryteria podpisu.

## Ćwiczenia

1. **Łatwe.** Uruchom `code/main.py`. Porównaj FID przy N=100 z N=1000 w tych samych rozkładach syntetycznych. Zgłoś wielkość odchylenia.
2. **Średni.** Zaimplementuj CMMD z syntetycznych funkcji w stylu CLIP (wzór można znaleźć w Jayasumana i in., 2024). Porównaj wrażliwość na różnice w jakości z FID.
3. **Trudne.** Powtórz konfigurację HPSv2: weź 1000 par podpowiedzi obrazu z podzbioru Pick-a-Pic, dostosuj mały punktator oparty na CLIP na podstawie preferencji i zmierz jego zgodność z zatrzymanym zestawem.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|----------------------|
| FID | „Odległość początkowa Frécheta” | Odległość Frécheta Gaussa pasuje do cech rzeczywistych i genowych Incepcji. |
| Wynik CLIP | „Podobieństwo tekstu do obrazu” | Podobieństwo cosinusowe między obrazem CLIP a osadzeniem tekstu. |
| CMMD | „Wymiana FID” | MMD z funkcją CLIP; mniej stronniczy, bez założenia Gaussa. |
| JEST | „Wynik początkowy” | Exp KL(p(y|x) || p(y)); słabo koreluje z nowoczesnymi modelami, na emeryturze. |
| HPSv2 / ImageReward / PickScore | „Wyuczone proxy preferencji” | Małe modele wytrenowane w oparciu o ludzkie preferencje; pełnić funkcję automatycznych sędziów. |
| Elo | „Ocena szachowa” | Agregacja zwycięstw parami Bradleya-Terry'ego. |
| PartiPrompts | „Zestaw podpowiedzi wzorcowych” | 1600 podpowiedzi wybranych przez Google w 12 kategoriach. |
| FD-DINO | „Wymiana samozasilająca” | FD wykorzystujący funkcje DINOv2; lepsze dla domen spoza ImageNet. |

## Uwaga produkcyjna: ocena również wymaga wnioskowania

Uruchomienie FID na 10 tys. próbek oznacza wygenerowanie 10 tys. obrazów. W przypadku 50-stopniowej bazy SDXL przy 1024² na pojedynczym L4 oznacza to ~11 godzin wnioskowania w ramach pojedynczego żądania. Budżety ewaluacyjne są rzeczywiste, a ramy są dokładnie zgodne ze scenariuszem wnioskowania offline (maksymalizacja przepustowości, ignorowanie TTFT):

- **Twarde przetwarzanie wsadowe, zapomnij o opóźnieniu.** Ocena offline = statyczne przetwarzanie wsadowe w największym rozmiarze mieszczącym się w pamięci. `pipe(...).images` z `num_images_per_prompt=8` na 80GB H100 działa 4-6 razy szybciej niż w przypadku pojedynczego żądania.
- **Przechowuj w pamięci podręcznej rzeczywiste cechy.** Ekstrakcja cech Inception (FID) lub CLIP (CLIP-score, CMMD) na podstawie rzeczywistego zestawu referencyjnego jest uruchamiana *raz* i przechowywana jako `.npz`. Nie obliczaj ponownie według eval.

Dla bramek CI/regresji: wykonaj ocenę FID + CLIP na podzbiorze 500 próbek na PR (~30 min); co wieczór biegaj pełne 10 tys. FID + HPSv2 + Elo.

## Dalsze czytanie

- [Heusel i in. (2017). GAN wytrenowane przez regułę aktualizacji w dwóch skalach czasowych zbiegają się do lokalnej równowagi Nasha (FID)](https://arxiv.org/abs/1706.08500) — artykuł FID.
- [Jayasumana i in. (2024). Nowe podejście do FID: w stronę lepszego miernika oceny generowania obrazu (CMMD)](https://arxiv.org/abs/2401.09603) – CMMD.
- [Radford i in. (2021). Uczenie się możliwych do przeniesienia modeli wizualnych na podstawie nadzoru nad językiem naturalnym (CLIP)](https://arxiv.org/abs/2103.00020) — CLIP.
- [Wu i in. (2023). HPSv2: kompleksowy wynik preferencji ludzkich](https://arxiv.org/abs/2306.09341) — HPSv2.
- [Xu i in. (2023). ImageReward: Uczenie się i ocena ludzkich preferencji w zakresie generowania tekstu na obraz](https://arxiv.org/abs/2304.05977) — ImageReward.
- [Yu i in. (2023). Skalowanie modeli autoregresyjnych do generowania bogatego w treść tekstu na obraz (Parti + PartiPrompts)](https://arxiv.org/abs/2206.10789) — PartiPrompts.
- [Stein i in. (2023). Ujawnianie wad metryk oceny modelu generatywnego](https://arxiv.org/abs/2306.04675) — ankieta dotycząca trybu awarii.