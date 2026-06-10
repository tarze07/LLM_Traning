# Obsługa wielu regionów LLM i lokalność pamięci podręcznej KV

> Równoważenie obciążenia metodą Round-Robin (okrężną) jest wysoce szkodliwe dla wydajności buforowanego wnioskowania LLM. Zapytanie, które nie trafi do węzła przechowującego odpowiedni prefiks, ponosi pełny koszt fazy prefill (wstępnego wypełnienia) – co oznacza ok. 800 ms (P50) dla długiego promptu, w porównaniu z zaledwie ok. 80 ms w przypadku trafienia w cache (cache hit). W 2026 roku standardem produkcyjnym są routery uwzględniające stan pamięci podręcznej (cache-aware routers, np. routery vLLM napisane w Rust, router llm-d), które podejmują decyzje o kierowaniu ruchu na podstawie zdarzeń z pamięci podręcznej KV oraz dopasowywania skrótów (hashy) prefiksów. Najnowsze analizy (np. badanie GORGO) wskazują, że opóźnienie sieci międzyregionalnej powinno być jawnym parametrem w algorytmach routingu. Komercyjne usługi typu „cross-region inference” (np. AWS Bedrock Cross-Region Inference, bramy wieloklastrowe GKE) traktują wnioskowanie w sposób nieprzejrzysty (black box) – optymalizują one ogólną dostępność zasobów, a nie czas TTFT. Instytucje takie jak JPMorgan i Mayo Clinic osiągnęły w listopadzie 2024 r. czas przełączenia awaryjnego (failover) do regionu us-east-1 na poziomie ok. 22 minut. Rzeczywistość systemów odzyskiwania po awarii (Disaster Recovery, DR): aż 32% niepowodzeń procedur DR w środowiskach LLM wynika z sytuacji, w których zespoły zabezpieczyły wagi modelu, lecz zapomniały o plikach tokenizera lub konfiguracji kwantyzacji.

**Typ:** Ucz się
**Języki:** Python (stdlib, uproszczona symulacja routera kierującego ruch na podstawie prefiksów i stanu pamięci podręcznej)
**Wymagania wstępne:** Faza 17 · 04 (Wewnętrzne mechanizmy vLLM), Faza 17 · 06 (SGLang RadixAttention)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnij, dlaczego tradycyjne równoważenie obciążenia metodą Round-Robin drastycznie obniża efektywność buforowania i oszacuj związany z tym wzrost opóźnienia TTFT.
- Zaprojektuj architekturę routera uwzględniającego stan pamięci podręcznej: zdefiniuj dane wejściowe (zdarzenia pamięci podręcznej KV), algorytm (dopasowywanie prefiksu za pomocą skrótu hash) oraz kryterium rozstrzygające (poziom obciążenia GPU).
- Zidentyfikuj przyczynę 32% niepowodzeń procedur odzyskiwania po awarii (DR) dla modeli LLM (brakujące pliki tokenizera/konfiguracji kwantyzacji) i opracuj 3-plikową listę kontrolną DR.
- Odróżnij komercyjne usługi międzyregionalne (Bedrock CRI, GKE Multi-Cluster Gateway) od zaawansowanego routingu uwzględniającego lokalność pamięci podręcznej KV.

## Problem

Twoja usługa działa w trzech regionach: us-east-1, us-west-2 oraz eu-west-1. Do kierowania ruchu używasz standardowego równoważnika obciążenia (ALB) z algorytmem Round-Robin. W rezultacie współczynnik trafień w pamięć podręczną prefiksów (prefix cache hit rate) na produkcji spada do zaledwie 8%. Opóźnienie TTFT dla percentyla P50 rośnie 3-krotnie. Logi vLLM wykazują, że niemal każde zapytanie zmusza system do kosztownego, pełnego prefillu.

Algorytm Round-Robin doskonale sprawdza się w usługach bezstanowych. Wnioskowanie LLM jest jednak procesem stanowym – pamięć podręczna KV przechowuje kontekst przetworzonych dotychczas tokenów. Kierowanie zapytań „na ślepo” skutkuje wysyłaniem ich do węzłów, które nie posiadają odpowiednich danych w cache.

