# SGLang i RadixAttention do obciążeń wymagających dużych prefiksów

> SGLang traktuje pamięć podręczną KV jako pierwszorzędny zasób wielokrotnego użytku przechowywany w drzewie radix. Tam, gdzie vLLM planuje żądania FCFS (kto pierwszy, ten lepszy), harmonogram obsługujący pamięć podręczną SGLang nadaje priorytet żądaniom z dłuższymi współdzielonymi prefiksami — w rzeczywistości jest to przechodzenie w głąb podstawy, dzięki czemu gorące gałęzie pozostają rezydujące w HBM. W Llama 3.1 8B z podpowiedziami 1K podobnymi do ShareGPT, SGLang osiąga ~16 200 tok/s do ~12 500 tok/s vLLM, co stanowi przewagę ~29%. W przypadku obciążeń RAG z dużą ilością prefiksów przewaga sięga 6,4x. W przypadku obciążeń związanych z klonowaniem głosu współczynnik trafień w pamięci podręcznej wyczyścił 86%. Wdrożone na ponad 400 000 procesorów graficznych w 2026 r. w platformach xAI, LinkedIn, Cursor, Oracle, GCP, Azure i AWS. Problem w tym, że liczba 6,4x zanika, gdy kolejność prefiksów jest niespójna — kolejność jest dźwignią inżyniera.

**Typ:** Ucz się
**Języki:** Python (stdlib, pamięć podręczna drzewa radix-tree + harmonogram obsługujący pamięć podręczną)
**Wymagania wstępne:** Faza 17 · 04 (wewnętrzni pracownicy vLLM), faza 14 (Agentic RAG)
**Czas:** ~75 minut

## Cele nauczania

- Diagram RadixAttention: jak prefiksy są przechowywane w drzewie radix i jak bloki KV są współdzielone pomiędzy sekwencjami zakorzenionymi w tej samej gałęzi.
- Wyjaśnij planowanie uwzględniające pamięć podręczną i dlaczego FCFS jest niewłaściwy w przypadku ruchu z dużą ilością prefiksów.
- Oblicz oczekiwane przyspieszenie dla obciążenia, biorąc pod uwagę współczynnik trafień w pamięci podręcznej prefiksów i rozkład długości podpowiedzi.
- Wymień dyscyplinę szybkiego zamawiania, która sprawia, że ​​liczba 6,4x jest realna w porównaniu z utraconą zaletą.

## Problem

Udostępnianie klasyczne traktuje monit o każdym żądaniu jako nieprzejrzysty. Nawet jeśli wszystkie 5000 żądań RAG rozpoczyna się od tego samego monitu systemowego zawierającego 2000 tokenów i tej samej preambuły pobierania, vLLM wstępnie wypełnia ten prefiks zawierający 2000 tokenów 5000 razy. Procesor graficzny wykonuje w kółko tę samą pracę.

Obserwacja: podpowiedzi w obciążeniach agentowych i RAG prawie zawsze mają wspólne długie przedrostki. Podpowiedź systemowa, schematy narzędzi, kilka przykładów, nagłówki pobierania, historia rozmów – wszystko to powtarza się w przypadku żądań. Jeśli raz zapisałeś pamięć podręczną KV dla tego prefiksu i użyłeś jej ponownie, nie wypełniłbyś jej ponownie.

RadixAttention robi dokładnie to. Tokeny są indeksowane w drzewie radix; każdy węzeł posiada bloki KV dla sekwencji tokenów na swojej ścieżce od katalogu głównego. Nowe żądanie przechodzi przez drzewo: każdy węzeł, którego token pasuje, ponownie wykorzystuje bloki KV tego węzła. Koszt wstępnego wypełnienia staje się proporcjonalny do „nowego” sufiksu, a nie do pełnego monitu.

Wyzwaniem jest planowanie. Jeśli dwa żądania mają wspólny prefiks zawierający 2000 tokenów, a trzecie ma tylko 200 tokenów tego samego prefiksu, chcesz obsłużyć dwa długo współdzielone żądania razem, tak aby długi prefiks pozostał w HBM. FCFS działa odwrotnie — obsługuje każdego, kto przybył pierwszy, potencjalnie eksmitując gorącą gałąź przed trafieniem kolejnego żądania z długim prefiksem.

## Koncepcja

### Drzewo radix jako indeks KV

Drzewo radix (zwarte trie) przechowuje sekwencje tokenów. Każdy węzeł posiada zakres tokenów i bloki KV obliczone dla tego zakresu. Dzieci rozszerzają sekwencję o jeden lub więcej żetonów.

