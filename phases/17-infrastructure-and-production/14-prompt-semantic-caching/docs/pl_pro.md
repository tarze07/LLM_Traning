# Natychmiastowe buforowanie i ekonomia buforowania semantycznego

> **Przegląd cen z dnia 2026-04.** Poniższe wartości odzwierciedlają stawki dostawców zarejestrowane w momencie publikacji tej lekcji; przed zacytowaniem ich w dalszej części tekstu zweryfikuj je z aktualną dokumentacją.

> Buforowanie odbywa się w dwóch warstwach. Buforowanie promptów/prefiksów L2 (na poziomie dostawcy API) ponownie wykorzystuje pamięć podręczną KV-cache dla powtarzających się prefiksów – dokumentacja firmy Anthropic dotycząca buforowania promptów zapowiada redukcję kosztów o 90% i skrócenie opóźnień o 85% w przypadku długich promptów; dla Claude 3.5 Sonnet odczyt z pamięci podręcznej kosztuje $0.30/M zamiast $3.00/M (stawka standardowa) przy 5-minutowym TTL i z 2-krotnym narzutem za zapis dla opcji z 1-godzinnym TTL (docs.anthropic.com, 2026-04). Buforowanie promptów w OpenAI jest stosowane automatycznie w przypadku zapytań zawierających ≥1024 tokenów, a przetwarzanie buforowanych danych wejściowych jest objęte około 90% rabatem w stosunku do standardowych stawek (platform.openai.com, 2026–04); dokładna stawka dla każdego modelu zależy od aktualnego cennika. Buforowanie semantyczne L1 (na poziomie aplikacji) pozwala całkowicie pominąć LLM w przypadku wykrycia podobnego zapytania na podstawie osadzeń (embeddings). Deklarowana przez dostawców „dokładność na poziomie 95%” odnosi się do trafności dopasowania semantycznego, a nie do współczynnika trafień (hit rate) – w warunkach produkcyjnych współczynnik ten waha się od 10% (otwarty czat) do 70% (ustrukturyzowane bazy FAQ); żaden z dostawców nie publikuje oficjalnych danych bazowych, dlatego te statystyki należy traktować jako dane społecznościowe, a nie gwarantowane parametry. Pułapki produkcyjne: współbieżność (równoległość) niszczy efektywność buforowania (N równoległych zapytań wysłanych przed wykonaniem pierwszego zapisu w pamięci podręcznej może drastycznie zwiększyć koszty), a dynamiczna treść wewnątrz prefiksu całkowicie uniemożliwia trafienia. Zespół ProjectDiscovery zgłosił wzrost współczynnika trafień z 7% do 74% (2025-11) po przeniesieniu dynamicznego tekstu poza buforowany prefiks.

**Typ:** Teoria i praktyka
**Języki:** Python (stdlib, uproszczony symulator dwuwarstwowej pamięci podręcznej)
**Wymagania wstępne:** Faza 17 · 04 (Wewnętrzna architektura vLLM), faza 17 · 06 (SGLang RadixAttention)
**Czas:** ~60 minut

## Cele naukowe

- Rozróżnianie buforowania promptów/prefiksów L2 (ponowne użycie pamięci podręcznej KV-cache u dostawcy API) od buforowania semantycznego L1 (omijanie LLM w przypadku podobnych promptów).
- Wyjaśnienie jawnego oznaczania `cache_control` w API Anthropic oraz dwóch opcji TTL (5 minut vs 1 godzina) wraz z ich mnożnikami kosztów.
- Obliczanie oczekiwanych miesięcznych oszczędności na podstawie współczynnika trafień (hit rate), proporcji promptów do odpowiedzi oraz cennika tokenów.
- Zidentyfikowanie antywzorca współbieżności, który może zwiększyć rachunki 5-10 razy, oraz antywzorca dynamicznej zawartości, drastycznie obniżającego współczynnik trafień.

## Problem

