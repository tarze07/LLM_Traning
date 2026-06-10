# Refleksja: Uczenie się ze wzmocnieniem werbalnym

> RL oparty na gradiencie wymaga tysięcy prób i klastra GPU, aby naprawić tryb awaryjny. Refleksja (Shinn i in., NeurIPS 2023) robi to w języku naturalnym: po każdej nieudanej próbie agent zapisuje refleksję, przechowuje ją w pamięci epizodycznej i na tej pamięci warunkuje kolejną próbę. Jest to wzór leżący u podstaw obliczeń czasu snu Letty, wniosków CLAUDE.md Claude’a Code i reguły uczenia się pro-workflow.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (Pętla agenta), Faza 14 · 02 (ReWOO)
**Czas:** ~60 minut

## Cele nauczania

- Wymień trzy składniki refleksji (aktor, oceniający, autorefleksja) i rolę pamięci epizodycznej.
- Zaimplementuj pętlę refleksyjną stdlib z binarnym modułem oceny, buforem refleksji i nowymi ponownymi próbami.
- Wybieraj pomiędzy skalarnymi, heurystycznymi i samooceniającymi się źródłami informacji zwrotnej dla danego zadania.
- Wyjaśnij, dlaczego wzmocnienie werbalne wychwytuje błędy, których naprawienie oparte na gradiencie RL wymagałoby tysięcy prób.

## Problem

Agent nie wykonuje zadania. W standardowym RL można byłoby przeprowadzić tysiące kolejnych prób, obliczyć gradienty i zaktualizować wagi. Drogie, powolne i większość agentów produkcyjnych nie ma budżetu szkoleniowego na każdą awarię.

Reflexion (Shinn i in., arXiv:2303.11366) zadaje inne pytanie: co by było, gdyby agent po prostu pomyślał o tym, dlaczego mu się nie udało, i spróbował ponownie, mając tę ​​myśl w podpowiedzi? Brak aktualizacji wagi. Brak gradientu. Tylko język naturalny przechowywany pomiędzy próbami.

Wynik: w ALFWorld bije ReAct i inne nie dostrojone linie bazowe. W HotpotQA poprawia się w stosunku do ReAct. Jeśli chodzi o generowanie kodu (HumanEval/MBPP), wyznacza on ówczesny stan wiedzy. Wszystko bez jednego stopnia gradientu.

## Koncepcja

### Trzy komponenty

```
Actor         : generates a trajectory (ReAct-style loop)
Evaluator     : scores the trajectory — binary, heuristic, or self-eval
Self-Reflector: writes a natural-language reflection on the failure
```

Plus jedna struktura danych:

```
Episodic memory: list of prior reflections, prepended to the next trial's prompt
```

Jedna próba uruchamia aktora. Oceniający to ocenia. Jeśli wynik jest niski, Self-Reflector generuje refleksję („Wybrałem niewłaściwe narzędzie, ponieważ błędnie odczytałem pytanie jako pytanie o X, podczas gdy pytało o Y”). Refleksja przechodzi do pamięci epizodycznej. Następna próba zaczyna się od nowa, ale widać odbicie.

### Trzy typy ewaluatorów

1. **Skalar** — zewnętrzny sygnał binarny. Sukces lub porażka ALFWorld. Testy HumanEval przechodzą pomyślnie lub nie. Najprostszy, najwyższy sygnał.
2. **Heurystyka** — predefiniowane sygnatury awarii. „Jeśli agent wykonał tę samą czynność dwa razy z rzędu, oznacz jako utknięty.” „Jeśli trajektoria przekracza 50 kroków, oznacz jako nieefektywną.”
3. **Samoocena** — LLM ocenia własną trajektorię. Potrzebne, gdy nie jest dostępna żadna podstawowa prawda. Słabszy sygnał; dobrze łączy się z weryfikacją opartą na narzędziach (Lekcja 05 – KRYTYKA).

Wartość domyślna na rok 2026 to mieszanka: skalar, jeśli jest dostępny, samoocena, jeśli nie, heurystyki jako poręcze bezpieczeństwa.

### Dlaczego to uogólnia

Refleksja nie jest nowym algorytmem, ale nazwanym wzorcem. Prawie każdy produkcyjny agent „samonaprawiający się” uruchamia jakiś wariant:

- Obliczanie czasu snu Letty (Lekcja 08): oddzielny agent analizuje przeszłe rozmowy i zapisuje do bloków pamięci.
- Wzorzec `CLAUDE.md` Claude'a Code'a / „zachowaj pamięć”: refleksje uchwycone jako wnioski i dodane do przyszłych sesji.
- polecenie pro-workflow `/learn-rule`: poprawki zapisane jako jawne reguły.
- Węzły refleksyjne LangGraph: węzeł oceniający wyniki i trasy do udoskonalenia w razie potrzeby.

Wszystkie wywodzą się z tego samego spostrzeżenia: język naturalny jest wystarczająco bogatym medium, aby przenosić „to, czego nauczyłem się po porażce” pomiędzy seriami.

### Kiedy to działa, a kiedy nie

Refleksja działa, gdy:

- Istnieje wyraźny sygnał awarii (niepowodzenie testu, błąd narzędzia, zła odpowiedź).
- Klasa zadania jest powtarzalna (można zadać ponownie ten sam typ pytania).
- W ramach refleksji można ulepszyć trajektorię (wystarczający budżet na działania).

Refleksja nie pomaga, gdy:

- Agentowi udaje się już za pierwszym razem.
- Awaria ma charakter zewnętrzny (awaria sieci, uszkodzenie narzędzia) — refleksja „awaria sieci” nie pomaga w przyszłych uruchomieniach.
- Refleksja zamienia się w przesąd — przechowywanie narracji o jednorazowym, niepewnym biegu.

