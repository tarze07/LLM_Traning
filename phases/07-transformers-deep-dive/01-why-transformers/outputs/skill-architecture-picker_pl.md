---

name: sequence-architecture-picker
description: Wybierz architekturę sekwencji (RNN, transformator, SSM, hybryda) podając długość, przepustowość i budżet szkoleniowy.
version: 1.0.0
phase: 7
lesson: 1
tags: [transformers, architecture, rnn, ssm]

---

Biorąc pod uwagę problem z sekwencją (maksymalna długość, kształt partii, budżetowane tokeny szkoleniowe, docelowe opóźnienie wnioskowania, klasa urządzenia), wynik:

1. Architektura pierwotna. Jeden z nich: transformator, model przestrzeni stanów (Mamba/RWKV), hybrydowy SSM+uwaga, RNN. Powód jednozdaniowy powiązany z dominującym ograniczeniem.
2. Strategia długości kontekstu. W przypadku transformatora: odcięcie pełnej uwagi, rozmiar okna przesuwnego, współczynnik skalowania RoPE. Jeśli SSM: zeskanuj rozmiar fragmentu. Jeśli RNN: ukryta szerokość.
3. Treningowy profil FLOP. Przybliżone FLOPy na token z architektury + kontekstu; zwróć uwagę, czy specyfikacja mieści się w budżecie obliczeniowym.
4. Profil pamięci wnioskowania. Pamięć podręczna KV dla transformatorów, rozmiar stanu dla SSM, pamięć na token dla RNN. Oznacz, jeśli urządzenie docelowe może pomieścić pojedynczą partię 1.
5. Uwaga dotycząca ryzyka. Jeden konkretny tryb awarii, o którym wiadomo, że ten wybór występuje w skali specyfikacji (np. OOM transformatora w kontekście 64 KB na procesorze graficznym 24 GB bez Flash Attention).

Odmów polecania czystego RNN dla jakichkolwiek przebiegów treningowych powyżej tokenów 1B bez wyraźnego określenia kar za przepływ gradientu i równoległość. Odmów polecania transformatora pełnej uwagi dla kontekstu > 64K bez podania kosztu pamięci `O(N^2)`. Odmawiaj rekomendowania do produkcji zupełnie nowej architektury (opublikowanej <12 miesięcy temu) bez nazwanego rozwiązania awaryjnego.