Wdrażasz buforowanie promptów w swojej usłudze RAG, ale rachunki nie spadają. Mierzysz współczynnik trafień (hit rate) i wynosi on zaledwie 7%. Twoje prompty wydają się statyczne, ale w rzeczywistości tak nie jest – prompt systemowy zawiera bieżącą datę z dokładnością do minuty, identyfikator żądania (request ID) oraz losowo zmieniający się zestaw przykładów mający zapewnić różnorodność odpowiedzi. W rezultacie każde zapytanie tworzy nowy wpis w pamięci podręcznej i nie dochodzi do żadnych odczytów.

Innym problemem jest sytuacja, w której agent wykonuje dziesięć równoległych wywołań narzędzi dla jednego pytania użytkownika. Wszystkie dziesięć zapytań dociera do dostawcy API zanim zakończy się pierwszy zapis w pamięci podręcznej. Skutkuje to dziesięcioma zapisami i zerem odczytów. Ostatecznie rachunek jest 5-10 razy wyższy niż zakładane koszty działania „z buforowaniem”.

Buforowanie to protokół postępowania, a nie zwykły przełącznik. Mamy tu do czynienia z dwiema warstwami i dwoma różnymi scenariuszami awarii.

## Koncepcja

### L2 – Buforowanie promptów/prefiksów u dostawcy (Provider-level)

Dostawca przechowuje wartości kluczy i zapytań (KV-cache) dla buforowanego prefiksu i wykorzystuje je przy kolejnym zapytaniu pasującym do tego prefiksu. Płacisz raz za zapis, a odczytujesz po znacznie obniżonej stawce.

**Anthropic (seria Claude 3.5 / 3.7 / 4)**: jawne oznaczanie bloków do buforowania za pomocą parametru `cache_control` w zapytaniu. Sam decydujesz, które sekcje mają trafić do pamięci podręcznej. Dostępne są dwa warianty TTL: 5 minut (zapis kosztuje 1,25x stawki bazowej) lub 1 godzina (zapis kosztuje 2x stawki bazowej). Odczyt buforowanych tokenów dla Claude 3.5 Sonnet kosztuje $0.30/M w porównaniu do $3.00/M za świeże dane – czyli 10-krotnie taniej (docs.anthropic.com, stan na kwiecień 2026). Ceny różnią się w zależności od modelu (Opus/Haiku mają inne stawki); zawsze weryfikuj cennik na żywo.

**OpenAI**: automatyczne buforowanie promptów o długości ≥1024 tokenów (platform.openai.com, kwiecień 2026). Brak konieczności stosowania dodatkowych flag. Buforowane tokeny wejściowe są około 10 razy tańsze od standardowych w aktualnych cennikach dla gpt-4o/gpt-5. Dokumentacja nie podaje domyślnego współczynnika trafień, ale społeczność raportuje wyniki na poziomie 30–60% przy odpowiedniej konstrukcji promptów. Aby monitorować te dane, analizuj wartość `usage.cached_tokens` w odpowiedziach API.

**Google (Gemini)**: buforowanie kontekstu (context caching) realizowane przez jawne API; przy kontekstach sięgających 1M tokenów przynosi to ogromne oszczędności.

**Własny hosting (vLLM, SGLang)**: W fazie 17 · 06 omówiono mechanizm RadixAttention, który wdraża ten sam schemat w ramach własnej infrastruktury obliczeniowej.

### L1 – Buforowanie semantyczne na poziomie aplikacji (Application-level)

Zanim wyślesz zapytanie do LLM, tworzysz osadzenie wektorowe (embedding) promptu i szukasz podobnego żądania w lokalnej pamięci podręcznej (stosując podobieństwo cosinusowe powyżej określonego progu, zazwyczaj 0.95+). W przypadku trafienia zwracana jest bezpośrednio odpowiedź z pamięci podręcznej. Przy braku trafienia następuje wywołanie LLM, a jego wynik jest zapisywany w bazie.

Rozwiązania open source: Redis (wyszukiwanie wektorowe), GPTCache, Qdrant. Rozwiązania komercyjne: Portkey, Helicone.

Deklaracje dostawców dotyczące dokładności (np. 95%) określają, jak często zwrócona odpowiedź z pamięci podręcznej była poprawna semantycznie, a nie jak często dochodziło do trafienia (hit rate). Rzeczywiste współczynniki trafień w środowisku produkcyjnym:

- Otwarty czat: 10–15%.
- Ustrukturyzowane FAQ / systemy wsparcia: 40–70%.
- Zapytania dotyczące kodu: 20–30% (nawet drobne różnice w składni uniemożliwiają trafienie).
- Agenci głosowi o powtarzalnych schematach: 50–80% (przy zastosowaniu normalizacji tekstu).

### Antywzorzec współbieżności (Parallelism Antipattern)

Agent wykonuje równolegle 10 wywołań narzędzi. Wszystkie 10 zapytań zawiera ten sam prompt systemowy o rozmiarze 4K tokenów. Zapisy w pamięci podręcznej Anthropic odbywają się na żądanie – pierwszy zapis kończy się około 300 ms po przetworzeniu promptu przez dostawcę. Zapytania od 2 do 10 docierają w tym samym oknie czasowym (milisekundowym) i w każdym z nich następuje brak trafienia (cache miss). Płacisz 10-krotny narzut za zapis zamiast skorzystać z rabatu za odczyt.

Rozwiązanie: Wyślij najpierw pierwsze żądanie sekwencyjnie, a po zapełnieniu cache (po ok. 300 ms) uruchom równolegle zapytania 2–10. Doda to drobne opóźnienie do pierwszego wywołania, ale pozwoli obniżyć koszty nawet 5-10 razy.

### Antywzorzec dynamicznej zawartości (Dynamic Content Antipattern)

Prompt systemowy wygląda następująco:

```
You are a helpful assistant. The current time is 14:32:17.
User ID: abc123. Today is Tuesday...
```

Każde zapytanie staje się unikalne, wywołując zapis nowej pamięci podręcznej bez jakichkolwiek trafień.

Rozwiązanie: Przenieś statyczną część instrukcji na początek (do buforowanego prefiksu), a dynamiczne zmienne umieść na samym końcu, poza obszarem buforowania:

```
[cacheable]
You are a helpful assistant. [rules, examples, instructions]
[/cacheable]
[dynamic, not cached]
Current time: 14:32:17. User: abc123.
```

W ten sposób zespół ProjectDiscovery zwiększył współczynnik trafień w cache z 7% do 74%, publikując szczegółową analizę tego przypadku.

### Łączenie trybu wsadowego (Batch) z buforowaniem dla zadań asynchronicznych

Batch API (omówione w fazie 17 · 15) oferuje 50% zniżki przy realizacji zadań w ciągu 24 godzin. Nałożenie na to buforowania promptów pozwala obniżyć koszty dodatkowo ok. 10-krotnie. Dzięki połączeniu tych metod, koszty nocnego przetwarzania (np. klasyfikacji, etykietowania czy generowania raportów) mogą spaść do zaledwie ~10% ceny synchronicznego przetwarzania bez użycia cache.

### Kluczowe statystyki do zapamiętania

Podane ceny pochodzą z dokumentacji dostawców z kwietnia 2026 roku i mogą ulegać zmianom – należy je zweryfikować przed wdrożeniem produkcyjnym.

- Odczyt z pamięci podręcznej Anthropic: $0.30/M tokenów w Claude 3.5 Sonnet, czyli około 10 razy taniej niż w przypadku standardowego przetwarzania wejścia (docs.anthropic.com).
- Narzut za zapis w cache Anthropic: 1,25x (przy TTL 5 minut) lub 2x (przy TTL 1 godzina).
- Automatyczne buforowanie w OpenAI: włączane dla promptów ≥1024 tokenów; dane w cache kosztują ok. 10% standardowej ceny wejściowej (platform.openai.com).
- Współczynnik trafień w pamięci podręcznej semantycznej (dane społeczności): ~10% dla luźnych konwersacji, do ~70% dla ustrukturyzowanych systemów FAQ. Brak oficjalnych gwarancji ze strony dostawców.
- ProjectDiscovery: wzrost współczynnika trafień z 7% do 74% po usunięciu dynamicznych elementów z prefiksu (dane z bloga projektu, listopad 2025).
- Antywzorzec współbieżności: 5-10 razy wyższe koszty w przypadku wysłania N równoległych zapytań przed ukończeniem pierwszego zapisu w cache.

