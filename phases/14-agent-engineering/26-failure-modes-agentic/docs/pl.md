# Tryby awarii: dlaczego agenci się psują

> MASFT (Berkeley, 2025) kataloguje 14 wieloagentowych trybów awarii w 3 kategoriach. Taksonomia firmy Microsoft dokumentuje, w jaki sposób istniejące awarie sztucznej inteligencji nasilają się w ustawieniach agenta. Dane terenowe branży skupiają się na pięciu powtarzających się trybach: halucynacjach, pełzaniu zakresu, kaskadowych błędach, utracie kontekstu, niewłaściwym użyciu narzędzi.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 05 (Samodoskonalenie i KRYTYK), Faza 14 · 24 (Obserwowalność)
**Czas:** ~60 minut

## Cele nauczania

- Wymień trzy kategorie awarii MASFT i co najmniej cztery konkretne tryby w każdej z nich.
- Wyjaśnij, dlaczego awaria agenta wzmacnia istniejące tryby awarii AI (stronniczość, halucynacje).
- Opisać pięć powtarzających się w branży trybów i ich łagodzenia.
— Zaimplementuj detektor stdlib, który oznacza ślady agentów etykietami trybu awarii.

## Problem

Zespoły wysyłają agentów, którzy pracują nad 90% śladów. Te 10% niepowodzeń nie jest przypadkowym szumem — można je podzielić na niewielką liczbę powtarzających się kategorii. Gdy już je nazwiesz, możesz je monitorować i naprawiać.

## Koncepcja

### MASFT (Berkeley, arXiv:2503.13657)

Taksonomia awarii systemu wieloagentowego. 14 trybów awarii podzielonych na 3 kategorie. Kappa między komentatorami Cohena 0,88 — kategorie można wiarygodnie rozróżnić.

Główne twierdzenie: awarie są podstawowymi wadami konstrukcyjnymi systemów wieloagentowych, a nie ograniczeniami LLM, które można naprawić za pomocą lepszych modeli podstawowych.

### Taksonomia firmy Microsoft dotycząca trybu awarii w agentycznych systemach AI

- Istniejące awarie sztucznej inteligencji (stronniczość, halucynacje, wycieki danych) nasilają się w ustawieniach agenta.
- Z autonomii wyłaniają się nowe niepowodzenia: niezamierzone działania na dużą skalę, niewłaściwe użycie narzędzi, dryfowanie misji.
- Biała księga stanowi rejestr ryzyka dla produktów agentycznych.

### Charakterystyka błędów agentycznej sztucznej inteligencji (arXiv:2603.06847)

- Awarie wynikają z orkiestracji, ewolucji stanu wewnętrznego i interakcji ze środowiskiem.
- Nie tylko „zły kod” lub „złe dane wyjściowe modelu”.

### Ankieta dotycząca halucynacji agentów LLM (arXiv:2509.18970)

Dwa główne przejawy:

1. **Odchylenie od instrukcji** — agent nie postępuje zgodnie z poleceniami systemu.
2. **Długoterminowe niewłaściwe użycie kontekstowe** – agent zapomina lub błędnie stosuje kontekst z poprzednich tur.

Błędy podrzędne: pominięcie (pominięty krok), nadmiarowość (powtórzony krok), zaburzenie (kroki poza kolejnością).

### Pięć powtarzających się trybów branżowych

Analizy terenowe Arize, Galileo, NimbleBrain 2024–2026 zbiegają się w zakresie:

1. **Działania halucynacyjne.** Agent przywołuje narzędzie, które nie istnieje lub fabrykuje argumenty.
2. **Rozszerzanie zakresu.** Agent rozszerza zadanie poza prośbę użytkownika (tworzy dodatkowe PR, wysyła dodatkowe e-maile).
3. **Błędy kaskadowe.** Jedno błędne wywołanie powoduje dalsze skutki. Halucynacja fantomowa SKU uruchamia cztery wywołania API – incydent obejmujący wiele systemów.
4. **Utrata kontekstu.** Zadania długoterminowe pozwalają zapomnieć o ograniczeniach pojawiających się na początku tury.
5. **Niewłaściwe użycie narzędzia.** Wywołuje właściwe narzędzie z błędnymi argumentami lub całkowicie niewłaściwe narzędzie.

Kaskadowanie jest zabójcze. Agenci nie potrafią odróżnić „nie udało mi się” od „zadanie jest niemożliwe” i często halucynują się komunikatem o powodzeniu dotyczącym 400 błędów, aby zamknąć pętlę.

### Łagodzenie: bramy na każdym kroku

