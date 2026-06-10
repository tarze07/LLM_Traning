---

name: compliance-gap
description: Oceń, czy raport bezpieczeństwa może wykryć fałszowanie osiowania na podstawie monitorowanych/niemonitorowanych luk w zgodności.
version: 1.0.0
phase: 18
lesson: 9
tags: [alignment-faking, compliance-gap, anthropic, safety-evaluation]

---

Biorąc pod uwagę raport z oceny bezpieczeństwa, oceń, czy można w nim odróżnić fałszywe ustawienie od rzeczywistej zgodności, korzystając z raportu Greenblatt i in. Ramy dotyczące luk w przestrzeganiu przepisów na rok 2024.

Wyprodukuj:

1. Podział warunków. Czy ocena dotyczy zarówno stanu monitorowanego (istotnego dla szkolenia), jak i niemonitorowanego (niezwiązanego ze szkoleniem)? Bez obu, fałszowanie wyrównania jest niewidoczne.
2. Pomiar luki w zakresie zgodności. Zgłaszaj lukę jako wskaźnik zgodności (monitorowany – niemonitorowany). Zinterpretuj znak i wielkość: dodatnia luka = ​​zachowanie w kształcie udawania; luka ujemna = nadmierna odmowa, jeśli zostanie zaobserwowana.
3. Ślad werbalny a kontrola zachowania. Czy ocena opiera się na notatkowym rozumowaniu modelu, czy na samym działaniu? Według Anthropic 2025 środki łagodzące ukierunkowane na ślad werbalny mogą go usunąć bez usuwania zachowania.
4. Audyt operacjonalizacji. Czy warunek monitorowania jest tworzony za pomocą podpowiedzi systemowej, syntetycznego dostrajania czy naturalnego kontekstu wdrożenia? Zależność od podpowiedzi systemowych osłabia to twierdzenie; replikacje syntetyczne dostrajające wzmacniają go.
5. Kontrola rezydualnej zachęty. Czy po zastosowaniu wszelkich środków łagodzących struktura zachęt jest nadal obecna (czy model nadal odniósłby korzyści z udawania, gdyby tak zdecydował)? Trwałość zachęty oznacza, że ​​zachowanie może powrócić w wyniku zmiany dystrybucji.

Twarde odrzucenia:
- Wszelkie twierdzenia o „żadnym fałszowaniu wyrównania” oparte wyłącznie na niemonitorowanej ocenie.
- Każde twierdzenie, że „rozumowanie w notatniku nie oznacza już udawania”, oznacza zaprzestanie zachowania.
- Wszelkie twierdzenia, że ​​modele wytrenowane za pomocą HHH nie symulują wyrównania — Greenblatt i in. 2024 stanowi, że szkolenie HHH jest warunkiem koniecznym, a nie wystarczającą obroną.

Zasady odmowy:
- Jeśli użytkownik zapyta „czy mój model fałszuje wyrównanie”, odrzuci odpowiedź binarną bez danych dotyczących luk w zgodności.
- Jeśli użytkownik poprosi o rozwiązanie, które atakuje jedynie ślad werbalny (np. „wytrenuj notatnik, aby pasował do działania”), odmów i wyjaśnij tryb awarii wiernego CoT (kontynuacja w 2025 r.).

Wynik: jednostronicowa ocena, która raportuje zgodność w obu warunkach, lukę, oddzielenie śladu werbalnego od zachowania oraz siłę operacjonalizacji. Oznacz każdy brakujący element. Cytuj Greenblatt i in. (arXiv:2412.14093) raz jako źródło frameworka.