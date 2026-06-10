# Bramy AI — LiteLLM, Portkey, Kong AI Gateway, Bifrost

> **Przegląd cen z dnia 2026-04.** Poniższe wartości odzwierciedlają stawki dostawców zarejestrowane w momencie publikacji tej lekcji; przed zacytowaniem ich w dalszej części tekstu zweryfikuj je z aktualną dokumentacją.

> Brama AI (AI Gateway) pośredniczy między Twoimi aplikacjami a dostawcami modeli LLM. Do jej podstawowych zadań należą: routing zapytań, mechanizmy awaryjne (fallback), ponawianie prób (retries), limitowanie częstotliwości zapytań (rate limiting), bezpieczne przechowywanie kluczy API (secrets management), monitorowanie (observability) oraz filtry bezpieczeństwa (guardrails). Podział rynku w 2026 roku wygląda następująco:
> **LiteLLM**: projekt open-source na licencji MIT wspierający ponad 100 dostawców, w pełni kompatybilny z formatem API OpenAI. Przy ruchu rzędu 2000 RPS (przy 8 GB RAM) w testach obciążeniowych miewa problemy ze stabilnością (błędy kaskadowe); optymalny dla systemów opartych na Pythonie przy ruchu <500 RPS, przydatny w fazie deweloperskiej i prototypowaniu.
> **Portkey**: koncentruje się na warstwie kontroli (guardrails, usuwanie danych osobowych/PII, wykrywanie ataków jailbreak, audyt logów). Od marca 2026 roku udostępniony na licencji Apache 2.0. Generuje narzut opóźnienia na poziomie 20–40 ms, a jego plan produkcyjny kosztuje od 49 USD/miesiąc.
> **Kong AI Gateway**: zbudowany na dojrzałym silniku Kong Gateway. W oficjalnych testach porównawczych Konga na maszynie z 12 procesorami okazał się o 228% szybszy od Portkey i o 859% szybszy od LiteLLM. Koszt wynosi 100 USD/model/miesiąc (maksymalnie 5 modeli w planie Plus) – odpowiedni dla przedsiębiorstw korzystających już z ekosystemu Konga.
> **Bifrost** (Maxim AI): automatyczne ponawianie zapytań z konfigurowalnym czasem oczekiwania (exponential backoff) oraz automatycznym przełączaniem na Anthropic w razie wystąpienia błędu 429 (przepełnienie limitu zapytań) w OpenAI.
> **Cloudflare / Vercel AI Gateways**: w pełni zarządzane usługi (serverless), niewymagające własnej infrastruktury, oferujące podstawowe funkcje monitorowania i ponawiania prób.
> Wymóg lokalizacji danych (data residency) często decyduje o konieczności hostowania bramy we własnej infrastrukturze (self-hosted), co wspierają projekty Portkey OSS, LiteLLM oraz Kong.

**Typ:** Teoria i praktyka
**Języki:** Python (stdlib, uproszczony symulator routingu w bramie AI)
**Wymagania wstępne:** Faza 17 · 01 (Zarządzane platformy LLM), faza 17 · 16 (Routing modeli)
**Czas:** ~60 minut

## Cele naukowe

- Omówienie sześciu fundamentalnych funkcji bramy AI (routing, fallback, retries, rate limiting, secrets management, observability oraz guardrails).
- Porównanie czterech głównych rozwiązań w 2026 roku (LiteLLM, Portkey, Kong AI Gateway, Bifrost) pod kątem wydajności i zastosowań biznesowych.
- Analiza benchmarków wydajnościowych (Kong o 228% szybszy niż Portkey i o 859% szybszy niż LiteLLM) pod kątem wymagań dla systemów przetwarzających >500 RPS.
- Podejmowanie decyzji o wyborze wariantu self-hosted lub chmury zarządzanej (managed) z uwzględnieniem lokalizacji danych oraz kosztów utrzymania.

## Problem

