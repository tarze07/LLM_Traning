# Samodoskonalenie i KRYTYK: Iteracyjna poprawa wyników

> Self-Refine (Madaan i in., 2023) wykorzystuje jeden LLM w trzech rolach — generowanie, przesyłanie informacji zwrotnej, udoskonalanie — w pętli. Średni zysk: +20 bezwzględnie na 7 zadaniach. KRYTYK (Gou i in., 2023) wzmacnia etap przekazywania informacji zwrotnej, kierując weryfikację za pośrednictwem narzędzi zewnętrznych. W roku 2026 ten wzorzec będzie dostępny w każdym środowisku jako „optymalizator oceniający” (Anthropic) lub pętla poręczy (SDK OpenAI Agents).

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (Pętla agenta), Faza 14 · 03 (Odbicie)
**Czas:** ~60 minut

## Cele nauczania

- Podaj trzy podpowiedzi narzędzia Samodoskonalenie (generuj, przesyłaj informacje zwrotne, udoskonalaj) i wyjaśniaj, dlaczego historia ma znaczenie dla podpowiedzi udoskonalania.
- Wyjaśnij krytyczne spostrzeżenie KRYTYKA: LLM są zawodne w przypadku samoweryfikacji bez zewnętrznego uziemienia.
- Zaimplementuj pętlę stdlib Self-Refine z historią i opcjonalnym zewnętrznym weryfikatorem.
— Zamapuj ten wzorzec na przepływ pracy „optymalizatora oceny” firmy Anthropic i bariery wyjściowe pakietu OpenAI Agents SDK.

## Problem

Agent daje odpowiedź, która jest prawie prawidłowa. Być może w wierszu kodu występuje błąd składniowy. Być może podsumowanie jest za długie. Może plan pomija przypadek Edge. To, czego chcesz, to: agent krytykuje własne wyniki, a następnie je poprawia.

Funkcja Self-Refine pokazuje, że działa to w przypadku pojedynczego modelu, bez danych treningowych i bez RL. Jest jednak pewien haczyk: menedżerowie LLM słabo radzą sobie z samoweryfikacją twardych faktów. KRYTYK nazywa poprawkę — kieruj krok weryfikacji przez narzędzia zewnętrzne (wyszukiwanie, interpreter kodu, kalkulator, uruchamiający test).

Razem te dwa artykuły definiują domyślne podejście do iteracyjnego doskonalenia na rok 2026: generuj, weryfikuj (zewnętrznie, jeśli to możliwe), udoskonalaj, zatrzymuj, gdy weryfikator przejdzie pomyślnie.

## Koncepcja

### Samodoskonalenie (Madaan i in., NeurIPS 2023)

Jeden LLM, trzy role:

```
generate(task)            -> output_0
feedback(task, output_0)  -> critique_0
refine(task, output_0, critique_0, history) -> output_1
feedback(task, output_1)  -> critique_1
refine(task, output_1, critique_1, history) -> output_2
...
stop when feedback says "no issues" or budget exhausted.
```

Kluczowy szczegół: `refine` widzi pełną historię — wszystkie wcześniejsze wyniki i uwagi krytyczne — więc nie powtarza błędów. Artykuł to obala: historia spadku, a jakość gwałtownie spada.

Nagłówek: +20 bezwzględnej poprawy uśrednionej dla 7 zadań (matematyka, kod, akronim, okno dialogowe), w tym GPT-4. Bez szkoleń, bez zewnętrznych narzędzi, jeden model.

### KRYTYK (Gou i in., arXiv:2305.11738, wersja 4 lutego 2024 r.)

Słabość Self-doskonalenia: etap informacji zwrotnej sam w sobie jest punktacją LLM. W przypadku twierdzeń opartych na faktach jest to niewiarygodne (halucynacje często wydają się przekonujące dla modelu, który je wytworzył). CRITIC zastępuje `feedback(task, output)` przez `verify(task, output, tools)`, gdzie `tools` zawiera:

- Wyszukiwarka roszczeń faktycznych.
- Interpreter kodu sprawdzający poprawność kodu.
- Kalkulator arytmetyczny.
- Weryfikatory specyficzne dla domeny (testy jednostkowe, sprawdzanie typów, linters).

