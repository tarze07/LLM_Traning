# Benchmarki: SWE-bench, GAIA, AgentBench

> Trzy testy porównawcze Ocena agenta kotwiczącego w 2026 r. SWE-bench testuje łatanie kodu. GAIA testuje ogólne użycie narzędzi. AgentBench testuje rozumowanie wielośrodowiskowe. Poznaj ich skład, historię skażenia i to, czego nie mierzą.

**Typ:** Ucz się
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 06 (Użycie narzędzi)
**Czas:** ~60 minut

## Cele nauczania

- Nazwij wiązkę testową SWE-bench (FAIL_TO_PASS) i wyjaśnij, dlaczego jest ona bramką w testach jednostkowych.
- Wyjaśnij, dlaczego istnieje SWE-bench Verified (OpenAI, 500 zadań) i co usuwa.
- Opisz projekt GAIA: prosty dla ludzi, trudny dla sztucznej inteligencji; trzy poziomy trudności.
- Wymień osiem środowisk AgentBench i jego główny bloker dla LLM typu open source.
- Podsumuj ustalenia dotyczące zanieczyszczenia na podstawie SWE-bench+ i jego konsekwencje.

## Problem

Tabele liderów informują, który model wygrywa w jednym teście porównawczym. Nie mówią ci:

- Czy benchmark jest zanieczyszczony (rozwiązania w danych treningowych, wycieki testowe).
- Czy test porównawczy mierzy to, na czym Ci zależy (kod, przeglądanie, vs. ogólne).
- Czy osoba oceniająca jest solidna (dopasowanie AST, kontrole stanu, przegląd ręczny).

Zanim podasz liczbę, poznaj trzy wzorce zakotwiczenia i ich tryby awarii.

## Koncepcja

### Zespół SWE (Jimenez i in., ICLR 2024, ustnie)

- 2294 rzeczywistych problemów z GitHubem z 12 popularnych repozytoriów Pythona.
- Agent otrzymuje: bazę kodu w momencie zatwierdzenia przed poprawką + opis problemu w języku naturalnym.
- Agent produkuje: łatkę.
- Osoba oceniająca: zastosuj poprawkę, uruchom zestaw testów repo. Łatka musi odwracać testy FAIL_TO_PASS (wcześniej kończyły się niepowodzeniem, teraz zaliczały się pomyślnie) bez przerywania testów PASS_TO_PASS.

SWE-agent (Yang i in., 2024) osiągnął 12,5% w momencie wydania, kładąc nacisk na interfejsy agent-komputer (polecenia edytora plików, składnia wyszukiwania zrozumiała dla modelu).

### SWE-bench zweryfikowane

OpenAI, sierpień 2024 r. Podzbiór 500 zadań wybrany przez człowieka. Usuwa niejednoznaczne problemy, zawodne testy i zadania, w których rozwiązanie było niejasne. Główny punkt odniesienia dla pytania „czy Twój agent wysyła prawdziwe poprawki?”

### Zanieczyszczenie

- Ponad 94% problemów w środowisku SWE miało miejsce przed zakończeniem większości modeli.
- **SWE-bench+** znalazł rozwiązania w 32,67% udanych poprawek, które wyciekły w tekście problemu (model widział poprawkę w opisie), a 31,08% było podejrzliwych ze względu na słaby zasięg testów.
- Sprawdzono, że jest czystszy, ale nie wolny od zanieczyszczeń.

Praktyczne implikacje: model, który uzyskał 50% wyniku w SWE-bench, może uzyskać 35% w SWE-bench+. Zawsze zgłaszaj oba, jeśli twierdzisz, że działasz w środowisku SWE.

### GAIA (Mialon i in., listopad 2023)

- 466 pytań; 300 zatrzymanych w prywatnej tabeli liderów na stronie huggingface.co/gaia-benchmark.
- Filozofia projektowania: „koncepcyjnie proste dla ludzi (92%), ale trudne dla sztucznej inteligencji (GPT-4 z wtyczkami: 15%).”
- Testuje rozumowanie, multimodalność, sieć, użycie narzędzi.
- Trzy poziomy trudności; Poziom 3 wymaga długich łańcuchów narzędzi w różnych modalnościach.

GAIA jest tym, co uruchamiasz, aby zmierzyć „zdolności ogólne”. Nie mylić z benchmarkami specyficznymi dla kodu.

### AgentBench (Liu i in., ICLR 2024)

- 8 środowisk obejmujących kod (Bash, DB, KG), gry (Alfworld, LTP), internet (WebShop, Mind2Web) i generację otwartą.
- Wieloobrotowy, ~4–13 tys. obrotów na podział.
- Główny wniosek: długoterminowe rozumowanie, podejmowanie decyzji i przestrzeganie instrukcji to czynniki utrudniające OSS LLM doganianie komercji.

