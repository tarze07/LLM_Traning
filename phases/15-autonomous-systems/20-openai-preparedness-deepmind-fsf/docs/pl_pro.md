# Preparedness Framework (OpenAI) oraz Frontier Safety Framework (DeepMind)

> Polityka Preparedness Framework OpenAI v2 (z kwietnia 2025 roku) wprowadza kategorie badawcze (research categories) – takie jak autonomia dalekiego zasięgu, maskowanie zdolności (sandboxing/sandbagging), autonomiczna replikacja i adaptacja (ARA) oraz obchodzenie zabezpieczeń – które są oddzielone od kategorii stale monitorowanych (tracked categories). Kategorie monitorowane uruchamiają procedury sporządzania raportów o zdolnościach i zabezpieczeniach, weryfikowanych przez Safety Advisory Group. Z kolei projekt Frontier Safety Framework (FSF v3) firmy DeepMind (z września 2025 roku, zaktualizowany o poziomy zdolności 17 kwietnia 2026 roku) integruje autonomię z obszarem badań i rozwoju ML oraz cyberbezpieczeństwem (np. poziom AI R&D Autonomy 1 oznacza pełną automatyzację procesu badawczo-rozwojowego nad sztuczną inteligencją po kosztach konkurencyjnych wobec pracy ludzkiej). FSF v3 wprost odnosi się do problemu zwodniczego dopasowania (deceptive alignment) poprzez automatyczne monitorowanie przejawów instrumentalnego wnioskowania (instrumental reasoning). Istotna uwaga: kategorie badawcze w PF v2 (w tym autonomia dalekiego zasięgu) nie wymuszają automatycznego wdrażania środków zaradczych – dokument posługuje się jedynie sformułowaniem „potencjalne działania”. Samo DeepMind przyznaje, że automatyczny monitoring „nie będzie na dłuższą metę wystarczający”, jeśli model wykaże silne cechy wnioskowania instrumentalnego.

**Typ:** Ucz się
**Języki:** Python (stdlib, narzędzie do porównywania oparte na trzech platformach)
**Wymagania wstępne:** Faza 15 · 19 (Antropiczne RSP)
**Czas:** ~45 minut

## Problem

W Lekcji 19 przeanalizowano zasady odpowiedzialnego skalowania firmy Anthropic. Ta lekcja dopełnia obraz sytuacji poprzez analizę polityk bezpieczeństwa OpenAI oraz DeepMind. Te three dokumenty stanowią pokrewne ramy mające na celu określenie, kiedy wiodące laboratoria powinny wstrzymać prace nad modelem lub ograniczyć jego wdrażanie. Choć są zbieżne pod kątem kluczowych kategorii ryzyka, różnią się w kilku istotnych szczegółach.

Punkty wspólne: wszystkie trzy systemy wskazują autonomię dalekiego zasięgu jako kluczowy obszar do ciągłego monitorowania. Każdy z nich uznaje zwodnicze zachowanie modelu (np. maskowanie rzeczywistych możliwości, symulowanie dopasowania) za istotną klasę ryzyka. Wszystkie trzy przewidują również powołanie wewnętrznego organu doradczego.
Różnice: OpenAI dzieli kategorie na „Monitorowane” (tracked – wymagające wdrożenia środków zaradczych) oraz „Badawcze” (research – bez automatycznych procedur bezpieczeństwa). DeepMind z kolei integruje autonomię z konkretnymi domenami, zamiast traktować ją jako osobną kategorię. Sposób klasyfikowania poszczególnych zdolności i przydzielania ich do konkretnych poziomów (np. poziom 1 vs poziom 2) różni się w zależności od laboratorium, co pociąga za sobą odmienne konsekwencje operacyjne.

Porównawcza analiza tych dokumentów jest niezwykle wartościowa. Ta sama zdolność modelu może skutkować „obowiązkowym wstrzymaniem prac” w Anthropic, „monitorowaniem bez automatycznego blokowania” w OpenAI oraz „kierowaniem do weryfikacji domenowej” w DeepMind. Strategia polityczna poszczególnych laboratoriów ma tu kluczowe znaczenie.

## Koncepcja

### Preparedness Framework OpenAI v2 (kwiecień 2025 r.)

Struktura:

- **Kategorie monitorowane (tracked)**: ich przekroczenie wymaga sporządzenia raportów o możliwościach modelu i wdrożonych zabezpieczeniach, które przed udostępnieniem systemu weryfikuje Safety Advisory Group.
- **Kategorie badawcze (research)**: zdolności, które laboratorium obserwuje, ale nie zobowiązuje się do automatycznego wdrażania określonych kroków bezpieczeństwa. Obejmują one: autonomię dalekiego zasięgu, maskowanie zdolności (sandbagging), autonomiczną replikację i adaptację (ARA) oraz próby łamania zabezpieczeń.

