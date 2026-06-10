# Zgodność regulacyjna — SOC 2, HIPAA, RODO, PCI-DSS, Akt o sztucznej inteligencji (EU AI Act), ISO 42001

> Zapewnienie zgodności z wieloma standardami regulacyjnymi to absolutna podstawa przy zawieraniu kontraktów z przedsiębiorstwami. **Akt o sztucznej inteligencji (EU AI Act)** wszedł w życie 1 august 2024 roku, a większość przepisów dotyczących systemów wysokiego ryzyka zacznie obowiązywać od 2 sierpnia 2026 roku. Kary za naruszenie obowiązków dla systemów wysokiego ryzyka wynoszą do 15 mln euro lub 3% rocznego globalnego obrotu (art. 99 ust. 4), natomiast za stosowanie praktyk zakazanych – do 35 mln euro lub 7% obrotu (art. 99 ust. 3). Regulacja ta ma zastosowanie globalne, o ile systemy obsługują użytkowników z Unii Europejskiej. **Colorado AI Act** zacznie obowiązywać 30 czerwca 2026 roku (termin przesunięty z lutego 2026 roku ustawą SB25B-004) i wymaga przeprowadzania ocen wpływu (impact assessments) dla systemów wysokiego ryzyka oraz zapewnia użytkownikom prawo do odwołania się od decyzji podjętych przez AI. Podobne regulacje wdraża stan Wirginia w obszarach takich jak ocena zdolności kredytowej, zatrudnienie, mieszkalnictwo i edukacja. **SOC 2 Typ II** to de facto standard dla systemów B2B AI (szczególnie w wersji Typ II, a nie tylko Typ I, co jest kluczowe w sektorze fintech). **RODO**: najwyższa dotychczasowa kara za naruszenie prywatności przez systemy AI wyniosła 30,5 mln euro i została nałożona na Clearview AI przez holenderski organ ochrony danych (DPA) w wrześniu 2024 roku. Włoski organ Garante nałożył w grudniu 2024 roku karę w wysokości 15 mln euro na OpenAI (decyzja ta została później uchylona w wyniku odwołania w marcu 2026 roku). Maskowanie danych osobowych (PII/PHI) w czasie rzeczywistym na etapie wnioskowania to jedyny możliwy do obrony standard zgodności; usuwanie wrażliwych danych po przetworzeniu (post-processing scrubbing) jest niewystarczające. **HIPAA**: reguluje sektor opieki zdrowotnej w USA – przesyłanie chronionych informacji o zdrowiu (PHI) do zewnętrznych usług AI wymaga bezwzględnie podpisania umowy o partnerstwie biznesowym (BAA). **PCI-DSS**: zgodność warstwy interakcji z AI obsługującej dane kart płatniczych wymaga celowej konfiguracji i jasnych zapisów umownych, a nie dzieje się automatycznie. **ISO 42001** to nowy międzynarodowy standard zarządzania systemami sztucznej inteligencji, coraz częściej wymagany w procesach zakupowych jako rozszerzenie ISO 27001. Profil referencyjny: OpenAI posiada certyfikaty SOC 2 Typ II, ISO/IEC 27001:2022, ISO/IEC 27701:2019, zgodność z RODO/CCPA, HIPAA (oferuje umowy BAA), FERPA oraz PCI-DSS dla modułów płatniczych usługi ChatGPT. Mapowanie kontroli między różnymi standardami zmniejsza narzut pracy przy audytach: na przykład reguły kontroli dostępu można zmapować jednocześnie pod wymagania ISO 27001 A.5.15-5.18, art. 32 RODO oraz HIPAA §164.312(a).

**Typ:** Teoria / Nauka
**Języki:** (opcjonalnie Python — zgodność to polityka + proces, a nie kod)
**Wymagania wstępne:** Faza 17 · Lekcja 25 (Bezpieczeństwo), Faza 17 · Lekcja 13 (Obserwowalność)
**Czas:** ~60 minut

## Cele nauczania

