# Równoległe wywołania narzędzi i przesyłanie strumieniowe za pomocą narzędzi

> Trzy niezależne wyszukiwania pogody w odcinkach to trzy podróże w obie strony. Uruchom je równolegle, a całkowity czas spadnie do najwolniejszego pojedynczego połączenia. Każdy dostawca pograniczny emituje teraz wiele wywołań narzędzi w jednej turze. Wypłata jest realna; instalacja wodno-kanalizacyjna jest subtelna. Ta lekcja dotyczy obu połówek: równoległego rozwinięcia i ponownego złożenia argumentów strumieniowych, z naciskiem na pułapkę korelacji id.

**Typ:** Kompilacja
**Języki:** Python (stdlib, pula wątków + wiązka strumieniowa)
**Wymagania:** Faza 13 · 02 (funkcja wywołująca głębokie nurkowanie)
**Czas:** ~75 minut

## Cele nauczania

- Wyjaśnij, dlaczego `parallel_tool_calls: true` istnieje i kiedy należy go wyłączyć.
- Koreluj przesyłane strumieniowo fragmenty argumentów z odpowiednim identyfikatorem wywołania narzędzia podczas równoległego rozwinięcia.
- Złóż ponownie częściowe ciągi `arguments` w pełny kod JSON bez wcześniejszego analizowania.
- Przeprowadź test porównawczy pogody w trzech miastach, który pokazuje opóźnienie sekwencyjne i równoległe.

## Problem

Bez równoległych połączeń agent odpowiadający na pytanie „jaka jest pogoda w Bengaluru, Tokio i Zurychu” robi to:

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

Trzy podróże w obie strony LLM, z których każda pokrywa również opóźnienie wykonawcy. Mniej więcej 4-krotność idealnego czasu zegara ściennego.

W przypadku połączeń równoległych:

```
user -> LLM
LLM -> call get_weather(Bengaluru); call get_weather(Tokyo); call get_weather(Zurich)
host -> run all three executors concurrently, reply with three results
LLM -> final text answer
```

Jedna podróż w obie strony LLM. Czas wykonawcy to maksimum z trzech, a nie suma. Testy porównawcze programów OpenAI, Anthropic i Gemini pokazują redukcję zegara ściennego o 60 do 70 procent przy obciążeniach typu fan-out.

Ceną jest złożoność korelacji. Gdy trzy wywołania zostaną ukończone niewłaściwie, wyniki muszą zawierać pasujący `tool_call_id`, aby model mógł je dopasować. Gdy wyniki są przesyłane strumieniowo, przed wykonaniem należy złożyć częściowe fragmenty argumentów w pełny kod JSON. W Gemini 3 dodano unikalne identyfikatory, częściowo po to, aby rozwiązać rzeczywisty problem polegający na tym, że dwa równoległe wywołania tego samego narzędzia były nie do odróżnienia.

## Koncepcja

### Włączanie pracy równoległej

- **OpenAI.** `parallel_tool_calls: true` domyślnie włączone. Ustaw `false`, aby wymusić połączenie szeregowe.
- **Anthropic.** Równoległe przez `disable_parallel_tool_use: false` (domyślnie w Claude 3.5 i nowszych). Ustaw `true` dla numeru seryjnego.
- **Gemini.** Zawsze możliwość pracy równoległej; `tool_config.function_calling_config.mode = "AUTO"` pozwala decydować modelowi.

Wyłącz funkcję równoległą, gdy narzędzia mają zależności w zakresie porządkowania (`create_file`, a następnie `write_file`), gdy dane wyjściowe jednego wywołania informują o danych wejściowych innego lub gdy ogranicznik szybkości nie obsługuje rozgałęziania.

### Korelacja identyfikatora

Każde wywołanie emitowane przez model ma `id`. Każdy wynik zwracany przez hosta musi zawierać ten sam identyfikator. Bez tego wyniki są niejednoznaczne.

