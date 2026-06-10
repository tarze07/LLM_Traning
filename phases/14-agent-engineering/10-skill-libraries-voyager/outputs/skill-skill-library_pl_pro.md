---

name: skill-library
description: Wygeneruj bibliotekę umiejętności w stylu Voyagera z rejestracją, wyszukiwaniem semantycznym, wykonywaniem kompozycji i udoskonalaniem opartym na błędach.
version: 1.0.0
phase: 14
lesson: 10
tags: [voyager, skills, library, composition, refinement]

---

W oparciu o docelowe środowisko uruchomieniowe i domenę utwórz bibliotekę umiejętności obsługującą trzy komponenty Voyagera: integrator programu nauczania (curriculum hook), wyszukiwalny magazyn umiejętności oraz iteracyjne udoskonalanie.

Wygeneruj:

1. Typ danych `Skill` z polami `name`, `description`, `code`, `version`, `tags`, `depends_on`, `history`. Każdy zapis nowej wersji archiwizuje poprzedni kod w historii.
2. Klasa `SkillLibrary` z metodami `register(skill, dedup=True)` (rejestracja nowej wersji lub aktualizacja), `search(query, top_k, tag_filter)`, `get(name)`, `topo_order(name)` (głębokie rozwiązywanie zależności) oraz `execute(name, context)` (wykonanie w porządku topologicznym).
3. Wyszukiwanie MUST korzystać z podobieństwa osadzeń (embeddings) lub algorytmu BM25, a nie z oceniania przez LLM całej biblioteki. Ponowne pozycjonowanie (reranking) za pomocą LLM jest dopuszczalne wyłącznie dla krótkiej listy najlepszych kandydatów.
4. Wykonanie kodu MUST przechwytywać wyjątki z poszczególnych umiejętności i zapisywać je w logach (trace) jako informację zwrotną dla pętli udoskonalającej.
5. Mechanizm udoskonalania: po nieudanym wywołaniu `execute` środowisko uruchomieniowe zbiera dane (zadanie, nazwa_umiejętności, błąd, stan), przekazuje je do LLM i rejestruje poprawioną umiejętność za pomocą `register`. Wersja umiejętności zostaje podniesiona, a poprzedni kod trafia do historii.

Kryteria odrzucenia (Hard rejects):

- Biblioteka, w której umiejętności są opisane prozą zamiast kodu. Umiejętności muszą być bezpośrednio wykonywalne. Opisy słowne powinny trafiać wyłącznie do pola `description`.
- Kompozycja bez sortowania topologicznego (najpierw przeszukiwanie w głąb - DFS) z wykrywaniem cykli w grafie skierowanym (DAG) zależności.
- Ciche nadpisywanie wersji. Każde udoskonalenie MUST podnosić `version` i archiwizować stary kod w `history` w celach audytowych.

Zasady odmowy (Guardrails):

- Jeśli docelowe środowisko uruchomieniowe nie posiada bezpiecznej piaskownicy (sandbox), odrzuć wdrożenia w domenach, w których umiejętności wchodzą w bezpośrednią interakcję z systemami produkcyjnymi. Wymagaj środowiska izolowanego (zasady z Lekcji 09).
- Jeśli użytkownik żąda „automatycznego ponawiania prób bez wprowadzania poprawek”, odmów. Ponowne uruchamianie wadliwego kodu bez jego modyfikacji utrwala błędy zamiast je naprawiać.
- Jeśli wyszukiwanie płaskie obsługuje bibliotekę o rozmiarze przekraczającym ok. 200 umiejętności, nie określaj jej jako rozwiązania produkcyjnego. Wymagane jest wcześniejsze wdrożenie filtrów tagów i hierarchicznych przestrzeni nazw.

Wygenerowana struktura: pliki `skill.py`, `library.py`, `execute.py`, `refine.py` oraz `README.md` wyjaśniający zasady deduplikacji, backend wyszukiwania, prompty udoskonalania i politykę wersjonowania. Zakończ sekcją „Co czytać dalej”, odsyłając do Lekcji 17 (integracja z Claude Agent SDK), Lekcji 16 (mapowanie narzędzi w OpenAI Agents SDK) lub Lekcji 30 (ocena jakości biblioteki umiejętności).
