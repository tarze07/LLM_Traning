# Przewodnik po architekturze DeepSeek-V3

> Faza 10 · Lekcja 14 opisała sześć architektonicznych parametrów charakterystycznych dla każdego otwartego modelu. DeepSeek-V3 (grudzień 2024 r., łącznie 671B parametrów, 37B aktywnych) modyfikuje wszystkie sześć i wprowadza cztery kolejne: Multi-Head Latent Attention, pomocnicze równoważenie obciążenia bez strat, Multi-Token Prediction oraz trening DualPipe. Niniejsza lekcja omawia architekturę DeepSeek-V3 od ogółu do szczegółu i wyprowadza liczbę parametrów z opublikowanej konfiguracji. Po jej ukończeniu będziesz w stanie wyjaśnić, dlaczego stosunek 671B/37B jest właściwym wyborem oraz dlaczego MLA i MoE razem przewyższają każde z tych rozwiązań stosowane osobno na granicy możliwości sprzętowych.

**Typ:** Ucz się
**Języki:** Python (stdlib, kalkulator parametrów)
**Wymagania wstępne:** Faza 10 · 14 (przewodniki po otwartych modelach), Faza 10 · 17 (NSA), Faza 10 · 18 (MTP), Faza 10 · 19 (DualPipe)
**Czas:** ~75 minut

## Cele nauczania

- Przeanalizować konfigurację DeepSeek-V3 i wyjaśnić każde pole w odniesieniu do sześciu parametrów GPT-2 oraz czterech rozszerzeń specyficznych dla DeepSeek.
- Wyznaczyć całkowitą liczbę parametrów (671B), liczbę parametrów aktywnych (37B) i składniki wchodzące w skład każdej z tych wartości.
- Obliczyć rozmiar pamięci podręcznej KV dla MLA w kontekście 128 KB i porównać go z kosztem modelu o tej samej gęstości aktywnych parametrów korzystającego z GQA.
- Wskazać cztery innowacje specyficzne dla DeepSeek (MLA, MTP, routing bezstratny, DualPipe) i określić, której części architektury lub stosu treningowego każda z nich dotyczy.

## Problem

DeepSeek-V3 to pierwszy model z otwartymi wagami, którego architektura znacząco odbiega od rodziny Llama. Llama 3 405B to „GPT-2 z sześcioma parametrami". DeepSeek-V3 to GPT-2 z wszystkimi sześcioma parametrami i czterema dodatkowymi. Analiza konfiguracji Llamy 3 stanowi dobre wprowadzenie przed zapoznaniem się z konfiguracją DeepSeek, jednak głęboka struktura — kształt bloku uwagi, logika routingu, cel procesu treningowego — jest na tyle odmienna, że niezbędny jest osobny przewodnik.

Dlaczego warto to rozumieć: wydanie DeepSeek-V3 z otwartymi wagami zredefiniowało pojęcie „granicznych możliwości" w modelach otwartych. Architektura ta stała się wzorcem powielanym przez wiele procesów treningowych w 2026 r. Jej znajomość jest niezbędna dla każdej roli związanej z granicznym treningiem lub wnioskowaniem LLM.

## Koncepcja

### Niezmienny rdzeń

DeepSeek-V3 pozostaje modelem autoregresyjnym. Nadal składa się z bloków dekodera. Każdy blok zawiera uwagę, MLP i dwie normy RMSNorm. Model korzysta z SwiGLU w MLP oraz z RoPE. Stosuje pre-normalizację i osadzenia z dzielonymi wagami. Punkt wyjścia jest taki sam jak w przypadku Llamy czy Mistrala.

### Zmiana: MLA zamiast GQA

