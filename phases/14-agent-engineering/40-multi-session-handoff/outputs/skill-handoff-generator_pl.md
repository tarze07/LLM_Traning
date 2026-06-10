---

name: handoff-generator
description: Generuj pakiety przekazania na koniec sesji z artefaktów środowiska roboczego, tworząc zarówno czytelny dla człowieka Markdown, jak i czytelny dla maszyny JSON z kluczem do siedmiu pól kanonicznych.
version: 1.0.0
phase: 14
lesson: 40
tags: [handoff, generator, session-end, packet, next-action]

---

Biorąc pod uwagę środowisko robocze (stan, werdykt, przegląd, dziennik opinii, różnice), utwórz generator przekazania na koniec sesji podłączony do środowiska wykonawczego agenta.

Wyprodukuj:

1. `tools/generate_handoff.py` odsłaniający `generate_handoff(snapshot) -> (markdown, payload)`.
2. `outputs/handoff/<session_id>/handoff.md` i `handoff.json`.
3. `handoff.schema.json` obejmujący siedem wymaganych pól i format końcowej informacji zwrotnej.
4. Skrypt przechwytujący koniec sesji, który uruchamia generator i odmawia zamknięcia sesji, jeśli brakuje jakiegokolwiek pola.
5. `docs/handoff.md` wymieniający siedem pól, ich źródła i zasady przycinania.

Twarde odrzucenia:

- Przekazanie bez `next_action`. Raporty o stanie udające przekazania zatruwają następną sesję.
- Generator, który ręcznie pisze podsumowanie. Zadaniem agenta jest pozostawienie stołu roboczego w stanie umożliwiającym wygenerowanie.
- Pakiet przeceny, który odbiega od JSON. JSON jest źródłem; Markdown to render JSON.
- Ogon opinii dłuższy niż 30 wpisów. Pełny dziennik znajduje się w kontroli wersji; pakiet musi pozostać mały.

Zasady odmowy:

- Jeżeli brakuje raportu weryfikacyjnego, odmów wygenerowania pakietu. Przekazanie bez wyroku jest życzeniem.
- Jeśli brakuje raportu z przeglądu, a oczekiwano weryfikatora przez człowieka, odmów i zażądaj najpierw zaliczenia recenzji.
- Jeśli podsumowanie różnic jest puste, ale sesja trwała dłużej niż 5 minut, wykryj anomalię przed wygenerowaniem; podejrzewaj raczej zaklinowaną sesję niż prawdziwy brak operacji.

Struktura wyjściowa:

```
<repo>/
├── outputs/handoff/<session_id>/
│   ├── handoff.md
│   └── handoff.json
├── tools/generate_handoff.py
├── handoff.schema.json
└── docs/handoff.md
```

Zakończ słowami „co przeczytać dalej”, wskazując:

- Lekcja 41 zawierająca kompleksowe ćwiczenia na przykładowej aplikacji w prawdziwym stylu.
- Lekcja 42 dotycząca pakowania generatora do pakietu stołu warsztatowego zwieńczenia.
- Lekcja 29 (Środowisko wykonawcze) na temat łączenia końca sesji z wyzwalaczami kolejki, zdarzeń i cron.