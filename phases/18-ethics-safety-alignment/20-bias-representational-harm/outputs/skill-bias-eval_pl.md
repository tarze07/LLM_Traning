---

name: bias-eval
description: Przeprowadź audyt raportu oceny stronniczości pod względem kategorii metryk, intersekcjonalności i mechanizmu debias.
version: 1.0.0
phase: 18
lesson: 20
tags: [bias, fairness, weat, intersectionality, mechanistic-interpretability]

---

Biorąc pod uwagę raport z oceny stronniczości lub twierdzenie o uczciwości, przeprowadź kontrolę w całym Gallegos i in. Ramy trzech kategorii na rok 2024 i literatura dotycząca intersekcjonalności na lata 2024–2025.

Wyprodukuj:

1. Pokrycie metryczne. Czy ocena obejmuje co najmniej jeden wskaźnik z każdej kategorii: oparty na osadzaniu (w stylu WEAT), oparty na prawdopodobieństwie (logarytm wiarygodności stereotypów), oparty na wygenerowanym tekście (pomiar w dalszych etapach zadania)? Oznacz brakujące kategorie.
2. Separacja ze względu na krzywdę. Czy ewaluacja odróżnia szkodę reprezentacyjną od szkody alokacyjnej? Raport, który mierzy jedynie wytwarzanie stereotypów, nie mierzy alokacji zasobów na niższym szczeblu łańcucha dostaw.
3. Pokrycie intersekcjonalności. Czy oceniane są osie przekrojowe, czy tylko jednoosiowe (wyłącznie płeć, wyłącznie rasa)? Per An i in. 2025 r. w ocenie jednoosiowej rutynowo pomija się efekty przekrojowe.
4. Mechanizm Debiasa. Jeśli zastosowano debiasing, określ, czy działa on na osadzaniach (projekcja), neuronach MLP (Yu i Ananiadou 2025), cechach SAE (Ahsan i Wallace 2025), głowach uwagi (UniBias 2024), czy też na filtrowaniu wyników post-hoc. Oszacuj koszt ogólnej zdolności.
5. Różnorodność osi. Według metakrytyki z 2025 r. uprzedzenia binarne związane z płcią są nadmiernie badane w porównaniu z innymi osiami. Czy ocena obejmuje niepełnosprawność, religię, migrację lub wielojęzyczne osie tożsamości?

Twarde odrzucenia:
- Wszelkie „nieobiektywne” twierdzenia oparte na jednej kategorii miar.
- Wszelkie roszczenia dotyczące uczciwości bez oceny przekrojowej.
- Jakakolwiek interwencja Debia bez delty o ogólnych możliwościach.

Zasady odmowy:
- Jeśli użytkownik zapyta, czy jego model jest „wolny od stronniczości”, odrzuć twierdzenie binarne; błąd jest ciągłą właściwością z wieloma metrykami.
- Jeśli użytkownik poprosi o zalecaną operację debias, odrzuć pojedynczą rekomendację — wybór zależy od tego, gdzie znajduje się błąd (osadzenia, neurony, głowy, wyjścia).

Wynik: jednostronicowy audyt wypełniający pięć sekcji, oznaczający brakujące kategorie wskaźników i zalecający pojedynczą dodatkową ocenę o najwyższej wartości. Cytuj Gallegos i in. 2024 r. i po jednym dokumencie dotyczącym intersekcjonalności na lata 2024–2025.