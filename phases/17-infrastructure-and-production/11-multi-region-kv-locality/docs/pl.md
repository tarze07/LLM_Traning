# Obsługa wielu regionów LLM i lokalizacja pamięci podręcznej KV

> Okrężne równoważenie obciążenia jest aktywnie szkodliwe dla buforowanego wnioskowania LLM. Żądanie, które nie trafia do węzła przechowującego jego prefiks, płaci pełny koszt wstępnego wypełnienia — około 800 ms przy P50 w przypadku długiego monitu w porównaniu do ~ 80 ms w przypadku trafienia w pamięć podręczną. W roku 2026 wzorcem produkcyjnym będzie router obsługujący pamięć podręczną (router vLLM w języku Rust, router llm-d), który wykorzystuje zdarzenia i trasy pamięci podręcznej KV w ramach dopasowania skrótu prefiksu. Z ostatnich badań (GORGO) wynika, że ​​opóźnienie sieci międzyregionalnej jest wyraźnym określeniem celu routingu. Komercyjne oferty „wnioskowania między regionami” (wnioskowanie między regionami Bedrock, bramy wieloklastrowe GKE) traktują wnioskowanie jako nieprzejrzyste — obsługują dostępność, a nie TTFT. JPMorgan i Mayo Clinic uruchomiły tryb awaryjny us-east-1 w listopadzie 2024 r. w czasie ~22 minut. Rzeczywistość DR: 32% niepowodzeń LLM DR wynika z tego, że zespoły utworzyły kopie zapasowe wag, ale zapomniały plików tokenizera lub konfiguracji kwantyzacji.

**Typ:** Ucz się
**Języki:** Python (stdlib, zabawkowy symulator routera obsługujący prefiksy i pamięć podręczną)
**Wymagania wstępne:** Faza 17 · 04 (obsługa vLLM), faza 17 · 06 (SGLang RadixAttention)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnij, dlaczego równoważenie obciążenia okrężnie przerywa wnioskowanie w pamięci podręcznej i oszacuj karę za TTFT.
- Schemat routera obsługującego pamięć podręczną: dane wejściowe (zdarzenia pamięci podręcznej KV), algorytm (dopasowanie prefiksu i skrótu), element rozstrzygający (wykorzystanie GPU).
— Podaj nazwę sterownika awarii 32% DR dla LLM (brakujące pliki tokenizatora/konfiguracje kwantyzacji) i podaj trzyplikową listę kontrolną DR.
- Odróżnij komercyjne oferty międzyregionalne (Bedrock CRI, GKE Multi-Cluster Gateway) od routingu obsługującego KV.

## Problem

Twoja usługa działa w stanach us-east-1, us-west-2 i eu-west-1. W grze okrężnej stawiasz ALB z przodu. Współczynnik trafień w pamięci podręcznej prefiksów w produkcji spada do 8%. Potrójne TTFT P50. Twoje dzienniki vLLM pokazują, że każde żądanie wiąże się z pełnym kosztem wstępnego wypełnienia.

Metoda okrężna jest optymalna w przypadku usług bezstanowych. Wnioskowanie LLM jest z założenia stanowe — pamięć podręczna KV koduje wszystko, co widział model. Routing na ślepo oznacza kierowanie do niewłaściwej pamięci podręcznej.

Oddzielnie Twój zespół ma plan odzyskiwania po awarii. Tworzysz kopię zapasową wag modeli w regionie S3. Następuje regionalna awaria; próbujesz przejść w tryb awaryjny; replika nie chce się uruchomić. Zapomniałeś o pliku tokenizer.json, konfiguracji kwantyzacji i konfiguracji skalowania RoPE, które znajdowały się w osobnym zasobniku, którego nie zsynchronizowałeś.

Obsługa LLM w wielu regionach to problem z pamięcią podręczną, problemem z routingiem i problemem higieny DR, a nie problemem z równoważeniem obciążenia.

## Koncepcja

### Routing uwzględniający pamięć podręczną

Otrzymano żądanie z monitem. Router miesza prefiks (powiedzmy, pierwsze 512 tokenów); pyta każdą replikę „czy masz buforowany ten prefiks?”. Repliki publikują zdarzenia pamięci podręcznej KV na kanale pub/sub w trakcie przydzielania i wykluczania bloków. Router wybiera dopasowaną replikę, a jeśli nikt tego nie zrobi, przechodzi do rozstrzygania remisów opartego na GPU.