Twoja aplikacja komunikuje się jednocześnie z OpenAI, Anthropic oraz własną instancją modelu Llama. Każdy z tych dostawców wymaga użycia innego pakietu SDK, zwraca inne kody błędów, stosuje inne limity zapytań (rate limits) oraz metody uwierzytelniania. Potrzebujesz mechanizmu awaryjnego (jeśli OpenAI zwróci kod 429, spróbuj wysłać zapytanie do Anthropic), centralnego zarządzania kluczami API, ujednoliconego logowania metryk oraz limitów zużycia tokenów dla każdego klienta.

Próba implementacji tych mechanizmów bezpośrednio w kodzie aplikacji uzależnia każdą mikrousługę od specyficznych API dostawców. Warstwa bramy AI (AI Gateway) konsoliduje całą komunikację w jeden niezależny proces, wystawiający jednolite API (najczęściej w standardzie OpenAI), pod maską obsługując różnorodnych dostawców.

## Koncepcja

### Sześć kluczowych funkcji bram AI

1. **Unifikacja API i routing**: obsługa OpenAI, Anthropic, Gemini czy modeli własnych za pomocą jednego punktu końcowego.
2. **Mechanizmy awaryjne (Fallback)**: automatyczne przekierowanie zapytania do innego dostawcy w razie wystąpienia błędu 429, 5xx lub spadku jakości odpowiedzi.
3. **Ponawianie prób (Retries)**: zaawansowana logika powtórzeń z wykładniczym czasem oczekiwania (exponential backoff).
4. **Limitowanie zapytań (Rate Limiting)**: nakładanie limitów na poziomie pojedynczego klienta (tenant), klucza API lub wybranego modelu.
5. **Bezpieczeństwo kluczy (Secrets Management)**: dynamiczne wstrzykiwanie kluczy API z bezpiecznych magazynów (np. HashiCorp Vault) zamiast twardego kodowania ich w aplikacji.
6. **Monitorowanie (Observability)**: integracja z metrykami OpenTelemetry GenAI (opisywanymi w fazie 17 · 13) oraz dokładne rozliczanie kosztów.
7. **Filtry bezpieczeństwa (Guardrails)**: anonimizacja danych osobowych (PII scrubbing), wykrywanie prób obejścia zabezpieczeń (jailbreak) oraz filtry tematyczne promptów.

### LiteLLM (MIT Open Source, Python)

- Obsługuje ponad 100 dostawców API, zgodny ze standardem OpenAI, wspiera fallbacki i logowanie metryk.
- W testach wydajnościowych miewa problemy przy dużym natężeniu ruchu (około 2000 RPS na instancji z 8 GB RAM dochodzi do błędów kaskadowych).
- Kiedy stosować: aplikacje Pythonowe, ruch <500 RPS, środowiska testowe/stagingowe, eksperymenty z routingiem.
- Koszt: darmowy (wersja open-source), dostępne są też płatne warianty chmurowe.

### Portkey (Skupiony na kontroli i bezpieczeństwie)

- Licencja Apache 2.0 (od marca 2026 roku). Bogaty zestaw filtrów (guardrails), anonimizacja danych PII, wykrywanie jailbreaków i pełne audytowanie logów.
- Wprowadza narzut opóźnienia rzędu 20–40 ms na zapytanie.
- Koszt: wersja open-source jest darmowa; plany komercyjne z SLA zaczynają się od 49 USD/miesiąc.
- Kiedy stosować: branże regulowane wymagające restrykcyjnej ochrony danych i zaawansowanego audytu.

### Kong AI Gateway (Rozwiązanie wysokowydajne)

- Zbudowany na dojrzałej platformie Kong Gateway (Lua + OpenResty).
- Benchmark wydajnościowy (12 rdzeni CPU): o 228% szybszy od Portkey i o 859% szybszy od LiteLLM.
- Koszt: 100 USD za model miesięcznie (limit do 5 modeli w planie Plus).
- Kiedy stosować: duża skala (ruch >1000 RPS) oraz infrastruktura oparta już na Kong Gateway.

### Bifrost (Maxim AI)

