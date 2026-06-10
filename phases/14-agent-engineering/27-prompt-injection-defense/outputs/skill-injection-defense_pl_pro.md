---

name: injection-defense
description: Budowa warstwy PVE (Prompt-Validator-Executor) z obsługą tagowania źródeł treści, detekcją wstrzykiwania promptów oraz nawigacją w oparciu o listę dozwolonych dla środowiska uruchomieniowego agenta.
version: 1.0.0
phase: 14
lesson: 27
tags: [security, prompt-injection, pve, greshake, source-tag]

---

Mając agenta z dostępem do narzędzi oraz możliwością pobierania zewnętrznych danych (RAG), stwórz warstwę zabezpieczającą przed atakami typu Prompt Injection.

Zakres wdrożenia:

1. Znaczniki źródła (source tags) przypisane do każdego fragmentu danych: `user_message`, `tool_output`, `retrieved_web`, `retrieved_memory`, `retrieved_file`. Zapewnij propagację tych tagów w historii konwersacji.
2. Metoda `Validator.assess(tool_call, contents)`: odrzuca wywołania narzędzi zawierające argumenty o strukturze wskazującej na prompt injection lub pobraną treść; wywołania są dozwolone tylko wtedy, gdy tagi źródłowe odpowiadają wymaganemu poziomowi zaufania.
3. Listy dozwolonych/zablokowanych (Allowlists/Blocklists) dla zasobów sieciowych i lokalnych: dozwolone adresy URL, domeny oraz ścieżki systemów plików, z którymi agent może wchodzić w interakcję.
4. Bariera zapisu w pamięci (Memory guard): blokowanie i odrzucanie zapisów do bazy pamięci, które przypominają instrukcje sterujące.
5. Architektura izolacji danych (lekcja 23): surowe pobrane dane zewnętrzne powinny być przechowywane w zewnętrznym bezpiecznym magazynie, a w logach śladów (spans) należy umieszczać jedynie referencje do nich.
6. Zestaw testów bezpieczeństwa (Red Team Suite): pięć klas exploitów zidentyfikowanych przez Greshake i in. jako scenariusze testowe do oceny podatności systemu.

Kryteria odrzucenia (Hard Rejects):

- Udostępnienie wywołań narzędzi bez wdrożonego systemu oznaczania źródeł danych. Bez identyfikacji pochodzenia danych (provenance) nie da się poprawnie autoryzować uprawnień.
- Umieszczenie walidatora działającego wyłącznie na końcowej odpowiedzi dla użytkownika. Sprawdzanie wyjścia na końcu procesu nie zapobiega szkodliwym akcjom wykonanym przez narzędzia w trakcie pętli.
- Opieranie bezpieczeństwa na założeniu: „Prompt systemowy odpowiednio instruuje model i to wystarczy”. Prompty systemowe nie stanowią twardego i niezawodnego zabezpieczenia technicznego.

Zasady odmowy (Refusal Rules):

- Jeśli agent posiada mechanizmy pobierania danych zewnętrznych, ale nie wdrożono oznaczania ich źródła, odmów wdrożenia. Niezweryfikowane dane pobierane z zewnątrz są głównym wektorem ataków wstrzykiwania promptów.
- Jeśli krytyczne narzędzia (takie jak wysyłka wiadomości, wykonywanie poleceń powłoki systemowej, zapisywanie plików w katalogach systemowych) nie posiadają zatwierdzenia przez człowieka (Human-in-the-Loop), odmów.
- Jeśli operacje zapisu w pamięci długoterminowej nie są kontrolowane i weryfikowane, odmów. Trwałe zatrucie pamięci skutkuje ponownym zainfekowaniem agenta w kolejnych sesjach.

Dane wyjściowe: Pliki `validator.py`, `source_tag.py`, `allowlist.py`, `memory_guard.py`, `red_team.py`, `README.md` objaśniające sześć poziomów zabezpieczeń, ryzyko resztkowe oraz procedurę audytu bezpieczeństwa. Zakończ sekcją „Co przeczytać dalej”, odsyłającą do lekcji 21 (Bezpieczeństwo korzystania z komputera) oraz lekcji 23 (Izolacja treści i OTel).
