# Czat grupowy i wybór mówcy

> AutoGen GroupChat i AG2 GroupChat współdzielą jedną rozmowę między N agentami; funkcja selektora (LLM, cykliczna lub niestandardowa) wybiera kolejnego rozmówcę. Jest to archetyp dynamicznej (wyłaniającej się) rozmowy między agentami — agenci nie mają z góry określonej roli w statycznym grafie, lecz reagują na treść ze wspólnej puli. Semantyka GroupChat AutoGen v0.2 została zachowana w forku AG2; AutoGen v0.4 przepisał ten mechanizm w oparciu o model aktorów sterowany zdarzeniami. Firma Microsoft przełączyła AutoGen w tryb konserwacji w lutym 2026 r. i zintegrowała go z Semantic Kernel w ramach Microsoft Agent Framework (wersja RC, luty 2026 r.). Podstawowy moduł GroupChat przetrwał zarówno w AG2, jak i w Microsoft Agent Framework — poznaj go raz i używaj wszędzie.

**Typ:** Ucz się + Buduj
**Języki:** Python (biblioteka standardowa)
**Wymagania wstępne:** Faza 16 · 04 (model prymitywny)
**Czas:** ~60 minut

## Problem

Statyczne grafy (takie jak w LangGraph) świetnie sprawdzają się, gdy przepływ pracy jest z góry znany. Prawdziwe rozmowy są jednak dynamiczne: czasem programista zadaje pytanie recenzentowi, innym razem badaczowi, a kiedy indziej autorowi treści. Kodowanie na stałe każdego możliwego przekazania sterowania (handoff) prowadzi do wykładniczego wzrostu liczby krawędzi grafu. Lepszym rozwiązaniem jest sytuacja, w której *agenci reagują na wspólną pulę*, a dedykowana funkcja decyduje, kto powinien zabrać głos jako następny.

To jest dokładnie rola AutoGen GroupChat.

## Koncepcja

### Schemat działania

```
              ┌─── shared pool ────┐
              │   m1  m2  m3  ...  │
              └─────────┬──────────┘
                        │ (wszyscy czytają wszystko)
       ┌───────┬─────────┼─────────┬───────┐
       ▼       ▼         ▼         ▼       ▼
    Agent A  Agent B  Agent C  Agent D  Selektor
                                           │
                                           ▼
                                  "next speaker = C"
```

Każdy agent widzi każdą wiadomość. W każdej turze wywoływana jest funkcja selektora, która decyduje, kto zabierze głos w następnej kolejności.

### Trzy tryby selektora

**System cykliczny (round-robin).** Stała kolejność. Rozwiązanie w pełni deterministyczne. Skaluje się liniowo wraz z liczbą agentów (N), ale ignoruje kontekst rozmowy — programista otrzyma głos nawet wtedy, gdy dyskusja dotyczy wyłącznie kwestii prawnych.

**Wybór przez LLM.** Wywołanie LLM analizuje ostatni stan puli wiadomości i wskazuje optymalnego kolejnego rozmówcę. Rozwiązanie uwzględnia kontekst, ale jest wolniejsze: każda tura wymaga dodatkowego zapytania do LLM. Jest to domyślny mechanizm w AutoGen.

**Niestandardowy (custom).** Funkcja w Pythonie z dowolną logiką. Typowy schemat: wybór przez LLM z regułami rezerwowymi (fallback), np. „zawsze przekaż głos weryfikatorowi bezpośrednio po programiście”.

### Interfejs API ConversableAgent

```python
agent = ConversableAgent(
    name="coder",
    system_message="You write Python.",
    llm_config={...},
)
chat = GroupChat(agents=[coder, reviewer, tester], messages=[])
manager = GroupChatManager(groupchat=chat, llm_config={...})
```

`GroupChatManager` zarządza selektorem. Gdy agent kończy swoją turę, menedżer wywołuje selektor, który wskazuje kolejnego agenta. Pętla trwa do momentu spełnienia warunku zakończenia.

### Zakończenie konwersacji

Trzy popularne wzorce:

