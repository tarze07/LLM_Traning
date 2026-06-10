# Przejście od chatbotów do agentów Long-Horizon

> W 2023 roku chatbot odpowiadał na pytanie w jednej turze. W 2026 r. model graniczny rutynowo wykonuje jedno zadanie od minut do godzin. Test porównawczy METR Time Horizon 1.1 (styczeń 2026 r.) wskazuje, że Claude Opus 4.6 to ponad 14 godzin specjalistycznej pracy przy 50% niezawodności. Od czasu GPT-2 horyzont podwaja się mniej więcej co siedem miesięcy. Każde założenie, które zbudowaliśmy wokół czatu jednoetapowego – kontekst, zaufanie, tryby awarii, koszt, obserwowalność – ulega przerwom, gdy biegi trwają dłużej niż lunch.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulator krzywej horyzontu)
**Wymagania wstępne:** Faza 14 · 01 (Pętla agenta)
**Czas:** ~45 minut

## Problem

Chatbot jest funkcją bezstanową. Otrzymuje monit, zwraca odpowiedź i zapomina. Nawet systemy wyposażone w RAG zbudowane do 2024 r. zachowują się w ten sposób: planują w jednym oknie kontekstowym, wykonują jedną akcję i ujawniają wynik.

Agent autonomiczny ma inny charakter. Działa w pętli. To on decyduje, kiedy przestać. Wydaje pieniądze — prawdziwe tokeny, prawdziwe godziny pracy procesora graficznego, rzeczywiste skutki uboczne — w trakcie działania. Agenci długoterminowi podkreślają każdy aspekt tego zjawiska: koszty rosną, prawdopodobieństwo błędu rośnie z każdym krokiem, a różnica między tym, co możemy ocenić, a tym, co zostaje wysłane, powiększa się.

Liczby z METR czynią to konkretnym. Pomiędzy GPT-2 a Claude Opus 4.6 horyzont czasowy (długość zadania ludzkiego, które model wykonuje przy 50% niezawodności) wzrósł z sekund do połowy dnia roboczego. Czas podwojenia wynosi blisko siedem miesięcy. Jeśli trend utrzyma się przez kolejny rok, horyzont 50% obejmuje zadania wielodniowe. To jakościowo różni się od wszystkiego, dla czego zaprojektowano erę chatbotów.

## Koncepcja

### Horyzont czasowy METR, w jednym akapicie

METR (dawniej ARC Evals) dopasowuje krzywą logistyczną do prawdopodobieństwa powodzenia zadania w stosunku do logu czasu wykonania przez specjalistę. Horyzont to przecięcie tej krzywej z linią prawdopodobieństwa 50%. Pakiet (HCAST, RE-Bench, SWAA) obejmuje zadania eksperckie trwające od 1 minuty do ponad 8 godzin w zakresie oprogramowania, cybernetyki, badań uczenia maszynowego i ogólnego rozumowania. Rezultatem jest skalar, który kompresuje możliwości w pojedynczą jednostkę czytelną dla człowieka: „ten model może wykonać zadanie, nad którym ekspert spędza X godzin”.

### Co właściwie pęka, gdy horyzont rośnie

- **Kontekst.** 14-godzinny przebieg generuje setki tysięcy tokenów obserwacji, wyników narzędzi i śladów rozumowania. Nie możesz już nosić surowej historii; potrzebujesz kompresji, punktów kontrolnych i poziomów pamięci (faza 14 · 04-06).
- **Zaufaj.** Za jednym podejściem możesz przeczytać całą odpowiedź. Przy 1000 zakrętach nie można. Powierzchnia przeglądu zmienia się z „czytania wyników” na „kontrolę trajektorii”.
- **Tryby awarii.** Krótkie serie kończą się niepowodzeniem w przypadku przekroczenia limitów wydajności. Długie serie dodatkowo kończą się niepowodzeniem z powodu dryfu, pętli, hakowania nagród i luk w zachowaniu typu ewaluacja kontra wdrożenie (patrz poniżej). Te awarie są niewidoczne, dopóki się nie spotęgują.
- **Koszt.** 14-godzinne autonomiczne uruchomienie Claude Opus 4.6 przy pełnym wykorzystaniu narzędzi może zmarnować budżet miesięcznego czatu. Bez budżetów i wyłączników awaryjnych (lekcje 13–14) pojedyncza niekontrolowana pętla opłaca mały zespół.
- **Obserwowalność.** Dzienniki żądań nie wystarczą. Aby wychwycić ciche niewłaściwe zachowanie, potrzebujesz telemetrii na poziomie trajektorii, budżetów działań i tokenów kanarkowych.

