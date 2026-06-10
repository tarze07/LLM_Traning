---

name: checkpointing-planner
description: Wybierz politykę ponownego obliczania aktywacji dla każdej warstwy (brak / selektywna / pełna / odciążenie), biorąc pod uwagę konfigurację szkoleniową i budżet HBM.
version: 1.0.0
phase: 10
lesson: 34
tags: [gradient-checkpointing, activation-recomputation, selective-checkpoint, fsdp-offload, training-memory]

---

Biorąc pod uwagę konfigurację szkoleniową (liczba warstw L, ukryty rozmiar d, długość sekwencji S, mikropartia B, typ dtype bajtów na wartość, jądro uwagi, stopień równoległości tensora TP, stopień równoległości potoku PP, stopień równoległości eksperckiej EP w przypadku MoE) oraz budżet HBM na rangę po wagach i stanie optymalizatora, wynik:

1. Zasady dotyczące poszczególnych warstw. Dla każdej rodziny warstw w stosie (osadzanie, uwaga, FFN, ekspert MoE, norma, głowica wyjściowa) nie wybieraj żadnej, selektywne, pełne lub odciążające. Domyślnie selektywny dla uwagi, gdy S przekracza 4_096; domyślnie brak dla pozostałych strumieni i norm; domyślnie odciąża FFN tylko wtedy, gdy zmierzony czas transferu PCIe dla aktywacji tej warstwy jest krótszy niż zmierzony czas ponownego obliczenia.
2. Rozmiar segmentu k. Jeśli włączone jest pełne punktowanie, wybierz k jako round(sqrt(L)), aby uzyskać jednolity koszt warstwy, mniejsze k, gdy w budżecie dominuje pamięć aktywacyjna. Zgłoś dodatkowy procent FLOP jako (1/k) FLOPów forward.
3. Interakcja FlashAttention. Sprawdź, czy jądro uwagi już przelicza softmax. Jeśli tak, selektywne sprawdzanie uwagi niewiele daje; zniż do żadnego. Podaj nazwę jądra (FlashAttention-2/3, wydajne pod względem pamięci xFormers, waniliowe).
4. Plan TP/PP. W przypadku TP podaj nazwy aktywacji, które wymagają gromadzenia lub ponownego rozproszenia podczas ponownego obliczania, oraz dodane bajty komunikacji na każdym etapie. W przypadku PP należy potwierdzić, które etapy rurociągu są sprawdzane od końca do końca, aby odwrócić mikropartie zwalniając pamięć aktywacji przed ponownym przepływem.
5. Matematyka budżetowa. Przewiduj pamięć aktywacji przed i po polityce (w MB na rangę). Przewiduj narzut FLOP jako procent fwd+bwd. Odrzuć każdy plan, który nie mieści się w budżecie HBM z 10-procentowym zapasem.

Odmawiaj pełnego sprawdzania każdej warstwy, gdy selektywność wyłącznie na podstawie uwagi zamyka budżet; profile pokazuje, że narzut FLOP jest wielokrotnie wyższy niż selektywny dla tej samej oszczędności pamięci, a dokładny stosunek zależy od obciążenia. Odmawiaj odciążania, gdy zmierzony czas transferu aktywacji warstwy na docelowym łączu PCIe przekracza zmierzony czas ponownego obliczenia; przeliczyć wygrane. Odrzuć „wszędzie punkt kontrolny” w przypadku szkolenia w ramach 8PR, jeśli wybrane środowisko nie tworzy migawki historii amax; ponowne obliczenia przesuną skalę i po cichu uszkodzą gradienty.

Przykładowe dane wejściowe: „L=64, d=8192, S=8192, B=1, bf16, FlashAttention-3, TP=8, PP=4, budżet HBM na rangę 32 GB po wagach, MoE z 8 ekspertami i EP=8.”

Przykładowe wyjście:
- Polityka dotycząca poszczególnych warstw: selektywna względem uwagi, brak FFN, pełny ekspert MoE, brak osadzania, odciążanie głowicy wyjściowej.
- Rozmiar segmentu: całkowicie zastosowany na MoE tylko przy k=8; Narzut FLOP 12 procent na ścieżce eksperckiej, 0 gdzie indziej.
- Interakcja FlashAttention: FA-3 już przelicza softmax; selektywny na opakowaniu warstwy, a nie wewnątrz jądra.
- Plan TP/PP: TP zbiera dane wejściowe podczas ponownego obliczania, 0,3 GB na krok dodatkowych połączeń; PP etapuje każdy punkt kontrolny w pełnym zakresie; Etap 3 PP zachowuje swoje aktywacje do końcowego biegu wstecznego.
- Obliczenia budżetowe: aktywacje 38 GB bez polisy, 11 GB z polisą. Całkowity narzut FLOP 7,5 procent fwd+bwd.