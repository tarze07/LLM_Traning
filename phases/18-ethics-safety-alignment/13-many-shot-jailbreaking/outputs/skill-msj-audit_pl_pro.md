---
name: msj-audit
description: Przeprowadź audyt ewaluacji bezpieczeństwa w długim kontekście pod kątem podatności na jailbreakowanie wielokrotne (MSJ).
version: 1.0.0
phase: 18
lesson: 13
tags: [many-shot-jailbreaking, context-window, power-law, anthropic]
---

Na podstawie raportu z ewaluacji bezpieczeństwa modelu o długim kontekście zweryfikuj, czy testy obejmowały podatność na jailbreakowanie wielokrotne (MSJ).

Wyprodukuj:

1. Zakres liczby przykładów (shot counts). Podaj listę przetestowanych liczb przykładów (shots) – badanie powinno obejmować 1, 5, 16, 64, 256 oraz przynajmniej jedną wartość >= 512 dla modeli z kontekstem >= 1M. Ewaluacja oparta tylko na jednej liczbie przykładów nie jest miarodajna – MSJ opisuje krzywa, a nie pojedynczy punkt.
2. Dopasowanie do prawa potęgowego. Podaj wyznaczony wykładnik prawa potęgowego dla poszczególnych kategorii zachowań. Niski wykładnik oznacza, że model wykazuje odporność na ICL w danej kategorii; wysoki (stromy) wykładnik wskazuje na wybitną skuteczność MSJ.
3. Podział na kategorie. Skuteczność MSJ różni się w zależności od kategorii szkodliwości (np. przemoc, oszustwa, samookaleczenia, broń biologiczna). Zgodnie z pracą Anil i in. (2024), treści propagujące przemoc i oszustwa wymagają podania mniejszej liczby przykładów (shots) do przełamania zabezpieczeń. Wskaż kategorie, które pominięto w ewaluacji.
4. Identyfikacja metod obronnych. Czy wdrożono modyfikację promptów opartą na klasyfikatorach? Czy sam klasyfikator poddano testom odporności na ataki wrogie (adversarial robustness)? Raportowany przez Anthropic spadek skuteczności z 61% do 2% zależy ściśle od kalibracji klasyfikatora.
5. Weryfikacja ataków hybrydowych (compositional check). Czy ewaluacja sprawdza podatność na kombinacje ataków, np. MSJ + PAIR, MSJ + szablony perswazyjne lub MSJ + alternatywne kodowanie? Ataki hybrydowe (kompozycyjne) są zazwyczaj groźniejsze niż pojedyncze techniki.

Twarde odrzucenia:
- Wszelkie wnioski typu „nasz model z długim kontekstem jest bezpieczny” wyciągnięte na podstawie testów wyłącznie dla 5 przykładów (5-shot).
- Deklarowanie skuteczności metod obronnych bez jednoczesnego podania wskaźnika ASR ataku oraz wydajności ICL dla bezpiecznych zadań przy użyciu tego samego klasyfikatora – istotą problemu jest kompromis (trade-off) między bezpieczeństwem a funkcjonalnością.
- Podawanie skumulowanego wskaźnika ASR bez szczegółowego rozbicia na poszczególne kategorie szkodliwości.

Zasady odmowy:
- Jeśli użytkownik zapyta, czy podatność MSJ można całkowicie wyeliminować (załatwić łatką), odmów udzielenia jednoznacznej odpowiedzi tak/nie; MSJ dzieli ten sam mechanizm z pożytecznym ICL i nie da się go usunąć bez upośledzenia działania samego ICL.
- Jeśli użytkownik poprosi o rekomendację konkretnej liczby przykładów (shots) do przeprowadzenia ewaluacji, odmów podania pojedynczej wartości; wymagaj wyznaczenia dopasowania do prawa potęgowego w przedziale od 5 do 512 przykładów.

Wynik: Jednostronicowy raport z audytu przedstawiający zakres liczby przykładów, dopasowanie prawa potęgowego do poszczególnych kategorii, weryfikację metod obronnych oraz identyfikację luk na ataki hybrydowe. Należy jednokrotnie zacytować pracę Anil i in. (2024) (Anthropic) jako odniesienie metodologiczne.
