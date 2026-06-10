# Bezpieczeństwo — tajemnice, rotacja kluczy API, dzienniki audytu, poręcze

> Wyeliminuj rozprzestrzenianie się sekretów za pomocą scentralizowanych skarbców (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault). Nigdy nie przechowuj poświadczeń w plikach konfiguracyjnych, plikach env w VCS, arkuszach kalkulacyjnych. Używaj ról IAM zamiast kluczy statycznych; OIDC dla CI/CD. Wzorzec bramy AI to rozwiązanie na rok 2026: aplikacje → brama → dostawca modelu, z bramą pobierającą poświadczenia z skarbca w czasie wykonywania. Obróć w skarbcu, a wszystkie aplikacje zostaną uruchomione w ciągu kilku minut — bez konieczności ponownego wdrażania, bez komunikatów Slack „kto ma nowy klucz”. Polityka rotacji ≤90 dni; skanuj za pomocą TruffleHog / GitGuardian / Gitleaks przy każdym zatwierdzeniu. Zero zaufania: MFA, SSO, RBAC/ABAC, tokeny krótkotrwałe, stan urządzenia. Czyszczenie PII wykorzystuje rozpoznawanie podmiotów do maskowania PHI/PII przed przekazaniem; spójna tokenizacja (podejście Mesh) odwzorowuje wrażliwe wartości na stabilne symbole zastępcze, dzięki czemu LLM zachowuje semantykę kodu/relacji. Wyjście z sieci: usługi LLM w dedykowanej białej liście podsieci VPC/VNet `api.openai.com`, `api.anthropic.com` itp.; blokuj wszystkie inne połączenia wychodzące. Czynnikiem powodującym incydent w 2026 r.: Atak na łańcuch dostaw firmy Vercel za pomocą naruszonych danych uwierzytelniających CI/CD wydobył środowisko z tysięcy wdrożeń u klientów.

**Typ:** Ucz się
**Języki:** Python (stdlib, zabawka PII-scruber + zapis dziennika audytu)
**Wymagania wstępne:** Faza 17 · 19 (Bramy AI), Faza 17 · 13 (Obserwowalność)
**Czas:** ~60 minut

## Cele nauczania

- Wymień cztery antywzorce zarządzania sekretami (pliki konfiguracyjne w VCS, zakodowane na stałe env, arkusze kalkulacyjne, klucze statyczne) i nazwij ich zamienniki.
- Wyjaśnij wzorzec pobierania bram AI ze skarbca jako standard produkcyjny na rok 2026.
- Zaimplementuj skruber PII ze spójną tokenizacją (ta sama wartość → ten sam symbol zastępczy), aby semantyka przetrwała.
- Wymień incydent w łańcuchu dostaw Vercel z 2026 r. i czego on nauczył na temat higieny poświadczeń CI/CD.

## Problem

Stażysta zatwierdza `.env` za pomocą kluczy API. Szybko to usuwają. Klucze są już w historii Git — wychwytuje je skanowanie GitGuardian, proces rotacji wygląda następująco: „Zwolnij zespół, zaktualizuj 40 plików konfiguracyjnych, ponownie wdróż wszystkie usługi”. 8 godzin później połowa usług jest już aktywna, a połowa czeka na wdrożenie systemu Windows.

Oddzielnie monity użytkownika obejmują „Mój numer SSN to 123-45-6789”. Monit trafia do OpenAI. Masz umowę BAA, ale zgodnie z Twoją wewnętrzną polityką maskujesz dane osobowe przed przekazaniem dalej. Nie zrobiłeś tego.

Oddzielnie moduł LLM klastra EKS może uzyskać dostęp do dowolnego hosta internetowego. Ktoś eksportuje dane poprzez wyszukiwanie DNS do domeny kontrolowanej przez osobę atakującą. Nic tego nie blokowało.

Bezpieczeństwo usług LLM musi uwzględniać wszystkie trzy wektory. Poświadczenia obsługiwane przez Vault. Szorowanie PII. Filtrowanie ruchu wychodzącego z sieci. Dzienniki audytu.

