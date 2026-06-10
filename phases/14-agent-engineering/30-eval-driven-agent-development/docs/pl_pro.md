# Rozwój agentów oparty na ewaluacji (Eval-Driven Agent Development)

> Rekomendacja Anthropic brzmi: „zacznij od prostych promptów, optymalizuj je za pomocą kompleksowych ewaluacji, a wieloetapowe systemy agentowe dodawaj tylko wtedy, gdy są naprawdę niezbędne”. Ewaluacja to nie jednorazowy krok na końcu procesu. To zewnętrzna pętla sterująca, która warunkuje każdy wybór architektoniczny w projektowaniu agentów.

**Typ:** Nauka + Budowa
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 (wszystkie poprzednie lekcje)
**Czas:** ~60 minut

## Cele nauczania

- Wymień trzy warstwy ewaluacji – benchmarki statyczne, niestandardowe testy offline oraz monitorowanie online – i określ przeznaczenie każdej z nich.
- Wyjaśnij mechanizm działania szczelnej pętli ewaluator-optymalizator (evaluator-optimizer).
- Opisz najlepsze praktyki wdrożeniowe: przechowywanie testów ewaluacyjnych (evals) obok kodu, automatyczne uruchamianie ich w potokach CI oraz stosowanie ich jako bramek blokujących Pull Requesty.
- Przyporządkuj zagadnienia z poszczególnych lekcji Fazy 14 do odpowiadających im przypadków testowych.

## Problem

Agenci często świetnie radzą sobie na prezentacjach (demach), ale zawodzą w środowisku produkcyjnym w sposób niemożliwy do przewidzenia na etapie pokazów. Standardowe benchmarki oceniają ogólne możliwości modelu, a nie to, czy agent poprawnie generuje poprawki specyficzne dla Twojego produktu. Rozwiązaniem jest ciągła ewaluacja na trzech poziomach, w której każdy mechanizm zabezpieczający (guardrail) i każda wdrożona reguła biznesowa odpowiadają konkretnemu przypadkowi testowemu.

## Koncepcja

### Trzy warstwy ewaluacji

1. **Statyczne benchmarki:** SWE-bench Verified dla oceny kodu (lekcja 19), WebArena/OSWorld do testów interakcji sieciowych i systemowych (lekcja 20), GAIA jako ogólny sprawdzian asystencki (lekcja 19) oraz BFCL V4 do weryfikacji wywołań narzędzi (lekcja 06). Służą do porównywania modeli bazowych i wykrywania regresji. Należy uważać na zjawisko wycieku danych testowych (data contamination): analiza SWE-bench+ wykazała wyciek rozwiązań na poziomie 32,67%. Zawsze należy opierać się na wersjach „Verified” lub zweryfikowanych przez człowieka (human-audited).

2. **Niestandardowe testy offline:** Zestawy testowe dostosowane do logiki Twojego produktu:
   - Ewaluacja przy użyciu LLM jako sędziego (LLM-as-a-judge) za pomocą narzędzi Langfuse, Phoenix lub Opik (lekcja 24).
   - Weryfikacja oparta na wykonaniu (execution-based): np. uruchomienie wygenerowanego kodu i sprawdzenie wyników testów jednostkowych.
   - Analiza trajektorii (trajectory-based): porównanie sekwencji działań agenta z optymalną, wzorcową ścieżką (gold trajectory). Badanie OSWorld-Human wskazuje, że najlepsi agenci potrzebują średnio od 1,4 do 2,7 raza więcej kroków niż człowiek.

3. **Monitorowanie i testy online:** Ewaluacja w środowisku produkcyjnym:
   - Odtwarzanie sesji użytkowników (session replay) np. w Langfuse.
   - Monitorowanie alertów wyzwalanych przez guardrails (lekcja 16, lekcja 21).
   - Śledzenie kosztów i opóźnień każdego kroku wnioskowania za pomocą OpenTelemetry (lekcja 23).

### Ewaluator-optymalizator (Evaluator-Optimizer)

Szczelna pętla sterująca:

1. **Generator (Proposer):** Tworzy wersję roboczą odpowiedzi lub kodu.
2. **Ewaluator (Evaluator):** Ocenia wynik pod kątem kryteriów akceptacji.
3. **Optymalizator:** Wprowadza poprawki w pętli zwrotnej, dopóki ewaluator nie wyda pozytywnej oceny lub nie zostanie wyczerpany budżet rund.

To uogólniona wersja mechanizmu Self-Refine (lekcja 05). Każdy kluczowy przepływ agenta można wyposażyć w taką pętlę w celu zwiększenia niezawodności działania.

