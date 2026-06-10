---

name: text-encoder-picker
description: Wybierz architekturę kodera tekstu dla danego zestawu ograniczeń.
phase: 5
lesson: 08

---

Biorąc pod uwagę ograniczenia (zadanie, ilość danych, budżet opóźnień, cel wdrożenia, budżet obliczeniowy), wynik:

1. Architektura kodera: TextCNN, BiLSTM, BiLSTM-CRF, dostrajanie transformatora lub „wstępnie wyszkolony transformator jako zamrożony koder + mała głowica”.
2. Osadzanie danych wejściowych: losowe init, zamrożone GloVe lub fastText lub kontekstowe osadzanie transformatora.
3. Przepis na szkolenie w 5 liniach: optymalizator, szybkość uczenia się, wielkość wsadu, epoki, regularyzacja.
4. Jeden sygnał monitorujący. Modele RNN/CNN: sprawdź dokładność długości sekwencji pod kątem błędów związanych z długą zależnością. Transformator dostraja się: uważaj na załamanie dostrajania, jeśli LR jest za wysokie; sprawdź utratę pociągu w ciągu pierwszych 100 kroków.

Odmów zalecenia dostrajania transformatora, gdy użytkownik ma mniej niż 500 oznaczonych przykładów bez uprzedniego wykazania, że ​​linia bazowa TextCNN/BiLSTM osiągnęła plateau. Oznacz wdrożenie brzegowe (telefon, mikrokontroler, przeglądarka) jako wymagające podjęcia decyzji dotyczących architektury przed wszystkim innym.