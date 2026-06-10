---

name: fairness-criterion
description: Zidentyfikuj, na jakie kryterium uczciwości powołuje się roszczenie, i przeprowadź kontrolę powiązanych założeń.
version: 1.0.0
phase: 18
lesson: 21
tags: [fairness, demographic-parity, equalized-odds, counterfactual-fairness, impossibility]

---

Biorąc pod uwagę twierdzenie lub zasadę uczciwości, określ, na które kryterium się powołuje, na jakich założeniach opiera się to twierdzenie i co twierdzenia o niemożliwości implikują dla pozostałych kryteriów.

Wyprodukuj:

1. Identyfikacja kryterium. Oznacz roszczenie jako ukierunkowane na jeden z następujących czynników: parytet demograficzny, wyrównane szanse, równość dokładności użycia warunkowego, uczciwość indywidualna, uczciwość kontrfaktyczna. Przed kontynuowaniem należy wyjaśnić niejasne roszczenia.
2. Audyt stawki podstawowej. Jakie są stawki podstawowe dla poszczególnych grup we wdrożeniu? W przypadku nierównych stawek bazowych obowiązuje Chouldechova / KMR 2017 niemożliwość: żaden model nie spełnia wszystkich trzech kryteriów grupowych.
3. Zależność przyczynowo-DAG. Jeśli roszczenie dotyczy uczciwości kontrfaktycznej, jaki jest przyczynowy DAG? Sprawiedliwość alternatywna jest uzasadniona tylko w takim stopniu, jak DAG. Brak DAG powoduje nieważność reklamacji.
4. Metryka podobieństwa. Jeśli twierdzenie dotyczy indywidualnej rzetelności, jaka jest metryka podobieństwa d? Wybór zależy od konkretnego zadania i jest decyzją polityczną, a nie statystyczną.
5. Legalność interwencji. Jeżeli w twierdzeniu zastosowano rozumowanie alternatywne, czy w grę wchodzą interwencje dotyczące chronionych atrybutów? Jeśli tak, rozważ wycofanie się ze scenariuszy alternatywnych (arXiv:2401.13935), aby ominąć kwestie prawne.

Twarde odrzucenia:
- Wszelkie „uzasadnione” roszczenia bez określenia kryteriów.
- Wszelkie roszczenia dotyczące „spełnienia wszystkich kryteriów uczciwości” w ramach nierównych stawek podstawowych bez uznania Chouldechova / KMR 2017.
- Wszelkie roszczenia dotyczące uczciwości alternatywnej bez opublikowanego DAG przyczynowego.

Zasady odmowy:
- Jeśli użytkownik zapyta, które kryterium uczciwości jest „właściwe”, odrzuć ranking i wyjaśnij, że jest to wybór polityczny.
- Jeśli użytkownik zapyta, czy model jest „sprawiedliwy”, odrzuć twierdzenie binarne; sprawiedliwość ma charakter względny.

Wynik: jednostronicowy audyt, który wypełnia pięć powyższych sekcji, zaznacza niemożność, jeśli ma to zastosowanie, i podaje wybór polityki zawarty w roszczeniu. Cytuj Dworka i in. 2012, Kusner i in. 2017, Chouldechova 2017 po jednym razie w stosownych przypadkach.