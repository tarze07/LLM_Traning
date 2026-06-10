# Bezpieczeństwo — zarządzanie sekretami, rotacja kluczy API, dzienniki audytu i filtry bezpieczeństwa

> Wyeliminuj problem rozproszonych sekretów (secrets sprawl) za pomocą scentralizowanych systemów przechowywania (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault). Nigdy nie przechowuj poświadczeń w plikach konfiguracyjnych, plikach środowiskowych (.env) w systemie kontroli wersji (VCS) ani w arkuszach kalkulacyjnych. Wykorzystuj role IAM zamiast kluczy statycznych oraz tożsamości OIDC w potokach CI/CD. Nowoczesnym standardem staje się wzorzec bramy AI (AI gateway): aplikacja komunikuje się z bramą, a ta przesyła zapytanie do dostawcy modelu, pobierając niezbędne klucze ze skarbca dynamicznie w czasie wykonywania (runtime). Zmiana klucza w skarbcu powoduje, że wszystkie aplikacje zaczynają z niego korzystać w ciągu kilku minut – bez potrzeby ponownego wdrażania usług czy szukania informacji na Slacku. Wprowadź politykę rotacji kluczy co maksymalnie 90 dni i skanuj kod za pomocą narzędzi TruffleHog, GitGuardian lub Gitleaks przy każdym commicie. Wdrożenie architektury Zero Trust wymaga stosowania uwierzytelniania wieloskładnikowego (MFA), logowania jednokrotnego (SSO), kontroli dostępu RBAC/ABAC, krótkoterminowych tokenów oraz weryfikacji stanu urządzeń (device health). Anonimizacja danych osobowych (PII/PHI) powinna opierać się na rozpoznawaniu nazw własnych (Named Entity Recognition - NER) do maskowania wrażliwych informacji przed ich wysłaniem. Spójna tokenizacja (podejście typu mesh) mapuje te same poufne wartości na stabilne symbole zastępcze, co pozwala modelowi LLM zachować kontekst i strukturę relacji w danych. W obszarze bezpieczeństwa sieciowego umieść usługi LLM w dedykowanej podsieci VPC/VNet i zezwalaj na ruch wychodzący wyłącznie do zdefiniowanych adresów (np. `api.openai.com`, `api.anthropic.com`), blokując wszystkie inne połączenia. Głośnym incydentem bezpieczeństwa stał się atak na łańcuch dostaw Vercel, w którym przejęte poświadczenia CI/CD posłużyły do kradzieży zmiennych środowiskowych z tysięcy wdrożeń klientów.

**Typ:** Teoria / Nauka
**Języki:** Python (stdlib, uproszczony skruber PII + dziennik audytu w trybie append-only)
**Wymagania wstępne:** Faza 17 · Lekcja 19 (Bramy AI), Faza 17 · Lekcja 13 (Obserwowalność)
**Czas:** ~60 minut

## Cele nauczania

- Wymień cztery antywzorce w zarządzaniu sekretami (pliki konfiguracyjne w repozytorium VCS, zakodowane zmienne środowiskowe, arkusze kalkulacyjne, statyczne klucze dostępowe) i wskaż ich bezpieczne alternatywy.
- Wyjaśnij wzorzec integracji bramy AI ze skarbcem sekretów jako standard wdrożeń produkcyjnych.
- Zaimplementuj mechanizm anonimizacji (scrubber) PII ze spójną tokenizacją (mapowanie tej samej wartości na ten sam symbol zastępczy) w celu zachowania spójności semantycznej.
- Przywołaj incydent bezpieczeństwa w łańcuchu dostaw Vercel i opisz płynące z niego wnioski dotyczące higieny poświadczeń w procesach CI/CD.

## Problem

Praktykant omyłkowo commituje plik `.env` z kluczami API do repozytorium. Szybko go usuwa, ale klucze pozostają w historii systemu Git. Wykrywa je skaner GitGuardian, co wymusza procedurę awaryjnej rotacji kluczy: zespół przerywa bieżącą pracę, musi zaktualizować kilkadziesiąt plików konfiguracyjnych i ponownie wdrożyć wszystkie powiązane usługi. Osiem godzin później część z nich nadal nie została poprawnie zaktualizowana.

