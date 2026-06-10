---

name: reflexion-buffer
description: Utrzymuj bufor pamięci epizodycznej odbić dla werbalnego RL z TTL, deduplikacją i zakresem.
version: 1.0.0
phase: 14
lesson: 03
tags: [reflexion, episodic-memory, self-healing, verbal-rl, sleep-time]

---

Biorąc pod uwagę klasę zadania (powtarzający się rodzaj uruchomienia agenta — np. „refaktoryzacja funkcji”, „zamknięcie zgłoszenia pomocy technicznej”), utrzymuj bufor odbić w pamięci epizodycznej. Każde odbicie rejestruje tryb awarii i wgląd korygujący w języku naturalnym. Bufor jest dołączany do następnej próby tej samej klasy zadań.

Wyprodukuj:

1. Przechwytywanie odbicia. Gdy próba zakończy się wynikiem poniżej progu, wyemituj jednoliniowe odbicie w kształcie „Nie udało mi się zrobić X, ponieważ Y; następnym razem Z”. Odrzuć refleksje na temat awarii zewnętrznych (sieć, 500 upstream), chyba że są one powtarzalne.
2. TTL i deduplikacja. Domyślnie refleksje wygasają po N próbach (sugerowanych jest 10). Dokładne duplikaty upadają. Prawie duplikaty (> 0,9 cosinus w małym modelu osadzania lub współdzielony podciąg >= 80%) zachowują tylko najnowsze.
3. Polityka zakresu. Trzy zakresy: klasa zadania (na nazwę zadania), użytkownik (między zadaniami tego samego użytkownika), agent (dla wszystkich użytkowników). Wartość domyślna to klasa zadań. Eskaluj do zakresu użytkownika tylko wtedy, gdy odbicie odnosi się do preferencji specyficznych dla użytkownika; nigdy nie eskaluj automatycznie do zakresu agenta.
4. Zagęszczanie. Gdy bufor przekracza budżet, uruchom kompaktowanie w czasie uśpienia: klastruj prawie duplikaty, podsumuj, scal. Zagęszczanie przebiega poza gorącą ścieżką — nie opóźniaj reakcji głównego agenta.
5. Szybka integracja. Wyemituj pojedynczy blok zatytułowany „Czego nauczyłem się z poprzednich prób” z listą punktowaną. Ogranicz do 6 pozycji w monicie; przepełnienie trafia do osobnej pozycji podsumowania („... i 4 starsze refleksje na temat przekroczeń limitu czasu”).

Twarde odrzucenia:

- Zapisywanie refleksji w stylu „następnym razem zachowaj większą ostrożność”. To nie podlega zaskarżeniu. Uruchom ponownie reflektor, wyświetlając monit wymuszający podanie konkretnej instrukcji następnym razem.
- Wygasające odbicia na podstawie czasu zegara ściennego, a nie liczby prób. W przypadku uruchomień, które można odtwarzać w trybie offline, TTL powinien mieć charakter próbny, a nie czasowy.
- Przechowywanie refleksji odnoszących się do sekretów (klucze API, tokeny, PII). Odrzuć z konkretnym błędem klasy „zawiera sekret” przed zatwierdzeniem w buforze.

Zasady odmowy:

- Jeśli nie ma przydzielonego oceniającego, odmów i zarekomenduj Lekcję 05 (Samodoskonalenie/KRYTYK) — refleksja wymaga sygnału, a nie przeczucia.
- Jeżeli klasa zadania jest jednorazowa (nigdy się nie powtarza), odmów; pamięć epizodyczna nie robi nic w przypadku zadania, które nigdy się nie powtarza.

Dane wyjściowe: uporządkowany plik bufora (JSON z obiektami odbicia: identyfikator wersji próbnej, klasa zadania, zakres, tekst, utworzony_at, ttl_remaining), blok podpowiedzi dla następnej wersji próbnej oraz raport „nieaktualne odbicia” zawierający wpisy, które wkrótce wygasną.

Zakończ notatką „co przeczytać dalej” wskazującą na Lekcję 06 (kompresja kontekstu), jeśli bufor nadal osiąga limit, lub Lekcję 08 (Obliczanie czasu uśpienia Letta), aby przenieść zagęszczenie ze ścieżki gorącej.