## Koncepcja

### Scentralizowany skarbiec + ściąganie roli IAM

**Sejf**: HashiCorp Vault, Menedżer sekretów AWS, Azure Key Vault, Menedżer tajnych obiektów GCP. Jedno źródło prawdy.

**Rola IAM**: aplikacja/brama uwierzytelnia się za pomocą swojej tożsamości IAM, a nie klucza statycznego. Vault zwraca sekret przez cały okres istnienia tokena.

**Wzorzec bramy AI**: brama pobiera `OPENAI_API_KEY` ze skarbca w momencie żądania. Obróć w skarbcu; następne żądanie otrzyma nowy klucz. Żadnych ponownych wdrożeń.

### Polityka rotacji ≤ 90 dni

Wszystkie klucze API, tokeny główne skarbca, poświadczenia CI/CD. Tam, gdzie to możliwe, automatyczna rotacja. Ręczny obrót jest rejestrowany i śledzony.

### Tajne skanowanie

- **TruffleHog** — wyrażenie regularne + entropia przy zatwierdzeniach.
- **GitGuardian** — komercyjny, wysoka dokładność.
- **Gitleaks** — OSS, działa w CI.

Uruchamiaj przy każdym zatwierdzeniu. Zablokuj PR, jeśli wykryty zostanie nowy sekret.

### Postawa zerowego zaufania

- Wymagana pomoc MFA na wszystkich kontach.
- Logowanie jednokrotne poprzez SAML/OIDC.
- RBAC (oparty na rolach) lub ABAC (oparty na atrybutach) dla dostępu szczegółowego.
- Tokeny krótkotrwałe (godziny, nie dni).
- Stan urządzenia — tylko urządzenia korporacyjne z szyfrowaniem dysku.

### Czyszczenie PII/PHI

Zanim monit opuści infra:

1. Rozpoznanie podmiotu (spaCy NER, Presidio, komercyjny).
2. Zamaskuj dopasowane elementy: `"My SSN is 123-45-6789"` → `"My SSN is [SSN_TOKEN_A3F]"`.
3. Spójna tokenizacja (podejście Mesh): ta sama wartość jest odwzorowywana na ten sam symbol zastępczy, dzięki czemu LLM zachowuje relacje.
4. Opcjonalne mapowanie odwrotne dla odpowiedzi LLM.

Statyczne filtry wyrażeń regularnych wyłapują podstawowe wzorce; NER łapie więcej. Użyj obu.

### Poręcze wejściowe i wyjściowe

Wejście: blokuj znane jailbreaki, zabronione tematy; limit stawek na użytkownika.

Dane wyjściowe: czyszczenie wyrażeń regularnych pod kątem wyciekających tajemnic (wzorce kluczy API, wzorce wiadomości e-mail w kontekstach odmowy), klasyfikator naruszeń zasad.

### Biała lista ruchu wychodzącego z sieci

Usługi LLM w dedykowanej podsieci:
- Biała lista: `api.openai.com`, `api.anthropic.com`, punkty końcowe wektorowej bazy danych, punkty końcowe skarbca.
- Wszystko inne: upuść.
- DNS za pośrednictwem narzędzia rozpoznawania nazw dostępnego tylko na liście dozwolonych (unikaj exfil tunelowania DNS).

### Dziennik audytu

Niezmienny dziennik każdego połączenia LLM z:
- Znacznik czasu.
- Użytkownik / najemca.
- Hash podpowiedzi (nie surowy monit o prywatność).
- Model + wersja.
- Liczy się token.
- Koszt.
- Hash odpowiedzi.
- Wszelkie wycieczki po poręczach.

Zachowaj zgodnie z wymogami regulacyjnymi (SOC 2 1 rok, HIPAA 6 lat).

### Incydent w Vercel w 2026 r

Atak na łańcuch dostaw: złamane dane uwierzytelniające CI/CD wyciekły z tysięcy wdrożeń klientów. Lekcja: Poświadczenia CI/CD są równoważne produktom. Przechowuj w skarbcu. Zakres wąsko. Obracaj agresywnie.

