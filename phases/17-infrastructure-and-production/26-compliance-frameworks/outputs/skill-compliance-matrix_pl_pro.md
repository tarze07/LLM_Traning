---

name: compliance-matrix
description: Stwórz matrycę zgodności regulacyjnej dla usługi LLM SaaS na podstawie lokalizacji klienta, segmentu rynkowego oraz zakresu umowy. Zmapuj procedury kontrolne pod wymagania SOC 2, HIPAA, RODO, PCI-DSS, Aktu o sztucznej inteligencji (EU AI Act), Colorado AI Act oraz normy ISO 42001.
version: 1.0.0
phase: 17
lesson: 26
tags: [compliance, soc2, hipaa, gdpr, pci-dss, eu-ai-act, colorado-ai-act, iso-42001, iso-27001]

---

Na podstawie lokalizacji klientów (USA / UE / rynek globalny lub poszczególne stany USA), segmentu rynkowego (SaaS / opieka zdrowotna / fintech), zakresu umów (enterprise vs SMB) oraz bieżącego statusu zgodności, przygotuj matrycę wymaganych standardów regulacyjnych.

Wygeneruj:

1. Wymagane standardy: Wymień wszystkie standardy regulacyjne, które musi spełniać system, wraz ze szczegółowym uzasadnieniem biznesowym (geografia, segment, profil klienta).
2. Harmonogram i status: Dla każdego standardu określ bieżący status (brak / Typ I / w trakcie audytu / Typ II) oraz zidentyfikuj powstałe luki (gap analysis).
3. Mapowanie zabezpieczeń (Cross-Mapping): Zidentyfikuj procedury i mechanizmy kontrolne, które spełniają jednocześnie wymagania wielu standardów (np. logowanie dostępu, szyfrowanie, dzienniki audytu, zarządzanie zmianami).
4. Klasyfikacja pod EU AI Act: Określ kategorię ryzyka dla oferowanego produktu (ryzyko niedozwolone / wysokie / ograniczone / minimalne). Jeśli produkt kwalifikuje się jako system wysokiego ryzyka, zaplanuj ścieżkę formalnej oceny zgodności przed wejściem przepisów w życie (2 sierpnia 2026 r.).
5. Przetwarzanie PII/PHI: Wdrożenie maskowania danych osobowych w czasie rzeczywistym na poziomie bramy wnioskowania (Faza 17 · Lekcja 25) – usuwanie danych po przetworzeniu (post-processing) nie zapewnia zgodności z RODO. Zweryfikuj i potwierdź podpisanie umów BAA ze wszystkimi zewnętrznymi dostawcami AI przetwarzającymi dane PHI.
6. Narzędzia do audytu: Wybierz system do automatyzacji procesów zgodności (np. Drata, Vanta, Secureframe). Zastosowanie tych narzędzi przynosi duże oszczędności przy konieczności obsługi wielu standardów jednocześnie.

Kryteria odrzucenia planu (Hard rejects):
- Deklarowanie zgodności z SOC 2 na podstawie raportu Typu I w procesach zakupowych klasy enterprise: Odrzuć – kluczowym warunkiem wejścia jest raport Typu II.
- Przesyłanie chronionych danych zdrowotnych (PHI) do dostawcy API bez podpisanej umowy BAA: Odrzuć – stanowi to bezpośrednie naruszenie HIPAA.
- Stosowanie anonimizacji danych osobowych po przetworzeniu (post-processing scrubbing) jako metody spełnienia RODO: Odrzuć – wymagaj maskowania danych w czasie rzeczywistym.

Zasady odrzucenia:
- Jeśli produkt jest oferowany użytkownikom z UE bez opracowanego rejestru z art. 30 RODO, zablokuj wejście na rynek unijny do czasu przygotowania odpowiedniej dokumentacji.
- Jeśli produkt jest udostępniany mieszkańcom stanu Kolorado w obszarach takich jak ocena zdolności kredytowej, rekrutacja, mieszkalnictwo, edukacja lub podstawowe usługi publiczne, wymagaj przedstawienia udokumentowanej oceny wpływu (impact assessment) przed udostępnieniem usługi na rynku, z ostatecznym terminem do 30 czerwca 2026 r. (data wejścia w życie Colorado AI Act zgodnie z SB24-205 ze zmianami wprowadzonymi przez SB25B-004).
- Jeśli produkt kwalifikuje się jako system wysokiego ryzyka pod EU AI Act, a zespół nie posiada gotowego planu oceny zgodności ani wyznaczonego partnera wdrożeniowego, odrzuć deklarację gotowości na sierpień 2026 roku.

Wynik: Jednostronicowa matryca zawierająca wykaz wymaganych standardów regulacyjnych, bieżący status, analizę luk, harmonogram wdrożeń, zmapowane procedury kontrolne, kategorię ryzyka pod EU AI Act, procedury maskowania PII/PHI oraz wybrane narzędzia wspierające audyt. Na końcu umieść 12-miesięczną mapę drogową (roadmap) z kwartalnymi kamieniami milowymi dla każdego z wdrażanych standardów.
