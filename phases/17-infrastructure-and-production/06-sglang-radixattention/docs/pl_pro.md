# SGLang i RadixAttention w zadaniach o wysokiej powtarzalności prefiksów

> Projekt SGLang traktuje pamięć podręczną KV Cache jako kluczowy zasób wielokrotnego użytku, organizując ją w strukturze drzewa skróconego (radix tree). Podczas gdy vLLM domyślnie kolejkuje zapytania według zasady First-Come, First-Served (FCFS), harmonogram SGLang (cache-aware scheduler) nadaje priorytet żądaniom posiadającym najdłuższe wspólne prefiksy. Odpowiada to przechodzeniu drzewa w głąb (depth-first traversal), dzięki czemu najczęściej używane gałęzie są stale utrzymywane w pamięci HBM. Dla modelu Llama 3.1 8B przy promptach o długości 1k tokenów (zbiór ShareGPT), SGLang osiąga wydajność ~16 200 tokenów na sekundę w porównaniu do ~12 500 tokenów na sekundę dla vLLM – co daje przewagę na poziomie ok. 29%. W zadaniach typu Retrieval-Augmented Generation (RAG) o wysokiej powtarzalności prefiksów przewaga ta rośnie do 6,4x, a w zadaniach związanych z klonowaniem głosu współczynnik trafień w pamięci podręcznej (cache hit rate) przekracza 86%. W 2026 roku technologia ta działa na ponad 400 000 procesorów GPU w infrastrukturze firm takich jak xAI, LinkedIn, Cursor, Oracle, GCP, Azure oraz AWS. Należy jednak pamiętać, że zysk rzędu 6,4x spada do zera, jeśli kolejność elementów w promptach wejściowych jest niespójna – właściwe ustrukturyzowanie promptu to główne zadanie inżyniera.

**Typ:** Teoria (Learn)
**Języki:** Python (stdlib, pamięć podręczna typu radix tree oraz harmonogram uwzględniający stan pamięci podręcznej)
**Wymagania wstępne:** Faza 17 · 04 (Wewnętrzne mechanizmy serwowania vLLM), faza 14 (Agentic RAG)
**Czas:** ~75 minut

## Cele nauczania

- Zrozumienie mechanizmu RadixAttention: sposób przechowywania prefiksów w drzewie skróconym (radix tree) oraz zasada współdzielenia bloków KV Cache przez sekwencje posiadające ten sam początek.
- Definicja harmonogramu uwzględniającego stan pamięci podręcznej (cache-aware scheduler) i wyjaśnienie, dlaczego standardowe kolejkowanie FCFS jest nieefektywne przy częstym powtarzaniu tych samych fragmentów promptu.
- Obliczanie szacowanego przyspieszenia generacji dla danego obciążenia na podstawie współczynnika trafień w pamięci podręcznej prefiksów (cache hit rate) oraz rozkładu długości promptów wejściowych.
- Wdrożenie zasad strukturyzacji promptu (prompt ordering), które pozwalają na uzyskanie pełnego przyspieszenia w warunkach produkcyjnych.

## Problem

Klasyczne serwowanie modeli LLM traktuje prompt wejściowy każdego zapytania jako niezależny, nieprzeźroczysty blok danych. Jeśli 5000 zapytań w systemie RAG rozpoczyna się od tego samego promptu systemowego o długości 2000 tokenów oraz zawiera tę samą preambułę wyszukiwania, silnik vLLM będzie przetwarzał (faza prefill) ten 2000-tokenowy prefiks 5000 razy. Jednostki GPU będą wykonywać dokładnie te same operacje obliczeniowe wielokrotnie.

W rzeczywistych potokach agentowych oraz RAG, prompty wejściowe niemal zawsze zawierają długie, wspólne fragmenty początkowe (prefiksy). Instrukcje systemowe, opisy dostępnych narzędzi (schemas), przykłady (few-shot examples), kontekst wyszukiwania czy historia dotychczasowej konwersacji – wszystkie te elementy powtarzają się w kolejnych zapytaniach. Gdyby zapisać obliczoną raz pamięć podręczną KV Cache dla tego prefiksu i użyć jej ponownie przy kolejnych zapytaniach, faza prefill dla tych tokenów mogłaby zostać całkowicie pominięta.