Z fazy 10 · 14 wiadomo, że GQA zmniejsza pamięć podręczną KV, dzieląc K i V pomiędzy grupami głowic Q. Multi-Head Latent Attention (MLA) idzie o krok dalej: K i V są kompresowane do wspólnej reprezentacji ukrytej niskiej rangi (`kv_lora_rank`), a następnie dekompresowane dla każdej głowy w trakcie obliczeń. Pamięć podręczna KV przechowuje wyłącznie dane ukryte — zazwyczaj 512 wartości zmiennoprzecinkowych na token na warstwę, zamiast 8 × 128 = 1024 wartości.

Dla kontekstu 128 kB DeepSeek-V3 z MLA (jeden wspólny wektor ukryty `c^{KV}` na token na warstwę; zarówno K, jak i V są wyprowadzane z tego wektora przez projekcje w górę, które można wchłonąć przez kolejny matmul) obliczenia wyglądają następująco:

```
kv_cache = num_layers * kv_lora_rank * max_seq_len * bytes_per_element
         = 61 * 512 * 131072 * 2
         = 7.6 GB
```

Hipotetyczna linia bazowa z GQA (kształt Llamy 3 70B, 8 głowic KV, wymiar głowicy 128) dałaby:

```
kv_cache = 2 * 61 * 8 * 128 * 131072 * 2
         = 30.5 GB
```

MLA zajmuje czterokrotnie mniej miejsca niż pamięć podręczna GQA w stylu Llama-3-70B przy kontekście 128 KB.

Kompromis: MLA dodaje krok dekompresji przy każdym obliczeniu uwagi (na głowę). Narzut obliczeniowy jest jednak niewielki w porównaniu z oszczędnościami przepustowości. Bilans jest korzystny przy wnioskowaniu w długim kontekście.

### Routing: równoważenie obciążenia bez strat

Routery MoE decydują, którzy eksperci przetwarzają każdy token. Naiwny router koncentruje zbyt dużo pracy na kilku ekspertach, pozostawiając pozostałych bezczynnych. Standardowe rozwiązanie polega na dodaniu pomocniczego członu straty karającego za brak równowagi obciążenia. Działa to skutecznie, lecz nieznacznie pogarsza wyniki na głównym zadaniu.

DeepSeek-V3 wprowadza schemat bezstratny. Do logitów routera dodawane są człony odchylenia dla poszczególnych ekspertów, dostosowywane podczas treningu według prostej reguły: jeśli ekspert `e` jest przeciążony, `bias_e` maleje; jeśli jest niedociążony, rośnie. Nie ma dodatkowego członu straty. Trening pozostaje przejrzysty, a obciążenie ekspertów utrzymuje się w równowadze.

Wpływ na główną stratę: żaden mierzalny. Wpływ na architekturę MoE: prostszy projekt pozbawiony hiperparametrów pomocniczych strat do strojenia.

### MTP: gęstszy trening i darmowy draft

Z fazy 10 · 18 wiadomo, że DeepSeek-V3 dodaje moduł MTP o głębokości D=1, który przewiduje token o dwie pozycje do przodu. Po zakończeniu treningu moduł jest ponownie wykorzystywany jako model szkicowy w dekodowaniu spekulatywnym z akceptacją powyżej 80%. W trakcie treningu każdy stan ukryty jest nadzorowany względem D+1 = 2 celów, co zapewnia gęstszy sygnał gradientowy.

Liczba parametrów: 14B przy głównym modelu 671B. Narzut: 2,1%.

### Trening: DualPipe

Z fazy 10 · 19 wiadomo, że DualPipe to dwukierunkowy potok nakładający fragmenty przejścia w przód i w tył przy użyciu komunikacji „wszyscy do wszystkich" między węzłami. W konfiguracji 2048 procesorów H800 DeepSeek-V3 odzyskuje w ten sposób około 245 tys. godzin GPU, które byłyby utracone w harmonogramie 1F1B wskutek bąbli potoku.

### Konfiguracja — pole po polu

Poniżej przedstawiono uproszczoną konfigurację DeepSeek-V3:

