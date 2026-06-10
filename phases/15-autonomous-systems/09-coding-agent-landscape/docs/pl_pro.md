# Krajobraz autonomicznych agentów kodujących (2026)

> Wskaźnik skuteczności na benchmarku SWE-bench Verified wzrósł z 4% do 80,9% w niecałe trzy lata. Ten sam model Claude Sonnet 4.5 uzyskał 43,2% w środowisku SWE-agent v1 oraz 59,8% przy użyciu Cline – rusztowanie (scaffold) wokół modelu ma obecnie tak samo duże znaczenie jak sam model bazowy. OpenHands (dawniej OpenDevin) to najaktywniejsza platforma na licencji MIT, a jej pętla CodeAct wykonuje kod Pythona bezpośrednio w piaskownicy (sandbox) zamiast tradycyjnych wywołań narzędzi za pomocą JSON. Główne wyniki (headline numbers) skrywają jednak problem metodologiczny: 161 z 500 zadań w SWE-bench Verified wymaga zmiany zaledwie 1–2 linii kodu, podczas gdy skuteczność na trudniejszym SWE-bench Pro (zmiany powyżej 10 linii) wynosi od 23% do 59% dla tych samych modeli.

**Typ:** Ucz się
**Języki:** Python (porównanie wywołań systemowych w bibliotece standardowej, CodeAct oraz JSON)
**Wymagania wstępne:** Faza 14 · 07 (Użycie narzędzi), Faza 15 · 01 (Agenci z dalekiego horyzontu)
**Czas:** ~45 minut

## Problem

Pytanie „który agent kodujący jest najlepszy?” jest postawione wadliwie. Prawidłowe pytanie brzmi: jaką rzeczywistą niezawodność uzyskam przy rozkładzie zadań odpowiadającym specyfice mojej pracy oraz rusztowaniu, które zamierzam uruchomić produkcyjnie?

W latach 2022–2026 programiści zrozumieli, że to właśnie rusztowanie (scaffold) – obejmujące warstwę wyszukiwania plików, planer, piaskownicę, pętlę edycji i weryfikacji oraz format informacji zwrotnej – decyduje o sukcesie. Claude Sonnet 4.5 w środowisku SWE-agent v1 uzyskał wynik 43,2% na zbiorze SWE-bench Verified; ten sam model umieszczony w autonomicznym rusztowaniu Cline osiągnął 59,8%. To 16,6 punktu procentowego bezwzględnej różnicy na tych samych wagach modelu. Model podstawowy to jedynie komponent; pętla to gotowy produkt.

Dodatkowym problemem jest to, że wysokie wskaźniki na popularnych testach mogą maskować rzeczywiste regresje. Benchmark SWE-bench Verified zbliża się do nasycenia głównie dzięki puli łatwych zadań (161 z 500 zadań wymagających modyfikacji ≤ 2 linii kodu). Rzeczywistą skuteczność znacznie lepiej mierzy się na trudniejszych rozkładach, takich jak SWE-bench Pro (zmiany powyżej 10 linii kodu), gdzie liderzy tabel osiągają obecnie skromniejsze wyniki w granicach 23–59%.

## Koncepcja

### SWE-bench w pigułce

Zbiór SWE-bench (Jimenez i in.) bazuje na rzeczywistych problemach (issues) zgłaszanych w serwisie GitHub, do których dołączono oficjalne poprawki (patches) oraz powiązane z nimi testy jednostkowe. Zadaniem agenta jest wygenerowanie poprawki, która pomyślnie zaliczy cały zestaw testów. SWE-bench Verified (OpenAI, 2024) to wyselekcjonowany przez człowieka podzbiór 500 zadań, z którego usunięto zgłoszenia niejednoznaczne lub zepsute. SWE-bench Pro to znacznie trudniejszy następca, wymagający modyfikacji ponad 10 linii kodu, na którym skuteczność czołowych agentów wynosi obecnie od 23% do 59%.

### Jak wyglądała krzywa rozwoju 2022 → 2026

- **2022**: Pierwsze modele badawcze osiągają zaledwie ~4% skuteczności na surowym zbiorze SWE-bench.
- **2024**: GPT-4 połączony z rusztowaniem w stylu Devina uzyskuje ~14%, a SWE-agent osiąga ~12%.
- **2025**: Modele Claude 3.5/3.7 Sonnet w połączeniu z Aiderem i SWE-agentem wkraczają w przedział 40–55%.
- **2026**: Claude Sonnet 4.5 oraz jego najgroźniejsi konkurenci osiągają wyniki na poziomie 70–80%+ na SWE-bench Verified. Tabela liderów Epoch AI śledzi te postępy na żywo.

Ten gwałtowny wzrost wynika z nałożenia się trzech czynników: lepszych modeli bazowych, doskonalszych struktur rusztowań (CodeAct, autorefleksja, pętle weryfikacyjne) oraz czyszczenia samych benchmarków z szumu (wersje Verified).

