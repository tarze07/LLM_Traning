---

name: classifier-designer
description: Dobierz architekturę, metody augmentacji, strategię radzenia sobie z nierównowagą klas oraz metryki ewaluacji dla zadanego problemu klasyfikacji audio.
version: 1.0.0
phase: 6
lesson: 03
tags: [audio, classification, beats, ast]

---

Na podstawie zadanego problemu klasyfikacji audio (domena, liczba klas, gęstość etykiet na klip, wielkość zbioru danych, docelowe środowisko wdrożeniowe), określ:

1. Architekturę: k-NN na MFCC / 2D CNN / AST / BEATs / enkoder Whisper. Podaj jednozdaniowe uzasadnienie wyboru.
2. Augmentację: parametry SpecAugment (maksymalny rozmiar maski czasowej, liczba masek częstotliwości), współczynnik Mixup alpha, poziom dodawanego szumu tła (SNR).
3. Strategię radzenia sobie z nierównowagą klas: Zrównoważone próbkowanie (balanced sampler) vs. Focal Loss vs. wagi klas (class weights). Dobierz metodę w oparciu o stosunek liczebności klas rzadkich do dominujących.
4. Funkcję straty i metryki: Cross-Entropy (CE) / Binary Cross-Entropy (BCE) / Focal Loss; określ główną metrykę (Top-1 Accuracy / mAP / Macro F1-score) oraz metryki pomocnicze.
5. Podział danych i plan ewaluacji: Stratyfikowana walidacja krzyżowa (k-fold), podział rozłączny pod kątem mówców (speaker-disjoint split) dla zadań związanych z mową, lub podział chronologiczny (temporal split) w przypadku danych przesyłanych strumieniowo.

Zasady weryfikacji:
- Odrzuć projekty klasyfikacji wieloetykietowej (multi-label), które jako jedyną metrykę stosują ogólną dokładność (Accuracy); wymagaj użycia wskaźnika mAP.
- Odrzuć plany ewaluacji dla zadań zależnych od mówcy, które nie stosują podziału na rozłączne zbiory mówców (speaker-disjoint split) między zbiorem treningowym a testowym.
- Zgłoś zastrzeżenie (oznacz jako błąd) w przypadku uczenia architektury od zera (from scratch) dla zbiorów danych zawierających mniej niż 10 000 etykietowanych klipów — w takich sytuacjach wymagaj użycia wstępnie wytrenowanego modelu bazowego (SSL backbone).