```
hidden_size: 7168
intermediate_size: 18432   (dense MLP hidden size, used on first few layers)
moe_intermediate_size: 2048 (expert MLP hidden size)
num_hidden_layers: 61
first_k_dense_layers: 3    (first 3 layers use dense MLP)
num_attention_heads: 128
num_key_value_heads: 128   (formally equal to num_heads under MLA, but
                           the real compression is in kv_lora_rank)
kv_lora_rank: 512          (MLA latent dimension)
num_experts: 256            (MoE expert count per block)
num_experts_per_tok: 8      (top-8 routing)
shared_experts: 1           (always-on shared expert per block)
max_position_embeddings: 163840
rope_theta: 10000.0
vocab_size: 129280
mtp_module: 1               (1 MTP module at depth 1)
```

Analiza poszczególnych pól:

- `hidden_size=7168`: wymiar osadzeń.
- `num_hidden_layers=61`: całkowita głębokość modelu.
- `first_k_dense_layers=3`: pierwsze 3 bloki korzystają z gęstego MLP o rozmiarze 18432. Pozostałe 58 bloków używa MoE.
- `num_attention_heads=128`: 128 głowic zapytań.
- `kv_lora_rank=512`: K i V są kompresowane do tego wymiaru ukrytego i dekompresowane dla każdej głowy.
- `num_experts=256, num_experts_per_tok=8`: każdy blok MoE zawiera 256 ekspertów, z których wybieranych jest 8 najlepszych.
- `shared_experts=1`: oprócz 256 ekspertów routowanych, jeden ekspert zawsze aktywny przyczynia się do przetworzenia każdego tokena. Pełni on rolę „gęstej podłogi" gwarantującej niezawodny wynik dla każdego tokena.
- `moe_intermediate_size=2048`: wymiar ukryty MLP każdego eksperta. Jest mniejszy niż w gęstym MLP, ponieważ ekspertów jest 256.

### Zliczanie parametrów

Pełne obliczenia zawiera plik `code/main.py`. Najważniejsze składniki:

- Osadzenia: `vocab * hidden = 129280 * 7168 = ~0,93B`.
- Pierwsze 3 gęste bloki: uwaga z MLA (~144M na blok) + gęsty MLP (~260M na blok) + normy. Łącznie około 1,2B.
- 58 bloków MoE: uwaga z MLA (~144M) + 256 ekspertów (30M każdy) + 1 ekspert wspólny (30M) + norma. Łącznie ~7,95B na blok ze wszystkimi ekspertami, czyli 461B dla 58 bloków MoE.
- Moduł MTP: 14B.

Suma: ~476B dla architektury rdzeniowej + 14B MTP. Opublikowana liczba 671B uwzględnia dodatkowe parametry strukturalne (tensory odchyleń, składniki specyficzne dla ekspertów, wspólne skalowanie ekspertów itp.). Wynik uzyskany za pomocą kalkulatora mieści się w granicach 3–5% wartości opublikowanej — różnica wynika ze szczegółowej księgowości opisanej przez DeepSeek w załączniku, sekcja 2.

Parametry aktywne na jedno przejście w przód:

- Uwaga: 144M na warstwę × 61 = 8,8B (wszystkie warstwy aktywne).
- Aktywny MLP: pierwsze 3 warstwy gęste (3 × 260M = 780M), 58 warstw MoE z 8 routowanymi + 1 wspólnym ekspertem na warstwę, aktywny MLP na warstwę: ~260M. Razem: 3 × 260M + 58 × 260M = ~15,9B.
- Osadzenia i normy: 1,2B.
- Łącznie aktywnych: około 26B rdzenia + 14B MTP (przeszkolone, lecz nie zawsze aktywne przy wnioskowaniu) ≈ 37B.

### Stosunek 671B do 37B

