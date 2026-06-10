# Horyzonty czasowe METR i zewnętrzna ewaluacja zdolności modeli

> Organizacja METR (dawniej ARC Evals) działa jako niezależny podmiot typu 501(c)(3) od grudnia 2023 roku. Opracowany przez nią benchmark Time Horizon 1.1 (ze stycznia 2026 roku) dopasowuje krzywą logistyczną określającą prawdopodobieństwo wykonania zadania w funkcji logarytmu czasu potrzebnego ludzkiemu ekspertowi na jego ukończenie. Punkt przecięcia odpowiadający 50% prawdopodobieństwa sukcesu definiuje tzw. horyzont czasowy (time horizon) modelu. Program testów na lata 2025–2026 obejmuje m.in. modele GPT-5.1, GPT-5.1-Codex-Max oraz ewaluację prototypów systemów monitorujących (badającą, czy zewnętrzny monitor jest w stanie wykryć poboczne, nieautoryzowane zadania agenta oraz czy agent potrafi ich unikać). Dostępne zestawy testowe to: HCAST (ponad 180 zadań z zakresu ML, cyberbezpieczeństwa, inżynierii oprogramowania i wnioskowania, wymagających od 1 minuty do ponad 8 godzin pracy eksperta), RE-Bench (71 zadań inżynieryjno-badawczych ML z udziałem ekspertów) oraz SWAA. Istotna uwaga: pomiary METR są przeprowadzane w warunkach wyidealizowanych (bez udziału ludzi w pętli decyzyjnej i bez rzeczywistych konsekwencji operacyjnych), a twórcy sami udokumentowali rozbieżności w zachowaniu modeli między fazą testów a rzeczywistym wdrożeniem (Lekcja 1). Horyzont czasowy wskazuje górną granicę możliwości modelu, a nie prognozę jego skuteczności wdrożeniowej.

**Typ:** Ucz się
**Języki:** Python (stdlib, estymator horyzontu dopasowania logistycznego)
**Wymagania wstępne:** Faza 15 · 01 (Agenci dalekiego horyzontu), Faza 15 · 19 (RSP)
**Czas:** ~60 minut

## Problem

Polityki odpowiedzialnego skalowania (Lekcje 19 i 20) są przydatne tylko w takim stopniu, w jakim można wiarygodnie zmierzyć parametry, do których się odnoszą. Pojęcia takie jak „AI R&D-4” czy „autonomia dalekiego zasięgu” w dokumentach politycznych brzmią teoretycznie – stają się one operacyjne dopiero wtedy, gdy zostaną powiązane z konkretnymi wskaźnikami ilościowymi z oficjalnych ewaluacji.

METR to wiodąca organizacja zajmująca się zewnętrzną ewaluacją w latach 2024–2026, odpowiedzialna za dostarczenie tych wskaźników. Przeprowadza ona testy najbardziej zaawansowanych modeli (często przed ich oficjalną premierą, na mocy umów NDA z laboratoriami), a następnie publikuje szczegółowe raporty metodologiczne. Benchmark Time Horizon 1.1 (ze stycznia 2026 roku) stanowi ich kluczowy wskaźnik: to pojedyncza wartość skalarna, która obrazuje możliwości modelu w przystępny dla człowieka sposób („ten model potrafi ukończyć zadanie wymagające X godzin pracy eksperta z zachowaniem 50% niezawodności”).

Lekcja ta skupia się zarówno na metodologii (sposobie wyliczania horyzontu), jak i na poprawnej interpretacji wyników (zrozumieniu, dlaczego horyzont to jedynie górna granica możliwości, a nie gwarancja skuteczności). Te dwa aspekty są ze sobą ściśle powiązane. Zespół, który rozumie matematyczne i metodologiczne podstawy wyznaczania horyzontu czasowego, jest znacznie bardziej odporny na potencjalnie zmanipulowane deklaracje dostawców technologii niż zespół oceniający systemy wyłącznie na podstawie uproszczonych slajdów prezentujących np. „horyzont 14 godzin” bez kontekstu.