Dodatkowo Twój zespół opracował plan odzyskiwania po awarii (DR). Wagi modelu są replikowane do zasobnika S3 w innym regionie. Dochodzi do awarii regionalnej; próbujesz uruchomić zapasową infrastrukturę, lecz replika zgłasza błąd podczas startu. Okazuje się, że plik `tokenizer.json`, parametry kwantyzacji oraz konfiguracja skalowania RoPE znajdowały się w osobnym zasobniku, który został pominięty w procesie synchronizacji.

Uruchamianie modeli LLM w architekturze wieloregionowej wymaga zaawansowanego buforowania, inteligentnego routingu oraz rygorystycznej higieny procesów DR – nie jest to problem, który da się rozwiązać prostym równoważeniem obciążenia sieciowego.

## Koncepcja

### Routing uwzględniający stan pamięci podręcznej (Cache-Aware Routing)

Gdy zapytanie trafia do systemu, router oblicza skrót (hash) dla prefiksu promptu (np. dla pierwszych 512 tokenów). Następnie weryfikuje, która replika posiada ten prefiks w pamięci podręcznej. Repliki na bieżąco raportują stan swojej pamięci (dodanie lub usunięcie bloków) do systemu pub/sub. Router wybiera replikę z dopasowanym prefiksem, a w przypadku braku trafienia kieruje zapytanie do najmniej obciążonego procesora graficznego.

- **vLLM Router** (napisany w Rust, standard produkcyjny w 2026 r.): Subskrybuje zdarzenia `kv.cache.block_added`, utrzymuje mapowanie `skrót prefiksu → identyfikator repliki` i realizuje routing w czasie O(1). W przypadku braku trafień kieruje ruch do repliki o najkrótszej kolejce zadań.
- **llm-d router**: Rozwiązanie realizujące ten sam wzorzec, natywne dla środowisk Kubernetes. Publikuje zdarzenia za pośrednictwem API ControlPlane.
- **SGLang RadixAttention** (Faza 17 · 06): Odpowiada za zarządzanie pamięcią podręczną wewnątrz pojedynczej repliki. Router wieloregionowy działa szczebel wyżej, koordynując ruch pomiędzy wieloma replikami.

### Dane liczbowe

Opóźnienie TTFT (P50) dla promptu o długości 2k tokenów (Llama-3.3-70B FP8 na H100):
- Trafienie w pamięć podręczną (ta sama replika, prefiks w cache): ok. 80 ms.
- Brak trafienia (pełny prefill od zera): ok. 800 ms.

Różnica jest 10-krotna. Jeśli router kieruje zapytania tak, że współczynnik trafień wynosi 60–80%, wydajność systemu skaluje się liniowo wraz z liczbą replik N. Jeśli współczynnik ten wynosi zaledwie 10%, system działa tak, jakbyśmy stosowali naiwne skalowanie bez buforowania.

### Nowe ograniczenie w architekturach międzyregionalnych: opóźnienie sieci

Czas podróży pakietu w obie strony (RTT) między regionami:
- us-east-1 ↔ us-west-2: ok. 65 ms.
- us-east-1 ↔ eu-west-1: ok. 75 ms.
- us-east-1 ↔ ap-southeast-1: ok. 220 ms.

Jeśli router skieruje zapytanie z regionu us-east-1 do repliki w ap-southeast-1 tylko dlatego, że znajduje się tam pasujący prefiks, oszczędność na prefillu (spadek z 800 ms do 80 ms) zostanie całkowicie zniwelowana przez opóźnienie sieciowe wynoszące 440 ms w obie strony. Publikacja naukowa opisująca system GORGO (2026 r.) wskazuje wprost: należy optymalizować sumę `prefill_time + network_latency`, a nie te parametry osobno. Najczęściej optymalnym rozwiązaniem okazuje się pozostanie w regionie lokalnym, za wyjątkiem promptów o gigantycznych rozmiarach (wielomegabajtowych), gdzie czas prefillu całkowicie dominuje nad czasem transmisji sieciowej.