Osiemnastokrotny współczynnik rzadkości (parametry aktywne stanowią 5,5% łącznej liczby). DeepSeek-V3 to najrzadszy model MoE z otwartymi wagami, jaki trafił do użytku publicznego. Mixtral 8x7B o stosunku 13/47 (28%) jest znacznie gęstszy. Llama 4 Maverick przy stosunku 17B/400B (4,25%) plasuje się podobnie. Zakład DeepSeek: przy pionierskiej skali więcej ekspertów z niższym współczynnikiem aktywacji zapewnia lepszą jakość na aktywny FLOP.

### Miejsce DeepSeek-V3 na mapie modeli

| Model | Razem | Aktywny | Stosunek | Uwaga | Innowacje |
|-------|-------|---------|----------|-------|-----------|
| Llama 3 70B | 70B | 70B | 100% | GQA 64/8 | — |
| Llama 4 Maverick | 400B | 17B | 4,25% | GQA | — |
| Mixtral 8x22B | 141B | 39B | 27% | GQA | — |
| DeepSeek V3 | 671B | 37B | 5,5% | MLA 512 | MLA + MTP + routing bezstratny + DualPipe |
| Qwen 2.5 72B | 72B | 72B | 100% | GQA 64/8 | Rozszerzone osadzenia pozycji |

### Co dalej: R1, V4

DeepSeek-R1 (2025) to model trenujący rozumowanie zbudowany na szkielecie V3. Korzysta z tej samej architektury — zmieniła się wyłącznie procedura po-treningowa (uczenie ze wzmocnieniem na dużą skalę na zadaniach z weryfikowalnym wynikiem), nie zaś architektura pre-treningowa.

Oczekuje się, że DeepSeek-V4 zachowa MLA + MoE + MTP i doda DSA (DeepSeek Sparse Attention) — następcę NSA z fazy 10 · 17. Kierunek rozwoju jest stabilny: innowacje na poziomie architektury nawarstwiają się, a każda wersja dołącza kolejne modyfikacje.

## Jak to wykorzystać

`code/main.py` to kalkulator parametrów dostosowany do kształtu DeepSeek-V3. Uruchom go, porównaj wyniki z liczbami z artykułu, a następnie sprawdź hipotetyczne warianty (256 ekspertów vs 512, top-8 vs top-16, ranga MLA 512 vs 1024).

Na co zwrócić uwagę:

- Całkowita liczba parametrów w porównaniu z opublikowaną wartością 671B.
- Liczba parametrów aktywnych w porównaniu z opublikowaną wartością 37B.
- Rozmiar pamięci podręcznej KV w kontekście 128 KB — porównanie MLA z GQA.
- Rozkład na warstwy, ukazujący faktyczne przeznaczenie budżetu parametrów.

## Wyjście

Ta lekcja produkuje plik `outputs/skill-deepseek-v3-reader.md`. Dla modelu z rodziny DeepSeek (V3, R1 lub dowolnego przyszłego wariantu) generuje on opis architektury komponent po komponencie, zawierający nazwy wszystkich pól konfiguracji, obliczenia liczby parametrów według składnika oraz identyfikację czterech innowacji specyficznych dla DeepSeek zastosowanych w danym modelu.

## Ćwiczenia

1. Uruchom `code/main.py`. Porównaj szacowaną całkowitą liczbę parametrów z opublikowaną wartością 671B i wskaż źródło różnicy. Pełne wyszczególnienie zawiera sekcja 2 artykułu.

2. Zmodyfikuj konfigurację, zmieniając rangę MLA z 512 na 256. Oblicz wynikowy rozmiar pamięci podręcznej KV w kontekście 128 KB. O ile procent zmniejszy się jej rozmiar i jakim kosztem dla ekspresji na głowę?

3. Porównaj routing DeepSeek-V3 (256 ekspertów, top-8) z hipotetycznym wariantem (512 ekspertów, top-8). Całkowita liczba parametrów rośnie; liczba aktywnych pozostaje bez zmian. Co teoretycznie wnosi większa pojemność ekspercka i ile kosztuje przy wnioskowaniu?

