---

name: omni-streaming-budget
description: Dobiera rozmiar i optymalizuje budżet opóźnień dla strumieniowego potoku głosowego Thinker-Talker (Qwen-Omni / Moshi / Mini-Omni) na podstawie docelowego TTFAB.
version: 1.0.0
phase: 12
lesson: 20
tags: [qwen-omni, moshi, mini-omni, streaming, ttfab, thinker-talker]

---

Na podstawie specyfikacji systemu głosowego (docelowe opóźnienie TTFAB, częstotliwość próbkowania mikrofonu, obsługa wideo [tak/nie], wielojęzyczność, pełny dupleks) oraz ograniczeń obliczeniowych (klasa GPU, budżet), dobierz parametry i zwymiaruj potok Thinker-Talker.

Wygeneruj:

1. **Wybór rodziny modeli:** Moshi (najniższe opóźnienia), Qwen2.5-Omni (najlepszy zbiór otwartych funkcji), Qwen3-Omni (najwyższa jakość), Mini-Omni (najprostsza implementacja).
2. **Rozmiary modułów Thinker i Talker:** Thinker 7B + Talker 200-300M dla uzyskania TTFAB <400 ms. Zastosowanie klasy Thinker 70B+ podniesie jakość kosztem wyższego TTFAB.
3. **Szczegółowy rozkład TTFAB:** Oszacowanie opóźnienia z podziałem na każdy krok przetwarzania.
4. **Model konwersacji (Dupleks):** Tryb półdupleksu (naprzemienny) z przełączaniem tur przez VAD, lub pełny dupleks, jeśli produkt wymaga ciągłej obsługi wtrąceń (backchanneling).
5. **Obsługa wideo:** Integracja klatek wideo przy użyciu TMRoPE with bezwzględnymi znacznikami czasu.
6. **Architektura wdrożenia:** Uruchomienie na pojedynczej karcie GPU lub podział (Thinker na karcie A, Talker na karcie B) w zależności od wymagań dotyczących przepustowości.

Kryteria odrzucenia (Twarde reguły):
- Proponowanie modułu Talker o skali 70B. Talker musi być małym modelem, aby dotrzymać kroku wymaganemu tempu generowania tokenów audio.
- Stosowanie niestrumieniowego dekodera mowy. Powoduje to drastyczny wzrost (eksplozję) opóźnienia TTFAB.
- Traktowanie trybu pełnego dupleksu jako rozwiązania typu plug-and-play. Wdrożenie tego wymaga specyficznych danych treningowych.

Zasady odmowy (Rezygnacja z projektu):
- Jeśli docelowe opóźnienie TTFAB wynosi <200 ms, odrzuć modele większe niż zintegrowany model Moshi (skala 7B) na pojedynczym GPU A100.
- Jeśli produkt wymaga generowania muzyki w locie, odrzuć tę architekturę i zaproponuj wydzielony potok syntezy muzycznej.
- Jeśli wymagana jest ścisła obsługa dźwięku 48 kHz (jakość studyjna), wskaż konieczność wdrożenia silniejszego enkodera audio zamiast prostego resamplingu.

Dane wyjściowe: Jednostronicowy raport z planu wdrożenia strumieniowego zawierający wybór modelu, rozmiary modułów, rozbicie opóźnień TTFAB, model dupleksu, strategię integracji wideo oraz schemat wdrożenia. Na końcu umieść odnośniki do prac: arXiv 2503.20215 (Qwen2.5-Omni) oraz 2410.00037 (Moshi).
