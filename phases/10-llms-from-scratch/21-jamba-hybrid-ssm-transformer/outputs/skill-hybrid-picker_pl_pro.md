---

name: hybrid-picker
description: Wybierz optymalną architekturę (czysty Transformer, hybryda w stylu Jamba lub czysty SSM) dla danego obciążenia.
version: 1.0.0
phase: 10
lesson: 21
tags: [jamba, mamba, ssm, hybrid, long-context, memory-budget, architecture]

---

Na podstawie specyfikacji obciążenia (profil długości kontekstu p50/p99, profil zadań, budżet pamięci GPU, docelowa przepustowość, priorytet jakość/szybkość) dobierz odpowiedni model spośród: czystego Transformera (+MoE +MLA), hybrydy w stylu Jamba lub czystego modelu Mamba.

Wygeneruj:

1. Klasyfikację długości kontekstu. Podziel na zakresy: krótki (poniżej 16 tys.), średni (16–64 tys.), długi (64–256 tys.) lub bardzo długi (ponad 256 tys. tokenów). Podejmij decyzję na samym początku.
2. Rekomendację architektoniczną. Wybierz spośród opcji: czysty Transformer, hybrydy w proporcjach 1:7, 1:3, 1:15 lub czysta Mamba. Uzasadnij wybór długością kontekstu oraz wymaganiami zadania w zakresie wyszukiwania/przywoływania informacji (context recall).
3. Weryfikację budżetu pamięci. Oblicz rozmiar KV cache oraz stan SSM dla docelowego kontekstu. Upewnij się, że model zmieści się w pamięci docelowego akceleratora po uwzględnieniu wag i pamięci aktywacji (zwykle dodatkowe 10–20 GB poza wagami i KV cache).
4. Zestawienie kompromisów jakościowych. Udokumentuj wpływ wybranego poziomu rzadkości (sparsity) na jakość działania modelu. Modele hybrydowe o proporcjach poniżej 1:7 wykazują mierzalny spadek skuteczności wyszukiwania informacji w kontekście; czysta Mamba gorzej radzi sobie z niektórymi zadaniami wymagającymi śledzenia stanu (state tracking).
5. Zgodność ze stosem technologicznym wnioskowania (inferencji). Potwierdź wsparcie dla wybranej architektury w docelowym frameworku (vLLM, TensorRT-LLM, SGLang, llama.cpp). Narzędzia dla modeli hybrydowych są słabiej rozwinięte w porównaniu do czystych Transformerów.

Kategoryczne odrzucenia:
- Stosowanie hybrydy w stylu Jamba dla kontekstów krótszych niż 16 tys. tokenów – narzut architektoniczny przewyższa korzyści.
- Stosowanie czystej Mamby do zadań wymagających złożonego rozumowania lub analizy porównawczej wielu dokumentów (cross-document reasoning). Ograniczenia w śledzeniu stanu negatywnie wpływają na efektywność.
- Proporcje hybrydowe rzadsze niż 1:15. Poniżej tej wartości przywoływanie informacji z kontekstu staje się niestabilne.
- Wszelkie rekomendacje przekraczające wyliczony budżet pamięci dla wskazanego akceleratora.

Zasady odmowy wykonania zadania:
- Jeśli obciążenie produkcyjne łączy zarówno krótkie, jak i długie konteksty, odrzuć rekomendację hybrydową i zaproponuj czysty Transformer (najlepiej z MLA) — modele hybrydowe wykazują największą przewagę przy przewadze zadań długokontekstowych.
- Jeśli docelowym akceleratorem jest karta klasy konsumenckiej (24 GB VRAM lub mniej), odrzuć pełne modele hybrydowe i zalecaj małe destylowane hybrydy lub skwantowany czysty Transformer.
- Jeśli wymagana jest generacja o niskich opóźnieniach przy batch size = 1, a model jest nowy (brak sprawdzonych ścieżek wdrożeniowych), odrzuć i zalecaj dobrze wspierany czysty Transformer z dekodowaniem spekulatywnym (faza 10, lekcja 15) jako prostsze i stabilniejsze rozwiązanie.

Format wyjściowy: Jednostronicowa rekomendacja zawierająca klasyfikację długości kontekstu, wybraną architekturę, zapotrzebowanie na KV cache, wykaz kompromisów jakościowych oraz zgodność ze stosem wnioskowania. Zakończ sekcją „Co monitorować”, wskazującą konkretny test długiego kontekstu (L-Eval, LongBench, Needle In A Haystack - NIAH), który zweryfikuje poprawność decyzji w trakcie pierwszych 10 tysięcy zapytań produkcyjnych.
