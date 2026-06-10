# Bramy AI — LiteLLM, świstoklik, Kong AI Gateway, Bifrost

> Brama znajduje się pomiędzy Twoimi aplikacjami i dostawcami modeli. Podstawowe funkcje to routing dostawcy, powrót do sieci, ponowne próby, ograniczanie szybkości, tajne referencje, obserwowalność, poręcze. Podział rynku w 2026 r.: **LiteLLM** to MIT OSS z ponad 100 dostawcami, kompatybilny z OpenAI, ale działa około 2000 RPS (pamięć 8 GB, kaskadowe awarie w opublikowanych testach); najlepsze dla Pythona, <500 RPS, tworzenie/prototypowanie. **Portkey** jest umiejscowiony na płaszczyźnie kontrolnej (poręcze ochronne, redagowanie informacji umożliwiających identyfikację, wykrywanie jailbreak, ścieżki audytu), wersja Apache 2.0 typu open source z marca 2026 r., obciążenie związane z opóźnieniem 20–40 ms, $49/mo production tier. **Kong AI Gateway** built on Kong Gateway — Kong's own benchmark on same 12 CPUs: 228% faster than Portkey, 859% faster than LiteLLM; $cena 100/model/miesiąc (maks. 5 w warstwie Plus); odpowiedni dla przedsiębiorstw, jeśli korzystasz już z Konga. **Bifrost** (Maxim AI) — automatyczne ponowne próby z konfigurowalnym wycofywaniem, powrót do Anthropic na OpenAI 429. **Cloudflare / Vercel AI Gateways** — zarządzane, zero operacji, podstawowe ponawianie. Miejsce przechowywania danych wpływa na decyzję o własnym gospodarzu; Portkey i Kong siedzą pośrodku z OSS + opcjonalnie zarządzanym.

**Typ:** Ucz się
**Języki:** Python (stdlib, zabawkowy symulator routingu bramy)
**Wymagania wstępne:** Faza 17 · 01 (zarządzane platformy LLM), faza 17 · 16 (trasowanie modelu)
**Czas:** ~60 minut

## Cele nauczania

- Wymień sześć podstawowych funkcji bramy (routing, rezerwa, ponowne próby, limity szybkości, tajemnice, obserwowalność, poręcze).
- Zmapuj cztery bramy 2026 (LiteLLM, Portkey, Kong AI, Bifrost), aby skalować sufity i przypadki użycia.
- Przytocz test porównawczy Kong (228% w porównaniu z Portkey, 859% w porównaniu z LiteLLM) i wyjaśnij, dlaczego ma to znaczenie w przypadku > 500 RPS.
- Wybierz hosting własny lub zarządzany, biorąc pod uwagę miejsce przechowywania danych i budżet operacyjny.

## Problem

Twój produkt nazywa się OpenAI, Anthropic i hostowaną przez siebie Lamą. Każdy dostawca ma inny zestaw SDK, model błędów, limit szybkości i schemat uwierzytelniania. Potrzebujesz pracy awaryjnej (jeśli OpenAI 429, wypróbuj Anthropic), pojedynczego magazynu danych uwierzytelniających, ujednoliconej obserwowalności i limitów szybkości na dzierżawcę.

Wynalezienie tego na nowo w warstwie aplikacji łączy każdą usługę z każdym dostawcą. Warstwa bramy konsoliduje go w jeden proces z jednym interfejsem API (zwykle zgodnym z OpenAI), który jest udostępniany dostawcom.

## Koncepcja

### Sześć podstawowych funkcji

1. **Routing dostawców** — OpenAI, Anthropic, Gemini, self-hosting itp. za jednym API.
2. **Powrót** — w przypadku połączenia 429, 5xx lub awarii jakości spróbuj ponownie gdzie indziej.
3. **Ponowne próby** — wykładniczy backoff, ograniczone próby.
4. **Limity stawek** — na najemcę, na klucz, na model.
5. **Tajne referencje** — pobieraj dane uwierzytelniające ze skarbca w czasie wykonywania (nigdy w aplikacji).
6. **Obserwowalność** — atrybuty Otel + GenAI (faza 17 · 13) + przypisanie kosztów.
7. **Poręcze** — redakcja danych osobowych, wykrywanie jailbreak, filtry dozwolonych tematów.

