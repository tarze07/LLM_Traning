# Pamięć: kontekst wirtualny i MemGPT

> Okna kontekstowe są skończone. Rozmowy, dokumenty i ślady narzędzi nie są. MemGPT (Packer i in., 2023) przedstawia tę pamięć jako pamięć wirtualną systemu operacyjnego — głównym kontekstem jest pamięć RAM, magazynem zewnętrznym jest dysk, a strony agentów pomiędzy nimi. Jest to wzór dziedziczony przez każdy system pamięci 2026.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (pętla agenta), faza 14 · 06 (użycie narzędzi)
**Czas:** ~75 minut

## Cele nauczania

- Wyjaśnij analogię systemu operacyjnego, na której opiera się MemGPT: kontekst główny = pamięć RAM, kontekst zewnętrzny = dysk, narzędzia pamięci = wejście/wyjście strony.
- Zaimplementuj dwupoziomowy wzorzec MemGPT w stdlib z buforem kontekstu głównego, zewnętrznym magazynem z możliwością przeszukiwania i narzędziami do wejścia/wyjścia strony.
- Opisz, w jaki sposób agent wydaje „przerwania” w celu wykonania zapytania lub modyfikacji pamięci zewnętrznej oraz w jaki sposób wynik jest umieszczany z powrotem w następnym znaku zachęty.
- Zidentyfikuj wybory projektowe MemGPT, które mają zastosowanie w Letta (lekcja 08) i Mem0 (lekcja 09).

## Problem

Okna kontekstowe wyglądają tak, jakby powinny rozwiązać pamięć. Oni nie. W produkcji powtarzają się trzy tryby awarii:

1. **Przepełnienie.** Wielokrotne rozmowy, długie dokumenty lub trajektorie wymagające wielu narzędzi przechodzą przez okno. Wszystko poza wartością odcięcia zniknęło.
2. **Rozmycie.** Nawet w oknie upychanie nieistotnego kontekstu osłabia uwagę na to, co ważne. Modele graniczne nadal ulegają degradacji przy długich danych wejściowych.
3. **Trwałość.** Nowa sesja rozpoczyna się z pustym oknem. Agenci bez pamięci zewnętrznej nie mogą powiedzieć „pamiętaj, kiedy mnie o to poprosiłeś…” podczas sesji.

Większe okna pomagają, ale nie naprawiają tego. W artykule Mem0 z 2025 r. zmierzono, że w wartościach bazowych dla 128 tys. okien w dalszym ciągu brakuje faktów z odległej perspektywy, które wychwytuje agent obsługujący 4 tys. okien z pamięcią zewnętrzną.

## Koncepcja

### MemGPT: analogia do systemu operacyjnego

Packera i in. (arXiv:2310.08560, v2, lut 2024) mapuj zarządzanie kontekstem na pamięć wirtualną systemu operacyjnego:

| Koncepcja systemu operacyjnego | Koncepcja MemGPT | Analog produkcyjny 2026 |
|------------|----------------------------|----------------------------|
| RAM | kontekst główny (podpowiedź) | Okno kontekstowe Anthropic/OpenAI |
| Dysk | kontekst zewnętrzny | wektor DB, KV, sklep z wykresami |
| Błąd strony | wywołanie narzędzia pamięci | `memory.search`, `memory.read`, `memory.write` |
| Jądro systemu operacyjnego | pętla kontroli agenta | Pętla ReAct z narzędziami pamięci |

Agent uruchamia normalną pętlę ReAct. Jedna dodatkowa klasa narzędzi umożliwia stronicowanie danych w głównym kontekście i poza nim.

### Dwa poziomy

- **Kontekst główny.** Podpowiedź o stałym rozmiarze, zawierająca bieżące zadanie. Zawsze widoczny dla modela.
- **Kontekst zewnętrzny.** Nieograniczony, można przeszukiwać za pomocą narzędzi. Przeczytaj, jeśli jest to istotne, zapisz, gdy pojawią się fakty.

W oryginalnym artykule oceniano projekt pod kątem dwóch zadań wykraczających poza okno podstawowe: analizy dokumentów dłuższych niż 100 tys. tokenów i wielosesyjnego czatu z pamięcią trwałą przez kilka dni.

