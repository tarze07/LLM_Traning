# AutoGen v0.4: Model aktora i struktura agenta

> AutoGen v0.4 (Microsoft Research, styczeń 2025 r.) przeprojektowano orkiestrację agentów wokół modelu aktora. Asynchroniczna wymiana komunikatów, agenci sterowani zdarzeniami, izolacja błędów, naturalna współbieżność. Struktura znajduje się teraz w trybie konserwacji, a następcą staje się Microsoft Agent Framework (publiczna wersja zapoznawcza z października 2025 r.).

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (pętla agenta), faza 14 · 12 (wzorce przepływu pracy)
**Czas:** ~75 minut

## Cele nauczania

- Opisz model aktora: agenci jako aktorzy, komunikaty jako jedyny IPC, izolacja awarii według aktora.
- Wymień trzy warstwy API AutoGen v0.4 — Core, AgentChat, Extensions — i do czego służą.
- Wyjaśnij, dlaczego oddzielenie dostarczania komunikatów od obsługi zapewnia izolację błędów i naturalną współbieżność.
- Zaimplementuj środowisko wykonawcze aktora stdlib w Pythonie i przenieś do niego przepływ przeglądu kodu przez dwóch agentów.

## Problem

Większość struktur agentów jest synchronicznych: jeden agent produkuje, drugi używa, w stosie wywołań. Awarie powodują awarię stosu. Współbieżność jest włączona. Dystrybucja wymaga przepisania.

Odpowiedź AutoGen v0.4: model aktora. Każdy agent jest aktorem z prywatną skrzynką odbiorczą. Wiadomości są jedyną interakcją. Środowisko wykonawcze oddziela dostawę od obsługi. Niepowodzenia dotyczą jednego aktora. Współbieżność jest natywna. Dystrybucja to po prostu inny transport.

## Koncepcja

### Aktorzy

Aktor ma:

- Państwo prywatne (nigdy bezpośrednio nie dotykane z zewnątrz).
- Skrzynka odbiorcza (kolejka wiadomości).
- Procedura obsługi: `receive(message) -> effects`, gdzie efektami mogą być „odpowiedz”, „wyślij do innego aktora”, „spawnuj nowego aktora”, „aktualizuj stan”, „zatrzymaj siebie”.

Dwóch aktorów nie może dzielić pamięci. Mogą jedynie wysyłać wiadomości.

### Trzy warstwy API w AutoGen v0.4

1. **Core.** Struktura aktorów niskiego poziomu. `AgentRuntime`, `Agent`, `Message`, `Topic`. Asynchroniczna wymiana komunikatów sterowana zdarzeniami.
2. **AgentChat.** API wysokiego poziomu oparte na zadaniach (zamiennik ConversableAgent wersji 0.2). `AssistantAgent`, `UserProxyAgent`, `RoundRobinGroupChat`, `SelectorGroupChat`.
3. **Rozszerzenia.** Integracje — OpenAI, Anthropic, Azure, narzędzia, pamięć.

### Dlaczego oddzielenie ma znaczenie

W modelu v0.2 wywołanie `agent_a.chat(agent_b)` synchronicznie blokuje agenta_a do czasu powrotu agenta_b. W wersji 0.4 `send(agent_b, msg)` umieszcza wiadomość w skrzynce odbiorczej agenta_b i wraca. Środowisko wykonawcze dostarcza później. Trzy konsekwencje:

- **Izolacja błędów.** Awaria agenta B nie powoduje awarii agenta A — środowisko wykonawcze wychwytuje awarię w procedurze obsługi B i decyduje, co zrobić (logowanie, ponowna próba, utracona wiadomość).
- **Naturalna współbieżność.** Wiele wiadomości przesyłanych jednocześnie; aktorzy jednocześnie przetwarzają swoją skrzynkę odbiorczą.
- **Gotowy do dystrybucji.** Skrzynka odbiorcza + transport to ta sama abstrakcja, niezależnie od tego, czy aktor jest w trakcie, czy na innym hoście.

### Topologie

- **RoundRobinGroupChat.** Agenci zmieniają się w ustalonej rotacji.
- **SelectorGroupChat.** Agent selekcyjny wybiera następną osobę na podstawie kontekstu rozmowy.
- **Magentic-One.** Referencyjny zespół wieloagentowy do przeglądania stron internetowych, wykonywania kodu i obsługi plików. Zbudowany na AgentChat.

### Obserwowalność

Wbudowana obsługa OpenTelemetry. Każdy komunikat emituje zakres; wywołania narzędzi zawierają atrybuty `gen_ai.*` zgodnie z konwencjami semantycznymi OTel GenAI 2026 (lekcja 23).

