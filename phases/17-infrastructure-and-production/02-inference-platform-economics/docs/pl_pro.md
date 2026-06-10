# Ekonomia platformy wnioskowania — Fireworks, Together AI, Baseten, Modal, Replicate, Anyscale

> Rynek wnioskowania w 2026 roku to znacznie więcej niż zwykły wynajem czasu pracy GPU. Dzieli się on na dostawców dedykowanych układów scalonych (Groq, Cerebras, SambaNova), platformy GPU (Baseten, Together AI, Fireworks, Modal) oraz rynki oparte na API (Replicate, DeepInfra). Podwyżka cen w Fireworks o 1 USD/godz. za GPU od 1 maja 2026 roku oraz wycena firmy na poziomie 4 mld USD przy przetwarzaniu ponad 10 bilionów (10T) tokenów dziennie pokazują, że model biznesowy oparty na wolumenie zapytań sprawdza się w praktyce. Z kolei Baseten w styczniu 2026 roku zamknął rundę finansowania Series E o wartości 300 mln USD przy wycenie 5 mld USD. Reguły pozycjonowania rynkowego są proste: Fireworks optymalizuje opóźnienia, Together AI stawia na bogaty katalog modeli, Baseten dostarcza rozwiązania dla klientów korporacyjnych, Modal oferuje wyjątkowe środowisko programistyczne (DX) zintegrowane z Pythonem, Replicate zapewnia świetną obsługę modeli multimodalnych, a Anyscale specjalizuje się w rozproszonych obliczeniach w Pythonie. Ta lekcja przedstawia matrycę porównawczą, którą możesz bezpośrednio zaprezentować kadrze zarządzającej.

**Typ:** Teoria (Learn)
**Języki:** Python (stdlib, prosty symulator kosztów i opóźnień wnioskowania)
**Wymagania wstępne:** Faza 17 · 01 (Zarządzane platformy LLM), faza 17 · 04 (Wewnętrzne mechanizmy serwowania vLLM)
**Czas:** ~60 minut

## Cele nauczania

- Poznaj trzy segmenty rynku wnioskowania (dedykowane układy scalone, platformy GPU, usługi zorientowane na API) i przyporządkuj do nich poszczególnych dostawców.
- Dowiedz się, dlaczego ceny usług API w modelu „za token” zbiegają w stronę krzywej kosztów silnika serwującego (serving engine), a nie kosztów samego sprzętu.
- Oblicz efektywny koszt zapytania u co najmniej trzech dostawców i dowiedz się, kiedy rozliczanie minutowe (Baseten, Modal) staje się tańsze niż rozliczanie za tokeny.
- Dowiedz się, jak dobrać odpowiednią platformę do specyfiki obciążenia (skokowe zapotrzebowanie bezserwerowe, stały ruch o wysokiej intensywności, modele niestandardowe i fine-tuned, aplikacje multimodalne).

## Problem

Przeanalizowałeś już zarządzane platformy od hiperskalera. Zdecydowałeś, że potrzebujesz bardziej wyspecjalizowanego i szybszego dostawcy – Fireworks do minimalizacji opóźnień, Together AI ze względu na szeroki wybór modeli, lub Baseten do uruchomienia precyzyjnie dostrojonego modelu niestandardowego. Masz przed sobą sześć realnych opcji, ale cenniki dostawców są sformułowane w zupełnie różny sposób. Fireworks podaje ceny w USD za milion tokenów ($/M tokens); Baseten rozlicza czas pracy w USD za minutę; Modal stosuje rozliczenie sekundowe; a Replicate wycenia pojedyncze wykonanie (prediction). Bez zamodelowania profilu obciążenia bezpośrednie porównanie tych ofert jest niemożliwe.

Co więcej, model operacyjny każdego z dostawców jest inny. Fireworks korzysta z własnego, autorskiego silnika serwującego (FireAttention) na współdzielonej infrastrukturze GPU, a stawka za token odzwierciedla krzywą wykorzystania ich zasobów. Baseten oferuje framework Truss oraz dedykowane procesory graficzne – opłata minutowa gwarantuje wyłączność zasobów GPU. Modal to klasyczne środowisko bezserwerowe (serverless) rozliczane za sekundy, zapewniające zimny start (cold start) w czasie poniżej sekundy. W efekcie za to samo zadanie (odpowiedź LLM) zapłacisz według trzech różnych funkcji kosztu.

