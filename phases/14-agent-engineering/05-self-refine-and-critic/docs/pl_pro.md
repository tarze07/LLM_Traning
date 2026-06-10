# Samodoskonalenie (Self-Refine) i KRYTYK (CRITIC): Iteracyjna poprawa wyników

> Metoda Self-Refine (Madaan i in., 2023) wykorzystuje pojedynczy model LLM w trzech rolach działających w pętli: generowanie, ocena (feedback) oraz poprawianie (refine). Średni przyrost skuteczności to ponad 20 punktów procentowych w 7 zróżnicowanych zadaniach. Z kolei CRITIC (Gou i in., 2023) wzmacnia etap oceny, opierając weryfikację na zewnętrznych narzędziach. W 2026 roku wzorzec ten jest powszechnie stosowany pod nazwą „Evaluator-Optimizer” (Anthropic) lub jako pętla walidacyjna (Output Guardrails w SDK OpenAI Agents).

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (Pętla agenta), Faza 14 · 03 (Odbicie)
**Czas:** ~60 minut

## Cele nauczania

- Wskaż trzy typy promptów w metodzie Self-Refine (generowanie, ocena, poprawianie) i wyjaśnij, dlaczego historia interakcji ma kluczowe znaczenie dla promptu poprawiającego.
- Wyjaśnij kluczowe spostrzeżenie autorów metody CRITIC: modele LLM są mało wiarygodne w samoweryfikacji bez oparcia o zewnętrzne źródła wiedzy.
- Zaimplementuj pętlę Self-Refine przy użyciu wyłącznie biblioteki standardowej (stdlib), uwzględniając historię operacji oraz opcjonalny zewnętrzny weryfikator.
- Przeanalizuj mapowanie tego wzorca na przepływ pracy „Evaluator-Optimizer” (Anthropic) oraz mechanizmy Output Guardrails w pakiecie SDK OpenAI Agents.

## Problem

Agent generuje odpowiedź, która jest niemal poprawna. Być może w kodzie znajduje się drobny błąd składniowy, podsumowanie minimalnie przekracza limit znaków lub wypracowany plan pomija przypadek brzegowy (edge case). W takich sytuacjach pożądanym zachowaniem jest, aby agent krytycznie ocenił swój własny wynik, a następnie go poprawił.

Metoda Self-Refine dowodzi, że proces ten może zachodzić w ramach jednego modelu, bez dodatkowych danych treningowych czy uczenia ze wzmocnieniem (RL). Istnieje jednak istotne ograniczenie: modele LLM słabo radzą sobie z samoweryfikacją faktów. Rozwiązaniem tego problemu jest podejście CRITIC, które przekazuje etap weryfikacji do zewnętrznych narzędzi (np. wyszukiwarki internetowej, interpretera kodu, kalkulatora lub środowiska testowego).

Obie te koncepcje definiują standardowe podejście do iteracyjnej poprawy wyników: wygeneruj, zweryfikuj (o ile to możliwe przy użyciu zewnętrznych narzędzi), popraw i zakończ proces, gdy weryfikator potwierdzi poprawność.

## Koncepcja

### Samodoskonalenie (Madaan i in., NeurIPS 2023)

Pojedynczy model LLM, three role:

```
generate(task)            -> output_0
feedback(task, output_0)  -> critique_0
refine(task, output_0, critique_0, history) -> output_1
feedback(task, output_1)  -> critique_1
refine(task, output_1, critique_1, history) -> output_2
...
stop when feedback says "no issues" or budget exhausted.
```

Kluczowy szczegół: krok poprawiania (`refine`) ma dostęp do pełnej historii – wszystkich wcześniejszych wyników oraz uwag krytycznych – dzięki czemu model nie powiela tych samych błędów. Autorzy publikacji wykazali, że pominięcie historii w prompcie poprawiającym skutkuje gwałtownym spadkiem jakości wyników.

Kluczowy wynik: Ponad 20% bezwzględnej poprawy wyników średnio w 7 zadaniach (matematyka, programowanie, akronimy, dialogi) z wykorzystaniem m.in. GPT-4. Bez konieczności dotrenowywania modeli i bez narzędzi zewnętrznych – przy użyciu jednego modelu.

### KRYTYK (Gou i in., arXiv:2305.11738, wersja 4 lutego 2024 r.)

Słabość Self-Refine: Etap oceny (feedback) opiera się wyłącznie na wnioskowaniu modelu LLM. W przypadku faktów jest to zawodne podejście (halucynacje często wydają się spójne i poprawne dla modelu, który je wygenerował). CRITIC zastępuje krok `feedback(task, output)` operacją `verify(task, output, tools)`, w której narzędzia (`tools`) obejmują:

- Wyszukiwarkę internetową do weryfikacji faktów.
- Interpreter kodu do uruchamiania i sprawdzania programów.
- Kalkulator do weryfikacji obliczeń.
- Narzędzia specyficzne dla danej domeny (testy jednostkowe, weryfikacja typów, lintery).