### LiteLLM — MIT OSS, Python

- Ponad 100 dostawców, kompatybilny z OpenAI, konfiguracja routera, rezerwa, podstawowa obserwowalność.
- W benchmarku Konga osiąga około 2000 RPS; 8 GB pamięci, kaskadowe awarie przy ciągłym obciążeniu.
- Najlepsze dopasowanie: aplikacja w języku Python, <500 RPS, bramy programistyczne/staging, routing eksperymentalny.
- Koszt: 0 USD za OSS; istnieje poziom wolny od chmury.

### Świstoklik — pozycjonowanie płaszczyzny sterującej

— Apache 2.0 OSS, stan na marzec 2026 r. Guardrails, redakcja danych osobowych, wykrywanie jailbreak, ścieżki audytu.
— Narzut związany z opóźnieniem wynoszącym 20–40 ms na żądanie.
- 49 USD miesięcznie za warstwę produkcyjną z utrzymaniem + SLA.
- Najlepsze dopasowanie: regulowane branże wymagające poręczy + pakiet obserwowalności.

### Kong AI Gateway — gra skali

- Zbudowany na Kong Gateway (dojrzały produkt bramy API, lua + OpenResty).
- Własny test Konga na odpowiedniku z 12 procesorami: 228% szybszy niż Portkey, 859% szybszy niż LiteLLM.
- Ceny: 100 USD/model/miesiąc, maksymalnie 5 na poziomie Plus.
- Najlepsze dopasowanie: już w Kongu; >1000 obr./s; chętny do licencjonowania.

### Bifrost (Maxim AI)

- Automatyczne ponowne próby z konfigurowalnym wycofywaniem.
- Powrót do Anthropic na OpenAI 429 to przepis kanoniczny.
- Nowszy uczestnik; handlowy.

### Brama Cloudflare AI / Brama Vercel AI

- Zarządzane, zero operacji. Podstawowe ponawianie prób i obserwowalność.
- Najlepsze dopasowanie: aplikacje JavaScript obsługujące brzegi w Cloudflare/Vercel.
- Ograniczone w porównaniu do Kong/świstoklika w zakresie poręczy i limitów stawek.

### Własny hosting a zarządzany

Miejsce zamieszkania danych jest funkcją wymuszającą. Domyślny własny host w zakresie opieki zdrowotnej i finansów (LiteLLM, Portkey OSS lub Kong). Produkty konsumenckie zarządzane domyślnie (Cloudflare AI Gateway) lub warstwy środkowej (zarządzane przez Portkey). Hybrydowy: hostowany samodzielnie przez regulowanego najemcę, zarządzany przez innych.

### Budżet opóźnień

- LiteLLM: typowy narzut 5-15 ms.
- Świstoklik: 20-40 ms narzutu.
- Kong: 3-8 ms nad głową.
- Cloudflare/Vercel: 1-3 ms narzutu (przewaga krawędzi).

Opóźnienie bramy bezpośrednio zwiększa wartość TTFT. Dla TTFT P99 < 100 ms SLA, Kong lub Cloudflare. Dla P99 < 500 ms dowolne.

### Semantyka limitów szybkości ma znaczenie

Prosty wiadro tokenów działa na umiarkowaną skalę. Obsługa wielu dzierżawców wymaga przesuwanego okna + dodatku na serię + warstwowania na dzierżawcę. LiteLLM dostarcza wiadro tokenów; Przesuwane okno na statkach Kong; Statki świstoklik wielopoziomowe.

### Brama + obserwowalność + tworzenie tras

Faza 17 · 13 (obserwowalność) + 16 (trasowanie modelu) + 19 (bramy) to ta sama warstwa produkcyjna. Wybierz jedno narzędzie, które obsługuje wszystkie trzy lub ostrożnie je połącz: większość wdrożeń na rok 2026 łączy Helicone (obserwowalność) lub świstoklik (poręcze) ​​z Kong (skala) w celu podziału ról.