## Najlepsze praktyki wdrożeniowe

- Testy ewaluacyjne (evals) powinny znajdować się bezpośrednio w repozytorium obok kodu aplikacji.
- Są automatycznie uruchamiane w potokach CI (Continuous Integration) dla każdego Pull Requestu.
- Służą jako bramka blokująca scalenie kodu (merge gate) w przypadku wykrycia regresji (np. dopuszczając spadek dokładności o maksymalnie 5% w stosunku do gałęzi głównej).
- Każdy mechanizm zabezpieczający (guardrail) ma odpowiadający mu przypadek testowy w ewaluacji.
- Każda nowo wdrożona reguła działania (np. z mechanizmu Reflexion lub wniosków z analizy przepływu) odnosi się do konkretnego historycznego błędu na produkcji.

### Podsumowanie Fazy 14

Każda lekcja w Fazie 14 generuje przypadki testowe dla ewaluacji:

| Lekcja | Wygenerowany przypadek testowy |
|--------|------------------------|
| 01 Pętla Agenta | Wyczerpanie budżetu kroków, zatrzymanie pętli nieskończonej |
| 02 ReWOO | Planista modyfikuje plan działania po awarii narzędzia |
| 03 Reflexion | Zastosowanie wyciągniętych wniosków (refleksji) przy kolejnej próbie |
| 05 Self-Refine/CRITIC | Pomyślna weryfikacja udoskonalonego wyniku przez sędziego |
| 06 Narzędzia | Poprawna walidacja argumentów, odrzucenie wywołań nieznanych narzędzi |
| 07-10 Pamięć | Zgodność cytatów ze źródłami, unieważnianie zdezaktualizowanych faktów |
| 12 Wzorce Workflow | Prawidłowość struktury danych wyjściowych dla każdego wzorca przepływu |
| 13 LangGraph | Dokładność wznawiania działania z zapisanego punktu kontrolnego |
| 14 AutoGen (Aktorzy) | Przekierowanie zawieszonych lub uszkodzonych zadań do kolejki DLQ |
| 16 OpenAI Agents SDK | Prawidłowa reakcja zabezpieczeń na zdefiniowane dane wejściowe |
| 17 Claude Agent SDK | Pomyślny powrót wyników z podagentów do orkiestratora |
| 19-20 Benchmarki | Wynik SWE-bench Verified, wskaźnik sukcesu WebArena, wydajność OSWorld |
| 21 Computer Use | Zablokowanie złośliwych instrukcji wstrzykniętych do drzewa DOM |
| 23 OTel | Poprawność i kompletność atrybutów emitowanych w spanach |
| 26 Tryby Awarii | Wykrywanie i flagowanie znanych sygnatur błędów |
| 27 Prompt Injection | Odrzucenie zainfekowanych danych przez architekturę PVE |
| 28 Orkiestracja | Poprawność routingu zadań do właściwego specjalisty przez nadzorcę |
| 29 Modele Uruchomieniowe | Stabilność kolejki DLQ przy zdefiniowanym poziomie błędów (N%) |

Jeśli Twój zestaw testów obejmuje scenariusze dla wszystkich powyższych obszarów, Faza 14 została w pełni opanowana.

### Gdzie rozwój oparty na ewaluacji może zawieść

- **Brak linii bazowej (baseline):** Ewaluacja bez porównania z ostatnią znaną poprawną wersją systemu nie pozwala na obiektywną ocenę. Zawsze zapisuj i wersjonuj wyniki bazowe.
- **Halucynacje sędziego LLM:** Modele oceniające również popełniają błędy. Zgodnie z wzorcem CRITIC (lekcja 05), sędzia powinien opierać swoje werdykty na zewnętrznych narzędziach weryfikacji.
- **Nadmierne dopasowanie (Over-fitting):** Optymalizacja promptów wyłącznie pod kątem przejścia konkretnego zestawu testowego (eval suite) może pogorszyć stabilność na produkcji. Należy regularnie rotować przypadki testowe.
- **Niestabilność testów (Flakiness):** Niedeterministyczne zachowanie modeli generuje fałszywe alarmy w potokach CI. Należy zamrażać ziarna losowości (pin seeds) oraz zapisywać migawki stanu systemu do analizy.

## Zbuduj to

Plik `code/main.py` implementuje prosty framework ewaluacyjny oparty na bibliotece standardowej:

- Rejestr przypadków testowych podzielony na kategorie (benchmark, offline, online).
- Oskryptowany agent testowy.
- Pętla ewaluatora-optymalizatora: generowanie, ocena, iteracyjne poprawianie aż do uzyskania akceptacji lub wyczerpania limitu rund.
- Integracja z CI: wyliczanie zagregowanego wskaźnika sukcesu i weryfikacja pod kątem regresji w stosunku do linii bazowej.

Uruchomienie:

```bash
python3 code/main.py
```

Dane wyjściowe: status (pass/fail) dla każdego testu, flaga wykrycia regresji oraz ostateczny werdykt bramki CI.

## Użyj tego

- Przechowuj definicje testów ewaluacyjnych w tym samym repozytorium, co kod źródłowy agenta.
- Skonfiguruj automatyczne uruchamianie testów w potoku CI dla każdego Pull Requestu.
- Zablokuj scalanie kodu (fail build) w przypadku wykrycia regresji względem gałęzi głównej.
- Monitoruj trendy wskaźnika sukcesu (pass rate) w czasie.
- Każdy nowo wykryty błąd produkcyjny przekształcaj w przypadek testowy w pakiecie ewaluacyjnym, aby zapobiec jego ponownemu wystąpieniu.

## Wyślij to

Plik `outputs/skill-eval-suite.md` buduje trzywarstwowy pakiet ewaluacyjny dla produktu, zintegrowany z bramkami CI i analizą regresji.

## Ćwiczenia

1. Wybierz jeden z rzeczywistych błędów, który wystąpił w Twojej aplikacji. Napisz przypadek testowy, który go odwzorowuje. Sprawdź, czy Twój agent przechodzi go poprawnie po wprowadzeniu poprawek.
2. Zdefiniuj szczegółowe kryteria oceny dla sędziego LLM dla swojej domeny biznesowej (np. poprawność faktów, ton wypowiedzi, kompletność odpowiedzi). Przetestuj ich stabilność na próbie 50 sesji.
3. Zintegruj pakiet testowy z potokiem CI i skonfiguruj regułę blokującą wdrożenie, jeśli regresja przekroczy progi tolerancji (np. >=5%).
4. Zaimplementuj metrykę wydajności trajektorii (trajectory efficiency): zmierz, o ile więcej kroków wykonuje agent w porównaniu z optymalną ścieżką ludzką (gold trajectory).
5. Przeprowadź audyt swojego pakietu testowego pod kątem pokrycia wszystkich obszarów wymienionych w tabeli podsumowującej Fazę 14. Zidentyfikuj i uzupełnij brakujące scenariusze testowe.

## Kluczowe pojęcia

| Termin | Co potocznie się mówi | Co to oznacza w rzeczywistości |
|------|----------------|------------------------|
| Statyczny benchmark | „Gotowy test” | Znormalizowane zbiory testowe (np. SWE-bench, GAIA, AgentBench, WebArena, OSWorld) do ogólnej oceny modeli |
| Niestandardowy test offline | „Ewaluacja domenowa” | Testy specyficzne dla aplikacji, oparte na sędziowaniu LLM, weryfikacji wykonania lub porównywaniu trajektorii |
| Monitorowanie online | „Ewaluacja na produkcji” | Analiza logów produkcyjnych, odtwarzanie sesji, zliczanie alertów z guardrails oraz analiza opóźnień i kosztów |
| Ewaluator-optymalizator | „Pętla poprawiania wyników” | Schemat iteracyjny, w którym model poprawia swoje wyjście na podstawie ocen sędziego, aż przejdzie walidację |
| Bramka CI (CI gate) | „Blokada merge'a” | Zautomatyzowany krok w procesie budowania aplikacji, który odrzuca zmiany w kodzie w przypadku wykrycia regresji jakościowej |
| Linia bazowa (Baseline) | „Punkt odniesienia” | Wyniki poprzedniej, stabilnej wersji systemu, służące do oceny czy nowe zmiany nie pogarszają jakości |
| Wydajność trajektorii | „Długość ścieżki agenta” | Stosunek liczby kroków wykonanych przez agenta do liczby kroków w optymalnym scenariuszu ludzkim |

## Dalsza lektura

- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) – przewodnik: „zacznij prosto, optymalizuj ewaluacjami”
- [OpenAI, SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) – omówienie moderowanego benchmarku dla zadań programistycznych
- [Berkeley Function Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html) – lider weryfikacji modeli pod kątem obsługi wywołań narzędzi (tool calls)
- [Langfuse docs](https://langfuse.com/) – praktyczne wskazówki dotyczące wdrażania ewaluacji i odtwarzania sesji