Ta lekcja analizuje sześciu dostawców i wskazuje sytuacje, w których każdy z nich jest najbardziej opłacalny.

## Koncepcja

### Trzy segmenty rynku

**Dedykowane układy scalone (Custom Silicon)** — Groq (LPU), Cerebras (CS-3 / WSE), SambaNova (RDU). Zapewniają zazwyczaj 5–10 razy szybsze generowanie tokenów niż standardowy klaster GPU na tym samym modelu. Cena za token bywa wyższa (pod koniec 2025 roku cena Groq wynosiła ok. 0,99 USD/M tokenów dla modelu Llama-70B), ale są one bezkonkurencyjne w scenariuszach krytycznych pod kątem opóźnień. Groq to powszechny wybór produkcyjny dla agentów głosowych i tłumaczeń w czasie rzeczywistym.

**Platformy GPU** — Baseten, Together AI, Fireworks, Modal, Anyscale. Działają na infrastrukturze NVIDIA (H100, H200, B200 w 2026 roku) lub AMD. Stanowią warstwę pośrednią pomiędzy wypożyczaniem surowej mocy obliczeniowej GPU (RunPod, Lambda) a zarządzanymi usługami hiperskalera (Bedrock).

**Usługi zorientowane na API** — Replicate, DeepInfra, OpenRouter, Fal AI. Oferują bogate katalogi modeli, rozliczanie za zapytanie lub za sekundę i skupiają się na minimalizacji czasu integracji.

### Fireworks — platforma GPU zoptymalizowana pod kątem opóźnień

- Korzysta z autorskiego silnika FireAttention; deklaruje 4-krotnie mniejsze opóźnienia niż standardowa konfiguracja vLLM.
- Oferuje tańsze przetwarzanie wsadowe (batch) z rabatem ok. 50% dla zadań niewymagających natychmiastowej interakcji.
- Pozwala na uruchamianie precyzyjnie dostrojonych modeli (fine-tuned) w tej samej cenie, co modele bazowe — to ogromny wyróżnik na tle dostawców pobierających dodatkowe opłaty za adaptery LoRA.
- Połowa 2026 r.: Podwyżka cen za wynajem procesorów graficznych na żądanie o 1 USD/godz. obowiązująca od 1 maja 2026 r. Ceny hurtowe podlegają negocjacji w zależności od skali.
- Metryki biznesowe: Wycena spółki na poziomie 4 mld USD, wolumen ponad 10T tokenów dziennie.

### Together AI — optymalizacja pod kątem katalogu modeli

- Ponad 200 modeli w ofercie, w tym najnowsze wersje open-source dostępne w kilka dni po oficjalnej publikacji.
- Koszty niższe o 50-70% w porównaniu do Replicate na analogicznych modelach – pozycjonowanie jako „chmura natywna dla AI” opiera się na skali i szerokości katalogu.
- Oferuje wnioskowanie, dostrajanie (fine-tuning) i szkolenie modeli w ramach jednego, spójnego API.

### Baseten — dedykowany dla klientów korporacyjnych

- Framework Truss: Ułatwia pakowanie modeli wraz z zależnościami, kluczami dostępu (secrets) i konfiguracją serwowania w jednym manifeście.
- Szeroki wybór procesorów GPU: Od ekonomicznych układów T4 do najnowocześniejszych B200. Rozliczanie minutowe z optymalizacją czasu zimnego startu.
- Zgodność z SOC 2 Type II oraz standardem HIPAA. Częsty wybór w branżach regulowanych, takich jak fintech i digital health.
- Wycena spółki: 5 mld USD (runda Series E, styczeń 2026 r., 300 mln USD pozyskane m.in. od CapitalG, IVP, NVIDIA).

### Modal — dedykowany dla środowiska Python

- Infrastruktura jako kod (IaC) w czystym Pythonie. Konfiguracja zasobów sprowadza się do dekoratora `@modal.function(gpu="A100")` i jednego polecenia wdrożenia.
- Dokładne rozliczanie sekundowe. Zimny start trwa 2-4 sekundy w wersji zoptymalizowanej (pre-warmed) i poniżej sekundy dla małych modeli.
- Wycena spółki: 1,1 mld USD (runda Series B, 2025 r., 87 mln USD). Najlepsze oceny w niezależnych ankietach badających zadowolenie programistów (Developer Experience - DX).

