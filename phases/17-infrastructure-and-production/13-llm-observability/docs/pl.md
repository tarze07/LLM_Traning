# Wybór stosu obserwowalności LLM

> Rynek obserwowalności w 2026 r. dzieli się na dwie kategorie. Platformy programistyczne (LangSmith, Langfuse, Comet Opik) łączą monitorowanie z ewaluacją, szybkim zarządzaniem, powtórkami sesji. Narzędzia bramowe/instrumentacyjne (Helicone, SigNoz, OpenLLMetry, Phoenix) skupiają się na telemetrii. Langfuse to rdzeń na licencji MIT z silnym balansem OSS (50 tys. zdarzeń/miesiąc bezpłatna chmura). Phoenix jest natywny dla OpenTelemetry w ramach Elastic License 2.0 — doskonale nadaje się do wizualizacji dryfu/RAG, a nie do trwałego zaplecza produkcyjnego. Arize AX wykorzystuje integrację z zerową kopią Iceberg/Parquet, twierdząc, że jest 100 razy tańsza niż obserwowalność monolityczna. LangSmith prowadzi dla LangChain/LangGraph, 39 USD/użytkownika/mies., własny host tylko w przedsiębiorstwie. Helicone działa w oparciu o serwer proxy z konfiguracją trwającą 15–30 minut, 100 tys. wymagań/mies., ale mniejszą głębokością śladów agenta. Wspólny schemat produkcji: Gateway (Helicone/Portkey) + platforma ewaluacyjna (Phoenix/TruLens) sklejona metodą OpenTelemetry.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulator próbkowania śledzenia zabawek)
**Wymagania wstępne:** Faza 17 · 08 (metryki wnioskowania), faza 14 (inżynieria agenta)
**Czas:** ~60 minut

## Cele nauczania

- Odróżnij platformy programistyczne (w pakiecie: evals + podpowiedzi + sesje) od narzędzi bramowych/telemetrycznych (tylko ślady + metryki).
- Przyporządkuj sześć głównych narzędzi (Langfuse, LangSmith, Phoenix, Arize AX, Helicone, Opik) do ich licencji, cen i przypadków wykorzystania najlepszych punktów.
- Wyjaśnij wzór kleju OpenTelemetry, który pozwala połączyć narzędzie bramy z oddzielną platformą eval.
- Podaj nazwę wyróżnika kosztów w roku 2026 (podejście Arize AX polegające na zerowej kopiowaniu a przetwarzanie monolityczne) i podaj przybliżony mnożnik 100-krotny.

## Problem

Dostarczyłeś funkcję LLM. To działa. Nie masz wglądu w awarie monitów, pętle narzędzi, regresje opóźnień, skoki kosztów ani współczynnik trafień w pamięci podręcznej podpowiedzi. Wpisz w Google „obserwowalność LLM” i uzyskaj osiem narzędzi, z których wszystkie twierdzą, że rozwiązują ten sam problem w trzech różnych przedziałach cenowych.

Nie rozwiązują tego samego problemu. LangSmith odpowiada: „Dlaczego ten przebieg LangGraph się nie powiódł?” Firma Phoenix odpowiada na pytanie: „Czy mój rurociąg RAG dryfuje?” Helicone odpowiada „która aplikacja spala tokeny?” Langfuse odpowiada: „Czy mogę sam zorganizować całość?” Różne narzędzia, różni odbiorcy.

Wybór obejmuje cztery osie: stos (LangChain? surowy SDK? wielu dostawców?), tolerancja licencji (tylko MIT? Elastic OK? komercyjna kara?), budżet (bezpłatna warstwa? $100/mo? $1000/mies.?) i własny host (koniecznie? miło mieć? nigdy?).

## Koncepcja

### Dwie kategorie

**Platformy programistyczne** łączą obserwowalność z ewaluacją, szybkim zarządzaniem, wersjonowaniem zbioru danych, odtwarzaniem sesji. Przeprowadzasz eksperymenty, sprawdzasz, który monit zadziałał, regresję zbioru danych nowy monit w porównaniu ze starymi zwycięzcami. LangSmith, Langfuse, Kometa Opik.

