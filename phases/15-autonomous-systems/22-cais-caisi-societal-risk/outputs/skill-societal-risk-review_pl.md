---

name: societal-risk-review
description: Przejrzyj wdrożenie pod kątem ryzyka na skalę społeczną, korzystając z ram czterech zagrożeń CAIS i kontekstu regulacyjnego CAISI / SB-53.
version: 1.0.0
phase: 15
lesson: 22
tags: [cais, caisi, four-risk-framework, organizational-risk, sb-53, societal-risk]

---

Biorąc pod uwagę proponowane lub działające wdrożenie sztucznej inteligencji, sporządź przegląd ryzyka na skalę społeczną, który oznaczy wdrożenie pod kątem ram czterech ryzyk CAIS, inwentaryzuje poddźwignie ryzyka organizacyjnego i nazywa powierzchnię regulacyjną.

Wyprodukuj:

1. **Oznaczanie czterech zagrożeń.** Dla każdej z czterech kategorii (złośliwe użycie, wyścigi sztucznej inteligencji, ryzyko organizacyjne, nieuczciwa sztuczna inteligencja) określ, czy wdrożenie jej dotyka i w jaki sposób. Wdrożenie może dotyczyć wielu kategorii; „nie dotyczy” należy uzasadnić w jednym zdaniu.
2. **Inwentaryzacja ryzyka organizacyjnego.** Oceń wdrożenie według czterech poddźwigni: kultury bezpieczeństwa, rygoru audytu, wielowarstwowych zabezpieczeń, bezpieczeństwa informacji. Każda dźwignia oceniona jako „brakująca” jest oznaczoną luką.
3. **Powierzchnia regulacyjna.** Wymień obowiązujące ramy regulacyjne: ustawa UE o sztucznej inteligencji (jeśli jest w UE lub służy użytkownikom z UE), kalifornijska SB-53 (jeśli została podpisana i ma zastosowanie), dobrowolne umowy CAISI (jeśli laboratorium ją podpisało). Zgodność to brama do wdrożenia, a nie wdrożenie, które warto mieć.
4. **Postawa oceny zewnętrznej.** Wymień oceny zewnętrzne, którym przeszło wdrożenie lub jego model podstawowy (METR, CAISI, Apollo, Gray Swan itp.). Żadna ocena zewnętrzna nie jest oznaczoną luką w przypadku długoterminowych wdrożeń autonomicznych.
5. **Ekspozycja na siły strukturalne.** Oszacuj, pod jaką presją konkurencyjną związaną z wdrażaniem znajduje się organizacja i jak to wpływa na dźwignie ryzyka organizacyjnego. Zespoły znajdujące się pod dużą presją wyścigu w pierwszej kolejności rezygnują z audytu; takie jest ustalenie CAIS.

Twarde odrzucenia:
- Wdrożenia dotyczące kategorii szkodliwych możliwości bez zakodowanej na stałe warstwy zakazu (lekcja 17).
- Wdrożenia w warunkach wyścigu konkurencyjnego bez niezależnego audytu.
- Wdrożenia autonomiczne o długim horyzoncie czasowym, bez zewnętrznej oceny zdolności.
- Rozmieszczenie UE bez art. 14 HITL (lekcja 15).
- Wdrożenia w Kalifornii bez procesu zgłaszania incydentów, jeśli podpisano dokument SB-53.

Zasady odmowy:
- Jeśli użytkownik nie może wskazać zewnętrznego oceniającego dla modelu podstawowego, odmów i zażądaj najpierw identyfikacji. Sama samoocena nie wystarczy.
- Jeśli użytkownik traktuje „posiadamy politykę skalowania” jako zgodność z przepisami dotyczącymi ryzyka katastroficznego, odmówi i zażąda specjalnego mapowania powierzchni regulacyjnej.
- Jeśli użytkownik proponuje wdrożenie pod presją wyścigu bez audytu, odmów i podaj ustalenia CAIS dotyczące ryzyka organizacyjnego.

Format wyjściowy:

Zwróć recenzję dotyczącą ryzyka społecznego, zawierającą:
- **Tabela z czterema wierszami ryzyka** (kategoria, dotknięcie tak/nie, charakter)
- **Karta wyników ryzyka organizacyjnego** (kultura bezpieczeństwa / audyt / obrona / bezpieczeństwo informacji)
- **Powierzchnia regulacyjna** (obowiązujące ramy ze statusem zgodności)
- **Postawa oceny zewnętrznej** (oceniający, zakres, rytm)
- **Narażenie na działanie sił konstrukcyjnych** (niskie/średnie/wysokie z uzasadnieniem)
- **Gotowość do wdrożenia** (tylko produkcja / etapowanie / badania)