### Porównanie: CodeAct a wywołania narzędzi przez JSON

OpenHands (All-Hands-AI, arXiv:2407.16741, dawniej OpenDevin) przyjął konkretne założenie architektoniczne: zamiast generować ustrukturyzowane wywołania narzędzi w formacie JSON (które host musi zdekodować i wykonać), model generuje bezpośrednio kod w języku Python, który jądro w stylu Jupytera uruchamia wewnątrz piaskownicy. Dzięki temu agent może w ramach jednej akcji tworzyć pętle na plikach, łączyć ze sobą narzędzia i samodzielnie obsługiwać wyjątki.

Kompromis:

- **Wywołania narzędzi przez JSON:** każda akcja to jedna tura; wysoka łatwość audytowania; ograniczona kompozycyjność; domyślnie bezpieczne, ponieważ każde wywołanie przechodzi przez zewnętrzny moduł weryfikacji.
- **CodeAct:** pojedyncza akcja może stanowić kompletny program; wysoka kompozycyjność; wymaga bardzo silnej piaskownicy (OpenHands opiera się na kontenerach Docker); potencjalne tryby awarii obejmują wszystko, na co pozwala powłoka piaskownicy.

Oba te podejścia są stosowane produkcyjnie. CodeAct dominuje na platformach open-source (OpenHands, smolagents). Wywołania JSON pozostają standardem w usługach zarządzanych (zarządzani agenci Anthropic, asystenci OpenAI), gdzie dostawca platformy w pełni kontroluje środowisko wykonawcze.

### Przegląd struktur rusztowań w 2026 roku

| Rusztowanie | Licencja | Model wykonawczy | Kluczowa cecha |
|---|---|---|---|
| OpenHands (OpenDevin) | MIT | CodeAct w Dockerze | Najaktywniejsza platforma otwarta; odtwarzanie strumienia zdarzeń |
| SWE-agent | MIT | Interfejs agent-komputer (ACI) | Pierwsze kompletne rusztowanie zaprojektowane pod SWE-bench |
| Aider | Apache-2 | Modyfikacja przez diff w lokalnym repozytorium | Lekkie rusztowanie o doskonałej odporności na regresję |
| Cline | Apache-2 | Wtyczka do VS Code z kontrolą uprawnień | Najwyżej oceniane otwarte rusztowanie w połączeniu z Sonnet 4.5 |
| Devin (Cognition) | Zastrzeżone | Dedykowana maszyna wirtualna + planer | Pierwszy komercyjny produkt pozycjonowany jako „Inżynier AI” |
| Claude Code | Zastrzeżone | Interaktywne tryby uprawnień i procedur | Autorskie narzędzie od Anthropic optymalizujące pętlę agenta |

### Dlaczego jakość rusztowania decyduje o sukcesie

Proces programowania to długi horyzont działań (Lekcja 1). Niezawodność systemu kumuluje się na każdym etapie. Trzy kluczowe obszary, w których odpowiednie rusztowanie przynosi największe zyski:

1. **Wyszukiwanie informacji (retrieval):** znalezienie odpowiednich plików do edycji to ukryte wąskie gardło wielu systemów. Narzędzia takie jak ACI w SWE-agencie, indeksowanie plików w OpenHands czy repo-mapy w Aiderze skutecznie rozwiązują ten problem.
2. **Pętla weryfikacji:** automatyczne uruchamianie testów, analiza śladów stosu (stack traces) i ponawianie prób dają przyrost skuteczności przekraczający 10 punktów procentowych na SWE-bench.
3. **Izolacja i obsługa błędów:** piaskownica potrafiąca wycofać zmiany po wykryciu awarii zapobiega kumulacji uszkodzeń kodu. Ten sam model z pętlą weryfikacji i bez niej zachowuje się jak dwa zupełnie różne produkty.

### Nasycenie benchmarków a rzeczywista dystrybucja zadań

Zarówno twórcy OpenHands, jak i analitycy Epoch AI wskazują, że wysokie wyniki na SWE-bench Verified wynikają z obecności łatwych zadań (161 zadań wymagających modyfikacji zaledwie 1–2 linii). Zbiór SWE-bench Pro odrzuca te proste przypadki i stawia przed modelami wymaganie zmian powyżej 10 linii kodu, co obniża skuteczność najlepszych systemów do poziomu 23–59%. Rzeczywiste zgłoszenia i błędy w Twoim projekcie będą niemal na pewno znacznie bliższe specyfice wersji Pro niż Verified.

Wniosek: przy wyborze agenta przetestuj go na podzbiorze własnych, reprezentatywnych błędów o stopniu skomplikowania odpowiadającym wersji Pro. Liczy się tylko ten wynik, który odzwierciedla Twoje rzeczywiste środowisko produkcyjne.

## Użyj tego

Skrypt `code/main.py` porównuje działanie dwóch uproszczonych struktur rusztowań na zadanym zestawie mini-zadań:

1. Rusztowanie **wywołania narzędzi przez JSON**, wykonujące jedną akcję na turę.
2. Rusztowanie **CodeAct**, potrafiące wygenerować i uruchomić krótki skrypt w Pythonie w ramach jednej akcji.

Oba systemy korzystają z tego samego, deterministycznego modelu pomocniczego, co pozwala na pełne odizolowanie wpływu samego rusztowania na wynik. Dane wyjściowe pokazują, że rusztowanie CodeAct radzi sobie z zadaniami w mniejszej liczbie tur, jednak kosztem większego ryzyka niekontrolowanych skutków ubocznych (promień rażenia / blast radius) przy pojedynczej akcji.

## Wdrożenie

Szablon `outputs/skill-scaffold-audit.md` ułatwia przeprowadzenie audytu proponowanego rusztowania przed jego wdrożeniem: ocenia jakość wyszukiwania plików, obecność pętli weryfikacyjnej, szczelność piaskownicy oraz dopasowanie testów do specyfiki Twojego kodu.

## Ćwiczenia

1. Uruchom `code/main.py`. Ile tur potrzebuje każde z rusztowań do rozwiązania tego samego zestawu zadań? Jaki jest promień rażenia (blast radius) dla każdego z nich?

2. Przeczytaj publikację na temat OpenHands (arXiv:2407.16741). Autorzy dowodzą, że CodeAct zdecydowanie przewyższa wywołania JSON przy złożonych zadaniach. Wskaż jeden typ awarii opisany w artykule i napisz jedno zdanie o tym, w jakich sytuacjach produkcyjnych ten błąd będzie dominował.

3. Wybierz z własnego repozytorium jedno zadanie wymagające zmiany ponad 10 linii kodu w co najmniej dwóch różnych plikach. Oszacuj prawdopodobieństwo sukcesu modelu pionierskiego w architekturze: (a) wywołań JSON oraz (b) CodeAct. Uzasadnij różnicę.

4. Zbiór SWE-bench Verified zawiera 161 zadań jednoplikowych o długości modyfikacji 1–2 linii. Zaproponuj metodę ich odfiltrowania ze wskaźników. Jak Twoim zdaniem zmieniłaby się wówczas tabela liderów?

5. Przeczytaj artykuł „Introducing SWE-bench Verified” od OpenAI. Wyjaśnij szczegółowo metodologię zastosowaną do eliminacji błędnych i niejednoznacznych zadań i wskaż jedną kategorię błędów, której ta procedura mogła nie wykryć.

## Kluczowe terminy

| Termin | Co mówią ludzie | Co to naprawdę oznacza |
|---|---|---|
| SWE-bench | „Benchmark programowania” | Zbiór testowy bazujący na rzeczywistych issue z GitHuba i powiązanych z nimi poprawkach oraz testach jednostkowych |
| SWE-bench Verified | „Oczyszczona wersja testów” | Podzbiór 500 zadań zweryfikowanych przez ludzi, pozbawiony szumu, ale zawierający dużą pulę łatwych zadań |
| SWE-bench Pro | „Trudny zestaw testowy” | Zadania wymagające zmiany ponad 10 linii kodu; skuteczność modeli wynosi tu zaledwie 23–59% |
| CodeAct | „Kod jako akcja” | Architektura, w której agent generuje kod w Pythonie wykonywany bezpośrednio w piaskownicy |
| Wywołanie narzędzia JSON | „Wywołanie funkcji” | Tradycyjna komunikacja, gdzie każda akcja to ustrukturyzowany format JSON weryfikowany przed uruchomieniem |
| Rusztowanie / Szkielet | „Struktura wokół modelu” | Kod zarządzający wyszukiwaniem plików, planowaniem zadań i weryfikacją wyników wokół modelu LLM |
| ACI (Agent-Computer Interface) | „Interfejs agent-komputer” | Zestaw uproszczonych komend systemowych zaprojektowanych pod kątem ergonomii pracy modeli LLM, a nie ludzi |
| Pętla weryfikacji | „Uruchom testy i popraw” | Proces automatycznego uruchamiania testów i poprawiania kodu na bazie błędów; kluczowy czynnik wzrostu skuteczności |

## Dalsze czytanie

- [Strona główna projektu SWE-bench](https://www.swebench.com/) – dokumentacja i metodologia.
- [Introducing SWE-bench Verified (OpenAI)](https://openai.com/index/introducing-swe-bench-verified/) – szczegóły selekcji podzbioru zadań.
- [Wang i in. — OpenHands: An Open Platform for AI Software Developers](https://arxiv.org/abs/2407.16741) – architektura CodeAct i obsługa strumieni zdarzeń.
- [Epoch AI — SWE-bench Leaderboard](https://epoch.ai/benchmarks) – wyniki i statystyki na żywo.
- [Anthropic — Measuring Agent Autonomy](https://www.anthropic.com/research/measuring-agent-autonomy) – długofalowe ramy oceny niezawodności agentów kodujących.
