---

name: router-plan
description: Projektowanie planu routingu modeli LLM – wybór wzorca (pre-routing, kaskada, konsylium), sygnałów sterujących (zadanie, długość, osadzenia, pewność) oraz bramek jakości online.
version: 1.0.0
phase: 17
lesson: 16
tags: [routing, cascade, model-cascade, routellm, notdiamond, cost-reduction]

---

Na podstawie charakterystyki ruchu (podział zapytań na kategorie), minimalnych wymagań jakościowych, tolerancji opóźnień oraz obecnych kosztów miesięcznych, przygotuj plan routingu.

Przygotuj:

1. Wybór wzorca routingu: Pre-routing (najszybszy, oparty na klasyfikatorze), kaskada (gwarantująca najlepszy kompromis jakościowy) lub konsylium (wyłącznie dla próbkowania testów A/B). Uzasadnij wybór wymaganiami jakościowymi oraz budżetem opóźnień (latency budget).
2. Sygnały sterujące: Wybierz spośród: klasyfikacji zadań, długości promptu, podobieństwa osadzeń wektorowych do trudnych przypadków (hard cases), pewności odpowiedzi (confidence). Określ wybrane kombinacje (zazwyczaj 2-3) oraz regułę ich łączenia.
3. Dobór modeli (para tani/frontier): Podaj nazwy konkretnych modeli (np. Claude 3.5 Haiku + GPT-5). Uzasadnij wybór ich kosztami oraz możliwościami technologicznymi.
4. Prognozę oszczędności: Oblicz szacowany koszt hybrydowy przy nowym podziale ruchu; porównaj prognozowane koszty miesięczne (USD) z obecnymi wydatkami.
5. Bramki jakości online (Online Quality Gates): Zdefiniuj system weryfikacji na żywo (np. 5% ruchu z każdej trasy oceniane przez model klasy frontier; alert przy spadku jakości Δ > 2%). Monitoruj współczynnik eskalacji (alert, jeśli wskaźnik wzrośnie o więcej niż 10 punktów procentowych w ujęciu miesięcznym).
6. Plan wdrożenia: Faza testowa w tle (shadow routing – router działa, ale decyzje nie wpływają na użytkownika; ewaluacja offline), wdrożenie typu canary (10% dla wybranej grupy użytkowników), pełne udostępnienie po zaliczeniu testów jakościowych.

Kryteria odrzucenia planu:
- Projekt routingu pozbawiony bramek jakości online. Odrzuć – dryf modeli i brak kontroli jakości to najczęstsze przyczyny niepowodzeń wdrożeń.
- Opieranie routingu wyłącznie na sygnale klasyfikacji zadań. Odrzuć – takie podejście ignoruje faktyczny stopień skomplikowania pojedynczego pytania.
- Kierowanie zadań o wysokiej trudności (kod, matematyka, wnioskowanie wieloetapowe) do tańszych modeli bez mechanizmu awaryjnego (fallback/kaskada). Odrzuć – drastycznie obniża to minimalną jakość aplikacji.

Zasady odmowy/zastrzeżenia:
- Jeśli wymagane jest zachowanie absolutnego braku regresji jakościowej (zero-regression), odrzuć pre-routing i zaproponuj kaskadowanie z czułym progiem eskalacji.
- Jeśli tańszy model ma tendencję do częstych odmów lub błędnej interpretacji wywołań narzędzi (tool calls), odrzuć tę parę modeli – spowoduje to ciche awarie u agentów.
- Jeśli routing ma być realizowany między różnymi dostawcami chmurowymi (cross-provider cascade), wymagaj wdrożenia bramy AI Gateway (omówionej w fazie 17 · 19) w celu ujednolicenia formatów API.

Format końcowy: Jednostronicowy raport zawierający: wybrany wzorzec routingu, sygnały sterujące, parę modeli, prognozowane oszczędności, bramki online oraz plan wdrożenia. Raport należy zakończyć kluczowym wskaźnikiem: 7-dniowym współczynnikiem eskalacji, służącym jako wyzwalacz detekcji dryfu w przypadku odchylenia o >10 punktów procentowych.