Mechanizm RadixAttention realizuje to zadanie. Tokeny są indeksowane w strukturze drzewa skróconego (radix tree), a każdy węzeł przechowuje bloki KV Cache wyliczone dla sekwencji tokenów na ścieżce od korzenia (root). Nowe zapytanie przechodzi przez drzewo: dla każdego węzła, którego tokeny pasują do promptu wejściowego, system bezpośrednio importuje gotowe bloki KV Cache. Koszt obliczeniowy fazy prefill ogranicza się do przetworzenia nowego zakończenia promptu (sufiksu), a nie całego zapytania.

Kluczowym wyzwaniem staje się jednak harmonogramowanie zadań. Jeśli dwa zapytania w kolejce posiadają wspólny prefiks o długości 2000 tokenów, a trzecie zapytanie pasuje tylko w obrębie 200 tokenów, harmonogram powinien przetwarzać dwa zapytania z długim prefiksem jedno po drugim. Dzięki temu wspólne bloki o rozmiarze 2000 tokenów zostaną utrzymane w pamięci podręcznej GPU (HBM). Standardowa kolejka FCFS przetwarza żądania wyłącznie według czasu przybycia, co przy mieszanym ruchu prowadzi do ciągłego usuwania z pamięci gorących gałęzi i drastycznego spadku wydajności.

## Koncepcja

### Drzewo radix jako indeks pamięci KV Cache

Drzewo skrócone (radix tree) przechowuje sekwencje tokenów. Każdy węzeł zawiera określony fragment tekstu oraz wyliczone dla niego bloki KV Cache. Węzły potomne rozszerzają tę sekwencję o kolejne tokeny.

```
root
 |- "You are a helpful assistant..."  (2,000 tokenów, 124 bloki KV)
      |- "Context: <doc A>..."        (500 tokenów, 31 bloków)
           |- "Question: Alice..."    (80 tokenów, 5 bloków)
           |- "Question: Bob..."      (95 tokenów, 6 bloków)
      |- "Context: <doc B>..."        (520 tokenów, 33 bloki)
```

Gdy do systemu trafia nowe zapytanie zawierające prompt systemowy + „Context: <doc A>” + „Question: Carol”, harmonogram przeszukuje drzewo: dopasowuje prefiks systemowy (importuje gotowe 124 bloki) oraz gałąź z dokumentem A (importuje kolejne 31 bloków), po czym alokuje i wylicza nowe bloki wyłącznie dla fragmentu „Question: Carol” (4 bloki). Koszt fazy prefill ogranicza się do wyliczenia 4 bloków zamiast 160. Daje to ok. 40-krotną oszczędność obliczeniową.

### Harmonogram uwzględniający stan pamięci podręcznej (Cache-aware scheduling)

Współdzielenie bloków z użyciem drzewa radix jest efektywne tylko wtedy, gdy dane w pamięci podręcznej nie rotują zbyt szybko. Wdrożono tu dwie kluczowe zasady:

1. **Przechodzenie drzewa w głąb (depth-first dispatch):** Dobierając kolejne zadanie z kolejki, harmonogram nadaje priorytet zapytaniom korzystającym z tej samej gałęzi drzewa, która jest aktualnie załadowana w GPU. Zabezpiecza to gorącą gałąź przed usunięciem z pamięci.
2. **Usuwanie danych na poziomie gałęzi (branch-level LRU):** Gdy brakuje wolnej pamięci, system usuwa z cache całe najrzadziej używane gałęzie (zaczynając od liści), a nie pojedyncze, rozproszone bloki, dzięki czemu struktura pamięci podręcznej odzwierciedla strukturę drzewa radix.

Standardowe kolejkowanie FCFS łamie obie te zasady. Zapytanie wymagające prefiksu o długości 2000 tokenów może zostać zablokowane w kolejce przez krótkie zadanie, co doprowadzi do usunięcia gałęzi 2000 tokenów z pamięci podręcznej w celu zwolnienia miejsca na małe zapytanie.

### Liczby warte zapamiętania

- Model Llama 3.1 8B na układzie H100 (prompty 1k, zbiór ShareGPT): SGLang osiąga ~16 200 tokenów/s vs vLLM ~12 500 tokenów/s (ok. 29% zysku).
- Zadania RAG z powtarzalnymi dokumentami i różnymi pytaniami: do 6,4x wyższa wydajność w SGLang.
- Zadania klonowania głosu: współczynnik trafień prefiksów (cache hit rate) na poziomie 86.4%.
- Wskaźnik trafień na produkcji u klientów SGLang: od 50% do 99% przy zachowaniu zasad strukturyzacji promptu.
- Skala wdrożeń: ponad 400 000 procesorów GPU w 2026 roku.

