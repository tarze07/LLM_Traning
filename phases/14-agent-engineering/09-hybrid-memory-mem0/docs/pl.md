# Pamięć hybrydowa: wektor + wykres + KV (Mem0)

> Mem0 (Chhikara i in., 2025) traktuje pamięć jako trzy równoległe zasoby — wektor dla podobieństwa semantycznego, KV dla szybkiego wyszukiwania faktów, wykres dla wnioskowania między jednostkami. Warstwa punktacji łączy trzy podczas pobierania. Jest to standard produkcyjny pamięci zewnętrznej na rok 2026.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 07 (MemGPT), Faza 14 · 08 (Bloki Letta)
**Czas:** ~75 minut

## Cele nauczania

- Wyjaśnij, dlaczego pojedyncza pamięć (tylko wektor, tylko wykres, tylko KV) jest niewystarczająca dla pamięci agenta.
- Wymień trzy równoległe sklepy Mem0 i pod kątem optymalizacji każdego z nich.
- Opisz punktację fuzji Mem0 — trafność, znaczenie, aktualność — i dlaczego jest to suma ważona, a nie hierarchia.
- Zaimplementuj zabawkową pamięć z trzema magazynami w stdlib z `add()`, która zapisuje do wszystkich trzech i `search()`, która łączy wyniki.

## Problem

Jeden sklep jest nieprawidłowy dla jednej z trzech klas zapytań:

- **Podobieństwo semantyczne** — „o czym rozmawialiśmy w zeszłym tygodniu na temat dryfu agenta?” Wektor wygrywa; Brak KV i wykresu.
- **Wyszukiwanie faktów** — „jaki jest numer telefonu użytkownika?” KV wygrywa; wektor jest marnotrawstwem, wykres jest przesadą.
- **Rozumowanie dotyczące relacji** — „którzy klienci korzystają z tego samego podmiotu rozliczeniowego?” Wykres wygrywa; wektor i KV nie mogą odpowiedzieć.

Agenci produkcyjni wystawiają wszystkie trzy w jednej sesji. W przypadku dwóch z nich pamięć o jednym sklepie jest zawsze błędna. Wkład Mem0 polega na okablowaniu wszystkich trzech elementów za pojedynczą powierzchnią `add`/`search` z funkcją oceniania, która je łączy.

## Koncepcja

### Trzy sklepy równolegle

Mem0 (arXiv:2504.19413, kwiecień 2025) w `add(text, user_id, metadata)`:

1. Wyodrębnij z tekstu fakty dotyczące kandydatów (krok oparty na LLM).
2. Zapisz każdy fakt w magazynie wektorowym (osadzając) w celu wyszukiwania semantycznego.
3. Zapisz każdy fakt w zapisanej bazie KV (identyfikator_użytkownika, typ_faktu, jednostka) w celu wyszukania O(1).
4. Zapisz każdy fakt w magazynie wykresów (Mem0g) jako wpisane krawędzie dla zapytań o relacje.

W `search(query, user_id)`:

1. Przechowywanie wektorów zwraca górę-k poprzez osadzenie cosinusa.
2. Magazyn KV zwraca bezpośrednie trafienia wpisane na podstawie zapytania (identyfikator_użytkownika, typ, encja).
3. Magazyn wykresów zwraca podgraf dostępny z jednostek zapytań.
4. Warstwa punktacji łączy te trzy.

### Punktacja Fuzji

```
score = w_relevance * relevance(q, record)
      + w_importance * importance(record)
      + w_recency * recency(record)
```

- **Istotność** — cosinus wektora, dokładne dopasowanie KV, waga ścieżki wykresu.
- **Ważność** — oznaczona w momencie pisania lub wyuczona (niektóre fakty mają większe znaczenie: nazwiska, identyfikatory, zasady).
- **Recency** — wykładniczy zanik w czasie od ostatniego zapisu lub odczytu.

Wagi są dostosowywane do każdego produktu. Wyższe `w_recency` dla agentów czatu; wyższe `w_importance` dla agentów ds. zgodności; wyższy `w_relevance` dla agentów wyszukiwania.

### Mem0g i rozumowanie temporalne

Mem0g dodaje detektor konfliktów. Kiedy nowy fakt jest sprzeczny z istniejącą krawędzią, istniejąca krawędź zostaje oznaczona jako nieważna, ale nie usunięta. Zapytania czasowe („jakie było miasto użytkownika w marcu?”) przechodzą przez podgraf aktualny.

Jest to zachowanie na poziomie zgodności, które uogólnia wzór unieważnienia Letty.

### Liczby porównawcze

Raporty z artykułu Mem0 (2025):

- **LoCoMo** (długa pamięć konwersacji): 91,6
- **LongMemEval** (pamięć epizodyczna o długim horyzoncie): 93,4
- **BEAM 1M** (test porównawczy pamięci tokena 1M): 64.1

Wszystkie linie bazowe porównania (pełnokontekstowy 128 tys. LLM, płaska baza wektorowa, płaska KV) tracą ponad 10 punktów. Same testy porównawcze nie uzasadniają wyboru – kształt operacyjny tak – ale liczby pokazują, że projekt syntezy jądrowej nie jest błędnym zaokrągleniem.

### Taksonomia zakresu

Mem0 dzieli pamięć według zakresu:

- **Pamięć użytkownika** — utrzymuje się podczas sesji, kluczowana na `user_id`.
- **Pamięć sesji** — utrzymuje się w obrębie jednego wątku.
- **Pamięć agenta** — stan instancji poszczególnych agentów.

