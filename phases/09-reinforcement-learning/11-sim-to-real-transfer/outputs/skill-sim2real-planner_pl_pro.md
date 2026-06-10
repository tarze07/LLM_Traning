---

name: sim2real-planner
description: Zaplanuj proces transferu z symulacji do rzeczywistości (sim-to-real) dla określonej platformy robotycznej i zadania, uwzględniając randomizację dziedziny (DR), identyfikację systemu (SysId) oraz kwestie bezpieczeństwa.
version: 1.0.0
phase: 9
lesson: 11
tags: [rl, sim2real, robotics, domain-randomization]

---

Na podstawie opisu platformy robotycznej, zadania oraz dostępności fizycznego sprzętu, wygeneruj:

1. **Identyfikację różnic między symulacją a rzeczywistością (reality gap):** potencjalne źródła rozbieżności uszeregowane według przewidywanego wpływu (np. dynamika kontaktu, opóźnienia siłowników, dokładność sensorów, percepcja wizualna).
2. **Parametry randomizacji dziedziny (Domain Randomization - DR):** szczegółową listę, zakresy zmienności oraz rozkłady prawdopodobieństwa. Uzasadnij każdy zakres na podstawie pomiarów ze świata rzeczywistego.
3. **Kroki identyfikacji systemu (System Identification - SysId):** wskazanie parametrów fizycznych do zmierzenia oraz metod ich pomiaru.
4. **Architekturę nauczyciel-uczeń (Teacher-Student):** określenie, z jakich uprzywilejowanych informacji (privileged information) korzysta model nauczyciela oraz jakie obserwacje (observations) są dostępne dla modelu ucznia.
5. **Margines bezpieczeństwa (safety envelope):** niskopoziomowe ograniczenia ruchu, wyłączniki awaryjne (e-stops) oraz kontrolery rezerwowe.

Odmów wdrożenia na fizycznym robocie w przypadku braku: (a) testów w symulacji w trybie zero-shot, (b) mechanizmów ochronnych (safety guardrails), (c) procedury awaryjnego wycofania (rollback plan). Oznacz każdy zakres randomizacji dziedziny (DR) szerszy niż 3-krotność zmierzonej zmienności w świecie rzeczywistym jako potencjalnie zbyt szeroki (over-randomized).