### Znaczenie kolejności elementów w promptach (Prompt ordering)

Wydajność wyższa o 6,4x zależy od zachowania spójnej kolejności elementów w szablonie promptu. Jeśli system w części zapytań układa prompt w kolejności `[system, tools, context, history, question]`, a w innych stosuje strukturę `[system, context, tools, history, question]`, silnik RadixAttention nie rozpozna wspólnego prefiksu. Dwa prompty o tej samej treści, ale odmiennej kolejności bloków, tworzą w drzewie radix dwie zupełnie różne gałęzie.

Złota zasada: szablon promptu jest kluczem do pamięci podręcznej. Uporządkuj jego strukturę. Na samym początku umieszczaj elementy niezmienne (instrukcje systemowe, opisy narzędzi, schematy danych). Dopiero za nimi umieszczaj pobrany kontekst (np. dokumenty RAG), a treść zapytania użytkownika pozycjonuj zawsze na samym końcu promptu. Unikaj wplatania dynamicznych zmiennych wewnątrz statycznego prefiksu.

Rzeczywisty przypadek: Wydzielenie dynamicznych danych z buforowanego prefiksu pozwoliło podnieść współczynnik trafień w pamięci podręcznej z 7% do 74% w ramach jednej modyfikacji.

### Kiedy RadixAttention przynosi największe korzyści, a kiedy traci przewagę?

Najwyższy zysk wydajnościowy (wygrywa):
- Potoki Retrieval-Augmented Generation (RAG) – wspólny kontekst dokumentów.
- Systemy agentowe – te same zestawy narzędzi i instrukcji systemowych.
- Długie sesje czatu z rozbudowanym promptem systemowym.
- Zadania multimodalne (audio/wideo) z powtarzającymi się metadanymi początkowymi.

Brak odczuwalnych korzyści (wydajność zbieżna z vLLM):
- Generowanie jednokrotne (single-shot) z unikalnymi promptami (np. autouzupełnianie kodu źródłowego).
- Wysoce dynamiczne prompty, w których każde zapytanie wplata unikalne parametry na samym początku tekstu.

### Dlaczego harmonogramowanie jest kluczowe?

Współdzielenie bloków KV Cache można wdrożyć jako lokalną optymalizację jądra obliczeniowego, jednak zysk z tego rozwiązania jest widoczny tylko wtedy, gdy harmonogram (scheduler) dba o utrzymanie gorących gałęzi w pamięci podręcznej GPU. Naiwne podejście typu „użyj cache, jeśli jest dostępny” doprowadzi do ciągłej rotacji danych przy zróżnicowanym obciążeniu. SGLang zmienia tę optymalizację w stabilną przewagę produkcyjną na poziomie 29% dzięki wdrożeniu harmonogramu bezpośrednio zintegrowanego ze strukturą drzewa radix.

### Porównanie z silnikiem vLLM

Oba projekty rozwijają się równolegle. Silnik vLLM wprowadził buforowanie prefiksów (`--enable-prefix-caching`) oraz router analizujący stan cache (vLLM Router napisany w języku Rust). Różnica wydajnościowa zmniejszyła się, jednak SGLang od początku był projektowany wokół struktury drzewa skróconego, dzięki czemu zachowuje pozycję lidera w zadaniach z powtarzalnymi prefiksami. W przypadku ogólnych systemów bez wyraźnych wzorców powtarzalności początkowej, vLLM pozostaje rozwiązaniem o równej lub wyższej wydajności.

## Użyj tego

Skrypt `code/main.py` implementuje uproszczoną pamięć podręczną KV Cache opartą na drzewie radix oraz harmonogram obsługujący kolejkowanie w dwóch wariantach: FCFS oraz z uwzględnieniem stanu pamięci podręcznej (cache-aware). Uruchamia on testy dla obu metod, raportując wskaźnik trafień prefiksów oraz zysk wydajnościowy. Zawiera również test pokazujący spadek wydajności w przypadku zaburzenia kolejności elementów w promptach.

## Wdróż to (Ship It)

