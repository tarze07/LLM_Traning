---

name: dualpipe-planner
description: Planowanie strategii równoległości potokowej (Pipeline Parallelism: 1F1B, Zero Bubble, DualPipe, DualPipeV) dla klastra treningowego
version: 1.0.0
phase: 10
lesson: 19
tags: [pipeline-parallelism, dualpipe, dualpipev, zero-bubble, expert-parallelism, distributed-training]

---

Na podstawie specyfikacji klastra treningowego (całkowita liczba GPU, topologia połączeń sieciowych, model akceleratora, pamięć VRAM na GPU), architektury modelu (całkowita liczba parametrów, liczba aktywnych parametrów, MoE lub model gęsty/dense, oczekiwana liczba warstw) oraz docelowego wolumenu danych treningowych, zaproponuj strategię równoległości potokowej i wyznacz oczekiwany udział bąbli potoku (pipeline bubble fraction).

Zwróć:

1. **Liczbę etapów potoku (pipeline depth) P**: Dobierz wartość na podstawie budżetu pamięci GPU (na każdą rangę musi przypadać jeden etap potoku), obecności MoE/architektury gęstej oraz przepustowości połączeń sieciowych. Zakres: od $P=4$ dla mniejszych klastrów do $P=16\text{–}32$ dla trenowania zaawansowanych modeli MoE (frontier MoE training).
2. **Liczbę mikro-batchy M**: Dla algorytmów DualPipe i DualPipeV wartość ta musi być podzielna przez 2. Typowy stosunek $M/P$ mieści się w przedziale od 8 do 16. Uzasadnij wybór założeniami akumulacji gradientów oraz rozmiarem pamięci aktywacji przy docelowej długości kontekstu.
3. **Wybór harmonogramu (schedule)**: Wybierz spośród 1F1B, Zero Bubble, DualPipe lub DualPipeV. Schemat wyboru:
   - Trening modeli gęstych (dense) na mniej niż 500 GPU $\rightarrow$ Zero Bubble.
   - Modele MoE z równoległością ekspertów (Expert Parallelism) $\rightarrow$ DualPipe.
   - Trening modeli gęstych na ponad 500 GPU bez narzutu all-to-all $\rightarrow$ DualPipeV.
   - Mniejsze obciążenia na poniżej 100 GPU $\rightarrow$ 1F1B jest wystarczający.
4. **Oczekiwany udział bąbli potoku (pipeline bubble fraction)**: Oblicz wartość dla wybranego harmonogramu przy docelowych $P$ i $M$. Określ procentową oraz bezwzględną oszczędność w godzinach pracy GPU w porównaniu z klasycznym 1F1B przy zakładanym budżecie treningowym.
5. **Plan replikacji parametrów (dotyczy tylko DualPipe)**: Upewnij się, że 2-krotna replikacja parametrów mieści się w dostępnej pamięci VRAM. Określ efektywną gęstość parametrów na pojedynczy GPU, biorąc pod uwagę wybraną wartość $P$.

Zasady bezwzględnego odrzucenia (red flags):
- Stosowanie DualPipe przy braku równoległości ekspertów (Expert Parallelism). Dwukrotna replikacja wag nie jest uzasadniona, jeśli nie służy do nakładania i ukrywania kosztów komunikacji all-to-all w EP.
- Ustawienie $P > 64$ w dowolnym treningu. Frakcja bąbli rośnie liniowo wraz z $P$, niezależnie od wybranego harmonogramu.
- Liczba mikro-batchy niebędąca wielokrotnością 2 dla DualPipe/DualPipeV. Taki harmonogram jest matematycznie niemożliwy do zrealizowania.
- Stosowanie równoległości potokowej w sytuacjach, gdy model w całości mieści się w pamięci jednego GPU. Stosuj wyłącznie równoległość danych (Data Parallelism).

Kryteria odmowy zatwierdzenia:
- Jeśli połączenie sieciowe węzłów (interconnect) charakteryzuje się przepustowością $\le$ 200 Gb/s na GPU – odrzuć DualPipe i zarekomenduj DualPipeV. Okno czasowe na nałożenie operacji all-to-all na obliczenia jest zbyt wąskie, aby uzasadnić replikację wag.
- Jeśli użytkownik nie może dostarczyć zoptymalizowanych kerneli komunikacyjnych all-to-all dostosowanych do topologii klastra – rekomenduj Zero Bubble zamiast DualPipe.
- Jeśli całkowity wolumen danych treningowych wynosi mniej niż 1B tokenów – odrzuć plany stosowania równoległości potokowej i zarekomenduj połączenie równoległości danych (DP) oraz tensorowej (TP).

Rezultat: jednostronicowa specyfikacja zawierająca wartości $P$ i $M$, wybrany harmonogram, oczekiwaną frakcję bąbli, koszt pamięciowy replikacji parametrów (dla DualPipe) oraz rekomendacje dotyczące bibliotek i kerneli komunikacyjnych. Zakończ dokument sekcją „Kryterium wycofania (Fallback trigger)”, określającą minimalną wartość MFU (Model FLOPs Utilization) zmierzoną podczas pierwszych 1000 kroków, poniżej której należy wycofać modyfikacje i powrócić do prostszego schematu równoległości.
