---

name: open-model-picker
description: Wybierz otwartą rodzinę LLM, kwantyzację i stos wnioskowania dla danego celu wdrożenia.
version: 1.0.0
phase: 10
lesson: 14
tags: [open-models, llama, deepseek, mixtral, qwen, gemma, moe, gqa, mla, quantization]

---

Biorąc pod uwagę cel wdrożenia (typ procesora graficznego, pamięć VRAM na procesor graficzny, liczba procesorów graficznych, docelowa długość kontekstu, docelowe opóźnienie p50/p99, szczytowa liczba jednoczesnych żądań) i profil zadania (czat, kod, rozumowanie, pobieranie długiego kontekstu, użycie narzędzi), zarekomenduj model otwarty i stos obsługujący z wyraźnym uzasadnieniem każdego z sześciu elementów architektonicznych z lekcji 14.

Wyprodukuj:

1. Krótka lista modeli. Trzej kandydaci, każdy z całkowitymi parametrami, aktywnymi parametrami (obsługujący MoE), flagami architektury (norma / aktywacja / pozycja / uwaga / MoE / kontekst) i pojedynczym powodem, dla którego znalazł się na krótkiej liście.
2. Sprawdzenie budżetu pamięci. Dla najlepszego kandydata: pamięć wagowa przy BF16 i przy wybranej kwantyzacji; Pamięć podręczna KV w kontekście docelowym dla docelowej wielkości partii; zapas aktywacji. Zatrzymaj zalecenie, jeśli wagi + pamięć podręczna KV + aktywacje przekraczają dostępną pamięć VRAM.
3. Wybór kwantyzacji. GPTQ-4bit, AWQ-4bit, FP8 lub BF16. Uzasadnij wrażliwość zadania na dokładność (zadania związane z kodem/matematyką/wnioskowaniem są bardziej narażone na agresywną kwantyzację niż czat lub pobieranie).
4. Stos wnioskowania. vLLM, TensorRT-LLM, SGLang lub llama.cpp. Uzasadnij: konieczność ciągłego przetwarzania wsadowego, obsługa dekodowania spekulatywnego, zgodność formatu kwantyzacji oraz topologia jedno- i wielowęzłowa.
5. Kontrola poprawności przepustowości. Szacunki dotyczące wstępnego wypełniania tokenów/s i dekodowania tokenów/s na podstawie przepustowości pamięci GPU (dekodowanie) i wartości TFLOP (wstępne wypełnianie). Odrzuć zalecenie, jeśli przepustowość dekodowania jest niższa niż dolna granica liczby jednoczesnych użytkowników docelowych.
6. Powrót. Drugi wybór, jeśli najlepszy kandydat przekracza budżet pamięci VRAM lub przepustowości. Zawsze wymieniaj jedno.

Twarde odrzucenia:
- Gęste modele powyżej 30B na jednym konsumenckim procesorze graficznym 24 GB bez odciążania i agresywnej kwantyzacji.
- Modele MoE na stosie obsługującym bez wsparcia równoległego ekspertów.
- Długi kontekst (128 tys.+) na architekturach bez GQA lub MLA (eksploduje pamięć podręczna KV).
- Wszelkie zalecenia, które nie zawierają nazwy konkretnej wersji modelu (np. „Llama 3 8B Instruct v3.1”, a nie „Llama 3”).

Wynik: jednostronicowy model zawierający rekomendacje, kwantyzację, stos, z numerowanymi dowodami dla każdej decyzji. Zakończ akapitem „warto rozważyć ponownie, jeśli…”, podając nazwę konkretnej możliwości lub parametru wdrożenia, który mógłby zmienić wybór.