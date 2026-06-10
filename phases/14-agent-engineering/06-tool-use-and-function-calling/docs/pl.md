# Użycie narzędzia i wywoływanie funkcji

> Toolformer (Schick i in., 2023) rozpoczął samonadzorowane dodawanie adnotacji do narzędzi. Berkeley Function Calling Leaderboard V4 (Patil i in., 2025) wyznacza poprzeczkę na rok 2026: 40% agentów, 30% wieloturowych, 10% na żywo, 10% niena żywo, 10% halucynacji. Pojedynczy obrót został rozwiązany. Pamięć, dynamiczne podejmowanie decyzji i długoterminowe łańcuchy narzędzi już nie.

**Typ:** Kompilacja
**Języki:** Python (stdlib)
**Wymagania wstępne:** Faza 14 · 01 (pętla agenta), faza 13 · 01 (funkcja wywołująca głębokie nurkowanie)
**Czas:** ~60 minut

## Cele nauczania

- Wyjaśnij sygnał samonadzorowanego szkolenia Toolformera: przechowuj adnotacje dotyczące narzędzi tylko wtedy, gdy wykonanie zmniejszy stratę następnego tokena.
- Wymień pięć kategorii oceny BFCL V4 i co każda z nich mierzy.
- Zaimplementuj rejestr narzędzi stdlib z walidacją schematu, wymuszaniem argumentów i piaskownicą wykonywania.
- Zdiagnozuj trzy otwarte problemy na rok 2026: długoterminowe łączenie narzędzi w łańcuchy, dynamiczne podejmowanie decyzji i pamięć.

## Problem

Wczesne użycie narzędzia zadało pytanie: czy model może przewidzieć prawidłowe wywołanie funkcji? Współczesne użycie narzędzi zadaje pytanie: czy model może łączyć narzędzia w 40 krokach, z pamięcią, z częściową obserwowalnością, z możliwością odzyskiwania po awariach narzędzi, bez halucynujących narzędzi, które nie istnieją?

Toolformer ustalił punkt odniesienia: modele mogą nauczyć się, kiedy wywołać narzędzia, dzięki samonadzorowi. BFCL V4 określa cel oceny na rok 2026. Różnica między nimi wynika z przestrzeni, w której żyją agenci produkcji.

## Koncepcja

### Formformer (Schick i in., NeurIPS 2023)

Pomysł: pozwól modelowi dodać adnotacje do własnego korpusu przedtreningowego z kandydującymi wywołaniami API. Wykonaj go dla każdego kandydata. Zachowaj adnotację tylko wtedy, gdy uwzględnienie wyniku narzędzia zmniejszy stratę na następnym żetonie. Dostrój przefiltrowany korpus.

Objęte narzędzia: kalkulator, system kontroli jakości, wyszukiwarki, tłumacz, kalendarz. Sygnał samonadzoru dotyczy wyłącznie tego, czy narzędzie pomaga przewidzieć tekst, a nie ludzkich etykiet.

Wynik skali: wykorzystanie narzędzi pojawia się na dużą skalę. Mniejsze modele bolały od adnotacji dotyczących narzędzi; większe modele zyskują. Właśnie dlatego modele frontierowe na rok 2026 charakteryzują się dużym wykorzystaniem narzędzi, podczas gdy większość modeli 7B wymaga wyraźnego dostrojenia użycia narzędzi, aby były niezawodne.

### Tablica liderów wywołań funkcji Berkeley, wersja 4 (Patil i in., ICML 2025)

BFCL to de facto ocena z 2026 r. Skład V4:

- **Agentyczny (40%)** — pełne trajektorie agenta: pamięć, wieloobrotowość, dynamiczne decyzje.
- **Wieloobrotowy (30%)** — interaktywne rozmowy z łańcuchami narzędziowymi.
- **Na żywo (10%)** — prawdziwe podpowiedzi przesłane przez użytkownika (trudniejsza dystrybucja).
- **Non-Live (10%)** — syntetyczne przypadki testowe.
- **Halucynacja (10%)** — wykrywa, kiedy nie należy wywoływać żadnego narzędzia.

