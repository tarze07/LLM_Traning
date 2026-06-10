---

name: inference-server
description: Dostarczaj serwer wnioskowania z dekodowaniem spekulatywnym z wersjami roboczymi EAGLE-3 lub P-EAGLE, automatycznym skalowaniem K8 i pełnym raportem dotyczącym przepustowości/opóźnień/kosztów.
version: 1.0.0
phase: 19
lesson: 14
tags: [capstone, inference, vllm, sglang, eagle-3, p-eagle, speculative-decoding, quantization, hpa]

---

Biorąc pod uwagę dwa otwarte modele docelowe (Llama 3.3 70B i Qwen3-Coder-30B MoE lub GPT-OSS-120B), wyślij produkcyjny stos obsługujący z dekodowaniem spekulatywnym, kwantyzacją i autoskalowaniem Kubernetes. Publikuj zmierzone przyspieszenia i wartości opóźnień końcowych.

Plan budowy:

1. Wdróż modele docelowe w vLLM 0.7 (lub SGLang 0.4) z kwantyzacją Marlin FP8.
2. Załaduj dostosowaną wersję roboczą EAGLE-3 z Red Hat Speculators (lub wytrenuj ją za pośrednictwem SpecForge).
3. Liczby bazowe: tokeny/s i opóźnienie p50/p99 w partii 1/8/32 bez spekulacji.
4. Włącz EAGLE-3. Uruchom ponownie ten sam test porównawczy. Przyspieszenie raportu, współczynnik akceptacji, delta opóźnienia ogona p99.
5. Włącz równoległą spekulację P-EAGLE; zgłoś przegięcie, w którym głębsze drzewa pomagają, a nie szkodzą.
6. Przeprowadź testy porównawcze w różnych dystrybucjach: ShareGPT, HumanEval, dane domeny. Opublikuj zmianę współczynnika akceptacji.
7. Powtórz na drugim modelu docelowym (MoE); zidentyfikować wrażliwość na zakłócenia tras w akceptacji projektu.
8. Wdróż na platformie Kubernetes ze śledzeniem HPA `queue_wait_ms`. Zademonstruj skalowanie w poziomie przy trzykrotnym obciążeniu.
9. Porównaj tokeny $/1M z Anthropic Claude Sonnet 4.7 i OpenAI GPT-5.4 na dopasowanych ewaluacjach.

Rubryka oceny:

| Waga | Kryterium | Pomiar |
|:-:|---|---|
| 25 | Zmierzone przyspieszenie w porównaniu z wartością bazową | Ponad 2,5x przepustowość przy dopasowanej jakości w obu modelach |
| 20 | Wskaźnik akceptacji dla realistycznego ruchu | Raport dotyczący współczynnika akceptacji poszczególnych dystrybucji |
| 20 | Dyscyplina opóźnienia ogona P99 | p99 w partii 1/8/32 ze spekulacjami i bez |
| 20 | Operacje | Wdrażanie K8, HPA w oczekiwaniu na kolejkę, płynne wdrażanie, aktualizacja polegająca przede wszystkim na wyczerpaniu zasobów |
| 15 | Opis i metodologia | Jasne wyprowadzenie metryk, dopasowane wartości bazowe |

Twarde odrzucenia:

- Raportowanie przepustowości w stanie ustalonym bez opóźnień końcowych.
- HPA na procesorze zamiast oczekiwania w kolejce. Będzie się miotał przy nasyceniu GPU.
- Ignorowanie dostosowania wersji roboczej do docelowej. Dryfujące wersje robocze kosztują więcej niż brak spekulacji.
- Porównania kosztów, które pomijają rabaty na buforowanie natychmiastowe hostowanych interfejsów API.

Zasady odmowy:

- Odmówić podania bez odpływu. Uaktualnianie na miejscu w trakcie realizacji żądań jest dyskwalifikujące.
- Odmów zgłaszania współczynnika akceptacji zagregowanego w różnych dystrybucjach. Dystrybucja jest obowiązkowa.
- Odmów uznania wygranych w dekodowaniu spekulatywnym przy bs=32 bez dopasowanej liczby niespekulacyjnej.

Dane wyjściowe: repozytorium zawierające konfiguracje vLLM/SGLang, wersję roboczą skryptu do pobrania EAGLE-3, manifesty wdrożenia K8, konfigurację HPA w kolejce oczekiwania, zestaw testów porównawczych dla danych ShareGPT/HumanEval/domeny, tabelę porównawczą tokenów $/1M oraz opis wymieniający trzy wprowadzone spekulatywne dekodowanie regresji opóźnienia ogona i łagodzenie (bramkowanie wsadowe, powrót ngramów, modyfikacja kwantyzacji), które naprawiony każdy.