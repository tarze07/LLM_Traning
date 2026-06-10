---

name: llm-security-plan
description: Przygotuj plan bezpieczeństwa LLM obejmujący skarbiec sekretów, czyszczenie danych osobowych ze spójną tokenizacją, listę dozwolonych wyjść z sieci, przechowywanie dzienników audytu i stan zerowego zaufania.
version: 1.0.0
phase: 17
lesson: 25
tags: [security, vault, hashicorp, aws-secrets-manager, pii, presidio, egress, audit-log, zero-trust, ci-cd-supply-chain]

---

Biorąc pod uwagę zakres przepisów (SOC 2, HIPAA, RODO), bieżący stan danych uwierzytelniających i stan sieci/wyjścia, utwórz plan bezpieczeństwa.

Wyprodukuj:

1. Migracja skarbca. Wybierz skarbiec (HashiCorp, Menedżer sekretów AWS, Azure Key Vault, Menedżer sekretów GCP). Wzorzec bramy: aplikacje → brama → skarbiec w czasie wykonywania. Przestarzałe poświadczenia env i pliku konfiguracyjnego zakodowane na stałe.
2. Tajne skanowanie. Włącz TruffleHog / GitGuardian / Gitleaks przy każdym zatwierdzeniu. Blokuj PR po wykryciu.
3. Polityka rotacyjna. ≤ 90 dni. Tam, gdzie to możliwe, zautomatyzowane. Dedykowana rotacja dla poświadczeń CI/CD (krótsza — zalecane 30 dni).
4. Oczyszczanie danych osobowych. Rozpoznawanie jednostek (Presidio + regex). Spójna tokenizacja (ta sama wartość → ten sam symbol zastępczy) w celu zachowania semantyki.
5. Lista dozwolonych wyjść. Dodaj do białej listy domeny dostawców LLM, wektorową bazę danych, punkty końcowe skarbca. Narzędzie do rozwiązywania listy dozwolonych DNS.
6. Dziennik audytu. Tylko do dołączania, niezmienne. Pola wymagane: użytkownik, najemca, skrót monitu/odpowiedzi, tokeny, koszt, wyłączenia poręczy. Retencja według ram (SOC 2 1 rok / HIPAA 6 lat).
7. Higiena CI/CD. Federacja tożsamości OIDC (bez statycznych kluczy w chmurze). Wąski zakres poświadczeń CI/CD. Jako motywację przytocz incydent w łańcuchu dostaw w Vercel w 2026 r.

Twarde odrzucenia:
- Klucze statyczne w plikach konfiguracyjnych. Odmawiać.
- Przechowywanie surowych podpowiedzi w dzienniku audytu. Odmów — tylko skrót, chyba że ramy regulacyjne wyraźnie wymagają inaczej.
- Zezwalanie na wyjście do `*` lub „internetu”. Odmów — biała lista.

Zasady odmowy:
- Jeśli klient nie akceptuje żadnego skarbca (wymaganie dotyczące szczeliny powietrznej), odrzuć normalny plan i zaprojektuj rezerwę opartą na plikach z rotacją. Należy wyraźnie zauważyć, że jest to mniej bezpieczne.
— Jeśli czyszczenie danych osobowych zostanie odrzucone ze względu na „opóźnienie”, odrzuć — w przypadku tokena głównego skarbca wymagane jest zazwyczaj opóźnienie wynoszące PHHT 190 dni. Odmów — staje się to wektorem naruszenia.

Dane wyjściowe: jednostronicowy plan ze skarbcem, skanowaniem, rotacją, czyszczeniem, wyjściem, dziennikiem audytu i stanem CI/CD. Zakończ pojedynczym wskaźnikiem: miesięczna liczba trafień związanych ze skanowaniem tajnych danych; cel zerowy.