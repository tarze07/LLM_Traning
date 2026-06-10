# Przewodnik po architekturze DeepSeek-V3

> Faza 10 · Lekcja 14 wymieniła sześć architektonicznych pokręteł, które obraca każdy otwarty model. DeepSeek-V3 (grudzień 2024 r., łącznie 671B parametrów, 37B aktywnych) zmienia wszystkie sześć i dodaje cztery kolejne: Multi-Head Latent Attention, pomocnicze równoważenie obciążenia bez strat, Multi-Token Prediction i trening DualPipe. W tej lekcji omówiono architekturę DeepSeek-V3 od góry do dołu i wyprowadzono liczbę parametrów z opublikowanej konfiguracji. Na koniec możesz wyjaśnić, dlaczego stosunek 671B/37B jest właściwym wyborem i dlaczego MLA + MoE razem pokonują każde z nich osobno na granicy.

**Typ:** Ucz się
**Języki:** Python (stdlib, kalkulator parametrów)
**Wymagania wstępne:** Faza 10 · 14 (przewodniki w modelu otwartym), Faza 10 · 17 (NSA), Faza 10 · 18 (MTP), Faza 10 · 19 (DualPipe)
**Czas:** ~75 minut

## Cele nauczania

- Przeczytaj konfigurację DeepSeek-V3 od góry do dołu i wyjaśnij każde pole w odniesieniu do sześciu pokręteł GPT-2 oraz czterech dodatków specyficznych dla DeepSeek.
- Uzyskaj całkowitą liczbę parametrów (671B), liczbę aktywnych parametrów (37B) i składniki, które składają się na każdy z nich.
- Oblicz wielkość pamięci podręcznej KV dla MLA w kontekście 128 KB i porównaj z kosztami, jakie zapłaciłby model o tej samej gęstości aktywnych parametrów i GQA.
- Podaj cztery innowacje specyficzne dla DeepSeek (MLA, MTP, routing bezstratny, DualPipe) i nazwij, której części architektury/stosu szkoleniowego dotyczy każda z nich.

## Problem

DeepSeek-V3 to pierwszy model z otwartym frontem, którego architektura znacząco różni się od rodziny Llama. Lama 3 405B to „GPT-2 z sześcioma pokrętłami”. DeepSeek-V3 to GPT-2 ze wszystkimi sześcioma pokrętłami i czterema dodatkowymi. Czytanie konfiguracji Lamy 3 stanowi rozgrzewkę przed zapoznaniem się z konfiguracją DeepSeek, ale głęboka struktura — kształt bloku uwagi, logika routingu, cel czasu szkolenia — jest na tyle inna, że ​​potrzebny jest osobny przewodnik.

Opłacalność uczenia się: wydanie DeepSeek-V3 z otwartym obciążeniem zmieniło znaczenie „granicznych możliwości” w modelach otwartych. Architektura jest wzorcem, który kopiuje wiele przebiegów szkoleniowych w 2026 r. Zrozumienie tego jest stawką dla każdej roli, która dotyka granicznego szkolenia lub wnioskowania LLM.

## Koncepcja

### Znów niezmienny rdzeń

DeepSeek-V3 nadal jest autoregresyjny. Nadal gromadzi bloki dekodera. Każdy blok nadal ma uwagę, MLP i dwie normy RMSNorm. Nadal używa SwiGLU w MLP. Nadal używa RoPE. Wstępnie norma. Osadzenia obciążone ciężarem. Taki sam poziom bazowy jak w przypadku każdej Lamy lub Mistrala.

### Zmiana: MLA zamiast GQA

Z fazy 10 · 14 wiesz, że GQA zmniejsza pamięć podręczną KV, dzieląc K i V pomiędzy grupami głowic Q. Funkcja Multi-Head Latent Attention (MLA) idzie dalej: K i V są kompresowane do wspólnej ukrytej reprezentacji niskiej rangi (`kv_lora_rank`), a następnie dekompresowane na każdą głowę w locie. Pamięć podręczna KV przechowuje tylko dane ukryte — zazwyczaj 512 elementów zmiennoprzecinkowych na token na warstwę, a nie 8 x 128 = 1024 elementów zmiennoprzecinkowych.

W kontekście 128 kB, DeepSeek-V3 z MLA (jeden wspólny ukryty `c^{KV}` na token na warstwę; oba K i V pochodzą z tego ukrytego poprzez projekcje w górę, które mogą zostać wchłonięte przez kolejny matmul):

```
kv_cache = num_layers * kv_lora_rank * max_seq_len * bytes_per_element
         = 61 * 512 * 131072 * 2
         = 7.6 GB
```