Weryfikator (Evaluator) generuje ustrukturyzowaną krytykę na podstawie rzeczywistych wyników działania narzędzi. Moduł poprawiający (Optimizer) koryguje następnie wynik w oparciu o te informacje.

Kluczowy wynik: CRITIC osiąga znacznie lepsze rezultaty niż Self-Refine w zadaniach wymagających zgodności z faktami, ponieważ krytyka opiera się na rzeczywistych danych. W zadaniach, w których brak zewnętrznych weryfikatorów (np. pisanie kreatywne, formatowanie), CRITIC zachowuje się tożsamo z Self-Refine.

### Warunek zatrzymania

Dwa popularne kształty:

1. **Pomyślny wynik weryfikacji**: Testy zewnętrzne kończą się powodzeniem. Jest to zalecana metoda, jeśli dysponujemy odpowiednimi narzędziami (np. testy jednostkowe, lintery, walidatory guardrails).
2. **Brak uwag krytycznych**: Model oceniający uznaje, że wynik jest poprawny. Tańsza, ale mniej pewna metoda; wymaga ograniczenia maksymalnej liczby iteracji.

Standardowa konfiguracja: Metoda hybrydowa. „Przerwij, jeśli weryfikator zewnętrzny potwierdzi poprawność LUB model nie zgłosi uwag ORAZ liczba iteracji >= 2 LUB osiągnięto limit max_iterations.”

### Optymalizator-ewaluator (Anthropic, 2024)

W oficjalnych rekomendacjach Anthropic z grudnia 2024 roku wzorzec ten został zakwalifikowany jako jeden z pięciu podstawowych przepływów pracy. Występują w nim dwie role:

- **Oceniający (Evaluator)**: analizuje wynik i przygotowuje uwagi krytyczne.
- **Optymalizator (Optimizer)**: modyfikuje wynik w oparciu o otrzymane uwagi.

Pętla trwa, dopóki oceniający nie zatwierdzi wyniku. To praktyczna interpretacja Self-Refine/CRITIC według Anthropic. Firma ta zwraca uwagę na kluczowy aspekt inżynieryjny: prompty dla oceniającego i optymalizatora powinny mieć znacząco różną strukturę i styl, aby zapobiec mechanicznemu akceptowaniu błędów przez model.

### Poręcze wyjściowe SDK agentów OpenAI

Pakiet SDK OpenAI Agents wdraża ten wzorzec pod nazwą „Output Guardrails” (poręcze wyjściowe). Jest to moduł walidacyjny uruchamiany na końcowym rezultacie pracy agenta. Jeśli walidacja nie powiedzie się (zostanie zgłoszony wyjątek `OutputGuardrailTripwireTriggered`), wynik jest odrzucany, a agent podejmuje ponowną próbę. Poręcze mogą wchodzić w interakcję z narzędziami (jak w CRITIC) lub opierać się na prostych regułach i ocenach LLM (jak w Self-Refine).

### Pułapki 2026

- **Pętle wzajemnej akceptacji (pieczątki)**: Użycie tego samego modelu do generowania i krytyki przy podobnej strukturze promptów prowadzi do szybkiego uznawania błędnych odpowiedzi za poprawne. Rozwiązanie: używaj znacząco odmiennych promptów do oceny lub zaangażuj do tego celu mniejszy, tańszy model.
- **Zbyt duża liczba poprawek (nadmierne udoskonalanie)**: Każda kolejna iteracja zwiększa czas odpowiedzi oraz zużycie tokenów. Ogranicz proces do 1–3 poprawek, a w razie braku zbieżności przekaż zadanie do weryfikacji człowiekowi.
- **Używanie CRITIC do prostych zadań**: Jeśli dla danego zadania nie istnieje zewnętrzny weryfikator, CRITIC zachowuje się dokładnie tak jak Self-Refine. W takich przypadkach nie warto generować dodatkowych opóźnień na wywoływanie pośredniczących modułów.

## Zbuduj to

Plik `code/main.py` implementuje podejścia Self-Refine oraz CRITIC na przykładzie prostego zadania polegającego na utworzeniu krótkiej listy punktowanej na wybrany temat. Walidator weryfikuje format (dokładnie 3 punkty, z których każdy musi mieć poniżej 60 znaków). CRITIC rozszerza ten proces o zewnętrzny moduł weryfikacji faktów, który wychwytuje i eliminuje typowe halucynacje.

Komponenty:

- `generate` – generuje pierwotną odpowiedź.
- `feedback` – krytyka generowana bezpośrednio przez model LLM.
- `verify_external` – zewnętrzny, ugruntowany weryfikator (styl CRITIC).
- `refine` – modyfikuje odpowiedź z uwzględnieniem dotychczasowej historii.
- Warunek zatrzymania: pomyślny wynik weryfikacji lub osiągnięcie limitu 4 iteracji.

