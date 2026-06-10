# Capstone 02 — RAG w bazie kodu (wyszukiwanie semantyczne między repo)

> Każda poważna organizacja inżynierska w 2026 r. przeprowadza wewnętrzne wyszukiwanie kodu, które rozumie znaczenie, a nie tylko ciągi znaków. Sourcegraph Amp, odpowiedzi z bazy kodu Cursora, wykres korporacyjny Augment, repomapa Aidera, wewnętrzny MCP Pinteresta – ten sam kształt. Pozyskuj wiele repozytoriów, analizuj z opiekunem drzewa, osadzaj fragmenty na poziomie funkcji i klas, przeszukuj hybrydowo, zmieniaj ranking, odpowiadaj cytatami. W tym zwieńczeniu prosisz o zbudowanie takiego, który obsłuży 2 miliony linii kodu w 10 repozytoriach i przetrwa przyrostowe ponowne indeksowanie przy każdym wypychaniu git.

**Typ:** Zwieńczenie
**Języki:** Python (pozyskiwanie), TypeScript (API + interfejs użytkownika)
**Wymagania wstępne:** Faza 5 (podstawy NLP), Faza 7 (transformatory), Faza 11 (inżynieria LLM), Faza 13 (narzędzia), Faza 17 (infrastruktura)
**Wykonywane fazy:** P5 · P7 · P11 · P13 · P17
**Czas:** 30 godzin

## Problem

Do 2026 r. każdy pionierski agent kodujący będzie wyposażony w warstwę odzyskiwania bazy kodu, ponieważ same okna kontekstowe nie rozwiążą problemów związanych z krzyżowymi repo. Kontekst tokena 1M Claude'a pomaga; nie eliminuje to potrzeby wyszukiwania rankingowego. Naiwne wyszukiwanie cosinusów na surowych fragmentach zatruwa wyniki wygenerowanego kodu, duplikacji monorepo i długiego ogona rzadko importowanych symboli. Odpowiedzią produkcyjną jest przeszukiwanie hybrydowe (gęste + BM25) fragmentów obsługujących AST za pomocą narzędzia do zmiany rankingu, poparte wykresem odniesień do symboli.

Dowiesz się tego, indeksując prawdziwą flotę — a nie jedno repozytorium samouczków — i mierząc MRR@10, wierność cytowań i przyrostową świeżość. Tryby awarii mają charakter infrastrukturalny: monorepo zawierające 100 tys. plików, push retuszujący połowę plików, zapytanie, które musi przejść przez cztery repozytoria, aby odpowiedzieć poprawnie.

## Koncepcja

Potok pozyskiwania obsługujący technologię AST analizuje każdy plik za pomocą modułu nadzorującego drzewo, wyodrębnia węzły funkcji i klas oraz fragmenty na granicach węzłów, a nie stałe okna tokenów. Każdy fragment ma trzy reprezentacje: gęste osadzenie (kod Voyage-3 lub nomic-embed-code), rzadkie terminy BM25 i krótkie podsumowanie w języku naturalnym. Podsumowanie dodaje trzecią możliwą do odzyskania modalność — użytkownicy pytają „w jaki sposób X jest autoryzowany”, a podsumowanie wspomina „authz”, nawet jeśli kod zawiera tylko `check_permission`.

Odzyskiwanie jest hybrydowe. Zapytanie uruchamia zarówno wyszukiwanie gęste, jak i BM25, łączy top-k i przekazuje związek do narzędzia do zmiany rankingu między koderami (Cohere rerank-3 lub bge-reranker-v2-gemma-2b). Ponownie sklasyfikowana lista trafia do syntezatora o długim kontekście (Claude Sonnet 4.7 z szybkim buforowaniem lub Llama 3.3 70B na własnym serwerze) z instrukcjami cytowania każdego roszczenia według zakresu plików i linii. Odpowiedzi bez cytatów są odrzucane przez post-filtr.

Problemem infrastrukturalnym jest rosnąca świeżość. Git Push uruchamia różnicę: które pliki się zmieniły, które symbole się zmieniły. Tylko dotknięte fragmenty są ponownie osadzane. Dotknięte krawędzie symboli między plikami (importy, wywołania metod) są ponownie obliczane. Indeks pozostaje spójny bez ponownego przetwarzania 2 milionów wierszy przy każdym zatwierdzeniu.

## Architektura

```
git push --> webhook --> ingest worker (LlamaIndex Workflow)
                           |
                           v
             tree-sitter parse + AST chunk
                           |
            +--------------+----------------+
            v              v                v
          dense        BM25 index       summary (LLM)
        (Voyage / bge)  (Tantivy)        (Haiku 4.5)
            |              |                |
            +------> Qdrant / pgvector <----+
                            |
                            v
                      symbol graph (Neo4j / kuzu)
                            |
  query --> LangGraph agent (retrieve -> rerank -> synth)
                            |
                            v
                 Claude Sonnet 4.7 1M context
                            |
                            v
                 answer + file:line citations
```

