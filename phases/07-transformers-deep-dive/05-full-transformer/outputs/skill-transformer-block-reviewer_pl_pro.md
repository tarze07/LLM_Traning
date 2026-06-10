---

name: transformer-block-reviewer
description: Przejrzyj implementację bloku modelu Transformer pod kątem zgodności z nowoczesnymi standardami oraz wykrywania błędów konfiguracyjnych (configuration drift).
version: 1.0.0
phase: 7
lesson: 5
tags: [transformers, architecture, review]

---

Na podstawie kodu źródłowego bloku Transformera (PyTorch / JAX / NumPy / pseudokod) oraz jego przeznaczenia (enkoder / dekoder / enkoder-dekoder) wygeneruj:

1. Połączenia i przepływ (wiring/routing): Pre-LN czy Post-LN. Obecność połączeń rezydualnych wokół każdej podwarstwy. Oznacz wariant Post-LN jako niezgodny z nowoczesnymi standardami, chyba że autor przedstawi konkretne uzasadnienie.
2. Normalizacja: LayerNorm vs RMSNorm. Preferowana jest RMSNorm. Wskaż, czy w projekcjach Q/K/V/O występują wektory obciążenia (bias terms) – większość modeli z nich rezygnuje.
3. Typ atencji: MHA/GQA/MQA/MLA. W przypadku bloków dekodera sprawdź obecność maski przyczynowej (causal mask). W przypadku atencji krzyżowej (cross-attention) upewnij się, że zapytania Q pochodzą z dekodera, a klucze/wartości K/V z enkodera.
4. Warstwa FFN: funkcja aktywacji (ReLU / GELU / SwiGLU / GeGLU) oraz współczynnik ekspansji (expansion factor). SwiGLU ze współczynnikiem ~2,67x jest nowoczesnym standardem; klasyczny wariant to 4x dla ReLU/GELU.
5. Kodowanie pozycyjne: potwierdź poprawność aplikacji RoPE / ALiBi / kodowania absolutnego (w przypadku RoPE weryfikacji wymagają projekcje Q i K).

Odmawiaj zatwierdzenia architektury bloku, która składa się z więcej niż 12 warstw w konfiguracji Post-LN bez harmonogramu rozgrzewki (warmup schedule) – taki trening będzie niestabilny (rozbieżny). Odrzucaj bloki dekodera bez maskowania przyczynowego (causal masking). Oznacz każdy blok, w którym współczynnik ekspansji warstwy FFN spada poniżej 2x, ze względu na ryzyko utraty zdolności reprezentacyjnych modelu. Ostrzegaj, jeśli rozmiar modelu `d_model` jest na sztywno wpisany w kodzie bez możliwości konfiguracji.
