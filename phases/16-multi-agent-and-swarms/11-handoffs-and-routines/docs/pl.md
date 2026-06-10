# Przekazywanie i procedury — orkiestracja bezstanowa

> Swarm OpenAI (październik 2024 r.) podzielił orkiestrację wieloagentową na dwa podstawowe elementy: **procedury** (instrukcje + narzędzia jako monit systemowy) i **przekazania** (narzędzie, które zwraca innego agenta). Brak maszyny stanu, brak rozgałęzień DSL — trasy LLM poprzez wywołanie odpowiedniego narzędzia przekazywania. Pakiet SDK OpenAI Agents (marzec 2025) jest następcą produkcyjnym. Sam rój pozostaje najczystszym odniesieniem koncepcyjnym — całe jego źródło mieści się w kilkuset linijkach. Wzorzec jest wirusowy, ponieważ interfejs API wygląda mniej więcej tak: „agent = zachęta + narzędzia; przekazanie = agent zwracający funkcję”. Ograniczenie: bezstanowe, więc problemem osoby wywołującej jest pamięć.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 04 (model prymitywny)
**Czas:** ~60 minut

## Problem

Każda platforma wieloagentowa chce, abyś nauczył się DSL: węzły i krawędzie LangGraph, załogi i zadania CrewAI, AutoGen GroupChat i menedżerowie. Linie DSL to prawdziwe abstrakcje, ale sprawiają, że całość wydaje się cięższa, niż powinna.

Rój pcha w przeciwnym kierunku: użyj możliwości przywoływania narzędzi, którą model już posiada. Handoffy stają się wywołaniami narzędzi. Koordynatorem jest agent, który aktualnie prowadzi konwersację. Maszyna stanów jest zawarta w monitach systemowych agentów.

## Koncepcja

### Dwa elementy pierwotne

**Procedura.** Podpowiedź systemowa określająca rolę agenta i dostępne narzędzia. Pomyśl o tym jak o ograniczonym zestawie instrukcji: „jesteś agentem selekcji; jeśli użytkownik pyta o zwrot pieniędzy, przekaż to agentowi ds. zwrotu pieniędzy”.

**Przekazanie.** Narzędzie, które może wywołać agent i które zwraca nowy obiekt Agenta. Środowisko wykonawcze Swarm wykrywa wartość zwracaną przez Agenta i przełącza aktywnego agenta na następną turę.

To jest cała abstrakcja.

```
def transfer_to_refunds():
    return refund_agent  # Swarm sees Agent return → switch active agent

triage_agent = Agent(
    name="triage",
    instructions="Route the user to the right specialist.",
    functions=[transfer_to_refunds, transfer_to_sales, transfer_to_support],
)
```

Podpowiedź systemowa agenta selekcji sprawia, że wybiera on właściwe przekazanie na podstawie komunikatu użytkownika. Wywołanie narzędzia LLM wykonuje routing.

### Dlaczego to jest wirusowe

- **Mały interfejs API.** Dwie koncepcje do nauczenia.
- **Wykorzystuje to, co już robi model.** Wywoływanie narzędzi jest już na poziomie produkcyjnym u różnych dostawców.
- **Brak obciążenia maszyny stanowej.** Nie opisujesz wykresu; Podpowiedzi agentów opisują, komu przekazują.

### Handel bezpaństwowy

Rój jest jawnie bezstanowy pomiędzy uruchomieniami. Struktura przechowuje historię komunikatów podczas uruchamiania, ale niczego nie utrwala. Pamięć, ciągłość, długotrwałe zadania — to wszystko jest problemem dzwoniącego.

W środowisku produkcyjnym (OpenAI Agents SDK, marzec 2025 r.) była to jedna z głównych rzeczy, które uległy zmianie: pakiet SDK dodaje wbudowane zarządzanie sesjami, poręcze i śledzenie, zachowując jednocześnie prymitywne przekazywanie.

### Gdy pasuje rój/przekazanie

- **Wzorce segregacji.** Agent pierwszej linii kieruje użytkownika do specjalisty.
- **Przekazanie w oparciu o umiejętności.** „Jeśli zadanie wymaga kodu, zadzwoń do programisty; jeśli potrzebne są badania, zadzwoń do badacza”.
- **Krótkie, ograniczone rozmowy.** Obsługa klienta, FAQ do zgłoszenia, proste przepływy pracy.

### Gdy rój walczy

- **Długie sesje z pamięcią współdzieloną.** Przekazanie resetuje stan konwersacji do monitu nowego agenta i historii. Brak trwałego stanu między agentami bez pamięci zarządzanej przez wywołującego.
- **Wykonywanie równoległe.** Przekazywanie odbywa się pojedynczo — przełącza się aktywny agent. Równoległość wymaga, aby osoba wywołująca zorganizowała wiele przebiegów roju.
- **Audyt i ponowne odtwarzanie.** Przebiegi bezstanowe są trudne do dokładnego odtworzenia; wybór przekazania LLM nie jest deterministyczny.

### Pakiet SDK agentów OpenAI (marzec 2025 r.)

Następca produkcyjny dodaje:

- **Stan sesji.** Trwały wątek między przebiegami.
- **Poręcze ochronne.** Haki sprawdzające wejście/wyjście.
- **Tracing.** Każde wywołanie i przekazanie narzędzia jest rejestrowane.
- **Filtry przekazania.** Kontroluj, jaki kontekst jest przesyłany przy przekazywaniu.