```
root
 |- "You are a helpful assistant..."  (2,000 tokens, 124 KV blocks)
      |- "Context: <doc A>..."        (500 tokens, 31 blocks)
           |- "Question: Alice..."    (80 tokens, 5 blocks)
           |- "Question: Bob..."      (95 tokens, 6 blocks)
      |- "Context: <doc B>..."        (520 tokens, 33 blocks)
```

Pojawia się nowe żądanie z zachętą systemową + „Kontekst: <doc A>” + „Pytanie: Karol”. Program planujący przegląda: dopasowania prefiksów systemowych (ponownie wykorzystane 124 bloki), dopasowania gałęzi doc-A (ponownie wykorzystane 31 bloków), a następnie przydziela nowe bloki tylko dla „Pytanie: Carol” (4 bloki). Koszt wstępnego uzupełnienia: 4 bloki nowych tokenów. Bez drzewa: 160 bloków. ~40x oszczędność na wstępnym napełnieniu.

### Planowanie uwzględniające pamięć podręczną

Ponowne użycie oparte na drzewie Radix jest bezcelowe, jeśli pamięć podręczna ulegnie zmianie. Dwie kluczowe zasady:

1. **Wysyłka w głąb**. Wybierając kolejne żądanie z kolejki, preferuj żądania zrootowane w tej samej gałęzi, w której znajduje się bieżący zestaw. Dzięki temu gorąca gałąź zostanie przygwożdżona.
2. **LRU na poziomie oddziału, a nie bloku**. Eksmituj całe gałęzie (zaczynając od najkrócej używanych liści), a nie pojedyncze bloki, tak aby kształt skrytki odpowiadał kształtowi podstawy.

FCFS narusza oba. Żądanie udostępnienia 2000 tokenów znajduje się za żądaniem udostępnienia 50, a następnie oddział z 2000 tokenami zostaje eksmitowany, aby przyjąć oddział z 50 tokenami.

### Liczby wzorcowe, które powinieneś zapamiętać

- Komunikaty Lamy 3.1 8B, H100, ShareGPT 1K: SGLang ~16 200 tok/s w porównaniu z vLLM ~12 500 (~29% krawędzi).
- RAG z dużą liczbą prefiksów (ten sam system + ten sam dokument, różne pytania): do 6,4x w SGLang.
- Obciążenia związane z klonowaniem głosu: współczynnik trafień w pamięci podręcznej prefiksów na poziomie 86,4%.
- Wskaźniki trafień produkcyjnych u klientów SGLang: 50-99% w zależności od szybkiej dyscypliny.
— Wdrożono na ponad 400 000 procesorów graficznych w 2026 r.

### Problem z zamówieniem

Liczba 6,4x opiera się na spójnej kolejności w szablonie podpowiedzi. Jeśli Twój klient konstruuje podpowiedzi jako `[system, tools, context, history, question]` w niektórych żądaniach i `[system, context, tools, history, question]` w innych, drzewo nie może znaleźć współdzielonego prefiksu. To, co wygląda na wspólny przedrostek dla człowieka, jest dwiema odrębnymi sekwencjami drzewa podstawy.

Dźwignia inżyniera: szablon podpowiedzi to klucz do pamięci podręcznej. Napraw zamówienie. Na pierwszym miejscu umieść wszystko, co niezmienne (system, narzędzia, schematy). Następnie umieść kontekst pobierania. Umieść pytanie użytkownika na końcu. Nie przeplataj zawartości dynamicznej z przedrostkiem.

Prawdziwy przypadek z badania: przeniesienie zawartości dynamicznej z prefiksu buforowanego wymagało jednego wdrożenia współczynnika trafień w pamięci podręcznej z 7% do 74% w jednej zmianie.

### Gdzie RadixAttention wygrywa i przegrywa

Wygrywa:
- RAG (ta sama preambuła wyszukiwania, różne pytania).
- Agenci (te same schematy narzędzi, różne zapytania).
- Czat z długim monitem systemowym.
- Obciążenia głosowe/wizyjne z powtarzającymi się preambułami.

Straty (powraca do przepustowości na poziomie vLLM):
- Generowanie pojedynczego strzału z unikalnymi monitami (uzupełnianie kodu, otwarty czat bez podpowiedzi systemowych).
- Dynamiczne monity, w których każde żądanie wplata unikalną treść w prefiks.

### Dlaczego jest to problem z harmonogramem, a nie tylko z jądrem

Możesz zaimplementować ponowne użycie KV jako sztuczkę jądra. SGLang uważa, że ​​ponowne użycie opłaca się tylko wtedy, gdy program planujący utrzymuje rezydentną gałąź gorącą. Naiwna zasada „użyj ponownie, jeśli jest dostępna” spowoduje zmianę pamięci podręcznej przy mieszanym obciążeniu. Harmonogram indeksowany radix-tree zmienia sztuczkę jądra w 29% przewagę produkcyjną.

### Współpraca z vLLM

