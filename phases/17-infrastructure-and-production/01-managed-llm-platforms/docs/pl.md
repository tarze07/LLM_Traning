# Zarządzane platformy LLM — Bedrock, Vertex AI, Azure OpenAI

> Trzy hiperskalery, trzy różne strategie. AWS Bedrock to modelowy rynek — Claude, Llama, Titan, Stability, Cohere za jednym API. Azure OpenAI to ekskluzywne partnerstwo OpenAI plus zapewnione jednostki przepustowości (PTU) dla dedykowanej pojemności. Vertex AI jest pierwszym Gemini z najlepszą historią wielokontekstową i multimodalną. W 2026 r. sztuczna analiza mierzy Azure OpenAI przy medianie ~50 ms i Bedrock przy ~75 ms na odpowiednikach Llama 3.1 405B — jednostki PTU wyjaśniają różnicę, ponieważ dedykowana pojemność przewyższa współdzieloną na żądanie. Regułą podejmowania decyzji nie jest pytanie „który jest najszybszy”, ale „który katalog modeli i powierzchnia FinOps pasują do mojego produktu”. Ta lekcja uczy cię wybierać, mając zapisane kompromisy, a nie wibracje.

**Typ:** Ucz się
**Języki:** Python (stdlib, komparator kosztów i opóźnień zabawek)
**Wymagania wstępne:** Faza 11 (Inżynieria LLM), Faza 13 (Narzędzia i protokoły)
**Czas:** ~60 minut

## Cele nauczania

- Nazwij trzy strategie platformowe (rynek, wyłączność, najpierw Gemini) i dopasuj każdą do przypadku użycia produktu.
— Wyjaśnij, jakie jednostki przepustowości (PTU) kupujesz w Azure OpenAI i dlaczego baza Bedrock na żądanie zwykle odczytuje ~25 ms wolniej w skali 405B.
- Diagram powierzchni atrybucji FinOps dla każdej platformy (profile wnioskowania aplikacji Bedrock vs projekt Vertex na zespół vs zakresy Azure + rezerwacje PTU).
– Zapisz zasady „minimum dwóch dostawców” i wyjaśnij, dlaczego uzależnienie od jednego dostawcy będzie kosztownym błędem w 2026 r.

## Problem

Jako swój produkt wybrałeś Claude 3.7 Sonnet. Teraz musisz to podać. Możesz wywołać Anthropic API bezpośrednio, możesz to zrobić poprzez AWS Bedrock, lub możesz przejść przez bramę. Bezpośrednie API jest najprostsze; Bedrock dodaje BAA, punkty końcowe VPC, IAM i atrybucję CloudWatch. Brama dodaje przełączanie awaryjne, ujednolicone rozliczenia i limity stawek u różnych dostawców.

Głębszym pytaniem jest katalog. Jeśli potrzebujesz Claude'a, Lamy i Gemini w tym samym produkcie, nie możesz kupić ich wszystkich w jednym miejscu, chyba że tym miejscem jest jednocześnie Bedrock, Vertex i Azure OpenAI. Hiperskalerów nie można stosować wymiennie — każdy z nich postawił inny zakład na to, kto jest właścicielem warstwy modelu.

W tej lekcji omówiono trzy zakłady, lukę w opóźnieniu, lukę w FinOps i ryzyko zablokowania.

## Koncepcja

### Trzy strategie

**AWS Bedrock** — rynek. Claude (Anthropic), Lama (Meta), Titan (własna strona AWS), Stability (obraz), Cohere (osadzenie), Mistral, a także podkatalogi obrazów i osadzania. Jeden interfejs API, jedna powierzchnia IAM, jeden eksport CloudWatch. Firma Bedrock zakłada, że ​​klienci bardziej chcą opcji niż pojedynczego modelu.

**Azure OpenAI** — wyłączne partnerstwo. Otrzymujesz serię GPT-4 / 4o / 5 / o, DALL·E, Whisper i dostrajanie modeli OpenAI w centrach danych Azure. W katalogu „Azure OpenAI Service” nie ma modeli innych niż OpenAI — trafiają one do Azure AI Foundry (oddzielny produkt). Azure stawia na to, że OpenAI pozostanie pionierem, a klienci chcą mieć kontrolę korporacyjną nad tą konkretną relacją.

**Vertex AI** — Najpierw Bliźnięta, potem wszystko inne. Gemini 1.5 / 2.0 / 2.5 Flash i Pro oraz Model Garden (innej firmy). Zakład Vertex jest wielomodalny w długim kontekście — kontekst Gemini z tokenem 1M jest wyróżnikiem.

### Luka w opóźnieniu na dużą skalę

