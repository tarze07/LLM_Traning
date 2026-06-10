# Wybór stosu obserwowalności LLM

> Rynek narzędzi do monitorowania i obserwowalności (observability) systemów LLM w 2026 r. dzieli się na dwie główne kategorie. Platformy deweloperskie (np. LangSmith, Langfuse, Comet Opik) łączą funkcje monitorowania z ewaluacją modeli (evals), zarządzaniem promptami oraz odtwarzaniem sesji użytkowników. Z kolei bramy (gateways) i narzędzia instrumentacyjne (np. Helicone, SigNoz, OpenLLMetry, Phoenix) skupiają się na zbieraniu i analizie surowych danych telemetrycznych. Langfuse to otwarty projekt (licencja MIT) stanowiący doskonały kompromis w duchu open source, oferujący bezpłatny pakiet chmurowy do 50 tys. zdarzeń miesięcznie. Phoenix wspiera natywnie standard OpenTelemetry (licencja Elastic License 2.0) – świetnie sprawdza się przy wizualizacji dryfu (driftu) modeli oraz potoków RAG, ale nie jest projektowany jako trwałe zaplecze (backend) produkcyjne. Arize AX oferuje architekturę bezkopiową (zero-copy data lake integration) z formatami Iceberg/Parquet, co według deklaracji producenta zapewnia nawet 100-krotnie niższe koszty w porównaniu z monolitycznymi systemami obserwowalności. LangSmith jest wiodącym rozwiązaniem dla ekosystemów LangChain i LangGraph, z ceną 39 USD za użytkownika miesięcznie (opcja self-hosting dostępna jest wyłącznie w pakiecie Enterprise). Helicone działa jako serwer proxy (konfiguracja zajmuje zaledwie 15–30 minut), oferując darmowy limit do 100 tys. żądań miesięcznie, lecz zapewnia mniejszą szczegółowość śledzenia zachowań agentowych (śladów wieloetapowych). Typowy schemat produkcyjny: brama (np. Helicone lub Portkey) połączona z platformą ewaluacyjną (np. Phoenix lub TruLens) za pośrednictwem standardu OpenTelemetry.

**Typ:** Ucz się
**Języki:** Python (stdlib, uproszczona symulacja próbkowania śladów telemetrycznych)
**Wymagania wstępne:** Faza 17 · 08 (Metryki wnioskowania), Faza 14 (Inżynieria systemów agentowych)
**Czas:** ~60 minut

## Cele nauczania

- Odróżnij platformy deweloperskie (oferujące zintegrowaną ewaluację, zarządzanie promptami i sesje) od narzędzi bramowych i telemetrycznych (skupiających się na logowaniu śladów i metrykach).
- Przypisz sześć głównych narzędzi (Langfuse, LangSmith, Phoenix, Arize AX, Helicone, Opik) do ich licencji, modeli cennikowych oraz optymalnych scenariuszy użycia (sweet spot).
- Wyjaśnij wzorzec integracji za pomocą standardu OpenTelemetry, który pozwala na łączenie bramy sieciowej z osobną platformą ewaluacyjną.
- Zdefiniuj czynnik decydujący o kosztach w 2026 r. (bezkopiowa architektura Arize AX w opozycji do monolitycznego przetwarzania danych) i wyjaśnij źródło szacowanego 100-krotnego zysku finansowego.

## Problem

Wdrożyłeś funkcjonalność opartą na LLM. Kod działa prawidłowo, jednak nie posiadasz żadnego wglądu w błędy generowane przez prompty, pętle wykonywane przez agenty, regresje opóźnień, skoki kosztów czy współczynnik trafień cache dla promptów. Wpisując w wyszukiwarkę hasło „obserwowalność LLM”, otrzymujesz zestaw ośmiu narzędzi, z których każde deklaruje rozwiązanie Twoich problemów w zupełnie innych przedziałach cenowych.

Narzędzia te nie rozwiązują tych samych problemów. LangSmith odpowiada na pytanie: „Dlaczego ten przebieg grafu LangGraph zakończył się błędem?”. Phoenix wyjaśnia: „Czy mój potok RAG doświadcza dryfu danych (data drift)?”. Helicone informuje: „Która aplikacja generuje największe koszty tokenów?”. Z kolei Langfuse pozwala na kompleksowe zarządzanie całym tym procesem we własnej infrastrukturze. Różne narzędzia adresują potrzeby różnych odbiorców.