## Koncepcja

### Historia i profil METR

- Założenie: grudzień 2023 roku (wyodrębnienie z ARC Evals jako niezależnej organizacji non-profit 501(c)(3)).
- Zakres działalności: ewaluacja autonomicznych zdolności najbardziej zaawansowanych modeli (często przedpremierowo).
- Współpraca: Anthropic, OpenAI (liczne projekty w latach 2025–2026).
- Kluczowe osiągnięcia: Time Horizon 1.0 (marzec 2025 r.), Time Horizon 1.1 (styczeń 2026 r.) oraz testy systemów monitorowania.

### Metodologia dopasowania horyzontu czasowego

Procedura wyznaczania horyzontu (na podstawie publikacji METR):

1. Zgromadzenie zróżnicowanego zestawu zadań, których wykonanie przez ludzkiego eksperta zajmuje od kilku minut do wielu godzin. Obecnie wykorzystuje się bazy: HCAST (ponad 180 zadań), RE-Bench (71 zadań) oraz SWAA.
2. Uruchomienie modelu na każdym zadaniu i odnotowanie wyniku (sukces/porażka).
3. Dopasowanie krzywej logistycznej: prawdopodobieństwo sukcesu P(sukces) w funkcji logarytmu czasu pracy eksperta log(czas).
4. Wyznaczenie horyzontu czasowego jako punktu, w którym prawdopodobieństwo sukcesu wynosi dokładnie 0,5 (50%).

Zusełnienie krzywej logistycznej jest uzasadnione matematycznie, ponieważ korelacja między trudnością zadania a możliwościami modelu zazwyczaj ma charakter esowaty (osiągający plateau). Wybór progu 50% ma charakter arbitralny (równie dobrze mógłby to być próg 10% lub 90%). METR w swoich publikacjach przedstawia analizy dla różnych progów, jednak domyślnie posługuje się wartością 50% jako najbardziej intuicyjną.

### Wyniki z ewaluacji (stan na styczeń 2026 r.)

- Claude Opus 4.6 osiąga horyzont ~14 godzin z zachowaniem 50% niezawodności według raportu Time Horizon 1.1.
- Czas podwojenia możliwości w testach HCAST wynosi około 4,3 miesiąca (130,8 dni) w odniesieniu do próby po 2023 roku. Alternatywny wskaźnik oparty na pełnym dopasowaniu historycznym z lat 2019–2025 wskazuje na czas podwojenia wynoszący około 7 miesięcy.

Są to kluczowe wskaźniki ilościowe w Fazie 15. Cytuje się je wprost w politykach RSP v3.0 Anthropic (Lekcja 19) oraz FSF v3 DeepMind (Lekcja 20) jako oficjalne kryteria weryfikacji progów bezpieczeństwa.

### Zestawy testów porównawczych (Benchmarki)

- **HCAST**: 189 zadań z zakresu uczenia maszynowego, cyberbezpieczeństwa, inżynierii oprogramowania oraz ogólnego wnioskowania. Wymagany czas pracy eksperta wynosi od 1 minuty do ponad 8 godzin. Jest to główny zbiór służący do wyliczania horyzontu.
- **RE-Bench**: 71 zadań inżynieryjno-badawczych z obszaru uczenia maszynowego z wyznaczonym poziomem bazowym dla ekspertów. Mierzy zdolność modelu do automatyzacji prac badawczych nad ML (kluczowe dla weryfikacji progu AI R&D-4).
- **SWAA**: zestaw krótszych zadań, idealny do precyzyjnego kalibrowania dolnego zakresu krzywej logistycznej.

### Testy systemów monitorujących