### Ograniczenia komercyjnych usług „Cross-Region Inference”

Mechanizm AWS Bedrock Cross-Region Inference automatycznie przekierowuje zapytania do innych regionów chmurowych w przypadku wyczerpania limitów przepustowości. Usługa ta optymalizuje dostępność (high availability), a nie czas TTFT, i traktuje wnioskowanie jako czarną skrzynkę. Podobnie działa brama wieloklastrowa GKE (GKE Multi-Cluster Gateway) – realizuje ona przełączanie awaryjne na poziomie usług sieciowych, nie mając świadomości stanu pamięci podręcznej KV.

Nawet przy korzystaniu z tych narzędzi, w warstwie aplikacji wciąż niezbędny jest router uwzględniający stan pamięci podręcznej. Narzędzia chmurowe rozwiązują problem typu „awaria regionu us-east-1”, podczas gdy router aplikacyjny dba o optymalizację czasu TTFT.

### Higiena procedur DR: eliminacja problemu brakujących plików (32%)

Statystyki z 2026 roku pokazują, że 32% nieudanych prób odzyskania środowisk LLM po awarii wynika z sytuacji, gdy zespoły odtworzyły wagi modelu, lecz zapomniały o replikacji:

- Plików `tokenizer.json` lub `tokenizer.model`.
- Konfiguracji kwantyzacji (`quantize_config.json`, parametrów skalowania AWQ czy punktów zerowych GPTQ).
- Specyficznych parametrów modelu (np. skalowania RoPE, masek uwagi, szablonów czatów).
- Konfiguracji silnika (pliku `vllm_config.yaml`, domyślnych ustawień próbkowania, manifestów adapterów LoRA).

Rozwiązaniem jest wdrożenie manifestu DR składającego się z trzech kluczowych komponentów:

1. Wszystkich plików z repozytorium modelu Hugging Face (wagi, konfiguracja, tokenizer).
2. Konfiguracji specyficznej dla wybranego silnika wnioskowania.
3. Manifestów wdrożeniowych (YAML dla Kubernetes, pliki Dockerfile, wersje zależności).

Zaleca się regularne (np. kwartalne) przeprowadzanie testów DR. Przećwiczenie scenariusza awarii regionu us-east-1 przez zespół JPMorgan w listopadzie 2024 r. pozwoliło skrócić czas przełączenia awaryjnego do zaledwie 22 minut.

### Lokalizacja danych (Data Residency) a routing

Wymogi dotyczące przechowywania i przetwarzania danych są nadrzędne. Dane osobowe (np. informacje medyczne PHI) obywateli UE nie mogą opuszczać granic unijnych. Jeśli router skieruje zapytanie z Paryża do regionu us-east-1 tylko ze względu na dopasowanie prefiksu w cache, dojdzie do naruszenia przepisów RODO (GDPR), niezależnie od uzyskanego zysku wydajnościowego. Przed wdrożeniem optymalizacji cache należy zdefiniować reguły routingu uwzględniające granice jurysdykcji danych.

### Liczby, które powinieneś zapamiętać

- Różnica w TTFT przy trafieniu i braku trafienia w cache: ok. 10x (80 ms vs 800 ms dla promptu 2K).
- Opóźnienie sieciowe (RTT) na trasie USA-UE: ok. 75 ms.
- Statystyka awarii DR: 32% przypadków wynika z braku plików tokenizera lub konfiguracji kwantyzacji.
- Czas przełączenia awaryjnego (JPMorgan, us-east-1, listopad 2024 r.): 22 minuty (przy umowie SLA na poziomie 30 minut).

## Użycie

Skrypt `code/main.py` symuluje trzy strategie routingu (okrężny Round-Robin, regionalny uwzględniający cache oraz globalny uwzględniający cache) w infrastrukturze wieloregionowej. Raportuje wskaźniki trafień cache, opóźnienia TTFT dla percentyli P50/P99 oraz koszty transferu międzyregionalnego.