Inny przypadek: zapytanie użytkownika (prompt) zawiera poufny numer identyfikacyjny (np. PESEL lub SSN). Zapytanie to trafia w niezmienionej formie do zewnętrznego API OpenAI. Choć posiadasz odpowiednie umowy o poufności (np. BAA), wewnętrzna polityka bezpieczeństwa nakazuje maskowanie danych osobowych przed ich wysłaniem z własnej sieci. W tym przypadku procedura ta nie zadziałała.

Kolejny scenariusz: kontener z aplikacją LLM w klastrze Kubernetes (EKS) ma nieograniczony dostęp do sieci zewnętrznej. Atakujący wykorzystuje to do eksfiltracji wrażliwych danych za pomocą tunelowania zapytań DNS (DNS tunneling) do kontrolowanej przez siebie domeny. Brak odpowiednich filtrów sieciowych uniemożliwił zablokowanie tego wycieku.

Bezpieczeństwo usług opartych na LLM musi adresować wszystkie trzy wektory: zarządzanie poświadczeniami przez skarbiec, maskowanie danych osobowych (PII/PHI) oraz restrykcyjne filtrowanie ruchu wychodzącego, a także prowadzenie niezmiennych dzienników audytu.

## Koncepcja

### Scentralizowany skarbiec + pobieranie poświadczeń przez rolę IAM

**Skarbiec (Vault)**: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager. Stanowią one jedyne źródło prawdy (Single Source of Truth) dla poświadczeń.

**Rola IAM**: Aplikacja lub brama AI uwierzytelnia się za pomocą tożsamości IAM, a nie statycznego klucza. Skarbiec zwraca tymczasowy sekret powiązany z czasem życia tokenu.

**Wzorzec bramy AI**: Brama pobiera klucz `OPENAI_API_KEY` ze skarbca dynamicznie podczas obsługi zapytania. Zmiana klucza w skarbcu sprawia, że kolejne zapytania natychmiast korzystają z nowej wartości bez konieczności restartu usług.

### Polityka rotacji kluczy co ≤ 90 dni

Dotyczy to wszystkich kluczy API, głównych tokenów dostępowych skarbca oraz poświadczeń CI/CD. W miarę możliwości należy stosować automatyczną rotację, a każda ręczna zmiana musi być rejestrowana.

### Sanimowanie w poszukiwaniu wycieków sekretów

- **TruffleHog** – narzędzie analizujące wyrażenia regularne i entropię tekstu podczas zatwierdzania zmian.
- **GitGuardian** – zaawansowane narzędzie komercyjne o wysokiej skuteczności.
- **Gitleaks** – narzędzie Open Source zintegrowane bezpośrednio z potokiem CI.

Skanowanie powinno być uruchamiane przy każdym zatwierdzeniu kodu (commit). Jeśli system wykryje wgranie sekretu, powinien zablokować Pull Request.

### Podejście Zero Trust

- Wymuszona weryfikacja wieloskładnikowa (MFA) dla wszystkich kont użytkowników i administratorów.
- Wdrożenie logowania jednokrotnego (SSO) w oparciu o protokoły SAML/OIDC.
- Zastosowanie mechanizmów RBAC (Role-Based) lub ABAC (Attribute-Based Access Control) do precyzyjnego zarządzania uprawnieniami.
- Stosowanie tokenów o krótkim okresie ważności (liczonych w godzinach, a nie w dniach).
- Weryfikacja stanu urządzeń (device posture) – dopuszczanie wyłącznie urządzeń służbowych z włączonym szyfrowaniem dysków.

### Anonimizacja i oczyszczanie danych PII/PHI

Zanim zapytanie opuści infrastrukturę wewnętrzną:

1. Wykrywanie nazw własnych i encji (np. spaCy NER, Microsoft Presidio lub rozwiązania komercyjne).
2. Zamaskuj dopasowane elementy: `"My SSN is 123-45-6789"` → `"My SSN is [SSN_TOKEN_A3F]"`.
3. Spójna tokenizacja (podejście typu mesh): mapowanie tej samej oryginalnej wartości na ten sam unikalny token (symbol zastępczy) w ramach sesji, co pozwala modelowi LLM zachować kontekst i logiczne powiązania w tekście.
4. Opcjonalne odwrócenie procesu (detokenizacja) przy prezentowaniu odpowiedzi z modelu LLM.

Filtry oparte na wyrażeniach regularnych (regex) dobrze radzą sobie z ustrukturyzowanymi wzorcami (np. numery identyfikacyjne), natomiast algorytmy NER lepiej wykrywają nazwy własne czy kontekstualne dane osobowe. Najlepsze efekty daje połączenie obu tych metod.

### Filtry bezpieczeństwa na wejściu i wyjściu (Guardrails)

Wejście (input): blokowanie prób jailbreaku (manipulacji modelem), filtrowanie zabronionych tematów oraz limitowanie częstotliwości zapytań (rate limiting) na użytkownika.

Wyjście (output): skanowanie wygenerowanego tekstu pod kątem wycieku sekretów (np. wzorce kluczy API lub wrażliwe dane w komunikatach o odmowie) oraz klasyfikacja pod kątem zgodności z politykami organizacji.

### Biała lista połączeń wychodzących (Egress Filtering)

Umieść usługi LLM w dedykowanej podsieci:
- Biała lista: `api.openai.com`, `api.anthropic.com`, adresy baz wektorowych oraz skarbca.
- Pozostały ruch wychodzący: całkowicie blokowany (drop).
- Obsługa zapytań DNS wyłącznie przez zatwierdzone serwery nazw, aby zapobiec eksfiltracji danych przez tunelowanie DNS.

### Dzienniki audytu (Audit Logs)

Niezmienny i chroniony przed modyfikacją rejestr każdego zapytania do LLM zawierający:
- Znacznik czasu.
- Identyfikator użytkownika lub organizacji (tenant).
- Skrót (hash) promptu wejściowego (zamiast pełnego tekstu, w celu ochrony prywatności).
- Użyty model oraz jego wersję.
- Liczbę przetworzonych tokenów.
- Koszt operacji.
- Skrót (hash) wygenerowanej odpowiedzi.
- Rejestr wszelkich zdarzeń naruszenia filtrów bezpieczeństwa.

Dane należy przechowywać zgodnie z wymogami regulacyjnymi (np. minimum rok dla SOC 2, 6 lat dla regulacji HIPAA).

### Incydent bezpieczeństwa Vercel

Podczas tego ataku przejęcie poświadczeń w potokach CI/CD doprowadziło do kradzieży poufnych danych konfiguracyjnych tysięcy klientów. Wnioski: Poświadczenia w CI/CD mają krytyczne znaczenie dla bezpieczeństwa produkcji. Należy przechowywać je w skarbcu, nadawać im minimalne niezbędne uprawnienia i regularnie je rotować.

### Kluczowe dane do zapamiętania

- Cykl rotacji kluczy: co maksymalnie 90 dni.
- Skanowanie przy każdym commicie: TruffleHog / GitGuardian / Gitleaks.
- Incydent Vercel: przejęcie poświadczeń CI/CD wywołało wyciek zmiennych środowiskowych u tysięcy klientów.
- Czas przechowywania logów audytowych: SOC 2 = minimum 1 rok, HIPAA = 6 lat.

## Kod demonstracyjny

Skrypt `code/main.py` przedstawia uproszczoną implementację maskowania danych osobowych (PII) za pomocą spójnej tokenizacji oraz logowania zdarzeń do dziennika audytowego w trybie append-only.

## Rezultat zadania