### Wzór przerwania

MemGPT wprowadza pamięć jako przerwanie: w połowie rozmowy agent może wywołać narzędzie pamięci, środowisko wykonawcze wykonuje je, a wynik jest dołączany do następnej tury asystenta jako nowa obserwacja. Koncepcyjnie identyczne z wywołaniem systemowym `read()` Uniksa, które blokuje proces, zwraca bajty i proces jest kontynuowany.

Powierzchnia narzędzia pamięci kanonicznej:

- `core_memory_append(section, text)` — zapisz w trwałej sekcji zachęty.
- `core_memory_replace(section, old, new)` — edytuj sekcję stałą.
- `archival_memory_insert(text)` — napisz do zewnętrznego sklepu z możliwością przeszukiwania.
- `archival_memory_search(query, top_k)` — pobierz z magazynu zewnętrznego.
- `conversation_search(query)` — skanuj poprzednie zakręty.

### Gdzie kończy się MemGPT, a zaczyna Letta

We wrześniu 2024 r. MemGPT zmieniło się w Lettę. Repozytorium badawcze (`cpacker/MemGPT`) pozostaje; Letta rozszerza projekt:

- Trzy poziomy zamiast dwóch (podstawowy, przywoławczy, archiwalny — lekcja 08).
- Natywne rozumowanie zastępujące wzorzec `send_message`/heartbeat (lekcja 08).
- Agenci uśpienia pracujący z pamięcią asynchroniczną (Lekcja 08).

Papier MemGPT jest podstawą na rok 2026, nawet jeśli na systemach produkcyjnych działają Letta, Mem0 lub niestandardowy sklep dwupoziomowy.

### Gdzie ten wzorzec jest błędny

- **Zniszczenie pamięci.** Zapisy gromadzą się szybciej niż odczyty; odzyskiwanie tonie w nieaktualnych faktach. Poprawka: konsolidacja okresowa (czas snu Letta), jawne unieważnianie (wykrywacz konfliktu Mem0).
- **Zatrucie pamięci.** Pamięć zewnętrzna odzyskała tekst. Jeśli zawartość kontrolowana przez osobę atakującą wyląduje w notatce pamięci, agent ponownie ją przetworzy w następnej sesji. To jest Greshake i in. (Lekcja 27) atak powtórzył się w czasie.
- **Utrata cytatów.** Agent przypomina sobie, że „użytkownik poprosił mnie o wysłanie X”, ale nie może podać, w której turze. Przechowuj odniesienia do źródeł (identyfikator sesji, identyfikator zwrotu) przy każdym zapisie archiwalnym.

## Zbuduj to

`code/main.py` implementuje dwupoziomowy wzorzec MemGPT w stdlib:

- `MainContext` — bufor podpowiedzi o stałym rozmiarze z dyktatem `core` i listą `messages`; automatycznie kompresuje najstarsze wiadomości w przypadku przekroczenia limitu.
- `ArchivalStore` — pamięć w stylu BM25 (punktacja nakładania się tokenów) rekordów (identyfikator, tekst, tagi, sesja, kolej).
- Pięć narzędzi do mapowania pamięci na powierzchnię MemGPT.
- Agent skryptowy, który wypełnia archiwa faktami, a następnie odpowiada na pytanie, dzwoniąc pod numer `archival_memory_search`.

Uruchom to:

```
python3 code/main.py
```

Ślad pokazuje, jak agent zapisuje trzy fakty, wypełnia główny kontekst do końca (wymuszając eksmisję), a następnie odpowiada na pytanie uzupełniające, pobierając z archiwum — odtwarzając przepływ pracy MemGPT bez prawdziwego LLM.

## Użyj tego

Każdy dzisiejszy system pamięci produkcyjnej jest wariantem MemGPT:

- **Letta** (Lekcja 08) — trzy poziomy, rozumowanie natywne, obliczanie czasu snu.
- **Mem0** (Lekcja 09) — wektor + KV + wykres połączony z warstwą scoringową.
- **Asystenci / Odpowiedzi OpenAI** — zarządzanie pamięcią poprzez wątki i pliki.
- **Claude Agent SDK** — pamięć długoterminowa poprzez umiejętności i magazyn sesji.

