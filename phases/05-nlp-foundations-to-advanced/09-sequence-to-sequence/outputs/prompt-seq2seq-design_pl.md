---

name: seq2seq-design
description: Zaprojektuj potok sekwencyjny dla danego zadania.
phase: 5
lesson: 09

---

Biorąc pod uwagę zadanie (tłumaczenie, podsumowanie, parafrazę, przepisanie pytania), wynik:

1. Architektura. Wstępnie wytrenowany koder-dekoder transformatorowy (BART, T5, mBART, NLLB) jest domyślny. Seq2seq oparty na RNN tylko dla określonych ograniczeń (strumieniowanie, wnioskowanie brzegowe, pedagogika).
2. Rozpoczęcie punktu kontrolnego. Nadaj mu nazwę (`facebook/bart-base`, `google/flan-t5-base`, `facebook/nllb-200-distilled-600M`). Dopasuj punkt kontrolny do zakresu zadania i języka.
3. Strategia dekodowania. Chciwy na deterministyczne wyniki, wyszukiwanie wiązki (szerokość 4-5) dla jakości, próbkowanie z temperaturą dla różnorodności. Uzasadnienie jednym zdaniem.
4. Jeden tryb awarii do sprawdzenia przed wysyłką. Błąd ekspozycji objawia się dryfem generacji w przypadku dłuższych wyników; pobierz 20 wyników o długości 90. percentyla i gałce ocznej.

Odmów polecania szkolenia seq2seq od zera dla mniej niż 1 miliona równoległych przykładów. Oznacz dowolny potok przy użyciu zachłannego dekodowania treści wyświetlanych użytkownikowi jako delikatny (zachłanne powtórzenia i pętle).