Do tej lekcji dołączono narzędzie `outputs/skill-radix-scheduler-advisor.md`. Na podstawie charakterystyki obciążenia (struktura szablonu promptu, specyfika pobierania kontekstu, poziom współbieżności) wygeneruje ono rekomendację dotyczącą wdrożenia silnika SGLang oraz instrukcję optymalnego ustrukturyzowania promptów.

## Ćwiczenia

1. Uruchom skrypt `code/main.py`. Porównaj wydajność kolejkowania FCFS oraz harmonogramu uwzględniającego cache przy tym samym profilu obciążenia. Z czego wynika uzyskana różnica – z oszczędności czasu fazy prefill, fazy decode czy ze skrócenia czasu oczekiwania w kolejce?
2. Zmodyfikuj symulator tak, aby kolejność elementów w promptach była losowo zmieniana: `[system, tools, context]`. Uruchom testy i przeanalizuj, co stało się ze współczynnikiem trafień w pamięci podręcznej oraz dlaczego.
3. Oblicz narzut pamięciowy (HBM) dla utrzymania w cache promptu systemowego o długości 2000 tokenów jako pojedynczej gałęzi drzewa radix dla modelu Llama 3.1 8B. Porównaj ten wynik z narzutem pamięciowym dla 16 niezależnych sesji bez współdzielenia prefiksu.
4. Przeanalizuj publikację naukową opisującą technologię RadixAttention. Wyjaśnij, dlaczego usuwanie danych z pamięci podręcznej na poziomie gałęzi (branch-level LRU) jest bardziej efektywne niż usuwanie na poziomie pojedynczych bloków (block-level LRU) w zadaniach z długimi prefiksami.
5. Klient zgłasza niski współczynnik trafień w pamięci podręcznej (cache hit rate) na poziomie zaledwie 8%. Wskaż trzy potencjalne przyczyny tego problemu i opisz procedurę diagnostyczną dla każdej z nich.

## Kluczowe terminy

| Termin | Potoczny opis | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| RadixAttention | „optymalizacja SGLang” | Mechanizm buforowania pamięci KV Cache oznaczony strukturą drzewa skróconego, pozwalający na współdzielenie obliczeń prefiksów. |
| Radix tree | „drzewo skrócone” | Struktura danych, w której każdy węzeł przechowuje fragment sekwencji tokenów oraz powiązane z nim bloki KV Cache. |
| Cache-aware scheduler | „harmonogram z cache” | Mechanizm kolejkowania, który nadaje priorytet zapytaniom korzystającym z gałęzi załadowanych aktualnie w pamięci GPU. |
| Prefix cache hit rate | „współczynnik trafień prefiksów” | Odsetek tokenów promptu wejściowego, dla których pobrano gotowe bloki KV Cache, pomijając obliczenia fazy prefill. |
| FCFS | „kolejkowanie czasowe” | First-Come, First-Served – standardowe kolejkowanie zapytań według czasu zgłoszenia, nieoptymalne dla buforowania prefiksów. |
| Branch-level LRU | „czyszczenie gałęzi” | Polityka usuwania danych z cache usuwająca najrzadziej używane gałęzie drzewa, zachowując spójność strukturalną. |
| Prompt ordering | „kolejność promptu” | Uporządkowanie elementów promptu wejściowego (od najbardziej statycznych do dynamicznych) w celu optymalizacji cache. |
| System prompt pinning | „przypinanie instrukcji” | Blokowanie usuwania z cache bloków KV Cache odpowiadających instrukcjom systemowym w celu zagwarantowania stałych zysków. |

## Dalsze czytanie

- [SGLang GitHub Repository](https://github.com/sgl-project/sglang) — kod źródłowy, instrukcje instalacji i dokumentacja.
- [SGLang Documentation](https://sgl-project.github.io/) — szczegółowe informacje o RadixAttention i konfiguracji harmonogramu.
- [SGLang Paper — Efficiently Programming Large Language Models (arXiv:2312.07104)](https://arxiv.org/abs/2312.07104) — publikacja naukowa definiująca założenia projektu.
- [LMSYS Blog — SGLang with RadixAttention](https://www.lmsys.org/blog/2024-01-17-sglang/) — oficjalne benchmarki wydajności i uzasadnienie projektowe.
- [vLLM Prefix Caching Feature](https://docs.vllm.ai/en/latest/features/prefix_caching.html) — opis implementacji buforowania prefiksów w silniku vLLM do analizy porównawczej.
