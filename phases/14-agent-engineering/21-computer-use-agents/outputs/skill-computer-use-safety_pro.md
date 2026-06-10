---

name: computer-use-safety
description: Zaimplementuj niezależny system bezpieczeństwa weryfikujący akcje krok po kroku oraz bramkę autoryzacji dla agenta sterującego komputerem, z białą listą adresów URL i filtrowaniem wstrzyknięć promptów.
version: 1.0.0
phase: 14
lesson: 21
tags: [computer-use, safety, claude, openai-cua, gemini]

---

Na podstawie specyfikacji agenta sterującego komputerem oraz listy aplikacji docelowych, utwórz warstwę bezpieczeństwa weryfikującą (klasyfikującą) każdą planowaną akcję przed jej wykonaniem.

Wyprodukuj:

1. Moduł `SafetyClassifier.assess(action, screen) -> SafetyVerdict` zwracający pola: `allow` (zezwolenie), `reason` (powód) oraz `needs_confirmation` (wymaga zatwierdzenia).
2. Białą listę etykiet elementów interfejsu (allowlist), które agent ma prawo kliknąć (w przeciwnym razie akcja jest odrzucana).
3. Białą listę dozwolonych adresów URL, na które agent może nawigować, z blokowaniem przekierowań na strony spoza listy.
4. Filtr wstrzyknięć promptów (prompt injection filter) sprawdzający tekst w strukturze DOM, pobraną zawartość oraz tekst wpisywany przez agenta (dowolne dopasowanie wzorca blokuje akcję).
5. Bramkę autoryzacji dla operacji wrażliwych (logowanie, transakcje płatnicze, usuwanie zasobów, publikowanie treści) wykorzystującą interfejs zatwierdzania przez człowieka (Human-in-the-loop).
6. Moduł telemetrii (śledzenia) rejestrujący każdą podjętą decyzję (akcja, werdykt bezpieczeństwa, powód).

Kategoryczne odrzucenia (Twarde kryteria):

- Weryfikacja bezpieczeństwa działająca wyłącznie dla pierwszej akcji. Każda kolejna akcja w pętli must zostać obowiązkowo zweryfikowana.
- Stosowanie symboli wieloznacznych (np. `*`) w białych listach. Lista zezwalająca na wszystko przestaje pełnić funkcję ochronną.
- Pomijanie autoryzacji przez człowieka ze względu na wysoki stopień pewności deklarowany przez model (confidence score). Pewność modelu nie gwarantuje bezpieczeństwa.

Zasady odmowy wykonania usługi (Refusal rules):

- Jeśli agent steruje komputerem bez wdrożonej weryfikacji akcji krok po kroku (step-by-step safety), odmów wdrożenia.
- Jeśli agent ma możliwość przejścia pod dowolne adresy URL, odmów. Wymagaj wdrożenia listy dozwolonych (allowlist) lub blokowanych (denylist).
- Jeśli istnieje jakakolwiek ścieżka wykonania, w której operacja wrażliwa omija bramkę autoryzacji człowieka, odmów.

Pliki wynikowe: `classifier.py`, `allowlist.py`, `confirmation.py`, `trace.py`, `README.md` wyjaśniające reguły działania bramek bezpieczeństwa, mechanizmy wykrywania wstrzyknięć oraz zasady zarządzania białą listą. Zakończ sekcją „Dalsza lektura”, wskazując na Lekcję 27 (wstrzykiwanie promptów - Prompt Injection) oraz Lekcję 23 (konfiguracja i śledzenie spanów OTel dla logiki bezpieczeństwa).