Pułapka 2026: zgnilizna pamięci. Odbicia kumulują się; niektóre są przestarzałe lub błędne; powtórki stają się wolniejsze w miarę wzrostu bufora epizodycznego. Łagodzenie: okresowe zagęszczanie (Lekcja 06), TTL na odbiciach lub oddzielny środek czyszczący w czasie snu (Letta).

## Zbuduj to

`code/main.py` implementuje refleksję na zabawkowej łamigłówce: utwórz 3-elementową listę, która sumuje się do celu. Aktor publikuje listy kandydatów; Oceniający sprawdza sumę; Self-Reflector pisze linijkę o tym, co poszło nie tak. Refleksja trafia do pamięci epizodycznej na potrzeby następnej próby.

Komponenty:

- `Actor` — strategia skryptowa, która poprawia się, gdy pojawia się refleksja.
- `Evaluator.binary()` — wynik pozytywny/negatywny dla sumy docelowej.
- `SelfReflector` — generuje jednoliniową diagnozę awarii.
- `EpisodicMemory` — lista ograniczona z semantyką TTL.

Uruchom to:

```
python3 code/main.py
```

Ślad pokazuje trzy próby. Próba 1 kończy się niepowodzeniem, odbicie jest zapisywane, próba 2 widzi odbicie i poprawia się, ale nadal kończy się niepowodzeniem, próba 3 kończy się sukcesem. Porównaj z przebiegiem bazowym (bez odbicia) — pozostaje przy odpowiedzi z próby 1.

## Użyj tego

LangGraph dostarcza odbicie jako wzór węzła. Komenda `/memory` Claude Code i `/learn-rule` pro-workflow udostępniają bufor epizodyczny jako plik przeceny. Obliczenia czasu snu Letty uruchamiają Self-Reflector w przypadku przestojów, dzięki czemu główny agent pozostaje ograniczony opóźnieniami. Pakiet SDK dla agentów OpenAI nie dostarcza bezpośrednio Reflexion; budujesz go z niestandardową poręczą, która odrzuca trajektorie według wyniku, i pamięcią `Session`, która przetrwa wszystkie przebiegi.

## Wyślij to

`outputs/skill-reflexion-buffer.md` tworzy i utrzymuje bufor epizodyczny z przechwytywaniem odbić, TTL i deduplikacją. Biorąc pod uwagę klasę zadania i niepowodzenie, emituje odbicie, które faktycznie pomaga w następnej próbie (a nie ogólne „bądź bardziej ostrożny”).

## Ćwiczenia

1. Przełącz się z binarnego na skalarny ewaluator, który zwraca metrykę odległości (jak daleko od celu). Czy zbiega się szybciej?
2. Dodaj do odbić TTL wynoszący 10 prób. Czy starsze refleksje bolą czy pomagają po tym momencie?
3. Zastosuj ewaluator heurystyczny: oznacz próbę jako zatrzymaną, jeśli ta sama akcja się powtórzy. Jak to współdziała z Self-Reflectorem?
4. Uruchom Refleksję z wrogim Aktorem, który ignoruje odbicia. Jaka jest minimalna inżynieria szybkiego odbicia, która zmusza aktora do ich zauważenia?
5. Przeczytaj sekcję 4 dokumentu refleksyjnego na temat AlfWorld. Odtwórz koncepcyjnie poprawę wskaźnika sukcesu o 130%: jaka jest kluczowa delta w porównaniu do zwykłego ReAct?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Refleksja | „Samokorekta” | Shinn i in. 2023 — Aktor, Ewaluator, Autorefleksja plus pamięć epizodyczna |
| Wzmocnienie werbalne | „Nauka bez gradientów” | Refleksja w języku naturalnym poprzedzająca zachętę do następnej próby |
| Pamięć epizodyczna | „Refleksje dotyczące poszczególnych zadań” | Ograniczony bufor wcześniejszych refleksji dla jednej klasy zadań |
| Ewaluator skalarny | „Binarny sygnał sukcesu” | Zaliczony/niezaliczony lub wynik liczbowy na podstawie prawdy podstawowej |
| Ewaluator heurystyczny | „Detektor oparty na wzorach” | Predefiniowane sygnatury błędów (np. utknięta pętla, zbyt wiele kroków) |
| Samoocena | „LLM-jako-sędzia na własnym tropie” | Awaryjny niższy sygnał w przypadku braku prawdy podstawowej — w połączeniu z weryfikacją opartą na narzędziu |
| Zgnilizna pamięci | „Nieaktualne refleksje” | Bufor epizodyczny zapełnia się przestarzałymi wpisami; naprawić za pomocą zagęszczania/TTL |
| Refleksja w czasie snu | „Asynchroniczna autorefleksja” | Wyłącz Self-Reflector z gorącej ścieżki, aby główny agent pozostał szybki |

## Dalsze czytanie

- [Shinn i in., Reflexion: Language Agents with Verbal Reinforcement Learning (arXiv:2303.11366)](https://arxiv.org/abs/2303.11366) — artykuł kanoniczny
- [Letta, Obliczanie czasu snu](https://www.letta.com/blog/sleep-time-compute) — asynchroniczne odbicie w produkcji
- [Anthropic, Efektywna inżynieria kontekstu dla agentów AI](https://www.anthropic.com/engineering/efektyw-context-engineering-for-ai-agents) — zarządzanie buforem epizodycznym jako częścią kontekstu
- [Omówienie LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) — wzór węzła odbicia