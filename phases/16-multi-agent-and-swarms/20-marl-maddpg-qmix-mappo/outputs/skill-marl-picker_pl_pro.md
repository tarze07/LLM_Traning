---

name: marl-picker
description: Wybierz odpowiedni algorytm MARL (np. MADDPG, QMIX, MAPPO, IQL lub ich rozszerzenia) do specyfiki danego zadania wieloagentowego. Uwzględnia charakterystykę kooperacji/rywalizacji, typ przestrzeni akcji, heterogeniczność populacji, strukturę nagród oraz skalowalność.
version: 1.0.0
phase: 16
lesson: 20
tags: [multi-agent, MARL, MADDPG, QMIX, MAPPO, CTDE]

---

Na podstawie opisu zadania wieloagentowego wybierz najbardziej adekwatny algorytm MARL.

Opracuj następujące elementy:

1. **Klasyfikacja zadania (task taxonomy).** Określenie charakteru: pełna kooperacja (wspólna nagroda), pełna rywalizacja (gra o sumie zerowej), scenariusz mieszany lub o sumie niezerowej (ogólnej). Liczba agentów w systemie. Homogeniczność vs heterogeniczność populacji.
2. **Obserwowalność środowiska.** Pełna (każdy agent ma wgląd w stan globalny), częściowa (agent ma dostęp tylko do lokalnych obserwacji) lub z możliwością wymiany informacji (komunikacja).
3. **Przestrzeń akcji (action space).** Dyskretna (np. w stylu gier Atari czy środowiska SMAC) lub ciągła (np. Particle World, symulacje fizyczne MuJoCo). Typ przestrzeni decyduje o doborze algorytmu.
4. **Struktura nagród.** Gęsta (dense – nagrody cząstkowe przyznawane w każdym kroku) vs rzadka (sparse – nagroda przyznawana wyłącznie na końcu epizodu). Gęsta struktura nagród sprzyja zastosowaniu MAPPO; rzadka wymaga metod efektywnego przypisywania zasług (credit assignment), takich jak dekompozycja wartości w QMIX.
5. **Rekomendacja algorytmu.** Domyślnie rekomenduje się rozpoczęcie od wdrożenia MAPPO jako modelu referencyjnego (zgodnie z wnioskami Yu i in., 2022). Zmień wybór na:
   - QMIX: w zadaniach w pełni kooperacyjnych z populacją homogenicznych agentów, przy rzadkich nagrodach wymagających zaawansowanego przypisywania zasług (credit assignment).
   - MADDPG: w środowiskach o charakterze mieszanym (kooperacja i rywalizacja) z ciągłą przestrzenią akcji.
   - Nowsze rozszerzenia (np. QTRAN, QPLEX, FACMAC): w sytuacjach, gdy narzucony przez QMIX warunek monotoniczności okazuje się zbyt ograniczający.
6. **Zaplecze szkoleniowe.** Ocena gotowości infrastrukturalnej: dostępność danych interakcyjnych, budżet obliczeniowy, kompetencje w obszarze projektowania nagród (reward shaping) oraz budżet na weryfikację stabilności wyników (5-10 różnych eksperymentów z różnymi ziarnami losowości/seeds). Jeśli zaplecze jest niewystarczające, rekomenduj stosowanie strategii na poziomie promptów dla agentów LLM.
7. **Architektura uruchomieniowa (runtime contract).** Zasada CTDE: upewnij się, że w trybie wdrożeniowym każdy agent ma dostęp wyłącznie do swoich lokalnych obserwacji. Zapisz te wymagania w specyfikacji, aby były ściśle przestrzegane w kodzie produkcyjnym.

Kryteria twardego odrzucenia projektu:

- Wybór modelu bazowego innego niż MAPPO na start. MAPPO stanowi oficjalny standard referencyjny w 2026 roku.
- Stosowanie QMIX w zadaniach o charakterze mieszanym (kooperacja i rywalizacja). Dekompozycja wartości w tym algorytmie opiera się na założeniu monotoniczności.
- Rekomendowanie szkolenia MARL dla agentów LLM w sytuacjach braku wystarczających danych interakcyjnych lub stabilnego sygnału nagrody. W takich warunkach znacznie lepiej sprawdzą się strategie na poziomie promptów.
- Prowadzenie treningu bez logowania obserwacji i akcji poszczególnych agentów. Uniemożliwia to debugowanie systemu.

Zasady odmowy (rekomendacje alternatywne):

- Jeśli zbiór danych interakcyjnych obejmuje mniej niż ~1000 epizodów, rekomenduj oparcie systemu na promptach lub uczeniu nadzorowanym (fine-tuning).
- Jeśli środowisko nie spełnia założeń procesu Markowa (wymaga pamięci historycznej), a rekomendacja nie uwzględnia zastosowania krytyków rekurencyjnych (recurrent critics), wskaż tę lukę w projekcie.
- Jeśli zadanie charakteryzuje się rywalizacją o sumie niezerowej (występowanie wielu punktów równowagi), same algorytmy MARL nie wskażą rozwiązania; zalecaj wdrożenie teorii projektowania mechanizmów (mechanism design) lub zdefiniowanie kryterium wyboru równowagi.

Format wyjściowy: jednostronicowy brief projektowy. Rozpocznij od jednozdaniowej rekomendacji (np. „Model bazowy MAPPO ze scentralizowaną funkcją wartości; dyskretny aktor dla każdego agenta; wdrożenie w architekturze CTDE; 5 eksperymentów z różnymi ziarnami losowości”), po czym przedstaw omówienie siedmiu powyższych punktów. Całość zakończ opisem kolejnych kroków wdrożeniowych: zbieranie danych, szkolenie, ocena jakości, wdrożenie produkcyjne.
