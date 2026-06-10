---

name: compliance-matrix
description: Stwórz wymaganą matrycę ramową dla usługi LLM SaaS, biorąc pod uwagę lokalizację klienta, segment i zakres umowy. Kontrole mapy w ramach SOC 2, HIPAA, RODO, PCI-DSS, ustawy UE o sztucznej inteligencji, ustawy o sztucznej inteligencji stanu Kolorado, ISO 42001.
version: 1.0.0
phase: 17
lesson: 26
tags: [compliance, soc2, hipaa, gdpr, pci-dss, eu-ai-act, colorado-ai-act, iso-42001, iso-27001]

---

Biorąc pod uwagę lokalizację klientów (USA / UE / cały świat lub określone stany USA), segment (SaaS / opieka zdrowotna / fintech), zakres umowy (przedsiębiorstwo vs SMB) i aktualny stan zgodności, utwórz matrycę wymaganych ram.

Wyprodukuj:

1. Wymagane frameworki. Wymień wszystkie ramy, które należy osiągnąć, wraz z uzasadnieniem (geografia, segment, profil klienta).
2. Oś czasu. Dla każdej struktury podaj bieżący stan (brak / Typ I / w audycie / Typ II). Nazwij lukę.
3. Międzyplatformowe mapowanie sterowania. Dla każdej wymaganej struktury zidentyfikuj kontrole, które spełniają wiele wymagań (dziennik dostępu, szyfrowanie, dziennik audytu, zarządzanie zmianami).
4. Stanowisko dotyczące unijnej ustawy o sztucznej inteligencji. Sklasyfikuj poziom ryzyka produktu (niedopuszczalny / wysoki / ograniczony / minimalny). Jeśli wiąże się to z wysokim ryzykiem, wymagaj ścieżki oceny zgodności przed datą wejścia w życie 2 sierpnia 2026 r.
5. Obsługa PII/PHI. Potwierdź redakcję warstwy wnioskowania w czasie rzeczywistym (faza 17 · 25) – przetwarzanie końcowe nie jest chronione przez RODO. Potwierdź umowy BAA dla wszystkich dostawców sztucznej inteligencji mających kontakt z PHI.
6. Narzędzia do audytu. Drata / Vanta / Secureframe do automatyzacji między platformami. Warte swojej ceny w zakresie wielu platform.

Twarde odrzucenia:
- Twierdzenie, że SOC 2 typu I jest „zgodny z SOC 2” w przypadku zamówień dla przedsiębiorstw. Odmów — typ II to brama.
- Wysyłanie PHI do dostawcy bez BAA. Odmowa — naruszenie ustawy HIPAA.
- Oczyszczanie danych osobowych po przetworzeniu zgodnie z wymogami RODO. Odmów — żądaj w czasie rzeczywistym.

Zasady odmowy:
- Jeżeli produkt jest przeznaczony dla użytkowników z UE bez zapisów na podstawie art. 30 RODO, należy odmówić wysyłki do klientów z UE do czasu ustalenia odpowiednich zapisów.
- Jeśli produkt służy mieszkańcom Kolorado w zakresie kredytów/zatrudnienia/mieszkania/edukacji/podstawowych usług, należy przed wprowadzeniem na rynek wymagać przedstawienia dowodu ukończenia oceny skutków do 30 czerwca 2026 r. (data wejścia w życie ustawy Colorado AI Act zgodnie z SB24-205 ze zmianami zmienionymi przez SB25B-004).
- Jeśli produkt jest obarczony wysokim ryzykiem zgodnie z ustawą UE o sztucznej inteligencji, a zespół nie ma planu oceny zgodności, odmów obietnicy gotowości na sierpień 2026 r. bez wyznaczonego partnera wdrożeniowego.

Wynik: jednostronicowa matryca zawierająca wymagane ramy, stan bieżący, luki, harmonogram, kontrole między platformami, poziom unijnej ustawy o sztucznej inteligencji, stan informacji umożliwiających identyfikację, narzędzia. Zakończ 12-miesięcznym planem działania: kwartalne kamienie milowe poszczególnych ram.