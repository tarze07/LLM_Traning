---

name: llm-security-plan
description: Przygotuj plan bezpieczeństwa dla systemów LLM obejmujący wdrożenie skarbca sekretów, anonimizację danych osobowych (PII) ze spójną tokenizacją, białą listę połączeń wychodzących (egress), przechowywanie dzienników audytu oraz architekturę Zero Trust.
version: 1.0.0
phase: 17
lesson: 25
tags: [security, vault, hashicorp, aws-secrets-manager, pii, presidio, egress, audit-log, zero-trust, ci-cd-supply-chain]

---

Na podstawie wymogów regulacyjnych (SOC 2, HIPAA, RODO), bieżącego sposobu zarządzania poświadczeniami oraz konfiguracji sieci i ruchu wychodzącego, przygotuj plan bezpieczeństwa.

Wygeneruj:

1. Migracja do skarbca: Wybierz system przechowywania sekretów (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager). Zastosuj wzorzec bramy AI (aplikacje -> brama AI -> skarbiec w runtime). Wycofaj zakodowane na stałe poświadczenia w plikach środowiskowych (.env) i plikach konfiguracyjnych.
2. Skanowanie kodu: Uruchom skanowanie za pomocą TruffleHog, GitGuardian lub Gitleaks przy każdym commicie. Blokuj zatwierdzanie Pull Requestów w przypadku wykrycia sekretu.
3. Polityka rotacji: Co maksymalnie 90 dni, w miarę możliwości w pełni zautomatyzowana. Wprowadź bardziej rygorystyczny cykl rotacji dla poświadczeń CI/CD (np. co 30 dni).
4. Anonimizacja PII: Wykrywanie nazw własnych (Microsoft Presidio + wyrażenia regularne). Zastosuj spójną tokenizację (mapowanie tej samej poufnej wartości na ten sam symbol zastępczy) w celu zachowania kontekstu semantycznego.
5. Filtrowanie ruchu wychodzącego (Egress): Add do białej listy domeny dostawców API LLM, baz wektorowych oraz skarbca. Skonfiguruj zapytania DNS wyłącznie przez zatwierdzony serwer nazw.
6. Dziennik audytu: Rejestr typu append-only (niemożliwy do zmodyfikowania). Wymagane pola: użytkownik, najemca (tenant), hash promptu/odpowiedzi, liczba tokenów, koszt, historia naruszeń filtrów bezpieczeństwa. Czas przechowywania logów dobierz do standardów (np. 1 rok dla SOC 2, 6 lat dla HIPAA).
7. Higiena CI/CD: Wprowadź federację tożsamości OIDC (brak statycznych kluczy chmurowych w CI/CD). Ogranicz uprawnienia dla potoków CI/CD do niezbędnego minimum. Jako uzasadnienie biznesowe przywołaj incydent bezpieczeństwa w łańcuchu dostaw Vercel.

Kryteria odrzucenia planu (Hard rejects):
- Przechowywanie statycznych kluczy w plikach konfiguracyjnych: Odrzuć.
- Zapisywanie pełnej, surowej treści promptów w dzienniku audytu: Odrzuć – dozwolone jest zapisywanie wyłącznie skrótu (hash), chyba że przepisy regulacyjne stanowią inaczej.
- Zezwalanie na nieograniczony ruch wychodzący (np. do gwiazdki `*` lub całego internetu): Odrzuć – wymagaj ścisłej białej listy (egress filtering).

Zasady odrzucenia:
- Jeśli architektura klienta wymaga całkowitej izolacji sieciowej (air-gapped) i nie dopuszcza zewnętrznego skarbca sekretów, odrzuć standardowy plan i zaprojektuj rozwiązanie oparte na plikach z częstą rotacją, jednoznacznie wskazując na wyższe ryzyko takiego podejścia.
- Jeśli zespół odrzuca anonimizację danych osobowych (PII scrubbing) ze względu na narzut opóźnień (latency), odrzuć plan – brak maskowania wrażliwych danych na wejściu stanowi bezpośrednie ryzyko naruszenia bezpieczeństwa.

Wynik: Jednostronicowy plan zawierający konfigurację skarbca, mechanizmy skanowania, rotacji, maskowania danych, filtracji ruchu wychodzącego, struktury logów audytowych oraz potoku CI/CD. Na końcu dodaj główny wskaźnik (KPI): miesięczna liczba wycieków sekretów wykrytych przez skanery; cel to zero.