**Narzędzia bramowe/telemetryczne** wywołania wnioskowania o instrumentach — monit, odpowiedź, tokeny, opóźnienie, model, koszt. Helicone, SigNoz, OpenLLMetry, Phoenix. Minimalistyczny. Można połączyć z oddzielnym narzędziem ewaluacyjnym za pośrednictwem OpenTelemetry.

### Langfuse — saldo OSS

- licencja Core Apache/MIT; własny host za pośrednictwem Dockera.
- Poziom bezpłatny w chmurze: 50 tys. zdarzeń/miesiąc. Płatne: 29 USD miesięcznie dla zespołu.
- Ewaluacje, szybkie zarządzanie, ślady, zbiory danych. Rozsądne pokrycie wszystkich czterech funkcji platformy deweloperskiej.
- Idealny punkt: chcesz funkcji klasy LangSmith, ale musisz samodzielnie hostować lub pozostać na licencji OSS.

### Phoenix (Arize) — przede wszystkim telemetria, natywnie OpenTelemetry

- Licencja Elastyczna 2.0; samodzielne hostowanie jest trywialne.
- Doskonała do wizualizacji RAG i dryfu. Wykresy rozproszone z przestrzenią do osadzania dostarczane jako pierwszorzędne.
— Nie został zaprojektowany jako trwałe zaplecze produkcyjne — przede wszystkim możliwość obserwacji w czasie programowania.
- Najlepszy punkt: rozwój rurociągu RAG, debugowanie dryfu, parowanie z oddzielną bramą do produkcji.

### Arize AX — gra skali

- Komercyjne. Integracja z jeziorem danych bez kopiowania za pośrednictwem Iceberg/Parquet.
- Twierdzenia ~100 razy tańsze niż obserwowalność monolityczna (klasa Datadog) na dużą skalę. Matematyka: przechowujesz ślady na swoim własnym parkiecie na S3; Arize czyta bezpośrednio.
- Optymalny punkt: >10 milionów śladów dziennie, istniejące jezioro danych, potrzebne pulpity nawigacyjne specyficzne dla LLM bez cen Datadog.

### LangSmith — najpierw LangChain/LangGraph

- Komercyjne, 39 USD/użytkownika/miesiąc. Self-host tylko w Enterprise.
- Najlepsze w swojej klasie dla stosów LangChain i LangGraph. Jeśli nie należysz do żadnego z nich, jest to mniej przekonujące.
- Najlepszy punkt: zespół zaangażowany w LangChain, gotowy zapłacić.

### Helicone — minimalna wartość oparta na proxy

- 15-30 minut konfiguracji poprzez zamianę `OPENAI_API_BASE` na serwer proxy Helicone.
- licencja MIT; 100 tys. wymagań/mies. za darmo, płatne 20 USD/mies.+.
- Obejmuje przełączanie awaryjne, buforowanie, limity szybkości - działa również jako brama.
- Mniejsza głębokość śladów agenta/wieloetapowych.
- Idealne miejsce: szybki start, aplikacja z jednym stosem, wymagana bramka + obserwowalność w jednym.

### Opik (Comet) — platforma deweloperska OSS

- Apache 2.0, w pełni OSS.
- Podobny zestaw funkcji do Langfuse z dziedzictwem Comet.
- Dobry punkt: zespoły ML już pracujące w Comet, chcą, aby LLM było obserwowalne w tym samym panelu.

### SigNoz — pierwszy pełny APM OpenTelemetry

- Apache 2.0. Obsługuje ogólne APM i LLM za pośrednictwem OpenTelemetry.
- Sweet spot: ujednolicona obserwowalność usług i połączeń LLM.

### Klej: konwencje semantyczne OpenTelemetry + GenAI

OpenTelemetry opublikował konwencje semantyczne GenAI pod koniec 2025 r. (`gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`). Narzędzia korzystające z Otel mogą ze sobą współpracować. Pojawiający się model produkcji:

1. Emituj Otel z konwencjami GenAI z każdego wywołania LLM.
2. Trasa do bramy (Helicone / Świstoklik) na co dzień.
3. Podwójny statek na platformę ewaluacyjną (Phoenix / Langfuse) dla regresji.
4. Archiwum w Data Lake (Iceberg) do długoterminowej analizy za pośrednictwem Arize AX lub DuckDB.

### Pułapka: oprzyrządowanie na niewłaściwej warstwie