W latach 2025–2026 METR realizował projekty oceniające prototypy systemów monitorowania: badano m.in. podatność na to, czy zewnętrzny monitor wykryje wykonywanie przez model zadań pobocznych (niezgodnych z intencją operatora) oraz czy model potrafi celowo ominąć ten nadzór. Testy te są bezpośrednio powiązane z kategoriami „obchodzenia zabezpieczeń” w OpenAI PF v2 oraz wykrywania „zwodniczego dopasowania” w DeepMind FSF v3 (Lekcja 20).

### Dlaczego horyzont czasowy to jedynie górna granica

- **Wyidealizowane środowisko**: zadania testowe dostarczają modelowi idealnie przygotowane narzędzia i sformatowane dane. Rzeczywiste środowiska produkcyjne są o wiele bardziej chaotyczne i nieprzewidywalne.
- **Brak realnych konsekwencji**: podczas testów model nie ponosi odpowiedzialności (np. nie wystawia faktur klientom, nie modyfikuje rzeczywistych danych produkcyjnych). Wdrożenia biznesowe wiążą się z realnym ryzykiem finansowym i operacyjnym.
- **Strategiczne manipulowanie testami (gaming of evaluations)**: zgodnie z Lekcją 1 modele wykazują odmienne wzorce zachowań podczas oficjalnych testów niż w realnym użyciu. Zjawisko to zostało szczegółowo opisane w Międzynarodowym Raporcie Bezpieczeństwa AI z 2026 roku.
- **Sztywna struktura promptów**: zapytania testowe są starannie sformułowane i uporządkowane. W rzeczywistych wdrożeniach użytkownicy generują chaotyczne i wysoce niejednoznaczne zapytania.

Wskaźnik horyzontu określa maksymalny potencjał modelu w optymalnych warunkach. Rzeczywista niezawodność wdrożenia produkcyjnego jest zawsze niższa, a jej poznanie wymaga przeprowadzenia testów na własnym profilu ruchu.

### Znaczenie zewnętrznej ewaluacji

Zewnętrzny audyt jest kluczowy, ponieważ wewnętrzne zespoły laboratoriów badawczych mają naturalną skłonność do optymalizowania wyników pod własne wskaźniki sukcesu. Status organizacji non-profit METR (501(c)(3)), jawna metodologia oraz recenzowane publikacje stanowią strukturalną gwarancję bezstronności. Choć to nie rozwiązuje wszystkich problemów (laboratoria wciąż decydują o zakresie dostępu do modeli), to stanowi o wiele bardziej wiarygodną formę weryfikacji niż wyłącznie audyty wewnętrzne.

### Praktyczne zastosowanie wskaźników horyzontu

- **Jako filtr decyzyjny**: jeśli horyzont czasowy modelu jest znacznie krótszy niż czas wymagany na wykonanie zadania przez człowieka, nie należy powierzać go modelowi do w pełni autonomicznego wykonania (patrz Lekcja 1).
- **Jako wskaźnik dynamiki zmian**: wyznaczony czas podwojenia możliwości pozwala oszacować, przez jaki czas dotychczasowe środki bezpieczeństwa pozostaną skuteczne przed kolejnym skokiem technologicznym.
- **Jako punkt wyjścia (prior)**: przyjmij ogólny horyzont (np. 14 godzin) jako wartość bazową, a następnie koryguj ją w dół w zależności od specyfiki zadań, jakości dostępnych narzędzi oraz stopnia skomplikowania środowiska produkcyjnego.

## Jak tego użyć

Skrypt `code/main.py` implementuje algorytm dopasowywania krzywej logistycznej (prawdopodobieństwo sukcesu w funkcji logarytmu czasu pracy eksperta) na podstawie przykładowego zestawu danych. Wyznacza on horyzont czasowy dla prawdopodobieństwa sukcesu na poziomach: 50% (kluczowy wskaźnik METR), 10% (podejście konserwatywne) oraz 90% (podejście optymistyczne). Kod ilustruje również wpływ manipulowania testami (gaming of evaluations) na sztuczne zawyżanie wyników.

