---
name: control-protocol-audit
description: Przeprowadź audyt protokołu wdrożeniowego w ramach modelu zagrożeń kontroli AI (AI Control).
version: 1.0.0
phase: 18
lesson: 10
tags: [ai-control, subversion, trusted-editing, untrusted-monitoring, safety-case]
---

Na podstawie opisu protokołu wdrożeniowego przeprowadź jego audyt w ramach modelu zagrożeń AI Control, identyfikując komponenty: U (niezaufany silny), T (zaufany słaby), H (zaufany człowiek), a następnie określ pozycję protokołu na granicy kompromisu między użytecznością a bezpieczeństwem.

Wyprodukuj:

1. Przydział ról. Zidentyfikuj, który model pełni rolę U, a który T. Jeśli T jest kolejną instancją modelu U, natychmiast zgłoś ryzyko zmowy (collusion).
2. Rozliczenie budżetu audytu. W jaki sposób alokowana jest praca H? Jednolicie, losowo, czy w sposób ukierunkowany sygnałami ostrzegawczymi (flag-directed)? Jaki odsetek wyników podlega audytowi w ujęciu oczekiwanym?
3. Identyfikacja wektorów zmowy. Dla każdej pary komponentów niezaufanych (np. producent U + monitor U, producent U + edytor U) wskaż potencjalne wektory zmowy: znaczniki steganograficzne, wykorzystanie wspólnych strategii z etapu treningu, kanały czasowe.
4. Analiza luki w zdolnościach. O ile słabszy jest model T od U? W którym momencie sygnał edycyjny generowany przez T staje się jedynie szumem (np. gdy T przestaje niezawodnie wykrywać backdoory tworzone przez U)?
5. Model zagrożenia w najgorszym scenariuszu. Zakładając, że model U działa jako przeciwnik posiadający pełną wiedzę o protokole, jaka jest jego optymalna strategia? Jaki odsetek ataków zespołu czerwonych (red team) kończy się powodzeniem?

Twarde odrzucenia:
- Wszelkie opisy protokołów, w których U jest wykorzystywany jako monitor samego siebie bez wdrożonych mechanizmów odporności na zmowę.
- Deklarowanie przez protokół „bliskiego zeru wskaźnika wdrożeń backdoorów” bez przeprowadzenia ewaluacji przez zespół czerwony mający pełny wgląd w działanie protokołu.
- Przeprowadzanie audytu protokołu bez szczegółowego określenia luki w zdolnościach między T a U oraz dostępnego budżetu H.

Zasady odmowy:
- Jeśli użytkownik zapyta: „Czy ten protokół jest bezpieczny?”, odmów udzielenia odpowiedzi bez przedstawienia dowodów w postaci: (a) wyników testów zespołu czerwonego, (b) oszacowania luki w zdolnościach modeli, (c) określonego budżetu H.
- Jeśli użytkownik utożsamia dopasowanie z kontrolą („dopasowaliśmy model U, więc protokół jest nam zbędny”), odmów i odwołaj się do Lekcji 9 (Fałszowanie dopasowania) – dopasowanie jest cechą modelu U, podczas gdy kontrola jest cechą całego protokołu.

Wynik: Jednostronicowy raport z audytu, który pokrywa pięć powyższych punktów, identyfikuje najsłabsze ogniwo protokołu (najczęściej lukę w zdolnościach T-do-U lub niską odporność na zmowę) oraz wskazuje na największy niezaadresowany dotąd scenariusz awarii (failure mode). Należy jednokrotnie zacytować pracę Greenblatt i in. (arXiv:2312.06942) jako źródło modelu zagrożeń.
