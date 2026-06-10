---

name: speculative-tuning
description: Sprofiluj proces dekodowania i wybierz model pomocniczy (draft), długość ciągu pomocniczego K, próg temperatury oraz politykę wycofania (fallback) dla dekodowania spekulatywnego.
version: 1.0.0
phase: 10
lesson: 25
tags: [speculative-decoding, draft-model, alpha, throughput, inference, decode-latency]

---

Na podstawie parametrów modelu docelowego (rozmiar, rodzina, tokenizator), danych telemetrycznych obciążenia (zestaw zadań, stosunek tokenów promptu do generowanych, opóźnienie dekodowania p50/p99, wolna pamięć akceleratora/HBM, średni batch size, rozkład temperatury próbkowania) oraz dostępnych punktów kontrolnych (checkpoints) modelu pomocniczego (draft), wygeneruj:

1. Wybór modelu pomocniczego. Wybierz mniejszy model z tej samej rodziny (np. Llama-3.2-1B dla Llama-70B), wydestylowany model dedykowany (np. Qwen3-0.6B-spec), głowice typu Medusa dołączone do modelu docelowego, bądź też zarekomenduj rezygnację z dekodowania spekulatywnego, jeśli zysk z jego wdrożenia jest mniejszy niż 30% kosztu operacji FLOP modelu pomocniczego. Potwierdź zgodność tokenizatora z modelem docelowym (porównanie bajt po bajcie); odrzuć modele z niezgodnym tokenizatorem.
2. Optymalną długość ciągu spekulacji K. Oblicz z zależności `argmax E[tokens] / (1 + K * c)`, gdzie `c` oznacza stosunek kosztu generacji modelu pomocniczego do docelowego. Przedstaw obliczenia dla K równego 2, 3, 4, 5, 6, używając zmierzonego parametru alfa (współczynnika akceptacji) z przebiegu kalibracyjnego na próbce 5 000 tokenów o rozkładzie produkcyjnym. Przyjmij wartości domyślne: K=4 dla konwersacji (chat), K=6 dla generowania kodu, K=2 dla kreatywnego pisania przy wysokiej temperaturze próbkowania.
3. Próg temperatury (bramkowanie). Ustal próg temperatury, powyżej którego dekodowanie spekulatywne zostaje wyłączone. Standardowo wynosi on 0,8; obniż go do 0,6, jeśli kalibracja wykaże spadek współczynnika akceptacji alfa przy niższych temperaturach. Odrzuć mechanizmy sprawdzania temperatury w czasie rzeczywistym, które dodają do czasu obsługi zapytania więcej niż 50 mikrosekund.
4. Strukturę drzewa spekulacji (tree budget). Jeśli framework obsługuje spekulację na drzewach tokenów (tree-drafting), wybierz małe, stałe drzewo (głębokość 2, rozgałęzienie 3-2) dla batch size poniżej 8; dla batch size powyżej 32 zastosuj prosty łańcuch (łańcuch liniowy). Podaj minimalny rozmiar pamięci podręcznej KV weryfikatora w bajtach i potwierdź, że mieści się on w wolnym budżecie pamięci HBM.
5. Politykę wycofania (fallback policy). Zdefiniuj metrykę (np. współczynnik alfa mierzony w oknie kroczącym ostatnich 1 000 weryfikacji) oraz próg (np. alfa < 0,4), przy którym system przełącza się na standardowe dekodowanie autoregresywne dla danego strumienia zapytań. Określ czas obowiązywania tej decyzji (TTL dla fallbacku).

Kategorycznie odrzucaj dekodowanie spekulatywne w sytuacjach, gdy batch size przekracza punkt, w którym weryfikator staje się ograniczony przez moc obliczeniową (compute-bound). W takich warunkach znikają wolne zasoby obliczeniowe (FLOPs), które model pomocniczy miał zagospodarować, co prowadzi do spadku przepustowości. Odrzuć dekodowanie spekulatywne dla zadań, w których zmierzony współczynnik akceptacji alfa spada poniżej 0,4 (narzut modelu pomocniczego zaczyna dominować, wydłużając rzeczywisty czas generacji). Odrzuć model pomocniczy, jeśli nie został on zwalidowany pod kątem rozbieżności KL na próbce testowej 1 000 tokenów względem modelu docelowego (brak walidacji grozi cichym dryfem rozkładu).

Przykładowe dane wejściowe: „Llama-3.3-70B na 8xH100, obciążenie czatem, partia 16, dekodowanie p50 28 ms, p99 60 ms, średni rozkład temperatury 0,4 / maks. 1,2, kalibracja pokazuje alfa 0,78 na czacie, 0,61 w kodzie.”

Przykładowe dane wyjściowe:
- Model pomocniczy (draft): Llama-3.2-1B-Instruct-spec. Ten sam tokenizator, ta sama rodzina, współczynnik c około 0,03.
- Długość K: 4. E[tokeny/weryfikacja] = 3,4 (chat), 2,5 (kod). Ustawienie K=5 daje zysk zaledwie 0,1 tokena dla chatu kosztem dodatkowych operacji o wartości 0,03 c – odrzucono.
- Próg temperatury (bramkowanie): 0,8. Powyżej tej wartości współczynnik alfa spada poniżej 0,45 na zbiorze kalibracyjnym.
- Struktura drzewa: głębokość 2, rozgałęzienie (3, 2). Narzut pamięci podręcznej KV (scratch space) wynoszący 480 MB przy batch size = 16 mieści się w limitach.
- Polityka wycofania: jeśli współczynnik alfa w oknie kroczącym 1 000 weryfikacji spadnie poniżej 0,40, wyłącz dekodowanie spekulatywne dla danego strumienia zapytań na 30 sekund, po czym wykonaj próbę ponownego włączenia (probe).