## Stos

- Parsowanie: Tree Sitter z 17 gramatykami językowymi (Python, TS, Rust, Go, Java, C++ itp.)
- Gęste osadzanie: Voyage-code-3 (hostowany) lub nomic-embed-code-v1.5 (samodzielny host), rezerwowy bge-code-v1
- Indeks rzadki: Tantivy (Rust) z BM25F, ważony polem na podstawie nazwy symbolu w porównaniu z treścią
- Vector DB: Qdrant 1.12 z wyszukiwaniem hybrydowym lub pgvector + pgvectorscale dla zespołów poniżej 50M wektorów
- Model podsumowania fragmentów: Claude Haiku 4.5 lub Gemini 2.5 Flash, buforowany w pamięci podręcznej
- Re-ranker: Cohere rerank-3 lub bge-reranker-v2-gemma-2b na własnym serwerze
- Orkiestracja: przepływy pracy LlamaIndex do przyjmowania, LangGraph dla agenta zapytań
- Syntezator: Claude Sonnet 4.7 (kontekst 1M) z szybkim buforowaniem
- Wykres symboli: Neo4j (zarządzany) lub kuzu (wbudowany) dla krawędzi importu i połączeń
- Obserwowalność: zakresy Langfuse'a na pobieranie + etap syntezy

## Zbuduj to

1. **Prowadzący przetwarzanie.** Iteruj historię git na każdym haku. Zbierz zmienione pliki. Dla każdego pliku dokonaj analizy za pomocą modułu nadzorującego drzewo, wyodrębnij węzły funkcji i klas z ich pełnym zakresem źródłowym. Emituj rekordy fragmentów `{repo, path, start_line, end_line, symbol, body}`.

2. **Podsumowanie fragmentów.** Podział fragmentów na wywołania Haiku 4.5 z natychmiastowym buforowaniem w preambule systemowej. Podpowiedź: „Podsumuj tę funkcję w jednym zdaniu, wymieniając jej zamówienie publiczne i skutki uboczne”. Podsumowanie przechowywania obok fragmentu.

3. **Pula osadzania.** Dwie równoległe kolejki: gęsta (kod rejsu-3 partia 128) i podsumowująca (ten sam model, ale w ciągu podsumowującym). Zapisz wektory do Qdrant z ładunkiem `{repo, path, start_line, end_line, symbol, kind}`.

4. **Indeks BM25.** Indeks Tantivy ważony polami: waga nazwy symbolu 4, waga symbolu 1, sumaryczna waga 2. Umożliwia wykonywanie zapytań „znajdź funkcję o nazwie X” wraz z „znajdź funkcję wykonującą X”.

5. **Wykres symboli.** Dla każdego fragmentu zapisz krawędzie: import (w tym pliku używany jest symbol Y z repozytorium Z), wywołania (ta funkcja wywołuje metodę M w klasie C), dziedziczenie. Przechowuj w kuzu. Używane w czasie zapytania w celu rozszerzenia pobierania poza granice repo.

6. **Agent zapytań.** LangGraph z trzema węzłami. `retrieve` uruchamia równolegle gęste + BM25, deduplikuje według (repo, ścieżka, symbol). `rerank` uruchamia koder krzyżowy na 50 najlepszych i utrzymuje 10 najlepszych. `synth` wywołuje Claude Sonnet 4.7 z fragmentami o zmienionym rankingu w kontekście, buforuje monit systemowy, wymaga cytatów plik:wiersz.

7. **Wymuszanie cytowania.** Przeanalizuj dane wyjściowe modelu; każde roszczenie bez kotwicy `(repo/path:start-end)` zostanie oznaczone do ponownego zapytania lub odrzucone. Zwróć użytkownikowi odpowiedź zawierającą tylko cytowane informacje.

8. **Przyrostowe ponowne indeksowanie.** Na każdym webhooku oblicz różnicę na poziomie symboli. Osadzaj ponownie tylko fragmenty, których tekst się zmienił. Oblicz ponownie krawędzie symboli dla fragmentów, których import uległ zmianie. Środek: 50 plików przesłanych ponownie zindeksowanych w mniej niż 60 sekund dla floty 2M-LOC.

9. **Eval.** Oznacz 100 pytań typu cross-repo ze złotymi odpowiedziami typu plik:wiersz. Zmierz MRR@10, nDCG@10, wierność cytowań (ułamek twierdzeń z weryfikowalnymi kotwicami) i opóźnienie p50/p99.

## Użyj tego

```
$ code-rag ask "how is S3 multipart abort wired into our retry budget?"
[retrieve]  12 chunks dense + 7 chunks bm25, 16 unique after dedup
[rerank]    top-5 kept (cohere rerank-3)
[synth]     claude-sonnet-4.7, cache hit rate 68%, 2.1s
answer:
  Multipart aborts are triggered by `AbortMultipartOnFail` in
  services/uploader/retry.go:122-148, which decrements the per-bucket
  retry budget defined in config/budgets.yaml:34-51 ...
  citations: [services/uploader/retry.go:122-148, config/budgets.yaml:34-51,
              libs/s3client/multipart.ts:44-61]
```

