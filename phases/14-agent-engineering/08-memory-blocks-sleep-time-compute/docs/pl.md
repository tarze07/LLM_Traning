# Bloki pamięci i obliczenia czasu uśpienia (Letta)

> W 2024 r. MemGPT zmieniło nazwę na Letta. Ewolucja na rok 2026 dodaje dwa pomysły: dyskretne bloki pamięci funkcjonalnej, które model może bezpośrednio edytować, oraz agent czasu uśpienia, który asynchronicznie konsoliduje pamięć, gdy agent główny jest bezczynny. W ten sposób skalujesz pamięć poza jedną rozmowę.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania:** Faza 14 · 07 (MemGPT)
**Czas:** ~75 minut

## Cele nauczania

- Wymień trzy poziomy pamięci, z których korzysta Letta (rdzeniowy, przywoławczy, archiwalny) i rolę każdego z nich.
- Wyjaśnij wzór bloku pamięci: blok ludzki, blok osoby i bloki zdefiniowane przez użytkownika jako obiekty pierwszej klasy.
— Opisz, czym są obliczenia w czasie uśpienia, dlaczego znajdują się poza ścieżką krytyczną i dlaczego mogą uruchamiać silniejszy model niż agent główny.
- Zaimplementuj skryptową pętlę dwóch agentów, w której agent główny obsługuje odpowiedzi, a agent uśpiony konsoliduje bloki pomiędzy turami.

## Problem

MemGPT (lekcja 07) rozwiązało przepływ kontroli pamięci wirtualnej. Pojawiły się trzy problemy produkcyjne:

1. **Opóźnienie.** Każda operacja pamięci odbywa się na ścieżce krytycznej. Jeśli agent musi oczyścić, podsumować lub pogodzić, podczas gdy użytkownik czeka, zwiększa się opóźnienie ogona.
2. **Zniszczenie pamięci.** Zapisy kumulują się. Sprzeczne fakty pozostają. Pobieranie tonie w nieaktualnej zawartości.
3. **Utrata struktury.** Płaski magazyn archiwalny nie może wyrazić „blok Człowieka jest zawsze w monicie; blok Persona jest zawsze w monicie; blok Zadań jest wymieniany w trakcie sesji.”

Letta (letta.com) to przeróbka z 2026 roku. Bloki pamięci uwydatniają strukturę; obliczenia w czasie uśpienia przesuwają konsolidację ze ścieżki krytycznej.

## Koncepcja

### Trzy poziomy

| Poziom | Zakres | Gdzie mieszka | Napisane przez |
|------|-------|----------------|------------|
| Rdzeń | Zawsze widoczny | Wewnątrz głównego znaku zachęty | Wywołanie narzędzia agenta + przepisanie w czasie uśpienia |
| Przypomnijmy | Historia rozmów | możliwe do odzyskania | Automatyczne rejestrowanie skrętów |
| Archiwalne | Arbitralne fakty | Wektor + KV + wykres | Wywołanie narzędzia agenta + przetwarzanie w czasie snu |

Rdzeń to rdzeń MemGPT. Recall to bufor konwersacji z eksmitowanym ogonem. Archiwum to sklep zewnętrzny. Podział usuwa dwupoziomowe przeciążenie MemGPT.

### Bloki pamięci

Blok to wpisana, trwała i edytowalna sekcja warstwy podstawowej. W oryginalnym artykule MemGPT zdefiniowano dwa:

- **Blok ludzki** — fakty o użytkowniku (imię i nazwisko, rola, preferencje, cele).
- **Blokada osobowości** — koncepcja siebie agenta (tożsamość, ton, ograniczenia).

Letta uogólnia na dowolne bloki zdefiniowane przez użytkownika: blok `Task` dla bieżącego celu, blok `Project` dla faktów z bazy kodu, blok `Safety` dla twardych ograniczeń. Każdy blok zawiera `id`, `label`, `value`, `limit` (wielkość znaków), `description` (dzięki czemu model wie, kiedy edytować to).

Bloki można edytować poprzez powierzchnię narzędzia:

- `block_append(label, text)`
- `block_replace(label, old, new)`
- `block_read(label)`
- `block_summarize(label)` — skondensuj blok, który jest bliski limitu.

### Obliczanie czasu uśpienia

Dodatek Letta 2025: uruchom drugiego agenta w tle, poza ścieżką krytyczną. Agenci uśpienia przetwarzają transkrypcje rozmów i kontekst bazy kodu, zapisują `learned_context` we współdzielonych blokach oraz konsolidują lub unieważniają zapisy archiwalne.

Właściwości, które wypadają:

- **Brak kosztów opóźnień.** Odpowiedzi podstawowe nie czekają na operacje pamięci.
- **Dopuszczalny silniejszy model.** Agent czasu uśpienia może być droższym i wolniejszym modelem, ponieważ nie ma ograniczeń związanych z opóźnieniami.
- **Naturalne okno konsolidacji.** Deduplikacja, podsumowanie, unieważnienie sprzecznych faktów, gdy użytkownik nie czeka.

Kształt odpowiada sposobowi pracy człowieka: wykonujesz zadanie, śpisz na nim, a pamięć długoterminowa zapada w pamięć.

### Letta V1 i natywne rozumowanie

