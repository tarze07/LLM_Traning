---
name: attack-audit
description: Przeprowadź audyt raportu z ewaluacji red-teamingowej pod kątem pokrycia metodami ataków, budżetu zapytań, sędziego i zestawu zachowań.
version: 1.0.0
phase: 18
lesson: 12
tags: [red-teaming, jailbreak, pair, harmbench, jailbreakbench, asr]
---

Na podstawie raportu z ewaluacji zespołu czerwonego (red-teaming) zweryfikuj, czy uzyskane wyniki są porównywalne z opublikowanymi liniami bazowymi i czy uzasadniają sformułowane wnioski.

Wyprodukuj:

1. Pokrycie metodami ataków. Wypisz każdy przetestowany atak: PAIR, GCG, AutoDAN, TAP, PAP, testy manualne. Wskaż brakujące klasy ataków. Raport oparty wyłącznie na jednej rodzinie ataków nie daje podstaw do wnioskowania o odporności modelu.
2. Budżet zapytań na atak. Podaj limit zapytań przypadający na jeden prompt dla każdego ataku. Deklaracje o skuteczności PAIR przy 20 zapytaniach nie są bezpośrednio porównywalne z wynikami GCG uzyskanymi przy 500 krokach optymalizacji.
3. Sędzia oceniający. Jaki model pełnił rolę sędziego (np. GPT-4-turbo, Llama Guard, StrongREJECT, wewnętrzny klasyfikator)? Kalibracja sędziego ma decydujący wpływ na wahania wskaźnika ASR.
4. Zbiór testowanych zachowań. JailbreakBench (100 zachowań w 10 kategoriach), HarmBench (510 zachowań w 7 kategoriach), wewnętrzny zbiór danych czy inny standard? Określ, czy wykorzystany zbiór jest publicznie dostępny i pozwala na replikację wyników.
5. Podatność na transfer (transfer check). Jeśli wrogie prompty optymalizowano pod kątem jednego konkretnego modelu, czy sprawdzono wskaźnik ASR po ich przeniesieniu (transferze) na inne modele? Skuteczność ataku zmierzona na jednym modelu stanowi jedynie oszacowanie górnej granicy odporności rodziny modeli, a nie jej gwarantowane minimum.

Twarde odrzucenia:
- Wszelkie deklaracje typu „nasz model jest bezpieczny/odporny” formułowane na podstawie testów tylko jedną rodziną ataków.
- Podawanie wskaźników ASR bez określenia budżetu zapytań.
- Wyliczanie ASR z użyciem sędziego niezgodnego ze standardowymi benchmarkami, bez uprzedniej kalibracji względem sędziego referencyjnego.

Zasady odmowy:
- Jeśli użytkownik zapyta: „Czy nasz model jest odporny na próby złamania zabezpieczeń (jailbreak)?”, odmów udzielenia jednoznacznej odpowiedzi tak/nie i wskaż na konieczność analizy wielu metod ataków, wielu sędziów oraz weryfikacji podatności na transfer.
- Jeśli użytkownik poprosi o rekomendację konkretnego zestawu narzędzi do przeprowadzania ataków, odmów wskazania pojedynczego rozwiązania i odwołaj się do zróżnicowania wyników wykazanego w benchmarku HarmBench w 2024 roku.

Wynik: Jednostronicowy raport z audytu, który pokrywa pięć powyższych obszarów, wskazuje pominięte klasy ataków oraz określa, czy raportowany wskaźnik ASR jest niedoszacowany, czy też przeszacowany w porównaniu z wynikami z referencyjnych benchmarków. Należy jednokrotnie zacytować pracę Chao i in. (arXiv:2310.08419) oraz odpowiednią publikację powiązaną z użytym benchmarkiem.