### Liczby, które powinieneś zapamiętać

- Polityka rotacji: ≤ 90 dni.
- Skanuj przy każdym zatwierdzeniu: TruffleHog / GitGuardian / Gitleaks.
- Vercel 2026: naruszenia wiarygodności CI/CD → wyciekły tysiące danych środowiskowych klientów.
- Przechowywanie dziennika audytu: SOC 2 = 1 rok, HIPAA = 6 lat.

## Użyj tego

`code/main.py` implementuje narzędzie do analizowania danych osobowych w zabawkach ze spójną tokenizacją i dziennikiem kontrolnym umożliwiającym tylko dołączanie.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-llm-security-plan.md`. Biorąc pod uwagę zakres przepisów i bieżący stan, planuje migrację skarbca, skruber, wyjście, dziennik audytu.

## Ćwiczenia

1. Uruchom `code/main.py`. Wyślij dwa monity odwołujące się do tego samego numeru SSN. Potwierdź, że oba otrzymają ten sam symbol zastępczy.
2. Zaprojektuj politykę ruchu wychodzącego sieci dla wdrożenia vLLM-on-EKS wywołującego OpenAI + Anthropic + Weaviate.
3. Odkrywasz klucz w historii gita (2 lata). Jaka jest prawidłowa reakcja — obróć klucz, przeczyść historię, a może jedno i drugie? Uzasadniać.
4. Twój dziennik audytu powiększa się o 10 GB/dzień. Poziomy przechowywania projektu (gorący 30 dni, ciepły 12 miesięcy, zimny 6 lat).
5. Przekonaj się, czy odwrotna tokenizacja (podstawienie wartości rzeczywistych z powrotem do odpowiedzi LLM) jest warta złożoności w porównaniu z utrzymywaniem widoczności symboli zastępczych.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Skarbiec | „sklep tajemnic” | Scentralizowana usługa zarządzania danymi uwierzytelniającymi |
| Rola IAM | „autoryzacja oparta na tożsamości” | Rola przyjmowana przez aplikację; zwraca krótkotrwałe kredyty |
| OIDC dla CI/CD | „tokeny wydawane w chmurze” | Brak kluczy statycznych w CI — tożsamość poprzez OIDC |
| TruffleHog / GitGuardian / Gitleaks | „tajne skanery” | Wykrywanie sekretu w czasie zatwierdzenia |
| RBAC / ABAC | „kontrola dostępu” | Oparte na rolach a oparte na atrybutach |
| Oczyszczanie danych osobowych | „maskowanie danych” | Usuń lub tokenizuj wrażliwe podmioty |
| Konsekwentna tokenizacja | „stabilne elementy zastępcze” | Ta sama wartość → ten sam token za każdym razem |
| Podejście siatkowe | „Tokenizacja siatki” | Wzorzec tokenizacji zachowujący semantykę |
| Biała lista wyjść | „lista dozwolonych połączeń wychodzących” | Dostępne tylko dozwolone domeny |
| Dziennik audytu | „niezmienna historia” | Rekord umożliwiający tylko dołączenie w celu zapewnienia zgodności |

## Dalsze czytanie

— [Doppler — zaawansowane zabezpieczenia LLM](https://www.doppler.com/blog/advanced-llm-security)
- [Portkey — Zarządzaj kluczami API LLM za pomocą tajnych referencji](https://portkey.ai/blog/secret-references-ai-api-key-management/)
— [Datadog — najlepsze praktyki dotyczące poręczy LLM] (https://www.datadoghq.com/blog/llm-guardrails-best-practices/)
— [JumpServer — najlepsze praktyki w zakresie zarządzania tajemnicami, 2026 r.](https://www.jumpserver.com/blog/secret-management-best-practices-2026)
- [Microsoft Presidio](https://github.com/microsoft/presidio) — wykrywanie i anonimizacja danych osobowych.
- [Dokumentacja Vault HashiCorp](https://developer.hashicorp.com/vault/docs)