# Zarządzane platformy LLM — Bedrock, Vertex AI, Azure OpenAI

> Trzy hiperskalery, trzy różne strategie. AWS Bedrock to rynek modeli (model marketplace) oferujący Claude, Llamę, Titan, Stability i Cohere pod jednym ujednoliconym API. Azure OpenAI to ekskluzywne partnerstwo z OpenAI oraz gwarantowane jednostki przepustowości (PTU) dla dedykowanych zasobów obliczeniowych. Vertex AI stawia przede wszystkim na modele Gemini, oferując najlepsze wsparcie dla długiego kontekstu i multimodalności. W 2026 roku serwis Artificial Analysis wykazuje medianę opóźnienia na poziomie ~50 ms dla Azure OpenAI oraz ~75 ms dla AWS Bedrock przy modelach klasy Llama 3.1 405B – dedykowane jednostki PTU tłumaczą tę różnicę, jako że wydzielona moc obliczeniowa przewyższa współdzieloną infrastrukturę na żądanie. Złotą zasadą przy wyborze nie jest pytanie „która platforma jest najszybsza”, ale „który katalog modeli i model rozliczeń FinOps najlepiej pasują do mojego produktu”. Ta lekcja uczy świadomego wyboru w oparciu o twarde dane o kompromisach, a nie na podstawie przeczuć.

**Typ:** Teoria (Learn)
**Języki:** Python (stdlib, prosty symulator kosztów i opóźnień)
**Wymagania wstępne:** Faza 11 (Inżynieria LLM), Faza 13 (Narzędzia i protokoły)
**Czas:** ~60 minut

## Cele nauczania

- Poznaj trzy strategie platformowe (marketplace, partnerstwo na wyłączność, priorytet dla Gemini) i dopasuj każdą z nich do konkretnego biznesowego przypadku użycia.
- Wyjaśnij, czym są jednostki przepustowości (PTU) w Azure OpenAI i dlaczego zapytania na żądanie w Bedrock są zwykle o ~25 ms wolniejsze dla modeli skali 405B.
- Przeanalizuj strukturę rozliczania kosztów (FinOps) dla każdej platformy (profile wnioskowania aplikacji w Bedrock vs podział na projekty w Vertex AI vs subskrypcje i rezerwacje PTU w Azure).
- Zrozum zasadę „minimum dwóch dostawców” i dowiedz się, dlaczego uzależnienie od jednego dostawcy (vendor lock-in) w 2026 roku jest kosztownym błędem.

## Problem

Jako kluczowy model w swoim produkcie wybrałeś Claude 3.7 Sonnet. Teraz musisz udostępnić go produkcyjnie. Możesz bezpośrednio wywołać API Anthropic, skorzystać z usługi AWS Bedrock lub wdrożyć własną bramę (gateway). Bezpośrednie wywołanie API jest najprostsze. Z kolei Bedrock dodaje obsługę umów BAA, prywatne punkty końcowe VPC, uprawnienia IAM oraz integrację z metrykami AWS CloudWatch. Własna brama pozwala dodatkowo na automatyczne przełączanie awaryjne (failover), ujednolicone rozliczenia oraz limity zapytań (rate limits) u różnych dostawców.

Kluczową kwestią jest jednak dostępny katalog modeli. Jeśli Twój produkt wymaga jednoczesnego korzystania z Claude, Llamy i Gemini, nie uzyskasz do nich dostępu z poziomu jednego dostawcy, chyba że zintegrujesz system z AWS Bedrock, Vertex AI oraz Azure OpenAI jednocześnie. Hiperskalerów nie można stosować w pełni zamiennie – każdy z nich przyjął inną strategię dotyczącą dostępu do wiodących modeli.

W tej lekcji omówiono trzy strategie, różnice w opóźnieniach, specyfikę zarządzania kosztami (FinOps) oraz ryzyko uzależnienia od jednego dostawcy.

## Koncepcja

### Trzy strategie

**AWS Bedrock** — rynek modeli (marketplace). Oferuje Claude (Anthropic), Llamę (Meta), Titan (rozwijany przez AWS), Stability (generowanie obrazów), Cohere (embeddingi), Mistral oraz inne dedykowane modele. Zapewnia jedno API, jeden spójny model uprawnień IAM i zintegrowany eksport logów do CloudWatch. AWS zakłada, że dla klientów ważniejsza jest możliwość wyboru i elastyczność niż koncentracja na jednym dostawcy modeli.

