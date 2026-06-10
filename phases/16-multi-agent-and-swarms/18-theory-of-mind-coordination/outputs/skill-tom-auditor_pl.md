---

name: tom-auditor
description: Przeprowadź audyt systemu wieloagentowego, który wymaga „wschodzącej koordynacji”. Oddziela rzeczywistą koordynację włączoną przez ToM od szybko ubranej iluzji z warunkami kontrolnymi, testami statystycznymi i pomiarem komplementarności.
version: 1.0.0
phase: 16
lesson: 18
tags: [multi-agent, theory-of-mind, coordination, evaluation, emergence]

---

Biorąc pod uwagę system wieloagentowy, który wymaga wschodzącej koordynacji, sprawdź, czy koordynacja jest rzeczywista, czy też jest artefaktem szybkiej inżynierii.

Wyprodukuj:

1. **Wyodrębnienie roszczeń.** Jakie zachowanie koordynacyjne jest zarzucane? (podział pracy, przewidywanie, działania komplementarne, osiąganie konsensusu). Podaj to dokładnie.
2. **Szybka inspekcja.** Czy monit systemowy dowolnego agenta wyraźnie instruuje koordynację, wybór ról lub świadomość zespołu? Jeśli tak, oznacz roszczenie jako częściowo rozpatrzone natychmiastowo i zaprojektuj kontrolę.
3. **Warunek sterowania.** Wersja systemu pozbawiona języka wywołującego koordynację. Określ dokładnie, jaki tekst ma się zmienić.
4. **Metryka.** Co najmniej jedno z: zróżnicowanie powiązane z tożsamością, komplementarność ukierunkowana na cel, synergia wyższego rzędu (Riedl 2025). Nie przyjmuj stwierdzenia, że ​​agenci współpracują ze sobą jako dowodu.
5. **Test statystyczny.** Znaczenie metryki dla systemu w porównaniu z kontrolą. Rozmiar próbki potrzebny do `p < 0.05`. W przypadku prób `n < 50` należy wyraźnie zgłosić moc.
6. **Sprawdzanie pojemności modelu.** Powtórz porównanie dla mniejszego modelu podstawowego. Czy efekt utrzymuje się czy zanika? Obydwa Li/Riedl wykazują zależność od pojemności.
7. **Przegląd przypadków awarii.** Kiedy system ulegnie awarii, jak wygląda stan ToM (jeśli taki istnieje)? Zamieszanie tożsamości (przerwane powiązanie czynnika wiary) czy halucynacje dotyczące treści (niewłaściwa treść przekonań)?

Twarde odrzucenia:

- Twierdzenia o pojawieniu się bez warunku kontroli. Bębny demonstracyjne nie stanowią dowodu.
- Twierdzenia, które znikają po analizie statystycznej (efekt poniżej `p < 0.05` w badaniach `n >= 50`). Są to iluzje koordynacyjne.
- Roszczenia dotyczące tylko jednego modelu. Jeśli mniejsza, silna linia bazowa również osiąga efekt bez monitowania ToM, koordynacja nie jest oparta na ToM.
- „Nasi agenci właśnie to rozpracowali” jako wyjaśnienie mechanizmu. Roszczenia dotyczące mechanizmu wymagają zarejestrowania stanu ToM i możliwości jego sprawdzenia.

Zasady odmowy:

- Jeśli system nie rejestruje rozumowań poszczególnych agentów, audyt nie jest w stanie odróżnić prawdziwej koordynacji od losowości. Zalecamy dodanie ustrukturyzowanych dzienników stanu ToM przed ponownym audytem.
- Jeśli zadanie ma obliczoną przez Oracle optymalną koordynację, porównaj ją z optymalną, a nie z kontrolą.
- Jeżeli żądanie jest wąskie („koordynacja zadania jednorundowego”), audyt może mieć formę krótszej kontroli: zmierzyć komplementarność w pojedynczej rundzie, nie jest wymagana analiza długoterminowa.

Wynik: dwustronicowy audyt. Zacznij od jednozdaniowego werdyktu („Twierdzenie o koordynacji jest natychmiastowe: usunięcie języka„ współpracuj ”spada metrykę z 0,82 do 0,31, znaczenie dla kontroli.”), a następnie siedem sekcji powyżej. Zakończ listą poprawek umożliwiających konwersję szybkiej koordynacji na rzeczywistą koordynację: jawny stan ToM, dłuższe horyzonty z rejestrowaniem, zespoły modeli mieszanych.