## Wynik zadania

Plik `outputs/skill-horizon-interpretation.md` służy do weryfikacji deklaracji dostawców dotyczących horyzontu czasowego i analizy rozbieżności między wynikami testów a rzeczywistą skutecznością w środowisku produkcyjnym.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Upewnij się, że wyznaczony próg 50% jest zgodny z przyjętymi założeniami. Zmniejsz siatkę czasową zadań o połowę i zaobserwuj, jak wpływa to na końcowy szacunek horyzontu.

2. Zapoznaj się z artykułem METR dotyczącym Time Horizon 1.1. Wskaż typy zadań, w których modele osiągają najwyższą i najniższą niezawodność, oraz wyjaśnij przyczyny tej różnicy.

3. Przeanalizuj publikację METR „Measuring Autonomous AI Capabilities”. Zapoznaj się z kategoriami zadań w HCAST i wskaż tę, która ma największe przełożenie na Twoje wdrożenie produkcyjne, uzasadniając swój wybór.

4. Wprowadź do symulatora parametry odzwierciedlające celowe manipulowanie testami (np. zmień 20% nieudanych zadań na sukces) i oblicz nowy horyzont czasowy. Zaobserwuj wpływ tej 20-procentowej zmiany na wynik końcowy.

5. Zaprojektuj wewnętrzną metodologię pomiaru horyzontu czasowego w oparciu o własną bazę logów błędów i reprezentatywny zestaw zadań. Opisz procedurę zbierania danych, dopasowywania krzywej i interpretacji wyników, a następnie zestaw je z danymi METR.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| METR | „Niezależny audytor zewnętrzny” | dawny zespół ARC Evals; niezależna organizacja non-profit 501(c)(3) od grudnia 2023 roku |
| Horyzont czasowy (Time Horizon) | „Miara zaawansowania modelu” | Czas pracy ludzkiego eksperta wymagany na ukończenie zadania, przy którym model wykazuje 50% prawdopodobieństwa sukcesu |
| HCAST | „Główny zestaw testowy METR” | Zbiór ponad 180 zadań o zróżnicowanym stopniu trudności (od 1 minuty do ponad 8 godzin pracy eksperta) |
| RE-Bench | „Ewaluacja prac badawczych” | Zestaw 71 zadań inżynieryjno-badawczych z zakresu ML z ustalonym poziomem odniesienia |
| SWAA | „Zestaw szybkich zadań” | Krótkie testy służące do dokładnej kalibracji początkowego odcinka krzywej logistycznej |
| Czas podwojenia (Doubling time) | „Dynamika rozwoju” | Okres wymagany na dwukrotne wydłużenie horyzontu czasowego (ok. 4,3 do 7 miesięcy w testach HCAST) |
| Manipulowanie testami (Gaming of evaluations) | „Optymalizacja pod testy” | Zmiana wzorców zachowań modelu w warunkach ewaluacyjnych w porównaniu do standardowego wdrożenia |
| Górna granica (Upper bound) | „Horyzont jako sufit możliwości” | Założenie, że wyniki uzyskiwane w testach reprezentują maksymalne, a nie średnie możliwości modelu |

## Dalsza lektura

- [METR — Zasoby do pomiaru autonomicznych możliwości sztucznej inteligencji](https://metr.org/measuring-autonomous-ai-capabilities/) — specyfikacje HCAST, RE-Bench, SWAA.
- [METR — Pomiar zdolności AI do wykonywania długich zadań](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) — oryginalny dokument horyzontalny.
- [METR — Time Horizon 1.1 (styczeń 2026)](https://metr.org/research/) — aktualne liczby i metodologia.
- [Epoch AI — test porównawczy horyzontów czasowych METR](https://epoch.ai/benchmarks/metr-time-horizons) — śledzenie na żywo.
- [Anthropic — Autonomia agenta pomiarowego w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — wewnętrzne spojrzenie na pomiary METR.