- Skupia się na automatycznym ponawianiu zapytań ze spersonalizowanymi regułami opóźnień.
- Posiada gotowy scenariusz automatycznego przełączania z OpenAI (w razie błędu 429) do Anthropic.
- Nowe, w pełni komercyjne rozwiązanie.

### Cloudflare AI Gateway / Vercel AI Gateway

- W pełni zarządzane (SaaS), bezobsługowe rozwiązania. Oferują podstawowe funkcje monitorowania i retries.
- Kiedy stosować: projekty oparte na architekturze Serverless (np. Next.js, Cloudflare Workers).
- Ograniczenia: mniejsze możliwości w zakresie filtrów bezpieczeństwa (guardrails) i zaawansowanego rate limitingu w porównaniu z Kongiem czy Portkey.

### Własna infrastruktura (Self-hosted) vs Chmura zarządzana

Lokalizacja danych (data residency) jest tu kluczowym kryterium wyboru. Sektor medyczny i finansowy najczęściej wymaga hostowania bramy u siebie (LiteLLM, Portkey OSS lub Kong). Aplikacje konsumenckie chętnie wybierają rozwiązania w pełni zarządzane (Cloudflare AI Gateway) lub platformy SaaS (zarządzany Portkey).

### Narzut opóźnień (Latency Budget)

- **LiteLLM**: narzut 5-15 ms na zapytanie.
- **Portkey**: narzut 20-40 ms na zapytanie (ze względu na filtry guardrails).
- **Kong AI Gateway**: narzut 3-8 ms na zapytanie.
- **Cloudflare/Vercel**: narzut 1-3 ms (przetwarzanie na brzegu sieci – edge serving).

Opóźnienie generowane przez bramę bezpośrednio wydłuża wskaźnik TTFT (Time to First Token). Jeśli Twoje SLA wymaga TTFT P99 < 100 ms, jedynym wyborem jest Kong lub Cloudflare. Przy wymaganiach P99 < 500 ms sprawdzi się każde z tych rozwiązań.

### Metody limitowania zapytań (Rate Limiting)

Algorytm kubełkowego (token bucket) sprawdza się przy średnim natężeniu ruchu. Jednak zaawansowane systemy multi-tenant wymagają algorytmu przesuwanego okna (sliding window) z obsługą nagłych skoków (bursts). LiteLLM opiera się na algorytmie kubełkowym, Kong wdraża przesuwane okno, a Portkey oferuje zaawansowane reguły wielopoziomowe.

### Ekosystem: Brama + Obserwowalność + Routing

Zagadnienia monitorowania (faza 17 · 13), routingu (faza 17 · 16) oraz bram AI (faza 17 · 19) tworzą jedną, spójną warstwę infrastruktury produkcyjnej. Możesz wybrać jedno uniwersalne narzędzie lub połączyć dedykowane systemy: standardem w 2026 roku jest łączenie Helicone (monitorowanie) lub Portkey (bezpieczeństwo promptów) z Kongiem (wysoka wydajność).

### Kluczowe statystyki do zapamiętania

- LiteLLM: spadek stabilności przy ~2000 RPS na instancji z 8 GB RAM.
- Portkey: narzut opóźnień 20-40 ms; licencja Apache 2.0 od marca 2026 r.
- Kong AI Gateway: o 228% szybszy od Portkey i o 859% szybszy od LiteLLM.
- Cennik Kong: 100 USD/model/miesiąc (do 5 modeli w planie Plus).
- Cloudflare/Vercel: znikomy narzut 1-3 ms dzięki sieci edge.

## Praktyczne zastosowanie

Skrypt `code/main.py` symuluje mechanizmy routingu i fallbacku w bramie AI przy obsłudze 3 różnych dostawców podczas symulowanych błędów 429/5xx. Raportuje opóźnienia, statystyki powtórzeń i skuteczność przekierowań awaryjnych.

## Zadanie wdrożeniowe

