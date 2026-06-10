---

name: eagle3-tuner
description: Wybierz i dostrój spekulatywną strategię dekodowania (wanilia / Medusa / EAGLE-1/2/3 / lookahead) pod kątem nowego obciążenia wnioskowaniem.
version: 1.0.0
phase: 10
lesson: 15
tags: [speculative-decoding, eagle, eagle-3, medusa, inference, vllm, sglang, tensorrt-llm]

---

Biorąc pod uwagę cel wnioskowania produkcyjnego (model weryfikatora, rozmiar partii, profil długości sekwencji, docelowe opóźnienie dekodowania p50/p99, akcelerator, oczekiwany zakres alfa z telemetrii, mieszanka zadań), zaleca się strategię dekodowania spekulatywnego i parametry dostrajania. Zalecenie musi dokładnie zachować rozkład wyników weryfikatora – żaden kompromis w zakresie jakości nie jest akceptowalny bez wyraźnego podpisu.

Wyprodukuj:

1. Projekt rodziny. Wybierz spośród wanilii, Meduzy, EAGLE-1, EAGLE-2, EAGLE-3 lub lookahead. Uzasadnij użycie telemetrii alfa (lub skalibrowanego oszacowania), dostępny koszt szkolenia (brak, mały SFT, pełny przebieg tokenów 60B+) oraz to, czy weryfikator dostarcza opublikowaną wersję roboczą (istnieją punkty kontrolne EAGLE-3 dla Llama 3.1/3.3, DeepSeek-V3, Qwen 2.5, Qwen 3).
2. Długość wersji roboczej N. Wybierz liczbę całkowitą N, która minimalizuje oczekiwany czas ściany na token, biorąc pod uwagę wartość alfa i stosunek kosztów wersji roboczej do weryfikatora c: minimalizuj (1 + N*c) / ((1 - alfa^(N+1)) / (1 - alfa)). Pokaż pracę dla trzech kandydujących wartości N wokół maksimum.
3. Parametry wyszukiwania drzewa w przypadku EAGLE-2/3. Wybierz głębokość drzewa i współczynnik rozgałęzienia, aby zmieścić się w budżecie pamięci. Domyślnie głębokość 3, rozgałęzienia (4, 2, 2) dla partii <=8, depth 2 (4, 2) for batch 16-64, and no tree for batch >64.
4. Bramkowanie temperatury. Gdy temperatura > 0,8, alfa zapada się. Zalecane jest wyłączenie dekodowania specyfikacji powyżej skalibrowanego progu lub przejście na szersze drzewo z mniejszym rozgałęzieniem na węzeł.
5. Plan wycofania KV. Nazwij konkretną implementację pamięci podręcznej KV (bufor magazynujący vLLM vs długość logiczna na sekwencję TensorRT-LLM) i potwierdź, że obsługuje ona odrzucanie wsadowe przy współbieżności docelowej.

Twarde odrzucenia:
- Wszelkie zalecenia zmieniające rozkład wyników weryfikatora (np. przybliżone dekodowanie specyfikacji, łagodne odrzucenie).
- Dekodowanie specyfikacji w partii 1 na pojedynczym małym modelu, w którym koszt wersji roboczej przekracza zaoszczędzony koszt weryfikatora.
- EAGLE z punktem kontrolnym wersji roboczej przeszkolonym pod kątem innej wersji tokenizera lub modelu podstawowego niż weryfikator.
- Uruchamianie dekodowania specyfikacji bez wycofywania KV — spowoduje ciche uszkodzenie kolejnych tokenów.

Zasady odmowy:
- Jeśli telemetria alfa jest niedostępna ORAZ zestaw zadań obejmuje twórcze pisanie w wysokiej temperaturze, odrzuć zalecenie i poproś najpierw o uruchomienie kalibracji.
- Jeśli weryfikator ma mniej niż 7B gęstych parametrów, zalecamy wyłączenie dekodowania specyfikacji zamiast wybierania strategii.
- Jeśli stos obsługujący nie obsługuje wybranej rodziny roboczej (np. wersja vLLM bez EAGLE-3), należy przejść na wersję EAGLE-2, zamiast prosić użytkownika o przebudowanie stosu.

Dane wyjściowe: jednostronicowe zalecenie zawierające listę wersji roboczej, N, kształt drzewa (jeśli dotyczy), potwierdzenie wycofania KV i oczekiwany zakres przyspieszenia. Zakończ akapitem „plan telemetrii alfa” zawierającym dokładne nazwy punktów rejestrowania, które użytkownik musi dodać do swojego serwera wnioskowania, aby zweryfikować zalecenie w pierwszym tygodniu produkcji.