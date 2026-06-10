---

name: moe-configurator
description: Wybierz liczbę ekspertów, top-k, strategię równoważenia i układ wspólnego eksperta dla nowego transformatora MoE.
version: 1.0.0
phase: 7
lesson: 11
tags: [transformers, moe, mixture-of-experts, scaling]

---

Biorąc pod uwagę specyfikację transformatora (całkowity budżet parametrów, pożądane aktywne parametry na token, dostępne tokeny szkoleniowe, sprzęt do wnioskowania), wynik:

1. Układ MŚ. `n_experts`, `top_k`, `n_shared`. Wybierz drobnoziarnisty (ponad 256 ekspertów, 8 najlepszych) dla skal granicznych; klasyczny (8 ekspertów, top-2) dla mniejszych. Powód w jednym zdaniu.
2. Strategia równoważenia. Pomocnicza bez strat (DeepSeek-V3, domyślnie), utrata pomocy pomocniczej w stylu przełącznika lub pojemność ekspercka + upuszczenie tokena. Nazwij wartość `γ`, jeśli jest ona pozbawiona strat aux.
3. Ekspercki plan równoległości. Jak podzielić ekspertów na różne procesory graficzne, biorąc pod uwagę pamięć VRAM. Podaj koszt pamięci VRAM na eksperta i całkowitą wielkość floty.
4. Precyzja routingu. Wyniki routera FP32 w porównaniu z FP16. Precyzja routera ma znaczenie w skali.
5. Kontrola trybu awaryjnego. Nazwane ryzyko: awaria routera, brak ekspertów, wąskie gardło sieci, opóźnienia w wnioskowaniu wynikające z narzutu routingu, zużycie pamięci przez punkt kontrolny.

Odmów rekomendowania MoE dla liczby aktywnych parametrów poniżej 4B – gęste wygrywa przy dopasowanych obliczeniach. W przypadku nowych projektów w 2026 r. odmów bilansowania pomocniczego opartego wyłącznie na stratach (domyślnie jest to bilansowanie bezstratne). Odmów wysłania MoE bez planu równoległego dla ekspertów, jeśli łączna wielkość parametrów przekracza 80 GB. Oznacz MoE dla ścieżek pojedynczego użytkownika o krytycznym opóźnieniu jako prawdopodobnie wolniejsze niż gęste odpowiedniki.