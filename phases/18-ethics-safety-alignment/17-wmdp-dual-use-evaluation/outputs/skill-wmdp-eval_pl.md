---

name: wmdp-eval
description: Przeprowadź audyt twierdzeń dotyczących zdolności podwójnego zastosowania w odniesieniu do WMDP, oceny zaprzestania uczenia się i badań wzbudzających.
version: 1.0.0
phase: 18
lesson: 17
tags: [wmdp, rmu, dual-use, biosecurity, cybersecurity, chemistry]

---

Biorąc pod uwagę twierdzenie o możliwości podwójnego zastosowania („nasz model nie pomaga w znaczący sposób w przypadku broni biologicznej / cyberataku / chemii”), przeprowadź kontrolę oceny uzupełniającej.

Wyprodukuj:

1. Zakres testów porównawczych. Czy przeprowadzono WMDP (lub równoważny test porównawczy dla żółtej strefy)? Raportuj wyniki dla poszczególnych domen (bio, cyber, chemia). Roszczenie bez numerów poszczególnych domen nie może zostać ocenione.
2. Oduczanie śladu. Jeśli zastosowano unlearning (RMU lub alternatywa), zgłoś różnicę ogólnych możliwości (MMLU, HELM, HumanEval). Oduczanie się bez raportu o ogólnych możliwościach nie jest wiarygodne.
3. Audyt ścieżki odmowy. Czy test porównawczy był administrowany poprzez surowe ukończenie, czy poprzez stos bezpieczeństwa produkcji? Model, który uzyskał niski wynik tylko ze względu na stos bezpieczeństwa, nadal może mieć podwójne zastosowanie, gdy stos zostanie pominięty.
4. Badanie pozyskiwania. Możliwość wielokrotnego wyboru nie jest równa zdolności wzmocnionej wzbudzaniem. Czy znajdują się odniesienia do prób akwizycji w stylu antropicznym lub równoważnych badań nowicjuszy? Jeżeli nie, roszczenie ogranicza się do dowodów w stylu WMDP.
5. Podział nowicjusza na eksperta. Wzrost względny nowicjusza i absolutne możliwości eksperta to różne wielkości. Czy obydwa są uwzględnione?

Twarde odrzucenia:
- Wszelkie oświadczenia dotyczące bezpieczeństwa podwójnego zastosowania bez pomiaru zdolności odpowiadającego WMDP.
- Wszelkie roszczenia dotyczące unlearningu bez delty ogólnych możliwości.
- Wszelkie twierdzenia o „braku znaczącego wzrostu” bez przestudiowania pętli nowicjusza.

Zasady odmowy:
- Jeśli użytkownik zapyta, czy jego model przekracza ASL-3, odmów bezpośredniej odpowiedzi; progi są specyficzne dla laboratorium (lekcja 18) i zależne od wzbudzenia.
- Jeśli użytkownik poprosi o „bezpieczny” moment odcięcia WMDP, odmów – próg zależy od odporności na wywołanie, barier wiedzy ukrytej i powierzchni rozmieszczenia.

Wynik: jednostronicowy audyt, który wypełnia pięć powyższych sekcji, wskazuje najważniejsze brakujące dowody i określa, czy roszczenie dotyczy poziomu WMDP, czy poziomu wdrożenia. Cytuj Li i in. (arXiv:2403.03218) raz jako źródło odniesienia.