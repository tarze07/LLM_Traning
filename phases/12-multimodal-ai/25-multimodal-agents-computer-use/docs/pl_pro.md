# Agenci multimodalni i korzystanie z komputera (Capstone)

> Najnowocześniejszym produktem (frontier product) w 2026 roku jest multimodalny agent, który odczytuje zrzuty ekranu, klika przyciski, nawiguje po interfejsach internetowych, wypełnia formularze i realizuje kompleksowe przepływy pracy (end-to-end workflows). Modele SeeClick i CogAgent (2024) udowodniły, że jest to skuteczny sposób uziemiania GUI (GUI grounding). W Ferret-UI dodano obsługę urządzeń mobilnych. ChartAgent wprowadził wizualne wykorzystanie narzędzi do analizy wykresów. VisualWebArena i AgentVista (2026) to benchmarki wyznaczające obecne granice możliwości – i nawet modele Gemini 3 Pro oraz Claude Opus 4.7 uzyskują w nich jedynie ~30% skuteczności na trudnych zadaniach AgentVista. Ten projekt końcowy (capstone) łączy wszystkie wątki Fazy 12: percepcję (VLM w wysokiej rozdzielczości), rozumowanie (LLM wykorzystujące narzędzia), uziemianie (generowanie współrzędnych), pamięć długoterminową oraz ewaluację.

**Typ:** Projekt końcowy (Capstone)
**Języki:** Python (biblioteka standardowa, schemat akcji + szkielet pętli agenta)
**Wymagania wstępne:** Faza 12 · 05 (LLaVA), Faza 12 · 09 (Qwen-VL JSON), Faza 14 (Architektura agentów)
**Czas:** ~240 minut

## Cele nauczania

- Zaprojektuj multimodalną pętlę agenta: postrzegaj → rozumuj → działaj → obserwuj → powtarzaj.
- Zbuduj schemat wyjściowy uziemiania GUI (współrzędne kliknięć, wpisywanie tekstu, przewijanie, przeciąganie), który model VLM może generować w formacie JSON.
- Porównaj agentów działających wyłącznie w oparciu o zrzuty ekranu (screenshot-only) z agentami wykorzystującymi drzewo dostępności (accessibility tree) oraz agentami hybrydowymi.
- Skonfiguruj benchmark ewaluacyjny dla agenta multimodalnego na wydzielonym fragmencie zbioru VisualWebArena.

## Problem

Scenariusz działania na stronie rezerwacyjnej: „Znajdź mi lot do Tokio na 15 kwietnia, miejsce przy przejściu poniżej 800 USD i dokonaj rezerwacji”.

Agent multimodalny musi:

1. Wykonać zrzut ekranu przeglądarki.
2. Przeanalizować zrzut ekranu, adres URL oraz cel w planie działania.
3. Wykonać ustrukturyzowaną akcję: kliknięcie (we współrzędnych x, y), wpisanie „Tokio” (w elemencie E), przewinięcie w dół, zaznaczenie opcji (radio button).
4. Wykonać akcję w przeglądarce.
5. Zaobserwować nowy stan (kolejny zrzut ekranu).
6. Powtarzać procedurę do momentu ukończenia zadania.

Każdy krok to multimodalne wywołanie VLM. Wynik działania VLM musi być poprawnym obiektem JSON gotowym do parsowania. Błędy kumulują się na poszczególnych etapach, dlatego kluczowa jest zdolność do obsługi błędów i samonaprawy (error recovery).

## Koncepcja

### Uziemianie GUI (GUI Grounding)

Uziemianie GUI polega na tym, że na podstawie zrzutu ekranu i instrukcji w języku naturalnym model generuje współrzędne (x, y) punktu, który należy kliknąć (lub wykonać na nim inną akcję).

SeeClick (arXiv:2401.10935) był jednym z pierwszych otwartoźródłowych modeli tej klasy na dużą skalę: dostrojono model VLM na syntetycznych i rzeczywistych danych GUI, a współrzędne były generowane w postaci zwykłego tekstu. Rozwiązanie to działało w praktyce.

CogAgent (arXiv:2312.08914) wprowadził kodowanie obrazu w wysokiej rozdzielczości (1120x1120) dla gęstych interfejsów użytkownika. Wynik: ~84% skuteczności w nawigacji internetowej.

Ferret-UI (arXiv:2404.05719) koncentruje się na mobilnych interfejsach użytkownika i integruje się z danymi dostępności (accessibility) systemu iOS.

Format wyjściowy to zazwyczaj JSON:

```json
{"action": "click", "x": 384, "y": 220, "element_desc": "Search button"}
```

Pole `element_desc` ułatwia obsługę błędów: jeśli współrzędne przesuną się (dryf) między zrzutami ekranu, wskazówka semantyczna pozwala systemowi na ponowne uziemienie (re-grounding).

### Schematy akcji (Action Spaces)

Typowa przestrzeń akcji składa się z 6-10 typów operacji:

