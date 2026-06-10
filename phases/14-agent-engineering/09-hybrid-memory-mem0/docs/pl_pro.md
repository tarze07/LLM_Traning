# Pamięć hybrydowa: wektor + graf + KV (Mem0)

> Mem0 (Chhikara i in., 2025) traktuje pamięć jako trzy równoległe zasoby — wektor dla podobieństwa semantycznego, KV dla szybkiego wyszukiwania faktów oraz graf dla wnioskowania o relacjach między jednostkami. Warstwa punktacji łączy te trzy źródła podczas pobierania danych. Jest to standard produkcyjny pamięci zewnętrznej na rok 2026.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 07 (MemGPT), Faza 14 · 08 (Bloki Letta)
**Czas:** ~75 minut

## Cele nauczania

- Wyjaśnij, dlaczego pojedyncza pamięć (tylko wektorowa, tylko grafowa lub tylko typu klucz-wartość) jest niewystarczająca dla agenta.
- Wymień trzy równoległe magazyny Mem0 i opisz cele optymalizacji każdego z nich.
- Opisz fuzję punktacji w Mem0 — uwzględniającą trafność, ważność oraz aktualność — i wyjaśnij, dlaczego stosuje się sumę ważoną, a nie strukturę hierarchiczną.
- Zaimplementuj w Pythonie (przy użyciu biblioteki standardowej) uproszczony system pamięci złożony z trzech magazynów z metodami `add()` (zapisującą do wszystkich trzech) oraz `search()` (scalającą wyniki).

## Problem

Pojedynczy magazyn nie sprawdzi się w przypadku jednej z trzech klas zapytań:

- **Podobieństwo semantyczne** – „o czym rozmawialiśmy w zeszłym tygodniu w kontekście dryfu agenta?”. Magazyn wektorowy wygrywa; KV i graf są tutaj bezużyteczne.
- **Wyszukiwanie faktów** – „jaki jest numer telefonu użytkownika?”. Magazyn KV wygrywa; wektor to marnotrawstwo zasobów, a graf to przesada.
- **Wnioskowanie o relacjach** – „którzy klienci korzystają z tego samego podmiotu rozliczeniowego?”. Graf wygrywa; wektor i KV nie potrafią odpowiedzieć na to pytanie.

W środowisku produkcyjnym agenci korzystają ze wszystkich trzech rodzajów zapytań w ramach jednej sesji. Przy zastosowaniu tylko jednego magazynu, pamięć będzie działać niepoprawnie dla pozostałych dwóch klas zapytań. Wkład Mem0 polega na połączeniu wszystkich trzech elementów pod wspólnym interfejsem `add`/`search` wraz z funkcją oceniania (scoringową), która scala wyniki.

## Koncepcja

### Trzy magazyny równolegle

Działanie Mem0 (arXiv:2504.19413, kwiecień 2025) przy wywołaniu `add(text, user_id, metadata)`:

1. Wyodrębnij z tekstu potencjalne fakty (krok oparty na LLM).
2. Zapisz każdy fakt w magazynie wektorowym (generując osadzenie/embedding) na potrzeby wyszukiwania semantycznego.
3. Zapisz każdy fakt w bazie KV (identyfikator_użytkownika, typ_faktu, jednostka) w celu wyszukiwania w czasie O(1).
4. Zapisz każdy fakt w bazie grafowej (Mem0g) jako krawędzie typowane na potrzeby zapytań o relacje.

Przy wywołaniu `search(query, user_id)`:

1. Magazyn wektorowy zwraca wyniki top-k na podstawie podobieństwa cosinusowego osadzeń.
2. Magazyn KV zwraca bezpośrednie trafienia dopasowane na podstawie parametrów zapytania (identyfikator_użytkownika, typ, jednostka).
3. Magazyn grafowy zwraca podgraf osiągalny z jednostek występujących w zapytaniu.
4. Warstwa punktacji łączy te trzy grupy wyników.

### Fuzja punktacji

```
score = w_relevance * relevance(q, record)
      + w_importance * importance(record)
      + w_recency * recency(record)
```

- **Trafność (Relevance)** – podobieństwo cosinusowe wektorów, dokładne dopasowanie KV, waga ścieżki w grafie.
- **Ważność (Importance)** – określona w momencie zapisu lub wyuczona (niektóre fakty mają większe znaczenie, np. nazwiska, identyfikatory, reguły).
- **Aktualność (Recency)** – wykładniczy spadek wartości wraz z upływem czasu od ostatniego zapisu lub odczytu.

