# Dekodowanie spekulatywne EAGLE-3 w produkcji

> Dekodowanie spekulatywne łączy szybki model z modelem docelowym. W projekcie zaproponowano tokeny K; cel sprawdza w pojedynczym przekazie; akceptowane tokeny są bezpłatne. W 2026 r. EAGLE-3 będzie wariantem klasy produkcyjnej — uczy szefa wersji roboczej w zakresie ukrytych stanów modelu docelowego, a nie surowych tokenów, przesuwając współczynnik akceptacji alfa do zakresu 0,6–0,8 na czacie ogólnym. Właściwym pytaniem nie jest „jak szybka jest wersja robocza”, ale „jaka jest wersja alfa w moim ruchu?” Jeśli wartość alfa spadnie poniżej ~ 0,55, dekodowanie spekulatywne będzie ujemne przy dużej współbieżności, ponieważ każda odrzucona wersja robocza kosztuje drugie docelowe przejście w przód. Ta lekcja uczy, jak najpierw zmierzyć alfa, a następnie odwrócić flagę.

**Typ:** Ucz się
**Języki:** Python (stdlib, symulator wskaźnika akceptacji zabawek)
**Wymagania wstępne:** Faza 17 · 04 (wewnętrzne serwery vLLM), faza 10 · 18 (przewidywanie wielu tokenów)
**Czas:** ~60 minut

## Cele nauczania

- Wymień trzy generacje dekodowania spekulatywnego i wyjaśnij, jakie zmiany EAGLE-3 różni się od EAGLE-2 i od klasycznego modelu roboczego.
- Zdefiniuj współczynnik akceptacji alfa, oblicz oczekiwane przyspieszenie na podstawie alfa i K (długość wersji roboczej) i zidentyfikuj próg rentowności alfa dla docelowej współbieżności.
- Wyjaśnij, dlaczego dekodowanie spekulatywne jest opcjonalne (nie domyślne) w vLLM 2026 i dlaczego włączenie go bez pomiaru alfa jest antywzorcem produkcyjnym.
- Napisz plan pomiarów: który punkt odniesienia, który monit o dystrybucję, jaki punkt współbieżności, na którą metrykę się zdecydować.

## Problem

Dekodowanie jest powiązane z pamięcią. Na H100 z systemem Llama 3.3 70B FP8 każdy zdekodowany token odczytuje wagi ~140 GB/s i emituje jeden token. Podczas dekodowania procesor graficzny jest prawie bezczynny — wąskim gardłem jest przepustowość HBM, a nie przepustowość Matmul.

Dekodowanie spekulatywne wykorzystuje lukę. Wygeneruj K tokenów kandydatów za pomocą taniego modelu roboczego, a następnie poproś model docelowy o zweryfikowanie wszystkich K w jednym przebiegu do przodu. Każdy zweryfikowany token jest faktycznie darmowy (amortyzowany w formie partii K, którą cel i tak musiałby zrobić).

Klasyczne podejście do modelu szkicowego wykorzystuje mniejszy model z tej samej rodziny (rysunek Lamy 3.2 1B dla Lamy 3.3 70B). Działa, ale współczynnik akceptacji jest przeciętny — dystrybucja mniejszego modelu odbiega od wartości docelowej. EAGLE, następnie EAGLE-2, a następnie EAGLE-3 trenują głowicę lekkiego przeciągu bezpośrednio na stanach wewnętrznych modelu docelowego, dzięki czemu dystrybucja przeciągu znacznie dokładniej śledzi cel. Dlatego alfa zmienia się z 0,4 w modelu roboczym na 0,6-0,8 w EAGLE-3.

Haczyk: EAGLE-3 jest opcjonalny w vLLM 2026. Wartość `speculative_config` musi być ustawiona jawnie. Żadnej flagi, żadnego przyspieszenia. Zespoły, które włączają tę opcję bez pomiaru alfa rzeczywistego ruchu, często zauważają, że opóźnienie ogona się pogarsza, a nie poprawia.

## Koncepcja

### Co faktycznie kupuje spekulatywne dekodowanie

Bez dekodowania specyfikacji koszt za token wynosi jeden cel do przodu. Przy dekodowaniu specyfikacji przy długości roboczej K i alfa akceptacji oczekiwane tokeny na docelowe przesyłanie wynoszą `1 + K * alpha`. Przyspieszenie wynosi `(1 + K * alpha) / (1 + epsilon)`, gdzie epsilon to narzut związany z wersją roboczą i weryfikacją. Dla K=5, alfa=0,7: `(1 + 5*0.7) / (1 + 0.1) = 4.5 / 1.1 = 4.1x`. Liczby w świecie rzeczywistym skupiają się wokół 2-3x, ponieważ alfa rzadko jest tak wysoka w ruchu produkcyjnym, a epsilon rośnie przy dużym rozmiarze partii.

### Dlaczego alfa to jedyny ważny wskaźnik

