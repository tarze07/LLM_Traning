# Bloki pamięci i obliczenia w czasie bezczynności (Letta)

> W 2024 roku projekt MemGPT został przekształcony w Lettę. Ewolucja tej architektury przyniosła dwie kluczowe innowacje: dyskretne bloki pamięci funkcjonalnej (Memory Blocks), które model może bezpośrednio edytować, oraz procesy działające w czasie bezczynności (Sleep-time compute), które asynchronicznie konsolidują pamięć, gdy główny agent nie wykonuje żadnych zadań. Pozwala to na skalowanie pamięci poza ramy pojedynczej konwersacji.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania:** Faza 14 · 07 (MemGPT)
**Czas:** ~75 minut

## Cele nauczania

- Wymień trzy poziomy pamięci wykorzystywane przez Lettę (Core, Recall, Archival) i opisz rolę każdego z nich.
- Wyjaśnij wzorzec bloków pamięci (Memory Blocks): blok Human (dane użytkownika), blok Persona (tożsamość agenta) oraz bloki definiowane przez użytkownika jako obiekty pierwszej klasy (first-class citizens).
- Opisz koncepcję obliczeń w czasie bezczynności (Sleep-time compute) i wyjaśnij, dlaczego proces ten zachodzi poza główną ścieżką wykonania oraz dlaczego może wykorzystywać mocniejszy model niż główny agent.
- Zaimplementuj uproszczony system składający się z dwóch agentów, w którym agent główny (Primary Agent) generuje odpowiedzi, a agent pomocniczy (Sleep-time Agent) konsoliduje bloki pamięci w przerwach między interakcjami.

## Problem

Architektura MemGPT (Lekcja 07) uporządkowała procesy kontroli pamięci wirtualnej. Jednak w środowiskach produkcyjnych pojawiły się trzy istotne problemy:

1. **Opóźnienie (Latency)**: Wszystkie operacje na pamięci są wykonywane synchronicznie w głównym wątku. Jeśli agent musi uporządkować, streścić lub uzgodnić fakty, użytkownik musi na to czekać, co drastycznie zwiększa opóźnienie systemu (szczególnie opóźnienie ogonowe – tail latency).
2. **Degradacja pamięci**: Nowe informacje nieustannie się kumulują, co prowadzi do powstawania sprzecznych faktów. W efekcie wyszukiwanie w bazie zaczyna zwracać nieaktualne dane.
3. **Brak struktury**: Płaski magazyn archiwalny nie pozwala na definiowanie ról informacji (np. „dane o użytkowniku muszą być stale obecne w prompcie, tożsamość agenta również, a blok zadań powinien być dynamicznie podmieniany w trakcie sesji”).

Projekt Letta (letta.com) rozwiązuje te problemy. Wprowadzenie bloków pamięci (Memory Blocks) strukturyzuje dane, a obliczenia w czasie bezczynności (Sleep-time compute) przenoszą proces konsolidacji danych poza główny przepływ wykonania.

## Koncepcja

### Trzy poziomy

| Poziom | Zakres | Gdzie się znajduje | Kto modyfikuje |
|------|-------|----------------|------------|
| Core | Zawsze widoczny | Bezpośrednio w głównym prompcie | Wywołanie narzędzia przez agenta lub procesy tła (Sleep-time) |
| Recall | Historia konwersacji | Dostępny do przeszukania | Automatyczny zapis kolejnych tur |
| Archival | Dowolne fakty | Baza wektorowa, KV, baza grafowa | Wywołanie narzędzia przez agenta lub procesy tła (Sleep-time) |

Warstwa Core odpowiada za pamięć podręczną (rdzeń z MemGPT). Recall pełni funkcję historii rozmów, z której najstarsze wpisy są automatycznie usuwane. Archival stanowi zewnętrzną bazę danych. Ten podział pozwala uniknąć przeciążenia, z którym borykała się dwupoziomowa struktura MemGPT.

### Bloki pamięci

Blok pamięci (Memory Block) to ustrukturyzowany, trwały i edytowalny segment warstwy Core. W oryginalnej specyfikacji MemGPT zdefiniowano dwa z nich:

- **Blok Human**: Informacje i fakty o użytkowniku (imię, rola, preferencje, cele).
- **Blok Persona**: Definicja tożsamości agenta (charakter, ton wypowiedzi, ograniczenia).