Wagi są dostosowywane do konkretnego zastosowania. Większa wartość `w_recency` dla agentów konwersacyjnych (czatów); większa `w_importance` dla agentów weryfikujących zgodność (compliance); większa `w_relevance` dla agentów wyszukujących.

### Mem0g i wnioskowanie temporalne

Mem0g wprowadza wykrywanie konfliktów. Kiedy nowy fakt jest sprzeczny z istniejącą krawędzią, ta istniejąca krawędź jest oznaczana jako nieważna (nieaktywna), ale nie jest usuwana. Zapytania uwzględniające czas („w jakim mieście mieszkał użytkownik w marcu?”) przeszukują odpowiedni historyczny podgraf.

Jest to mechanizm spójności danych, który uogólnia wzorzec unieważniania (invalidation) znany z projektów takich jak Letta.

### Wyniki testów porównawczych

Raporty z publikacji Mem0 (2025):

- **LoCoMo** (pamięć o długich konwersacjach): 91,6
- **LongMemEval** (pamięć epizodyczna o długim horyzoncie): 93,4
- **BEAM 1M** (benchmark pamięci o pojemności 1 mln tokenów): 64,1

Wszystkie punkty odniesienia (pełny kontekst LLM 128k, prosta baza wektorowa, prosta baza KV) uzyskują wyniki gorsze o ponad 10 punktów. Same testy nie decydują o wyborze architektury – decyduje o tym specyfika operacyjna – ale liczby pokazują, że architektura fuzji pamięci przynosi realne korzyści.

### Taksonomia zakresów

Mem0 dzieli pamięć według zakresu:

- **Pamięć użytkownika** – utrzymuje się między sesjami, powiązana z `user_id`.
- **Pamięć sesji** – utrzymuje się w obrębie jednego wątku/konwersacji.
- **Pamięć agenta** – stan instancji konkretnego agenta.

Każdy zapis wybiera jeden zakres. Pobieranie może odpytywać różne zakresy, stosując dla nich odrębne wagi. Bezrefleksyjne mieszanie zakresów prowadzi do incydentów typu „asystent przekazał Alicji informacje o projekcie Boba”.

### Potencjalne problemy i wady wzorca

- **Dryft osadzeń (embeddings drift).** Wyniki wyszukiwania wektorowego, które wyglądają dobrze dla pierwszych stu zapytań, pogarszają się w miarę wzrostu bazy danych. Rozwiązaniem jest okresowe generowanie nowych osadzeń dla N najczęściej używanych rekordów.
- **Naruszenie schematu KV.** Układ `(user_id, type, entity)` wydaje się prosty, dopóki każdy zespół nie zacznie dodawać własnych typów (`type`). Wymaga to regularnego audytu zestawu typów (np. co kwartał).
- **Eksplozja grafu.** Jeden zbyt aktywny ekstraktor potrafi dodać 50 krawędzi na jedną wiadomość. Rozwiązaniem jest ograniczenie liczby zapisów do grafu przy każdym wywołaniu `add` oraz odrzucanie krawędzi o niskim poziomie pewności.

## Zbuduj to

Plik `code/main.py` implementuje wzorzec trzech magazynów w bibliotece standardowej Pythona:

- `VectorStore` – uproszczone podobieństwo oparte na nakładaniu się tokenów (jako zastępstwo dla pełnych osadzeń).
- `KVStore` – słownik indeksowany kluczem `(user_id, fact_type, entity)`.
- `GraphStore` – krawędzie typowane (podmiot, relacja, obiekt, ważność).
- `Mem0` – fasada najwyższego poziomu oferująca metody `add()`, `search()`, fuzję ocen oraz wyszukiwanie uwzględniające zakresy.
- Przykładowy przebieg działania (trace) w konwersacji z udziałem wielu użytkowników i sesji.

Uruchomienie:

```
python3 code/main.py
```

Wygenerowane dane pokazują wyniki z trzech osobnych ścieżek wyszukiwania oraz połączoną listę top-k. Zmień wagi punktacji na początku funkcji `main()` i zaobserwuj, jak wpływa to na ranking.

