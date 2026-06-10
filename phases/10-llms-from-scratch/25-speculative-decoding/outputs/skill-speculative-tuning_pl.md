---

name: speculative-tuning
description: Sprofiluj obciążenie dekodowaniem i wybierz model wersji roboczej, długość wersji roboczej K, bramkę temperaturową i zasady awaryjne na potrzeby dekodowania spekulatywnego.
version: 1.0.0
phase: 10
lesson: 25
tags: [speculative-decoding, draft-model, alpha, throughput, inference, decode-latency]

---

Biorąc pod uwagę model docelowy (rozmiar, rodzina, tokenizator), dane telemetryczne obciążenia (zestaw zadań, stosunek tokenów podpowiedzi do dekodowania, opóźnienie dekodowania p50/p99, zapas akceleratora i HBM, średni rozmiar partii, rozkład temperatury próbkowania) oraz dostępne punkty kontrolne wersji roboczej, wynik:

1. Projekt wyboru. Wybierz spośród małych jednostek tej samej rodziny (Llama-3.2-1B dla Llama-70B), destylowanego ciągu (specyfikacja Qwen3-0.6B), głów Meduzy przykręconych do celu lub „bez dekodowania specyfikacji”, jeśli brak zanurzenia jest bliższy niż 30% współczynnika kosztu FLOP. Potwierdź dopasowanie tokenizera do docelowego bajtu po bajcie; odrzuć niedopasowany tokenizer.
2. Długość zanurzenia K. Argmax of E[tokens] / (1 + K x c) gdzie c jest stosunkiem kosztu przeciągu do docelowego. Pokaż pracę dla K w 2, 3, 4, 5, 6, używając zmierzonej wartości alfa z przebiegu kalibracji na 5_000 tokenach danych w dystrybucji. Domyślnie K=4 dla czatu, K=6 dla kodu, K=2 dla kreatywnego pisania w wysokiej temperaturze.
3. Bramka temperaturowa. Ustaw próg temperatury, powyżej którego dekodowanie specyfikacji jest wyłączone. Domyślnie 0,8; niższa do 0,6, jeśli kalibracja wykazuje wcześniejsze załamanie alfa. Odrzuć każdą bramkę temperaturową, która zależy od kontroli na żądanie, która dodaje więcej niż 50 mikrosekund.
4. Budżet drzewa. Jeśli stos obsługujący obsługuje kreślenie drzew, wybierz małe, stałe drzewo (głębokość 2, gałąź 3-2) dla partii poniżej 8; płaski łańcuch dla partii powyżej 32. Podaj rozmiar minimalnej wartości KV weryfikatora w bajtach i potwierdź, że mieści się on w zapasie HBM.
5. Polityka awaryjna. Nazwij metrykę (alfa mierzona w przesuwającym się oknie w ciągu ostatnich 1_000 weryfikacji) i próg (alfa poniżej 0,4), przy którym serwer powraca do zwykłego dekodowania autoregresyjnego dla tego strumienia żądań. Uwzględnij czas życia decyzji awaryjnej na żądanie.

Odrzuć dekodowanie specyfikacji przy rozmiarze partii powyżej punktu, w którym weryfikator jest powiązany z obliczeniami. Powyżej tego punktu niewykorzystane FLOPy, które spekulant miał wchłonąć, już nie istnieją; spadki przepustowości. Odrzuć dekodowanie specyfikacji dla dowolnej rodziny zadań ze zmierzoną wartością alfa poniżej 0,4; dominuje narzut związany z przeciągiem, a opóźnienie zegara ściennego staje się większe. Odrzuć wersję roboczą, która nie została zatwierdzona na wystawionej próbce 1_000 żetonów przeciwko celowi: niezatwierdzona wersja robocza jest cichym dryfem KL.

Przykładowe wejście: „Llama-3.3-70B na 8xH100, obciążenie czatem, partia 16, dekodowanie p50 28 ms, p99 60 ms, średni rozkład temperatury 0,4 / maks. 1,2, kalibracja pokazuje alfa 0,78 na czacie, 0,61 w kodzie.”

Przykładowe wyjście:
- Wersja robocza: Llama-3.2-1B-Instruct-spec. Ten sam tokenizator, ta sama rodzina, współczynnik c około 0,03.
- K: 4. E[tokeny/weryfikacja] = 3,4 czat, 2,5 kod. K=5 zyskuje 0,1 tokena na czacie i płaci dodatkowo 0,03 c; odrzucić.
- Bramka temperaturowa: 0,8. Powyżej 0,8 alfa spada poniżej 0,45 na zestawie kalibracyjnym.
- Budżet drzewa: głębokość 2 gałęzi (3, 2). KV Scratch 480 MB w partii 16 pasuje.
- Awaryjne działanie: alfa z przesuwanym oknem przez ostatnie 1_000 weryfikuje wartość poniżej 0,40, wyłącza dekodowanie specyfikacji dla tego strumienia na 30 s, a następnie sonduje ponownie.