Kluczowe założenie wersji v2.0: Kategorie badawcze nie uruchamiają automatycznych procedur ochronnych. Dokument wspomina jedynie o „potencjalnych” środkach zaradczych. To bardzo ważna różnica: przypisanie danej zdolności do kategorii monitorowanych bądź badawczych decyduje o tym, czy prace zostaną wstrzymane, czy model będzie jedynie obserwowany.

### Frontier Safety Framework (DeepMind FSF v3)

Struktura (zaktualizowana o poziomy zdolności 17 kwietnia 2026 roku):

- **Krytyczne poziomy zdolności (Critical Capability Levels - CCL)**: zdefiniowane progi w pięciu kluczowych domenach: cyberbezpieczeństwo, biotechnologia, badania i rozwój uczenia maszynowego (ML R&D), CBRN oraz autonomia (powiązana z ML R&D i cyberbezpieczeństwem).
- **Monitorowane poziomy zdolności**: szczegółowe kryteria dodane w kwietniu 2026 roku. Przykładowo, poziom autonomii w ML R&D na poziomie 1 oznacza pełną automatyzację prac badawczo-rozwojowych nad AI po kosztach porównywalnych lub niższych od pracy ludzi.
- **Weryfikacja dopasowania pod kątem zwodniczym**: formalne zobowiązanie do monitorowania zachowań modelu w poszukiwaniu przejawów instrumentalnego dążenia do celów pobocznych (instrumental convergence/reasoning).

Podejście do autonomii różni się od propozycji OpenAI. DeepMind nie wydziela jej jako osobnej domeny najwyższego poziomu, lecz analizuje ją w kontekście obszarów, w których mogłaby wyrządzić realne szkody (ML R&D oraz cyberbezpieczeństwo). Argumentem za takim podejściem jest założenie, że autonomia sama w sobie nie generuje ryzyka bez konkretnego pola działania. Kontrargument wskazuje jednak, że ogólna autonomia między domenami stanowi metaryzyko, które powinno zostać jawnie zdefiniowane w polityce.

### Punkty wspólne wszystkich trzech podejść

- Powołanie wewnętrznych komitetów ds. bezpieczeństwa (Anthropic SAG, OpenAI SAG, wewnętrzny komitet DeepMind) weryfikujących zaawansowane modele przed wdrożeniem.
- Uwzględnienie zwodniczego dopasowania i celowego ukrywania zdolności jako istotnej klasy ryzyka.
- Zobowiązanie do regularnego publikowania dokumentów (Anthropic: plany bezpieczeństwa i raporty o ryzyku; OpenAI: raporty o możliwościach i zabezpieczeniach; DeepMind: cykliczne aktualizacje ram FSF).
- Zrozumienie ograniczeń systemów monitorowania. DeepMind wprost stwierdza, że „automatyczny nadzór nie będzie wystarczający w dłuższej perspektywie”.

### Główne rozbieżności

- **Anthropic**: wycofanie się ze sztywnego zobowiązania do pauzy w wersji v3.0 na rzecz ogólnego określenia progu AI R&D-4 jako kolejnego etapu wdrożeniowego.
- **OpenAI**: wyraźny podział na kategorie monitorowane i badawcze (te ostatnie, jak autonomia dalekiego zasięgu, nie blokują automatycznie prac).
- **DeepMind**: powiązanie autonomii z konkretnymi domenami zastosowań oraz wprowadzenie bardzo szczegółowych poziomów zdolności w kwietniu 2026 roku.

### Maskowanie zdolności (Sandbagging) jako wyzwanie dla ewaluacji

Zjawisko sandbaggingu (celowe zaniżanie wyników testów przez model w celu ukrycia rzeczywistych możliwości) zostało zaklasyfikowane przez OpenAI as kategoria badawcza. W polityce RSP Anthropic v3.0 próbuje się je ograniczać poprzez doprecyzowanie procedur ewaluacyjnych (Lekcja 1), natomiast DeepMind podchodzi do tego poprzez wdrożenie systemów wykrywania zwodniczego dopasowania w FSF v3.

Jeśli model celowo fałszuje wyniki testów, zdefiniowane w politykach progi stają się bezużyteczne. Cała struktura bezpieczeństwa opiera się na wiarygodności pomiarów. Z tego względu kluczowe znaczenie mają zewnętrzne, niezależne audyty (Lekcja 21, METR) oraz testy kontradyktoryjne.

### Jak analizować polityki bezpieczeństwa

- **Identyfikacja**: upewnij się, czy kluczowe dla Ciebie aspekty są wprost wymienione w dokumencie. Jeśli dana funkcja lub ryzyko nie jest opisane, polityka go nie obejmuje.
- **Klasyfikacja**: sprawdź status danej zdolności (czy jej przekroczenie wymusza kroki bezpieczeństwa, czy jest jedynie obserwowana).
- **Cykliczność**: czy dokument przewiduje sztywne terminy aktualizacji, czy jest modyfikowany jedynie reaktywnie?
- **Niezależność**: czy weryfikacja zewnętrzna jest wymagana, czy jedynie opcjonalna? Anthropic współpracuje w tym zakresie z Apollo i amerykańskim Instytutem Bezpieczeństwa AI, OpenAI z organizacją METR, natomiast DeepMind opiera się głównie na wewnętrznych komitetach.