Letta V1 (`letta_v1_agent`, 2026) wycofuje `send_message`/heartbeat i wbudowane tokeny `Thought:` na rzecz rozumowania natywnego. Interfejsy API Responses (OpenAI) i Messages API z rozszerzonym myśleniem (Anthropic) emitują rozumowanie na oddzielnym kanale, przekazywanym kolejno (szyfrowanym między dostawcami w środowisku produkcyjnym). Pętla sterowania to nadal ReAct. Ślad myślowy ma charakter strukturalny, a nie podpowiadający.

### Gdzie ten wzorzec jest błędny

- **Blokuj wzdęcia.** Infinite `block_append` szybko osiąga limit. Podłącz sumator bloków przed zapisem, który przesuwa się nad nasadką.
- **Cichy dryf.** Agent w czasie uśpienia przepisuje blok, a agent główny nigdy tego nie zauważa. Bloki wersji i różnice powierzchniowe w śladzie.
- **Zatruta konsolidacja.** Agent czasu uśpienia przetwarza zawartość dostępną dla atakującego w rdzeniu. Lekcja 27 dotyczy również powierzchni czasu snu.

## Zbuduj to

`code/main.py` implementuje:

- `Block` — identyfikator, etykieta, wartość, limit, opis.
- `BlockStore` — CRUD + pomocnik `near_limit(label)`.
- Dwóch agentów skryptowych — `PrimaryAgent` obsługuje turę, `SleepTimeAgent` konsoliduje się pomiędzy turami.
- Ślad pokazujący trzyetapową konwersację z zapisami blokowymi oraz przepustkę w czasie uśpienia, która podsumowuje blok i unieważnia nieaktualny fakt.

Uruchom to:

```
python3 code/main.py
```

Transkrypcja pokazuje podział: zwoje pierwotne są szybkie i powodują nieprzetworzone zapisy; przepustka do spania zagęszcza i oczyszcza.

## Użyj tego

- **Letta** (letta.com) dla implementacji referencyjnej. Chmura z własnym hostem lub zarządzana.
- **Umiejętności Claude Agent SDK** w postaci wiedzy w kształcie bloku — umiejętność to nazwany, wersjonowany i możliwy do odzyskania blok instrukcji, który agent ładuje na żądanie.
- **Niestandardowe kompilacje** dla zespołów, które chcą mieć kontrolę nad zapleczem pamięci masowej. Skorzystaj z umowy Letta API, aby móc przeprowadzić migrację później.

## Wyślij to

`outputs/skill-memory-blocks.md` generuje system bloków w kształcie Letty z hakami uśpienia dla dowolnego czasu działania, łącznie z zasadami bezpieczeństwa i okablowaniem cytowań.

## Ćwiczenia

1. Dodaj narzędzie `block_summarize`, które zastępuje wartość bloku podsumowaniem wygenerowanym przez model, gdy `near_limit` zwraca wartość true. Który próg wyzwalania minimalizuje zarówno wywołania podsumowujące, jak i przepełnienie bloku?
2. Zaimplementuj deduplikację czasu uśpienia zamiast archiwizacji: dwa rekordy, których tekst ma ponad 90% nakładania się tokenów, zwijają się do jednego. Rób to tylko w fazie uśpienia, nigdy na ścieżce krytycznej.
3. Bloki wersji. Przy każdym zapisie zapisz starą wartość i różnicę. Ujawnij `block_history(label)`, aby operatorzy mogli debugować „dlaczego agent zapomniał X”.
4. Traktuj agentów nocnych jak niezaufanych pisarzy. Kiedy dotkną bloku Persona lub Safety, przed zatwierdzeniem poproś o sprawdzenie przez drugiego agenta.
5. Przenieś przykład, aby używać Letta API (`letta_v1_agent`). Jakie zmiany w schemacie blokowym i w jaki sposób rozumowanie natywne zmienia kształt śladu?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Blok pamięci | „Edytowalna sekcja podpowiedzi” | Wpisany, trwały, edytowalny przez LLM segment pamięci rdzeniowej |
| Blok ludzki | „Pamięć użytkownika” | Fakty o użytkowniku, przypięte w rdzeniu |
| Blok osoby | „Tożsamość agenta” | Pojęcie siebie, ton, ograniczenia, przypięte do rdzenia |
| Obliczanie czasu snu | „Asynchroniczna praca pamięci” | Drugi agent przeprowadzający konsolidację poza ścieżką krytyczną |
| Rdzeń / Przypomnienie / Archiwizacja | „Poziomy” | Trójwarstwowy podział pamięci: zawsze widoczna / rozmowa / zewnętrzna |
| Limit bloku | „Czapka” | Limit znaków na blok; podsumowanie sił |
| Rodzime rozumowanie | „Kanał myślący” | Dane wyjściowe na poziomie dostawcy, a nie na poziomie podpowiedzi `Thought:` |
| Wyuczony kontekst | „Wyjście snu” | Fakty, które agent czasu snu zapisuje we wspólnych blokach |

## Dalsze czytanie

- [Letta, blog o blokach pamięci](https://www.letta.com/blog/memory-blocks) — wzór blokowy
– [Letta, blog dotyczący obliczeń w czasie snu](https://www.letta.com/blog/sleep-time-compute) — konsolidacja asynchroniczna
— [Letta, Rearchitecting the Agent Loop](https://www.letta.com/blog/letta-v1-agent) — przepisanie natywnego rozumowania
- [Packer et al., MemGPT (arXiv:2310.08560)](https://arxiv.org/abs/2310.08560) — pochodzenie