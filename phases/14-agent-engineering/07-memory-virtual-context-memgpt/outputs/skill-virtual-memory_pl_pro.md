---

name: virtual-memory
description: Zaimplementuj dwupoziomowy system pamięci w stylu MemGPT (kontekst główny, magazyn archiwalny, interfejs narzędziowy) z obsługą wygaszania danych, cytowaniem źródeł i ochroną przed niezweryfikowanymi danymi.
version: 1.0.0
phase: 14
lesson: 07
tags: [memory, memgpt, virtual-context, archival, citations]

---

Dla wybranego środowiska uruchomieniowego (Python, Node, Rust), dostawcy modelu (Anthropic, OpenAI, model lokalny) oraz silnika bazy danych (w pamięci, SQLite, baza wektorowa, KV, baza grafowa) zaimplementuj system pamięci wzorowany na architekturze MemGPT.

Przygotuj:

1. Klasa `MainContext`: Powinna zawierać słownik `core` (dla nazwanych sekcji trwałych) oraz lista `messages` (działającą jako kolejka FIFO). Zaimplementuj automatyczne usuwanie (eksmisję) najstarszych komunikatów po przekroczeniu limitu rozmiaru; usunięte tury konwersacji muszą pozostać dostępne dla przeszukiwania za pomocą funkcji `conversation_search`.
2. Magazyn archiwalny `ArchivalStore`: Obsługujący operacje zapisu oraz wyszukiwania. Każdy wpis musi zawierać pola: `id`, `text`, `tags`, `session_id`, `turn_id`, `created_at`. Każdy udany zapis musi zwracać identyfikator wpisu, który posłuży do cytowania źródeł.
3. Interfejs pięciu narzędzi pamięci: Zgodny ze specyfikacją MemGPT (`core_memory_append`, `core_memory_replace`, `archival_memory_insert`, `archival_memory_search`, `conversation_search`). Zdefiniuj dla nich precyzyjne opisy (`description`), które jasno wskażą modelowi właściwy moment użycia każdej z funkcji.
4. Reguła cytowania: Każde wyszukiwanie archiwalne musi zwracać identyfikatory rekordów wraz z ich treścią. Agent ma obowiązek powoływać się na te identyfikatory w sformułowanej odpowiedzi. Generowanie odpowiedzi bez wskazania źródeł jest traktowane jako błąd (soft failure).
5. Interfejs konsolidacji (haki): Pozwalający procesom tła (sleep-time z Lekcji 08) na integrację z systemem pamięci. Udostępnij funkcje `list_records_since(timestamp)` oraz `delete(id)`.

Kryteria odrzucenia:
- Realizowanie wyszukiwania w archiwum wyłącznie za pomocą oceny całego korpusu przez model LLM. Do pobierania danych użyj właściwego silnika (np. BM25, wyszukiwanie wektorowe). Ponowne ocenianie (reranking) przez model LLM jest dopuszczalne jedynie dla wąskiej listy wstępnie wybranych kandydatów.
- Pozostawienie głównego kontekstu bez mechanizmu usuwania (eksmisji) starych danych. Kontekst bez ograniczeń będzie cicho rósł, aż przekroczy limit okna modelu.
- Przekazywanie pobranych danych z archiwum w taki sposób, jakby były to bezpieczne instrukcje systemowe. Wszelkie treści z bazy archiwalnej należy traktować jako dane niezaufane (Lekcja 27) i przekazywać je modelowi wyłącznie jako obserwacje (wyniki działania narzędzi).
- Wdrożenie funkcji `core_memory_clear` czyszczącej całą pamięć roboczą. Pamięć Core przechowuje kluczowy kontekst, a jej całkowite usunięcie zakłóca stabilność agenta. Zamiast operacji czyszczenia (`clear`) należy udostępnić operację modyfikacji/zastąpienia (`replace`).

Zasady odmowy wykonania zadania:
- Jeśli użytkownik żąda pominięcia cytowań w odpowiedziach, odmów realizacji w domenach krytycznych (np. medycyna, prawo, finanse, polityka). Jako alternatywę zaproponuj kompromisowe rozwiązanie, np. prezentowanie źródeł w formie przypisów dolnych zamiast wtrąceń w tekście.
- Jeśli użytkownik żąda bezkrytycznego zapisywania wszelkich pobranych z sieci danych z powrotem do bazy archiwalnej bez uprzedniego filtrowania, odmów wykonania i powołaj się na Lekcję 27. Pobrane treści mogą pochodzić od osób trzecich i prowadzić do trwałego zatrucia bazy danych (memory poisoning).
- Jeśli wybrane środowisko uruchomieniowe nie zapewnia trwałego zapisu danych, odmów wdrożenia agenta reklamowanego jako posiadający „pamięć długoterminową”. Należy wówczas skorygować opis produktu, a nie maskować brak trwałości.

Oczekiwany rezultat: Osobny plik dla każdego komponentu (`main_context.*`, `archival_store.*`, `memory_tools.*`, `agent.*`) oraz plik `README.md` opisujący politykę usuwania danych, zasady cytowania oraz punkty integracji z rozwiązaniami z Lekcji 08 (konsolidacja w czasie bezczynności) i Lekcji 09 (baza Mem0). Na końcu umieść sekcję „Sugerowane lektury” odsyłającą do Lekcji 08 (gdy wymagana jest pamięć trójwarstwowa lub asynchroniczne kompaktowanie) lub Lekcji 09 (gdy zachodzi potrzeba łączenia bazy wektorowej, KV oraz grafów).
