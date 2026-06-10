# Krajobraz autonomicznego agenta kodującego (2026)

> Wskaźnik SWE-bench Verified wzrósł z 4% do 80,9% w niecałe trzy lata. Ten sam Claude Sonnet 4.5 uzyskał 43,2% na SWE-agent v1 i 59,8% na Cline autonomicznym — rusztowanie wokół modelu ma teraz takie samo znaczenie jak sam model. OpenHands (dawniej OpenDevin) to najaktywniejsza platforma na licencji MIT, a jej pętla CodeAct wykonuje akcje Pythona bezpośrednio w piaskownicy zamiast wywołań narzędzi JSON. Liczby nagłówkowe skrywają problem metodologiczny: 161 z 500 zadań SWE-bench Verified wymaga jedynie zmiany 1–2 linii, a SWE-bench Pro (10+ zadań liniowych) wynosi 23–59% dla tych samych modeli granicznych.

**Typ:** Ucz się
**Języki:** Python (porównanie wywołań narzędzi stdlib, CodeAct i JSON)
**Wymagania wstępne:** Faza 14 · 07 (Użycie narzędzi), Faza 15 · 01 (Agenci z dalekiego horyzontu)
**Czas:** ~45 minut

## Problem

„Który agent kodujący jest najlepszy” to niewłaściwe pytanie. Właściwe pytanie brzmi: jaką kompleksową niezawodność uzyskam przy podziale zadań odpowiadającym mojej pracy i rusztowaniu, które będę uruchamiał w produkcji?

W latach 2022–2026 badacze dowiedzieli się, że rusztowanie — warstwa wyszukiwania, planista, piaskownica, pętla edycji i weryfikacji oraz format informacji zwrotnej — przenosi obciążenie. Claude Sonnet 4.5 na SWE-agent v1 uzyskał 43,2% na SWE-bench Verified; ten sam model znajdujący się na autonomicznym rusztowaniu Cline’a uzyskał 59,8%. 16,6 bezwzględnych punktów różnicy, te same wagi. Model podstawowy jest komponentem; pętla jest produktem.

Problem towarzyszący polega na tym, że nasycenie wzorców ukrywa regresje. SWE-bench Verified jest bliski nasycenia, a ogon łatwych zadań (161 z 500 zadań wymagających ≤2 wierszy) zapewnia najwyższe wyniki. Jakość w świecie rzeczywistym jest lepiej mierzona w dystrybucjach takich jak SWE-bench Pro (ponad 10 zmian linii), gdzie ci sami liderzy nadal plasują się na poziomie 23–59%.

## Koncepcja

### Ławka SWE, jeden akapit

SWE-bench (Jimenez i in.) rozwiązuje rzeczywiste problemy z GitHubem, wprowadzając rzeczywiste łatki i prosi agenta o stworzenie łatki, która sprawi, że zestaw testów przejdzie pomyślnie. SWE-bench Verified (OpenAI, 2024) to wyselekcjonowany przez człowieka podzbiór 500 zadań, z których usunięto niejednoznaczne i uszkodzone zadania. SWE-bench Pro jest trudniejszym następcą — zadania wymagające ponad 10 linii zmian, gdzie obecni agenci graniczni wynoszą 23–59%.

### Co właściwie pokazuje krzywa 2022 → 2026

- **2022**: modele badawcze na poziomie ~4% na surowym stole SWE.
- **2024**: GPT-4 + rusztowanie w stylu Devina ~14%; Agent SWE na poziomie ~12%.
- **2025**: Claude 3.5/3.7 Sonnet w Aiderze i agencie SWE osiąga zakres 40–55%.
- **2026**: Claude Sonnet 4.5 i czołowi konkurenci na poziomie 70–80%+ w testach SWE Zweryfikowano. Tablica liderów Epoch AI śledzi tę sytuację na żywo.

Nachylenie pochodziło z trzech źródeł złożonych: lepszych modeli podstawowych, lepszego rusztowania (CodeAct, odbicie, pętle weryfikatora) i lepszych testów porównawczych (zweryfikowane usuwanie szumu).

### Wywołania narzędzi CodeAct i JSON

