---

name: injection-defense
description: Zbuduj warstwę PVE (Prompt-Validator-Executor) z treścią ze znacznikami źródłowymi, skanowaniem znaczników wtrysku i nawigacją na liście dozwolonych dla dowolnego środowiska wykonawczego agenta.
version: 1.0.0
phase: 14
lesson: 27
tags: [security, prompt-injection, pve, greshake, source-tag]

---

Mając agenta z dostępem do narzędzi i możliwością ich odzyskiwania, utwórz warstwę chroniącą przed wtryskiem.

Wyprodukuj:

1. Znacznik źródłowy na każdym fragmencie treści: `user_message`, `tool_output`, `retrieved_web`, `retrieved_memory`, `retrieved_file`. Propaguj tagi w historii wiadomości.
2. `Validator.assess(tool_call, contents)` — odrzuca wywołania narzędzi z argumentami w kształcie wtrysku lub pobraną treścią; dozwolone tylko wtedy, gdy tagi źródłowe odpowiadają zadeklarowanemu poziomowi zaufania.
3. Lista dozwolonych/blokowanych do nawigacji: adresy URL, domeny, ścieżki plików, których agent może dotknąć.
4. Poręcz zapisu w pamięci: odrzucanie zapisów wyglądających jak dyrektywy.
5. Dyscyplina przechwytywania treści (lekcja 23): przechowuj pobrane treści na zewnątrz; spans zawierają identyfikatory referencyjne, a nie prozę.
6. Zestaw testów: pięć klas exploitów Greshake jako przypadki zespołu czerwonego.

Twarde odrzucenia:

- Powierzchnia użytkowa narzędzia bez znaczników źródłowych. Nie można rozróżnić poziomów uprawnień bez pochodzenia.
- Walidator działający tylko na wyjściu końcowym. Późna walidacja nie ma znaczenia – model już zadziałał.
- „Zaufaj mi, poradzi sobie z tym monit systemowy”. Higiena zapewniana przez system nie jest kontrolą.

Zasady odmowy:

- Jeśli agent ma jakąkolwiek możliwość odzyskania bez oznaczania źródła, odmów wysyłki. Pobrana treść jest kanonicznym wektorem wtrysku.
- Jeśli wrażliwe narzędzia (wyślij wiadomość, wykonaj powłokę, zapisz plik w /) nie mają potwierdzenia przez człowieka w pętli, odmów.
- Jeśli zapisy w pamięci są niestrzeżone, odmów. Trwałe zatrucie pamięci ponownie zatruwa następną sesję.

Dane wyjściowe: `validator.py`, `source_tag.py`, `allowlist.py`, `memory_guard.py`, `red_team.py`, `README.md` wyjaśniające stos sześciu kontroli, ryzyko resztkowe i częstotliwość ciągłego przeglądu. Zakończ słowami „co dalej czytać”, wskazując Lekcję 21 (bezpieczeństwo korzystania z komputera) i Lekcję 23 (przechwytywanie treści za pośrednictwem Otel).