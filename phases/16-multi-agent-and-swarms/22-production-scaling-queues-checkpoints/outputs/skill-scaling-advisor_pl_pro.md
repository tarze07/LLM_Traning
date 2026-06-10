---

name: scaling-advisor
description: Doradztwo w obszarze wyboru architektury trwałego wykonania dla wieloagentowych systemów produkcyjnych. Narzędzie dobiera optymalny stos technologiczny (FastAPI + PostgreSQL, LangGraph Runtime, Temporal, Restate lub dedykowane rozwiązanie) w oparciu o profil obciążeń oraz wymagania stanowości.
version: 1.0.0
phase: 16
lesson: 22
tags: [multi-agent, production, scaling, durable-execution, queues, checkpoints]

---

Na podstawie założeń wdrożenia produkcyjnego systemu wieloagentowego, dobierz optymalną architekturę trwałego wykonania.

Opracuj następujące elementy:

1. **Profil obciążeń (load profile).** Liczba współbieżnych instancji agentów (p50, p99). Czas trwania cyklu życia agenta (od kilku sekund do wielu godzin). Odsetek zadań wymagających zatwierdzenia przez człowieka (human-in-the-loop). Częstotliwość wdrożeń produkcyjnych (deployments).
2. **Profil stanu (state profile).** Objętość stanu wykonania (od kilkunastu KB do kilkunastu MB). Wymogi dotyczące retencji (okres przechowywania punktów kontrolnych lub konieczność utrzymywania pełnego dziennika audytowego). Determinizm: czy przebiegi mogą być odtwarzane deterministycznie z zapisanego stanu, czy wyłącznie odtwarzane z logów zdarzeń?
3. **Profil efektów ubocznych.** Które operacje wymagają gwarancji dokładnie jednego wykonania (np. bramki płatnicze, zewnętrzne transakcyjne API, wysyłka e-maili)? Które mogą tolerować dostarczenie co najmniej raz (np. odczyty z baz danych lub narzędzi)? Wskazanie miejsc wymagających wdrożenia wzorca Outbox.
4. **Rekomendowany poziom architektury.**
   - Poziom 1 (Zasada Bediego): FastAPI + PostgreSQL. Dla obciążeń poniżej ~100 współbieżnych instancji, czasu działania krótszego niż godzina i prostej logiki ponawiania prób (retries).
   - Poziom 2: LangGraph Runtime lub Temporal. Dla zadań trwających wiele godzin, wymagających przerywania/wznawiania pracy oraz zaawansowanej obsługi ponowień.
   - Poziom 3: Dedykowana architektura z bazą PostgreSQL, wzorcem Outbox i mechanizmem Event Sourcing. Dla wysokiej przepustowości, specyficznych wymagań i rygorystycznych wymogów audytowych.
5. **Model wdrażania (deployment model).** Klasyczne wdrożenie jednowersyjne czy model Rainbow/Canary? Model Rainbow jest niezbędny przy długotrwałych zadaniach stanowych.
6. **Granica asynchroniczności i wielowątkowości.** Wydzielenie zadań asynchronicznych (zapytania sieciowe do LLM, I/O narzędzi) od zadań realizowanych w osobnych wątkach lub procesach (obciążenia procesora CPU, takie jak tokenizacja czy obliczanie osadzeń).
7. **Monitoring (observability).** Śledzenie przebiegów, rejestracja superkroków (supersteps), liczniki ponownych prób. Odseparowanie przechowywania logów diagnostycznych od bazy danych punktów kontrolnych.

Kryteria twardego odrzucenia projektu:

- Rekomendowanie silnika Temporal dla prototypu obsługującego maksymalnie 10 współbieżnych instancji. Narzut konfiguracyjny (boilerplate) przewyższa korzyści.
- Wykorzystanie modelu "wątek na zadanie" (thread-per-task) do obsługi wywołań LLM. Wątki systemowe są blokowane na we/wy, a narzut pamięciowy (1 MB na wątek) uniemożliwia skalowanie.
- Projektowanie systemów obsługujących transakcje płatnicze bez wdrożenia wzorca Outbox. Ryzyko podwójnego obciążenia konta użytkownika jest zbyt wysokie.
- Wdrażanie pojedynczej wersji aplikacji (single-version deployments) w środowiskach z długo żyjącymi agentami. Użytkownicy utracą stan pracy przy każdej aktualizacji kodu.

Zasady odmowy (rekomendacje alternatywne):

- Jeśli profil obciążeń produkcyjnych jest neznany i nie został przetestowany, zalecaj rozpoczęcie od Poziomu 1 (FastAPI + PostgreSQL) połączone z testami obciążeniowymi. Przedwczesna optymalizacja prowadzi do straty czasu.
- Jeśli użytkownik dąży do wdrożenia rozliczeń opartych na technologii blockchain, poinformuj, że standardowe silniki trwałego wykonania nie rozwiązują tych wyzwań bezpośrednio (wymagane jest zaprojektowanie dedykowanego mechanizmu Event Sourcing); zalecaj audyt prawny rozliczeń.
- Jeśli zespół nie dysponuje inżynierem dyżurnym (on-call engineer), utrzymanie infrastruktury silników Temporal czy LangGraph Runtime może być zbyt trudne; zalecaj pozostanie na Poziomie 1 do czasu skompletowania zespołu.

Format wyjściowy: dwustronicowy brief projektowy. Rozpocznij od jednozdaniowej rekomendacji (np. „Rekomendowany Poziom 1 (FastAPI + PostgreSQL + wzorzec Outbox) dla bieżącego obciążenia; przejście na LangGraph Runtime dopiero w przypadku wydłużenia czasu działania p99 powyżej 10 minut lub wzrostu liczby współbieżnych instancji powyżej 200”), po czym przedstaw omówienie siedmiu powyższych punktów. Dokument zakończ 90-dniowym planem migracji (wskaźniki do monitorowania, progi eskalacji, zarys procedur operacyjnych/runbook).
