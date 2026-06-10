# Czat grupowy i wybór mówcy

> AutoGen GroupChat i AG2 GroupChat współdzielą jedną rozmowę pomiędzy N agentami; funkcja selektora (LLM, działanie okrężne lub niestandardowa) wybiera, kto będzie mówił następny. Jest to archetyp wyłaniającej się rozmowy między agentami — agenci nie znają swojej roli na statycznym wykresie, po prostu reagują na wspólną pulę. Semantyka GroupChat AutoGen v0.2 została zachowana w rozwidleniu AG2; AutoGen v0.4 przepisał go jako model aktora sterowanego zdarzeniami. Firma Microsoft przełączyła AutoGen w tryb konserwacji w lutym 2026 r. i połączyła go z jądrem semantycznym w Microsoft Agent Framework (RC, luty 2026 r.). Podstawowy moduł GroupChat przetrwał zarówno w AG2, jak i w Microsoft Agent Framework — naucz się go raz, używaj go wszędzie.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 16 · 04 (model prymitywny)
**Czas:** ~60 minut

## Problem

Wykresy statyczne (LangGraph) świetnie sprawdzają się, gdy znany jest przepływ pracy. Prawdziwe rozmowy nie są statyczne: czasem koder pyta recenzenta, czasem badacza, czasem pisarza. Zakodowanie na stałe każdego możliwego przekazania powoduje eksplozję krawędzi. Chcesz, aby *agenci reagowali na współdzieloną pulę* z jakąś funkcją decydującą, kto będzie mówił dalej.

To jest dokładnie to, co robi AutoGen GroupChat.

## Koncepcja

### Kształt

```
              ┌─── shared pool ────┐
              │   m1  m2  m3  ...  │
              └─────────┬──────────┘
                        │ (everyone reads all)
      ┌───────┬─────────┼─────────┬───────┐
      ▼       ▼         ▼         ▼       ▼
    Agent A  Agent B  Agent C  Agent D  Selector
                                           │
                                           ▼
                                  "next speaker = C"
```

Każdy agent widzi każdą wiadomość. W każdej turze wywoływana jest funkcja selektora, aby wybrać, kto będzie mówił następny.

### Trzy smaki selektora

**System okrężny.** Cykl stały. Deterministyczny. Skaluje się liniowo w N, ale ignoruje kontekst — kolej na programistę przypada nawet wtedy, gdy tematem jest kontrola prawna.

**Wybrane przez LLM.** Wywołanie LLM, które odczytuje ostatnią pulę i zwraca najlepszego następnego mówcę. Kontekstowy, ale powolny: każda tura dodaje połączenie LLM. Wartość domyślna AutoGen.

**Niestandardowe.** Funkcja Pythona z dowolną logiką. Typowe: wybrane przez LLM z zasadami awaryjnymi (np. „zawsze daj weryfikatorowi kolej po koderze”).

### Interfejs API ConversableAgent

```
agent = ConversableAgent(
    name="coder",
    system_message="You write Python.",
    llm_config={...},
)
chat = GroupChat(agents=[coder, reviewer, tester], messages=[])
manager = GroupChatManager(groupchat=chat, llm_config={...})
```

`GroupChatManager` przechowuje selektor. Kiedy agent zakończy turę, menedżer wywołuje selektor, który zwraca następnego agenta. Pętla trwa aż do warunku zakończenia.

### Zakończenie

Trzy popularne wzorce:

- **Maksymalna liczba rund.** Twardy limit całkowitej liczby obrotów.
- **Token „TERMINACJA”.** Agenci mogą emitować wiadomość wartowniczą; menedżer zatrzymuje się, gdy ktoś się pojawia.
- **Kontrola osiągnięcia celu.** W każdej turze uruchamiany jest lekki weryfikator, który po zakończeniu zatrzymuje czat.

### Podział AutoGen → AG2 i połączenie Microsoft Agent Framework

Na początku 2025 r. Microsoft rozpoczął gruntowne przepisywanie AutoGen (wersja 0.4) wokół modelu aktora sterowanego zdarzeniami. Społeczność rozwidlała semantykę GroupChat AutoGen v0.2 jako AG2, zachowując interfejs API zintegrowany przez pierwszych użytkowników.

W lutym 2026 r. Microsoft ogłosił, że AutoGen przejdzie w tryb konserwacji, a model aktora sterowanego zdarzeniami połączy się z **Microsoft Agent Framework** (RC, luty 2026 r., obecnie połączony z Semantic Kernel). Koncepcja GroupChat przetrwała w obu ścieżkach; szczegóły implementacji są różne. AG2 jest preferowanym źródłem kodu zgodnego z wersją 0.2.

### Kiedy GroupChat pasuje

- **Rozmowy w nagłych przypadkach.** Nie chcesz wstępnie podłączać wszystkich możliwych kolejnych głośników.
- **Zadania polegające na łączeniu ról.** Koder pyta badacza, badacz pyta archiwistę, archiwista pyta kodera. Flow to nie DAG.
- **Odkrywcze rozwiązywanie problemów.** Pomyśl o „burzy mózgów”, a nie o „linii montażowej”.

### Kiedy się nie powiedzie

