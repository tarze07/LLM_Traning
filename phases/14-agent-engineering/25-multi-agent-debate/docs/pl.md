# Debata i współpraca między agentami

> Du i in. (ICML 2024, „Society of Minds”) uruchamia N instancji modelu, które niezależnie proponują odpowiedzi, a następnie iteracyjnie krytykują się nawzajem w rundach R, aby uzyskać zbieżność. Poprawia faktyczność, przestrzeganie zasad i rozumowanie. Topologia rzadka przewyższa pełną siatkę pod względem kosztu symbolicznego.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 12 (Wzorce przepływu pracy), Faza 14 · 05 (samodoskonalenie i KRYTYK)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnij protokół debaty: N wnioskodawców, R rund, zbiegają się w sprawie wspólnej odpowiedzi.
- Opisz, dlaczego debata poprawia fakty, przestrzeganie zasad i rozumowanie.
- Wyjaśnij rzadką topologię: nie każdy dyskutant musi się widzieć.
- Zaimplementuj debatę stdlib nad skryptowym LLM z wariantami z pełną siatką i rzadkimi; mierz koszt tokena w porównaniu z dokładnością.

## Problem

Samodoskonalenie (lekcja 05) to jeden z modeli krytykowania samego siebie – ryzyko to myślenia grupowego. KRYTYK (Lekcja 05) opiera krytykę na narzędziach zewnętrznych – nie zawsze dostępnych. Debata wprowadza trzeci tryb: wielokrotne przypadki, wzajemna krytyka, zbieżność przez brak porozumienia.

## Koncepcja

### Society of Minds (Du i in., ICML 2024)

- N instancji modelu niezależnie proponuje odpowiedzi na to samo pytanie.
- Podczas rund R każdy model czyta propozycje innych i je krytykuje.
- Modele aktualizują swoje odpowiedzi w oparciu o krytykę.
- Po rundach R zwróć zbieżną odpowiedź.

Zastosowano oryginalne eksperymenty N=3, R=2 ze względu na koszt. Dokładność poprawia się wraz z większą liczbą agentów i większą liczbą rund przy trudnych problemach (MMLU, GSM8K, ważność ruchów szachowych, generowanie biografii).

Kombinacje międzymodelowe pokonują debaty dotyczące jednego modelu: ChatGPT + Bard razem > albo osobno.

### Topologia rzadka

„Udoskonalanie debaty wieloagentowej za pomocą rzadkiej topologii komunikacji” (arXiv:2406.11776, 2024–2025) pokazało, że debata w trybie pełnej siatki nie zawsze jest optymalna. Rzadkie topologie (gwiazda, pierścień, piasta i szprychy) mogą dorównać dokładnością przy niższym koszcie tokena. Każdy dyskutant widzi tylko podzbiór rówieśników.

Implikacje:

- Pełna siatka N=5, R=3 = 5 × 3 = 15 propozycji, każdy czytający 4 równorzędni = 60 krytyków.
- Gwiazda N=5, R=3 (jedna piasta + 4 szprychy) = 15 propozycji, szprychy czytają tylko piastę = 12 operacji krytycznych.

### Kiedy debata pomaga

- **Fakty.** N niezależnych propozycji, sprawdzenie krzyżowe zmniejsza halucynacje.
- **Przestrzeganie zasad.** Ważność ruchu szachowego — jeden model pomija regułę, inni ją łapią.
- **Rozumowanie otwarte.** Wiele ujęć zawęża właściwą odpowiedź.

### Kiedy debata boli

- **UX wrażliwy na opóźnienia.** N × R rund seryjnych to opóźnienie, którego możesz nie mieć.
- **Skala uwzględniająca koszty.** N × R tokenów na pytanie.
- **Proste wyszukiwanie faktów.** Jedno wyszukiwanie jest tańsze niż pięć debat.

### 2026 praktycznych instancji

- **Antropiczni orkiestratorzy-pracownicy** (Lekcja 12) — jeden wariant debaty z etapem syntezy.
- **Nadzorca LangGraph** (Lekcja 13) — router centralny + wyspecjalizowani agenci mogą realizować debatę jako węzeł.
- **OpenAI Agents SDK** (Lekcja 16) — agenci przekazują informacje tam i z powrotem w celu iteracyjnej krytyki.
- **Ewaluacje wieloagentowe** — debata w parach + ewaluator-optymalizator sygnału eval.