- **Maksymalna liczba rund (Max rounds).** Sztywny limit łącznej liczby tur.
- **Token zakończenia.** Agenci mogą wysłać specjalny komunikat sygnalizacyjny (np. `TERMINATE`); menedżer przerywa działanie, gdy taki komunikat się pojawi.
- **Weryfikacja osiągnięcia celu.** W każdej turze uruchamiany jest prosty ewaluator, który kończy konwersację po zrealizowaniu zadania.

### Podział AutoGen → AG2 i integracja z Microsoft Agent Framework

Na początku 2025 roku Microsoft rozpoczął gruntowne przepisywanie biblioteki AutoGen (wersja 0.4) w oparciu o model aktorów sterowany zdarzeniami. Społeczność utworzyła fork (AG2) zachowujący semantykę GroupChat z wersji AutoGen v0.2, dzięki czemu zachowano kompatybilność z dotychczasowymi wdrożeniami.

W lutym 2026 roku Microsoft ogłosił przejście AutoGen w tryb wsparcia (maintenance), a model aktorów sterowany zdarzeniami został zintegrowany z Microsoft Agent Framework (wersja RC z lutego 2026 r., obecnie połączona z Semantic Kernel). Koncepcja GroupChat przetrwała w obu projektach, choć szczegóły implementacji się różnią. AG2 pozostaje preferowanym wyborem dla zachowania kompatybilności z wersją 0.2.

### Kiedy GroupChat się sprawdza

- **Dynamiczne konwersacje.** Nie ma potrzeby wcześniejszego definiowania wszystkich możliwych przejść między rozmówcami.
- **Zadania oparte na współpracy ról.** Programista pyta badacza, badacz archiwistę, a archiwista ponownie programistę. Przepływ ten nie jest skierowanym grafem acyklicznym (DAG).
- **Eksploracyjne rozwiązywanie problemów.** Przypomina to burzę mózgów, a nie linię montażową.

### Kiedy się nie sprawdza

- **Wymóg ścisłego determinizmu.** Selektor LLM może działać niespójnie: ten sam prompt w różnych uruchomieniach może wskazać innych rozmówców.
- **Syndrom potakiwania (kaskady pochlebstw).** Agenci ślepo zgadzają się z tym, który wypowiada się z największą pewnością siebie. Rozwiązaniem jest jawne zachęcanie do konstruktywnego sceptycyzmu lub krytyki.
- **Przepełnienie kontekstu.** Każdy agent czyta całą historię; po kilkunastu turach rozmiar kontekstu drastycznie rośnie. Użyj projekcji (Lekcja 15), aby ograniczyć widoczność historii dla poszczególnych ról.
- **Dominacja jednego rozmówcy (Hot speakers).** Jeden agent przejmuje dyskusję, ponieważ selektor faworyzuje jego specjalizację. Wprowadź mechanizm bilansowania wypowiedzi w funkcji selektora.

### Czat grupowy a architektura z nadzorcą

Te same elementy podstawowe, ale różne ustawienia domyślne:

- Nadzorca (Supervisor): jeden agent planuje działania, a pozostali je realizują. Selektor sprowadza się do pytania: „zapytaj koordynatora o następny krok”.
- Czat grupowy (Group Chat): wszyscy agenci są równorzędnymi uczestnikami; selektor podejmuje decyzje na podstawie stanu wspólnej puli wiadomości.

Oba podejścia bazują na czterech podstawowych elementach z lekcji 04. Domyślna konfiguracja czatu grupowego opiera się na orkiestracji sterowanej przez LLM oraz pełnym współdzieleniu stanu (puli).

## Zbuduj to

Plik `code/main.py` zawiera podstawową implementację GroupChat napisaną w standardowej bibliotece Pythona. W projekcie bierze udział trzech agentów (programista, recenzent, menedżer). Zaimplementowano warianty wyboru: cykliczny (round-robin) oraz sterowany przez LLM, a także zakończenie rozmowy po wykryciu tokenu `TERMINATE`.

Program demonstracyjny wypisuje zapis rozmowy oraz logi decyzji selektora dla obu wariantów.

Uruchomienie:

```bash
python3 code/main.py
```

## Zastosowanie

Plik `outputs/skill-groupchat-selector.md` konfiguruje selektor GroupChat dla wybranego zadania — określając tryb cykliczny (round-robin), wybór przez LLM lub reguły niestandardowe, a także definiując dane wejściowe selektora (ostatnie wiadomości, specjalizacje agentów, licznik tur).

