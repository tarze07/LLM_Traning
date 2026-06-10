---

name: virtual-memory
description: Zbuduj dwupoziomowy system pamięci w kształcie MemGPT (kontekst główny + magazyn archiwalny + narzędzia pamięci) dla dowolnego docelowego środowiska wykonawczego z poprawną obsługą eksmisji, cytowań i niezaufanych danych wejściowych.
version: 1.0.0
phase: 14
lesson: 07
tags: [memory, memgpt, virtual-context, archival, citations]

---

Biorąc pod uwagę docelowe środowisko wykonawcze (Python, Node, Rust), dostawcę modelu (Anthropic, OpenAI, lokalny) i zaplecze pamięci masowej (in-memory, SQLite, Vector DB, KV, graph), utwórz poprawny system pamięci w kształcie MemGPT.

Wyprodukuj:

1. Typ `MainContext` z dyktatem `core` (nazwanymi sekcjami trwałymi) i listą `messages` (FIFO). Automatyczna eksmisja w przypadku ograniczenia rozmiaru; eksmitowane zwroty pozostają możliwe do odzyskania przez `conversation_search`.
2. `ArchivalStore` z wstawianiem i wyszukiwaniem. Dokumentacja MUSI zawierać `id`, `text`, `tags`, `session_id`, `turn_id`, `created_at`. Każdy zapis zwraca przechowywany identyfikator do cytowania.
3. Pięć narzędzi pamięci pasujących do powierzchni MemGPT: `core_memory_append`, `core_memory_replace`, `archival_memory_insert`, `archival_memory_search`, `conversation_search`. Przedstaw je modelowi za pomocą tekstu `description`, który informuje modela, kiedy użyć każdego z nich.
4. Umowa o cytowanie: przy każdym pobraniu archiwalnym MUSZĄ być zwracane identyfikatory rekordów wraz z tekstem, a agent MUSI je cytować w ostatecznych odpowiedziach. Odpowiedzi bez cytatów to miękka porażka.
5. Hak konsolidacyjny (w wersji 1 może nie działać), aby agenci uśpienia z Lekcji 08 mogli podłączyć się bez konieczności ponownej instalacji. Odsłoń `list_records_since(timestamp)` i `delete(id)`.

Twarde odrzucenia:

- Wyszukiwanie archiwalne z pełną punktacją LLM. Użyj odpowiedniego backendu do pobierania (BM25, podobieństwo wektorów). Ponowne umieszczenie w rankingu LLM jest dozwolone na krótkiej liście najlepszych kandydatów, a nie w pełnym korpusie.
- Główny kontekst bez polityki eksmisji. Nieograniczony główny kontekst cicho rośnie za oknem.
- Przechowywanie pobranych treści tak, jakby były to instrukcje dla użytkownika. Cała zawartość archiwalna jest tekstem niezaufanym (Lekcja 27). Przekaż go modelowi jako obserwację, a nie jako monit systemowy.
- Napisanie narzędzia `core_memory_clear`, które czyści wszystkie sekcje. Rdzeń jest nośny; oczyszczanie to strzał w dziesiątkę. Obsługuje `replace`, a nie `clear`.

Zasady odmowy:

- Jeśli użytkownik poprosi o „żadnych cytatów, tylko odpowiedzi”, odrzuć jakąkolwiek domenę, w której podanie źródła ma znaczenie (medyczne, prawne, polityczne, finansowe). Zaproponuj kompromis: cytaty renderowane jako przypisy, a nie w tekście.
- Jeśli użytkownik poprosi o „zapisanie całej odzyskanej treści z powrotem do archiwum bez filtrowania”, odmów i wskaż Lekcję 27. Pobrana treść jest dostępna dla atakującego; ogólne odpisywanie to zatrucie pamięci.
- Jeśli środowisko wykonawcze nie ma warstwy trwałości, odmów wysłania agenta opisanego jako posiadający „pamięć długoterminową”. Zmień opis produktu, a nie implementację.

Dane wyjściowe: jeden plik na komponent (`main_context.*`, `archival_store.*`, `memory_tools.*`, `agent.*`) plus `README.md` wyjaśniający politykę eksmisji, umowę cytowania i miejsce podłączenia lekcji 08 (konsolidacja czasu snu) i lekcji 09 (fuzja Mem0). Zakończ słowami „Co dalej czytać”, wskazując Lekcję 08, jeśli agent potrzebuje trzech warstw lub konsolidacji asynchronicznej, lub Lekcję 09, jeśli agent potrzebuje fuzji wektorów, KV i wykresów.