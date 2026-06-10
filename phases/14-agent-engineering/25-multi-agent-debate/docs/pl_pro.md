# Debata i współpraca między agentami (Multi-Agent Debate)

> Badanie Du i in. (ICML 2024, „Society of Minds”) opisuje podejście, w którym uruchamia się N instancji modelu. Proponują one niezależnie własne odpowiedzi, a następnie w ramach R rund iteracyjnie krytykują nawzajem swoje propozycje, dążąc do konsensusu (zbieżności). Metoda ta poprawia poprawność faktograficzną, przestrzeganie reguł oraz zdolności wnioskowania. Ponadto rzadka topologia komunikacji (sparse topology) okazuje się lepsza od pełnej siatki (full mesh) pod względem optymalizacji zużycia tokenów.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 12 (Wzorce przepływu pracy), Faza 14 · 05 (samodoskonalenie i KRYTYK)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnij protokół debaty wieloagentowej: N uczestników proponujących odpowiedzi, R rund wzajemnej krytyki, dążenie do wspólnego konsensusu.
- Opisz, jak debata wpływa na poprawę zgodności z faktami, przestrzeganie reguł oraz jakość rozumowania modeli.
- Wyjaśnij koncepcję rzadkiej topologii komunikacji (sparse topology): dlaczego nie każdy uczestnik debaty musi widzieć wypowiedzi wszystkich pozostałych.
- Zaimplementuj system debaty (oparty na bibliotece standardowej stdlib) symulujący działanie LLM w wariantach z pełną siatką (full mesh) oraz rzadką topologią, a następnie zmierz stosunek zużycia tokenów do dokładności odpowiedzi.

## Problem

Samodoskonalenie (Self-Refine, lekcja 05) opiera się na tym, że pojedynczy model krytykuje samego siebie – co niesie ze sobą ryzyko myślenia życzeniowego lub autokorelacji błędów (groupthink). Z kolei schemat CRITIC (lekcja 05) wymaga dostępu do zewnętrznych narzędzi weryfikacji, które nie zawsze są dostępne. Debata wprowadza trzecie podejście: wiele instancji modeli, wzajemna krytyka i wypracowanie konsensusu poprzez konfrontację różnych perspektyw.

## Koncepcja

### Society of Minds (Du i in., ICML 2024)

- N instancji modeli niezależnie generuje propozycje odpowiedzi na to samo pytanie.
- Przez R rund każdy model zapoznaje się z odpowiedziami pozostałych uczestników i je krytykuje.
- Modele aktualizują swoje odpowiedzi na podstawie otrzymanej krytyki.
- Po R rundach system zwraca wypracowaną, spójną odpowiedź.

W oryginalnych eksperymentach ze względu na koszty stosowano głównie parametry N=3 i R=2. Dokładność odpowiedzi rośnie wraz ze zwiększaniem liczby agentów oraz rund, szczególnie w przypadku trudnych zadań (takich jak testy MMLU, GSM8K, weryfikacja poprawności ruchów szachowych czy generowanie biografii).

Co ciekawe, debata prowadzona między różnymi modelami (np. ChatGPT + Bard) daje lepsze efekty niż debata w obrębie instancji tego samego modelu.

### Rzadka topologia komunikacji (Sparse Topology)

Praca „Udoskonalanie debaty wieloagentowej za pomocą rzadkiej topologii komunikacji” (arXiv:2406.11776) wykazała, że debata w modelu pełnej siatki (full mesh) nie zawsze jest najbardziej efektywna kosztowo. Rzadkie topologie (gwiazda, pierścień, piasta i szprychy – hub-and-spoke) mogą zapewnić zbliżoną dokładność przy znacznie mniejszym zużyciu tokenów. W tym scenariuszu każdy uczestnik widzi tylko wybrane wypowiedzi rówieśników (peers).

Przykładowe porównanie:

- Pełna siatka (N=5, R=3): 5 agentów × 3 rundy = 15 wygenerowanych odpowiedzi. Każdy czyta propozycje 4 pozostałych = łącznie 60 procesów krytyki.
- Gwiazda (N=5, R=3; 1 hub + 4 spoke): 15 propozycji, ale agenci zewnętrzni (szprychy) komunikują się tylko z agentem centralnym (piastą) = łącznie tylko 12 procesów krytyki.

### Kiedy debata przynosi korzyści

- **Zgodność z faktami:** N niezależnych propozycji i ich wzajemna weryfikacja skutecznie redukują halucynacje.
- **Przestrzeganie reguł:** Np. przy weryfikacji poprawności ruchu szachowego – jeśli jeden model przeoczy regułę, inny ją wychwyci.
- **Rozumowanie otwarte (open-ended reasoning):** Spojrzenie na problem z różnych perspektyw pomaga doprecyzować i ujednolicić właściwą odpowiedź.

### Kiedy debata generuje problemy (wady rozwiązania)

- **Wysokie opóźnienia (latency):** Sekwencyjne wykonywanie N × R rund wprowadza opóźnienie czasowe, które może być nieakceptowalne dla użytkownika (UX).
- **Wysokie koszty:** N × R razy większe zużycie tokenów na jedno zapytanie.
- **Proste wyszukiwanie faktów:** Zwykłe odpytanie bazy danych lub wyszukiwarki jest znacznie tańsze i szybsze niż angażowanie pięciu agentów w debatę.

### Praktyczne zastosowania w 2026 roku

