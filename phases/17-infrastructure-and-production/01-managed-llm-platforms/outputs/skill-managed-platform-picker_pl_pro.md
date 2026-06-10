---

name: managed-platform-picker
description: Wybierz zarządzaną platformę LLM (AWS Bedrock, Azure OpenAI, Vertex AI) oraz platformę dodatkową dla zapewnienia nadmiarowości. Rekomendacja uwzględnia profil obciążenia, wymagania SLA i zgodność z regulacjami, a także zawiera plan konfiguracji narzędzi FinOps.
version: 1.0.0
phase: 17
lesson: 01
tags: [bedrock, azure-openai, vertex-ai, ptu, finops, managed-platforms]

---

Na podstawie profilu obciążenia (wymagane modele, miesięczna liczba tokenów, SLA dla wskaźnika TTFT na poziomie P50/P99, ograniczenia regulacyjne oraz dotychczasowa infrastruktura chmurowa) przygotuj rekomendację wyboru platformy.

Przygotuj:

1. **Platforma główna.** Wskaż rekomendowaną platformę, konkretne obsługiwane modele oraz określ, czy optymalnym wyborem będą rozliczenia na żądanie, czy dedykowana wydajność (PTU w Azure / Provisioned Throughput w Bedrock) w oparciu o profil obciążenia. Przedstaw wyliczenia progu rentowności (PTU staje się opłacalne przy stałym, bazowym wykorzystaniu na poziomie około 40–60%).
2. **Platforma dodatkowa.** Wskaż drugą platformę w celu zapewnienia niezależności od jednego dostawcy (LLM redundancy). Uzasadnij wybór tej pary — nadmiarowość musi obejmować zarówno dostępność zbieżnych modeli (np. Claude w Bedrock + GPT w Azure OpenAI), jak i redundancję geograficzną (pokrycie regionów).
3. **Oprzyrządowanie i konfiguracja FinOps.** Określ elementy do wdrożenia od pierwszego dnia: profile wnioskowania aplikacji w Bedrock (Application Inference Profiles), subskrypcje i grupy zasobów w Azure (z uwzględnieniem rezerwacji PTU jako obiektów kosztowych) lub dedykowane projekty GCP dla poszczególnych zespołów wraz z eksportem bilingu do BigQuery w Vertex AI. Zdefiniuj wymiary atrybucji kosztów — na użytkownika, na zadanie, na dzierżawcę (tenant).
4. **Weryfikacja umowy SLA.** Porównaj docelowy wskaźnik TTFT P99 z rzeczywistymi benchmarkami wydajności (Azure OpenAI z PTU ≈ 50 ms P50; Bedrock na żądanie ≈ 75 ms P50). Jeśli wymagania SLA są bardziej rygorystyczne niż wydajność gwarantowana przez rozliczenia na żądanie, wskaż konieczność zakupu dedykowanych jednostek PTU.
5. **Weryfikacja zgodności z regulacjami.** Jeśli dotyczy, zweryfikuj wymagania dotyczące umów BAA, certyfikacji SOC 2 Type II, HIPAA oraz lokalizacji danych (np. przechowywanie na terenie UE). Pamiętaj, że choć wszyscy trzej dostawcy spełniają podstawowe standardy bezpieczeństwa, to zasady retencji logów i procedury wyłączenia monitorowania nadużyć (abuse monitoring) znacznie się różnią.
6. **Plan wdrożenia i migracji.** Wskaż jeden prosty i odwracalny krok do wykonania w bieżącym tygodniu (np. integracja z bramą API / ujednoliconym dostawcą abstrakcji; dodanie odpowiednich nagłówków atrybucji kosztów w zapytaniach) oraz jeden krok długoterminowy (zakup rezerwacji PTU; konfiguracja przełączania awaryjnego między regionami).

Bezwzględne odrzucenie rekomendacji w przypadku:

- Rekomendowania pojedynczej platformy bez wskazania rozwiązania zapasowego. Wymagaj wdrożenia strategii opartej na co najmniej dwóch dostawcach.
- Rekomendowania zakupu PTU bez przedstawienia szacunków dotyczących poziomu wykorzystania zasobów. Wymagaj podania szacowanego, stałego obciążenia bazowego.
- Ignorowania profili wnioskowania aplikacji (Application Inference Profiles) w AWS Bedrock, gdy precyzyjna atrybucja kosztów jest jednym z wymagań – to najbardziej przejrzyste natywne rozwiązanie.

Zasady weryfikacji i odmowy:

- Jeśli projekt wymaga jednoczesnego korzystania z modeli Claude, Gemini i GPT jako kluczowych (P0), przedstaw realne rozwiązanie oparte na trzech platformach (Bedrock + Vertex + Azure OpenAI za wspólną bramą), zamiast sugerować, że pojedyncza platforma obsłuży wszystkie trzy.
- Jeśli umowa SLA wymaga wskaźnika TTFT P99 < 100 ms, a budżet nie pozwala na zakup rezerwacji PTU, odmów zagwarantowania takiego SLA – wyjaśnij, że opóźnienia w modelach rozliczanych na żądanie charakteryzują się zbyt dużą wariancją.
- Jeśli celem klienta jest wyłącznie „wybór najtańszego dostawcy”, odrzuć takie uproszczenie – koszt infrastruktury LLM jest wielowymiarowy (cena za token, koszt dedykowanej przepustowości, nakłady na konfigurację atrybucji oraz ryzyko vendor lock-in).

Format wyjściowy: Jednostronicowy dokument decyzyjny określający platformę główną, dodatkową, decyzję o wyborze PTU vs rozliczenia na żądanie, listę niezbędnego oprzyrządowania, analizę SLA/zgodności oraz dwa etapy migracji. Zakończ podaniem kluczowej metryki pozwalającej wykryć odchylenia od założeń planu (np. poziom stałego wykorzystania, marnotrawstwo zarezerwowanych jednostek PTU lub pokrycie atrybucji kosztów).