## Jak tego użyć

Skrypt `code/main.py` implementuje proste narzędzie porównawcze w postaci matrycy decyzyjnej. Na podstawie wskazanej zdolności (np. autonomia, zwodnicze dopasowanie, automatyzacja R&D, cyberbezpieczeństwo) system wizualizuje, jak dana cecha jest klasyfikowana przez poszczególne laboratoria oraz jakie procedury bezpieczeństwa uruchamia. Jest to interaktywny przewodnik po analizowanych politykach.

## Wynik zadania

Plik `outputs/skill-cross-policy-diff.md` zawiera szczegółowe zestawienie różnic w podejściu poszczególnych laboratoriów do konkretnych zdolności i ryzyk modeli.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Upewnij się, że generowane zestawienie jest spójne z dokumentacją źródłową dla co najmniej dwóch wybranych cech.

2. Zapoznaj się z pełną treścią Preparedness Framework OpenAI v2. Wypisz wszystkie kategorie badawcze i wyjaśnij w jednym zdaniu dla każdej z nich, dlaczego zaklasyfikowano ją jako obszar badawczy, a nie monitorowany.

3. Przeczytaj DeepMind FSF v3 oraz aktualizację dotyczącą poziomów zdolności z kwietnia 2026 roku. Zidentyfikuj szczegółowe kryteria przypisane do Poziomu 1 autonomii w ML R&D. Jak można zmierzyć te parametry za pomocą zewnętrznych narzędzi?

4. Zjawisko sandbaggingu jest w OpenAI kategorią badawczą. Zaprojektuj procedurę testową, która uniemożliwi modelowi celowe zaniżanie wyników testów w celu ukrycia rzeczywistych możliwości, odwołując się do teorii gier omówionej w Lekcji 1.

5. Dokonaj analizy porównawczej trzech polityk bezpieczeństwa dla wybranej zdolności modelu. Wskaż, które podejście jest najbardziej rygorystyczne, a które najbardziej liberalne, uzasadniając wybór cytatami z tekstów źródłowych.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| Preparedness Framework | „Polityka bezpieczeństwa OpenAI” | Ramy gotowości w wersji PF v2 (kwiecień 2025 r.), wprowadzające kategorie monitorowane i badawcze |
| Kategoria monitorowana (Tracked category) | „Obowiązkowe procedury bezpieczeństwa” | Zdolności, których osiągnięcie uruchamia raporty o zabezpieczeniach i weryfikację SAG |
| Kategoria badawcza (Research category) | „Wyłącznie obserwacja” | Zdolności monitorowane bez automatycznego wdrażania procedur blokujących (np. autonomia dalekiego zasięgu) |
| Frontier Safety Framework | „Polityka bezpieczeństwa DeepMind” | Ramy bezpieczeństwa w wersji FSF v3 (wrzesień 2025 r.) rozbudowane o poziomy zdolności (kwiecień 2026 r.) |
| CCL (Critical Capability Level) | „Krytyczny poziom zdolności” | Zdefiniowane przez DeepMind progi zdolności dla poszczególnych domen (Cyber, Bio, ML R&D, CBRN) |
| AI R&D Autonomy Level 1 | „Automatyzacja badań nad AI” | Pełna i opłacalna automatyzacja procesu badawczo-rozwojowego nad sztuczną inteligencją |
| Sandbagging | „Celowe zaniżanie wyników” | Strategiczne ukrywanie zdolności i zaniżanie wyników testów przez model |
| Wnioskowanie instrumentalne (Instrumental reasoning) | „Dążenie do celów pośrednich” | Rozumowanie nastawione na realizację celów pobocznych wbrew intencjom twórców |

## Dalsza lektura

- [OpenAI — aktualizacja naszych ram gotowości](https://openai.com/index/updating-our-preparedness-framework/) — ogłoszenie wersji v2.
- [OpenAI — Gotowość Framework v2 PDF](https://cdn.openai.com/pdf/18a02b5d-6b67-4cec-ab64-68cdfbddebcd/preparedness-framework-v2.pdf) — pełny dokument.
- [DeepMind — Wzmocnienie naszych ram bezpieczeństwa na granicach](https://deepmind.google/blog/strengthening-our-frontier-safety-framework/) — ogłoszenie FSF v3.
- [DeepMind — Aktualizacja ram bezpieczeństwa na granicy (kwiecień 2026 r.)](https://deepmind.google/blog/updating-the-frontier-safety-framework/) — dodanie poziomów możliwości.
- [Raport FSF Gemini 3 Pro](https://storage.googleapis.com/deepmind-media/gemini/gemini_3_pro_fsf_report.pdf) — przykładowy raport o ryzyku w formacie FSF.