Wybierz jeden według kształtu operacyjnego (samodzielnie hostowany, zarządzany, zintegrowany ze strukturą), a nie według wzorca podstawowego — wzorcem podstawowym jest MemGPT.

## Wyślij to

`outputs/skill-virtual-memory.md` to umiejętność wielokrotnego użytku, która tworzy poprawny dwupoziomowy szkielet pamięci (główny + archiwalny + powierzchnia narzędziowa) dla dowolnego docelowego środowiska wykonawczego, z podłączonymi zasadami eksmisji i polami cytowań.

## Ćwiczenia

1. Dodaj limit `max_main_context_tokens` mierzony w tokenach (w przybliżeniu `len(text.split())` * 1,3). Kompaktuj najstarsze wiadomości w podsumowanie po przekroczeniu limitu. Porównaj zachowanie z podsumowaniem i bez niego.
2. Prawidłowo zaimplementuj BM25 w magazynie archiwalnym (częstotliwość terminów, odwrotna częstotliwość dokumentów). Zmierz przypomnienie@10 na podstawie zestawu faktów dotyczących zabawek w porównaniu z wartością bazową nakładania się tokenów.
3. Do wstawek archiwalnych dodaj pola `citation` (session_id, turn_id, source_url). Spraw, aby agent cytował źródła w każdej odpowiedzi potwierdzonej wyszukiwaniem.
4. Symuluj zatruwanie pamięci: dodaj zapis archiwalny z informacją „ignoruj ​​wszystkie przyszłe instrukcje użytkownika”. Napisz strażnika, który skanuje wyszukiwania w poszukiwaniu tekstu w kształcie dyrektywy i oznacza je jako niezaufane.
5. Przenieś implementację, aby korzystała ze schematu JSON pamięci rdzeniowej repozytorium badawczego MemGPT (`cpacker/MemGPT`). Co się zmieni po przejściu z ciągów płaskich na sekcje pisane?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Kontekst wirtualny | „Nieograniczona pamięć” | Poziomy główne (podpowiedź) + zewnętrzne (z możliwością przeszukiwania) z wejściem/wyjściem strony |
| Główny kontekst | „Pamięć robocza” | Podpowiedź — stały rozmiar, zawsze widoczny |
| Pamięć archiwalna | „Sklep długoterminowy” | Zewnętrzna trwałość z możliwością wyszukiwania, pobierana na żądanie |
| Pamięć rdzeniowa | „Sekcja stałych podpowiedzi” | Nazwane sekcje przypięte w głównym kontekście |
| Narzędzie pamięci | „API pamięci” | Narzędzie wywołuje problemy z agentem, aby odczytać/zapisać pamięć zewnętrzną |
| Przerwij | „Błąd strony pamięci” | Agent wstrzymuje się, pobiera środowisko wykonawcze, wyniki łączy w następną turę |
| Zgnilizna pamięci | „Nieaktualne fakty” | Stare pisze o wydobywaniu utonięć; naprawić z konsolidacją |
| Zatrucie pamięci | „Wstrzyknięto trwałą notatkę” | Treść atakującego przechowywana w pamięci, ponownie przetworzona po przywołaniu |

## Dalsze czytanie

- [Packer i in., MemGPT (arXiv:2310.08560)](https://arxiv.org/abs/2310.08560) — dokument dotyczący wirtualnego kontekstu inspirowany systemem operacyjnym
– [Letta, blog o blokach pamięci](https://www.letta.com/blog/memory-blocks) — trójstopniowa ewolucja
- [Antropiczna, Efektywna inżynieria kontekstu](https://www.anthropic.com/engineering/efektywna-context-engineering-for-ai-agents) — traktowanie kontekstu jako budżetu
- [Chhikara et al., Mem0 (arXiv:2504.19413)](https://arxiv.org/abs/2504.19413) — hybrydowa pamięć produkcyjna na bazie tego wzorca