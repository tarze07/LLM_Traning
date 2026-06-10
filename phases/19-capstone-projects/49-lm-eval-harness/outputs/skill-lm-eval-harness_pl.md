---

name: lm-eval-harness
description: Minimalna wiązka ewaluacyjna modelu języka ze specyfikacją zadań JSONL, pięcioma metrykami, wymiennym adapterem i danymi wyjściowymi JSON tabeli liderów.
version: 1.0.0
phase: 19
lesson: 49
tags: [evaluation, metrics, leaderboard, harness]

---

## Kiedy używać

Porównaj dwa modele, dwa punkty kontrolne lub dwa szablony podpowiedzi z ustalonym zestawem zadań. Wszystko, co jest dostarczane i co trzeba monitorować w miarę upływu czasu.

## Specyfikacja zadania

Jedna linia JSONL na przykład:

```json
{"id": "ex-001", "prompt": "...", "targets": ["..."], "metric": "exact_match", "extras": {}}
```

Wszystkie przykłady w pliku mają wspólną metrykę. Nazwa pliku jest nazwą zadania.

## Metryki

| Metryczne | Podpis | Użyj dla |
|--------|-----------|--------|
| dokładne_dopasowanie | normalizuj dolne + białe znaki, równość | Arytmetyka, odpowiedzi faktoidowe |
| podciąg_zawiera | cel musi pojawić się w znormalizowanej prognozie | Generowanie dowolnej formy ze słowami kotwiczącymi |
| wybór_wielokrotny | dopasowanie pierwszej litery | Pytania w stylu A/B/C/D |
| różowy_l | LCS F1 nad tekstem tokenizowanym | Podsumowanie, parafraza |
| kod_exec | uruchom przewidywanie `f` na io_pairs, policz dopasowania | Generowanie kodu |

Wszystkie metryki zwracają wartość zmiennoprzecinkową w [0,0, 1,0]. Wynik zadania jest średnią.

## Adapter

```python
class Adapter(Protocol):
    name: str
    def generate(self, prompts: list[str]) -> list[str]: ...
```

Adapter to jedyny kod specyficzny dla modelu.

## Tablica liderów JSON

Ciąg schematu, sygnatura czasowa, wyniki dla poszczególnych zadań i opóźnienia, średnia ogólna. Uwzględnij rekordy dla poszczególnych przykładów podczas porównywania przebiegów, aby widoczne były regresje na poziomie przewidywań.

## Tryby awarii

- Metryka zwraca poza [0, 1]: ogólny wynik staje się niemożliwy do interpretacji.
- Mieszane metryki w jednym pliku zadania: wyzwalanie asercji; zachowaj jedną metrykę na plik.
- code_exec bez ograniczonej przestrzeni nazw: wykonanie dowolnego kodu.
— Brak ciągu schematu: ewolucja formatu psuje dalsze pulpity nawigacyjne.