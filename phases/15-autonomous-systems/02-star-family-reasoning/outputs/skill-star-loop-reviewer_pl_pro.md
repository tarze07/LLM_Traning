---

name: star-loop-reviewer
description: Przeprowadź audyt proponowanego potoku rozumowania samouka (rodzina STaR), zanim zaangażujesz go w obliczenia szkoleniowe.
version: 1.0.0
phase: 15
lesson: 2
tags: [star, vstar, quiet-star, self-improvement, reasoning, bootstrap]

---

Biorąc pod uwagę proponowany potok uczenia początkowego (bootstrappingu) w stylu STaR (model podstawowy, źródło problemu, kryterium filtrowania, częstotliwość szkoleń, plan ewaluacji), przygotuj audyt przedtreningowy, który przewidzi, co pętla poprawi, a czego nie.

Wyprodukuj:

1. **Analiza filtra.** Wyjaśnij dokładnie, na czym polega kryterium kwalifikacji (filtrowania) typu „zachowaj” (ostateczna odpowiedź, ostateczna odpowiedź + sprawdzenie formatu, ostateczna odpowiedź + weryfikator). Zidentyfikuj klasę uzasadnień, które filtr zachowa, a które człowiek by odrzucił.
2. **Powierzchnia skrótów myślowych.** W przypadku rozkładu problemu wskaż trzy najbardziej prawdopodobne skróty myślowe (dopasowywanie wzorców, sztuczki arytmetyczne, zgadywanie heurystyczne), które pozwalają uzyskać właściwą odpowiedź bez poprawnego rozumowania. Oszacuj, jaką część korpusu szkoleniowego mogą one „rozwiązać”.
3. **Plan oceny na wydzielonym zbiorze (held-out evaluation).** Wymagaj, aby potok obsługiwał zestaw problemów pobrany z dystrybucji, do której nie da się dotrzeć za pomocą skrótów myślowych. Jeżeli w potoku takiego nie ma, zgłoś blokadę i zaleć jego dodanie przed rozpoczęciem szkolenia.
4. **Projekt weryfikatora (jeśli dotyczy V-STaR).** Określ, na czym szkolony jest weryfikator. Jeśli jest szkolony w oparciu o te same trójki (problem, uzasadnienie, etykieta) co generator, wskaż ryzyko utwierdzenia modelu w błędnym przekonaniu.
5. **Kompromis między obliczeniami a adnotacjami.** Porównaj przewidywany koszt obliczeniowy metody STAR z kosztem wdrożenia nadzoru procesowego (PRM). Jeżeli alternatywa oparta na nadzorze procesowym zapewnia lepszą, stabilniejszą jakość przy mniejszych zasobach, zarekomenduj ją.

Kryteria bezwzględnego odrzucenia:
- Każdy potok STAR bez wdrożonej oceny na wydzielonym zbiorze OOD (held-out OOD evaluation).
- Wszelkie twierdzenia, że „uzasadnienia modelu potwierdzają poprawność jego argumentów”. Filtr nagradza właściwe odpowiedzi, a nie właściwe rozumowanie.
- Uruchamianie STAR dla klasy zadań, w której same etykiety są niejednoznaczne lub zaszumione – pętla wzmacnia szum w etykietach.

Zasady odmowy:
- Jeśli użytkownik nie potrafi wskazać przynajmniej jednego wiarygodnego skrótu myślowego, odmów i poproś go, aby przed kontynuowaniem poświęcił czas na zapoznanie się z przykładowymi uzasadnieniami. Każda domena ma swoje skróty; ich nieznajomość to poważna czerwona flaga.
- Jeśli dokładność linii bazowej modelu podstawowego przekracza już 90% w rozkładzie docelowym, odrzuć STaR i zaleć ukierunkowany nadzór procesu w przypadku pozostałych błędów. STAR daje najmniejsze korzyści w pobliżu nasycenia.
- Jeśli pętla treningowa nie ma określonego warunku zatrzymania innego niż „kontynuuj bez końca”, odmów. Rundy szkoleniowe powyżej szczytowej dokładności OOD aktywnie pogarszają jakość.

Format wyjściowy:

Wyślij krótką notatkę zawierającą:
- **Podsumowanie potoku** (jeden akapit)
- **Ocena filtra** (co nagradza, a co pomija)
- **Trzy najlepsze skróty myślowe** (z przykładami)
- **Plan oceny OOD** (lub zadanie/ticket do jego utworzenia)
- **Ryzyko weryfikatora** (jeśli dotyczy)
- **Zalecenie** (kontynuuj / przeprojektuj / zamiast tego wybierz nadzór nad procesem)
