---

name: skill-library
description: Wygeneruj bibliotekę umiejętności w kształcie Voyagera z rejestracją, wyszukiwaniem na podstawie podobieństwa, wykonaniem kompozycji i udoskonalaniem opartym na awariach.
version: 1.0.0
phase: 14
lesson: 10
tags: [voyager, skills, library, composition, refinement]

---

Biorąc pod uwagę docelowy czas wykonania i domenę, utwórz bibliotekę umiejętności, która obsługuje trzy komponenty Voyagera: haczyk programu nauczania, możliwy do odzyskania magazyn umiejętności, udoskonalanie iteracyjne.

Wyprodukuj:

1. Typ `Skill` z `name`, `description`, `code`, `version`, `tags`, `depends_on`, `history`. Każdy zapis rejestruje poprzedni kod.
2. `SkillLibrary` z `register(skill, dedup=True)` (nowa wersja lub aktualizacja), `search(query, top_k, tag_filter)`, `get(name)`, `topo_order(name)` (głęboka rozdzielczość), `execute(name, context)` (bieg topologiczny).
3. Pobieranie MUSI wykorzystywać podobieństwo osadzania lub BM25, a nie punktację LLM w całej bibliotece. Zmiana pozycji LLM dozwolona na krótkiej liście najlepszych kandydatów.
4. Wykonanie MUSI wychwytywać wyjątki dla poszczególnych umiejętności i wyświetlać je w śladzie jako informację zwrotną, którą może wykorzystać pętla udoskonalająca.
5. Hak udoskonalenia: po nieudanym `execute` środowisko wykonawcze zbiera (zadanie, nazwa_umiejętności, błąd, stan_stanu), przekazuje je do modelu i wywołuje `register` w przypadku przepisanej umiejętności. Wyboje wersji; historia zachowuje stary kod.

Twarde odrzucenia:

- Biblioteka, w której umiejętności to ciągi prozy, a nie kod. Umiejętności są wykonalne. Proza należy do `description`.
- Kompozycja bez sortowania topologicznego. Najpierw głębokość, bez przerw w wykrywaniu cykli w umiejętnościach DAG.
- Cicha wersja nadpisuje. Każde udoskonalenie MUSI podbić `version` i przenieść stary kod do `history` w celu audytu.

Zasady odmowy:

- Jeśli docelowe środowisko wykonawcze nie ma piaskownicy do wykonywania umiejętności, odrzuć domeny, w których umiejętności dotykają systemów produkcyjnych. Wymagaj piaskownicy (zasady lekcji 09) przed wysyłką.
- Jeśli użytkownik poprosi o „automatyczne ponawianie próby przy każdym niepowodzeniu bez poprawiania”, odmów. Ponowne próby bez udoskonalenia wzmacniają błąd; nie naprawiają tego.
- Jeśli biblioteka przekracza ~200 umiejętności przy pobieraniu płaskim, nie nazywaj jej „gotową do produkcji”. Najpierw dodaj filtry tagów i hierarchiczne przestrzenie nazw.

Dane wyjściowe: `skill.py`, `library.py`, `execute.py`, `refine.py` i `README.md` wyjaśniające regułę deduplikacji, zaplecze pobierania, monit o udoskonalenie i zasady wersji. Zakończ słowami „Co przeczytać dalej”, wskazując Lekcję 17 na temat integracji pakietu SDK Claude Agent, Lekcję 16 na temat tłumaczenia narzędzia SDK dla agentów OpenAI lub Lekcję 30 na temat oceny jakości biblioteki umiejętności.