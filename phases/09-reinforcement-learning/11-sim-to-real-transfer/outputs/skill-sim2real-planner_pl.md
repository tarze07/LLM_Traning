---

name: sim2real-planner
description: Zaplanuj potok transferu z symulacji do rzeczywistości dla danego robota + zadania, obejmujący DR, SI i bezpieczeństwo.
version: 1.0.0
phase: 9
lesson: 11
tags: [rl, sim2real, robotics, domain-randomization]

---

Biorąc pod uwagę platformę robota, zadanie i dostęp do rzeczywistego czasu sprzętowego, wynik:

1. Inwentaryzacja luk rzeczywistości. Podejrzane źródła uszeregowane według oczekiwanego wpływu (kontakt, wykrywanie, opóźnienie aktywacji, wizja).
2. Parametry DR. Dokładna lista, zakresy, dystrybucja. Uzasadnij każdy zakres względem rzeczywistych pomiarów.
3. Kroki SI. Jakie parametry mierzyć; metoda pomiaru.
4. Podział nauczyciel/uczeń. Z jakich uprzywilejowanych informacji korzysta nauczyciel; jakiego obs używa uczeń.
5. Koperta bezpieczeństwa. Ograniczenia niskiego poziomu, wyłączniki awaryjne, sterownik rezerwowy.

Odmów wdrożenia bez (a) testu wariantu symulacji zerowego strzału, (b) osłony zabezpieczającej, (c) planu wycofywania. Oznacz dowolny zakres DR szerszy niż 3× zmierzona rzeczywista zmienność jako prawdopodobnie nadmiernie losowy.