- Wymień siedem standardów i ram regulacyjnych istotnych dla produktów opartych na LLM i dopasuj je do odpowiednich segmentów klientów.
- Przedstaw harmonogram wdrażania unijnego Aktu o sztucznej inteligencji (wejście w życie w sierpniu 2024 r., egzekwowanie przepisów dla systemów wysokiego ryzyka od sierpnia 2026 r.) oraz dwupoziomowy system kar (do 15 mln euro lub 3% obrotu za uchybienia przy systemach wysokiego ryzyka; do 35 mln euro lub 7% za praktyki zakazane).
- Wyjaśnij, dlaczego anonimizacja danych osobowych po przetworzeniu (post-processing scrubbing) jest niewystarczająca z punktu widzenia RODO, i uzasadnij wdrożenie maskowania danych w czasie rzeczywistym na poziomie bramy wnioskowania jako właściwego standardu.
- Opisz proces mapowania zabezpieczeń między różnymi standardami (np. mapowanie procedur kontroli dostępu pod wymagania ISO 27001 A.5.15-5.18, RODO art. 32 oraz HIPAA §164.312(a)).

## Problem

Klient korporacyjny w procesie zakupowym wymaga przedstawienia certyfikatów SOC 2 Typ II, zgodności z RODO, podpisania umowy HIPAA BAA, certyfikatu ISO 27001 oraz deklaracji zgodności z unijnym Aktem o sztucznej inteligencji. Twój zespół posiada jedynie SOC 2 Typ I, do uzyskania raportu Typu II pozostało jeszcze sześć miesięcy, a prace nad rejestrem czynności przetwarzania z art. 30 RODO nawet się nie rozpoczęły.

Zapewnienie zgodności z wieloma standardami nie jest problemem specyficznym wyłącznie dla LLM – to klasyczne wyzwanie dla systemów SaaS klasy enterprise, wzbogacone o specyfikę generatywnej sztucznej inteligencji. Działy zakupowe oczekują przejrzystych macierzy zgodności, w których wiersze reprezentują poszczególne standardy regulacyjne, a kolumny opisują wdrożone zabezpieczenia, zamiast ogólnych deklaracji w plikach PDF.

## Koncepcja

### Siedem struktur

| Standard regulacyjny | Zakres stosowania | Wymagania specyficzne dla LLM |
|----------|-------|---------------|
| SOC 2 Typ II | Podstawowy standard dla systemów B2B SaaS | Audyt weryfikujący skuteczne działanie zabezpieczeń przez okres 6-12 miesięcy |
| HIPAA | Rynek opieki zdrowotnej w USA | Wymagana umowa BAA; chronione dane zdrowotne (PHI) nie mogą opuścić infrastruktury bez formalnego porozumienia |
| RODO | Obsługa użytkowników w Unii Europejskiej | Maskowanie danych osobowych w czasie rzeczywistym; obsługa praw osób, których dane dotyczą (np. prawo do bycia zapomnianym); prowadzenie rejestru z art. 30 |
| PCI-DSS | Przetwarzanie danych kart płatniczych | Specjalna konfiguracja i zapisy umowne w przypadku integracji systemów AI z procesami płatniczymi |
| Akt o sztucznej inteligencji (EU AI Act) | Udostępnianie systemów AI na rynku UE | Klasyfikacja poziomów ryzyka; systemy wysokiego ryzyka wymagają formalnej oceny zgodności, dokumentacji technicznej i szczegółowego logowania zdarzeń |
| Colorado AI Act | Obsługa mieszkańców stanu Kolorado (USA) | Przeprowadzanie ocen wpływu (impact assessments); prawo użytkowników do odwołania od decyzji podjętych przez algorytm |
| ISO 42001 | Zarządzanie systemami AI w organizacji | Nowy standard wdrażany jako rozszerzenie systemu zarządzania bezpieczeństwem informacji (np. ISO 27001) |

### Harmonogram wdrażania Aktu o sztucznej inteligencji (EU AI Act)

