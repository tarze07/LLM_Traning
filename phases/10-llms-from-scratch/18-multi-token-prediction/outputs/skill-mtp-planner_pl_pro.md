---

name: mtp-planner
description: Planowanie integracji mechanizmu Multi-Token Prediction (MTP) na potrzeby nowego procesu pre-trainingu
version: 1.0.0
phase: 10
lesson: 18
tags: [mtp, multi-token-prediction, deepseek-v3, pre-training, speculative-decoding]

---

Na podstawie parametrów pre-trainingu (skala modelu, wymiar ukryty, liczba warstw, budżet tokenów, topologia GPU, docelowe wdrożenie) oraz zdefiniowanego celu (gęstszy sygnał treningowy vs wykorzystanie modułu jako modelu draft w dekodowaniu spekulatywnym vs oba), stwórz plan integracji mechanizmu MTP.

Zwróć:

1. **Głębokość D (liczba dodatkowych tokenów)**: Wybierz 1 lub 2. DeepSeek-V3 stosuje głębokość $D=1$, co pozwala na uzyskanie wskaźnika akceptacji (acceptance rate) w dekodowaniu spekulatywnym na poziomie $\ge$ 80%. Ustawienie $D=2$ charakteryzuje się malejącymi korzyściami (diminishing returns) przy rosnącym narzucie. Uzasadnij wybór budżetem obliczeniowym – każda kolejna głębokość dodaje w przybliżeniu jeden pełny blok obliczeniowy Transformera na krok treningowy.
2. **Harmonogram zmian parametru $\lambda$ (waga straty MTP)**: Domyślnie: 0,3 przez pierwsze 10% treningu, następnie spadek do 0,1. Zwiększ wartość do 0,5 na początku treningu dla mniejszych modeli (poniżej 7B), gdzie gęstszy sygnał ma większe znaczenie; skoryguj wartość w dół, jeśli strata MTP (MTP loss) zacznie dominować nad stratą główną (main loss).
3. **Budżet parametrów**: Określ liczbę dodatkowych parametrów wprowadzanych przez moduły MTP w odniesieniu do modelu głównego. Upewnij się, że przyrost liczby parametrów nie przekracza 5% dla modeli gęstych (dense) lub 3% dla modeli MoE.
4. **Narzut pamięciowy i obliczeniowy**: Oszacuj dodatkową liczbę operacji FLOP na krok dla przejścia w przód (w przybliżeniu `D * koszt_bloku_transformatora`), przyrost pamięci dla przejścia wstecznego (pamięć aktywacji dla modułów o głębokości $D$) oraz dodatkowe zapotrzebowanie na szczytową pamięć VRAM (współdzielone warstwy osadzeń i LM head nie generują narzutu, lecz bloki projekcji i warstwy Transformera dla modułu MTP – tak).
5. **Integracja w fazie wnioskowania (inference integration)**: Opisz sposób wykorzystania modułów MTP jako wbudowanych modeli draft na potrzeby dekodowania spekulatywnego podczas wnioskowania. Wskaż mechanizm weryfikacji tokenów oraz logikę cofania stanów KV cache (KV rollback). Potwierdź kompatybilność z docelowym stosem (vLLM, SGLang lub TensorRT-LLM).

Zasady bezwzględnego odrzucenia (red flags):
- Próba dodania modułów MTP do gotowego modelu (dense pre-trained) wytrenowanego bez nich. Brak możliwości wstecznego dodania (retrofitting) – moduły MTP muszą przejść wspólny proces pre-trainingu.
- Ustawienie $D > 2$ w pierwszej integracji. Przyrost wydajności powyżej $D=1$ jest znikomy, podczas punktu gdy złożoność kodu i narzut obliczeniowy rosną gwałtownie.
- Stosowanie MTP w modelach o liczbie aktywnych parametrów poniżej 1B. Zysk z dodatkowego sygnału jest mniejszy niż narzut obliczeniowy.
- Stosowanie równoległych głowic wyjściowych (w stylu Gloeckle'a), gdy głównym celem jest dekodowanie spekulatywne. Tokeny te nie są generowane przyczynowo (brak zależności autoregresyjnej).

Kryteria odmowy zatwierdzenia:
- Jeśli w zbiorze treningowym dominują krótkie sekwencje (poniżej 2k tokenów) – odrzuć projekt. Zyski z MTP opierają się na założeniu, że sekwencje są wystarczająco długie, by nadzór nad kolejnymi tokenami miał znaczenie.
- Jeśli docelowy stos nie wspiera dekodowania spekulatywnego – pamiętaj, że MTP nadal dostarcza gęstszy sygnał gradientu podczas uczenia (pre-training benefit); możesz kontynuować, ale oznacz ten fakt jako niespójność konfiguracji.
- Jeśli użytkownik zamierza kontynuować pre-training na istniejącym checkpointcie bez MTP – odrzuć projekt i rekomenduj wdrożenie MTP wyłącznie od początku nowego procesu treningowego lub przy pełnym resecie rozkładu danych.

Rezultat: jednostronicowy plan integracji zawierający: głębokość $D$, harmonogram zmian parametru $\lambda$, narzut parametrów (bezwzględny oraz procentowy), narzut obliczeniowy (procentowy wzrost kosztu na krok treningowy) oraz architekturę integracji dekodowania spekulatywnego. Zakończ dokument sekcją „Kryterium sukcesu”, wskazującą mierzalną metrykę uzasadniającą wdrożenie MTP (np. wskaźnik akceptacji dla głębokości 1 po przetworzeniu 50B tokenów musi przekraczać 70%, w przeciwnym razie należy wycofać modyfikację architektury).