Zautomatyzowane bramki weryfikacyjne na każdym etapie łańcucha rozumowania, sprawdzające uziemienie faktyczne w stosunku do stanu środowiska. Konkretnie:

- Klasyfikator bezpieczeństwa krokowy (Lekcja 21).
- Walidacja argumentu wywołania narzędzia (lekcja 06).
- Sprawdzaj pobrane treści ze znanymi faktami (Lekcja 05, KRYTYK).
- Wykryj halucynacje sukcesu poprzez ponowne sprawdzenie stanu (czy plik faktycznie został utworzony?).

### Gdzie monitorowanie awarii nie działa

- **Awaria dotyczy tylko tagowania.** Większość błędów agenta generuje prawidłowo wyglądające dane wyjściowe. Potrzebujesz kontroli na poziomie treści.
- **Brak wartości bazowej.** Wykrywanie dryfu wymaga ostatniego znanego dobra; bez tego nie można powiedzieć: „jest coraz gorzej”.
- **Nadmierne alarmowanie.** Każda awaria powoduje wyświetlenie strony. Klaster i limit szybkości.

## Zbuduj to

`code/main.py` implementuje tager trybu awarii stdlib:

- Syntetyczny zestaw danych śledzenia obejmujący pięć trybów.
- Funkcje detektora według trybu (wzorce podpisów przy wywołaniach narzędzi, wyjściach, powtarzalnych czynnościach).
- Tagger oznaczający każdy ślad i rozkład trybu raportowania.

Uruchom to:

```
python3 code/main.py
```

Dane wyjściowe: etykiety poszczególnych śladów + dystrybucja zbiorcza, tania reprodukcja tego, co ukazuje klasterowanie śladów Phoenix.

## Użyj tego

- **Phoenix** do grupowania dryfów produkcyjnych (lekcja 24).
- **Langfuse** do odtwarzania sesji + adnotacja.
- **Niestandardowe** dla podpisów specyficznych dla domeny, których Twoja platforma obserwowalności nie może wykryć.

## Wyślij to

`outputs/skill-failure-detector.md` generuje detektory trybu awarii dostosowane do Twojej domeny, połączone z magazynem śledzenia.

## Ćwiczenia

1. Dodaj detektor „halucynacji sukcesu”: agent zwraca sukces, ale stan docelowy pozostaje niezmieniony.
2. Oznacz 100 prawdziwych śladów produktu, który zbudowałeś. Który tryb dominuje? Jaki jest koszt naprawy?
3. Zaimplementuj metrykę „promień kaskady”: biorąc pod uwagę niepowodzenie w kroku N, na ile kolejnych etapów miało to wpływ?
4. Przeczytaj 14 trybów awarii MASFT. Wybierz trzy, które dotyczą Twojego produktu. Napisz detektory.
5. Podłącz jeden detektor do zadania CI: kompilacja zakończy się niepowodzeniem, jeśli >=5% śladów oznacza tryb.

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| MASFT | „Taksonomia błędów wieloagentowych” | Kategoryzacja 14 trybów Berkeley |
| Błąd kaskadowy | „Awaria tętnienia” | Jeden wczesny błąd rozprzestrzenia się przez N kroków |
| Utrata kontekstu | „Zapomniałem o ograniczeniu” | Tura długohoryzontna obniża fakty dotyczące wczesnej tury |
| Niewłaściwe użycie narzędzia | „Złe narzędzie / złe argumenty” | Prawidłowe wywołanie, błędne wywołanie |
| Halucynacja sukcesu | „Sfałszowane zakończenie” | Agent ogłasza sukces na 400; stan bez zmian |
| Pełzanie lunety | „Przekroczenie zasięgu” | Agent robi więcej, niż się prosi |
| Odchylenie od instrukcji | „Nieposłuszeństwo” | Ignoruje monit systemowy lub ograniczenie użytkownika |
| Błędy podrzędne | „Błędy w planie” | Zaniechanie, redundancja, nieporządek w realizacji planu |

## Dalsze czytanie

- [Cemri et al., MASFT (arXiv:2503.13657)](https://arxiv.org/abs/2503.13657) — 14 trybów awarii, 3 kategorie
- [Microsoft, Taksonomia trybu awarii w agentycznych systemach AI](https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/final/en-us/microsoft-brand/documents/Taxonomy-of-Failure-Mode-in-Agentic-AI-Systems-Whitepaper.pdf) — rejestr ryzyka
- [Arize Phoenix](https://docs.arize.com/phoenix) — grupowanie dryfów w praktyce
– [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-efektywne-agents) — gdy prostsze wzorce całkowicie unikają trybów