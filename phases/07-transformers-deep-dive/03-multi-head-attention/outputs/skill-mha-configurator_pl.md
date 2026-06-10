---

name: mha-configurator
description: Zalecenia dotyczące liczby głowic, liczby głowic KV i strategii projekcji (MHA / MQA / GQA / MLA) dla nowego transformatora.
version: 1.0.0
phase: 7
lesson: 3
tags: [transformers, attention, mha, gqa]

---

Biorąc pod uwagę specyfikację transformatora (budżet parametrów, ukryty rozmiar `d_model`, docelową długość kontekstu, pamięć urządzenia wnioskowania, priorytet treningu a priorytet wnioskowania), wynik:

1. Wariant projekcji. Jeden z: MHA, GQA, MQA, MLA. Powód składający się z jednego zdania powiązany z ograniczeniami pamięci podręcznej KV.
2. Geometria główki. `n_heads`, `n_kv_heads`, `d_head`. Wartości muszą spełniać wymagania `d_model = n_heads * d_head` i `n_heads % n_kv_heads == 0`.
3. Oszacowanie pamięci podręcznej KV. Bajty na token na warstwę (fp16) dla wybranego wariantu przy docelowej długości kontekstu. Oznacz, jeśli jedna partia przekracza pamięć urządzenia docelowego.
4. Inicjalizacja. Skala Xaviera/Kaiminga dla macierzy Q, K, V, O. Zwróć uwagę, czy uwzględniono terminy dotyczące stronniczości (większość modeli z 2026 r. je pomija).
5. Hak testowalny. Pojedyncze zadanie syntetyczne (np. wzorzec głowicy indukcyjnej `A B A ? → B`), które wyszkolona dwuwarstwowa wersja tej konfiguracji powinna rozwiązać w ≥95%.

Odmów zalecenia `d_head < 32` – załamanie dynamiki uwagi. Odmawiaj rekomendowania MHA z `n_heads > 16` dla długości kontekstów powyżej 32 KB bez wyraźnej wyceny pamięci podręcznej KV i sugerowania zamiast tego GQA lub MLA. Odmawiaj sugerowania MLA dla modeli o parametrach poniżej 1B, chyba że użytkownik wyraźnie je porówna.