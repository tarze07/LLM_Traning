---

name: eagle3-rollout
description: Przygotuj etapowy plan wdrożenia dekodowania spekulatywnego EAGLE-3, zakładający obowiązkowy pomiar współczynnika akceptacji alfa na rzeczywistym ruchu przed uruchomieniem produkcyjnym.
version: 1.0.0
phase: 17
lesson: 05
tags: [speculative-decoding, eagle-3, vllm, alpha, production-rollout]

---

Na podstawie parametrów modelu docelowego, specyfikacji sprzętowej (typ i liczba procesorów GPU), charakterystyki ruchu (czat ogólny / kod / zapytania specjalistyczne), docelowego poziomu współbieżności oraz bieżących metryk bazowych (TTFT, ITL, przepustowość) przygotuj etapowy plan wdrożenia technologii EAGLE-3.

Przygotuj:

1. **Podstawowy plan pomiarów.** Dobierz metodę testów (LLMPerf, GenAI-Perf lub produkcyjny ruch testowy typu shadow), określ strukturę promptów testowych, zdefiniuj poziom współbieżności i wskaż metryki do rejestracji (średnia i percentyl P99 TTFT, średnia i percentyl P99 ITL, przepustowość, współbieżność).
2. **Wybór głowicy pomocniczej (draft head).** Uzasadnij wybór: użycie standardowej głowicy EAGLE-3 przeszkolonej na ogólnych zbiorach konwersacyjnych w przypadku ruchu ogólnego, bądź decyzja o wytrenowaniu dedykowanej głowicy w specyficznej dziedzinie (kod źródłowy, medycyna, prawo) przed wdrożeniem produkcyjnym.
3. **Konfiguracja.** Wskaż dokładne parametry bloku `speculative_config` w vLLM (metoda, model, num_speculative_tokens). Uwzględnij kompatybilność z vLLM w wersji v0.18.0: dekodowanie spekulatywne z osobnym modelem pomocniczym (draft model) nie może być łączone z parametrem `--enable-chunked-prefill` (jedynym wyjątkiem jest jądro N-gram na GPU).
4. **Próg akceptacji (Alpha Gate).** Zdefiniuj próg wdrożeniowy dla współczynnika $\alpha \ge 0.55$ przy docelowym ruchu produkcyjnym. Określ procedurę pomiarową: rejestracja ruchu testowego przez 24 godziny, analiza metryk vLLM `spec_decode_metrics`, wyznaczenie współczynnika $\alpha$ poprzez podzielenie liczby zaakceptowanych tokenów przez długość propozycji $K$. Zdefiniuj regułę awaryjną: wyłączenie optymalizacji, jeśli współczynnik $\alpha$ spadnie poniżej 0.45 w dowolnym 1-godzinnym oknie pomiarowym.
5. **Monitorowanie opóźnień długiego ogona (Tail latency watch).** Analiza różnicy (delta) percentyla P99 ITL (przy włączonej vs wyłączonej optymalizacji). Jeśli wartość delta wykaże pogorszenie opóźnień długiego ogona, oznacza to, że narzut dwuetapowy odrzuconej propozycji pomocniczej przewyższa zyski. W takim przypadku wskaż potrzebę zmniejszenia parametru $K$ lub wyłączenia optymalizacji dla tego typu zadań.
6. **Analiza opłacalności.** Na podstawie deklarowanej współbieżności oblicz próg rentowności współczynnika $\alpha$ dla rzeczywistego narzutu weryfikacji. Zezwól na uruchomienie produkcyjne tylko wtedy, gdy zmierzony wskaźnik $\alpha$ przewyższa wyznaczony próg rentowności o co najmniej 0.1.

Bezwzględne odrzucenie planu w przypadku:

- Zgody na wdrożenie produkcyjne bez wcześniejszego pomiaru współczynnika $\alpha$ na rzeczywistym ruchu. Wymagaj przeprowadzenia 24-godzinnych testów shadow.
- Deklarowania przyspieszenia rzędu 2-3x bez podania zmierzonej wartości współczynnika $\alpha$.
- Włączania dekodowania spekulatywnego dla zadań wsadowych offline (batch), w których czas odpowiedzi pojedynczego zapytania nie jest kluczowym parametrem.
- Łączenia dekodowania spekulatywnego z osobnym modelem pomocniczym oraz chunked prefill w silniku vLLM v0.18.0 ze względu na krytyczną niekompatybilność.

Zasady weryfikacji i odmowy:

- Jeśli ruch w systemie składa się głównie z bardzo krótkich odpowiedzi (średnio poniżej 50 tokenów), odrzuć wdrożenie – koszt generowania propozycji zdominuje zyski; zaleć korzystanie ze standardowego modelu docelowego.
- Jeśli system działa na sprzęcie klasy konsumenckiej (np. RTX 4090/5090), a rozmiar paczki (batch size) wynosi poniżej 8, zaleć standardowe generowanie – amortyzacja narzutu weryfikacji wymaga poziomu współbieżności, którego ten sprzęt nie jest w stanie zapewnić.
- Jeśli użytkownik proponuje automatyczne dobieranie parametru $K$ bez wdrożenia pętli pomiarowej, odrzuć taką propozycję – optymalna wartość $K$ musi wynikać z rzeczywistych pomiarów współczynnika $\alpha$ oraz narzutu weryfikacji.

Format wyjściowy: Jednostronicowy, etapowy plan wdrożenia zawierający kroki: pomiary bazowe → konfiguracja → testy z progiem alfa → monitorowanie opóźnień ogona → weryfikacja progu rentowności. Zakończ sekcją „Dalsze rekomendacje”, wskazując – w zależności od wyników – na potrzebę dotrenowania dedykowanej głowicy EAGLE-3, zmniejszenia wartości $K$ lub powrotu do standardowego modelu docelowego.