**Azure OpenAI** — partnerstwo na wyłączność. Zapewnia dostęp do modeli GPT-4 / 4o / 5 / o, DALL·E, Whisper oraz możliwość dostrajania (fine-tuning) modeli OpenAI w chmurze Azure. W katalogu „Azure OpenAI Service” nie znajdziesz modeli innych niż OpenAI – te trafiają do usługi Azure AI Foundry (która jest osobnym produktem). Microsoft stawia na to, że OpenAI utrzyma pozycję lidera technologicznego, a klienci biznesowi oczekują korporacyjnych standardów bezpieczeństwa przy korzystaniu z tych konkretnych modeli.

**Vertex AI** — priorytet dla Gemini. Oferuje modele Gemini 1.5 / 2.0 / 2.5 Flash i Pro oraz zewnętrzny katalog Model Garden. Największym atutem Vertex AI jest natywne wsparcie dla multimodalności oraz obsługa bardzo długiego kontekstu (okno kontekstowe rzędu 1M tokenów w modelach Gemini to cecha wyróżniająca tę platformę).

### Różnice w opóźnieniach w dużej skali

Serwis Artificial Analysis prowadzi ciągłe testy porównawcze wydajności chmur. Dla modeli klasy Llama 3.1 405B (w wersjach na żądanie), mediana opóźnienia do wygenerowania pierwszego tokenu (TTFT) w Azure OpenAI wynosi około 50 ms, podczas gdy w AWS Bedrock wynosi około 75 ms. Ta różnica nie wynika ze słabości infrastruktury AWS – to kwestia odmiennych modeli rozliczeniowych i alokacji zasobów. Microsoft Azure oferuje jednostki PTU (Provisioned Throughput Units), które rezerwują dedykowaną moc układów GPU dla konkretnego klienta. W Bedrock również istnieje odpowiednik gwarantowanej wydajności (Provisioned Throughput), ale ceny zaczynają się od około 21 USD za godzinę za jednostkę, przez co większość klientów decyduje się na tańszą infrastrukturę współdzieloną na żądanie.

Współdzielona przepustowość na żądanie konkuruje o zasoby z ruchem generowanym przez innych klientów, podczas gdy pojemność dedykowana gwarantuje stałą wydajność. Jeśli umowa SLA Twojego produktu wymaga opóźnienia TTFT < 100 ms dla percentyla P99, musisz zainwestować w jednostki PTU w Azure, wykupić gwarantowaną przepustowość w Bedrock lub zaakceptować większe wahania wydajności na żądanie.

### Ekonomika dedykowanej przepustowości

Jednostki PTU w chmurze Azure to zarezerwowany blok mocy obliczeniowej dla wnioskowania. Przy przewidywalnym, stabilnym ruchu pozwalają one zaoszczędzić do 70% kosztów w porównaniu z rozliczeniem na żądanie. Generują one jednak stałe opłaty godzinowe niezależnie od faktycznego wykorzystania – płacisz za rezerwację nawet wtedy, gdy system nie przetwarza zapytań. Próg rentowności (break-even point) w stosunku do rozliczeń na żądanie osiąga się zwykle przy ciągłym obciążeniu na poziomie 40–60%.

Gwarantowana przepustowość w Bedrock kosztuje od 21 do 50 USD za godzinę w zależności od wybranego modelu i regionu. Kalkulacja ekonomiczna jest podobna – próg rentowności wynosi około połowy maksymalnego wykorzystania zasobów, przy czym AWS wymaga deklaracji korzystania z usługi na okres co najmniej miesiąca.

Dedykowana przepustowość w Vertex AI jest rozliczana na poziomie poszczególnych jednostek SKU modeli Gemini; cennik zależy od modelu i regionu i rzadziej podlega publicznej negocjacji.

### Zarządzanie kosztami (FinOps) — kluczowe różnice

**Profile wnioskowania aplikacji w Bedrock (Application Inference Profiles)** to najbardziej precyzyjne natywne narzędzie do atrybucji kosztów na rynku. Umożliwiają one oznaczenie profilu tagami takimi jak `team`, `product` czy `feature`. Wszystkie wywołania modeli przechodzące przez dany profil są automatycznie sumowane, a CloudWatch pozwala na natychmiastowe raportowanie kosztów bez konieczności dodatkowej obróbki danych. Funkcja ta, wprowadzona w 2025 roku, stanowi najbardziej szczegółowe rozwiązanie u hiperskalera.

W **Vertex AI** atrybucja kosztów opiera się na podziale na projekty Google Cloud (GCP) przypisane do poszczególnych zespołów oraz na szczegółowym etykietowaniu (labels) zasobów. Do generowania raportów i podsumowań wykorzystuje się eksport danych bilingowych do BigQuery i wizualizację w DataStudio. Wymaga to konfiguracji, ale pozwala na dowolne analizowanie danych finansowych za pomocą języka SQL.