Każdy zapis wybiera jeden zakres. Pobieranie może wykonywać zapytania w różnych zakresach z wagami dla każdego zakresu. Mieszanie zakresów bez zastanowienia pozwala uzyskać incydenty typu „asystent powiedział Alicji o projekcie Boba”.

### Gdzie ten wzorzec jest błędny

- **Dryfowanie osadzania.** Wyniki wektorowe, które wyglądają dobrze w przypadku pierwszych stu zapytań, pogarszają się wraz ze wzrostem korpusu. Dodaj okresowe ponowne osadzanie N najczęściej używanych rekordów.
- **Pękanie schematu KV.** `(user_id, type, entity)` wygląda prosto, dopóki każdy zespół nie doda własnego `type`. Audyt zestawu typów co kwartał.
- **Eksplozja wykresu.** Jeden hałaśliwy ekstraktor dodaje 50 krawędzi na wiadomość. Wykres Cap zapisuje każde wywołanie `add`; upuść krawędzie o niskiej pewności.

## Zbuduj to

`code/main.py` implementuje wzorzec trzech sklepów w stdlib:

- `VectorStore` — naiwne podobieństwo nakładania się tokenów jako zastępstwo przy osadzaniu.
- `KVStore` — dykt wpisany na `(user_id, fact_type, entity)`.
- `GraphStore` — wpisane krawędzie (podmiot, relacja, obiekt, ważny).
- `Mem0` — fasada najwyższego poziomu z `add()`, `search()`, ocenianiem fuzji i wyszukiwaniem uwzględniającym zakres.
- Działający ślad w rozmowie z wieloma użytkownikami i sesjami.

Uruchom to:

```
python3 code/main.py
```

Dane wyjściowe pokazują trzy oddzielne ścieżki przywracania plus połączone top-k. Odwróć wagi punktacji na górze `main()` i obserwuj zmianę rankingu.

## Użyj tego

- **Mem0 (Apache 2.0)** — gotowy do produkcji. Hostuj samodzielnie z Postgres + Qdrant + Neo4j lub skorzystaj z zarządzanej chmury.
- **Letta** — trójpoziomowy rdzeń/wycofanie/archiwum; przynieś własne wektory i wykresy.
- **Zep** — alternatywa komercyjna z tymczasowym KG i ekstrakcją faktów.
- **Kompilacje niestandardowe** — gdy potrzebujesz dokładnej kontroli nad ekstraktorem (zgodność) lub wagą fuzji (agenci głosowi, gdzie dominuje aktualność).

## Wyślij to

`outputs/skill-hybrid-memory.md` generuje trzy składową rusztowanie pamięci z podłączonym wskaźnikiem fuzji, taksonomią zakresu i unieważnieniem czasowym.

## Ćwiczenia

1. Zastąp podobieństwo wektora zabawek prawdziwym modelem osadzania (transformatory zdań, Ollama, osadzanie OpenAI). Zmierz zapamiętywanie@10 podczas syntetycznej długiej rozmowy. Czy ranking dryfuje powyżej 1000 wpisów?
2. Dodaj zapytanie tymczasowe: `search(query, as_of=timestamp)`. Zwracaj tylko rekordy ważne w tym czasie lub wcześniej. Który sklep wymaga najwięcej pracy?
3. Zastosuj detektor konfliktu: jeśli nadchodzący fakt jest sprzeczny z krawędzią wykresu, unieważnij starą krawędź i zarejestruj oba. Test na „użytkownik mieszka w Berlinie” -> „użytkownik mieszka w Lizbonie”.
4. Przenieś punktację fuzji, aby uwzględnić wymiar `user_feedback` (kciuki w górę za pobrane rekordy). Jak zapobiegać graniu (agent zwraca tylko te nagrania, które już polubił)?
5. Przeczytaj dokumentację Mem0 (`docs.mem0.ai`). Przenieś zabawkę do wywołań klienta `mem0`. Porównaj jakość wyszukiwania dla tych samych 20 zapytań testowych.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Pamięć hybrydowa | „Wektor plus wykres plus KV” | Trzy sklepy zapisane równolegle, połączone podczas wyszukiwania |
| Ekstrakcja faktów | „Przejmowanie pamięci” | Krok LLM, który dzieli tekst na (jedność, relację, fakt) krotki |
| Punktacja Fuzji | „Ranking trafności” | Suma ważona trafności, ważności, aktualności |
| Zakres | „Przestrzeń nazw pamięci” | użytkownik / sesja / agent — określa, kto co widzi |
| Pamięć0g | „Wykres pamięci” | Wpisane krawędzie z czasową ważnością dla zapytań o relacje |
| Unieważnienie czasowe | „Miękkie usuwanie” | Oznacz sprzeczne krawędzie jako nieprawidłowe; nigdy nie usuwaj |
| Osadzanie dryfu | „Zgnilizna odzyskiwania” | Jakość wektora pogarsza się wraz ze wzrostem korpusu; osadzaj ponownie okresowo |

## Dalsze czytanie

- [Chhikara et al., Mem0 (arXiv:2504.19413)](https://arxiv.org/abs/2504.19413) — artykuł oryginalny
- [Dokumentacja Mem0](https://docs.mem0.ai/platform/overview) — produkcyjne API, SDK, zarządzana chmura
- [Packer et al., MemGPT (arXiv:2310.08560)](https://arxiv.org/abs/2310.08560) — poprzednik w kontekście wirtualnym
– [Letta, blog o blokach pamięci](https://www.letta.com/blog/memory-blocks) — trójpoziomowy projekt rodzeństwa