Sztuczna analiza przeprowadza ciągłe testy porównawcze. W przypadku równoważnych wdrożeń Llama 3.1 405B (udostępnianych na żądanie) mediana opóźnienia pierwszego tokenu platformy Azure OpenAI wynosi około 50 ms; Podłoże wynosi około 75 ms. Ta luka nie jest awarią AWS — jest to różnica w modelu wydajności. Platforma Azure sprzedaje jednostki PTU (zaopatrzone jednostki przepustowości), które rezerwują pojemność procesora GPU dla Twojej dzierżawy. Odpowiednik Bedrock (zaopatrzona przepustowość) istnieje, ale zaczyna się od około 21 USD za godzinę za jednostkę, a większość klientów korzysta z współdzielenia na żądanie.

Współdzielona przepustowość na żądanie konkuruje z ruchem wszystkich pozostałych klientów. Pojemność dedykowana nie. Jeśli umowa SLA Twojego produktu wynosi TTFT < 100 ms przy P99, możesz kupić jednostki PTU na platformie Azure, kupić zapewnioną przepustowość Bedrock lub zaakceptować odchylenie domyślne.

### Ekonomika zapewnionej przepustowości

Jednostki PTU platformy Azure: zarezerwowany blok obliczeń wnioskowania. Do ~70% oszczędności w porównaniu z rozwiązaniami na żądanie w przypadku przewidywalnych obciążeń. Koszty stałe za godzinę niezależnie od natężenia ruchu — płacisz za rezerwację nawet w stanie bezczynności. Próg rentowności wynosi zwykle około 40–60% ciągłego wykorzystania.

Udostępniona przepustowość Bedrock: $21-$50 na godzinę w zależności od modelu i regionu. Podobna matematyka – próg rentowności wynosi około połowy maksymalnego wykorzystania. Wymagane miesięczne zaangażowanie.

Moc udostępniona przez firmę Vertex jest sprzedawana na jednostkę SKU Gemini; ceny różnią się w zależności od modelu i regionu i są rzadziej reklamowane publicznie.

### Powierzchnia FinOps — prawdziwy wyróżnik

**Profile wnioskowania aplikacji Bedrock** to najczystsza atrybucja na rynku. Oznacz profil tagami `team`, `product`, `feature`; kieruj przez niego wszystkie wywołania modelu; CloudWatch oblicza koszt profilu bez przetwarzania końcowego. Dodano 2025, wciąż najbardziej szczegółowy natywny hiperskaler.

**Vertex** atrybucja dotyczy projektu na zespół plus etykiety – wszędzie. Modelujesz każdy zespół jako projekt GCP, umieszczasz etykiety na każdym zasobie i używasz BigQuery Billing Export + DataStudio do podsumowań. Więcej pracy, ale BigQuery udostępnia dowolny kod SQL na podstawie danych o kosztach.

**Azure** opiera się na zakresach subskrypcji/grup zasobów oraz tagach, a rezerwacje PTU stanowią pierwszorzędny obiekt kosztowy. Tagi są dziedziczone z grup zasobów, a nie z żądań, więc atrybucja na żądanie wymaga niestandardowych metryk Application Insights lub bramy, która stempluje nagłówki.

Wzorzec: Bedrock jest najczystszym natywnym rozwiązaniem, Vertex jest najbardziej elastyczny dzięki BigQuery, Azure jest najbardziej nieprzejrzysty, chyba że użyjesz instrumentu.

### Zamknięcie to ryzyko w 2026 r

Zaangażowanie w pojedynczy hiperskaler było w porządku, gdy dominował jeden model. W 2026 r. granica przesuwa się co miesiąc – w pierwszym kwartale Claude 3,7, w następnym Gemini 2,5, w kolejnym kwartale GPT-5. Zablokowanie się na jednej platformie blokuje dostęp do dwóch trzecich granicy.

Zespoły robocze wzorców przyjmują: minimum dwóch dostawców dla każdego wezwania LLM o znaczeniu krytycznym dla produktu. Bedrock i Azure OpenAI to wspólna para — Claude z jednego, GPT z drugiego, przełączanie awaryjne między nimi, ta sama brama. Wzrost kosztów jest znikomy, ponieważ trasy bram są optymalne; wzrost dostępności podczas przestojów (takich jak incydent Azure OpenAI w styczniu 2025 r., awaria AWS us-east-1) ma decydujące znaczenie.

### Miejsce przechowywania danych, umowy BAA i branże regulowane

Podłoże: BAA w większości regionów; punkty końcowe VPC; poręcze. Typowa wartość domyślna fintech.
Azure OpenAI: HIPAA, SOC 2, ISO 27001; miejsce przechowywania danych w UE; niewykonanie zobowiązania regulowane przez przedsiębiorstwo.
Vertex: HIPAA, RODO, miejsce przechowywania danych według regionu; Stos zgodności Google Cloud.

Wszystkie trzy spełniają podstawowe pole wyboru. Różnice dotyczą zasad przechowywania danych, sposobu obsługi dzienników i tego, czy monitorowanie nadużyć odczytuje Twój ruch (w większości przypadków opcja ta jest domyślna; opcja rezygnacji jest dostępna w przypadku przedsiębiorstw).

### Liczby, które powinieneś zapamiętać