**vLLM Router** (Rust, stos produkcyjny 2026): subskrybuje zdarzenia `kv.cache.block_added`, utrzymuje skrót przedrostka → indeks repliki, trasy z wyszukiwaniem O(1). W przypadku braku dopasowania przechodzi do najniższej głębokości kolejki.

**llm-d router**: ten sam wzorzec, natywny dla Kubernetes. Publikuje zdarzenia za pośrednictwem interfejsu API ControlPlane.

**SGLang RadixAttention** (faza 17 · 06) jest odpowiednikiem wewnątrz repliki. Routing między replikami odbywa się wyłącznie w górę.

### Liczby

TTFT P50 z monitem o żeton 2 tys., Lama 3.3 70B FP8, H100:
- Trafienie w pamięć podręczną (ta sama replika, rezydent prefiksu): ~80 ms.
- Brak pamięci podręcznej (wstępne wypełnienie na zimno): ~800 ms.

10x przerwa. Jeśli router osiągnie 60–80% pamięci podręcznej prefiksów w replikach, przybliżoną wydajność pojedynczej repliki przy pojemności N replik. Jeśli osiągnie 10%, przybliżasz naiwne skalowanie.

### Międzyregiony mają nowe ograniczenie — opóźnienie sieci

Międzyregionalny RTT:
- us-wschód-1 ↔ us-zachód-2: ~65 ms.
- us-east-1 ↔ eu-west-1: ~75 ms.
- us-wschód-1 ↔ ap-południowy wschód-1: ~220 ms.

Jeśli routing przenosi żądanie z us-east-1 do gorącego prefiksu w ap-sutheast-1, zapisane wstępne wypełnienie (800 → 80 ms) jest przyćmione w porównaniu z 440 ms w obie strony. GORGO (badanie z 2026 r.) wyraźnie to stwierdza — minimalizuj `prefill_time + network_latency` łącznie, a nie samodzielnie. Często odpowiedzią jest utrzymanie routingu regionalnego, z wyjątkiem ogromnych prefiksów o wielkości wielu MB, w których dominuje wstępne wypełnianie.

### Komercyjne „wnioskowanie między regionami” tutaj nie pomaga

Wnioskowanie między regionami AWS Bedrock automatycznie kieruje żądania do innych regionów w przypadku ograniczenia wydajności. Optymalizuje dostępność, a nie TTFT, i traktuje wnioskowanie jako nieprzejrzyste. Brama wieloklastrowa GKE działa tak samo — przełączanie awaryjne na poziomie usług, brak świadomości pamięci podręcznej KV.

Nadal potrzebujesz routera obsługującego pamięć podręczną w warstwie aplikacji, nawet jeśli ich używasz. Zajmują się sprawą „us-east-1 się pali”. Routing uwzględniający pamięć podręczną obsługuje przypadek TTFT.

### Higiena DR — 32% problemu brakujących plików

Szeroko cytowana statystyka z 2026 r.: 32% niepowodzeń LLM DR ma miejsce, ponieważ zespoły cofnęły ciężary, ale zapomniały:

- `tokenizer.json` lub `tokenizer.model`
- Konfiguracje kwantyzacji (`quantize_config.json`, skale AWQ, punkty zerowe GPTQ)
- Konfiguracje specyficzne dla modelu (skalowanie RoPE, maski uwagi, szablony czatów)
- Konfiguracja silnika (`vllm_config.yaml`, domyślne ustawienia próbkowania, manifesty adaptera LoRA)

Rozwiązaniem jest manifest DR składający się z co najmniej trzech plików:

1. Wszystkie pliki w repozytorium modelu HF (wagi + konfiguracje + tokenizer).
2. Konfiguracja obsługi specyficzna dla silnika.
3. Manifest wdrożenia (YAML K8s, plik Dockerfile, blokada zależności).

Plus: co kwartał przeprowadzaj ćwiczenie DR. Ćwiczenia JPMorgan us-east-1 w listopadzie 2024 r. zakończyły się 22-minutową poprawą tylko dlatego, że przećwiczono scenariusz.

### Miejsce przechowywania danych jest ortogonalne