Weryfikator tworzy ustrukturyzowaną krytykę opartą na wynikach narzędzi. Rafineria następnie uzależnia się od tej krytyki.

Nagłówek: KRYTYK ma lepsze wyniki niż Samodoskonalenie w przypadku zadań opartych na faktach, ponieważ krytyka jest oparta na podstawach. W przypadku zadań bez zewnętrznych weryfikatorów (kreatywne pisanie, formatowanie) KRYTYK ogranicza się do Samodoskonalenia.

### Warunek zatrzymania

Dwa popularne kształty:

1. **Weryfikator przechodzi pomyślnie.** Test zewnętrzny zakończył się sukcesem. Preferowane, jeśli są dostępne (testy jednostkowe, sprawdzanie typu, potwierdzanie poręczy).
2. **Nie wydano opinii.** Model twierdzi, że „wyjście jest w porządku”. Tańsze, ale zawodne; sparuj z limitem maksymalnej iteracji.

Wartość domyślna 2026: połącz je. „Zatrzymaj, jeśli weryfikator przejdzie pomyślnie LUB model powie dobrze ORAZ iteracje >= 2 LUB iteracje >= max_iterations.”

### Optymalizator-ewaluator (Anthropic, 2024)

W poście Anthropic z grudnia 2024 r. wymieniono to jako jeden z pięciu wzorców przepływu pracy. Dwie role:

- Oceniający: ocenia wyniki i formułuje krytykę.
- Optymalizator: koryguje dane wyjściowe biorąc pod uwagę krytykę.

Zapętlaj, aż osoba oceniająca przejdzie. To samodoskonalenie/KRYTYK w ujęciu Anthropic. Anthropic dodaje kluczowy szczegół inżynieryjny: komunikaty oceniające i optymalizujące powinny zasadniczo się różnić, aby model nie był jedynie pieczątką.

### Poręcze wyjściowe SDK agentów OpenAI

Pakiet SDK OpenAI Agents dostarcza ten wzorzec jako „poręcze wyjściowe”. Poręcz ochronna to moduł sprawdzający, który działa na końcowych danych wyjściowych agenta. Jeśli barierka zadziała (podniesie `OutputGuardrailTripwireTriggered`), dane wyjściowe zostaną odrzucone i agent będzie mógł ponowić próbę. Poręcze mogą wywoływać narzędzia (w stylu KRYTYKA) lub być czystymi funkcjami (w stylu Samodoskonalenia).

### Pułapki 2026

- **Pętle z pieczątkami.** Ten sam model generowania i krytykowania, z tym samym szybkim stylem, zbiega się w kwestii „wygląda dobrze”. Do krytyki użyj strukturalnie różnych podpowiedzi lub mniejszego, taniego modelu.
- **Nadmierne udoskonalenie.** Każde udoskonalenie zwiększa opóźnienia i tokeny. Budżet 1-3 karnety; następnie przejdź do weryfikacji ręcznej.
- **KRYTYK przy trywialnych zadaniach.** Jeśli nie ma zewnętrznego weryfikatora, KRYTYK przechodzi w Samodoskonalenie; nie płać za opóźnienie dla weryfikatora pośredniczącego.

## Zbuduj to

`code/main.py` implementuje funkcję Samodoskonalenia i KRYTYKA w przypadku zadania zabawkowego: utwórz krótką listę punktowaną dla danego tematu. Weryfikator sprawdza format (3 punktory, każdy poniżej 60 znaków). KRYTYK dodaje zewnętrzny „weryfikator faktów”, który karze znane halucynacje.

Komponenty:

- `generate` — producent scenariusza.
- `feedback` — samokrytyka w stylu LLM.
- `verify_external` — ugruntowany weryfikator w stylu KRYTYKA.
- `refine` — przepisuje dane wyjściowe z podanej historii.
- Warunek zatrzymania – weryfikator przechodzi pomyślnie lub maksymalnie 4 iteracje.

Uruchom to:

```
python3 code/main.py
```

