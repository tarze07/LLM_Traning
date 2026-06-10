---

name: llava-vibes-eval
description: Przeprowadź 10-sekundową ocenę wibracji na VLM z rodziny LLaVA i utwórz czytelną dla człowieka kartę wyników.
version: 1.0.0
phase: 12
lesson: 05
tags: [llava, vlm, vibes-eval, instruction-tuning]

---

Mając VLM z rodziny LLaVA (LLaVA-1.5, LLaVA-NeXT, LLaVA-OneVision lub fork społecznościowy) i zestaw obrazów testowych, przeprowadź 10-zdaniowy test dymu obejmujący podpisy, VQA, rozumowanie, odmowę i zgodność formatu. Przygotuj kartę wyników potwierdzającą prawidłowe połączenie projektora i LLM.

Wyprodukuj:

1. Dziesięć podpowiedzi z opisami oczekiwanych zachowań:
   - Trzy napisy (krótkie, szczegółowe, kreatywne).
   - Trzy VQA (liczenie, kolor, obecność obiektu).
   - Dwa rozumowania (porównanie dwóch regionów, przyczyna i skutek).
   - Dwie odmowy (osoba prywatna, identyfikująca PII).
2. Wynik na zachętę. Zaliczony/częściowy/niezaliczony z uzasadnieniem jednowierszowym.
3. Ogólna diagnoza wzorca. Jeśli napisy przebiegną pomyślnie, ale VQA nie powiedzie się, podejrzewamy miksowanie danych na etapie 2. Jeśli szczegółowe napisy wskazują na halucynacje, podejrzewaj, że dane w stylu ShareGPT4V są niewystarczające. Jeżeli odmowa nie powiedzie się, oznacz lukę w danych dotyczących bezpieczeństwa.
4. Kontrola rozdzielczości. Uruchom jeden monit wymagający OCR w rozdzielczości bazowej 336x336 i ponownie w AnyRes; zwróć uwagę na deltę. Oczekiwana jest awaria w niskiej rozdzielczości; awaria wysokiej rozdzielczości oznacza, że ​​AnyRes jest źle skonfigurowany.
5. Sugerowane dalsze działania. Trzy konkretne dodatki do danych szkoleniowych, które obiekt wywołujący może uruchomić, jeśli określone kategorie zawiodą.

Twarde odrzucenia:
- Ocenianie VLM na podstawie wyników testów porównawczych bez uruchamiania pakietu wibracji. Można grać w benchmarki; wibracje ujawniają rzeczywistą gotowość do wdrożenia.
- Łączenie halucynacji ze stylistyczną gadatliwością. Oznacz konkretnie, które przedmioty zostały wymyślone, a które jedynie szczegółowo opisane.
- Żądanie przekazania podpowiedzi bez sprawdzania łańcucha rozumowania, a nie tylko ostatecznej odpowiedzi.

Zasady odmowy:
- Jeśli rozmówca poprosi o ocenę wibracji zastrzeżonego VLM (Gemini, Claude, GPT-5V) bez dostępu do API, odmów — test wymaga faktycznego wnioskowania.
- Jeśli docelowym przypadkiem użycia jest diagnoza medyczna lub porada prawna, odmów — vibes-eval nie jest certyfikatem i nie można go używać w domenach o wysoką stawkę.
- Jeśli nie dostarczono żadnych obrazów, odmów – test z definicji opiera się na obrazie.

Dane wyjściowe: karta wyników składająca się z 10 wierszy (podpowiedź, obraz, oczekiwany, rzeczywisty, pozytywny/częściowy/negatywny), ogólna diagnoza wzorca i trzyelementowa lista działań następczych. Zakończ akapitem „co dalej czytać” wskazującym na lekcję 12.06 (AnyRes) dotyczącą błędów związanych z rozdzielczością lub lekcję 12.07 (ablacje) dotyczącą dostrajania miksu danych.