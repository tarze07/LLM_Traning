---

name: moe-configurator
description: Dobierz architekturę Mixture of Experts (MoE) – liczbę ekspertów, parametry top-k, strategię równoważenia obciążenia oraz mechanizm ekspertów współdzielonych dla nowego modelu Transformer.
version: 1.0.0
phase: 7
lesson: 11
tags: [transformers, moe, mixture-of-experts, scaling]

---

Na podstawie specyfikacji modelu Transformer (całkowity budżet parametrów, liczba aktywnych parametrów na token, wolumen danych treningowych, sprzęt docelowy do wnioskowania) wygeneruj:

1. Układ MoE: wartości parametrów `n_experts`, `top_k`, `n_shared`. Wybierz podejście drobnoziarniste (fine-grained, np. >256 ekspertów, top-8) dla modeli o największej skali (frontier scale) lub podejście klasyczne (np. 8 ekspertów, top-2) dla mniejszych modeli. Podaj jednozdaniowe uzasadnienie.
2. Strategia równoważenia obciążenia (load balancing): bezstratna regularyzacja routera (auxiliary-loss-free, np. styl DeepSeek-V3, preferowana), klasyczna funkcja straty pomocniczej (auxiliary loss) lub ograniczenie pojemności ekspertów (expert capacity) z odrzucaniem nadmiarowych tokenów (token dropping). Podaj wartość współczynnika `γ`, jeśli wybrano metodę bezstratną.
3. Plan równoległości ekspertów (Expert Parallelism): schemat podziału ekspertów między karty GPU z uwzględnieniem pamięci VRAM. Podaj szacowane zużycie pamięci VRAM przez pojedynczego eksperta oraz wymagane zasoby sprzętowe.
4. Precyzja obliczeniowa routera (routing precision): analiza obliczeń w precyzji FP32 vs FP16. Wskazanie wpływu precyzji na stabilność routingu przy dużej skali.
5. Analiza ryzyka: zapadanie się routera (router collapse), wąskie gardła sieciowe podczas komunikacji All-to-All, narzut opóźnień (latency overhead) związany z procesem routingu, wymagania pamięciowe checkpointów.

Odmawiaj rekomendowania architektury MoE dla modeli o liczbie aktywnych parametrów poniżej 4B – klasyczne modele gęste (dense) osiągają lepsze wyniki przy tym samym budżecie obliczeniowym. Odmawiaj stosowania przestarzałych metod równoważenia opartych wyłącznie na klasycznych funkcjach straty pomocniczej (aux-loss) – standardem jest równoważenie bezstratne (aux-loss-free). Odmawiaj zatwierdzenia projektów MoE bez precyzyjnie określonego planu równoległości (Expert Parallelism), jeśli całkowity rozmiar parametrów modelu przekracza 80 GB. Oznaczaj projekty MoE dla scenariuszy z pojedynczym użytkownikiem (single-batch) o krytycznych wymaganiach opóźnienia (low-latency) jako potencjalnie wolniejsze od ich gęstych odpowiedników.