Letta rozszerza tę koncepcję na dowolne bloki definiowane przez programistę: np. blok `Task` (dla bieżącego celu), blok `Project` (dla danych o strukturze kodu) lub blok `Safety` (zabezpieczenia i twarde ograniczenia). Każdy blok opisany jest przez atrybuty: `id`, `label` (etykieta), `value` (zawartość), `limit` (maksymalny rozmiar w znakach) oraz `description` (opis ułatwiający modelowi decyzję o modyfikacji).

Modyfikacja bloków odbywa się za pomocą dedykowanych narzędzi:

- `block_append(label, text)`
- `block_replace(label, old, new)`
- `block_read(label)`
- `block_summarize(label)` – kondensuje zawartość bloku, gdy ten zbliża się do limitu rozmiaru.

### Obliczanie czasu bezczynności (Sleep-time compute)

Kluczowa innowacja: uruchomienie pomocniczego agenta w tle, poza ścieżką krytyczną interakcji. Agent działający w czasie bezczynności (Sleep-time Agent) analizuje przebieg rozmów i strukturę kodu, zapisuje wyciągnięte wnioski (`learned_context`) we wspólnych blokach pamięci oraz porządkuje bazę archiwalną (konsoliduje lub usuwa nieaktualne wpisy).

Kluczowe korzyści:

- **Brak opóźnień (No latency overhead)**: Główny proces nie jest blokowany przez operacje porządkowania bazy.
- **Możliwość użycia silniejszych modeli**: Procesy w tle mogą korzystać z bardziej zaawansowanych, wolniejszych modeli, ponieważ czas odpowiedzi nie jest tu krytyczny.
- **Dedykowany czas na konsolidację danych**: Deduplikacja, streszczanie i rozwiązywanie konfliktów zachodzą w czasie bezczynności systemu.

Architektura ta naśladuje ludzki mózg: wykonujemy zadanie w ciągu dnia, a konsolidacja wiedzy i przenoszenie informacji do pamięci długoterminowej zachodzi w czasie snu.

### Letta V1 i natywne rozumowanie

Wersja Letta V1 (`letta_v1_agent`) odchodzi od wymuszania wywołań `send_message`, sygnału taktującego (heartbeat) oraz wstrzykiwania tokenów typu `Thought:` na rzecz natywnego rozumowania (native reasoning). Nowoczesne interfejsy API, takie jak OpenAI Responses API czy Anthropic Messages API (z obsługą rozszerzonego myślenia), przesyłają strumień myśli na osobnym, dedykowanym kanale. Pętla sterująca wciąż opiera się na wzorcu ReAct, jednak ścieżka myślowa ma charakter ustrukturyzowany, a nie tekstowy.

### Słabe strony

- **Rozrost bloków (Block bloating)**: Nieograniczone dopisywanie danych za pomocą `block_append` szybko zapełnia dostępny limit. Rozwiązaniem jest dodanie modułu streszczającego, który uruchamia się przed przekroczeniem limitu.
- **Cichy dryf**: Agent w tle modyfikuje zawartość bloku, a główny proces nie jest o tym powiadamiany. Rozwiązaniem jest wersjonowanie bloków i logowanie zmian.
- **Zatruta konsolidacja**: Sleep-time Agent analizuje niezaufane dane wejściowe. Zabezpieczenia z Lekcji 27 muszą być stosowane również w procesach działających w tle.

## Zbuduj to

Plik `code/main.py` implementuje:

- `Block` – struktura przechowująca id, etykietę, wartość, limit znaków oraz opis.
- `BlockStore` – operacje CRUD oraz funkcja pomocnicza `near_limit(label)` sprawdzająca zapełnienie bloku.
- Uproszczony system dwuagentowy: `PrimaryAgent` obsługuje interakcję z użytkownikiem, a `SleepTimeAgent` porządkuje dane w tle.
- Ślad wykonania pokazujący trzyetapowy dialog z zapisami w blokach oraz fazę bezczynności (sleep-time), która streszcza blok i unieważnia nieaktualny fakt.

Uruchomienie:

```
python3 code/main.py
```

Logi pokazują wyraźny podział ról: tury obsługiwane przez głównego agenta są szybkie i generują nieprzetworzone zapisy, natomiast proces w tle (sleep-time) kompaktuje dane i usuwa zbędne wpisy.

