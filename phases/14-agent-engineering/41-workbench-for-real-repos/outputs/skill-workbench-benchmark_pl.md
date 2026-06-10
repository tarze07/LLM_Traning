---

name: workbench-benchmark
description: Uruchom to samo zadanie za pomocą potoków zawierających tylko podpowiedzi i środowisko robocze we własnej przykładowej aplikacji projektu i wyemituj raport z pięcioma wynikami przed/po.
version: 1.0.0
phase: 14
lesson: 41
tags: [benchmark, before-after, evaluation, workbench, sample-app]

---

Biorąc pod uwagę repozytorium, produkt agenta i małą przykładową aplikację, utwórz przenośną wiązkę ewaluacyjną, która porównuje tylko podpowiedzi z potokami sterowanymi przez środowisko robocze.

Wyprodukuj:

1. `eval/sample_app/` — minimalnie wykonalna przykładowa aplikacja pobrana z domeny projektu.
2. `eval/run_prompt_only.py` i `eval/run_workbench.py`, każdy z nich pobiera opis zadania i zwraca `TaskOutcome`.
3. `eval/report.py`, który obsługuje oba potoki i zapisuje `before-after-report.md` i `comparison.json`.
4. Przepływ pracy CI, który kończy się niepowodzeniem, gdy wyniki warsztatu ulegają regresji w ustalonym zestawie zadań.
5. `docs/benchmark.md` wyjaśniający pięć wyników i to, co liczy się jako regresja.

Twarde odrzucenia:

- Punkt odniesienia z tylko jednym rurociągiem. Porównanie to cały sedno.
- Wyniki wyrażone w procentach bez mianownika. Zawsze zgłaszaj `n / m`.
- Przykładowa aplikacja, w zakresie której przeszkolono produkt agenta. Użyj urządzenia dostrojonego do domeny.
- Raporty ukrywające fałszywe negatywy. Należy wyliczyć zadania, w przypadku których tylko monit był szybszy.

Zasady odmowy:

- Jeśli projekt nie ma polecenia akceptacji, odmów wysyłki benchmarku. Nie ma nic do zmierzenia.
- Jeśli potok środowiska roboczego zajmuje więcej niż 3-krotność potoku wymagającego tylko podpowiedzi w zadaniu mediany, wyjaw to ustalenie; Uproszczenia wymaga stół warsztatowy, a nie model.
- Jeśli wiązka nie może działać w trybie offline, odmów podłączenia jej do CI. Niestabilność sieci zakłóci porównanie.

Struktura wyjściowa:

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

Zakończ słowami „co przeczytać dalej”, wskazując:

- Lekcja 42 dotycząca pakietu zwieńczeń, który obejmuje każdą powierzchnię wykorzystywaną przez rurociąg stołu warsztatowego.
- Lekcja 19 (SWE-bench, GAIA, AgentBench) dotycząca makropunktów odniesienia, które to uzupełnia.
- Lekcja 30 (Tworzenie agenta opartego na ewaluacji) na temat ciągłych pętli eval po podłączeniu testu porównawczego.