Instrumentacja wewnątrz struktury agenta (np. dodanie śladów LangSmitha) łączy Cię z tą strukturą. Instrumentacja w warstwie HTTP/OpenAI-SDK (za pośrednictwem OpenLLMetry lub bramy) jest przenośna.

### Próbkowanie — nie możesz zachować wszystkiego

Przy > 1 mln żądań dziennie zachowanie pełnego śledzenia kosztuje więcej niż połączenia LLM. Próbka według reguł: 100% błędów, 100% wysokich kosztów, 5% sukcesu. Zawsze przechowuj agregaty; zachować surowość dla długiego ogona.

### Liczby, które powinieneś zapamiętać

- Bezpłatna chmura Langfuse: 50 tys. zdarzeń/miesiąc.
- LangSmith: 39 USD/użytkownika/miesiąc.
- Bez helikoptera: zapotrzebowanie 100 tys./miesiąc.
- Twierdzenie Arize AX: ~100x tańsze niż monolityczne na dużą skalę.
- Konwencje OpenTelemetry GenAI: wysyłka 2025, 2026 powszechnie przyjęte.

## Użyj tego

`code/main.py` symuluje 1-milionowy dzień śledzenia dla różnych strategii przechowywania (100% pozyskiwanie, próbkowanie, próbkowanie + błędy). Raportuje koszty przechowywania i straty w ramach każdego z nich.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-observability-stack.md`. Biorąc pod uwagę stos, skalę, budżet, stan licencji, wybiera narzędzie(a).

## Ćwiczenia

1. Twój zespół w LangChain potrzebuje możliwości obserwowania na własnym serwerze OSS. Wybierz Langfuse lub Opik i uzasadnij.
2. Przy 5 milionach śladów/dzień z Datadog kwotowaniem 150 000 USD/miesiąc oblicz próg rentowności dla Arize AX.
3. Zaprojektuj zestaw atrybutów OpenTelemetry GenAI, który wytyczne Twojej organizacji powinny obowiązywać przy każdym wywołaniu LLM.
4. Uzasadnij, czy sam Phoenix wystarczy do produkcji. Kiedy to nie wystarczy?
5. Helicone to narzut proxy 20 ms. Czy przy P99 TTFT 300 ms jest to akceptowalne? A co jeśli SLA wynosi 100 ms?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| OpenLLMetry | „OTel dla LLM” | Instrumentacja OpenTelemetry typu open source dla LLM |
| Konwencje GenAI | „Atrybuty Otel” | Standardowe nazwy atrybutów Otel dla wywołań LLM |
| LangSmitha | „Obserwowalność LangChaina” | Platforma komercyjna połączona z ekosystemem LangChain |
| Langfuse | „OSS LangSmith” | MIT OSS z podobnym zestawem funkcji |
| Feniks | „Narzędzie programistyczne Arize” | Platforma deweloperska/ewaluacyjna natywna dla OpenTelemetry |
| Arize AX | „obserwowalność skali” | Komercyjna kopia zerowa Widoczność góry lodowej/parkietu |
| Helikon | „obserwowalność proxy” | Serwer proxy HTTP zbierający dane telemetryczne LLM + funkcje bramy |
| Opik | „Kometa LLM” | Platforma deweloperska Apache 2.0 OSS firmy Comet |
| Powtórka sesji | „ponowne uruchomienie śledzenia” | Odtwórz pełną sesję agenta z wywołaniami narzędzi |
| Ewa | „test offline” | Uruchamianie modelu/podpowiedzi kandydata na oznaczonym zbiorze danych |

## Dalsze czytanie

- [SigNoz — najlepsze narzędzia do obserwacji LLM 2026](https://signoz.io/comparisons/llm-observability-tools/)
- [Langfuse — analiza alternatywy Arize AX](https://langfuse.com/faq/all/best-phoenix-arize-alternatives)
- [PremAI — konfiguracja Langfuse, LangSmith, Helicone, Phoenix](https://blog.premai.io/llm-observability-setting-up-langfuse-langsmith-helicone-phoenix/)
- [Konwencje semantyczne OpenTelemetry GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
– [Dokumentacja Arize Phoenix](https://docs.arize.com/phoenix)
- [Dokumentacja Helicone](https://docs.helicone.ai/)