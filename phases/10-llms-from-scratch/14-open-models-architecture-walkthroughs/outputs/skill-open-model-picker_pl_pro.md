---

name: open-model-picker
description: Wybór otwartej rodziny modeli LLM, metody kwantyzacji oraz stosu technologicznego do wnioskowania (inference) dla zadanego celu wdrożenia
version: 1.0.0
phase: 10
lesson: 14
tags: [open-models, llama, deepseek, mixtral, qwen, gemma, moe, gqa, mla, quantization]

---

Dla zadanego celu wdrożenia (typ GPU, pamięć VRAM na układ GPU, liczba układów GPU, docelowa długość kontekstu, docelowe opóźnienie p50/p99, szczytowa liczba jednoczesnych zapytań) oraz profilu zadania (czat, kod, rozumowanie, wyszukiwanie w długim kontekście, korzystanie z zewnętrznych narzędzi/API), zaproponuj otwarty model LLM oraz stos serwujący (serving stack) wraz z uzasadnieniem dla każdego z sześciu kryteriów architektonicznych z lekcji 14.

Zwróć:

1. **Krótką listę modeli**: Trzech kandydatów. Dla każdego podaj: całkowitą liczbę parametrów, liczbę aktywnych parametrów (w przypadku MoE), cechy architektury (metoda normalizacji, funkcja aktywacji, kodowanie pozycyjne, typ atencji, konfiguracja MoE, okno kontekstowe) oraz jednozdaniowe uzasadnienie wyboru.
2. **Walidację budżetu pamięci**: Dla rekomendowanego kandydata określ: rozmiar wag w formacie BF16 oraz przy wybranym typie kwantyzacji; rozmiar KV cache przy docelowym oknie kontekstu i docelowym batch_size; margines na aktywacje. Wycofaj rekomendację, jeśli suma (wagi + KV cache + aktywacje) przekracza dostępną pamięć VRAM.
3. **Dobór kwantyzacji**: Wybór spośród GPTQ-4bit, AWQ-4bit, FP8 lub BF16. Uzasadnij wybór wrażliwością zadania na utratę precyzji (zadania programistyczne, matematyczne i logiczne są znacznie bardziej czułe na agresywną kwantyzację niż czat czy wyszukiwanie informacji).
4. **Stos technologiczny do wnioskowania**: Wybór spośród vLLM, TensorRT-LLM, SGLang lub llama.cpp. Uzasadnij wybór na podstawie zapotrzebowania na ciągły batching, wsparcia dla dekodowania spekulatywnego, kompatybilności z wybranym formatem kwantyzacji oraz planowanej topologii (jedno- lub wielowęzłowej).
5. **Weryfikację przepustowości**: Szacunkowa prędkość przetwarzania fazy prefill (tokeny/s) oraz dekodowania (tokeny/s) wyliczona na podstawie przepustowości pamięci GPU (faza decode) oraz TFLOPS (faza prefill). Odrzuć rekomendację, jeśli szacowana przepustowość fazy dekodowania nie pozwala na obsługę zakładanej liczby jednoczesnych użytkowników.
6. **Opcję zapasową (Fallback)**: Drugi wybór na wypadek, gdyby najlepszy kandydat przekroczył budżet VRAM lub nie spełnił wymagań przepustowości. Zawsze wskaż jedną alternatywę.

Zasady bezwzględnego odrzucenia (red flags):
- Modele gęste (dense) o rozmiarze powyżej 30B na pojedynczym konsumenckim GPU z 24 GB VRAM bez zastosowania offloadingu lub agresywnej kwantyzacji.
- Modele MoE uruchamiane na stosie serwującym bez wdrożonej obsługi równoległości ekspertów (expert parallelism).
- Długi kontekst (128k+ tokenów) uruchamiany na architekturach bez GQA lub MLA (grozi gwałtownym przepełnieniem KV cache).
- Rekomendacje, które nie określają dokładnej wersji modelu (np. podaj „Llama 3.1 8B Instruct”, zamiast ogólnego „Llama 3”).

Rezultat: jednostronicowa specyfikacja zawierająca rekomendację modelu, kwantyzacji i stosu, wraz z ustrukturyzowanym uzasadnieniem dla każdej decyzji. Zakończ dokument sekcją „Kiedy warto ponownie przeanalizować wybór…”, wskazując zmianę warunków wdrożeniowych lub założeń biznesowych, która wpłynęłaby na zmianę rekomendacji.