### Liczby, które powinieneś zapamiętać

- LiteLLM: przerwy przy ~2000 RPS, 8 GB pamięci.
- Świstoklik: 20-40 ms narzutu; Apache 2.0 od marca 2026 r.
- Kong: 228% szybszy niż Portkey, 859% szybszy niż LiteLLM.
- Ceny Konga: 100 USD/model/miesiąc, maksymalnie 5 na poziomie Plus.
- Cloudflare/Vercel: 1-3 ms nad głową na krawędzi.

## Użyj tego

`code/main.py` symuluje routing bramy z rezerwowym połączeniem u 3 dostawców w ramach zastrzyku 429/5xx. Raportuje opóźnienia, częstotliwość ponownych prób i częstotliwość trafień awaryjnych.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-gateway-picker.md`. Biorąc pod uwagę skalę, stan operacji, zgodność, budżet opóźnień, wybiera bramę.

## Ćwiczenia

1. Uruchom `code/main.py`. Skonfiguruj rezerwę z OpenAI → Anthropic → hostowane samodzielnie. Jaki jest oczekiwany współczynnik trafień przy wskaźniku błędów dostawcy wynoszącym 5%?
2. Twoja umowa SLA wynosi TTFT P99 < 200 ms przy linii bazowej 300 ms. Które bramy mieszczą się w budżecie?
3. Klient opieki zdrowotnej wymaga samodzielnego hostowania + redakcji danych osobowych + audytu. Wybierz Portkey OSS lub Kong.
4. Porównaj LiteLLM z Kongiem: przy jakim pułapie RPS zespół powinien migrować?
5. Zaprojektuj politykę limitów stawek dla SaaS z wieloma dzierżawcami: warstwa bezpłatna, warstwa próbna, warstwa płatna. Wiadro na żetony czy przesuwane okno?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Brama | „Broker API” | Proces odbywa się pomiędzy aplikacjami i dostawcami |
| LiteLLM | „ten z MIT” | Python OSS, ponad 100 dostawców, przerwy przy 2 tys. RPS |
| Świstoklik | „brama poręczy” | Płaszczyzna sterowania + obserwowalność, Apache 2.0 |
| Brama Kong AI | „pierwsza skala” | Zbudowany na bazie Kong Gateway, lider wzorców |
| Bifrost | „Brama Maxima” | Ponowne próby + Antropiczny przepis awaryjny |
| Brama Cloudflare AI | „zarządzane brzegowo” | Brama zarządzana wdrożona na krawędzi, zero operacji |
| Redakcja PII | „szorowanie danych” | Maska Regex + NER przed wysłaniem do modelki |
| Wykrywanie jailbreaka | „szybka osłona wtrysku” | Klasyfikator na podstawie danych wejściowych użytkownika |
| Ścieżka audytu | „dziennik regulowany” | Niezmienny zapis każdego połączenia LLM |
| Wiadro na żetony | „prosty limit stawki” | Ogranicznik dawki oparty na uzupełnieniu |
| Okno przesuwne | „dokładny limit stawki” | Ogranicznik szybkości w oknie czasowym; lepsza sprawiedliwość |

## Dalsze czytanie

— [Temat porównawczy bramy AI Kongh](https://konghq.com/blog/engineering/ai-gateway-benchmark-kong-ai-gateway-portkey-litellm)
— [TrueFoundry — porównanie AI Gateways 2026](https://www.truefoundry.com/blog/a-definitive-guide-to-ai-gateways-in-2026-competitive-landscape-comparison)
- [Techsy — najlepsze narzędzia LLM Gateway 2026](https://techsy.io/en/blog/best-llm-gateway-tools)
- [LiteLLM GitHub](https://github.com/BerriAI/litellm)
- [Portkey GitHub] (https://github.com/Portkey-AI/gateway)
– [Dokumentacja Kong AI Gateway] (https://docs.konghq.com/gateway/latest/ai-gateway/)