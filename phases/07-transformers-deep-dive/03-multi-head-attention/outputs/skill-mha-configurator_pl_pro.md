---

name: mha-configurator
description: Dobierz wariant mechanizmu atencji (MHA / MQA / GQA / MLA) oraz konfigurację głowic (liczba głowic Q i KV) dla nowego modelu Transformer.
version: 1.0.0
phase: 7
lesson: 3
tags: [transformers, attention, mha, gqa]

---

Na podstawie specyfikacji modelu Transformer (budżet parametrów, wymiar ukryty `d_model`, docelowa długość kontekstu, pamięć urządzenia wnioskowania, priorytet: trening vs wnioskowanie) wygeneruj:

1. Wybrany wariant atencji: jeden z MHA, GQA, MQA, MLA. Podaj jednozdaniowe uzasadnienie powiązane z limitami pamięci podręcznej KV Cache.
2. Geometria głowic: wartości parametrów `n_heads`, `n_kv_heads`, `d_head`. Wartości te muszą spełniać zależności: `d_model = n_heads * d_head` oraz `n_heads % n_kv_heads == 0`.
3. Oszacowanie rozmiaru KV Cache: liczba bajtów na token na warstwę (dla precyzji FP16) przy docelowej długości kontekstu. Oznacz przypadek, gdy obsługa pojedynczego batcha przekracza pamięć urządzenia docelowego.
4. Inicjalizacja wag: metoda inicjalizacji wag (Xavier/Kaiming) dla macierzy wag Q, K, V, O. Określ, czy stosowane są wektory obciążenia (bias terms) – większość nowoczesnych modeli rezygnuje z nich.
5. Test syntetyczny (testability hook): opis prostego zadania syntetycznego (np. wzorzec powtarzania sekwencji typu induction head: `A B A ? → B`), które dwuwarstwowy model w tej konfiguracji powinien rozwiązać ze skutecznością ≥95% po przeszkoleniu.

Odmawiaj rekomendowania wymiaru głowicy `d_head < 32` – grozi to niestabilnością dynamiki atencji. Odmawiaj rekomendowania standardowej atencji MHA z `n_heads > 16` dla kontekstów dłuższych niż 32K bez jawnego wyliczenia rozmiaru pamięci podręcznej KV Cache i zasugerowania w zamian GQA lub MLA. Odmawiaj rekomendowania atencji MLA dla modeli o rozmiarze poniżej 1B parametrów, chyba że użytkownik wyraźnie zażąda takiego porównania.