W wersji 3 wprowadzono ocenę opartą na stanie: po sekwencji narzędzi sprawdź rzeczywisty stan interfejsu API (np. „czy plik został utworzony?”), a nie dopasuj AST wywołań narzędzi. W wersji 4 dodano kategorie wyszukiwania w Internecie, pamięci i wrażliwości na format.

Kluczowe odkrycie z 2026 r.: wywoływanie funkcji jednoobrotowych jest prawie rozwiązane. Niepowodzenia koncentrują się na pamięci (przenoszenie kontekstu przez tury), dynamicznym podejmowaniu decyzji (wybór narzędzi w oparciu o wcześniejsze wyniki), łańcuchach o długim horyzoncie (dryfowanie po ponad 20 krokach) i wykrywaniu halucynacji (odmowa wywołania, gdy żadne narzędzie nie pasuje).

### Schemat narzędzia

Każdy dostawca ma schemat. Różnią się szczegółami, ale mają ten sam kształt:

```
name: string
description: string (what it does, when to use it)
input_schema: JSON Schema (properties, required, types, enums)
```

Anthropic używa bezpośrednio `input_schema`. OpenAI używa `function.parameters`. Oba akceptują schemat JSON. Opisy są nośne – model je czyta, aby wybrać odpowiednie narzędzie. Złe opisy narzędzi są główną przyczyną niepowodzeń źle wybranych narzędzi.

### Walidacja argumentu

Nie ufaj żadnemu wywołaniu narzędzia. Zweryfikuj:

1. **Wpisz przymus.** Model może zwrócić ciąg „5”, jeśli schemat mówi int. Przymus, jeśli jest jednoznaczny; odrzuć, jeśli nie.
2. **Weryfikacja wyliczenia.** Jeśli schemat mówi `status in {"open", "closed"}`, a model emituje `"in_progress"`, odrzuć z błędem opisowym.
3. **Pola wymagane.** Brak wymaganego pola -> natychmiastowa obserwacja błędu z powrotem do modelu, a nie awaria.
4. **Weryfikacja formatu.** Daty, e-maile, adresy URL — sprawdzaj za pomocą konkretnych analizatorów składni, a nie wyrażeń regularnych.

Każdy błąd walidacji powinien zwrócić uporządkowaną obserwację, aby model mógł ponowić próbę z poprawnym kształtem.

### Równoległe wywołania narzędzi

Współcześni dostawcy obsługują równoległe wywołania narzędzi w jednej turze asystenta. Pętla:

1. Model emituje 3 wywołania narzędzi z różnymi `tool_use_id`s.
2. Runtime wykonuje je (równolegle, jeśli są niezależne).
3. Każdy wynik wraca jako blok `tool_result` skorelowany przez `tool_use_id`.

Reguła inżynierska: traktuj identyfikatory korelacji jako nośne. Zamień je, a otrzymasz przekierowanie od złego narzędzia do złego wyniku.

### Piaskownica

Wykonanie narzędzia jest granicą piaskownicy. Szczegóły znajdziesz w Lekcji 09. Wersja krótka: każde narzędzie powinno określać powierzchnię odczytu/zapisu, dostęp do sieci, limit czasu, limit pamięci. Ogólny `run_shell(cmd)` to czerwona flaga; konkretny `git_status()` jest bezpieczniejszy.

## Zbuduj to

`code/main.py` implementuje rejestr narzędzi w kształcie produkcyjnym:

- Walidator podzbioru schematu JSON (tylko stdlib).
- Rejestracja narzędzia z opisem, schematem wejściowym, limitem czasu i wykonawcą.
- Wymuszanie argumentów i sprawdzanie poprawności wyliczeń.
- Równoległe wysyłanie narzędzi z identyfikatorami korelacji.
- Obserwacje błędów w postaci ciągów strukturalnych.

Uruchom to:

```
python3 code/main.py
```

Ślad pokazuje miniagenta wywołującego trzy narzędzia w jednej turze, z jednym celowo zniekształconym wywołaniem, które jest odrzucane z powodu błędu opisowego, na podstawie którego model może działać.

