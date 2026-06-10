---

name: handoff-generator
description: Generuj pakiety przekazania na koniec sesji na podstawie artefaktów środowiska roboczego. Narzędzie tworzy zarówno czytelny dla człowieka plik Markdown, jak i czytelny dla maszyn plik JSON zawierający siedem kluczowych pól przekazania.
version: 1.0.0
phase: 14
lesson: 40
tags: [handoff, generator, session-end, packet, next-action]

---

Na podstawie danych ze środowiska roboczego (stan, werdykt, raport recenzji, logi sprzężenia zwrotnego, diff) utwórz generator pakietów przekazania na koniec sesji, zintegrowany ze środowiskiem uruchomieniowym agenta.

Wymagane elementy:

1. Skrypt `tools/generate_handoff.py` udostępniający funkcję `generate_handoff(snapshot) -> (markdown, payload)`.
2. Pliki `outputs/handoff/<session_id>/handoff.md` oraz `handoff.json`.
3. Schemat `handoff.schema.json` opisujący strukturę siedmiu wymaganych pól i format skróconych logów (trimmed feedback).
4. Skrypt przechwytujący zdarzenie zakończenia sesji, który uruchamia generator i blokuje zamknięcie sesji w przypadku braku któregokolwiek z wymaganych pól.
5. Dokument `docs/handoff.md` szczegółowo opisujący siedem pól, ich źródła danych oraz zasady przycinania logów.

Bezwzględne odrzucenia (Twarde kryteria):

- Przekazanie bez zdefiniowanego pola `next_action`. Raporty o stanie udające przekazanie prac paraliżują start kolejnej sesji.
- Ręczne opisywanie podsumowania przez generator. Zadaniem agenta jest utrzymanie środowiska roboczego w stanie pozwalającym na automatyczną generację raportu.
- Rozbieżności strukturalne między plikiem Markdown a plikiem JSON. JSON stanowi pierwotne źródło danych, a plik Markdown jest jedynie jego wizualizacją.
- Uwzględnienie w logach (feedback tail) więcej niż 30 wpisów. Pełna historia logów znajduje się w systemie kontroli wersji; pakiet przekazania musi pozostać lekki.

Zasady odmowy współpracy (Refusal rules):

- Jeśli raport weryfikacji nie istnieje, odmów wygenerowania pakietu. Przekazanie prac bez werdyktu weryfikacyjnego jest bezcelowe.
- Jeśli brakuje raportu z recenzji, a wymagana jest manualna weryfikacja przez człowieka, odmów wygenerowania pakietu i zażądaj najpierw przeprowadzenia recenzji.
- Jeśli zestaw zmian (diff) jest pusty, lecz sesja trwała dłużej niż 5 minut, zgłoś anomalię przed generowaniem raportu. Istnieje duże prawdopodobieństwo zawieszenia sesji, a nie rzeczywistego braku działań (no-op).

Struktura plików:

```
<repo>/
├── outputs/handoff/<session_id>/
│   ├── handoff.md
│   └── handoff.json
├── tools/generate_handoff.py
├── handoff.schema.json
└── docs/handoff.md
```

Na koniec dodaj sekcję „Co przeczytać dalej”, wskazującą na:

- Lekcję 41 zawierającą kompleksowe ćwiczenia na bazie rzeczywistej aplikacji deweloperskiej.
- Lekcję 42 poświęconą integracji generatora z końcowym środowiskiem roboczym projektu.
- Lekcję 29 (Środowisko uruchomieniowe) na temat automatycznego wiązania końca sesji z wyzwalaczami kolejek, zdarzeń oraz zadań cron.