## Wyślij to

Możliwość dostarczenia umiejętności `outputs/skill-codebase-rag.md`. Mając zbiór repozytoriów, uruchamia potok pozyskiwania, indeks hybrydowy i agenta zapytań, a następnie zwraca cytowaną odpowiedź na każde pytanie dotyczące wielu repozytoriów. Rubryka:

| Waga | Kryterium | Jak to się mierzy |
|:-:|---|---|
| 25 | Jakość wyszukiwania | MRR@10 i nDCG@10 w zestawie 100 pytań wstrzymanych |
| 20 | Wierność cytatów | Część żądań odpowiedzi z weryfikowalnymi plikami:kotwice linii |
| 20 | Opóźnienie i skala | opóźnienie zapytania p95 przy 10 tys. QPS w indeksowanym rozmiarze korpusu |
| 20 | Poprawność indeksowania przyrostowego | Czas od git push do możliwości przeszukiwania w przypadku zatwierdzenia 50 plików |
| 15 | UX i formatowanie odpowiedzi | Klikalność cytatów, podgląd fragmentów, afordancja kontynuacji |
| **100** | | |

## Ćwiczenia

1. Zamień Voyage-code-3 na nomic-embed-code hostowany samodzielnie. Zmierz deltę MRR@10. Zgłoś, czy luka się zamyka po włączeniu ponownego rankingu.

2. Wstrzyknij wygenerowany w 20% kod (płytę wzorcową wyprodukowaną przez LLM) do korpusu i ponownie oceń. Obserwuj zatrucie podczas pobierania. Dodaj „wygenerowaną” flagę do ładunku i zmniejsz wagę tych trafień.

3. Porównanie wyszukiwania hybrydowego Qdrant vs pgvector + pgvectorscale w rozmiarze korpusu. Zgłoś p99 dla partii o wielkości 1.

4. Dodaj kontrolę dryfu opartą na próbkowaniu: co tydzień powtarzaj ocenę składającą się ze 100 pytań. Ostrzeżenie w przypadku spadku MRR@10 > 5%.

5. Rozszerzenie do rozdzielczości symboli w wielu językach: funkcja Pythona, która wywołuje usługę Go przez gRPC. Użyj wykresu symboli, aby je połączyć.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|-----------------|--------------------------------------|
| Kawałki świadome AST | „Podziały na poziomie funkcji” | Kod wycinający na granicach węzłów nadzorujących drzewo zamiast stałych okien tokenów |
| Wyszukiwanie hybrydowe | „Gęsty + rzadki” | Uruchom równolegle BM25 i wyszukiwanie wektorów, połącz top-k, zmień rangę |
| Zmiana rangi cross-enkodera | „Ranga drugiego stopnia” | Model, który ocenia każdą parę (zapytanie, kandydat) razem, dokładniejszy niż cosinus |
| Natychmiastowe buforowanie | „Podpowiedź systemowa w pamięci podręcznej” | Funkcja Claude / OpenAI 2026, która obniża tokeny z powtarzającymi się prefiksami aż do 90% |
| Wykres symboli | „Wykres kodowy” | Krawędzie dla importów, wywołań, dziedziczenia między plikami i repozytoriami |
| Wierność cytatów | „Uziemiony wskaźnik odpowiedzi” | Część roszczeń, które użytkownik może zweryfikować, klikając kotwicę i czytając zakres, do którego się odwołuje |
| Przyrostowe ponowne indeksowanie | „Czas push-to-search” | Zegar ścienny z git push do zmienionych symboli, które można zapytać |

## Dalsze czytanie

- [Sourcegraph Amp](https://ampcode.com) — inteligencja produkcyjnego kodu cross-repo
— [Architektura Sourcegraph Cody RAG](https://sourcegraph.com/blog/how-cody-understands-your-codebase) — referencyjne szczegółowe informacje na temat tego zwieńczenia
- [Mapa repozytorium Aider](https://aider.chat/docs/repomap.html) — widok rankingowego repozytorium drzewa
- [Wykres korporacyjny kodu rozszerzonego] (https://www.augmentcode.com) — wykres symboli komercyjnych RAG
- [Dokumentacja wyszukiwania hybrydowego Qdrant](https://qdrant.tech/documentation/concepts/hybrid-queries/) — implementacja referencyjna
- [Osadzanie kodu Voyage AI](https://docs.voyageai.com/docs/embeddings) — szczegóły Voyage-code-3
- [Cohere rerank-3](https://docs.cohere.com/reference/rerank) — odniesienie do wielu koderów
- [Wewnętrzne wyszukiwanie Pinterest MCP](https://medium.com/pinterest-engineering) — odniesienie do wewnętrznej platformy