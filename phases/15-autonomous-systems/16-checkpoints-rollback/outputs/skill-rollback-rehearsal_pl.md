---

name: rollback-rehearsal
description: Zaprojektuj test wycofywania zmian dla proponowanego autonomicznego przepływu pracy i przeprowadź audyt zaplecza punktu kontrolnego pod kątem trwałości ścieżki audytu.
version: 1.0.0
phase: 15
lesson: 16
tags: [checkpointing, rollback, idempotency, eu-ai-act-article-14, durable-execution]

---

Biorąc pod uwagę proponowany autonomiczny przepływ pracy o długim horyzoncie, zaprojektuj test wycofywania zmian, który udowodni, że idempotencja + warunek wstępny + weryfikacja + stos wycofywania faktycznie działa od początku do końca, a następnie przeprowadź audyt zaplecza punktu kontrolnego pod kątem gotowości do stosowania przez organy regulacyjne.

Wyprodukuj:

1. **Skrypt próbny.** Konkretny test, który (a) rozpoczyna przepływ pracy, (b) zawiesza go w połowie zatwierdzania, (c) wznawia, (d) potwierdza, że akcja uruchamia się dokładnie raz, (e) wprowadza błąd weryfikacji, (f) potwierdza uruchomienie wycofywania i przywrócenie stanu. Żaden proces produkcyjny nie powinien przebiegać bez pozytywnego zaliczenia tego testu przynajmniej raz.
2. **Audyt idempotencji.** Potwierdź, że klucz idempotencji pochodzi z treści propozycji (Lekcja 15), a logika zatwierdzania wykorzystuje jawne stany wykonania (`pending` -> `executing` -> `committed`/`failed`). Zarezerwuj/zablokuj kluczem idempotencji przed skutkiem ubocznym i zaznacz `committed` dopiero po zweryfikowaniu efektu ubocznego.
3. **Wykaz warunków wstępnych.** Wymień wszystkie warunki wstępne, które przepływ pracy musi ponownie sprawdzić w momencie zatwierdzenia. Najczęstszym błędem produkcyjnym są luki w czasie kontroli i czasie użytkowania; warunek wstępny należy ocenić przy zatwierdzeniu, a nie przy propozycji.
4. **Sprawdź stan zapasów.** Dla każdego wynikającego z tego działania podaj konkretny odczyt potwierdzający wystąpienie efektu ubocznego. „Zwrócone 200” jest niedopuszczalne.
5. **Wycofanie zapasów.** Dla każdego wynikającego z tego działania należy sklasyfikować wycofanie jako alert w paśmie, transakcja kompensacyjna lub alert poza pasmem. Wycofywanie bez operacji („nie możemy tego cofnąć”) musi zostać wyraźnie nazwane w propozycji (metadane z lekcji 15).

Twarde odrzucenia:
- Przepływy pracy bez przećwiczonego wycofywania.
- Backendy Checkpoint, które tracą dane podczas wdrażania.
- Ścieżki zatwierdzenia, w których status jest zapisywany po wykonaniu, a nie przed.
- Stany „Zweryfikowane”, które sprawdzają tylko kod powrotu wywołania narzędzia.
- Sprawdzanie warunków wstępnych, które są uruchamiane tylko w czasie proponowania, a nie w czasie zatwierdzania.

Zasady odmowy:
- Jeśli użytkownik nie uruchomił skryptu próby przynajmniej raz w fazie inscenizacji, odmów wdrożenia produkcyjnego.
- Jeśli użytkownik nie może wygenerować schematu magazynu punktów kontrolnych, odmów i najpierw zażądaj dokumentacji schematu. Organy regulacyjne chcą stanu, który można zapytać.
- Jeśli przepływ pracy zależy od punktu kontrolnego w pamięci (brak trwałości), odmów.

Format wyjściowy:

Zwróć plan prób zawierający:
- **Zarys skryptu testowego** (kroki z asercjami)
- **Tabela idempotencji** (skład kluczy, kolejność zapisu stanu)
- **Tabela warunków wstępnych** (sprawdź, po ocenie, konsekwencje)
- **Sprawdź tabelę** (działanie, przeczytaj, to potwierdza)
- **Tabela wycofania** (akcja, typ, stan docelowy)
- **Zaświadczenie backendu** (przechowywanie, przetrwanie i wdrożenie tak/nie, gotowość do zapytania tak/nie)
- **Gotowość** (tylko produkcja / etapowanie / badania)