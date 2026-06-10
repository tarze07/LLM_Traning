---

name: spec-decode-picker
description: Wybierz strategię spekulatywnego dekodowania (tradycyjna / Medusa / EAGLE / lookahead) i dostosuj parametry pod kątem konkretnego obciążenia roboczego podczas wnioskowania z LLM.
version: 1.0.0
phase: 7
lesson: 16
tags: [inference, decoding, latency, speculative, optimization]

---

# Selektor spekulatywnego dekodowania

Pomóż inżynierowi wybrać odpowiednią strategię dekodowania spekulatywnego (tradycyjna / Medusa / EAGLE / lookahead) oraz dostosować `N` (długość sekwencji próbnej) do konkretnego obciążenia roboczego.

## Dane wejściowe do zebrania

1. **Model weryfikujący (verifier model)** – model LLM, który zatwierdza końcowe tokeny. Rozmiar ma znaczenie (koszt działania modelu pomocniczego/roboczego (draft model) musi być znacząco niższy od kosztu weryfikatora, aby uzyskać przyspieszenie).
2. **Typ obciążenia (workload)** – kod, czat, ustrukturyzowane dane wyjściowe (JSON), streszczanie tekstu. Determinuje to współczynnik akceptacji (acceptance rate).
3. **Strategia próbkowania (sampling)** – zachłanne (greedy), niska temperatura (low-T), wysoka temperatura (high-T), poszukiwanie wiązkowe (beam search). Próbkowanie z wysoką temperaturą obniża współczynnik akceptacji.
4. **Docelowy sprzęt** – budżet pamięci określa, czy w pamięci GPU zmieści się oddzielny model pomocniczy (draft).
5. **Budżet inżynieryjny** – metody Medusa i EAGLE wymagają dostrajania (fine-tuning); tradycyjne dekodowanie spekulatywne i lookahead tego nie wymagają.
6. **Docelowe opóźnienie (latency)** – czat interaktywny (<500 ms TTFT, <50 ms na token) kontra przetwarzanie wsadowe (priorytetem jest przepustowość).

## Reguły decyzyjne

- **Szybki start, brak treningu**: Tradycyjne dekodowanie spekulatywne z modelem pomocniczym (draft) o rozmiarze 1B–3B z tej samej rodziny. Zazwyczaj daje to ok. 2-krotne przyspieszenie.
- **Możliwość przeprowadzenia dostrajania**: EAGLE-2 lub EAGLE-3 wykorzystujące stany ukryte (hidden states) weryfikatora. Zazwyczaj daje to 3–4-krotne przyspieszenie.
- **Możliwość dostrajania, ale brak zasobów na uruchomienie dwóch modeli**: Medusa (dodatkowe głowice predykcyjne na weryfikatorze). Zazwyczaj daje to 2–3-krotne przyspieszenie.
- **Brak budżetu na trening i brak dostępnego modelu pomocniczego**: Dekodowanie typu lookahead. Zazwyczaj daje to 1.3–1.6-krotne przyspieszenie.
- **Przetwarzanie intensywnie wsadowe (batch-heavy)**: Ciągłe tworzenie pakietów (continuous batching) ma większe znaczenie; zyski z dekodowania spekulatywnego maleją wraz ze wzrostem rozmiaru paczki (batch size), ponieważ weryfikator jest już w pełni obciążony.
- **Wysoka temperatura lub próbkowanie stochastyczne**: Współczynnik akceptacji gwałtownie spada. Rozważ zmniejszenie wartości N (do 2–3) lub całkowite wyłączenie spekulacji.
- **Ustrukturyzowane dane wyjściowe (JSON, kod)**: Współczynnik akceptacji jest wysoki. Można zwiększyć N do 7+, aby uzyskać maksymalne przyspieszenie.

## Strojenie (Tuning)

- **N (długość sekwencji próbnej)**: Zacznij od 5. Zmierz współczynnik akceptacji (α). Jeśli α > 0,9, zwiększ N do 7. Jeśli α < 0,6, zmniejsz N do 3.
- **Temperatura modelu pomocniczego (draft)**: Powinna być dopasowana do temperatury weryfikatora. Rozbieżność temperatur obniża współczynnik akceptacji (α).
- **Głębokość drzewa (EAGLE-2 / Medusa)**: Zazwyczaj 3–5 gałęzi; szersze drzewa pomagają tylko przy α > 0,8.
- **Rozmiar modelu pomocniczego**: Najmniejszy model, który osiąga α > 0,7. Typowym wyborem jest model pomocniczy 1B dla weryfikatora 70B; upewnij się, że tokenizator i embeddingi modelu pomocniczego są zgodne z weryfikatorem.

## Zawsze ostrzegaj (Zwróć uwagę na)

- Sprawdź, czy model pomocniczy (draft) i weryfikator korzystają z tego samego tokenizera. Różne słowniki BPE uniemożliwiają poprawne działanie spekulacji.
- Dekodowanie spekulatywne wchodzi w interakcję z ciągłym tworzeniem pakietów (continuous batching) w vLLM: zyski z przyspieszenia maleją, gdy karta GPU jest w pełni obciążona dużym batchem.
- EAGLE wymaga dostępu do wewnętrznych stanów ukrytych weryfikatora; nie zawsze są one eksponowane przez standardowe API Hugging Face. Preferuj dedykowane środowiska uruchomieniowe, takie jak vLLM lub SGLang.
- Głowice Medusa wymagają nadzorowanego uczenia na wyjściach generowanych przez sam weryfikator. Etap zbierania tych danych często stanowi główną część kosztów wdrożenia.

## Format wyjściowy

Zwróć:

1. **Rekomendacja** – nazwa strategii i parametry strojenia (np. „EAGLE-2, N=5, głębokość_drzewa=4”).
2. **Oczekiwane przyspieszenie** – przy wyraźnie określonym założeniu dotyczącym współczynnika akceptacji (α).
3. **Weryfikacja zgodności** – dopasowanie tokenizera, wsparcie ze strony środowiska uruchomieniowego, obsługa przywracania pamięci podręcznej KV (KV Cache rollbacks).
4. **Plan awaryjny** – alternatywne rozwiązania na wypadek, gdyby podstawowa strategia nie przyniosła oczekiwanych rezultatów.
5. **Plan pomiarów** – sposób weryfikacji współczynnika akceptacji i rzeczywistego przyspieszenia na reprezentatywnej próbie.
