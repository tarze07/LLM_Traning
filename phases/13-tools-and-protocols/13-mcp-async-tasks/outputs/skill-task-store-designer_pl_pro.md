---

name: task-store-designer
description: Zaprojektuj trwały magazyn zadań dla długotrwałego narzędzia MCP (struktura stanu, wagi TTL, trwałość, mechanizmy anulowania i odzyskiwania po awarii).
version: 1.0.0
phase: 13
lesson: 13
tags: [mcp, tasks, durable-store, long-running, sep-1686]

---

Na podstawie specyfikacji długotrwałego narzędzia (badania, kompilacja, eksport, generowanie raportów) zaprojektuj architekturę magazynu zadań asynchronicznych zgodnego ze standardem SEP-1686.

Wygeneruj:

1. Struktura stanu zadania. Wskaż minimalne wymagane pola: `id`, `state`, `progress`, `result`, `error`, `ttl`, `created_at` oraz opcjonalne: `request_meta`, `parent_task_id` (pod kątem planowanej obsługi podzadań).
2. Warstwa trwałości (Persistence). Dobierz technologię zapisu: system plików (dla celów testowych/lokalnych), SQLite (dla pojedynczego procesu) lub Redis (dla systemów rozproszonych) wraz z uzasadnieniem technologicznym.
3. Konfiguracja wsparcia zadań (`taskSupport`). Przypisz status `forbidden`, `optional` lub `required` dla narzędzia wraz z jednozdaniowym uzasadnieniem.
4. Strategia anulowania. Opisz, w jaki sposób proces roboczy (worker) weryfikuje sygnał anulowania zadania oraz jak obsługiwany jest stan częściowego wykonania prac.
5. Odzyskiwanie po awarii. Zdefiniuj reguły weryfikacji i ładowania zadań przy starcie aplikacji oraz opisz, w jaki sposób błędy typu `CRASH_RECOVERY` są prezentowane klientowi.

Kryteria odrzucenia (Twarde reguły):
- Zaprojektowanie magazynu, który traci dane o zakończonych zadaniach przed upływem zadeklarowanego czasu TTL.
- Brak zdefiniowania jednoznacznych statusów końcowych dla stanu zadania (`completed`, `failed`, `cancelled`).
- Brak zachowania idempotentności dla akcji anulowania zadania.

Zasady odmowy usługi:
- Jeśli czas wykonywania narzędzia nie przekracza zazwyczaj 5 sekund, odmów projektowania pętli asynchronicznej (wykonanie synchroniczne jest optymalne).
- Jeśli zadanie generuje pliki wynikowe o rozmiarze przekraczającym 10 MB, odmów weryfikacji i zalecaj wdrożenie strumieniowego przesyłania bloków treści.
- Jeśli serwer działa w środowisku bezstanowym uniemożliwiającym zachowanie stanu sesji (np. stateless serverless edge functions), odmów weryfikacji i rekomenduj migrację do środowiska stanowego (stateful runtime).

Format wyjściowy: Jednostronicowy projekt magazynu zadań zawierający strukturę stanu, technologię zapisu danych, flagi taskSupport, strategię anulowania oraz reguły odzyskiwania po awarii. Na końcu określ, czy i w jaki sposób planowane wprowadzenie podzadań w SEP-1686 wpłynie na ten projekt.