Proces wyboru narzędzia powinien być prowadzony w oparciu o cztery kryteria: stos technologiczny (LangChain, surowy SDK czy środowisko wielodostawcze), wymagania licencyjne (wyłącznie MIT, akceptacja licencji Elastic czy komercyjne opłaty), budżet (pakiet bezpłatny, do 100 USD/miesiąc czy powyżej 1000 USD/miesiąc) oraz wymagania dotyczące hostingu (konieczność wdrożenia lokalnego/self-hosted).

## Koncepcja

### Dwie kategorie narzędzi

**Platformy deweloperskie** łączą obserwowalność z ewaluacją modeli (evals), zarządzaniem promptami i ich wersjonowaniem, zarządzaniem zbiorami danych testowych oraz odtwarzaniem sesji użytkowników. Pozwalają na przeprowadzanie eksperymentów, weryfikację skuteczności poszczególnych promptów oraz badanie regresji przy porównywaniu nowych wersji promptów z wersjami dotychczasowymi. Przykłady: LangSmith, Langfuse, Comet Opik.

**Narzędzia bramowe i telemetryczne (gateways)** służą do rejestrowania parametrów zapytań do modeli (prompt, odpowiedź, liczba tokenów, opóźnienie, wersja modelu, koszt). Przykłady: Helicone, SigNoz, OpenLLMetry, Phoenix. Są to rozwiązania minimalistyczne, które można zintegrować z zewnętrznymi systemami ewaluacyjnymi za pośrednictwem standardu OpenTelemetry.

### Langfuse — Kompromis w duchu Open Source

- Licencja Core Apache/MIT; możliwość łatwego wdrożenia we własnej infrastrukturze za pomocą Docker.
- Darmowy limit w chmurze (Cloud): 50 tys. zdarzeń miesięcznie. Pakiet dla zespołów: od 29 USD/miesiąc.
- Ewaluacje, wersjonowanie promptów, rejestracja śladów, zarządzanie zbiorami danych. Oferuje zbalansowane pokrycie wszystkich kluczowych obszarów platform deweloperskich.
- Sweet spot: Zespół poszukuje funkcjonalności zbliżonych do LangSmith, ale z wymaganiem własnego hostingu lub oparcia na licencji open source (OSS).

### Phoenix (Arize) — Telemetria natywna dla OpenTelemetry

- Licencja Elastic License 2.0; bardzo prosta konfiguracja lokalna.
- Narzędzie zoptymalizowane pod kątem wizualizacji potoków RAG oraz analizy dryfu danych. Udostępnia zaawansowane wykresy przestrzeni osadzeń (embeddings) jako standardową funkcjonalność.
- Projektowany przede wszystkim jako narzędzie deweloperskie, a nie trwałe zaplecze (backend) do przechowywania logów produkcyjnych.
- Sweet spot: Analiza i rozwój potoków RAG, debugowanie dryfu modeli, integracja z zewnętrzną bramą produkcyjną.

### Arize AX — Narzędzie dla dużej skali

- Rozwiązanie w pełni komercyjne. Oferuje integrację z jeziorami danych bez kopiowania zasobów (zero-copy data lake integration) z wykorzystaniem formatów Iceberg/Parquet.
- Gwarantuje ok. 100-krotną redukcję kosztów w porównaniu z monolitycznymi systemami monitoringu (klasy Datadog) przy dużych wolumenach danych. Zasada działania: logi telemetryczne są zapisywane bezpośrednio w formacie Parquet w zasobniku S3 klienta, z którego Arize AX bezpośrednio odczytuje dane.
- Sweet spot: Wolumen ruchu powyżej 10 milionów zapytań dziennie, posiadanie wdrożonego jeziora danych, zapotrzebowanie na dedykowane pulpity nawigacyjne (dashboards) dla LLM bez ponoszenia wysokich kosztów systemów klasy Datadog.

### LangSmith — Dedykowane rozwiązanie dla stosu LangChain/LangGraph

- Licencja komercyjna, cena od 39 USD za użytkownika miesięcznie. Opcja self-hosted dostępna wyłącznie dla klientów Enterprise.
- Najlepsze na rynku wsparcie i integracja dla systemów opartych na frameworkach LangChain oraz LangGraph. Rozwiązanie mniej atrakcyjne w przypadku korzystania z innych bibliotek.
- Sweet spot: Zespoły deweloperskie opierające swoją architekturę na ekosystemie LangChain, posiadające odpowiedni budżet.

### Helicone — Minimalistyczna brama proxy

