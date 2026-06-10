---

name: eagle3-rollout
description: Przygotuj etapowy plan wdrożenia EAGLE-3 z dekodowaniem spekulatywnym, który mierzy współczynnik akceptacji alfa w rzeczywistym ruchu przed wysyłką.
version: 1.0.0
phase: 17
lesson: 05
tags: [speculative-decoding, eagle-3, vllm, alpha, production-rollout]

---

Biorąc pod uwagę model docelowy, sprzęt (typ i liczba GPU), opis ruchu (czat ogólny/kod/specjalistyczny), docelową współbieżność i bieżące metryki bazowe (TTFT, ITL, przepustowość), stwórz etapowy plan wdrożenia EAGLE-3.

Wyprodukuj:

1. Podstawowy plan pomiarów. Który test porównawczy (LLMPerf, GenAI-Perf lub cień produkcyjny), który skłania do dystrybucji, jaki punkt współbieżności, jakie metryki rejestrować (średnia TTFT/P99, średnia ITL/P99, przepustowość, współbieżność).
2. Wybór głowicy pociągowej. Udostępnij EAGLE-3 przeszkolony przez GPT do czatu ogólnego. Przeszkolony w domenie EAGLE-3 dla ruchu specjalistycznego (kod, medycyna, prawo) lub decyzja o przeszkoleniu go przed wysyłką.
3. Konfiguracja Dokładne pola vLLM `speculative_config` (metoda, model, num_speculative_tokens). Zwróć uwagę na kompatybilność z wersją 0.18.0: spekulacje dotyczące modelu roboczego nie mogą łączyć się z `--enable-chunked-prefill`; Wyjątkiem jest dekodowanie specyfikacji GPU N-gram w wersji 1.
4. Brama alfa. Docelowa alfa >= 0,55 przy współbieżności produkcyjnej. Procedura pomiaru: ruch w cieniu przez 24 godziny, log vLLM `spec_decode_metrics`, podziel zaakceptowane tokeny przez żądaną długość zanurzenia. Wyłącznik awaryjny, jeśli wartość alfa spadnie poniżej 0,45 w dowolnym 1-godzinnym oknie.
5. Zegarek na ogon. Wykres delta P99 ITL (specyfikacja włączona – specyfikacja wyłączona). Jeśli delta jest dodatnia, wzór dwuprzebiegowy odrzuconej wersji roboczej jest gryzący. Zmniejsz K lub wyłącz to obciążenie.
6. Kontrola rentowności. Przy zgłoszonej współbieżności oblicz próg rentowności alfa dla bieżącego obciążenia związanego z weryfikacją. Wysyłka tylko wtedy, gdy zmierzona alfa przekroczy próg rentowności o co najmniej 0,1.

Twarde odrzucenia:
- Wysyłka bez pomiaru alfa w ruchu produkcyjnym. Odmów i zażądaj całodobowego pomiaru cienia.
- Żądanie przyspieszenia 2-3x bez podawania zmierzonej wartości alfa.
— Włączenie dekodowania spekulatywnego dla zadań wsadowych offline, gdzie opóźnienie nie jest ograniczeniem.
— Łączenie spekulacji na temat modelu roboczego z fragmentarycznym wstępnym wypełnianiem w vLLM v0.18.0. Twarda niezgodność.

Zasady odmowy:
- Jeśli ruch to przede wszystkim bardzo krótkie wyjścia (średnio poniżej 50 tokenów), odmów. Dominuje przeciąg; statek, zwykły cel.
- Jeśli sprzęt jest przeznaczony dla konsumentów (RTX 4090/5090), a wielkość partii pozostaje poniżej 8, zaleca się zwykły cel — amortyzacja wsadowa w celu sprawdzenia, czy narzut wymaga współbieżności, której sprzęt nie jest w stanie zapewnić.
- Jeśli użytkownik chce automatycznego dostrojenia K bez pętli pomiarowej, odmów. K jest wybierane spośród zmierzonej wartości alfa plus sprawdzenie narzutu; żadne automatyczne dostrajanie nie zastępuje pomiaru.

Wynik: jednostronicowy etapowy plan wdrożenia zawierający listę bazową → konfiguracja → bramka alfa → obserwacja ogona → potwierdzenie progu rentowności. Zakończ akapitem „Co dalej mierzyć” wymieniając szkolenie EAGLE-3 specyficzne dla domeny, niższe K lub powrót do zwykłego celu, w zależności od diagnozy.