- **1 sierpnia 2024 r.**: Wejście przepisów w życie.
- **2 lutego 2025 r.**: Początek egzekwowania zakazów dotyczących praktyk niedozwolonych.
- **2 sierpnia 2026 r.**: Wejście w życie obowiązków dla systemów wysokiego ryzyka (ocena zgodności, dokumentacja, logowanie).
- **Sierpień 2027 r.**: Obowiązki dla systemów wysokiego ryzyka wbudowanych w produkty podlegające innym unijnym przepisom harmonizacyjnym.

Poziomy ryzyka w EU AI Act: Niedopuszczalne (systemy zakazane), Wysokie ryzyko (wymagane wdrożenie procedur zgodności i rejestrowania zdarzeń), Ograniczone ryzyko (wymogi przejrzystości i informowania użytkownika), Minimalne ryzyko (brak dodatkowych ograniczeń). Większość systemów B2B LLM SaaS kwalifikuje się jako systemy o ograniczonym ryzyku. Kategoria wysokiego ryzyka ma zastosowanie przede wszystkim w obszarach rekrutacji, oceny zdolności kredytowej, edukacji, egzekwowania prawa, kontroli granicznej oraz zarządzania krytyczną infrastrukturą.

Kary finansowe (art. 99): do 15 mln euro lub 3% rocznego globalnego obrotu za naruszenie obowiązków dotyczących systemów wysokiego ryzyka (art. 99 ust. 4); do 35 mln euro lub 7% obrotu za stosowanie zabronionych praktyk (art. 99 ust. 3) – w zależności od tego, która z tych kwot jest wyższa.

### RODO — maskowanie danych w czasie rzeczywistym jako standard

Procedury usuwania danych osobowych wykonywane po fakcie (tj. po wysłaniu ich do zewnętrznego modelu LLM) są niemożliwe do obrony podczas audytu RODO – model zdążył już przetworzyć te dane. Prawidłowym standardem wdrożeń produkcyjnych jest maskowanie i anonimizacja danych w czasie rzeczywistym (real-time scrubbing) przed wyjściem zapytania poza sieć lokalną:

- Identyfikacja nazw własnych i encji (NER) na etapie przygotowywania zapytania.
- Zastosowanie spójnej tokenizacji (podejście typu mesh) w celu zachowania logicznych powiązań i semantyki w tekście.
- Zapisywanie w logach wyłącznie zanonimizowanych promptów i zachowanie jasnych rejestrów zgód użytkowników na przetwarzanie danych.

Przykłady egzekwowania przepisów: kara w wysokości 30,5 mln euro nałożona na Clearview AI przez holenderski organ ochrony danych (DPA) w wrześniu 2024 roku pozostaje najwyższą dotychczasową karą za naruszenia RODO w obszarze sztucznej inteligencji. Grzywna 15 mln euro nałożona na OpenAI przez włoskiego Garante w grudniu 2024 roku (uchylona w marcu 2026 roku po odwołaniu) pokazuje determinację organów regulacyjnych. Zapewnienia firm o usuwaniu danych "po fakcie" (post-processing scrubbing) były wielokrotnie odrzucane przez audytorów jako niezgodne z przepisami.

### HIPAA — umowa BAA jest obowiązkowa

Przesyłanie chronionych informacji zdrowotnych (PHI) do zewnętrznych dostawców modeli AI bez podpisania umowy o partnerstwie biznesowym (Business Associate Agreement - BAA) stanowi naruszenie prawa. Najwięksi dostawcy chmurowi (AWS Bedrock, Azure OpenAI, Google Vertex AI) oraz bezpośrednie API od OpenAI i Anthropic oferują możliwość zawarcia umowy BAA. Przed rozpoczęciem przetwarzania takich danych upewnij się, że umowa została formalnie podpisana.

### SOC 2 Typ II

Typ I: Audyt weryfikuje, czy zabezpieczenia zostały odpowiednio zaprojektowane i udokumentowane w danym punkcie w czasie.
Typ II: Audyt weryfikuje, czy wdrożone zabezpieczenia działały skutecznie w sposób ciągły przez okres od 6 do 12 miesięcy.

W procesach zakupowych B2B standardem jest raport Typu II. Raport Typu I traktowany jest jako rozwiązanie tymczasowe na start; do nawiązania współpracy z dużymi przedsiębiorstwami niezbędny jest raport Typu II.

