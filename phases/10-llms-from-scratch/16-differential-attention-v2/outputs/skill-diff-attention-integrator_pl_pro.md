---

name: diff-attention-integrator
description: Plan integracji umożliwiający dodanie mechanizmu Differential Attention V2 do nowego procesu pre-trainingu lub dostrajania metodą LoRA
version: 1.0.0
phase: 10
lesson: 16
tags: [differential-attention, diff-transformer, long-context, flash-attention, pre-training, lora]

---

Dla zadanej architektury modelu (wymiar ukryty, liczba głów, liczba głów KV, liczba warstw, wymiar głowy $d_{\text{head}}$), docelowej długości kontekstu, skłonności do halucynacji lub profilu działania na długim kontekście (typowe błędy w dotychczasowych ewaluacjach) oraz budżetu treningowego (dostępne tokeny, liczba godzin GPU), stwórz plan integracji mechanizmu DIFF V2 (Differential Attention V2).

Zwróć:

1. **Tryb integracji**: Wybierz spośród: trening od zera (pre-training from scratch), wymiana architektury przy kontynuacji treningu (continual pre-training) lub dostrajanie LoRA na projekcjach $Q$. Uzasadnij wybór, uwzględniając budżet treningowy i specyfikę zadań.
2. **Zmiany w architekturze**: Szczegółowa lista modyfikacji: które projekcje liniowe ulegają powiększeniu, które pozostają bez zmian, ile parametrów zostanie dodanych i w którym miejscu w bloku atencji realizowane jest odejmowanie macierzy atencji. Uwzględnij harmonogram inicjalizacji parametru $\lambda$ (`lambda_init`) w zależności od głębokości warstwy (domyślny wzór z oryginalnej publikacji naukowej to: `0.8 - 0.6 * exp(-0.3 * (depth - 1))`; zmodyfikuj go, jeśli telemetria wykazuje niestabilność na głębszych warstwach).
3. **Obsługa kerneli (kernel support)**: Potwierdź kompatybilność z FlashAttention 2 lub 3, biorąc pod uwagę specyfikę obliczeń w wersji V2 (podwójna liczba operacji). Odrzuć niestandardową implementację kernela dla wersji V1, chyba że użytkownik wymaga jej ze względu na odtwarzalność wyników.
4. **Budżet pamięci**: Rozmiar KV cache powinien pozostać bez zmian (liczba głów KV nie ulega modyfikacji). Oblicz przyrost pamięci aktywacji na token (dodatkowe głowy $Q$, dodatkowe obliczenia atencji). Podaj wartości bezwzględne dla docelowej długości kontekstu.
5. **Plan stabilizacji treningu**: Opisz parametry podlegające ciągłemu monitorowaniu: dryf parametru $\lambda$ na warstwach, entropia atencji na poszczególnych głowach, wariancja gradientów w projekcjach $Q$. Wskaż konkretną metrykę, która powinna wywołać procedurę wycofania (fallback) do standardowego mechanizmu atencji w przypadku wykrycia rozbieżności (divergence) treningu.

Zasady bezwzględnego odrzucenia (red flags):
- Dodanie mechanizmu atencji DIFF do gotowego, wstępnie wytrenowanego modelu (pre-trained) bez przeprowadzenia fazy kontynuacji pre-trainingu (continual pre-training). Powoduje to drastyczne zaburzenie rozkładu wyjść modelu – to nie jest rozwiązanie typu plug-and-play.
- Stosowanie wersji DIFF V1 w nowych procesach treningowych rozpoczynanych po kwietniu 2026 roku. Wersja V2 wykazuje zdecydowaną przewagę we wszystkich mierzonych aspektach.
- Integracja mechanizmu DIFF bez włączenia danych treningowych z długim kontekstem. Zysk z tej architektury ujawnia się dopiero przy kontekstach przekraczających 32k tokenów.
- Zmiana wartości `lambda_init` na ujemną bez kontrolowanych testów. Ujemna wartość początkowa powoduje zbyt silną redukcję atencji i doprowadzi do rozbieżności (załamania) treningu.

Kryteria odmowy zatwierdzenia:
- Jeśli docelowa długość kontekstu wynosi poniżej 16k tokenów – odrzuć integrację i zarekomenduj standardowy mechanizm atencji. Narzut pamięciowy i obliczeniowy nie jest w tym przypadku uzasadniony korzyściami z tłumienia szumów atencji.
- Jeśli użytkownik nie posiada odpowiednich zbiorów ewaluacyjnych dla długiego kontekstu (np. L-Eval, Needle In A Haystack, MultiNeedle) – odrzuć plan i zażądaj dostarczenia danych kalibracyjnych.
- Jeśli stos oprogramowania użytkownika nie obsługuje FlashAttention-2 lub nowszego – odrzuć plan i zalecaj aktualizację sterowników i bibliotek przed integracją.

Rezultat: jednostronicowa specyfikacja zawierająca: wybrany tryb integracji, zmianę liczby parametrów, wpływ na KV cache, potwierdzenie kompatybilności z FlashAttention, harmonogram zmian parametru $\lambda$ oraz zestaw 3 kluczowych metryk do monitorowania. Zakończ dokument sekcją „Kryterium sukcesu”, wskazującą minimalny oczekiwany przyrost wyniku w testach długiego kontekstu (np. różnica punktów procentowych na benchmarku RULER 64k), który uzasadnia wdrożenie DIFF V2 zamiast powrotu do architektury bazowej.