Odrzucone żetony nie znikają — popychają drugi cel do przodu po pierwszy odrzucony żeton. W przypadku obciążenia, w którym alfa spada do 0,4, płacisz koszty ogólne wersji roboczej, weryfikację i ponowne losowanie. Przy dużej współbieżności (powiedzmy 256 współbieżnych) partia dekodowania jest już wystarczająco duża, że ​​luka w przepustowości pamięci między „samym celem” a „celem z weryfikacją” maleje. Poniżej alfa 0,55 na większości sprzętu z roku 2026 dekodowanie specyfikacji jest ujemne.

Alfa różni się w zależności od obciążenia. Na czacie ogólnym w stylu ShareGPT, EAGLE-3 przeszkolony na ShareGPT osiągnął wynik 0,6-0,8. W przypadku ruchu specyficznego dla domeny (kodowy, medyczny, prawny) szef projektu przeszkolony na danych ogólnych spada do 0,4-0,6. Szkolenie kierownika projektu specyficznego dla domeny przywraca stan alfa — jest to lekkie i szybkie zadanie szkoleniowe w porównaniu z dostrajaniem celu.

### Pokolenia EAGLE w skrócie

- **Klasyczny model roboczy**: mały model tej samej rodziny. Alfa 0,3-0,5. Infrastruktura prosta — załadowano dwa modele, przeciągi K do przodu na każdy cel do przodu.
- **EAGLE-1 (2024)**: pojedynczy szef przeszkolony w zakresie docelowych stanów ukrytych (ostatnia warstwa). Alfa ~0,5-0,6. Mały nad głową param nad celem.
- **EAGLE-2 (2025)**: adaptacyjna długość zanurzenia i przeciągi oparte na drzewach (weryfikacja wielu gałęzi w jednym przebiegu docelowym). Alfa ~0,6-0,7. Bardziej złożony harmonogram wersji roboczej.
- **EAGLE-3 (2025-2026)**: szef przeszkolony na wielu warstwach docelowych (nie tylko na ostatniej), lepsze ustawienie. Alfa ~0,6-0,8 na czacie ogólnym.

### Przepis na produkcję 2026

1. Zwykły model docelowego statku. Zmierz bazową przepustowość TTFT, ITL i przy docelowej współbieżności.
2. Włącz wersję roboczą EAGLE-3 poprzez vLLM `speculative_config`. Uruchom ponownie benchmark.
3. Wskaźnik akceptacji dziennika alfa. vLLM V1 zgłasza to jako `spec_decode_metrics.accepted_tokens_per_request`. Podziel przez żądaną długość zanurzenia, aby uzyskać alfa.
4. Jeśli alfa < 0,55 w dystrybucji ruchu produkcyjnego, wyłącz dekodowanie specyfikacji lub wytrenuj wersję roboczą EAGLE-3 specyficzną dla domeny.
5. Przy współbieżności produkcji uruchom ponownie. Potwierdź, że P99 ITL nie uległ pogorszeniu.

### Pułapka produkcyjna: ogon P99

Średnie spadki ITL przy dekodowaniu specyfikacji. P99 może się pogorszyć, jeśli nie dostroisz. Odrzucone wersje robocze uruchamiają sekwencję dwóch przejść (wersja robocza + weryfikacja-niepowodzenie + przerzucenie). W przypadku pełnej partii te dwa przebiegi serializują. Oglądaj P99 ITL, a nie P50.

### Gdzie EAGLE-3 jest już wdrożony

Google wdrożyło dekodowanie spekulatywne w przeglądach AI w 2025 r. (ta sama jakość, szybsza reakcja). vLLM V1 dostarcza `speculative_config` jako udokumentowany interfejs; Dekodowanie spekulatywne N-gramowego GPU w wersji 1 jest wariantem zgodnym z wstępnym wypełnieniem fragmentarycznym. SGLang obsługuje EAGLE-3 jako zalecaną ścieżkę roboczą dla obciążeń wymagających dużej liczby prefiksów.

### Matematyka progu rentowności w jednym wierszu

Oczekiwane przyspieszenie: `S(alpha, K) = (1 + K*alpha) / (1 + verify_overhead)`. Ustawienie `S = 1` rozwiązuje problem alfa: `alpha_breakeven = verify_overhead / K`. Dla typowego narzutu zweryfikowanego ~0,15 i K=5: `alpha_breakeven = 0.03`. Ale to jest surowa matematyka dekodowania. Przy dużej współbieżności narzut weryfikacyjny wzrasta, a partia dekodowania już amortyzuje odczyty pamięci w sekwencjach, więc efektywna wartość alpha_breakeven w praktyce wzrasta do ~ 0,45-0,55.

### Kiedy nie używać dekodowania spekulatywnego

- Generowanie offline w trybie Batch-1, gdzie opóźnienie nie ma znaczenia. Użyj zwykłego celu.
- Bardzo krótkie wyjścia (poniżej 50 żetonów). Opracuj koszty ogólne i zweryfikuj, czy dominują koszty.
- Wyspecjalizowane domeny bez przeszkolonego w tej dziedzinie kierownika projektu. Alfa za niska.
- vLLM v0.18.0 plus dekodowanie specyfikacji modelu roboczego oraz `--enable-chunked-prefill`. Ta kombinacja nie kompiluje się. Udokumentowanym wyjątkiem jest dekodowanie specyfikacji GPU N-gram w wersji 1.