- **Ścisły determinizm.** Selektor LLM może być niespójny. Ten sam monit, różne przebiegi, inni kolejni mówcy.
- **Kaskady pochlebstw.** Agenci podporządkowują się temu, kto wypowiada się z największą pewnością siebie. Wyraźna odpowiedź przeciwna.
- **Rozdęty kontekst.** Każdy agent czyta każdą wiadomość; po 10 turach kontekst jest ogromny. Użyj rzutów (Lekcja 15), aby określić zakres widoków.
- **Gorący mówcy.** Jeden agent dominuje w rozmowie, ponieważ selekcjoner faworyzuje jego specjalizacje. Wprowadź balans głośników jako funkcję selektora.

### Czat grupowy a przełożony

Te same elementy podstawowe, różne ustawienia domyślne:

- Przełożony: jeden agent planuje, a inni wykonują. Selektor to „zapytaj planistę, co zrobić”.
- Czat grupowy: wszyscy agenci są równorzędnymi osobami; selektor jest funkcją współdzielonej puli.

W obu przypadkach zastosowano cztery elementy podstawowe z lekcji 04. Domyślnym ustawieniem czatu grupowego jest orkiestracja wybrana przez LLM i stan współdzielenia pełnej puli.

## Zbuduj to

`code/main.py` implementuje GroupChat od podstaw w stdlib. Trzej agenci (programista, recenzent, menedżer), warianty okrężne i wybrane przez LLM oraz zakończenie na tokenie `TERMINATE`.

Wersja demonstracyjna drukuje transkrypcję rozmowy oraz ślad decyzji selektora dla obu wariantów.

Uruchom:

```
python3 code/main.py
```

## Użyj tego

`outputs/skill-groupchat-selector.md` konfiguruje selektor GroupChat dla danego zadania — działanie okrężne, wybrane przez LLM czy niestandardowe, a także dane wejściowe selektora (ostatnie wiadomości, specjalizacje agentów, liczba tur) do użycia.

## Wyślij to

Lista kontrolna:

- **Maksymalny limit rund.** Zawsze. 10-20 dla typowych zadań.
- **Wskaźnik balansu głośników.** Śledź obroty według agenta; ostrzega, gdy brak równowagi przekracza próg.
- **Token zakończenia.** `TERMINATE` lub dedykowany agent weryfikujący.
- **Pamięć projekcyjna lub ograniczona.** Po ~10 wiadomościach rozważ udostępnienie każdemu agentowi tylko widoku ograniczonego, aby zapobiec rozdęciu kontekstu.
- **Rejestrowanie selektora.** W przypadku wariantów wybranych przez LLM należy rejestrować zarówno dane wejściowe selektora, jak i jego wybór. W przeciwnym razie debugowanie jest niemożliwe.

## Ćwiczenia

1. Uruchom `code/main.py`. Porównaj rozmowę w trybie okrężnym z wybraną przez LLM. Który agent dominuje w każdym z nich?
2. Dodaj w selektorze regułę „max-speaks-per-agent”. Jak to wpływa na transkrypcję?
3. Wprowadź rozwiązanie zakończone osiągnięciem celu: zatrzymaj, gdy recenzent zwróci komunikat „zatwierdzony”. Jak często uruchamia się przed okrągłą czapką?
4. Przeczytaj stabilną dokumentację AutoGen na GroupChat (https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/group-chat.html). Zidentyfikuj domyślny selektor używany przez `GroupChatManager`.
5. Przeczytaj repozytorium AG2 (https://github.com/ag2ai/ag2) i porównaj jego wersję GroupChat w wersji 0.2 z wersją sterowaną zdarzeniami w wersji 0.4. Jakie konkretne właściwości (przepustowość, odporność na błędy, możliwość komponowania) dodaje wersja 0.4?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Czat grupowy | „Agenci w jednym pokoju rozmów” | Wspólna pula wiadomości + funkcja selektora. Prymitywny AutoGen / AG2. |
| Wybór głośników | „Kto będzie mówił dalej” | Funkcja wybierająca kolejnego agenta. Okrężne, wybrane przez LLM lub niestandardowe. |
| Menedżer czatu grupowego | „Gospodarz spotkania” | Komponent AutoGen, który jest właścicielem selektora i wykonuje pętle na zakrętach. |
| ConversableAgent | „Agent bazowy” | klasa bazowa AutoGen; agent, który może wysyłać i odbierać wiadomości. |
| Token zakończenia | „Słowo „stop”” | Ciąg wartowniczy (zwykle `TERMINATE`), który kończy czat. |
| Gorący głośnik | „Dominuje jeden agent” | Tryb niepowodzenia, w którym selektor wybiera tego samego agenta. |
| Rozdęcie kontekstu | „Basen rośnie bez ograniczeń” | Każdy agent czyta każdą wcześniejszą wiadomość; kontekst rośnie z kolei. |
| Projekcja | „Widok w zakresie” | Widok specyficzny dla roli w puli udostępnionej, aby zapobiec rozdęciu kontekstu. |

## Dalsze czytanie

- [Dokumentacja czatu grupowego AutoGen](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/group-chat.html) — implementacja referencyjna
- [Repo AG2](https://github.com/ag2ai/ag2) — kontynuacja społeczności AutoGen v0.2
— [Dokumentacja Microsoft Agent Framework](https://microsoft.github.io/agent-framework/) — połączony następca, RC, luty 2026 r.
— [Informacje o wersji AutoGen v0.4](https://microsoft.github.io/autogen/stable/) — szczegóły przepisywania modelu aktora sterowanego zdarzeniami