## Efekt końcowy

W ramach tej lekcji tworzony jest dokument `outputs/skill-multi-region-router.md`. Na podstawie struktury regionów, ograniczeń prawnych dotyczących danych oraz wymogów SLA generuje on plan trasowania ruchu (routing plan).

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Przy jakiej długości promptu wejściowego routing międzyregionalny zaczyna przynosić korzyści w porównaniu z routingiem wyłącznie lokalnym, przy założeniu opóźnienia RTT na poziomie 75 ms?
2. Współczynnik trafień w pamięć podręczną (cache hit rate) spada nagle z 70% do 12%. Zdiagnozuj trzy potencjalne przyczyny i opisz, jakie metryki w logach mogą potwierdzić każdą z nich.
3. Zaprojektuj manifest DR dla skwantowanego za pomocą AWQ modelu klasy 70B, uruchomionego na vLLM z wdrożonymi 5 adapterami LoRA. Wymień wszystkie niezbędne pliki i pliki konfiguracyjne.
4. Przeanalizuj, czy mechanizm AWS Bedrock Cross-Region Inference jest wystarczający dla systemu finansowego o rygorystycznych wymaganiach SLO dla parametru TTFT. Uzasadnij swoje stanowisko na podstawie zachowania tej usługi.
5. Zapytanie pochodzące z Paryża pasuje do prefiksu zapisanego w pamięci podręcznej w regionie us-east-1. Czy router powinien przekierować to zapytanie? Zaproponuj odpowiednią regułę bezpieczeństwa (policy).

## Kluczowe terminy

| Termin | Potoczna nazwa | Rzeczywiste znaczenie |
|------|----------------|--------------------------------------|
| Routing uwzględniający cache | „inteligentny load balancer” | Kierowanie zapytań na podstawie skrótu (hash) prefiksu do repliki przechowującej odpowiednią pamięć podręczną KV |
| Zdarzenia pamięci podręcznej KV | „pub-sub dla cache” | Publikowanie przez repliki informacji o alokacji i usuwaniu bloków pamięci; dane są indeksowane przez router |
| Skrót prefiksu | „klucz cache” | Hash obliczony z pierwszych N tokenów promptu, używany przez router do wyszukiwania replik |
| GORGO | „routing międzyregionalny” | Publikacja naukowa (arXiv 2602.11688) opisująca uwzględnianie opóźnień sieciowych w routingu cache |
| Cross-Region Inference | „Bedrock CRI” | Usługa AWS realizująca automatyczne przełączanie awaryjne w celu zapewnienia dostępności; nie analizuje stanu TTFT ani cache KV |
| Manifest DR | „lista kopii zapasowej” | Kompletna lista plików niezbędnych do odtworzenia środowiska wnioskowania od zera (nie tylko wagi modelu) |
| Lokalizacja danych | „residency / RODO” | Prawne ograniczenia określające, w których regionach geograficznych mogą być przetwarzane dane użytkowników |
| RTT | „opóźnienie w obie strony” | Czas potrzebny na przebycie pakietu sieciowego w obie strony; ok. 75 ms na trasie USA-UE, ok. 220 ms USA-APAC |

## Dalsze czytanie

- [BentoML — Multi-Cloud and Cross-Region Inference](https://bentoml.com/llm/infrastructure-and-operatives/multi-cloud-and-cross-region-inference)
- [arXiv — GORGO (2602.11688)](https://arxiv.org/html/2602.11688v1) — Praca naukowa na temat ponownego wykorzystania pamięci podręcznej KV w sieciach o wysokim opóźnieniu.
- [TianPan — Multi-region LLM serving cache-locality](https://tianpan.co/blog/2026-04-17-multi-region-llm-serving-data-residency-routing) — Analiza routingu i suwerenności danych.
- [AWS Bedrock Cross-Region Inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html) — Oficjalna dokumentacja dotycząca przełączania awaryjnego.
- [vLLM Production Stack Router](https://github.com/vllm-project/production-stack) — Kod źródłowy referencyjnego routera uwzględniającego stan cache.