Typowe dowody audytowe obejmują: logi dostępowe (kto i kiedy miał dostęp do danych), procedury zarządzania zmianą (w jaki sposób wdrażano kod), kwartalne oceny ryzyka oraz testy procedur reagowania na incydenty. Struktura dziennika audytu z Fazy 17 · Lekcji 25 może zostać bezpośrednio wykorzystana do spełnienia tych wymogów.

### Mapowanie zabezpieczeń między standardami (Cross-Mapping)

Jedna polityka kontroli dostępu spełnia wiele kontroli struktury:

| Wdrożone zabezpieczenie | Zgodne z wymaganiami standardów |
|--------|-----------|
| Logowanie i kontrola dostępu | ISO 27001 A.5.15-5.18, RODO art. 32, HIPAA §164.312(a) |
| Zarządzanie zmianami (Change management) | ISO 27001 A.8.32, wymagania PCI DSS 6, HIPAA Breach Notification Rules |
| Szyfrowanie danych w locie (in transit) | ISO 27001 A.8.24, RODO art. 32, HIPAA §164.312(e) |
| Bezpieczne zarządzanie sekretami | ISO 27001 A.8.19, wymagania PCI DSS 8, SOC 2 CC6.1 |

Platformy automatyzujące procesy zgodności (takie jak Drata, Vanta czy Secureframe) automatycznie mapują te zabezpieczenia. Przy dużej skali działalności inwestycja w nie szybko się zwraca.

### ISO 42001 — nowy standard

Standard opublikowany pod koniec 2023 roku, coraz częściej pojawiający się jako warunek w dużych przetargach obok normy ISO 27001. Definiuje on ramy zarządzania systemami AI, w tym procedury analizy ryzyka, dbałość o jakość danych uczących, przejrzystość algorytmów oraz nadzór człowieka.

### Profil zgodności OpenAI jako punkt odniesienia

OpenAI posiada certyfikaty SOC 2 Typ II, ISO/IEC 27001:2022, ISO/IEC 27701:2019, deklaruje zgodność z RODO/CCPA, oferuje umowy HIPAA BAA, spełnia FERPA oraz PCI-DSS dla modułów płatniczych ChatGPT. Pokazuje to poziom wymagań, jakich należy się spodziewać przy współpracy z dużym biznesem.

### Kluczowe dane do zapamiętania

- Kary w EU AI Act: do 15 mln euro lub 3% obrotu (naruszenie obowiązków wysokiego ryzyka, art. 99 ust. 4); do 35 mln euro lub 7% obrotu (stosowanie praktyk zakazanych, art. 99 ust. 3).
- Wejście w życie obowiązków wysokiego ryzyka w EU AI Act: 2 sierpnia 2026 roku.
- Najwyższa dotychczasowa kara za naruszenie RODO przez systemy AI: 30,5 mln euro (Clearview AI, wrzesień 2024 r.).
- Najwyższa kara RODO nałożona bezpośrednio na twórców LLM: 15 mln euro (OpenAI, grudzień 2024 r., uchylona w marcu 2026 r.).
- Minimalny okres obserwacji w audycie SOC 2 Typ II: 6-12 miesięcy ciągłego działania zabezpieczeń.
- Wejście w życie Colorado AI Act: 30 czerwca 2026 roku (przesunięte ustawą SB25B-004).

## Kod demonstracyjny

Skrypt `code/main.py` przedstawia weryfikator zgodności napisany w Pythonie – na podstawie wprowadzonych zabezpieczeń generuje on wykaz standardów regulacyjnych, których wymagania zostały spełnione.

## Rezultat zadania

W ramach tej lekcji powstanie plik `outputs/skill-compliance-matrix.md`. Na podstawie segmentu obsługiwanych klientów oraz rynków geograficznych definiuje on niezbędne standardy regulacyjne i odpowiadające im mechanizmy kontrolne.

## Ćwiczenia