## Użyj tego

`code/main.py` symuluje pętlę dekodowania z dekodowaniem spekulatywnym i bez niego w zakresie wartości alfa i długości ciągu K. Drukuje wartość alfa progu rentowności, zmierzone przyspieszenie i zachowanie końcowe. Uruchom go na kilku kombinacjach (alfa, K), aby dokładnie zobaczyć, gdzie dekodowanie spekulacyjne przestaje się opłacać.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-eagle3-rollout.md`. Biorąc pod uwagę model docelowy, opis dystrybucji ruchu i docelową współbieżność, tworzy etapowy plan wdrożenia EAGLE-3 — punkt odniesienia dla testu porównawczego, konfiguracja włączenia, pomiar alfa, bramka na poziomie alfa >= 0,55, obserwacja P99 ITL.

## Ćwiczenia

1. Uruchom `code/main.py`. Przy K=5, jakiej alfa potrzebujesz, aby przyspieszyć 2x? Dla 3-krotnego przyspieszenia? Jak wrażliwe jest to na zweryfikowanie_narzutu?
2. Wyobraź sobie, że ruch produkcyjny dzieli się na 70% czat ogólny i 30% kod. Czat ogólny w wersji alfa 0.7 z programem EAGLE-3 przeszkolonym na ShareGPT; kod trafia w wersję alfa 0.4. Co to jest mieszana alfa i czy dekodowanie specyfikacji jest dodatnie?
3. Przeczytaj dokumentację vLLM `speculative_config`. Nazwij trzy tryby (model roboczy, EAGLE, N-gram) i który z nich jest kompatybilny z wstępnym wypełnieniem fragmentarycznym.
4. Widzisz średni spadek ITL o 25% po włączeniu EAGLE-3, ale P99 ITL wzrósł o 15%. Zdiagnozuj i zaproponuj środki łagodzące.
5. Oblicz koszt pamięci głowicy roboczej EAGLE-3 dla Lamy 3.3 70B. Jak wypada w porównaniu z uruchamianiem Llamy 3.2 1B w klasycznej wersji roboczej?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Dekodowanie spekulatywne | „wersja robocza i weryfikacja” | Zaproponuj K tokenów z tanim modelem, zweryfikuj wszystkie K w jednym celu do przodu |
| Wskaźnik akceptacji alfa | „wskaźnik akceptacji specyfikacji” | Część żetonów draftu zaakceptowana przez cel; jedyny wskaźnik, który się liczy |
| Długość zanurzenia K | "spec k" | Ile tokenów projekt proponuje na docelowego napastnika; typowe 4-8 |
| Sprawdź narzut epsilon | „narzut specyfikacji” | Dodatkowy koszt weryfikacji i ponownego rzutu w porównaniu ze zwykłym napastnikiem docelowym; rośnie wraz z partią |
| ORZEŁ-3 | „najnowszy EAGLE” | wariant 2025-2026; trenuje głowicę pociągową na wielu warstwach docelowych; alfa 0.6-0.8 na czacie ogólnym |
| `speculative_config` | „Konfiguracja specyfikacji vLLM” | Wyraźna zgoda w vLLM V1; brak wartości domyślnych oznacza brak przyspieszenia |
| Dekodowanie specyfikacji N-gramów | „N-gramowy projekt” | Wersja robocza po stronie GPU z wykorzystaniem wyszukiwania N-gramów w wierszu poleceń; kompatybilny z fragmentacją |
| Próg rentowności alfa | „alfa bez operacji” | Alfa, przy której dekodowanie specyfikacji daje zerowe przyspieszenie; obejrzyj to przy współbieżności produkcji |
| Odrzucony projekt dwuprzebiegowy | „koszt ponownego rzutu” | Dwóch docelowych napastników w przypadku odrzucenia draftu; napędza ogon P99 |

## Dalsze czytanie

- [vLLM — dokumentacja spekulatywnego dekodowania](https://docs.vllm.ai/en/latest/features/spec_decode/) — wiarygodne źródło na temat `speculative_config` i zgodności z fragmentowanym wstępnym wypełnianiem w wersji 1.
- [vLLM Speculative Config API](https://docs.vllm.ai/en/latest/api/vllm/config/speculative/) — dokładny zestaw pól.
- [Artykuł EAGLE (arXiv:2401.15077)](https://arxiv.org/abs/2401.15077) — oryginalne sformułowanie głowicy roboczej EAGLE.
- [Artykuł EAGLE-2 (arXiv:2406.16858)](https://arxiv.org/abs/2406.16858) — wersje adaptacyjne i drzewa.
- [UC Berkeley EECS-2025-224](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2025/EECS-2025-224.html) — wydajny system LLM z dekodowaniem spekulatywnym.
- [BentoML — Dekodowanie spekulacyjne](https://bentoml.com/llm/inference-optimization/speculative-decoding) — lista kontrolna wdrożenia produkcyjnego.