## Wdrożenie produkcyjne

Lista kontrolna:

- **Limit maksymalnej liczby rund.** Stosuj go zawsze (zazwyczaj 10-20 dla standardowych zadań).
- **Metryka balansu wypowiedzi.** Zliczaj tury przypadające na każdego agenta i generuj ostrzeżenie, gdy dysproporcja przekroczy ustalony próg.
- **Token zakończenia.** Użyj słowa `TERMINATE` lub przypisz tę rolę dedykowanemu agentowi weryfikującemu.
- **Ograniczenie historii lub projekcja pamięci.** Po około 10 wiadomościach rozważ udostępnianie agentom wyłącznie przefiltrowanego widoku historii, aby uniknąć przepełnienia kontekstu.
- **Logowanie decyzji selektora.** Przy wyborze sterowanym przez LLM zapisuj zarówno prompt wejściowy, jak i wyjściową decyzję selektora. W przeciwnym razie debugowanie będzie niemożliwe.

## Ćwiczenia

1. Uruchom `code/main.py`. Porównaj konwersację w trybie cyklicznym z tą sterowaną przez LLM. Który agent dominuje w poszczególnych wariantach?
2. Wprowadź w selektorze regułę „max-speaks-per-agent” (maksymalna liczba wypowiedzi na agenta). Jak wpływa to na zapis rozmowy?
3. Zaimplementuj warunek zakończenia oparty na celu: zatrzymaj czat, gdy recenzent wyśle komunikat „zatwierdzono”. Jak często udaje się zakończyć rozmowę przed osiągnięciem limitu rund?
4. Przeczytaj oficjalną dokumentację AutoGen na temat GroupChat (https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/group-chat.html). Sprawdź, jaki jest domyślny selektor używany przez `GroupChatManager`.
5. Przeanalizuj repozytorium AG2 (https://github.com/ag2ai/ag2) i porównaj implementację GroupChat bazującą na wersji 0.2 z wersją sterowaną zdarzeniami z wersji 0.4. Jakie konkretne zalety (przepustowość, odporność na błędy, modularność) wprowadza wersja 0.4?

## Kluczowe terminy

| Termin | Obiegowe określenie | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Czat grupowy (Group Chat) | „Agenci w jednym pokoju rozmów” | Wspólna pula wiadomości + funkcja selektora. Podstawowy mechanizm w AutoGen / AG2. |
| Wybór głośnika (Speaker selection) | „Kto będzie mówił dalej” | Funkcja wskazująca kolejnego agenta (cyklicznie, przez LLM lub według reguł niestandardowych). |
| Menedżer czatu grupowego | „Gospodarz spotkania” | Komponent AutoGen zarządzający selektorem i koordynujący kolejne tury rozmowy. |
| ConversableAgent | „Agent bazowy” | Klasa bazowa w AutoGen; agent zdolny do wysyłania i odbierania wiadomości. |
| Token zakończenia | „Słowo stopu” | Ciąg znaków (zazwyczaj `TERMINATE`) kończący konwersację. |
| Dominujący rozmówca (Hot speaker) | „Jeden agent monopolizuje czat” | Błąd (antywzorzec), w którym selektor w kółko wybiera tego samego agenta. |
| Przepełnienie kontekstu | „Pula wiadomości rośnie bez limitu” | Sytuacja, w której każdy agent czyta całą historię; z każdą turą rozmiar kontekstu rośnie. |
| Projekcja (Projection) | „Zawężony widok” | Dostosowany do roli, ograniczony widok wspólnej puli wiadomości zapobiegający przepełnieniu kontekstu. |

## Literatura uzupełniająca

- [Dokumentacja AutoGen Group Chat](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/group-chat.html) — implementacja referencyjna
- [Repozytorium AG2](https://github.com/ag2ai/ag2) — rozwijana przez społeczność wersja AutoGen v0.2
- [Dokumentacja Microsoft Agent Framework](https://microsoft.github.io/agent-framework/) — zintegrowany następca projektu (wersja RC, luty 2026 r.)
- [Informacje o wydaniu AutoGen v0.4](https://microsoft.github.io/autogen/stable/) — szczegóły dotyczące nowego modelu aktorów sterowanego zdarzeniami