OpenHands (All-Hands-AI, arXiv:2407.16741, dawniej OpenDevin) przyjął konkretny projekt architektoniczny: zamiast modelu emitującego wywołania narzędzi JSON, które host dekoduje i wykonuje, model emituje kod Pythona, a jądro w stylu Jupytera uruchamia go w piaskownicy. Agent może zapętlać pliki, łączyć narzędzia i przechwytywać własne wyjątki w ramach jednej akcji.

Kompromis:

- **Wywołania narzędzi JSON**: każda akcja to jedna tura; łatwy do audytu; ograniczona kompozycyjność; domyślnie bezpieczne, ponieważ każde wywołanie przechodzi przez jawny moduł sprawdzający.
- **CodeAct**: jedna akcja może stanowić cały program; kompozycyjny; wymaga wzmocnionej piaskownicy (OpenHands wykorzystuje izolację Dockera); tryby awarii obejmują wszystko, na co pozwala środowisko wykonawcze piaskownicy.

Obie architektury są w fazie produkcji. CodeAct dominuje na platformach otwartych (OpenHands, smolagents). Wywołania narzędzi JSON pozostają dominujące w usługach zarządzanych (Agenci zarządzani Anthropic, Asystenci OpenAI), gdzie dostawca kontroluje wykonawcę.

### Rusztowania w krajobrazie 2026 roku

| Rusztowanie | Licencja | Model wykonania | Godna uwagi nieruchomość |
|---|---|---|---|
| OpenHands (OpenDevin) | MIT | CodeAct w Dockerze | Najbardziej aktywna otwarta platforma; możliwość odtwarzania strumienia zdarzeń |
| Agent SWE | MIT | Interfejs agent-komputer (ACI) | Pierwsze kompleksowe rusztowanie stołowe SWE |
| Pomocnik | Apache-2 | edit-via-diff w lokalnym repozytorium | Minimalne rusztowanie, silna stabilność regresji |
| Cline | Apache-2 | Agent VS Code z polityką narzędziową | Najwyżej punktowane otwarte rusztowanie w Sonnet 4.5 |
| Devin (Poznanie) | Zastrzeżone | Zarządzana maszyna wirtualna + planista | Pierwsza kategoria produktów „Inżynier oprogramowania AI” |
| Kod Claude'a | Zastrzeżone | Tryby uprawnień + procedury | Lekcja 10 szczegółowo omawia pętlę agenta |

### Dlaczego rusztowania dominują

Proces kodowania to trajektoria o długim horyzoncie (lekcja 1). Niezawodność związków w różnych etapach. Trzy miejsca, w których za rusztowanie kupuje się punkty:

1. **Pobieranie**: znalezienie odpowiednich plików do odczytania to ciche wąskie gardło. ACI agenta SWE, indeks plików OpenHands i mapa repo Aidera atakują to.
2. **Pętla weryfikatora**: uruchamianie testów, odczytywanie śladów stosu i ponowna próba to ponad 10-punktowa delta w środowisku SWE.
3. **Powstrzymywanie awarii**: piaskownica, która wycofuje się w przypadku błędu, zapobiega kumulowaniu się uszkodzeń. Ten sam model z pętlą weryfikatora i bez niej wygląda jak dwa różne produkty.

### Nasycenie wzorcowe i rozkład rzeczywisty

Zarówno autorzy OpenHands, jak i Epoch AI zauważają, że platforma SWE Verified ma łatwy ogon: 161 z 500 zadań wymaga tylko 1–2 linii zmian. Wysokie wyniki wynikają częściowo z tego ogona. SWE-bench Pro ogranicza do ponad 10 zmian linii i zwraca wyniki w zakresie 23–59% nawet w przypadku systemów granicznych. Twoja dystrybucja produkcji jest prawie na pewno bliższa Pro niż Verified.

Konsekwencje wyboru agenta: uruchom podzbiór własnego rejestru błędów w stylu Pro. Wynik, który się liczy, to wynik zadań reprezentatywnych dla tego, co wysyłasz.

## Użyj tego

`code/main.py` porównuje dwa rusztowania agentów zabawek w ustalonym rozkładzie minizadań:

1. Rusztowanie **wywołania narzędzia JSON**, które wykonuje jedną akcję na turę.
2. Rusztowanie **CodeAct**, które może emitować mały fragment kodu Pythona na akcję.