4. Przeczytaj sekcję 2.1 raportu technicznego DeepSeek-V3 (arXiv:2412.19437) poświęconą MLA. W trzech zdaniach wyjaśnij, dlaczego macierze dekompresji K i V można „wchłonąć" przez kolejny matmul w celu poprawy efektywności wnioskowania.

5. DeepSeek-V3 korzysta z treningu FP8 dla większości operacji. Oblicz oszczędność pamięci przy FP8 w porównaniu z BF16 dla przechowywania 671B wag. Jak ma się to do budżetu treningowego wynoszącego 14,8T tokenów?

## Kluczowe terminy

| Termin | Potoczne określenie | Właściwe znaczenie |
|--------|--------------------|--------------------|
| MLA | „Wielogłowa uwaga ukryta" | K i V są kompresowane do wspólnego wektora ukrytego niskiej rangi (kv_lora_rank, zazwyczaj 512), dekompresowanego dla każdej głowy w trakcie obliczeń; pamięć podręczna KV przechowuje wyłącznie ten wektor |
| kv_lora_rank | „Wymiar kompresji MLA" | Rozmiar wspólnego wektora ukrytego dla K i V; DeepSeek-V3 używa wartości 512 |
| first_k_dense_layers | „Pierwsze warstwy pozostają gęste" | Kilka pierwszych warstw modelu MoE pomija router i korzysta z gęstego MLP, co poprawia stabilność treningu |
| num_experts_per_tok | „Routing top-k" | Liczba routowanych ekspertów aktywowanych dla każdego tokena; DeepSeek-V3 używa wartości 8 |
| shared_experts | „Eksperci zawsze aktywni" | Eksperci przetwarzający każdy token niezależnie od routingu; DeepSeek-V3 używa 1 |
| Routing bezstratny | „Balansowanie obciążenia przez odchylenie" | Człony odchylenia dla ekspertów są dostosowywane podczas treningu, utrzymując równowagę obciążenia bez dodatkowego członu straty |
| Moduł MTP | „Dodatkowa głowa predykcyjna" | Blok transformatorowy przewidujący token t+2 na podstawie h^(1) i E(t+1); zapewnia gęstszy trening i bezpłatny model szkicowy dla dekodowania spekulatywnego |
| DualPipe | „Potok dwukierunkowy" | Harmonogram treningu nakładający obliczenia przejścia w przód i w tył z komunikacją „wszyscy do wszystkich" między węzłami |
| Współczynnik aktywnych parametrów | „Rzadkość" | aktywne_parametry / wszystkie_parametry; DeepSeek-V3 osiąga 5,5% |
| Trening FP8 | „Trening 8-bitowy" | Przechowywanie wag i wiele operacji obliczeniowych w formacie FP8; wymaga około połowy pamięci w porównaniu z BF16 przy marginalnym koszcie jakości |

## Dalsza lektura

- [DeepSeek-AI — raport techniczny DeepSeek-V3 (arXiv:2412.19437)](https://arxiv.org/abs/2412.19437) — pełny dokument dotyczący architektury, treningu i wyników
- [Karta modelu DeepSeek-V3 na Hugging Face](https://huggingface.co/deepseek-ai/DeepSeek-V3) — pliki konfiguracyjne i wskazówki dotyczące wdrożenia
- [Artykuł DeepSeek-V2 (arXiv:2405.04434)](https://arxiv.org/abs/2405.04434) — poprzednik wprowadzający MLA
- [Artykuł DeepSeek-R1 (arXiv:2501.12948)](https://arxiv.org/abs/2501.12948) — następnik trenujący rozumowanie na architekturze V3
- [Native Sparse Attention (arXiv:2502.11089)](https://arxiv.org/abs/2502.11089) — przyszły kierunek rozwoju mechanizmu uwagi w rodzinie DeepSeek
- [Repozytorium DualPipe](https://github.com/deepseek-ai/DualPipe) — implementacja referencyjna harmonogramu treningu