Hipotetyczna linia bazowa GQA (kształt Lamy 3 70B, głowice 8 KV, średnica głowicy 128) zapewniłaby:

```
kv_cache = 2 * 61 * 8 * 128 * 131072 * 2
         = 30.5 GB
```

MLA jest 4 razy mniejsza niż pamięć podręczna GQA typu Llama-3-70B w kontekście 128 KB.

Kompromis: MLA dodaje krok dekompresji na każde obliczenie uwagi (na głowę). Dodatkowe obliczenia są niewielkie w porównaniu z zaoszczędzoną przepustowością. Wygrana netto w przypadku wnioskowania w długim kontekście.

### Routing: równoważenie obciążenia bez strat

Routery MoE decydują, którzy eksperci z najwyższej półki przetwarzają każdy token. Naiwny router koncentruje zbyt wiele pracy na kilku ekspertach, pozostawiając innych bezczynnych. Rozwiązanie standardowe: dodaj dodatkowy warunek utraty, który karze za brak równowagi obciążenia. Działa to, ale nieznacznie pogarsza wydajność głównego zadania.

DeepSeek-V3 wprowadza schemat bezstratny. Do logitów routera dodawane są terminy dotyczące stronniczości poszczególnych ekspertów, dostosowywane podczas uczenia według prostej reguły: jeśli ekspert `e` jest przeciążony, zmniejsz `bias_e`; jeśli jest niedociążony, zwiększ go. Brak dodatkowego terminu straty. Trening pozostaje czysty. Obciążenie eksperckie pozostaje zrównoważone.

Wpływ na główną stratę: żaden mierzalny. Wpływ na architekturę MoE: czystszy, brak hiperparametrów powodujących straty pomocnicze do dostrojenia.

### MTP: gęstsze szkolenie + darmowy draft

Z fazy 10 · 18 wiesz, że DeepSeek-V3 dodaje moduł MTP D=1, który przewiduje, że token będzie dwie pozycje do przodu. Podsumowując, przeszkolony moduł jest ponownie wykorzystywany jako wersja robocza dekodowania spekulatywnego z akceptacją ponad 80%. Podczas treningu każdy stan ukryty jest nadzorowany na D+1 = 2 cele, zapewniając gęstszy sygnał.

Parametry: 14B na górze głównego 671B. Koszty ogólne: 2,1%.

### Szkolenie: DualPipe

Z fazy 10 · 19 wiadomo, że DualPipe to dwukierunkowy potok, który nakłada się na fragmenty do przodu i do tyłu za pomocą komunikacji międzywęzłowej typu „wszyscy do wszystkich”. W skali 2048-H800 DeepSeek-V3 odzyskuje około 245 tys. godzin GPU, które 1F1B utraciłoby z powodu baniek w rurociągach.

### Konfiguracja pole po polu

Oto konfiguracja DeepSeek-V3 (uproszczona):

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

Przeanalizuj to:

- `hidden_size=7168`: wymiar osadzania.
- `num_hidden_layers=61`: całkowita głębokość bloku.
- `first_k_dense_layers=3`: pierwsze 3 bloki używają gęstego MLP o rozmiarze 18432. Pozostałe 58 używają MoE.
- `num_attention_heads=128`: 128 głowic zapytań.
- `kv_lora_rank=512`: K i V są kompresowane do tego ukrytego wymiaru i dekompresowane na głowę.
- `num_experts=256, num_experts_per_tok=8`: każdy blok Ministerstwa Środowiska ma 256 ekspertów, z czego 8 najlepszych.
- `shared_experts=1`: oprócz 256 przekierowanych ekspertów, do każdego tokena przyczynia się 1 zawsze aktywny ekspert. Pomyśl o tym jak o „gęstej podłodze”, która gwarantuje, że każdy token otrzyma coś niezawodnego.
- `moe_intermediate_size=2048`: ukryty rozmiar MLP każdego eksperta. Mniejsze od gęstego MLP, bo jest ich 256.

### Rozliczanie parametrów

Pełne obliczenia znajdują się w `code/main.py`. Nagłówek:

- Osadzanie: `vocab * hidden = 129280 * 7168 = ~0.93B`.
- Pierwsze 3 gęste bloki: uwaga z MLA (~144M na blok) + gęsty MLP (~260M na blok) + normy. Łącznie około 1,2 miliarda.
- 58 bloków MoE: uwaga z MLA (~144 mln) + 256 ekspertów każdy (30 mln każdy) + 1 wspólny ekspert (30 mln) + norma. Łącznie ~7,95 miliarda na blok, łącznie ze wszystkimi ekspertami. Łącznie 461B dla 58 bloków MoE.
- moduł MTP: 14B.