- Bardzo szybka konfiguracja (15-30 minut) polegająca na zmianie adresu bazowego API (`OPENAI_API_BASE`) na adres proxy Helicone.
- Licencja MIT; bezpłatny limit do 100 tys. zapytań miesięcznie, pakiety płatne od 20 USD/miesiąc.
- Udostępnia funkcje bramy sieciowej (gateway), w tym przełączanie awaryjne (failover), buforowanie (caching) oraz limity zapytań (rate limiting).
- Oferuje mniejszą szczegółowość w analizie złożonych, wieloetapowych procesów agentowych.
- Sweet spot: Projekty wymagające szybkiego startu, proste aplikacje jednowątkowe, zapotrzebowanie na integrację bramy i systemu monitorowania w jednym narzędziu.

### Opik (Comet) — Platforma deweloperska OSS

- Licencja Apache 2.0, pełny model open source.
- Funkcjonalnie zbliżony do Langfuse, bazujący na doświadczeniach platformy Comet.
- Sweet spot: Zespoły inżynierii danych i ML korzystające z narzędzi Comet, które chcą monitorować systemy LLM w ramach tego samego panelu administracyjnego.

### SigNoz — Pełne monitorowanie APM w standardzie OpenTelemetry

- Licencja Apache 2.0. Obsługuje monitorowanie wydajności aplikacji (APM) oraz telemetrię LLM za pośrednictwem standardu OpenTelemetry.
- Sweet spot: Potrzeba wdrożenia jednolitej platformy monitorowania wydajności (observability) zarówno dla klasycznych mikroserwisów, jak i usług opartych o modele LLM.

### Integracja: Standard OpenTelemetry oraz konwencje GenAI

Pod koniec 2025 r. konsorcjum OpenTelemetry opublikowało oficjalny standard konwencji semantycznych dla systemów GenAI (np. `gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`). Dzięki temu narzędzia wspierające standard OTel mogą swobodnie wymieniać dane. Rekomendowany schemat architektury produkcyjnej:

1. Generowanie i wysyłanie metryk OTel zgodnych z konwencjami GenAI przy każdym wywołaniu modelu LLM.
2. Kierowanie bieżącego ruchu produkcyjnego przez bramę proxy (np. Helicone lub Portkey).
3. Równoległe przesyłanie śladów (dual-shipping) do platformy ewaluacyjnej (np. Phoenix lub Langfuse) w celu analizy regresji.
4. Archiwizowanie danych w jeziorze danych (data lake w formacie Iceberg) do długoterminowych analiz (np. za pomocą Arize AX lub DuckDB).

### Pułapka: Instrumentacja na niewłaściwym poziomie

Wdrożenie systemu monitorowania bezpośrednio wewnątrz kodu frameworka agentowego (np. śledzenie na poziomie kodu LangSmith) silnie uzależnia architekturę od wybranej biblioteki. Lepszym i bardziej uniwersalnym podejściem jest wdrożenie instrumentacji na poziomie protokołu HTTP lub biblioteki klienckiej SDK (np. poprzez OpenLLMetry lub bramę proxy).

### Próbkowanie danych — Ograniczanie kosztów zapisu

Przy wolumenie ruchu przekraczającym milion zapytań dziennie, koszt zapisu i przechowywania kompletnych logów telemetrycznych może przewyższyć koszt samych zapytań do modeli LLM. Należy wdrożyć inteligentne reguły próbkowania (sampling): zapisuj 100% zapytań zakończonych błędem, 100% zapytań o wysokim koszcie oraz losową próbkę 5% zapytań zakończonych sukcesem. Zbiorcze statystyki powinny być zachowywane w całości, natomiast szczegółowe ślady warto ograniczyć do analizy przypadków skrajnych.

### Liczby, które powinieneś zapamiętać

- Darmowy limit w chmurze Langfuse: 50 tys. zdarzeń miesięcznie.
- Licencja komercyjna LangSmith: od 39 USD za użytkownika miesięcznie.
- Darmowy limit w Helicone: 100 tys. zapytań miesięcznie.
- Szacowane oszczędności Arize AX na dużą skalę: ok. 100-krotna redukcja kosztów.
- Konwencje semantyczne OpenTelemetry GenAI: opublikowane w 2025 r., powszechnie stosowane w 2026 r.

## Użycie

Skrypt `code/main.py` symuluje generowanie miliona śladów telemetrycznych w ciągu doby przy zastosowaniu różnych strategii przechowywania danych (zapis 100% ruchu, próbkowanie losowe, próbkowanie z priorytetem błędów). Raportuje koszty składowania logów oraz stopień utraty istotnych informacji diagnostycznych w każdym ze scenariuszy.