- **Orkiestracja typu Orchestrator-Workers (Anthropic)** (lekcja 12): wariant debaty z dodatkowym etapem syntezy wyników.
- **Supervisor w LangGraph** (lekcja 13): centralny router oraz wyspecjalizowani agenci mogą realizować debatę w ramach dedykowanego węzła grafu.
- **OpenAI Agents SDK** (lekcja 16): agenci wymieniają wiadomości w celu prowadzenia iteracyjnej krytyki.
- **Ewaluacja wieloagentowa (Multi-agent evals):** Debata w parach modeli z zewnętrznym ewaluatorem optymalizującym sygnał oceny.

### Gdzie ten wzorzec może zawieść

- **Pozorna zbieżność (premature convergence):** Wszyscy agenci szybko zgadzają się co do błędnej odpowiedzi. Można temu zapobiegać, wymuszając rundy prezentacji odmiennych opinii.
- **Awaria centralnego węzła (hub failure):** W topologii gwiazdy błąd głównego agenta (huba) propaguje się na cały system. Rozwiązaniem jest rotacja roli huba lub stosowanie wielu hubów.
- **Szybka homogenizacja:** Jeśli wszyscy agenci korzystają z tego samego promptu i modelu, generują identyczne odpowiedzi. Należy stosować zróżnicowane prompty i/lub różne modele LLM.

## Zbuduj to

Plik `code/main.py` implementuje prosty system debaty oparty na bibliotece standardowej:

- Klasa `Debater` (symulująca uczestnika debaty z możliwością modyfikacji stanowiska).
- Klasy orkiestrujące `FullMeshDebate` oraz `SparseDebate`.
- Trzy rodzaje pytań testowych: oparte na faktach, oparte na regułach oraz wymagające logicznego rozumowania.
- Śledzone metryki: ostateczna zbieżna odpowiedź, liczba rund do osiągnięcia konsensusu, łączna liczba wygenerowanych krytyk.

Uruchomienie:

```
python3 code/main.py
```

Dane wyjściowe: porównanie dokładności oraz kosztu protokołu. Rzadka topologia osiąga zbliżoną dokładność do pełnej siatki przy niższym koszcie.

## Użyj tego

- **Orkiestracja typu Orchestrator-Workers (Anthropic)**: do prostych debat z udziałem 2-3 agentów roboczych.
- **LangGraph**: w przypadku złożonych, wielorundowych debat stanowych (stateful) z punktami kontrolnymi (checkpoints).
- **Własna implementacja**: na potrzeby projektów badawczych lub gdy wymagane są niestandardowe mechanizmy weryfikacji.

## Wyślij to

Plik `outputs/skill-debate.md` tworzy szablon systemu debaty wieloagentowej z konfigurowalną topologią komunikacji, liczbą agentów (N), liczbą rund (R) oraz regułą konsensusu.

## Ćwiczenia

1. Wprowadź regułę „wymuszonego braku porozumienia”: w pierwszej rundzie każdy uczestnik debaty musi przedstawić unikalną propozycję. Zmierz, jak wpływa to na szybkość osiągania konsensusu.
2. Wprowadź ważenie odpowiedzi na podstawie wskaźnika pewności (confidence): agenci zwracają parę (odpowiedź, pewność), a agregator waży ich głosy. Sprawdź, czy to pomaga?
3. Zastąp jednego z agentów modelem o wyraźnie odmiennych instrukcjach systemowych. Czy heterogeniczność grupy wpływa na zwiększenie dokładności?
4. Zmierz rzeczywiste zużycie tokenów dla pełnej siatki oraz rzadkiej topologii na zestawie 3 pytań. Porównaj stosunek kosztów do precyzji.
5. Przeczytaj oryginalną publikację „Society of Minds”. Przetestuj system dla parametrów N=5, R=3. Zaobserwuj, jakie problemy się pojawiają, a co ulega poprawie.

## Kluczowe terminy

| Termin | Co potocznie się mówi | Co to oznacza w rzeczywistości |
|------|----------------|--------------------------------------|
| Debata wieloagentowa | „Wzajemna krytyka modeli” | N instancji modeli generujących odpowiedzi i krytykujących się przez R rund w celu wypracowania konsensusu |
| Pełna siatka (Full Mesh) | „Każdy widzi każdego” | Każdy uczestnik debaty zapoznaje się z wypowiedziami wszystkich pozostałych w każdej rundzie |
| Rzadka topologia (Sparse) | „Ograniczony widok grupy” | Uczestnicy debaty widzą wypowiedzi tylko wybranego podzbioru rówieśników |
| Piasta i szprychy (Hub-and-spoke) | „Topologia gwiazdy” | Jeden centralny agent komunikuje się ze wszystkimi, a pozostali (N-1) widzą tylko wypowiedzi centrum |
| Zbieżność (Convergence/Konsensus) | „Uzgodnienie stanowisk” | Osiągnięcie zgodności uczestników debaty co do ostatecznej odpowiedzi |
| Society of Minds | „Praca o debacie Du et al.” | Publikacja z ICML 2024 opisująca metodę debaty wieloagentowej |

## Dalsze czytanie

- [Du i in., Society of Minds (arXiv:2305.14325)](https://arxiv.org/abs/2305.14325) – kanoniczna praca naukowa na temat debaty wieloagentowej
- [Topologia rzadkiej komunikacji (arXiv:2406.11776)](https://arxiv.org/abs/2406.11776) – analiza wydajności rzadkich struktur komunikacji
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) – opis wzorca orkiestrator-pracownicy jako wariantu debaty
- [Madaan i in., Self-Refine (arXiv:2303.17651)](https://arxiv.org/abs/2303.17651) – opis mechanizmu autokrytyki w obrębie jednego modelu
