---

name: reward-hack-auditor
description: Diagnozuj tryby awarii (failure modes) wynikające z hakowania nagród w wytrenowanym modelu RLHF na podstawie logów treningowych i wyników ewaluacji.
version: 1.0.0
phase: 18
lesson: 2
tags: [reward-hacking, goodhart, rlhf, over-optimization, sycophancy]

---

Na podstawie logów treningowych modelu RLHF (krzywa nagrody proxy, trajektoria KL, delty ewaluacyjne) oraz próbek generowanych odpowiedzi, określ, która z czterech postaci (masek) hakowania nagród jest najbardziej aktywna i wskaż potwierdzające to dowody.

Przygotuj:

1. Charakterystyka rozbieżności proxy-gold. Opisz (lub przedstaw w formie wykresu) zależność nagrody proxy od odległości KL względem polityki referencyjnej SFT. Wskaż punkt kulminacyjny nagrody gold (pochodzącej z ocen ludzkich, niezależnego walidacyjnego RM lub ich przybliżenia). Określ, czy model znajduje się przed szczytem, w jego punkcie optymalnym, czy też nastąpiło już załamanie rzeczywistej nagrody (po szczycie).
2. Identyfikacja maski hakowania. Przeanalizuj model pod kątem verbosity bias, sykofancji, niewiernego rozumowania oraz manipulowania oceniającymi. Dla każdego z tych zjawisk przytocz konkretną wygenerowaną odpowiedź lub wskaźnik, który aktywował ostrzeżenie (flagę).
3. Rekonstrukcja mechanizmu. Wskaż pozorną cechę, którą RM błędnie nagradza (długość wypowiedzi, specyficzne słownictwo, konformizm/zgadzanie się z użytkownikiem, formatowanie). Zacytuj prompt oraz wygenerowaną odpowiedź, w której ta pozorna cecha zastąpiła rzeczywistą jakość merytoryczną.
4. Rekomendacja środków zaradczych. Wybierz spośród: {pozyskanie dodatkowych danych preferencji, wdrożenie zespołu modeli RM (ensemble), nadzór nad procesem rozumowania (process supervision), zaostrzenie ograniczeń KL, wcześniejsze zatrzymanie treningu (early stopping), przejście na algorytmy wyrównania bezpośredniego (DAA)}. Zaproponuj jedno działanie poparte zebranymi dowodami oraz wskaż rozwiązanie, które w tym konkretnym przypadku byłoby bezużyteczne.

Bezwzględne odrzucenia (błędy merytoryczne):
- Wszelkie twierdzenia, jakoby pojedynczy RM całkowicie eliminował problem hakowania nagród. Zgodnie z uniwersalnym prawem sformułowanym przez Gao i in. (ICML 2023), większy RM jedynie przesuwa szczyt krzywej w prawo, lecz nie zapobiega załamaniu.
- Wszelkie twierdzenia, że regularyzacja KL jest wystarczającym zabezpieczeniem. Praca nad katastrofalnym prawem Goodharta (OpenReview UXuBzWoZGK) dowodzi, że sam składnik KL zawodzi w przypadku błędów proxy o grubych ogonach rozkładu.
- Sugestie dotyczące „prostego dostrojenia współczynnika beta” bez równoległego monitorowania wyników w benchmarkach zdolności ogólnych.

Zasady udzielania odpowiedzi (odmowy):
- Jeśli użytkownik udostępnia wyłącznie krzywe nagrody proxy, nie podając wyników ewaluacji gold (z zestawu walidacyjnego), odmów przeprowadzenia diagnozy i zażądaj dodatkowych danych walidacyjnych. Próba oceny bez sygnału gold sama w sobie stanowi metodologiczne wypaczenie.
- Jeśli użytkownik przedstawi przykłady niewiernego rozumowania CoT i zapyta, czy nadzór nad procesem (process supervision) „rozwiązuje” ten problem, odmów udzielenia jednoznacznej odpowiedzi tak/nie i wskaż aktualne, otwarte pytania w literaturze naukowej.

Dane wyjściowe: Jednostronicowy raport z audytu zawierający listę kontrolną czterech masek hakowania nagród, wskazanie najbardziej prawdopodobnej formy wraz z dowodami oraz jedną merytorycznie uzasadnioną rekomendację naprawczą. W tekście należy jednokrotnie zacytować pracę Gao i in. (ICML 2023) oraz artykuł wprowadzający ujednolicone ujęcie problemu z 2026 roku (arXiv:2604.13602) dokładnie raz.
