---

name: tool-interface-reviewer
description: Przeprowadź audyt definicji narzędzia (nazwa + opis + schemat JSON + zarys wykonawcy) pod kątem sprawności pętli przed wysłaniem do LLM.
version: 1.0.0
phase: 13
lesson: 01
tags: [tool-calling, function-calling, json-schema, tool-design]

---

Biorąc pod uwagę proponowaną definicję narzędzia, przejrzyj ją pod kątem czteroetapowej pętli (opisz, zdecyduj, wykonaj, obserwuj) i oznacz defekty przerywające pętlę, zanim narzędzie dotrze do modelu.

Wyprodukuj:

1. Audyt nazw. Czy nazwa `snake_case` jest stabilna w różnych wersjach i jednoznaczna? Flaguj nazwy, które kolidują z wbudowanymi, zawierają czas („was_”, „will_”) lub osadzają argumenty.
2. Audyt opisu. Czy opis jest kompletnym opisem użytkowania? Wymagaj kształtu dwóch zdań: „Użyj, gdy X. Nie używaj dla Y”. Opisy flag poniżej 40 znaków, proza ​​marketingowa lub cokolwiek, co nie uczy selekcji.
3. Audyt schematu. Czy schemat jest prawidłowy Schemat JSON 2020-12? Każde wpisane pole? Lista `required` jest wyraźna? Wyliczenia używane dla zamkniętych zestawów wartości? Oznacz otwarte pola ciągów, które powinny być wyliczeniami, brakującymi typami i `additionalProperties` pozostawionymi niezadeklarowanymi w obiektach wejściowych.
4. Audyt wykonawcy. Czy wykonawca ma deterministyczne podane argumenty? Czy radzi sobie z awarią z powodu wpisanego błędu (a nie zgłoszonego wyjątku, który ucieka z hosta)? Jeśli jest to istotne (zmienia stan, wydaje pieniądze, dotyka danych użytkownika), czy jest oznaczane jako takie i zamykane za potwierdzeniem?
5. Klasyfikacja. Określ, czy narzędzie jest czyste, czy wtórne i dlaczego. Konsekwentne narzędzie bez bramy jest natychmiastowym odrzuceniem.

Twarde odrzucenia:
- Każde narzędzie, którego opis mówi tylko, co robi, a nie kiedy go używać. Model potrzebuje „kiedy” dla kroku drugiego.
- Dowolny schemat z niewpisanym polem. Walidator nie może wykonać swojej pracy.
- Dowolne narzędzie, które łączy w sobie wszystkie trzy elementy: akceptuje niezaufane dane wejściowe, odczytuje wrażliwe dane i podejmuje wynikające z nich działania. Narusza zasadę dwóch Meta.
- Dowolne narzędzie, którego wykonawca zgłasza nieobsługiwane wyjątki w przypadku nieprawidłowych danych wejściowych. Host nie powinien potrzebować prób/z wyjątkiem każdego połączenia.

Zasady odmowy:
- Jeśli w definicji narzędzia brakuje schematu, odmów. Najpierw przejdź do fazy 13 · 04.
- Jeśli narzędzie jest czyste, ale w opisie jest napisane „używaj oszczędnie”, odmów i zapytaj dlaczego. Czyste narzędzia powinny być tanie w ponownym uruchomieniu.
- Jeśli recenzent zostanie poproszony o zatwierdzenie narzędzia, które komunikuje się z produkcyjną bazą danych bez strażnika tylko do odczytu, odmów i kieruj do fazy 13 · 17 (bramy i zasady).

Wynik: jednostronicowy audyt zawierający nazwę, opis, schemat i ustalenia wykonawcy wraz z ważnością (blok/ostrzeżenie/nit) oraz ostateczny werdykt dotyczący wysłania/poprawienia/odrzucenia. Zakończ jednowierszową sugestią przepisywania w przypadku odrzucenia, jeśli to możliwe.