PHI klienta z UE nie mogą opuścić UE. Jeśli Twój router obsługujący pamięć podręczną wysyła żądanie pochodzące z Paryża do us-east-1 w celu dopasowania prefiksu, naruszyłeś RODO niezależnie od wzmocnienia TTFT. Przed optymalizacją pod kątem pamięci podręcznej podziel routery według granic miejsca zamieszkania.

### Liczby, które powinieneś zapamiętać

- Przerwa w TTFT trafienia w pamięci podręcznej i chybienia: ~10x (80 ms w porównaniu z 800 ms w trybie 2K).
- Międzyregionalny RTT USA-UE: ~75 ms.
- Awaria DR: 32% brakujących konfiguracji tokenizera/ilościowych.
— Przełączenie awaryjne JPMorgan us-east-1, listopad 2024 r.: 22 minuty (30-minutowa umowa SLA).

## Użyj tego

`code/main.py` symuluje trzy strategie routingu (okrężne, regionalne obsługujące pamięć podręczną, globalne obsługujące pamięć podręczną) w obciążeniu obejmującym wiele regionów. Raportuje współczynnik trafień w pamięci podręcznej, TTFT P50/P99 i rachunek między regionami.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-multi-region-router.md`. Biorąc pod uwagę regiony, ograniczenia dotyczące miejsca zamieszkania i umowę SLA, projektuje plan tras.

## Ćwiczenia

1. Uruchom `code/main.py`. Przy jakiej długości podpowiedzi routing między regionami jest lepszy od routingu tylko lokalnego, biorąc pod uwagę czas RTT 75 ms?
2. Współczynnik trafień w pamięci podręcznej spada z 70% do 12%. Zdiagnozuj trzy możliwe przyczyny i obserwacje, które potwierdzają każdą z nich.
3. Zaprojektuj manifest DR dla skwantowanego modelu 70B AWQ udostępnianego w vLLM z 5 adapterami LoRA. Lista wszystkich plików i konfiguracji.
4. Omów, czy wnioskowanie międzyregionalne Bedrock jest „wystarczające” dla fintechu ze ścisłymi SLO TTFT. Przytocz konkretne zachowania.
5. Żądanie pochodzenia z Paryża pasuje do prefiksu w us-east-1. Czy to kierujesz? Napisz politykę.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Routing uwzględniający pamięć podręczną | „inteligentny LB” | Trasa po dopasowaniu skrótu prefiksu do repliki przechowującej pamięć podręczną KV |
| Zdarzenia w pamięci podręcznej KV | „pub-sub pamięci podręcznej” | Repliki publikują blokowe dodawanie/eksmitowanie; indeksy routerów |
| Hash przedrostka | „klucz pamięci podręcznej” | Hash pierwszych N tokenów używanych do wyszukiwania routerów |
| GORGO | „badania tras międzyregionalnych” | arXiv 2602.11688; opóźnienie sieci jako określenie jawne |
| Wnioskowanie międzyregionalne | „Podstawa CRI” | produkt AWS; przełączanie awaryjne dostępności, a nie świadomość TTFT |
| Manifest DR | "lista kopii zapasowych" | Każdy plik potrzebny do przywrócenia — nie tylko wagi |
| Miejsce zamieszkania danych | „Granica RODO” | Ograniczenia prawne dotyczące tego, który region widzi dane użytkownika |
| RTT | „czas podróży w obie strony” | Opóźnienie sieci; 75 ms USA-UE, 220 ms USA-APAC |
| LB świadomy LLM | „LB trafienia w pamięć podręczną” | Router obsługujący pamięć podręczną jako kategoria produktu |

## Dalsze czytanie

- [BentoML — wnioskowanie dotyczące wielu chmur i regionów](https://bentoml.com/llm/infrastructure-and-operatives/multi-cloud-and-cross-region-inference)
- [arXiv — GORGO (2602.11688)](https://arxiv.org/html/2602.11688v1) — ponowne wykorzystanie pamięci podręcznej KV między regionami z opóźnieniem sieci.
— [TianPan — wieloregionowa lokalizacja pamięci podręcznej LLM obsługującej lokalizację](https://tianpan.co/blog/2026-04-17-multi-region-llm-serving-data-residency-routing)
— [Wnioskowanie międzyregionalne AWS Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html) — dokumentacja dotycząca przełączania awaryjnego dostępności.
- [vLLM Production Stack Router](https://github.com/vllm-project/production-stack) — źródło routera obsługującego pamięć podręczną.