### Replicate — multimodalność i prostota integracji

- Rozliczanie za pojedyncze wykonanie (prediction). Domyślny wybór dla modeli generujących i przetwarzających obrazy, wideo oraz dźwięk.
- Bogaty ekosystem wtyczek i integracji (Zapier, Vercel, systemy CMS).
- Mniej opłacalny przy masowym przetwarzaniu tekstu (LLM), ale niezastąpiony w różnorodnych potokach multimodalnych.

### Anyscale — natywna integracja z frameworkiem Ray

- Zbudowany bezpośrednio na technologii Ray; RayTurbo to autorski silnik wnioskowania konkurujący z vLLM.
- Najlepsze rozwiązanie dla rozproszonych potoków w Pythonie, gdzie wnioskowanie LLM stanowi jeden z węzłów w większym grafie obliczeniowym.
- Zarządzane klastry Ray ze ścisłą integracją z Ray AIR i Ray Serve.

### Za tokeny czy minutowo — kiedy wygrywa dany model?

Opłaty za tokeny (per-token) są optymalne, gdy obciążenie systemu jest nieregularne lub nie wymaga stałych, minimalnych opóźnień – płacisz wtedy wyłącznie za faktycznie przetworzone zapytania. Rozliczanie minutowe (per-minute) jest korzystniejsze przy wysokim i przewidywalnym natężeniu ruchu – pełne wysycenie mocy GPU sprawia, że koszt w przeliczeniu na pojedynczy token jest znacznie niższy.

Ogólna zasada: przy stałym wykorzystaniu dedykowanego procesora GPU przekraczającym **~30%**, model minutowy (Baseten, Modal) staje się tańszy niż model rozliczany za tokeny (Fireworks, Together AI). Poniżej tego progu rentowności lepsze jest rozliczanie per-token, ponieważ nie płacisz za czas bezczynności maszyn.

### Autorski silnik serwujący jako przewaga konkurencyjna

Każda z wiodących platform buduje własne optymalizacje ponad standardowymi silnikami vLLM i SGLang (np. FireAttention w Fireworks czy RayTurbo w Anyscale). Choć deklaracje marketingowe obiecują ogromne zyski wydajnościowe, w rzeczywistości vLLM i SGLang obsługują ok. 80% otwartego oprogramowania w produkcji. Kluczowymi wyróżnikami platform pozostają interfejs programistyczny (DX), szczegółowość raportowania kosztów oraz gwarancje SLA.

### Liczby warte zapamiętania

- Koszt wynajmu GPU w Fireworks: podwyżka o 1 USD/godz. od 1 maja 2026 roku.
- Deklarowana wydajność Fireworks: 4-krotnie mniejsze opóźnienia niż standardowy vLLM.
- Together AI: ceny o 50-70% niższe niż Replicate dla modeli LLM.
- Wycena Baseten: 5 mld USD (runda Series E, styczeń 2026 r., 300 mln USD).
- Wycena Modal: 1,1 mld USD (runda Series B, 2025 r.).
- Próg opłacalności rozliczeń minutowych w stosunku do tokenowych: stałe obciążenie GPU powyżej ~30%.

## Użyj tego

Skrypt `code/main.py` pozwala porównać sześciu dostawców przy syntetycznym obciążeniu w różnych modelach rozliczeniowych. Generuje on zestawienia kosztów dziennych ($/day) oraz efektywnej ceny za milion tokenów ($/M tokens). Uruchom go, aby precyzyjnie wyznaczyć punkt rentowności dla swojego systemu.

## Wdróż to (Ship It)