W ramach tej lekcji przygotowano plik `outputs/skill-gateway-picker.md`. Narzędzie to analizuje skalę ruchu, wymagania operacyjne, zgodność regulacyjną i budżet opóźnień, ułatwiając wybór optymalnej bramy AI.

## Ćwiczenia

1. Uruchom `code/main.py`. Skonfiguruj ścieżkę awaryjną (fallback): OpenAI → Anthropic → Model własny. Jaka będzie skuteczność obsługi zapytań, jeśli bazowy współczynnik błędów każdego dostawcy wynosi 5%?
2. Twoje SLA wymaga TTFT P99 < 200 ms (przy bazowym opóźnieniu samej inferencji wynoszącym 300 ms). Które bramy AI zmieszczą się w budżecie opóźnień?
3. Klient z sektora medycznego wymaga wdrożenia w swojej infrastrukturze (self-hosted), anonimizacji danych osobowych (PII) oraz audytowalności logów. Wybierz między Portkey OSS a Kong AI Gateway.
4. Porównaj LiteLLM z Kong AI Gateway: przy jakiej skali zapytań (RPS) zespół powinien bezwzględnie przeprowadzić migrację na Konga?
5. Zaprojektuj reguły limitów zapytań (rate limits) dla platformy SaaS: dla kont darmowych (Free), próbnych (Trial) oraz płatnych (Premium). Wybierz odpowiedni algorytm (kubełkowy lub przesuwane okno) i uzasadnij wybór.

## Słownik pojęć

| Termin | Popularne określenie | Rzeczywiste znaczenie |
|------|----------------|--------------------------------------|
| AI Gateway | „brama API dla LLM” | Warstwa pośrednicząca w komunikacji między aplikacją a dostawcami modeli |
| LiteLLM | „ten na licencji MIT” | Popularna bramka open-source w Pythonie, wspierająca ponad 100 dostawców |
| Portkey | „strażnik bezpieczeństwa” | Bramka skupiona na warstwie ochrony danych, logowaniu audytowym (na licencji Apache 2.0) |
| Kong AI Gateway | „Demon szybkości” | Wysokowydajny moduł bramy zbudowany na silniku Kong Gateway |
| Bifrost | „bramka Bifrost” | Bramka dedykowana do zaawansowanych mechanizmów retries i fallbacków |
| Cloudflare AI Gateway | „bramka serverless” | Bezobsługowa bramka AI działająca na infrastrukturze edge |
| Anonimizacja PII | „czyszczenie promptów” | Automatyczne wycinanie lub maskowanie danych osobowych przed wysłaniem ich do zewnętrznego API |
| Wykrywanie Jailbreaków | „blokowanie wstrzykiwania promptów” | Filtrowanie wejścia użytkownika pod kątem prób przejęcia kontroli nad modelem |
| Log Audytowy | „audit trail” | Niezmienny, chroniony zapis każdego zapytania i odpowiedzi LLM dla celów zgodności |
| Kubełek tokenów (Token Bucket) | „limit kubełkowy” | Prosty algorytm limitowania zapytań na podstawie dostępnych w puli żetonów |
| Przesuwane okno (Sliding Window) | „precyzyjny rate limit” | Zaawansowany i sprawiedliwy algorytm limitowania ruchu w ruchomym oknie czasowym |

## Materiały uzupełniające

- [Kong AI Gateway Benchmark](https://konghq.com/blog/engineering/ai-gateway-benchmark-kong-ai-gateway-portkey-litellm)
- [TrueFoundry – AI Gateways Comparison 2026](https://www.truefoundry.com/blog/a-definitive-guide-to-ai-gateways-in-2026-competitive-landscape-comparison)
- [Techsy – Best LLM Gateway Tools 2026](https://techsy.io/en/blog/best-llm-gateway-tools)
- [LiteLLM GitHub](https://github.com/BerriAI/litellm)
- [Portkey GitHub](https://github.com/Portkey-AI/gateway)
- [Kong AI Gateway Documentation](https://docs.konghq.com/gateway/latest/ai-gateway/)