— Mediana TTFT platformy Azure OpenAI w odpowiednikach Lamy 3.1 405B: ~50 ms (z jednostkami PTU).
- Mediana Bedrock TTFT na żądanie: ~75 ms.
- Zapewniona przepustowość Bedrock: $21-$50/godz. na jednostkę.
— Próg rentowności jednostek PTU platformy Azure: ciągłe wykorzystanie ~40–60%.
- Oszczędność PTU w porównaniu do zapotrzebowania na żądanie przy wysokim obciążeniu: do 70%.

## Użyj tego

`code/main.py` porównuje trzy platformy pod kątem syntetycznego obciążenia — modeluje ekonomię na żądanie w porównaniu z ekonomią PTU, wariancję TTFT i wierność atrybucji kosztów. Uruchom go, aby zobaczyć, gdzie PTU się opłacają i gdzie szerokość modeli na rynku przewyższa lukę w TTFT.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-managed-platform-picker.md`. Biorąc pod uwagę profil obciążenia (potrzebne modele, umowa SLA TTFT, dzienny wolumen, wymagania dotyczące zgodności), zaleca platformę podstawową, rezerwową i plan oprzyrządowania FinOps.

## Ćwiczenia

1. Uruchom `code/main.py`. Przy jakim stałym wykorzystaniu jednostka Azure PTU przewyższa zapotrzebowanie na żądanie w przypadku modelu klasy 70B? Oblicz próg rentowności i porównaj z reklamowanym przedziałem 40-60%.
2. Twój produkt wymaga Claude 3.7 Sonnet i GPT-4o. Zaprojektuj wdrożenie z udziałem dwóch dostawców — które jest kierowane do którego hiperskalera, jaka brama znajduje się z przodu, jakie są zasady przełączania awaryjnego?
3. Klient objęty regulowaną opieką zdrowotną wymaga umów BAA, miejsca zamieszkania w USA-Wschód i czasu trwania P99 TTFT poniżej 100 ms. Wybierz platformę i uzasadnij ją trzema konkretnymi funkcjami.
4. Odkrywasz, że Twój rachunek za usługę Bedrock wzrósł w tym miesiącu czterokrotnie, bez zmian w ruchu. Jak bez profili wnioskowania aplikacji można znaleźć winowajcę? W przypadku profili, ile czasu to zajmuje?
5. Przeczytaj strony z cenami Azure OpenAI i Bedrock. Co jest tańsze w przypadku obciążenia Claude o wartości 100 mln tokenów miesięcznie – bezpośrednie Anthropic API, Bedrock na żądanie czy Bedrock Provisioned Throughput?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Podłoże | „Usługa AWS LLM” | Modelowy rynek w Claude, Lama, Titan, Mistral, Cohere |
| Azure OpenAI | „CzatGPT platformy Azure” | Ekskluzywne modele OpenAI w centrach danych Azure z kontrolą korporacyjną |
| Wierzchołkowa sztuczna inteligencja | „LLM Google” | Pierwsza platforma Gemini z Model Garden dla modeli innych firm |
| PTU | „pojemność dedykowana” | Udostępniona jednostka przepustowości — zarezerwowane procesory graficzne z wnioskowaniem, cena za godzinę |
| Profil wnioskowania aplikacji | „Tagowanie podłoża” | Profil kosztów/wykorzystania produktu ze znacznikami, natywny dla CloudWatch |
| Modelowy ogród | „Katalog wierzchołków” | Sekcja modeli innych firm Vertex AI, oddzielna od Gemini |
| Minimum dwóch dostawców | „Zwolnienie LLM” | Polityka prowadzenia każdej krytycznej ścieżki LLM w ≥2 hiperskalerach |
| BAA | „Dokumentacja HIPAA” | Umowa o współpracy biznesowej; wymagane dla PHI; dostarczone przez wszystkie trzy |
| Monitorowanie nadużyć | „obserwator kłód” | Skanowanie bezpieczeństwa po stronie dostawcy w przypadku monitów/wyników; rezygnacja w przedsiębiorstwie |

## Dalsze czytanie

– [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/) — autorytatywny arkusz stawek i ceny za udostępnioną przepustowość.
— [Ceny usług Azure OpenAI](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/) — ekonomika PTU i arkusze stawek.
– [Ceny Vertex AI Generative AI](https://cloud.google.com/vertex-ai/generative-ai/pricing) — poziomy Gemini i dopłaty Model Garden.
- [Tabela wyników sztucznej analizy LLM](https://artificialanalytics.ai/) — ciągłe testy porównawcze opóźnień i przepustowości u różnych dostawców.
- [The AI ​​Journal — AWS Bedrock vs Azure OpenAI CTO Guide 2026](https://theaijournal.co/2026/03/aws-bedrock-vs-azure-openai/) — ramy decyzyjne przedsiębiorstwa.
- [Finout — Bedrock vs Vertex vs Azure FinOps](https://www.finout.io/blog/bedrock-vs.-vertex-vs.-azure-cognitive-a-finops-comparison-for-ai-spend) — mechanika atrybucji obok siebie.