---

name: workbench-benchmark
description: Uruchomienie tego samego zadania w dwóch potokach — opartym wyłącznie na prompcie oraz z użyciem środowiska warsztatowego (workbench) — na przykładowej aplikacji projektowej i wygenerowanie raportu przed/po z pięcioma kluczowymi wskaźnikami.
version: 1.0.0
phase: 14
lesson: 41
tags: [benchmark, before-after, evaluation, workbench, sample-app]

---

Mając do dyspozycji repozytorium, gotowe rozwiązanie agentowe oraz małą aplikację przykładową, utwórz przenośny pakiet ewaluacyjny (uprząż testową), który porównuje działanie potoku opartego wyłącznie na promptach z potokiem sterowanym przez środowisko warsztatowe (workbench).

Wymagane rezultaty:

1. `eval/sample_app/` — minimalna działająca aplikacja przykładowa reprezentatywna dla domeny projektu.
2. Skrypty `eval/run_prompt_only.py` oraz `eval/run_workbench.py`, z których każdy przyjmuje opis zadania i zwraca `TaskOutcome`.
3. Skrypt `eval/report.py`, który uruchamia oba potoki i zapisuje wyniki w plikach `before-after-report.md` oraz `comparison.json`.
4. Konfiguracja przepływu pracy (workflow) CI, która kończy się niepowodzeniem, jeśli wyniki środowiska warsztatowego wykażą regresję na ustalonym zestawie zadań.
5. Plik `docs/benchmark.md` wyjaśniający pięć wskaźników oraz kryteria uznania wyniku za regresję.

Kryteria odrzucenia (Twarde reguły):

- Benchmark z tylko jednym potokiem. Istotą zadania jest bezpośrednie porównanie.
- Prezentowanie wyników procentowych bez podania mianownika. Zawsze podawaj ułamek `n / m`.
- Przykładowa aplikacja, na której rozwiązanie agentowe było wcześniej trenowane. Użyj środowiska testowego (fixture) specyficznego dla danej domeny.
- Raporty ukrywające przypadki fałszywie negatywne. Należy jawnie wymienić zadania, w których wykonanie przy użyciu samego promptu było szybsze.

Kryteria odmowy wykonania:

- Jeśli projekt nie posiada testów lub poleceń akceptacyjnych, odmów wdrożenia benchmarku. W takim przypadku nie ma mierzalnych parametrów.
- Jeśli potok środowiska warsztatowego dla mediany zadań trwa ponad 3-krotnie dłużej niż potok oparty na samym prompcie, należy to wyraźnie zgłosić. W takiej sytuacji uproszczenia wymaga samo środowisko warsztatowe (workbench), a nie model bazowy.
- Jeśli pakiet ewaluacyjny nie może działać w trybie offline, odmów wdrożenia go w potoku CI. Niestabilność sieci mogłaby zafałszować wyniki porównania.

Struktura katalogów i plików:

```
<repo>/
├── eval/
│   ├── sample_app/
│   ├── run_prompt_only.py
│   ├── run_workbench.py
│   └── report.py
├── outputs/eval/
│   ├── before-after-report.md
│   └── comparison.json
├── docs/benchmark.md
└── .github/workflows/benchmark.yml
```

Zakończ sekcją „Co przeczytać dalej”, odsyłającą do:

- Lekcji 42 dotyczącej projektu końcowego (capstone), który obejmuje każdy interfejs wykorzystywany w potoku środowiska warsztatowego.
- Lekcji 19 (SWE-bench, GAIA, AgentBench) poświęconej makro-benchmarkom, które uzupełniają to rozwiązanie.
- Lekcji 30 (Rozwój agentów oparty na ewaluacji) dotyczącej ciągłych pętli ewaluacji po wdrożeniu benchmarku.