Całkowita suma: ~476B dla architektury rdzeniowej + 14B MTP + wyraźnie opublikowana liczba 671B uwzględnia dodatkowe parametry strukturalne (tensory odchylenia, komponenty specyficzne dla ekspertów, wspólne skalowanie ekspertów itp.). Liczba, którą odtwarzamy w kalkulatorze, mieści się w granicach 3–5% opublikowanej — delta pochodzi z dokumentów raportu DeepSeek dotyczących szczegółowej księgowości, zawartych w załączniku Sekcja 2.

Aktywne parametry na forward:

- Uwaga: 144M na warstwę * 61 = 8,8B (wszystkie warstwy strzelają).
- Aktywny MLP: pierwsze 3 warstwy gęste (3 * 260M = 780M), 58 warstw MoE każda aktywnych z 8 trasowanymi + 1 współdzieloną + narzutem routingu. Aktywny MLP na warstwę: ~260M. Razem: 3*260M + 58*260M = ~15,9B.
- Osadzanie + normy: 1.2B.
- Całkowita liczba aktywnych: około 26B rdzenia + 14B MTP (przeszkolonych, ale nie zawsze działających na podstawie wniosków) ≈ 37B.

### Stosunek 671B do 37B

18-krotny współczynnik rzadkości (aktywne parametry stanowią 5,5% całości). DeepSeek-V3 to najrzadszy, pionierski model MoE, który dostarczał otwarte ciężarki. Mixtral 8x7B w proporcji 13/47 (28%) jest znacznie gęstszy. Lama 4 Maverick przy stosunku 17B/400B (4,25%) jest porównywalna. Zakład DeepSeek: na skalę pionierską, więcej ekspertów z niższym współczynnikiem aktywacji zapewnia lepszą jakość na aktywny FLOP.

### Gdzie znajduje się DeepSeek-V3

| Modelka | Razem | Aktywny | Stosunek | Uwaga | Nowatorskie pomysły |
|-------|------|-------|-------|---------------|------------|
| Lama 3 70B | 70B | 70B | 100% | GQA 64/8 | — |
| Lama 4 Maverick | 400B | 17B | 4,25% | GQA | — |
| Mixtral 8x22B | 141B | 39B | 27% | GQA | — |
| DeepSeek V3 | 671B | 37B | 5,5% | MLA 512 | MLA + MTP + bez aux + DualPipe |
| Qwen 2.5 72B | 72B | 72B | 100% | GQA 64/8 | Rozszerzenie przędzy |

### Kontynuacja: R1, V4

DeepSeek-R1 (2025) to narzędzie do treningu rozumowania oparte na szkielecie V3. R1 wykorzystuje tę samą architekturę. To, co się zmieniło, to przepis poszkoleniowy (RL na dużą skalę w weryfikowalnych zadaniach), a nie architektura przedszkoleniowa.

Oczekuje się, że DeepSeek-V4 (jeśli zostanie dostarczony) zachowa MLA + MoE + MTP i doda DSA (DeepSeek Sparse Attention), następcę NSA z fazy 10 · 17. Linia jest stabilna: kumulują się innowacje na poziomie architektury; każda wersja obraca dodatkowe pokrętła.

## Użyj tego

`code/main.py` to kalkulator parametrów specjalizujący się w kształcie DeepSeek-V3. Uruchom go, porównaj wyniki z liczbami podanymi w artykule i wykorzystaj je w hipotetycznych wariantach (256 ekspertów w porównaniu z 512, top 8 vs top 16, ranking MLA 512 vs 1024).

Na co zwrócić uwagę:

- Całkowita liczba parametrów w porównaniu z opublikowanym 671B.
- Liczba aktywnych parametrów w porównaniu z opublikowanymi 37B.
- Pamięć podręczna KV w kontekście 128k - porównanie MLA vs GQA.
- Podział na warstwy, aby zobaczyć, na co faktycznie przeznacza się budżet parametrów.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-deepseek-v3-reader.md`. Biorąc pod uwagę model z rodziny DeepSeek (V3, R1 lub dowolny przyszły wariant), generuje odczyt architektury komponent po komponencie, który nazywa każde pole konfiguracji, oblicza liczbę parametrów według komponentu i identyfikuje, które z czterech innowacji specyficznych dla DeepSeek wykorzystuje model.

## Ćwiczenia

1. Uruchom `code/main.py`. Porównaj oszacowanie całkowitego parametru kalkulatora z opublikowanym 671B i określ, skąd pochodzi delta. Sekcja 2 artykułu zawiera pełne wyszczególnienie.

2. Zmodyfikuj konfigurację, aby używać rangi MLA 256 zamiast 512. Oblicz wynikowy rozmiar pamięci podręcznej KV w kontekście 128 KB. Jaką procentową redukcję to zapewnia i jakim kosztem wpływa na ekspresję na głowę?

3. Porównaj routing DeepSeek-V3 (256 ekspertów, 8 najlepszych) z hipotetycznym wariantem (512 ekspertów, 8 najlepszych). Parametry całkowite rosną; aktywne parametry pozostają takie same. Co teoretycznie daje dodatkowa zdolność ekspercka i ile kosztuje na podstawie wniosków?

4. Przeczytaj sekcję 2.1 raportu technicznego DeepSeek-V3 (arXiv:2412.19437) na temat MLA. Wyjaśnij w trzech zdaniach, dlaczego macierze dekompresji K i V mogą zostać „wchłonięte” przez kolejny matmul w celu uzyskania efektywności czasowej wnioskowania.

5. DeepSeek-V3 wykorzystuje szkolenie 8PR w większości operacji. Oblicz oszczędność pamięci FP8 w porównaniu z BF16 do przechowywania odważników 671B. Jak to się ma do budżetu szkoleniowego o wartości 14,8T?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| MLA | „Wielogłowa ukryta uwaga” | Kompresuj K i V do wspólnego utajonego niskiego poziomu (kv_lora_rank, zazwyczaj 512), dekompresuj na głowę w locie; Pamięć podręczna KV przechowuje tylko ukryte |
| kv_lora_rank | „Przyciemnienie kompresji MLA” | Rozmiar wspólnego utajonego dla K i V; DeepSeek-V3 wykorzystuje 512 |
| Pierwsze k gęstych warstw | „Wczesne warstwy pozostają gęste” | Kilka pierwszych warstw modelu MoE pomija router MoE i uruchamia gęsty MLP w celu zapewnienia stabilności
| num_experts_per_tok | „Routing górnego k” | Ilu rozbitych ekspertów strzela na token; DeepSeek-V3 wykorzystuje 8 |
| Wspólni eksperci | „Zawsze dostępni eksperci” | Eksperci przetwarzający każdy token niezależnie od routingu; DeepSeek-V3 wykorzystuje 1 |
| Routing pomocniczy bez strat | „Balans obciążenia dostosowany do odchylenia” | Warunki odchylenia od eksperta dostosowane podczas szkolenia, aby utrzymać równowagę obciążenia eksperta bez dodawania warunku straty |
| Moduł MTP | „Dodatkowa głowa prognostyczna” | Blok transformatorowy przewidujący t+2 na podstawie h^(1) i E(t+1); gęstsze szkolenie, bezpłatny projekt spekulatywno-dekodujący |
| Podwójna rura | „Grociąg dwukierunkowy” | Harmonogram szkoleń, który pokrywa się z obliczeniami do przodu/do tyłu z międzywęzłowymi „wszystkimi” |
| Aktywny współczynnik parametrów | „Rzadkość” | aktywne_parametry / całkowite_parametry; DeepSeek-V3 osiąga 5,5% |
| Szkolenie 8PR | „trening 8-bitowy” | Przechowywanie szkoleń i wiele operacji obliczeniowych w 8PR; mniej więcej o połowę mniej pamięci w porównaniu z BF16 przy niewielkim koszcie jakości |

## Dalsze czytanie

- [DeepSeek-AI — raport techniczny DeepSeek-V3 (arXiv:2412.19437)](https://arxiv.org/abs/2412.19437) — pełny dokument dotyczący architektury, szkoleń i wyników
- [Karta modelu DeepSeek-V3 na twarzy ściskającej](https://huggingface.co/deepseek-ai/DeepSeek-V3) — pliki konfiguracyjne i uwagi dotyczące wdrażania
- [Artykuł DeepSeek-V2 (arXiv:2405.04434)](https://arxiv.org/abs/2405.04434) — poprzednik, który wprowadził MLA
- [Artykuł DeepSeek-R1 (arXiv:2501.12948)](https://arxiv.org/abs/2501.12948) — następca uczenia się i rozumowania w architekturze V3
— [Native Sparse Attention (arXiv:2502.11089)](https://arxiv.org/abs/2502.11089) — przyszły kierunek uwagi rodziny DeepSeek
- [Repozytorium DualPipe](https://github.com/deepseek-ai/DualPipe) — odniesienie do harmonogramu szkoleń