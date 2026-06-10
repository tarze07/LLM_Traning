---

name: vla-action-format-picker
description: Wybierz format działania (dyskretny pojemnik, FAST, dopasowanie przepływu, podwójny system) i rodzinę VLA (RT-2, OpenVLA, π0, GR00T) dla zadania robota.
version: 1.0.0
phase: 12
lesson: 21
tags: [vla, rt-2, openvla, pi0, groot, action-tokenization]

---

Biorąc pod uwagę zadanie robota (manipulacja, nawigacja, humanoid obejmujący całe ciało), liczbę DOF, wymagania dotyczące szybkości sterowania i ograniczenia obliczeniowe, wybierz format akcji i rodzinę VLA.

Wyprodukuj:

1. Format działania. Dyskretny pojemnik do prostych zadań z jednym ramieniem, FAST do trajektorii wrażliwych na prędkość, dopasowanie przepływu dla płynnej, ciągłej kontroli, podwójny system dla humanoidów.
2. Wybór rodziny VLA. RT-2 (zamknięty), OpenVLA (otwarty 7B), π0 (otwarty przepływ), GR00T N1 (otwarty humanoid z dwoma systemami).
3. Możliwość kontroli szybkości. Dopasuj przepustowość formatu do wymaganej częstotliwości sterującej. Dyskretny pojemnik nie może pracować > 10 Hz w modelu 7B.
4. Mieszanka danych treningowych. Współczynnik współdostrojenia (sieć VQA: robot). Zacznij od 0,5:1, dostosowuj według zadania.
5. Dostosuj plan. LoRA na demonstracjach ~ 500-1000 zadań; pełne dostrojenie przy ~10 tys. dem.
6. Bramki zabezpieczające. Wymagane kontrole warstwy kontrolnej poza VLA.

Twarde odrzucenia:
— Zalecanie VLA bez specyfikacji warstwy bezpieczeństwa. Zawsze uwzględniaj ograniczenia połączeń i obcinanie prędkości.
- Twierdzenie, że tokenizacja dyskretna jest wystarczająco szybka, aby zapewnić kontrolę przy częstotliwości 30 Hz. Tak nie jest.
- Proponowanie dopasowywania przepływów bez odpowiednich ograniczeń gładkości. Nadal zdarzają się akcje poza dystrybucją.

Zasady odmowy:
- Jeżeli wymagana częstotliwość sterowania > 50 Hz na <=7B model with discrete-bin format, refuse; recommend π0 or a specialized head.
- If robot has >30 DOF (humanoidalnym), należy odrzucić architekturę jednostopniową; wymagają systemu podwójnego (GR00T).
- Jeśli budżet nie pozwala na wstępne szkolenie w skali Open X-Embodiment, odmów VLA od zera; zalecamy dostrojenie OpenVLA.

Dane wyjściowe: jednostronicowy plan z formatem akcji, wybór VLA, kontrola szybkości kontroli, miks dostrajający, bramki zabezpieczające. Zakończ za pomocą arXiv 2307.15818 (RT-2), 2406.09246 (OpenVLA), 2410.24164 (π0), 2503.14734 (GR00T).