### Gdzie ten wzorzec jest błędny

- **Załamanie zbieżności.** Wszyscy agenci zbiegają się w sprawie pierwszej błędnej odpowiedzi. Łagodź za pomocą wymaganych rund niezgody.
- **Awaria koncentratora.** W topologii gwiazdy zły koncentrator psuje wszystkich. Obróć lub użyj wielu koncentratorów.
- **Szybka homogenizacja.** Wszyscy agenci korzystają z tego samego podpowiedzi; dają te same odpowiedzi. Używaj różnorodnych podpowiedzi i/lub modeli.

## Zbuduj to

`code/main.py` implementuje debatę na temat stdlib:

- Zajęcia `Debater` (skrypt LLM z możliwością zmiany opinii każdego uczestnika).
- biegacze `FullMeshDebate` i `SparseDebate`.
- Trzy pytania: jedno oparte na faktach, jedno oparte na zasadach, jedno uzasadniające.
- Metryki: zbieżna odpowiedź, rundy do zbieżności, całkowita krytyka.

Uruchom to:

```
python3 code/main.py
```

Dane wyjściowe: dokładność i koszt protokołu; rzadkie dopasowuje pełną siatkę na 2/3 pytań przy niższym koszcie.

## Użyj tego

- **Antropiczni orkiestratorzy-pracownicy** do prostych debat dla 2-3 pracowników.
- **LangGraph** dla stanowej, wielorundowej debaty z punktami kontrolnymi.
- **Niestandardowe** dla badań lub specjalistycznych gwarancji poprawności.

## Wyślij to

`outputs/skill-debate.md` tworzy szkielet debaty między agentami z konfigurowalną topologią, N, R i regułą zbieżności.

## Ćwiczenia

1. Wprowadź zasadę „wymuszonego braku porozumienia”: w pierwszej rundzie każdy debatujący musi przedstawić odrębną propozycję. Zmierz wpływ na szybkość konwergencji.
2. Dodaj agregację ważoną ufnością: powracający debatanci (odpowiedź, pewność siebie); agregator waży według ufności. Czy to pomaga?
3. Zamień jednego „agenta” na innego skryptowego LLM z różnymi opiniami. Czy heterogeniczność poprawia dokładność?
4. Zmierz koszt tokena dla pełnej siatki w porównaniu z rzadką na 3 pytania. Koszt wydruku a dokładność.
5. Przeczytaj artykuł Towarzystwa Umysłów. Przenieś swoją zabawkę do N=5, R=3. Co się psuje? Co staje się lepsze?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Debata | „Krytyka wieloagentowa” | N wnioskodawców, R rund wzajemnej krytyki, zbiegają się |
| Pełna siatka | „Każdy czyta każdego” | Każdy dyskutant czyta każdego rówieśnika w każdej rundzie |
| Rzadka topologia | „Ograniczony widok peer” | Dyskutanci czytają tylko podzbiór równorzędnych |
| Centrum i szprychy | „Topologia gwiazdy” | Jeden z głównych dyskutantów, szprychy N-1, czytał tylko centrum |
| Konwergencja | „Umowa” | Dyskutanci są zgodni co do wspólnej odpowiedzi |
| Towarzystwo Umysłów | „Du i wsp. Dokument debatowy” | Metoda debaty wieloagentowej ICML 2024 |

## Dalsze czytanie

- [Du i in., Society of Minds (arXiv:2305.14325)](https://arxiv.org/abs/2305.14325) — kanoniczna debata wieloagentowa
- [Topologia rzadkiej komunikacji (arXiv:2406.11776)](https://arxiv.org/abs/2406.11776) — wyniki topologii rzadkiej
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-efektywne-agents) — orkiestrator-pracownicy jako wariant debaty
- [Madaan i in., Self-Refine (arXiv:2303.17651)](https://arxiv.org/abs/2303.17651) — odpowiednik samokrytyki w jednym modelu