## Użyj tego

- **Mem0 (Apache 2.0)** – rozwiązanie gotowe do wdrożeń produkcyjnych. Możesz hostować je samodzielnie, używając Postgres + Qdrant + Neo4j, lub skorzystać z wersji w chmurze zarządzanej.
- **Letta** – trójpoziomowa pamięć (core/recall/archival); pozwala na podłączenie własnych wektorów i grafów.
- **Zep** – komercyjna alternatywa z grafem wiedzy (KG) uwzględniającym aspekt czasowy oraz ekstrakcją faktów.
- **Własne wdrożenia** – przydatne, gdy potrzebujesz pełnej kontroli nad ekstraktorem (spójność) lub wagami fuzji (np. w agentach głosowych, gdzie kluczowe znaczenie ma aktualność).

## Wyślij to

Plik `outputs/skill-hybrid-memory.md` tworzy szkielet pamięci składający się z trzech komponentów wraz z zaimplementowanym systemem fuzji ocen, taksonomią zakresów oraz unieważnianiem czasowym.

## Ćwiczenia

1. Zastąp uproszczone wyszukiwanie wektorowe rzeczywistym modelem osadzeń (sentence-transformers, Ollama, OpenAI embeddings). Zmierz wskaźnik recall@10 podczas długiej, syntetycznej konwersacji. Czy ranking ulega degradacji przy ponad 1000 wpisach?
2. Dodaj zapytanie czasowe: `search(query, as_of=timestamp)`. Zwracaj tylko te rekordy, które były aktualne w podanym momencie lub wcześniej. Który z magazynów wymaga najwięcej modyfikacji?
3. Zastosuj detektor konfliktów: jeśli nowo dodawany fakt jest sprzeczny z krawędzią grafu, oznacz starą krawędź jako nieważną i zapisz obie. Przetestuj na przykładzie: „użytkownik mieszka w Berlinie” -> „użytkownik mieszka w Lizbonie”.
4. Zmodyfikuj fuzję punktacji, aby uwzględniała wymiar opinii użytkownika `user_feedback` (np. polubienia pobranych rekordów). Jak zapobiec manipulowaniu wynikami (ang. gaming the system), kiedy agent zwraca wyłącznie te rekordy, które użytkownik już wcześniej polubił?
5. Przeczytaj dokumentację Mem0 (`docs.mem0.ai`). Zastąp uproszczoną wersję wywołaniami klienta biblioteki `mem0`. Porównaj jakość wyszukiwania dla tych samych 20 zapytań testowych.

## Kluczowe terminy

| Termin | Co mówią ludzie | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Pamięć hybrydowa | „Wektor plus graf plus KV” | Trzy magazyny zapisywane równolegle, łączone podczas wyszukiwania |
| Ekstrakcja faktów | „Zapisywanie w pamięci” | Krok LLM, który dzieli tekst na krotki (podmiot, relacja, obiekt) |
| Fuzja punktacji | „Ranking trafności” | Suma ważona trafności, ważności oraz aktualności |
| Zakres | „Przestrzeń nazw pamięci” | Użytkownik / sesja / agent — określa, kto co widzi |
| Mem0g | „Graf pamięci” | Typowane krawędzie z czasową ważnością na potrzeby zapytań o relacje |
| Unieważnienie czasowe | „Miękkie usuwanie” | Oznaczenie sprzecznych krawędzi jako nieważne; nigdy nie są usuwane |
| Dryft osadzeń | „Degradacja jakości wyszukiwania” | Jakość wyszukiwania wektorowego spada wraz ze wzrostem wolumenu danych; generuj osadzenia ponownie w regularnych odstępach czasu |

## Dalsze czytanie

- [Chhikara et al., Mem0 (arXiv:2504.19413)](https://arxiv.org/abs/2504.19413) — artykuł oryginalny
- [Dokumentacja Mem0](https://docs.mem0.ai/platform/overview) — produkcyjne API, SDK, chmura zarządzana
- [Packer et al., MemGPT (arXiv:2310.08560)](https://arxiv.org/abs/2310.08560) — poprzednik wprowadzający koncepcję pamięci wirtualnej
- [Letta, blog o blokach pamięci](https://www.letta.com/blog/memory-blocks) — siostrzany projekt oparty na trójpoziomowej architekturze|