### Stan: tryb konserwacji

Początek 2026 r.: AutoGen v0.7.x jest stabilny do celów badawczych i prototypowania. Firma Microsoft przeniosła aktywny rozwój na platformę Microsoft Agent Framework (publiczna wersja zapoznawcza 1 października 2025 r.; wersja 1.0 GA planowana na koniec pierwszego kwartału 2026 r.). Wzorce AutoGen są przesyłane w sposób przejrzysty — model aktora to trwały pomysł.

## Zbuduj to

`code/main.py` implementuje środowisko wykonawcze aktora stdlib:

- `Message` — ładunek wpisany za pomocą `sender`, `recipient`, `topic`, `body`.
- `Actor` — streszczenie z `receive(message, runtime)`.
- `Runtime` — pętla zdarzeń ze współdzieloną kolejką, dostawą, izolacją awarii.
- Demo dla dwóch aktorów: `ReviewerAgent` przegląda kod, `ChecklistAgent` uruchamia listę kontrolną; wymieniają wiadomości aż do osiągnięcia konsensusu.

Uruchom to:

```
python3 code/main.py
```

Ślad pokazuje dostarczenie komunikatu, symulowaną awarię u jednego aktora, która nie powoduje awarii drugiego, oraz zbieżność w zakresie wspólnego werdyktu.

## Użyj tego

- **AutoGen v0.4/v0.7** (konserwacja) — stabilny do badań, prototypowania i wzorców wieloagentowych.
- **Microsoft Agent Framework** (publiczna wersja zapoznawcza) — ścieżka przekazywania; te same pomysły na modele aktorów w odświeżonym interfejsie API.
- **Topologia roju LangGraph** (Lekcja 13) — podobny wzór dzięki przekazywaniu wspólnych narzędzi.
- **Niestandardowe środowisko wykonawcze aktora** — gdy potrzebujesz określonego transportu (NATS, RabbitMQ, gRPC).

## Wyślij to

`outputs/skill-actor-runtime.md` generuje minimalny czas działania aktora oraz szablon zespołu (RoundRobin lub Selector) dla danego zadania wieloagentowego.

## Ćwiczenia

1. Dodaj kolejkę utraconych wiadomości: gdy osoba obsługująca zgłosi się, zaparkuj wiadomość, która nie powiodła się, do kontroli człowieka. Jak często DLQ zostaje trafiony w twoją zabawkę?
2. Zaimplementuj `SelectorGroupChat`: aktor selektora wybiera, kto przetworzy następną wiadomość, na podstawie stanu konwersacji.
3. Dodaj transport rozproszony: zamień kolejkę procesu na serwer JSON-over-HTTP, aby aktorzy mogli działać w oddzielnych procesach.
4. Podłącz zakres Otel na wiadomość (lub zastępstwo bez operacji). Emituj `gen_ai.agent.name`, `gen_ai.operation.name` na lekcję 23.
5. Przeczytaj post poświęcony architekturze AutoGen v0.4. Przenieś swoją zabawkę do prawdziwego API `autogen_core`. Co pominąłeś, co ma znaczenie w produkcji?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Aktor | „Agent” | Stan prywatny + skrzynka odbiorcza + moduł obsługi; brak pamięci współdzielonej |
| Wiadomość | „Wydarzenie” | Wpisany ładunek; jedyny sposób, w jaki aktorzy wchodzą w interakcję |
| Skrzynka odbiorcza | „Skrzynka pocztowa” | Kolejka oczekujących wiadomości według aktora |
| Czas wykonania | „Host agenta” | Pętla zdarzeń, która kieruje komunikaty i izoluje awarie |
| Temat | „Kanał” | Nazwana trasa publikowania i subskrybowania między aktorami |
| Izolacja usterek | „Niech się rozbije” | Niepowodzenie jednego aktora nie powoduje awarii innych |
| OkrągłyRobinGrupowyCzat | „Zespół o stałej rotacji” | Agenci zmieniają się w kolejności |
| SelectorGrupowy Czat | „Zespół kierowany kontekstowo” | Selektor wybiera, kto będzie następny |
| Magiczny-Jeden | „Zespół referencyjny” | Zespół wielu agentów dla sieci + kod + pliki |

## Dalsze czytanie

- [AutoGen v0.4, Microsoft Research](https://www.microsoft.com/en-us/research/articles/autogen-v0-4-reimagining-the-foundation-of-agentic-ai-for-scale-extensibility-and-robustness/) — post dotyczący przeprojektowania
- [Przegląd LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) — alternatywa w kształcie wykresu
- [Konwencje semantyczne OpenTelemetry GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — obejmuje domyślnie emitowane przez AutoGen