Obydwa używają „modelu” pośredniczącego (reguły deterministyczne), więc porównanie izoluje szkielet od jakości modelu. Dane wyjściowe pokazują, że rusztowanie CodeAct rozwiązuje więcej zadań w mniejszej liczbie tur kosztem większego promienia wybuchu na akcję.

## Wyślij to

`outputs/skill-scaffold-audit.md` pomaga w audytowaniu proponowanego szkieletu agenta kodującego przed jego przyjęciem: jakość pobierania, obecność weryfikatora, izolacja piaskownicy i dopasowanie wzorca do dystrybucji.

## Ćwiczenia

1. Uruchom `code/main.py`. Ile tur wykonuje każde rusztowanie przy tym samym zestawie zadań? Jaki jest promień wybuchu każdego z nich?

2. Przeczytaj artykuł OpenHands (arXiv:2407.16741). W artykule argumentowano, że CodeAct pokonuje wywołania narzędzi JSON w przypadku złożonych zadań. Zidentyfikuj jeden rodzaj awarii, o którym mowa w artykule, i napisz jedno zdanie o tym, kiedy ten tryb będzie dominował w produkcji.

3. Wybierz jedno zadanie ze swojego rejestru błędów, które wymagałoby ponad 10 linii zmian w dwóch plikach. Oszacuj kompleksowe prawdopodobieństwo sukcesu modelu granicznego w ramach (a) wywołań narzędzi JSON i (b) CodeAct. Uzasadnij lukę.

4. SWE-bench Verified zawiera 161 zadań jednoplikowych, 1–2 liniowych. Skonstruuj wynik, który je wyklucza. W jaki sposób następuje przetasowanie tabeli liderów?

5. Przeczytaj „Przedstawiamy zweryfikowaną wersję SWE” (OpenAI). Wyjaśnij konkretną metodologię stosowaną w celu usunięcia niejednoznacznych zadań i wskaż jedną kategorię, którą pominęłaby selekcja.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|---|---|---|
| Ławka SWE | „Porównanie kodowania” | Prawdziwe problemy z GitHubem dotyczące poprawek i zestawów testów opartych na faktach |
| Zweryfikowano w SWE-bench | „Wyczyszczony podzbiór” | 500 zadań wybranych przez ludzi, łatwiejszy ogon |
| SWE-bench Pro | „Trudniejszy podzbiór” | Ponad 10 zmian linii; granica wynosi 23–59% |
| Akt Kodeksu | „Kod jako działanie” | Agent emituje Pythona; Jądro w stylu Jupytera jest wykonywane w piaskownicy |
| Wywołanie narzędzia JSON | „Wywołanie funkcji” | Każda akcja to ustrukturyzowany ładunek JSON sprawdzany przed wykonaniem |
| Rusztowanie | „Struktura agenta” | Pobieranie + planista + wykonawca + pętla weryfikatora wokół modelu bazowego |
| ACI (interfejs agent-komputer) | „Format agenta SWE” | Zestaw poleceń zaprojektowany z myślą o ergonomii LLM, a nie ludzkich skorupach |
| Pętla weryfikatora | „Test i ponowna próba” | Uruchom testy, odczytaj dane wyjściowe, zrewiduj łatkę; największy pozamodelowy wzrost niezawodności |

## Dalsze czytanie

- [Jimenez i in. — SWE-bench](https://www.swebench.com/) — oryginalny punkt odniesienia i metodologia.
- [OpenAI — Przedstawiamy zweryfikowany SWE-bench](https://openai.com/index/introducing-swe-bench-verified/) — jak zbudowano wybrany podzbiór.
- [Wang i in. — OpenHands: otwarta platforma dla twórców oprogramowania AI](https://arxiv.org/abs/2407.16741) — Architektura CodeAct i projektowanie strumieni zdarzeń.
- [Epoch AI — tabela wyników SWE-bench](https://epoch.ai/benchmarks) — wyniki na żywo.
- [Anthropic — autonomia agenta pomiarowego](https://www.anthropic.com/research/measuring-agent-autonomy) — długoterminowe ramy niezawodności agenta kodującego.