# Tryby awarii: dlaczego agenci zawodzą

> Publikacja MASFT (Berkeley, 2025) kataloguje 14 trybów awarii systemów wieloagentowych, dzieląc je na 3 kategorie. Taksonomia opracowana przez firmę Microsoft dokumentuje, jak znane dotychczas problemy sztucznej inteligencji (np. halucynacje, uprzedzenia) nasilają się w środowiskach agentowych. Dane z wdrożeń produkcyjnych wskazują na pięć najczęstszych problemów: halucynacje behawioralne, rozszerzanie zakresu działania (scope creep), błędy kaskadowe, utratę kontekstu oraz niewłaściwe użycie narzędzi.

**Typ:** Ucz się + Buduj
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 05 (Samodoskonalenie i KRYTYK), Faza 14 · 24 (Obserwowalność)
**Czas:** ~60 minut

## Cele nauczania

- Wymień trzy kategorie awarii według klasyfikacji MASFT oraz co najmniej cztery konkretne tryby awarii w każdej z nich.
- Wyjaśnij, w jaki sposób architektura agentowa potęguje istniejące problemy systemów AI (takie jak stronniczość czy halucynacje).
- Opisz pięć najczęściej występujących w branży trybów awarii oraz metody ich ograniczania (mitigation).
- Zaimplementuj prosty detektor (oparty na stdlib), który analizuje ślady (traces) i automatycznie przypisuje im etykiety odpowiednich trybów awarii.

## Problem

Zespoły często wdrażają agentów, którzy działają poprawnie w 90% przypadków. Pozostałe 10% niepowodzeń nie jest jednak losowym szumem – można je sklasyfikować w kilka powtarzających się kategorii. Identyfikacja i nazwanie tych trybów awarii pozwala na ich systemowe monitorowanie i eliminację.

## Koncepcja

### MASFT (Berkeley, arXiv:2503.13657)