Te dwa systemy nie stanowią ścisłej konkurencji. W 2026 vLLM dodał buforowanie prefiksów (`--enable-prefix-caching`) i router obsługujący pamięć podręczną (vLLM Router w Rust). Luka zmniejszyła się, ale nie zniknęła całkowicie — cały stos SGLanga jest oparty na podstawie; vLLM go zaszczepił. W przypadku obciążeń zdominowanych przez ponowne użycie prefiksów SGLang pozostaje domyślnym. W przypadku obsługi ogólnego przeznaczenia bez silnych wzorców przedrostków wartość vLLM pozostaje taka sama lub lepsza.

## Użyj tego

`code/main.py` implementuje zabawkową pamięć podręczną KV radix-tree oraz harmonogram z dwiema zasadami: FCFS i obsługującą pamięć podręczną. Uruchamia to samo obciążenie w obu przypadkach, raportuje współczynnik trafień w pamięci podręcznej prefiksów i różnicę przepustowości. Następnie uruchamia obciążenie „kodowanym porządkowaniem”, aby pokazać zwinięcie 6,4x.

## Wyślij to

Ta lekcja przedstawia `outputs/skill-radix-scheduler-advisor.md`. Biorąc pod uwagę opis obciążenia (kształt szablonu podpowiedzi, wzorzec pobierania, liczbę jednoczesnych dzierżawców), generuje receptę na szybkie zamówienie i decyzję o przyjęciu/nie przyjęcia SGLang.

## Ćwiczenia

1. Uruchom `code/main.py`. Porównaj FCFS i obsługę pamięci podręcznej przy tym samym obciążeniu. Skąd bierze się delta – oszczędności przy wstępnym wypełnieniu, oszczędności przy dekodowaniu czy opóźnienie w kolejce?
2. Zmodyfikuj obciążenie tak, aby monity losowo przełączały `[system, tools, context]`. Ponowne odtworzenie. Co się dzieje ze współczynnikiem trafień? Dlaczego?
3. Oblicz koszt HBM utrzymania rezydenta podpowiedzi systemowej o pojemności 2000 tokenów jako jednej gałęzi radix w Lamie 3.1 8B. Porównaj z kosztem partii 16 sekwencji bez ponownego użycia prefiksu.
4. Przeczytaj dokument SGLang RadixAttention. Wyjaśnij w trzech zdaniach, dlaczego eksmisja LRU w kształcie drzewa jest lepsza od LRU w kształcie bloku przy dużym obciążeniu przedrostkiem.
5. Klient zgłasza tylko 8% współczynnika trafień w pamięci podręcznej. Wymień trzy prawdopodobne przyczyny i diagnostykę, którą przeprowadziłbyś dla każdej z nich.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| RadixUwaga | „sprawa SGLang” | Pamięć podręczna KV indeksowana jako drzewo radix, więc współdzielone prefiksy ponownie wykorzystują bloki |
| Drzewo radix | „kompaktowa próba” | Drzewo, w którym każdy węzeł posiada zakres tokenów i jego bloki KV |
| Harmonogram obsługujący pamięć podręczną | „najpierw gorąca gałąź” | Harmonogram preferujący żądania współdzielenia gałęzi rezydentnej |
| Współczynnik trafień w pamięci podręcznej prefiksów | „Jaka część Twojego monitu była bezpłatna” | Część tokenów podpowiedzi obsługiwanych z ponownie wykorzystanych bloków KV |
| FCFS | „kto pierwszy, ten lepszy” | Domyślne planowanie, które przerywa lokalizację prefiksu |
| LRU na poziomie oddziału | „eksmituj liść” | Polityka eksmisyjna dopasowana do kształtu podstawy |
| Szybkie zamawianie szablonu | „klucz pamięci podręcznej” | Kolejność komponentów podpowiedzi określa, co drzewo może współdzielić |
| Przypinanie monitu systemowego | „prefiks rezydenta” | Trzymaj niezmienną część systemu przypiętą, aby uniknąć wyrzucania |

## Dalsze czytanie

- [SGLang GitHub](https://github.com/sgl-project/sglang) — źródło i dokumentacja.
- [Dokumentacja SGLang](https://sgl-project.github.io/) — RadixAttention i szczegóły harmonogramu.
- [Dokument SGLang — Efektywne programowanie modeli dużych języków (arXiv:2312.07104)](https://arxiv.org/abs/2312.07104) — odniesienie do projektu.
- [Blog LMSYS — SGLang z RadixAttention](https://www.lmsys.org/blog/2024-01-17-sglang/) — liczby testów porównawczych i uzasadnienie harmonogramu.
- [vLLM — Prefix Caching](https://docs.vllm.ai/en/latest/features/prefix_caching.html) — dla porównania własna implementacja vLLM przypominająca radix.