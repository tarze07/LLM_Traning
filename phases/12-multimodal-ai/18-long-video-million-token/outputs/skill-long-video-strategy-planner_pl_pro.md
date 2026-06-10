---

name: long-video-strategy-planner
description: Wybiera strategię przetwarzania długich nagrań wideo (siłowy kontekst, RingAttention, kompresja tokenów lub wyszukiwanie agentowe) oraz oblicza opóźnienie i skuteczność wyszukiwania.
version: 1.0.0
phase: 12
lesson: 18
tags: [long-video, gemini, ring-attention, videoagent, retrieval]

---

Na podstawie czasu trwania wideo, stopnia złożoności zapytania (lokalizacja pojedynczego zdarzenia czy globalne podsumowanie) oraz wymagań dotyczących licencji (open-source vs komercyjne), dobierz strategię analizy wideo i wygeneruj odpowiednią konfigurację.

Wygeneruj:

1. **Wybór strategii:** Przetwarzanie siłowe (brute-force context), uwaga pierścieniowa (RingAttention - LongVILA), kompresja tokenów (Video-XL) lub wyszukiwanie agentowe (VideoAgent).
2. **Budżet tokenów:** Wyliczenie typu: `czas_trwania * FPS * tokeny_na_klatkę`. Wygeneruj ostrzeżenie, jeśli wynik przekracza dopuszczalny kontekst LLM.
3. **Oczekiwana skuteczność wyszukiwania (Recall):** Wskazanie prawdopodobieństwa odnalezienia „igły w stogu siana” w zależności od długości nagrania. W stosownych przypadkach przytocz oficjalne raporty dla Gemini 1.5.
4. **Opóźnienia:** Szacowany czas przetwarzania promptu (prefill time) w podejściu siłowym, lub czas wyszukiwania i analizy wybiórczej w podejściu agentowym.
5. **Zarys implementacji:** Szkielet kodu ilustrujący działanie wybranej strategii.
6. **Rozwiązanie hybrydowe (plan awaryjny):** Globalne streszczenie oparte na skompresowanym kontekście w połączeniu z wyszukiwaniem agentowym dla pytań szczegółowych.

Kryteria odrzucenia (Twarde reguły):
- Proponowanie bezpośredniego przetwarzania pełnego kontekstu dla dwugodzinnego filmu przy użyciu otwartego modelu klasy 72B. Taki wolumen danych nie zmieści się w oknie kontekstowym.
- Zakładanie, że wyszukiwanie agentowe jest zawsze optymalnym wyborem. W przypadku pytań o charakterze globalnym (wymagających syntezy całego filmu) podejście to traci przewagę nad pełnym przetwarzaniem kontekstu.
- Rekomendowanie kompresji tokenów bez jasnego wskazania, że obniża to skuteczność wyszukiwania informacji.

Zasady odmowy (Rezygnacja z projektu):
- Jeśli wymagana skuteczność wyszukiwania dla 90-minutowego nagrania wynosi >95%, odrzuć otwarte modele i zarekomenduj Gemini 2.5 Pro.
- Jeśli budżet czasowy lub finansowy nie pozwala na wykonywanie pętli wywołań narzędzi (tool calls), odrzuć wyszukiwanie agentowe i zaproponuj skompresowane przetwarzanie siłowe.
- Jeśli użytkownik wymaga przetwarzania w czasie rzeczywistym (analiza na bieżąco podczas odtwarzania), odrzuć wyszukiwanie agentowe jako zbyt wolne i poleć strumieniowanie za pomocą Qwen2.5-VL.

Dane wyjściowe: Jednostronicowy raport zawierający wybraną strategię, budżet tokenów, oczekiwaną skuteczność Recall, szacowane opóźnienia, zarys kodu oraz plan awaryjny. Na końcu dodaj odnośniki do prac: arXiv 2403.05530 (Gemini 1.5) oraz 2403.10517 (VideoAgent).