- **OpenAI.** `tool_call_id` w każdym komunikacie dotyczącym roli narzędzia.
- **Anthropic.** `tool_use_id` w każdym bloku `tool_result`.
- **Gemini.** `id` na każdym `functionResponse` (Gemini 3 i nowsze; Gemini 2 dopasowane według nazwy, która zepsuła się w przypadku połączeń równoległych o tej samej nazwie).

### Równoczesne uruchamianie połączeń

Host uruchamia moduł wykonujący każde wywołanie w swoim własnym wątku, współprogramie lub zdalnym procesie roboczym. Najprostsza uprząż wykorzystuje pulę wątków; produkcja wykorzystuje asyncio z `asyncio.gather` lub współbieżność strukturalną. Kolejność realizacji jest nieprzewidywalna – identyfikatorem jest identyfikator.

Jeden częsty błąd: odpowiedź z wynikami w kolejności listy połączeń, a nie kolejności zakończenia. Zwykle działa to, ponieważ model interesuje się tylko `tool_call_id`, ale jeśli wynik zostanie porzucony lub zduplikowany, przesłanie poza kolejnością utrudnia debugowanie. Wolę odpowiadać w kolejności zakończenia, podając wyraźne identyfikatory.

### Wywołania narzędzi do przesyłania strumieniowego

Gdy model jest przesyłany strumieniowo, `arguments` dociera do odbiorców w kawałkach. Trzy oddzielne strumienie fragmentów dla trzech równoległych połączeń przeplatają się na przewodzie. Potrzebujesz jednego akumulatora na każdy identyfikator.

Kształt według dostawcy:

- **OpenAI.** Każdy fragment to `choices[0].delta.tool_calls[i].function.arguments` (częściowy ciąg znaków). Kawałek zawiera `index` (pozycja na liście połączeń). Gromadzisz według indeksu, czytasz `id`, gdy pojawia się on po raz pierwszy i analizujesz JSON, gdy `finish_reason = "tool_calls"`.
- **Anthropic.** Zdarzenia strumienia to `message_start`, następnie jedno `content_block_start` na blok o typie `tool_use` (zawiera identyfikator, nazwę i puste dane wejściowe). Zdarzenia `content_block_delta` zawierają `input_json_delta` fragmenty. `content_block_stop` zamyka każdy blok.
- **Gemini.** `streamFunctionCallArguments` (Gemini 3 i nowsze) emituje fragmenty z `functionCallId`, więc wywołania przeplatają się czysto. Przed Gemini 3 przesyłanie strumieniowe zapewniało jedno pełne połączenie na raz.

### Częściowy JSON i wczesna pułapka analizy

Nie możesz analizować `arguments`, dopóki nie zostanie ukończony. Częściowy kod JSON, taki jak `{"city": "Beng`, jest nieprawidłowy i spowoduje wzrost. Prawidłową bramką jest sygnał zakończenia połączenia dostawcy: `finish_reason = "tool_calls"` OpenAI, `content_block_stop` firmy Anthropic lub zdarzenie końca strumienia firmy Gemini. Dopiero wtedy spróbuj `json.loads`. Bardziej niezawodne podejście wykorzystuje przyrostowy analizator składni JSON, który generuje zdarzenia w miarę ukończenia struktury; Przewodnik po transmisji strumieniowej OpenAI zaleca tę opcję dla UX, która pokazuje wskaźnik „myślenia” na żywo. Liczenie nawiasów jest zawodne jako test kompletności (nawiasy klamrowe w cudzysłowie lub treść, w której występuje ucieczka, powodują fałszywe alarmy) i powinno być używane wyłącznie jako nieformalna heurystyka debugowania.

### Zakończenie poza kolejnością

```
call_A: fast API, returns first
call_B: slow API, returns second
call_C: median API, returns third
```

Odpowiedź gospodarza musi nadal zawierać identyfikatory:

