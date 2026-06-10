# Równoległe wywołania narzędzi i przesyłanie strumieniowe

> Trzy niezależne zapytania o pogodę wykonywane sekwencyjnie to trzy pełne cykle komunikacji (round-trips). Uruchom je równolegle, a całkowity czas oczekiwania spadnie do czasu najwolniejszego pojedynczego połączenia. Każdy wiodący dostawca LLM pozwala obecnie na generowanie wielu wywołań narzędzi w jednej turze. Korzyści są bardzo duże, ale implementacja bywa subtelna. Ta lekcja dotyczy obu aspektów: równoległego uruchamiania oraz ponownego składania strumieniowanych argumentów, ze szczególnym uwzględnieniem pułapki korelacji identyfikatorów (ID).

**Typ:** Kompilacja
**Języki:** Python (biblioteka standardowa, pula wątków + obsługa strumieni)
**Wymagania:** Faza 13 · 02 (Głębokie nurkowanie w wywoływanie funkcji)
**Czas:** ~75 minut

## Cele nauczania

- Wyjaśnij, dlaczego istnieje parametr `parallel_tool_calls: true` i kiedy należy go wyłączyć.
- Skoreluj strumieniowane fragmenty argumentów z odpowiednim identyfikatorem wywołania narzędzia podczas równoległego przetwarzania.
- Złóż ponownie częściowe ciągi znaków `arguments` w pełny format JSON bez przedwczesnego parsowania.
- Przeprowadź test porównawczy (benchmark) sprawdzający pogodę w trzech miastach, pokazujący różnicę w opóźnieniach między wykonaniem sekwencyjnym a równoległym.

## Problem

Bez wywołań równoległych agent odpowiadający na pytanie „jaka jest pogoda w Bengaluru, Tokio i Zurychu” działa w następujący sposób:

```
user -> LLM
LLM -> call get_weather(Bengaluru)
host -> run executor, reply with result
LLM -> call get_weather(Tokyo)
host -> run executor, reply with result
LLM -> call get_weather(Zurich)
host -> run executor, reply with result
LLM -> final text answer
```

Trzy pełne cykle komunikacji (round-trips) LLM, z których każdy obejmuje dodatkowo opóźnienie wykonawcy (executora). Łącznie daje to około 4-krotność idealnego czasu rzeczywistego (wall-clock time).

W przypadku wywołań równoległych:

```
user -> LLM
LLM -> call get_weather(Bengaluru); call get_weather(Tokyo); call get_weather(Zurich)
host -> run all three executors concurrently, reply with three results
LLM -> final text answer
```

Jeden cykl komunikacji LLM. Czas wykonania to maksimum z trzech czasów, a nie ich suma. Testy porównawcze modeli OpenAI, Anthropic i Gemini pokazują skrócenie czasu rzeczywistego o 60 do 70 procent przy obciążeniach typu fan-out (rozgałęzionych).

Ceną za to jest złożoność korelacji danych. Gdy trzy wywołania zakończą się w różnym czasie, wyniki muszą zawierać pasujący `tool_call_id`, aby model mógł je odpowiednio dopasować. Gdy wyniki są przesyłane strumieniowo, przed wykonaniem narzędzia należy złożyć częściowe fragmenty argumentów w pełny kod JSON. W Gemini dodano unikalne identyfikatory, częściowo po to, aby rozwiązać problem polegający na tym, że dwa równoległe wywołania tego samego narzędzia były nie do odróżnienia.

## Koncepcja

### Włączanie pracy równoległej

- **OpenAI.** Parametr `parallel_tool_calls: true` jest domyślnie włączony. Ustaw go na `false`, aby wymusić wywołania sekwencyjne.
- **Anthropic.** Równoległość jest kontrolowana przez `disable_parallel_tool_use: false` (domyślnie w Claude 3.5 i nowszych). Ustaw `true`, aby wymusić wywołania sekwencyjne.
- **Gemini.** Zawsze obsługuje pracę równoległą; ustawienie `tool_config.function_calling_config.mode = "AUTO"` pozwala modelowi decydować o jej użyciu.

Wyłącz funkcję równoległą, gdy narzędzia mają zależności kolejnościowe (np. `create_file`, a następnie `write_file`), gdy dane wyjściowe jednego wywołania wpływają na dane wejściowe innego, lub gdy limit zapytań (rate limiter) nie pozwala na współbieżne wywołania.

