---

name: cold-start-planner
description: Wybierz i stosuj rozwiązania ograniczające zimny start dla bezserwerowych wdrożeń LLM. Fazy ​​budżetu (węzeł, obraz, wagi, silnik, pierwsze przekazanie) i dopasowanie środków zaradczych do umowy SLA.
version: 1.0.0
phase: 17
lesson: 10
tags: [cold-start, serverless, bottlerocket, model-streamer, gpu-snapshot, warm-pool, serverlessllm]

---

Biorąc pod uwagę rozmiar modelu, SLA (TTFT P99), kształt ruchu (stały lub gwałtowny) i stan budżetu, tworzą plan łagodzący przy zimnym uruchomieniu.

Wyprodukuj:

1. Budżet zimnego startu. Rozbij surową ścieżkę zimnego startu (dostarczenie węzła, pociągnięcie obrazu, wagi do HBM, inicjalizacja silnika, pierwsze przesyłanie do przodu). Użyj nominalnych sekund 2026 dla podanego rozmiaru modelu.
2. Wybór warstwy. Wybierz minimalną liczbę warstw, która spowoduje, że suma będzie niższa niż SLA: obraz wstępny (L1), streamer modelu (L2), migawka GPU (L3), ciepła pula (L4), ładowanie warstwowe (L5). Uzasadnij każdą warstwę względem konkretnej fazy, którą atakuje.
3. Rozmiar ciepłego basenu. Podaj stan `min_workers` dla ścieżki podstawowej. Jeśli umowa SLA wynosi TTFT P99 < 60 s w modelu 70B+, należy wprowadzić obowiązek podgrzewania basenu niezależnie od kosztów.
4. Kosztorys. Miesięczny koszt procesora graficznego dla wybranej ciepłej puli i oczekiwana liczba zimnych startów dziennie.
5. Polityka ogonowa. Co dzieje się z pierwszym użytkownikiem świeżej repliki — czy czeka go kolejka do ciepłej repliki, czy też płaci podatek zimnego rozruchu? Nazwij konkretną zasadę (np. „przekieruj pierwsze żądanie do dowolnej ciepłej repliki w ciągu 10 s; przejdź do zimnej”).
6. Tryb awaryjny. Co się stanie, jeśli ciepła replika umrze w połowie sesji? Czy odzyskiwanie odbywa się automatycznie (migracja na żywo), czy też jest to zimny start przy następnym żądaniu?

Twarde odrzucenia:
- Propozycja „po prostu dodaj ciepły basen” bez obliczania miesięcznych kosztów.
- Twierdzenie o łagodzeniu bez określonej fazy, którą atakuje (np. „użyj Bottlerocket”, nie mówiąc, że eliminuje to przyciąganie obrazu z lat 80.).
- Ignorowanie ograniczeń topologii poszczególnych procesorów graficznych w migawkach GPU — jeśli platforma migruje jednostkę SKU, migawki są nieprawidłowe.

Zasady odmowy:
- Jeśli SLA wynosi TTFT P99 < 5 s przy świeżym zimnym starcie 70 B bez ciepłego basenu, odmowa – matematycznie niemożliwe przy prędkościach infrastruktury 2026.
- Jeśli budżet nie pozwala na ciepły basen, ale umowa SLA wymaga zimnego startu poniżej 30 sekund, podaj poprawkę specyficzną dla platformy (migawki modalnego GPU, wstępne podgrzewanie Baseten) i nie obiecuj umowy SLA na inną platformę bez niej.
— Jeśli operator prosi o skalowanie do zera przy dużym ruchu i modelu 70B, odmów obietnicy SLA — matematyka nie działa bez migawek i ciepłych pul.

Dane wyjściowe: jednostronicowy plan zawierający listę faz, warstw, `min_workers`, kosztów miesięcznych, zasad dotyczących ogona, trybu awarii. Zakończ pojedynczym pomiarem, o którym ma być wyświetlany alert: P99 czas zimnego startu w ciągu ostatniej godziny.