```
[{role: "tool", tool_call_id: "call_A", content: ...},
 {role: "tool", tool_call_id: "call_B", content: ...},
 {role: "tool", tool_call_id: "call_C", content: ...}]
```

Kolejność odpowiedzi nie ma znaczenia dla poprawności w OpenAI lub Anthropic. Gemini przyjmuje każde zamówienie pod warunkiem, że identyfikatory się zgadzają.

### Test porównawczy: sekwencyjny a równoległy

Uprząż w `code/main.py` symuluje trzy moduły wykonujące z opóźnieniem 400, 600 i 800 ms. Sekwencyjne uruchamia go w sumie w 1800 ms. Równolegle uruchamia się w max (400, 600, 800) = 800 ms. Różnica jest stała, a nie proporcjonalna, więc oszczędności rosną wraz z liczbą narzędzi.

Zastrzeżenie dotyczące świata rzeczywistego: wywołania równoległe obciążają dalsze interfejsy API. 10-kierunkowe rozwinięcie usługi o ograniczonej stawce zakończy się niepowodzeniem. Faza 13 · 17 obejmuje przeciwciśnienie na poziomie bramki; Semantyka ponownych prób jest planowana na przyszłą fazę.

### Zegar ścienny z funkcją strumieniowego przesyłania strumieniowego

Jeśli sam model jest przesyłany strumieniowo, możesz rozpocząć wykonywanie natychmiast po skompletowaniu argumentów jednego wywołania, zamiast czekać na sfinalizowanie wszystkich wywołań. Jest to optymalizacja dokumentów OpenAI, ale nie wszystkie pakiety SDK udostępniają. Tak działa uprząż przedstawiona w tej lekcji: gdy tylko symulowany strumień dostarczy kompletny obiekt argumentu, host rozpoczyna to wywołanie.

## Użyj tego

`code/main.py` ma dwie połowy. Pierwsza uruchamia trzy symulowane wywołania pogodowe, sekwencyjnie i równolegle, używając `concurrent.futures.ThreadPoolExecutor` i wypisuje czas zegara ściennego. Druga połowa odtwarza fałszywą odpowiedź strumieniową — fragmenty `arguments` dla trzech równoległych wywołań przeplatanych w jednym strumieniu — i ponownie składa je według identyfikatora za pomocą `StreamAccumulator`. Żadnego LLM, żadnej sieci, tylko logika ponownego montażu.

Na co zwrócić uwagę:

- Minutnik sekwencyjny osiąga 1,8 sekundy. Zegar równoległy osiąga 0,8 sekundy przy tych samych fałszywych opóźnieniach.
- Akumulator obsługuje fragmenty przybywające w niewłaściwej kolejności, buforując identyfikator i analizując je tylko po zakończeniu każdego wywołania JSON.
- Wykonanie rozpoczyna się natychmiast po sfinalizowaniu argumentów identyfikatora, a nie po zakończeniu wszystkich strumieni.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-parallel-call-safety-check.md`. Biorąc pod uwagę rejestr narzędzi, przeprowadzane są audyty umiejętności, które narzędzia można bezpiecznie łączyć równolegle, które mają zależności w kolejności i które przerosłyby limity szybkości na dalszym etapie — zwracając poprawiony rejestr z flagami `parallel_safe` dla poszczególnych narzędzi.

## Ćwiczenia

1. Uruchom `code/main.py` i różnicuj symulowane opóźnienia. Upewnij się, że stosunek równoległości do sekwencji wynosi w przybliżeniu `max/sum` (rzeczywiste przebiegi nieznacznie odbiegają od ideału ze względu na planowanie wątków, serializację i obciążenie wiązki). Przy jakim rozkładzie opóźnień równoległość przestaje mieć znaczenie?

2. Rozszerz akumulator, aby obsługiwał przypadek „połączenie zostało anulowane w trakcie transmisji”, usuwając jego bufor i emitując zdarzenie `cancelled`. Który dostawca wyraźnie dokumentuje ten przypadek? Sprawdź semantykę `content_block_stop` Anthropic i zachowanie `finish_reason: "length"` OpenAI.

3. Zamień pulę wątków na `asyncio.gather`. Porównaj oba. Powinieneś zobaczyć małe wygrane w przypadku asynchronizacji ze względu na niższy koszt przełączania kontekstu, ale tylko wtedy, gdy wykonawcy wykonują prawdziwe operacje we/wy.

4. Wybierz dwa narzędzia, które NIE powinny działać równolegle (np. `create_file`, a następnie `write_file`). Dodaj wykres `ordering_dependency` do rejestru i bramkuj równoległe rozwinięcie na tym wykresie. Jest to minimalny mechanizm planowania uwzględniającego zależności, który formalizuje przyszła faza inżynierii agentów.

5. Przeczytaj sekcję OpenAI dotyczącą wywoływania funkcji równoległych i dokumentację `disable_parallel_tool_use` firmy Anthropic. Zidentyfikuj jeden typ narzędzia ze świata rzeczywistego, w przypadku którego Anthropic zaleca wyłączenie równoległości. (Wskazówka: mutacje następcze w tym samym zasobie.)

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Równoległe wywołania narzędzi | „Wachlowanie w jednej turze” | Model emituje wiele wywołań narzędzi w jednej wiadomości asystenta |
| `parallel_tool_calls` | „Flaga OpenAI” | Włącz lub wyłącz emisję wielu połączeń |
| `disable_parallel_tool_use` | „Odwrotność antropiczna” | Flaga rezygnacji; domyślnie włączone jest połączenie równoległe |
| Identyfikator wywołania narzędzia | „Uchwyt korelacji” | Identyfikator połączenia, w którym komunikat wynikowy musi zawierać echo |
| Akumulator | „Bufor strumieniowy” | Bufor ciągu znaków dla identyfikatora dla częściowych `arguments` fragmentów |
| Zakończenie poza kolejnością | „Najpierw najszybszy” | Połączenia równoległe kończą się w nieprzewidywalnej kolejności; identyfikatory są klejem |
| Wykres zależności | „Ograniczenia porządkowe” | Narzędzia, których wyniki stanowią wkład w dane wejściowe innych narzędzi; nie można zrównoleglić |
| Analiza-wczesna pułapka | „JSON.parse eksplodował” | Próba przeanalizowania niekompletnego ciągu znaków `arguments` |
| `streamFunctionCallArguments` | „Funkcja Gemini 3” | Przesyłane strumieniowo fragmenty argumentów z unikalnym identyfikatorem na wywołanie |
| Odpowiedź na zamówienie | „Nie czekaj na wszystkich” | Odpowiadaj, podając wyniki, gdy tylko się pojawią, oznaczone identyfikatorem |

## Dalsze czytanie

- [OpenAI — Równoległe wywoływanie funkcji](https://platform.openai.com/docs/guides/function-calling#parallel-function-calling) — domyślne zachowanie i flaga rezygnacji
- [Anthropic — Użycie narzędzia: wdrożenie użycia narzędzia](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implementing-tool-use) — `disable_parallel_tool_use` i grupowanie wyników
- [Google — funkcja Gemini wywołująca sekcję równoległą](https://ai.google.dev/gemini-api/docs/function-calling) — równoległe wywołania skorelowane z identyfikatorem z Gemini 3
- [OpenAI — Odpowiedzi strumieniowe z narzędziami](https://platform.openai.com/docs/api-reference/responses-streaming) — ponowne składanie argumentów fragmentarycznych dla strumieni OpenAI
- [Anthropic — wiadomości przesyłane strumieniowo](https://docs.anthropic.com/en/api/messages-streaming) — `content_block_delta` z `input_json_delta`