### Czego to nie mierzy

- Koszty operacyjne w świecie rzeczywistym (żetony, zegar ścienny).
- Zachowanie bezpieczne w nieprzyjaznych warunkach.
- Wydajność w Twojej domenie (użyj własnych ewaluacji, Lekcja 30).
- Awarie ogonów (średnia w benchmarkach; operatorzy produkcyjni zwracają uwagę na najgorszy 1%).

### Gdzie benchmarking się nie udaje

- **Ustalanie jednej liczby.** SWE-bench 50% podaje mniej niż koszt P50/P75/P95 + rozkład kroków.
- **Zanieczyszczone twierdzenia.** Zgłaszanie SWE-bench bez wspomnienia Verified lub SWE-bench+ wprowadza w błąd.
- **Benchmark jako cel-rozwojowy.** Optymalizacja pod kątem benchmarku odbiega od użyteczności produkcyjnej.

## Zbuduj to

`code/main.py` implementuje zabawkową uprząż przypominającą ławkę SWE:

- Syntetyczne zadania naprawiania błędów (3 zadania).
- Skryptowany „agent” proponujący poprawki.
- Program uruchamiający test, który sprawdza FAIL_TO_PASS (błąd już naprawiony) i PASS_TO_PASS (nic nie jest zepsute).
- Klasyfikator trudności w stylu GAIA oparty na głębokości rozkładu pytań.

Uruchom to:

```
python3 code/main.py
```

Dane wyjściowe pokazują współczynnik rozdzielczości na zadanie + na stopień trudności i konkretyzują zasady oceniającego.

## Użyj tego

- **SWE-bench Verified** dla agentów kodujących. Zawsze zgłaszaj zweryfikowane wyniki.
- **GAIA** dla agentów ogólnych. Użyj prywatnego podziału tabeli liderów.
- **AgentBench** do porównywania wielu środowisk.
- **Niestandardowe oceny** (Lekcja 30) rzeczywistego kształtu Twojego produktu.

## Wyślij to

`outputs/skill-benchmark-harness.md` tworzy uprząż w stylu SWE-bench dla dowolnej pary kod-zadania z bramkowaniem FAIL_TO_PASS / PASS_TO_PASS.

## Ćwiczenia

1. Przenieś uprząż zabawkową, aby działała na prawdziwym repozytorium (wybierz jedno ze swoich). Napisz 3 testy FAIL_TO_PASS dla znanych błędów.
2. Dodaj metrykę liczby kroków. Ile kroków agenta przypada na każde rozwiązanie w przypadku trzech zadań?
3. Przeczytaj dokument SWE-bench+. Zaimplementuj kontrolę wycieków rozwiązań (dopasuj wzór tekstu problemu do różnicy).
4. Pobierz pytanie GAIA z publicznego podziału. Prześledź, co zrobiłby agent klasy GPT-4. Jakich narzędzi potrzebuje?
5. Przeczytaj podział AgentBench na środowiska. Które środowisko odzwierciedla powierzchnię Twojego produktu? Jak tam wygląda „SOTA”?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Ławka SWE | „Porównanie agenta kodu” | 2294 problemów z GitHubem; poprawka musi odwrócić testy FAIL_TO_PASS |
| Zweryfikowano w SWE-bench | „Czysty stół SWE” | 500 zadań wybranych przez ludzi, OpenAI |
| FAIL_TO_PASS | „Napraw bramę” | Testy, które wcześniej zakończyły się niepowodzeniem, muszą zostać zaliczone po łatce |
| PASS_TO_PASS | „Brama bez regresji” | Testy, które przechodziły i muszą jeszcze przejść |
| GAJA | „Ogólny punkt odniesienia” | 466 pytań dotyczących wielu narzędzi łatwych dla człowieka / trudnych dla sztucznej inteligencji |
| Ławka agenta | „Benchmark wielu środowisk” | 8 środowisk; wieloobrotowy długohoryzontalny |
| Zanieczyszczenie | „Wyciek zestawu szkoleniowego” | Zadania porównawcze obecne w szkoleniu modelowym |
| Ławka SWE+ | „Audyt skażenia” | W udanych poprawkach SWE-Bench wykryto 32,67% wycieku roztworu |

## Dalsze czytanie

- [Jimenez i in., SWE-bench (arXiv:2310.06770)](https://arxiv.org/abs/2310.06770) — oryginalny test porównawczy
- [OpenAI, SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) — wyselekcjonowany podzbiór
- [Mialon i in., GAIA (arXiv:2311.12983)](https://arxiv.org/abs/2311.12983) — ogólny punkt odniesienia
- [Liu i in., AgentBench (arXiv:2308.03688)](https://arxiv.org/abs/2308.03688) — pakiet wielośrodowiskowy