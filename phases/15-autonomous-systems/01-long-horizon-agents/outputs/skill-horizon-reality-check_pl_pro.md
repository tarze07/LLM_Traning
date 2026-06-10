---

name: horizon-reality-check
description: Ocena, czy planowane zadanie dla agenta mieści się w horyzoncie możliwości wybranego modelu z bezpiecznym marginesem.
version: 1.0.0
phase: 15
lesson: 1
tags: [autonomous-agents, metr, time-horizon, reliability, deployment]

---

Na podstawie opisu planowanego zadania autonomicznego (zakres prac, szacowany czas wykonania przez człowieka, konsekwencje/koszt błędu), przeprowadź analizę weryfikacyjną (reality check), czy horyzont możliwości współczesnych modeli pozwala na jego bezpieczną realizację.

Wymagane rezultaty:

1. **Szacowany czas eksperta.** Zapytaj użytkownika o średni czas potrzebny specjaliście na wykonanie tego zadania (w minutach lub godzinach). Jeśli użytkownik nie jest w stanie go określić, odmów wykonania analizy i zalecaj najpierw zmierzenie czasu na małej próbce zadań.
2. **Wskaźnik zapasu bezpieczeństwa (headroom).** Podziel 50-procentowy horyzont czasowy METR wybranego modelu przez szacowany czas pracy eksperta. Oznacz flagą ostrzegawczą każdy wynik poniżej 4x — przy 50-procentowym prawdopodobieństwie sukcesu wymagany jest duży margines bezpieczeństwa. Przy współczynniku 2x lub niższym odmów wdrożenia produkcyjnego, chyba że proces zakłada ciągły nadzór człowieka (HITL) nad każdą kluczową operacją.
3. **Budżet niezawodności.** Oszacuj długość trajektorii (liczbę wywołań narzędzi), a następnie oblicz prawdopodobieństwo sukcesu całego procesu (end-to-end) przy niezawodności pojedynczego kroku wynoszącej odpowiednio: 0,95, 0,99 oraz 0,995. Jeśli długość zadania przekracza próg 50% szans na sukces przy danej niezawodności kroku, nakaż wdrożenie punktów kontrolnych lub podział zadania na mniejsze etapy.
4. **Korekta testy vs produkcja.** Uwzględnij 20–40% różnicy (spadku wydajności) między horyzontem w środowisku testowym a produkcyjnym. W uzasadnieniu dla interesariuszy powołuj się na badanie Anthropic z 2024 roku nad symulowaniem zgodności (alignment faking) lub Międzynarodowy raport o bezpieczeństwie AI z 2026 roku.
5. **Wymagane mechanizmy kontrolne.** Na podstawie wyliczonego wskaźnika zapasu określ minimalne zabezpieczenia: limity budżetowe, limit iteracji, wyłącznik bezpieczeństwa (kill switch), punkty zatwierdzania przez człowieka (HITL), tokeny kanaryjskie oraz harmonogram audytów trajektorii.

Kryteria odrzucenia (Twarde reguły):

- Wdrażanie procesów przy wskaźniku zapasu horyzontu poniżej 2x, jeśli nie zapewniono nadzoru człowieka (HITL) nad każdą kluczową operacją.
- Twierdzenie, że model „na pewno wykona” zadanie wyłącznie na podstawie horyzontu czasowego METR. Horyzont to jedynie punkt 50% na krzywej sukcesu — błędy w skrajnych przypadkach są nieuniknione.
- Traktowanie wskaźników METR jako gwarantowanego minimum (linii odniesienia), a nie maksymalnego sufitu możliwości.

Kryteria odmowy wykonania:

- Jeśli użytkownik nie potrafi oszacować czasu potrzebnego specjaliście na wykonanie zadania, odmów analizy i poproś o wcześniejsze zebranie danych testowych. Inne działanie to tylko spekulacje.
- Jeśli szacowany koszt zadania przy pełnym obciążeniu przekracza maksymalny dopuszczalny budżet użytkownika, odmów analizy i zalecaj wdrożenie mechanizmów kontroli kosztów opisanych w Lekcji 13.
- Jeśli zadanie obejmuje operacje nieodwracalne (np. transakcje finansowe, zapisy w produkcyjnej bazie danych, wysyłkę e-maili do klientów) i nie przewidziano warstwy zatwierdzania przez człowieka (HITL), odmów wykonania analizy. Sam wysoki wskaźnik horyzontu nie usprawiedliwia braku zabezpieczeń przy operacjach krytycznych.

Format raportu:

Przygotuj zwięzły dokument zawierający:
- **Podsumowanie zadania** (jedno zdanie)
- **Szacowany czas eksperta** (z jednostkami)
- **Wskaźnik zapasu bezpieczeństwa** (konkretna wartość liczbowa)
- **Szacunkowa ogólna niezawodność** (tabela dla trzech poziomów niezawodności kroku)
- **Minimalne zabezpieczenia** (lista punktowana)
- **Decyzja (Go / Hold / No-Go)** (jednoznaczny werdykt wraz z jednozdaniowym uzasadnieniem)
