---

name: sequence-architecture-picker
description: Wybierz architekturę modelowania sekwencji (RNN, Transformer, SSM, hybryda) na podstawie długości kontekstu, przepustowości i budżetu obliczeniowego.
version: 1.0.0
phase: 7
lesson: 1
tags: [transformers, architecture, rnn, ssm]

---

Na podstawie opisu problemu modelowania sekwencji (maksymalna długość sekwencji, rozmiar batcha, budżet tokenów treningowych, docelowe opóźnienie wnioskowania, klasa sprzętu docelowego) wygeneruj:

1. Rekomendowana architektura: Transformer, model przestrzeni stanów (SSM - np. Mamba/RWKV), hybryda SSM i mechanizmu atencji, lub RNN. Podaj jednozdaniowe uzasadnienie powiązane z głównym ograniczeniem projektu.
2. Strategia obsługi długiego kontekstu: dla Transformera: pełna atencja (full attention), okno przesuwne (sliding window) lub skalowanie pozycji RoPE. Dla SSM: rozmiar bloku/fragmentu skanowania (scan chunk size). Dla RNN: wymiar stanu ukrytego (hidden state dimension).
3. Oszacowanie kosztów obliczeniowych (FLOPs) treningu: przybliżona liczba FLOP-ów na token wynikająca z architektury i długości kontekstu. Wskaż, czy konfiguracja mieści się w zakładanym budżecie obliczeniowym.
4. Zużycie pamięci podczas wnioskowania (inference): rozmiar pamięci podręcznej KV Cache dla Transformerów, rozmiar stanu ukrytego dla SSM, narzut pamięci na token dla RNN. Zaznacz, czy docelowe urządzenie jest w stanie obsłużyć wnioskowanie dla batch size = 1.
5. Analiza ryzyka: jeden konkretny scenariusz awarii (np. błąd braku pamięci - OOM Transformera przy kontekście 64K na GPU z 24 GB VRAM bez użycia FlashAttention).

Odmawiaj rekomendowania czystych architektur RNN do treningu na zbiorach powyżej 1B tokenów bez jasnego określenia konsekwencji dla przepływu gradientu i możliwości zrównoleglenia obliczeń. Odmawiaj rekomendowania Transformerów z pełną atencją (full attention) dla kontekstów powyżej 64K bez jawnego wyliczenia kosztu pamięciowego klasy `O(N^2)`. Odmawiaj rekomendowania na środowiska produkcyjne nowo opublikowanych architektur (wydanych mniej niż 12 miesięcy temu) bez zdefiniowania sprawdzonego rozwiązania alternatywnego (fallback).