## Użyj tego

Każdy dostawca ma swój własny schemat narzędzi — Anthropic, OpenAI, Gemini, Bedrock. Użyj warstwy translacyjnej (OpenAI Agents SDK, Vercel AI SDK, adapter narzędzi LangChain), jeśli potrzebujesz wielu dostawców. BFCL to punkt odniesienia — porównaj go z agentem przed wysyłką, jeśli użycie narzędzi ma kluczowe znaczenie dla produktu.

## Wyślij to

`outputs/skill-tool-registry.md` generuje katalog narzędzi, schemat i rejestr dla danej domeny zadaniowej. Obejmuje kontrolę jakości opisu (czy opis każdego narzędzia informuje model, kiedy go użyć?).

## Ćwiczenia

1. Dodaj narzędzie „no-op”, które pozwala modelowi wyraźnie odmówić użycia jakiegokolwiek innego narzędzia. Zmierz w teście halucynacji podobnym do BFCL.
2. Zaimplementuj wymuszanie argumentów dla znaków typu int-as-string i float-as-string. Gdzie zaczyna się przymus ukrywania prawdziwych błędów?
3. Dodaj limit czasu dla każdego narzędzia i wyłącznik automatyczny (odrzuć narzędzie na 60 s po 3 kolejnych awariach). Co to zmienia w sposobie odzyskiwania modelu?
4. Przeczytaj opis BFCL V4. Wybierz jedną kategorię (np. „wieloobrotowy”) i przeprowadź 10 przykładowych podpowiedzi za pośrednictwem swojego agenta. Zgłoś wskaźnik zdawalności.
5. Przenieś walidator stdlib do Pydantic lub Zod. Co Pydantic/Zod złapał, a czego nie zauważyła zabawka?

## Kluczowe terminy

| Termin | Co ludzie mówią | Co to właściwie oznacza |
|------|----------------|--------------------------------------|
| Wywołanie funkcji | „Korzystanie z narzędzi” | Wywoływanie narzędzia do ustrukturyzowanych wyników z zatwierdzonym schematem |
| Kształtownik | „Adnotacja narzędzia samonadzorującego” | Schick 2023 — zachowaj wywołania narzędzi, których wyniki zmniejszają stratę następnego tokena |
| BFCL | „Tabela wyników wywołań funkcji w Berkeley” | Benchmark na rok 2026: 40% agentów, 30% wieloobrotowych, 10% na żywo, 10% nie na żywo, 10% halucynacji |
| Schemat narzędzia | „Podpis funkcji dla modelu” | nazwa, opis, JSON Schemat argumentów |
| identyfikator_użycia narzędzia | „Identyfikator korelacji” | Wiąże wywołanie narzędzia z jego wynikiem; niezbędne do wysyłki równoległej |
| Wykrywanie halucynacji | „Wiedź, kiedy nie dzwonić” | Kategoria V4: odmowa połączenia, gdy żadne narzędzie nie pasuje |
| Przymus argumentacyjny | „Naprawa ciągu znaków do int” | Wąskie poprawki przewidywalnych niedopasowań schematu; odrzucić, jeżeli jest niejednoznaczne |
| Piaskownica | „Granica wykonania narzędzia” | Powierzchnia odczytu/zapisu dla każdego narzędzia, sieć, przekroczenie limitu czasu, limit pamięci |

## Dalsze czytanie

- [Schick i in., Toolformer (arXiv:2302.04761)](https://arxiv.org/abs/2302.04761) — adnotacja dotycząca narzędzia samonadzorowanego
– [Tabela liderów wywołań funkcji Berkeley (V4)](https://gorilla.cs.berkeley.edu/leaderboard.html) – test porównawczy eval 2026
- [Anthropic, dokumentacja użycia narzędzi](https://platform.claude.com/docs/en/agent-sdk/overview) — schemat narzędzia produkcyjnego w pakiecie SDK Claude Agent
- [Dokumentacja pakietu SDK OpenAI Agents](https://openai.github.io/openai-agents-python/) — typ narzędzia funkcyjnego i poręcze