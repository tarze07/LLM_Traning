---

name: task-store-designer
description: Zaprojektuj magazyn zadań dla długotrwałego narzędzia MCP: kształt stanu, czas trwania, trwałość, anulowanie, odzyskiwanie po awarii.
version: 1.0.0
phase: 13
lesson: 13
tags: [mcp, tasks, durable-store, long-running, sep-1686]

---

Biorąc pod uwagę długotrwałe narzędzie (badanie, kompilacja, eksport, generowanie raportów), zaprojektuj magazyn zadań obsługujący rozszerzanie zadań SEP-1686.

Wyprodukuj:

1. Kształt stanu. Minimalne pola: `id`, `state`, `progress`, `result`, `error`, `ttl`, `created_at`. Opcjonalnie: `request_meta`, `parent_task_id` (dla przyszłych podzadań).
2. Wybór trwałości. System plików dla zabawek; SQLite dla jednego procesu; Redis dla wielu replik. Uzasadniać.
3. Flaga wsparcia zadania. `forbidden`, `optional` lub `required` na narzędzie; uzasadnienie jednowierszowe.
4. Plan anulowania. Jak pracownik sprawdza sygnał anulowania; co dzieje się w przypadku częściowego postępu.
5. Odzyskiwanie po awarii. Reguła przeładowania w czasie rozruchu; jak dla klienta wyglądają awarie `CRASH_RECOVERY`.

Twarde odrzucenia:
- Każdy sklep, który utraci ukończone wyniki w ciągu ttl.
- Dowolny stan zadania bez wyraźnych stanów końcowych (`completed`, `failed`, `cancelled`).
- Każde anulowanie, które nie jest idempotentne.

Zasady odmowy:
- Jeśli narzędzie działa krócej niż 5 sekund, odmów awansu do zadania. Synchroniczne jest prostsze.
- Jeśli zadanie wygenerowałoby więcej niż 10 MB wyniku, odmów i zalecaj blokowanie treści przesyłanych strumieniowo.
- Jeśli serwer nie ma procesu zdolnego do utrzymywania stanu (bezstanowa funkcja brzegowa), odmów i zalecaj przejście na trwałe środowisko wykonawcze.

Wynik: jednostronicowy projekt sklepu z kształtem stanu, wyborem trwałości, flagą taskSupport, planem anulowania i regułą odzyskiwania po awarii. Zakończ jednowierszową poradą dotyczącą tego, czy podzadania SEP-1686 będą miały wpływ na ten projekt po wysłaniu.