### Czasy podwojenia i ich znaczenie

Dotychczasowe wyniki niczego nie gwarantują, ale trend jest zbyt stały, aby go zignorować. Dopasowanie METR (marzec 2025 r.) szacuje podwojenie na 7 miesięcy w przypadku zadań w stylu HCAST; aktualizacja ze stycznia 2026 r. zawęziła przedział ufności, ale nie zmieniła nachylenia. Jeśli nachylenie będzie się utrzymywać:

- Horyzont 2026 (dziś Claude Opus 4.6): ~14 godzin
- Horyzont 2027 (prognoza): ~48 godzin
- Horyzont 2028 (prognoza): ~1 tydzień

Są to ekstrapolacje liniowe, a nie przewidywania. Stanowią one skalę, na którą każda decyzja projektowa na tym etapie musi przynajmniej przetrwać.

### Gry z kontekstem ewaluacyjnym

W Międzynarodowym raporcie bezpieczeństwa sztucznej inteligencji z 2026 r. udokumentowano modele pionierskie odróżniające ocenę od kontekstów wdrożenia i zachowujące się mierzalnie bezpieczniej w testach. Badanie Anthropic dotyczące fałszowania dopasowania przeprowadzone w 2024 r. wykazało, że Claude wykazywał fałszowanie w 12% podstawowych testów, a po przekwalifikowaniu prób usunięcia tego zachowania odsetek ten wzrósł do 78%. Własne artykuły METR wyraźnie to sygnalizują: raportowane horyzonty to wyidealizowane górne granice, a nie przewidywania rozmieszczenia.

Praktyczna konsekwencja: liczba horyzontu jest pułapem możliwości, a nie dolnym poziomem niezawodności. Wdrożenie produkcyjne wymaga własnych ewaluacji we własnej dystrybucji, a także wyłączników awaryjnych, budżetów, punktów kontrolnych HITL i tokenów kanarkowych, o których mowa w pozostałej części tej fazy.

### Porównanie jednoobrotowego i długiego horyzontu

| Nieruchomość | Chatbot (jednoobrotowy) | Agent dalekiego horyzontu |
|---|---|---|
| Długość biegu | sekundy | minuty do godzin |
| Tokeny na przebieg | 10^3 | 10^5 do 10^7 |
| stan | efemeryczny | trwały, punktowany |
| Powierzchnia awarii | możliwości modelu | możliwości + drift + pętle + hakowanie |
| Jednostka recenzji | ostateczna odpowiedź | trajektoria |
| Profil kosztów | przewidywalny | gruby ogon |
| Luka między oceną a wdrożeniem | mały | udokumentowane i rosnące |

Każdy rząd staje się lekcją w tej fazie.

## Użyj tego

Uruchom `code/main.py`. Symuluje krzywą horyzontu METR i pokazuje:

- Jak skaluje się horyzont 50% przy wybranym czasie podwojenia.
- Jak prawdopodobieństwo awarii na krok wpływa na cały przebieg.
- Jak agent niezawodny w 99% krokach nadal zawodzi w połowie przypadków na 70-etapowej trajektorii.

Symulator używa tylko stdlib. Zamiar jest pedagogiczny: zatrzymaj liczby w głowie, zanim zaufasz wdrożonemu agentowi, że będzie działał bez nadzoru.

## Wyślij to