Do tej lekcji dołączono narzędzie `outputs/skill-inference-platform-picker.md`. Na podstawie profilu obciążenia, wymagań SLA oraz dostępnego budżetu dobierze ono główną platformę wnioskowania oraz zaproponuje rozwiązanie zapasowe.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Przy jakim stałym poziomie wykorzystania Baseten (rozliczany minutowo) staje się tańszy niż Fireworks (rozliczany za tokeny) dla modelu 70B na pojedynczym układzie H100? Wyznacz ten próg i porównaj go z ogólną zasadą 30%.
2. Twój produkt łączy generowanie obrazów, czat tekstowy oraz transkrypcję mowy na tekst. Wybierz optymalne platformy dla każdego z tych zadań i zaproponuj architekturę bramy API integrującej te usługi.
3. Fireworks podnosi stawkę za hosting Twojego głównego modelu o 1 USD/godz. Przeanalizuj wpływ tej zmiany na koszty operacyjne, zakładając, że 40% ruchu zostanie przekierowane do kolejki przetwarzania wsadowego (batch) z 50% rabatem.
4. Klient z sektora regulowanego wymaga zgodności z SOC 2 Type II, HIPAA oraz hostingu na dedykowanych procesorach GPU. Które trzy platformy spełniają te warunki i która z nich oferuje najlepsze mechanizmy zarządzania kosztami (FinOps)?
5. Porównaj koszt przetworzenia 1000 zapytań dla modelu Llama 3.1 70B w wersji bezserwerowej Fireworks, w Together AI na żądanie, na dedykowanym GPU w Baseten oraz w API Replicate. Która opcja jest najtańsza przy natężeniu ruchu wynoszącym 10 zapytań dziennie? A która przy 10 000 zapytań?

## Kluczowe terminy

| Termin | Potoczny opis | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Custom Silicon | „chipy inne niż GPU” | Dedykowane układy scalone (np. Groq LPU, Cerebras WSE, SambaNova RDU) zoptymalizowane pod kątem szybkiego generowania tokenów. |
| FireAttention | „silnik Fireworks” | Autorskie jądra obsługi mechanizmu Attention; zapewnia znacznie mniejsze opóźnienia niż standardowy vLLM. |
| Truss | „format Baseten” | Standard pakowania i konteneryzacji modeli LLM ułatwiający zarządzanie zależnościami i konfiguracją serwowania. |
| Per-token | „cena za tokeny” | Model rozliczeniowy oparty na liczbie przetworzonych tokenów; płacisz tylko za faktyczne użycie, bez kosztów bezczynności maszyn. |
| Per-minute | „dedykowane GPU” | Model rozliczeniowy opłacany za czas pracy procesora GPU; najbardziej opłacalny przy dużym, stabilnym ruchu. |
| Per-prediction | „cena za zapytanie” | Stała opłata za jedno wywołanie modelu; popularna w modelach generowania mediów (obraz, wideo). |
| RayTurbo | „silnik Anyscale” | Zoptymalizowany silnik wnioskowania dla platformy Ray, konkurujący bezpośrednio z vLLM w klastrach obliczeniowych. |
| Batch tier | „kolejka batchowa” | Asynchroniczne przetwarzanie zapytań z rabatem (często ok. 50%) oferowane m.in. przez Fireworks i OpenAI. |
| Fine-tuned at base rate | „darmowe adaptery LoRA” | Możliwość uruchamiania własnych adapterów LoRA w Fireworks bez dodatkowych opłat za dedykowane GPU. |

## Dalsze czytanie

- [Fireworks AI Pricing](https://fireworks.ai/pricing) — cenniki za tokeny, przetwarzanie wsadowe oraz wynajem dedykowanych GPU.
- [Baseten Pricing](https://www.baseten.co/pricing/) — stawki za minutę pracy GPU, opcje dedykowane i cenniki korporacyjne.
- [Modal Pricing](https://modal.com/pricing) — sekundowe rozliczenia pracy układów GPU oraz darmowy pakiet startowy.
- [Together AI Pricing](https://www.together.ai/pricing) — katalog modeli i cennik rozliczeń za tokeny.
- [Anyscale Pricing](https://www.anyscale.com/pricing) — szczegóły dotyczące RayTurbo i zarządzanych klastrów Ray.
- [Northflank — Alternatywy dla Fireworks AI](https://northflank.com/blog/7-best-fireworks-ai-alternatives-for-inference) — porównanie popularnych platform.
- [Infrabase — Dostawcy API wnioskowania w 2026 roku](https://infrabase.ai/blog/ai-inference-api-providers-compared) — analiza rynku i zestawienie ofert.