W **Azure OpenAI** rozliczenia opierają się na subskrypcjach, grupach zasobów oraz tagach, a rezerwacje PTU stanowią oddzielną pozycję kosztową. Tagi są przypisywane na poziomie grup zasobów, a nie poszczególnych zapytań API. Precyzyjna atrybucja kosztów wymaga więc zbierania metryk przez Application Insights lub wdrożenia bramy pośredniczącej, która znakuje nagłówki zapytań.

Podsumowując: Bedrock oferuje najbardziej przejrzyste natywne mechanizmy rozliczeń, Vertex zapewnia największą elastyczność dzięki BigQuery, natomiast Azure wymaga dodatkowego oprzyrządowania do uzyskania pełnej czytelności kosztów.

### Ryzyko uzależnienia od jednego dostawcy (vendor lock-in) w 2026 roku

Korzystanie z usług jednego dostawcy chmurowego było uzasadnione, gdy na rynku dominował tylko jeden wiodący model. W 2026 roku sytuacja zmienia się dynamicznie – w jednym kwartale liderem może być Claude 3.7, w kolejnym Gemini 2.5, a jeszcze później GPT-5. Ograniczenie się do jednego hiperskalera odcina Twój produkt od większości najnowocześniejszych rozwiązań.

Wiodące zespoły inżynieryjne stosują zasadę: minimum dwóch dostawców chmurowych dla każdego krytycznego wywołania LLM w systemie. Częstym wyborem jest łączenie AWS Bedrock i Azure OpenAI – korzystanie z modeli Claude u jednego i GPT u drugiego, z automatycznym przełączaniem awaryjnym i jedną bramą API. Wzrost kosztów jest znikomy, ponieważ brama optymalizuje ścieżki zapytań, a zyskujesz odporność na awarie infrastruktury (takie jak przestoje Azure OpenAI w styczniu 2025 r. czy awarie AWS us-east-1).

### Zgodność z regulacjami i lokalizacja danych (data residency)

- **AWS Bedrock:** Umowy BAA (Business Associate Agreement) dostępne w większości regionów; prywatne punkty końcowe VPC; filtry bezpieczeństwa (Guardrails). Jest to standardowy wybór w branży fintech.
- **Azure OpenAI:** HIPAA, SOC 2, ISO 27001; gwarancja przechowywania danych na terenie UE; domyślne spełnianie standardów korporacyjnych.
- **Vertex AI:** HIPAA, RODO, elastyczny dobór lokalizacji danych w regionach Google Cloud; pełny zestaw certyfikatów zgodności chmury Google.

Wszyscy trzej dostawcy spełniają kluczowe wymagania bezpieczeństwa. Różnice dotyczą szczegółowych zasad przechowywania danych, sposobu obsługi logów oraz tego, czy automatyczne filtry wykrywania nadużyć (abuse monitoring) analizują treść zapytań i odpowiedzi (co jest domyślnym ustawieniem; klienci biznesowi mogą wnioskować o wyłączenie tej analizy).

### Liczby warte zapamiętania

- Mediana TTFT w Azure OpenAI dla modeli klasy Llama 3.1 405B: ~50 ms (przy użyciu PTU).
- Mediana TTFT w AWS Bedrock (na żądanie): ~75 ms.
- Gwarantowana przepustowość Bedrock: 21–50 USD/godz. za jednostkę.
- Próg rentowności rezerwacji PTU w Azure: ciągłe obciążenie na poziomie ~40–60%.
- Oszczędność przy użyciu PTU zamiast rozliczeń na żądanie (przy dużym ruchu): do 70%.

## Użyj tego

Skrypt `code/main.py` pozwala na porównanie trzech platform pod kątem syntetycznego obciążenia. Modeluje on opłacalność rozwiązań na żądanie w stosunku do rezerwacji PTU, wahania wskaźnika TTFT oraz dokładność raportowania kosztów. Uruchom go, aby sprawdzić, kiedy inwestycja w PTU staje się opłacalna i w jakich sytuacjach dostęp do szerokiego katalogu modeli w Bedrock przewyższa różnice w opóźnieniach.

## Wdróż to (Ship It)