Porównaj przebiegi Self-Refine i CRITIC. KRYTYK wychwytuje błąd rzeczowy. Samodoskonalenie pominęło, ponieważ zewnętrzny weryfikator ma podstawy, których samokrytyk nie ma.

## Użyj tego

Optymalizatorem oceniającym firmy Anthropic jest ten wzorzec napisany w języku przyjaznym dla Claude'a. Poręcze wyjściowe pakietu SDK agentów OpenAI mają kształt KRYTYCZNY (poręcze mogą wywoływać narzędzia). LangGraph dostarcza węzeł refleksji, który brzmi jak Self-Refine. Google Gemini 2.5 Computer Use dodaje narzędzie do oceny bezpieczeństwa poszczególnych kroków, które jest wariantem KRYTYCZNYM: każde działanie jest weryfikowane przed zatwierdzeniem.

## Wyślij to

`outputs/skill-refine-loop.md` konfiguruje pętlę ewaluatora-optymalizatora, biorąc pod uwagę kształt zadania, dostępność weryfikatora i budżet iteracji. Emituje monity dotyczące generatora, oceniającego/weryfikatora i optymalizatora, a także zasady zatrzymania.

## Ćwiczenia

1. Uruchom zabawkę z max_iterations=1. Czy CRITIC nadal pomaga?
2. Wymień weryfikator zewnętrzny na zaszumiony (losowo 30% wyników fałszywie pozytywnych). Co robi pętla? Taka jest rzeczywistość większości stosów poręczy w roku 2026.
3. Zaimplementuj wariant „krytyki generatora w różnych modelach”: duży model generuje, mały model krytykuje. Czy przebija ten sam model?
4. Przeczytaj sekcję 3 KRYTYKA (arXiv:2305.11738 v4). Nazwij trzy kategorie narzędzi do weryfikacji i podaj przykład dla każdej z nich.
5. Przypisz `output_guardrails` pakiet SDK OpenAI Agents SDK do roli weryfikatora CRITIC. Co SDK robi źle, a co dobrze?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Samodoskonalenie | „LLM, który sam się naprawia” | Generuj -> informacje zwrotne -> udoskonal pętlę w jednym modelu z historią |
| KRYTYK | „Weryfikacja oparta na narzędziach” | Zastąp informację zwrotną zewnętrznym weryfikatorem (wyszukiwanie, kodowanie, obliczanie, testy) |
| Ewaluator-Optymalizator | „Antropiczny wzorzec przepływu pracy” | Dwie role — oceniający oceniający, optymalizujący weryfikuje — zapętlony do zbieżności |
| Poręcz wyjściowa | „Kontrola post-hoc” | Walidator zestawu SDK agentów OpenAI uruchamiany po wygenerowaniu danych wyjściowych przez agenta |
| Sprawdź krok | „Faza krytyki” | Decyzja nośna: uziemiona lub samoocena |
| Udoskonal historię | „Co model już wypróbował” | Wcześniejsze wyniki + krytyka dodana w celu udoskonalenia podpowiedzi; spadek i załamanie jakości |
| Pętla na pieczątkę | „Niepowodzenie samoporozumienia” | Ta sama szybka krytyka zwraca „wygląda dobrze”; naprawić za pomocą strukturalnie różnych podpowiedzi |
| Warunek zatrzymania | „Test konwergencji” | Weryfikator przechodzi LUB nie otrzymuje informacji zwrotnej ORAZ limit iteracji; nigdy pojedynczy warunek |

## Dalsze czytanie

- [Madaan i in., Self-Refine (arXiv:2303.17651)](https://arxiv.org/abs/2303.17651) — artykuł kanoniczny
- [Gou i in., CRITIC (arXiv:2305.11738)](https://arxiv.org/abs/2305.11738) — weryfikacja oparta na narzędziach
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-efektywne-agents) — wzorzec przepływu pracy narzędzia oceniającego-optymalizatora
- [Dokumentacja pakietu SDK OpenAI Agents](https://openai.github.io/openai-agents-python/) — wyjściowe poręcze ochronne jako weryfikatory w kształcie KRYTYKA