### Korelacja identyfikatora

Każde wywołanie wygenerowane przez model ma swój identyfikator `id`. Każdy wynik zwracany przez hosta musi zawierać ten sam identyfikator. Bez tego dopasowanie wyników byłoby niemożliwe.

- **OpenAI.** `tool_call_id` w każdym komunikacie z rolą `tool`.
- **Anthropic.** `tool_use_id` w każdym bloku `tool_result`.
- **Gemini.** `id` w każdym obiekcie `functionResponse` (od wersji Gemini 1.5/3; wcześniejsze wersje dopasowywały wywołania po nazwie, co nie działało poprawnie przy równoległych wywołaniach tej samej funkcji).

### Równoczesne uruchamianie wywołań

Host uruchamia wykonawcę (executora) dla każdego wywołania w osobnym wątku, korutynie lub zdalnym procesie roboczym (workerze). Najprostszy mechanizm wykorzystuje pulę wątków (thread pool); w środowiskach produkcyjnych stosuje się `asyncio` z `asyncio.gather` lub współbieżność strukturalną (structured concurrency). Kolejność wykonywania jest nieprzewidywalna – kluczem do powiązania danych jest identyfikator.

Częsty błąd: zwracanie odpowiedzi z wynikami w kolejności z listy wywołań, a nie w kolejności ich zakończenia. Zazwyczaj to działa, ponieważ model opiera się wyłącznie na `tool_call_id`, ale jeśli wynik zostanie zgubiony lub zduplikowany, wysyłanie ich niezgodnie z kolejnością zakończenia utrudnia debugowanie. Zaleca się odpowiadanie w kolejności zakończenia, podając wyraźne identyfikatory.

### Wywołania narzędzi przy przesyłaniu strumieniowaniu

Gdy model generuje odpowiedź strumieniowo, `arguments` docierają do odbiorcy w fragmentach (chunks). Trzy oddzielne strumienie fragmentów dla trzech równoległych wywołań przeplatają się w trakcie transmisji. Wymaga to posiadania osobnego akumulatora dla każdego identyfikatora.

Struktura w zależności od dostawcy:

- **OpenAI.** Każdy fragment to `choices[0].delta.tool_calls[i].function.arguments` (częściowy ciąg znaków). Fragment zawiera `index` (pozycję na liście wywołań). Agregujesz dane według indeksu, odczytujesz `id` przy jego pierwszym pojawieniu się i parsujesz JSON, gdy `finish_reason = "tool_calls"`.
- **Anthropic.** Zdarzenia strumienia zaczynają się od `message_start`, po czym następuje jedno zdarzenie `content_block_start` dla każdego bloku o typie `tool_use` (zawiera ono identyfikator, nazwę i pusty obiekt wejściowy). Zdarzenia `content_block_delta` zawierają fragmenty `input_json_delta`. Blok jest zamykany przez `content_block_stop`.
- **Gemini.** `streamFunctionCallArguments` emituje fragmenty wraz z `functionCallId`, dzięki czemu wywołania przeplatają się w czytelny sposób. Przed wprowadzeniem tej funkcji przesyłanie strumieniowe obsługiwało tylko jedno pełne wywołanie naraz.

### Częściowy JSON i pułapka zbyt wczesnego parsowania

Nie można parsować `arguments`, dopóki cała treść nie zostanie odebrana. Częściowy JSON, taki jak `{"city": "Beng`, jest niepoprawny i spowoduje błąd parsera. Bezpiecznym punktem startu jest sygnał zakończenia wywołania od dostawcy: `finish_reason = "tool_calls"` w OpenAI, `content_block_stop` w Anthropic lub zdarzenie końca strumienia w Gemini. Dopiero wtedy należy wywołać `json.loads`. Bardziej zaawansowane podejście wykorzystuje przyrostowy parser JSON (incremental JSON parser), który generuje zdarzenia w miarę budowania struktury. Przewodnik po przesyłaniu strumieniowym OpenAI zaleca to rozwiązanie w celu poprawy UX (np. wyświetlanie wskaźnika "myślenia" w czasie rzeczywistym). Zliczanie nawiasów klamrowych jako test kompletności jest zawodne (klamry wewnątrz cudzysłowów lub znaki ucieczki mogą generować fałszywe wyniki) i powinno być stosowane wyłącznie jako prosta heurystyka podczas debugowania.