MASFT to taksonomia awarii systemów wieloagentowych (Multi-Agent System Failure Taxonomy). Klasyfikuje ona 14 trybów awarii podzielonych na 3 główne kategorie. Współczynnik zgodności sędziów (Cohen's Kappa) wynosi w tym badaniu 0,88, co oznacza, że kategorie te można wiarygodnie rozróżnić.

Główna teza: te awarie wynikają z błędów projektowych samych systemów wieloagentowych, a nie z wewnętrznych ograniczeń modeli LLM, których rzekomo można by uniknąć poprzez proste przejście na lepsze modele bazowe.

### Taksonomia firmy Microsoft dotycząca trybów awarii w agentowych systemach AI

- Typowe problemy sztucznej inteligencji (stronniczość, halucynacje, wycieki danych) ulegają nasileniu w architekturach agentowych.
- Z autonomii agentów wynikają nowe rodzaje zagrożeń: niezamierzone działania na dużą skalę, niewłaściwe użycie narzędzi oraz dryfowanie celu (mission drift).
- Opracowana przez Microsoft publikacja służy jako rejestr ryzyka (risk register) dla wdrożeń agentowych.

### Charakterystyka błędów agentowych (arXiv:2603.06847)

- Awaria systemu agentowego rzadko jest wyłącznie skutkiem „złego kodu” czy „błędnej odpowiedzi modelu”.
- Problemy te najczęściej wynikają ze złożonej orkiestracji, ewolucji stanu wewnętrznego agenta oraz jego interakcji z dynamicznym środowiskiem zewnętrznym.

### Badanie nad halucynacjami u agentów LLM (arXiv:2509.18970)

Wyróżnia dwa główne przejawy tego problemu:

1. **Odchylenie od instrukcji (Instruction deviation):** Agent ignoruje lub modyfikuje instrukcje systemowe.
2. **Utrata kontekstu długoterminowego (Long-term contextual misuse):** Agent zapomina kluczowe fakty podane we wcześniejszych turach rozmowy lub błędnie je interpretuje.

Typowe błędy w planowaniu działań: pominięcie (omijanie kroków), nadmiarowość (pętlenie i powtarzanie tych samych kroków) oraz zaburzenie kolejności (wykonywanie kroków w złej kolejnością).

### Pięć najczęstszych trybów awarii w praktyce

Analizy wdrożeń produkcyjnych (Arize, Galileo, NimbleBrain 2024–2026) wskazują na następujące typowe problemy:

1. **Działania halucynacyjne (Action hallucination):** Agent wywołuje nieistniejące narzędzia lub wymyśla dla nich niepoprawne argumenty.
2. **Rozszerzanie zakresu (Scope creep):** Agent podejmuje działania wykraczające poza intencję użytkownika (np. generuje dodatkowe Pull Requesty, wysyła niepotrzebne e-maile).
3. **Błędy kaskadowe (Cascading failures):** Pojedynczy błąd na wczesnym etapie wywołuje lawinę kolejnych problemów (np. halucynacja nieistniejącego SKU skutkuje serią błędnych odpytań API w innych systemach).
4. **Utrata kontekstu (Context drift/loss):** Przy długich procesach agent zapomina o ograniczeniach zdefiniowanych na samym początku interakcji.
5. **Niewłaściwe użycie narzędzia (Tool misuse):** Agent wybiera złe narzędzie lub przekazuje do poprawnego narzędzia niepoprawne dane.

Błędy kaskadowe są najtrudniejsze w obsłudze. Agenci rzadko potrafią odróżnić chwilowy problem (np. „wywołanie nie powiodło się”) od sytuacji patowej („zadanie jest niewykonalne”). Często w odpowiedzi na serię błędów generują fałszywy raport o sukcesie (halucynacja sukcesu), byle tylko zamknąć pętlę wykonania.

### Metody ograniczania ryzyka (Mitigations): bramki kontrolne

Wprowadzenie automatycznych bramek walidacyjnych na każdym etapie łańcucha wnioskowania w celu weryfikacji faktów i spójności ze stanem środowiska:

- Klasyfikatory bezpieczeństwa uruchamiane na każdym kroku (sekwencyjna kontrola, lekcja 21).
- Walidacja typów i wartości argumentów przekazywanych do narzędzi (lekcja 06).
- Weryfikacja pobranych informacji ze znaną bazą faktów (wzorzec CRITIC, lekcja 05).
- Wykrywanie „halucynacji sukcesu” poprzez weryfikację stanu faktycznego w środowisku (np. sprawdzenie, czy plik rzeczywiście został zapisany na dysku).

### Gdzie monitorowanie awarii może zawieść

- **Ograniczanie się do prostej analizy kodu powrotu:** Większość błędnych odpowiedzi agenta zwraca status sukcesu i poprawny format JSON. Niezbędna jest ewaluacja jakościowa generowanych treści.
- **Brak linii bazowej (baseline):** Detekcja dryfu wymaga posiadania wzorcowego zbioru poprawnych uruchomień. Bez tego nie da się obiektywnie stwierdzić pogorszenia jakości.
- **Zasypywanie alertami (alert fatigue):** Generowanie powiadomienia przy każdym pojedynczym błędzie prowadzi do ignorowania ostrzeżeń. Alerty należy grupować i ograniczać częstotliwość ich wysyłania (rate-limiting).

## Zbuduj to

Plik `code/main.py` implementuje prosty moduł do oznaczania trybów awarii (tagger) oparty na bibliotece standardowej:

- Syntetyczny zbiór danych zawierający ślady (traces) reprezentujące pięć głównych trybów awarii.
- Funkcje detekcji dla każdego trybu (analiza sygnatur wywołań narzędzi, danych wyjściowych, powtarzających się akcji).
- Moduł przypisujący etykiety do poszczególnych śladów oraz generujący raport z rozkładu błędów.

Uruchomienie:

```
python3 code/main.py
```

Dane wyjściowe: etykiety dla każdego śladu oraz zestawienie statystyczne błędów – prosta, lokalna namiastka funkcji klastrowania śladów dostępnej w Arize Phoenix.

## Użyj tego

- **Arize Phoenix**: do zaawansowanego grupowania dryfu i anomalii na produkcji (lekcja 24).
- **Langfuse**: do odtwarzania sesji krok po kroku oraz ręcznego oznaczania śladów (adnotacji).
- **Własna implementacja**: do wykrywania specyficznych dla danej domeny sygnatur błędów, których standardowe platformy nie potrafią automatycznie zidentyfikować.

## Wyślij to

Plik `outputs/skill-failure-detector.md` opisuje sposób budowy detektorów trybów awarii dostosowanych do specyfiki Twojej domeny biznesowej i zintegrowanych z bazą śladów.

## Ćwiczenia

1. Zaimplementuj detektor „halucynacji sukcesu”: sytuacja, w której agent zwraca komunikat o powodzeniu operacji, ale faktyczny stan docelowy środowiska nie uległ zmianie.
2. Przeanalizuj ręcznie 100 rzeczywistych śladów ze swojej aplikacji. Który tryb awarii występuje najczęściej? Jaki byłby szacunkowy koszt jego eliminacji?
3. Zaimplementuj metrykę „promienia kaskady” (cascade radius): zbadaj, na ile kolejnych kroków procesu wpłynął błąd popełniony w kroku N.
4. Zapoznaj się z 14 trybami awarii w klasyfikacji MASFT. Wybierz trzy najbardziej prawdopodobne w Twoim projekcie i napisz dla nich reguły detekcji.
5. Zintegruj detektor błędów z potokiem CI: proces budowania powinien zakończyć się niepowodzeniem, jeśli >=5% śladów testowych zostanie oznaczonych etykietą trybu awarii.

## Kluczowe terminy

| Termin | Co potocznie się mówi | Co to oznacza w rzeczywistości |
|------|----------------|--------------------------------------|
| MASFT | „Klasyfikacja błędów wieloagentowych” | Opracowany na Berkeley system kategoryzacji 14 trybów awarii |
| Błąd kaskadowy (Cascading failure) | „Błąd lawinowy” | Sytuacja, w której jeden wczesny błąd propaguje się na N kolejnych kroków |
| Utrata kontekstu | „Zapominanie ustaleń” | Długi proces powoduje ignorowanie ograniczeń zdefiniowanych na początku sesji |
| Niewłaściwe użycie narzędzia | „Złe wywołanie API / złe argumenty” | Wywołanie poprawnego narzędzia z błędnymi danymi lub wybór niewłaściwego narzędzia |
| Halucynacja sukcesu | „Fałszywy sukces” | Agent zgłasza udane ukończenie zadania, mimo że operacja się nie udała lub stan docelowy nie uległ zmianie |
| Rozszerzanie zakresu (Scope creep) | „Nadgorliwość agenta” | Wykonywanie przez agenta nadmiarowych czynności, o które użytkownik nie prosił |
| Odchylenie od instrukcji | „Ignorowanie system promptu” | Niezastosowanie się do instrukcji systemowych lub ograniczeń narzuconych przez użytkownika |
| Błędy planowania | „Błędy w strukturze planu” | Pominięcie kroku, powtórzenie wykonanego kroku lub zaburzenie kolejności w harmonogramie działań |

## Dalsze czytanie

- [Cemri et al., MASFT (arXiv:2503.13657)](https://arxiv.org/abs/2503.13657) – publikacja naukowa o 14 trybach awarii podzielonych na 3 kategorie
- [Microsoft, Taxonomy of Failure Mode in Agentic AI Systems](https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/final/en-us/microsoft-brand/documents/Taxonomy-of-Failure-Mode-in-Agentic-AI-Systems-Whitepaper.pdf) – biała księga Microsoftu będąca rejestrem ryzyka
- [Arize Phoenix](https://docs.arize.com/phoenix) – dokumentacja dotycząca analizy dryfu i grupowania śladów
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) – przewodnik jak unikać trybów awarii poprzez stosowanie prostszych, przewidywalnych wzorców orkiestracji