Uruchomienie:

```
python3 code/main.py
```

Porównaj logi wykonania dla Self-Refine oraz CRITIC. CRITIC skutecznie wychwytuje błąd merytoryczny, który został pominięty przez Self-Refine. Dzieje się tak, ponieważ zewnętrzny weryfikator bazuje na obiektywnych kryteriach, podczas gdy samokrytyka modelu opiera się wyłącznie na jego własnej wiedzy.

## Użyj tego

Wzorzec Evaluator-Optimizer od Anthropic to implementacja tego konceptu dostosowana do specyfiki modeli Claude. Wyjściowe poręcze w SDK OpenAI Agents realizują założenia CRITIC (guardrails mogą wchodzić w interakcję z zewnętrznymi narzędziami). LangGraph oferuje dedykowane węzły refleksji, które działają analogicznie do Self-Refine. W Gemini 2.5 Computer Use (Google) dodano mechanizm weryfikacji bezpieczeństwa dla poszczególnych kroków, będący odmianą wzorca CRITIC: każda zaplanowana akcja jest weryfikowana przed jej wykonaniem.

## Wyślij to

Plik `outputs/skill-refine-loop.md` opisuje konfigurację pętli Evaluator-Optimizer z uwzględnieniem specyfiki zadania, dostępności weryfikatorów zewnętrznych oraz limitu iteracji. Definiuje on prompty dla generatora, oceniającego (weryfikatora) i optymalizatora, a także reguły zakończenia pętli.

## Ćwiczenia

1. Przetestuj uproszczony model z parametrem max_iterations=1. Czy CRITIC wciąż przynosi korzyści?
2. Zastąp zewnętrzny weryfikator modułem generującym szum (losowo zwracającym 30% fałszywych alarmów). Jak wpływa to na przebieg pętli? Odzwierciedla to rzeczywiste wyzwania wdrożeniowe systemów guardrails.
3. Zaimplementuj podejście krzyżowe: niech większy model odpowiada za generowanie wyników, a mniejszy za ich krytykę. Czy takie rozwiązanie przewyższa jakość pracy pojedynczego modelu w obu rolach?
4. Przeczytaj sekcję 3 artykułu o CRITIC. Wskaż trzy kategorie zewnętrznych narzędzi weryfikacyjnych i podaj przykład dla każdej z nich.
5. Przeprowadź mapowanie funkcji `output_guardrails` z SDK OpenAI Agents na rolę weryfikatora w architekturze CRITIC. Wskaż mocne i słabe strony implementacji w tym pakiecie SDK.

## Kluczowe terminy

| Termin | Potoczne określenie | Co to w rzeczywistości oznacza |
|------|----------------|--------------------------------------|
| Self-Refine | „Model samonaprawiający się” | Pętla: generowanie -> ocena -> poprawianie realizowana w ramach jednego modelu z zachowaniem historii. |
| CRITIC | „Weryfikacja oparta na narzędziach” | Wzbogacenie oceny o zewnętrzne narzędzia (wyszukiwarki, kompilatory, kalkulatory, testy). |
| Evaluator-Optimizer | „Przepływ pracy według Anthropic” | Podział na rolę oceniającego (Evaluator) i poprawiającego (Optimizer) działających w pętli do osiągnięcia celu. |
| Output Guardrail | „Walidacja post-hoc” | Mechanizm weryfikacyjny w SDK OpenAI Agents, uruchamiany po wygenerowaniu odpowiedzi przez agenta. |
| Krok weryfikacji | „Krytyka wyniku” | Kluczowy etap oceny – może opierać się na samoocenie LLM lub obiektywnych testach zewnętrznych. |
| Historia poprawek | „Zapis dotychczasowych prób” | Przekazywany do promptu optymalizatora rejestr wcześniejszych wersji i uwag, zapobiegający powielaniu błędów. |
| Pętla wzajemnej akceptacji | „Problem automatycznej pieczątki” | Błąd polegający na tym, że model bezkrytycznie akceptuje własne pomyłki; rozwiązaniem są zróżnicowane prompty lub modele. |
| Warunek stopu | „Kryteria zbieżności” | Zbiór reguł przerywających pętlę (np. pomyślna weryfikacja lub przekroczenie limitu prób). |

## Dalsze czytanie

- [Madaan i in., Self-Refine (arXiv:2303.17651)](https://arxiv.org/abs/2303.17651) — artykuł kanoniczny
- [Gou i in., CRITIC (arXiv:2305.11738)](https://arxiv.org/abs/2305.11738) — weryfikacja oparta na narzędziach
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-efektywne-agents) — wzorzec przepływu pracy narzędzia oceniającego-optymalizatora
- [Dokumentacja pakietu SDK OpenAI Agents](https://openai.github.io/openai-agents-python/) — wyjściowe poręcze ochronne jako weryfikatory w kształcie KRYTYKA