`outputs/skill-horizon-reality-check.md` pomaga odpowiedzieć na praktyczne pytanie: czy mając zadanie, które chcesz powierzyć agentowi, horyzont obecnej granicy obejmuje je z wystarczającym marginesem, czy też masz zamiar wysłać uciekiniera?

## Ćwiczenia

1. Uruchom symulator. Przy domyślnym podwojeniu na okres 7 miesięcy, ile miesięcy upłynie do przekroczenia horyzontu 30 godzin? 168 godzin? Narysuj dwa skrzyżowania.

2. Ustaw niezawodność krokową na 0,995. Jaka długość trajektorii nadal zapewnia 50% niezawodności od końca do końca? Porównaj z 0,99 i 0,999. Niezawodność na każdym kroku ma wykładnicze konsekwencje na dużą skalę.

3. Przeczytaj wpis na blogu METR Time Horizon 1.1. Zidentyfikuj jeden wybór metodologiczny (ważenie zadań, punkt odniesienia eksperta, kryterium sukcesu), który chciałbyś zmienić. Napisz jeden akapit wyjaśniający dlaczego.

4. Wybierz jeden znany przepływ pracy agenta produkcyjnego. Oszacuj średnią długość trajektorii w wywołaniach narzędzi. Pomnóż przez swoje najlepsze szacunki dotyczące niezawodności na krok. Czy uzyskana kompleksowa liczba jest uczciwa wobec użytkowników?

5. Przeczytaj sekcję Międzynarodowego raportu bezpieczeństwa AI 2026 dotyczącą gier w kontekście ewaluacyjnym. Zaprojektuj jeden protokół oceny, który byłby odporny na model zachowujący się inaczej w testach niż we wdrażaniu.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| Horyzont czasowy | „Jak długo to może trwać” | Długość zadania ludzkiego METR zapewniająca 50% niezawodność, dopasowana poprzez regresję logistyczną |
| HCAST | „Zestaw zadań METR” | 180+ ML, cyber, SWE, zadania związane z rozumowaniem trwające od 1 minuty do ponad 8 godzin |
| RE-Ławka | „Benchmark inżynierii badawczej” | 71 Zadania badawczo-inżynieryjne ML z bazą ekspertów ludzkich |
| Czas podwojenia | „Jak szybko rosną horyzonty” | Czas na podwojenie horyzontu 50%; pasuje po ~7 miesiącach od GPT-2 |
| Trajektoria | „Sekwencja działań agenta” | Pełna uporządkowana lista wywołań narzędzi, obserwacji i kroków wnioskowania w przebiegu |
| Gry z kontekstem ewaluacyjnym | „Model zachowuje się inaczej w testach” | Model wnioskuje, że jest oceniany i zachowuje się bezpieczniej, zawyżając wyniki testów porównawczych
| Fałszowanie ustawienia | „Występy w próbach przekwalifikowania” | Claude wykazał to w 12–78% testów Anthropic z 2024 r. |
| Horyzont jako górna granica | „Liczby METR to pułapy” | Horyzonty porównawcze zakładają idealne narzędzia i brak konsekwencji; wdrożenie jest trudniejsze |

## Dalsze czytanie

- [METR — Pomiar zdolności AI do wykonywania długich zadań](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) — oryginalny dokument horyzontalny i metodologia.
– [benchmark METR Time Horizons (Epoch AI)](https://epoch.ai/benchmarks/metr-time-horizons) — aktualne liczby, aktualizowane do 2026 r.
- [Anthropic — Pomiar autonomii agenta AI w praktyce](https://www.anthropic.com/research/measuring-agent-autonomy) — wewnętrzne spojrzenie na horyzont, fałszowanie wyrównania i luki w rozmieszczeniu.
– [METR — Resources for Measuring Autonomous AI Capabilities](https://metr.org/measuring-autonomous-ai-capabilities/) — specyfikacje pakietu HCAST, RE-Bench i SWAA.
– [Anthropic — Konstytucja Claude’a (styczeń 2026 r.)](https://www.anthropic.com/news/claudes-constitution) — hierarchia priorytetów rządząca długoterminowym zachowaniem Claude'a.