1. Twój pierwszy kluczowy klient korporacyjny wymaga przedstawienia raportu SOC 2 Typ II, podpisania umowy HIPAA BAA oraz deklaracji zgodności z EU AI Act. Jaki jest minimalny zestaw zabezpieczeń, który musisz wdrożyć, aby móc sfinalizować tę transakcję?
2. Sklasyfikuj trzy wybrane hipotetyczne produkty oparte na LLM według kategorii ryzyka zdefiniowanych w unijnym Akcie o sztucznej inteligencji. Jakie dodatkowe obowiązki powstaną, jeśli produkt zostanie uznany za system wysokiego ryzyka?
3. Wykryto omyłkowe przesłanie chronionych danych zdrowotnych (PHI) do dostawcy API, z którym nie podpisano umowy BAA. Opracuj plan reagowania na ten incydent bezpieczeństwa.
4. Rozważ, czy certyfikacja ISO 42001 jest w 2026 roku niezbędnym krokiem biznesowym dla średniej wielkości dostawcy usług AI.
5. Dokonaj mapowania pól z dziennika audytu LLM (zaprojektowanego w Fazie 17 · Lekcji 25) na wymagania co najmniej trzech różnych standardów zgodności.

## Słownik pojęć

| Termin | Jak się potocznie mówi | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| SOC 2 Typ II | „certyfikat bezpieczeństwa SaaS” | Raport z niezależnego audytu weryfikujący ciągłą skuteczność zabezpieczeń przez 6-12 miesięcy |
| HIPAA BAA | „umowa medyczna” | Business Associate Agreement – obligatoryjna umowa przy przetwarzaniu chronionych danych zdrowotnych (PHI) |
| RODO / GDPR | „unijne prawo o ochronie danych” | Europejskie rozporządzenie; wdrożenie maskowania danych w czasie rzeczywistym jest jedynym bezpiecznym standardem dla systemów AI |
| Akt o sztucznej inteligencji (EU AI Act) | „unijna ustawa o AI” | Unijne rozporządzenie klasyfikujące systemy AI; egzekwowanie kar (do 15/35 mln euro) oraz wymogów wysokiego ryzyka od sierpnia 2026 r. |
| Colorado AI Act | „prawo stanowe Kolorado o AI” | Amerykańska ustawa stanowa wchodząca w życie 30 czerwca 2026 r., wprowadzająca obowiązkowe oceny wpływu systemów AI |
| ISO 42001 | „zarządzanie AI” | Międzynarodowa norma definiująca System Zarządzania Sztuczną Inteligencją w organizacji |
| ISO 27001 | „certyfikat ISO bezpieczeństwa” | Międzynarodowy standard wdrożenia Systemu Zarządzania Bezpieczeństwem Informacji (SZBI) |
| Ocena zgodności (Conformity Assessment) | „audyt unijny AI” | Wymóg dla systemów wysokiego ryzyka obejmujący opracowanie dokumentacji technicznej, testy i logowanie |
| Mapowanie zabezpieczeń (Cross-mapping) | „jeden proces, wiele certyfikatów” | Technika pozwalająca na spełnienie wymagań wielu standardów regulacyjnych za pomocą jednego wdrożonego procesu |

## Materiały uzupełniające

- [OpenAI Security and Privacy](https://openai.com/security-and-privacy/) — referencyjny profil zgodności.
- [GuardionAI — zgodność LLM 2026: ISO 42001, ustawa UE o sztucznej inteligencji, SOC 2, RODO](https://guardion.ai/blog/llm-compliance-guide-iso-42001-eu-ai-act-soc2-gdpr-2026)
- [Dsalta — Przewodnik audytu typu 2 SOC 2 2026: 10 kontroli AI](https://www.dsalta.com/resources/ai-compliance/soc-2-type-2-audit-guide-2026-10-ai-powered-controls-every-saas-team-needs)
- [oficjalny tekst unijnego aktu o sztucznej inteligencji](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) – źródło pierwotne.
- [Ustawa Kolorado o sztucznej inteligencji](https://leg.colorado.gov/bills/sb24-205) – źródło główne.
- [ISO/IEC 42001:2023](https://www.iso.org/standard/81230.html) – norma dotycząca systemu zarządzania sztuczną inteligencją.