- `click`: (x, y)
- `type`: (tekst, x?, y?)
- `scroll`: (kierunek, wartość/dystans)
- `drag`: (x0, y0, x1, y1)
- `select`: (indeks_opcji)
- `hover`: (x, y)
- `navigate`: (url)
- `wait`: (ms)
- `done`: (sukces, wyjaśnienie)

Agent wykonuje jedną akcję na krok. Interfejs automatyzacji przeglądarki wykonuje ją i zwraca zaktualizowany stan.

### Screenshot-only a Drzewo Dostępności

Dwa podejścia do danych wejściowych:

- Screenshot-only: pełny obraz interfejsu bez informacji strukturalnych. Najbardziej uniwersalne podejście; działa z każdą aplikacją.
- Drzewo dostępności (Accessibility Tree): ustrukturyzowana informacja o dostępności z DOM lub interfejsów systemowych iOS/Android. O wiele bardziej niezawodna metoda uziemiania; działa wszędzie tam, gdzie drzewo jest dostępne.
- Hybrydowe: łączy drzewo dostępności (jako stabilne oparcie dla akcji atomowych) ze zrzutami ekranu (dla kontekstu semantycznego).

Produkcyjni agenci, o ile to możliwe, korzystają z podejścia hybrydowego. Narzędzia do automatyzacji przeglądarek (np. Selenium, Playwright + accessibility APIs) zawsze mają dostęp do drzewa; aplikacje desktopowe – tylko czasami.

### Pamięć o długim horyzoncie (Long-Horizon Memory)

Przepływ pracy składający się z 20 kroków generuje 20 zrzutów ekranu. Okno kontekstowe modelu VLM zapełnia się bardzo szybko. Trzy strategie kompresji to:

- Łańcuch podsumowań (Summary chain): co 5 kroków podsumuj dotychczasowy przebieg i usuń stare zrzuty ekranu.
- Pomijanie klatek (Frame skipping): zachowaj pierwszy, ostatni i co trzeci zrzut ekranu.
- Dziennik akcji narzędziowych (Tool execution log): zapisuj podjęte akcje w postaci tekstowego dziennika logów; nie przetwarzaj ponownie historycznych zrzutów ekranu.

Interfejs API Claude do obsługi komputera (Computer Use) wykorzystuje wzorzec dziennika tekstowego. Jest prostszy i bardziej niezawodny.

### Wizualne korzystanie z narzędzi (Visual Tool Use)

ChartAgent (arXiv:2510.04514) wprowadza koncepcję narzędzi wizualnych ułatwiających zrozumienie wykresów: kadrowanie, przybliżanie, OCR, wywoływanie zewnętrznych detektorów. Agent może wygenerować polecenie: „przytnij region (100, 200, 300, 400), a następnie uruchom OCR” jako wywołanie narzędzia. Narzędzie zwraca tekst, a model VLM kontynuuje wnioskowanie.

Wzorzec ten można uogólnić: nakładanie siatek (set-of-mark), adnotacje regionów i zewnętrzne narzędzia detekcji – wszystko to pasuje do schematu „wygeneruj wywołanie narzędzia, odbierz ustrukturyzowaną odpowiedź”.

### Benchmarki 2026

- ScreenSpot-Pro: Baza testowa GUI zawierająca ~1 tys. zrzutów ekranu ze stron internetowych. Najlepsze modele open-source (np. Qwen2.5-VL-72B) uzyskują ~85%. Najbardziej zaawansowane modele komercyjne (SOTA) osiągają ~90%.
- VisualWebArena: Kompleksowe zadania internetowe (sklep e-commerce, fora, ogłoszenia). Najlepsze modele open-source osiągają ~20%, Gemini 3 Pro ~27%.
- AgentVista (arXiv:2602.23166): Najbardziej wymagający benchmark w 2026 roku. Realistyczne scenariusze w 12 domenach. Modele komercyjne (frontier models) uzyskują w nim 27-40%, a modele open-source 10-20%.
- WebArena / Shopping: Starsze benchmarki; ich wyniki zostały już nasycone przez modele klasy frontier.

### Dlaczego to wciąż trudne wyzwanie

Główne ograniczenia wydajności agentów:

1. Uziemianie wizualne obiektów o małej skali: próba kliknięcia małego iksa "X" w rozdzielczości mobilnej często kończy się niepowodzeniem.
2. Planowanie długoterminowe: po wykonaniu około 10 akcji agent ma tendencję do oddalania się od głównego celu.
3. Naprawa błędów (Error recovery): w przypadku nieudanego kliknięcia (np. trafienia w zły przycisk), modele rzadko potrafią wykryć błąd i podjąć próbę naprawy.
4. Kontekst międzykartowy (Cross-tab/page context): przechodzenie między kartami przeglądarki lub wypełnianie długich formularzy prowadzi do utraty informacji o stanie.

Kierunki badań: architektury pamięci, jawne ponowne planowanie (replanning), multimodalna weryfikacja (porównywanie zrzutów ekranu w celu oceny powodzenia akcji).

### Budowa projektu końcowego (Capstone)

Główne zadanie: zbuduj agenta obsługi komputera, który:

1. Odczytuje kod HTML oraz zrzut ekranu symulowanej strony rezerwacji.
2. Planuje wielokrokową sekwencję: wyszukaj → wybierz → wypełnij formularz → prześlij.
3. Generuje akcje w formacie JSON zgodne ze schematem.
4. Ewaluuje model na zestawie 10 zadań testowych.

Lekcja udostępnia szkielet kodu (boilerplate), który można łatwo rozbudować do obsługi rzeczywistej przeglądarki.

## Użycie kodu

Plik `code/main.py` stanowi szkielet projektu końcowego:

- Definicja schematu akcji JSON (10 akcji).
- Symulacja stanu przeglądarki reprezentowana jako słownik (dict).
- Szkielet pętli agenta: pobranie stanu, wygenerowanie akcji, wykonanie akcji, przejście do kolejnego kroku pętli.
- Mini-benchmark składający się z 10 zadań (syntetyczne strony) do pomiaru wskaźnika sukcesu (end-to-end success rate).
- Mechanizm obsługi błędów w przypadku niepowodzenia akcji.

## Dostarczenie projektu

Wynikiem tej lekcji jest plik `outputs/skill-multimodal-agent-designer.md`. Na podstawie opisu docelowego produktu (domena, zestaw akcji, cel ewaluacji), plik ten definiuje pełną pętlę agenta, strategię zarządzania pamięcią, tryb uziemiania oraz oczekiwane wyniki w benchmarkach.

## Ćwiczenia

1. Rozbuduj schemat akcji o narzędzie `screenshot_region` (kadrowanie + przybliżenie). Jakie zadania mogą na tym skorzystać?

2. Zapoznaj się z artykułem AgentVista (arXiv:2602.23166). Opisz najtrudniejszą kategorię zadań i wyjaśnij, dlaczego topowe modele komercyjne wciąż sobie z nią nie radzą.

3. Kompresja pamięci o długim horyzoncie: zaprojektuj łańcuch podsumowań przechowujący na żywo maksymalnie 4 zrzuty ekranu oraz dowolną liczbę wpisów tekstowych w dzienniku.

4. Zbuduj mechanizm obsługi błędów: jakie kroki powinien podjąć agent w przypadku nieudanej akcji (np. gdy nie odnaleziono przycisku)?

5. Porównaj działanie modelu Claude 4.7 w trybie screenshot-only z hybrydowym podejściem modelu Qwen2.5-VL (zrzut ekranu + drzewo dostępności) na zestawie 10 zadań internetowych. Który model radzi sobie lepiej i w jakich typach zadań?

## Kluczowe terminy

| Termin | Potoczne rozumienie | Rzeczywiste znaczenie |
|------|-----------------|--------------------------------------|
| Uziemianie GUI (GUI Grounding) | „Klikanie współrzędnych” | Generowanie przez model współrzędnych (x, y) celu wskazanego w instrukcji na podstawie zrzutu ekranu |
| Schemat działania (Action Schema) | „Definicje narzędzi” | Opis w formacie JSON dozwolonych akcji (kliknięcie, wpisywanie, przewijanie, przeciąganie) |
| Drzewo dostępności (Accessibility Tree) | „Strukturalny DOM” | Hierarchia elementów interfejsu przystosowana do odczytu maszynowego przez API przeglądarki lub systemu operacyjnego (iOS/Android) |
| Agent hybrydowy | „Zrzut ekranu + drzewo” | Agent korzystający zarówno z obrazu, jak i informacji strukturalnych; rozwiązanie bardziej niezawodne niż każde z nich osobno |
| Korzystanie z narzędzi wizualnych | „Przybliżanie/kadrowanie/detekcja” | Wywoływanie przez agenta zewnętrznych narzędzi wizyjnych (OCR, detektory obiektów) w trakcie realizacji planu |
| Łańcuch podsumowań (Summary Chain) | „Kompresja pamięci” | Okresowe tworzenie tekstowych podsumowań historii działań w celu zastąpienia nimi obszernych historycznych zrzutów ekranu |
| VisualWebArena | „Kompleksowy benchmark webowy E2E” | Benchmark z 2024 roku służący do ewaluacji zadań internetowych realizowanych od początku do końca |
| AgentVista | „Trudny benchmark 2026” | Realistyczne scenariusze przepływów pracy w 12 domenach; nawet Gemini 3 Pro osiąga w nim jedynie ~30% |

## Dalsze czytanie

- [Cheng i in. — SeeClick (arXiv:2401.10935)](https://arxiv.org/abs/2401.10935)
- [Hong i in. — CogAgent (arXiv:2312.08914)](https://arxiv.org/abs/2312.08914)
- [Ty i in. — Ferret-UI (arXiv:2404.05719)](https://arxiv.org/abs/2404.05719)
- [ChartAgent (arXiv:2510.04514)](https://arxiv.org/abs/2510.04514)
- [Koh i in. — VisualWebArena (arXiv:2401.13649)](https://arxiv.org/abs/2401.13649)
- [AgentVista (arXiv:2602.23166)](https://arxiv.org/abs/2602.23166)