Do tej lekcji dołączono narzędzie `outputs/skill-managed-platform-picker.md`. Na podstawie profilu obciążenia Twojego systemu (wymagane modele, SLA dla wskaźnika TTFT, dzienny wolumen zapytań, wymagania regulacyjne) zarekomenduje ono platformę główną, zapasową oraz plan wdrożenia FinOps do kontroli kosztów.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Przy jakim stałym poziomie obciążenia rezerwacja Azure PTU staje się tańsza niż rozliczenia na żądanie dla modelu klasy 70B? Oblicz próg rentowności i porównaj go z deklarowanym zakresem 40–60%.
2. Twój produkt wymaga jednoczesnego korzystania z modeli Claude 3.7 Sonnet i GPT-4o. Zaprojektuj architekturę opartą na dwóch dostawcach chmurowych – wskaż, które zapytania trafiają do którego hiperskalera, jak skonfigurować bramę API oraz jakie reguły przełączania awaryjnego (failover) należy wdrożyć.
3. Klient z regulowanego sektora opieki zdrowotnej wymaga podpisania umowy BAA, przechowywania danych w regionie US-East oraz utrzymania wskaźnika P99 TTFT poniżej 100 ms. Wybierz odpowiednią platformę chmurową i uzasadnij swoją decyzję, wskazując trzy konkretne funkcje tej platformy.
4. Zaobserwowałeś, że Twój rachunek za usługę AWS Bedrock wzrósł w tym miesiącu czterokrotnie, mimo braku zmian w natężeniu ruchu użytkowników. Jak zidentyfikować źródło problemu bez skonfigurowanych profili wnioskowania (Application Inference Profiles), a ile czasu zajmie to przy ich użyciu?
5. Przeanalizuj cenniki Azure OpenAI i AWS Bedrock. Które rozwiązanie będzie najtańsze przy przetwarzaniu wolumenu 100 mln tokenów miesięcznie dla modelu Claude: bezpośrednie API Anthropic, Bedrock na żądanie czy Bedrock z gwarantowaną przepustowością (Provisioned Throughput)?

## Kluczowe terminy

| Termin | Potoczny opis | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| AWS Bedrock | „Usługa LLM od AWS” | Platforma typu marketplace oferująca modele Claude, Llama, Titan, Mistral, Cohere i inne. |
| Azure OpenAI | „ChatGPT w Azure” | Usługi hostowania modeli OpenAI w infrastrukturze Microsoft Azure z zabezpieczeniami korporacyjnymi. |
| Vertex AI | „LLM od Google” | Platforma Google chmurowo zorientowana na modele Gemini, zawierająca katalog Model Garden dla rozwiązań firm trzecich. |
| PTU | „rezerwowana wydajność” | Provisioned Throughput Unit – dedykowane, opłacane godzinowo zasoby GPU gwarantujące stałą przepustowość wnioskowania. |
| Application Inference Profile | „tagowanie w Bedrock” | Funkcja AWS Bedrock do precyzyjnej atrybucji kosztów i monitorowania zużycia zasobów, zintegrowana z CloudWatch. |
| Model Garden | „katalog Vertex” | Sekcja platformy Vertex AI grupująca modele open-source i rozwiązania partnerów zewnętrznych, oddzielona od natywnych modeli Gemini. |
| LLM redundancy | „dwóch dostawców” | Strategia projektowa polegająca na obsłudze krytycznych funkcji LLM przez co najmniej dwóch niezależnych dostawców chmurowych. |
| BAA | „zgodność z HIPAA” | Business Associate Agreement – umowa wymagana przy przetwarzaniu danych medycznych (PHI), oferowana przez wszystkich trzech dostawców. |
| Abuse monitoring | „skanowanie logów” | Automatyczna analiza zapytań i odpowiedzi przez dostawcę chmurowego pod kątem bezpieczeństwa; korporacje mogą wnioskować o jej wyłączenie. |

## Dalsze czytanie

- [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/) — oficjalne cenniki i warunki zakupu gwarantowanej przepustowości.
- [Ceny usługi Azure OpenAI](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/) — szczegóły dotyczące rezerwacji jednostek PTU i stawek na żądanie.
- [Ceny Vertex AI Generative AI](https://cloud.google.com/vertex-ai/generative-ai/pricing) — stawki za korzystanie z modeli Gemini i zasobów Model Garden.
- [Artificial Analysis LLM Leaderboard](https://artificialanalytics.ai/) — niezależne, ciągłe testy porównawcze opóźnień i wydajności u różnych dostawców chmurowych.
- [The AI Journal — AWS Bedrock vs Azure OpenAI Guide](https://theaijournal.co/2026/03/aws-bedrock-vs-azure-openai/) — ramy podejmowania decyzji technologicznych w przedsiębiorstwie.
- [Finout — Bedrock vs Vertex vs Azure FinOps](https://www.finout.io/blog/bedrock-vs.-vertex-vs.-azure-cognitive-a-finops-comparison-for-ai-spend) — szczegółowe porównanie mechanizmów rozliczania i atrybucji kosztów.