W ramach tej lekcji powstanie plik `outputs/skill-llm-security-plan.md`. Uwzględniając wymagania regulacyjne i stan obecny systemu, definiuje on plan migracji do skarbca, implementację maskowania danych, filtrację sieciową oraz strukturę dziennika audytu.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Wyślij dwa zapytania zawierające ten sam numer SSN. Upewnij się, że w obu przypadkach został przypisany identyczny token zastępczy.
2. Zaprojektuj politykę filtracji ruchu wychodzącego (egress filtering) dla instancji vLLM wdrożonej w klastrze EKS, komunikującej się z API OpenAI, Anthropic oraz bazą Weaviate.
3. Wykryto obecność klucza API w historii systemu Git sprzed dwóch lat. Jaka powinna być prawidłowa reakcja – rotacja klucza, wyczyszczenie historii Git, czy obie te akcje? Przedstaw uzasadnienie.
4. Dziennik audytu przyrasta w tempie 10 GB dziennie. Zaprojektuj strategię przechowywania logów w podziale na warstwy: gorącą (hot - 30 dni), ciepłą (warm - 12 miesięcy) oraz zimną (cold - 6 lat).
5. Rozważ zalety i wady detokenizacji (podmieniania tokenów zastępczych na oryginalne wartości w odpowiedzi modelu LLM). Czy jest ona warta dodatkowej złożoności implementacyjnej w porównaniu z prezentowaniem użytkownikowi zamaskowanego tekstu?

## Słownik pojęć

| Termin | Jak się potocznie mówi | Co to dokładnie oznacza |
|------|----------------|--------------------------------------|
| Skarbiec (Vault) | „magazyn sekretów” | Scentralizowany system do bezpiecznego przechowywania poświadczeń i kluczy |
| Rola IAM | „uprawnienia dla tożsamości” | Krótkoterminowe uprawnienia nadawane dynamicznie aplikacji bez użycia klucza statycznego |
| OIDC w CI/CD | „bezkluczykowe CI/CD” | Eliminacja statycznych sekretów w potokach CI na rzecz autoryzacji opartej o federację tożsamości OIDC |
| Skanery sekretów | „wykrywacze kluczy w kodzie” | Narzędzia do automatycznego wyszukiwania haseł i kluczy w repozytorium kodu |
| RBAC / ABAC | „zarządzanie dostępem” | Kontrola dostępu oparta odpowiednio na zdefiniowanych rolach użytkownika lub na dynamicznych atrybutach |
| Maskowanie danych (scrubbing) | „wycinanie PII” | Proces usuwania lub zastępowania poufnych informacji w tekście |
| Spójna tokenizacja | „powtarzalne maski” | Mechanizm mapowania identycznych danych wrażliwych na ten sam token w ramach sesji |
| Podejście typu mesh | „mapowanie semantyczne” | Architektura tokenizacji pozwalająca modelom LLM poprawnie interpretować relacje logiczne bez dostępu do danych jawnych |
| Egress Filtering | „blokada wyjścia z sieci” | Ograniczenie połączeń wychodzących z infrastruktury wyłącznie do autoryzowanych adresów URL |
| Dziennik audytu (Audit Log) | „logi bezpieczeństwa” | Niezmienny rejestr zdarzeń i zapytań (typu append-only) służący celom bezpieczeństwa i zgodności |

## Materiały uzupełniające

- [Doppler — zaawansowane zabezpieczenia LLM](https://www.doppler.com/blog/advanced-llm-security)
- [Portkey — Zarządzaj kluczami API LLM za pomocą tajnych referencji](https://portkey.ai/blog/secret-references-ai-api-key-management/)
- [Datadog — najlepsze praktyki dotyczące poręczy LLM](https://www.datadoghq.com/blog/llm-guardrails-best-practices/)
- [JumpServer — najlepsze praktyki w zakresie zarządzania tajemnicami, 2026 r.](https://www.jumpserver.com/blog/secret-management-best-practices-2026)
- [Microsoft Presidio](https://github.com/microsoft/presidio) — wykrywanie i anonimizacja danych osobowych.
- [Dokumentacja Vault HashiCorp](https://developer.hashicorp.com/vault/docs)