Operacja podstawowa przekazania zostaje zachowana; Do tego dochodzi ergonomia produkcji.

### Rój kontra GroupChat

Obydwa korzystają z routingu opartego na LLM, ale różnią się **kto wybiera następny**:

- GroupChat: selektor (funkcja lub LLM) wybiera następnego mówcę z zewnątrz.
- Rój: bieżący agent wybiera swojego następcę, wywołując narzędzie przekazywania.

Rój to „agent decyduje, co dalej”; GroupChat to „menedżer decyduje, co dalej”. Decyzja roju wynika z wywołania narzędzia aktywnego agenta; GroupChat żyje w `GroupChatManager`.

## Zbuduj to

`code/main.py` implementuje Swarm od podstaw: klasę danych Agenta, mechanizm przekazywania (narzędzie zwraca Agenta) i pętlę uruchamiania, która wykrywa przełączanie agentów.

Wersja demonstracyjna: agent segregujący kieruje do specjalistów zajmujących się zwrotami kosztów, sprzedażą lub wsparciem. Każdy specjalista ma swoje własne narzędzia. Pętla uruchamiania wypisuje każde przekazanie.

Uruchom:

```
python3 code/main.py
```

## Użyj tego

`outputs/skill-handoff-designer.md` projektuje topologię przekazania dla danego zadania: jacy agenci istnieją, jakie przekazania mogą wywołać, jaki kontekst przekazuje.

## Wyślij to

Lista kontrolna:

- **Rejestrowanie przekazania.** Każde przekazanie zapisuje zdarzenie śledzenia z migawką kontekstu od agenta do agenta.
- **Zasady transferu kontekstu.** Zdecyduj, co ma się wydarzyć po przekazaniu: pełna historia (droga), ostatnie N wiadomości czy podsumowanie.
- **Poręcz przy przekazaniu.** Przekazanie specjalisty z innymi uprawnieniami do narzędzia musi zostać uwierzytelnione — w przeciwnym razie natychmiastowe wstrzyknięcie może wymusić niechciane przekazania.
- **Wykrywanie pętli.** Dwóch agentów przekazujących informacje tam i z powrotem to częsta awaria; wykryć za pomocą prostego sprawdzenia ostatniego pierścienia K.
- **Agent awaryjny.** Jeśli cel przekazania nie istnieje, przywróć bezpieczne ustawienie domyślne.

## Ćwiczenia

1. Uruchom `code/main.py` i przejdź do agenta ds. zwrotu kosztów. Potwierdź, że aktywny agent drugiej tury otrzyma zwrot pieniędzy.
2. Dodaj regułę wykrywania pętli: jeśli ci sami dwaj agenci przekazali połączenie 3 razy z rzędu, wymuś wyjście. Zaprojektuj rezerwę.
3. Przeczytaj dokumentację OpenAI Agents SDK na temat filtrów przekazywania. Zaimplementuj wersję „podsumowania przy przekazaniu”: agent wychodzący kompresuje kontekst do podsumowania w postaci punktorów, zanim agent przychodzący przejmie kontrolę.
4. Porównaj przekazanie roju z selektorem GroupChatManager. Który wzór pogarsza szybkość wstrzyknięcia i dlaczego?
5. Przeczytaj książkę kucharską Swarm (https://developers.openai.com/cookbook/examples/orchestrating_agents). Zidentyfikuj jedną wyraźną decyzję projektową podjętą przez Swarm, dotyczącą zmiany lub zachowania pakietu SDK OpenAI Agents.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Rutyna | „Podpowiedź agenta” | Podpowiedź systemowa + lista narzędzi. Definiuje rolę i dostępne przekazania. |
| Przekazanie | „Przeniesienie do innego agenta” | Narzędzie, które może wywołać aktywny agent i które zwraca nowego agenta. Środowisko wykonawcze przełącza aktywnego agenta. |
| Bezpaństwowiec | „Brak pamięci między uruchomieniami” | Rój niczego nie utrzymuje; pamięć jest obowiązkiem dzwoniącego. |
| Aktywny agent | „Kto teraz mówi” | Agent aktualnie prowadzący rozmowę. Handoff to zmienia. |
| Przeniesienie kontekstu | „Co się rusza po przekazaniu” | Zasady dotyczące historii, którą widzi przychodzący agent: pełna, ostatnie N lub podsumowana. |
| Pętla przekazywania | „Agenci do ping-ponga” | Tryb awarii, w którym dwóch agentów przekazuje sobie nawzajem informacje. |
| Pakiet SDK agentów OpenAI | „Rój produkcyjny” | Następca z marca 2025 r .; dodaje sesje, poręcze i śledzenie na wierzchu prymitywu przekazania. |
| Filtr przekazania | „Brama na transfer” | Funkcja SDK do sprawdzania i modyfikowania kontekstu na granicy przekazania. |

## Dalsze czytanie

- [Książka kucharska OpenAI — Agenci orkiestrujący: procedury i przekazywanie](https://developers.openai.com/cookbook/examples/orchestrating_agents) — artykuł referencyjny
- [Repozytorium OpenAI Swarm](https://github.com/openai/swarm) — oryginalna implementacja, zachowana jako odniesienie koncepcyjne
- [Dokumentacja OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) — następca produkcyjny z sesjami i śledzeniem
– [Antropiczne notatki dotyczące przekazania w Claude](https://docs.anthropic.com/en/docs/claude-code) – jak podagenci Claude Code wykorzystują wzorzec podobny do przekazania za pośrednictwem `Task`