### Zakończenie poza kolejnością

```
call_A: szybkie API, zwraca wynik jako pierwsze
call_B: wolne API, zwraca wynik jako drugie
call_C: średnio szybkie API, zwraca wynik jako trzecie
```

Odpowiedź hosta musi nadal zawierać identyfikatory:

```
[{role: "tool", tool_call_id: "call_A", content: ...},
 {role: "tool", tool_call_id: "call_B", content: ...},
 {role: "tool", tool_call_id: "call_C", content: ...}]
```

Kolejność odpowiedzi nie ma znaczenia dla poprawności działania w OpenAI czy Anthropic. Gemini również akceptuje dowolną kolejność, o ile identyfikatory się zgadzają.

### Test porównawczy: sekwencyjnie a równolegle

Skrypt w `code/main.py` symuluje trzy moduły wykonawcze z opóźnieniami odpowiednio 400, 600 i 800 ms. Wykonanie sekwencyjne zajmuje łącznie 1800 ms. Wykonanie równoległe trwa tyle, co najdłuższe z nich: max(400, 600, 800) = 800 ms. Różnica ta ma charakter bezwzględny, a nie proporcjonalny, więc oszczędność czasu rośnie wraz z liczbą wywoływanych narzędzi.

Uwaga praktyczna: równoległe wywołania znacznie bardziej obciążają zewnętrzne interfejsy API. Dziesięciokrotne rozgałęzienie (fan-out) do usługi z limitami zapytań zakończy się niepowodzeniem. Faza 13 · 17 opisuje mechanizmy kontroli przepływu (backpressure); obsługa ponownych prób (retry) zostanie omówiona w kolejnej fazie.

### Czas rzeczywisty przy przesyłaniu strumieniowym

Jeśli sam model przesyła dane strumieniowo, można rozpocząć wykonywanie narzędzia natychmiast po skompletowaniu argumentów dla danego wywołania, zamiast czekać na zakończenie całego strumienia. Jest to optymalizacja zalecana w dokumentacji OpenAI, choć nie wszystkie biblioteki SDK ją wspierają. Właśnie tak działa mechanizm w tej lekcji: jak tylko symulowany strumień dostarczy pełny obiekt argumentów, host uruchamai powiązane z nim wywołanie.

## Użyj tego

Plik `code/main.py` składa się z dwóch części. Pierwsza z nich uruchamia trzy symulowane wywołania pogodowe (sekwencyjnie oraz równolegle) przy użyciu `concurrent.futures.ThreadPoolExecutor` i mierzy czas rzeczywisty (wall-clock time). Druga część odtwarza symulowaną odpowiedź strumieniową – fragmenty `arguments` dla trzech równoległych wywołań są przeplatane w jednym strumieniu – i składa je z powrotem na podstawie identyfikatorów za pomocą klasy `StreamAccumulator`. Całość działa lokalnie – bez udziału LLM ani sieci.

Na co warto zwrócić uwagę:

- Wykonanie sekwencyjne zajmuje około 1,8 sekundy. Wykonanie równoległe zajmuje tylko 0,8 sekundy przy tych samych opóźnieniach.
- Akumulator poprawnie obsługuje fragmenty przychodzące w różnej kolejności, buforując dane dla każdego ID i parsując JSON dopiero po zakończeniu pobierania całego wywołania.
- Wykonanie uruchamia się natychmiast po skompletowaniu argumentów dla danego ID, bez czekania na zakończenie całego strumienia.

## Wynik wdrożenia

W ramach tej lekcji powstaje plik `outputs/skill-parallel-call-safety-check.md`. Narzędzie to analizuje rejestr narzędzi pod kątem bezpieczeństwa wykonywania równoległego: sprawdza, które narzędzia można bezpiecznie łączyć, które posiadają zależności kolejnościowe, a które mogłyby przekroczyć limity zapytań (rate limits) zewnętrznych usług. Zwraca ono zaktualizowany rejestr z flagami `parallel_safe` dla poszczególnych narzędzi.

## Ćwiczenia

1. Uruchom `code/main.py` i poeksperymentuj z opóźnieniami. Upewnij się, że stosunek czasu równoległego do sekwencyjnego wynosi w przybliżeniu `max/sum` (rzeczywiste wyniki mogą się nieznacznie różnić z powodu planowania wątków, serializacji i narzutu systemu). Przy jakim rozkładzie opóźnień równoległość przestaje przynosić korzyści?

