---

name: checkpointing-planner
description: Dobierz strategię rekomputacji aktywacji (gradient checkpointing) dla poszczególnych warstw (brak, selektywny, pełny, offload) na podstawie konfiguracji treningowej i budżetu pamięci HBM.
version: 1.0.0
phase: 10
lesson: 34
tags: [gradient-checkpointing, activation-recomputation, selective-checkpoint, fsdp-offload, training-memory]

---

Na podstawie konfiguracji treningowej (liczba warstw L, wymiar ukryty d, długość sekwencji S, rozmiar mikro-batcha B, typ danych dtype/liczba bajtów na wartość, jądro attention, stopień równoległości tensora TP, stopień równoległości potoku PP, stopień równoległości ekspertów EP dla MoE) oraz wolnego budżetu pamięci HBM na rangę (po uwzględnieniu wag i stanu optymalizatora), wygeneruj:

1. Politykę rekomputacji dla poszczególnych warstw. Dla każdej rodziny warstw w modelu (embeddingi, attention, FFN, eksperci MoE, warstwy normalizacji, głowica wyjściowa) wybierz jedną z opcji: brak, selektywny, pełny lub offload (odciążenie do pamięci RAM CPU). Domyślnie rekomenduj selektywny checkpointing dla warstw attention, gdy S przekracza 4096; brak rekomputacji dla pozostałych przepływów i normalizacji; offload dla warstw FFN tylko wtedy, gdy zmierzony czas transferu PCIe dla aktywacji tych warstw jest krótszy niż czas ich rekomputacji.
2. Rozmiar segmentu k (chunk size). Jeśli włączony jest pełny checkpointing, dobierz k jako `round(sqrt(L))`, aby zbalansować narzut obliczeniowy, lub mniejsze k, gdy budżet pamięci jest silnie ograniczony przez aktywacje. Podaj dodatkowy narzut obliczeniowy w procentach jako `(1/k)` operacji FLOP fazy forward.
3. Interakcję z FlashAttention. Sprawdź, czy stosowane jądro attention dokonuje już rekomputacji macierzy softmax w locie. Jeśli tak, selektywny checkpointing na poziomie attention przyniesie minimalne korzyści; zmień rekomendację na brak rekomputacji w tym obszarze. Podaj nazwę jądra (FlashAttention-2/3, memory-efficient xFormers, standardowe).
4. Plan dla TP/PP. Dla Tensor Parallelism (TP) wskaż aktywacje wymagające operacji all-gather lub scatter podczas rekomputacji oraz dodatkowy wolumen komunikacji w bajtach na krok. Dla Pipeline Parallelism (PP) określ, które etapy potoku powinny być objte checkpointingiem od końca do końca w celu zwolnienia pamięci aktywacji przed wykonaniem fazy backward.
5. Bilans pamięci (matematyka budżetowa). Oszacuj rozmiar pamięci aktywacji przed i po wdrożeniu wybranej strategii (w MB na rangę). Oszacuj narzut obliczeniowy FLOP jako procent sumarycznych operacji fwd+bwd. Odrzuć projekty, które nie mieszczą się w budżecie HBM z zachowaniem 10% marginesu bezpieczeństwa.

Odradzaj stosowanie pełnego checkpointingu dla wszystkich warstw, jeśli zastosowanie selektywnej rekomputacji samej uwagi pozwala zmieścić się w budżecie (analiza profilu wykazuje, że narzut FLOP przy pełnym checkpointingu jest wielokrotnie wyższy niż przy selektywnym przy podobnej oszczędności pamięci). Odradzaj stosowanie offloadu, jeśli zmierzony czas transferu aktywacji warstwy przez magistralę PCIe przekracza czas potrzebny na ich ponowne obliczenie (rekomputacja jest wówczas szybsza). Odrzuć opcję „wszędzie checkpointing” przy treningu w formacie FP8, jeśli framework nie obsługuje poprawnie zapamiętywania historii wartości amax (ponowna kalkulacja zaburzy skalowanie i doprowadzi do cichej degradacji gradientów).

Przykładowe dane wejściowe: „L=64, d=8192, S=8192, B=1, bf16, FlashAttention-3, TP=8, PP=4, budżet HBM na rangę 32 GB po wagach, MoE z 8 ekspertami i EP=8.”

Przykładowe dane wyjściowe:
- Strategia dla poszczególnych warstw: selektywny dla attention, brak dla FFN, pełny dla ekspertów MoE, brak dla embeddingów, offload dla głowicy wyjściowej.
- Rozmiar segmentu (chunk size): pełny checkpointing zastosowany wyłącznie dla MoE przy k=8; narzut obliczeniowy 12% na ścieżce eksperckiej, 0% dla pozostałych warstw.
- Interakcja z FlashAttention: FA-3 rekomputuje macierz softmax w locie; selektywny checkpointing stosowany na poziomie wrappera warstwy, a nie wewnątrz samego jądra.
- Plan TP/PP: TP wymaga dodatkowych operacji all-gather podczas rekomputacji (dodatkowe 0,3 GB komunikacji na krok); PP stosuje pełny checkpointing na etapach początkowych; etap 3 PP przechowuje aktywacje do momentu wykonania ostatecznej fazy backward.
- Bilans pamięci: pamięć aktywacji bez wdrożonej strategii wynosi 38 GB, z wdrożoną strategią – 11 GB. Całkowity narzut obliczeniowy FLOP wynosi 7,5% sumy operacji fwd+bwd.
