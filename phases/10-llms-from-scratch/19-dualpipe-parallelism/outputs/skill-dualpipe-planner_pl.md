---

name: dualpipe-planner
description: Zaplanuj strategię równoległości potoku (1F1B, Zero Bubble, DualPipe, DualPipeV) dla klastra szkoleniowego.
version: 1.0.0
phase: 10
lesson: 19
tags: [pipeline-parallelism, dualpipe, dualpipev, zero-bubble, expert-parallelism, distributed-training]

---

Biorąc pod uwagę specyfikację klastra szkoleniowego (całkowita liczba procesorów graficznych, topologia połączeń międzysieciowych, model akceleratora, pamięć na procesor graficzny), kształt modelu (parametry całkowite, parametry aktywne, MoE lub gęstość, oczekiwana liczba warstw) oraz docelową objętość danych szkoleniowych, zarekomenduj strategię równoległości potoku i potwierdź oczekiwaną frakcję bąbelków.

Wyprodukuj:

1. Głębokość potoku P. Wybierz na podstawie budżetu pamięci GPU (musi zmieścić się jeden stopień potoku na rangę), MoE w porównaniu z gęstością i przepustowością połączeń wzajemnych. Zasięg: 4 dla małych klastrów, 16–32 dla przygranicznych szkoleń MoE.
2. Liczba mikropartii M. Musi być podzielna przez 2 dla DualPipe i DualPipeV. Typowy stosunek M/P pomiędzy 8 a 16. Uzasadnij cele akumulacji gradientowej i pamięć aktywacji przy docelowej długości sekwencji.
3. Wybór harmonogramu. Wybierz spośród 1F1B, Zero Bubble, DualPipe, DualPipeV. Tabela decyzyjna: gęsty trening poniżej 500 procesorów graficznych -> Zero Bubble. MoE z fachową równoległością -> DualPipe. Gęsty trening powyżej 500 procesorów graficznych bez obciążania wszystkich -> DualPipeV. Małe obciążenia poniżej 100 procesorów graficznych -> 1F1B jest w porządku.
4. Oczekiwana frakcja pęcherzyków. Oblicz dla wybranego harmonogramu przy docelowych P i M. Podaj wartość procentową i bezwzględną zaoszczędzoną liczbę godzin GPU w porównaniu z 1F1B przy całkowitym budżecie szkoleniowym.
5. Plan replikacji parametrów (tylko DualPipe). Upewnij się, że replikacja parametrów 2x mieści się w dostępnej pamięci VRAM. Zgłoś efektywną gęstość parametrów na procesor graficzny, biorąc pod uwagę wybraną opcję P.

Twarde odrzucenia:
- DualPipe bez zaawansowanej równoległości. Dwukrotna replikacja nie jest uzasadniona bez ukrywania komunikatów obciążających EP.
- P > 64 w dowolnym biegu treningowym. Frakcja pęcherzykowa rośnie liniowo wraz z P, niezależnie od harmonogramu.
- Liczba mikropartii nie jest podzielna przez 2 dla DualPipe/DualPipeV. Harmonogram nie zostanie zamknięty.
- Równoległość potoku w ogóle występuje, gdy model mieści się w pamięci jednego procesora graficznego. Używaj tylko równoległości danych.

Zasady odmowy:
- Jeśli połączenie wzajemne ma prędkość 200 Gb/s lub wolniejszą na procesor graficzny, odrzuć DualPipe i poleć DualPipeV. Okno nakładania się wszystkich na wszystkich jest zbyt wąskie, aby uzasadnić replikację.
- Jeśli użytkownik nie może zapewnić niestandardowego jądra typu „wszystko dla wszystkich” odpowiedniego dla jego topologii klastra, zaleca się opcję Zero Bubble zamiast DualPipe.
— Jeśli przebieg szkoleniowy jest niższy niż tokeny 1B, całkowicie odrzuć planowanie równoległości potoku i zaleć równoległość danych plus równoległość tensora.

Dane wyjściowe: jednostronicowy plan zawierający listę P, M, harmonogram, oczekiwaną część bąbelków, koszt replikacji parametrów (w przypadku DualPipe) i kompleksowe zalecenia dotyczące jądra. Zakończ akapitem „wywołanie wycofywania”, podając konkretny wskaźnik wykorzystania (łączny procent wykorzystania procesora graficznego mierzony w pierwszych 1000 krokach), który uzasadniałby przejście na prostszy harmonogram, jeśli docelowa liczba nie zostanie osiągnięta.