## Praktyczne zastosowanie

Skrypt `code/main.py` symuluje działanie buforowania L1 i L2 przy zrównociowanym ruchu. Prezentuje on współczynniki trafień, koszty oraz obrazuje stratę finansową wynikającą ze współbieżnego wysyłania zapytań.

## Zadanie wdrożeniowe

W ramach tej lekcji przygotowano plik `outputs/skill-cache-auditor.md`. Narzędzie to analizuje szablon promptu oraz charakterystykę ruchu, oceniając podatność na buforowanie i proponując optymalną restrukturyzację kodu.

## Ćwiczenia

1. Uruchom `code/main.py`. Zmień flage dotyczącą współbieżności. Jak wpłynęło to na ostateczny rachunek?
2. Prompt systemowy zawiera dynamiczną datę. Przenieś ją w inne miejsce. Oblicz i porównaj współczynnik trafień przed i po zmianie.
3. Biorąc pod uwagę częstotliwość napływu żądań, oblicz próg opłacalności dla TTL trwającego 1 godzinę (narzut zapisu 2x) w porównaniu z TTL wynoszącym 5 minut (narzut zapisu 1,25x).
4. Semantyczna pamięć podręczna z progiem podobieństwa 0.95 daje współczynnik trafień na poziomie 20%. Przy progu 0.85 wzrasta on do 50%, ale w odpowiedziach pojawiają się halucynacje i błędnie dopasowane dane. Wybierz optymalny próg i uzasadnij swoją decyzję.
5. Wysyłasz równolegle 10 podzapytań na jedno pytanie użytkownika. Przepisz logikę aplikacji tak, aby była przyjazna dla buforowania, minimalizując jednocześnie dodatkowe opóźnienia (latency).

## Słownik pojęć

| Termin | Popularne określenie | Rzeczywiste znaczenie |
|------|----------------|--------------------------------------|
| Pamięć podręczna promptów L2 | „buforowanie prefiksów” | Przechowywanie KV-cache przez dostawcę dla powtarzających się fragmentów |
| `cache_control` | „znacznik cache Anthropic” | Jawne nagłówki/atrybuty oznaczające bloki przeznaczone do buforowania |
| Narzut za zapis w cache | „koszt zapisu” (write cost) | Dodatkowa opłata za pierwszy zapis przy cache miss (1.25x lub 2x stawki standardowej) |
| Pamięć podręczna semantyczna L1 | „buforowanie wektorowe” | Porównywanie osadzeń (embeddings) na poziomie aplikacji przed wysłaniem zapytania do LLM |
| GPTCache | „biblioteka buforowania LLM” | Popularna biblioteka open-source do obsługi pamięci podręcznej L1 |
| Współczynnik trafień w cache | „hit rate” | Odsetek zapytań obsłużonych bezpośrednio z pamięci podręcznej |
| Antywzorzec współbieżności | „problem jednoczesnych zapisów” | Sytuacja, w której N równoległych zapytań generuje błąd cache (miss) i powiela koszty zapisu |
| Pułapka dynamicznej treści | „zmienna w nagłówku” | Dynamiczne elementy umieszczone zbyt wcześnie w prompcie, uniemożliwiające buforowanie prefiksu |
| RadixAttention | „wbudowany cache silnika” | Wydajna implementacja pamięci podręcznej prefiksów w silniku SGLang |

## Materiały uzupełniające

- [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) – oficjalna dokumentacja dotycząca specyfikacji `cache_control` oraz czasów TTL.
- [OpenAI Prompt Caching](https://platform.openai.com/docs/guides/prompt-caching) – szczegóły automatycznego buforowania i rozliczeń.
- [TianPan – Semantic Caching for LLM Production](https://tianpan.co/blog/2026-04-10-semantic-caching-llm-production)
- [ProjectDiscovery – How we cut LLM cost by 59% with prompt caching](https://projectdiscovery.io/blog/how-we-cut-llm-cost-with-prompt-caching)
- [DigitalOcean / Anthropic – Prompt Caching with DigitalOcean](https://www.digitalocean.com/blog/prompt-caching-with-digital-ocean)
