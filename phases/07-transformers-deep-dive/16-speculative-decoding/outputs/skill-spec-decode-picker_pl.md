---

name: spec-decode-picker
description: Wybierz spekulatywną strategię dekodowania (waniliowa / Medusa / EAGLE / lookahead) i dostosuj parametry dla nowego obciążenia wnioskowaniem LLM.
version: 1.0.0
phase: 7
lesson: 16
tags: [inference, decoding, latency, speculative, optimization]

---

# Selektor spekulatywnego dekodowania

Pomóż inżynierowi wybrać pomiędzy dekodowaniem spekulatywnym, Medusa, EAGLE lub dekodowaniem z wyprzedzeniem i dostosuj `N` (długość robocza) do określonego obciążenia.

## Dane wejściowe do zebrania

1. **Model weryfikatora** — który LLM generuje końcowy wynik. Rozmiar ma znaczenie (koszt wersji roboczej musi wynosić < verifier cost for speedup).
2. **Workload type** — code, chat, structured output, summarization. Determines acceptance rate.
3. **Sampling strategy** — greedy, low-T, high-T, beam. High-T sampling degrades acceptance.
4. **Hardware target** — memory budget determines if you can fit a separate draft model.
5. **Engineering budget** — Medusa and EAGLE need fine-tuning; vanilla and lookahead don't.
6. **Latency target** — interactive chat (<500ms TTFT, <50ms per token) vs batch (throughput-first).

## Decision rules

- **Quick start, no training**: vanilla draft with a same-family 1B–3B model. 2× typical.
- **You can fine-tune**: EAGLE-2 or EAGLE-3 using the verifier's hidden states. 3–4× typical.
- **You can fine-tune but can't run two models**: Medusa (extra heads on verifier). 2–3×.
- **No training budget, no draft model available**: lookahead decoding. 1.3–1.6×.
- **Batch-heavy serving**: continuous batching matters more; speculative gains diminish as batch grows because the verifier is already saturated.
- **High temperature or stochastic sampling**: acceptance drops sharply. Consider lower N (2–3) or disabling.
- **Structured output (JSON, code)**: acceptance is high. Push N to 7+ for max speedup.

## Tuning

- **N (draft length)**: start at 5. Measure acceptance. If α > 0,9, przejdź do 7. Jeśli α < 0.6, drop to 3.
- **Draft temperature**: match the verifier's temperature. Mismatched draft sampling loses α.
- **Tree depth (EAGLE-2 / Medusa)**: 3–5 branches; wider trees help only at α > 0,8.
- **Rozmiar modelu roboczego**: najmniejszy, który osiąga α > 0,7. Typowy jest projekt 1B dla weryfikatora 70B; nie schodź poniżej zgodności tokenizatora/osadzania weryfikatora.

## Zawsze flaguj

- Sprawdź, czy wersja robocza i weryfikator mają wspólny tokenizer. Różne podziały BPE łamią gwarancje spekulacyjne.
- Dekodowanie specyfikacji współdziała z ciągłym przetwarzaniem wsadowym w vLLM: przyspieszenie na żądanie spada, gdy partia jest już nasycona.
- Wejście stanu ukrytego EAGLE wymaga wewnętrznych elementów weryfikatora; nie zawsze ujawniane za pośrednictwem interfejsów API HF. Preferuj środowiska wykonawcze vLLM lub SGLang.
- Głowy meduz wymagają nadzorowanego dostrojenia wyników własnych weryfikatora. Etap gromadzenia danych jest często kosztem dominującym.

##Format wyjściowy

Powrót:

1. **Zalecenie** — jedna nazwa strategii i parametry strojenia (np. „EAGLE-2, N=5, głębokość_drzewa=4”).
2. **Oczekiwane przyspieszenie** — przy wyraźnym założeniu α.
3. **Kontrola zgodności** — dopasowanie tokenizera, obsługa środowiska wykonawczego, obsługa przywracania pamięci podręcznej KV.
4. **Plan awaryjny** – co dalej próbować, jeśli podstawowa strategia nie przynosi oczekiwanych rezultatów.
5. **Plan pomiarów** — jak zweryfikować stopień akceptacji i przyspieszenie na reprezentatywnej próbie.