## Użyj tego

- **Letta** (letta.com): Referencyjna implementacja tego wzorca, dostępna w wersji chmurowej oraz do samodzielnego hostowania.
- **Claude Agent SDK (Skills)**: Wykorzystanie koncepcji bloków wiedzy – umiejętność (skill) stanowi wersjonowany, dynamicznie ładowany segment instrukcji.
- **Własne wdrożenia**: Rozwiązanie dla zespołów wymagających pełnej kontroli nad bazą danych. Warto zachować zgodność z interfejsem Letta API w celu ułatwienia ewentualnej migracji w przyszłości.

## Wyślij to

Plik `outputs/skill-memory-blocks.md` opisuje proces tworzenia systemu bloków pamięci w stylu Letta z obsługą procesów w tle, regułami bezpieczeństwa oraz integracją cytowań.

## Ćwiczenia

1. Zaimplementuj funkcję `block_summarize` zastępującą zawartość bloku podsumowaniem wygenerowanym przez model LLM, gdy `near_limit` zwraca wartość true. Dobierz próg aktywacji, który minimalizuje liczbę wywołań streszczających, zapobiegając jednocześnie przepełnieniu bloku.
2. Zaimplementuj mechanizm deduplikacji w tle: jeśli dwa rekordy w bazie archiwalnej pokrywają się w ponad 90%, scal je w jeden wpis. Proces ten uruchamiaj wyłącznie w fazie bezczynności (sleep-time), nigdy w głównym wątku.
3. Wprowadź wersjonowanie bloków. Przy każdej modyfikacji zapisuj poprzednią wartość oraz wygenerowany diff. Udostępnij funkcję `block_history(label)` ułatwiającą debugowanie zmian w pamięci agenta.
4. Traktuj procesy działające w tle jako komponenty o ograniczonym zaufaniu. Wszelkie modyfikacje bloków Persona lub Safety dokonywane przez Sleep-time Agent powinny wymagać zatwierdzenia (walidacji) przez niezależny moduł kontrolny.
5. Zmodyfikuj kod w oparciu o oficjalne Letta API (`letta_v1_agent`). Jak wpływa to na strukturę bloków i w jaki sposób wykorzystanie natywnego rozumowania modyfikuje logi wykonania?

## Kluczowe terminy

| Termin | Potoczne określenie | Co to w rzeczywistości oznacza |
|------|----------------|--------------------------------------|
| Blok pamięci | „Edytowalny segment promptu” | Ustrukturyzowany, trwały segment pamięci podręcznej (Core) edytowalny przez model. |
| Blok Human | „Profil użytkownika” | Informacje i preferencje dotyczące użytkownika, na stałe przypięte w sekcji Core. |
| Blok Persona | „Profil agenta” | Zdefiniowana tożsamość, styl komunikacji i reguły zachowania agenta, przypięte w sekcji Core. |
| Obliczenia w czasie bezczynności | „Sleep-time compute” | Uruchamianie procesów porządkowania i konsolidacji bazy danych w tle, poza głównym wątkiem. |
| Core / Recall / Archival | „Warstwy pamięci” | Trójwarstwowy podział pamięci: pamięć robocza (prompt) / historia rozmowy / zewnętrzna baza danych. |
| Limit bloku | „Rozmiar maksymalny” | Limit znaków dla pojedynczego bloku pamięci, wymuszający jego kompaktowanie. |
| Natywne rozumowanie | „Kompilacja myśli” | Strumieniowanie ścieżki myślowej modelu na wydzielonym kanale API (poza głównym promptem). |
| Learned Context | „Wnioski z bezczynności” | Nowe fakty wyciągnięte przez Sleep-time Agent i zapisane we wspólnych blokach pamięci. |

## Dalsze czytanie

- [Letta, blog o blokach pamięci](https://www.letta.com/blog/memory-blocks) — wzór blokowy
- [Letta, blog dotyczący obliczeń w czasie snu](https://www.letta.com/blog/sleep-time-compute) — konsolidacja asynchroniczna
- [Letta, Rearchitecting the Agent Loop](https://www.letta.com/blog/letta-v1-agent) — przepisanie natywnego rozumowania
- [Packer et al., MemGPT (arXiv:2310.08560)](https://arxiv.org/abs/2310.08560) — pochodzenie