2. Rozbuduj akumulator o obsługę przypadku, w którym „wywołanie zostało anulowane w trakcie transmisji”, usuwając jego bufor i emitując zdarzenie `cancelled`. Który dostawca jawnie dokumentuje ten przypadek? Przeanalizuj semantykę `content_block_stop` u Anthropic oraz zachowanie `finish_reason: "length"` w OpenAI.

3. Zastąp pulę wątków przez `asyncio.gather`. Porównaj oba rozwiązania. Powinieneś zauważyć niewielkie zyski wydajnościowe przy użyciu asynchroniczności dzięki mniejszemu narzutowi na przełączanie kontekstu, pod warunkiem, że wykonawcy wykonują rzeczywiste operacje wejścia/wyjścia (I/O).

4. Wybierz dwa narzędzia, które NIE powinny działać równolegle (np. `create_file` i `write_file`). Dodaj graf zależności kolejności (`ordering_dependency`) do rejestru i zabezpiecz równoległe wywoływanie na jego podstawie. Jest to uproszczony mechanizm planowania uwzględniający zależności, który zostanie sformalizowany w przyszłej fazie inżynierii agentów.

5. Przeczytaj sekcję dotyczącą równoległego wywoływania funkcji w dokumentacji OpenAI oraz informacje o `disable_parallel_tool_use` u Anthropic. Zidentyfikuj jeden rzeczywisty scenariusz, w którym Anthropic zaleca wyłączenie równoległości (Wskazówka: sekwencyjne modyfikacje tego samego zasobu).

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Równoległe wywołania narzędzi | „Wachlowanie w jednej turze” | Model emituje wiele wywołań narzędzi w jednej wiadomości asystenta |
| `parallel_tool_calls` | „Flaga OpenAI” | Włącza lub wyłącza generowanie wielu wywołań równolegle |
| `disable_parallel_tool_use` | „Odwrotność u Anthropic” | Flaga wyłączająca; domyślnie wywołania równoległe są włączone |
| Identyfikator wywołania narzędzia | „Klucz korelacji” | Identyfikator wywołania, który musi zostać powtórzony w komunikacie z wynikiem |
| Akumulator | „Bufor strumienia” | Bufor tekstowy przypisany do ID, gromadzący częściowe fragmenty `arguments` |
| Zakończenie poza kolejnością | „Najpierw najszybszy” | Wywołania równoległe kończą się w nieprzewidywalnej kolejności; identyfikatory służą jako spoiwo |
| Wykres zależności | „Ograniczenia kolejności” | Narzędzia, których wyniki stanowią dane wejściowe dla innych narzędzi; nie mogą być uruchamiane równolegle |
| Analiza-wczesna pułapka | „Błąd parsowania JSON” | Próba sparsowania niekompletnego ciągu znaków `arguments` |
| `streamFunctionCallArguments` | „Funkcja Gemini 3” | Strumieniowanie fragmentów argumentów wraz z unikalnym identyfikatorem dla każdego wywołania |
| Odpowiedź na zamówienie | „Nie czekaj na wszystkich” | Zwracanie wyników w miarę ich pojawiania się, oznaczonych odpowiednim identyfikatorem |

## Dalsze czytanie

- [OpenAI — Równoległe wywoływanie funkcji](https://platform.openai.com/docs/guides/function-calling#parallel-function-calling) — domyślne zachowanie i flaga rezygnacji
- [Anthropic — Użycie narzędzia: wdrożenie użycia narzędzia](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implementing-tool-use) — `disable_parallel_tool_use` i grupowanie wyników
- [Google — funkcja Gemini wywołująca sekcję równoległą](https://ai.google.dev/gemini-api/docs/function-calling) — równoległe wywołania skorelowane z identyfikatorem z Gemini 3
- [OpenAI — Odpowiedzi strumieniowe z narzędziami](https://platform.openai.com/docs/api-reference/responses-streaming) — ponowne składanie argumentów fragmentarycznych dla strumieni OpenAI
- [Anthropic — wiadomości przesyłane strumieniowo](https://docs.anthropic.com/en/api/messages-streaming) — `content_block_delta` z `input_json_delta`
