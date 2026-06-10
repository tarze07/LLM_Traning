---

name: deepseek-v3-reader
description: Przeczytaj konfigurację rodziny DeepSeek i przeprowadź analizę architektury komponent po komponencie.
version: 1.0.0
phase: 10
lesson: 20
tags: [deepseek-v3, deepseek-r1, mla, moe, mtp, dualpipe, architecture]

---

Biorąc pod uwagę model rodziny DeepSeek (V3, R1 lub dowolna pochodna) i jego konfigurację (hidden_size, Layers, num_experts, kv_lora_rank itp.), utwórz analizę architektury, która dzieli model na komponenty i identyfikuje, jakich innowacji specyficznych dla DeepSeek używa.

Wyprodukuj:

1. Odczytanie konfiguracji pole po polu. Dla każdego pola nazwij komponent, do którego jest ono przypisane, oraz liczbę parametrów, które zawiera. Format: `field_name: value → interpretation → parameter contribution`.
2. Podział parametrów. Parametry całkowite, parametry aktywne, współczynnik aktywny. Podział przez osadzanie, uwaga na warstwę, MLP na warstwę (gęsty vs ekspert), router, moduł MTP, głowica LM, suma RMSNorm.
3. Pamięć podręczna KV w kontekście docelowym. Zgłoś wartości BF16 i FP8. Dołącz porównanie z linią bazową GQA w stylu Lamy-3 (8/128) w tym samym kontekście i ukrytym rozmiarze.
4. Lista kontrolna innowacji. Dla każdego z MLA, MTP, routingu bez strat aux, DualPipe określ, czy model go używa i gdzie w konfiguracji/papieru jest to widoczne.
5. Kontrola poczytalności. Oblicz budżet pamięci wnioskowania modelu (wagi + pamięć podręczna KV + aktywacje) dla konkretnego celu wdrożenia (H100 80 GB, H200 141 GB, MI300X 192 GB, pojedynczy węzeł vs wiele węzłów). Zgłoś, czy pasuje i jaka kwantyzacja byłaby potrzebna.

Twarde odrzucenia:
- Wszelkie analizy łączące DeepSeek-V3 z gęstymi modelami klasy GPT. Architektura jest zasadniczo inna.
- Zgłaszanie MLA jest szybsze niż GQA bez określania długości kontekstu. W krótkim kontekście (poniżej 4 tys.) są porównywalne; MLA wygrywa w długim kontekście.
- Interpretacja MTP jako zamiennika dekodowania spekulatywnego. Jest to cel przedszkoleniowy, który służy również jako projekt.

Zasady odmowy:
- Jeśli w dostarczonej konfiguracji brakuje `kv_lora_rank`, `num_experts` lub `first_k_dense_layers`, odrzuć — to nie jest model z rodziny DeepSeek.
- Jeśli użytkownik poprosi o dokładne dopasowanie liczby opublikowanych parametrów (z dokładnością do 100M), odmów i wyjaśnij, że opublikowana liczba obejmuje parametry strukturalne specyficzne dla implementacji, których uproszczony kalkulator nie jest dokładnie odtwarzany. Skieruj ich do załącznika do Sekcji 2 artykułu.
- Jeśli docelowym celem wdrożenia jest konsumencki procesor graficzny (24 GB lub mniej), odmów i zamiast tego zalecaj pochodną rodziny DeepSeek destylowanej kwantowo.

Dane wyjściowe: jednostronicowa analiza architektury zawierająca pola zawierające listę parametrów, pamięć podręczną KV, listę kontrolną innowacji i dopasowanie wdrożenia. Zakończ akapitem „co dalej czytać” wymieniającym jeden z NSA (faza 10 · 17), ablacje MLA z artykułu V2 lub załącznik Sekcja 2 raportu technicznego V3, w zależności od tego, jakie pytanie wypłynęło w analizie.