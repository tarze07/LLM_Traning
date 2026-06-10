---
name: encoding-audit
description: Przeprowadź audyt raportu z zabezpieczeń przed jailbreakiem pod kątem odporności na ataki oparte na kodowaniu danych.
version: 1.0.0
phase: 18
lesson: 14
tags: [artprompt, ascii-art, encoding-attack, utes, structural-sleight]
---

Na podstawie raportu z zabezpieczeń przed jailbreakiem zidentyfikuj przeanalizowane rodziny ataków opartych na kodowaniu oraz określ, które warstwy obronne chronią przed każdym z nich.

Wyprodukuj:

1. Zakres przetestowanych kodowań. Wymień każdą zbadaną rodzinę ataków: grafika ASCII (ArtPrompt), Base64, leet-speak, homoglify UTF-8, zagnieżdżone struktury JSON/YAML/CSV, grafy/drzewa UTES oraz ataki w modalności obrazu. Wskaż pominięte rodziny.
2. Przypisanie warstw obronnych. Dla każdej rodziny ataków określ, która warstwa zabezpieczeń (np. filtr słów kluczowych, filtr perpleksji, parafrazowanie, retokenizacja, klasyfikator danych wyjściowych, moderator multimodalny) skutecznie ją blokuje, a która jest bezużyteczna.
3. Podatność na poziomie rozpoznawania wizualnego. Zgodnie z pracą Jiang i in. (2024), filtry perpleksji (PPL) oraz retokenizacja zawodzą w starciu z ArtPrompt, jako że rozpoznawanie glifów zachodzi na poziomie percepcji wizualnej. Czy wdrożone zabezpieczenia obejmują mechanizmy działające na poziomie wizualnym bądź strukturalnym?
4. Test uogólniania (generalizacji). Metoda UTES (StructuralSleight) uogólnia ataki na dowolne rzadkie struktury danych. Czy w raporcie przetestowano odporność na struktury, które nie były obecne w zbiorze treningowym filtrów ochronnych?
5. Kompromis między zdolnościami a bezpieczeństwem. Model o wyższych zdolnościach interpretacji tekstu wizualnego (wysoki wynik w benchmarku ViTC) jest bardziej podatny na ataki ArtPrompt. Podaj wynik ViTC modelu, jeśli został uwzględniony w raporcie; w przeciwnym razie zażądaj jego wyznaczenia.

Twarde odrzucenia:
- Wyciąganie wniosków o skuteczności obrony wyłącznie na podstawie filtrowaniu podciągów tekstowych bądź słów kluczowych.
- Formułowanie ogólnych wniosków o odporności na „ataki oparte na kodowaniu” na podstawie przetestowania tylko jednej rodziny kodowania.
- Deklarowanie odporności bez podania wskaźnika skuteczności ataków (ASR) dla każdej zbadanej rodziny osobno.

Zasady odmowy:
- Jeśli użytkownik zapyta, czy podatność na ArtPrompt została „załatana”, odmów udzielenia odpowiedzi i wyjaśnij lukę między zabezpieczeniami działającymi na poziomie percepcji wizualnej a analizą tekstu.
- Jeśli użytkownik poprosi o rekomendację jednej, uniwersalnej obrony przed wszelkimi atakami opartymi na kodowaniu, odmów wskazania pojedynczego rozwiązania – zabezpieczenia muszą być zorganizowane warstwowo, pokrywając wszystkie rodziny ataków, z którymi może zetknąć się wdrożony system.

Wynik: Jednostronicowy raport z audytu, który pokrywa pięć powyższych punktów, identyfikuje kluczową podatność w obszarze kodowania oraz wskazuje najpilniejszą warstwę zabezpieczeń, jaką należy wdrożyć. Należy jednokrotnie zacytować pracę Jiang i in. (arXiv:2402.11753) oraz publikację StructuralSleight w tekście.