## Efekt końcowy

W ramach tej lekcji powstaje dokument `outputs/skill-observability-stack.md`. Na podstawie wybranego stosu technologicznego, skali działania, budżetu oraz wymagań licencyjnych generuje on rekomendację i plan wdrożenia odpowiednich narzędzi obserwowalności.

## Ćwiczenia

1. Twój zespół rozwija aplikację w oparciu o LangChain i wymaga wdrożenia lokalnego systemu monitorowania opartego na licencji open source. Dokonaj wyboru pomiędzy Langfuse a Opik i uzasadnij swoją decyzję.
2. Przy wolumenie ruchu na poziomie 5 milionów zapytań dziennie, wdrożenie narzędzia Datadog zostało wycenione na 150 000 USD miesięcznie. Oblicz punkt rentowności dla wdrożenia systemu Arize AX.
3. Zaprojektuj standardowy zestaw atrybutów OpenTelemetry GenAI, który powinien być dołączany do każdego wywołania modelu LLM w Twojej organizacji.
4. Oceń, czy samodzielne wdrożenie narzędzia Phoenix jest wystarczające do obsługi ruchu produkcyjnego. W jakich scenariuszach to rozwiązanie przestanie być wystarczające?
5. Wdrożenie bramy Helicone wprowadza dodatkowe opóźnienie sieciowe na poziomie 20 ms. Czy przy opóźnieniu P99 TTFT wynoszącym 300 ms jest to wartość akceptowalna? Jak zmieni się sytuacja, gdy SLA wymaga czasu TTFT na poziomie 100 ms?

## Kluczowe terminy

| Termin | Potoczna nazwa | Rzeczywiste znaczenie |
|------|----------------|--------------------------------------|
| OpenLLMetry | „OTel dla LLM” | Otwarta biblioteka instrumentacyjna zgodna ze standardem OpenTelemetry, dedykowana dla modeli LLM |
| Konwencje GenAI | „atrybuty OTel GenAI” | Ustandaryzowane nazwy parametrów i atrybutów w standardzie OpenTelemetry dla komunikacji z LLM |
| LangSmith | „chmura LangChain” | Komercyjna platforma monitorowania i ewaluacji ściśle zintegrowana z ekosystemem LangChain |
| Langfuse | „otwarty LangSmith” | Platforma deweloperska o bogatej funkcjonalności, udostępniana na otwartej licencji MIT |
| Phoenix | „narzędzie od Arize” | Otwarty system telemetryczny i ewaluacyjny natywnie wspierający standard OpenTelemetry |
| Arize AX | „bezkopiowy monitoring” | Komercyjne rozwiązanie do monitorowania na dużą skalę, odczytujące dane bezpośrednio z formatów Iceberg/Parquet w jeziorze danych |
| Helicone | „brama i proxy” | Serwer proxy HTTP zbierający dane telemetryczne wywołań API i udostępniający funkcje bramy |
| Opik | „Comet dla LLM” | Otwarta platforma deweloperska LLM na licencji Apache 2.0 rozwijana przez Comet |
| Odtwarzanie sesji | „session replay / trace” | Możliwość prześledzenia pełnego grafu wywołań w ramach jednej sesji użytkownika lub agenta |
| Ewaluacja | „eval / testy offline” | Proces automatycznego testowania promptów lub modeli na przygotowanym, oznaczonym zbiorze danych walidacyjnych |

## Dalsze czytanie

- [SigNoz — Best LLM Observability Tools 2026](https://signoz.io/comparisons/llm-observability-tools/) — Zestawienie i porównanie wiodących systemów monitorowania.
- [Langfuse — Arize Phoenix Alternative Analysis](https://langfuse.com/faq/all/best-phoenix-arize-alternatives) — Analiza porównawcza systemów Langfuse i Phoenix.
- [PremAI — Setting up LLM Observability](https://blog.premai.io/llm-observability-setting-up-langfuse-langsmith-helicone-phoenix/) — Przewodnik po konfiguracji narzędzi Langfuse, LangSmith, Helicone oraz Phoenix.
- [OpenTelemetry GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — Oficjalna specyfikacja atrybutów standardu OTel dla GenAI.
- [Arize Phoenix Documentation](https://docs.arize.com/phoenix) — Podręcznik użytkownika platformy ewaluacyjnej Phoenix.
- [Helicone Documentation](https://docs.helicone.ai/) — Instrukcja konfiguracji i wdrożenia bramy proxy Helicone.
